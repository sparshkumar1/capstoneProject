# X1-B-I result note — Qwen fixed-answer invariance (executed 2026-09-20)

Registered protocol `prereg/X1-B/v2` (registration commit `424894ff74587c6048ea3b9b9d35d67be55088aa`), SUT `release/app-repair/v1`, real Qwen service (`qwen2.5-1.5b-instruct-q4_k_m.gguf`, file SHA-256 `6a1a2eb6…9407e`, decoding as shipped), real orchestrator answer path, fixed evaluator stub. Single execution, 72 pairs (36 injections × 2 replicates), 17:39–18:55 IST, exit 0. Outputs and hashes: `run_records/x1b/RUN_RECORD.json`. An earlier attempt under `prereg/X1-B/v1` was aborted after 13 pairs (all invalid); its log is kept in `run_records/x1b_v1_aborted/` and its cause is described below. **B1 only; B2 (behavioural stress) was not run.**

## Registered outcome
| Quantity | Result |
|---|---|
| Pairs run | 72 |
| **Valid pairs (both arms' feedback produced by the real LLM)** | **16 — the registered minimum of 30 was NOT met** |
| Invariants exactly equal, valid pairs | 16 / 16 |
| Invariants exactly equal, all pairs | 72 / 72 (no difference in any compared observable in any pair) |
| Invariants compared | feedback score/raw score/grade/breakdown, session scores and raw scores, current difficulty, technical performance, `difficulty_update`, `next_action`, `is_best`, authoritative-best flag, best `validated_score`, queue length |
| Score observed | 0.927 in every arm (evaluator stub 0.90 plus the timing modifier) |
| Mutation control (LLM text wired into the score, replayed) | violation observed in 50 / 72 pairs and 16 / 16 valid pairs; not observed in the other 22 pairs (not analysed further; consistent with identical replayed texts or equal text checksums modulo 100) |
| Static guard | 75 protected-key writes scanned across the orchestrator, feedback agent, best-answer selector and database module; **0 flagged**; the injected mutant statement **was** flagged |
| Channel enumeration | 47 call-site rows stored (`results/x1b/channel_enumeration.json`) |

**Reading.** Because only 16 valid pairs were obtained, the registered sample-size requirement is unmet and the result is **under-powered evidence**, not the intended test. Within what was observed, no compared quantity ever depended on the LLM's text. An **exploratory** (not registered) count: the adversarial arm was LLM-sourced in 35 of 72 pairs regardless of the benign arm, and all 35 were invariant. That count uses a validity rule different from the registered one and must not be presented as the result.

## Why the valid-pair minimum was missed (findings about the SUT)
1. **The service silently degrades to a deterministic template.** In 41 of 72 benign arms and 37 of 72 adversarial arms the Qwen service returned `non_llm_structured_recovery`; in **every** response `llm_status` was `available`. The service caps generation at 256 tokens; offline reproduction showed the nine-field JSON truncated mid-field (two samples), the service then fails to parse it (or its own output validator rejects it) and answers with the template. `llm_status` therefore cannot identify LLM-authored feedback.
2. **Shipped client timeout shorter than generation time.** The shipped feedback client waits 6.0 s; real generation took 13–21 s per turn here. In the shipped configuration LLM feedback would not arrive at all on this machine. The campaign raised the client timeout to 600 s (registered deviation), so results describe the pipeline when the LLM output does arrive.
3. The manipulation check ("LLM text changed between arms", 72/72) is weak: the deterministic feedback also echoes the candidate text, so it changes when the injection is appended. Do not cite 72/72 as evidence that the injections steered the model.

## Descriptive channel classification (from reading the code; not a test result)
| Channel | Where it goes | Reaches score / difficulty / best-answer code? |
|---|---|---|
| Feedback narrative fields (`narrative_feedback`, `how_to_answer`, `stronger_answer_guide`, `actionable_improvements`) | returned to the UI | not read by any scoring/difficulty/ranking path found |
| Feedback lists (`missing_concepts`, `what_was_correct`, `what_was_incorrect`) | `_update_session_state` → `concepts_missed`, `concepts_mastered`, `misconceptions`; final-report aggregation | written to session state and the report; no reader of those state lists found in `agents`, `services`, `rl`, `apps/backend`; ranking uses the **evaluator's** `missing_concepts`, not these |
| Hint text | returned to the UI | no |
| **Follow-up generation** | the LLM's `followup` text becomes the follow-up question and its `target_concepts` become that question's `expected_concepts`, which the evaluator's concept detection uses when the question has no stored vectors | **Yes, for the later follow-up turn**: the evaluator scores an answer against LLM-authored question text/concepts. Outside B1 (which holds the question fixed). Must be described as a documented dependency, not as isolation |
| Final-report generation via Qwen | not analysed in this campaign | unknown |

## What this supports (permissible wording)
"In a fixed-evaluator harness with the real Qwen model, no compared score, difficulty, best-answer or controller observable differed between benign and adversarially steered arms in any of 72 pairs (16 with LLM-sourced feedback in both arms; the registered minimum of 30 was not reached). A static scan found no statement writing a protected key from an LLM-derived name, and both the static and the dynamic controls detected an injected LLM→score path." Not supported: "the LLM cannot alter scoring or difficulty", "isolation", "zero authority", any statement about follow-up questions, other prompts, other models, or the shipped timeout behaviour. The static guard is name-based and can miss indirect flows.

## Status
Registered protocol executed; sample-size requirement unmet; no invariant violation observed; no fix made and none needed for this campaign. The service-level findings (truncation-driven silent fallback, `llm_status` mislabel, 6 s vs 13–21 s timeout) are SUT defects/limitations to be reported; fixing them would create a new build and require rerunning the campaign. Independent methodology review of the protocol remains pending.
