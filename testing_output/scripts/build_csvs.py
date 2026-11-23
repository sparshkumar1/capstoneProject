"""Builds the four required CSV deliverables from this exercise's actual
results (testing_output/results_raw.json) plus the pre-existing suites'
logged outcomes. Read-only with respect to application source."""
import csv
import json
from pathlib import Path

ROOT = Path(r"D:\Capstone_29_AUG\capstoneProject")
OUT = ROOT / "testing_output"
raw = json.loads((OUT / "results_raw.json").read_text(encoding="utf-8"))

# ---- fix the one ID collision + reclassify MOD-AUD-001 per report Ch.10.4 ----
by_id_seen = {}
rows = []
for r in raw:
    rid = r["id"]
    if rid == "MOD-EVAL-001" and r["description"] == "Evaluator health":
        rid = "MOD-EVAL-HEALTH"
    status = r["status"]
    if r["id"] == "MOD-AUD-001":
        status = "FAIL"  # reclassified, see report Chapter 10.4
    rows.append({**r, "id": rid, "status": status})

# ---- VALID/TIMER module script results ----
valid_timer_path = OUT / "Testing_Evidence" / "MOD-VALID-TIMER_results.json"
vt = json.loads(valid_timer_path.read_text(encoding="utf-8")) if valid_timer_path.exists() else []
# Use the corrected (second) run results if present; the run script overwrites the same file,
# so this already reflects the corrected, final run.

# ========================= 1. Testing_Results_Master.csv =========================
master_path = OUT / "Testing_Results_Master.csv"
with open(master_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["test_id", "category", "module", "description", "status", "notes", "evidence_file"])
    for r in rows:
        cat = "Integration" if (r["id"].startswith("INT-") or r["id"] in ("NEG-001", "NEG-002", "MOD-QWEN-002") or r["id"] == "E2E-006") else (
              "Performance" if r["id"].startswith("PERF-") else
              "Negative" if r["id"].startswith("NEG-") else "Module")
        w.writerow([r["id"], cat, r["module"], r["description"], r["status"], r.get("notes", ""), r.get("evidence_file", "")])
    for v in vt:
        w.writerow([v["id"], "Module", "Score Validator / Question Timer (new)", v["description"], v["status"], v["detail"][:300], "Testing_Evidence/MOD-VALID-TIMER_results.json"])
    # Pre-existing suites, re-run fresh -- summarized (full per-test detail in the referenced logs)
    legacy = [
        ("T-N02-01..10", "Module", "Strategy (PPO)", "RL checkpoint sanity, 10 constructed candidate-state scenarios", "PASS (10/10)", "Re-run fresh, identical to prior recorded result", "testing_output/logs/rl_T-N02_fresh.log"),
        ("T-N03-01..13", "Module", "Strategy (Guardrails)", "Guardrail boundary verification, 13 constructed states incl. the previously-fixed G5 gap", "PASS (13/13)", "Re-run fresh, identical to prior recorded result; confirms no regression", "testing_output/logs/rl_T-N03_fresh.log"),
        ("T-N06-01..10", "Module", "Evaluator", "Adversarial/edge-case input battery, 10 cases", "PASS (10/10)", "Re-run fresh, identical to prior recorded result", "testing_output/logs/eval_T-N06_fresh.log"),
        ("T-N04-01..07", "Integration", "Evaluator API", "Flask API contract, 7 checks", "PASS (7/7)", "Re-run fresh, identical to prior recorded result", "testing_output/logs/api_T-N04_fresh.log"),
        ("T-N10-01..11", "Module", "Question Selector", "Difficulty-matching + topic-rotation correctness, 11 checks", "PASS (11/11)", "Re-run fresh, identical to prior recorded result", "testing_output/logs/qs_T-N10_fresh.log"),
        ("PYTEST-SUITE", "Module+Integration", "Backend (full suite)", "25-file backend automated suite, 298 collected tests", "264 passed, 19 failed, 15 skipped", "Re-run fresh; identical split to prior documented baseline; every failure individually attributed, see Chapter 11.5", "testing_output/logs/full_pytest_run.log"),
        ("VITEST-SUITE", "Module", "Frontend", "4-file Vitest component suite, 28 tests", "PASS (28/28)", "Re-run fresh, identical to prior baseline", "testing_output/logs/vitest_run.log"),
    ]
    for lid, cat, mod, desc, status, notes, ev in legacy:
        w.writerow([lid, cat, mod, desc, status, notes, ev])
print(f"Wrote {master_path}")

