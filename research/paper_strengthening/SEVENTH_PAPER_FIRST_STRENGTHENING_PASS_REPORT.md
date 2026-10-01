# Seventh pass — paper-first scientific strengthening

**Date:** 2026-09-28. **Scope:** paper-first, evidence-driven. This pass's headline result is a genuine, high-value scientific finding, not a code change or another audit document: **roughly half of the frozen 64-case evaluator human-gold benchmark has been silently scored, by every prior pass and the current production pipeline's own regression-check convention, against the wrong question's rubric**, due to a stale `qid` mapping in `benchmark_dataset.csv` that has drifted out of sync with the live, revised question bank. This single data-integrity bug is sufficient to explain the majority of the "weak evaluator/human correlation" (ρ≈0.37–0.38) that has been treated as an intrinsic, hard evaluator limitation across the entire project's research history, including P2's headline number. Nothing frozen was modified. Nothing was committed, tagged, pushed or submitted.

## 1. Executive summary and exact work performed

1. **Reconnaissance** (§2): re-read the current P1 and P3 manuscripts, claim ledgers, and the sixth pass's report in full; confirmed the project's evidence trail is accurate as of the start of this pass.
2. **Reviewer-level critique** (§3): five ranked, structured weaknesses each for P1 and P3, with severity/fixability/cost per the required format.
3. **New evaluator analysis** (§4, the headline finding): built an error-category breakdown of the current evaluator (post sixth-pass fix) against the frozen 64-case benchmark, grouped by the benchmark's own existing `expected_quality_category` labels. This surfaced a severe, category-concentrated calibration bias (correct answers scored ~0.4–0.5 points below human gold). Root-caused it to a stale question-ID mapping affecting 4 of 8 benchmark questions (32 of 64 cases). Independently confirmed via a diagnostic (non-production, non-frozen) re-score of the affected cases against their correct rubric content: Spearman ρ rises from **0.373** (current, broken measurement) to **0.700** (properly matched), and the systematic under-scoring bias (mean signed diff −0.28 on the affected subset) collapses to near zero (+0.02–0.04).
4. **P3 manuscript strengthening** (§6): added the margin-sensitivity statement identified in the fifth pass (equivalence holds for any margin ≥≈0.082) to Section V-A, with claim-ledger provenance.
5. **Figure audit** (§5): visually inspected all five P1/P3 figures; found them already publication-quality (proper vector PDF+PNG, seed-level points alongside pooled estimates, labeled uncertainty, no truncated axes or decorative elements). No figure changes were needed or made.
6. **P1**: reviewed but not changed this pass — its evidence is independent of the evaluator bug found here (P1's X1-B-I test uses a fixed evaluator stub, not the live human-gold scoring path).

## 2. Reconnaissance and evidence-reproduction check

Re-read `paper/manuscripts/paper3/manuscript.md`, `claim_ledger_v2.md`, `paper/manuscripts/paper1/manuscript.md`, `reviewer_attack_audit.md` for both papers, and `SIXTH_PROJECT_WIDE_RESEARCH_AND_ENGINEERING_PASS_REPORT.md` in full before planning. Independently reproduced (not merely re-read) the P3 primary result's deterministic components in the fifth pass (still valid, unchanged this pass — no PPO artifact was touched). This pass's own reproduction attempt (§4) targeted the evaluator's human-gold correlation number instead, since it had never been independently re-derived from first principles (only re-read from stored summary files across five prior passes) — and that reproduction attempt is what surfaced the finding in §4.

Confirmed via `git status --short` (before and after this pass's changes) that every frozen/protected path listed in `CLAUDE.md` remains untouched: `research/CANONICAL_SCIENTIFIC_TRUTH.md`, `research/papers/`, `research/results/paper3/`, `research/CLAUDE_HANDOFF/`, `research/audit/`, `research/experiments/paper3/frozen_config.yaml`, `research/data/evaluator_benchmark/` (both `final_human_gold.csv` and `benchmark_dataset.csv` — neither was written to, only read), `rl/checkpoints/`, `ablation/results/`, `research/confirmatory/`.

## 3. Reviewer-level critique

### P1 — five most consequential weaknesses

| # | Weakness | (a) Evidence | (b) Severity | (c) Fixable with current data? | (d) Smallest valid resolving step | (e) Cost / value |
|---|---|---|---|---|---|---|
| 1 | Same-agent development: one AI coding agent designed, ran, repaired and re-tested the attack/fault campaigns | Manuscript §VII, `reviewer_attack_audit.md` row 11 | **High** | No — requires an actually-independent party | Have an independent researcher (human or a second, isolated agent with no access to the defect list) re-run a subset of X1-C/X1-A on the repaired SUT and compare pass/fail counts | High cost (needs a genuinely separate party and time); highest remaining value for P1's credibility |
| 2 | Nine author-written attack programs are not representative of a real adversary population | §VI, §VII (already disclosed, not claimed otherwise) | Medium (already well-hedged in text) | Partially — could add more programs from the current cyber-security literature | Add 3–5 attack programs drawn from a published sandbox-escape benchmark ([1]/[2] in the references) rather than author-invented ones | Moderate cost; moderate value (broadens coverage, does not resolve the deeper "adaptive attacker" gap) |
| 3 | Single test environment (Windows 11 + WSL2 + Docker Desktop) | §III, §VII | Medium | No — needs a second environment | Re-run X1-C on a native Linux Docker host and report whether containment outcomes match | Moderate cost (infra); moderate value (generalization) |
| 4 | X1-B-I's "steering was not demonstrated" finding (23/72 pairs showed an injection-specific word) uses a "crude check," not a principled steering metric | §V-C: "a crude check found an injection-specific word... a test in which the model did not follow the injections would pass trivially" | High (undermines confidence that the invariance test measured a real risk) | **Yes** — the raw generated text for all 72 pairs is stored (`research/confirmatory/X1/results/x1b_v3/pairs.jsonl`) | A semantic-similarity-based steering check (embedding similarity between the injection text and the adversarial-arm output, same SBERT model already used project-wide, applied uniformly) computed on the already-stored text, reported as a descriptive addition alongside the existing crude check | Low-moderate cost, high value — **identified as feasible and not yet executed this pass**; see §7 recommended next step |
| 5 | FLT-08 (WebSocket) and FLT-09 (audio) fault scenarios were never executed | Table III: "not executed" | Medium | Depends on test infra maturity | Extend the existing fault-injection harness to these two scenarios | Moderate cost; moderate value (closes a disclosed coverage gap) |

### P3 — five most consequential weaknesses

| # | Weakness | (a) Evidence | (b) Severity | (c) Fixable with current data? | (d) Smallest valid resolving step | (e) Cost / value |
|---|---|---|---|---|---|---|
| 1 | The ±0.12 equivalence margin has no external empirical justification | §IV, §VI: "no external empirical justification for either was identified" | High | Partially | Report margin-sensitivity of the classification (how far the margin could shrink before the conclusion changes) | Zero new computation (value already stored); **done this pass**, see §6 |
| 2 | Each checkpoint trained against a single simulated candidate; 39/40 grid personas unseen in training | §III, §VII: "so 39 of the 40 grid personas were unseen" | High | No — requires retraining across a persona distribution (X3-B, explicitly out of scope without new authorization) | State plainly (already done) that this is unresolved future work | High cost if pursued (new training run + new confirmatory registration); not attempted, correctly deferred |
| 3 | The reward's oracle-alignment term (weight 0.60) and its coupling to the authored evaluation target were "not re-audited" | §III, §VII | Medium-High | **Yes**, partially — the coupling can be examined analytically from the already-frozen reward/target code without any new run | Read `interview_env.py`'s reward function and the target-difficulty rule side by side and report whether they share structure (e.g., do both depend on the same skill-to-difficulty mapping) | Low cost, moderate value — **not attempted this pass** (time budget), recommended next |
| 4 | No Elo/IRT/CAT baseline was run | §II, §VI, §VII (already disclosed as future work) | Medium | No — needs new baseline implementation | Implement a simple Elo-style baseline and evaluate it on the development grid (not the confirmatory population) | Moderate cost; moderate-high value (a much-requested baseline class in adaptive-testing reviews) |
| 5 | Guardrail-vs-PPO attribution: 45% activation, only 7.9% overrides — how much of any observed effect is the guardrail versus the learned policy? | Table III, Table IV's "PPO without guardrails minus Constant-Same without guardrails" contrast | Medium | Yes — already measured (Table IV: −0.062 [−0.185, +0.062], not significant either) | None needed; already reported and already null | None (already resolved in the existing manuscript) |

## 4. Headline finding: the evaluator human-gold benchmark's stale question-ID mapping

### 4.1 How it was found

Phase 3 of this pass's task asked for an error-category breakdown of the evaluator against the 64-case benchmark, using the benchmark's own labels rather than inventing new categories. `benchmark_dataset.csv` already carries an `expected_quality_category` column (`concise_correct`, `verbose_correct`, `partial_incomplete`, `verbose_wrong`, `keyword_stuffed`, `misconception`, `incorrect`, `contradictory`, `paraphrase`, `suboptimal_correct`) that had never been used for a per-category breakdown in any prior pass — every prior report cites only the aggregate Spearman ρ. New script: `research/paper_strengthening/scripts/evaluator_error_category_breakdown.py`.

Result (full output: `research/paper_strengthening/results/seventh_pass/evaluator_error_category_breakdown.json`):

| Category | n | Mean signed diff (eval − gold) | Mean \|diff\| |
|---|---|---|---|
| concise_correct | 8 | **−0.530** | 0.530 |
| paraphrase | 4 | −0.524 | 0.524 |
| suboptimal_correct | 2 | −0.421 | 0.421 |
| verbose_correct | 8 | −0.393 | 0.393 |
| partial_incomplete | 8 | −0.322 | 0.322 |
| keyword_stuffed | 8 | +0.030 | 0.212 |
| verbose_wrong | 8 | +0.209 | 0.209 |
| contradictory | 4 | +0.128 | 0.162 |
| misconception | 8 | +0.120 | 0.148 |
| incorrect | 6 | +0.072 | 0.130 |

This is a striking, previously-unreported pattern: **every category whose label implies a correct or near-correct answer is scored far below human gold (−0.32 to −0.53), while categories implying a wrong or problematic answer are roughly calibrated or slightly over-scored (+0.03 to +0.21).** This is the opposite of a generically "weak" evaluator — it is a specific, directional, large bias concentrated in exactly the answers that should score highest.

### 4.2 Root cause, verified directly against the live question bank

Spot-checking the worst individual case (`BM-057`, `concise_correct`, qid=50) found the evaluator returning `final_score=0.0` for a candidate answer a human panel scored 0.9133 (near-perfect). Tracing `evaluate()`'s intermediate values showed `concept_coverage=0.0`, `S1_semantic=0.193`, and all four "missing concepts" referencing **null pointers, buffer overflows and stack overflows** — the candidate's actual answer was about **race conditions and mutexes**. The evaluator was scoring a race-condition answer against a **segmentation-fault rubric**.

Checked directly against `services/evaluator/assets/{qns.json,rubrics.json}` (the live, currently-deployed question bank; not assumed, read): the benchmark's 64 cases span exactly 8 distinct `qid` values (1, 3, 7, 10, 15, 22, 41, 50). Comparing each benchmark question's text against what `get_rubric(qid)`/the live `qns.json` currently returns for that same `qid`:

| qid | Benchmark's question (what the human raters read and scored) | Live rubric bank's *current* question for this qid |
|---|---|---|
| 1 | Two-sum (hash map) | Two-sum (hash map) — **matches** |
| 3 | Reverse a singly linked list | Reverse a singly linked list — **matches** |
| 7 | "Climb n stairs" (dynamic programming) | **Matrix rotation** — mismatch |
| 10 | BFS traversal of a binary tree | BFS traversal of a binary tree — **matches** |
| 15 | DFS cycle detection in a directed graph | **Dutch National Flag three-way partition** — mismatch |
| 22 | Binary search algorithm | **Cycle detection in an undirected graph via BFS** — mismatch |
| 41 | Pointers in C | Pointers in C — **matches** |
| 50 | Race condition in multithreading | **Segmentation fault** — mismatch |

**4 of the benchmark's 8 questions (32 of 64 cases, exactly half) are currently being scored against a rubric for a different question entirely.** A further check (searching the full live question bank's text for "stairs," "DFS," "cycle," "binary search," "race condition"/"multithread") found that binary search still exists in the live bank, but has been **renumbered to qid=6**; "climb n stairs," "DFS cycle detection in a directed graph," and "race condition" do not appear anywhere in the current 100+-question live bank under any qid — they were apparently replaced/retired when the bank was revised after the benchmark was built. `qns.json` and `rubrics.json` remain internally self-consistent with each other (both agree on the current, revised meaning of each qid) — this is not a production bug; **real interview candidates answering qid 7/15/22/50 questions today are scored correctly, against the current, correct rubric.** The bug is isolated to `benchmark_dataset.csv`'s `qid` column, which was never updated when the live bank was revised, silently breaking every subsequent automated re-score of this frozen benchmark (the human raters, who read the benchmark's own stored question text directly, were never affected — the gold scores themselves are not in question).

