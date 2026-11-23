"""Session-scoped coordinator: calls agents, validates what comes back, arbitrates, records provenance.

It owns no authoritative session state. The hub builds an immutable `TurnObservation`, asks the coordinator for
decisions, and commits the result itself. One coordinator instance per session (no process-global state), so
sessions and their per-agent circuit breakers are isolated.

Fault handling per agent call (FAULT -> DETECTION -> RESPONSE):
  timeout / crash / unavailable / open breaker -> no proposal; the default policy decides
  malformed output                              -> schema_violation, proposal dropped
  forbidden key (score, terminate, ...)         -> authority_violation, proposal dropped
  proposal for another turn/version             -> stale_state, proposal dropped
  second answer for the same state version      -> duplicate, second answer dropped
"""
from __future__ import annotations

import asyncio
import inspect
import json
import time
from typing import Any, Callable, Dict, List, Optional, Set

from pydantic import ValidationError

from agents.multiagent.arbitration import (
    DifficultyDecision, GuardrailFn, ProbeDecision, arbitrate_difficulty, arbitrate_probe,
)
from agents.multiagent.authority import authority_violation
from agents.multiagent.contracts import (
    COACHING, COORDINATOR, STRATEGY, AgentMessage, CoachingPlan, DecisionRecord, StrategyProposal, TurnObservation,
)
from agents.multiagent.grounding import check_plan, evidence_concepts
from agents.orchestrator.circuit_breaker import CircuitBreaker


