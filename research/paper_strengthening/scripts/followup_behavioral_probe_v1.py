"""
Follow-up mechanism live-model behavioral probe (V1).

Every prior pass in this engagement (RESEARCH_IMPROVEMENT_EXECUTION_V1 through
FOURTH_RESEARCH_IMPROVEMENT_PASS) flagged the same open item without executing
it: the evidence-gated follow-up mechanism (services/qwen/app.py::generate_followup)
has only ever been tested at the structural/format level (JSON-parses, passes
_validate_followup_output, doesn't repeat the original question) -- never against
the real, unmodified GGUF model's actual generated text for whether it is
plausibly grounded in the specific gap it was asked to probe.

This script closes that gap partially and honestly: it calls the real
generate_followup() coroutine (not a mock, not a raw model-text shortcut) for
five constructed cases, one per non-skip trigger category documented in
docs/FOLLOW_UP_SYSTEM.md's decision matrix (misconception, missing concept,
below-threshold score, unresolved weakest-gap, and a combined case). For each,
it records:
  - decision_source / llm_status (did the real model path fire, or the
    deterministic fallback -- both are legitimate outcomes and neither is
    treated as a defect)
  - a coarse, disclosed keyword-overlap check: does the generated follow-up
    text share any content word with the specific concept/misconception it
    was asked to probe? This is NOT a semantic-groundedness measurement (no
    validated instrument for that exists in this project) -- it is a cheap,
    transparent sanity check that can only fail to detect grounding it should
    have detected (false negatives), never invent grounding that isn't there,
    so a "no overlap" result is flagged as worth manual reading, not scored
    as a defect by itself.
  - the raw generated text, for manual inspection (stored verbatim in the
    output JSON, not summarized away).

No training, no scoring-code change, no new confirmatory experiment. Five
real-model calls only -- small N, disclosed, indicative rather than a
powered study, consistent with this project's other small-N direct
measurements (qwen_latency_measurement.py, n=6).

Usage: python followup_behavioral_probe_v1.py
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

OUT_DIR = Path(__file__).resolve().parent.parent / "results" / "followup_behavioral_probe_v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

_STOPWORDS = {
    "the", "a", "an", "is", "are", "of", "to", "and", "or", "in", "on", "for",
    "does", "do", "how", "what", "why", "explain", "describe", "can", "you",
    "your", "this", "that", "it", "its", "with", "when", "where", "which",
    "answer", "candidate", "question", "concept", "about", "not", "no",
}


def _content_words(text: str) -> set:
    return {w for w in re.findall(r"[a-zA-Z]+", text.lower()) if len(w) > 2 and w not in _STOPWORDS}


CASES = [
    {
        "case_id": "misconception",
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
    },
    {
        "case_id": "missing_concept",
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
    },
    {
        "case_id": "below_threshold_score",
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
    },
    {
        "case_id": "weakest_gap",
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
            # Corrected after the first run of this probe: the value below was
            # originally a long, hand-written descriptive sentence, which is
            # NOT representative of how services/evaluator/app.py actually
            # populates weakest_gap in production (lines 521-529: always one
            # of a small set of short phrases, e.g. "Reasoning depth and
            # mechanistic explanation", never a free-form sentence). The
            # original value did surface a real fallback-template defect
            # (_synthesize_structured_followup's weakest_gap branch breaks on
            # long free-form text), but that defect is not reachable in
            # production given the evaluator's actual output shape, so it is
            # disclosed as a latent/unreachable-in-practice finding rather
            # than re-tested here; this case now uses the realistic short
            # form to test the TASK-line fix under representative conditions.
            weakest_gap="Reasoning depth and mechanistic explanation",
        ),
        "probe_target": "reasoning depth / mechanistic explanation",
    },
    {
        "case_id": "combined_missing_and_misconception",
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
    },
]


async def run_case(case: dict) -> dict:
    req = case["req"]
    probe_target = case.get("probe_target", "")
    resp = await generate_followup(req)
    gen_words = _content_words(resp.followup)
    target_words = _content_words(probe_target)
    overlap = sorted(gen_words & target_words)
    orig_words = _content_words(req.original_question)
    repeats_question = len(gen_words & orig_words) >= max(3, len(orig_words) // 2)
    return {
        "case_id": case["case_id"],
        "probe_target": probe_target,
        "decision_source": resp.decision_source,
        "llm_status": resp.llm_status,
        "generated_followup": resp.followup,
        "generated_reason": resp.reason,
        "generated_target_concepts": resp.target_concepts,
        "keyword_overlap_with_probe_target": overlap,
        "has_keyword_overlap": len(overlap) > 0,
        "coarse_repeats_original_question_flag": repeats_question,
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
    }

    results = []
    for case in CASES:
        r = await run_case(case)
        results.append(r)
        print(f"[{case['case_id']}] decision_source={r['decision_source']} "
              f"overlap={r['has_keyword_overlap']} -> {r['generated_followup'][:120]!r}")

    n_llm = sum(1 for r in results if r["decision_source"] == "qwen_1.5b_llm")
    n_overlap = sum(1 for r in results if r["has_keyword_overlap"])
    n_repeats_flag = sum(1 for r in results if r["coarse_repeats_original_question_flag"])

    out = {
        "status": "MEASURED",
        "env": env,
        "n_cases": len(results),
        "summary": {
            "n_llm_path_used": n_llm,
            "n_fallback_path_used": len(results) - n_llm,
            "n_with_keyword_overlap_on_probe_target": n_overlap,
            "n_flagged_possibly_repeating_original_question": n_repeats_flag,
        },
        "cases": results,
        "method_caveats": [
            "Keyword overlap is a coarse, disclosed heuristic (shared content words between the "
            "generated follow-up and a hand-written description of the probed gap), not a semantic "
            "or human-judged groundedness measurement. It can under-detect true grounding (a "
            "follow-up can be well-grounded while using none of the same words) but cannot "
            "over-detect it beyond incidental word overlap.",
            "N=5, one real-model call per case, no repetition per case -- indicative of current "
            "qualitative behavior, not a powered or statistically analyzed study.",
            "This probe tests generate_followup() directly; it does not exercise the orchestrator-level "
            "strong-answer skip condition, which is a separate gate upstream of this function and is "
            "not itself an LLM call.",
        ],
    }
    out_path = OUT_DIR / "results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out["summary"], indent=2))
    print(f"Full results: {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
