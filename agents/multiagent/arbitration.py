"""Deterministic arbitration of proposals. No learned or LLM component lives here.

Difficulty precedence (documented in research/multiagent/ARCHITECTURE_ASSESSMENT.md, evaluated by ablation, not assumed optimal):
  1. hard session constraints (infrastructure failure, bounds [1, 5])        - absolute
  2. guardrail rule layer, applied last to the selected candidate            - wins whenever a rule fires
  3. validated Strategy proposal (confidence >= tau, evidence present)       - wins over the PPO/heuristic action
  4. PPO action, or the labelled non-RL heuristic when PPO is unavailable
Probe precedence: hard follow-up cap > validated Strategy probe (grounded concept, confidence >= tau) > hub default policy.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Set, Tuple

from agents.multiagent.grounding import normalize_concept
from agents.multiagent.contracts import (
    ARBITRATOR, GUARDRAIL, PPO, STRATEGY, DecisionRecord, StrategyProposal, TurnObservation,
)

GuardrailFn = Callable[[str], Tuple[str, Optional[str]]]   # candidate action -> (final action, rule id or None)

FOLLOWUP_HARD_CAP = 2


def apply_action(level: int, action: str) -> int:
    if action == "Easier":
        return max(1, level - 1)
    if action == "Harder":
        return min(5, level + 1)
    return level


@dataclass
class DifficultyDecision:
    final_action: str
    new_level: int
    candidate_source: str                 # "strategy" | "ppo" | "heuristic" | "hard_constraint"
    guardrail_rule: Optional[str] = None
    conflict: bool = False                # strategy proposal differed from the base action and was considered
    records: List[DecisionRecord] = field(default_factory=list)


def _rec(obs: TurnObservation, proposer: str, proposed: str, status: str, reason: str,
         final: str = "", detail: str = "") -> DecisionRecord:
    return DecisionRecord(
        session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version, decision="difficulty",
        proposer=proposer, proposed=proposed, status=status, final=final, reason_code=reason, detail=detail,
    )


def arbitrate_difficulty(
    obs: TurnObservation,
    base_action: str,
    base_source: str,
    strategy: Optional[StrategyProposal],
    guardrail_fn: Optional[GuardrailFn],
    tau: float,
) -> DifficultyDecision:
    level = obs.difficulty
    records: List[DecisionRecord] = []

    # 1. hard constraint: an infrastructure failure never degrades or escalates difficulty
    if obs.infrastructure_failure:
        records.append(_rec(obs, ARBITRATOR, "Same", "accepted", "hard_infrastructure_failure", final="Same"))
        return DifficultyDecision("Same", level, "hard_constraint", None, False, records)

    candidate, source, conflict = base_action, base_source, False
    base_proposer = PPO if base_source == "ppo" else base_source

    # 3. Strategy proposal (already schema/authority/state-version validated by the coordinator)
    if strategy is not None:
        if strategy.confidence < tau:
            records.append(_rec(obs, STRATEGY, strategy.difficulty_action, "rejected", "low_confidence",
                                detail=f"{strategy.confidence:.2f} < tau {tau:.2f}"))
        elif not strategy.evidence:
            records.append(_rec(obs, STRATEGY, strategy.difficulty_action, "rejected", "no_evidence"))
        else:
            proposed = strategy.difficulty_action
            if apply_action(level, proposed) == level and proposed != "Same":
                records.append(_rec(obs, STRATEGY, proposed, "modified", "bound_clamp", final="Same",
                                    detail=f"level {level} cannot move {proposed}"))
                proposed = "Same"
            else:
                records.append(_rec(obs, STRATEGY, proposed, "accepted", "validated_proposal", final=proposed))
            if proposed != base_action:
                conflict = True
                records.append(_rec(obs, base_proposer, base_action, "rejected", "superseded_by_strategy",
                                    final=proposed))
            candidate, source = proposed, "strategy"

    # 2. guardrail layer, applied last to whatever candidate was selected
    rule = None
    final = candidate
    if guardrail_fn is not None:
        g_action, rule = guardrail_fn(candidate)
        if rule is not None:
            final = g_action
            status = "accepted" if g_action == candidate else "modified"
            records.append(_rec(obs, GUARDRAIL, g_action, status, f"guardrail:{rule}", final=g_action,
                                detail=f"candidate {candidate} from {source}"))
    if source != "strategy" and rule is None:
        records.append(_rec(obs, base_proposer, base_action, "accepted", "default_policy", final=final))

    return DifficultyDecision(final, apply_action(level, final), source, rule, conflict, records)


@dataclass
class ProbeDecision:
    inject: bool
    concept: Optional[str]
    source: str                      # "hub_default" | "strategy" | "none"
    records: List[DecisionRecord] = field(default_factory=list)


def arbitrate_probe(
    obs: TurnObservation,
    hub_default_inject: bool,
    strategy: Optional[StrategyProposal],
    seen_concepts: Set[str],
    tau: float,
) -> ProbeDecision:
    """Follow-up decision. The hub's existing threshold policy remains the default; the Strategy Agent may add a probe
    the thresholds would not trigger (proactive) or retarget one, but never beyond the hard cap."""
    def rec(status: str, reason: str, proposer: str, proposed: str, final: str = "", detail: str = "") -> DecisionRecord:
        return DecisionRecord(
            session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version, decision="probe",
            proposer=proposer, proposed=proposed, status=status, final=final, reason_code=reason, detail=detail,
        )

    records: List[DecisionRecord] = []
    if obs.consecutive_followups >= FOLLOWUP_HARD_CAP:
        if strategy is not None and strategy.probe is not None:
            records.append(rec("rejected", "hard_followup_cap", STRATEGY, strategy.probe.concept))
        return ProbeDecision(False, None, "none", records)

    probe = strategy.probe if strategy is not None else None
    if probe is not None:
        if strategy.confidence < tau:
            records.append(rec("rejected", "low_confidence", STRATEGY, probe.concept))
            probe = None
        elif normalize_concept(probe.concept) not in seen_concepts:
            records.append(rec("rejected", "ungrounded_concept", STRATEGY, probe.concept,
                               detail="concept never appeared in evaluator evidence this session"))
            probe = None

    if probe is not None:
        if hub_default_inject:
            records.append(rec("modified", "retargeted_default_probe", STRATEGY, probe.concept, final=probe.concept))
        else:
            records.append(rec("accepted", "proactive_probe", STRATEGY, probe.concept, final=probe.concept))
        return ProbeDecision(True, probe.concept, "strategy", records)

    if hub_default_inject:
        records.append(rec("accepted", "default_policy", "hub_default", "probe", final="probe"))
        return ProbeDecision(True, None, "hub_default", records)
    return ProbeDecision(False, None, "none", records)
