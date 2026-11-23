# Sixth system-paper strengthening pass

**Date:** 2026-09-29. Scope: `research/paper_strengthening/FINAL_MANUSCRIPT_EVIDENCE_V2.md` and its supporting claim ledger, following the fifth pass's manuscript reconstruction. Named "sixth" to match this document's own numbering (five prior passes on this specific track: the four passes described in `RESEARCH_IMPROVEMENT_EXECUTION_V1_REPORT.md` through `FOURTH_RESEARCH_IMPROVEMENT_PASS_REPORT.md`, plus the fifth pass recorded in `PREPAIRED_SYSTEM_PAPER_MAX_STRENGTHENING_REPORT.md`). This is distinct from, and should not be confused with, the separate P1/P3-track passes of the same ordinal numbers (`SIXTH_PROJECT_WIDE_RESEARCH_AND_ENGINEERING_PASS_REPORT.md` through `NINTH_RESEARCH_STRENGTHENING_PASS_REPORT.md`), which this pass reads from and cites but does not duplicate.

Nothing was committed, tagged, pushed, or submitted. No frozen path was modified (`git status --short` checked against every protected path both before and after this pass: `research/CANONICAL_SCIENTIFIC_TRUTH.md`, `research/papers/`, `research/results/paper3/`, `research/CLAUDE_HANDOFF/`, `research/audit/`, `research/experiments/paper3/frozen_config.yaml`, `research/data/evaluator_benchmark/*.csv`, `rl/checkpoints/`, `ablation/results/`).

## 1. Initial state

The prior turn's compacted summary described this track as having completed a "fifth pass." On inspecting the repository directly at the start of this pass, the actual on-disk state was considerably further advanced than that summary reflected: `FINAL_MANUSCRIPT_EVIDENCE_V2.md` already contained a fully reconstructed §III–IX, a real 13-reference Related Work section, and detailed §XI findings on the evaluator, RL controller, speech channel, prompt-injection mitigation, fault tolerance, and multimodal scope — consistent with the fifth pass's own report but more extensive than the summary's brief description suggested. This is noted here as a caution for future passes: verify the manuscript's actual current state by reading it, not by trusting a prior turn's summary of it.