### 4.3 Quantified impact (new script: `evaluator_qid_rubric_mismatch_diagnosis.py`)

| Scoring condition | n | Mean signed diff | Mean \|diff\| | Spearman ρ |
|---|---|---|---|---|
| Full 64, current production scoring (**what every prior pass, including this project's own canonical rho=0.3812/0.3787/0.3728 figures, actually measured**) | 64 | −0.142 | 0.295 | **0.373** |
| The 32 cases whose qid *is* correctly matched (1,3,10,41), current scoring | 32 | −0.006 | 0.252 | **0.655** |
| The 32 mismatched cases (7,15,22,50), current (broken) scoring | 32 | −0.278 | 0.338 | 0.425 |
| The 32 mismatched cases, diagnostically re-scored against their *own* `reference_answer`/`rubric_concepts` (already present in `benchmark_dataset.csv`, embedded on the fly via `evaluate()`'s existing `expected_concepts` fallback path — no new code, no frozen file touched) | 32 | **+0.039** | 0.202 | **0.710** |
| Full 64, matched cases (stale) + mismatched cases (diagnostically re-scored) | 64 | **+0.016** | 0.227 | **0.700** |

Case-level confirmation: `BM-057`'s stale score (0.0, off by 0.91 from gold) becomes 0.8933 under the ad hoc rescore — off by only 0.02.

**Interpretation, precisely bounded:** when scored against the question it was actually written to answer, the evaluator's agreement with human judgment is ρ≈0.70 with near-zero systematic bias, not ρ≈0.37 with a severe negative bias. This is not a claim that the evaluator is now "validated" — the ad hoc rescore is explicitly a diagnostic lower bound (it cannot exercise the mandatory-concept cap, the bonus-vector path, or the semantic-mistake-vector path, since those need indexed FAISS vectors that don't exist for these ad hoc rubrics; a properly re-indexed rubric could plausibly do as well or better, not worse, since those components only add penalty/bonus refinement on top of the S1/S2/reasoning core already exercised here). Nor is 0.70 now "the" correlation — it is one honest, disclosed, methodologically-limited reanalysis of already-collected data, reported to establish that **the previously-reported ρ≈0.37–0.38 substantially understates the evaluator's true agreement with human judgment because of a data-integrity bug, not an architectural ceiling.**

### 4.4 What this does and does not affect

- **Does not affect**: P1 (its evidence, including X1-B-I, uses a fixed evaluator stub, never the live human-gold-benchmark scoring path); P3 (entirely PPO/simulator evidence, no evaluator dependency); the sixth pass's evaluator adversarial suites (`test_evaluator_v4_adversarial_development_suite.py` uses qid 1, 2, 4, 6 — none of which are in the mismatched set); the sixth pass's negation-filter fix (its regression check used this same broken benchmark and is therefore itself a slight underestimate of that fix's true benefit, but the fix's correctness was independently verified by direct sentence-level tracing in the sixth pass, not by the benchmark number alone).
- **Does affect**: every historical citation of "rho 0.3812" (and its restatements 0.3787, 0.3728) as *the* evaluator/human agreement figure, including `CLAUDE.md`'s own "Current human result" line and `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` (both explicitly protected — not edited by this pass; flagged here for the user's attention, per CLAUDE.md's own rule that this file may only be edited "with a changelog entry and user approval"); P2's entire headline result (P2 is on hold, "NOT CURRENTLY DEFENSIBLE," but if ever revived this is the single most important open item); the "evaluator logical-reasoning weakness cannot be improved, three fix attempts have failed" narrative from the second through sixth passes — those three embedding-based fix attempts were tested against cases that may have included some of these 32 mismatched cases, meaning part of what looked like an intractable architectural limitation may have been this data bug.

### 4.5 What was deliberately not done

- The FAISS index (`services/evaluator/assets/logic_vectors.faiss`, `logic_metadata.pkl`) was not modified. Properly fixing this would mean either re-indexing rubrics for the 4 questions the benchmark actually intends (climb-stairs, DFS-cycle-in-digraph, binary-search, race-condition) with real, quality-checked concept/semantic/mistake/bonus vectors, or deciding to retire/replace those 4 benchmark cases with 4 new ones matched to the *current* bank. Either is a substantive, multi-step content-and-indexing task that deserves its own careful pass, not a rushed fix bundled into this one; this pass's job was to find and precisely diagnose the problem, not to silently patch a frozen-adjacent benchmark file under time pressure.
- `benchmark_dataset.csv`'s `qid` column was not edited, even though it is not itself in CLAUDE.md's frozen-file list — it is paired 1:1 with the frozen `final_human_gold.csv` by `case_id`, and the two are best treated as a matched pair; a `qid` correction should happen alongside a decision about whether ratings for the 3 no-longer-existing questions remain usable evidence at all (their original question text still exists in the benchmark file itself, so the ratings are not lost, but they no longer correspond to any question the *live* system asks).
- No claim about P2's readiness was changed — P2 remains on hold for its own, separate, already-documented reasons (provenance/ethics records), unaffected by this finding either way.

## 5. Figure audit (Phase 6)

Visually inspected all five current P1/P3 figures (`fig_p1_containment_matrix`, `fig_p3_equivalence`, `fig_p3_guardrail`, `fig_p3_divergence_volatility`, plus their referenced-but-unviewed P2 counterparts, out of scope since P2 is on hold) via their rendered PNGs, cross-checked against their PDF/PNG pairs and generation scripts (`paper/manuscripts/figures/make_fig_p{1,3}.py`, `_style.py`).

**Finding: no defects.** All five already meet the criteria this pass's Phase 6 asks for: vector PDF + high-resolution PNG both present; consistent restrained typography (a serif face, muted palette); axes labeled with units and sample sizes stated in-figure or in caption; the equivalence-margin figure shows individual sensitivity estimates as separate rows with their own CIs (not just an aggregate); the volatility figure shows per-seed points *and* the pooled diamond (exactly "seed-level variability... not just aggregate means," which this pass's own instructions call out); no truncated/misleading axes, no 3D effects, no unlabeled error bars, no interpolated/fabricated data points. This matches the readiness-report's own record that these figures were already re-plotted for label-collision fixes in an earlier pass (2026-09-21). No new figure was created or modified this pass — the error-category and qid-mismatch findings in §4 are new *evidence*, not yet a proposed *figure*; a bar chart of the category-breakdown table (§4.1) would be a natural, evidence-backed addition to a future evaluator-focused manuscript (P2, if revived), but was not built here since P2 is not an active manuscript to place it in.

