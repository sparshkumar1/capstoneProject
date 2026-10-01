# Final Scientific Audit — E1-series Reconciliation and Paper 3 Strengthening Pass

**Date:** 2026-09-28. **Scope:** read-only audit of the full evidence base (Paper 3's X3-A confirmatory study plus the E1/E1-Improve V1/E1-Improve V2/E1 Dynamics Match V1 exploratory series), followed by conservative, traceable edits to `paper/manuscripts/paper3/manuscript.md` and its supporting ledgers. No training, retraining, or confirmatory evaluation was run. No frozen file, checkpoint, protocol, or historical result was modified. Nothing was pushed.

## 1. Executive summary and overall scientific assessment

`paper/manuscripts/paper3/manuscript.md` (v2) is a mature, heavily self-audited manuscript (its own `claim_ledger_v2.md`, `reviewer_attack_audit.md`, `limitations_checklist.md` already existed before this pass). It reports a pre-registered equivalence result (X3-A: PPO+guardrail vs. Constant-Same+guardrail, 40 personas × 5 training seeds, Δ = −0.0350, 95% CI [−0.0818, +0.0021], equivalent within an author-selected ±0.12 margin) plus extensive, carefully-hedged behavioural accounting. Independent re-verification found **no numerical errors in the manuscript's own tables** (Tables I–IV all reproduce exactly from source files, including an independent re-aggregation of the 1250-turn guardrail log). The manuscript's core claim — no demonstrated PPO advantage over a state-blind constant, and no claim of learner benefit — is well-supported and does not need weakening.

This session separately ran four more rounds of PPO experimentation (E1, E1-Improve V1, E1-Improve V2, E1 Dynamics Match V1) under `research/paper_strengthening/`, entirely outside the X3-A protocol, on a different development-only evaluation grid, explicitly never touching confirmatory data. That series consistently reinforces the paper's core finding (no PPO configuration tested — budget-selected, gate-extended, or dynamics-matched — beat a simple heuristic on its own grid) and, more specifically, empirically tested and refuted the hypothesis that the documented train/eval dynamics mismatch was suppressing a real PPO advantage: deliberately matching the mismatch made tracking error worse, not better. This is genuinely new, decision-relevant information for the paper's Discussion and was not previously in it.

The audit also found and corrected a real gap: **the paper's own data implies a raw Heuristic+G tracking error of 1.533 on its 40-persona grid — worse than the trivial "never move" policy (1.000)** — but the manuscript only ever stated the *difference* (−0.46414), never the raw value. This is a materially informative number (it shows the heuristic's ranking against PPO and against a constant policy reverses between the paper's two evaluation populations) that is now stated explicitly.

**Overall assessment: the manuscript was already scientifically sound and conservatively worded. The edits made are additive completions of already-available evidence (a third dynamics mismatch, a raw baseline value, a properly-scoped mention of later confirmatory-adjacent exploratory evidence) rather than corrections of an error.** No claim in the paper needed to be weakened; a few needed to be completed.

## 2. Verified findings and discrepancies

**Independently reverified (all exact matches, no discrepancies):**
- Table I primary result, Table II's 7 sensitivity estimates, Table III's guardrail-accounting counts (563/99/464/41 — independently re-aggregated from the raw 3500-row turn log, not just read from a summary), Table IV's 8 secondary-contrast rows — all reproduce exactly from `research/confirmatory/X3-A/results/` and `research/analysis/phase1/x3_0/` source files.
- E1 Dynamics Match V1's pooled MAE for arms OOO (0.273485) and MMM (0.390303) at 24,576 steps were independently recomputed by this session directly from the raw 24-cell-x-5-seed per-cell CSV (`e1dynmatch_per_cell_results.csv`) and matched the stored decision summary to 6+ decimal places. The 5 regressed cells (all at skill ≥ 0.80, k ≥ 0.30; largest +0.836 at skill=0.80,k=0.60), the per-seed paired MMM-minus-OOO differences (all positive, i.e. worse, across all 5 seeds), and the extended-budget trigger's correctly-negative evaluation were all confirmed from raw data, not merely read from the report.
- The three previously-documented train/eval dynamics mismatches (step size, horizon) and the newly-found third mismatch (starting-difficulty distribution) were re-read directly from `rl/env/interview_env.py` in this pass (lines 63, 306, 401–405), not taken on the E1 reports' word.
- Frozen-artifact hashes (P3 frozen config, the deployed seed-123 checkpoint, the human-gold benchmark CSV) and the shared RL training log hash all match their previously recorded values; `git status` on every protected directory is clean.

**Discrepancy found and corrected:** the manuscript's raw Heuristic+G tracking error on the 40-persona confirmatory grid (1.533) was never stated as a number, only recoverable by subtracting Table IV's difference row from Table I's PPO+G value. It is now stated explicitly (Section V-F), sourced to `research/confirmatory/X3-A/results/x3a_condition_summary.csv`, row `Heuristic|G`.

**Gap found and corrected:** Section III and Section VII stated only two of the three confirmed train/eval dynamics mismatches (horizon; step continuity). The third (training starts from `Uniform(0.3, 0.7)` difficulty, evaluation always starts at a fixed 0.6-normalised difficulty — `interview_env.py:306`) was missing from both sections and has been added, along with a quantified floor difference (0.1 training vs. 0.2 evaluation).

**No leakage found.** A background agent independently grepped the entire `research/paper_strengthening/` tree for any reference to the X3-A confirmatory seed range (21021–40040) or held-out profiles and found none used, only disclosed as untouched. One naming-hygiene point is worth recording, not because it is leakage but because it could read as sloppy: E1's "development" evaluation seeds `[1001, 2002, 3003, 4004, 5005]` are numerically identical to the *first five* of X3-A's own 20-seed confirmatory pool (1001…20020). The simulated populations are unrelated (E1 evaluates a single "normal"-type candidate with a synthetic k-decoupling offset; X3-A evaluates five distinct authored persona-type classes), so no X3-A result, checkpoint, or persona data was reused — but the seed *integers* overlap. This is disclosed here for completeness; it does not affect any number in the paper.

## 3. Consolidated experiment comparison

| Experiment | Status | Population | Baseline comparator (raw MAE) | PPO's best result | Beats baseline? |
|---|---|---|---|---|---|
| P3 frozen study (original) | Frozen, historical | 5 personas × 5 seeds | Heuristic (no G): 0.473 | PPO+G 0.673–0.687 | No — guardrails, not PPO, explain the gain over Fixed |
| X3-A (confirmatory, this paper) | Pre-registered, executed, primary evidence of this manuscript | 40 personas × 5 training seeds × 20 eval seeds | Heuristic+G (this grid): **1.533** (newly stated) | Equivalent to Constant-Same+G (Δ −0.035, within ±0.12) | Not tested against Heuristic+G as the primary comparison; descriptively, PPO+G (1.069) beats Heuristic+G (1.533) here, but Constant-Same+G (1.104) does too, so this does not credit PPO specifically |
| X3-A five-persona replay | Same registration, secondary/descriptive | 5 personas × 5 train × 5 eval seeds | Heuristic+G: 0.473 | PPO+G: 0.677 | No |
| E1 development run | Exploratory, dev-only, this session | 24-cell single-persona-type grid × 5 dev seeds | Heuristic+G (this grid): 0.2674 | B2 primary-budget: 0.2735 | No (marginally worse; also budget-fragile) |
| E1-Improve V1 | Exploratory, dev-only | same grid | 0.2674 | B2@16,384: 0.2697 | No (within noise) |
| E1-Improve V2 | Exploratory, dev-only | same grid | 0.2674 | unchanged (4/5 candidate gates proved no-ops) | No |
| E1 Dynamics Match V1 | Exploratory, dev-only, pre-registered internally | same grid, 2×2×2 factorial | 0.2674 | OOM: 0.2702 | No; matching dynamics (MMM) made it worse, 0.3903 |

**What this table does and does not license:** four different, non-comparable evaluation populations produce four different Heuristic-vs-PPO orderings. This is not a contradiction — each result is population-specific and already labelled as such in its own report — but no single number from this table should be quoted as "the" PPO-vs-Heuristic comparison. The paper's own primary claim (equivalence of PPO+G and Constant-Same+G on the 40-persona confirmatory grid) is unaffected by any of the exploratory rows; those rows are cited in the paper (Section VI) only as later, separate, non-confirmatory context for the training/evaluation mismatch discussion, never as additional confirmatory evidence.

## 4. Claim-by-claim audit of the paper's most important statements

Using the classification scheme (A: directly supported; B: supported, narrower wording needed; C: exploratory, needs explicit qualification; D: unsupported):

- **Abstract's equivalence claim, margin, and superiority statement** — **A**. Matches `x3a_decision.json` exactly.
- **"Equivalence does not mean identical behaviour" + guardrail/divergence/volatility figures in the abstract** — **A**. Independently re-verified from raw turn logs.
- **Section III's training/evaluation description** — was **B** (materially incomplete — missing one of three confirmed mismatches); now **A** after this pass's edit.
- **Section V-F's heuristic comparison** — was **B** (correct but incomplete — omitted a materially informative raw value); now **A** after this pass's edit.
- **Section VI/VII's framing of PPO's lack of demonstrated advantage** — **A**, and now additionally reinforced (not merely asserted) by the newly-added, properly-scoped paragraph citing the separate dynamics-matching investigation.
- **Every "no claim of X" / "does not show Y" hedge throughout (Sections IV–IX)** — **A**. These are stated more conservatively than the underlying data would even require in most cases; none needed loosening or tightening.
- **Reference list [1]–[14]** — not independently re-verified in this pass (out of scope; already covered by `inventory.md`'s own verification-level column); no new issues surfaced.
- Nothing in the manuscript was classified **D** (unsupported, requiring removal). No claim required removal or retraction.

## 5. Exact files changed, with summary of each change

1. **`paper/manuscripts/paper3/manuscript.md`** — 4 edits, all additive completions of already-verified stored data, no existing sentence's meaning was reversed or weakened:
   - Section III: added the third confirmed train/eval mismatch (starting-difficulty distribution) and quantified the floor difference (0.1 vs 0.2).
   - Section VII ("Training and evaluation"): same addition, mirrored into the limitations text.
   - Section V-F: added the raw Heuristic+G grid MAE (1.533), its derivation, and a sentence on the heuristic's rank reversal across populations.
   - Section VI: added one new paragraph ("A later, separate check of the training/evaluation mismatch") summarizing E1 Dynamics Match V1 (and, briefly, the two earlier bounded improvement attempts) as separate, non-confirmatory, differently-populated evidence, explicitly scoped as not bearing on the primary equivalence result.
2. **`paper/manuscripts/paper3/claim_ledger_v2.md`** — 4 new rows (L2-P3-17 through L2-P3-19, one row covers two closely related facts) documenting the source, verification method, and manuscript location of each new/changed claim, following the file's existing format.
3. **`paper/manuscripts/paper3/limitations_checklist.md`** — one existing row's wording expanded (row 8) and two new rows added (23, 24) for the heuristic rank-reversal and the later dynamics-matching check.

No other file under `paper/`, `research/`, or `rl/` was modified. `git status` on every frozen/protected directory (`research/papers/`, `research/results/paper3/`, `research/CLAUDE_HANDOFF/`, `research/audit/`, `rl/checkpoints/`, `ablation/results/`, `research/confirmatory/`, `research/analysis/`) is clean.

## 6. Important claims that remain unsupported or require additional evidence

- Section V-G's training-time Same-action shares and the seed-123 probe-sweep count (8/66) were **not independently re-derived** by this audit (the underlying source file was not located in this pass); they were already flagged in `claim_ledger.md` and remain at the same verification status as before this audit. Not changed.
- The X3-A protocol's equivalence margin (±0.12) and superiority threshold (−0.20) remain, as the paper itself already states, without external literature justification. This audit did not find one and made no attempt to manufacture one.
- No new evidence bears on real-learner effectiveness, the deployed-vs-evaluated checkpoint mismatch, or any of the other pre-existing limitations already itemized in `limitations_checklist.md` items 1–22; this audit neither strengthened nor weakened those.

## 7. Remaining methodological limitations and threats to validity

All previously identified by the paper's own Section VII stand unchanged. Newly surfaced by this audit:
- The E1-series development seeds numerically overlap the first five values of X3-A's confirmatory seed pool (Section 2 above). Not leakage (different simulated populations), but worth the authors' awareness if E1-series work is ever extended.
- The E1-series' own internal Heuristic+G baseline (0.2674) is computed on a grid that varies only a single authored persona type (via a synthetic confidence/hesitation decoupling parameter) rather than the five distinct persona-type classes used in this paper's own studies — it is a narrower population than either of the paper's own two evaluation grids and should not be read as a fourth confirmation of anything about the paper's five-persona-type construction.

## 8. Test, formatting, and integrity-check results

- Frozen-file hash spot checks (P3 frozen config, deployed seed-123 checkpoint, human-gold benchmark CSV) — all match previously recorded values.
- Shared RL training log hash — unchanged from its E1 Dynamics Match V1 pre/post run values.
- `git status --short` on every protected directory — clean, no changes.
- `git diff --stat` on the edited files — exactly the 3 intended files, 11 insertions / 4 deletions, no unintended changes.
- No training, retraining, or evaluation script was executed during this audit pass. No test suite run was required by the scope of the edits (prose/documentation changes only, no code changed).

## 9. Work deliberately not performed

- No new training, retraining, fine-tuning, or simulation campaign of any kind.
- No confirmatory evaluation, no D1, no access to the X3-A confirmatory seed range (21021–40040) or held-out profiles.
- No modification to any frozen source, evaluator, reward function, PPO state/action definition, guardrail, checkpoint, or historical result file.
- No retrospective change to any registered protocol or its criteria (E1 Dynamics Match V1's extended-budget trigger, X3-A's equivalence margin, etc. are all reported as originally registered).
- No push, publish, or commit was made.
- No attempt to independently re-verify Section V-G's action-share numbers or the full reference list beyond what `inventory.md` already recorded — flagged above (Section 6) rather than assumed.
- No merging of the E1-series exploratory numbers into the paper's primary tables (Table I–IV) or abstract; they were added only as clearly-scoped supplementary Discussion context, per the explicit instruction not to treat development iterations as confirmatory replications.

## 10. Recommended next step

The manuscript is in a stronger, more complete state than before this pass, with no open numerical discrepancies. The single most defensible next step, based only on what this audit examined, is **not** further exploratory PPO experimentation (four independent lines have now converged on the same non-result) but either (a) locating and independently re-verifying Section V-G's stored action-share source file to close the one remaining unverified claim in the claim ledger, or (b) if the paper is otherwise considered complete, proceeding to venue-formatting and reference-finalization work, which this audit did not touch.