A parallel discovery: several files existed (`PPO_V2_CONFIRMATORY_EVALUATION.md`, `SIXTH_PROJECT_WIDE_RESEARCH_AND_ENGINEERING_PASS_REPORT.md` through `NINTH_RESEARCH_STRENGTHENING_PASS_REPORT.md`) that were not part of this track's own history. Investigation confirmed these belong to this project's separate P1/P3 manuscript track (fifth-through-ninth passes on that track, matching the prior summary's own description of "five research-strengthening passes, 5th–9th"), not a conflicting concurrent-agent edit, and that the PPO V2 confirmatory evaluation was correctly **not executed** — only its protocol was prepared, pending authorization, per the standing rule. No rule violation was found. This verification is recorded because the alternative (silently assuming either duplication or a violation) would have been worse than the ~15 minutes spent checking.

## 2. Weaknesses selected, and why

Given realistic per-turn scope (this pass does not span a literal four-hour block; work below is what was actually completed, not a phased plan), two items were prioritized over a broader sweep of the master prompt's full checklist:

1. **A cross-track evidence integration the prior pass had not yet made**: the P1/P3 track's seventh/ninth passes had independently discovered and partially repaired a qid-mismatch bug in the exact same 64-case, 8-question evaluator benchmark this manuscript's central Table X (§XI.1) is built from — but this manuscript had not yet incorporated that finding. This was judged the single highest-value, already-substantially-vetted (reproduced twice on the sibling track) improvement available, directly affecting the paper's most load-bearing evidentiary table, and squarely within the master prompt's top priority ("strengthen evidence wherever feasible," "don't stop at cosmetic editing when substantive improvement is feasible").
2. **The explicit §5.1 instruction not to leave the follow-up behavioral probe at "another handful of easy, constructed examples"**: the existing probe (fifth pass, N=5) was expanded to 12 constructed cases across 8 evidence categories plus a 9th skip-verification category, with a repeat-run variability check and a manually-read correction of one heuristic miss.

Both were chosen over, e.g., a fresh PPO baseline sweep (already well-covered by the sibling track's checkpoint-selection ablation and X3-A) or further evaluator architecture changes (already attempted three times on the sibling track and correctly deferred pending the benchmark repair, per `NINTH_RESEARCH_STRENGTHENING_PASS_REPORT.md` §8).

## 3. Technical improvements implemented

**One production code fix**, `services/qwen/app.py::_build_followup_prompt`: a follow-up can be triggered by score alone (`InterviewOrchestrator`'s score<0.80 branch) even when the evaluator's own missing-concept/incorrect-claim/weakest_gap fields are all empty (a thin, generic answer that doesn't clearly hit or miss any specific rubric concept). The prompt builder's final fallback previously produced the same vacuous "targeting the missing concept(s): None identified" instruction that two earlier defects (fixed in the fifth pass) also produced. Fixed to ask for depth/specificity, citing the actual score, instead of naming a nonexistent gap. One new regression test added (`tests/unit/test_qwen_followup_feedback.py::test_build_followup_prompt_task_line_targets_depth_when_all_signals_empty`); 48/48 tests in that file pass (47 prior + 1 new).

No other production code was changed. No frozen file, checkpoint, or dataset was modified.

## 4. Experiments conducted

### 4.1 Expanded follow-up behavioral probe (`followup_behavioral_probe_v2.py`)

12 constructed cases (15 real GGUF `generate_followup()` calls after 2 cases were each repeated 3×) spanning misconception, missing concept, all three of `weakest_gap`'s non-trivial production string formats, below-threshold score, conflicting evidence, a near-boundary ambiguous case, sparse/incomplete evaluator output, and non-redundancy against a prior follow-up — plus a 9th category, a strong-answer skip case verified via the production gate predicate rather than an LLM call (since production never calls `generate_followup()` in that situation either). Full raw output: `research/paper_strengthening/results/followup_behavioral_probe_v2/results.json`.

Results: 15/15 real-model calls used the live LLM path; 14/15 showed keyword overlap with the hand-written probe target. The one miss was manually read and found well-targeted (an exact-word-match heuristic limitation, not a real targeting failure). This surfaced the defect fixed in §3 above; re-running after the fix showed a qualitatively more mechanism-specific generated question on the same case (single before/after comparison, not a powered study). A repeat-run check (temperature 0.1, top_p 0.9, no per-call seed) found genuine but modest output variability (mean pairwise keyword-set Jaccard 0.852 and 0.689 across two cases' 3 repeats each), with the probed concept preserved in every repeat. 6/15 generations were flagged by a coarse "possibly repeats original question" heuristic; manual reading of all six found no literal repeats, but confirmed a real, disclosed stylistic pattern (some follow-ups closely echo the original question's phrasing while narrowing to the new target).

### 4.2 Qid-clean, current-code matched-subset re-analysis of Table X

Two scripts were written. The first, `reanalyze_evaluator_ablation_matched_subset.py`, extended the existing `reanalyze_evaluator_ablation.py` methodology by filtering the same frozen `paper2_case_level_results.csv` to the 32 qid-clean cases. Its own built-in consistency check against the sibling P1/P3-track's already-independently-verified matched-subset number (ρ=0.655, `evaluator_benchmark_repair_package/matched_subset_evaluation.json`) **failed** (this script computed ρ=0.7092). Direct per-case comparison found 6 of the 32 "clean" cases' stored `final_score` in the frozen CSV differs from a live re-score, with all 32 gold scores identical — confirming the frozen CSV is stale relative to the current, uncommitted evaluator code (carrying this engagement's own earlier NaN-handling and negation-filter fixes), independent of and in addition to the qid-mismatch contamination. This first script's output is **not cited** in the manuscript; it is retained in the scripts directory only because its failed consistency check is itself the evidence for the staleness finding.

The second script, `evaluator_matched_subset_live_rescore.py`, re-derives all seven Table X configurations (S1, S2, R, S1+S2, S1+R, S2+R, full composite) via a live, non-mock call to the current `evaluate()` function against `benchmark_dataset.csv`'s self-contained question/answer text, restricted to the 4 qid-clean questions. Its full-composite item-level ρ (0.655) exactly reproduces the sibling pass's number, confirmed by an in-script assertion before any of the other six rows are used. Output: `results/evaluator_matched_subset_live_rescore.json`.

**Result:** the paired full-composite-vs-R-only comparison (the one pre-specified inferential test this document has run on this question, mirroring the original Table X's own design) gives mean difference −0.0119, 95% CI [−0.0323, 0.0103] — still includes zero. The qualitative conclusion (no demonstrated advantage of the full weighting over R-only) is unchanged and, by holding under an independently-corrected data source, is reported as reinforced; the point estimate's sign reverses (previously full composite marginally worse, now marginally better), itself additional evidence the effect is within this instrument's noise floor rather than a real advantage in either direction. No other pairwise comparison across the seven new rows was run or is reported as inferential, since none was pre-specified and the reduced 4-question cluster count makes informal CI-overlap comparisons unreliable — deliberately avoided, consistent with the standing rule against post-hoc comparison mining.

## 5. Comparison with the previous state

| Item | Before this pass | After this pass |
|---|---|---|
| Follow-up probe | N=5, 5 categories | N=12 constructed cases (15 calls), 8 categories + 1 skip-verification category, plus a repeat-run variability check |
| Follow-up prompt defects fixed (this engagement, cumulative) | 2 (misconception/missing-concept, weakest-gap TASK-line priority) | 3 (+ sparse/incomplete-evidence fallback) |
| Table X provenance | Believed to be a clean 8-question, 64-case analysis, exploratory only | Disclosed as half qid-contaminated (32/64 cases) AND partially stale relative to current evaluator code (6/32 of the "clean" half); a corrected qid-clean current-code 4-question re-analysis now exists alongside it |
| Central evaluator finding (full composite vs. R-only) | CI includes zero, one data source | CI includes zero, reproduced on an independently-corrected data source; conclusion reinforced |
| Two-track disclosure | Not mentioned in the manuscript | Limitations bullet added, cross-linking the separate human-study-gated system-paper workspace |
| `test_stage11_5_coding_adaptation.py` status in this manuscript's own text | Described as currently failing | Corrected to reflect the fix (verified via a fresh full-suite run, §6) |

## 6. Tests executed and results

- Targeted: `EVALUATOR_MOCK_MODE=1 pytest -q tests/unit/test_qwen_followup_feedback.py` → **48 passed** (47 prior + 1 new), 44.96s.
- Full suite: `EVALUATOR_MOCK_MODE=1 pytest -q` → **358 passed, 0 failed, 501.70s (0:08:21)** — exactly one more than the previous pass's 357, matching this pass's one new regression test; zero regressions.
- All three new/modified scripts (`followup_behavioral_probe_v2.py`, `reanalyze_evaluator_ablation_matched_subset.py`, `evaluator_matched_subset_live_rescore.py`) were executed to completion, not assumed to work; exact commands are in §8.

## 7. Manuscript sections improved

`FINAL_MANUSCRIPT_EVIDENCE_V2.md`: Abstract (evaluator-finding sentence extended with the corrected-subset caveat), §VII (follow-up probe v2 paragraph added), §XI.1 (qid-mismatch and staleness disclosure, corrected Table X, paired-comparison reinterpretation), §XII (three new/corrected Limitations bullets: test-status correction, Table X provenance, two-track disclosure), §XIII (reproducibility references for all three new scripts, with an explicit note that the frozen-CSV matched-subset script's output should not be cited).

`CLAIM_LEDGER_SYSTEM_PAPER_V1.md`: new "Sixth System-Paper Pass" section, SP-52 through SP-61.

## 8. New or updated research artifacts

- `research/paper_strengthening/scripts/followup_behavioral_probe_v2.py` (new)
- `research/paper_strengthening/results/followup_behavioral_probe_v2/results.json` (new)
- `research/paper_strengthening/scripts/reanalyze_evaluator_ablation_matched_subset.py` (new; output not cited, retained for transparency of the staleness discovery)
- `research/paper_strengthening/results/evaluator_reanalysis_matched_subset.json` (new; not cited)
- `research/paper_strengthening/scripts/evaluator_matched_subset_live_rescore.py` (new; cited)
- `research/paper_strengthening/results/evaluator_matched_subset_live_rescore.json` (new; cited)
- `services/qwen/app.py` (modified: `_build_followup_prompt`'s final fallback)
- `tests/unit/test_qwen_followup_feedback.py` (modified: +1 regression test)

Exact reproduction commands:
```
.venv/Scripts/python.exe research/paper_strengthening/scripts/followup_behavioral_probe_v2.py
.venv/Scripts/python.exe research/paper_strengthening/scripts/evaluator_matched_subset_live_rescore.py
EVALUATOR_MOCK_MODE=1 .venv/Scripts/python.exe -m pytest -q tests/unit/test_qwen_followup_feedback.py
```
(The first two require real, non-mock models and take several minutes each; the follow-up probe additionally requires the GGUF model file to be present at `GGUF_MODEL_PATH`.)

## 9. Remaining blockers

Unchanged from the fifth pass and the sibling P1/P3 track, restated rather than re-investigated since nothing new was found about them this pass:
1. A full repair of the evaluator benchmark (re-indexed rubric content for the 4 affected questions, authored independently of the development team) — a complete, ready-to-execute package exists on the sibling track; only the author decision is missing.
2. PPO V2 confirmatory-evaluation authorization — a ready-to-run protocol exists (`PPO_V2_CONFIRMATORY_EVALUATION.md` §6); not executed, per the standing rule, and not attempted this pass.
3. Reconciliation of the two system-paper tracks — now disclosed in the manuscript for the first time (§XII), but the reconciliation itself remains an unresolved author decision.
4. `CLAUDE.md`'s "Known gotchas" section is now stale on the `test_stage11_5_coding_adaptation.py` item; flagged for the user to correct via the project's own governance process, not edited unilaterally in this pass.

## 10. Recommended next steps

1. Author decision on the evaluator benchmark repair (item 1 above) — unblocks the single most consequential remaining evidentiary gap for both this manuscript and the sibling P1/P3 track.
2. If a larger follow-up behavioral study is ever wanted: the N=12 probe here is still constructed, not sampled from real candidate answers; a next step would draw cases from actual session transcripts (once available) rather than hand-authored ones, and add the human-judged rubric dimensions (technical correctness, specificity, non-redundancy) this pass explicitly did not attempt to automate.
3. Update `CLAUDE.md`'s gotchas section (item 4 above) through the project's normal documentation-maintenance process.
