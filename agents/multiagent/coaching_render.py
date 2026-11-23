"""Render a validated CoachingPlan onto the existing feedback dict.

Only additive presentation fields and presentation lists may change. Evaluator results, scores and evidence lists are
protected: if any of them differs after rendering the function raises (authority enforcement at the point of effect)
and the caller's feedback dict is left exactly as it was.
"""
from __future__ import annotations

import copy
from typing import Any, Dict

from agents.multiagent.contracts import CoachingPlan

PROTECTED_KEYS = (
    "final_score", "grade", "score_breakdown", "covered_concepts", "missing_concepts", "what_was_correct",
    "what_was_incorrect", "what_was_incomplete", "incorrect_claims", "transcript", "decision_source", "llm_status",
)
_PRESENTATION_LISTS = ("actionable_improvements", "how_to_improve", "communication_tips", "vague_points")
_NOTES = {
    "encouraging": "Progress takes repetition; focus on one concept at a time.",
    "neutral": "",
}


def apply_coaching_plan(feedback: Dict[str, Any], plan: CoachingPlan, topic: str = "") -> Dict[str, Any]:
    """Render onto a deep copy, validate the protected fields, and only then commit the result into `feedback` in place.

    On success `feedback` (the same object, which callers rely on) is updated and returned; on failure it is left untouched.
    """
    original = feedback
    feedback = copy.deepcopy(original)
    lead = plan.emphasize[0] if plan.emphasize else None

    if lead:
        prio = f"Priority: cover {lead}"
        for key in ("actionable_improvements", "how_to_improve"):
            cur = list(feedback.get(key) or [])
            if not any(lead.lower() in str(x).lower() for x in cur[:1]):
                feedback[key] = [prio] + [x for x in cur if prio not in str(x)]

    if plan.depth == "brief":
        for key in _PRESENTATION_LISTS:
            if isinstance(feedback.get(key), list):
                feedback[key] = feedback[key][:1]
    elif plan.depth == "detailed":
        extra = [f"Review: {c}" for c in (feedback.get("missing_concepts") or [])[:3]]
        if extra:
            feedback["coaching_detail"] = extra

    if plan.give_hint and lead:
        feedback["coaching_hint"] = f"Hint: think about {lead} and how it relates to the question."
    if plan.give_example:
        try:
            from agents.orchestrator.feedback_agent import _TOPIC_STRUCTURE_TIPS
            tip = _TOPIC_STRUCTURE_TIPS.get(topic)
        except Exception:
            tip = None
        if tip:
            feedback["coaching_example"] = tip
    if plan.remediation:
        feedback["coaching_remediation"] = plan.remediation
    note = _NOTES.get(plan.tone, "")
    if note:
        feedback["coaching_note"] = note
    feedback["coaching_plan"] = plan.model_dump(mode="json")

    if any(feedback.get(k) != original.get(k) for k in PROTECTED_KEYS):
        raise RuntimeError("coaching render modified protected evaluator fields")
    original.update(feedback)
    return original
