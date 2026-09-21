# P2 INDEPENDENT HIGH-RISK AUDIT (2026-09-21, audit-v2 pass)

Scope: `paper2/manuscript_v1_archive.md` (audited) → `paper2/manuscript.md` (v2). Evidence re-read: `research/results/paper2/paper2_case_level_results.csv`, `research/analysis/phase1/x2_a/*` (incl. `x2a_analysis.py`), `research/confirmatory/X2-B/results/*` (`X2B_REPORT.md`, `metrics_point_ci.csv`), `research/audit/P0_7_HUMAN_ETHICS_FORENSIC.md` and `P0_1_CROSSENCODER_FORENSIC.md` (as cited by the frozen manuscript-preparation files). Only read-only descriptive checks were run (listed in Section 6).

## 1. New findings

| ID | Finding | Evidence | Action taken |
|---|---|---|---|
| P2-F1 | **Terminology error.** v1 called the reference score for all 64 answers "three-rater human consensus" (abstract, RQ, Section IV, tables). Only 54 answers are `mean_of_three`; 10 are adjudicated. | `paper2_case_level_results.csv`: `gold_method` = `mean_of_three` ×54, `expert_adjudication` ×10 | v2 uses "human reference score", defined once with the 54/10 split; "three-rater" is used only for the 54 or for the raters' raw ratings. The frozen file label `expert_adjudication` is explicitly *not* used as a description (a sentence says so). |
| P2-F2 | The locked RQ contained "human consensus". Changing it alters a locked sentence. | claim-lock files | RQ now reads "…agree with human reference scores…". **Author decision D-2** (accept the RQ wording change). |
| P2-F3 | v1 text "under-scored in every category" was made about category *means* but read as about answers, and "under-scored" was undefined. | data | v2 defines under-scored as composite < human reference; 38 of 64, 0 ties, 26 over-scored; category statements are about category means. |
| P2-F4 | The nominal p-value appeared in the Results and again as a numeric in the Discussion objection list. | manuscript v1 | Numeric removed from Discussion; the value appears once (Section VI-B) with the mandated label and the clustering statement. Not in abstract or conclusion. |
| P2-F5 | Interval types were separated in text but not compared in a single table. | — | New Table II (estimate, resampling, cluster unit, interval, role). |
| P2-F6 | Interval type of the AUROC intervals was unstated. | `x2a_analysis.py` lines 110–116; `x2b_run.py` lines 245–251: AUROC replicates are drawn with `two_level_draw` (B = 10,000) | Table V caption states two-level. |
| P2-F7 | Two values for the cross-encoder alone (0.4832 stored R vs 0.4825 re-run in X2-B) were unexplained. | `X2B_REPORT.md`: derived reproduction max \|mapped raw − stored R\| = 0.0005 | Explanatory note added to Section VI-D. |
| P2-F8 | "Composite not safer than R alone" used a safety word for a false-accept comparison. | — | Reworded: "did not accept fewer adversarial answers than R alone". |
| P2-F9 | "word count is informative because of how the answers were constructed" asserts a cause. | — | Reworded to "consistent with a length confound"; explicit that the finding is benchmark-level, exploratory, and not a claim that the evaluator is length-dependent. |
| P2-F10 | "compatible with adaptation toward scoring such answers" (derived vs upstream CE) implied a mechanism. | — | Removed; the difference is reported and not interpreted as evidence about training data. |
| P2-F11 | Pilot-overlap wording ("compatible with optimism from the pilot-based settings") was hedged but not explicit about the overlap. | — | v2: overlapping questions were available during earlier development; an optimistic reading is possible; point estimates only; not held-out validation. |
| P2-F12 | Shared foundational citation missing: injected-instruction probes are related to LLM-grader injection work already in the verified package (Paper 1 [12]). | arXiv:2606.03090 verified | Added as [16] with a limiting sentence (probes target a similarity scorer, not an LLM grader). |
| P2-F13 | Unverified metadata in several references. | Crossref/arXiv check (see `REFERENCE_AUDIT.md`) | [2], [11], [12], [13], [14] now carry verified DOI/pages; [4] states what is verified. |