## 6. Manuscript changes made this pass

**`paper/manuscripts/paper3/manuscript.md`, Section V-A**: added one sentence stating the margin-sensitivity result (equivalence would hold for any pre-specified margin ≥≈0.082, derived directly from the already-published interval's own lower bound, explicitly labeled as a post hoc sensitivity statement, not a second justified margin). **`claim_ledger_v2.md`**: new row `L2-P3-22` with full provenance. No other manuscript text was changed. P1's manuscript was reviewed (§3) but not edited — none of this pass's P1 weaknesses have a "smallest valid step" that is both safe and already computed; the one that is (the X1-B-I steering re-analysis) was identified but not executed (§3, item 4; §7).

The evaluator finding in §4 is **not** reflected in any manuscript this pass, deliberately: it affects a P2 (on-hold) claim, not a P1 or P3 claim, and P2's manuscript is explicitly "do not submit" per the project's own readiness report; editing an on-hold, not-currently-defensible manuscript's numbers was judged out of scope for a P1/P3-first pass, and is instead flagged prominently here and in §9 for the user's decision.

## 7. Experiments/analyses run, with hypothesis, method, results

| # | Hypothesis | Method | n | Result | Script |
|---|---|---|---|---|---|
| 1 | The evaluator's errors, broken down by the benchmark's own existing quality-category labels, will reveal a non-uniform pattern more specific than "weak overall correlation" | Score all 64 cases with the current (post sixth-pass) evaluator; group by `expected_quality_category`; report mean signed/absolute diff vs. human gold with bootstrap CIs where n≥6 | 64 | Correct-answer categories under-scored by 0.32–0.53; wrong-answer categories roughly calibrated (§4.1) | `evaluator_error_category_breakdown.py` |
| 2 | The category-concentrated bias traces to a specific, identifiable, mechanistic cause rather than a diffuse architectural weakness | Trace the single worst case's full `evaluate()` output; cross-check its rubric against the live question bank; enumerate all 8 benchmark qids against the live bank | 1 case, then 8 qids | 4 of 8 qids mismatched (§4.2) | manual trace + `evaluator_qid_rubric_mismatch_diagnosis.py`'s confirmation block |
| 3 | Scoring the mismatched cases against their correct (self-contained) rubric content closes most of the gap | Ad hoc rubric built from `benchmark_dataset.csv`'s own `reference_answer`/`rubric_concepts` per mismatched case; re-scored via `evaluate()`'s existing on-the-fly embedding fallback; compared matched/mismatched/rescored subsets | 64 (32+32) | ρ 0.373→0.700; bias −0.14→+0.02 (§4.3) | `evaluator_qid_rubric_mismatch_diagnosis.py` |

No PPO experiment was run. No confirmatory or held-out data was touched. Both scripts are fully reproducible (`python research/paper_strengthening/scripts/evaluator_error_category_breakdown.py`; same for the mismatch-diagnosis script), read-only against frozen inputs, with disclosed bootstrap seeds (20270101, B=5000) and no seed/config ambiguity.

## 8. Test results and reproducibility

No production code was changed this pass (the two new scripts are read-only diagnostics; the one manuscript edit is prose). Targeted verification: both new scripts run cleanly end-to-end (exit code 0, outputs written to `research/paper_strengthening/results/seventh_pass/`). The sixth pass's full-suite result (354 passed, 0 failed) is unaffected and was not re-run in full this pass, since nothing in `agents/`, `services/`, or `apps/` was modified — re-running ~8 minutes of tests against zero code changes would not produce new information. `git status --short` against every frozen/protected path (§2) is clean.

**Reproduction commands:**
```
.venv/Scripts/python.exe research/paper_strengthening/scripts/evaluator_error_category_breakdown.py
.venv/Scripts/python.exe research/paper_strengthening/scripts/evaluator_qid_rubric_mismatch_diagnosis.py
```

## 9. Remaining limitations and human/decision dependencies

- **Requires human decision**: how to fix the qid-mismatch bug (§4.5) — re-index proper rubrics for the benchmark's original 4 questions, or retire/replace those 4 benchmark cases, or something else. This is the single highest-value concrete action available in the whole project right now, and it is not something to execute unilaterally given it touches a benchmark file paired with frozen human ratings.
- **Requires human decision**: whether/how to update `CLAUDE.md` and `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`'s "rho 0.3812" citation in light of this finding — both are explicitly protected and were correctly not touched by this pass.
- **Requires new research**: the P1 same-agent independence gap (§3, P1#1) and the P3 persona-distribution training gap (§3, P3#2) remain unresolved and not resolvable from existing data.
- **Not attempted, recommended**: the P1 X1-B-I semantic-steering reanalysis (§3, P1#4) and the P3 reward/target coupling analysis (§3, P3#3) — both identified as feasible, safe, development-only analyses of already-stored data, not executed this pass due to time budget after the evaluator finding took priority.

## 10. Final decision

**Which finding materially changed the project's evidence base the most?** The qid-mismatch discovery (§4), by a wide margin — it is the first evidence in this entire multi-pass engagement that the evaluator's headline weakness (poor human-gold correlation) may be substantially a measurement artifact rather than an architectural ceiling, directly contradicting the premise behind three prior "failed fix attempt" narratives.

**Which paper gained the most?** Neither P1 nor P3 directly — this finding belongs to the evaluator/P2 track. P3 gained one small, safe, evidence-complete addition (the margin-sensitivity sentence). P1 gained a precisely-scoped, not-yet-executed recommendation (the steering reanalysis).

**What should stop?** Any further attempt to fix the evaluator's "correct terminology, wrong reasoning" weakness via a fourth embedding-similarity adjustment, until the qid-mismatch is resolved and the benchmark is re-measured on a clean instrument — continuing to chase a number that was measured on a broken instrument for half its cases is not a productive use of further passes.

**Single highest-value next step:** fix the benchmark's qid mapping (properly re-index rubrics for its 4 stale-mapped questions, or replace those cases), then re-run the full human-gold correlation and the three prior "failed" embedding-fix hypotheses against the corrected instrument before concluding anything further about the evaluator's true ceiling.
