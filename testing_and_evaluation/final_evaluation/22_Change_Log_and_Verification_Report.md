# 22. Change Log and Verification Report

**Purpose:** list every document created/changed in this task, explain why, and confirm — explicitly and
itemized — that no production code, test code, dataset, checkpoint, PPO artifact, or historical result was
modified. Also performs the 15-point final quality-control review the task specification requires before
delivery.

---

## 1. Files created in this task

| File | Type | Relationship to prior work |
|---|---|---|
| `testing_and_evaluation/final_evaluation/19_Revised_Experimental_Proposal.md` | New document | Revised/corrected successor-for-review to `18_MultiAgent_vs_SingleAgent_Evaluation_Proposal.md`, which is **unmodified and still present on disk** |
| `testing_and_evaluation/final_evaluation/20_Architecture_and_Baseline_Comparison_Specification.md` | New document | Elaborates Phase 1/Phase 2 content referenced from document 19; summarizes (does not replace) `17_Architecture_Audit_Report.md` |
| `testing_and_evaluation/final_evaluation/21_Experimental_Results_Framework.md` | New document | Elaborates Phase 4/Phase 6/Phase 8 content referenced from document 19 |
| `testing_and_evaluation/final_evaluation/22_Change_Log_and_Verification_Report.md` | New document (this file) | Deliverable 4 |

**No existing file was edited.** Document 18 (the original proposal) was read but not modified — confirmed by
using the `Write` tool only on new file paths throughout this task, never `Edit` on an existing deliverable.

---

## 2. Itemized corrections applied, relative to document 18, and why

| # | Correction | Where applied | Reason |
|---|---|---|---|
| 1 | Title changed from "Multi-Agent vs. Single-Agent" framing to "Specialised, Orchestrator-Coordinated Architecture vs. Unified Single-Controller" | Doc 19 title | Document 18's title presupposed the system under test was multi-agent; the architecture audit (doc 17) found no verified peer-to-peer agent communication, so the comparison is more accurately framed as specialisation-plus-orchestration vs. unification |
| 2 | Objective rewritten to not assume full multi-agent collaboration | Doc 19 §1 | Same reason; objective must not presuppose its own conclusion |
| 3 | Architecture audit (doc 17) explicitly treated as completed Phase 1 work, with two specific caveats independently re-verified against current source | Doc 19 §2 | Avoids redundant re-inspection while still satisfying "verify this finding against the current repository" for the two claims most load-bearing for the new study (Qwen scoring, verbal/coding separation) |
| 4 | Single-controller baseline definition strengthened: tools/models remain shared; only control-flow consolidation changes | Doc 20 §2 | Document 18's Configuration B description was thinner and risked being read as "remove functionality to simplify," which the task explicitly prohibits |
| 5 | Benchmark expanded from 10 to 17 scenario categories | Doc 19 §5 | Matches the task specification's expanded Phase 3 list exactly (misconceptions, hesitation/prosody, conflicting multimodal evidence, failure/recovery added) |
| 6 | Primary/secondary endpoints explicitly defined, with a recommended (not adopted) primary endpoint | Doc 19 §6; doc 21 §2 | Task requires endpoints fixed before data collection; document 18 listed metrics without designating a primary endpoint |
| 7 | Execution/reproducibility requirements expanded (seed logging, statistical unit = persona, isolation from production) | Doc 19 §7 | Matches task Phase 5 requirements; aligns statistical-unit rule with `CLAUDE.md`'s existing Paper 3 convention rather than inventing a new one |
| 8 | Sample-size and statistical methodology section added, explicitly deferring a concrete N until a power/precision analysis is possible | Doc 19 §8 | Task explicitly prohibits an arbitrary sample size; no number is given because none is yet justified |
| 9 | "Coordination-disabled" ablation replaced with "decision-component ablation" (C1–C4: PPO+guardrails / guardrails-only / heuristic-only / fixed) | Doc 19 §9 | Direct correction required by the task: document 18's Phase 7 assumed disable-able inter-agent coordination that the audit did not establish exists |
| 10 | Explicit historical-vs-new-results separation added, including the corrected provenance of the Fixed/Heuristic/PPO/PPO+guardrails MAE table | Doc 21 §3 | Mandatory per task §12; see §3 of this report for the specific correction made |
| 11 | Results/Discussion framework and visualisation plan added in full, with all four possible conclusions stated as equally open | Doc 21 §4 | Matches task Phase 8 requirement; document 18 had no Results/Discussion section at all |
| 12 | Comparison table and ablation table added, every cell "Pending," none fabricated | Doc 21 §3.B, §3.C | Matches task §12.B requirement exactly, including the explicit warning against illustrative values |
| 13 | Final research objective restated to match the task's seven numbered investigation questions | Doc 19 §1 | Alignment with task §2 |
| 14 | Document status summary updated to explicitly separate "completed," "designed-not-implemented," and "not executed" phases | Doc 19 §11 | Matches task §15 requirement |
| 15 | Approval gate restated verbatim at the end of doc 19 | Doc 19 §11 (closing line) | Preserved per task's explicit instruction not to drop it |

