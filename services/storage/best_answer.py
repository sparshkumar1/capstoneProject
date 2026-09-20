"""Authoritative best-answer eligibility and selection (pure functions, no I/O).

An attempt may be the authoritative best answer for a question ONLY when the existing authoritative technical
evaluation classifies it as correct or partially correct. Recency, raw score alone, feedback text, language or
confidence signals, Qwen output and retry order can never make an incorrect attempt eligible.

Classification reuses the repository's existing authoritative semantics; no new threshold is introduced:

* Code attempts: the sandbox verdict recorded with the attempt (`status` from
  FeedbackAgent.generate_code_feedback, or the orchestrator's `passed` / `tests_passed`): accepted/passed =
  correct; any other verdict (fails closed: timeout, runtime_error, memory_limit, policy_blocked, ...) is
  partial only if the sandbox reports at least one passed test, otherwise incorrect. The score is consulted
  only when no verdict at all was recorded.
* Verbal attempts: the evaluator's validated technical score (`validated_score`, i.e. `final_score` of
  services/evaluator/app.py evaluate() after the score validator) against the evaluator's own grade
  boundaries: >= 0.60 (grade Good/Excellent) -> correct, >= 0.40 (grade Average) -> partial, below 0.40
  (grade Poor) -> incorrect. An unavailable evaluator or STT failure is recorded with score 0.0 and is therefore
  incorrect (nothing is fabricated).

Among eligible attempts the pre-existing deterministic ranking is unchanged:
highest validated_score, then fewest missing concepts, then most recent attempt_number.
"""

from __future__ import annotations

import json
import math
from typing import Any, Dict, Iterable, Optional

CORRECT = "correct"
PARTIAL = "partial"
INCORRECT = "incorrect"
ELIGIBLE_LABELS = frozenset({CORRECT, PARTIAL})

# Mirrors the grade boundaries in services/evaluator/app.py evaluate() (Good >= 0.60, Average >= 0.40).
VERBAL_CORRECT_FLOOR = 0.60
VERBAL_PARTIAL_FLOOR = 0.40


def _as_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
        except ValueError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _score(value: Any) -> Optional[float]:
    try:
        s = float(value)
    except (TypeError, ValueError):
        return None
    return s if math.isfinite(s) else None


def classify_attempt(attempt: Dict[str, Any]) -> str:
    """Return 'correct', 'partial' or 'incorrect' from the attempt's authoritative evaluation fields."""
    fb = _as_dict(attempt.get("feedback_json"))
    if str(attempt.get("answer_type", "verbal")).lower() == "code":
        status = str(fb.get("status", "")).strip().lower()
        passed_flag = fb.get("passed")
        # An explicit sandbox verdict is authoritative and fails closed: any verdict other than `accepted`
        # (wrong_answer, compilation_error, runtime_error, timeout, memory_limit, policy_blocked,
        # sandbox_error, or an unknown one) is a failed execution and can never fall through to the score.
        if status == "accepted" or (not status and passed_flag is True):
            return CORRECT
        if status or passed_flag is False:
            tests = fb.get("tests_passed", _as_dict(fb.get("score_breakdown")).get("tests_passed"))
            n = _score(tests)
            return PARTIAL if n is not None and n > 0 else INCORRECT
        # no sandbox verdict recorded at all: fall through to the score boundaries
    score = _score(attempt.get("validated_score"))
    if score is None:
        return INCORRECT
    if score >= VERBAL_CORRECT_FLOOR:
        return CORRECT
    if score >= VERBAL_PARTIAL_FLOOR:
        return PARTIAL
    return INCORRECT


def is_eligible(attempt: Dict[str, Any]) -> bool:
    return classify_attempt(attempt) in ELIGIBLE_LABELS


def _missing_count(attempt: Dict[str, Any]) -> int:
    m = attempt.get("missing_concepts")
    if isinstance(m, str):
        try:
            m = json.loads(m or "[]")
        except ValueError:
            m = []
    return len(m) if isinstance(m, (list, tuple)) else 0


def ranking_key(attempt: Dict[str, Any]):
    """Pre-existing deterministic ranking (unchanged): score, fewest missing concepts, most recent attempt."""
    return (float(_score(attempt.get("validated_score")) or 0.0), -_missing_count(attempt),
            int(attempt.get("attempt_number", 0)))


def select_best(attempts: Iterable[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """The authoritative best attempt, or None when no attempt is eligible. Follow-up attempts are excluded."""
    pool = [a for a in attempts
            if str(a.get("attempt_type", "primary")).lower() == "primary" and is_eligible(a)]
    return max(pool, key=ranking_key) if pool else None
