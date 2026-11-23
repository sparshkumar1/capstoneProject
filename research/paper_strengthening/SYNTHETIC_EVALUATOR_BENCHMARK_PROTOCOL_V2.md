# Synthetic Category-Discrimination Benchmark for the Hybrid Evaluator — V2

**Status: complete protocol, NOT executed, NOT registered.** Supersedes `SYNTHETIC_EVALUATOR_BENCHMARK_PROTOCOL.md` (V1, kept unmodified as a historical draft). No model has been called; the two computations below (§1, §4.4) are re-analyses of already-existing files (`data/rubrics/rubrics_final_clean.json`, `paper2_case_level_results.csv`) — no new model score, no new data collection. This document is not to be registered or executed until reviewed and approved.

## 0. What changed from V1, and why

| V1 | Problem raised | V2 |
|---|---|---|
| 30 questions, arbitrary cap | Sample size not justified; feasibility of using more not checked | Full eligible bank used: **122 of 125** questions, after a disclosed, stricter eligibility audit (§1) |
| Split by question (10 dev / 20 confirmatory) | Doesn't test generalization to unseen topics; 20 questions may be underpowered | Split by **topic** (§2); confirmatory precision explicitly projected before committing (§4.4) |
| One template per category | Categories trivially separable by template artifacts; no minimal pairs; no construction-validity check | Multiple variants per category, an explicit minimal-pair rule (C1↔C4), automated construction-validity checks, and negative controls (§3) |
| 7 hypotheses, all treated as one family, "no significant difference" used as evidence of paraphrase-equivalence | Paraphrase claim used the wrong test (absence of evidence ≠ evidence of absence); 7-way multiplicity not addressed | 3 pre-specified **primary** hypotheses with Holm correction; paraphrase claim now a properly powered **TOST equivalence test** with a disclosed margin; the keyword-stuffing claim now an explicit two-part pre-registered test (§4) |
| No component-mechanism ablations beyond S1/S2/R combinations | Dampening, mistake-penalty, and mandatory-cap contributions never isolated | Three additional, clearly distinct ablations added (§4.5) |
| No computational-cost check | Scale decision made without knowing if it was even feasible | Estimated at **under 15 minutes of CPU-bound scoring, one-time**, using this project's own recorded evaluator latency (§2.3) — cost does not constrain scope |

## 1. Eligibility audit (executed in this pass — data inspection only, no model call)

