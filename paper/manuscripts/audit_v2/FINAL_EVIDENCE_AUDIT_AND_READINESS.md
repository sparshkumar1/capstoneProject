# Final Evidence Audit and Publication-Readiness Review — Paper 3

**Date:** 2026-09-28. **Scope:** read-only verification of `paper/manuscripts/paper3/manuscript.md` against `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`, the prior audit report (`audit_v2/E1_SERIES_RECONCILIATION_AUDIT.md`), `claim_ledger_v2.md`, `limitations_checklist.md`, and the underlying X3-A/x3_0 evidence, followed by minimal, evidence-traced edits. No training, PPO experiment, confirmatory evaluation, or D1 access occurred. No checkpoint, raw dataset, frozen output, protocol, or historical result was modified. Nothing was committed, tagged, pushed or submitted.

## 1. Executive verdict

The manuscript's primary, pre-registered claim (X3-A equivalence result) remains fully supported and unchanged by this pass. This audit closed the one open item flagged by the prior audit (Section V-G's two unverified numeric claims) and found, independently, one genuine mischaracterization (a "last logging window" label that does not match the underlying counter's code) and one new, well-evidenced, previously-unreported fact (a 120/120 oracle-vs-PPO divergence on guardrail-free turns). Both are now corrected/added in the manuscript with full traceability. The manuscript's reference list was already independently verified against Crossref/arXiv in a prior pass (`reference_audit_p3.md`, 2026-09-21) and required no changes. Two minor IEEE-style acronym-definition gaps (SD, MLP) were fixed. **The manuscript is in a defensible, publication-ready state for its own stated scope** (a simulation-only equivalence study); no claim was strengthened, and several were completed or corrected toward greater precision.

## 2. Section V-G verification (the task's priority item)

**(a) Training-time Same-action share.** Source: `research/analysis/phase1/x3_0/x3_0a_training_action_shares.csv`, derived from `research/results/paper3/paper3_convergence_results.csv` (frozen), whose `action_easier/same/harder_pct` columns are produced by `TrainingConvergenceCallback` in `research/scripts/execute_paper3_study.py` (lines 120–172).
- **Values — Verified.** 0.5069, 0.5130, 0.5345, 0.5168, 0.5247 for seeds 42/123/456/789/999 match the stored CSV exactly; no denominator, exclusion, duplication or seed-attribution issue found (one row per seed, `total_timesteps=24576` for all five, no missing/duplicate seeds).
- **Characterization — was Incorrect, now corrected.** The manuscript (and its source, `X3_0A_REPORT.md` §7) described this as "the last logging window." Reading `TrainingConvergenceCallback.__init__` (`self.action_counts = {0:0,1:0,2:0}`) and `_on_step` (only ever increments this dict; no reset call anywhere in the class, including no reset in `_on_training_end`) shows the percentage logged at any timestep is the **cumulative share since the start of training**, not a windowed statistic. (For contrast, `mean_reward_rolling` in the same callback genuinely is windowed, via `self.episode_rewards[-100:]` — only the action-share fields were mischaracterized.) The manuscript now states this correctly. `X3_0A_REPORT.md` itself is a hash-pinned historical output (`manifest_X3-0a.json` records its SHA-256) and was **not edited**, per the preservation constraint; the discrepancy is flagged here rather than silently repaired in that file.

**(b) Seed-123 probe-sweep count (8/66).** Source: `research/analysis/phase1/x3_0/x3_0a_sensitivity_probes.csv`.
- **Value — Verified.** Independently re-summed from the raw per-dimension counts (`s0_perf`: 0/11, `s1_avg_perf`: 2/11, `s2_conf`: 0/11, `s3_hes`: 0/11, `s4_progress`: 0/11, `s5_diff`: 6/11 non-Same probes) = 8 of 66 (6 dimensions × 11 probes each). No duplicate or excluded rows found. The manuscript's characterization ("at one neutral point of the other state coordinates") matches the file's own methodology note.

**(c) New finding, developed to close the same evidence gap (not previously computed or stored anywhere):** using the frozen `oracle_action_from_obs` rule (`rl/env/interview_env.py:193–223`, re-read directly in this pass) and the exact `avg_perf` construction from the frozen `simulate()` function (`x3a_lib.py:106–149`, rolling mean of `hist[-5:]` including the current step), this audit reconstructed the oracle's proposal at each of PPO+G's 1,250 five-persona-replay turns using only stored `x3_0c_replay_turn_log.csv` values (perf, conf, hes, difficulty_before) — no simulation, no RNG, no re-running any policy. Result: 687 guardrail-free turns (1250 − 563, consistent with Table III); on those, the oracle proposes Harder 120 times, and PPO's raw proposal is Same on all 120. A sanity check (raw_action must equal final_action when no guardrail activates) passed with zero mismatches, validating the reconstruction. This is now stated in Section V-G, explicitly hedged: the oracle is an authored rule, not a validated optimal policy, so this is evidence of a systematic divergence pattern, not evidence that PPO is "wrong."

**Classification summary:** (a) value **Verified**, characterization **Incorrect → Corrected**; (b) **Verified**; (c) **New, Verified** (independently derived and cross-checked against Table III's own counts).

## 3. Scientific consistency

- **X3-A primary result** (Δ −0.0350, CI [−0.0818, +0.0021], margin ±0.12) — unchanged, re-confirmed present and correctly stated; this audit made no changes to Sections IV, V-A or V-B.
- **Guardrail facts restated in the task prompt** — all independently re-verified directly from `x3_0c_replay_turn_log.csv` in this pass (not merely re-read from the manuscript or a summary file): activation 563/1250 = 45.04%; overrides 99/1250 = 7.92%; G6 zero activations ("never fires"); G5 205 activations, zero overrides. All match the manuscript exactly.
- **Heuristic+G MAE kept separate by population**, as instructed: five-persona replay 0.473, 40-persona confirmatory grid 1.533 (stated explicitly in Section V-F as of the prior audit pass), E1-internal 24-cell development grid 0.2674 (referenced only in the Section VI paragraph about the later, separate dynamics-matching check, never merged into Table I–IV). No sentence in the manuscript uses one population's Heuristic+G value to characterize another.
- **"PPO+G 1.069 vs Heuristic+G 1.533 does not establish PPO-specific superiority"** — this is already the manuscript's own position: Section V-F states Constant-Same+G (1.104) also beats Heuristic+G on this grid, and Table I frames the primary comparison as PPO-vs-Constant-Same, not PPO-vs-Heuristic. No change was needed here; verified consistent.
- **E1 Dynamics Match V1** (OOO 0.273485, MMM 0.390303) — these exact figures were independently recomputed from the raw per-cell CSV in the prior audit pass (matched to 6+ decimal places) and are referenced in Section VI only as separate, non-confirmatory, differently-populated evidence, per instruction. The manuscript's wording already says "the dominant contributor" for the step-size/floor factor, not universal causality — verified as already correctly hedged, no change needed.
- **Development vs. confirmatory evidence** — remains separated throughout: the one Section VI paragraph referencing E1-series work is explicit that its grid, population and registration are different from X3-A's, and that its numbers are "not merged with this study's."

## 4. References

A dedicated reference audit already exists (`paper/manuscripts/audit_v2/reference_audit_p3.md`, dated 2026-09-21) verifying all 14 references against Crossref and the arXiv API: existence, DOI, authors, venue, volume/issue/pages, and date, plus a claim-support cross-check against `QUOTE_AUDIT.md`. This pass re-read that audit rather than re-querying every source, since no reference was added, removed, or re-cited by this session's edits (the reference list itself is untouched). Its findings, restated for this report:
- **11 of 14 peer-reviewed, 3 preprints** ([5] Schmucker et al., [6] Jiang et al., [8] Olukola & Rahimi) — correctly labeled as preprints in-text.
- **Two open items, both already disclosed in the manuscript, neither invented or silently resolved:** [7] (Che et al., *Sci. Rep.*) has a verified DOI and volume but its article number was not confirmed; [1] (Kadam et al.) is cited from its publisher landing page only (abstract/highlights/contributions), with the manuscript itself stating "whose body we did not read beyond its abstract, highlights and contribution statements" (Section I). Both are pre-existing, accurately flagged limitations, not new problems.
- No reference number is orphaned or unused; [1]–[14] all appear in the body (verified by a fresh read of Sections I, II, VI in this pass).
- **No new reference was invented, added, or altered by this audit.**

## 5. IEEE readiness

Checked directly against `manuscript.md` (this pass; no PDF rebuild was performed — the existing venue-specific PDF exports under `paper/manuscripts/venue/HCII_P3/preview/` predate this session's edits and were not regenerated, since regenerating them is outside the scope of "re-audit manuscript.md" and requires running a build script this audit did not execute):
- **Structure:** Abstract → Keywords → I Introduction → II Related Work → III Simulator/Policies/Guardrails → IV Study Design → V Results (A–G) → VI Discussion → VII Threats to Validity and Limitations → VIII Reproducibility → IX Conclusion → References. Roman-numeral top-level sections, consistent IEEE-style em-dash abstract/keyword labels. No missing or duplicated section numbers.
- **Figures/Tables:** Fig. 1–3 and Table I–IV, sequential, each referenced in the body before or at its point of appearance. No orphaned figure/table.
- **Acronyms — two gaps found and fixed (both non-numeric, cosmetic):** "SD" (standard deviation) and "MLP" (multi-layer perceptron) were used without a first-use expansion; both now spelled out at first occurrence (Table I and Section III respectively). No other undefined acronym was found in a fresh scan of the body text.
- **Units, CIs, rounding:** difficulty/MAE consistently unitless (1–5 raw or normalized scale), all intervals consistently formatted as "[lower, upper]" with "95%" stated at each first use in a subsection. **One pre-existing, unresolved stylistic inconsistency, not fixed:** primary results (Tables I–II) are reported to 4 decimal places while several secondary contrasts (Table IV, Section V-E's volatility figures) are reported to 5 — this reflects the differing precision stored in their respective frozen source files (`x3a_decision.json` vs `x3a_secondary_contrasts.csv`) and was left alone rather than arbitrarily re-rounded, since changing precision without a stated reproducible reason would itself be a fabrication risk; flagged here as a camera-ready copy-editing item for the authors to decide on, not resolved by this audit.
- **Statistical language:** no significance-testing language was found where only descriptive/bootstrap-interval language is warranted; "equivalent" is used only for the pre-specified primary/sensitivity results, consistent with the stated protocol.
- **Venue:** per `paper/README.md`, the target venue remains formally TBD; venue-specific ports exist under `paper/manuscripts/venue/` (e.g., `HCII_P3`) but are separate, exploratory artifacts from an earlier session and were not touched or re-verified here, since the task named `manuscript.md` specifically.

**Readiness statement:** manuscript.md is structurally IEEE-consistent and numerically verified end-to-end for the claims it makes; it is not yet bound to a specific venue's page limit/template, per the project's own stated open decision.

## 6. Files changed, with summary

1. `paper/manuscripts/paper3/manuscript.md` — 3 edits this pass: (i) Section V-G's training-action-share characterization corrected from "last logging window" to "cumulative over the full training run," with the discrepancy's source cited; (ii) a new sentence added to Section V-G reporting the independently-reconstructed 687-guardrail-free-turn oracle-vs-PPO Harder/Same divergence (120/120); (iii) two acronym-definition fixes (SD in Table I, MLP in Section III).
2. `paper/manuscripts/paper3/claim_ledger_v2.md` — row L2-P3-13 updated to record the correction and its source; two new rows (L2-P3-20, L2-P3-21) added for the V-G resolution and the new oracle-divergence finding.
3. `paper/manuscripts/paper3/limitations_checklist.md` — unchanged this pass (no new limitation was introduced; the resolved items were evidence gaps, not limitations).
4. This file and no other new file were created.

No file outside `paper/manuscripts/paper3/` and `paper/manuscripts/audit_v2/` was modified.

## 7. Validation

- `git diff --stat` on `paper/manuscripts/paper3/` (this pass, on top of the prior pass's uncommitted edits): 3 files, 16 insertions / 7 deletions — matches the 3 described edits, no unintended change.
- `git status --short` on every protected/frozen directory (`research/papers/`, `research/results/paper3/`, `research/CLAUDE_HANDOFF/`, `research/audit/`, `rl/checkpoints/`, `ablation/results/`, `research/experiments/paper3/frozen_config.yaml`, `research/confirmatory/`, `research/analysis/`, `research/data/evaluator_benchmark/`, `research/scripts/execute_paper3_study.py`) — clean, no changes.
- Hash spot-checks (frozen config, human-gold CSV, deployed checkpoint, `x3a_decision.json`, `x3_0c_replay_turn_log.csv`, `X3_0A_REPORT.md`) — `X3_0A_REPORT.md`'s hash matches its own manifest-recorded value exactly, confirming it was correctly left unedited despite containing the mischaracterization discussed in Section 2 above; all others unchanged from prior checks.
- No training, evaluation, or simulation script was executed. The only code-adjacent action was read-only reconstruction of the oracle rule against already-stored CSV values, run in a scratch script outside the repository (no repository file was executed as part of a pipeline, and no repository file changed as a result).
- Nothing was committed, tagged, or pushed.

## 8. Outstanding blockers

- Venue is still formally TBD (project-level open decision, not something this audit resolves).
- Table IV/Table I-II's rounding-precision inconsistency (4 vs 5 decimal places) is a cosmetic camera-ready item, not a numerical error, and is left for the authors' venue-formatting pass.
- `X3_0A_REPORT.md`'s own "last logging window" phrase remains uncorrected in that historical file (by design — it is a hash-pinned frozen output); if the authors want it corrected there too, that would need an explicit, separate re-registration/versioning decision, since it is listed as historical evidence.
- Section V-G's evaluation-time Same-action share remains genuinely unstored/unrecoverable (not a blocker introduced by this audit — already disclosed in the manuscript as such).

## 9. Next steps (recommendation, not a decision)

No further evidence-gathering is indicated by this pass — the one open item (Section V-G) is now closed, and no other numeric claim in the manuscript remains unverified. If the authors intend to proceed toward submission, the remaining work is venue selection and the corresponding template/page-limit compliance pass (explicitly out of scope until a venue is chosen, per the project's own stated policy), not further scientific audit or additional experimentation.
