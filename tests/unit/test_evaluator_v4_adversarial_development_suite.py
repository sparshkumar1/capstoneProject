"""
PrepAIred — Evaluator V4 Adversarial Development Suite
========================================================
Fourth Research Improvement Pass, item 3.2. This is a DEVELOPMENT-ONLY suite,
explicitly separate from:
  - the 64-case human-gold benchmark (research/data/evaluator_benchmark/),
    which must never be tuned against;
  - the third pass's 7-case adversarial set
    (test_evaluator_logical_reasoning_adversarial.py), which this suite
    extends with different failure-mode categories rather than duplicating;
  - any confirmatory or held-out data.

Ten cases, each covering one of the failure-mode categories item 3.2 names.
Every case documents: the failure mode under test, the relevant scoring
component, expected behavior, and why the case is diagnostically useful.
Several cases document CURRENT behavior as a positive finding (no defect);
one (case 9) documents an already-known, already-disclosed limitation
(rubric mistake-text collision) rather than re-deriving it as new. No fix
in this file was accepted without first checking it against this whole
suite plus the human-gold benchmark (see EVALUATOR_V4_VALIDATION.md).
"""
import pytest
from services.evaluator.app import evaluate, get_rubric, _ensure_evaluator_assets_loaded


@pytest.fixture(scope="module", autouse=True)
def load_assets():
    _ensure_evaluator_assets_loaded()


TWO_SUM_QN = "Explain your logic to find the two indices in an array that sum up to a target value."
FLOYD_QN = "Explain Floyd's Cycle-Finding algorithm to detect a loop in a linked list."
KADANE_QN = "Explain Kadane's algorithm for maximum subarray sum."
BSEARCH_QN = "Explain how binary search finds a target in a sorted array."


# ─────────────────────────────────────────────────────────────────────────────
# Case 1 — Correct terminology with incorrect reasoning
# Failure mode: fluent vocabulary masking a broken mechanism
# Component: S2 (concept coverage) vs reasoning_score (cross-encoder)
# Expected: penalized or capped low; diagnostic for whether concept-matching
#   alone can be gamed by vocabulary without actual correctness
# ─────────────────────────────────────────────────────────────────────────────
def test_case1_correct_terminology_incorrect_reasoning():
    rubric = get_rubric("1")
    ans = (
        "I will use a hash map and compute the complement as target minus the current element to achieve O(n) time. "
        "I insert every element into the hash map first before doing any lookups, then afterward I search the hash map "
        "for the complement of the target and element, so I always find both indices pointing at the same single element "
        "and never look at any other index."
    )
    result = evaluate(TWO_SUM_QN, ans, rubric)
    # KNOWN LIMITATION (unchanged from the third pass): still scores "Good"
    # territory. Pinned, not silently accepted -- see EVALUATOR_V4_VALIDATION.md.
    assert result["grade"] in ("Good", "Average")


# ─────────────────────────────────────────────────────────────────────────────
# Case 2 — Correct conclusion supported by invalid reasoning
# Failure mode: does the evaluator verify the MECHANISM, or just check
#   whether the final stated complexity/conclusion matches?
# Component: concept_detection (S2) primarily
# Expected: low score despite the correct O(log n) conclusion, because the
#   described mechanism (discard only the middle element, scan the rest
#   one at a time) is actually linear, not the real binary-search halving
# ─────────────────────────────────────────────────────────────────────────────
def test_case2_correct_conclusion_invalid_reasoning():
    rubric = get_rubric("6")
    ans = (
        "We check the middle element, and if it does not match, we throw away only the middle element and keep "
        "searching the rest of the array one element at a time, which still gives us O(log n) time since we are "
        "being efficient about it."
    )
    result = evaluate(BSEARCH_QN, ans, rubric)
    # Diagnostically useful finding: this IS correctly caught (Poor), but via
    # concept-coverage collapse (the described non-halving mechanism doesn't
    # match the "halves the search space" concept vector), not via explicit
    # verification that the claimed complexity follows from the description.
    assert result["grade"] == "Poor"
    assert result["concept_coverage"] == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Case 3 — Incorrect complexity analysis (correct mechanism, wrong Big-O)
