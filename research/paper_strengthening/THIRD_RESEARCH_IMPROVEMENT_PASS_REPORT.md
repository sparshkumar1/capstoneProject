# Third Research Improvement Pass — PPO V2 + Evaluator Reasoning + Integrated Validation

Builds directly on `PPO_FORMULATION_INVESTIGATION_V1_REPORT.md` and `SECOND_EXECUTION_PASS_V1_REPORT.md`; does not repeat the completed entropy experiment, evaluator fixes, feedback validation, or session-recovery implementation. `git status` at the start of this pass matched exactly what the prior two passes left, with no other process running.

## 1. PPO V2 — mechanism diagnosis and checkpoint-selection intervention

### 1.1 Diagnosis (no new training; existing stored evaluation data only)

Full account: `PPO_V2_MECHANISM_DIAGNOSIS.md`. Summary: re-analyzed the already-stored `e1_dev_eval`/`e1_dev_eval_extended` raw evaluation data (never previously broken down per-cell against each other this precisely). Findings:

- **The extended-budget regression is not diffuse.** 99.4% of the total pooled-cell MAE regression is concentrated in 6 of 24 cells, all at skill ∈ {0.80, 0.90}. Every cell at skill ≤ 0.65 is stable between budgets (≤0.02 delta).
- **A specific, narrow behavior is learned, then lost.** The primary-budget checkpoint proposes "Harder" for skill=0.80 at a stable ~8-10% rate across all four persona-diversity (k) values; the extended-budget checkpoint has largely or fully abandoned it (0-6%, down to exactly 0% at one cell). skill=0.90's Harder-rate is preserved at 3 of 4 k-values.
- **Oracle-agreement rising while MAE collapses is not a contradiction** — it is evidence of a self-reinforcing "stuck" dynamic: once the policy stops proposing "Harder," the state never reaches a region where the oracle would prescribe "Harder" either, so local per-step agreement can look fine even as episode-level tracking error grows.
- This generalizes, rather than contradicts, the prior pass's "single correctly-timed Harder action" finding (`E1_DEVELOPMENT_RUN_REPORT.md` §6) — that was one instance of a broader, skill=0.80-specific pattern.

### 1.2 Intervention: periodic checkpointing + predeclared, dev-grid-only checkpoint selection

Chosen over a reward redesign (higher risk, touches frozen reward code, would need its own separately-validated new term for a mechanism only partially understood) and over repeating the already-tested entropy intervention. Predeclared hypothesis, decision rule, and methodology: `research/paper_strengthening/scripts/ppo_v2_checkpoint_selection_experiment.py`'s module docstring, written before training ran.

**Implementation:** `ppo_v2_checkpoint_selection_experiment.py` trains B2 with the exact same reward/state/action/hyperparameters as every prior E1 run, for the same 5 training seeds, saving a checkpoint every 8192 steps across one continuous 98,304-step run (12 checkpoints/seed, 60 total). `ppo_v2_checkpoint_selection_eval.py` evaluates every checkpoint on the same 24-cell × 5-development-eval-seed grid used throughout the E1 series (no confirmatory seed, no held-out profile), then applies the predeclared selection rule: pick the single training-step interval (common across all 5 seeds, not a per-seed cherry-pick) that minimizes cross-seed-averaged pooled dev-grid MAE.

**Result: the predeclared rule is SUPPORTED.**

| checkpoint step | cross-seed-averaged pooled dev-grid MAE |
|---|---|
| 8,192 | 0.2776 |
| **16,384** | **0.2697 ← selected (minimum)** |
| 24,576 (= original fixed "primary budget") | 0.2735 |
| 32,768 | 0.2785 |
| 40,960 | 0.3036 |
| 49,152 | 0.3376 |
| 57,344 | 0.3820 |
| 65,536 | 0.4115 |
| 73,728 | 0.4150 (worst) |
| 81,920 | 0.4033 |
| 90,112 | 0.3962 |
| 98,304 (= original fixed "extended budget") | 0.3994 |

MAE stays low and clustered (0.270–0.278) for the first four checkpoints (8,192–32,768), then rises sharply and roughly monotonically through 73,728 before a partial, still-much-worse recovery toward 98,304 — the same shape the mechanism diagnosis predicted (an early-peaking, narrow behavior that degrades with continued training, not a smooth or reversible trend). The selected checkpoint (16,384 steps — actually *fewer* steps than the original "primary budget" of 24,576) achieves MAE 0.2697, **0.0038 better than** the fixed-primary-budget result and well inside the ±0.01 tolerance, without the experiment ever having been told 24,576 was a good choice — the selection procedure found this independently, using only development-grid evaluation, never confirmatory data.

**This does not authorize confirmatory evaluation.** It demonstrates that checkpoint selection is a viable, low-risk way to avoid the extended-training regression on the development grid; per every prior E1-family pass's stopping discipline, moving to confirmatory evaluation on a new PPO configuration requires its own registered protocol and separate approval, not a passing development-stage result alone (see, e.g., `E1_DEVELOPMENT_RUN_REPORT.md` §6's identical reasoning for the original B2/B0 comparison, which mechanically passed its own development gate yet was correctly not advanced without further scrutiny).

## 2. Evaluator V3 — logical-reasoning investigation

