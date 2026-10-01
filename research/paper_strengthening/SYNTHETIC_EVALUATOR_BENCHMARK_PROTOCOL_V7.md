# Synthetic Category-Discrimination Benchmark for the Hybrid Evaluator — V7 (final)

**Status: complete protocol, NOT executed, NOT registered.** V1–V6 preserved unmodified. This version makes two corrections found by actually running the cross-checks requested, not by re-reading and re-trusting V6: a disclosure correction (§1 — no design change, but a claim that needed to be stated more precisely) and a real statistical correction to the estimator itself (§2 — this one required a fix, not just a caveat).

## 1. Cross-experiment qid/topic overlap — checked directly, not assumed

I generated V6's actual confirmatory and development qid lists (from the registered seed, 20260921) and cross-referenced them against the qids used in the frozen Paper-2 human benchmark (`paper2_case_level_results.csv`: qids 1, 3, 7, 10, 15, 22, 41, 50) and the metamorphic-invariance tests (`paper2_metamorphic_results.csv`: qids 1, 3, 10 — the same three cases whose observed deltas partly justify D1's 0.10 margin, V4 §4).

**Result:**
- **5 of the 8 Paper-2 human-benchmark qids (1, 7, 10, 15, 50) fall inside D1's 67-question confirmatory set.** 2 more (3, 22) fall inside D1's own 26-question development set. 1 (41) falls in the excluded 29-question cap-excess pool.
- **2 of the 3 metamorphic-test qids (1, 10) fall inside D1's confirmatory set.** The third (3) falls inside D1's development set.
- **No prior D1 pilot work exists to check** — nothing has been generated or scored for D1 yet, so this part of the request has nothing to find; stated plainly rather than skipped.

