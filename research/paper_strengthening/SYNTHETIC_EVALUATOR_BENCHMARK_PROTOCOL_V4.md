# Synthetic Category-Discrimination Benchmark for the Hybrid Evaluator — V4

**Status: complete protocol, NOT executed, NOT registered.** V1–V3 are preserved unmodified as the historical record of this review process. This pass found one genuinely serious problem in V3 (C5's circularity, §1) that required a structural redesign, not a patch, plus a real statistical imprecision (the non-inferiority direction, §2) that needed to be stated correctly rather than hand-waved. My own final verdict is at the end (§9) — this document does not assume its own approval.

## 1. Misconception leakage in C5 — the most serious fix in this pass

**The problem, stated plainly:** V3 built C5 by textually restating one of the rubric's own `common_mistakes` entries. But the evaluator's own mistake-penalty term (`P_mistake`, Eq. 5) is computed by matching candidate sentences against embedding vectors built from that *same* `common_mistakes` field. V3's C5 was therefore not testing whether the evaluator can recognize a misconception — it was testing whether a lookup mechanism fires on a near-verbatim copy of its own lookup key. That is close to circular, and it is a more serious version of the C1-verbatim problem I already partly fixed for the paraphrase test.

**Redesign: split C5 into two explicit, separately-reported sub-tests, not variants of one category.**
- **C5a — lexically-matched misconception** (a close paraphrase of the exact `common_mistakes` text). This is now explicitly a **manipulation check**, not a scientific claim: it confirms the mistake-penalty mechanism fires on the input it was literally built to catch. A failure here would indicate a construction or implementation problem, not a finding about general misconception-detection.
- **C5b — independently-worded misconception** (new). Conveys the *same underlying technical error* as one of the rubric's listed mistakes, but is authored with deliberately low lexical overlap to that mistake's own text. This is the genuinely informative test: can the CrossEncoder (or S1) recognize the answer is wrong via semantic/entailment signal, *without* the literal mistake-penalty lookup being able to fire on it?

**Lexical controls (both required, both automated, both disclosed before any scoring):**
1. **Low overlap with the source mistake:** C5b's word-overlap (Jaccard, content words only, stopwords removed) with its source `common_mistakes` entry must be **below 0.30** — verified by a deterministic script, not by the evaluator.
2. **Comparable topical relevance to C1:** C5b must still overlap with C1's core vocabulary at a level *comparable* to C5a's overlap with C1 (within a disclosed tolerance, e.g. ±15 percentage points) — this prevents "independently worded" from silently becoming "so different it's really testing topic drift, not misconception recognition." Both checks are on raw text, calling no model.

**What this buys, and what it costs:** C5a and C5b are reported and analyzed **separately**, never averaged — averaging would erase exactly the distinction this fix exists to draw. This roughly doubles C5's item count per question (2 items instead of up to 2 pooled variants), which is accounted for in the exact item counts in §6.

## 2. Statistical correctness — estimands, directions, rejection criteria, multiplicity, stated precisely

V3's non-inferiority direction was described loosely ("the one-sided CI upper bound... stays inside +0.10 appropriately signed") — imprecise enough that a reviewer would rightly ask what, exactly, is being tested. Restated exactly:

### 2.1 P1 Part A — non-inferiority of S2 under keyword-stuffing (corrected)
- **Estimand:** the population mean, over confirmatory topics, of the per-question paired difference `d = S2(C4) − S2(C1)` (negative values mean C4's coverage score is lower than C1's).
- **Null hypothesis (the "bad" outcome we must rule out):** H0: mean(d) ≤ −Δ_S2 (C4's coverage is meaningfully *lower* than C1's — coverage was fooled *downward* rather than staying "fooled high").
- **Alternative:** H1: mean(d) > −Δ_S2 (non-inferior — coverage remains high on the keyword-stuffed item, which is the premise the dampening mechanism needs).
- **Rejection criterion:** compute the topic-clustered bootstrap distribution of mean(d) (§8); reject H0 (conclude non-inferiority) if the **5th percentile** of that distribution exceeds −Δ_S2. This is a one-sided 95% test at α=0.05.
- **Margin Δ_S2 = 0.10**, with an explicitly disclosed limitation: this margin was validated (§4) against `final_score` movement under paraphrase, not against S2 specifically — applying it to S2 is a reasonable but **independently unverified extrapolation**, stated as such, not presented as equally well-supported.

### 2.2 P1 Part B — reframed from a threshold test to an estimation claim (see §3 for why)
- **Estimand:** mean, over confirmatory topics, of `e = final_score(C1) − final_score(C4)`.
- **Reported as a confidence interval, not a threshold pass/fail.** A one-sided significance check (H0: mean(e) ≤ 0 vs. H1: mean(e) > 0; reject H0 if the 5th percentile of the bootstrap distribution of mean(e) exceeds 0) establishes only that a *nonzero, positive* gap exists — it does not, by itself, establish the gap is *large enough to matter*. See §3 for the full reasoning and how magnitude is reported.

### 2.3 P2 — paraphrase TOST, stated as two one-sided tests
- **Estimand:** mean, over confirmatory topics, of `f = final_score(C1) − final_score(C2)`.
- **Two one-sided null hypotheses:** H0_upper: mean(f) ≥ Δ (C1 scores meaningfully higher than C2); H0_lower: mean(f) ≤ −Δ (C2 scores meaningfully higher than C1).
- **Rejection criteria:** reject H0_upper if the 95th percentile of the bootstrap distribution of mean(f) is < Δ; reject H0_lower if the 5th percentile is > −Δ. **Equivalence is concluded only if both are rejected**, equivalent to requiring the 90% (5th–95th percentile) bootstrap interval for mean(f) to lie entirely within (−Δ, +Δ).
- **Margin Δ = 0.10** (justification reconsidered in §4).

### 2.4 Multiplicity — corrected reasoning, not just a stated correction
- **Within P1 (Part A and Part B/estimation):** no additional correction is applied *between* the two parts. This is deliberate, not an oversight: since the compound claim "the dampening mechanism's rationale holds" requires **both** parts to succeed (an intersection–union structure), the overall false-positive rate for the compound claim is already bounded by the stricter of the two component tests' α — combining two α=0.05 tests with an AND does not inflate Type I error the way combining them with an OR would. (This is the standard intersection–union test result, not a novel argument invented for this document.)
- **Between P1 (as one compound claim) and P2:** these are two genuinely distinct scientific questions, each separately reportable regardless of the other's outcome, so they *are* treated as a 2-member family with Holm correction at overall α=0.05. This is unchanged in conclusion from V3, now with the reasoning for why P1's internal parts are *not* separately corrected made explicit.

## 3. The 0.10 threshold in P1 Part B — could not be independently justified, so it is downgraded

Reusing the paraphrase-equivalence margin as a "how big a gap proves the mechanism works" threshold is not defensible on reflection: an equivalence margin answers "how small a difference is practically nothing," which is a different question from "how large a difference proves a specific mechanism is doing meaningful work," and conflating the two would let one convenient number quietly answer both without separate justification. **No independently defensible discrimination threshold was found for this specific claim in this pass.** Per the instruction's own fallback: **P1 Part B is now a pure estimation claim** (§2.2) — the primary reported quantity is the effect size `final_score(C1) − final_score(C4)` with its topic-clustered 95% CI, plus a one-sided significance check that the gap is positive and nonzero. The manuscript may *describe* the magnitude relative to the 0.10 reference point borrowed from the metamorphic protocol (e.g., "a gap of this size or larger would match this project's own established threshold for a non-trivial score movement"), but explicitly **as an interpretive anchor, not a pre-registered success criterion**.

## 4. Paraphrase margin — what MG-1 actually establishes, and a second, independent check

**Honest limit of the MG-1 justification:** MG-1's 0.10 threshold is an **engineering acceptance criterion** this project chose for itself — evidence that 0.10 is *internally consistent* with a standard this project already applies, not evidence that 0.10 is an externally validated, objectively "correct" practical-equivalence margin. V3's wording already leaned this way; this version states the distinction as its own explicit subsection rather than a passing qualifier, per the direct challenge to assess this critically.

**A second, independent anchor found in this pass:** the evaluator's own documented decision thresholds (Table V of the manuscript: follow-up triggers at 0.45, 0.75, 0.80, 0.90; the mandatory cap at 0.60; the reasoning floor at 0.30) have a **smallest gap between adjacent decision-relevant thresholds of 0.10** (0.90 − 0.80, the depth-probe boundary). This gives a second, independently-motivated reading of 0.10: it is not only a prior engineering choice (MG-1) but also the smallest score movement that would already change which of this system's own downstream decisions fires. Both anchors point to the same number for different reasons, which is more corroboration than V3 had, though neither is an external, domain-validated ground truth — that would require, for example, evidence about what score difference changes a real grading or hiring decision, which does not exist in this project and is not invented here.

**Ensuring C1 and C2 differ only in wording:** an automated check is added — C2 must cover the **identical set** of mandatory/semantic concepts as its paired C1 (verified by the same concept-presence check the evaluator itself uses conceptually, but implemented here as an independent, disclosed text-matching rule against the rubric's own concept list, not by calling the evaluator), so a clumsy paraphrase cannot silently drop or add content while still passing as "just reworded."

## 5. Construction validity — every category, exactly how it is checked, without using the evaluator as ground truth

| Category | Construction rule | Automated (text-only) check | What still requires human judgment, disclosed as such |
|---|---|---|---|
| C1 (correct) | Independently worded (not verbatim rubric text, §3.2 of V3), covers all mandatory + semantic content | ≥1 causal connective present; concept-presence check confirms full mandatory/semantic coverage; minimum word count | Fluency/naturalness (spot-checked, §below) |
| C2 (paraphrase) | Independently worded, differs from C1 by a disclosed transformation | Same concept-presence check as C1 (§4); zero verbatim-sentence overlap with C1 (a simple n-gram check) | That the reworded meaning is truly preserved (spot-checked) |
| C3 (partial) | A true subtractive edit of C1 (delete target clause(s) only) | Verbatim match to C1 except for the deleted span(s), verified by a diff check; concept-presence check confirms exactly the intended concept(s) are now absent | — (mechanical construction leaves little to validate beyond the diff check) |
| C4 (keyword-stuffed) | Shares ≥90% of C1's key terms (minimal pair), zero connectives, ≥2 distinct concepts present (not one term repeated) | Banned-connective list check; term-overlap check against paired C1; a distinctness check (≥2 non-duplicate mandatory/concept terms present) | That it still superficially resembles something a real candidate might type (spot-checked) |
| C5a (lexically-matched misconception) | Near-verbatim restatement of one `common_mistakes` entry | High overlap check with the source mistake text (this is a manipulation check, §1 — high overlap is *intended*, not a flaw here) | — |
| C5b (independently-worded misconception) | Same underlying error as a `common_mistakes` entry, low lexical overlap with its text | Overlap-with-source < 0.30; topical-overlap-with-C1 within tolerance of C5a's (§1) | **That the claim is actually technically wrong** — this cannot be automated without circularity (checking correctness with a model would reintroduce the very problem being fixed); verified by the construction team's own domain knowledge, cross-checked by the blind spot-check reader answering a correctness question, not just a category-matching question (extended below) |
| C6 (contradictory) | An affirmative claim plus its explicit negation, both about the same sub-claim | Negation-marker check; the negated clause must share high word-overlap with the affirmative clause it negates (operationalizing "same claim, now negated," not an unrelated negation elsewhere) | — |
| C7 (irrelevant) | One of 3 rotated, topic-independent templates | A topic-keyword-absence check (confirms none of the question's own key terms appear) | That no template accidentally reads as relevant to some question (spot-checked) |

**Extended blind spot-check (replaces V3's category-only version):** before the confirmatory run, one team member not involved in template design reads a random 10% sample of the *development* set and, for each item, answers two questions without being shown the intended label: (1) which of the 7 (now effectively 8, counting C5a/C5b) categories does this look like, and (2) is the technical content correct or incorrect. Disagreement on either question for a development item triggers a review of that item's template before anything is frozen for the confirmatory run. This is disclosed exactly as what it is: a single-organization, non-blinded-to-the-project (though blinded to the specific label) spot-check, not independent expert validation — the same honest limitation as V3, now extended to also probe correctness, not just category membership.

## 6. Aggregation, exact sample sizes, and the limits of generalization

### 6.1 Aggregation hierarchy (stated precisely, was underspecified in V3)
1. **Within-question, across variants:** C2's two wording variants are averaged to one per-question C2 value. C5b's independently-worded variant(s) are averaged to one per-question C5b value (using 1 variant per question in this version, for tractability — see §6.2). C3's "high" and "low" partial levels are **not** averaged — they test different completeness degrees and are kept as two separate secondary contrasts. C1, C4, C5a, C6, C7 have exactly one item per question, no averaging needed.
2. **Within-topic, across questions:** for reporting (not for the bootstrap itself), a topic's descriptive value for any contrast is the mean of its questions' per-question values.
3. **Across topics (the inferential level):** the primary hypotheses' bootstrap resamples **topics** with replacement (B=5000, seed fixed and disclosed at registration, separate from the split-selection seed); each resampled topic instance contributes **all** of its own per-question values (so an 8-question topic contributes proportionally more data whenever drawn than a 1-question topic, which is the correct, standard behavior of a cluster bootstrap, not an error to correct). This is the same procedure already used and validated earlier in this project's own re-analysis of the human benchmark, extended here to topics of unequal size.

### 6.2 Exact counts, every split, no ranges
- **Eligible questions:** 122 of 125.
- **Development:** 6 topics (`BitManipulation, DynamicProgramming, Graphs, Heaps, LinkedLists, Strings`), **26 questions**.
- **Confirmatory:** 31 topics, **67 questions** (includes the 3 oversized topics capped at 8 each: `C_Programming`, `DSA_Theory`, `Arrays`; 19 single-question topics; the remaining small multi-question topics).
- **Cap-excess reserve (development-only, not scored):** 29 questions.
- **Items per confirmatory question:** C1 (1) + C2 (2 variants → 1 aggregate) + C3 (2, kept separate) + C4 (1) + C5a (1) + C5b (1) + C6 (1) + C7 (1) = **10 constructed items, 8 distinct per-question analysis values** after the aggregation in §6.1.
- **Total confirmatory items:** 67 × 10 = **670**.

### 6.3 Inferential unit and generalization limits, stated explicitly
The inferential unit for every primary and secondary hypothesis is the **topic** (31 in the confirmatory set), with the **question** as the sub-unit determining each topic's contribution weight. This benchmark's findings generalize only to: (a) the 37 topics present in this project's own rubric bank — not a random or representative sample of all technical-interview topics; (b) rule-constructed synthetic text, not organically written candidate answers; (c) English, text-only content (no speech/audio channel is exercised); (d) the specific evaluator checkpoint scored at run time. None of these boundaries is new to this pass, but V3 did not state them together in one place; this version does, so the eventual manuscript has one clear paragraph to draw from rather than scattered caveats.

## 7. Manipulation check (M1) — always reported, failure is diagnosed, not suppressed

V3's wording risked implying a failed manipulation check would cause results to be silently withheld. Corrected: **M1 (`final_score(C1) > final_score(C7)`) is reported in every case, regardless of outcome.**
- **If M1 holds:** proceed to interpret P1/P2 normally.
- **If M1 fails:** before drawing any conclusion, check whether the C1 and/or C7 items involved passed their own construction-validity checks (§5) and the blind spot-check. Two outcomes:
  - **Construction checks passed:** the M1 failure is **not** attributed to construction. It is reported as a genuine, informative finding about the evaluator — that it did not reliably separate a complete, correct, on-topic answer from a fixed off-topic template — which would itself be a substantive, reportable result, not a discarded run.
  - **Construction checks reveal a specific flaw** in the particular items involved: **at most one disclosed remediation pass** is allowed — reconstruct only the flagged item(s), re-verify against the same checks, and re-run the analysis once. This single correction is logged (what changed, why, before/after) in the eventual results write-up. No second remediation pass is permitted; if M1 still fails after one disclosed correction, the finding stands and is reported as evidence about the evaluator, closing off the iterative "keep adjusting until it passes" failure mode explicitly.

## 8. Analysis integrity — the exact bootstrap procedure, validity under unequal topic sizes

For every hypothesis (P1 Part A, P1 Part B, P2, M1, and the secondary contrasts): compute the relevant per-question paired difference (after the within-question aggregation in §6.1); resample the 31 confirmatory topics with replacement, B=5000 times; for each resampled multiset of topics, pool **all** per-question values belonging to the resampled topics (a topic drawn twice contributes its questions twice); compute the mean of the pooled values; collect the resulting distribution across the 5000 replicates; read off the 2.5th/5th/95th/97.5th percentiles as needed per §2. This procedure is valid for singleton topics (they simply contribute one value whenever drawn, exactly like any other cluster) and for the 8-to-1 range of topic sizes present here (larger topics contribute more data whenever drawn, which is the intended, correct behavior of cluster-robust resampling, not a distortion to correct for separately). The bootstrap and hypothesis-testing code itself is written and hashed as part of the registered protocol, before any confirmatory score exists, so no analysis-code choice can be made after seeing results.

**Contingency if a remediated item (§7) leaves a topic empty:** prefer reconstructing a valid replacement question for that same topic to keep the topic count at 31; if genuinely impossible (a topic with no further eligible questions), that topic is dropped and the confirmatory topic count is disclosed as 30, not silently reported as 31.

## 9. Final verdict on this pass (not a rubber stamp)

**What is now defensible:** the statistical machinery (§2, §8) is precise, correctly signed, and its multiplicity reasoning is sound. The most serious validity threat found across all four passes — C5's circularity — is structurally fixed, not patched. The paraphrase margin now has two independent, if still non-external, anchors (§4) instead of one borrowed number. The manipulation check can no longer quietly suppress an inconvenient result (§7). Sample sizes and the aggregation hierarchy are now exact, not ranges (§6).

**What remains a real, disclosed limitation, not resolved by this pass:**
- Whether a constructed misconception (C5b) is genuinely *false* still rests on the construction team's own domain judgment, cross-checked by one blinded reader from the same organization — not independent expert validation. This is a structural limit of doing this work without new human-subject recruitment, which the user has explicitly ruled out; it is not fixable within that constraint, only disclosed honestly.
- The 0.10 margin, however now double-anchored, is still a project-internal choice, not an externally validated practical-equivalence value.
- The `topic` field's semantic homogeneity (is "DSA_Theory" one coherent cluster or a catch-all) is still unverified, flagged again in this pass, not investigated further, since it would require qualitative content review out of scope for this statistical audit.
- Applying the 0.10 margin to the S2 sub-score (§2.1) extrapolates beyond what MG-1 actually measured (`final_score` only); disclosed, not fixed.

**Recommendation:** the design is now statistically and experimentally defensible **for the scoped, exploratory construction-property claim it makes** — not as a general validation of the evaluator's semantic understanding, and only if every limitation named above is stated in the eventual manuscript exactly as disclosed here. I would not have signed off on V3 as written; I would sign off on V4 at this scope. Registration (hashing, tagging, run-manifest approval) is still the user's decision to make, not mine to grant.