---

## 3. Specific correction made to a claim in the task specification itself

The task specification (Task 1, §12) stated: *"the architecture audit reports these existing difficulty-tracking
MAE values: Fixed 1.200, Heuristic 0.473, PPO raw 0.804, PPO plus guardrails 0.677."*

**This was checked, not assumed.** A grep of `17_Architecture_Audit_Report.md` for these exact values returned
zero matches — that report does not contain this table. The numbers themselves are real and are correctly
stated (confirmed against `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §D.2, which cites
`paper3_baseline_results.csv`/`paper3_seed_results.csv`/`paper3_summary_results.csv`), but their source
attribution in the task specification was incorrect. This has been corrected in
`21_Experimental_Results_Framework.md` §3.A, with the accurate source cited and the original mandatory caveat
("the heuristic is better than every PPO variant... PPO's contribution under guardrails is not identified...
claim 'PPO improves tracking' is withdrawn") preserved verbatim, since it is part of the historical record and
must not be dropped when the table is reused. This is reported here, rather than silently fixed, per the
project's standing rule to never invent or silently correct a provenance claim without disclosure.

---

## 4. Treatment of the second pasted item (the "does this invalidate the project" discussion)

The second block in this task's input was explanatory/discussion text (addressed to the project team, not a set
of instructions to execute), summarizing the architecture audit's implications, proposing a terminology table,
and recommending against rebuilding the system to defend a "multi-agentic" label. It is **consistent with, and
independently corroborated by, this engagement's own verified findings** (doc 17's classification, the
hub-and-spoke grep evidence, the Qwen-never-scores finding re-verified in doc 20 §1.3). Its specific content —
the 0%-autonomous-peer-agent framing, the "no rewrite required" table, and the terminology recommendations — has
been treated as **project-level framing and rationale**, not as new technical evidence, and has been reflected
in this work as follows:

- The revised proposal (doc 19) does not claim or imply the project's prior engineering, models, or research are
  invalidated by the audit's classification — it explicitly frames this as an architecture-comparison question,
  separate from model/engineering quality.
- No terminology table from that discussion was inserted verbatim into a numbered deliverable as if it were an
  audit finding; where this report references it (here, §4), it is clearly attributed as discussion context
  supplied by the user, not as independently re-derived evidence.
- The suggestion that a future, genuinely collaborative multi-agent redesign is a *separate, optional* future
  direction — not part of this task — is carried into doc 19 §3, matching both that discussion and the task
  specification's own explicit instruction.

---

## 5. Preservation confirmation (explicit, itemized)

| Constraint | Status |
|---|---|
| Production application code (`agents/`, `apps/`, `services/`) | **Untouched** — no `Edit`/`Write` call targeted any file under these directories in this task |
| `InterviewOrchestrator` | **Untouched** |
| PPO policy / checkpoints (`rl/checkpoints/`) | **Untouched** — not read, not retrained, not replaced |
| Guardrails (`rl/guardrails.py`, orchestrator's private copy) | **Untouched** — their documented divergence (doc 17 §3.3) is referenced, not fixed |
| Frozen datasets (`research/data/evaluator_benchmark/*`, `data/questions/qns.json`) | **Untouched** — read-only grep/read access only |
| Historical results (`research/results/paper3/*`, `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`) | **Untouched** — read-only, cited with corrected attribution, not recalculated or overwritten |
| Test files (`tests/`) | **Untouched** |
| Historical logs (`testing_and_evaluation/logs/*`) | **Untouched** |
| Docker sandbox / security configuration | **Untouched** |
| Model configurations (Qwen, SBERT, CrossEncoder) | **Untouched** |
| Single-controller baseline (Configuration B) | **Not implemented** — specification only (doc 20) |
| New comparative experiment | **Not executed** — zero results exist (doc 21 §3.B, §3.C all "Pending") |
| External submission/publication | **None performed** |

---

## 6. Final quality-control review (15-point checklist)

1. **Architectural terminology accurately reflects the implementation.** ✅ Verified — doc 19/20 use "specialised
   components under central orchestration," not "multi-agent," consistent with doc 17's classification.
2. **No deterministic helper incorrectly labelled an autonomous agent.** ✅ Verified — classification matrix in
   doc 20 §1.1 carries forward doc 17's Category C/D labels for ScoreValidator, QuestionTimer, SessionLogger,
   the evaluator, the Docker sandbox, and `select_questions`.
3. **Existing architecture has not been modified.** ✅ Confirmed, §5 above.
4. **Single-controller comparison is scientifically fair.** ✅ Addressed via doc 20 §2.3–§2.5 and the explicit
   fairness checklist (doc 20 §3); not yet *achieved* because nothing is built, but the design does not
   intentionally weaken Configuration B.
5. **Both configurations have equivalent access to relevant tools and information.** ✅ Specified in doc 20 §2.3;
   enforcement is a build-time requirement, not yet verified in running code.
6. **Benchmark is reproducible.** ✅ Specified (doc 19 §5) to use frozen datasets plus documented new
   constructions; not yet built, so reproducibility is a design property, not yet a demonstrated one.
7. **Metrics have operational definitions.** ✅ Doc 21 §1 defines every metric operationally.
8. **Primary endpoint specified before results.** ✅ Doc 19 §6 / doc 21 §2 — recommended, pending adoption, with
   zero results existing yet.
9. **Statistical unit correctly defined.** ✅ Persona, per `CLAUDE.md`'s existing Paper 3 convention, carried
   into doc 19 §7 item 9.
10. **Historical results not mixed with new comparative results.** ✅ Doc 21 §3.A/§3.B/§3.C are explicitly
    separated, with a direct statement that §3.A is not evidence for the new research question.
11. **Old coordination-ablation problem corrected.** ✅ Doc 19 §9, explicit correction with rationale.
12. **Research conclusion not predetermined.** ✅ Doc 21 §4 states all four possible conclusions as equally open;
    no document in this task asserts which configuration will or did win.
13. **All unexecuted work explicitly labelled pending.** ✅ Every results cell in doc 21 is "Pending"; status
    tables in doc 19 §11 and this document's §5 above are explicit.
14. **Approval gate preserved.** ✅ Doc 19's closing section restates it verbatim; this report does not authorize
    proceeding to implementation.
15. **Revised document is internally consistent and professionally formatted.** ✅ Reviewed for consistency
    across docs 19–22 — file paths, section cross-references, and the MAE-table correction are consistent across
    all four documents (checked by re-reading the relevant cross-referenced sections of each during drafting).

---

## 7. What happens next (not authorized by this report)

Per the task's explicit final instruction, this report does **not** authorize implementation of Configuration B,
construction of benchmark scenario instances, or execution of any experimental run. Those require a separate,
explicit human approval decision on documents 19 and 20 before any further work proceeds.