# ========================= 2. Module_Test_Coverage.csv =========================
module_rows = [
    ("MOD-FE", "Frontend SPA", "apps/web/src/*", 28, 28, "Component-level: full; browser/pixel-level: not performed this exercise"),
    ("MOD-BE", "Backend orchestration layer", "apps/backend/main.py", 9, 9, "All tested routes correct except the WS request_hint gap (tracked under MOD-QWEN/Integration)"),
    ("MOD-ORCH", "Interview Orchestrator", "agents/orchestrator/interview_orchestrator.py", 6, 6, "Exercised via live WS integration flow"),
    ("MOD-QS", "Question Selector", "agents/question_selector/question_selector.py", 11, 11, "Re-run fresh (T-N10) + confirmed live via INT-001/005"),
    ("MOD-AUD", "Audio/STT pipeline", "agents/audio/*", 3, 2, "1 FAIL (real transcription unavailable, WhisperX not installed); 2 diagnostic confirmations"),
    ("MOD-EVAL", "Composite Evaluator", "services/evaluator/app.py", 19, 19, "10 adversarial + 7 API contract (both re-run fresh) + 2 live-scoring confirmations"),
    ("MOD-QWEN", "Qwen feedback/hint service", "services/qwen/app.py", 4, 3, "1 FAIL (WS request_hint dispatch gap, DEF-001)"),
    ("MOD-PPO", "Strategy layer (PPO + guardrails)", "agents/strategy/hybrid_orchestrator.py, rl/guardrails.py", 25, 25, "10+13 re-run fresh (T-N02/T-N03), 0 mismatches; 2 live confirmations"),
    ("MOD-SBX", "Coding Sandbox (Docker)", "agents/coding_executor/*", 2, 1, "1 BLOCKED (Docker daemon unreachable); 1 PASS (orchestrator handling of the blocked state)"),
    ("MOD-DB", "Persistence (SQLite)", "services/storage/database.py", 2, 2, "Referential integrity + real write-growth confirmed"),
    ("MOD-REPORT", "Reporting/Analytics", "services/storage/analytics.py", 2, 2, "Report content matches actual session turns"),
    ("MOD-ADMIN", "Admin dashboard (backend)", "apps/backend/main.py admin routes", 2, 2, "Confirmed reads in-memory session dict (known characteristic, not a new defect)"),
    ("MOD-VALID", "Score Validator", "agents/validation/score_validator.py", 7, 7, "New module, previously untested; all cases pass"),
    ("MOD-TIMER", "Question Timer", "agents/timing/timer.py", 6, 6, "New module, previously untested; all cases pass after this exercise's own test-script self-correction"),
]
with open(OUT / "Module_Test_Coverage.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["module_id", "module_name", "main_files", "test_cases_executed", "test_cases_passed", "observations"])
    for row in module_rows:
        w.writerow(row)
print("Wrote Module_Test_Coverage.csv")

# ========================= 3. Integration_Test_Coverage.csv =========================
int_rows = [
    ("INT-001", "Frontend-protocol<->Backend<->Orchestrator<->Question Selector", "WS 'start' -> first question", "PASS"),
    ("INT-002", "Orchestrator<->Evaluator(S1+S2+R)<->Strategy/Guardrails", "WS 'voice_answer' (strong answer) -> scored feedback", "PASS"),
    ("INT-003", "Orchestrator<->Evaluator<->Strategy/Guardrails (adaptive path)", "WS 'voice_answer' (weak answer) -> low score + difficulty decision", "PASS"),
    ("MOD-QWEN-002", "Orchestrator<->Qwen (HTTP :8001)", "WS 'request_hint' -> expected hint message", "FAIL (DEF-001)"),
    ("INT-004", "Orchestrator<->Coding Sandbox (Docker)", "WS 'code_submission' while Docker unreachable", "BLOCKED (handling itself PASS)"),
    ("INT-005", "Orchestrator<->Question Selector", "WS 'next_question' -> distinct next question", "PASS"),
    ("INT-006", "Orchestrator<->Reporting", "WS 'end_session' -> report id", "PASS"),
    ("INT-007", "Backend<->Database", "GET history reflects persisted attempts", "PASS"),
    ("E2E-006", "Orchestrator/Reporting<->Database<->API", "GET session report matches actual turns", "PASS"),
    ("NEG-001", "Backend<->WS session validation", "WS connect to nonexistent session_id", "PASS"),
    ("NEG-002", "Backend<->WS input validation", "Malformed JSON over open WS", "PASS"),
]
with open(OUT / "Integration_Test_Coverage.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["test_id", "integration_boundary", "scenario", "status"])
    for row in int_rows:
        w.writerow(row)
print("Wrote Integration_Test_Coverage.csv")

# ========================= 4. E2E_Test_Results.csv =========================
e2e_rows = [
    ("E2E-01", "Complete interview lifecycle", "PASS", "1 embedded, separately-counted defect (MOD-QWEN-002); all other steps correct"),
    ("E2E-02", "Audio-based interview", "BLOCKED", "WhisperX not installed; transcription step produces no transcript (DEF-002)"),
    ("E2E-03", "Text-based interview", "PASS", "Same verbal-answer path as E2E-01"),
    ("E2E-04", "Adaptive interview (state->PPO->guardrail->next question)", "PASS", "Strong/weak answers produced consistent, guardrail-verified difficulty decisions"),
    ("E2E-05", "Failure and recovery", "PARTIAL", "3 of 7 sub-scenarios executed (invalid input, and 2 unintentional-but-informative dependency-failure cases); 4 disclosed as not executed"),
    ("E2E-06", "Session and report consistency", "PASS", "Report content matches actual session turns"),
    ("E2E-07", "Repeated sessions", "NOT FULLY EXECUTED", "Only 1 of N sessions run in this exercise; cross-session isolation not directly re-verified"),
]
with open(OUT / "E2E_Test_Results.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["scenario_id", "scenario_name", "status", "notes"])
    for row in e2e_rows:
        w.writerow(row)
print("Wrote E2E_Test_Results.csv")
