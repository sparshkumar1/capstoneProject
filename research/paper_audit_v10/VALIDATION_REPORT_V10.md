# PREPAIred Independent Validation & Quality Assurance Report (V10)

**Date**: 2026-09-30  
**Evaluator**: Senior Research & Software Verification Engineer  
**Scope**: Complete Technical, Empirical, Editorial, and PDF Verification for Manuscript V10  

---

## 1. AUTOMATED TEST SUITE AUDIT & EXECUTION TRACE

### 1.1 Tests Actually Executed This Session
The following 16 tests in the targeted evaluator-reliability and score-validation suite were executed fresh on the active Python 3.12 environment:

```bash
pytest -q tests/unit/test_score_validator.py tests/unit/test_evaluator_infrastructure_failure_flag.py
```
- **Outcome**: **16 passed in 17.10s** (100% pass rate, 0 failures, 0 warnings).
- **Execution Log**: Recorded in background task log `task-14395.log`.
- **Individual Test Results**:
  1. `test_validator_clamps_out_of_range_numeric` — PASSED
  2. `test_validator_handles_missing_and_none_score` — PASSED
  3. `test_validator_handles_wrong_type_and_non_numeric` — PASSED
  4. `test_validator_handles_nan_and_inf` — PASSED
  5. `test_validator_handles_malformed_and_none_evidence` — PASSED
  6. `test_validator_enforces_mandatory_cap_on_contradictory_evaluation` — PASSED
  7. `test_validator_applies_mistake_penalty` — PASSED
  8. `test_validator_penalizes_coding_failures` — PASSED
  9. `test_validator_distinguishes_infrastructure_failure_from_candidate_failure` — PASSED
  10. `test_validator_flags_non_finite_score_as_infrastructure_failure` — PASSED
  11. `test_validator_does_not_accept_invalid_score_under_success_status` — PASSED
  12. `test_score_validator_non_finite_score_flagged_as_infrastructure_failure` — PASSED
  13. `test_evaluate_verbal_propagates_non_finite_flag_and_logs_infrastructure_error` — PASSED
  14. `test_evaluate_verbal_genuine_zero_score_is_not_flagged_as_infrastructure_failure` — PASSED
  15. `test_evaluate_verbal_missing_score_is_not_reported_as_success` — PASSED
  16. `test_evaluate_verbal_nonnumeric_score_is_not_reported_as_success` — PASSED

### 1.2 Tests Inspected & Traced to Historical Audit Records
- **Targeted Keyword Selection (87 Tests)**: Traced to `pytest -q tests/unit/ -k "validat or orchestrator or evaluat"` (87 passed, 217 deselected). Reconciled in `research/analysis/test_count_reconciliation_20260930/RESULT_NOTE.md`: exactly 53 tests from the 5 primary evaluator/orchestrator files + 34 tests from secondary files with matching name substrings.
- **Full Backend Suite (314 Tests)**: Traced to prior full-suite run (314 passed, 1 skipped, 1 known pre-existing failure in `test_stage11_5_coding_adaptation.py`).

### 1.3 Tests Not Run This Session
- Full end-to-end multi-turn voice interviews with real microphone hardware (requires live human input).
- Live Docker Desktop C sandbox runs on Windows WSL2 (requires active Docker engine daemon).
- GPU-accelerated local Qwen2.5 inference (development ran in mock/CPU mode).

---

## 2. MATHEMATICAL FORMULA & SYSTEM DESIGN RE-VERIFICATION

Every formula and architectural constant in Manuscript V10 was cross-verified against source code:

| Component | Manuscript V10 Representation | Source Code Authority | Verification Finding |
|---|---|---|---|
| **Composite Verbal Scoring** | $S_{\text{base}} = 0.15 S_1 + 0.35 S_2^{\text{effective}} + 0.50 R$ | `services/evaluator/app.py:487-491` | **Exact match.** Weights 0.15, 0.35, 0.50 verified. |
| **Anti-Gaming Damping** | $S_2^{\text{effective}} = S_2$ if $R > 0.30$ else $0.60 \cdot S_2$ | `services/evaluator/app.py:484` | **Exact match.** Damps concept score by 40% when reasoning floor $\le 0.30$. |
| **Sentence Deduplication** | `dedupe_repeated_sentences(text)` | `services/evaluator/app.py:81-105` | **Exact match.** Verbatim sentence repeats dropped prior to scoring. |
| **Mandatory Concept Ceiling** | $S_{\text{final}} = \min(0.60, S_{\text{final}})$ if mandatory missed | `services/evaluator/app.py:499-500` | **Exact match.** Capped at 0.60. |
| **PPO 6D State Space** | $[\text{perf}, \text{avg\_perf}_5, \text{conf}, \text{hes}, \text{prog}, \text{diff}] \in [0, 1]^6$ | `rl/env/interview_env.py:50-187` | **Exact match.** Latency explicitly excluded from state vector. |
| **PPO Discrete Actions** | $a \in \{0: \text{Easier } (-0.1), 1: \text{Same } (0.0), 2: \text{Harder } (+0.1)\}$ | `rl/env/interview_env.py:65` | **Exact match.** Single-step curriculum constraints verified. |
| **Canonical Guardrails** | Priority: $\text{Infra} \to \text{G4} \to \text{G1} \to \text{G2} \to \text{G5} \to \text{G6}$ | `rl/guardrails.py:33-106` | **Exact match.** G4 (Stuck Candidate) holds highest pedagogical priority. |
| **Acoustic Confidence** | $C_{\text{final}} = 0.28 V_Q + 0.27 L + 0.22 F_{\text{fluency}} + 0.13 F_{\text{rate}} + 0.10 F_{\text{rhythm}}$ | `agents/audio/confidence_scorer.py:103-115` | **Exact match.** Vocal delivery decoupled from technical score. |
| **Pacing / Fast-Wrong Rule** | Bonus $+0.03$ max requires $S \ge 0.70$; fast errors receive $0.00$ bonus | `agents/timing/timer.py:42-43` | **Exact match.** Fast-wrong gaming immunity verified. |
| **Follow-up Trigger Policy** | Two-condition-class gate: skip if $S \ge 0.85 \land \text{no gap}$; else trigger | `agents/orchestrator/interview_orchestrator.py:1760-1791` | **Exact match.** Max 2 follow-ups per primary question. |

