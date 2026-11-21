"""
T-N10 — Question selection correctness (corrected scope).

NOTE: Phase 2 found that agents/question_selector/question_selector.py has no
FAISS/embedding dependency -- it is a rule-based nearest-difficulty + topic-
rotation selector, not semantic retrieval (the capstone report's architecture
diagram is wrong on this point; the repo's FAISS index is used only by the
evaluator for concept-coverage scoring, not for question selection). This
script tests the REAL mechanism: difficulty-match accuracy, topic rotation
fairness, and no-repeat enforcement across a simulated session.

Read-only against the real production code
(agents.question_selector.question_selector). No files modified.

Run: .venv/Scripts/python.exe testing_and_evaluation/ml_evaluation/T-N10_question_selector_correctness.py
"""
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import agents.question_selector.question_selector as qs  # noqa: E402


def main() -> int:
    failures = []

    # --- 1. Difficulty-match accuracy: nearest_difficulty should always return
    #        a value that is actually present in the question bank's difficulty set.
    available = qs.AVAILABLE_DIFFICULTIES
    print(f"Available discrete difficulty values in question bank: {available}")
    test_targets = [0.1, 0.25, 0.45, 0.55, 0.65, 0.75, 0.9, 1.5, -1.0]
    for t in test_targets:
        nd = qs.nearest_difficulty(t)
        ok = nd in available
        status = "OK" if ok else "FAIL"
        if not ok:
            failures.append(f"nearest_difficulty({t}) returned {nd}, not in available set")
        print(f"[{status}] nearest_difficulty({t}) -> {nd}")

    # --- 2. Topic-rotation / no-immediate-repeat / session-length correctness
    #        over a simulated 15-question session at a fixed difficulty.
    qs.reset_session_state()
    target_diff = qs.nearest_difficulty(0.5)
    selected = []
    topics_in_order = []
    for turn in range(15):
        q = qs.select_next_question(target_diff)
        if q is None:
            print(f"[INFO] select_next_question exhausted at turn {turn} (expected once topic/difficulty pool is depleted)")
            break
        selected.append(q["qid"])
        topics_in_order.append(q["topic"])
        qs.session_state["questions_asked"].add(q["qid"])
        qs.session_state["topic_count"][q["topic"]] += 1
        qs.session_state["previous_topic"] = q["topic"]

    print(f"\nSimulated session: {len(selected)} questions selected before exhaustion/15-cap")
    print(f"Topics in order: {topics_in_order}")

    # No duplicate question IDs within the session
    dup_check = len(selected) == len(set(selected))
    if not dup_check:
        failures.append(f"Duplicate qids selected within one session: {Counter(selected)}")
    print(f"[{'OK' if dup_check else 'FAIL'}] No question repeated within the simulated session")

    # No two consecutive turns use the same topic (per select_question_from_topic's
    # previous_topic exclusion in get_valid_topics)
    consecutive_repeats = [
        (i, topics_in_order[i]) for i in range(1, len(topics_in_order))
        if topics_in_order[i] == topics_in_order[i - 1]
    ]
    no_consec = len(consecutive_repeats) == 0
    if not no_consec:
        failures.append(f"Consecutive same-topic turns found: {consecutive_repeats}")
    print(f"[{'OK' if no_consec else 'FAIL'}] No consecutive same-topic turns (topic-rotation working)")

    # Topic distribution spread (informational, not a hard pass/fail -- just
    # confirms the rotation isn't pathologically skewed to one topic)
    topic_counts = Counter(topics_in_order)
    print(f"Topic distribution across the session: {dict(topic_counts)}")

    print()
    print(f"Failures: {len(failures)}")
    if failures:
        for f in failures:
            print(f"  - {f}")
        return 1
    print("Question selection: difficulty-match always valid, no duplicate questions, no consecutive-same-topic turns.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
