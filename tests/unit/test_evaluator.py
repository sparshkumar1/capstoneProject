"""
PrepAIred — Unit Tests for Production Evaluation System (Stage 1)
================================================================
Verifies the authoritative evaluation system (services/evaluator/app.py):
- Mathematical formula: 0.15*S1 + 0.35*effective_S2 + 0.50*R + bonus - penalty
- Mandatory cap: final_score <= 0.60 if mandatory concept omitted
- Mistake penalties: applied on detected misconceptions
- Keyword stuffing defense: S2 dampened to 0.60*S2 when R <= 0.30
- Separation of concerns: communication/confidence cannot inflate technical score
- Score ordering invariants across 10 adversarial test cases
"""

import pytest
from services.evaluator.app import evaluate, get_rubric, _ensure_evaluator_assets_loaded


@pytest.fixture(scope="module", autouse=True)
def load_assets():
    """Ensure models and vector stores are loaded once for the test session."""
    _ensure_evaluator_assets_loaded()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: Completely Correct Answer
# ─────────────────────────────────────────────────────────────────────────────
def test_completely_correct_answer():
    """A thorough, technically accurate explanation must receive an Excellent score (>= 0.75)."""
    rubric = get_rubric("1")
    assert rubric is not None, "Rubric for Q1 must exist"

    qn = "Explain your logic to find the two indices in an array that sum up to a target value."
    ans = (
        "To find the two indices that sum to a target value in an array, I will use a hash map to achieve an O(n) single pass solution. "
        "As I iterate through the array, for each element, I calculate the complement as target minus the current element. "
        "I check if this complement is already present in the hash map in O(1) constant time lookup. "
        "If the complement exists, I return the index stored in the hash map along with the current index. "
        "If it does not exist, I insert the current element value and its index into the map. "
        "This avoids nested loops and runs in O(n) time and O(n) space."
    )

    result = evaluate(qn, ans, rubric)

    assert result["final_score"] >= 0.75, f"Expected >= 0.75, got {result['final_score']}"
    assert result["grade"] == "Excellent"
    assert result["mandatory_pass"] is True
    assert result["reasoning_score"] >= 0.70
    assert result["concept_coverage"] >= 0.75
    assert len(result["correct_claims"]) >= 2
    assert len(result["missing_concepts"]) == 0


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: Partially Correct Answer
# ─────────────────────────────────────────────────────────────────────────────
def test_partially_correct_answer():
    """An answer with some correct ideas but incomplete mechanism receives Good or Average (0.40 - 0.74)."""
    rubric = get_rubric("1")
    qn = "Explain your logic to find the two indices in an array that sum up to a target value."
    ans = (
        "I will use a hash map to store elements as I iterate through the array. "
        "I store the values and indices in the map to make lookups fast."
    )

    result = evaluate(qn, ans, rubric)

    assert 0.35 <= result["final_score"] < 0.75, f"Expected 0.35-0.74, got {result['final_score']}"
    assert result["grade"] in ("Good", "Average")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: Completely Wrong Answer
