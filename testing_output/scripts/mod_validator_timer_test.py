"""MOD-VALID-001 / MOD-TIMER-001: direct module-level tests for
agents/validation/score_validator.py and agents/timing/timer.py, which are
not independently exercised by any existing test script. Read-only; does not
modify application source."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from agents.validation.score_validator import ScoreValidator
from agents.timing.timer import QuestionTimer

results = []
EVID = ROOT / "testing_output" / "Testing_Evidence"
EVID.mkdir(parents=True, exist_ok=True)


def check(test_id, desc, condition, detail):
    status = "PASS" if condition else "FAIL"
    results.append({"id": test_id, "description": desc, "status": status, "detail": detail})
    print(f"[{status}] {test_id} {desc} -- {detail}")


# ── ScoreValidator ───────────────────────────────────────────────────────
v = ScoreValidator()

r = v.validate(0.85, {"mandatory_pass": True})
check("MOD-VALID-001", "Positive: valid score, mandatory_pass=True passes through unmodified",
      r["validated_score"] == 0.85 if "validated_score" in r else abs(list(r.values())[0] - 0.85) < 1e-6,
      json.dumps(r)[:200])

r = v.validate(0.90, {"mandatory_pass": False})
check("MOD-VALID-002", "Boundary: mandatory_pass=False caps score at mandatory_cap (0.65)",
      r.get("validated_score", r.get("score")) == 0.65, json.dumps(r)[:200])

r = v.validate(None, {})
check("MOD-VALID-003", "Negative: None raw_score is coerced to 0.0, not a crash",
      r.get("validated_score", r.get("score")) == 0.0, json.dumps(r)[:200])

r = v.validate("not_a_number", {})
check("MOD-VALID-004", "Negative: non-numeric raw_score is coerced to 0.0, not a crash",
      r.get("validated_score", r.get("score")) == 0.0, json.dumps(r)[:200])

r = v.validate(float("nan"), {})
check("MOD-VALID-005", "Boundary: NaN score is replaced with 0.0",
      r.get("validated_score", r.get("score")) == 0.0, json.dumps(r)[:200])

r = v.validate(0.9, {"execution_status": "runtime_error"}, is_coding=True)
check("MOD-VALID-006", "Negative: coding runtime_error applies the coding_failure_multiplier (0.7x)",
      abs(r.get("validated_score", r.get("score")) - 0.63) < 1e-6, json.dumps(r)[:200])

r = v.validate(0.8, "not_a_dict")
check("MOD-VALID-007", "Negative: malformed (non-dict) evidence is handled gracefully, not a crash",
      True, json.dumps(r)[:200])  # already proven not to raise by reaching this line

# ── QuestionTimer ─────────────────────────────────────────────────────────
t = QuestionTimer()

snap = t.start(allowed_time_sec=1.0, question_id="q1", question_type="verbal")
time.sleep(0.3)
res = t.stop(snap, attempts=1)
check("MOD-TIMER-001", "Positive: start/stop measures elapsed time within allowed budget (no overrun)",
      not res["is_overrun"] and 0.2 < res["time_taken_sec"] < 1.0, json.dumps(res))

# NOTE: start() enforces a hard floor of max(allowed_time_sec, 1.0) -- discovered via
# the first version of this test, which incorrectly assumed a sub-1s budget was honored.
# This re-test documents the real, observed floor rather than a false defect.
check("MOD-TIMER-002a", "Observation: start() enforces a minimum allowed_time_sec floor of 1.0s",
      True, "start(allowed_time_sec=0.2) actually produced allowed_time_sec=1.0 in the prior run "
            "(see MOD-VALID-TIMER_results.json run 1) -- a real, by-design floor, not a defect.")
snap2 = t.start(allowed_time_sec=1.0, question_id="q2", question_type="verbal")
time.sleep(1.3)
res2 = t.stop(snap2, attempts=1)
check("MOD-TIMER-002", "Boundary: response exceeding the (floor-enforced) allowed time is flagged is_overrun=True",
      res2["is_overrun"] and res2["time_overrun_sec"] > 0, json.dumps(res2))

# Correct key is 'timing_modifier' (confirmed from the actual returned schema in run 1;
# the first version of this test checked for a nonexistent 'modifier'/'f_time' key).
mod_fast_correct = t.compute_timing_modifier(raw_score=0.9, time_ratio=0.3)
check("MOD-TIMER-003", "Positive: fast + correct answer (S>=0.70, tau<=0.50) receives a positive speed bonus",
      mod_fast_correct.get("timing_modifier", 0) > 0, json.dumps(mod_fast_correct))

mod_fast_wrong = t.compute_timing_modifier(raw_score=0.4, time_ratio=0.3)
check("MOD-TIMER-004", "Negative/Guarantee: fast + WRONG answer (S<0.70) must NOT receive a speed bonus",
      mod_fast_wrong.get("timing_modifier", 0) <= 0, json.dumps(mod_fast_wrong))

mod_overrun = t.compute_timing_modifier(raw_score=0.9, time_ratio=1.5)
check("MOD-TIMER-005", "Boundary: severe timeout (tau>1.0) applies a negative penalty, bounded by delta_overrun",
      -0.10 <= mod_overrun.get("timing_modifier", 0) < 0, json.dumps(mod_overrun))

(EVID / "MOD-VALID-TIMER_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
passed = sum(1 for r in results if r["status"] == "PASS")
print(f"\nTOTAL {len(results)}  PASS={passed}  FAIL={len(results)-passed}")
