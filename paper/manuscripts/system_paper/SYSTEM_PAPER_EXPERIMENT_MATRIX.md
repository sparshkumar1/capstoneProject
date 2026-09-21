# System paper — experiment matrix (PROPOSED; nothing executed)

Every row is future work unless the status says otherwise. Keep it small enough to run rigorously.

| ID | Question | Design | Needs | Status |
|---|---|---|---|---|
| S0 | What is implemented and what evidence exists? | Repository audit | none | DONE (`SYSTEM_PAPER_RESEARCH_AUDIT.md`) |
| S1 | Do the runtime conditions (constant, rule-based, PPO+guardrail) run correctly and identically apart from the difficulty rule? | Engineering tests, deterministic scripted sessions, logged | approval to add runtime switches; tests | NOT STARTED |
| S2 | Are the held-out parallel forms equivalent in difficulty? | Independent blinded ratings of candidate answers to each form | rater documentation; ethics route | NOT STARTED |
| S3 | Does adaptation change post-test quality relative to non-adaptive practice? | Randomized between-participant, pre/post on held-out questions, blinded human rating | ethics/consent; participants; approved protocol | **BLOCKED** (ethics undetermined; no approval; no arms) |
| S4 | Does the automated evaluator track independent human ratings on the held-out answers? | Correlation/agreement with intervals on the human-rated set | same data as S3 | BLOCKED (same reasons) |
| S5 | Usability and workload | Standard instrument administered after the session | instrument chosen and verified | BLOCKED |
| S6 | Reliability in use (failures, timeouts, completion) | Logged from S3 sessions | S3 | BLOCKED |
| S7 | Ablation of the input modalities | See `SYSTEM_PAPER_ABLATION_PLAN.md` | only after S3 design is fixed | NOT PLANNED |

Rules: no arm is added or dropped after seeing outcomes without registering a new experiment; the P1 and P3 frozen results are never re-run or altered for this study; results from S3–S6 cannot retroactively change P1 or P3.