# Failure mode: does the penalty logic catch a wrong complexity CLAIM when
#   the described mechanism itself is otherwise correct?
# Component: mistake_penalty's high-S2/weak-R tier (fixed in the second pass)
# Expected: nonzero penalty; grade below what the correct mechanism alone
#   would earn
# ─────────────────────────────────────────────────────────────────────────────
def test_case3_incorrect_complexity_analysis():
    rubric = get_rubric("2")
    ans = (
        "We maintain current_sum and max_sum. At each element, current_sum becomes the max of the element alone or "
        "current_sum plus the element, and we update max_sum if current_sum is bigger. Since we compare against every "
        "previous subarray ending at each position, this takes O(n^2) time overall."
    )
    result = evaluate(KADANE_QN, ans, rubric)
    assert result["penalty"] > 0.0
    assert result["grade"] in ("Poor", "Average")


# ─────────────────────────────────────────────────────────────────────────────
# Case 4 — Contradictory statements (self-contradiction within one answer)
# Failure mode: does the evaluator notice when an answer asserts two
#   mutually exclusive things about the same variable?
# Component: reasoning_score (cross-encoder) + mistake_penalty
# Expected: penalized; low reasoning_score since no single coherent
#   interpretation of the answer matches the reference mechanism
# ─────────────────────────────────────────────────────────────────────────────
def test_case4_contradictory_statements():
    rubric = get_rubric("2")
    ans = (
        "current_sum resets to zero after every single element regardless of its value. "
        "current_sum also accumulates the running total across the whole array without ever resetting. "
        "max_sum tracks the largest current_sum seen."
    )
    result = evaluate(KADANE_QN, ans, rubric)
    assert result["penalty"] > 0.0
    assert result["grade"] == "Poor"


# ─────────────────────────────────────────────────────────────────────────────
# Case 5 — Correct answer containing irrelevant but convincing jargon
# Failure mode: does impressive-sounding but irrelevant technical language
#   (amortized analysis, cache locality, load-factor resizing -- none of
#   which the rubric asks about) inflate the score of an answer whose CORE
#   mechanism is genuinely correct?
# Component: S1 (semantic score), bonus_score
# Expected: scores well (the core mechanism IS correct) but not artificially
#   inflated to "Excellent" purely by the jargon padding
# ─────────────────────────────────────────────────────────────────────────────
def test_case5_correct_answer_with_irrelevant_jargon():
    rubric = get_rubric("1")
    ans = (
        "Leveraging amortized O(1) hash map insertions and exploiting cache locality for iteration, I compute the "
        "complement as target minus the current element and check the hash map, which stores value-to-index mappings, "
        "before inserting. This achieves O(n) time with favorable constant factors due to load-factor-aware resizing."
    )
    result = evaluate(TWO_SUM_QN, ans, rubric)
    # Positive finding: correct core mechanism scores "Good", not artificially
    # pushed to "Excellent" by jargon, and not penalized for the padding either.
    assert result["grade"] in ("Good", "Excellent")
    assert result["penalty"] == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Case 6 — Incorrect answer with high semantic similarity to the reference
# Failure mode: heavy vocabulary overlap (mid, left/right-adjacent framing,
#   "sorted") describing an actually-linear scan, not real binary search
# Component: S2 (concept_detection) vs superficial lexical overlap
# Expected: low score despite heavy vocabulary overlap with the reference
# ─────────────────────────────────────────────────────────────────────────────
def test_case6_near_miss_high_similarity_wrong_answer():
    rubric = get_rubric("6")
    ans = (
        "Given a sorted array, we scan from the left pointer to the right pointer, checking array[mid] at each "
        "position against the target as we go one index at a time, continuing until we find the target or reach "
        "the right pointer, giving O(log n) time."
    )
    result = evaluate(BSEARCH_QN, ans, rubric)
    assert result["grade"] == "Poor"


