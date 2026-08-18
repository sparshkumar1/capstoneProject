"""
PrepAIred — FastAPI Backend
All REST API routes + WebSocket interview handler

Run with:
    uvicorn main:app --reload --port 8000

Requires: fastapi, uvicorn, python-multipart
    pip install fastapi uvicorn python-multipart python-dotenv
"""

from __future__ import annotations

import asyncio
import json
import os
import pickle
import re
import sys
import tempfile
import time
import uuid
from datetime import UTC, datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

np = None
PPO = None
RL_RUNTIME_AVAILABLE = False

# ── Optional heavy imports (fail gracefully in dev mode) ────────────────
try:
    from logging_agent.logging_agent import LoggingAgent
    LOGGING_READY = True
except ImportError:
    LOGGING_READY = False

try:
    from agents.strategy.hybrid_orchestrator import HybridOrchestrator
    ORCHESTRATOR_READY = True
except ImportError:
    ORCHESTRATOR_READY = False

try:
    from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
    _INTERVIEW_ORCHESTRATOR_READY = True
except ImportError:
    InterviewOrchestrator = None
    _INTERVIEW_ORCHESTRATOR_READY = False

try:
    from agents.orchestrator.feedback_agent import FEEDBACK_AGENT
    FEEDBACK_AGENT_READY = True
except ImportError:
    FEEDBACK_AGENT = None
    FEEDBACK_AGENT_READY = False

try:
    from agents.timing.timer import QuestionTimer
    TIMER_READY = True
except ImportError:
    QuestionTimer = None
    TIMER_READY = False

try:
    from agents.validation.score_validator import ScoreValidator, aggregate_scores
    _SCORE_VALIDATOR = ScoreValidator()
    VALIDATOR_READY = True
except ImportError:
    _SCORE_VALIDATOR = None
    VALIDATOR_READY = False

EVALUATOR_READY = False
EVALUATOR_SOURCE = "mock"
_evaluator_eval = None
_evaluator_get_rubric = None

try:
    from services.evaluator.app import evaluate as _prod_evaluate
    from services.evaluator.app import get_rubric as _prod_get_rubric
    _evaluator_eval = _prod_evaluate
    _evaluator_get_rubric = _prod_get_rubric
    EVALUATOR_READY = True
    EVALUATOR_SOURCE = "services_evaluator"
    print("[INFO] Authoritative production evaluator loaded from services.evaluator.app")
except Exception as exc:
    print(f"[ERROR] Could not load production evaluator from services.evaluator.app: {exc}")
    EVALUATOR_READY = False
    EVALUATOR_SOURCE = "mock"

PIPELINE_READY = LOGGING_READY or ORCHESTRATOR_READY or EVALUATOR_READY
if not PIPELINE_READY:
    print("[WARN] ML pipeline not loaded — running in mock/dev mode")
elif EVALUATOR_READY:
    print(f"[INFO] Evaluator source: {EVALUATOR_SOURCE}")


def _run_integrated_evaluator(transcript: str, question: dict) -> Optional[dict]:
    if not EVALUATOR_READY or _evaluator_eval is None or _evaluator_get_rubric is None:
        return None

    qid = str(question.get("id", "") or question.get("qid", "")).strip()
    rubric = _evaluator_get_rubric(qid)
    if not rubric:
        return None

    q_text = str(question.get("text", "") or question.get("question_text", ""))
    raw = _evaluator_eval(q_text, transcript, rubric)
    if not raw:
        return None

    score = float(raw.get("final_score", 0.0))
    grade = str(raw.get("grade", "Poor"))
    s1 = float(raw.get("S1_semantic", score))
    s2 = float(raw.get("S2_structural", score))
    r = float(raw.get("reasoning_score", score))

    covered_concepts = list(raw.get("correct_claims", []))
    missing_concepts = list(raw.get("missing_concepts", []))
    incorrect_claims = list(raw.get("incorrect_claims", []))
    strong_points = list(raw.get("strong_points", []))

    # Apply score validation rules if validator ready
    if VALIDATOR_READY and _SCORE_VALIDATOR is not None:
        evidence = {
            "mandatory_pass": bool(raw.get("mandatory_pass", True)),
            "mistake_penalty": float(raw.get("penalty", 0.0)),
        }
        validation = _SCORE_VALIDATOR.validate(score, evidence, is_coding=False)
        score = float(validation.get("validated_score", score))
        raw["validation_trace"] = validation.get("validation_trace", [])

    return {
        "final_score": round(score, 4),
        "question_score": round(score, 4),
        "technical_correctness": round(score, 4),
        "grade": grade,
        "S1_semantic": s1,
        "S2_structural": s2,
        "reasoning_score": r,
        "reasoning_quality": r,
        "concept_coverage": s2,
        "relevance": s1,
        "depth": raw.get("depth", 0.5),
        "communication": raw.get("communication", 0.8),
        "evaluation_confidence": raw.get("evaluation_confidence", 0.9),
        "mandatory_pass": raw.get("mandatory_pass", True),
        "covered_concepts": covered_concepts,
        "missing_concepts": missing_concepts,
        "incorrect_claims": incorrect_claims,
        "weakest_gap": raw.get("weakest_gap", "None"),
        "strong_points": strong_points,
        "concept_details": raw.get("concept_details", []),
        "decision_source": raw.get("decision_source", EVALUATOR_SOURCE),
        "raw": raw,
    }

