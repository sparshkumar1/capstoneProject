"""
Integration test: real evaluator output -> real feedback validator.

Each of these two components was independently fixed and unit-tested in
isolation this pass (services/evaluator/app.py::evaluate for the
misconception/repetition defects; services/qwen/app.py::_validate_feedback_output
for the incorrect_claims contradiction check). Neither unit test suite
verifies that the evaluator's ACTUAL return shape, once a real misconception
is detected, correctly drives the feedback validator's rejection path --
that requires composing the two real functions together, which is what this
file does. This directly answers item 5 of the Third Research Improvement
Pass ("whether feedback and follow-up generation remain aligned with the
latest evaluator evidence"), using the real production functions on both
sides, not a shadow copy of either.
"""
import pytest

from services.evaluator.app import evaluate, get_rubric, _ensure_evaluator_assets_loaded
from services.qwen.app import _validate_feedback_output, FeedbackRequest


@pytest.fixture(scope="module", autouse=True)
def load_assets():
    _ensure_evaluator_assets_loaded()


def test_real_evaluator_incorrect_claim_is_rejected_if_feedback_echoes_it_as_correct():
    """End-to-end: run the real evaluator on a genuinely wrong answer,
    confirm it flags something in incorrect_claims, then confirm the real
    feedback validator rejects a (simulated LLM) feedback response that
    echoes that exact flagged claim back as correct."""
    rubric = get_rubric("1")
    qn = "Explain your logic to find the two indices in an array that sum up to a target value."
    wrong_ans = (
        "I will run two nested loops i and j from 0 to n. "
        "For every pair, if array[i] + array[j] equals target, I return the values array[i] and array[j]. "
        "This is the most optimal way."
    )

    eval_result = evaluate(qn, wrong_ans, rubric)
    assert len(eval_result["incorrect_claims"]) > 0, "This case is expected to trigger a real detected misconception"
    flagged_claim = eval_result["incorrect_claims"][0]

    req = FeedbackRequest(
        question_text=qn,
        topic="Arrays",
        candidate_answer=wrong_ans,
        structured_evaluation={
            "final_score": eval_result["final_score"],
            "grade": eval_result["grade"],
            "correct_claims": eval_result["correct_claims"],
            "missing_concepts": eval_result["missing_concepts"],
            "incorrect_claims": eval_result["incorrect_claims"],
        },
    )
    # Simulated LLM output that would (wrongly) echo the flagged misconception as correct.
    bad_feedback = {
        "what_candidate_said": "The candidate described a nested-loop approach.",
        "what_was_correct": [flagged_claim],
        "what_was_incorrect": [],
        "what_was_incomplete": [],
        "missing_concepts": eval_result["missing_concepts"],
        "how_to_answer": "A hash map would achieve this in a single O(n) pass instead of nested loops.",
        "narrative_feedback": "Good use of a systematic approach to compare every pair of elements in the array.",
    }
    assert _validate_feedback_output(bad_feedback, req) is False


def test_real_evaluator_correct_answer_feedback_passes_validation():
    """Control: a real evaluator run on a genuinely correct answer, paired
    with well-formed, grounded feedback that does not contradict any
    evaluator evidence, must pass validation -- confirming the integration
    doesn't reject good-faith accurate feedback."""
    rubric = get_rubric("1")
    qn = "Explain your logic to find the two indices in an array that sum up to a target value."
    correct_ans = (
        "To find the two indices that sum to a target value in an array, I will use a hash map to achieve an O(n) single pass solution. "
        "As I iterate through the array, for each element, I calculate the complement as target minus the current element. "
        "I check if this complement is already present in the hash map in O(1) constant time lookup. "
        "If the complement exists, I return the index stored in the hash map along with the current index."
    )

    eval_result = evaluate(qn, correct_ans, rubric)
    assert eval_result["final_score"] >= 0.60

    req = FeedbackRequest(
        question_text=qn,
        topic="Arrays",
        candidate_answer=correct_ans,
        structured_evaluation={
            "final_score": eval_result["final_score"],
            "grade": eval_result["grade"],
            "correct_claims": eval_result["correct_claims"],
            "missing_concepts": eval_result["missing_concepts"],
            "incorrect_claims": eval_result["incorrect_claims"],
        },
    )
    good_feedback = {
        "what_candidate_said": "The candidate described using a hash map with a complement lookup in a single pass.",
        "what_was_correct": eval_result["correct_claims"][:2] or ["Correct single-pass hash map approach"],
        "what_was_incorrect": [],
        "what_was_incomplete": [],
        "missing_concepts": eval_result["missing_concepts"],
        "how_to_answer": "This is already the optimal O(n) time, O(n) space approach using a hash map for complement lookups.",
        "narrative_feedback": "This response correctly identifies the hash-map-based single-pass approach and its O(n) time complexity, matching the expected solution.",
    }
    assert _validate_feedback_output(good_feedback, req) is True
