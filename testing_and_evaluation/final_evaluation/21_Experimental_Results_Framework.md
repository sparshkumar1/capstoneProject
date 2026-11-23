# 21. Experimental Results Framework

**Status: FRAMEWORK ONLY — no experiment has been run, no data exists.** This document defines metrics,
separates existing historical results from the (not-yet-collected) new comparative results, provides the
comparison-table template, and outlines the Results/Discussion structure the eventual report must follow.
Every table below contains either real, cited historical numbers (clearly labeled as such and not related to
the new research question) or placeholder cells explicitly marked **Pending**. Nothing has been fabricated,
estimated, or illustratively populated.

---

## 1. Metric definitions (operational)

### A. Evaluation quality
- **Expert-reference agreement:** correlation (Spearman ρ, with bootstrap CI) between blinded expert ratings and
  system output, computed per-configuration against the same reference set.
- **Evaluation correctness:** binary/graded agreement between system-assigned grade and rubric-derived ground
  truth per scenario.
- **Consistency:** variance in system score across repeated presentations of the same answer (stochastic-run
  repeats).
- **Misconception identification:** recall/precision of flagged misconceptions against the rubric's known
  misconception list (cf. `FeedbackAgent._MISCONCEPTIONS`, `feedback_agent.py:33-60`, for the existing
  architecture's own reference list — Configuration B must be evaluated against the same list, not a different
  one).
- **Partial-credit appropriateness:** rubric-defined expected partial score vs. system output, per scenario.

### B. Adaptive questioning
- **Question relevance:** rubric/expert judgment of topical fit to candidate state.
- **Difficulty alignment:** |assigned difficulty − rubric-expected difficulty| per turn.
- **Difficulty progression:** trajectory shape over a full session vs. an expected progression curve for the
  scenario's scripted persona.
- **Adaptation appropriateness:** whether a difficulty change direction (Easier/Same/Harder) matches the
  scenario's documented expected direction.

### C. Feedback quality
- **Technical correctness:** rubric-checked factual accuracy of feedback content.
- **Specificity / actionability / usefulness:** blinded expert Likert ratings (1–5), rubric anchors defined
  before rating begins.
- **Consistency with evaluation evidence:** feedback claims must not contradict the evaluator's own
  covered/missing-concept lists (an automatable check, not requiring a human rater).

### D. Multimodal integration
- **Correct use of speech evidence:** does confidence/hesitation signal appear in the final observation/feedback
  as expected for the scripted audio scenario?
- **Correct integration of verbal and speech information:** cross-check between `last_confidence_score` and the
  6-D PPO observation's `conf`/`hes` components (`hybrid_orchestrator.py:100-114`).
- **Conflicting-signal handling:** scripted scenarios where delivery confidence and technical correctness
  disagree — does the system avoid conflating them (e.g. scoring a confidently-delivered wrong answer as
  correct)?
- **Preservation of source evidence:** does a later turn's state carry forward a prior turn's `last_confidence_
  score`/`last_hesitation_score` without being overwritten by an unrelated turn type (the exact property the
  known, separately-tracked `test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics` issue
  concerns — see `CLAUDE.md`'s "known gotchas"; this benchmark axis will likely reproduce that same pre-existing
  finding in Configuration A, and it must be reported as pre-existing, not as a new discovery of this study).

### E. Coding workflow
- **Compilation correctness, runtime correctness, test-case evaluation correctness:** rubric-defined expected
  outcome per scripted code submission vs. system `status`/`passed`/`tests_passed`/`tests_total`.
- **Error handling:** does a compilation/runtime/timeout/OOM scenario produce the correctly classified status
  (`coding_executor.py:359-378`)?
- **Sandbox security and execution behaviour:** confirmed by re-running the existing dedicated tests
  (`test_docker_network_isolation_blocked`, etc. — already verified passing in
  `testing_and_evaluation/final_evaluation/16_Docker_Verification_Report.md`); not re-litigated by this study,
  only re-confirmed as unchanged.
- **Mandatory benchmark item:** at least one scenario must exercise the full REST `/api/run_code` → WS
  `code_submission` path end-to-end for Configuration A, to runtime-test (not merely re-read) the static-
  inspection finding in `17_Architecture_Audit_Report.md` §5/§10 about `apps/backend/main.py:1360`'s
  `_current_question` lookup. The outcome of that specific scenario is an **integration-correctness finding**,
  reported separately from the Configuration-A-vs-B comparison table (§3 below), because it is a property of
  Configuration A's backend wiring, not of "specialised architecture" as a concept — Configuration B would need
  its own equivalent test-case-sourcing logic, and any difference found is a fairness/implementation detail, not
  evidence about orchestration value.

### F. State management
- **Candidate-state consistency / correct state transitions:** scripted multi-turn scenarios with known-correct
  expected state after each turn (same approach as the existing `tests/unit/test_stage11_5_coding_adaptation.py`
  suite, reused as a template, not modified).
