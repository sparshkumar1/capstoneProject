# Synthetic Category-Discrimination Benchmark for the Hybrid Evaluator — V3

**Status: complete protocol, NOT executed, NOT registered.** This is a genuine critical revision of V2, not a defense of it — several V2 design choices are changed, one number in V2 (the confirmatory scale) turns out to have been optimistic once a necessary safeguard is applied, and V2's TOST margin justification is replaced with a stronger one grounded in this project's own existing evidence. Two computations below (§1, §2, §6.4) are re-analyses/inspections of already-existing files — no model call, no new score, no frozen file modified.

## Ranked list of changes from V2 (most scientifically important first)

1. **Fixed a real leakage risk in the paraphrase test.** V2's C1 was built directly from verbatim rubric phrasing, giving it a built-in wording advantage over C2 that had nothing to do with paraphrase robustness. This could have made the paraphrase-equivalence test fail for a construction-artifact reason, not a genuine evaluator property. Both C1 and C2 are now independently worded away from the rubric's exact phrasing (§3.2).
2. **Corrected the confirmatory sample size, once a necessary topic-imbalance safeguard is applied.** Three topics (`C_Programming` 25, `DSA_Theory` 18, `Arrays` 10) would otherwise supply 43% of all data. Capping each at 8 questions (moving the excess to a development-only reserve) is necessary to prevent three topics' idiosyncrasies from driving the result — but it means the realistic confirmatory scale is **31 topics / 67 questions**, not the ~107 questions loosely estimated in V2. This is reported honestly as a downward revision, not smoothed over (§2).
3. **Replaced the TOST margin's justification.** The V2 margin (Δ=0.10, borrowed from an unrelated human-rater-disagreement threshold) is replaced with the *same* margin, but now justified by this project's own existing, already-frozen metamorphic-invariance protocol, which already uses **|delta| ≤ 0.10** as its own paraphrase-invariance criterion (`paper2_metamorphic_results.csv`, relation MG-1) — and whose observed deltas (−0.039, −0.051, −0.043 on 3 base cases) sit comfortably inside that margin, giving genuine, if limited, empirical support (§4).
4. **Surfaced a directly relevant existing finding that changes the paper's expectations.** The same metamorphic file already shows the *keyword-injection* criterion (score ≤ 0.50 without supporting reasoning) **failing in 2 of its 3 existing test cases** (0.578 and 0.664, both above the 0.50 bound). This means D1's central "does dampening work" hypothesis is not a safe bet to confirm — it is a genuinely open question with an existing hint of trouble, and the manuscript should be written to survive either outcome, not to expect confirmation (§4.3, §7).
5. **Corrected a mismatch in the precision projection.** V2's projection recycled a different dataset's variance structure (the human-rated benchmark's full-vs-R-only error) as a stand-in for D1's own, different hypotheses. This is now labeled explicitly as an illustrative, generic demonstration that more clusters narrow CIs — not a power calculation for D1's actual tests — and is recomputed at the *realistic* capped scale (§6.4).
6. **Simplified the primary hypothesis family and specified every remaining test concretely.** V2's third hypothesis (a fuzzy full-category ordering) is removed as a scored primary claim and demoted to a pre-registered, non-corrected **manipulation check** (C1 must beat C7 — if it doesn't, stop and investigate construction before interpreting anything else). The primary family is now exactly **2** hypotheses (§5).
7. **Removed single-template lexical shortcuts in two places.** C7 (irrelevant) used one fixed string for all 122 questions — trivially learnable as "this exact string is always low," not a real test of irrelevance-detection. Now built from 3 rotated templates. C4 (keyword-stuffed) used one fixed surface pattern (a flat term list) — now varies packaging (list, header-style, comma-run-on) across items so the test isn't keyed to one syntactic shape (§3.4).
8. **Added a sharper control distinguishing "reasoning" from "the presence of connective words."** A CrossEncoder trained for passage relevance may reward connectives like "because" as a relevance/entailment cue even when the reasoning they introduce is circular or vacuous. A new secondary variant — connective-laden but circular reasoning — tests whether R rewards genuine soundness or just surface connectivity (§3.5).
9. **Disclosed and partially mitigated single-author construction bias.** Unlike the human benchmark (three independent raters), this benchmark's category labels and text are constructed by one team without independent verification that items read as intended. A cheap blind spot-check (a second, template-uninvolved team member guesses categories on a random development-set sample before the confirmatory run) is added as a manipulation-validity safeguard (§3.6).
10. **Clarified effective sample size explicitly, everywhere.** The item count (~670, once corrected — see §2.3) is not the inferential sample size; 67 questions / 31 topics is. Multiple variants per category buy construction robustness and enable the component ablations, not additional statistical power. This is now stated as a standing rule for how any result from this benchmark may be described (§6.5).
11. **Added a per-configuration comparison table**, mirroring `EXISTING_EVIDENCE_ANALYSIS.md`, so the "does the full evaluator actually help" question is answered with the same rigor here as it was for the human benchmark (§6.3).
12. **Tightened C3's construction rule** to a true subtractive edit of C1 (delete target clauses, keep all other wording verbatim) rather than an independent rewrite, removing an incidental-wording confound (§3.3).
13. **Added a mandatory-cap edge case**: whether bonus credit can improperly offset the 0.60 cap, a real formula-interaction question worth checking alongside the existing cap ablation (§6.6, minor).

