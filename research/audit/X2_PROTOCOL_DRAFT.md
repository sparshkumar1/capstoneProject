# X2 Protocol Draft — Paper 2 evaluator validity (2026-09-19)

**Status: DRAFT. Not registered, not hashed, not tagged, not executed.** Fields marked **[FIX IN PHASE 2]** are completed and reviewed before hashing/tagging (`PREREGISTRATION_SPEC.md`). No X2 evaluation, item authoring, rating or contact with raters may start before the relevant protocol is tagged (and, for human data, before the ethics gate in `HUMAN_BENCHMARK_PROVENANCE_PLAN.md`).

Locked decisions (`PHASE0_DECISION_LOCK.md`): current CrossEncoder frozen and retained; wording "partially fine-tuned derivative with incomplete provenance"; X2-A and X2-B approved; **primary upstream comparison = mapping-independent R-only metrics; no composite mapping invented or fitted after seeing results**; **one** new confirmatory human benchmark (X2-C) that becomes the confirmatory set; the old 64-case benchmark becomes exploratory/initial evidence; **no second human round**.

## 0. Central question
How well does the deterministic, LLM-free hybrid evaluator (S1 SBERT + S2 FAISS + R CrossEncoder, safety-hardened) agree with blinded human ratings of technical-interview answers, does that agreement replicate on questions the evaluator and its tuning never saw, and how much depends on the undocumented fine-tune of R?

## 1. Frozen evaluator (for all X2 experiments)
Evaluator code commit, weights (`0.15/0.35/0.50`), θ = 0.30, dampening (×0.6 when R ≤ 0.30), R mapping, bonus/penalty/cap rules, SBERT weights, FAISS index and CrossEncoder (`6a241a55…4450`) are frozen by hash **before** any new item is authored or rated; none may change afterwards. No tuning on X2-C data (and none on the 64 cases). The hash set goes into the protocol and each run manifest.

## 2. X2-A — Stored-data re-analysis (analysis, no new data)
**Question.** How sensitive is the frozen ρ to question clustering, rater choice, category composition and the pilot overlap?
**Inputs (frozen, read-only).** `research/results/paper2/paper2_case_level_results.csv`, `final_human_gold.csv` (SHA-256 `363dbe6d…6ce2`), the three hash-pinned rater files.
**Analyses (fixed list).** (1) Two-level cluster bootstrap for composite and component ρ (resample the 8 questions, then answers within question; B ≥ 10 000; RNG seed fixed; percentile and BCa); (2) leave-one-question-out ρ; (3) per-question and per-category ρ with sample sizes (2–8 per category; descriptive); (4) within-question (demeaned) ρ; (5) rater leave-one-out sensitivity of the gold and ρ; (6) **adversarial false-accept analysis** (below); (7) overlap vs non-overlap questions with the pilot (qid 1, 3, 10, 41 vs 7, 15, 22, 50), reported as **exploratory**; (8) signed bias (model − human) by category and answer length; (9) Kendall τ-b, Lin's CCC, Bland–Altman.
**Adversarial false-accept endpoint (fixed before running).** For categories {keyword_stuffed, misconception, contradictory, incorrect, verbose_wrong}, the fraction of items whose evaluator score ≥ an acceptance threshold τ_accept, for composite vs R-only vs S1 vs S1+R. **τ_accept is taken from the evaluator's documented grade boundary [FIX IN PHASE 2: verify against code]; it may not be chosen after seeing scores.** Purpose: test the only defensible reason to ship the composite (it correlates below R-only).
**Outputs.** new script + new result files (never overwriting frozen ones), with manifest; results registered as `EXPLORATORY` except the cluster bootstrap. **Interpretation.** if the composite does not beat R-only on the adversarial endpoint, the paper says so and presents R-only as the accuracy-optimal component and the composite as a design choice with a measured cost.

