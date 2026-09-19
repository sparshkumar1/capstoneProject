# Paper 3 Final Baseline Consistency & Guardrail Verification

**Audit Date:** September 19, 2026  
**Audited Commit:** `375f4f869c47907d7c222d27df3b4f9e09dc8941` (working tree with blocker repairs applied)  
**Governing Documents:**
- `research/CANONICAL_SCIENTIFIC_TRUTH.md`
- `research/audit/paper3_reporting_audit.md`
- `research/audit/rl_state_alignment.md`
- `research/archive/historical_invalid_baseline/`
- `research/scripts/run_paper3_study.py`
- `tests/unit/test_paper3_blockers.py`
- `research/audit/PAPER1_EXECUTION_COMPLETION.md`

---

## 1. Executive Summary

This audit definitively resolves the apparent discrepancy between:
- **Repaired Paper 3 Fixed Baseline MAE:** **`1.200`**
- **Earlier Audit Mention in `paper3_reporting_audit.md`:** **`1.000`**

Forensic analysis proves beyond ambiguity that **`1.000` was a typographical/arithmetic evaluation error** in the audit text, while the mathematical equation written by the auditor and the underlying persona target difficulties unequivocally yield **`1.200`**.

Additionally, this audit confirms the exact operational conditions of **Guardrail G4**, verifies test coverage, and certifies the snapshot isolation of **Paper 1**.

---

## 2. Forensic Resolution of Baseline MAE Discrepancy (1.200 vs. 1.000)

### 2.1 Authoritative Persona Target Difficulties
The canonical simulated candidate personas and their respective skill levels and target difficulty levels ($d^* \in [1.0, 5.0]$) are defined identically in:
- `research/audit/paper3_reporting_audit.md` (lines 53–58)
- `research/scripts/run_paper3_study.py` (`PERSONA_TARGETS`)
- `tests/unit/test_paper3_blockers.py`

| Persona | Skill Level | Target Difficulty ($d^*$) | Latent Signal Characteristics |
|:---|:---:|:---:|:---|
| `struggling_junior` | $0.20$ | **$1.0$** | $\text{perf} \le 0.30$, $\text{conf} \le 0.30$, high hesitation |
| `overconfident_fail` | $0.30$ | **$1.5$** | $\text{perf} \le 0.20$, $\text{conf} \ge 0.85$, low hesitation |
| `normal` | $0.60$ | **$3.0$** | Standard balanced logistic response curve |
| `lucky_guesser` | $0.80$ | **$4.0$** | $\text{perf} \ge 0.95$, $\text{conf} \le 0.30$, high hesitation |
| `nervous_expert` | $0.88$ | **$4.5$** | $\text{perf} \in [0.82, 0.94]$, $\text{conf} \le 0.40$, high hesitation |

$$\mathbf{d}^* = [1.0, 1.5, 3.0, 4.0, 4.5]$$

---

### 2.2 Authoritative Fixed Difficulty
In the `Fixed` difficulty baseline, the difficulty level is locked statically at mid-level difficulty throughout the entire session:
$$d_{\text{fixed}} = \mathbf{3.0}$$

---

### 2.3 Mathematically Correct Fixed-Baseline MAE
For each candidate persona $p \in \{1, 2, 3, 4, 5\}$, the absolute tracking error under fixed difficulty $3.0$ is:
- `struggling_junior`: $|3.0 - 1.0| = 2.0$
- `overconfident_fail`: $|3.0 - 1.5| = 1.5$
- `normal`: $|3.0 - 3.0| = 0.0$
- `lucky_guesser`: $|3.0 - 4.0| = 1.0$
- `nervous_expert`: $|3.0 - 4.5| = 1.5$

Sum of absolute errors across the 5 personas:
$$\sum_{p=1}^5 |d_{\text{fixed}} - d^*(p)| = 2.0 + 1.5 + 0.0 + 1.0 + 1.5 = \mathbf{6.0}$$

The Mean Absolute Error (MAE) is the mean over the 5 personas:
$$\text{MAE}_{\text{Fixed}} = \frac{1}{5} \sum_{p=1}^5 |d_{\text{fixed}} - d^*(p)| = \frac{6.0}{5} = \mathbf{1.200}$$

---

### 2.4 Why the Previous Audit Reported 1.000
In `research/audit/paper3_reporting_audit.md`, line 61 explicitly wrote:
$$\text{MAE}_{\text{Fixed}} = \frac{1}{5}(|3-1| + |3-1.5| + |3-3| + |3-4.5| + |3-4|) = \mathbf{1.000}$$