---

## 3. PDF RENDERING & VISUAL QUALITY ASSURANCE

### 3.1 PDF Compilation Parameters
- **Rendering Engine**: Google Chrome DevTools Protocol (`Page.printToPDF`) via headless Chrome.
- **Page Size**: Letter ($8.5 \times 11$ inches), Margins: top 0.85in, bottom 0.95in, left/right 0.62in.
- **Math Engine**: MathJax 3.2.2 client-side rendering (verified with 6-second delay).

### 3.2 Physical Page Structure & Layout Audit

| PDF Deliverable | Page Count | Visual Inspection Findings |
|---|---|---|
| `manuscript_v10_author.pdf` | **9 Pages** | • Page 1: Balanced two-column layout with 5 authors, affiliations, 224-word abstract, and Introduction.<br>• Pages 2–3: Related Work and Architecture with Table I and Table II.<br>• Page 4: Full-width SVG Figure 1 and Evaluator formulas.<br>• Pages 5–8: Speech Confidence, PPO, Follow-up, Results & Discussion, and Limitations.<br>• Page 9: Substantial two-column closing page containing Data/Code Availability, Conclusion & Future Work, Acknowledgments, and References [1]–[17]. Zero orphaned headers. |
| `manuscript_v10_blind.pdf` | **7 Pages** | • Page 1: Anonymized title banner with placeholder; no author block; compact 224-word abstract.<br>• Pages 2–6: Core body text, tables, and equations flow continuously.<br>• Page 7: Conclusion, anonymized acknowledgments, and References [1]–[17] end cleanly at the base of column 2. |

### 3.3 Anonymity Audit on Blind Deliverable (`manuscript_v10_blind.pdf`)
A complete text-extraction sweep was executed over all 7 pages of `manuscript_v10_blind.pdf`:
- Author names (`Uma`, `Sparsh`, `Kumar`, `Naveen`, `Khadd`, `Athreya`, `Shashidhara`, `Manasa`): **0 occurrences**.
- Institutional keywords (`PES`, `Bengaluru`): **0 occurrences**.
- Author email domains (`@gmail.com`, `@pes.edu`): **0 occurrences**.
- Document Title & PDF Metadata: Verified clean of author credentials.

---

## 4. SCIENTIFIC & EDITORIAL CONSISTENCY AUDIT

1. **Abstract Length**: Reduced from 558 words down to **224 words**, strictly communicating:
   - Research problem (technical reasoning vs. verbal delivery, unconstrained LLM vulnerabilities).
   - System & methodological contribution (decoupled architecture, multi-tier evaluator, independent acoustic confidence, PPO difficulty adaptation, deterministic evidence gating).
   - Setup & dataset size (exploratory benchmark of $n = 64$ constructed answers across 8 questions).
   - Most informative verified results (CrossEncoder $\rho = 0.4832$, composite $\rho = 0.3812$, length confound $\rho = 0.6594$, partial correlation drop to $0.2434$ $[−0.008, 0.507]$).
   - Core limitations (length-independent reasoning contribution not established, no candidate learning gains claimed, no superiority claim for PPO over simpler guardrailed policies).
2. **Empirical Grounding**: Every numerical value matches Section X.B and frozen project records.
3. **No Retracted Claims Re-introduced**: The unsupported 0.796 correlation, the synthetic-persona diagnostic, and the LLM partial-evaluation latency table remain completely excluded.
4. **Citation Integrity**: All 17 citations are numbered strictly by first appearance; verified against IEEE citation standards.

---

## 5. VERDICT

Manuscript V10 and its accompanying deliverables are **verified code-grounded, statistically consistent, and publication-ready for generic IEEE review**. All V8/V9 versioning anomalies are eliminated, the score-validation defect is confirmed resolved and covered by 16 passing regression tests, and both PDFs are freshly compiled and verified.
