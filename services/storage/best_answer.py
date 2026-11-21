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
    """Coerce a value to a dict, parsing it as JSON first if it's a string.

    Args:
        value (Any): A dict, a JSON-encoded string, or anything else.

    Returns:
        Dict[str, Any]: `value` itself if already a dict, the parsed object
            if `value` is a JSON string encoding a dict, or `{}` otherwise
            (including parse failures and non-dict JSON values).
    """
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
    """Coerce a value to a finite float, or None if that's not possible.

    Args:
        value (Any): Value to convert.

    Returns:
        Optional[float]: The finite float value, or None if `value` isn't
            numeric or is NaN/infinite.
    """
    try:
        s = float(value)
    except (TypeError, ValueError):
        return None
    return s if math.isfinite(s) else None


def classify_attempt(attempt: Dict[str, Any]) -> str:
    """Classify one attempt as correct, partial, or incorrect using authoritative evaluation fields.

    For code attempts, an explicit sandbox verdict in `feedback_json`
    (`status`/`passed`) is authoritative and fails closed — any verdict
    other than "accepted" is at best partial (only if at least one test
    passed), never correct; the validated score is consulted only when no
    sandbox verdict was recorded at all. For verbal attempts (or code
    attempts with no verdict), classification follows the evaluator's own
    grade boundaries on `validated_score`.

    Args:
        attempt (Dict[str, Any]): One attempt record, with `answer_type`,
            `feedback_json` (dict or JSON string), and `validated_score`.

    Returns:
        str: One of `CORRECT`, `PARTIAL`, `INCORRECT`.
    """
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
    """Check whether an attempt is eligible to be the authoritative best answer.

    Args:
        attempt (Dict[str, Any]): One attempt record (see
            `classify_attempt`).

    Returns:
        bool: True if `classify_attempt(attempt)` is `CORRECT` or
            `PARTIAL`.
    """
    return classify_attempt(attempt) in ELIGIBLE_LABELS


def _missing_count(attempt: Dict[str, Any]) -> int:
    """Count the missing concepts recorded for an attempt.

    Args:
        attempt (Dict[str, Any]): One attempt record; its
            `missing_concepts` field may be a list or a JSON-encoded list
            string.

    Returns:
        int: Number of missing concepts, or 0 if the field is absent,
            unparseable, or not a list/tuple.
    """
    m = attempt.get("missing_concepts")
    if isinstance(m, str):
        try:
            m = json.loads(m or "[]")
        except ValueError:
            m = []
    return len(m) if isinstance(m, (list, tuple)) else 0


def ranking_key(attempt: Dict[str, Any]):
    """Build a sort key for ranking attempts: highest score, fewest missing concepts, most recent.

    Args:
        attempt (Dict[str, Any]): One attempt record.

    Returns:
        tuple: `(validated_score, -missing_concept_count, attempt_number)`,
            suitable for `max()`/`sorted()` (higher score wins first, then
            fewer missing concepts, then the later attempt).
    """
    return (float(_score(attempt.get("validated_score")) or 0.0), -_missing_count(attempt),
            int(attempt.get("attempt_number", 0)))


def select_best(attempts: Iterable[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Select the authoritative best primary attempt among a question's attempts.

    Args:
        attempts (Iterable[Dict[str, Any]]): All attempts for a question;
            follow-up attempts (`attempt_type != "primary"`) are excluded
            before ranking.

    Returns:
        Optional[Dict[str, Any]]: The eligible primary attempt with the
            highest `ranking_key`, or None if no primary attempt is
            eligible (see `is_eligible`).
    """
    pool = [a for a in attempts
            if str(a.get("attempt_type", "primary")).lower() == "primary" and is_eligible(a)]
    return max(pool, key=ranking_key) if pool else None
