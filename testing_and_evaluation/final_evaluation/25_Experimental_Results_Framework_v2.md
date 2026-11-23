# 25. Experimental Results Framework v2 — Frozen Endpoint and Statistical Plan

**Status: FRAMEWORK ONLY — no experiment has been run, no data exists.** Supersedes-in-review document 21
(`21_Experimental_Results_Framework.md`), unmodified and preserved. This revision responds to the external
review's two central findings on document 21: the primary endpoint was not sufficiently specified, and the
statistical methodology needed significant strengthening before any confirmatory run.

---

## 1. Primary endpoint (frozen)

**Adopted: the reviewer's Option 1.** The primary endpoint is:

> **Blinded expert-rated technical evaluation quality** — the degree to which the system's numeric score and its
> stated justification (covered/missing/incorrect concepts) correctly reflect the technical correctness of the
> candidate's answer, as judged by a blinded expert rater against the scenario's independently-sourced expected
> outcome (per `23_Revised_Experimental_Proposal_v2.md` §5.2).

**Feedback quality is explicitly not part of the primary endpoint.** It is Category C below, reported as an
important, separately-analyzed secondary endpoint. Rationale, adopted directly from the external review: a
system can grade correctly while explaining poorly, or grade slightly less accurately while explaining
excellently; combining the two without a pre-justified weighting would let one dimension's result mask the
other's, and any weighting chosen after seeing which configuration performs better on each would be exactly
the kind of post-hoc endpoint selection this project's standing rules prohibit.

**Rubric requirement (must be piloted and frozen before the confirmatory run, per
`23_Revised_Experimental_Proposal_v2.md` §7.2):**
- Each scenario's technical-evaluation-quality rating uses a fixed anchor scale (to be defined during piloting,
  e.g. 1–5 with written anchors), applied identically by all raters.
- Inter-rater reliability (e.g. weighted kappa or ICC, chosen during piloting) must meet a pre-specified minimum
  before the rubric is considered frozen; if it does not, the rubric is revised and re-piloted, not loosened
  post hoc.
- Raters are blinded to which configuration (A or B) produced the output under review.

---

## 2. Metric categories (secondary endpoints), reported separately — never combined into one overall score

Per the external review's explicit requirement, the following categories are each reported on their own; no
composite "overall winner" score is computed across them. Categories A–H carry over from document 21 §1
(definitions unchanged; see that document for the full operational detail of each), with Category C now
explicitly scoped to exclude the primary endpoint's content (per §1 above). **Category I is new.**

- **A. Evaluation quality** — secondary detail metrics (consistency, misconception identification, partial-
  credit appropriateness) supporting but distinct from the primary endpoint itself.
- **B. Adaptive questioning.**
- **C. Feedback quality** — now explicitly the secondary endpoint carrying what was previously conflated with
  the primary endpoint; see §1.
- **D. Multimodal integration.**
- **E. Coding workflow** — including the mandatory REST `/api/run_code` end-to-end scenario from document 21
  §1-E, whose outcome remains reported separately from the architecture-comparison table per
  `23_Revised_Experimental_Proposal_v2.md` §6.
- **F. State management.**
- **G. End-to-end performance** — explicitly excluding "agent-coordination errors" as a named metric (no
  verified peer-to-peer coordination exists to fail).
- **H. Computational efficiency.**

### I. Software Engineering / Maintainability (new)

Added per the external review's closing point: if candidate-facing outcomes (Categories A–H) turn out to be
statistically indistinguishable between A and B, that is a legitimate, reportable finding — but any claim that
specialisation is "worthwhile anyway" must be backed by a measured engineering property, not asserted. Operational
definitions:

