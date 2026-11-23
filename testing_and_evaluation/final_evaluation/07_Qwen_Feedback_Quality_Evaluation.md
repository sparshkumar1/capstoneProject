# Qwen Narrative Feedback Quality Evaluation — Final Evaluation Phase

**Scope and honesty statement, per this phase's explicit instruction:** this is a **single-reviewer, structured, criteria-based qualitative review** of real, live-captured Qwen outputs. It is **not** a blinded, multi-rater human study (no independent human reviewers were available in this phase), and no human quality ratings were fabricated. Where a judgment below is a qualitative assessment rather than an automated check, it is stated as such. This evaluation is new — the prior testing package explicitly disclosed that no Qwen output-quality evaluation of any kind existed before this phase.

**Samples evaluated:** 4 real, live calls to the actual running Qwen2.5-1.5B-Instruct GGUF service (not mocked, `mock_mode: false` confirmed at call time), covering the 3 LLM-backed response types the project actually has (`feedback`, `followup`) plus the 2 template-only types discovered this phase (`hint`, `report` — see §4). Raw evidence: `testing_output/Testing_Evidence/QWEN_QUALITY_SAMPLES.json`, `QWEN_POSTFIX_feedback_strong.json`.

## 1. Rubric

| # | Criterion | Definition used |
|---|---|---|
| 1 | Factual correctness | Does the generated explanation itself state true facts about C/pointers? |
| 2 | Relevance | Does the output address the actual question and the candidate's actual answer? |
| 3 | Grounding | Is every claim traceable to the `structured_evaluation`/`candidate_answer` input, not invented? |
| 4 | Specificity | Concrete and concept-specific, not generic filler? |
| 5 | Actionability | Does the candidate know exactly what to do differently? |
| 6 | Clarity | Readable, unambiguous prose? |
| 7 | Unsupported claims | Any assertion not backed by the input data? |
| 8 | Contradictions | Internal consistency between fields (e.g. `what_was_correct` vs `narrative_feedback`)? |
| 9 | Repetition | Needless restatement across fields? |
| 10 | Follow-up appropriateness | (follow-up only) Does it target a genuine gap? |
| 11 | Hint usefulness | (hint only) Does it help without giving the answer away? |
| 12 | Consistency | Same input style → comparably structured output? |

## 2. Feedback Generation (`/api/qwen/feedback`) — Genuinely LLM-Sourced

### Sample A — strong, correct answer (post-fix capture, real model, `decision_source: qwen_1.5b_llm`)

> *narrative_feedback:* "The candidate provided a factual summary of pointer arithmetic in C. The final score of 0.88 indicates an excellent understanding of the topic. The candidate's explanation was clear and concise, but could benefit from a more detailed explanation of how pointer arithmetic works, including the concept of pointer size and how it affects the increment value."