# ─────────────────────────────────────────────────────────────────────────────
# Case 7 — Correct answer using alternative terminology (synonym substitution
#   at the CONCEPT level: "low/high" instead of "left/right", not just
#   different sentence structure)
# Failure mode: distinct from the third pass's paraphrase-stability test,
#   which varied sentence structure but kept the same core vocabulary; this
#   varies the VOCABULARY itself for an equivalent concept
# Component: concept_detection (S2) -- threshold-based matching against
#   concept vectors that may be anchored to specific reference terminology
# Expected / actual finding: this IS a real, disclosed sensitivity -- concept
#   coverage lands at only 0.500 for a fully mechanically-correct answer,
#   pulling the grade down to "Average" rather than "Good"/"Excellent"
# ─────────────────────────────────────────────────────────────────────────────
def test_case7_alternative_terminology_correct_answer():
    rubric = get_rubric("6")
    ans = (
        "Assuming the array is sorted, we track a low bound and a high bound. We repeatedly examine the midpoint "
        "between them; if it matches the target we are done, if the target is bigger we move the low bound past the "
        "midpoint, and if smaller we move the high bound before the midpoint. This continues until the bounds cross, "
        "halving the candidate range every time for O(log n) time."
    )
    result = evaluate(BSEARCH_QN, ans, rubric)
    # Documents the actual (not ideal) current behavior: a real, disclosed
    # vocabulary-level paraphrase sensitivity, distinct from and additional to
    # the sentence-structure-level paraphrase robustness already validated in
    # test_evaluator.py::test_paraphrase_stability_across_multiple_wordings.
    assert result["penalty"] == 0.0  # not penalized, just under-credited on concept coverage
    assert result["concept_coverage"] <= 0.60


# ─────────────────────────────────────────────────────────────────────────────
# Case 8 — Repeated content without additional information (generalization
#   check for the dedup fix on a question it was never tested against)
# Failure mode: verbatim repetition inflating reasoning_score
# Component: dedupe_repeated_sentences (fixed in the second pass)
# Expected: identical score whether the content is stated once or twice
# ─────────────────────────────────────────────────────────────────────────────
def test_case8_repetition_dedup_generalizes_to_new_question():
    rubric = get_rubric("2")
    ans = (
        "current_sum is updated to the max of the element itself or current_sum plus the element, and we update "
        "max_sum whenever current_sum exceeds it, giving O(n) time."
    )
    once = evaluate(KADANE_QN, ans, rubric)
    twice = evaluate(KADANE_QN, ans + " " + ans, rubric)
    assert once["final_score"] == twice["final_score"]


# ─────────────────────────────────────────────────────────────────────────────
# Case 9 — Rubric mistake-text collision with a valid answer
# Failure mode: a mistake-vector description sharing vocabulary with the
#   concept it describes can false-positive-match a genuinely correct answer
#   using that same vocabulary (this is a KNOWN, ALREADY-DOCUMENTED and
#   ALREADY-REVERTED case from the third pass -- re-asserted here as a
#   permanent regression guard, not re-discovered)
# Component: mistake_penalty (rubric-text overflow path)
# Expected: a correct answer must never be penalized by a mistake-text entry
#   that happens to share its vocabulary
# ─────────────────────────────────────────────────────────────────────────────
def test_case9_rubric_mistake_text_does_not_collide_with_valid_answer():
    rubric = get_rubric("4")
    ans = "We use two pointers, a slow pointer moving one step and a fast pointer moving two steps; if they meet, there is a cycle."
    result = evaluate(FLOYD_QN, ans, rubric)
    assert result["penalty"] == 0.0
    assert result["grade"] in ("Good", "Average")


# ─────────────────────────────────────────────────────────────────────────────
# Case 10 — Partial answer that should receive partial (not full, not zero)
#   credit
# Failure mode: does an incomplete-but-not-wrong answer get appropriately
#   differentiated, or does it get swept into the same penalty tier as a
#   genuinely contradictory one?
# Component: effective_S2 dampening + the high-S2/weak-R penalty tier
# Expected / actual finding: lands at "Average" (0.43), which is directionally
#   reasonable for partial credit, but the high-S2/weak-R penalty tier (fixed
#   in the second pass specifically to catch misconceptions) also fires here
#   (0.080 penalty) even though this answer is merely incomplete, not wrong --
#   a real, disclosed side effect worth flagging for anyone revisiting that
#   fix, not a new defect introduced in this pass
# ─────────────────────────────────────────────────────────────────────────────
def test_case10_partial_answer_gets_differentiated_partial_credit():
    rubric = get_rubric("6")
    ans = (
        "The array must be sorted. We look at the middle element and compare it to the target to decide which half "
        "to search next, repeating until found."
    )
    result = evaluate(BSEARCH_QN, ans, rubric)
    assert 0.20 < result["final_score"] < 0.75  # neither zero-credit nor full-credit
    assert result["grade"] in ("Average", "Good")