## 1. Eligibility audit (unchanged methodology, exact counts restated)

Same criteria as V2 §1. **122 of 125 questions eligible** (3 excluded — qid 26, 39, 110 — for mandatory phrases too long to flatten into a clean keyword list, without ambiguity). **37 distinct topics** among the eligible set.

## 2. Scale, topic imbalance, and the corrected split

### 2.1 The imbalance is worse than V2 acknowledged
Exact topic sizes among the 122 eligible questions: `C_Programming` 25, `DSA_Theory` 18, `Arrays` 10 — **three topics alone are 43% of all eligible data.** At the other extreme, **19 of the 37 topics (51%) have exactly one eligible question.** V2's "≈30–32 confirmatory topics, ~102–107 questions" did not account for what happens if the three oversized topics are left uncapped: they would dominate any topic-clustered statistic with their own idiosyncrasies (e.g., C-syntax mechanics vs. conceptual theory questions may behave differently under the evaluator, and an uncapped design would let that difference masquerade as a general finding).

### 2.2 Per-topic cap, applied and reported honestly
A cap of **8 questions per topic** is applied to the 3 oversized topics before any split is drawn. Excess questions (17 from `C_Programming`, 10 from `DSA_Theory`, 2 from `Arrays` — 29 total) are set aside as **development-only reserve material** (extra template-piloting content, never scored), not discarded and not silently used to inflate the confirmatory count.

### 2.3 The corrected, exact split (computed in this pass, seed disclosed: 20260921)
- **Development: 6 topics, 26 questions** — deliberately chosen to *exclude* the 3 oversized topics (so their depth is preserved for confirmatory), drawn from the remaining multi-question topics: `BitManipulation, DynamicProgramming, Graphs, Heaps, LinkedLists, Strings`.
- **Confirmatory: 31 topics, 67 questions** — includes the capped versions of the 3 oversized topics (8 each), all 19 singleton topics, and the remaining small multi-question topics (`Sorting` 3, `Stack` 4, `Trees` 5, `Matrix`/`BinarySearch`/`Recursion`/`Memory Management`/`Storage Classes`/`Binary Trees` 2 each).
- **This is smaller than V2's estimate.** V2 projected ~107 confirmatory questions by not accounting for the cap; the honest number, once the cap is applied, is **67**. This is reported as a correction, not minimized — it is still an **8x increase in independent question-level units and a ~4x increase in independent topic-clusters** over the existing 8-question human benchmark, which remains the paper's real point of comparison.