## 2. Claim-area audit (every area named in the brief)

| Area | v2 status | Notes |
|---|---|---|
| Human reference scores | Fixed | 54 mean-of-three, 10 adjudicated; no "expert/independent/gold" wording (the only occurrences are the negated sentence in Section IV). |
| Rater process / consensus | Fixed | "consensus" no longer used as a term. |
| Adjudication | Disclosed | 10 cases = all 8 keyword-stuffed + 2 partial answers (descriptive (D) split, read from the frozen case-level file); adjudicator number/identity undocumented. |
| Reliability | Qualified | ICC(2,1) 0.9528, ICC(2,k) 0.9838, α 0.9523, each with the "constructed items, categories separated, not natural answers" qualification; not offered as representativeness. |
| Ethics / provenance | Disclosed, unresolved | Table I lists each undocumented item; no repair by prose. Submission gate: see `venue/paper2/PAPER2_SUBMISSION_GATE.md`. |
| Question clustering | Handled | Table II; per-question, leave-one-question-out, within-question. |
| p-value | Fixed (F4) | one occurrence, labelled. |
| Confidence intervals | Fixed (F5, F6) | every interval is typed in text, tables and figure captions. |
| Length | Fixed (F9) | 0.4897 [0.2186, 0.7080], AUROC 0.8864; "competitive", "length confound"; no "learned length". |
| Baselines | OK | BM25 0.3812, TF-IDF 0.245, token overlap 0.4301, upstream CE 0.1454, derived CE 0.4825. |
| CrossEncoder | OK | 16.28% differ; layers 0–3 identical; provenance unrecoverable; overlap cannot be excluded; "partially fine-tuned derivative"; no invented trainer details. |
| Pilot overlap | Fixed (F11) | 0.7092 vs 0.4249. |
| Under-scoring | Fixed (F3) | −0.134; 38/64 (59.4%); category means with n; verbose wrong +0.219; no fairness claim. |
| Robustness | OK | metamorphic 19/21, adversarial 11/13, "author-set criteria", "not a robustness estimate". |
| Generalisation | OK | explicit non-claim in abstract, Sections VII–VIII. |

## 3. Required canonical numbers (checked against files)

| Quantity | Manuscript | Source |
|---|---|---|
| S1 / S2 / R / S1+S2 / S1+R / S2+R / Full | .2070 / .3021 / .4832 / .2894 / .4884 / .4171 / .3812 | `paper2_ablation_results.csv` (via earlier trace; numeric check found all present) |
| Composite − R-only | −0.102 [−0.2849, +0.1174] (two-level) | `x2a_bootstrap_rho_diff.csv` |
| Length-only | ρ .4897 [.2186, .7080]; AUROC .8864 | `metrics_point_ci.csv` |
| Derived CE | ρ .4825; AUROC .7821 | same |
| BM25 / TF-IDF / token overlap | .3812 / .245 / .4301 | same |
| Bias | −0.1338 (−0.134); under-scored 38/64 (re-derived: 38 lower, 0 equal, 26 higher) | case-level file |
| Category means (human / model) | concise .912 / .397; paraphrase .844 / .361; verbose correct .984 / .591 | case-level file (recomputed by `figures/make_fig_p2.py`; see rounding note below) |
| ICC / α | .9528 / .9838 / .9523 | `x2a_agreement.csv` |
| Pilot overlap | .7092 vs .4249 | `x2a_overlap.csv` |

**Rounding note (resolved):** the composite's keyword-stuffed category mean is exactly 0.34450 (difference from the human mean 0.30500 is +0.03950). The figure script prints 0.344 because of floating-point round-half-even; Table VI prints 0.345 and +0.040 (round half up). Both are the same value; no correction needed. No author decision required.

## 4. Disposition of the 19 high-risk objections (after v2)

Definitions: **Answered** = the stored evidence and the manuscript address the objection (not that it is refuted); **Partial** = addressed in part; **Unresolved** = cannot be closed by any edit or by existing data.

