# X1-C result note — containment campaign (executed 2026-09-20)

Single execution of the registered campaign (`prereg/X1-C/v1`, registration commit `21a4c9c4e456a7f25136bc1d3573879094bfc7eb`, SUT `release/app-repair/v1`), exit 0, 90 runs, 0 harness errors, no orphan containers left (`docker ps -a` empty afterwards). Outputs and their SHA-256: `run_records/x1c/RUN_RECORD.json`. No retry, no parameter change. Criteria were computed by the harness (`results/x1c/results.csv`, `runs.jsonl`).

## Per-attack outcome (5 repetitions each; no pooled percentage)
| Attack | Shipped configuration: criteria met | Permissive control: breach detected | Benign cross-oracle false positives | Observed in the shipped configuration |
|---|---|---|---|---|
| SEC-01 ptrace (static layer) | 5/5 | 5/5 (pre-flight disabled) | 0/5 | `policy_blocked`, no container created. With pre-flight disabled the call reached the sandbox and `ptrace(PTRACE_TRACEME)` **returned 0** (not blocked by any container control) |
| SEC-02 socket + connect | 5/5 | 5/5 (`--net=none` removed) | 0/5 | `socket()` returned a descriptor (3); `connect()` returned −1, errno 101 (ENETUNREACH); listener saw 0 connections. Control: connect succeeded, 1 connection |
| SEC-03 syntax error | 5/5 | n/a | 0/5 | `compilation_error`, exactly one container (compile) |
| SEC-04 SIGSEGV | 5/5 | n/a | 0/5 | exit 139, `runtime_error`, program did not resume |
| SEC-05 CPU loop | 5/5 | 5/5 (timeout 2 → 12 s) | 0/5 | `timeout`, exit 124, 2.53–2.56 s execution time (bound 6 s); control 12.6–13.0 s |
| SEC-06 RAM | 5/5 | 5/5 (memory 128 → 1024 MB) | 0/5 | killed, exit 137, Docker `oom` event, last progress marker 96 MB, never completed the 256 MB touch; control touched 224 MB and completed |
| SEC-07 exfiltration | 5/5 | 5/5 (`--net=none` removed) | 0/5 | connect −1/ENETUNREACH; listener 0 connections, 0 bytes. Control: 39-byte canary token received |
| SEC-08 fork attempts (bounded 100) | 5/5 | 5/5 (pids limit 32 → 256) | 0/5 | 30 forks succeeded, then `EAGAIN` (11) every time (limit 32 includes the shell and the program); control: 100 succeeded |
| SEC-09 filesystem write | 5/5 | 5/5 (`--read-only` removed + host canary dir mounted rw) | 0/5 | `/etc` write refused EROFS (30); `/canary` open failed ENOENT; host canary hash unchanged. Control: canary write succeeded |
| BEN benign | 10/10 (shipped and permissive-shim) | | | accepted, exit 0 |

The shipped `docker run` flags actually issued (stored per run): `--user 1001:1001 --net=none --cap-drop=ALL --security-opt=no-new-privileges --cpus=1.0 --memory=128m --memory-swap=128m --pids-limit=32 --read-only --tmpfs /workspace…`, default seccomp profile.

## What this supports (permissible wording)
"On one Docker Desktop (WSL2) machine, for nine specified attack programs, the shipped sandbox configuration met the pre-specified containment and host-unchanged criteria in 5 of 5 runs per attack, while a single-change permissive control produced the corresponding breach in 5 of 5 runs (where a control applies), so the oracles were able to fail." Not supported: "secure", "isolated", "zero violations", any statement about attacks outside these nine programs, kernel/runtime escapes, other hosts, UDP/DNS/IPv6.

## Facts that qualify or correct earlier statements (keep in the paper)
1. The static pre-flight (`validate_source_safety`) blocks only `ptrace(` and sources over 64 KB; `RESTRICTED_C_HEADERS` is defined but unused. Socket, exfiltration and filesystem programs were **not** blocked by it; containment came from the container configuration.
2. `socket()` succeeds under `--net=none`; what fails is `connect()` (no route). The earlier design label "socket creation blocked" is inaccurate.
3. With the pre-flight bypassed, `ptrace(PTRACE_TRACEME)` returned 0 inside the container: the container configuration did not block that call (effect limited to a self-trace; not evaluated further).
4. Executor status strings cannot serve as an oracle: for SEC-02, 07, 08 and 09 the executor reported `wrong_answer` in **both** the shipped (contained) and the permissive (breached) configuration, so the status alone does not distinguish contained from breached. (For SEC-01 and SEC-03–06 the status differed by outcome, but those statuses were not the criterion.)
5. Harness limitation: the canary directory was not reset between SEC-09 permissive repetitions, so the host-hash-change evidence appears only in the first permissive run (r1); detection in r2–r5 came from the self-report criterion `canary_write_refused`. The shipped-configuration result is unaffected.
6. Peak per-container memory/CPU was not measured; host free-memory change is descriptive noise (−0.26 to +0.61 GB between runs) and carries no criterion.
7. Timing bound (6 s) was set from benign fixtures (≈0.6–0.9 s), not from attack runs.

## Status
Registered protocol executed as written; no defect found in the shipped configuration for these nine programs; no post-hoc change. Independent methodology review of the protocol is still pending.
