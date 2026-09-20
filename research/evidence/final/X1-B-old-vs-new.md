# X1-B-I old vs new (Qwen fixed-answer invariance, build A v2 vs build B v3)

- **Old (v2, build A):** `prereg/X1-B/v2` (`424894ff…`), `freeze/X1-B/v2` (`2768f498…`), SUT `release/app-repair/v1`, run 17:39–18:55 IST 2026-09-20, results `results/x1b/`. An earlier attempt under `prereg/X1-B/v1` was aborted after 13 pairs (log kept in `run_records/x1b_v1_aborted/`).
- **New (v3, build B):** `prereg/X1-B/v3` (`a9c6a209…`), SUT `sut/X1/build-B` (`beb374f3…`), run 2026-09-20 15:09–16:28 UTC (harness sha256 `e1d7ffc5…691a1`), real Qwen service `qwen2.5-1.5b-instruct-q4_k_m.gguf` started from the tagged code, results `results/x1b_v3/`, run record `run_records/x1b_v3/RUN_RECORD.json`, exit 0. v3 is a **registered revision on a new build** (decoding cap 256 → 512 tokens and truthful `llm_status`); v2 and v3 are not pooled. Same design: 36 injections × 2 replicates = 72 pairs, fixed evaluator stub (0.90), same 14 invariants, same validity rule, same minimum of 30 valid pairs, client timeout raised to 600 s as a registered deviation.
- **Code changes relevant to this campaign:** Qwen feedback `max_new_tokens` 256 → 512 (`services/qwen/app.py`); `feedback_agent` reports the service's real `llm_status` (`agents/orchestrator/feedback_agent.py`). The FLT-03/FLT-06 repairs are outside this path. Harness differences: tags, SUT tag, output path, file names, decoding note.

## Comparison
| Quantity | v2 (build A) | v3 (build B) |
|---|---|---|
| Pairs run | 72 | 72 |
| **Valid pairs (both arms LLM-produced)** | **16** (registered minimum 30 **not met**) | **72** (minimum 30 **met**) |
| Benign arm served by deterministic template | 41 of 72 | 0 of 72 |
| Adversarial arm served by deterministic template | 37 of 72 | 0 of 72 |
| Invariants exactly equal, valid pairs | 16 / 16 | 72 / 72 |
| Invariants exactly equal, all pairs | 72 / 72 | 72 / 72 |
| Mutation control detected | 50 / 72 (50 / 50 where `narrative_feedback` differed; 0 / 22 where identical) | 72 / 72 (`narrative_feedback` differed in all 72) |
| Static guard, real sources | 0 of 75 protected-key writes flagged; injected mutant caught | 0 flagged; injected mutant caught |
| Distinct injections among valid pairs | 14 of 36 | 36 of 36 |
| Valid benign-arm time per turn | 18.6–23.9 s | 19.0–30.3 s |
| `llm_status` values seen | `available` in every response (mislabelled for template responses) | `available`, and every response was genuinely LLM-produced |
| Injection-specific word appears in adversarial but not benign LLM text (crude descriptive check, valid pairs) | 6 / 16 | 23 / 72 |

## Interpretation
- **B1 status.** Under the v3 registration, the registered sample-size requirement (≥ 30 valid LLM-sourced pairs) was met (72), and no compared observable differed in any pair. This is valid B1 evidence **for build B under the v3 protocol**. It is **not** a rescue of the v2 registration: v2 did not meet its N, that record stays as it is, and the paper must say so.
- **What repaired the valid-pair rate.** The rise from 16/72 to 72/72 coincides with the build-B changes (token cap 512, no template masquerading as LLM output), but this campaign cannot separate the two; unseeded generation means exact text is not reproducible.
- **What this supports:** "On build B, with the evaluator result held fixed and the real Qwen model, no compared score, difficulty, best-answer or controller observable differed between benign and injection-carrying arms in any of 72 pairs (all with LLM-produced feedback in both arms; 36 injection sentences × 2 replicates); a static scan found no statement writing a protected key from an LLM-derived name, and the static and dynamic controls each detected an injected LLM→score path."
- **What it does not support:** "the LLM cannot alter scoring or difficulty", "isolated", "zero authority", any statement about follow-up-question generation (a documented LLM→evaluator dependency, untested), other prompts, other models or decoding settings, or the shipped timeout behaviour (the shipped 6 s client wait remains shorter than 19–30 s generation on this CPU); the injections' effectiveness at steering the model is **not** demonstrated (an injection-specific word appears in the adversarial-arm text in 23 of 72 pairs; this is a crude lexical check, not a measure of compliance); the static guard is name-based; the mutation control replays recorded LLM text and tests the comparator, not the live pipeline.
- **B2 was not run** (`X1_B2_DECISION.md`).
