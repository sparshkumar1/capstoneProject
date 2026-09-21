# FINAL MANUSCRIPT AUDIT (2026-09-21)

Scope: three first-draft manuscripts (Markdown sources) and their support files under `paper/manuscripts/`. No frozen evidence, code, checkpoint, result or protocol was modified; no experiment or build was run; nothing was committed, pushed, tagged, frozen or submitted.

## 1. Repository state
| | Before drafting | After drafting |
|---|---|---|
| HEAD | `11b7fe6e4c4cfedbd5a05c7de8aab0cd2fba1e0f` (branch `workspace/human-eval-clean-push`) | unchanged |
| `git status --short` entries | 55 (34 tracked modified from the earlier claim-lock passes, 21 untracked including `paper/`) | 55 (same set) |
| New files | — | all under `paper/manuscripts/` (untracked; `paper/` was already untracked) |
| `git diff --check` | — | exit 0 (only pre-existing LF→CRLF notices for files edited in earlier passes) |

## 2. Phases completed
1 Evidence audit and map (claim matrices, manuscript-preparation files, stored result files read directly for every reported number) · 2 Paper 1 draft · 3 Paper 1 adversarial audit · 4 Paper 2 draft · 5 Paper 2 methodological audit (`PAPER2_HIGH_RISK_REVIEW.md`) · 6 Paper 3 draft · 7 Paper 3 adversarial audit · 8 Cross-paper overlap · 9 Venue-fit audit · 10 Formatting readiness (below).

## 3. Numerical consistency
- Automated trace (`cross/numeric_trace_check.py`): every decimal number with at least three decimals in each manuscript body (Paper 2: 176 distinct, Paper 3: 85) was found in the listed frozen source files (0 unmatched); Paper 1's two-decimal numbers were checked separately (1 unmatched: "8.15 GB", a unit conversion of the recorded `mem_total` 8,154,980,352 bytes). The check shows presence, not correct attribution; attribution was checked by hand against the claim ledgers.
- Paper 2 intervals are never merged: case-level [0.1575, 0.5774]; two-level [0.1529, 0.6490]; question-only [0.3066, 0.5888]; in every table each interval carries its type. The composite's two-level upper bound is 0.6490 in X2-A and 0.6473 in X2-B (different bootstrap streams); the manuscript states this.
- Paper 3: 563/1250 = 45.0%; 99/1250 = 7.9%; 41/125; 50/125 (final-action sequence); 25/125 (executed path); 5/125 (session MAE); overrides by direction 30 / 30 / 34 / 5 (sum 99; the 39 Harder proposals replaced = 34 + 5); 464 = 563 − 99 (82.4%).
- Abstract–introduction–results–conclusion comparison: quantitative statements match in all three papers. One conclusion sentence in Paper 2 was reworded to avoid implying a significant difference (composite − R-only interval includes zero).

## 4. New descriptive figures computed during drafting (read-only arithmetic on frozen files; labelled (D) in the text; author to confirm inclusion)
| Paper | Figure | Source file | Also recorded elsewhere |
|---|---|---|---|
| 2 | 38 of 64 answers under-scored (59.4%) | `results/paper2/paper2_case_level_results.csv` | `audit/P0_P1_DECISION_PLAN.md` |
| 2 | mean word count by category (115.6 verbose correct; 17.6–41.4 others) | `confirmatory/X2-B/results/scores.csv` (`length_only` column) | no |
| 2 | all 8 keyword-stuffed and 2 partial answers were the adjudicated cases | `results/paper2/paper2_case_level_results.csv` (`gold_method`) | 10 adjudicated cases recorded; the category split is new |
| 3 | override direction tally 30 / 30 / 34 / 5 | `analysis/phase1/x3_0/x3_0c_replay_turn_log.csv` | `audit/P0_4_GUARDRAIL_FORENSIC.md` §3 |
| 3 | Constant-Same without guardrails MAE = 1.000 by construction (start 3.0 at the centre of the target range) | arithmetic from `x3a_config.json` | matches stored 1.000 |

## 5. Places where the drafting brief and the stored record differ (stored record used)
- Per-question Spearman range: stored 0.4364–0.9048, reported as 0.44–0.90 (brief: ".44–.91").
- "10 expert-adjudication cases": the frozen file's `gold_method` label is `expert_adjudication`; the manuscript says "adjudicated cases" and states that the number, identity and qualifications of adjudicators are not documented.
- "Blinded" wording: the rating sheets omit category labels and evaluator scores (header verified); no attestation of what raters saw exists. The manuscript states only the sheet content.
- Benchmark README (`research/data/evaluator_benchmark/README.md`) describes blinding and independence as protocol and lists 11 categories; the frozen case-level file has 10; the README also says labels were "pending". It is not used as evidence.
- Guardrail rules: "0 violations" is not used; "boundary-saturated attempted actions before clipping" is used.
- ICETC: the brief's IEEE template and 5/6-page facts were confirmed on the submission page; the home page mentions only a Word template.
- SAC 2027 AIED track: not verified (the AI-for-Education track page found is for SAC 2026).
- ICMETE 2026: no matching conference found. ICTCS 2026: found only as the Italian theoretical-CS conference, already held.

