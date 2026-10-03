"""Glue between the unchanged InterviewOrchestrator hub and the agent layer.

The hub keeps every authoritative decision and write. This runtime (a) builds the immutable observation from hub state,
(b) collects validated proposals through the coordinator, (c) hands arbitration results back to the hub, and
(d) counts committed state transitions so stale proposals can be detected (state_version).
It exists only when `multiagent_enabled` is true; otherwise the hub never touches this package.
"""
from __future__ import annotations

import math
from typing import Any, Callable, Dict, Optional, Tuple

from pydantic import ValidationError

from agents.multiagent.arbitration import DifficultyDecision, GuardrailFn, ProbeDecision
from agents.multiagent.coaching_agent import CoachingAgent
from agents.multiagent.contracts import (
    COACHING, STRATEGY, CoachingPlan, DecisionRecord, StrategyProposal, TurnObservation,
)
from agents.multiagent.coordinator import AgentCoordinator
from agents.multiagent.strategy_agent import StrategyAgent

DEFAULTS: Dict[str, Any] = {
    "strategy": True, "coaching": True, "tau": 0.6, "timeout_s": 2.0,
    "arbitration": True, "grounding": True, "authority": True, "communication": True,
}


def _unit(v: Any, default: float = 0.0) -> float:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return default
    return min(1.0, max(0.0, f)) if math.isfinite(f) else default


def _strs(xs: Any) -> Tuple[str, ...]:
    if not isinstance(xs, (list, tuple)):
        return ()
    return tuple(str(x) for x in xs if str(x).strip())


