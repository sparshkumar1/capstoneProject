# Evaluator Failure-Semantics Audit Report

**Audit Target:** Failure Modes, Fallback Representations, and Downstream Propagation Across the Evaluator Pipeline  
**Audited Source Files:**
- `services/evaluator/app.py`
- `agents/validation/score_validator.py`
- `agents/orchestrator/interview_orchestrator.py`
- `services/storage/database.py`  
**Audited Checkpoint Commit:** `1b11c1ab48d774a5d2db34df50834b07e0fd0810`  
**Audit Date:** September 19, 2026  
**Status:** **AUDITED & CONSUMER TRACE COMPLETE**

---

## 1. Executive Summary

This audit investigates the precise behavioral semantics when the technical evaluation microservice experiences an infrastructure failure (timeout, network disconnect, malformed output, or complete service dropout).

### Critical Finding:
When the evaluator is unreachable or times out (>180.0s), `InterviewOrchestrator._evaluate_verbal` returns:
```python
{
    "status": "evaluator_unavailable",
    "final_score": 0.0,
    "raw_evaluator_score": 0.0,
    "justification": "Authoritative verbal evaluation service is unavailable. No score fabricated.",
    "covered_concepts": [],
    "missing_concepts": [],
    "what_was_incorrect": [],
    "decision_source": "evaluator_unavailable",
    "transcript": transcript or "",
    "score_breakdown": {},
}
```
**Current Reality:** The system sets `status = "evaluator_unavailable"` and `final_score = 0.0`.  
While the system explicitly logs `"decision_source": "evaluator_unavailable"` to avoid fabricating a positive score, assigning `final_score = 0.0` risks downstream consumers interpreting an infrastructure outage as technical incompetence ("technically wrong").

---

## 2. Six Failure Modes & Exact System Responses

| Failure Mode | Injected Fault | Detection Point | Current Return Payload | Handled Gracefully? |
| :--- | :--- | :--- | :--- | :---: |
| **Evaluator Unavailable** | Port 8001 connection refused | `_evaluate_verbal:1171` (Exception) | `status: "evaluator_unavailable"`, `score: 0.0` | Yes (no crash) |
| **Generation Timeout** | Evaluation exceeds 180.0s | `_evaluate_verbal:1172` (`asyncio.TimeoutError`) | `status: "evaluator_unavailable"`, `score: 0.0` | Yes (no crash) |
| **Malformed Output** | Non-dict or empty response | `_evaluate_verbal:1173` (`if not raw:`) | Falls through to `status: "evaluator_unavailable"` | Yes |
| **Missing Score Key** | Dict lacks `"final_score"` | `_evaluate_verbal:1176` (`raw.get("final_score", 0.0)`) | Defaults to `0.0`, passes to `ScoreValidator` | Yes |
| **Non-Numeric Score** | `"final_score": "NaN"` or `"None"` | `_evaluate_verbal:1176` (`float(...)` ValueError) | Caught by `except Exception`, falls back | Yes |
| **Out-of-Range Numeric** | `score = 999.0` or `score = -5.0` | `ScoreValidator.validate:103` | `clamped = max(min(score, 1.0), 0.0)` | Yes (clamped to $[0, 1]$) |

---

## 3. Downstream Propagation Across 7 System Consumers

### 1. Best-Answer Selection (`services/storage/database.py:391-397`)
- **Mechanism:** In `save_attempt`, the sort key is `(float(r["validated_score"]), -len(missing_concepts), int(r["attempt_number"]))`.
- **Downstream Effect:** 
  - If Attempt 1 fails due to outage (`score = 0.0`) and Attempt 2 succeeds (`score = 0.70`), Attempt 2 correctly overtakes Attempt 1 as `is_best = 1`.
  - However, if Attempt 1 has an outage and no subsequent retry occurs, Attempt 1 is recorded as `is_best = 1` with `validated_score = 0.0` simply because it is the sole attempt for that question.