- **Preservation of speech confidence / prior evidence:** see D above.
- **Cross-turn consistency:** `scores`/`answers`/`difficulty_history` arrays must each grow by exactly one entry
  per non-retried turn (the same invariant `_rollback_tentative_attempt` enforces in Configuration A,
  `interview_orchestrator.py:790-817`) — Configuration B must be checked against the identical invariant.

### G. End-to-end performance
- **Successful interview completion, task completion:** binary, per full-session scenario.
- **Integration errors, routing errors, state-handoff failures:** counted directly from logs/exceptions, not
  inferred.
- **Recovery from failures:** does a scripted evaluator/Docker/Qwen-unavailable scenario produce the documented
  fail-closed response in both configurations, or does Configuration B need its own equivalent fail-closed logic
  built in (a fairness requirement, not optional)?
- **Explicitly excluded:** "agent-coordination errors" as a named metric, per the Phase 1 finding (§2 of
  `19_Revised_Experimental_Proposal.md`) that there is no verified peer-to-peer coordination in Configuration A
  to fail.

### H. Computational efficiency
End-to-end latency (wall-clock per turn and per full session); per-component latency (evaluator call, Docker
round-trip, Qwen call, PPO inference — each independently timed); token consumption (Qwen prompt+completion
tokens per call); model inference cost (PPO forward-pass count, evaluator embedding calls); memory footprint;
failure/retry overhead (count and time cost of fallback paths triggered).

---

## 2. Primary and secondary endpoints

**Primary endpoint (recommended, not yet adopted):** blinded expert-rated overall interview-evaluation quality
(category A/C composite), using a rubric piloted and frozen before the comparative run. Adoption is contingent
on (a) rater availability being confirmed, and (b) the rubric achieving acceptable inter-rater reliability in a
small pilot — neither has been done.

**Secondary endpoints:** every other metric in §1 (B, D, E, F, G, H), reported individually, not combined into a
single composite score, per the instruction not to select or redefine endpoints after seeing results.

---

## 3. Historical results vs. new experimental results — mandatory separation

### 3.A Existing historical results (already collected, under their own prior methodology — not new evidence for this study)

**Difficulty-tracking comparison (Fixed / Heuristic / PPO / PPO + guardrails):**

| Condition | Tracking MAE | Volatility | Source |
|---|---|---|---|
| Fixed (d = 3.0) | 1.200 | 0.000 | `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §D.2, citing `paper3_baseline_results.csv` |
| Heuristic | 0.473 | 0.160 | same |
| PPO raw, seed 123 | 0.804 | 0.088 | same |
| PPO + guardrails, seed 123 | 0.673 | 0.088 | same |
| PPO + guardrails, five seeds | 0.677 (per-seed: 0.687 / 0.673 / 0.676 / 0.673 / 0.676) | 0.186 (per-seed: 0.268 / 0.088 / 0.208 / 0.240 / 0.128) | same |

**Correction to the task specification that supplied these numbers:** the specification this framework was
built from stated that "the architecture audit reports these existing difficulty-tracking MAE values." **This
was checked directly and is inaccurate — `17_Architecture_Audit_Report.md` contains no such table** (confirmed
by grep: zero matches for these values in that file). The table's real, correct, and verifiable source is
`research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §D.2 (frozen-verified), citing the underlying
`paper3_baseline_results.csv`/`paper3_seed_results.csv`/`paper3_summary_results.csv` data files. The numbers
themselves are reproduced accurately above; only their attributed source has been corrected. This is reported
here, rather than silently fixed, because `CLAUDE.md` and this task's own rules require traceable provenance for
every number and explicit disclosure of corrections.

**Mandatory limitation, carried over verbatim from the canonical source and not to be dropped when this table is
cited elsewhere:** *"The guardrails account for essentially all of the improvement over Fixed; the heuristic
(0.473) is better than every PPO variant. PPO's contribution under guardrails is not identified by the frozen
study. Claim 'PPO improves tracking' is withdrawn."* (`CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` line 77, finding
P0-2). Sample size, exact configuration details, and additional caveats (checkpoint-hash mismatch between the
deployed and evaluated PPO artifacts, noted at line 79 of the same file) are part of this historical record and
must be preserved wherever this table is reproduced.

**Why this table is not evidence for or against this study's research question:** it compares *difficulty-
decision mechanisms* (Fixed/Heuristic/PPO/PPO+guardrails) under simulated-candidate RL training/evaluation
conditions (`research/scripts/run_paper3_study.py`, `rl/training/simulated_candidate.py`). It says nothing about
*control architecture* (one orchestrator coordinating several specialised classes vs. one unified controller
class) — the actual variable in Configuration A vs. B (§4 of `19_Revised_Experimental_Proposal.md`). It is
directly relevant, however, to the optional **decision-component ablation** (Phase 7, same document, §9), where
it already answers the C1/C3/C4 comparison for the tracking-MAE metric specifically, under its own methodology —
and that reuse, and that reuse only, is legitimate.

