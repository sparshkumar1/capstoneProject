"""Deterministic grounding check for coaching plans (a validator, not an agent).

A plan may only emphasise concepts that occur in the evaluator's evidence for this turn. This is a set-membership
test on normalised strings. It does NOT verify that generated feedback *text* is faithful; the Qwen-side lexical
check (`services/qwen/app.py::_validate_feedback_output`) is separate and equally limited.
"""
from __future__ import annotations

from typing import Optional, Set, Tuple

from agents.multiagent.contracts import CoachingPlan, TurnObservation


def normalize_concept(s: str) -> str:
    return " ".join(str(s).lower().split())


def evidence_concepts(obs: TurnObservation) -> Set[str]:
    return {normalize_concept(c) for c in (*obs.covered_concepts, *obs.missing_concepts, *obs.incorrect_claims) if str(c).strip()}


def ungrounded_concepts(plan: CoachingPlan, obs: TurnObservation) -> Tuple[str, ...]:
    ev = evidence_concepts(obs)
    return tuple(c for c in plan.emphasize if normalize_concept(c) not in ev)


def check_plan(plan: CoachingPlan, obs: TurnObservation) -> Optional[str]:
    """Return a reason code if the plan is not grounded, else None."""
    if ungrounded_concepts(plan, obs):
        return "ungrounded_concept"
    return None
