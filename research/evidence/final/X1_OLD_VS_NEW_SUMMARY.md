# X1 old vs new — summary index (build A vs build B)

| | Build A (`release/app-repair/v1`, `980747ff…`) | Build B (`sut/X1/build-B`, `beb374f3…`) |
|---|---|---|
| Change set | — | orchestrator fail-closed evaluator outage (FLT-03); executor container cleanup on timeout (FLT-06); `feedback_agent` truthful `llm_status`; Qwen feedback token cap 256 → 512; four tests adapted/added (full suite 283 passed, 1 known pre-existing failure `test_stage11_5_coding_adaptation`, run before the campaigns) |
| X1-C | `prereg/X1-C/v1` / `freeze/X1-C/v1`: 9 attacks 5/5 contained, controls 5/5 breach, benign 10/10 | `prereg/X1-C/v2`: identical outcomes — `X1-C-old-vs-new.md` |
| X1-A | `prereg/X1-A/v1` / `freeze/X1-A/v1`: FLT-03 0/5, FLT-06 0/5, FLT-07b 4/5, others 5/5 | `prereg/X1-A/v2`: all scenarios 5/5; FLT-03 and FLT-06 closed; FLT-07b pass is timing variation, not a repair — `X1-A-old-vs-new.md` |
| X1-B-I | `prereg/X1-B/v2` / `freeze/X1-B/v2`: 72 pairs, 16 valid (<30) | `prereg/X1-B/v3`: see `X1-B-old-vs-new.md` |

Registration commits: X1-C v2 and X1-A v2 `77cf3a57…`; X1-B v3 `a9c6a209…`. The harnesses differ from their v1/v2 predecessors only in tags, SUT tag, output path and file names. v2/v3 protocols were written after the earlier results were seen (disclosed in each protocol); the repairs and re-tests were performed by the same agent, so they are regression checks of specific fixes, not independent replications. Old results, the aborted X1-B v1 log and both builds' hashes are retained. Independent review of all X1 protocols remains outstanding (`X1_METHOD_AUDIT.md`).
