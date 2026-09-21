# P1 — SEC-05 "four vs five" reconciliation (2026-09-21)

**Question.** For how many attacks was the executor status string identical in shipped and permissive runs?

**Raw evidence (read-only; `research/confirmatory/X1/results/x1c/results.csv` and `x1c_v2/results.csv`, 90 rows each, columns `attack, config, status, exit_code`).** The status/exit-code pairs are identical in the two files:

| Attack | shipped | permissive | Identical? |
|---|---|---|---|
| SEC-01 | policy_blocked | wrong_answer/0 | no |
| SEC-02 | wrong_answer/0 | wrong_answer/0 | **yes** |
| SEC-03 | compilation_error | (no permissive control) | not comparable |
| SEC-04 | runtime_error/139 | (no permissive control) | not comparable |
| SEC-05 | timeout/124 | timeout/124 | **yes** |
| SEC-06 | memory_limit/137 | wrong_answer/0 | no |
| SEC-07 | wrong_answer/0 | wrong_answer/0 | **yes** |
| SEC-08 | wrong_answer/0 | wrong_answer/0 | **yes** |
| SEC-09 | wrong_answer/0 | wrong_answer/0 | **yes** |

**Result.** Five of the seven attacks with a permissive control (SEC-02, -05, -07, -08, -09) have an identical status in both configurations. SEC-05 is separated by execution time (shipped `exec_ms` about 2.5–2.9 s against 12.6–13.0 s for the control, per the frozen note).

**Frozen-note discrepancy (documented, not edited).** `X1C_RESULT_NOTE.md` line 28 lists four (SEC-02, -07, -08, -09) and says the status "differed by outcome" for SEC-01 and SEC-03–06. The raw data show that for SEC-05 the status did not differ, and for SEC-03/-04 there is no permissive run to compare. The frozen note was not modified.

**Manuscript decision.** The raw data support five, so the manuscript and the ICETC port now say five (abstract, contributions, oracle paragraph, discussion, conclusion), and the SEC-05 separation by execution time is stated. The abstract stays at ≤250 words (249). Earlier "four" wording is superseded; D-1 is closed on the evidence.
