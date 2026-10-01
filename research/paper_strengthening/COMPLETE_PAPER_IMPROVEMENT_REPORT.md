# Complete paper improvement report

**Date:** 2026-09-29. Covers this session's two passes on `FINAL_MANUSCRIPT_EVIDENCE_V2.md`: the sixth pass (full account in `SIXTH_SYSTEM_PAPER_STRENGTHENING_PASS_REPORT.md`) and a seventh, shorter pass responding to a follow-on mission asking for a complete manuscript-wide consistency check and any further feasible improvement. Written under an explicit resource-efficiency instruction (roughly half the session's usage budget already spent); this pass therefore prioritized a few high-value, cheap-to-verify improvements over another broad audit sweep. Nothing committed, tagged, or pushed. No frozen path modified (checked before and after via `git status --short` against the full protected-path list in `CLAUDE.md`).

## 1. Major system improvements implemented (this session, both passes)

- `services/qwen/app.py::_build_followup_prompt`: fixed a third instance of the same defect class (a vacuous "None identified" TASK-line instruction), this one triggered when a follow-up fires on score alone with all of the evaluator's missing/incorrect/weakest-gap signals empty. One new regression test; 48/48 passing in the affected test file, 358/358 passing repository-wide (up from 357, zero regressions).
- No other production code was changed. The PPO controller, evaluator scoring logic, and guardrails were investigated (via the sibling track's already-completed work, re-read and cross-checked, not re-run) but not modified — per §4's explicit instruction not to bypass PPO V2 confirmatory-evaluation authorization or force changes to components already performing within their documented, evidence-supported bounds. No credible, non-tuning-driven case for changing evaluator weights emerged from this session's evidence (see §2 below): the matched-subset configuration comparison exists to *characterize* the evaluator's current behavior, not to justify re-weighting it against a 4-question development set.

## 2. Experiments performed and their results

| Experiment | Hypothesis | Result |
|---|---|---|
| Expanded follow-up behavioral probe (5→12 cases, 8 categories, `followup_behavioral_probe_v2.py`) | The prior 5-case probe under-sampled the evidence-trigger space and might miss further prompt defects | 15/15 real-model calls used the live LLM path; 14/15 keyword-overlap with intended target (the 1 miss was a heuristic false negative, manually confirmed well-targeted); surfaced and enabled the fix in §1 above; found two real, disclosed (not fixed) qualitative patterns: modest output variability under repeat calls (mean pairwise keyword-Jaccard 0.85 and 0.69 across two repeated cases) and a stylistic tendency for some follow-ups to closely echo the original question's phrasing |
| Qid-clean, current-code matched-subset re-analysis of Table X's 7 configurations (`evaluator_matched_subset_live_rescore.py`) | The evaluator's central ablation table (Table X) might be recoverable from a data-provenance defect discovered on the sibling P1/P3 track | Built a corrected table via live re-scoring (not the stale frozen CSV — a first attempt using the frozen CSV failed its own consistency check, itself informative, see below). The paired full-composite-vs-R-only comparison reproduces the original table's conclusion (CI [−0.032, 0.010], includes zero) on an independently-corrected data source, with the point estimate's sign reversing — reported as reinforcing, not changing, the conclusion |
| Evaluator bias-source synthesis (analysis only, no new model calls) | The previously-reported systematic under-scoring bias might be an artifact of the qid-mismatch contamination rather than a general evaluator property | Confirmed: mean signed error is −0.2778 on the 32 mismatched cases vs. −0.0060 (near-zero, symmetric) on the 32 qid-clean cases, both under stale and current-code scoring. Residual clean-subset divergence is consistent with the already-disclosed §XI.1c logical-reasoning weakness, not a new, separate problem |
| Frozen-CSV matched-subset attempt (`reanalyze_evaluator_ablation_matched_subset.py`) | (Superseded en route) — same methodology as the corrected table above, but reading the frozen CSV instead of live-rescoring | **Failed its own built-in consistency check** (computed full-composite ρ=0.7092 vs. the sibling track's independently-verified 0.655) — this failure is what surfaced the CSV-staleness finding; the script's output is retained for transparency but is not cited in the manuscript |

## 3. Comparisons against baselines

- Evaluator: R-only, S1+R, and full-composite are compared against each other under two data sources this session (the original 8-question Table X and the corrected 4-question qid-clean re-analysis); the qualitative ranking (no configuration significantly beats R-only) is stable across both.
- Follow-up mechanism: pre-fix vs. post-fix generated text is compared on the same constructed case for the sparse/incomplete-evidence defect (single-case, non-powered, disclosed as such).
- No PPO baseline comparison was re-run this session; the sibling track's existing Constant-Same/Heuristic/PPO+G comparisons (§XI.2, already in the manuscript) were reviewed for currency and found unchanged and still accurately reported.

## 4. Material manuscript improvements

`FINAL_MANUSCRIPT_EVIDENCE_V2.md`:
- Abstract: evaluator-finding sentence extended with the corrected-subset caveat and reinforced conclusion.
- Introduction (Contributions list): two new bullets added (the cross-track evidence integration/bias synthesis; the follow-up behavioral evidence base), reflecting work this list previously did not cover.
- §VII (Follow-up generation): new paragraph documenting the 12-case/8-category probe, the third defect found+fixed, the repeat-run variability finding, and the disclosed stylistic pattern.
- §XI.1 (Evaluator results): qid-mismatch and CSV-staleness disclosure, corrected Table X, reinforced paired-comparison result, and the new bias-source synthesis paragraph.
- §XII (Limitations): three items added/corrected (stale test-status text fixed; Table X provenance caveat; disclosure of the separate human-study-gated system-paper workspace).
- §XIII (Reproducibility): references and exact commands for all three new scripts, with an explicit instruction that the superseded frozen-CSV script's output must not be cited.
- §XIV (Conclusion): corrected two now-false statements ("no new experiments"; the follow-up gate "never... exercised against a live model") and rewrote the paragraph to state what was actually done and what remains, consistent with this pass's instruction not to leave a superseded claim in the conclusion.

## 5. Tests performed

- Targeted: `tests/unit/test_qwen_followup_feedback.py` → 48/48 passed (sixth pass, before this pass's manuscript-only edits).
- Full suite: `EVALUATOR_MOCK_MODE=1 pytest -q` → **358 passed, 0 failed, 501.70s** (sixth pass; not re-run this seventh pass, since it made no further code changes — consistent with this mission's explicit instruction not to re-run the full suite without a reason).

## 6. Remaining blockers and unresolved claims

Unchanged from the sixth pass; restated rather than re-investigated since nothing new was found about them this pass:
1. **Evaluator benchmark repair** (re-indexed rubric content for the 4 qid-affected questions, authored independently of the development team) — the single highest-value remaining evidentiary gap; a complete, ready-to-execute package exists on the sibling track, pending an author decision.
2. **PPO V2 confirmatory-evaluation authorization** — a ready-to-run protocol exists; not executed, per the standing rule, and not attempted this session.
3. **Reconciliation of the two system-paper tracks** — disclosed in the manuscript (§XII); the reconciliation itself remains an author decision.
4. **`CLAUDE.md`'s "Known gotchas" section** is stale on the `test_stage11_5_coding_adaptation.py` item; flagged for the user, not edited unilaterally.
5. **The 4-question qid-clean subset is a genuinely weaker instrument than the original 8-question design** — every number derived from it this session is reported with that caveat attached, and none is presented as replacing the eventual need for a properly repaired 8-question benchmark.

## 7. Completion assessment against this mission's own definition (§12)

- Manuscript reviewed and materially strengthened: yes, across Abstract, Introduction, §VII, §XI.1, §XII, §XIII, §XIV.
- Meaningful system improvements investigated/implemented where justified: one production defect fixed (§1); evaluator/PPO changes investigated and *not* made, because no non-tuning-driven justification emerged — reported as a considered decision, not an omission.
- Promising changes evaluated against baselines: yes, see §2–3.
- Strongest verified findings integrated into the paper: yes.
- Methodology and evidence reproducible: yes — every new number traces to a script and a JSON output file listed in §XIII, with exact commands given.
- Abstract, tables, results, discussion, and conclusion agree: checked and corrected this pass (§XIV was the one section still inconsistent with the rest of the document; now fixed).
- Tests appropriate to the changes passed: yes (358/358, §5).
- **This manuscript is not being declared publication-ready.** It remains, by its own explicit and repeated framing, an audit-scoped contribution resting on development-grade and exploratory evidence (an 8-question, now partially 4-question, benchmark; simulation-only RL evidence; construct-case behavioral probes) — not a claim this pass changes. The blockers in §6, especially the evaluator benchmark repair and the PPO V2 authorization decision, are author-level decisions this session cannot and did not resolve.
