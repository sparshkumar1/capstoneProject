# Synthetic Category-Discrimination Benchmark for the Hybrid Evaluator — V6 (final)

**Status: complete protocol, NOT executed, NOT registered.** V1–V5 preserved unmodified. This version makes the corrections found necessary by a genuine re-check of V5's actual definitions and numbers (not a re-assertion that they were fine) — one real design flaw (§1), one precision gap in the compound-test math (§2), one interpretive clarification (§3), and one arithmetic error caught by recounting rather than trusting the prior total (§4). No new hypothesis, no expanded scope, per instruction.

## 1. The development-reserve / topic-holdout conflict — a real flaw, fixed by restriction, not by re-splitting

**The problem, checked and confirmed:** V2–V5 all described the 29 "cap-excess" questions (17 from `C_Programming`, 10 from `DSA_Theory`, 2 from `Arrays`) as "development-only reserve material" for template piloting. But those three topics *also* contribute capped subsets to the confirmatory set (8 questions each). If any of the 29 excess questions were actually looked at or used to pilot category templates, the people building those templates would have been exposed to `C_Programming`/`DSA_Theory`/`Arrays` content before the confirmatory run — meaning those three topics would **not** be genuinely unseen during development, even though the *specific questions* used for piloting differ from the *specific questions* scored in confirmatory. Topic-level holdout is about the topic, not the individual question ID, and this was a real gap between what was claimed ("unseen-topic generalization") and what the design actually enforced.

**Fix chosen (the first option offered, not a re-split):** the 29 cap-excess questions are **excluded from all active use**, full stop — not used for template piloting, not read, not referenced during construction of any category template, for any topic. They are reported only as an audit-trail record of what was set aside and why (transparency), never touched again. This preserves the full, already-justified confirmatory set (31 topics, 67 questions, including the capped 8-question subsets of the three large topics) exactly as designed in V3–V5 — no re-splitting was needed, and no confirmatory topic or question changes as a result of this fix.