class MultiAgentRuntime:
    def __init__(self, session_id: str, cfg: Optional[dict] = None):
        c = {**DEFAULTS, **(cfg or {})}
        overrides = c.get("agents") or {}
        self.session_id = session_id
        self.strategy_agent = overrides.get(STRATEGY, StrategyAgent() if c["strategy"] else None)
        self.coaching_agent = overrides.get(COACHING, CoachingAgent() if c["coaching"] else None)
        self.coordinator = AgentCoordinator(
            self.strategy_agent, self.coaching_agent, timeout_s=c["timeout_s"], tau=c["tau"],
            enforce_authority=c["authority"], enforce_grounding=c["grounding"],
            use_arbitration=c["arbitration"], communication=c["communication"],
        )
        self.version = 0
        self.coordinator.committed(0)
        self.pending: Optional[Tuple[int, Optional[StrategyProposal], TurnObservation]] = None

    # ------------------------------------------------------------------ observation
    def build_observation(self, state: dict, question: dict, eval_result: dict, score: float,
                          primary_budget: int, infrastructure_failure: bool = False) -> Optional[TurnObservation]:
        scores = [_unit(s) for s in state.get("scores", [])]
        conf = _unit(state.get("last_confidence_score", 0.5), 0.5)
        # Observations are taken just before the hub commits the turn, but decisions are made against the committed state.
        # The counters therefore carry the value the hub's _update_session_state will produce (same predicate, same rule).
        is_fu = bool(
            str(question.get("id", "")).startswith("fu_") or question.get("parent_question_id")
            or question.get("source") in {"qwen_followup", "non_llm_structured_recovery", "qwen_1.5b_llm"}
            or question.get("is_followup")
        )
        consec_post = int(state.get("consecutive_followups", 0)) + 1 if is_fu else 0
        main_post = int(state.get("main_questions_count", 0)) + (0 if is_fu else 1)
        try:
            return TurnObservation(
                session_id=self.session_id, turn_id=len(scores), state_version=self.version,
                question_id=str(question.get("id", "")), topic=str(question.get("topic", "")),
                difficulty=int(state.get("current_difficulty", 3)), score=_unit(score),
                covered_concepts=_strs(eval_result.get("correct_claims") or eval_result.get("covered_concepts")),
                missing_concepts=_strs(eval_result.get("missing_concepts")),
                incorrect_claims=_strs(eval_result.get("incorrect_claims")),
                weakest_gap=str(eval_result.get("weakest_gap", "") or ""),
                is_followup=is_fu,
                scores_history=tuple(scores), progress=_unit(state.get("progress", 0.0)),
                confidence=conf, hesitation=max(0.0, 1.0 - conf),
                primary_remaining=max(0, primary_budget - main_post),
                consecutive_followups=consec_post,
                baseline_complete=bool(state.get("baseline_complete", True)),
                infrastructure_failure=infrastructure_failure,
            )
        except (ValidationError, TypeError, ValueError) as exc:
            self.coordinator.records.append(DecisionRecord(
                session_id=self.session_id, turn_id=len(scores), state_version=self.version, decision="agent_call",
                proposer="coordinator", proposed="observation", status="rejected",
                reason_code="invalid_observation", detail=str(exc).splitlines()[0][:200]))
            return None

    # ------------------------------------------------------------------ per turn
    async def collect(self, obs: Optional[TurnObservation], *, coach: bool) -> Optional[CoachingPlan]:
        """Gather the Strategy proposal (kept for the later difficulty/follow-up decisions) and, for verbal turns, a coaching plan."""
        self.pending = None
        if obs is None:
            return None
        strat = await self.coordinator.strategy_proposal(obs) if self.strategy_agent is not None else None
        self.pending = (obs.turn_id, strat, obs)
        if coach and self.coaching_agent is not None:
            return await self.coordinator.coaching_plan(obs, strat)
        return None

    def commit(self) -> None:
        """The hub committed a turn to authoritative state: advance the version proposals must match."""
        self.version += 1
        self.coordinator.committed(self.version)

    def _pending_for(self, n_scores: int) -> Optional[Tuple[Optional[StrategyProposal], TurnObservation]]:
        if self.pending is not None and self.pending[0] == n_scores - 1:
            return self.pending[1], self.pending[2]
        return None

    def difficulty(self, n_scores: int, base_action: str, base_source: str, guardrail_fn: Optional[GuardrailFn]
                   ) -> Optional[DifficultyDecision]:
        p = self._pending_for(n_scores)
        if p is None:
            return None
        strat, obs = p
        obs = obs.model_copy(update={"ppo_action": base_action if base_source == "ppo" else None,
                                     "ppo_available": base_source == "ppo"})
        return self.coordinator.decide_difficulty(obs, base_action, base_source, strat, guardrail_fn)

    def probe(self, n_scores: int, hub_default_inject: bool) -> Optional[ProbeDecision]:
        p = self._pending_for(n_scores)
        if p is None:
            return None
        strat, obs = p
        return self.coordinator.decide_probe(obs, hub_default_inject, strat)

    # ------------------------------------------------------------------ recovery / reporting
    def export_state(self) -> dict:
        return {
            "version": self.version,
            "strategy": self.strategy_agent.export_state() if hasattr(self.strategy_agent, "export_state") else None,
            "coaching": self.coaching_agent.export_state() if hasattr(self.coaching_agent, "export_state") else None,
            "telemetry": self.coordinator.export_telemetry(),
        }

    def import_state(self, st: dict) -> None:
        self.version = int(st.get("version", 0))
        self.coordinator.committed(self.version)
        if st.get("strategy") and hasattr(self.strategy_agent, "import_state"):
            self.strategy_agent.import_state(st["strategy"])
        if st.get("coaching") and hasattr(self.coaching_agent, "import_state"):
            self.coaching_agent.import_state(st["coaching"])
        if isinstance(st.get("telemetry"), dict):                  # absent in snapshots written before this field existed
            self.coordinator.import_telemetry(st["telemetry"])

    def summary(self) -> dict:
        recs = self.coordinator.records
        by: Dict[str, int] = {}
        for r in recs:
            k = f"{r.decision}:{r.proposer}:{r.status}:{r.reason_code}"
            by[k] = by.get(k, 0) + 1
        return {"agent_calls": dict(self.coordinator.call_counts), "records": len(recs), "by_outcome": by}