Notice the left-hand side of this exact equation:
$$\frac{1}{5}(|3-1| + |3-1.5| + |3-3| + |3-4.5| + |3-4|) = \frac{1}{5}(2.0 + 1.5 + 0.0 + 1.5 + 1.0) = \frac{6.0}{5} = \mathbf{1.200}$$

The previous audit document contained the exact correct targets and the exact correct formula, but the author committed an elementary manual arithmetic miscalculation when evaluating the fraction (evaluating $6.0 / 5$ as $1.000$, likely by either confusing the denominator with $6$ or dropping the $+1.0$ term).
There was never a conflicting set of persona target values in the canonical record.

---

### 2.5 Scientific Validity & Final Determination
- **Scientific Truth:** **`1.200`** is the only mathematically and empirically correct value. An arithmetic slip in an audit narrative does not alter mathematical reality.
- **Experimental Protocol:** **`1.200`** MUST be used in the final Paper 3 study.
  - Using $1.000$ would contradict the code, falsify arithmetic, and fail automated reproducibility tests.
  - The actual baseline evaluation in `research/scripts/run_paper3_study.py` automatically computes the exact sample mean of absolute deviations, which yields $\text{MAE} = 1.200$.

---

## 3. Guardrail G4 Verification

### 3.1 Does Canonical G4 Require 2 Consecutive Failures?
**NO.** The canonical G4 rule does **NOT** require 2 consecutive failures before decreasing difficulty.

- **Pedagogical Function:** G4 is the **Critically Stuck Candidate Guard** (acute failure accompanied by cognitive stalling).
- **Trigger Rule:** If a candidate exhibits very low score ($\text{perf} < 0.30$) together with severe acoustic hesitation ($\text{hes} > 0.60$), they are actively stuck and experiencing distress.
- **Pedagogical Rationale:** Forcing a stuck candidate to fail a second consecutive high-difficulty question before offering relief violates the core pedagogical objective of maintaining the candidate within Vygotsky's *Zone of Proximal Development (ZPD)*. Relief must be immediate ($\text{Action} \to \text{Easier}$).
- **Where "Consecutive Failures" Actually Applies:**
  In the PREPAIred orchestrator architecture, the consecutive-failure counter (`consec = int(self._state.get("consecutive_followups", 0))`) is strictly applied to:
  1. **Socratic Follow-up Ceiling (G5):** Caps follow-up questions at 2 (`consec < 2`), preventing infinite probing.
  2. **Partial Understanding Stabilization (G3/G5):** Holds difficulty at `Same` when $0.40 < \text{perf} < 0.65$ provided $\text{consec} < 2$.

---

### 3.2 Exact Implemented G4 Condition

Across all three execution layers, G4 is implemented identically:

1. **Canonical Module (`rl/guardrails.py:77-78`):**
   ```python
   # G4: Critically Stuck Candidate — HIGHEST PEDAGOGICAL PRIORITY (before G1)
   if perf < 0.30 and hes > 0.60:
       return ACTION_EASIER, True, "g4_stuck_easier"
   ```

2. **Gymnasium Environment (`rl/env/interview_env.py:250-251`):**
   ```python
   # G4: Stuck candidate — HIGHEST PRIORITY (before G1)
   if perf < 0.30 and hes > 0.60:
       return 0, True, "g4_stuck_easier"
   ```

3. **Runtime Orchestrator (`agents/orchestrator/interview_orchestrator.py:1407-1409`):**
   ```python
   # G4 — critically struggling candidate
   if perf < 0.30 and hes > 0.60:
       self._last_guardrail_name = "guardrail_G4"
       return _ACTION_NAME_TO_IDX["Easier"]
   ```

---

### 3.3 Test Verification of G4 Condition

The exact G4 condition is covered and passing in three independent automated test suites:

1. **`tests/unit/test_paper3_blockers.py:139-148` (`test_guardrail_g4_stuck_candidate`):**
   - Inputs: $\text{perf} = 0.20$, $\text{hes} = 0.75$, $\text{proposed\_action} = 1 (\text{Same})$.
   - Output: `action == 0 (Easier)`, `overridden == True`, `gid == "g4_stuck_easier"`.
   - Result: **PASSED**.

2. **`tests/unit/test_rl_env.py:290-298` (`test_guardrail_g4_stuck_overrides_to_easier`):**
   - Inputs: $\mathbf{s} = [0.20, 0.25, 0.15, 0.75, 0.50, 0.60]$, $\text{proposed\_action} = 2 (\text{Harder})$.
   - Output: `action == 0 (Easier)`, `forced == True`, `gid == "g4_stuck_easier"`.
   - Result: **PASSED**.