**What this does, and does not, mean — the exact distinction requested:**
- **"Unseen during D1's own development/template-piloting process" still holds, for every one of D1's 67 confirmatory questions,** including the 5 that overlap with Paper-2. V6 §1's fix (excluding the 29 cap-excess questions from any active use) closes the only leakage path that existed between D1's *own* development activity and its confirmatory set; the Paper-2/metamorphic overlap is a separate fact about a *different, prior, unrelated* study, not about D1's construction process.
- **"Never previously evaluated by this project's evaluator" does not hold** for those 5 (Paper-2) and, for 2 of them, also not for the metamorphic tests. This is a materially different, weaker claim than the first one, and V6 did not distinguish them — it is stated explicitly here so the eventual manuscript cannot blur "novel to D1's construction" into "novel to any evaluation of this system."
- **Why this does not compromise D1's own statistical validity:** the evaluator is a fixed, frozen checkpoint applied deterministically per call — it is not adaptively updated between scoring sessions, so a question having been scored once before (on different, human-authored answer text, for an unrelated purpose) does not give the evaluator any advantage or disadvantage on D1's newly constructed synthetic items for that same question. The margin-derivation concern is addressed directly: the 0.10 margin (V4 §4) was set from the metamorphic protocol's *own* observed deltas on qids 1, 3, 10 under *its own* paraphrase transformations — D1 applies that pre-specified, already-fixed margin to *new* text (C1 vs. C2, newly constructed) for those same two question IDs among 65 others; it does not re-measure or re-validate the margin using D1's own data, so there is no circularity in the sense of "the threshold was tuned on the same data used to test against it."
- **Disclosure obligation (the actual correction):** the manuscript states both facts side by side — D1's confirmatory set was unseen during D1's own construction, *and* 5 of its 67 questions (2 of which also underlie part of the margin's justification) have prior evaluation history in this project under a different study. This is now explicit; V6 did not say it.

## 2. The topic-cluster bootstrap was estimating the wrong quantity — a real fix, not a caveat

**The problem, found by re-deriving the procedure rather than re-describing it:** V4–V6 defined the bootstrap as "resample the 31 confirmatory topics with replacement; for each resampled topic instance, pool *all* of its per-question values; compute the grand mean of the pooled values." That procedure gives *correct* cluster-robust uncertainty, but the **point estimate itself is a question-weighted average, not a topic-weighted one** — a topic capped at 8 questions (`C_Programming`, `DSA_Theory`, `Arrays`, 24 of 67 confirmatory questions between them, 36%) still contributes 8× the weight of any of the 19 singleton topics to the actual number being estimated. This directly works against the stated research claim — "generalizes across topics," the entire reason V3 introduced topic-based splitting and capping in the first place. Capping limited how *often* those three topics' individual questions appear, but the old estimator still let their sheer question count dominate the average. This is a genuine mismatch between the estimand and the claim, not a matter of degree.

**Fix — the estimator, not just the resampling, changes:**
1. **Within each confirmatory topic**, compute the topic's own mean of the relevant per-question contrast (e.g., for P1-i: `T_t = mean over topic t's questions of [final_score(C1) − final_score(C4)]`). A singleton topic's `T_t` is just its one question's value.
2. **Point estimate (topic-equal-weighted, matches the stated claim):** `estimate = mean over the 31 confirmatory topics of T_t` — every topic counts once, regardless of how many questions it contributed.
3. **Bootstrap CI:** resample the 31 topics with replacement (B=5000, as before); for each resampled multiset, average the **already-computed topic-level `T_t` values** for the resampled topics (a topic drawn twice contributes its own `T_t` twice — not its individual questions twice). This is the standard cluster-bootstrap-of-cluster-means procedure, and it is valid for singleton topics (a cluster of size 1 contributes its own mean, exactly like any other cluster) and for the 1-to-8 range of topic sizes present, without letting topic size distort the estimate itself.

**Applied everywhere the old procedure was used:** P1-i, P1-ii, P2 (both TOST components), the S2 descriptive report (V5 §1), and M1 — all now use topic-equal-weighted point estimates with topic-level cluster bootstrap CIs, replacing the question-pooled version in V4–V6 wherever it appeared. The p-value definitions in V6 §2.1–2.2 (proportions of the bootstrap distribution on the correct side of the null) are unchanged in form — only the quantity whose bootstrap distribution is being read (topic-mean-of-means, not pooled-question-mean) changes.

**Added, as a secondary, descriptive check only (not a new hypothesis, not part of the corrected primary family):** the question-weighted version of each primary contrast is also reported alongside the corrected topic-weighted version, so a reader can see whether the two weighting schemes materially disagree — informative context, not a competing claim requiring its own correction or hypothesis status.

**Precision-projection table (V4 §6.4 / V5 §2, already labeled illustrative, not a power calculation for D1) is unaffected by this fix** — it borrowed a different dataset's variance structure purely to illustrate that more clusters narrow CIs in general, and was never computed using D1's own (question-pooled) estimator in the first place, so there is nothing to re-derive there.

## 3. SHA-256 integrity — verified against actual bytes, not assumed

V6's previously reported hash (`a3643410bcd084f367ae1f86d0d329a9f3b1bdab8d924af603339ba7239837ed`) was re-computed against the file on disk in this pass and **matches exactly** — no integrity discrepancy was found in V6's own record-keeping. Because §2 is a substantive correction, V6 is superseded by this file, and the registration package below references **this file's** freshly computed hash, not V6's — computed after this document was finalized, reported in the chat response (never embedded self-referentially in the file itself).

## 4. Everything else — unchanged, carried forward by reference

The topic-holdout-use restriction (V6 §1, still in force and now cross-checked against external studies too, §1 above), the exact split and counts (122 eligible; 26 dev / 67 confirmatory / 29 excluded, unchanged in composition), the C5a/C5b redesign, the construction-validity table, the blind spot-check, the S2-descriptive-only treatment, the Holm procedure and its exact comparison values (V6 §2.3, structurally unchanged — only the underlying per-hypothesis point estimates and CIs it operates on are now topic-weighted), the manipulation-check diagnose-don't-suppress rule, and every standing limitation from V4 §9 / V6 §6 remain exactly as stated and are not repeated here.

## 5. Final audit conclusion

Both checks requested were performed by direct computation, not by re-asserting prior claims. One (§1) required a disclosure correction — a claim that was true but stated less precisely than it needed to be. The other (§2) required an actual fix to the estimator, because the previous version was answering a subtly different question than the one the paper claims to answer. No new hypothesis was added, no settled design decision (the split, the categories, the margin choices, the manipulation-check handling) was reopened. **No further issue was found in this pass beyond these two.**

## 6. Registration package (final)

- **Protocol file (frozen):** `SYNTHETIC_EVALUATOR_BENCHMARK_PROTOCOL_V7.md`
- **SHA-256:** see chat response for the exact value, computed after this file was written.
- **Proposed Git tag:** `prereg/D1-eval-synth/v1` (unchanged — still the first actual registration attempt; V1–V7 are drafting history).
- **Required run-manifest fields:** unchanged from V6 §7 — git commit at run time; evaluator/CrossEncoder checkpoint SHA-256 (expected `6a241a55…`, re-verified not assumed); the frozen confirmatory/development qid lists and the split seed (20260921); a separate, disclosed analysis-bootstrap seed fixed at registration; date; operator; environment-pin status.
- **Exact proposed commands:** unchanged from V6 §7 (`d1_generate_items.py` → `d1_score_items.py` [the sole model-inference step, requiring approval] → `d1_analyze.py`, the last of which now implements the corrected topic-weighted estimator from §2 above, not the question-pooled one).
- **Expected computational requirements:** unchanged, under ~10 minutes, CPU-only, one machine.
- **Pre-execution integrity checks:** V6 §7's six checks, plus a seventh added here: **confirm the analysis script computes topic-level means first and resamples those means (§2), not raw per-question values** — a direct code-level check against exactly the mistake this version fixes, so it cannot silently regress back to the old estimator at implementation time.

Not executed: no item generated, no model called, no tag created, nothing committed or pushed.
