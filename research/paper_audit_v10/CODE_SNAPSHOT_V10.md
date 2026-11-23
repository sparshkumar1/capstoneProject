# PREPAIred Code Snapshot & Software Verification Record (V10)

**Date**: 2026-09-30  
**Target Manuscript**: PrepAIred System Architecture & Empirical Evaluation (V10)  
**Authoring & Verification Environment**: Windows 11 | Python 3.12.7 | PyTorch 2.6.0+cu124  

---

## 1. EXACT REPOSITORY AND WORKTREE PROVENANCE

- **Repository Root**: `C:\Users\spars\Downloads\PrepAIred`
- **Authorized Feature Worktree**: `C:\Users\spars\Downloads\PrepAIred\.claude\worktrees\exp032-orchestrator-concept-list-fix`
- **Active Git Branch**: `worktree-exp032-orchestrator-concept-list-fix`
- **Base Commit SHA**: `b4161d9aae222ae92d0a0fc2dd793bc9693345a0`
- **Snapshot Classification**: **Working-Tree Development Snapshot** (contains pre-authorized, uncommitted reliability hardening; not yet merged into `main`).
- **Main Workspace Status**: Working on `workspace/human-eval-clean-push` (HEAD: `8e6cea8`). Zero modifications were made to `main` or unrelated teammate branches.

---

## 2. MODIFIED & AUDITED SOURCE CODE PATHS

In accordance with strict preservation rules, code changes are restricted to the authorized feature worktree:

1. `agents/validation/score_validator.py` (Modified: score type validation, non-finite handling, contradictory status override).
2. `agents/orchestrator/interview_orchestrator.py` (Modified: propagates `evaluation_status` and logs `infrastructure_errors`).
3. `tests/unit/test_score_validator.py` (Modified: regression tests for clamping, missing scores, non-numeric values, and contradictory success labels).
4. `tests/unit/test_evaluator_infrastructure_failure_flag.py` (New test file: end-to-end propagation tests through `_evaluate_verbal`).

---

## 3. CRYPTOGRAPHIC SHA-256 HASHES OF RELEVANT SOURCE FILES

Every load-bearing implementation file described in Manuscript V10 was hashed directly from the filesystem:

| File Path | SHA-256 Checksum | Architectural Function |
|---|---|---|
| `agents/validation/score_validator.py` | `bd4250a9e87b6198796a99824740d6b93561765fa1b545e54e0a055a4d9b5af9` | Deterministic score sanitization, clamping, and infra-failure classification |
| `agents/orchestrator/interview_orchestrator.py` | `303dad61c1ec71e7db88cc40829bcb48143b06224df1cdea39a02c2aa4072ec9` | Session state machine, turn orchestration, and async evaluator bridge |
| `services/evaluator/app.py` | `93cb3432a55e724e226a30debed8314c1eafab79690ace3d15a2a6a8096985ed` | Deployed evaluator microservice (S1 SBERT + S2 FAISS + R CrossEncoder) |
| `services/qwen/app.py` | `13cef913419bc15b1fc91df51a8cd5f3302d2f0ca2b22b10e66d313c384b0f9e` | Local Qwen2.5-1.5B-Instruct LLM runtime (llama.cpp / GGUF Q4_K_M) |
| `rl/env/interview_env.py` | `d776e19d1525091b6dc4fb6a64041a0053d113cbf82b20ba62b587b90ed095f4` | Gymnasium 6D state environment, transition dynamics, and hybrid reward |
| `rl/guardrails.py` | `e6e7b77d4f9b0e40358713e845bfdd96b6f8b54cb97780e5f9a45d477d7c1aa5` | Canonical deterministic pedagogical guardrail hierarchy (G1–G6) |
| `agents/timing/timer.py` | `a8d31bf66b6f118f928b1fa82853d5153bed0b442cb8d00f2c91616bb1a2c4eb` | Monotonic latency timing, pacing score modifier, and fast-wrong immunity |
| `agents/audio/confidence_scorer.py` | `eabeb48c08ad81e70fbedae9d2f47884d963c92b816bfc2306de1fdf0fae0797` | Multi-component acoustic confidence metric (Praat prosody) |
| `agents/audio/hesitation_scorer.py` | `554f899683012e1ab4372187eae5c4db619344451ce5f443dd832412481a73a0` | Dedicated acoustic hesitation scorer (pauses, fillers, pitch instability) |
| `agents/coding_executor/coding_executor.py` | `ed20243d52fe5590f69d87120eb72ab7c6e70a7205857819035e4b792f9e43ef` | Hardened ephemeral Docker C execution sandbox |
| `apps/web/src/FeedbackCard.jsx` | `e975d5fa7049ff56549180c63aeec1dc9b6c980a4df72c563ae1b22e10a1f290` | Candidate feedback view with complete numerical score suppression |
| `tests/unit/test_score_validator.py` | `f9d9460f8dedb0a5df3c284122aa957da8d9b62b434085f9a0d3f75b5aced9e4` | ScoreValidator unit and regression tests (11 tests) |
| `tests/unit/test_evaluator_infrastructure_failure_flag.py` | `b1e0f3ffb3118aebe9f86d88544ca586ad68c02b1e8b01131f5b5816ff27b1d4` | End-to-end evaluator outage propagation tests (5 tests) |