| # | Objection | Disposition | Manuscript location / remaining gap |
|---|---|---|---|
| 1 | Small benchmark | Partial | Intervals foregrounded (Table II; abstract); adequacy of N unknowable without a precision target |
| 2 | Only 8 questions | Partial | two-level, question-only, LOQO, per-question; representativeness unresolved |
| 3 | Author construction | **Unresolved** | disclosed as primary limitation; artifact not excludable |
| 4 | Length artifact | Partial | length baseline, category word counts, "length confound"; natural-answer length relation unknown |
| 5 | Rater independence | **Unresolved** | Table I "not documented"; no claim |
| 6 | Blinding | **Unresolved** (sheet content verified only) | Table I |
| 7 | Ethics / consent | **Unresolved** | Table I; submission gate |
| 8 | Provenance (identity, timing, adjudicators) | **Unresolved** | Table I |
| 9 | Clustering | Answered | Table II, three types |
| 10 | p-value | Answered | one labelled occurrence |
| 11 | CrossEncoder provenance | **Unresolved** | Section III, VIII |
| 12 | Pilot overlap | Partial | point estimates, no held-out claim; confounded with difficulty |
| 13 | Weak baselines / no LLM judge | Partial | disclosed as not run |
| 14 | R-only above composite | Answered (as a finding) | Table IV, intervals for differences include zero; cause untested |
| 15 | Concise/paraphrase under-scoring | Partial | descriptive, 2–8 per category, no fairness claim |
| 16 | Natural-answer generalisation | **Unresolved** | explicit non-claim |
| 17 | High human agreement | Answered | qualified, not used as validity evidence |
| 18 | Adjudicated keyword-stuffed reference | Partial | disclosed; adjudicator identity unknown |
| 19 | Why an exploratory paper | Partial | Section VII rationale; depends on venue |

Totals: Answered 4 (9, 10, 14, 17), Partial 8 (1, 2, 4, 12, 13, 15, 18, 19), Unresolved 7 (3, 5, 6, 7, 8, 11, 16).

## 5. Reviewer attack pass (Phase 14) — exact sentences

| Attack | Manuscript sentence | Survives? | Wording |
|---|---|---|---|
| "The benchmark is written by its developers." | "The benchmark is author-constructed, small and not representative of natural candidate answers" (IV) | Survives as a limitation | unchanged |
| "N = 64, 8 questions are tiny." | "the two-level interval spans about 0.15–0.65, the results are exploratory, and generalisation is not claimed" (VII) | Survives | unchanged |
| "Length alone beats your composite." | "Word count was competitive … it does not show that the evaluator is inherently length-dependent" (VI-D). Note: the word-count point estimate (0.4897) is higher than the composite (0.3812); intervals overlap widely. | Survives; stated as a finding | v2 |
| "Raters not documented as independent." | Table I, "not documented"; "rater independence … not documented" (abstract) | Survives | unchanged |
| "No ethics/consent records." | Table I; limitation; submission gate file | **Survives as a venue-level risk** | see gate |
| "CrossEncoder training data unknown." | Section III: "Overlap … cannot be excluded" | Survives | unchanged |
| "Nominal p ignores clustering." | "is not a confirmatory significance test" (VI-B) | Yes | v2 |
| "High human agreement is caused by constructed categories." | Section IV: between-category share of variance 0.98–0.99; Section VI-A qualification | Yes | unchanged |
| "Why publish an exploratory result?" | Section VII | Partial | value is the diagnostics; venue-dependent |

## 6. Read-only checks run in this audit
(1) `gold_method` counts and category split (54/10; 8 keyword-stuffed + 2 partial adjudicated). (2) Strict under-scored count (38 lower, 0 equal, 26 higher; mean error −0.13377). (3) Spearman recomputed from the case-level file = 0.3812 (a check of the stored value, not a new analysis). (4) Category means for Table VI and Fig. 3. (5) Which resampling produced AUROC intervals (code inspection). No new inference and no unregistered post-hoc analysis.

## 7. Verdict
**RED for submission to any venue requiring ethics/consent/rater-provenance documentation; YELLOW for template conversion of the exploratory manuscript** (the science is stated as far as the record supports; the venue gate is HOLD). See `venue/paper2/PAPER2_SUBMISSION_GATE.md`.