| Criterion | Assessment |
|---|---|
| 1. Factual correctness | **Pass.** No false claims in the narrative text itself. |
| 2. Relevance | **Pass.** Directly addresses the actual answer given. |
| 3. Grounding | **Pass** for `narrative_feedback` and `how_to_answer` (both restate the candidate's own correct content). **Fail** for two other fields — see §3 below. |
| 4. Specificity | **Partial.** "could benefit from a more detailed explanation... including the concept of pointer size" is somewhat generic — the candidate's answer *already* explained pointer size scaling explicitly, so this specific suggestion is weakly grounded, bordering on criterion-7 territory. |
| 5. Actionability | **Weak.** "provide a more detailed explanation" doesn't specify what additional detail, given the answer was already fairly complete. |
| 6. Clarity | **Pass.** |
| 9. Repetition | `stronger_answer_guide` and `actionable_improvements` restate near-identical content ("a senior engineer should provide a detailed explanation..." / "provide a more detailed explanation...") — mild redundancy across fields. |

### Sample B — weak, factually wrong answer (pre-fix capture, real model, `decision_source: qwen_1.5b_llm`)

> *narrative_feedback:* "The candidate provided a general attempt but missed the key difference between a dangling pointer and a null pointer. The final score of 0.15 indicates an average understanding. The candidate should clarify that a dangling pointer is a pointer that has been allocated memory but has not been assigned a valid address, while a null pointer is a pointer that has not been allocated memory and is therefore considered invalid."

| Criterion | Assessment |
|---|---|
| 1. Factual correctness | **FAIL — a genuine, concrete finding.** The model's own corrective explanation is technically confused: a dangling pointer is standard-CS-terminology for a pointer referencing memory that has been **freed/deallocated** (matching exactly the `missing_concepts: ["freed memory", "undefined behavior"]` the evaluator itself supplied as input) — not "allocated memory but not assigned a valid address," which is not a standard or coherent definition. The model was given the correct target concept in its input and still generated an incorrect restatement of it. |
| 2. Relevance | **Pass.** Correctly identifies that the core distinction was missed. |
| 3. Grounding | **Partial.** Correctly uses the input's `incorrect_claims` framing ("missed the key difference"), but the specific corrective content it generates is not grounded in — and actively contradicts — the `missing_concepts: ["freed memory"]` field it was given. |
| 4–6 | Reasonably specific, moderately actionable (tells the candidate the two concepts to distinguish), clear prose. |
| 7. Unsupported claims | **FAIL**, same issue as criterion 1 — the specific definition offered is not supported by (and conflicts with) the ground-truth concept the evaluator supplied. |
| 8. Contradictions | None found between fields in this sample (score 0.15 and "average understanding" language is slightly inconsistent — 0.15 is well below the evaluator's own documented "Average" band of ≥0.40, so calling it "average understanding" in prose under-states how far off the answer was — a minor score-to-language calibration issue, not a hard contradiction since no numeric grade field was echoed incorrectly here). |

**This is the single most important finding of this evaluation:** the model can generate fluent, well-structured, plausible-sounding *corrective* text that is itself factually wrong, even when the correct concept label was already provided to it as input. This is a real, substantive quality limitation, not a formatting bug, and is distinct from (and in addition to) the character-splitting defect fixed in `Application_Code_Changes.md`.

## 3. Grounding Failures Found in Structured Fields (Sample A, post-fix)

Independent of the narrative text, two of the **structured** (non-prose) fields in Sample A contain content that does not correspond to anything in the actual input, discovered only after the character-split bug was fixed (the scrambled pre-fix output made this impossible to assess):

- `"what_was_incomplete": ["Final Score: 0.88 (Excellent)"]` — a score restatement, not a description of what part of the *answer* was incomplete. Category error: the field is being used to echo metadata instead of its intended content.
- `"missing_concepts": ["General attempt"]` — the actual `structured_evaluation.missing_concepts` input for this sample was an **empty list** (`[]`, the answer was complete). The model invented a "missing concept" that is not a concept at all, for an answer that had none. This is a genuine, narrow **hallucination** — the model asserted content not present in, and contradicted by, its own structured input.

**This is a second, distinct, newly-discovered Qwen output-quality defect**, not fixed in this phase (per the instruction to document rather than silently patch every finding, and because fixing it would require prompt-engineering or model-output-validation changes beyond the narrow, already-approved scope of Change 1 in `Application_Code_Changes.md`). **Recommendation, not implemented:** extend `_validate_feedback_output()` (already present in `services/qwen/app.py`, currently checking narrative-text quality only) to also reject a response where `missing_concepts`/`what_was_incorrect` is non-empty but the corresponding evaluator-supplied input field was empty — this is a well-scoped, low-risk follow-up fix, deferred to keep this phase's actual code changes narrow and individually verifiable.

## 4. Hint and Report Generation — Not LLM-Sourced (Major Finding)

Direct code reading this phase (`services/qwen/app.py`, full functions) confirms `generate_hint()` and `generate_report()` are **pure Python f-string templates** — they never call the LLM, despite responses being labeled `decision_source: "qwen_hint"` / `"qwen_report"`, which reads as LLM-attributed.

**Consequence for this rubric:** criteria 10 ("follow-up appropriateness") and 11 ("hint usefulness") as originally framed by the task assume LLM-generated text; the hint sample evaluated here —

> "You have identified the initial setup. Consider how freed memory connects to the problem constraints and what invariant must hold."

— is in fact a fixed template (`f"You have identified {strong}. Consider how {missing} connects to the problem constraints and what invariant must hold."`) with only two words substituted (`strong`, `missing`) from the caller's input. It is **grounded by construction** (it can only ever say what the caller already told it) and **generic by construction** (the surrounding sentence never varies). This is neither a quality success nor failure in the LLM sense — it is a different kind of component entirely, and this phase's documents (§`05_ML_Evaluation_Results.md`, `Application_Code_Changes.md`) now say so explicitly rather than letting the misleading `decision_source` label stand uncorrected.

**This finding requires correction in prior deliverables produced earlier in this engagement** (the `Independent_Project_Audit`, the IEEE paper draft, and the presentation all describe Qwen's hint role as LLM-generated). See `14_Executive_Summary.md` for the full list and recommended correction text.

## 5. Follow-Up Generation (`/api/qwen/followup`) — Genuinely LLM-Sourced

> *followup:* "Could you explain how pointer arithmetic works in more detail, particularly focusing on how it affects the memory addresses?"
> *reason:* "This question addresses the candidate's gap by asking about the specifics of how pointer arithmetic affects memory addresses, which is a key aspect of understanding pointers."

| Criterion | Assessment |
|---|---|
| 10. Follow-up appropriateness | **Weak.** This sample was generated for a **strong, correct, complete** answer (`missing_concepts: []`) — there is no genuine gap to probe. The model nonetheless generated a follow-up framed around a "gap," which is not well-grounded in this specific input (a milder version of the same hallucination pattern found in §3). A better-grounded follow-up for a complete answer would probe depth/edge-cases rather than imply an unstated gap. |
| 2–6 | Otherwise relevant, specific, clear, and correctly scoped to the actual topic (pointer arithmetic). |

## 6. Consistency Across Samples

All 3 genuinely LLM-sourced samples (2 feedback, 1 followup) share the same field structure and a broadly similar register/tone — no wild structural inconsistency was found. The "gap invention" pattern (§3, §5) appeared in **2 of 3** LLM-sourced samples in this small batch, which is too small a sample to estimate a reliable rate, but is large enough to establish that the pattern is **real and reproducible**, not a one-off.

## 7. Latency (measured separately, not conflated with quality)

See `09_Performance_and_Reliability.md` for the full measurement. Summary: direct `/api/qwen/hint` calls (template-only, no LLM) averaged ~2.07s (n=5) in the earlier comprehensive testing phase — this is **network/process overhead, not LLM inference time**, now a materially important distinction given §4's finding that this endpoint never invokes the model at all.

## 8. Summary Verdict

Qwen's LLM-backed outputs (feedback, follow-up) are **relevant, clearly written, and correctly scoped to the actual question and topic** — genuine positive findings, now measured rather than assumed. They also exhibit **two concrete, reproducible quality limitations**: (1) generated corrective explanations can themselves be factually confused even when the correct concept was supplied as input (Sample B), and (2) structured fields can contain hallucinated content not grounded in the evaluator's input, particularly when there is genuinely nothing to report (Sample A's `missing_concepts`, the follow-up's implied gap). Neither limitation affects the numeric score (independently, separately re-confirmed never touched by Qwen — §`05_ML_Evaluation_Results.md` §6), but both are real limitations of the **narrative explanation layer** that a candidate actually reads, and should be disclosed in any academic write-up citing Qwen's output quality — not claimed as validated, and not hidden.