**Criterion (stricter than V1's loose pass/fail):** a question is eligible only if it supports every category **without an artificial or ambiguous construction**:
- `logic_markers.mandatory` has ≥2 entries (so a "partial" answer can meaningfully omit at least one while retaining at least one);
- `logic_markers.concept_groups` has ≥2 entries (enough distinct concepts for a keyword-stuffed list to read as a list, not a single term repeated);
- `semantic_targets` has ≥2 entries (enough content for a paraphrase to differ meaningfully from a bare restatement of the mandatory concepts);
- at least one `common_mistakes` entry has ≥4 words (phraseable as a coherent, if wrong, claim — not a one- or two-word fragment);
- every `mandatory` entry has ≤10 words (short enough to flatten into a keyword-stuffed list without the "list" itself reading as connected reasoning).

**Result:** `research/paper_strengthening/scripts/benchmark_v2_planning_analyses.py` (script; output `results/benchmark_v2_planning.json`) — **122 of 125 questions pass**. The 3 excluded (qid 26, 39 — both DynamicProgramming; qid 110 — C_Programming) fail only the last criterion: their mandatory concepts are written as long clauses, not short terms, so a keyword-stuffed construction from them would already read as a coherent (if compressed) explanation, defeating the purpose of that category. These 3 are excluded from the benchmark entirely, not force-fit.

**Coverage of the 122 eligible questions:** all 5 `type` values represented (theory 50, logic_approach 40, evaluate 15, general_tech 10, code 7 [10 minus the 3 excluded, all of which were code/DP-type]); 37 distinct topics, unevenly sized (`C_Programming` 26, `DSA_Theory` 18, `Arrays` 10, down to several topics with 1 question each).

## 2. Scale and split

### 2.1 Use the full eligible bank
All 122 eligible questions are used — not an arbitrary subset. There is no scientific reason to discard usable, already-vetted content once eligibility is confirmed, and §2.3 confirms this is computationally cheap.

### 2.2 Topic-based split (generalization test)
- **Development topics:** a fixed, disclosed selection of topics — one topic per `type` value where possible, chosen to also cover a range of topic sizes (large: `C_Programming`; small: e.g. a 1-question topic), for a total of **5–7 development topics**, comprising roughly 15–20 questions. Used only to pilot and correct the category-construction templates (§3) before anything is frozen.
- **Confirmatory topics:** every remaining eligible topic (roughly 30–32 topics, ~102–107 questions), **never touched during template development**, scored exactly once.
- **Exact topic assignment:** drawn by a fixed, disclosed random seed at registration time, stratified to keep development topics spanning all 5 `type` values; the seed and resulting lists are fixed *before* any answer text is written, and reported in the registered protocol, not chosen after seeing which topics "work well."
- **Why topic, not just question:** with `C_Programming` alone contributing 26 of 125 questions, splitting only by question would let templates be implicitly tuned on content very similar to much of the confirmatory set. A topic split tests whether the construction rules — and the evaluator's behavior — generalize to topics never seen during development.

### 2.3 Computational cost (checked before finalizing scope)
Using this project's own recorded evaluator latency (`paper1_latency_results.csv`, `FROZEN-VERIFIED`: median 404.6 ms per `evaluate()` call, steady state; P99 26 369.4 ms reflects rare cold-start-scale outliers, not the typical call), scoring the full richer item set (§3.5: ~10 items per question × 122 questions ≈ **1,220 items**) is projected at roughly 1,220 × 0.4 s ≈ **8 minutes of CPU-bound scoring**, plus a small, bounded allowance for cold-start effects — well under 15 minutes total, one machine, no GPU required, no retraining. **Cost does not justify limiting scope to a subset of the eligible bank.**

## 3. Category construction — rigor upgrades

### 3.1 Explicit construction-validity vs. semantic-quality distinction
Every category label is a **construction property** (was this text built by rule R from rubric field F), not a certified measure of true answer quality or human-perceived correctness. The manuscript and any resulting claims must say so explicitly: this benchmark tests whether the evaluator's score tracks a *known construction property*, not whether it tracks *ground-truth answer quality* in the way the (separate, human-rated) benchmark attempts to.

### 3.2 Minimal-pair rule (C1 ↔ C4)
For a given question, the C4 (keyword-stuffed) item must use **the same set of key terms** as that question's C1 (correct) item — verified by an automated keyword-overlap check (e.g., ≥90% of C1's mandatory/concept terms appear verbatim or as a near-synonym in C4) — and must differ from C1 **only** in the absence of connecting reasoning. This is the actual minimal pair the "does dampening work" question needs: same vocabulary, different structure.

### 3.3 Multiple variants per category (no single template)
- **C1 (correct):** 1 canonical construction from `semantic_targets` + `mandatory`.
- **C2 (paraphrase):** **2** variants per question, built by different rewording strategies (clause reordering; synonym/structure substitution), not one fixed transformation.
- **C3 (partial):** **2** completeness levels per question — "high partial" (omits exactly one mandatory concept, retains the rest) and "low partial" (retains only a general topic mention, omits all mandatory concepts) — rather than one fixed omission level.
- **C4 (keyword-stuffed):** 1 item, locked to the C1 minimal-pair rule (§3.2).
- **C5 (misconception):** up to **2** variants where the question's rubric lists ≥2 usable `common_mistakes` entries (most do — the mistake-count distribution found in this pass ranges 3–8 per question), each built from a distinct listed mistake; 1 variant where only one is usable.
- **C6 (contradictory):** 1 item — C1's core claim followed by its explicit negation (a disclosed, fixed negation-marker pattern, e.g. "...but actually the opposite is true: [negated claim]").
- **C7 (irrelevant):** 1 fixed, topic-independent template (unchanged from V1 — deliberately generic, since varying it risks accidentally encoding topic-relevant content).

**Approximate item count:** 1(C1) + 2(C2) + 2(C3) + 1(C4) + ~1.8(C5, averaged) + 1(C6) + 1(C7) ≈ **~10 items per question** (used in the §2.3 cost estimate).

