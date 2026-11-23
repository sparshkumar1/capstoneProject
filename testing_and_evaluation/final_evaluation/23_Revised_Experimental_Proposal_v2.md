# 23. Revised Experimental Proposal v2 — Addressing the P0 External Review Findings

**Status: PROPOSED — NOT YET EXECUTED. Supersedes-in-review documents 19 (`19_Revised_Experimental_Proposal.md`)
and 18, neither of which is modified or deleted.** This document is a second revision, produced in direct
response to an external document/methodology review of documents 19–22 (reproduced in full in this
conversation; not re-derived from the repository). That review's verdict was explicit: **"Strong revision. Not
ready for experimental execution."** Every "P0 — resolve before experiment approval" item it raised is addressed
below by name. Nothing in Phases 2–8 has been implemented or executed. Configuration B does not exist as code.

---

## 1. What changed, and why (map to the external review)

| External review item | Where resolved in this document |
|---|---|
| P0-1: Freeze the primary endpoint | §2 adopts the reviewer's Option 1 (technical evaluation quality alone); full operational definition in `25_Experimental_Results_Framework_v2.md` §1 |
| P0-2: Define Configuration A/B equivalence precisely | §4 narrows the research question to what is actually tested; the full equivalence contract is in `24_Architecture_and_Baseline_Comparison_Specification_v2.md` §2 |
| P0-3: Independent ground truth (not `FeedbackAgent._MISCONCEPTIONS` as sole reference) | §5.2 |
| P0-4: Fix the confirmatory statistical plan | §7, with the full specification in `25_Experimental_Results_Framework_v2.md` §4 |
| P0-5: Separate architecture findings from pre-existing integration defects | §6 |
| P1-6: Make the experimental variable explicit (modularity vs. autonomy) | §2, §4 |
| P1-7: Control order/execution effects | §7.3 |
| P1-8: Specify benchmark instances with independent validation | §5 |
| P1-9: Coding/multimodal boundaries | §5.1, carried from document 19 unchanged (already correct per the review) |
| P1-10: Auditable run manifest | §7.4 |

---

## 2. Reframed research question (adopting the reviewer's formulation)

**Primary research question (revised, narrower):**

> Does a specialised, orchestrator-coordinated architecture provide measurable advantages over a unified
> single-controller architecture in evaluation quality, adaptive interview management, workflow reliability and
> computational efficiency, when both configurations have equivalent access to the same models, tools and
> underlying capabilities?

This replaces document 19's seven-item, broader investigation list as the primary driver of the experiment. The
seven original items (specialisation benefit, orchestration effectiveness, evaluation quality, adaptive
questioning, multimodal integration, workflow reliability, complexity justification) remain **secondary
research questions**, each with its own metric category in `25_Experimental_Results_Framework_v2.md`, but only
the reframed question above drives the single primary endpoint and the confirmatory statistical test. This
directly addresses the reviewer's point that investigating seven things in one comparative experiment with one
endpoint conflates questions that need separate answers.

---

## 3. Explicit statement of the experimental variable (P1-6)

Per the reviewer's correction, and consistent with the architecture audit's own finding (`17_Architecture_Audit_
Report.md`): **this experiment does not test whether autonomous agents collaborate better than a single agent.**
No verified autonomous peer-to-peer collaboration exists in Configuration A to begin with (§4.1 of
`19_Revised_Experimental_Proposal.md`, reaffirmed here). Configuration B does not remove capability; it
consolidates the same capability behind fewer, less-specialised control classes. The actual variable under test
is:

> **Modularity and component-boundary specialisation under central orchestration, versus consolidated,
> in-lined control logic over the same underlying models and tools.**

Every document in this package, and the eventual results/discussion, must describe the comparison in this
language. Neither "multi-agent" nor "single-agent" is an accurate label for either configuration.

---

## 4. Configuration A and B (unchanged in substance, equivalence now precisely specified elsewhere)