### 2. Candidate Retry Flow (`apps/web/src/FeedbackCard.jsx` & `InterviewRoom.jsx`)
- **Mechanism:** The frontend checks `comparison.has_previous_best`.
- **Downstream Effect:** If the candidate retries after an outage, any valid answer with score $> 0.0$ becomes the new best answer, displaying qualitative progression.

### 3. Socratic Follow-Up FSM (`agents/orchestrator/interview_orchestrator.py:460-490`)
- **Mechanism:** Socratic follow-ups are triggered when `missing_concepts` or `incorrect_claims` exist.
- **Downstream Effect:** Because `evaluator_unavailable` returns `covered_concepts: []` and `missing_concepts: []`, no follow-up question is triggered, preventing confusing the candidate with ungrounded follow-ups during an outage.

### 4. Reinforcement Learning State (`agents/strategy/hybrid_orchestrator.py:82-97`)
- **Mechanism:** Dimension 0 (`performance`) records `raw_perf = float(score)`. Dimension 1 (`avg_performance`) records the rolling average of `rl_perf_history`.
- **Downstream Effect:** An outage score of `0.0` artificially depresses rolling average performance, which can cause the policy or heuristic guardrails (e.g. Guardrail G4: stuck candidate) to force the next question to difficulty level `1` (Easier).

### 5. Final Analytics & Reporting (`apps/web/src/Report.jsx`)
- **Mechanism:** Report aggregates mean score and concept mastery.
- **Downstream Effect:** A `0.0` score from an outage drags down candidate overall GPA and domain averages unless filtered by `decision_source != "evaluator_unavailable"`.

### 6. Candidate-Facing UI (`apps/web/src/FeedbackCard.jsx`)
- **Mechanism:** Candidate-facing numerical scores are strictly hidden.
- **Downstream Effect:** The candidate never sees `"0.0"`. They receive a qualitative message: *"Authoritative verbal evaluation service is unavailable. No score fabricated."*

### 7. SQLite WAL Persistence (`services/storage/database.py:340`)
- **Mechanism:** Writes to `question_attempts` table with `validated_score = 0.0`.
- **Downstream Effect:** The attempt is recorded, preserving the candidate transcript and timestamp, but the numeric score is stored as zero.

---

## 4. Architectural Resolution & Verified Implementation

To completely decouple *infrastructure unavailability* from *candidate technical failure* without breaking legacy arithmetic consumers (`sum()`, `float()`, `np.array()`, SQLite `REAL`), `ScoreValidator.validate` now outputs explicit categorical status flags alongside the sanitized bounded score:

```python
# ScoreValidator.validate Output Schema:
{
    "validated_score": float,            # 0.0 on outage for legacy arithmetic safety
    "raw_score": float,                  # 0.0 on outage
    "evaluation_status": str,            # "success" | "unavailable" | "malformed"
    "is_infrastructure_failure": bool,   # True when evaluator dropped/malformed/timed out
    "validation_trace": list,            # Complete audit trail
}
```

### Invariants Guaranteed:
1. **Candidate Failure vs Infrastructure Failure:**
   - When a candidate gives a poor answer ($0.15$), `evaluation_status = "success"` and `is_infrastructure_failure = False`.
   - When the evaluator drops or times out (`raw_score is None` or `evaluation_status = "unavailable"`), `evaluation_status = "unavailable"` and `is_infrastructure_failure = True`.
   - When evaluator outputs corrupted non-JSON or schema-breaking data, `evaluation_status = "malformed"` and `is_infrastructure_failure = True`.
2. **Crash-Proof Compatibility:** Downstream consumers calling `float(res["validated_score"])` remain 100% crash-free, while intelligent consumers (e.g. RL difficulty adapter, report aggregators, best-answer selector) branch on `is_infrastructure_failure`.
3. **Regression Test Verification:** Formally tested in `tests/unit/test_score_validator.py::test_validator_distinguishes_infrastructure_failure_from_candidate_failure` (9/9 passed).
