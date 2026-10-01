# Synthetic Category-Discrimination Benchmark for the Hybrid Evaluator — Execution-Ready Protocol

**Status: complete protocol, NOT executed.** No synthetic answer has been generated beyond the worked examples in §5 (illustrative only, drawn from already-existing rubric content, not scored). No model has been called. This becomes runnable once hashed, git-tagged, and its run manifest approved, per `CLAUDE.md`. This is identified as the single most valuable next experiment (see `EXPERIMENT_PLAN.md`, revised ranking) and is accordingly the one prepared to full execution-readiness, as instructed.

## 0. Why this design, and why it supersedes relying on the existing human benchmark alone

The existing 64-item human-rated benchmark has 8 independent units (questions) — its own documentation already states results from it cannot support a general validity claim, and the question-clustered reanalysis in `EXISTING_EVIDENCE_ANALYSIS.md` shows exactly why (wide, overlapping CIs; one or two questions can dominate the result). This design replaces the constraint of needing three human raters per item — which is what pins the unit count at 8 — with a **categorical ground truth that is true by construction**: an answer authored to contain a specific, named rubric mistake is a member of the "misconception" category by definition, not by anyone's rating. This allows the independent-unit count to scale to dozens of questions using only already-existing, already-authored rubric content, with no new human involvement of any kind.