## 3. X2-B — Baselines and upstream sensitivity (evaluation-only)
**Question.** (a) Do the evaluator/R beat trivial baselines? (b) How much does the undocumented fine-tune matter?
**Hypotheses.** (a) composite and R exceed lexical baselines on ρ and AUROC; (b) none directional — bounded-effect estimate.
**Scorers.** derived R (`6a241a55…`), **upstream R** (`cross-encoder/ms-marco-MiniLM-L-6-v2`, weights hash `821d1aa6…` to be re-verified at run time), TF-IDF cosine, BM25, token-overlap, length-only, and the existing S1/S2 components.
**Primary upstream comparison (locked): mapping-independent R-only metrics** — Spearman ρ, Kendall τ-b, AUROC (correct vs incorrect, threshold defined in the protocol before running) computed on the raw model outputs, so they are invariant to any monotone rescaling. **No composite is computed for the upstream arm** unless the frozen protocol contains a fully specified, label-free mapping approved by the user before any upstream output is seen; **no mapping may be invented or fitted after seeing results**, and none may use human labels. MAE-type metrics for upstream are not reported.
**Data.** the old 64 cases (exploratory) now; the X2-C benchmark (confirmatory) after its gold is frozen. The upstream arm on X2-C is run **once**, after the freeze.
**Unit.** question (cluster). **Tests/CIs.** two-level cluster bootstrap (B ≥ 10 000), paired differences (derived − upstream; scorer − baseline); permutation-null reference. **Effect sizes.** Δρ, ΔAUROC.
**Stopping.** single run per scorer per dataset; no repeated or adjusted runs.
**Interpretation.** *Small derived–upstream gap:* the fine-tune is immaterial; the public model can serve as primary/reference and provenance is a lesser concern. *Large gap on both strata:* the fine-tune matters; provenance and leakage caveat central. *Large gap only on the bank-sampled stratum* (X2-C): leakage suspicion **documented as a suspicion, not proven**.
**Contamination.** metrics and thresholds hashed before the first upstream output; label-free only; environment locked (`ENVIRONMENT_LOCK_SPEC.md`). **Artifacts.** model hashes, per-item scores, configuration, manifest, results CSV.

## 4. X2-C — Confirmatory benchmark and human rating round (the single new human round)
**Gate.** No item authoring/rating starts until: the institutional/venue enquiry has produced the required determination or a documented decision to proceed (`INSTITUTIONAL_ETHICS_ENQUIRY_DRAFT.md`), consent/ledger materials are approved, and this protocol is tagged. **INSTITUTIONAL DECISION REQUIRED** where noted there.

**Question.** Does the evaluator's agreement with blinded human raters replicate on a question-disjoint, temporally disjoint, independently authored benchmark?

**Hypotheses (to be fixed with the user before tagging).**
- H1 (primary): composite Spearman ρ on the confirmatory set has a two-level cluster-bootstrap 95 % CI whose lower bound exceeds **ρ_min [FIX IN PHASE 2; suggested 0.30]**.
- H2: R-only ρ ≥ composite ρ (expected; reported either way).
- H3: composite false-accept rate on adversarial categories < R-only's (the safety-hardening claim).
- Secondary/exploratory: within-question ρ; stratum contrast (temporally disjoint vs bank-sampled); constructed-contrast vs natural strata; upstream arm (X2-B); lexical baselines.

