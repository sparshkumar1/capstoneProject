"""
Follow-up mechanism live-model behavioral probe (V2) -- expanded evidence-category
coverage, repeat-run variability check, and a rubric scaffold for manual read-and-rate.

Builds on followup_behavioral_probe_v1.py (5 cases, one per trigger category, which
surfaced and helped fix the TASK-line targeting defect in services/qwen/app.py).
This version responds to the explicit sixth-pass instruction not to limit the
evaluation to "another handful of easy, constructed examples": it expands from 5 to
12 cases spanning 8 evidence categories (misconception; missing concept; weakest-gap
variants for all three of its non-trivial production forms -- reasoning-depth,
mandatory-requirement-omitted, and the "Misconception: ..." format; below-threshold
score; conflicting/ambiguous evidence; sparse/incomplete evidence; non-redundancy
against a prior follow-up; and a strong-answer case verified to correctly SKIP the
LLM call entirely), plus a same-input repeat-run check on 2 cases to see whether the
low-temperature (0.1) sampling in services/qwen/app.py's GGUF path produces stable
or varying output.

What this script does NOT do, disclosed up front:
  - It does not add or claim a validated semantic-groundedness metric. No such
    instrument exists in this project (per every prior pass's disclosure). The
    keyword-overlap check inherited from V1 is retained as a coarse, transparent,
    one-directional sanity check (can under-detect grounding, cannot over-detect it).
  - "Subjective" rubric dimensions (technical correctness, specificity, answerability,
    non-redundancy, evidence grounding, target relevance) are NOT scored by this
    script. They require reading the actual generated text, which happens in a
    separate manual pass after this script runs (recorded in a companion file,
    explicitly labeled as a single, non-blinded read by the research agent that
    built the probe -- not an independent or expert rating).
  - The strong-answer "should skip" case does not call generate_followup() at all,
    because production does not call it in that situation either (the gate lives in
    InterviewOrchestrator._decide_and_inject_followup, not in the Qwen service). It
    is instead verified by re-applying the exact skip predicate read from
    agents/orchestrator/interview_orchestrator.py lines 1782-1784 at the time of
    writing, quoted in this file's SKIP_PREDICATE_SOURCE constant so the check
    cannot silently drift from what production actually does without the constant
    being visibly stale.

Usage: python followup_behavioral_probe_v2.py
"""
import asyncio
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

os.environ.setdefault("EVALUATOR_MOCK_MODE", "0")

from services.qwen.app import (  # noqa: E402
    ModelRegistry,
    MOCK_MODE,
    GGUF_MODEL_PATH,
    FollowupRequest,
    generate_followup,
)

OUT_DIR = Path(__file__).resolve().parent.parent / "results" / "followup_behavioral_probe_v2"
OUT_DIR.mkdir(parents=True, exist_ok=True)

_STOPWORDS = {
    "the", "a", "an", "is", "are", "of", "to", "and", "or", "in", "on", "for",
    "does", "do", "how", "what", "why", "explain", "describe", "can", "you",
    "your", "this", "that", "it", "its", "with", "when", "where", "which",
    "answer", "candidate", "question", "concept", "about", "not", "no",
}


def _content_words(text: str) -> set:
    return {w for w in re.findall(r"[a-zA-Z]+", text.lower()) if len(w) > 2 and w not in _STOPWORDS}


# Verbatim, as read from agents/orchestrator/interview_orchestrator.py lines 1777-1784
# at the time this script was written. If production logic changes, this constant
# will silently stop matching it -- flagged here so a future reader knows to re-check
# it rather than trusting the "SKIP" verdict below indefinitely.
SKIP_PREDICATE_SOURCE = (
    "score >= 0.85 and not missing and not incorrect and "
    "(not weakest_gap or 'None' in str(weakest_gap))"
)


