# Viva / Project Evaluation Preparation Document

Likely panel questions with technically accurate, evidence-grounded answers. Answers are deliberately honest about limitations — per this project's own integrity discipline, no answer here claims more than the project's actual evidence supports. Cross-references point to the full report (`final_deliverables/02_University_Project_Report/`) and testing package (`testing_and_evaluation/`) for detail.

## Architecture

**Q: Walk me through what happens when a candidate submits an answer.**
A: The event arrives over WebSocket at the FastAPI backend (a thin dispatcher, no logic), which calls the orchestrator. The orchestrator serialises the call via an `asyncio.Lock`, routes verbal answers to the Flask evaluator (SBERT+FAISS+CrossEncoder) or code answers to the Docker sandbox, applies the Score Validator's deterministic correction rules, builds a 6-D state vector and consults the PPO policy + guardrails for the next difficulty, assembles 15-field feedback (calling Qwen only if the score is ≤0.65), selects the next question via rule-based difficulty/topic matching, and logs the turn. Full sequence diagram: report Chapter 7.

**Q: Why a single orchestrator instead of a true multi-agent system?**
A: It was designed this way for state-integrity reasons — a single authoritative writer avoids the coordination/arbitration complexity a real multi-agent design would introduce. We also explicitly investigated and excluded an unverified proposal for a true multi-agent "bounded authority" layer described in a supplied research-paper draft, because it does not exist in the codebase — see the next question.

**Q: I was told this system has a multi-agent coordination layer with a Strategy and Coaching agent. Where is that?**
A: It isn't implemented. A research-paper draft describing exactly that was supplied alongside the project materials; we independently verified, by direct code search, that no such layer, no arbitration module, and none of that draft's specific experimental results exist in this codebase. We excluded it from both the report and the IEEE paper rather than present it as real. This is disclosed explicitly, not something we're hiding — see report Chapter 10 §10.13.

**Q: Is the evaluator FastAPI or Flask?**
A: Flask. An earlier version of our own documentation said FastAPI; we found and corrected this discrepancy by reading the actual code (`app = Flask(__name__)`). The Qwen microservice genuinely is FastAPI.

**Q: Does question selection use semantic search / embeddings?**
A: No. We originally documented it as FAISS-based retrieval; direct code inspection found zero embedding dependency in `question_selector.py` — it's a deterministic nearest-difficulty-match plus topic-rotation algorithm. The FAISS index in the project is used only by the evaluator, for concept coverage within an answer, not for picking questions.

## Machine Learning / Evaluator

**Q: How accurate is your evaluator?**
A: Against a 64-answer, 8-question, 3-rater human benchmark, the full composite score correlates with human judgment at Spearman ρ=0.38 — moderate, and explicitly below simpler sub-combinations (R-alone ρ=0.48, S1+R ρ=0.49). We don't claim high accuracy; our own evidence record frames the composite as "safety-hardened rather than accuracy-optimal" — the extra component (concept coverage) trades some correlation for interpretability and keyword-stuffing resistance. We say this plainly rather than cite a flattering but unrepresentative number.

**Q: Qwen is an LLM — how do you know its output is correct?**
A: We don't claim to, for its text output specifically — and that's a deliberate, verified design property, not an oversight. Qwen never touches the numeric score (verified directly in code: the score is set before Qwen is called and never reassigned from its response). It only generates narrative feedback text, hints, and follow-up questions. The score's correctness story relies entirely on deterministic, inspectable components, not on trusting an LLM's self-judgment. Full detail: `testing_and_evaluation/Qwen_2.5_Viva_Explanation.md`.

**Q: What happens with adversarial or malformed input?**
A: Tested directly in this phase against 10 constructed cases (empty, whitespace, 16.5k-character keyword spam, garbled Unicode, SQL-injection-like text, an HTML script tag, emoji spam, punctuation-only, plus a correct-answer control): the evaluator never crashed and always returned a score in [0,1].

**Q: What's the CrossEncoder's training provenance?**
A: Incompletely documented — disclosed in our own evidence record as a "partially fine-tuned derivative" with incomplete training-data/hyperparameter records, not "off-the-shelf" as an earlier description claimed. We do not overstate this; it's an open item.

## Reinforcement Learning / PPO