### 2.4 What this split does and does not achieve
- **Achieves:** confirmatory testing on topics never touched during template development, spread across 31 distinct topics rather than concentrated in a few; the 3 largest topics remain present (capped, not excluded), so within-topic behavior on genuinely multi-question topics is still observable.
- **Limitation, disclosed rather than hidden:** 19 of the 31 confirmatory topics contribute exactly one question each. For those, "topic-clustered" and "question-level" analysis are identical — the clustering correction only does real work for the ~12 topics with multiple questions. This is stated plainly in the eventual manuscript, not implied away by citing "31 topics" as if it meant 31 equally-informative clusters.
- **Limitation:** the `topic` field's granularity was not independently reviewed for semantic homogeneity (e.g., whether "DSA_Theory" is a coherent conceptual cluster or a heterogeneous catch-all). This benchmark uses the field as given; a mislabeled or overly broad topic taxonomy would understate true clustering and is a residual risk not fully resolved here.

## 3. Category construction — further hardening

### 3.1 Construction-guaranteed vs. requires-validation (explicit table, all 7 categories)

| Category | Guaranteed by construction | Requires separate validation |
|---|---|---|
| C1 (correct) | Contains all mandatory concepts and semantic targets | Reads as fluent, natural prose (not stilted in a way that could itself depress scores) — checked via the blind spot-check, §3.6 |
| C2 (paraphrase) | Same propositional content as C1, independently worded | Genuinely preserves meaning without introducing a subtle error — spot-checked, §3.6 |
| C3 (partial) | Omits exactly the targeted mandatory concept(s), all else verbatim from C1 | That the omission is the *only* substantive change (enforced by the subtractive-edit rule, §3.3, not an independent rewrite) |
| C4 (keyword-stuffed) | Zero banned connectives; ≥90% term-overlap with its paired C1 | That the result still plausibly resembles something a real candidate might submit (not so garbled it fails as a fair test) |
| C5 (misconception) | Textually matches one specific, named `common_mistakes` entry | That the "mistake" reads as a plausible claim a candidate might actually believe, not an absurd strawman |
| C6 (contradictory) | Contains an affirmative claim and its explicit negation marker | That the contradiction isn't so obvious/marked that it becomes a trivial lexical-pattern match rather than a test of contradiction-sensitivity |
| C7 (irrelevant) | Drawn from one of 3 fixed, topic-independent templates (§3.4) | That none of the 3 templates accidentally contains topic-relevant content for some question |

**Standing rule:** every category label is a *construction property*, never asserted as a certified measure of real-world answer quality. This distinction is stated in the manuscript wherever this benchmark's results are reported.

### 3.2 Fixing the C1/C2 leakage risk (highest-priority change)
V2 built C1 directly from the rubric's own `semantic_targets`/`mandatory` wording, then built C2 as a reworded version of C1. This gives C1 an implicit "verbatim rubric overlap" advantage that C2 does not share — meaning a C1-vs-C2 score gap could reflect *wording overlap with the scoring reference*, not a real paraphrase-robustness failure. **Fix:** neither C1 nor C2 uses the rubric's exact phrasing. Both are independently worded restatements of the required content; C2 is additionally required to differ from C1 by a disclosed transformation (clause reordering, or synonym/structure substitution — 2 variants as in V2, §3.3 below), so the only planned difference between C1 and C2 is which of two independent wordings was used, not proximity to the rubric text.

### 3.3 Multiple variants and a tightened C3 rule
Unchanged from V2 for C1 (now non-verbatim, §3.2), C2 (2 variants, non-verbatim), C5 (up to 2, from distinct listed mistakes), C6 (1). **C3 changed:** built as a true subtractive edit of C1 — delete the sentence(s) covering exactly the targeted mandatory concept(s), keep every other word of C1 unchanged — rather than an independent rewrite, removing incidental-wording as a confound. Two completeness levels retained ("high partial": omit one mandatory concept; "low partial": omit all mandatory concepts, retain only a general topic mention).

