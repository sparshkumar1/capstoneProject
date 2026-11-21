# Qwen 2.5 — Viva Explanation

Companion to `Qwen_2.5_Evaluator_Validation_Report.md` (full investigation with code evidence). This document is the condensed, defend-in-the-room version.

## 1. Simple explanation (one paragraph, say this first)

"Qwen 2.5 does not grade anything in PrepAIred. The numeric score is computed by three deterministic, non-generative components — semantic similarity, concept coverage, and reasoning quality — combined by a fixed formula. Qwen is only called afterward, to write the human-readable feedback text, generate a hint if the candidate asks for one, or generate a follow-up question. We verified this directly in the code: the score variable is set before Qwen is even called, and Qwen's response is never used to change it."

## 2. Technical explanation of the evaluator architecture

Score = `0.15·S1 + 0.35·S2_eff + 0.50·R` + bonus − penalty, capped if a mandatory concept is missed.
- **S1** = SBERT cosine similarity (deterministic embedding model).
- **S2** = FAISS nearest-neighbour concept-coverage match against a rubric concept index (deterministic).
- **R** = a fine-tuned CrossEncoder relevance score (deterministic once weights are frozen).
- **Score Validator** applies deterministic post-hoc rules.
- **Qwen** is invoked separately, afterward, only for text generation (narrative feedback, hints, follow-ups) — confirmed by direct code inspection to never write back into the score.

## 3. How correctness of Qwen's output is independently verified

It isn't, for text quality specifically — and we say that plainly rather than overclaim. What *is* independently verified: the score itself (the part that actually determines pass/fail/grade) never depends on Qwen, so an incorrect or low-quality Qwen output cannot produce an incorrect grade — only a less helpful piece of feedback text, hint, or follow-up question.

## 4. What reference data and rubrics are used

A human-authored rubric per question (concept groups, mandatory concepts, a model answer) drives S1/S2. A separate, frozen 64-answer/8-question/3-rater human benchmark validates the deterministic score's agreement with human judgment (ρ=0.38 composite — openly below R-alone or S1+R, which is this project's own existing, disclosed finding, not something to hide).

## 5. Quantitative metrics actually used

Spearman ρ against human raters (score validity, not Qwen-specific). API-contract pass/fail tests and content-pattern checks for Qwen (does feedback differ appropriately between a strong and a weak answer) — structural, not a graded-quality metric. No MAE/accuracy/F1 exists for Qwen's text quality — stated honestly as a gap, not fabricated.

## 6. What happens when Qwen produces an incorrect or unsupported output

The grade is unaffected, by construction (see §2–3). If the Qwen *service* is unreachable, both the hint and feedback paths return an explicit "unavailable" state with a truthful message — never a fabricated hint or fabricated feedback. If Qwen *is* reachable but its text content is wrong or ungrounded, there is currently no automatic fact-check layer catching that — a genuine, disclosed limitation.

## 7. Why multiple evaluation signals beat relying on an LLM alone

This is the same principle the AutoSCORE paper (Wang et al. 2025, in this project's literature review) demonstrates empirically: decomposed, specialist scoring with a validating layer outperforms monolithic LLM judgment. PrepAIred goes one step further for the numeric score specifically — it doesn't use an LLM judgment for the score at all, removing the LLM-hallucination risk from the grading decision entirely, while still using an LLM where it's actually useful: generating readable, candidate-facing explanations.

## 8. Suggested concise answer if asked directly in the viva

*"We don't validate Qwen as an evaluator, because it isn't one in this system — the score comes entirely from deterministic components we can and did test directly. Qwen only writes the explanation. We verified this isn't just a design intention but the actual code behavior, by checking that the score variable can never be reassigned from Qwen's output anywhere in the codebase."*

## 9. Likely follow-up questions and honest answers

**Q: "So why use an LLM at all if it's not trusted for scoring?"**
A: Because deterministic scoring components produce a number and a concept-coverage list, not fluent, candidate-readable prose explaining *why*. Qwen is used for exactly the part it's good at (natural-language generation) and kept away from the part where hallucination would be costly (the grade).

**Q: "Could Qwen's bad feedback text mislead a candidate even if the score is correct?"**
A: Yes — that's a real, disclosed limitation (§6). We have no automated fact-check on Qwen's generated text; this is identified as future work, not claimed as solved.

**Q: "Did you validate this with real users?"**
A: No. No human-subject study has been conducted on this system, period — this is disclosed in both the project report and this document, not specific to Qwen.

**Q: "How do you know the deterministic score itself is 'correct', not just 'not-Qwen'?"**
A: We don't claim it's highly accurate — our own evidence shows moderate correlation (ρ≈0.38) with human raters on a small benchmark, explicitly framed as "safety-hardened rather than accuracy-optimal" in our own evidence record. We claim it's *deterministic and inspectable*, which is a different and more defensible property than "accurate," and is what this answer is really about.