def production_skip_predicate(score: float, missing: list, incorrect: list, weakest_gap: str) -> bool:
    return score >= 0.85 and not missing and not incorrect and (not weakest_gap or "None" in str(weakest_gap))


CASES = [
    {
        "case_id": "misconception",
        "category": "misconception",
        "req": FollowupRequest(
            original_question="Explain how a hash map achieves average O(1) lookup time.",
            topic="Data Structures",
            candidate_answer="A hash map is just an array where we search linearly through every "
                              "bucket for the key we want, so lookup is O(n) in every case, same as a list.",
            structured_evaluation={
                "final_score": 0.30, "grade": "Poor",
                "correct_claims": [],
                "missing_concepts": ["hash function", "average-case constant time"],
                "incorrect_claims": ["claims O(n) linear search is how hash maps look up keys"],
            },
            incorrect_concepts=["claims O(n) linear search is how hash maps look up keys"],
            misconceptions=["claims O(n) linear search is how hash maps look up keys"],
        ),
        "probe_target": "linear search misconception / O(1) average case",
        "repeat": True,
    },
    {
        "case_id": "missing_concept",
        "category": "missing_concept",
        "req": FollowupRequest(
            original_question="Describe how Breadth-First Search traverses a graph.",
            topic="Graph Algorithms",
            candidate_answer="BFS starts at a node, puts it in a queue, and repeatedly dequeues a node, "
                              "looks at its neighbors, and adds them to the queue, continuing until the "
                              "queue is empty.",
            structured_evaluation={
                "final_score": 0.60, "grade": "Good",
                "correct_claims": ["queue-based traversal", "processes neighbors level by level"],
                "missing_concepts": ["visited set to avoid revisiting/cycling nodes"],
                "incorrect_claims": [],
            },
            missing_concepts=["visited set to avoid revisiting/cycling nodes"],
        ),
        "probe_target": "visited set / cycle avoidance",
        "repeat": False,
    },
    {
        "case_id": "below_threshold_score",
        "category": "below_threshold",
        "req": FollowupRequest(
            original_question="Explain how recursion works and give an example of when to use it.",
            topic="Programming Fundamentals",
            candidate_answer="Recursion is when a function calls itself to solve a problem.",
            structured_evaluation={
                "final_score": 0.55, "grade": "Average",
                "correct_claims": ["a function calling itself"],
                "missing_concepts": ["base case", "call stack / stack frames"],
                "incorrect_claims": [],
            },
            missing_concepts=["base case", "call stack / stack frames"],
        ),
        "probe_target": "base case / stack frames (answer too shallow)",
        "repeat": False,
    },
    {
        "case_id": "weakest_gap_reasoning_depth",
        "category": "weakest_gap",
        "req": FollowupRequest(
            original_question="Explain how to reverse a singly linked list iteratively.",
            topic="Data Structures",
            candidate_answer="You walk through the list with a pointer, and for each node you flip its "
                              "next pointer to point backwards instead of forwards, until you reach the end, "
                              "then the last node becomes the new head.",
            structured_evaluation={
                "final_score": 0.72, "grade": "Good",
                "correct_claims": ["reversing next pointers", "new head is the old tail"],
                "missing_concepts": [],
                "incorrect_claims": [],
            },
            # Realistic short-phrase value, matching services/evaluator/app.py line 527
            # ("Reasoning depth and mechanistic explanation"), not a free-form sentence
            # (see V1's self-caught methodological correction on this exact field).
            weakest_gap="Reasoning depth and mechanistic explanation",
        ),
        "probe_target": "reasoning depth / mechanistic explanation",
        "repeat": True,
    },
    {
        "case_id": "weakest_gap_mandatory_omitted",
        "category": "weakest_gap",
        "req": FollowupRequest(
            original_question="What is the time and space complexity of merge sort, and why?",
            topic="Algorithms",
            candidate_answer="Merge sort splits the array in half repeatedly and merges the halves back "
                              "together in sorted order.",
            structured_evaluation={
                "final_score": 0.58, "grade": "Average",
                "correct_claims": ["divide-and-conquer splitting and merging"],
                "missing_concepts": [],
                "incorrect_claims": [],
                "mandatory_pass": False,
            },
            # Matches services/evaluator/app.py line 525's exact string, used when
            # missing_concepts is empty, incorrect_claims is empty, but a mandatory
            # rubric requirement was not met (e.g. the candidate never states the
            # actual complexity, only describes the mechanism).
            weakest_gap="Omitted mandatory requirement specified in rubric",
        ),
        "probe_target": "time complexity O(n log n) / space complexity O(n)",
        "repeat": False,
    },
    {
        "case_id": "weakest_gap_misconception_format",
        "category": "weakest_gap",
        "req": FollowupRequest(
            original_question="What is the difference between a process and a thread?",
            topic="Operating Systems",
            candidate_answer="Threads and processes are basically the same thing, just different names "
                              "for a running program; they both get their own separate memory space.",
            structured_evaluation={
                "final_score": 0.40, "grade": "Poor",
                "correct_claims": [],
                "missing_concepts": [],
                "incorrect_claims": ["claims threads have their own separate memory space like processes"],
            },
            incorrect_concepts=["claims threads have their own separate memory space like processes"],
            # Matches services/evaluator/app.py line 523's exact production format:
            # f"Misconception: {incorrect_claims[0]}" -- distinct from the
            # `misconceptions` list field tested by the "misconception" case above,
            # since here it arrives pre-formatted inside weakest_gap itself and
            # `misconceptions`/`incorrect_concepts` are populated too (as production
            # would, since both come from the same incorrect_claims source), but the
            # prompt-construction TASK-line priority (misconception > missing >
            # weakest-gap, per the V1 fix) means this case exercises the same code
            # path as "misconception" -- included to confirm the *format string*
            # itself (with the "Misconception: " prefix baked in) does not confuse
            # the model into echoing the prefix text back verbatim.
            weakest_gap="Misconception: claims threads have their own separate memory space like processes",
        ),
        "probe_target": "shared memory space / address space (threads vs processes)",
        "repeat": False,
    },
    {
        "case_id": "combined_missing_and_misconception",
        "category": "combined",
        "req": FollowupRequest(
            original_question="What is a race condition in multithreading and how do you prevent it?",
            topic="Concurrency",
            candidate_answer="A race condition happens when threads run in a random order. You can "
                              "prevent it by just making all your variables global so every thread can "
                              "see the latest value.",
            structured_evaluation={
                "final_score": 0.35, "grade": "Poor",
                "correct_claims": ["threads running in unsynchronized order"],
                "missing_concepts": ["mutual exclusion / locks", "critical section"],
                "incorrect_claims": ["claims making variables global prevents race conditions"],
            },
            missing_concepts=["mutual exclusion / locks", "critical section"],
            incorrect_concepts=["claims making variables global prevents race conditions"],
            misconceptions=["claims making variables global prevents race conditions"],
        ),
        "probe_target": "mutual exclusion/locking; global-variable misconception",
        "repeat": False,
    },
    {
        "case_id": "conflicting_evidence",
        "category": "conflicting_evidence",
        "req": FollowupRequest(
            # Deliberately constructed so the numeric score is mid-range but the
            # correct/incorrect claim lists pull in opposite directions -- a case
            # the evaluator's own scoring rules can produce (partial credit plus a
            # real misconception coexisting), not a synthetic contradiction outside
            # what services/evaluator/app.py can actually emit.
            original_question="Explain the difference between TCP and UDP.",
            topic="Networking",
            candidate_answer="TCP is connection-oriented and guarantees ordered, reliable delivery using "
                              "acknowledgements and retransmission. UDP is also reliable and guarantees "
                              "delivery, it's just faster because it skips the handshake.",
            structured_evaluation={
                "final_score": 0.50, "grade": "Average",
                "correct_claims": ["TCP is connection-oriented", "TCP uses acknowledgements/retransmission for reliability"],
                "missing_concepts": ["UDP is connectionless with no delivery guarantee"],
                "incorrect_claims": ["claims UDP guarantees reliable delivery"],
            },
            missing_concepts=["UDP is connectionless with no delivery guarantee"],
            incorrect_concepts=["claims UDP guarantees reliable delivery"],
            misconceptions=["claims UDP guarantees reliable delivery"],
        ),
        "probe_target": "UDP unreliability / no delivery guarantee",
        "repeat": False,
    },
    {
        "case_id": "ambiguous_partial_credit",
        "category": "ambiguous",
        "req": FollowupRequest(
            # Near the strong-answer skip boundary (0.80, just below 0.85) with a
            # single, narrow missing concept rather than a clear misconception --
            # meant to probe whether the follow-up stays narrowly targeted rather
            # than re-litigating the whole answer when the gap is small.
            original_question="What is the purpose of an index in a relational database?",
            topic="Databases",
            candidate_answer="An index speeds up lookups on a column by avoiding a full table scan, "
                              "similar to an index in a book. It does add some overhead.",
            structured_evaluation={
                "final_score": 0.80, "grade": "Good",
                "correct_claims": ["avoids full table scan", "speeds up lookups", "book-index analogy"],
                "missing_concepts": ["write-side overhead: index must be updated on insert/update/delete"],
                "incorrect_claims": [],
            },
            missing_concepts=["write-side overhead: index must be updated on insert/update/delete"],
        ),
        "probe_target": "write overhead on insert/update/delete",
        "repeat": False,
    },
    {
        "case_id": "sparse_incomplete_evidence",
        "category": "incomplete_evidence",
        "req": FollowupRequest(
            # Deliberately minimal structured_evaluation (only final_score, no
            # correct/incorrect/missing lists at all) -- simulates an evaluator
            # response that is thinner than the schema's happy path, to check the
            # prompt builder / model degrade gracefully rather than producing a
            # contradictory or vacuous follow-up.
            original_question="What is polymorphism in object-oriented programming?",
            topic="OOP",
            candidate_answer="Polymorphism lets objects of different classes be treated through a common "
                              "interface, so the same method call can behave differently depending on the "
                              "actual object type.",
            structured_evaluation={"final_score": 0.65, "grade": "Average"},
        ),
        "probe_target": "polymorphism example (override/runtime dispatch)",
        "repeat": False,
    },
    {
        "case_id": "non_redundancy_against_prior_followup",
        "category": "non_redundancy",
        "req": FollowupRequest(
            original_question="Explain how a binary search tree maintains sorted order.",
            topic="Data Structures",
            candidate_answer="Every node's left subtree contains smaller values and the right subtree "
                              "contains larger values, so an in-order traversal visits nodes in sorted order.",
            structured_evaluation={
                "final_score": 0.62, "grade": "Good",
                "correct_claims": ["left-smaller/right-larger invariant", "in-order traversal is sorted"],
                "missing_concepts": ["worst-case O(n) depth for an unbalanced tree"],
                "incorrect_claims": [],
            },
            missing_concepts=["worst-case O(n) depth for an unbalanced tree"],
            previous_questions=["Explain how a binary search tree maintains sorted order."],
            # A prior follow-up already asked about a DIFFERENT gap in this same
            # exchange, to check the new follow-up doesn't just re-ask it.
            previous_followups=["What happens to lookup time if the tree becomes unbalanced, "
                                 "for example if you insert already-sorted data?"],
        ),
        "probe_target": "worst-case O(n) depth / unbalanced tree",
        "repeat": False,
    },
]