### 3.4 Removing single-template lexical shortcuts
- **C7 (irrelevant):** 3 fixed, topic-independent templates (not 1), assigned to questions by a disclosed, fixed rotation (e.g., `qid mod 3`), so no single fixed string could be learned as "the" irrelevant marker and the test isn't reducible to recognizing one exact string.
- **C4 (keyword-stuffed):** the *terms* are locked to the C1 minimal pair (§3.2 of V1/V2, retained), but the **surface packaging** of those terms is varied across items — a flat comma list, a colon-headed list ("Key concepts: ..."), and a run-on enumeration without punctuation structure — assigned by the same disclosed rotation, so the construction-validity check (zero banned connectives) is satisfied by multiple surface forms, not one.

### 3.5 New: a connective-but-vacuous control (addresses "reasoning vs. surface cues")
A CrossEncoder trained on passage-relevance data may treat the presence of connective words ("because," "therefore") as a relevance signal independent of whether the reasoning they introduce is actually sound. To test this directly, one **secondary** (not primary-family) variant is added per confirmatory question: a "circular" answer that *does* contain connectives but whose reasoning is vacuous (e.g., "you use a hash map because a hash map is the right data structure for this problem"). If R scores this meaningfully higher than C4 (which lacks connectives) despite being equally uninformative, that is evidence R responds to surface connectivity rather than reasoning soundness — a genuinely informative, non-trivial finding either way, reported descriptively (not part of the Holm-corrected primary family, to avoid inflating the family for an exploratory addition).

### 3.6 Author-construction bias: disclosure and a cheap mitigation
This benchmark's text is written by the same team producing the paper, without the human benchmark's independent-rater check. **Mitigation:** before the confirmatory run, one team member not involved in writing the category templates blind-reads a random sample (a disclosed fraction, e.g. 10%, of development-set items) and guesses each item's intended category without being told the taxonomy in advance beyond a one-line description of each of the 7 categories. Disagreement between the intended and the blind-guessed category on a development item triggers a review of that template before it is used on any confirmatory item. This is a validity spot-check, not a substitute for the automated construction checks (§3.4 of V2, retained), and is reported in the manuscript as exactly what it is: a partial, non-blinded, single-organization safeguard, not independent expert validation.

## 4. The TOST margin, re-justified

**Margin retained at Δ = 0.10**, but now justified differently and more directly: this project's own existing metamorphic-invariance protocol (`research/results/paper2/paper2_metamorphic_results.csv`, relation **MG-1: Paraphrase Invariance**) already uses **|delta| ≤ 0.10** as its own criterion for acceptable paraphrase-induced score movement, and its three existing test cases (qid 1, 3, 10) show observed deltas of **−0.0386, −0.0506, −0.0431** — all comfortably inside that margin. Using the same margin here keeps this benchmark's paraphrase test consistent with an already-established, already-used project standard, rather than importing a number from an unrelated context (human-rater disagreement, as V2 argued). This margin is disclosed as a project-standard choice, revisable if the user prefers a different one, but it is no longer an ad hoc transfer.

**The same file surfaces a directly relevant, already-existing risk** (see the ranked list, item 4): its **MG-5: Keyword Injection** relation (criterion: score ≤ 0.50 without supporting reasoning) already **fails in 2 of 3 existing cases** (scores 0.578 and 0.664, both above the bound). This is small-sample existing evidence (only 3 cases) but it means D1's dampening/keyword-stuffing hypothesis should not be written up as an expected confirmation — the manuscript's framing must be able to report either outcome credibly, and this existing hint should be cited as prior context, not omitted because it's inconvenient.

## 5. Primary hypotheses, simplified and fully specified

**Primary family (exactly 2, Holm-corrected at α=0.05 across the pair):**

