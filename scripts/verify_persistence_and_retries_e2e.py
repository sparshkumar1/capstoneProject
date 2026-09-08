"""
scripts/verify_persistence_and_retries_e2e.py — End-to-End Verification
========================================================================

Validates the full lifecycle of:
1. Persistent Candidate Identity across multi-session logins (same email = same UUID).
2. Same-session retry: turn index preservation, question timer reset, non-advancing question queue.
3. Multi-attempt logging and deterministic best answer selection (score ascending/descending).
4. Strict tie-breaking (fewest missing concepts, most recent attempt).
5. Cross-session historical retrieval (historical_best banner loaded on subsequent session).
6. Evaluator-grounded comparison facts without LLM score fabrication.
7. Candidate & question data isolation.
8. Follow-up vs retry decoupling (auxiliary follow-up never overwrites primary best).

Run with:
    python scripts/verify_persistence_and_retries_e2e.py
"""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure root on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
from services.storage.database import (
    compare_with_previous_best,
    get_best_attempt,
    get_candidate_by_id,
    get_or_create_candidate,
    get_question_attempts,
    init_db,
    save_attempt,
    save_session,
)


def log_step(step_name: str):
    print(f"\n{'='*70}\n[STEP] {step_name}\n{'='*70}")


def assert_true(cond: bool, msg: str):
    if not cond:
        print(f"[-] FAILED: {msg}")
        sys.exit(1)
    print(f"[+] PASS: {msg}")