---

## 4. INDEPENDENT INVESTIGATION & RESOLUTION OF THE SCORE-VALIDATION DEFECT

### 4.1 Identified Vulnerability
In previous revisions, if the upstream evaluator service malfunctioned and returned a payload with missing (`final_score: None`), non-numeric (`final_score: "bad"`), or non-finite (`NaN` / `Inf`) values while retaining a default `evaluation_status: "success"` (or omitting an explicit error flag), `ScoreValidator` clamped the numeric value to `0.0`. 
Downstream components (session state, PPO reward calculation, candidate history) interpreted this `0.0` as an ordinary, legitimate candidate failure rather than an infrastructure anomaly.

### 4.2 Exact Call Path
1. `InterviewOrchestrator.handle_voice_answer()` receives candidate audio / transcript.
2. Calls `InterviewOrchestrator._evaluate_verbal(transcript, question)` via thread executor.
3. Upstream evaluator returns raw dict `raw = self._evaluator_fn(transcript, question)`.
4. Orchestrator extracts `rs = raw.get("final_score")` (without defaulting to 0.0) and calls `ScoreValidator.validate(rs, evidence, is_coding=False)`.
5. `ScoreValidator.validate()` executes structural, type, and evidence checks.

### 4.3 Implemented Defensive Logic (`ScoreValidator.validate`)
```python
# 1. Structural / Type Validation
try:
    if raw_score is None:
        invalid_score = True
        score = 0.0
        trace.append({"rule": "missing_score", "before": None, "after": 0.0, "reason": "Raw score was None"})
    else:
        score = float(raw_score)
except (ValueError, TypeError):
    invalid_score = True
    score = 0.0
    trace.append({"rule": "type_error", "before": str(raw_score), "after": 0.0, "reason": "Non-numeric raw score converted to 0.0"})

# 2. Non-finite Numeric Handling
non_finite_score = math.isnan(score) or math.isinf(score)
if non_finite_score:
    trace.append({"rule": "non_finite_score", "before": str(score), "after": 0.0, "reason": "NaN or Inf score replaced with 0.0"})
    score = 0.0

# 3. Contradictory Status Override
if isinstance(evidence, dict) and "evaluation_status" in evidence:
    eval_status = str(evidence["evaluation_status"]).lower()
    is_infra_failure = eval_status in {"unavailable", "evaluator_unavailable", "malformed", "timeout", "error"}
    if non_finite_score and not is_infra_failure:
        eval_status = "non_finite_score"
        is_infra_failure = True
    elif invalid_score and not is_infra_failure:
        eval_status = "invalid_score"
        is_infra_failure = True
elif raw_score is None:
    eval_status = "unavailable"
    is_infra_failure = True
elif non_finite_score:
    eval_status = "non_finite_score"
    is_infra_failure = True
elif invalid_score:
    eval_status = "invalid_score"
    is_infra_failure = True
else:
    eval_status = "success"
    is_infra_failure = False
```

