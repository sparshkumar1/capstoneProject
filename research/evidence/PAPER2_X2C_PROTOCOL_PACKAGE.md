# Paper 2 — X2-C Confirmatory Study: Protocol Package (PREPARATION ONLY)

Date: 2026-09-20. **Nothing here starts, simulates or collects data.** No human data was created, no rater/author was contacted, no consent/ethics/qualification/independence statement is made. This package is a draft for review; it is **not registered** (no hash, no tag) and supersedes nothing. It refines `research/audit/X2_PROTOCOL_DRAFT.md` §4 under the instructions of the 2026-09-20 block (threshold-free primary outcome; length baseline; strata). Where the draft and this package differ, the difference is listed in §11 for decision.

## 0. Status of existing evidence (preserved)
Old benchmark: N = 64 constructed answers to 8 questions (54 mean-of-three, 10 expert-adjudication — the label is an existing benchmark field; no rater qualifications are asserted); composite Spearman ρ = 0.3812, p = 0.0018863, case-bootstrap 95 % CI [0.1575, 0.5774] (two-level cluster [0.1529, 0.6490]); rater reliability ICC(2,1) 0.9528, ICC(2,k) 0.9838, Krippendorff α 0.9523; metamorphic 19/21 (90.5 %); adversarial 11/13 (84.6 %) vs author-set ceilings; 7-way ablation ρ: S1 .2070, S2 .3021, R .4832, S1+S2 .2894, S1+R .4884, S2+R .4171, full .3812 (the full composite is not best). Exploratory X2-B: length-only ρ 0.4897 [0.2186, 0.708] vs derived CrossEncoder 0.4825; BM25 0.3812; TF-IDF 0.245; reference-token overlap 0.4301. Central validity issue: **concise-correct and paraphrase answers are substantially under-scored.** The old benchmark is **exploratory/pilot**; its raters' provenance/ethics records are incomplete.

## 1. Question and estimands (threshold-free)
**Question.** How well does the frozen evaluator's continuous output agree with blinded human consensus on a question-disjoint, temporally separated, independently authored benchmark, and how does that agreement compare with simple baselines (especially length)?
**Primary outcome (no success threshold is invented).** Spearman ρ between composite score and human consensus with a two-level (question → answer) cluster-bootstrap 95 % interval, reported as an *estimate with its uncertainty*. No ρ threshold defines "success". Interpretation is descriptive: the interval is compared with the old-benchmark interval and with baselines' intervals.
**Co-primary comparisons (paired, same bootstrap draws):** composite − length-only; composite − R-only; composite − S1+R. **Secondary:** Kendall τ-b, Lin's CCC + Bland–Altman bias, within-question (demeaned) ρ, stratum-specific ρ, under-scoring rate of concise-correct and paraphrase strata (mean signed error vs human consensus), AUROC correct-vs-incorrect **only at a pre-specified, pre-freeze cut**, false-accept rate on adversarial strata. Rater reliability: ICC(2,1)/(2,k), Krippendorff α with CIs.
**Baselines (frozen before data):** answer word count; character count; BM25 and TF-IDF vs reference; reference-token overlap; R-only; S1+R. The evaluator is **not** modified if the length baseline is strong; that outcome is reported as a finding.

## 2. Benchmark construction rules
1. **Question-disjoint** from the 64-case benchmark, the N = 20 pilot and every set used for weights/θ/dampening (stored disjointness check against legacy lists).
2. **Temporally separated**: a stratum of questions and references authored after the CrossEncoder's commit date (2026-04-13), unpublished, not derived from the legacy bank; authoring dates logged. A second stratum sampled from the deployed bank (leakage status undetermined and labelled).
3. **Independently authored**: answers by people who have never seen evaluator output, or by a recorded fixed generator (model, prompt, seed, temperature), unfiltered; references authored **before** answers; author identities coded. Prefer naturally occurring/volunteer-style answers **where ethically and institutionally feasible** (§4); otherwise constructed answers are labelled as such.
4. **Evaluator-unaware, no score-based filtering**: the evaluator is not run on any candidate item before the item file is frozen; no item added, removed or reworded after any rater/evaluator output exists.
5. **Strata (controlled, balanced per question where feasible):** short-correct, long-correct, paraphrase-correct, short-wrong, long-wrong, adversarial/keyword-stuffed. Length is deliberately **crossed with correctness** so a length-only baseline cannot succeed by construction alone (the old benchmark lacks this guarantee — a suspected artifact, not established).
6. Ordering: freeze evaluator hashes → author references → author answers → freeze item file (hash) → blind rating → freeze gold (hash) → run evaluator **once** → registered analysis.
7. FAISS/S2: record whether the concept index contains the new questions (it should not for the temporally separated stratum).

## 3. Provenance ledger (schema; one JSON/CSV row per event; hashes at return)
`item_id, question_id, stratum, role(author|rater|adjudicator|generator), person_code (pseudonymous), qualification_statement_verbatim (as supplied; not verified), independence_declaration, tool_use_declaration (LLM/none/other), consent_record_id, instruction_version, sent_utc, returned_utc, time_spent_min, file_sha256_at_return, randomisation_seed, generator_config (model, prompt, seed, temperature) or null, notes`. Ledger rules: entries collected at the time, never back-filled; "not recorded" is a legal value; the words "independent", "expert", "approved", "consented" may appear in reports only where the corresponding record exists.