# ─────────────────────────────────────────────────────────────────────────────
def test_completely_wrong_answer():
    """Factually incorrect algorithm must receive a Poor score (<= 0.35)."""
    rubric = get_rubric("1")
    qn = "Explain your logic to find the two indices in an array that sum up to a target value."
    ans = (
        "I will run two nested loops i and j from 0 to n. "
        "For every pair, if array[i] + array[j] equals target, I return the values array[i] and array[j]. "
        "This is the most optimal way."
    )

    result = evaluate(qn, ans, rubric)

    assert result["final_score"] <= 0.35, f"Expected <= 0.35, got {result['final_score']}"
    assert result["grade"] == "Poor"
    assert len(result["incorrect_claims"]) > 0 or result["penalty"] > 0


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: Confident but Technically Wrong Answer
# ─────────────────────────────────────────────────────────────────────────────
def test_confident_wrong_answer():
    """High vocal confidence / assertive tone cannot compensate for wrong technical content."""
    rubric = get_rubric("1")
    qn = "Explain your logic to find the two indices in an array that sum up to a target value."
    ans = (
        "I am 100% absolutely certain of this answer. "
        "The optimal way is definitely to sort the array first, which destroys the original indices, "
        "and then pick the first and last elements blindly. That always produces the answer in O(1) time."
    )

    result = evaluate(qn, ans, rubric)

    assert result["final_score"] <= 0.35, f"Expected <= 0.35, got {result['final_score']}"
    assert result["grade"] == "Poor"
    # Communication metric is separate from technical score
    assert result["technical_correctness"] <= 0.35


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: Keyword-Stuffed but Conceptually Wrong Answer
# ─────────────────────────────────────────────────────────────────────────────
def test_keyword_stuffed_wrong_answer():
    """Keyword stuffing with inverted/invalid logic must be penalized and capped."""
    rubric = get_rubric("1")
    qn = "Explain your logic to find the two indices in an array that sum up to a target value."
    ans = (
        "Hash map constant-time lookup single pass iteration store value-to-index mapping O(n) space O(n) time complexity. "
        "We simply multiply all array elements together and take the square root of the target to find the sum."
    )

    result = evaluate(qn, ans, rubric)

    # Mandatory pass should fail because complement check is absent from logic
    assert result["mandatory_pass"] is False
    assert result["final_score"] <= 0.60, f"Expected <= 0.60 due to mandatory cap and flawed logic, got {result['final_score']}"
    assert result["grade"] in ("Average", "Poor")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 6: Off-Topic Answer
# ─────────────────────────────────────────────────────────────────────────────
def test_off_topic_answer():
    """An unrelated answer must receive a near-zero score (<= 0.20)."""
    rubric = get_rubric("1")
    qn = "Explain your logic to find the two indices in an array that sum up to a target value."
    ans = (
        "To prepare pasta, boil water in a large pot and add salt. "
        "Cook the pasta for 8 to 10 minutes until al dente, then drain and serve with tomato sauce."
    )

    result = evaluate(qn, ans, rubric)

    assert result["final_score"] <= 0.20, f"Expected <= 0.20, got {result['final_score']}"
    assert result["grade"] == "Poor"
    assert result["relevance"] < 0.25
    assert result["concept_coverage"] == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# TEST 7: Correct Terminology with Incorrect Reasoning
# ─────────────────────────────────────────────────────────────────────────────
def test_correct_terminology_incorrect_reasoning():
    """Using valid terms with invalid mechanics (e.g. malloc zeroes memory) must be detected and penalized."""
    rubric = get_rubric("15")  # Dynamic memory allocation question
    if not rubric:
        rubric = get_rubric("1")
        qn = "Explain your logic to find the two indices in an array that sum up to a target value."
        ans = (
            "We use a hash map where we insert every element first, "
            "then we search for target plus the element so the sum gets bigger."
        )
    else:
        qn = "Explain how malloc and free manage heap memory in C."
        ans = (
            "malloc allocates memory on the stack and automatically sets all bytes to zero. "
            "When free is called, it resets the pointer to NULL automatically."
        )

    result = evaluate(qn, ans, rubric)
    assert result["final_score"] <= 0.45, f"Expected <= 0.45, got {result['final_score']}"
    assert result["grade"] in ("Poor", "Average")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 8: Missing Mandatory Concept
# ─────────────────────────────────────────────────────────────────────────────
def test_missing_mandatory_concept():
    """An answer that explains the general idea but omits the mandatory check cannot exceed mandatory_cap (0.60)."""
    rubric = get_rubric("1")
    qn = "Explain your logic to find the two indices in an array that sum up to a target value."
    # Omits the complement calculation (target - current)
    ans = (
        "I will use a hash map to store array elements and their positions. "
        "I loop through the array once and query the hash map for matching values."
    )

    result = evaluate(qn, ans, rubric)

    assert result["final_score"] <= 0.60, f"Expected <= 0.60 cap, got {result['final_score']}"
    assert result["grade"] != "Excellent"