- **P1 — Dampening/keyword-stuffing, two-part (unchanged in structure from V2 §4.3, restated precisely):**
  - Part A: `S2(C4)` is non-inferior to `S2(C1)` (TOST, margin Δ_S2 = 0.10, same justification as above, applied to S2). *Analysis:* topic-clustered (cluster = topic; where a topic contributes 1 question, that question is its own cluster) percentile bootstrap of the paired mean difference `S2(C4) − S2(C1)`, B = 5000, seed disclosed at registration; conclude non-inferiority if the one-sided 95% CI upper bound (for a "C4 not much lower" claim) stays inside +0.10 appropriately signed.
  - Part B: `final_score(C1) − final_score(C4)` exceeds Δ = 0.10 (one-sided superiority, same clustered bootstrap procedure). **Both parts must hold** for the mechanism's design rationale to be considered supported by this run; the manuscript reports each part's result independently regardless of the other's outcome.
- **P2 — Paraphrase equivalence (TOST, unchanged in structure, margin re-justified in §4):** conclude equivalence only if the topic-clustered 90% CI (for TOST) on `final_score(C1) − final_score(C2)` falls entirely within [−0.10, +0.10].

**Manipulation check (not part of the corrected family — a validity gate, reported separately and checked first):**
- **M1:** `final_score(C1) > final_score(C7)`, topic-clustered paired comparison. If this does not hold clearly, the confirmatory run's other results are not interpreted until construction is reviewed — a benchmark that can't separate "correct" from "off-topic" has a construction problem, not a scientific finding.