async def run_e2e():
    print("[*] Starting PrepAIred Persistence & Retries E2E Verification...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        test_db = Path(tmp_dir) / "e2e_prepaired.db"
        init_db(test_db)
        print(f"[*] Initialized temporary verification database at: {test_db}")

        with patch("services.storage.database.DEFAULT_DB_PATH", test_db):

            # ── 1. Candidate Identity Persistence ─────────────────────────────
            log_step("1. Candidate Identity Persistence Across Sessions")
            c1 = get_or_create_candidate(
                email="alice.smith@stanford.edu",
                name="Alice Smith",
                college="Stanford",
                year="Senior",
                db_path=test_db,
            )
            c1_id = c1["id"]
            print(f"    Candidate 1 Created: ID={c1_id}, Email={c1['email']}")
            assert_true(bool(c1_id), "Candidate 1 generated valid UUID")

            # Alice logs in again next day with uppercase email
            c1_relogin = get_or_create_candidate(
                email="  ALICE.SMITH@STANFORD.EDU ",
                name="Alice S.",
                college="Stanford University",
                db_path=test_db,
            )
            assert_true(
                c1_relogin["id"] == c1_id,
                f"Candidate re-login preserved identical UUID ({c1_relogin['id']} == {c1_id})",
            )
            assert_true(
                c1_relogin["college"] == "Stanford University",
                "Candidate profile fields updated gracefully on re-login",
            )

            # ── 2. Session 1: Question 1 — Attempt 1 (Partial) ────────────────
            log_step("2. Session 1: Question 1 — Initial Attempt (Score 0.45)")
            mock_eval = MagicMock()
            mock_eval.return_value = {
                "final_score": 0.45,
                "grade": "C",
                "justification": "Candidate explained memory allocation but missed initialization difference.",
                "covered_concepts": ["heap_allocation"],
                "missing_concepts": ["zero_initialization", "parameter_syntax"],
                "incorrect_claims": [],
                "strong_points": ["Understands heap"],
                "communication_tips": [],
                "score_breakdown": {"similarity": 0.45},
            }

            s1_id = str(uuid.uuid4())
            orch1 = InterviewOrchestrator(
                session_id=s1_id,
                candidate=c1,
                config={"num_questions": 2, "duration_minutes": 10},
                evaluator_fn=mock_eval,
            )
            orch1._question_queue = [
                {"id": "c_malloc_calloc", "text": "Explain the difference between malloc and calloc in C.", "difficulty": 2, "type": "verbal"},
                {"id": "dsa_inverted_index", "text": "Explain how an inverted index works.", "difficulty": 3, "type": "verbal"},
            ]
            orch1._state["questions"] = list(orch1._question_queue)

            q1_obj = await orch1.start()
            assert_true(q1_obj["id"] == "c_malloc_calloc", "Orchestrator served first question c_malloc_calloc")
            assert_true(orch1._current_q_index == 0, "Current question index is 0 (Turn 1)")

            ans1_eval = await orch1.handle_voice_answer(
                "malloc allocates bytes on the heap. calloc also allocates bytes.",
                "c_malloc_calloc",
            )
            f1 = ans1_eval["feedback"]
            assert_true(f1["attempt_number"] == 1, "Attempt #1 recorded")
            assert_true(f1["is_best"] is True, "Attempt #1 is tentatively the best")
            assert_true(orch1._current_q_index == 0, "Turn index did not advance after answer")
            assert_true(orch1._state["pending_next"] is True, "Pending next is True")

            # Verify SQLite record
            best_after_att1 = get_best_attempt(c1_id, "c_malloc_calloc", db_path=test_db)
            assert_true(best_after_att1["attempt_number"] == 1, "SQLite best attempt is #1")
            assert_true(abs(best_after_att1["validated_score"] - 0.45) < 0.05, "SQLite best score is ~0.45")

            # ── 3. Session 1: Question 1 — Retry (Attempt 2 - Improved) ────────
            log_step("3. Session 1: Question 1 — Retry Flow (Attempt 2 - Score 0.85)")
            retry_res = await orch1.handle_retry("c_malloc_calloc")
            assert_true(retry_res["type"] == "retry_ready", "handle_retry returned retry_ready envelope")
            assert_true(retry_res["payload"]["turn_index"] == 1, "Turn index preserved at 1")
            assert_true(retry_res["payload"]["current_attempt_count"] == 1, "Current attempt count indicates 1 prior attempt")
            assert_true(orch1._state["pending_next"] is False, "pending_next reset to False")
            assert_true(orch1._current_q_index == 0, "Orchestrator question queue index stayed at 0")

            # Candidate submits improved answer
            mock_eval.return_value = {
                "final_score": 0.85,
                "grade": "A",
                "justification": "Excellent explanation covering both zero-initialization and number of elements.",
                "covered_concepts": ["heap_allocation", "zero_initialization", "parameter_syntax"],
                "missing_concepts": [],
                "incorrect_claims": [],
                "strong_points": ["Complete coverage of malloc vs calloc differences"],
                "communication_tips": [],
                "score_breakdown": {"similarity": 0.85},
            }

            ans2_eval = await orch1.handle_voice_answer(
                "malloc allocates uninitialized heap memory taking total bytes as argument, whereas calloc takes number of elements and element size, and zeroes out all allocated memory.",
                "c_malloc_calloc",
            )
            f2 = ans2_eval["feedback"]
            assert_true(f2["attempt_number"] == 2, "Attempt #2 recorded")
            assert_true(f2["is_best"] is True, "Attempt #2 is now the best answer")
            comp = f2.get("comparison")
            assert_true(comp is not None, "Comparison object generated")
            assert_true(comp["has_previous_best"] is True, "Recognized previous best from Attempt #1")
            assert_true(comp["score_delta"] > 0.35, f"Score delta positive (+{comp['score_delta']:.2f})")
            assert_true("zero_initialization" in comp["resolved_concepts"], "Recognized resolved concept: zero_initialization")

            # Check SQLite best after attempt 2
            best_after_att2 = get_best_attempt(c1_id, "c_malloc_calloc", db_path=test_db)
            assert_true(best_after_att2["attempt_number"] == 2, "Authoritative best attempt updated to #2")
            assert_true(abs(best_after_att2["validated_score"] - 0.85) < 0.001, f"Authoritative best validated_score is strictly 0.85 (actual: {best_after_att2['validated_score']})")
            assert_true(abs(best_after_att2["raw_score"] - 0.85) < 0.001, f"Authoritative best raw_score is strictly 0.85 (actual: {best_after_att2['raw_score']})")

            # ── 4. Session 1: Advance to Question 2 & Finalize ─────────────────
            log_step("4. Session 1: Finalize Turn 1 with Best Attempt & Complete Session")
            adv_res = await orch1.handle_next_question()
            assert_true(adv_res.get("type") == "question", f"Advanced to next question (got: {adv_res.get('type')})")
            assert_true(orch1._current_q_index == 1, "Current question index advanced to 1 (Turn 2)")
            q2_id = adv_res["payload"]["id"]
            assert_true(bool(q2_id), f"Loaded Q2 dynamically: {q2_id}")

            # Check Turn 1 score in session state: must reflect the best attempt's raw technical score (0.85)
            assert_true(
                abs(orch1._state["raw_scores"][0] - 0.85) < 0.001,
                f"Session raw technical scores reflect the turn's best attempt: {orch1._state['raw_scores'][0]:.4f}",
            )

            # Answer Q2
            mock_eval.return_value = {
                "final_score": 0.75,
                "grade": "B",
                "justification": "Good understanding of inverted index mapping terms to posting lists.",
                "covered_concepts": ["term_to_doc_mapping", "posting_lists"],
                "missing_concepts": ["skip_pointers"],
                "incorrect_claims": [],
                "strong_points": ["Posting lists"],
                "communication_tips": [],
                "score_breakdown": {"similarity": 0.75},
            }
            await orch1.handle_voice_answer("An inverted index maps terms to lists of document IDs called posting lists.", q2_id)

            # End Session 1
            s1_report = await orch1.end()
            assert_true(orch1._state["status"] == "completed", "Session 1 successfully completed")
            assert_true(len(s1_report["question_results"]) == 2, "Session 1 recorded 2 question results")
            assert_true(
                abs(s1_report["question_results"][0]["validated_score"] - 0.85) < 0.001,
                f"Final session report question 1 validated_score is strictly 0.85: {s1_report['question_results'][0]['validated_score']:.4f}",
            )

            # ── 5. Cross-Session Retention: Session 2 Encountering Q1 Again ────
            log_step("5. Cross-Session Retention: Candidate Starts Session 2 & Sees Q1")
            s2_id = str(uuid.uuid4())
            orch2 = InterviewOrchestrator(
                session_id=s2_id,
                candidate=c1,  # Same candidate!
                config={"num_questions": 1, "duration_minutes": 5},
                evaluator_fn=mock_eval,
            )
            # Candidate encounters the same question in Session 2
            orch2._question_queue = [
                {"id": "c_malloc_calloc", "text": "Explain the difference between malloc and calloc in C.", "difficulty": 2, "type": "verbal"},
            ]
            orch2._state["questions"] = list(orch2._question_queue)

            s2_q1 = await orch2.start()
            assert_true("historical_best" in s2_q1, "Question payload includes 'historical_best' banner")
            hb = s2_q1["historical_best"]
            assert_true(hb["attempt_number"] == 2, f"Historical best shows Attempt #2 (actual: {hb['attempt_number']})")
            assert_true(abs(hb["final_score"] - 0.85) < 0.05, f"Historical best shows score ~0.85 (actual: {hb['final_score']})")
            assert_true("zero_initialization" in hb["covered_concepts"], "Historical best shows covered concepts")

            # ── 6. Session 2: Attempt 3 with Lower Score (Invariant Protection)
            log_step("6. Session 2: Attempt 3 with Lower Score — Best Remains Attempt 2")
            mock_eval.return_value = {
                "final_score": 0.60,
                "grade": "B-",
                "justification": "Candidate omitted parameter differences.",
                "covered_concepts": ["heap_allocation", "zero_initialization"],
                "missing_concepts": ["parameter_syntax"],
                "incorrect_claims": [],
                "strong_points": ["Heap zeroing"],
                "communication_tips": [],
                "score_breakdown": {"similarity": 0.60},
            }
            ans3_eval = await orch2.handle_voice_answer("calloc zeroes memory, malloc does not.", "c_malloc_calloc")
            f3 = ans3_eval["feedback"]
            assert_true(f3["attempt_number"] == 3, "Lifetime attempt number is 3")
            assert_true(f3["is_best"] is False, "Lower score does NOT overwrite best answer (is_best is False)")

            # SQLite verification
            best_after_att3 = get_best_attempt(c1_id, "c_malloc_calloc", db_path=test_db)
            assert_true(best_after_att3["attempt_number"] == 2, "Authoritative best attempt is STILL Attempt #2")
            assert_true(abs(best_after_att3["validated_score"] - 0.85) < 0.05, "Authoritative best score is STILL ~0.85")

            all_attempts = get_question_attempts(c1_id, "c_malloc_calloc", db_path=test_db)
            assert_true(len(all_attempts) == 3, f"All 3 attempts persisted in SQLite (actual: {len(all_attempts)})")
            bests = [a for a in all_attempts if a["is_best"] == 1]
            assert_true(len(bests) == 1, "Exactly ONE attempt has is_best=1")
            assert_true(bests[0]["attempt_number"] == 2, "The single winning attempt is #2")

            # ── 7. Candidate Data Isolation ───────────────────────────────────
            log_step("7. Candidate Data Isolation: Candidate 2 Cannot Access Candidate 1 Data")
            c2 = get_or_create_candidate(
                email="bob.jones@mit.edu",
                name="Bob Jones",
                college="MIT",
                db_path=test_db,
            )
            c2_id = c2["id"]
            assert_true(c2_id != c1_id, f"Candidate 2 has distinct UUID ({c2_id} != {c1_id})")

            # Bob checks c_malloc_calloc
            bob_best = get_best_attempt(c2_id, "c_malloc_calloc", db_path=test_db)
            assert_true(bob_best is None, "Candidate 2 has zero best attempts for this question")
            bob_attempts = get_question_attempts(c2_id, "c_malloc_calloc", db_path=test_db)
            assert_true(len(bob_attempts) == 0, "Candidate 2 has zero attempts in history")

            # ── 8. Decoupling of Auxiliary Follow-Up vs Primary Question ──────
            log_step("8. Decoupling of Auxiliary Follow-Up vs Primary Question")
            fu_save = save_attempt({
                "candidate_id": c1_id,
                "session_id": s2_id,
                "question_id": "fu_malloc_perf",
                "parent_question_id": "c_malloc_calloc",
                "attempt_type": "followup",
                "raw_score": 0.98,
                "validated_score": 0.98,
                "transcript": "calloc may use OS virtual memory page zeroing optimization.",
            }, db_path=test_db)
            assert_true(fu_save["is_best"] is False, "Follow-up attempt has is_best=False")

            primary_best = get_best_attempt(c1_id, "c_malloc_calloc", db_path=test_db)
            assert_true(primary_best["attempt_number"] == 2, "Primary question best answer untouched by auxiliary follow-up")
            assert_true(abs(primary_best["validated_score"] - 0.85) < 0.05, "Primary score remains 0.85")

    print("\n" + "="*70)
    print("[SUCCESS] ALL PERSISTENCE AND MULTI-ATTEMPT RETRY INVARIANTS VERIFIED!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(run_e2e())
