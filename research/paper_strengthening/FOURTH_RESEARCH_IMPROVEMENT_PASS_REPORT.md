# Fourth Research Improvement Pass — PPO V2 Confirmatory Validation, Evaluator V4, Reproducibility

Builds directly on `THIRD_RESEARCH_IMPROVEMENT_PASS_REPORT.md`, `PPO_V2_MECHANISM_DIAGNOSIS.md`, `CLAIM_LEDGER_SYSTEM_PAPER_V1.md`, and `FINAL_MANUSCRIPT_EVIDENCE_V2.md`. Full companion documents: `PPO_V2_CONFIRMATORY_EVALUATION.md`, `EVALUATOR_V4_VALIDATION.md`, `D1_INDEPENDENT_REVIEW_PACKET.md`.

## 1. Audit (item 1)

`git status` at the start of this pass matched exactly the state left by the third pass, no other process running. All four required documents were read in full (not skimmed) before any change. Frozen/protected paths reconfirmed unchanged throughout: `research/CANONICAL_SCIENTIFIC_TRUTH.md`, `research/papers/*`, `research/results/paper3/*`, `research/confirmatory/X3-A/*`, `rl/checkpoints/*`, `ablation/results/*`, `research/data/evaluator_benchmark/final_human_gold.csv`. No discrepancy was found between the third pass's narrative and the underlying stored artifacts beyond one explained, non-error difference (see §2.1).

**What was already established (per the third pass):** the checkpoint-selection development result (0.2697 at step 16,384 vs. 0.2735 fixed-primary); the skill=0.80 mechanism diagnosis (2-point resolution); two evaluator fixes (misconception penalty tier, repetition dedup) shipped and correlation-neutral on human-gold; one evaluator fix (mistake-overflow bug) shipped; two evaluator content additions reverted after a real regression; D1 blocked on independent review; session recovery implemented and unit/integration tested below the live-socket layer.

**What remained unverified going into this pass:** whether the development result reproduces from stored artifacts (not just trusted); whether the checkpoint-selection win is uniform across seeds; whether the skill=0.80 mechanism holds at finer resolution; whether a different (non-embedding-similarity) evaluator fix approach exists; whether D1 has anything ready to package; whether session recovery works through the actual live WebSocket endpoint; whether the PPO V2 scripts have any silent-failure risk.

**Experiments authorized this pass:** independent reproduction/re-derivation from existing artifacts (no new training beyond re-running the already-hardened eval script against already-trained checkpoints); one new adversarial test-authoring pass (evaluator); one new integration test (live WebSocket); reproducibility hardening of existing scripts. **Not authorized/not executed:** any new PPO training sweep; any confirmatory-data evaluation; any new evaluator scoring-code change (none was found safe — see §3).

## 2. PPO V2 confirmatory validation

Full account: `PPO_V2_CONFIRMATORY_EVALUATION.md`. Summary:

### 2.1 Independent reproduction
Recomputed the cross-seed MAE directly from `by_step_summary.json`/`raw.json`: **0.26972 ≈ 0.2697 at step 16,384 — matches exactly.** One explained (not erroneous) discrepancy: the "extended budget" reference value differs slightly between this run's own step-98,304 checkpoint (0.3994) and the original, separately-trained B2 run (0.3942) — both correctly attributed to their own runs; itself a small additional data point on run-to-run training variance.

### 2.2 Selection procedure frozen and confirmed clean
Full source of both scripts re-read. Metric, eligible checkpoints (12/seed, every 8,192 steps), and seed aggregation (unweighted mean) all explicit in code. **No tie-breaking rule was predeclared** (a real, disclosed gap, not exercised in practice since 16,384 is a clear unique minimum). Confirmed, by direct source inspection, that neither script references the locked confirmatory seeds (21021-40040) or held-out profiles anywhere.