Configuration A and B retain the definitions in `19_Revised_Experimental_Proposal.md` §4 and
`20_Architecture_and_Baseline_Comparison_Specification.md`. What changes in this revision is that the
**equivalence contract is now a frozen, explicit checklist** rather than a narrative description — see
`24_Architecture_and_Baseline_Comparison_Specification_v2.md` §2, which specifies, functionality by
functionality, exactly how Configuration B must reproduce Configuration A's behaviour (including its one known
guardrail divergence from the canonical module, which must be preserved, not silently corrected, in both
configurations equally).

---

## 5. Benchmark design corrections

### 5.1 Coding and multimodal boundaries (P1-9, unchanged — already correct per review)

Carried forward unchanged from document 19 §5: coding execution and verbal evaluation remain two separate
scenario categories and two separate code paths in both configurations; speech-derived confidence/hesitation
signals are treated as measurable acoustic/linguistic features, never as a proxy for a candidate's actual
psychological state. The reviewer raised no objection to this boundary; it is restated here only so this
document remains self-contained.

### 5.2 Independent ground truth for misconception detection (P0-3)

**Problem identified by the reviewer:** `FeedbackAgent._MISCONCEPTIONS` (`agents/orchestrator/feedback_agent.
py:33-60`) is Configuration A's own implementation artifact. If this same dictionary is reused as the benchmark's
scoring key for "was the misconception correctly identified," Configuration A is graded against its own answer
key, which would bias the comparison in its favour before a single scenario is run.

**Resolution, adopted as a hard rule for this proposal:**

- The misconception taxonomy used to score **both** configurations' outputs must be authored **independently**
  of `FeedbackAgent._MISCONCEPTIONS` — by domain-expert review of the question bank and rubrics
  (`data/questions/qns.json`, `data/rubrics/rubrics_final_clean.json`), not derived from or cross-checked
  against the existing dictionary during authoring.
- `FeedbackAgent._MISCONCEPTIONS` may be consulted only *after* the independent taxonomy is frozen, as a sanity
  check that the independent list is not obviously incomplete relative to what the system already knows about —
  and any such cross-check must be logged (which items came from which source) so the provenance of every
  benchmark item is traceable.
- Every benchmark scenario's "expected outcome" field (per document 19 §5's schema) must record its **ground-
  truth source** explicitly: `independent-expert`, `existing-rubric` (for `data/rubrics/*`, which are not
  Configuration-A-specific), or `existing-dataset` (for `research/data/evaluator_benchmark/*`, likewise not
  Configuration-A-specific). No scenario may have `FeedbackAgent._MISCONCEPTIONS` as its sole or primary ground-
  truth source.
- This rule generalises beyond misconceptions: **any artifact that is part of Configuration A's own
  implementation (its guardrail thresholds, its specific heuristic formulas, its specific prompt templates) must
  not become the benchmark's ground truth**, for the same reason.

### 5.3 Guardrail rule itemization (P0-adjacent clarification)

The previous proposal's benchmark description ("G4, G1, G2, G3/G5, G6, plus the infrastructure-failure guard...
six documented rules") left the count ambiguous, as the reviewer noted. The complete, individually itemized list
— verified directly against the orchestrator's **live, private** guardrail implementation
(`agents/orchestrator/interview_orchestrator.py:1529-1573`), not the canonical `rl/guardrails.py` module, per the
critical distinction in §6 below — is:

| # | Rule | Exact condition (live orchestrator copy) | Action | Priority |
|---|---|---|---|---|
| 1 | G4 — critically struggling | `perf < 0.30 and hes > 0.60` | Easier | 1 (highest) |
| 2 | G1 — low performance at mid difficulty | `perf < 0.30 and 0.4 <= diff_norm <= 0.7` | Easier | 2 |
| 3 | G2 — low confidence + high hesitation | `conf < 0.30 and hes > 0.70 and perf < 0.80` | Easier if `hes > 0.85` else Same | 3 |
| 4 | G3 (live copy's boundary) — partial understanding | `0.40 < perf < 0.65 and avg_perf < 0.60 and consecutive_followups < 2` | Same | 4 |
| 5 | G6 — strong performer | `perf >= 0.90 and (perf - avg_perf) > 0.25 and not nervous_expert` | Harder | 5 |
| 6 | (fallthrough) — no rule fires | — | Pass through the proposed action unchanged | 6 (lowest) |

**Critical note, carried forward from `17_Architecture_Audit_Report.md` §3.3 and restated here because it
directly affects benchmark validity:** the live orchestrator's rule #4 boundary (`0.40 < perf < 0.65`) is the
**unfixed** boundary. The canonical `rl/guardrails.py` module (used only by the offline RL training/evaluation
path, not by live sessions) has a corrected boundary (`0.30 <= perf < 0.65`) and an additional infrastructure-
failure-protection rule that the live orchestrator's private copy does not implement at all. **The benchmark
must test the six rules exactly as the live orchestrator copy implements them** — this is what Configuration A
actually does during a real session — not the canonical module's (different, already-fixed) behaviour. Testing
the canonical module's rules would silently benchmark a system Configuration A does not run.

---

## 6. Separating architecture findings from pre-existing defects (P0-5)

Strengthened per the reviewer's explicit rules, adopted verbatim as binding constraints on how results may be
interpreted and reported:

1. **Pre-existing defects must be documented before the experiment runs**, not discovered and attributed
   retroactively. The two already-known candidates are the REST `/api/run_code` test-case lookup gap and the
   guardrail-boundary divergence above (both from `17_Architecture_Audit_Report.md`); any further pre-existing
   defect found during benchmark construction must be logged the same way, before any comparative run uses it.
2. **Both configurations must receive equivalent opportunity to execute the same workflow.** If Configuration
   A's known REST-path gap would prevent a scenario from completing, the same scenario must be run through
   Configuration A's WebSocket path (where the gap does not apply, per the original finding) so that the
   comparison is not accidentally testing "a known integration bug" instead of "the architecture."
3. **A defect found only in Configuration A must not, by itself, be reported as evidence that modular
   architecture is inferior.** It is evidence about that specific integration point, reported as such, separate
   from the architecture-comparison result.
4. **A defect avoided only because Configuration B happens not to have the equivalent code path (rather than
   because it was built more carefully) must be reported as an implementation difference, not an architectural
   advantage.** The same rule applies symmetrically to guardrail divergence, error-handling behaviour, and
   rollback/retry behaviour — covered precisely in the equivalence contract and error-handling table in
   `24_Architecture_and_Baseline_Comparison_Specification_v2.md` §2–§3.

---

## 7. Experimental execution corrections

### 7.1 Primary endpoint (P0-1)

**Adopted: the reviewer's Option 1.** The primary endpoint is **blinded expert-rated technical evaluation
quality** alone — not a combined evaluation-quality/feedback-quality composite. Feedback quality remains a
dedicated, separately reported secondary endpoint. Full operational definition, rubric requirements, and the
rationale for not combining the two: `25_Experimental_Results_Framework_v2.md` §1.

### 7.2 Sample size (unchanged principle, now sequenced correctly)

Document 19's refusal to propose an arbitrary sample size is retained. This revision adds the reviewer's
missing step explicitly: **a small, separate pilot study** — using the frozen primary-endpoint rubric on a
handful of scenarios, run on Configuration A only (Configuration B does not exist yet) — must estimate paired-
difference variability before any power/precision analysis is computed for the main comparative run. The pilot
is not itself the confirmatory experiment and its results are not used to select or adjust the primary
hypothesis.

### 7.3 Order and execution-effect control (P1-7)

**Correction to document 19 §7, item 1:** "both configurations receive identical benchmark scenarios, in the
same order" is revised. Scenario **content** and initial candidate state must be identical across configurations
for a given paired comparison, but:

- The **order in which Configuration A and Configuration B are run** for a given scenario/persona pair must be
  counterbalanced or randomised across the benchmark, not fixed (A always first).
- Each run must start from a **fresh, equivalent initial state** — no shared cache, no shared model-server
  session state, no shared Docker container reuse between a Configuration-A run and the immediately following
  Configuration-B run of the same scenario — to prevent order-dependent environmental effects (caching, server
  load, state leakage) from being mistaken for an architectural difference.

### 7.4 Auditable run manifest (P1-10)

Each individual run (one configuration, one scenario, one repetition) must record: configuration version
(commit hash of the harness code, not just "A" or "B"), model/checkpoint hashes actually invoked (PPO
checkpoint, Qwen model identifier, evaluator model artifacts), prompts sent, random seeds, execution
environment, scenario ID, raw output, timing per component, and every error/retry encountered. This is additive
to, not a replacement for, document 19 §7's existing requirements (identical scenarios, documented seeds, no
selective exclusion).