## 6. Claim-safety and terminology scans (manuscripts only)
Terms scanned: secure, security guarantee, fault-tolerant, universally contained, prompt-injection-proof, cannot affect scoring, validated, reliable, human-level, fair(ness), unbiased, generalis(e/able), state of the art, best, first, novel, novelty, formal shield, safety shield, shield, negative equivalence, expert panel, gold standard, blinded, independent raters, robust, superior, failure-aware, measurement validity, committee.
| Term | Hits | Disposition |
|---|---|---|
| secure | 1 (P1) | negation ("We do not claim that the pipeline is secure") |
| validated / validation | P1 "validated score" (a field name); P2 "not externally validated", "not a validation study", "validation Spearman" (training-record field), "held-out validation" (negated); P3 "not a fully validated model" (quoted from prior work) | all negations, field names or attributed |
| reliability / reliable | P1, P2 in reference titles and the term "reliability coefficient" | reference titles only in body; no unqualified claim |
| best | P1 "best-answer" (field), "is best read as"; P2 "best-correlating" | descriptive, not superlative claims |
| first | ordinal uses ("First, for SEC-01"; "first primary-run attempt"; "breadth-first") | no novelty use |
| independent | P1 "not an independent replication"; P2 "independent-case assumptions", "not independent"; P3 "not independent reproduction" | all negations or the mandated p-value wording; no "independent raters" remains |
| blinded | P2 Table I row and "Were the raters blinded ...? Not documented" | negation / documentation gap |
| fairness / generalise | P2 "no fairness claim", "can 8 questions generalise? No"; P3 "did not generalise to the grid" | negations |
| shield | P3 one use, describing safe-RL terminology and citing Alshiekh et al. | prior-work terminology; the study's layer is "application-level rule-based guardrail" |
| superiority / superior | P3 registered class names and "superiority not met" | required by the registered rule |
| interventions / violations | P3 "We call none of these counts 'interventions'"; "not called violations" | negations |
| fault-tolerant, universally contained, prompt-injection-proof, cannot affect scoring, state of the art, novel, human-level, unbiased, formal shield, safety shield, negative equivalence, expert panel, gold standard, independent raters, failure-aware, measurement validity, committee, robust | 0 | none |
Note: "expert" appears only as "expert policy" (literature) and the "nervous expert" persona; "safe/safety" only in negated safety-guarantee statements and reference titles.

## 7. Formatting-readiness audit (Phase 10)
| Item | Status |
|---|---|
| Source format | Markdown, IEEE-like section structure; **not yet ported** to any official template (ICETC IEEE/Word/LaTeX; HCII Springer LNCS; ATIS Springer CCIS) |
| Figures | none generated; planned figures listed per paper, each from stored data |
| Tables | in Markdown (4, 5 and 4 numbered tables); need conversion and column-width checks |
| References | 14, 15 and 14 entries in IEEE-like text form; must be exported from Zotero/verified sources for the final template; several are preprints and several were verified at abstract or metadata level only (see each `inventory.md`) |
| Abstract | 241, 221, 228 words; single paragraph; no citations |
| Keywords | six per paper |
| Length | body words (tables included) 4,046 / 4,513 / 4,047; likely 6–9 IEEE two-column pages before figures; ICETC charges beyond 6 pages; HCII/ATIS limits accommodate the drafts |
| Anonymity | author block withheld; ICETC double-blind status UNVERIFIED; HCII is single-blind |
| AI-assistance / ethics statements | not written; venue policies not verified; author decision |

## 8. Residual risk by paper
- **Paper 2 — highest.** Undocumented rater independence, blinding, consent and ethics; author-constructed benchmark; 8 clusters; cross-encoder provenance; full composite below its components; length confound. All are disclosed; none can be closed by wording. Do not submit to a venue that requires ethics or rater-consent documentation the record cannot supply.
- **Paper 3 — medium.** Simulation only; authored margin; single training candidate; evaluation-time Same share not stored; guardrail counts from five personas.
- **Paper 1 — medium.** One environment; same-agent design and repair; review report not in repository; ptrace and follow-up-channel limitations; length for a 6-page venue.

## 9. What this audit did not do
No LaTeX build or template check; no figures; no new literature search or re-verification of references beyond the earlier passes (venue pages were fetched in this pass); no independent human or tool review of the drafts; no reproduction of any experiment; no acceptance prediction.
