"""
PrepAIred — Adversarial Logical-Reasoning Test Set for the Evaluator (V3 pass)
================================================================================
Item 3.1 of the Third Research Improvement Pass: a focused adversarial set of
technical answers that use CORRECT terminology and a fluent, plausible
narrative structure, but describe a technically WRONG mechanism or draw a
backwards conclusion. These are not nonsensical/off-topic answers (already
covered by test_evaluator.py's test_off_topic_answer); they are specifically
constructed to probe whether the evaluator distinguishes genuine logical
correctness from surface-level fluency and vocabulary match.

Diagnosis (see PPO/evaluator investigation reports for the full account):
two independent probes both point to the same root cause -- the evaluator's
embedding-based components (SBERT semantic/concept matching AND the
cross-encoder) are sensitive to topical/lexical overlap but not reliably to
logical POLARITY (negation, causal direction, comparison direction):
  1. A sentence-level cross-encoder re-scoring experiment found WRONG
     answers' sentences scoring HIGHER against the reference than a CORRECT
     answer's sentences -- backwards, and not usable as a fix.
  2. Adding rubric text describing "using the same speed instead of
     different speeds is wrong" scored 0.759 cosine similarity against a
     CORRECT answer that describes using different speeds -- a severe false
     positive that was found by this test file's regression run and
     reverted from services/evaluator/assets/rubrics.json before being kept.

This file documents actual current behavior (some cases correctly penalized,
others not) as a CHARACTERIZATION suite, not a pass/fail assertion that the
evaluator is fully robust -- several of these tests currently assert on the
KNOWN-LIMITED behavior, explicitly labeled as such, so a future genuine fix
is expected to change these numbers (in the correct direction) rather than
break silently-wrong assumptions.
"""
import pytest
from services.evaluator.app import evaluate, get_rubric, _ensure_evaluator_assets_loaded


@pytest.fixture(scope="module", autouse=True)
def load_assets():
    _ensure_evaluator_assets_loaded()


TWO_SUM_QN = "Explain your logic to find the two indices in an array that sum up to a target value."
FLOYD_QN = "Explain Floyd's Cycle-Finding algorithm to detect a loop in a linked list."


# ─────────────────────────────────────────────────────────────────────────────
# Plausible-but-wrong reasoning, correct terminology
# ─────────────────────────────────────────────────────────────────────────────
def test_nonsensical_degenerate_mechanism_is_undercaught_known_limitation():
    """KNOWN LIMITATION, documented not silently accepted: a fluent
    description of a degenerate, always-wrong mechanism (always returns the
    same single index) currently scores 'Good' territory. This is the
    cross-encoder's own limitation (item 3.1 diagnosis); not fixed in this
    pass because two attempted fixes (sentence-level re-scoring, rubric-text
    extension) were each found to be either ineffective or unsafe (see
    module docstring). This test pins current behavior so a future fix's
    effect is measurable, and documents it as unfixed, not overlooked."""
    rubric = get_rubric("1")
    ans = (
        "I will use a hash map and compute the complement as target minus the current element to achieve O(n) time. "
        "I insert every element into the hash map first before doing any lookups, then afterward I search the hash map "
        "for the complement of the target and element, so I always find both indices pointing at the same single element "
        "and never look at any other index."
    )
    result = evaluate(TWO_SUM_QN, ans, rubric)
    assert result["final_score"] >= 0.55  # documents the current (undesirable) leniency
    assert result["grade"] in ("Good", "Average")


def test_inverted_complexity_claim_is_now_penalized():
    """A previously-fixed defect (second execution pass): claiming hash-map
    lookups are O(n) and therefore slower than O(1) nested loops -- a
    real, inverted-complexity misconception using correct vocabulary --
    must receive a nonzero penalty via the high-concept-coverage/
    weak-reasoning tier."""
    rubric = get_rubric("1")
    ans = (
        "Using a hash map for complement lookups here is a bad idea because "
        "hash map lookups are O(n) time, much slower than the O(1) time of "
        "nested loops, so nested loops are the better approach."
    )
    result = evaluate(TWO_SUM_QN, ans, rubric)
    assert result["penalty"] > 0.0