- **Change-locality / modification effort:** for a fixed set of representative maintenance tasks (defined before
  measurement, e.g. "add a new guardrail rule," "add a new feedback template for a new topic," "swap the
  evaluator's semantic-similarity threshold"), count the number of files touched and lines changed to implement
  each task correctly in Configuration A's existing structure vs. in Configuration B's consolidated structure.
- **Test isolation / unit-test coverage:** for the same components, the number of specialised components that
  can be unit-tested in isolation (with a mocked/stubbed dependency) vs. the number that require the full
  consolidated controller to be instantiated to test the equivalent logic.
- **Fault containment and recovery:** using the error-handling equivalence table
  (`24_Architecture_and_Baseline_Comparison_Specification_v2.md` §3), measure whether a deliberately injected
  fault in one component (e.g. a forced exception inside the feedback-construction call) propagates to or
  corrupts unrelated state, compared between A and B.
- **Complexity measures** (e.g. cyclomatic complexity per function/class, lines of code per responsibility) —
  reported descriptively and **interpreted cautiously**, explicitly not treated as proof of quality on their
  own, per the reviewer's own caution.
- **Time required to add a new capability without changing unrelated components:** for one or two representative
  new-capability tasks (e.g. "add a new modality signal to the state vector"), measure how many existing,
  unrelated components had to be touched in each configuration.

These are engineering-process metrics, not candidate-facing outcomes; they are reported in a separate results
subsection and are not combined with Categories A–H.

---

## 3. Historical results vs. new experimental results (unchanged, carried forward with its correction intact)

The §3.A/§3.B/§3.C structure, the corrected Fixed/Heuristic/PPO/PPO+guardrails MAE table and its source
attribution correction (`research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §D.2, not the architecture audit), and
the mandatory preserved limitation ("the heuristic is better than every PPO variant... the claim 'PPO improves
tracking' is withdrawn") all carry over **unchanged** from `21_Experimental_Results_Framework.md` §3. The
external review specifically endorsed this section ("extremely important... good research practice") and raised
no correction to it; it is not reproduced in full here to avoid drift between two copies of the same frozen
table — see that document.

---

## 4. Statistical methodology (fully specified, per the external review's requirement table)

| Requirement | Specification |
|---|---|
| Primary estimator | Paired difference, Configuration A minus Configuration B, on the primary endpoint (§1), per scenario/persona pair |
| Statistical unit | Persona (consistent with `CLAUDE.md`'s existing Paper 3 convention) |
| Repeated runs | Nested within persona; a persona's repeated runs are not treated as independent samples — variance decomposition must separate between-persona and within-persona (repeated-run) variability |
| Confidence intervals | Bootstrap (case-resampled at the persona level, consistent with the project's existing bootstrap convention for the evaluator-correlation CI), at a confidence level fixed during piloting (e.g. 95%) and not changed afterward |
| Primary hypothesis | Exact comparison: the population mean paired difference (A − B) on the primary endpoint is zero, tested two-sided unless a one-sided, pre-registered directional hypothesis is separately justified before data collection |
| Multiple-comparison correction | Applied across all Category A–I secondary endpoints reported alongside the primary (e.g. Holm–Bonferroni or Benjamini–Hochberg, chosen during piloting and fixed before the confirmatory run) — the primary endpoint itself is not subject to this correction, since it is the single pre-registered test |
| Missing data | A scenario that neither configuration can complete (e.g. both hit the same infrastructure failure) is excluded from the paired analysis and reported separately as a shared limitation, not imputed |
| Failed runs | A scenario where **one** configuration fails while the other completes is **not** silently excluded — it is recorded as a reliability-category (G) data point and separately flagged for the primary-endpoint analysis's missing-data handling, decided during piloting (e.g. worst-case imputation vs. exclusion-with-disclosure) and fixed before the confirmatory run, not chosen per-scenario after seeing results |
| Effect size | Reported alongside every p-value for every endpoint — standardized mean difference or an equivalent, scale-appropriate measure for the primary endpoint's rubric scale |
| Equivalence | Not claimed for any endpoint unless a specific margin and methodology (e.g. TOST) are pre-specified for that endpoint before data collection; absent that, a non-significant paired difference is reported as "no detected difference at this sample size," not as equivalence |

**Order/execution-effect control:** per `23_Revised_Experimental_Proposal_v2.md` §7.3, execution order is
counterbalanced/randomised, not fixed; this is a design requirement, not a statistical correction, and is
listed here only to confirm the statistical plan assumes it.

**Sequencing, restated from `23_...v2.md` §7.2:** the pilot study that estimates paired-difference variability
for the sample-size calculation must be run and analyzed **before** the confirmatory primary-endpoint analysis
is locked; the confirmatory analysis is then run once, on the full, pre-registered design, without adjustment
after seeing its own result.

---

## 5. Comparison-table templates (unchanged structure, now explicitly tied to the frozen plan above)

The §3.B (new architectural-comparison results) and §3.C (decision-component ablation) table templates from
`21_Experimental_Results_Framework.md` carry over unchanged, with every cell still marked **Pending**, plus one
addition: a new template row set for Category I (maintainability), equally marked Pending, to be populated only
after Stage 4 execution (`23_Revised_Experimental_Proposal_v2.md` §9) is explicitly approved and run.

| Metric | Existing architecture (A) | Single controller (B) | Difference | 95% CI | Statistical result |
|---|---|---|---|---|---|
| Change-locality effort (tasks, mean files touched) | **Pending** | **Pending** | **Pending** | **Pending** | **Pending** |
| Test isolation (components independently unit-testable) | **Pending** | **Pending** | **Pending** | **Pending** | **Pending** |
| Fault containment (injected-fault propagation rate) | **Pending** | **Pending** | **Pending** | **Pending** | **Pending** |
| Time-to-add-capability (representative tasks) | **Pending** | **Pending** | **Pending** | **Pending** | **Pending** |

No cell in any table in this document or its predecessor may be populated except by running the approved,
staged experiment described in `23_Revised_Experimental_Proposal_v2.md` §9 and recording its actual output.