### 3.4 Automated construction-validity checks (run before scoring, on text only — no model call)
- **C4 check:** the item contains **zero** connectives from a fixed, disclosed banned list (e.g. "because," "since," "therefore," "which means," "so that," "as a result," "due to") — a keyword-stuffed item that accidentally contains a causal connective is rejected and reconstructed.
- **C1/C2 check:** the item contains **at least one** connective from that same list (a "correct" answer with zero connectives risks reading like C4 and is rejected and reconstructed).
- **C5 check:** the item's core claim has high textual overlap (a disclosed similarity threshold) with one specific `common_mistakes` entry, so the mapping from category to source mistake is auditable, not asserted.
- **C6 check:** the item contains both an affirmative clause and the fixed negation-marker pattern.
- These are lint-style, deterministic, disclosed text checks — not a model call, not "new experimental data" in the `CLAUDE.md` sense, and can be run and fixed iteratively on the development set with no approval needed.

### 3.5 Negative controls (to prevent trivial separability)
- **Length control:** C1 and C4 (the minimal pair) are constructed to have comparable word counts (within a disclosed tolerance, e.g. ±20%), so a length-sensitive artifact cannot masquerade as a reasoning-sensitivity finding.
- **Scrambled-order control (exploratory, development set only):** a word-order-shuffled version of a C1 item, to informally check the evaluator isn't purely a bag-of-words matcher — reported descriptively, not part of the confirmatory hypothesis family, since this project's own frozen metamorphic-testing results (19/21 relations passed) already partially cover this.
- **Repeated-terminology control:** a variant of C4 that repeats the same one or two mandatory terms many times rather than listing distinct concepts, to check the evaluator penalizes empty repetition at least as much as varied-but-unconnected terminology — exploratory, not part of the primary confirmatory family, flagged as a candidate secondary hypothesis if development-set piloting suggests it's informative.

## 4. Statistical design upgrades

### 4.1 Primary vs. secondary hypotheses
**Primary family (3, Holm-corrected):**
- **P1 (dampening mechanism):** two-part, pre-specified (see §4.3).
- **P2 (paraphrase preservation):** TOST equivalence (see §4.2).
- **P3 (overall category ordering):** a single omnibus test that the mean `final_score` ordering C1≈C2 > C3 > {C4, C5, C6} > C7 holds at the topic-clustered level (a single pre-registered ranking test, e.g. a clustered Jonckheere–Terpstra-style ordered-alternatives test, or — if that is not readily available in the analysis environment — a pre-specified set of adjacent-category paired comparisons treated as one family with its own internal correction, decided and documented at registration, not after seeing results).

**Secondary/exploratory (reported, not used for the paper's central claim, no correction against the primary family):** individual category-vs-category comparisons beyond the three above; the repeated-terminology control; the scrambled-order control; per-topic heterogeneity description.

### 4.2 Paraphrase claim: TOST equivalence, not "no significant difference"
Reframed from V1's non-significance-based claim. **Pre-specified equivalence margin: Δ = 0.10** on the `final_score` scale (0–1). **Justification for this margin (disclosed, revisable):** the existing human-rated benchmark's own adjudication trigger treats a rater-pair spread of >0.20 as a meaningful disagreement requiring a third opinion; Δ = 0.10 is half that threshold, i.e., a difference smaller than what this project's own human raters treat as meaningful is treated here as practically equivalent. Two one-sided tests (TOST), topic-clustered, at α = 0.05 each: conclude equivalence only if both one-sided tests reject (i.e., the paired mean difference's 90% CI falls entirely within [−0.10, +0.10]).

### 4.3 Keyword-stuffing claim: an explicit two-part pre-registered test
- **Part A (concept coverage is not fooled into looking low):** `S2(C4)` is non-inferior to `S2(C1)` — TOST-style, with a margin of Δ_S2 = 0.10 (same justification as §4.2, applied to the S2 sub-score) — confirming C4 items genuinely read as "concept-rich" to the coverage component, which is the premise the dampening mechanism needs to be tested against.
- **Part B (the full evaluator appropriately reduces the score anyway):** `final_score(C4)` is lower than `final_score(C1)` by **more than** Δ = 0.10 (a one-sided superiority test against that same margin, topic-clustered, reported with a paired effect size and CI — not inferred from overlapping CIs).
- **Both parts must hold** for the dampening mechanism's design rationale to be considered supported; either part failing is reported as such, not reframed.