**Q: How was the PPO policy trained?**
A: Stable-Baselines3 PPO, `MlpPolicy` [64,64], 24,576 timesteps per training seed, five training seeds (42/123/456/789/999). This corrects our own prior documentation, which claimed "500,000 steps" and different seeds — we found that figure traces to no stored artifact and replaced it with the verified one.

**Q: Does PPO actually improve the system, or is it the guardrails?**
A: Our own prior frozen research evidence already established that the guardrail layer — not the policy — accounts for essentially all of the measured tracking-accuracy improvement over a fixed-difficulty baseline; "PPO improves tracking" is a claim our own evidence record has explicitly withdrawn. This phase's new testing is consistent with that: we found a real defect specifically in the guardrail layer (not the policy), reinforcing that guardrails are this system's primary, and most safety-critical, mechanism.

**Q: What's the guardrail defect you found?**
A: Testing the real, deployed PPO checkpoint against constructed candidate states, we found a below-average-scoring candidate (score 0.35) got a raw "Harder" action from the policy. Systematically testing the five guardrail rules' boundaries confirmed none of them cover performance scores in [0.30, 0.40) — a genuine gap between two adjacent rules' thresholds. We fixed it with a single-condition change (widening one rule's lower bound from 0.40 to 0.30), verified 13/13 boundary cases pass, and reran the full 283-test suite to confirm zero regressions.

**Q: Why didn't you catch this with the existing test suite before?**
A: The existing suite exercises typical, not adversarially-constructed, scenarios — this is exactly why we added direct, boundary-targeted testing against the real policy and guardrail function as a new testing category in this phase, rather than relying only on end-to-end functional tests.

**Q: Did you retrain PPO or change the reward function?**
A: No — explicitly out of scope and governed by the project's own experiment-preregistration policy. We only touched the guardrail layer (a deterministic post-inference override), not the policy or its training.

## Testing Methodology

**Q: How many tests, and what's the pass rate?**
A: 264 of 283 automated tests pass (93.3%), plus 28/28 frontend tests. Every one of the 19 non-passing tests is fully attributed: 18 to the Docker daemon not running in our test environment (an environment gap, not a code defect — the underlying sandbox configuration was independently verified correct by code review), and exactly 1 to a single, pre-existing, already-documented issue we deliberately did not alter.

**Q: What's novel about your testing approach versus just running the existing suite?**
A: We wrote 11 new, independently executed scripts that call production code directly rather than through end-to-end flows — this is specifically what surfaced the guardrail gap and the launcher crash, neither of which the existing suite's typical-scenario tests had caught.

**Q: What did you find and fix, concretely?**
A: Two real defects: the guardrail coverage gap above, and a Windows-specific crash in `launch.py` (an unguarded Unicode character crashing the process right after successful service startup, fixed by reconfiguring stdout to UTF-8). Both fixes were verified individually and via full regression testing.

## Limitations

**Q: What hasn't been validated?**
A: No formal human-subject usability or learning-outcome study (explicitly identified as the most significant outstanding gap, in both the Phase-2 report and this phase); no word-error-rate measurement of the audio pipeline (no verified reference-transcript dataset exists); Qwen's narrative-text quality has no quantitative human-rated evaluation; 18 Docker-dependent tests remain unexecuted pending a running daemon; one pre-existing test failure remains unresolved by deliberate choice.

**Q: Why didn't you just fix the one remaining known test failure?**
A: It's pre-existing and already flagged in the project's own documentation as an open, undecided issue — we reproduced it identically and left it as-is rather than make a unilateral interpretive call about how to resolve it, consistent with the project's stated policy on unresolved issues.

## Process / Integrity

**Q: Were there factual errors in the earlier project report?**
A: Yes — we found and corrected nine, each backed by direct code evidence, not assumption: training step count/seeds, the evaluator's fallback-chain description, an unverified ablation-study section, unverified calibration-experiment numbers, RL action-space size, the FAISS-retrieval claim, the evaluator's web framework, an unsupported headline accuracy figure, and the Qwen partial-credit claim. All nine are documented with evidence in `reference_material_analysis/Previous_Project_Report_Analysis.md` and corrected throughout the current report.

**Q: A separate paper draft was in your project materials describing much more sophisticated results. Why isn't that your IEEE paper?**
A: Because its central results — a two-agent coordination layer and four experimental campaigns — don't exist in this codebase. Submitting it as our IEEE paper would mean presenting fabricated results. We verified this independently, excluded that material, and wrote a new paper around the real guardrail-gap finding instead, which is smaller in scope but genuinely true.