### 2.3-2.4 Baselines and ablation
Compared the selected checkpoint (16,384) against the fixed primary-budget checkpoint (24,576) **per seed**, within the same training run (a clean, non-confounded comparison): **worse on 3/5 seeds** (42, 456, 789: +0.0015 to +0.0046), **better on 2/5** (123, 999: seed 999 by −0.0234, the outsized driver of the aggregate win). Traced the seed-999 effect to step-24,576 being a locally mediocre point for that seed specifically (its own skill=0.80 MAE: 0.264 at 24,576 vs. 0.132 at 16,384, while other seeds sit at the floor, 0.127, at *both* steps) — both checkpoints are inside the same broad low-MAE plateau; **not a large, robust, generalizable effect.** Against the final checkpoint (98,304), the selected checkpoint is dramatically and uniformly better on all 5 seeds — this part is robust. No prespecified alternative selection rule exists to compare against (none registered before this pass); none was invented, per instruction.

### 2.5 Skill=0.80 mechanism, full resolution
All 12 checkpoints × 6 skill values analyzed (§4 of the companion doc). Skills ≤0.65 essentially perfectly flat across the entire training range. Skill=0.90 rises moderately. **Skill=0.80 is flat-to-good through step 32,768, then collapses sharply and almost monotonically to a peak at step 73,728 (0.17→0.87), for every one of the 5 seeds** — systematic, not seed-specific noise. Skill=0.80's own per-checkpoint minimum is at step 16,384, which is the direct, causal reason the cross-seed selection procedure landed there.

### 2.6 Confirmatory evaluation: explicitly NOT executed
Given §2.4's per-seed non-uniformity, and per CLAUDE.md's standing requirement for an approved protocol and human authorization before any confirmatory spend, **this pass did not touch the locked confirmatory seeds or held-out profiles.** A complete, ready-to-run protocol (baselines, statistics, equivalence margin, required per-seed reporting) is registered in `PPO_V2_CONFIRMATORY_EVALUATION.md` §6, pending explicit authorization. **No claim of PPO superiority over simpler controllers is made.**

## 3. Evaluator V4