**Secondary/exploratory (reported descriptively, no family-wise correction, not used for the paper's central claim):** C1-vs-C3 (high/low partial) comparisons; C1-vs-C5 and C1-vs-C6; the C4-vs-connective-but-vacuous comparison (§3.5); the repeated-terminology and scrambled-order controls; per-topic heterogeneity; the dampening/mistake-penalty/mandatory-cap ablations (§6.6).

## 6. Analysis plan, leakage/artifact review, and cross-configuration comparison

### 6.1 What "effective sample size" means for this benchmark, stated once and applied consistently
**67 confirmatory questions across 31 topics is the inferential sample.** The ~670 total confirmatory items (67 questions × ~10 variants, per V2's §3.3 counting logic, now adjusted for §3.2's changes — recount at registration once exact variant counts per category are finalized) provide within-question construction robustness (no single template drives a category's result) and supply the component ablations (§6.6); they are **not** additional independent statistical power for P1/P2/M1, which are computed at the topic-clustered, one-comparison-per-topic-per-category level. Any manuscript sentence describing this benchmark's scale must say "67 questions / 31 topics," never "670 items," when describing statistical power.

### 6.2 Leakage, ceiling/floor effects, and other ways this could look deceptively favorable (direct response to point 7)
- **Ceiling risk on C1 (mitigated in §3.2):** verbatim-rubric construction would have given C1 an unrepresentative advantage; fixed by requiring independent wording for both C1 and C2.
- **Floor risk on C7:** an obviously off-topic template could make the C1-vs-C7 gap trivially large and uninformative — this is precisely why C1-vs-C7 is a manipulation check, not a scored scientific claim (§5): it is expected to be easy, and its only job is to confirm the benchmark isn't broken, not to demonstrate evaluator quality.
- **Construction leakage in the mandatory-cap ablation:** if every "high partial" item always omits exactly one concept in the same structural way, the cap-ablation test becomes a trivial, single-pattern check. §6.6 adds a bonus-interaction edge case specifically to avoid this being a one-note test.
- **Single-author systematic bias:** addressed by the blind spot-check (§3.6), disclosed as partial, not eliminated.
- **Multiple-comparisons inflation:** addressed by limiting the corrected family to 2 hypotheses (§5) and explicitly labeling everything else as descriptive/secondary.
- **Topic-taxonomy validity:** not fully resolved (§2.4) — flagged as a residual, disclosed limitation rather than assumed away.

### 6.3 Cross-configuration comparison (direct response to point 8)
For each of S1-only, S2-only, R-only, S1+R, S2+R, and the full composite (the same six configurations already compared in `EXISTING_EVIDENCE_ANALYSIS.md`), compute that configuration's own version of the P1-Part-B gap (`config(C1) − config(C4)`) and the P2 TOST result (`config(C1) − config(C2)`), each with a topic-clustered CI. This directly answers, on this benchmark, the same "does the full evaluator actually add discrimination beyond simpler configurations" question the human-benchmark reanalysis answered for correlation with human scores — using the same clustered-bootstrap standard, so the two benchmarks' findings are methodologically comparable and can be reported side by side.

### 6.4 Precision projection, corrected (direct response to point 4 — separating planning assumptions from findings)
**This is a planning illustration, not a power calculation for D1's own hypotheses**, because it recycles the *human benchmark's* full-vs-R-only error variance (a different outcome measure, from organically-authored constructed answers rated by humans) as a generic stand-in for "how much do more clusters help," not a projection of P1/P2/M1's actual expected effect sizes on *this* synthetic, categorical benchmark. Recomputed at the realistic, capped scale:

| K (topic-clusters) | Projected 95% CI half-width (generic illustration only) |
|---|---|
| 8 (existing human benchmark) | 0.032 |
| 31 (this design's actual confirmatory topic count) | 0.017 |
| 67 (this design's actual confirmatory question count, if treated as the clustering unit instead) | 0.011 |

No claim is made that P1 or P2's actual confirmatory CI will match these widths — this table only shows that the general principle (more independent clusters → tighter CIs) applies at this design's real scale, using a borrowed dataset's variance as an illustrative stand-in. A genuine power estimate for P1/P2 specifically would require either a pilot computation on the development set once real items exist, or an assumed minimum-detectable-effect stated and agreed before the confirmatory run — neither is done here.

### 6.5 Standing reporting rule
Every result from this benchmark states its cluster count (topics) and item count (questions × variants) separately, per §6.1, and every equivalence claim comes from a TOST procedure with a stated margin (§4, §5) — never from a non-significant test or from eyeballing overlapping CIs.

### 6.6 Mechanism ablations, plus one added edge case
Dampening, mistake-penalty, and mandatory-cap ablations as in V2 §4.5, recomputed from the confirmatory run's own S1/S2/R output (no extra model calls). **Added:** a check of whether accumulated bonus credit can push a "high partial" (mandatory-cap-triggering) item's pre-cap score above what the cap should enforce, and whether Eq. 9's `min(0.60, ...)` is applied correctly regardless — a real, specific formula-interaction question, not answered by the existing ablations as scoped in V2.

## 7. What this design would, and would not, establish (updated for the MG-5 context)

Same scope statement as V2 §7 (construction properties on synthetic text, not real-candidate validity), with one addition: because this project's own existing, if limited, evidence (§4) already shows the specific mechanism P1 tests can fail, this benchmark should be understood — and written up — as a genuine test that could go either way, not a confirmatory exercise expected to validate the existing design. A result showing the mechanism does not reliably hold at this larger scale would be a real, useful, reportable finding, not a failed experiment.

## 8. What requires approval, and what does not (unchanged in principle from V2 §5/§6)

Text/document design, the eligibility audit, the split computation, the TOST-margin literature check, and the blind spot-check protocol itself need no approval. Writing and validity-checking the confirmatory item set needs no approval. Running any of it through the live SBERT/FAISS/CrossEncoder pipeline requires full approval per `CLAUDE.md`, as does the resulting analysis (§6) since it is the same experiment's analysis step. Estimated cost at this corrected, smaller scale (~670 confirmatory items) is lower than V2's estimate — well under 10 minutes, CPU-only, one machine.