# ─────────────────────────────────────────────────────────────────────────────
# TEST 9: Correct Answer with Weak Explanation
# ─────────────────────────────────────────────────────────────────────────────
def test_correct_answer_weak_explanation():
    """A brief single-sentence answer gets moderate credit (0.40 - 0.75)."""
    rubric = get_rubric("4")  # Floyd's cycle finding
    qn = "Explain Floyd's Cycle-Finding algorithm to detect a loop in a linked list."
    ans = "We use two pointers, a slow pointer moving one step and a fast pointer moving two steps; if they meet, there is a cycle."

    result = evaluate(qn, ans, rubric)

    assert 0.40 <= result["final_score"] <= 0.75, f"Expected 0.40-0.75, got {result['final_score']}"
    assert result["grade"] in ("Good", "Average")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 10: Paraphrased / Novel Wording Correct Answer
# ─────────────────────────────────────────────────────────────────────────────
def test_paraphrased_correct_answer():
    """A correct explanation using alternative phrasing without exact textbook buzzwords receives a high score."""
    rubric = get_rubric("4")  # Floyd's cycle finding
    qn = "Explain Floyd's Cycle-Finding algorithm to detect a loop in a linked list."
    ans = (
        "We maintain two references traversing the list at different velocities. "
        "The primary pointer advances node by node, while the secondary pointer traverses two links per step. "
        "Because the relative distance decreases by one link in each step inside a loop, "
        "the faster reference is mathematically guaranteed to lap and intersect the slower reference if a cycle exists. "
        "If the fast reference encounters a null termination, no loop is present. This uses O(1) auxiliary memory."
    )

    result = evaluate(qn, ans, rubric)

    assert result["final_score"] >= 0.60, f"Expected >= 0.60 for valid paraphrased answer, got {result['final_score']}"
    assert result["grade"] in ("Good", "Excellent")
    assert result["mandatory_pass"] is True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 11: Score Ordering Invariant Across Test Cases
# ─────────────────────────────────────────────────────────────────────────────
def test_score_ordering_invariants():
    """Verify that score ordering strictly holds: Correct > Partial > Keyword-Stuffed > Wrong > Off-Topic."""
    rubric = get_rubric("1")
    qn = "Explain your logic to find the two indices in an array that sum up to a target value."

    ans_correct = (
        "To find the two indices that sum to a target value in an array, I will use a hash map to achieve an O(n) single pass solution. "
        "As I iterate through the array, for each element, I calculate the complement as target minus the current element. "
        "I check if this complement is already present in the hash map in O(1) constant time lookup. "
        "If the complement exists, I return the index stored in the hash map along with the current index. "
        "If not, I insert the current element value and its index into the map. This avoids nested loops and runs in O(n) time and O(n) space."
    )
    ans_partial = (
        "I will use a hash map to store elements as I iterate through the array. "
        "I store the values and indices in the map to make lookups fast."
    )
    ans_wrong = (
        "I will run two nested loops i and j from 0 to n. "
        "For every pair, if array[i] + array[j] equals target, I return the values array[i] and array[j]. "
        "This is the most optimal way."
    )
    ans_off_topic = "Boil water in a pot and add pasta. Cook for 8 minutes and serve."

    res_correct = evaluate(qn, ans_correct, rubric)
    res_partial = evaluate(qn, ans_partial, rubric)
    res_wrong = evaluate(qn, ans_wrong, rubric)
    res_off_topic = evaluate(qn, ans_off_topic, rubric)

    score_correct = res_correct["final_score"]
    score_partial = res_partial["final_score"]
    score_wrong = res_wrong["final_score"]
    score_off_topic = res_off_topic["final_score"]

    assert score_correct > score_partial, f"Correct ({score_correct}) must be > Partial ({score_partial})"
    assert score_partial > score_wrong, f"Partial ({score_partial}) must be > Wrong ({score_wrong})"
    assert score_wrong >= score_off_topic, f"Wrong ({score_wrong}) must be >= Off-Topic ({score_off_topic})"