This design does **not** replace the human benchmark or its finding; it answers a different, complementary question (can the evaluator discriminate formal answer categories, at scale) rather than the same question with more data (how well does it track a human's continuous quality judgment). Both should be reported side by side, clearly labeled as answering different questions.

## 1. Category taxonomy (7 categories, matching the requested design)

| Category | Definition | Deterministic construction rule |
|---|---|---|
| C1 — Correct & complete | Covers all mandatory concepts and semantic targets, correctly connected | Built from the rubric's own `semantic_targets` and `logic_markers.mandatory` fields |
| C2 — Valid paraphrase | Same content as C1, reworded | C1 rewritten with different sentence structure/vocabulary, same facts |
| C3 — Partial/incomplete | Covers some but not all mandatory concepts | C1 with one or more `logic_markers.mandatory` entries deliberately omitted |
| C4 — Keyword-stuffed | Mentions concept/mandatory terms without connecting reasoning | The rubric's own `concept_groups`/`mandatory` terms listed as a flat enumeration, with no causal or logical connective between them |
| C5 — Misconception | Contains a specific, identifiable technical error | Built directly from one entry in the rubric's own `common_mistakes` field — the "error" is authored by whoever wrote the rubric, not invented for this benchmark |
| C6 — Contradictory reasoning | Asserts a correct point, then negates or contradicts it in the same answer | C1's core claim followed by an explicit negation of that same claim |
| C7 — Irrelevant | Off-topic or non-answer | A fixed, topic-independent non-answer template (e.g., a generic restatement of the question with no technical content), not a random answer to a different question, since that would confound with "wrong-topic-but-competent" answers not in scope here |

Every category's ground-truth label is fixed at construction time by which rule produced it — no post-hoc judgment call is needed, and no rater is involved.

## 2. Sampling frame and unit of independence

- **Source:** `data/rubrics/rubrics_final_clean.json` (125 already-existing, already-authored questions; confirmed in this pass to have 37 distinct topics, 5 `type` values — theory 50, logic_approach 40, evaluate 15, general_tech 10, code 10 — and 100% coverage of `common_mistakes` and `logic_markers.mandatory` fields, which this design depends on).
- **Unit of independence: the question (`qid`)**, matching how the existing human benchmark is already analyzed (`EXISTING_EVIDENCE_ANALYSIS.md`), so the two benchmarks' results are methodologically comparable.
- **Target sample:** 30 questions (a >3x increase in independent units over the existing 8), stratified: at least 4 questions from each of the 5 `type` values, and no more than 3 questions sharing the same `topic` value, to avoid over-representing any one topic (e.g., `C_Programming` and `Arrays`, which are disproportionately large in the source file).
- **Selection procedure:** stratified random sample with a fixed, disclosed seed, drawn once and frozen before any answer is written. (Seed and exact qid list to be generated and recorded at protocol registration, not chosen after seeing which questions "work well.")
- **Items per question:** one answer per category (7) per question (30) = **210 items total**, each independently labeled by construction.

## 3. Held-out split (fixed before any scoring)

- Of the 30 sampled questions, **10 are designated development questions** (for confirming the generation templates actually produce answers that read as intended — a human sanity check on realism, not on evaluator behavior — and for catching construction errors before the confirmatory run).
- The remaining **20 are the held-out confirmatory set**, scored exactly once, with no template or category-construction change permitted afterward without registering a new, separate experiment.
- The development/held-out split is drawn with the same fixed seed as the question sample, before any answer text is written.

## 4. Pre-registered hypotheses (confirmatory, tested only on the 20 held-out questions)

Stated as directional, falsifiable claims, each tested via a question-clustered (by `qid`) paired comparison or ranking test, with Holm–Bonferroni correction across the family of 7 tests:

- **H1:** `final_score(C1)` > `final_score(C3)` (complete beats partial)
- **H2:** `final_score(C3)` > `final_score(C7)` (partial beats irrelevant)
- **H3:** `final_score(C1)` > `final_score(C5)` (complete beats misconception)
- **H4:** `final_score(C1)` > `final_score(C4)` (complete beats keyword-stuffed — this is the specific claim the dampening mechanism, Eq. 3, exists to guarantee)
- **H5:** `S2(C4)` is not significantly lower than `S2(C1)`, **but** `final_score(C4)` is significantly lower than `final_score(C1)` — i.e., concept coverage alone is fooled by keyword-stuffing, but the full evaluator (via reasoning verification and dampening) is not. This is the single most direct, targeted test of whether the hybrid architecture's specific design rationale (stated in §IV.B of the manuscript) actually holds.
- **H6:** `final_score(C1)` is **not** significantly different from `final_score(C2)` (paraphrase robustness — the evaluator should not penalize correct answers merely for different wording)
- **H7:** `final_score(C7)` is lower than every other category's score (irrelevant answers are the clear floor)

Each hypothesis has a pre-specified direction; none is stated as "test whether A and B differ" without a predicted direction, which would invite post-hoc interpretation.

## 5. Worked examples (illustrative only — not scored, not used as evidence)

Using qid 1 (Two-Sum / Arrays, already shown in the rubric file):

- **C1 (correct):** "You iterate through the array once, and for each element check whether its complement — the target minus the current value — already exists in a hash map. If it does, return the two indices; otherwise store the current value's index in the map before moving on."
- **C4 (keyword-stuffed):** "Hash map. Complement calculation. Single pass. O(n) time complexity. Store index not value." (the rubric's own mandatory/bonus terms, no connecting reasoning)
- **C5 (misconception):** "You use two nested loops to check every pair of elements against the target, which works because you check every possible combination." (this is the rubric's own listed common mistake — "uses nested loops instead of hashing" — restated as an answer)
- **C7 (irrelevant):** "This question is about arrays, which are a fundamental data structure used in many algorithms." (generic, no technical content addressing the actual problem)

These four are shown to demonstrate the construction rules produce clearly distinguishable text; the full 210-item set is not created until this protocol is approved.

## 6. What requires approval, and what does not

| Step | Approval needed? |
|---|---|
| Freezing the qid sample, dev/held-out split, and category-construction templates | No — this is text/document design, touches no model, no frozen artifact |
| Writing the 210 answer texts (or a generation script that renders them deterministically from the rubric fields) | No — text authoring, still touches no model |
| Running the 210 texts through the live SBERT / FAISS / CrossEncoder pipeline to obtain S1/S2/R/final_score | **Yes — full approval required.** This is new model inference producing new empirical claims about the deployed evaluator, squarely inside `CLAUDE.md`'s "no new experiment without a hashed, git-tagged protocol and an approved run manifest" rule, even though no human subject or new training is involved |
| Running the confirmatory statistical tests (H1–H7) on the held-out set once scores exist | Covered by the same approval as the scoring run — it is the analysis step of the same experiment, not a separate one |

## 7. Run manifest fields (for when approved)

Git commit at run time; evaluator config file and hash (`services/evaluator/app.py` state, or its frozen config equivalent); CrossEncoder checkpoint hash (already on record: `6a241a55…`); the frozen qid list and its selection seed; the frozen dev/held-out split; date; operator; a note confirming no evaluator code was changed between this run and the frozen Paper-2 run it is compared against (or, if the environment's dependency-pin mismatch noted in `EVIDENCE_AUDIT.md` §5 has not been resolved, an explicit statement that this run shares that same environment caveat).

## 8. Stopping and integrity rules

- No template, category assignment, or hypothesis is altered after the 20 held-out questions are scored. Any change requires registering a new experiment.
- No item is discarded post-hoc for producing an inconvenient score.
- The 10 development questions may be re-templated as many times as needed *before* the held-out run; the held-out run itself happens exactly once.
- If a construction rule turns out to be ambiguous or broken on a development question (e.g., a "keyword-stuffed" template that accidentally reads as coherent reasoning), fix the rule using only the development set, document the fix, and only then freeze it for the held-out run.

## 9. What this experiment would, and would not, establish if run

**Would establish** (if the confirmatory hypotheses hold): that the hybrid evaluator's stated anti-gaming design (dampening low-reasoning concept coverage, Eq. 3) functions as intended against constructed adversarial-style inputs, at a scale (30 questions) that supports a more general claim than the existing 8-question human benchmark can.

**Would not establish:** anything about how well the evaluator's *continuous* score matches a human's *subjective* quality judgment (that remains the human benchmark's role, exploratory, 8 questions, unaffected by this design), nor anything about real candidate behavior, nor — per this project's standing rule — any claim stronger than what a controlled, synthetic, non-human-subject evaluation can support.
