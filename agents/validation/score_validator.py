from dataclasses import dataclass
from typing import Any, Optional


DEFAULT_THEORY_WEIGHTS = {
    "semantic": 0.45,
    "conceptual": 0.55,
    "coding": 0.0,
}

DEFAULT_CODING_WEIGHTS = {
    "semantic": 0.25,
    "conceptual": 0.35,
    "coding": 0.40,
}


def aggregate_scores(
    semantic_score: float,
    conceptual_score: float,
    coding_score: float | None,
    is_coding: bool,
    theory_weights: dict | None = None,
    coding_weights: dict | None = None,
) -> dict:
    tw = theory_weights or DEFAULT_THEORY_WEIGHTS
    cw = coding_weights or DEFAULT_CODING_WEIGHTS

    semantic = float(max(min(semantic_score, 1.0), 0.0))
    conceptual = float(max(min(conceptual_score, 1.0), 0.0))
    coding = None if coding_score is None else float(max(min(coding_score, 1.0), 0.0))

    if is_coding:
        coding = 0.0 if coding is None else coding
        raw = (
            cw["semantic"] * semantic
            + cw["conceptual"] * conceptual
            + cw["coding"] * coding
        )
        active_weights = cw
    else:
        raw = tw["semantic"] * semantic + tw["conceptual"] * conceptual
        active_weights = tw

    return {
        "raw_score": round(float(max(min(raw, 1.0), 0.0)), 4),
        "semantic_score": semantic,
        "conceptual_score": conceptual,
        "coding_score": coding,
        "active_weights": active_weights,
    }


@dataclass
class ScoreValidator:
    mandatory_cap: float = 0.65
    max_mistake_penalty: float = 0.25
    coding_failure_multiplier: float = 0.7

    def validate(self, raw_score: Any, evidence: Optional[dict] = None, is_coding: bool = False) -> dict:
        import math
        trace = []

        # 1. Structural / Type Validation
        try:
            if raw_score is None:
                score = 0.0
                trace.append({"rule": "missing_score", "before": None, "after": 0.0, "reason": "Raw score was None"})
            else:
                score = float(raw_score)
        except (ValueError, TypeError):
            score = 0.0
            trace.append({"rule": "type_error", "before": str(raw_score), "after": 0.0, "reason": "Non-numeric raw score converted to 0.0"})

        # 2. Non-finite Numeric Handling
        if math.isnan(score) or math.isinf(score):
            trace.append({"rule": "non_finite_score", "before": str(score), "after": 0.0, "reason": "NaN or Inf score replaced with 0.0"})
            score = 0.0

        # 3. Evidence Schema Validation
        if isinstance(evidence, dict):
            ev = evidence
        else:
            ev = {}
            if evidence is not None:
                trace.append({"rule": "malformed_evidence", "reason": f"Expected dict evidence, got {type(evidence).__name__}"})

        raw_numeric = score

        mandatory_pass = bool(ev.get("mandatory_pass", True))
        if not mandatory_pass and score > self.mandatory_cap:
            trace.append(
                {
                    "rule": "mandatory_cap",
                    "before": round(score, 4),
                    "after": self.mandatory_cap,
                    "reason": "Mandatory logic not fully covered",
                }
            )
            score = self.mandatory_cap

        mistake_penalty = float(ev.get("mistake_penalty", 0.0))
        penalty_applied = min(max(mistake_penalty, 0.0), self.max_mistake_penalty)
        if penalty_applied > 0:
            before = score
            score -= penalty_applied
            trace.append(
                {
                    "rule": "mistake_penalty",
                    "before": round(before, 4),
                    "after": round(score, 4),
                    "reason": f"Penalty from detected mistake patterns ({penalty_applied:.3f})",
                }
            )

        if is_coding:
            status = str(ev.get("execution_status", "")).lower()
            if status in {"policy_blocked", "runtime_error", "timeout", "failed"}:
                before = score
                score *= self.coding_failure_multiplier
                trace.append(
                    {
                        "rule": "coding_execution_penalty",
                        "before": round(before, 4),
                        "after": round(score, 4),
                        "reason": f"Coding execution status was '{status}'",
                    }
                )

        clamped = max(min(score, 1.0), 0.0)
        if clamped != score:
            trace.append(
                {
                    "rule": "clamp_0_1",
                    "before": round(score, 4),
                    "after": round(clamped, 4),
                    "reason": "Final score clamped to [0, 1]",
                }
            )

        # Determine explicit evaluation_status and infrastructure failure flag
        if isinstance(evidence, dict) and "evaluation_status" in evidence:
            eval_status = str(evidence["evaluation_status"]).lower()
            is_infra_failure = eval_status in {"unavailable", "evaluator_unavailable", "malformed", "timeout", "error"}
        elif raw_score is None:
            eval_status = "unavailable"
            is_infra_failure = True
        elif isinstance(evidence, dict) and evidence.get("decision_source") in {"evaluator_unavailable", "stt_failure_handler"}:
            eval_status = "unavailable"
            is_infra_failure = True
        else:
            eval_status = "success"
            is_infra_failure = False

        return {
            "validated_score": round(float(clamped), 4),
            "raw_score": round(float(raw_numeric), 4),
            "evaluation_status": eval_status,
            "is_infrastructure_failure": is_infra_failure,
            "validation_trace": trace,
        }
