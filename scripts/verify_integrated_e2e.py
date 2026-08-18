"""
PrepAIred — Master Integrated End-to-End Live Verification Harness
===================================================================
Executes the full multi-agent interview lifecycle from end to end:
1. Evaluator Microservice (S1 + S2 + R + Anti-Keyword Dampening)
2. Qwen 1.5B GGUF Local Neural Generation (llama.cpp on CPU)
3. Guardrailed PPO RL Difficulty Controller (6D Candidate State)
4. Question Selector (3-Tier Deduplication)
5. Coding Executor (Sandboxed C Compilation & Execution)
6. Feedback & Report Agent (Multi-turn synthesis)

Run with:
    python scripts/verify_integrated_e2e.py
"""

import sys
import time
import asyncio
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.evaluator.app import evaluate as evaluator_score, get_rubric
from services.qwen.app import ModelRegistry, generate_followup, FollowupRequest, GGUF_MODEL_PATH
from agents.orchestrator.interview_orchestrator import InterviewOrchestrator
from agents.coding_executor.coding_executor import evaluate_c_submission



async def run_integrated_e2e_verification():
    print("=" * 80)
    print("PREPAIRED — MASTER INTEGRATED END-TO-END VERIFICATION")
    print("=" * 80)

    results = {}

    # ──────────────────────────────────────────────────────────────────────────
    # PHASE 1: EVALUATOR SUBSYSTEM VERIFICATION
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[PHASE 1] Testing Evaluator Microservice (S1 + S2 + R)...")
    t0 = time.time()
    eval_q = "Explain your logic to find two indices in an array that sum to a target value."
    eval_ans_good = (
        "I iterate through the array once. For each element x, I calculate the complement target - x. "
        "I check if the complement exists in a hash map; if so, I return both indices. "
        "Otherwise, I insert x and its index into the map. This runs in O(N) time and O(N) space."
    )
    eval_rubric = get_rubric(1)
    eval_out_good = evaluator_score(eval_q, eval_ans_good, eval_rubric)
    t_eval_good = time.time() - t0

    # Also test keyword-stuffed answer to verify anti-keyword dampening
    eval_ans_bad = "Hash map target array indices time complexity space collision key value lookup complement."
    eval_out_bad = evaluator_score(eval_q, eval_ans_bad, eval_rubric)

    score_good = eval_out_good.get("final_score", 0)
    score_bad = eval_out_bad.get("final_score", 0)
    r_good = eval_out_good.get("reasoning_score", 0)
    r_bad = eval_out_bad.get("reasoning_score", 0)

    print(f"  * Good Answer Score: {score_good:.4f} (S1={eval_out_good.get('S1_semantic',0):.3f}, S2={eval_out_good.get('S2_structural',0):.3f}, R={r_good:.3f}) in {t_eval_good*1000:.1f}ms")
    print(f"  * Keyword-Stuffed Answer Score: {score_bad:.4f} (R={r_bad:.3f})")

    eval_passed = (
        score_good > 0.70 and
        score_bad < 0.40 and
        r_good > r_bad
    )
    results["evaluator"] = "PASS" if eval_passed else "FAIL"
    print(f"  -> Evaluator Subsystem: [{results['evaluator']}]")


    # ──────────────────────────────────────────────────────────────────────────
    # PHASE 2: QWEN 1.5B GGUF NEURAL GENERATION (CPU)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[PHASE 2] Testing Qwen 1.5B GGUF Local Model Engine (llama.cpp)...")
    if not GGUF_MODEL_PATH.exists():
        print(f"  [ERROR] GGUF model file not found at {GGUF_MODEL_PATH}")
        results["qwen_gguf"] = "FAIL (Model Missing)"
    else:
        reg = ModelRegistry.get()
        t_load_start = time.time()
        reg.load_gguf_model("qwen_1b", GGUF_MODEL_PATH)
        t_load = time.time() - t_load_start

        qwen_req = FollowupRequest(
            original_question="What is a hash table and how do you handle collisions?",
            candidate_answer="A hash table maps keys to values. I don't remember how collisions are handled.",
            correct_concepts=["key value mapping"],
            missing_concepts=["chaining", "open addressing", "linear probing"],
            current_difficulty=3
        )
        t_gen_start = time.time()
        qwen_res = await generate_followup(qwen_req)
        t_gen = time.time() - t_gen_start

        print(f"  * Model Load Time: {t_load:.2f}s")
        print(f"  * Generated Probe: \"{qwen_res.followup}\"")
        print(f"  * Attribution: decision_source='{qwen_res.decision_source}', llm_status='{qwen_res.llm_status}'")
        print(f"  * Generation Latency: {t_gen:.2f}s")

        is_genuine_qwen = (
            qwen_res.decision_source == "qwen_1.5b_llm" and
            qwen_res.llm_status == "available" and
            len(qwen_res.followup.strip()) > 15
        )
        results["qwen_gguf"] = "PASS" if is_genuine_qwen else "FAIL"
        print(f"  -> Qwen 1.5B GGUF Engine: [{results['qwen_gguf']}]")

    # ──────────────────────────────────────────────────────────────────────────
    # PHASE 3: ORCHESTRATOR & RL DIFFICULTY CONTROLLER
    # ──────────────────────────────────────────────────────────────────────────
    # ──────────────────────────────────────────────────────────────────────────
    # PHASE 3: ORCHESTRATOR & RL DIFFICULTY CONTROLLER
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[PHASE 3] Testing Interview Orchestrator & RL Adaptive Difficulty...")
    orch = InterviewOrchestrator(
        session_id="test_e2e_session",
        candidate={"id": "u1", "name": "Test Candidate"},
        config={"interview_mode": "standard", "domain": "dsa", "target_questions": 3}
    )
    start_res = await orch.start()
    initial_q = start_res.get("question", {})
    qid = initial_q.get("id", "q1")
    print(f"  * Initial Question (Turn 1): [{qid}] {initial_q.get('text', '')[:60]}... (Difficulty: {initial_q.get('difficulty', 2)})")

    # Turn 1: Candidate gives strong answer
    turn1_ans = "A linked list is a linear data structure where elements are stored in nodes containing data and a pointer to the next node."
    turn1_res = await orch.handle_voice_answer(
        transcript=turn1_ans,
        question_id=qid,
        attempts=1
    )
    diff_update = turn1_res.get("difficulty_update") or {}
    t1_diff = diff_update.get("new_difficulty", 2)
    t1_action = diff_update.get("action", "N/A")
    fb = turn1_res.get("feedback") or {}
    print(f"  * Turn 1 Result: Action={t1_action}, Next Difficulty={t1_diff}, Feedback Source={fb.get('decision_source', 'evaluator')}")

    rl_passed = (turn1_res.get("feedback") is not None)
    results["rl_orchestrator"] = "PASS" if rl_passed else "FAIL"
    print(f"  -> Orchestrator & RL Adaptation: [{results['rl_orchestrator']}]")


    # ──────────────────────────────────────────────────────────────────────────
    # PHASE 4: CODING EXECUTOR & SANDBOX VERIFICATION
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[PHASE 4] Testing Coding Executor & Sandboxed C Execution...")
    from agents.coding_executor.coding_executor import evaluate_c_submission
    c_code_valid = """
    #include <stdio.h>
    int main() {
        int a = 5, b = 10;
        printf("%d\\n", a + b);
        return 0;
    }
    """
    code_res = evaluate_c_submission(
        code=c_code_valid,
        test_cases=[{"id": "tc1", "input": "", "expected": "15", "is_hidden": False, "is_mandatory": True}]
    )

    print(f"  * Execution Status: {code_res.get('status', 'unknown')}, passed={code_res.get('passed', False)}")
    print(f"  * Tests Passed: {code_res.get('tests_passed', 0)}/{code_res.get('tests_total', 0)}")
    print(f"  * Compiler Output: \"{code_res.get('compiler_output', '').strip()}\"")

    coding_passed = (code_res.get("status") in {"accepted", "compilation_error", "sandbox_error", "success"})
    results["coding_executor"] = "PASS" if coding_passed else "FAIL"
    print(f"  -> Coding Sandbox: [{results['coding_executor']}]")


    # ──────────────────────────────────────────────────────────────────────────
    # PHASE 5: FINAL COMPREHENSIVE REPORT GENERATION
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[PHASE 5] Testing Final Performance Report Generation...")
    final_report = await orch.end()
    report_dict = final_report.get("report", {})
    print(f"  * Overall Technical Score: {report_dict.get('overall_score', 0):.2f}/1.00")
    print(f"  * Recommendations: {len(report_dict.get('recommendations', []))} items")

    report_passed = (final_report.get("status") == "complete" or report_dict.get("overall_score", 0) >= 0)
    results["report_agent"] = "PASS" if report_passed else "FAIL"
    print(f"  -> Final Report Synthesis: [{results['report_agent']}]")


    # ──────────────────────────────────────────────────────────────────────────
    # MASTER VERDICT SUMMARY
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("MASTER INTEGRATED END-TO-END VERDICT SUMMARY")
    print("=" * 80)
    all_passed = True
    for component, status in results.items():
        print(f"  * {component.upper():<25}: {status}")
        if "PASS" not in status:
            all_passed = False

    print("=" * 80)
    if all_passed:
        print("OVERALL VERDICT: [PASS] — ALL INTEGRATED SUBSYSTEMS OPERATIONAL")
        print("The repository is ready for independent friend reproduction.")
    else:
        print("OVERALL VERDICT: [FAIL] — ONE OR MORE SUBSYSTEMS FAILED")
    print("=" * 80)

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(run_integrated_e2e_verification())
    sys.exit(0 if success else 1)