class AgentCoordinator:
    def __init__(
        self,
        strategy_agent: Any = None,
        coaching_agent: Any = None,
        *,
        timeout_s: float = 2.0,
        tau: float = 0.6,
        enforce_authority: bool = True,
        enforce_grounding: bool = True,
        use_arbitration: bool = True,
        communication: bool = True,
        breaker_threshold: int = 2,
        breaker_cooldown_s: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
    ):
        self._agents: Dict[str, Any] = {STRATEGY: strategy_agent, COACHING: coaching_agent}
        self.timeout_s = float(timeout_s)
        self.tau = float(tau)
        self.enforce_authority = bool(enforce_authority)
        self.enforce_grounding = bool(enforce_grounding)
        self.use_arbitration = bool(use_arbitration)
        self.communication = bool(communication)
        self._breakers = {
            name: CircuitBreaker(breaker_threshold, breaker_cooldown_s, clock=clock) for name in self._agents
        }
        self._answered: Set[tuple] = set()          # (agent, state_version): duplicate detection
        self._seen_concepts: Set[str] = set()       # concepts that appeared in evaluator evidence this session
        self.records: List[DecisionRecord] = []
        self.messages: List[AgentMessage] = []
        self.call_counts: Dict[str, int] = {STRATEGY: 0, COACHING: 0}
        self.current_version: int = 0

    # ---------------------------------------------------------------- bookkeeping
    @property
    def active(self) -> bool:
        return any(a is not None for a in self._agents.values())

    def committed(self, state_version: int) -> None:
        """Hub tells the coordinator the authoritative state moved to `state_version`."""
        self.current_version = int(state_version)

    def export_telemetry(self) -> Dict[str, Any]:
        """JSON-serialisable decision records, per-agent call counts and the evidence-concept set (for session recovery).

        Not exported: circuit-breaker state (it is tied to a monotonic clock that is meaningless in another process),
        the per-version duplicate set (versions only move forward) and the full message log (volume; not used in reports).
        """
        return {
            "records": [r.model_dump(mode="json") for r in self.records],
            "call_counts": dict(self.call_counts),
            "seen_concepts": sorted(self._seen_concepts),
        }

    def import_telemetry(self, st: Dict[str, Any]) -> None:
        """Replace (never extend) the telemetry with an exported copy, so repeated restoration cannot duplicate records."""
        self.records = [DecisionRecord.model_validate(r) for r in st.get("records", [])]
        counts = st.get("call_counts") or {}
        self.call_counts = {STRATEGY: int(counts.get(STRATEGY, 0)), COACHING: int(counts.get(COACHING, 0))}
        self._seen_concepts = {str(c) for c in st.get("seen_concepts", [])}

    def note_evidence(self, obs: TurnObservation) -> None:
        self._seen_concepts |= evidence_concepts(obs)

    def _record(self, obs: TurnObservation, agent: str, status: str, reason: str, latency_ms: Optional[float] = None,
                detail: str = "") -> None:
        self.records.append(DecisionRecord(
            session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version, decision="agent_call",
            proposer=agent, proposed=agent, status=status, reason_code=reason, detail=detail[:200],
            latency_ms=latency_ms,
        ))

    def _message(self, obs: TurnObservation, sender: str, recipient: str, kind: str,
                 payload: Dict[str, Any], confidence: Optional[float] = None) -> None:
        self.messages.append(AgentMessage(
            session_id=obs.session_id, turn_id=obs.turn_id, sender=sender, recipient=recipient,
            message_type=kind, state_version=obs.state_version, confidence=confidence, payload=payload,
            provenance={"coordinator": COORDINATOR},
        ))

    # ---------------------------------------------------------------- one validated agent call
    async def _call(self, name: str, model: type, obs: TurnObservation, peer: Any = None):
        agent = self._agents.get(name)
        if agent is None:
            self._record(obs, name, "rejected", "unavailable")
            return None
        breaker = self._breakers[name]
        if not breaker.allow():
            self._record(obs, name, "rejected", "breaker_open")
            return None
        key = (name, obs.state_version)
        if key in self._answered:
            self._record(obs, name, "rejected", "duplicate")
            return None
        self._answered.add(key)
        self.call_counts[name] += 1
        self._message(obs, COORDINATOR, name, "observation", {"turn_id": obs.turn_id, "score": obs.score})

        t0 = time.perf_counter()
        try:
            async def run():
                fn = agent.propose
                kwargs = {"peer": peer} if "peer" in inspect.signature(fn).parameters else {}
                if inspect.iscoroutinefunction(fn):
                    return await fn(obs, **kwargs)
                return await asyncio.to_thread(fn, obs, **kwargs)

            raw = await asyncio.wait_for(run(), timeout=self.timeout_s)
        except asyncio.TimeoutError:
            breaker.record_failure()
            self._record(obs, name, "rejected", "timeout", (time.perf_counter() - t0) * 1000)
            return None
        except Exception as exc:                     # agent crash
            breaker.record_failure()
            self._record(obs, name, "rejected", "crash", (time.perf_counter() - t0) * 1000, repr(exc))
            return None
        latency = (time.perf_counter() - t0) * 1000

        raw_dict = raw.model_dump() if isinstance(raw, model) else raw
        if self.enforce_authority and isinstance(raw_dict, (dict, list)):
            bad = authority_violation(raw_dict)
            if bad is not None:
                breaker.record_failure()
                self._record(obs, name, "rejected", "authority_violation", latency, f"forbidden key {bad!r}")
                return None
        try:
            proposal = raw if isinstance(raw, model) else model.model_validate(raw)
        except (ValidationError, TypeError, ValueError) as exc:
            breaker.record_failure()
            self._record(obs, name, "rejected", "schema_violation", latency, str(exc).splitlines()[0] if str(exc) else "")
            return None
        if proposal.state_version != obs.state_version or proposal.turn_id != obs.turn_id \
                or proposal.session_id != obs.session_id or obs.state_version != self.current_version:
            breaker.record_failure()
            self._record(obs, name, "rejected", "stale_state", latency,
                         f"proposal v{proposal.state_version} obs v{obs.state_version} current v{self.current_version}")
            return None
        breaker.record_success()
        self._record(obs, name, "accepted", "valid", latency)
        self._message(obs, name, COORDINATOR, "proposal", proposal.model_dump(mode="json"), proposal.confidence)
        return proposal

    # ---------------------------------------------------------------- public decisions
    async def strategy_proposal(self, obs: TurnObservation) -> Optional[StrategyProposal]:
        self.note_evidence(obs)
        return await self._call(STRATEGY, StrategyProposal, obs)

    def decide_difficulty(
        self, obs: TurnObservation, base_action: str, base_source: str,
        strategy: Optional[StrategyProposal], guardrail_fn: Optional[GuardrailFn],
    ) -> DifficultyDecision:
        if not self.use_arbitration:
            # Ablation: no arbitration layer. A strategy proposal, if any, replaces the base action with no
            # confidence/evidence/bound checks and the guardrail layer is skipped.
            action = strategy.difficulty_action if strategy is not None else base_action
            from agents.multiagent.arbitration import apply_action
            dec = DifficultyDecision(action, apply_action(obs.difficulty, action),
                                     "strategy" if strategy is not None else base_source)
        else:
            dec = arbitrate_difficulty(obs, base_action, base_source, strategy, guardrail_fn, self.tau)
        self.records.extend(dec.records)
        return dec

    def decide_probe(self, obs: TurnObservation, hub_default_inject: bool,
                     strategy: Optional[StrategyProposal]) -> ProbeDecision:
        if not self.use_arbitration:
            concept = strategy.probe.concept if (strategy is not None and strategy.probe) else None
            dec = ProbeDecision(bool(concept) or hub_default_inject, concept,
                                "strategy" if concept else ("hub_default" if hub_default_inject else "none"))
        else:
            dec = arbitrate_probe(obs, hub_default_inject, strategy, self._seen_concepts, self.tau)
        self.records.extend(dec.records)
        return dec

    async def coaching_plan(self, obs: TurnObservation, strategy: Optional[StrategyProposal]) -> Optional[CoachingPlan]:
        peer = strategy if self.communication else None
        plan = await self._call(COACHING, CoachingPlan, obs, peer=peer)
        if plan is None:
            return None
        if self.enforce_grounding:
            reason = check_plan(plan, obs)
            if reason is not None:
                self.records.append(DecisionRecord(
                    session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version,
                    decision="coaching", proposer=COACHING, proposed=",".join(plan.emphasize), status="rejected",
                    reason_code=reason, detail="emphasised concept absent from evaluator evidence"))
                return None
        self.records.append(DecisionRecord(
            session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version, decision="coaching",
            proposer=COACHING, proposed=plan.depth, status="accepted", final=plan.depth, reason_code="validated_plan"))
        return plan

    # ---------------------------------------------------------------- trace
    def trace_jsonl(self) -> str:
        return "\n".join(json.dumps(r.model_dump(mode="json"), sort_keys=True) for r in self.records)