## 4. Institutional / ethics requirements (decisions belong to the user and the institution)
Human-subject determination (exemption/approval/not-human-subjects) and data-protection handling must be obtained or a documented decision to proceed recorded **before** authoring/rating; consent text for raters/authors; compensation/credit rules; conflict-of-interest disclosure (study team authored the evaluator and the old benchmark); rules for using volunteer-style natural answers (privacy, identifiability, consent to reuse). The existing enquiry draft is `research/audit/INSTITUTIONAL_ETHICS_ENQUIRY_DRAFT.md`. **INSTITUTIONAL DECISION REQUIRED — status unknown to this session.** No wording asserting approval may be used.

## 5. Rater instructions (content outline)
Frozen rubric and scale from the existing protocol (unchanged); raters blind to stratum/category/author/evaluator output; item order randomised per rater with logged seed; no discussion between raters; no LLM use unless the instruction version allows and it is declared in the ledger; record time spent; note items they could not judge; adjudication (spread > 0.20 → blind adjudication by a person who is not an author) as in the existing protocol. ≥ 3 raters, **fully crossed**.

## 6. Blind-rating procedure
Item file stripped of stratum/category/author; opaque item IDs; per-rater random permutation; rating sheet returns hashed on receipt; evaluator outputs hidden from raters and from the person assembling gold; gold frozen (hash) before the evaluator is run once; unblinding key held separately and used only in the registered analysis.

## 7. Precision simulation specification (NOT RUN)
Goal: choose the number of questions Q and answers per question K so that the expected two-level cluster-bootstrap 95 % CI half-width for the composite ρ is ≤ a **pre-registered precision target** (the draft suggests 0.12 — to be confirmed by the user, not a success threshold). Method: parametric simulation calibrated to the 64-case variance components (question random effect, residual, rater noise from ICC); scenarios ρ ∈ {0.2, 0.4, 0.6}; Q ∈ {16, 20, 24, 30, 40}, K ∈ {6, 8, 10}; B_sim = 2,000 datasets × B_boot = 2,000; report the half-width and coverage; fixed seeds; code and outputs hashed **before** any confirmatory data exist. The result informs the sample size and is not used to change the primary outcome.

## 8. Analysis script specification (NOT WRITTEN)
Inputs: frozen item file, frozen gold, evaluator outputs (component and composite), baseline outputs, ledger. Steps: key-set assertions (items × raters complete; no duplicates; strata balance); consensus computation; ρ and paired differences with a two-level cluster bootstrap (B ≥ 10,000; seed logged; fresh generator per analysis; draw order stated in the protocol text *before* the run — lesson from X3-A/O7); within-question ρ; under-scoring by stratum; reliability; every output through `research/tools/run_manifest_v2.py` (declared inputs/models with full hashes, protocol tag, gate). The script is reviewed independently before tagging.

## 9. Claim map (allowed only after the corresponding evidence exists)
| Possible claim | Evidence needed | If the evidence is unfavourable |
|---|---|---|
| Agreement between the evaluator and blinded raters on question-disjoint items is *estimated* at ρ with interval I | X2-C primary | Report the interval; describe the old 0.3812 as an exploratory estimate |
| The composite is/ isn't distinguishable from length-only | paired difference CI | Report; no architecture-improvement claim |
| Concise-correct/paraphrase answers are (not) under-scored | stratum signed error | Report as validity limitation |
| Composite lowers false-accepts on adversarial strata relative to R-only | adversarial-stratum false-accept rates | Describe the composite as a design choice with a measured accuracy cost |
Not allowed at any outcome: "validated", "state-of-the-art", "human-level", "expert-validated", fairness/accent/subgroup claims, real-learner claims (unless the data are real learners'), deployment claims.

## 10. Data retention and hash procedure
Store item file, references, answers, authorship log, generator config, rater sheets (as returned), coded ledger, frozen gold, evaluator hash set, baseline outputs, analysis script and config, results, run manifest (v2) and environment lock; SHA-256 of each at creation and at return; write-once directories; retention period and access per the institutional determination; no personal identifiers in the repository; no raw rater identities outside the sealed key.

## 11. Differences from `X2_PROTOCOL_DRAFT.md` §4 (for user decision; the draft is not edited)
| Draft | This package |
|---|---|
| H1 primary: CI lower bound > ρ_min (suggested 0.30) | No ρ threshold; primary outcome is the estimate with its interval, plus paired comparisons. Requires the user to accept removing H1's threshold |
| H2/H3 as hypotheses | Retained as reported comparisons; H3 stays conditional on the adversarial stratum |
| Constructed-contrast subset + natural stratum | Six controlled strata with length crossed with correctness; natural answers preferred where ethics permit |
| Baselines "lexical baselines" secondary | Length and lexical baselines are co-primary paired comparisons |

## 12. Not done in this block
No protocol tag; no simulation run; no rater/author recruitment; no contact with the institution; no analysis script; no consent forms. Next exact action: the user decides the institutional pathway and whether to adopt the threshold-free primary outcome; then the precision simulation is run (with a hashed script), the protocol is registered, and only then can authoring begin.
