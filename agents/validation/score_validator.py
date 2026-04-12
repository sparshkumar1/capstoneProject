from dataclasses import dataclass


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

    def validate(self, raw_score: float, evidence: dict, is_coding: bool) -> dict:
        score = float(raw_score)
        trace = []

        mandatory_pass = bool(evidence.get("mandatory_pass", True))
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

        mistake_penalty = float(evidence.get("mistake_penalty", 0.0))
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
            status = str(evidence.get("execution_status", "")).lower()
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

        return {
            "validated_score": round(float(clamped), 4),
            "raw_score": round(float(raw_score), 4),
            "validation_trace": trace,
        }
