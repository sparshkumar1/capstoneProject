# X1-B-I v3 protocol — Qwen fixed-answer invariance on build B (Paper 1)

Registered by commit + annotated tag `prereg/X1-B/v3` BEFORE the v3 run. Harness `x1b_harness_v3.py`, prompt set `x1b_prompts.json` (unchanged, byte-identical to v2). Supersedes nothing: the v2 result (`freeze/X1-B/v2`: 72 pairs, 16 valid, minimum 30 not met) and the aborted v1 log stay as they are and are cited as the build-A record.

## 1. Why a revision
The v2 shortfall came from SUT defects, not from the design: the service capped feedback generation at 256 tokens so the nine-field JSON was often truncated and replaced by the deterministic template, and the feedback client labelled that template `llm_status: available`. Build B (`sut/X1/build-B`) raises the cap to 512 tokens and passes the service's real `llm_status` through. This changes the decoding configuration of the system under test, so v3 is a **revised** protocol on a new build, not the v2 experiment re-run; v2 and v3 are never pooled.

## 2. Design, validity rule, controls, interpretation
**Identical to `PROTOCOL_X1-B.md` (v2)**: same 36 injections × 2 replicates = 72 pairs, same fixed evaluator stub, same 14 invariants and exact-equality rule, same validity rule (both arms' feedback produced by the real LLM: `llm_status == available`, decision source Qwen and not `non_llm`), same minimum of 30 valid pairs (no re-drawing), same mutation control and static guard, same channel enumeration, same client-timeout deviation (600 s, disclosed; the shipped 6 s timeout is a documented, unchanged limitation), same not-allowed wording, same follow-up-channel exclusion. The v3 harness differs from v2 only in protocol tag, SUT tag, output directory, checked file names, and the decoding note (`max_new_tokens 512`).
The valid-pair count is reported against 30 as registered; if fewer than 30, the shortfall is reported and nothing is re-drawn or extended. **B2 (behavioural stress) is not part of v3.**

## 3. Findings recorded before the run (from the audit, not results)
- The injections' steering effect on the model is not demonstrated by v2 (`X1_METHOD_AUDIT.md` §3); "adversarially steered" is not to be written for v3 either unless a separate measurement is registered.
- The mutant's detection is by construction limited to pairs whose `narrative_feedback` differs between arms (v2 re-analysis: 50/50 vs 0/22).
- Real generation time may rise with the 512-token cap; run length is expected to be longer than v2's 76 min.