**Why this is sufficient, not just a caveat:** the split itself (which 8 of each large topic's questions go to confirmatory vs. the reserve) was already drawn by a disclosed, seeded random procedure before any human looked at content (§2.3 of V3, unchanged) — the random assignment itself does not leak information. The leakage risk was specifically in *using* the leftover 29 for piloting; removing that use closes the gap completely, for all three affected topics, not just partially.

**Corrected generalization claim (replaces the hedged version in V3–V5):** with this restriction in force, **all 31 confirmatory topics — including the capped subsets of `C_Programming`, `DSA_Theory`, and `Arrays` — are genuinely unseen during development.** The benchmark can now support an unseen-topic generalization claim across its full confirmatory set without qualification on this specific point. (The other, still-standing generalization limits — synthetic construction, English/text-only, this project's own rubric bank as the sampling frame, this specific evaluator checkpoint — are unchanged from V4 §6.3 and still apply.)

## 2. The compound hypothesis test, made exact

### 2.1 P1's combined p-value
For an intersection–union test (both P1-i and P1-ii must hold for the compound "dampening mechanism works as designed" claim), the combined p-value is:

`p_P1 = max(p_{P1-i}, p_{P1-ii})`

where each component p-value is defined from its own one-sided percentile-bootstrap distribution (B=5000 resamples of the 31 confirmatory topics, pooling all of each resampled topic's per-question values, per V4 §8):
- `p_{P1-i}` = the proportion of bootstrap replicates in which `mean(final_score(C1) − final_score(C4)) ≤ 0` (testing H0: mean ≤ 0 against H1: mean > 0).
- `p_{P1-ii}` = the proportion of bootstrap replicates in which `Δ_interaction ≥ 0` (testing H0: Δ_interaction ≥ 0 against H1: Δ_interaction < 0; see §3 for the exact definition of Δ_interaction).

Taking the max is the correct construction for an IUT: the compound null (at least one component fails) can only be rejected if *both* component nulls are individually rejected, which is equivalent to requiring the larger of the two p-values to clear the significance level.

### 2.2 P2 is also an intersection–union test — treated the same way, for consistency
TOST (§2.3 of V4/V5) already requires *both* one-sided nulls (H0_upper, H0_lower) to be rejected to conclude equivalence — it is structurally the same kind of compound test as P1. For consistency, P2's combined p-value is defined the same way:

`p_P2 = max(p_upper, p_lower)`

where `p_upper` = proportion of bootstrap replicates with `mean(final_score(C1) − final_score(C2)) ≥ Δ`, and `p_lower` = proportion of bootstrap replicates with `mean(final_score(C1) − final_score(C2)) ≤ −Δ`.

### 2.3 Holm correction across the family {P1, P2}, stated as an exact procedure
With `p_P1` and `p_P2` as the two family members (m=2), at family-wise α=0.05:
1. Let `p_min = min(p_P1, p_P2)` and `p_max = max(p_P1, p_P2)`.
2. Test the hypothesis with `p_min` at level α/2 = **0.025**. If `p_min ≤ 0.025`, reject it.
3. Only if step 2 rejects: test the hypothesis with `p_max` at level α/1 = **0.05**. If `p_max ≤ 0.05`, reject it.
4. If `p_min > 0.025`, stop — neither hypothesis is rejected at the family-wise level, regardless of `p_max`.

This is the standard Holm step-down procedure, stated with its exact comparison values rather than described in general terms, so there is no ambiguity about what number a given result is compared against.

### 2.4 Consistency check performed on the directional definitions (re-verified, not re-asserted)
- P1-i: null `mean(e) ≤ 0`, alternative `mean(e) > 0`, rejection when the **5th percentile** of the bootstrap distribution of `mean(e)` exceeds 0 — correct for a one-sided lower-bound test (verified by construction: a one-sided (1−α) confidence bound of the form (L, ∞) with L at the α-th percentile; L > 0 ⟺ the p-value, the mass at or below 0, is < α).
- P1-ii: null `Δ_interaction ≥ 0`, alternative `Δ_interaction < 0`, rejection when the **95th percentile** of the bootstrap distribution is below 0 — correct for a one-sided upper-bound test, by the mirror-image argument.
- P2: both one-sided tests re-checked against V4 §2.3's statement; signs and percentiles used there are consistent with the p-value definitions in §2.2 above.

No sign or direction error was found on this re-check; §2.1–2.2 make the previously-implicit p-value definitions exact rather than changing them.

### 2.5 Reporting rule (explicit, was implicit before)
**Both P1-i's and P1-ii's point estimates and topic-clustered 95% CIs are reported in every case**, regardless of whether the Holm-adjusted compound test (§2.3) rejects. A non-significant compound result does not license omitting either component's individual estimate — the reader needs to see both to know *which* part of the compound claim didn't hold, not just that "the combined test failed."

## 3. Dampening ablation — sign, interpretation, and scope, made explicit

**Identical inputs, restated as a requirement, not just a description:** the damped and undamped `final_score` for a given item must be computed from the exact same stored `S1`, `S2`, `R`, `bonus`, and `penalty` values obtained from the single confirmatory scoring pass — never from two separate scoring calls. This is now listed as a pre-execution integrity check (§7 below), not only a design description.

**Unambiguous definition, restated:**
`g_i(X) = final_score_damped(X) − final_score_undamped(X)` for question *i*, category *X* ∈ {C1, C4}.
`Δ_interaction = mean_i[g_i(C4)] − mean_i[g_i(C1)]`

**Sign and interpretation, stated explicitly:** because dampening can only ever reduce `S2_eff` relative to raw `S2` (`0.6·S2 ≤ S2` always), `g_i(X) ≤ 0` for any item where dampening fires, and `g_i(X) = 0` where it does not. C1 items are **expected**, though **not guaranteed by construction** (R is a model output, not something the construction rules fix directly), to score `R > 0.30` and so not trigger dampening; C4 items are expected to score `R ≤ 0.30` and trigger it. Under that expectation, `Δ_interaction < 0` (a negative interaction) is the signature that dampening differentially suppresses keyword-stuffed answers relative to correct ones — the mechanism working as designed. `Δ_interaction ≈ 0` would mean dampening fires equally (or not at all) on both categories — evidence the mechanism does **not** differentially target keyword-stuffing specifically, whatever its overall effect. (V5's phrasing implied C1's R>0.30 was a construction guarantee; it is not, and this version corrects that overstatement.)

**Explicit scope limit, added per instruction — this is the most important addition in this section:** a result showing `Δ_interaction < 0` would be evidence that **dampening changes the relative scores of these specific constructed keyword-stuffed and correct answers** in the expected direction. It would **not** be evidence that **the complete evaluator accurately assesses arbitrary technical answers** in general — those are different claims, and the second is not established by this benchmark at all (it would require a validity study against real, organically-produced answers of unknown category, which is outside this design's scope, per V3–V5 §7/§9's standing limitations). This distinction is stated here explicitly so it cannot be blurred in the eventual manuscript.

## 4. Final consistency audit — actual numbers re-derived, one error found and fixed

Performed by recomputing, not by re-reading and re-trusting prior statements:

- **Eligible count and exclusions:** 122 of 125; qid 26, 39, 110 excluded (mandatory phrases too long to flatten cleanly) — re-verified against the original eligibility script's logic; unchanged, no error found.
- **Split:** development 6 topics / 26 questions; confirmatory 31 topics / 67 questions; cap-excess 29 questions. Arithmetic check: 26 + 67 + 29 = 122. ✓. Unchanged, no error found; use of the 29 is now restricted per §1.
- **Answer-variant counts — error found and corrected:** V4/V5 stated "8 distinct per-question analysis values." Recounting the actual categories (C1, C2-aggregated, C3-high, C3-low, C4, C5a, C5b, C6, C7) gives **9 distinct analysis values, not 8** — a plain miscount in the earlier versions, corrected here. The **item** count (10 constructed items per question, 670 confirmatory items total: 67 × 10) was correct and is unchanged; only the *distinct-analysis-value* label was wrong.
- **Primary/secondary hypotheses:** P1 (compound: P1-i, P1-ii), P2 (TOST, compound: upper/lower), M1 (manipulation check, not part of the corrected family) — consistent with §2's exact restatement; the S2 descriptive report (V5 §1) remains outside the hypothesis family, correctly.
- **Bootstrap and multiplicity:** B=5000, topic-resampling with full pooling of each resampled topic's data (valid under the 1-to-8 range of topic sizes and the 19 singleton topics, per V4 §8's argument, re-checked and still valid); Holm procedure now stated with exact comparison values (§2.3), where V5 only described the correction in general terms.
- **Category construction and validation:** re-checked against V4 §5's table — no new issue found; the C5a/C5b split and its lexical-overlap thresholds remain internally consistent with §3's requirement that they be evaluator-independent checks.
- **Manipulation-check stopping/remediation rules:** V4 §7's diagnose-don't-suppress rule and single-remediation cap re-checked — no inconsistency found; it interacts correctly with the topic-holdout fix in §1 (a remediated item must still come from within its own topic's already-assigned confirmatory or development pool, never from the now-excluded 29).
- **Generalization claims:** updated per §1 — now stronger (unqualified for all 31 confirmatory topics) rather than weaker, as a direct result of closing the leakage gap rather than merely disclosing it.

**No further mathematical inconsistency, leakage, or circularity was found in this pass beyond the count correction and the holdout-use restriction above.**

## 5. Everything else — unchanged, carried forward by reference

All construction rules, the C5a/C5b design, the eligibility criteria, the blind spot-check, the S2 descriptive-only treatment (V5 §1), and every standing limitation named in V4 §9 (single-team construction validation; project-internal, non-externally-validated margins where margins are used at all; unverified topic-taxonomy homogeneity) remain exactly as stated there and are not repeated in full here.

## 6. Concise final audit

**Ready for registration**, at the scope this document and its predecessors disclose. This pass found and fixed one real design flaw (the topic-holdout leakage risk, §1 — the most consequential fix, since it directly bore on the paper's central generalization claim), tightened the compound-test statistics from descriptive to exact (§2), corrected an overstated construction guarantee and added an explicit non-overclaiming boundary (§3), and fixed a genuine miscount caught only by recomputing rather than re-reading (§4). No further substantive issue was found on this pass.

**Remaining limitations, unresolved by design (not oversights, structural to the constraint of no new human-subject work):**
- Misconception falsity (C5b) still rests on the construction team's own domain judgment, checked by one blinded reader from the same organization.
- The paraphrase margin (0.10) is directly validated for `final_score` by this project's own metamorphic protocol, but that protocol itself reflects an internal engineering choice, not an externally validated practical-equivalence value.
- The `topic` field's semantic homogeneity in the source rubric bank is unverified.
- A positive P1 finding would show the dampening mechanism behaves as designed on these constructed categories — not that the evaluator is accurate on arbitrary real answers (§3, stated explicitly to prevent this specific overclaim).

## 7. Registration package

- **Protocol file (frozen):** `SYNTHETIC_EVALUATOR_BENCHMARK_PROTOCOL_V6.md`
- **SHA-256:** computed after this file was written — see chat response for the exact value (not embedded here to avoid a self-referential hash).
- **Proposed Git tag:** `prereg/D1-eval-synth/v1` (unchanged proposal from V5 — this is still the first registration attempt; V1–V6 are drafting history, not separate experiment versions).
- **Required run-manifest fields:** git commit at run time; evaluator/CrossEncoder checkpoint SHA-256 (expected `6a241a55…`, to be re-verified, not assumed, at run time); the frozen confirmatory question/topic list and its split seed (20260921); a separate, disclosed seed for the analysis bootstrap (fixed at registration, distinct from the split seed); date; operator; explicit confirmation of environment state relative to the pin-mismatch caveat (`EVIDENCE_AUDIT.md` §5).
- **Exact experimental commands (proposed — the scripts below do not yet exist and would be written and hashed at registration, before any scoring occurs):**
  1. `python research/paper_strengthening/scripts/d1_generate_items.py --split-seed 20260921 --out research/paper_strengthening/data/d1_confirmatory_items.jsonl` — renders the frozen 670 confirmatory items (and 260 development items) from the rubric bank per §3/§5 of V4, applying every automated construction-validity check and failing loudly on any item that doesn't pass.
  2. `python research/paper_strengthening/scripts/d1_score_items.py --items research/paper_strengthening/data/d1_confirmatory_items.jsonl --out research/paper_strengthening/results/d1_confirmatory_scores.jsonl` — the one and only model-inference step; calls the live, unmodified SBERT/FAISS/CrossEncoder pipeline once per item; **this is the step requiring approval**.
  3. `python research/paper_strengthening/scripts/d1_analyze.py --scores research/paper_strengthening/results/d1_confirmatory_scores.jsonl --analysis-seed <fixed at registration> --out research/paper_strengthening/results/d1_analysis_report.json` — pure arithmetic on already-obtained scores: the dampening-disabled recomputation (§3), the topic-clustered bootstrap, the exact p-values and Holm procedure (§2), and the S2 descriptive report (V5 §1). No model call.
- **Expected computational requirements:** unchanged from V5's estimate — under ~10 minutes, CPU-only, one machine, no GPU, no retraining (670 items at the project's own recorded median evaluator latency of 404.6 ms/call); the dampening-disabled recomputation in step 3 adds negligible time since it calls no model.
- **Pre-execution integrity checks (all to be confirmed before step 2 runs):**
  1. The frozen confirmatory item file's hash matches what is registered in the tag.
  2. A literal set-intersection check confirms **zero overlap** between the 29 excluded cap-excess question IDs and any question ID referenced in the development item file or any construction script's history (enforcing §1).
  3. 100% of frozen confirmatory items pass every automated construction-validity check (§5 of V4) — not a sample, the full set.
  4. The analysis code (step 3's script, including the Holm procedure and the dampening-disabled recomputation) is committed and hashed **before** step 2 is run.
  5. The evaluator checkpoint's SHA-256 at run time matches the recorded `6a241a55…`, confirmed, not assumed.
  6. The run environment's dependency versions are checked against the project's pins; any mismatch is logged in the run manifest rather than silently ignored.

Not executed: no item was generated, no model was called, no tag was created, nothing was committed or pushed.