# ── Optional audio analysis agent imports (lazy) ───────────────────────
extract_prosodic_features = None
audio_confidence_score = None
audio_score_breakdown = None
analyze_linguistic_confidence = None
transcribe_and_align = None
score_hesitation = None
build_state_vector = None
reset_audio_session = None
AUDIO_ANALYSIS_READY = False
_AUDIO_IMPORT_ATTEMPTED = False


def _ensure_audio_analysis_imports() -> bool:
    global extract_prosodic_features
    global audio_confidence_score
    global audio_score_breakdown
    global analyze_linguistic_confidence
    global transcribe_and_align
    global score_hesitation
    global build_state_vector
    global reset_audio_session
    global AUDIO_ANALYSIS_READY
    global _AUDIO_IMPORT_ATTEMPTED

    if AUDIO_ANALYSIS_READY:
        return True
    if _AUDIO_IMPORT_ATTEMPTED:
        return False

    _AUDIO_IMPORT_ATTEMPTED = True
    try:
        from agents.audio.audio_features import extract_prosodic_features as _extract
        from agents.audio.confidence_scorer import score as _score
        from agents.audio.confidence_scorer import score_breakdown as _breakdown
        from agents.audio.hesitation_scorer import score_hesitation as _hesitation
        from agents.audio.nlp_analyzer import analyze_linguistic_confidence as _analyze
        from agents.audio.rl_state_vector import build_state_vector as _build_state
        from agents.audio.rl_state_vector import reset_session as _reset_audio_session
        from agents.audio.transcriber import transcribe_and_align as _transcribe

        extract_prosodic_features = _extract
        audio_confidence_score = _score
        audio_score_breakdown = _breakdown
        score_hesitation = _hesitation
        analyze_linguistic_confidence = _analyze
        build_state_vector = _build_state
        reset_audio_session = _reset_audio_session
        transcribe_and_align = _transcribe
        AUDIO_ANALYSIS_READY = True
        return True
    except Exception as exc:
        AUDIO_ANALYSIS_READY = False
        print(f"[WARN] Audio_Analysis_agent not loaded — audio confidence analysis disabled: {exc}")
        return False