**Design (locked requirements).**
| Requirement | Specification |
|---|---|
| **Question-disjoint** | No question from the old 64-case benchmark, the N=20 pilot, or any set used for tuning θ/dampening/weights. A disjointness check against the legacy bank and pilot lists is stored |
| **Temporally disjoint stratum** | Roughly half the questions **and all their references** newly authored after the CrossEncoder's commit date (2026-04-13), not published, not derived from the legacy bank; authoring dates recorded |
| **Bank-sampled stratum** | Roughly half the questions drawn from the deployed question bank, disjoint from the pilot/old benchmark; leakage status undetermined and labelled |
| **Independently authored** | Answers written by someone who has never seen evaluator output on any item, or generated by a recorded fixed generator (model, prompt, seed, temperature) and **not filtered**; a constructed-contrast subset (correct-concise/verbose, partial, incorrect, misconception, keyword-stuffed, contradictory, paraphrase) is kept for adversarial validity and reported separately; a natural/varied stratum reduces reliance on category construction. Author identities recorded (coded). References authored **before** answers |
| **No evaluator-aware filtering** | The evaluator is not run on any candidate item before the item list is frozen; no item is added, removed or reworded after any rater or evaluator output exists. Enforced by the ordering below and by the ledger |
| **Ordering (score-after-freeze)** | (1) freeze evaluator hashes → (2) author references then answers (no evaluator access) → (3) freeze item file (hash) → (4) blind rating → (5) freeze gold (hash) → (6) run the evaluator **once** → (7) analysis exactly as registered |
| **Raters** | ≥ 3 raters, **fully crossed** (every rater rates every item); blind to category, stratum, authorship and evaluator output; randomised item order per rater (seeds logged); frozen rubric and scale of the existing protocol; adjudication rule as in the existing protocol (spread > 0.20 → blind adjudication), adjudicator distinct from authors; rater/adjudicator roles recorded (coded) |
| **Documentation** | Ledger per `HUMAN_BENCHMARK_PROVENANCE_PLAN.md`: consent, roles, instructions version, send/return timestamps, time spent, tool-use and independence declarations collected **at the time**; file hashes at return |
| **S2/FAISS condition** | State explicitly whether the FAISS concept index contains the new questions (it should not for the temporally disjoint stratum); the tested condition is "unseen question" for those items |
| **Sample size** | Set by a precision simulation **before data collection [FIX IN PHASE 2]**, using the 64-case variance components: choose the number of questions so that the cluster-bootstrap CI half-width for ρ ≤ 0.12 at the observed effect size (working range 20–30 questions × 8 answers; an estimate, not a decision). Answers per question fixed; ≥ 3 raters |
| **Pilot of the instrument** | A 2–3-question instrument pilot on non-confirmatory items is allowed to test the rating sheet; excluded from analysis; must not use confirmatory items |

**Dependent variables.** human consensus score (mean of raters; adjudicated where spread > 0.20); evaluator composite and component scores.
**Statistics.** Spearman ρ (primary), Kendall τ-b, AUROC (correct vs incorrect; threshold pre-specified), Lin's CCC and Bland–Altman bias, within-question ρ; inference by two-level cluster bootstrap (B ≥ 10 000, RNG seed logged); paired ρ differences (composite vs R-only vs S1+R) by the same bootstrap; ICC(2,1)/(2,k) and Krippendorff α with CIs for the raters; false-accept rates with cluster-bootstrap CIs.
**Stopping.** fixed item list; no optional stopping; no new items; if a rater cannot complete, the round is reported incomplete — it is **not** replaced by a second round (locked decision) unless the user approves a documented protocol amendment.
**Interpretation.**
- *Positive:* H1 met → "moderate agreement replicated on question-disjoint, temporally disjoint items", still bounded to constructed/simulated answers and the tested domains.
- *Weak/null:* lower bound ≤ ρ_min → the 64-case result is reported as an optimistic exploratory estimate; the claim narrows to agreement on constructed contrast sets.
- *H2/H3 outcomes* reported whichever way; if H3 fails, the composite is described as a design choice with a measured accuracy cost.
**Contamination/leakage controls.** as in the design table; plus disclosure of the authors' involvement in both evaluator and benchmark construction; no tuning on X2-C.
**Artifacts.** item file + hash; reference/answer authorship log; generator config (if used); rater instrument version; coded ledger; frozen gold hash; evaluator hash set; analysis script/config; results; manifest; environment lock.

## 5. Reporting rules for Paper 2 (fixed now)
Describe R as a partially fine-tuned derivative with incomplete provenance (unless records are recovered); the 64-case benchmark is exploratory/initial; the confirmatory set is X2-C; state that the composite correlates below R-only on the 64 cases; report the under-scoring of concise-correct answers as a principal limitation; never write "independent experts", "committee", "approved", "consented" without records.

## 6. Open items **[FIX IN PHASE 2]**
ρ_min and the AUROC threshold; τ_accept; precision-simulation code and result; item counts per stratum; author and rater recruitment (user); generator specification if used; FAISS index handling; instrument pilot; analysis script skeleton hash; ethics-gate outcome.