### 4.4 Precision projection (executed in this pass — re-analysis of existing frozen data only)
Using the existing 8-question, 64-item paired absolute-error data (full composite vs. R-only, already computed in `EXISTING_EVIDENCE_ANALYSIS.md`), a bootstrap projection of how the 95% CI on the paired mean difference would narrow at larger K (script: `benchmark_v2_planning_analyses.py`):

| K (independent clusters) | Projected 95% CI half-width | Projected CI |
|---|---|---|
| 8 (V1's implicit scale, human benchmark) | 0.032 | [−0.015, 0.050] |
| 16 | 0.022 | [−0.007, 0.038] |
| 32 | 0.017 | [0.000, 0.033] |
| 64 | 0.012 | [0.004, 0.028] |
| 107 (this design's confirmatory scale) | 0.009 | [0.007, 0.025] |

**This is a projection under a disclosed assumption — that new questions have a similar effect size and variance structure to the existing 8 — not a guarantee.** It is presented only to justify that 20 questions (V1's confirmatory scale) was likely underpowered to resolve a small effect, and that the ~107-question scale in this design gives the confirmatory run a realistic chance of a conclusive answer either way, not to predict what that answer will be.

### 4.5 Additional, clearly separated evaluator-mechanism ablations
Each answers a distinct question, run on the same confirmatory item set, reported separately (secondary family, not part of the 3 primary hypotheses):
- **Dampening ablation:** compare `final_score` computed with vs. without Eq. 3's dampening step (recomputable from already-scored S1/S2/R once the confirmatory run exists — a re-analysis of that run's own output, not a second model-scoring run).
- **Mistake-penalty ablation:** compare `final_score` with vs. without the mistake-penalty term, isolating its specific contribution on the C5/C6 items it is designed to catch.
- **Mandatory-cap ablation:** compare `final_score` with vs. without the hard 0.60 cap (Eq. 9), isolating its effect on the C3 ("high partial," which by construction omits one mandatory concept) items specifically.
- These three require no additional model calls beyond the single confirmatory scoring run — they are recomputations from already-obtained S1/S2/R component values under the already-documented formulas, using only arithmetic already specified in the manuscript.

### 4.6 Reporting standard (binding on the eventual write-up)
Both topic-clustered and question-level statistics are reported side by side, as in `EXISTING_EVIDENCE_ANALYSIS.md`. No claim of equivalence is made from a non-significant difference or from overlapping CIs alone — only from a pre-specified TOST procedure with a disclosed margin. No claim of superiority is made without a paired, clustered comparison and an effect size, not a bare point-estimate comparison.

## 5. What requires approval, and what does not (unchanged in principle from V1, restated for V2's scale)

| Step | Approval needed? |
|---|---|
| This eligibility audit and the precision projection (§1, §4.4) | Already done in this pass — re-analysis of existing files only |
| Freezing the topic sample, the dev/confirmatory split, category templates, and the automated construction-validity checks | No — text/document design, touches no model |
| Writing and validity-checking the ~1,220 answer texts | No — text authoring and deterministic linting, touches no model |
| Running the confirmatory item set through the live SBERT / FAISS / CrossEncoder pipeline | **Yes — full approval required**, per `CLAUDE.md`. Estimated cost: under 15 minutes, one machine, no retraining, no GPU |
| The dampening/mistake-penalty/mandatory-cap ablations (§4.5) | Covered by the same approval as the scoring run — recomputation from its own output, not a second scoring pass |

## 6. Conditional follow-up (not specified further here)

Per the governing instruction: if this benchmark's confirmatory results indicate the hybrid evaluator (or one of its specific mechanisms) is poorly designed relative to a simpler alternative, any proposed replacement or reweighting is a **separate, subsequent experiment** — it would need its own registration, its own held-out data (not the same confirmatory set used to discover the problem, to avoid tuning against the test set this protocol just used), and the same explicit-approval gate as every other scoring-affecting change in this project. Nothing about that follow-up is designed here.

## 7. Honest scope statement

This design, even at full scale, establishes only whether the evaluator's score tracks *known, rule-constructed answer properties* on *synthetic, non-human-subject* text — not real candidate assessment validity, not learning outcomes, and not a claim about the evaluator's behavior on organically-written human answers beyond what the separate, smaller human-rated benchmark already (exploratorily) shows. Both must be cited together, never one in place of the other.