---

## 8. Engineering-benefit metrics (new, per reviewer's final point)

The reviewer's closing observation is adopted as a requirement, not an aspiration: if Configuration A and B
produce near-identical candidate-facing outcomes, that is not a failed experiment — it would indicate that
specialisation's value (if any) lies in engineering properties, not candidate-facing quality, and those
properties must be **measured**, not asserted. A new metric category (Category I — Software Engineering /
Maintainability) is added to the metrics framework; see `25_Experimental_Results_Framework_v2.md` §2-I for
operational definitions (change-locality effort, test isolation/coverage, fault containment and recovery,
complexity measures interpreted cautiously, time-to-add-a-capability).

---

## 9. Staged de-risking plan (replaces attempting everything in one pass)

Adopted from the reviewer's four-stage structure, mapped onto this proposal's existing phase numbering:

| Stage | Content | Maps to |
|---|---|---|
| **Stage 1 — Freeze the specification** | Research question (§2), equivalence contract (`24_...v2.md` §2), primary endpoint (§7.1, `25_...v2.md` §1), independent ground-truth process (§5.2), statistical plan (`25_...v2.md` §4), documented pre-existing defects (§6) | Phases 2, 4, 6 (design only) |
| **Stage 2 — Construct and validate the benchmark** | Scenario instances across the 17 categories, expert validation of expected outcomes, rubric piloting, variability estimation for sample size (§7.2) | Phase 3 |
| **Stage 3 — Build Configuration B in isolation, verify equivalence** | New research module only, never touching production code; verify against the equivalence contract and error-handling table before any comparative data collection | Phase 2 implementation (not yet authorized) |
| **Stage 4 — Run the experiment** | Paired, counterbalanced execution; blinded rating; full raw-output retention; pre-registered primary-endpoint analysis; secondary metrics and trade-offs reported separately | Phases 5–8 |

**This proposal requests approval to begin Stage 1 only.** Stages 2–4 each require a separate approval gate
before proceeding, consistent with the standing instruction that no code change or experiment execution occurs
without explicit sign-off.

---

## 10. Document status summary (v2)

| Item | Status |
|---|---|
| External review of documents 19–22 | Received and addressed item-by-item in this document and its companions (23–26) |
| P0-1 (primary endpoint) | **Resolved** — Option 1 adopted (§7.1) |
| P0-2 (A/B equivalence) | **Resolved** — equivalence contract specified in `24_...v2.md` §2 |
| P0-3 (independent ground truth) | **Resolved** — rule adopted (§5.2) |
| P0-4 (statistical plan) | **Resolved** — full specification in `25_...v2.md` §4 |
| P0-5 (defect separation) | **Resolved** — four binding rules adopted (§6) |
| P1-6 through P1-10 | **Resolved** — §3, §7.3, §5, §5.1, §7.4 respectively |
| Stage 1 (freeze specification) | **Requested for approval now** |
| Stages 2–4 | **Not started; each requires its own separate approval** |
| Production architecture | **Unchanged** |
| New comparative results | **None exist** |