# ── App ─────────────────────────────────────────────────────────────────
app = FastAPI(title="PrepAIred API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory stores (replace with DB in production) ────────────────────
CANDIDATES: Dict[str, dict] = {}
SESSIONS: Dict[str, dict] = {}
REPORTS: Dict[str, dict] = {}


# ── Pydantic models ──────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    name: str
    email: str
    college: str = ""
    year: str = ""
    roll: str = ""
    primary_lang: str = "C"
    experience: str = "intermediate"
    admin: bool = False
    adminPass: str = ""

class CreateSessionRequest(BaseModel):
    candidate_id: str
    c_topics: List[str]
    dsa_topics: List[str]
    duration_minutes: int = 20
    num_questions: int = 5
    interview_mode: str = "standard"  # standard | demo_rl
    baseline_questions: int = 3         # legacy input; demo_rl baseline runs easy->mid before RL

class RunCodeRequest(BaseModel):
    code: str
    session_id: str = ""

# ── Question bank (subset — expand from qns.json in Evaluator/) ─────────
QUESTION_BANK = {
    "pointers": [
        {"id": "ptr_01", "text": "Explain pointer arithmetic in C. What happens when you increment a pointer to an int vs a pointer to a char?", "type": "verbal", "difficulty": 2, "topic": "pointers"},
        {"id": "ptr_02", "text": "Write a C function that swaps two integers using pointers.", "type": "code", "difficulty": 2, "topic": "pointers", "code_template": "#include <stdio.h>\n\nvoid swap(int *a, int *b) {\n    // Your implementation\n}\n\nint main() {\n    int x = 5, y = 10;\n    swap(&x, &y);\n    printf(\"%d %d\\n\", x, y); // Expected: 10 5\n    return 0;\n}"},
        {"id": "ptr_03", "text": "What is a dangling pointer? How does it differ from a null pointer? Give a code example of each.", "type": "verbal", "difficulty": 3, "topic": "pointers"},
        {"id": "ptr_04", "text": "Write a C function to find the length of a string using only pointer arithmetic (no array indexing, no strlen).", "type": "code", "difficulty": 3, "topic": "pointers", "code_template": "#include <stdio.h>\n\nint str_len(const char *s) {\n    // Use only pointer arithmetic\n}\n\nint main() {\n    printf(\"%d\\n\", str_len(\"hello\")); // Expected: 5\n    return 0;\n}"},
        {"id": "ptr_05", "text": "Explain double pointers. Write a function that allocates a 2D array dynamically and returns it via a double pointer.", "type": "code", "difficulty": 4, "topic": "pointers"},
    ],
    "memory_management": [
        {"id": "mem_01", "text": "What is the difference between malloc, calloc, and realloc? When would you use each?", "type": "verbal", "difficulty": 2, "topic": "memory_management"},
        {"id": "mem_02", "text": "Write a C program that creates a dynamic array of n integers, fills them with squares, prints them, then frees the memory correctly.", "type": "code", "difficulty": 2, "topic": "memory_management", "code_template": "#include <stdio.h>\n#include <stdlib.h>\n\nint main() {\n    int n = 5;\n    // Your code here\n    return 0;\n}"},
        {"id": "mem_03", "text": "What is a memory leak? Write a function with a memory leak and then fix it.", "type": "code", "difficulty": 3, "topic": "memory_management"},
    ],
    "arrays_strings": [
        {"id": "arr_01", "text": "Write a C function to reverse a string in-place without using a temporary array.", "type": "code", "difficulty": 2, "topic": "arrays_strings", "code_template": "#include <stdio.h>\n#include <string.h>\n\nvoid reverse_str(char *s) {\n    // Your implementation\n}\n\nint main() {\n    char s[] = \"hello\";\n    reverse_str(s);\n    printf(\"%s\\n\", s); // Expected: olleh\n    return 0;\n}"},
        {"id": "arr_02", "text": "Explain how 2D arrays are laid out in memory in C. What is row-major order?", "type": "verbal", "difficulty": 2, "topic": "arrays_strings"},
    ],
    "linked_list": [
        {"id": "ll_01", "text": "Write a C function to reverse a singly linked list iteratively.", "type": "code", "difficulty": 3, "topic": "linked_list", "code_template": "#include <stdio.h>\n#include <stdlib.h>\n\nstruct Node { int data; struct Node *next; };\n\nstruct Node* reverse(struct Node *head) {\n    // Your implementation\n}\n\n// Helper: create list from array\nstruct Node* make_list(int *arr, int n) {\n    if (!n) return NULL;\n    struct Node *h = malloc(sizeof(struct Node));\n    h->data = arr[0]; h->next = NULL;\n    struct Node *t = h;\n    for (int i=1;i<n;i++) { struct Node *nd=malloc(sizeof(struct Node)); nd->data=arr[i]; nd->next=NULL; t->next=nd; t=nd; }\n    return h;\n}\n\nvoid print_list(struct Node *h) { while(h){printf(\"%d \",h->data);h=h->next;} printf(\"\\n\"); }\n\nint main() {\n    int arr[]={1,2,3,4,5};\n    struct Node *head=make_list(arr,5);\n    head=reverse(head);\n    print_list(head); // Expected: 5 4 3 2 1\n    return 0;\n}"},
        {"id": "ll_02", "text": "Detect a cycle in a linked list using Floyd's algorithm. Explain the tortoise and hare approach.", "type": "verbal", "difficulty": 3, "topic": "linked_list"},
    ],
    "dynamic_programming": [
        {"id": "dp_01", "text": "Implement the 0/1 knapsack problem in C using dynamic programming with a 2D table.", "type": "code", "difficulty": 4, "topic": "dynamic_programming", "code_template": "#include <stdio.h>\n\nint knapsack(int W, int *wt, int *val, int n) {\n    // Fill the DP table\n}\n\nint main() {\n    int val[] = {60, 100, 120};\n    int wt[]  = {10, 20, 30};\n    int W = 50, n = 3;\n    printf(\"%d\\n\", knapsack(W, wt, val, n)); // Expected: 220\n    return 0;\n}"},
        {"id": "dp_02", "text": "What is memoization? How does it differ from tabulation? When would you choose one over the other?", "type": "verbal", "difficulty": 3, "topic": "dynamic_programming"},
    ],
    "graphs": [
        {"id": "gr_01", "text": "Implement BFS traversal of a graph represented as an adjacency list in C.", "type": "code", "difficulty": 3, "topic": "graphs"},
        {"id": "gr_02", "text": "Explain Dijkstra's algorithm. What is its time complexity and when does it fail?", "type": "verbal", "difficulty": 4, "topic": "graphs"},
    ],
    "sorting": [
        {"id": "sort_01", "text": "Implement merge sort in C. Explain the time and space complexity.", "type": "code", "difficulty": 3, "topic": "sorting", "code_template": "#include <stdio.h>\n#include <stdlib.h>\n\nvoid merge(int *arr, int l, int m, int r) {\n    // Your merge step\n}\n\nvoid merge_sort(int *arr, int l, int r) {\n    // Your implementation\n}\n\nint main() {\n    int arr[] = {38,27,43,3,9,82,10};\n    merge_sort(arr, 0, 6);\n    for(int i=0;i<7;i++) printf(\"%d \",arr[i]);\n    return 0;\n}"},
    ],
    "trees": [
        {"id": "tree_01", "text": "Write a C function to find the height of a binary tree recursively.", "type": "code", "difficulty": 2, "topic": "trees"},
        {"id": "tree_02", "text": "Explain the difference between in-order, pre-order, and post-order traversal with an example.", "type": "verbal", "difficulty": 2, "topic": "trees"},
    ],
    "stacks_queues": [
        {"id": "sq_01", "text": "Implement a stack using a linked list in C with push, pop, and peek operations.", "type": "code", "difficulty": 2, "topic": "stacks_queues"},
        {"id": "sq_02", "text": "Using a stack, write a C function to check if parentheses in an expression are balanced.", "type": "code", "difficulty": 3, "topic": "stacks_queues"},
    ],
    "arrays_algo": [
        {"id": "aa_01", "text": "Implement Kadane's algorithm in C to find the maximum subarray sum.", "type": "code", "difficulty": 3, "topic": "arrays_algo", "code_template": "#include <stdio.h>\n\nint max_subarray(int *arr, int n) {\n    // Kadane's algorithm\n}\n\nint main() {\n    int arr[] = {-2,1,-3,4,-1,2,1,-5,4};\n    printf(\"%d\\n\", max_subarray(arr, 9)); // Expected: 6\n    return 0;\n}"},
        {"id": "aa_02", "text": "Explain the two-pointer technique. Give two problems where it reduces complexity from O(n²) to O(n).", "type": "verbal", "difficulty": 3, "topic": "arrays_algo"},
    ],
    "structs_unions": [
        {"id": "su_01", "text": "What is struct padding? Why does C add padding bytes and how can you control it?", "type": "verbal", "difficulty": 3, "topic": "structs_unions"},
    ],
    "bit_manipulation": [
        {"id": "bm_01", "text": "Write C functions to: (1) set bit k, (2) clear bit k, (3) toggle bit k, (4) check if bit k is set.", "type": "code", "difficulty": 3, "topic": "bit_manipulation"},
    ],
}


def _normalize_topic_key(value: str) -> str:
    return "".join(ch for ch in (value or "").lower() if ch.isalnum())


def _difficulty_to_level(value: Any) -> int:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return 3
    if v <= 1.0:
        return max(1, min(5, int(round(v * 5))))
    return max(1, min(5, int(round(v))))


def _lexical_token_overlap(t1: str, t2: str) -> float:
    """Calculate lexical/token Jaccard overlap between two question texts."""
    words1 = set(re.findall(r"\w+", (t1 or "").lower()))
    words2 = set(re.findall(r"\w+", (t2 or "").lower()))
    if not words1 or not words2:
        return 0.0
    return len(words1 & words2) / len(words1 | words2)

# Backward-compatible alias for existing imports/callers
_text_similarity = _lexical_token_overlap



def _load_question_bank_from_qns() -> Optional[Dict[str, List[dict]]]:
    root = Path(__file__).resolve().parent.parent.parent
    candidates = [
        root / "data" / "questions" / "qns.json",
        root / "services" / "evaluator" / "assets" / "qns.json",
        root / "qns.json",
    ]

    rubric_candidates = [
        root / "data" / "rubrics" / "rubrics_final_clean.json",
        root / "services" / "evaluator" / "assets" / "rubrics.json",
    ]

    rubrics_by_qid: Dict[str, dict] = {}
    for rpath in rubric_candidates:
        if rpath.exists():
            try:
                with rpath.open("r", encoding="utf-8") as rf:
                    rlist = json.load(rf)
                    if isinstance(rlist, list):
                        for r in rlist:
                            if isinstance(r, dict) and "qid" in r:
                                rubrics_by_qid[str(r["qid"])] = r
                if rubrics_by_qid:
                    break
            except Exception as rexc:
                print(f"[WARN] Failed loading rubrics from {rpath}: {rexc}")

    for path in candidates:
        if not path.exists():
            continue
        try:
            with path.open("r", encoding="utf-8") as f:
                rows = json.load(f)
            if not isinstance(rows, list):
                continue

            grouped: Dict[str, List[dict]] = {}
            for row in rows:
                if not isinstance(row, dict):
                    continue
                topic_raw = str(row.get("topic", "general"))
                topic_key = _normalize_topic_key(topic_raw) or "general"
                qid = str(row.get("qid", "")) or str(uuid.uuid4())
                q_text = (row.get("question_text") or row.get("text") or "").strip()
                q_type = str(row.get("type", "theory")).lower()

                # Get matching rubric
                rubric = rubrics_by_qid.get(qid, {})
                lm = rubric.get("logic_markers", {}) or rubric.get("logic_markers_covered", {})
                mandatory = list(lm.get("mandatory", [])) if isinstance(lm, dict) else []
                concept_groups = list(lm.get("concept_groups", [])) if isinstance(lm, dict) else []
                semantic_targets = list(rubric.get("semantic_targets", []) or rubric.get("semantic_coverage", []))
                common_mistakes = list(rubric.get("common_mistakes", []) or rubric.get("common_mistakes_addressed", []))
                bonus = list(lm.get("advanced_bonus", [])) if isinstance(lm, dict) else []
                ref_ans = str(rubric.get("logic_context") or rubric.get("answer") or "")

                expected_concepts = list(mandatory)
                for grp in concept_groups:
                    if isinstance(grp, list) and grp:
                        expected_concepts.append(grp[0])
                    elif isinstance(grp, str):
                        expected_concepts.append(grp)
                for st in semantic_targets:
                    if st not in expected_concepts:
                        expected_concepts.append(st)

                category = "c" if "c" in topic_key or topic_key in {
                    "pointers", "memorymanagement", "storageclasses", "functions", "cvariables",
                    "cprogramming", "preprocessor", "linkage", "enum", "structsunions", "bitmanipulation", "advancedc"
                } else "dsa"

                question = {
                    "id": qid,
                    "text": q_text,
                    "type": "code" if "coding" in q_type or "code" in q_type else "verbal",
                    "difficulty": _difficulty_to_level(row.get("difficulty", 3)),
                    "difficulty_float": float(row.get("difficulty", 0.6)),
                    "topic": topic_key,
                    "category": category,
                    "time_limit_sec": int(row.get("time_limit_sec", 75)),
                    "bloom_level": str(row.get("bloom_level") or row.get("blooms_level") or "L3"),
                    "expected_concepts": expected_concepts,
                    "mandatory_concepts": mandatory,
                    "common_mistakes": common_mistakes,
                    "reference_answer": ref_ans,
                    "possible_followups": bonus,
                    "rubric": rubric,
                    "constraints": row.get("constraints", ""),
                    "code_template": row.get("code_template") or row.get("starter_code") or "",
                }
                grouped.setdefault(topic_key, []).append(question)

            if grouped:
                total_loaded = sum(len(v) for v in grouped.values())
                print(f"[INFO] Loaded question bank from {path} ({total_loaded} questions, {len(rubrics_by_qid)} rubrics)")
                return grouped
        except Exception as exc:
            print(f"[WARN] Failed loading question bank from {path}: {exc}")

    return None


_loaded_bank = _load_question_bank_from_qns()
if _loaded_bank:
    QUESTION_BANK = _loaded_bank

def select_questions(
    c_topics: list,
    dsa_topics: list,
    num: int,
    difficulty: int = 2,
    exclude_ids: Optional[set] = None,
    candidate_state: Optional[dict] = None,
) -> list:
    """
    Personalized question selection with 3-level duplicate prevention and baseline Easy/Easy-Medium start.
    """
    seen_ids = set(exclude_ids or [])
    seen_texts = set()
    if candidate_state:
        for prev_qid in candidate_state.get("question_history", []):
            seen_ids.add(str(prev_qid))

    pool = []
    all_topics = [t for t in (c_topics + dsa_topics) if t]
    if all_topics:
        for topic in all_topics:
            topic_key = _normalize_topic_key(topic)
            for bank_topic, bank_qs in QUESTION_BANK.items():
                if topic_key == bank_topic or topic_key in bank_topic or bank_topic in topic_key:
                    pool.extend(bank_qs)

    if not pool:
        for qs in QUESTION_BANK.values():
            pool.extend(qs)

    # Level 1: Deduplicate by ID
    unique_pool = []
    for q in pool:
        qid = str(q.get("id", ""))
        if qid in seen_ids:
            continue
        # Level 2: Deduplicate by normalized text
        norm_text = re.sub(r"\s+", " ", q.get("text", "").strip().lower())
        if norm_text in seen_texts:
            continue
        seen_texts.add(norm_text)
        unique_pool.append(q)

    # Personalization scoring weights
    weaknesses = set(candidate_state.get("weaknesses", [])) if candidate_state else set()
    strengths = set(candidate_state.get("strengths", [])) if candidate_state else set()

    type_buckets = {"verbal": [], "code": []}
    for q in unique_pool:
        qtype = "code" if q.get("type") == "code" else "verbal"
        type_buckets[qtype].append(q)

    for items in type_buckets.values():
        items.sort(key=lambda q: (abs(q.get("difficulty", 3) - difficulty), q.get("id", "")))

    topic_counts: Dict[str, int] = {}
    result: List[dict] = []
    next_type = "verbal"

    while len(result) < num and (type_buckets["verbal"] or type_buckets["code"]):
        # First question MUST be Easy / Easy-Medium (difficulty <= 2)
        target_diff = 2 if len(result) == 0 else difficulty

        preferred = next_type if type_buckets[next_type] else ("code" if type_buckets["code"] else "verbal")
        candidates = type_buckets[preferred]
        if not candidates:
            # Fall back to other bucket
            alt = "code" if preferred == "verbal" else "verbal"
            candidates = type_buckets.get(alt, [])
            if not candidates:
                break
            preferred = alt

        pick_idx = 0
        best_score = None
        for i, q in enumerate(candidates):
            q_text = q.get("text", "")
            # Level 3: Lexical/token overlap deduplication (Jaccard threshold >= 0.75) against session history
            lexical_conflict = False
            for prev_selected in result:
                sim = _lexical_token_overlap(q_text, prev_selected.get("text", ""))
                if sim >= 0.75:
                    lexical_conflict = True
                    break
            if lexical_conflict:
                continue


            q_diff = q.get("difficulty", 3)
            diff_penalty = abs(q_diff - target_diff)
            # Enforce Easy/Easy-Medium constraint for question 1
            if len(result) == 0 and q_diff > 2:
                diff_penalty += 5.0

            topic = q.get("topic", "")
            diversity_penalty = topic_counts.get(topic, 0) * 0.40

            # Personalization adaptation
            adaptation_bonus = 0.0
            if topic in weaknesses and target_diff <= 2:
                adaptation_bonus -= 0.30  # prioritize foundational remediation
            elif topic in strengths and target_diff >= 4:
                adaptation_bonus -= 0.30  # prioritize advanced depth probe

            score = diff_penalty + diversity_penalty + adaptation_bonus
            if best_score is None or score < best_score:
                best_score = score
                pick_idx = i

        if best_score is None or not candidates:
            break

        q = candidates.pop(pick_idx)
        seen_ids.add(str(q.get("id", "")))
        result.append(q)
        topic = q.get("topic", "")
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
        next_type = "code" if preferred == "verbal" else "verbal"

    return result[:num]



def _analyze_audio_confidence(audio_path: str, transcript_text: str = "", session_id: str = "") -> Optional[dict]:
    if not _ensure_audio_analysis_imports():
        return None

    try:
        prosodic = extract_prosodic_features(audio_path)
        transcription = transcribe_and_align(audio_path) if transcribe_and_align else {}

        # Use authoritative server transcript for linguistic analysis
        effective_transcript = (transcription.get("transcript") or transcript_text or "").strip()

        linguistic = analyze_linguistic_confidence(effective_transcript)
        final_score = audio_confidence_score(prosodic, transcription, linguistic)

        breakdown = audio_score_breakdown(prosodic, transcription, linguistic)
        hesitation = score_hesitation(prosodic, transcription) if score_hesitation else None

        rl_state = None
        if build_state_vector:
            session = SESSIONS.get(session_id, {}) if session_id else {}
            raw_diff = session.get("current_difficulty", 3)
            try:
                diff_norm = float(raw_diff)
            except (TypeError, ValueError):
                diff_norm = 3.0
            if diff_norm > 1.0:
                diff_norm = max(0.0, min(1.0, diff_norm / 5.0))

            rl_state = build_state_vector(
                confidence_score=final_score,
                hesitation=hesitation or {"hesitation_score": 0.5},
                transcription=transcription,
                linguistic=linguistic,
                session_id=session_id or "default",
                current_difficulty=diff_norm,
                question_index=int(session.get("question_index", 0) or 0),
                max_questions=int(session.get("num_questions", 10) or 10),
            )

        return {
            "confidence_score": final_score,
            "label": (
                "high" if final_score >= 0.70 else
                "medium" if final_score >= 0.45 else
                "low"
            ),
            "prosodic": prosodic,
            "transcription": {
                "pause_count": transcription.get("pause_count", 0),
                "total_pause_time": transcription.get("total_pause_time", 0.0),
                "total_speech_time": transcription.get("total_speech_time", 0.0),
                "true_speaking_rate": transcription.get("true_speaking_rate", 0.0),
                "alignment_source": transcription.get("alignment_source", "unknown"),
            },
            "linguistic": linguistic,
            "breakdown": breakdown,
            "hesitation": hesitation,
            "rl_state": rl_state,
        }
    except Exception as exc:
        return {
            "error": str(exc),
            "confidence_score": 0.0,
            "label": "unavailable",
        }


# ── Session dict shim (handles both InterviewOrchestrator and legacy dicts)
def _get_session_dict(session_id: str) -> dict:
    obj = SESSIONS.get(session_id)
    if obj is None:
        return {}
    return obj.to_session_dict() if hasattr(obj, "to_session_dict") else obj


# ── REST Routes ──────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "pipeline_ready": PIPELINE_READY, "timestamp": datetime.now(UTC).isoformat()}


@app.post("/api/login")
async def login(req: LoginRequest):
    """Register/login a candidate."""
    # In production: check DB, hash passwords, issue JWT
    cid = str(uuid.uuid4())
    candidate = {
        "id": cid,
        "name": req.name,
        "email": req.email,
        "college": req.college,
        "year": req.year,
        "roll": req.roll,
        "primary_lang": req.primary_lang,
        "experience": req.experience,
        "is_admin": req.admin,
        "created_at": datetime.now(UTC).isoformat(),
    }
    CANDIDATES[cid] = candidate
    return candidate


@app.post("/api/sessions")
async def create_session(req: CreateSessionRequest):
    """Create a new interview session."""
    sid = str(uuid.uuid4())
    candidate = CANDIDATES.get(req.candidate_id, {"id": req.candidate_id})
    config = {
        "c_topics": req.c_topics,
        "dsa_topics": req.dsa_topics,
        "duration_minutes": req.duration_minutes,
        "num_questions": req.num_questions,
        "interview_mode": req.interview_mode,
        "baseline_questions": getattr(req, "baseline_questions", None),
    }

    if _INTERVIEW_ORCHESTRATOR_READY and InterviewOrchestrator is not None:
        orchestrator = InterviewOrchestrator(
            session_id=sid,
            candidate=candidate,
            config=config,
            evaluator_fn=_run_integrated_evaluator,
            select_questions_fn=select_questions,
        )
        SESSIONS[sid] = orchestrator
        if _ensure_audio_analysis_imports() and reset_audio_session is not None:
            try:
                reset_audio_session(sid)
            except Exception:
                pass
        return {k: v for k, v in orchestrator.to_session_dict().items() if k != "questions"}

    raise HTTPException(503, "InterviewOrchestrator unavailable — check server imports")


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(404, "Session not found")
    s = _get_session_dict(session_id)
    return {k: v for k, v in s.items() if k != "questions"}


@app.post("/api/sessions/{session_id}/end")
async def end_session(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(404, "Session not found")
    obj = SESSIONS[session_id]
    report = await obj.end()
    REPORTS[report["id"]] = report
    return {"report_id": report["id"]}


@app.get("/api/sessions/{session_id}/report")
async def get_report(session_id: str):
    # Try direct report lookup by report UUID
    if session_id in REPORTS:
        return REPORTS[session_id]
    # Try session's linked report — use _get_session_dict to handle both orch and legacy dict
    s = _get_session_dict(session_id)
    report_id = s.get("report_id") if s else None
    if report_id and report_id in REPORTS:
        return REPORTS[report_id]
    raise HTTPException(404, "Report not found")


@app.post("/api/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    session_id: str = Form(""),
    browser_preview: str = Form("", alias="transcript"),
):
    """
    Authoritative Speech-to-Text endpoint.
    Processes the raw uploaded candidate audio through the server-side STT/acoustic pipeline.
    Browser speech recognition text is preserved strictly as a non-authoritative preview.
    """
    suffix = Path(audio.filename or "audio.wav").suffix or ".wav"
    fd, tmp_name = tempfile.mkstemp(prefix="audio_", suffix=suffix)
    tmp_path = Path(tmp_name)
    browser_preview = (browser_preview or "").strip()

    try:
        try:
            os.close(fd)
        except Exception:
            pass

        audio_bytes = await audio.read()
        tmp_path.write_bytes(audio_bytes)

        server_transcript = ""
        transcription_meta = {}

        # 1. Authoritative server STT pipeline from raw audio
        if _ensure_audio_analysis_imports() and transcribe_and_align is not None:
            transcription_meta = transcribe_and_align(str(tmp_path))
            server_transcript = (transcription_meta.get("transcript", "") or "").strip()
        elif LOGGING_READY:
            try:
                from logging_agent.stt_processor import STTProcessor
                stt = STTProcessor()
                server_transcript = (stt.transcribe(str(tmp_path)) or "").strip()
            except Exception:
                pass

        # Strict STT validation: Never promote browser preview to authoritative evaluation transcript
        if server_transcript:
            stt_status = "success"
            transcript_source = transcription_meta.get("alignment_source", "whisperx")
            audio_analysis = _analyze_audio_confidence(str(tmp_path), server_transcript, session_id)
        else:
            stt_status = "stt_unavailable"
            transcript_source = "unavailable"
            audio_analysis = None

        # Store latest audio analysis in session for FeedbackAgent & Orchestrator
        if session_id and session_id in SESSIONS and audio_analysis and not audio_analysis.get("error"):
            orch_obj = SESSIONS[session_id]
            if hasattr(orch_obj, "ingest_audio_analysis"):
                orch_obj.ingest_audio_analysis(audio_analysis, audio_analysis.get("confidence_score"))
            else:
                orch_obj["last_audio_analysis"] = audio_analysis
                conf = audio_analysis.get("confidence_score")
                if conf is not None:
                    orch_obj["last_confidence_score"] = float(conf)

        return {
            "transcript": server_transcript,
            "browser_preview_transcript": browser_preview,
            "stt_status": stt_status,
            "transcript_source": transcript_source,
            "alignment_source": transcription_meta.get("alignment_source", "unavailable"),
            "words": transcription_meta.get("words", []),
            "pauses": transcription_meta.get("pauses", []),
            "total_pause_time": transcription_meta.get("total_pause_time", 0.0),
            "total_speech_time": transcription_meta.get("total_speech_time", 0.0),
            "true_speaking_rate": transcription_meta.get("true_speaking_rate", 0.0),
            "session_id": session_id,
            "audio_analysis_ready": AUDIO_ANALYSIS_READY,
            "audio_analysis": audio_analysis,
        }


    except Exception as e:
        return {
            "transcript": f"[STT error: {e}]",
            "browser_preview_transcript": browser_preview,
            "stt_status": "error",
            "transcript_source": "unavailable",
            "alignment_source": "unavailable",
            "words": [],
            "pauses": [],
            "total_pause_time": 0.0,
            "total_speech_time": 0.0,
            "true_speaking_rate": 0.0,
            "session_id": session_id,
            "audio_analysis_ready": AUDIO_ANALYSIS_READY,
            "audio_analysis": None,
        }
    finally:
        tmp_path.unlink(missing_ok=True)


@app.post("/api/run_code")
async def run_code(req: RunCodeRequest):
    """Run C code in authoritative Docker sandbox."""
    from agents.coding_executor.coding_executor import evaluate_c_submission

    test_cases = []
    # If session and question are active, try to fetch question test cases
    if req.session_id and req.session_id in SESSIONS:
        sess = SESSIONS[req.session_id]
        curr_q = getattr(sess, "_current_question", None)
        if isinstance(curr_q, dict) and curr_q.get("test_cases"):
            test_cases = curr_q["test_cases"]

    result = evaluate_c_submission(req.code, test_cases=test_cases)
    return result



# ── Admin routes ─────────────────────────────────────────────────────────

@app.get("/api/admin/sessions")
async def admin_sessions(filter: str = "all", sort: str = "date_desc"):
    sessions_list = []
    for sid in list(SESSIONS.keys()):
        s = _get_session_dict(sid)
        cand = CANDIDATES.get(s.get("candidate_id", ""), {})
        entry = {
            "id": sid,
            "candidate_name": cand.get("name"),
            "candidate_email": cand.get("email"),
            "college": cand.get("college"),
            "year": cand.get("year"),
            "overall_score": s.get("overall_score"),
            "c_score": s.get("c_score"),
            "dsa_score": s.get("dsa_score"),
            "topics": s.get("topics", []),
            "final_difficulty": s.get("current_difficulty"),
            "duration_minutes": s.get("duration_minutes"),
            "total_questions": s.get("num_questions"),
            "status": s.get("status", "unknown"),
            "created_at": s.get("created_at"),
            "strengths": s.get("strengths", []),
            "missing_concepts": s.get("missing_concepts", []),
            "behaviour": s.get("behaviour"),
        }
        sessions_list.append(entry)

    # Sort
    reverse = "desc" in sort
    key = "created_at" if "date" in sort else "overall_score"
    sessions_list.sort(key=lambda x: (x.get(key) or ""), reverse=reverse)

    return {"sessions": sessions_list, "total": len(sessions_list)}


@app.get("/api/admin/stats")
async def admin_stats():
    total = len(SESSIONS)
    all_s = [_get_session_dict(sid) for sid in SESSIONS]
    scores = [s.get("overall_score", 0) for s in all_s if s.get("overall_score") is not None]
    today = date.today().isoformat()
    active_today = sum(1 for s in all_s if (s.get("created_at") or "")[:10] == today)
    unique_cands = len(set(s.get("candidate_id") for s in all_s))
    durations = [s.get("duration_minutes", 0) for s in all_s]
    pass_rate = sum(1 for sc in scores if sc >= 0.6) / max(len(scores), 1)

    return {
        "total_sessions": total,
        "avg_score": sum(scores) / max(len(scores), 1),
        "active_today": active_today,
        "unique_candidates": unique_cands,
        "avg_duration_min": int(sum(durations) / max(len(durations), 1)),
        "pass_rate": pass_rate,
    }


@app.get("/api/admin/sessions/{session_id}")
async def admin_session_detail(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(404, "Session not found")
    s = _get_session_dict(session_id)
    cand = CANDIDATES.get(s.get("candidate_id", ""), {})
    report = REPORTS.get(s.get("report_id", ""), {})
    return {**s, **report, "candidate_name": cand.get("name"), "candidate_email": cand.get("email")}


# ── WebSocket Interview Handler ───────────────────────────────────────────

@app.websocket("/ws/interview/{session_id}")
async def interview_ws(websocket: WebSocket, session_id: str):
    """
    Thin dispatcher — delegates all logic to InterviewOrchestrator.

    Client → Server messages:
        start           : begin session
        voice_answer    : { transcript, question_id, attempts? }
        code_submission : { code, question_id, stdout, stderr, passed, tests_passed?, tests_total? }
        next_question   : move to next question after feedback
        request_hint    : { question_id }
        skip_question   : { question_id }
        end_session     : {}

    Server → Client messages:
        question        : { id, text, topic, difficulty, type, ... }
        feedback        : { final_score, justification, strong_points, ... }
        difficulty_update : { new_difficulty, reason, action }
        hint            : { text }
        session_end     : { report_id, overall_score }
        error           : { message }
    """
    await websocket.accept()

    if session_id not in SESSIONS:
        await websocket.send_json({"type": "error", "payload": {"message": "Session not found"}})
        await websocket.close()
        return

    orch: InterviewOrchestrator = SESSIONS[session_id]

    async def send(type_: str, payload: dict):
        try:
            await websocket.send_json({"type": type_, "payload": payload})
        except Exception:
            pass

    async def dispatch_answer(result: dict):
        await send("feedback", result["feedback"])
        if result.get("hint"):
            await send("hint", {"text": result["hint"]})
        if result.get("difficulty_update"):
            await send("difficulty_update", result["difficulty_update"])
        if result.get("next_action") == "session_end":
            report = await orch.end()
            REPORTS[report["id"]] = report
            await send("session_end", {
                "report_id": report["id"],
                "overall_score": report.get("overall_score", 0.0),
            })

    try:
        async for raw in websocket.iter_text():
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await send("error", {"message": "Invalid JSON"})
                continue

            mtype = msg.get("type")
            payload = msg.get("payload", {})

            if mtype == "start":
                result = await orch.start()
                if isinstance(result, dict) and result.get("type") == "session_end":
                    report = await orch.end()
                    REPORTS[report["id"]] = report
                    await send("session_end", {
                        "report_id": report["id"],
                        "overall_score": report.get("overall_score", 0.0),
                    })
                else:
                    await send("question", result)

            elif mtype == "voice_answer":
                result = await orch.handle_voice_answer(
                    payload.get("transcript", ""),
                    payload.get("question_id", ""),
                    int(payload.get("attempts", 1)),
                )
                await dispatch_answer(result)

            elif mtype == "code_submission":
                result = await orch.handle_code_submission(
                    payload.get("code", ""),
                    payload.get("question_id", ""),
                    bool(payload.get("passed", False)),
                    int(payload.get("tests_passed", 0)),
                    int(payload.get("tests_total", 0)),
                    payload.get("stdout", ""),
                    payload.get("stderr", ""),
                )
                await dispatch_answer(result)

            elif mtype == "next_question":
                res = await orch.handle_next_question()
                if res.get("type") == "session_end":
                    report = await orch.end()
                    REPORTS[report["id"]] = report
                    await send("session_end", {
                        "report_id": report["id"],
                        "overall_score": report.get("overall_score", 0.0),
                    })
                else:
                    await send("question", res.get("payload", res))

            elif mtype == "request_hint":
                hint = await orch.request_hint(payload.get("question_id", ""))
                await send("hint", hint)

            elif mtype == "skip_question":
                res = await orch.skip_question(payload.get("question_id", ""))
                if res.get("type") == "session_end":
                    report = await orch.end()
                    REPORTS[report["id"]] = report
                    await send("session_end", {
                        "report_id": report["id"],
                        "overall_score": report.get("overall_score", 0.0),
                    })
                else:
                    await send("question", res.get("payload", res))

            elif mtype == "end_session":
                report = await orch.end()
                REPORTS[report["id"]] = report
                await send("session_end", {
                    "report_id": report["id"],
                    "overall_score": report.get("overall_score", 0.0),
                })
                break

    except WebSocketDisconnect:
        orch.mark_abandoned()
        print(f"[WS] Client disconnected: {session_id}")
    except Exception as e:
        orch.mark_error()
        print(f"[WS] Error in session {session_id}: {e}")


# ─── Dead code removed (PR 2): _STATIC_HINTS, _async_hint, _generate_report,
# _make_recommendations now live in orchestrator_agent/interview_orchestrator.py


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