### 4.4 Invariants Enforced
- **Rejection of Invalid Scores**: Missing (`None`), non-numeric strings (`"error"`), complex objects (`{'val': 1}`), and non-finite floats (`NaN`, `+Inf`, `-Inf`) are converted to safe `0.0` and explicitly tagged as `is_infrastructure_failure: True`.
- **Preservation of Genuine Zero**: When a candidate provides an incorrect or irrelevant answer yielding a genuine `0.0` score, `evaluation_status` remains `"success"` and `is_infrastructure_failure` remains `False`.
- **Orchestrator Error Logging**: In `_evaluate_verbal`, whenever `evaluation_status in {"non_finite_score", "invalid_score", "unavailable"}`, an entry is appended to `_state["infrastructure_errors"]`, preserving forensic auditability.

---

## 5. TEST SUITE EXECUTION & VERIFICATION

### 5.1 Targeted Regression Suite (Executed Fresh)
Command:
```bash
pytest -q tests/unit/test_score_validator.py tests/unit/test_evaluator_infrastructure_failure_flag.py
```
Outcome:
- **16 passed in 17.10s** (100% pass rate).
- Test breakdown:
  - `test_validator_clamps_out_of_range_numeric`: PASSED
  - `test_validator_handles_missing_and_none_score`: PASSED
  - `test_validator_handles_wrong_type_and_non_numeric`: PASSED
  - `test_validator_handles_nan_and_inf`: PASSED
  - `test_validator_handles_malformed_and_none_evidence`: PASSED
  - `test_validator_enforces_mandatory_cap_on_contradictory_evaluation`: PASSED
  - `test_validator_applies_mistake_penalty`: PASSED
  - `test_validator_penalizes_coding_failures`: PASSED
  - `test_validator_distinguishes_infrastructure_failure_from_candidate_failure`: PASSED
  - `test_validator_flags_non_finite_score_as_infrastructure_failure`: PASSED
  - `test_validator_does_not_accept_invalid_score_under_success_status`: PASSED
  - `test_score_validator_non_finite_score_flagged_as_infrastructure_failure`: PASSED
  - `test_evaluate_verbal_propagates_non_finite_flag_and_logs_infrastructure_error`: PASSED
  - `test_evaluate_verbal_genuine_zero_score_is_not_flagged_as_infrastructure_failure`: PASSED
  - `test_evaluate_verbal_missing_score_is_not_reported_as_success`: PASSED
  - `test_evaluate_verbal_nonnumeric_score_is_not_reported_as_success`: PASSED

### 5.2 Broader Unit Test Context
- **Historical Full Unit Run**: 314 passed, 1 skipped, 1 pre-existing failure (`test_stage11_5_coding_adaptation.py`) in 465s.
- **Targeted Keyword Selection**: 87 passed (`-k "validat or orchestrator or evaluat"`).

---

## 6. REPRODUCIBILITY INSTRUCTIONS

To reproduce the exact software verification state documented in Manuscript V10:
1. Ensure Python 3.12 is active with PyTorch, SentenceTransformers, and Stable-Baselines3.
2. In the worktree `C:\Users\spars\Downloads\PrepAIred\.claude\worktrees\exp032-orchestrator-concept-list-fix`:
   ```bash
   pytest tests/unit/test_score_validator.py tests/unit/test_evaluator_infrastructure_failure_flag.py -v
   ```
3. To build the V10 PDFs:
   ```bash
   python scratch/test_cdp.py research/paper_audit_v10/manuscript_v10_author.html research/paper_audit_v10/manuscript_v10_author.pdf
   python scratch/test_cdp.py research/paper_audit_v10/manuscript_v10_blind.html research/paper_audit_v10/manuscript_v10_blind.pdf
   ```