Full account and test suite: `tests/unit/test_evaluator_logical_reasoning_adversarial.py`. Built a 7-case adversarial set (plausible, not nonsensical, wrong-mechanism answers across two questions, with correct-answer controls) to diagnose §1.1b's (second pass) already-known remaining limitation.

**Diagnosis, via two independent empirical probes:**

1. **Sentence-level cross-encoder re-scoring — tested and refuted.** Scoring each candidate sentence individually against the reference (instead of the whole answer) produced backwards results: a correct answer's sentences scored *lower* (0.211-0.339) than a wrong answer's (0.341-0.511). The cross-encoder's calibration doesn't transfer to sentence granularity. Not implemented.
2. **Rubric mistake-text extension — a real bug fixed, a content fix attempted and self-corrected.** Found and fixed two real defects: `mistake_penalty()` never consulted rubric-text `common_mistakes_addressed` at all (FAISS-vectors only), and `_detect_misconceptions()` silently dropped any text entry beyond the FAISS-indexed count. With that fixed, 3 new misconception descriptions were added to 2 rubrics; 2 of the 3 (Floyd's-cycle-specific) caused a measured regression — 0.759 and 0.662 cosine similarity against a genuinely correct answer, breaking 2 existing tests — and were reverted after the full suite caught it. This failure is itself first-hand evidence for the diagnosis: correct and incorrect answers sharing the same vocabulary around a polarity-flipped claim are not reliably separable by SBERT cosine similarity alone.

**Net result:** the overflow-detection bug fix is real, safe, kept, and tested. The two originally-targeted adversarial cases (degenerate always-same-index mechanism; same-speed-pointers claim) remain **unfixed and explicitly disclosed** via regression tests labeled as known limitations. A robust general fix would need a properly validated contradiction/NLI model (its own project) or much more extensive, individually-validated per-question authoring than was in scope here — named precisely, not glossed over.

## 3. D1 benchmark

Reassessed a third time. Conclusion unchanged; blocker now named precisely rather than generally: the missing requirement is independent technical review of authored content (someone other than the author verifying construction validity), which is unavailable in this session — not merely "content has not been written." Full account: `D1_FINAL_BLOCKER_ASSESSMENT.md`.

## 4. Integrated system validation

New integration tests (`tests/integration/test_evaluator_feedback_integration.py`, 2 tests) compose the real, independently-fixed `evaluate()` and `_validate_feedback_output()` together: confirm a real evaluator-detected misconception is correctly rejected if echoed back as "correct" by simulated feedback, and confirm a real correct-answer's well-formed feedback passes validation (control). Both pass. This directly tests "whether feedback and follow-up generation remain aligned with the latest evaluator evidence" using real production functions on both sides, not a shadow copy of either.

Not repeated: the already-completed unit tests for WPM/WPS, session recovery, and follow-up/prompt-injection validation, per this pass's own instruction not to duplicate prior work without a specific new reason.

## 5. Regression verification

- `tests/unit/test_evaluator.py`: 17/17 passed (real models).
- `tests/unit/test_evaluator_logical_reasoning_adversarial.py`: 7/7 passed (new file).
- `tests/integration/test_evaluator_feedback_integration.py`: 2/2 passed (new file).
- `tests/unit/test_qwen_followup_feedback.py` + `tests/unit/test_session_recovery.py`: 53/53 passed (health check; neither file was touched this pass).
- Full repository suite (`pytest -q`, `EVALUATOR_MOCK_MODE=1`): **340 passed, 1 failed, 455.9s.** The one failure is the same pre-existing, already-documented `test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics` (RL-observation `time_norm` issue, unrelated to this pass's changes, confirmed by direct reading in an earlier pass). No new failure was introduced.

No PPO reward/state/action code, no frozen driver, no frozen checkpoint, and no confirmatory/held-out data was modified. `rubrics.json` (a rubric *data* file, not in CLAUDE.md's protected list) received a minimal, surgical 1-entry addition (qid=1) after 2 higher-risk entries (qid=4) were tested and reverted.

## 6. What remains blocked, and why

- **D1 benchmark**: blocked on independent technical review, precisely named (§3).
- **Evaluator logical-reasoning weakness**: two general mitigations attempted, both found unsafe or ineffective; disclosed as an open limitation, not silently accepted (§2).
- **PPO V2 confirmatory promotion**: regardless of the checkpoint-selection result, no confirmatory evaluation is authorized by this pass — that decision requires its own registered protocol and separate approval, consistent with every prior E1-family pass's stopping discipline.

## Files changed this pass

Modified: `services/evaluator/app.py`, `services/evaluator/assets/rubrics.json`, `research/paper_strengthening/FINAL_MANUSCRIPT_EVIDENCE_V2.md`, `research/paper_strengthening/CLAIM_LEDGER_SYSTEM_PAPER_V1.md`.

New: `PPO_V2_MECHANISM_DIAGNOSIS.md`, `D1_FINAL_BLOCKER_ASSESSMENT.md`, this report, `research/paper_strengthening/scripts/ppo_v2_checkpoint_selection_experiment.py`, `ppo_v2_checkpoint_selection_eval.py`, `tests/unit/test_evaluator_logical_reasoning_adversarial.py`, `tests/integration/test_evaluator_feedback_integration.py`, and the `results/ppo_v2_checkpoint_selection/` output directory.

No commit, tag, push, or submission was made.