Full account: `EVALUATOR_V4_VALIDATION.md`. **No evaluator scoring code was changed this pass.** Audit confirmed all previously-fixed defects remain fixed. A third, distinct fix hypothesis (relative mistake-vs-reference similarity) was tested directly against the known false-positive pair and found to fail the same way as the first two attempts (backwards result: the correct answer's mistake-similarity, 0.759, still exceeds its reference-similarity, 0.725) — not implemented, per instruction not to force a fix with no safe general solution. A new, separately-labeled 10-case adversarial development suite (`tests/unit/test_evaluator_v4_adversarial_development_suite.py`) was built covering all 10 requested failure-mode categories; all 10 pass, characterizing real current behavior, and surfaced two new disclosed findings: a vocabulary-level (not just sentence-structure) paraphrase sensitivity, and a side effect of the second pass's misconception penalty tier also firing on merely-incomplete (not wrong) answers. Human-gold benchmark cited unchanged (0.3787; no code change to re-run against it).

## 4. D1

`D1_INDEPENDENT_REVIEW_PACKET.md`: the benchmark is **not** ready for review (no content exists in any split, unchanged finding). Built the review procedure infrastructure anyway — reviewer instructions, response template, disagreement-resolution procedure, blinding protocol — ready to use the moment content and a reviewer both exist. Neither exists yet; explicitly not fabricated.

## 5. Integration — closed the highest-risk previously-disclosed gap

`tests/integration/test_live_websocket_session_recovery.py`: drove the real `apps.backend.main` FastAPI app through a live WebSocket connection (`TestClient.websocket_connect`), created a session, took a real turn, disconnected, cleared the in-memory `SESSIONS` registry (the actual mechanism a real process restart wipes), reconnected on a new WebSocket connection with the same session_id, and confirmed transparent restoration (scores preserved, session continues normally) — plus a not-found control case. **Both tests pass on the first run**, closing the gap the second pass explicitly left documented. Other item-5 checks (PPO/guardrail conflict handling, NaN/Inf robustness) were confirmed already covered by existing test suites (guardrail predicate tests, FLT-04) rather than duplicated.

## 6. Reproducibility hardening

Both PPO V2 scripts previously had zero assertions protecting against silent partial-run acceptance. Added: dev-seed-identity assertion (refuses to run if the imported eval-seed list isn't exactly the development set), per-seed checkpoint-count assertion, duplicate-(seed,step) detection, per-checkpoint row-count assertion, finite-MAE assertion, duplicate-seed-argument rejection, and a hard failure (not a silently-recorded "completed") if a training run produces a truncated checkpoint set. **Re-ran the hardened evaluation script against the existing, already-trained checkpoints: identical results (0.2697/16,384), all new assertions pass** — confirms the hardening didn't change behavior, only added protection.

## 7. Manuscript and claim ledger

`FINAL_MANUSCRIPT_EVIDENCE_V2.md`: extended §XI.2's PPO discussion with the confirmatory-readiness audit and per-seed non-uniformity finding (explicit: no superiority claim made); extended §1c's evaluator discussion with the third refuted fix attempt and the two new adversarial-suite findings; extended §XIII (Reproducibility) with all new scripts/tests. `CLAIM_LEDGER_SYSTEM_PAPER_V1.md`: 10 new entries (SP-34 through SP-43), each traced to its evidence file.

## 8. Testing and final validation

- `tests/unit/test_evaluator_v4_adversarial_development_suite.py`: 10/10 passed (new).
- `tests/integration/test_live_websocket_session_recovery.py`: 2/2 passed (new).
- `research/paper_strengthening/scripts/ppo_v2_checkpoint_selection_eval.py` (hardened, re-run): exit code 0, all new assertions pass, identical results to before hardening.
- Full repository suite (`pytest -q`, `EVALUATOR_MOCK_MODE=1`): **352 passed, 1 failed, 511.98s.** The one failure is the identical, already-documented `test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics` (RL-observation `time_norm` issue, unrelated to speech/confidence scoring) — same test name, same failure, unchanged across every one of the four passes in this engagement. No new failure was introduced.

## 9. Files changed this pass

Modified: `research/paper_strengthening/scripts/ppo_v2_checkpoint_selection_experiment.py`, `ppo_v2_checkpoint_selection_eval.py`, `FINAL_MANUSCRIPT_EVIDENCE_V2.md`, `CLAIM_LEDGER_SYSTEM_PAPER_V1.md`.

New: `PPO_V2_CONFIRMATORY_EVALUATION.md`, `EVALUATOR_V4_VALIDATION.md`, `D1_INDEPENDENT_REVIEW_PACKET.md`, this report, `tests/unit/test_evaluator_v4_adversarial_development_suite.py`, `tests/integration/test_live_websocket_session_recovery.py`.

**No evaluator, orchestrator, database, or qwen production code was modified this pass** — only the two PPO V2 scripts (reproducibility guards, no behavior change) and documentation/tests. No commit, tag, push, or submission was made.

## 10. Research limitations (what the evidence still does not establish)

- Whether PPO V2's checkpoint-selection improvement generalizes beyond the development grid — not established; per-seed non-uniformity (§2.4) means even the development-stage evidence is weaker than the headline aggregate number suggests.
- Why skill=0.80 specifically (not 0.65 or 0.90) is the fragile persona — not established; would need new instrumentation beyond what existing artifacts support.
- Whether the evaluator's logical-reasoning weakness (fluent, wrong, vocabulary-correct answers) is fixable without a new, properly-validated model — not established; three independent embedding-based approaches have now failed for the same underlying reason.
- Whether the two new evaluator findings (vocabulary-paraphrase sensitivity, partial-credit/misconception-tier interaction) matter at scale — not established; each is a single documented case, not a measured frequency.
- Whether the D1 benchmark's underlying construction methodology (once content exists) will hold up to review — cannot be established without content and a reviewer, neither of which exist.

## 11. Next step — the single most consequential outstanding task

**Obtain explicit human authorization to either (a) run the registered confirmatory protocol (`PPO_V2_CONFIRMATORY_EVALUATION.md` §6) on the selected checkpoint, accepting the risk that its per-seed non-uniformity means it may not clear a confirmatory bar, or (b) decline and instead invest in understanding *why* skill=0.80 is uniquely fragile before spending confirmatory data on any checkpoint from this line of work.** This is the one decision every other open thread (the paper's PPO section, whether further PPO-side engineering is worthwhile at all, whether to continue investing in checkpoint-selection variants) is currently blocked behind, and it is the one decision this pass correctly identified it cannot make unilaterally.