def test_same_speed_pointers_is_undercaught_known_limitation():
    """KNOWN LIMITATION: claiming both pointers move at the SAME speed (which
    can never detect a cycle by 'meeting', since their relative distance
    never changes) currently receives zero penalty and a 'Good' grade. A
    targeted rubric-text fix for this exact case was attempted and reverted
    after it was found to score 0.759 cosine similarity against a genuinely
    CORRECT different-speed answer -- an unacceptable false-positive rate,
    not shipped. Documented as unfixed, with the false-positive risk that
    blocked the obvious fix recorded here for anyone attempting it again."""
    rubric = get_rubric("4")
    ans = (
        "We use two pointers that both move one step at a time through the linked list at the same speed. "
        "Because they move together at identical speed, if there is a cycle they will eventually meet at the same node, "
        "which tells us a loop exists. This runs in O(1) space."
    )
    result = evaluate(FLOYD_QN, ans, rubric)
    assert result["penalty"] == 0.0  # pins the known-limited current behavior
    assert result["grade"] == "Good"


def test_backwards_null_conclusion_receives_some_penalty():
    """Claiming the fast pointer reaching null 'proves' a cycle exists (the
    exact opposite of the true termination condition) already receives a
    partial penalty from the pre-existing null-check mistake-vector entry,
    which is topically close enough to fire without the reverted new
    entries. Not fully caught (final score is 'Average', not 'Poor'), but
    measurably better than zero penalty."""
    rubric = get_rubric("4")
    ans = (
        "We advance a slow pointer one node at a time and a fast pointer two nodes at a time. "
        "If the fast pointer reaches null, this proves conclusively that a cycle exists in the list."
    )
    result = evaluate(FLOYD_QN, ans, rubric)
    assert result["penalty"] > 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Control: the same fixes must not penalize genuinely correct, differently-worded answers
# ─────────────────────────────────────────────────────────────────────────────
def test_correct_different_speed_explanation_is_not_penalized():
    """This is deliberately the same brief (not thorough) correct answer as
    test_evaluator.py::test_correct_answer_weak_explanation, which already
    establishes "Good" or "Average" (not "Poor") as the expected band for a
    terse-but-correct answer; the check that actually matters here is that
    no mistake penalty fires."""
    rubric = get_rubric("4")
    ans = "We use two pointers, a slow pointer moving one step and a fast pointer moving two steps; if they meet, there is a cycle."
    result = evaluate(FLOYD_QN, ans, rubric)
    assert result["penalty"] == 0.0
    assert result["grade"] in ("Good", "Average")


def test_correct_null_termination_explanation_is_not_penalized():
    rubric = get_rubric("4")
    ans = (
        "We advance a slow pointer one node at a time and a fast pointer two nodes at a time. "
        "If the fast pointer reaches null, there is no cycle in the list, since a cycle would cause it to loop forever instead."
    )
    result = evaluate(FLOYD_QN, ans, rubric)
    assert result["grade"] in ("Good", "Excellent")


# ─────────────────────────────────────────────────────────────────────────────
# Mistake-vector overflow-detection fix (services/evaluator/app.py)
# ─────────────────────────────────────────────────────────────────────────────
def test_mistake_penalty_checks_rubric_text_beyond_faiss_vector_count():
    """Direct regression test for the fixed defect: mistake_penalty() and
    _detect_misconceptions() previously only ever checked the FAISS-indexed
    'mistake' vectors for a question, silently ignoring any
    common_mistakes_addressed rubric-text entry added after the FAISS index
    was built (a real, demonstrated gap: qid=1's rubric has 4 text entries
    but only 3 indexed vectors). This constructs a rubric with more mistake
    texts than vectors and confirms the overflow entries are reachable."""
    from services.evaluator.app import mistake_penalty, _detect_misconceptions

    rubric = get_rubric("1")
    assert len(rubric["common_mistakes_addressed"]) == 4  # 3 original + 1 added this pass
    ans = (
        "I will use a hash map to store elements. Returning or reusing the same array index for both "
        "required positions is exactly what I do here, since it is simpler to just report one index twice."
    )
    incorrect = _detect_misconceptions(ans, rubric)
    assert any("distinct positions" in c for c in incorrect)
