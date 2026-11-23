# Evaluator human-gold benchmark — repair package (ninth pass)

**Status: a proposal and a safe interim artifact set. The frozen benchmark (`research/data/evaluator_benchmark/{benchmark_dataset.csv,final_human_gold.csv}`) is unmodified and remains the sole authoritative source. Nothing here has been applied to it.**

## Contents

| File | What it is |
|---|---|
| `qid_mapping.json` | All 8 question IDs, the benchmark's stored question text, the current live `qns.json` question text for that same qid, and whether they match exactly. Machine-readable, regenerable from `ninth_pass_build_benchmark_repair_package.py`. |
| `affected_cases.json` | The 32 cases (4 questions) whose current production `get_rubric(qid)` scoring is invalid, with the reason, and an explicit note that the human gold rating itself is **not** affected (raters read the benchmark's own stored text, never `get_rubric(qid)`). |
| `proposed_corrected_schema.json` | A proposed v2 schema for a future corrected benchmark file (not applied), plus the exact list of rubric fields that would need new human-authored content before a full repair is possible. |
| `matched_subset_evaluation.json` | The recommended citable evaluator/human-gold estimate for now: full production scoring on the 32 cases (4 questions) whose qid is still correct. |

## The affected cases, at a glance

| qid | Benchmark's question | 8 case IDs |
|---|---|---|
| 7 | "How do you determine the number of distinct ways to climb n stairs...?" | BM-033, BM-034, BM-035, BM-036, BM-037, BM-038, BM-039, BM-040 |
| 15 | "Explain how Depth First Search (DFS) detects a cycle in a directed graph." | BM-041, BM-042, BM-043, BM-044, BM-045, BM-046, BM-047, BM-048 |
| 22 | "Explain the binary search algorithm and its preconditions." | BM-049, BM-050, BM-051, BM-052, BM-053, BM-054, BM-055, BM-056 |
| 50 | "What is a race condition in multithreading and how do you prevent it?" | BM-057, BM-058, BM-059, BM-060, BM-061, BM-062, BM-063, BM-064 |

(Copied directly from `affected_cases.json`/`qid_mapping.json`'s generated output, not retyped by hand from memory, to avoid a transcription error — verify against those files if this table and the JSON ever diverge after a regeneration.)

## Human annotation and adjudication protocol (for a future full repair)

This protocol applies **only if/when the author commissions new rubric content or new ratings** — it is written now so that decision, if made, has a ready-to-use procedure rather than requiring one to be designed from scratch under time pressure later.

1. **Content authoring, independent of grading.** The person who authors the missing `mandatory_concepts`/`common_mistakes_addressed`/bonus content for the 4 affected questions must not be the same person (or AI session) who will later serve as one of the 3 human raters or who tunes the evaluator against the result — mirroring the same same-agent-independence concern already raised for P1 in this project.
2. **Content basis.** New rubric content must be derived from the question's `reference_answer` already stored in `benchmark_dataset.csv` (for the semantic/concept fields) plus genuinely new authoring for `mandatory_concepts` and `common_mistakes_addressed` — the latter is new content and must be labeled as such, not presented as recovered original content.
3. **Re-indexing.** Once authored, embed and add the new vectors to a **new, versioned** FAISS index (not an in-place edit of `services/evaluator/assets/logic_vectors.faiss`), so the change is reviewable and reversible before being adopted as production.
4. **Re-rating decision.** Decide whether the existing 3 raters' original scores for these 32 cases remain valid (they rated the benchmark's own stored answer text against the question, which does not change) or whether re-rating is wanted because the rubric itself changed. If the rubric changes materially (e.g., a different weighting of what counts as "complete"), a re-rating pass with the same 3-rater/adjudication design already used for the other 32 cases is the consistent choice.
5. **Disagreement/adjudication.** Reuse the existing `final_human_gold.csv` methodology exactly: 3 raters, `max_pairwise_difference` computed, `adjudication_required` flagged per the same threshold already used for the other 56 cases (do not invent a new threshold for these 32 alone).
6. **Blinding.** Raters should not be told which cases are the "repaired" ones, to avoid a demand-characteristic bias toward giving these cases more scrutiny or leniency than the original 32.
7. **Provenance record.** Record rater identity/qualification, relationship to the development team, and the exact protocol version with the new ratings, since this is already a documented gap for the *original* 64-case benchmark (`D1_FINAL_BLOCKER_ASSESSMENT.md`) and should not be repeated for the repair.

## How future results should be reported

- **Do not** cite "ρ=0.3812" (or 0.3787, 0.3728) as a general evaluator-quality figure without the qid-mismatch caveat; those numbers were computed on the pre-repair, partially-broken instrument.
- **Until a full repair is completed**, cite `matched_subset_evaluation.json`'s result: **ρ=0.655 (95% CI [0.499, 0.809], question-clustered bootstrap, n=32 cases / 4 questions), full production scoring, no shortcuts** — and always state the reduced sample size (4 of the originally-intended 8 questions) alongside it.
- **Never** cite the ~0.700 diagnostic ad hoc rescore (mismatched cases only, reduced-fidelity scoring) as a validated or production-equivalent number; if cited at all, it must appear only as an explicitly labeled sensitivity/diagnostic estimate, never merged with the matched subset into one blended number.
- **After a full repair** (re-indexed rubrics, decision on re-rating made and executed), report the new full-8-question estimate as a **new benchmark version** (e.g. "v2"), with the v1/v2 distinction stated explicitly in any manuscript that cites it, and the v1 numbers preserved for comparison, not deleted.

## Reproducibility

```
.venv/Scripts/python.exe research/paper_strengthening/scripts/ninth_pass_build_benchmark_repair_package.py
```
Regenerates every JSON file in this directory from the frozen source files and the live production evaluator/rubric bank. No frozen file is written to.