# Not sent to generate_followup(): verified via the skip predicate instead, since
# production never calls generate_followup() for a strong answer in the first place.
STRONG_ANSWER_SKIP_CASE = {
    "case_id": "strong_answer_no_followup_expected",
    "category": "strong_answer_skip",
    "eval_result": {
        "final_score": 0.90,
        "missing_concepts": [],
        "incorrect_claims": [],
        "weakest_gap": "None — comprehensive answer",
    },
}


async def run_case(case: dict, repeat_index: int = 0) -> dict:
    req = case["req"]
    probe_target = case.get("probe_target", "")
    resp = await generate_followup(req)
    gen_words = _content_words(resp.followup)
    target_words = _content_words(probe_target)
    overlap = sorted(gen_words & target_words)
    orig_words = _content_words(req.original_question)
    repeats_question = len(gen_words & orig_words) >= max(3, len(orig_words) // 2)

    prev_followup_words = set()
    for pf in req.previous_followups:
        prev_followup_words |= _content_words(pf)
    redundant_with_prior = bool(prev_followup_words) and len(gen_words & prev_followup_words) >= max(3, len(prev_followup_words) // 2)

    return {
        "case_id": case["case_id"],
        "category": case["category"],
        "repeat_index": repeat_index,
        "probe_target": probe_target,
        "decision_source": resp.decision_source,
        "llm_status": resp.llm_status,
        "generated_followup": resp.followup,
        "generated_reason": resp.reason,
        "generated_target_concepts": resp.target_concepts,
        "keyword_overlap_with_probe_target": overlap,
        "has_keyword_overlap": len(overlap) > 0,
        "coarse_repeats_original_question_flag": repeats_question,
        "coarse_redundant_with_prior_followup_flag": redundant_with_prior,
    }


async def main():
    registry = ModelRegistry.get()
    load_status = "already_loaded"
    if "qwen_1b" not in registry.models and GGUF_MODEL_PATH.exists():
        registry.load_gguf_model("qwen_1b", GGUF_MODEL_PATH)
        load_status = "loaded_this_run"
    elif not GGUF_MODEL_PATH.exists():
        load_status = "gguf_path_missing"

    env = {
        "MOCK_MODE": MOCK_MODE,
        "gguf_model_path": str(GGUF_MODEL_PATH),
        "gguf_model_exists": GGUF_MODEL_PATH.exists(),
        "models_loaded": list(registry.models.keys()),
        "load_status": load_status,
        "sampling": {"temperature": 0.1, "top_p": 0.9, "note": "read from services/qwen/app.py generate_full(), gguf branch"},
    }

    results = []
    for case in CASES:
        r = await run_case(case, repeat_index=0)
        results.append(r)
        print(f"[{case['case_id']}] decision_source={r['decision_source']} "
              f"overlap={r['has_keyword_overlap']} -> {r['generated_followup'][:120]!r}")
        if case.get("repeat"):
            for i in (1, 2):
                r2 = await run_case(case, repeat_index=i)
                results.append(r2)
                print(f"  [repeat {i}] -> {r2['generated_followup'][:120]!r}")

    # Strong-answer skip case: verified via the production predicate, no LLM call.
    sc = STRONG_ANSWER_SKIP_CASE
    er = sc["eval_result"]
    would_skip = production_skip_predicate(er["final_score"], er["missing_concepts"], er["incorrect_claims"], er["weakest_gap"])
    skip_result = {
        "case_id": sc["case_id"],
        "category": sc["category"],
        "method": "verified_via_production_skip_predicate_not_llm_call",
        "skip_predicate_source": SKIP_PREDICATE_SOURCE,
        "eval_result_used": er,
        "predicate_says_skip": would_skip,
        "matches_expectation": would_skip is True,
    }

    n_llm_cases = [r for r in results if r["decision_source"] == "qwen_1.5b_llm"]
    n_overlap = sum(1 for r in results if r["has_keyword_overlap"])
    n_repeats_flag = sum(1 for r in results if r["coarse_repeats_original_question_flag"])
    n_redundant_flag = sum(1 for r in results if r["coarse_redundant_with_prior_followup_flag"])

    by_category = {}
    for r in results:
        by_category.setdefault(r["category"], {"n": 0, "n_overlap": 0})
        by_category[r["category"]]["n"] += 1
        by_category[r["category"]]["n_overlap"] += int(r["has_keyword_overlap"])

    # Repeat-run variability: for cases with repeat=True, compare the 3 generations
    # (index 0,1,2) verbatim and via keyword-set Jaccard similarity.
    variability = {}
    for case in CASES:
        if not case.get("repeat"):
            continue
        runs = [r for r in results if r["case_id"] == case["case_id"]]
        texts = [r["generated_followup"] for r in runs]
        word_sets = [_content_words(t) for t in texts]
        all_identical = len(set(texts)) == 1
        pairwise_jaccard = []
        for i in range(len(word_sets)):
            for j in range(i + 1, len(word_sets)):
                a, b = word_sets[i], word_sets[j]
                union = a | b
                pairwise_jaccard.append(len(a & b) / len(union) if union else 1.0)
        variability[case["case_id"]] = {
            "n_runs": len(runs),
            "all_identical_text": all_identical,
            "mean_pairwise_keyword_jaccard": round(sum(pairwise_jaccard) / len(pairwise_jaccard), 3) if pairwise_jaccard else None,
            "texts": texts,
        }

    out = {
        "status": "MEASURED",
        "env": env,
        "n_generate_followup_calls": len(results),
        "n_cases_including_skip_verification": len(CASES) + 1,
        "summary": {
            "n_llm_path_used": len(n_llm_cases),
            "n_fallback_path_used": len(results) - len(n_llm_cases),
            "n_with_keyword_overlap_on_probe_target": n_overlap,
            "n_flagged_possibly_repeating_original_question": n_repeats_flag,
            "n_flagged_redundant_with_prior_followup": n_redundant_flag,
            "strong_answer_skip_case_matches_expectation": skip_result["matches_expectation"],
        },
        "by_category": by_category,
        "repeat_run_variability": variability,
        "cases": results,
        "strong_answer_skip_verification": skip_result,
        "method_caveats": [
            "Keyword overlap is a coarse, disclosed heuristic (shared content words between the "
            "generated follow-up and a hand-written description of the probed gap), not a semantic "
            "or human-judged groundedness measurement. It can under-detect true grounding but cannot "
            "over-detect it beyond incidental word overlap.",
            "N=12 constructed cases (15 generate_followup() calls after repeats) plus 1 skip-predicate "
            "verification -- indicative of current qualitative behavior across evidence categories, not "
            "a powered or statistically analyzed study, and not a random or representative sample of "
            "real candidate answers.",
            "Subjective rubric dimensions (technical correctness, specificity, answerability, "
            "evidence grounding beyond keyword overlap, non-redundancy beyond the coarse flag above, "
            "target relevance) are NOT scored by this script. They are read and rated manually in a "
            "separate companion pass after this script runs, and that manual pass is a single, "
            "non-blinded read by the same research agent that built this probe -- not an independent "
            "or expert rating, and not to be cited as such.",
            "The strong-answer skip case does not call generate_followup(); it is verified by "
            "re-applying the production gate predicate (quoted in SKIP_PREDICATE_SOURCE) to a "
            "constructed eval_result, since production itself never calls generate_followup() in that "
            "situation.",
            "The repeat-run variability check (3 same-input calls for 2 cases) uses the real GGUF "
            "sampling settings (temperature=0.1, top_p=0.9, no explicit per-call seed) and is a "
            "within-session observation of 2 cases, not a systematic study of generation stability.",
        ],
    }
    out_path = OUT_DIR / "results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out["summary"], indent=2))
    print(json.dumps(variability, indent=2)[:2000])
    print(f"Full results: {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