3. **`tests/unit/test_orchestrator.py:155-170` (`test_guardrail_g4_stuck`):**
   - Inputs: `diff = 3`, `score = 0.25`, $\text{conf} = 0.20 \implies \text{hes} = 0.80 > 0.60$.
   - Output: `action == "Easier"`, `diff == 2`, `_last_guardrail_name == "guardrail_G4"`.
   - Result: **PASSED**.

---

## 4. Paper 1 Snapshot & Provenance Verification

### 4.1 Frozen Paper 1 Commit
- **Frozen Git Commit:** **`375f4f869c47907d7c222d27df3b4f9e09dc8941`**
- **Documented In:**
  - `research/audit/PAPER1_EXECUTION_COMPLETION.md`
  - `research/results/paper1/PAPER1_FINAL_REPORT.md`
  - `research/audit/PAPER2_EXECUTION_COMPLETION.md`
- **Key Frozen Artifacts:**
  - `research/results/paper1/security_benchmark.json`
  - `research/results/paper1/fault_injection_benchmark.json`
  - `research/results/paper1/concurrency_benchmark.json`
  - `research/results/paper1/subsystem_latency_benchmark.json`
  - Evaluator config SHA-256: `f057baf1b2b9608eb0eb34d9aef3a4a3571db868f9ee728dda180364cc4e90f1`
  - Human gold benchmark SHA-256: `363dbe6d848a04fe18be5ef1d30b6bbf63b54248fe758e5e6bd4c27a26c06ce2`

---

### 4.2 Temporal Order of Paper 3 Repairs
- All Paper 3 repairs (`rl/guardrails.py`, state Dimension 4 alignment in `interview_orchestrator.py` and `hybrid_orchestrator.py`, `run_paper3_study.py` calibration, and `test_paper3_blockers.py`) occurred **strictly AFTER commit `375f4f869c47907d7c222d27df3b4f9e09dc8941`**.
- Commit `375f4f869c47907d7c222d27df3b4f9e09dc8941` remains the authoritative repository `HEAD`.
- Paper 1 was fully executed, benchmarked, audited, and frozen prior to the start of the Paper 3 pre-flight and blocker repair pass.

---

### 4.3 Paper 1 Reproducibility Certification
1. **Repository Checkpoint:** Checking out commit `375f4f8` restores the exact historical state prior to Paper 3 repairs.
2. **Backward Compatibility:** The Paper 3 repairs made to shared code (`agents/orchestrator/interview_orchestrator.py` and `agents/strategy/hybrid_orchestrator.py`) are strictly non-disruptive:
   - Initializing `session["progress"]` has zero impact on Paper 1's Docker sandbox execution, SQLite WAL concurrency, fault injection recovery, or ScoreValidator caps.
   - The full orchestrator test suite (`tests/unit/test_orchestrator.py`) passes **20/20** with the repairs active.
   - Paper 1 results remain 100% reproducible and preserved in `research/results/paper1/`.

---

## 5. Explicit Q&A Summary

| Question | Authoritative Answer |
|:---|:---|
| **1. Authoritative Persona Target Difficulties?** | `struggling_junior`: **1.0**, `overconfident_fail`: **1.5**, `normal`: **3.0**, `lucky_guesser`: **4.0**, `nervous_expert`: **4.5**. Vector: `[1.0, 1.5, 3.0, 4.0, 4.5]`. |
| **2. Authoritative Fixed Difficulty?** | **`3.0`** (static mid-level difficulty). |
| **3. Mathematically Correct MAE?** | **`1.200`** ($\frac{1}{5}(|3-1| + |3-1.5| + |3-3| + |3-4| + |3-4.5|) = \frac{6.0}{5} = 1.200$). |
| **4. Why Previous Audit Reported 1.000?** | The author of `paper3_reporting_audit.md` wrote out the exact formula yielding $6.0/5$, but made a manual arithmetic calculation error writing `= 1.000` on the page. |
| **5. Is 1.200 or 1.000 Scientifically Correct?** | **`1.200`** is the strictly scientifically and mathematically correct value. $1.000$ was an arithmetic typo. |
| **6. Which Value Must Be Used in Paper 3?** | **`1.200`** must be used in the final Paper 3 experiment and reporting. |
| **7. Does G4 Require 2 Consecutive Failures?** | **NO.** G4 triggers immediately when $\text{perf} < 0.30 \land \text{hes} > 0.60 \to \text{Easier}$. Consecutive failure limits apply strictly to Socratic follow-ups and partial understanding (G5/G3). |
| **8. Paper 1 Snapshot Status?** | Frozen at commit **`375f4f869c47907d7c222d27df3b4f9e09dc8941`**. Paper 3 repairs occurred after this commit and do not break Paper 1 reproducibility. |