**Other historical evidence categories** (reviewed for completeness, not reproduced in full here — each has its
own source document and should be cited from there, not restated and risk drifting from the original):
- Evaluator-vs-human-consensus correlation: `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §C.1/§C.2 (current
  result: 3 raters, 64 answers, rho 0.3812, CI [0.158, 0.577] — exploratory).
- Docker/coding-sandbox test verification: `testing_and_evaluation/final_evaluation/16_Docker_Verification_
  Report.md` (19/19 itemized Docker-dependent tests passing against a live daemon, this session).
- Architecture classification itself: `17_Architecture_Audit_Report.md`.

### 3.B New architectural-comparison results (Configuration A vs. B) — template only, nothing collected

| Metric | Existing architecture (A) | Single controller (B) | Difference | 95% CI | Statistical result |
|---|---|---|---|---|---|
| Expert evaluation agreement | **Pending** | **Pending** | **Pending** | **Pending** | **Pending** |
| Evaluation consistency | **Pending** | **Pending** | **Pending** | **Pending** | **Pending** |
| Question relevance | **Pending** | **Pending** | **Pending** | **Pending** | **Pending** |
| Difficulty alignment | **Pending** | **Pending** | **Pending** | **Pending** | **Pending** |
| Feedback quality | **Pending** | **Pending** | **Pending** | **Pending** | **Pending** |
| Multimodal integration | **Pending** | **Pending** | **Pending** | **Pending** | **Pending** |
| Coding correctness | **Pending** | **Pending** | **Pending** | **Pending** | **Pending** |
| State consistency | **Pending** | **Pending** | **Pending** | **Pending** | **Pending** |
| Interview completion | **Pending** | **Pending** | **Pending** | **Pending** | **Pending** |
| Latency | **Pending** | **Pending** | **Pending** | **Pending** | **Pending** |
| Computational cost | **Pending** | **Pending** | **Pending** | **Pending** | **Pending** |

**No cell in this table may be populated except by running the approved experiment and recording its actual
output.** This table exists so that the reporting structure is agreed before data collection, not so that it can
be filled in from expectation, prior belief, or illustrative example.

### 3.C Decision-component ablation results — template only, separate from 3.A and 3.B

| Condition | Tracking MAE (this study, new benchmark) | Source |
|---|---|---|
| C1 — PPO + guardrails | **Pending (not yet run on this study's benchmark)** | — |
| C2 — Guardrails only | **Pending** | — |
| C3 — Heuristic only | **Pending** | — |
| C4 — Fixed | **Pending** | — |

This table is deliberately **not** pre-filled with the §3.A historical numbers, even though C1/C3/C4 correspond
conceptually to rows already measured in that table, because §3.A's numbers were produced on a different
benchmark (simulated-candidate RL episodes) under a different methodology. Reusing them here without re-running
on this study's own benchmark would conflate two different experiments. If, after design review, the team
decides the existing Paper 3 benchmark *is* the appropriate benchmark for this ablation (rather than constructing
a new one), that must be an explicit, documented decision — not an implicit substitution.

---

## 4. Results and Discussion structure (to be filled in only after Phase 5 execution)

### Results (planned section order)
1. Benchmark and sample description.
2. Configuration equivalence assessment (the §3 checklist from
   `20_Architecture_and_Baseline_Comparison_Specification.md`, confirmed satisfied or documented as violated).
3. Primary endpoint comparison.
4. Secondary metric comparisons (A–H, excluding the primary).
5. Component-level results (e.g. evaluator agreement in isolation, Docker correctness in isolation).
6. End-to-end results.
7. Reliability and failure analysis.
8. Latency and computational cost.
9. Decision-component ablation results (§3.C).
10. Statistical analysis (§ per `19_Revised_Experimental_Proposal.md` §8).

### Planned visualisations (to be generated only from actual recorded results)
1. Grouped bar/box comparison of primary and secondary metrics, A vs. B.
2. Confidence-interval / effect-size forest plot.
3. Difficulty-progression trajectory comparison (A vs. B, per scenario persona).
4. Latency and computational-cost comparison.
5. Component-level comparison (evaluator/Docker/Qwen/PPO call breakdown).
6. Decision-component ablation visualisation (§3.C).

### Discussion (outline, not pre-written conclusions)
- Which configuration performed better, on which specific metrics.
- Which differences were statistically supported vs. only numerically different.
- Which differences were practically meaningful given effect size, independent of significance.
- Which specific components (if any) are identifiable as the source of an observed difference.
- Whether specialisation provided measurable benefit distinct from orchestration itself.
- Whether central orchestration alone (without multiple specialised classes) would have sufficed.
- Whether the additional architectural/computational complexity of Configuration A is justified by the
  magnitude of any observed benefit.
- Trade-offs observed (e.g. latency vs. quality, complexity vs. maintainability).
- What the experiment cannot establish (e.g. it cannot speak to a genuinely collaborative, peer-to-peer
  multi-agent redesign, since neither configuration implements one).

### Possible conclusions (all four remain genuinely open until data exists)
A. Existing specialised architecture demonstrates meaningful advantages.
B. Unified single-controller architecture performs similarly or better.
C. Different architectures perform better on different task categories (trade-offs, no universal winner).
D. Evidence is insufficient to establish a reliable difference.

No conclusion is selected, implied, or hinted at in this framework document. All four remain equally available
pending actual execution.
