# Evaluator human-gold benchmark — corrected scoring, version 1 (eighth pass)

**Status: a versioned, non-frozen, clearly-labeled reanalysis artifact. Does NOT modify, replace, or supersede `research/data/evaluator_benchmark/final_human_gold.csv` or `benchmark_dataset.csv`, both of which remain untouched.** Source lineage: every `case_id` here is identical to and traceable back to those two frozen/source files; no score, rating, or rubric concept was invented.

## What this file is

A repair-option decision record plus the cleanest currently-available corrected estimate, produced after independently re-deriving the seventh pass's qid-mismatch finding from scratch (`eighth_pass_independent_reverification.py`; full data-integrity check found no additional issues — no duplicate case IDs, no missing/malformed values, no case-ID mismatch between the benchmark and gold files, exactly 8 cases per question).

## The three populations, kept strictly separate

| Population | n | Scoring method | Spearman ρ | Mean signed diff (eval − gold) | What it can support |
|---|---|---|---|---|---|
| **A. Matched-qid subset** (qid 1, 3, 10, 41) | 32 | Current production `evaluate()` via `get_rubric(qid)` — the real, fully-indexed rubric with mandatory/bonus/mistake vectors, unchanged | **0.655** | −0.006 (negligible bias) | The **cleanest currently-available estimate of the evaluator's true agreement with human judgment** — full production scoring pipeline, correct rubric, no shortcuts. Smaller sample (4 questions, 32 cases) than the original design intended. |
| **B. Mismatched-qid subset, current (broken) production scoring** (qid 7, 15, 22, 50) | 32 | Current production `evaluate()` via `get_rubric(qid)` — the WRONG rubric (a different question) | 0.425 | −0.278 (severe under-scoring) | **Nothing about evaluator quality.** This is a measurement of the bug itself, kept only to document its magnitude. Must never be cited as evidence about the evaluator. |
| **C. Mismatched-qid subset, diagnostic ad hoc rescoring** (qid 7, 15, 22, 50) | 32 | A rubric built in-memory, per case, from `benchmark_dataset.csv`'s own already-stored `reference_answer`/`rubric_concepts` columns, embedded on the fly via `evaluate()`'s existing `expected_concepts` fallback path (no FAISS index, no mandatory-cap, no bonus-vector, no semantic-mistake-vector components) | 0.710 | +0.039 (near-zero bias) | A **lower-bound sensitivity estimate**: shows the evaluator's semantic/concept-coverage/reasoning core (S1, S2, R — 100% of the score weight in this reduced form) recovers good agreement once given the correct question, but cannot speak to how the mandatory-cap/bonus/mistake-penalty components (which the real production pipeline has for every other question) would behave on these 4 questions, because those components have no indexed content for them. **Not a validated replacement for population A's rigor.** |

**Never blend B into anything.** Population C may be reported alongside A as a labeled sensitivity check, but a single merged "N=64 corrected" number (as this pass's predecessor report's §4.3 last row presented, ρ=0.700) **should be read as an upper-bound-of-plausibility illustration, not a defensible unified estimate** — it averages two populations scored by methodologically different pipelines (full production scoring for 32 cases, a reduced ad hoc scoring for the other 32), which is not a clean measurement design even though both directions point the same way. This pass's report and any future citation should present A and C side by side, not merged, per the master prompt's explicit instruction to keep them distinguishable.

## Repair options considered

**(a) Restore/re-index the original four rubrics with real FAISS-indexed vectors.** Feasible in part: `benchmark_dataset.csv` already contains the correct `reference_answer` and `rubric_concepts` for all 32 affected cases (nothing to invent for the semantic/concept-coverage components). **Not fully feasible without inventing content**: production rubrics also carry `mandatory` concepts, `common_mistakes_addressed` text, and bonus indicators (see any live `rubrics.json` entry, e.g. qid=1's structure) that do not exist anywhere in the benchmark file for these 4 questions and were never authored for them. Building those would mean writing new rubric content not backed by any existing source — exactly what this pass's instructions prohibit ("do not invent missing rubric concepts"). **Partial version (semantic + concept-coverage vectors only, properly FAISS-indexed rather than embedded ad hoc) would not change the reported numbers** — `concept_detection`/`semantic_score` already use the identical embedding computation whether the vectors are pre-indexed or computed on demand; indexing them permanently would only change performance/caching, not the score. So a "safe" version of option (a) reduces to population C above, already produced.

**(b) Exclude the mismatched cases from the primary analysis; report the matched-32 subset as primary, with the diagnostic rescore as a clearly labeled sensitivity check.** Fully feasible now, invents nothing, uses only already-existing data, and is the most defensible option available without new authoring work. **Recommended as the default for any citation until (a) or (c) is completed.**

**(c) Author a new, versioned benchmark (replace the 4 stale cases with 4 new ones matched to the current live bank, or re-collect ratings for corrected versions of the same 4 questions).** Requires either new human ratings (a real, non-trivial data-collection exercise — 3 raters × 32 new cases, matching the original protocol) or accepting a smaller, asymmetric benchmark. **Requires human/author decision and new data collection; not something this pass can execute.**

## Decision

**This pass adopts (b) as the interim default and does not execute (a)-in-full or (c).** Both require either inventing rubric content this pass has no authority to invent, or new human data collection this pass cannot perform. This is the "stop before that step, produce a precise decision document" case the eighth-pass instructions anticipated.

## What the author/mentor needs to decide

1. Whether to commission new `mandatory`/`common_mistakes_addressed`/bonus content for the 4 affected questions (enabling a full option-(a) repair), and who authors it (should not be the same process that also grades the resulting benchmark, per this project's own same-agent-independence concerns already raised for P1).
2. Whether P2 (on hold for separate reasons) should be updated to cite population A (ρ=0.655, n=32) instead of the original ρ=0.3812/0.3787/0.3728 figures if/when P2 is ever revived — not decided or executed here, since P2 remains out of scope for this pass.
3. Whether `CLAUDE.md`'s and `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`'s "current human result: ... rho 0.3812" line should be annotated or superseded — both are explicitly protected; this pass proposes no edit, only flags it (again, as the seventh pass did) for the required separate approval process.

## Reproducibility

```
.venv/Scripts/python.exe research/paper_strengthening/scripts/eighth_pass_independent_reverification.py
```
Full per-case data: `research/paper_strengthening/results/eighth_pass/independent_reverification.json`. Every number in the table above traces to that file's `correlations.matched_subset_stale`, `correlations.mismatched_subset_stale`, and `correlations.mismatched_subset_adhoc_rescored` keys.
