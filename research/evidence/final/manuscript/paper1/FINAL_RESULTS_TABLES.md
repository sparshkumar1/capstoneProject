# Paper 1 - result tables (exact stored numbers)
**Table 1. X1-C containment (5 deterministic repetitions per row)**
| Attack | Shipped met (A / B) | Permissive breach (A / B) | Benign false positives (A / B) | Shipped observation |
|---|---|---|---|---|
| SEC-01 ptrace (pre-flight layer) | 5/5 / 5/5 | 5/5 / 5/5 | 0/5 / 0/5 | policy_blocked; pre-flight disabled: ptrace returned 0 |
| SEC-02 socket+connect | 5/5 / 5/5 | 5/5 / 5/5 | 0/5 / 0/5 | socket()=3, connect()=-1 errno 101; listener 0 connections |
| SEC-03 syntax error | 5/5 / 5/5 | n/a | 0/5 / 0/5 | compilation_error |
| SEC-04 SIGSEGV | 5/5 / 5/5 | n/a | 0/5 / 0/5 | exit 139, runtime_error |
| SEC-05 CPU loop | 5/5 / 5/5 | 5/5 / 5/5 | 0/5 / 0/5 | timeout, exit 124, 2.53-2.56 s (A), 2.63-2.89 s (B), bound 6 s |
| SEC-06 RAM | 5/5 / 5/5 | 5/5 / 5/5 | 0/5 / 0/5 | killed exit 137, oom event |
| SEC-07 exfiltration | 5/5 / 5/5 | 5/5 / 5/5 | 0/5 / 0/5 | connect failed; 0 bytes; control: 39-byte token received |
| SEC-08 fork attempts (<=100) | 5/5 / 5/5 | 5/5 / 5/5 | 0/5 / 0/5 | 30 forks succeeded then EAGAIN; control 100 |
| SEC-09 filesystem write | 5/5 / 5/5 | 5/5 / 5/5 | 0/5 / 0/5 | /etc write EROFS; canary hash unchanged |
| Benign control | 10/10 / 10/10 | | | accepted, exit 0 |
Sources: results/x1c/environment_and_verdicts.json (A) and results/x1c_v2/... (B); runs.jsonl hashes 10c7d7be... / 1340fb7f....
**Table 2. X1-A fault injection (criteria met of 5; build A / build B)**
| Scenario | A | B | Note |
|---|---|---|---|
| FLT-01 Qwen unavailable | 5/5 | 5/5 | 4.84-4.90 s / 4.87-4.91 s vs SLA 5.0 s |
| FLT-02 Qwen slower than client timeout | 5/5 | 5/5 | 12.78-12.85 s / 12.79-12.82 s vs SLA 15.0 s |
| FLT-03 evaluator outage | **0/5** | 5/5 | A: recorded as 0.0, no flag; B: evaluator_unavailable, not scored |
| FLT-04 invalid score NaN / Inf / 999 / -3 | 5/5 each | 5/5 each | NaN, Inf, -3 become unflagged 0.0 (unrepaired) |
| FLT-05 Docker CLI not found | 5/5 | 5/5 | structured sandbox_error in ~0 s |
| FLT-06 compiler outlives timeout | **0/5** | 5/5 | A: container present 3 s after return (5/5); B: none |
| FLT-07a lock 2 s | 5/5 | 5/5 | 2.07-2.10 s |
| FLT-07b lock 34 s | 4/5 | 5/5 | A 32.58-33.09 s (one above the 33.0 s bound); B 32.61-32.66 s; not a repair |
| FLT-10 empty input | 5/5 | 5/5 | structured outcomes |
| FLT-08 WebSocket, FLT-09 audio | not executed | not executed | no claim |
Sources: results/x1a/verdicts.json (e3b46224...), results/x1a_v2/verdicts.json (46a27aa9...).
**Table 3. X1-B-I invariance**
| Quantity | v2 build A | v3 build B |
|---|---|---|
| Pairs / valid (both arms LLM-produced) / registered minimum | 72 / 16 / 30 (not met) | 72 / 72 / 30 (met) |
| Observables exactly equal (all pairs / valid pairs) | 72/72 / 16/16 | 72/72 / 72/72 |
| Mutation control detected | 50/72 (50/50 where narrative differed) | 72/72 |
| Static guard flagged (real sources) / injected mutant caught | 0 of 75 writes / yes | 0 / yes |
| Distinct injections among valid pairs | 14 of 36 | 36 of 36 |
| Template-served arms (benign / adversarial) | 41 / 37 | 0 / 0 |
Sources: results/x1b/summary.json (2eb8dd20...), results/x1b_v3/summary.json (32d80a18...).
