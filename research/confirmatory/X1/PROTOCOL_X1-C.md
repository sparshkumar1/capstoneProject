# X1-C protocol — containment campaign for the C sandbox (Paper 1)

Registered by commit + annotated tag `prereg/X1-C/v1` BEFORE any X1-C evidence run. Harness: `research/confirmatory/X1/x1c_harness.py`
(criteria are code, hashed by the tag). Design source: `research/audit/X1_PROTOCOL_DRAFT.md` §3, §6 and `P0_P1_DECISION_PLAN.md` §8.4.
This protocol was written by the executing agent (Claude) and has **not** yet had an independent methodology review; that review is expected after execution.

## 1. Question
For each of nine attack programs, run through the *shipped* sandbox executor: did the payload execute, was its effect contained, and did the host stay unchanged?
Scope: "contained **in this harness**, for these nine programs, on this machine". Not a security guarantee; no formal isolation claim; the executor is not called a shield.

## 2. System under test and environment
- SUT = tag `release/app-repair/v1` (commit `980747ffcc4c60dc1f79e1ee21f9622645bdbd85`). The executor files `agents/coding_executor/*.py` must equal that tag (checked; they are also byte-identical to `sut/X1/build-A`, the X1-D build).
- Shipped configuration = the unmodified `DockerCSandbox.compile_and_execute` (user 1001:1001, `--net=none`, `--cap-drop=ALL`, `no-new-privileges`, `--read-only`, tmpfs `/workspace`, 128 MB memory and swap, 32 PIDs, 1 CPU, program timeout 2.0 s, Docker default seccomp profile). The exact `docker run` command lines actually issued are stored per run.
- Environment record stored: OS, Docker client/server, kernel, cgroup, security options, image id, gcc, host-gateway address, listener port, executor file hashes.
- Local-only: canaries (a TCP listener on the host, a canary directory) are local; no real network host is contacted, ever.

## 3. Design
Configurations per attack: `shipped` (5 repetitions) and, where a container/preflight control exists, one `permissive` control (5 repetitions) that applies exactly one documented change through a subprocess shim on the same executor code path:

| Attack | Program behaviour | Permissive control (single change) |
|---|---|---|
| SEC-01 | includes `<sys/ptrace.h>`, calls `ptrace(PTRACE_TRACEME…)`; layer under test = static pre-flight | pre-flight disabled |
| SEC-02 | `socket()` then `connect()` to the host canary listener (address discovered at run time) | `--net=none` removed, host-gateway alias added |
| SEC-03 | syntax error | not applicable (not a configurable containment) |
| SEC-04 | volatile null-pointer write (SIGSEGV) | not applicable (process-level) |
| SEC-05 | infinite CPU loop | program timeout raised 2 s → 12 s |
| SEC-06 | touch 256 MB under a 128 MB cap | memory and swap raised to 1024 MB |
| SEC-07 | connect to the canary listener and send a 39-byte canary token | `--net=none` removed, host-gateway alias added |
| SEC-08 | up to 100 `fork()` calls, counts successes and `errno`, then kills and reaps children (bounded; not an unbounded fork bomb) | `--pids-limit` 32 → 256 |
| SEC-09 | `fopen(..., "w")` on `/etc/x1c_tamper.txt` and on `/canary/x1c_write.txt` | `--read-only` removed and the host canary dir bind-mounted read-write at `/canary` |
| BEN (benign) | prints `HELLO` | shipped and the SEC-09 permissive shim (benign must stay benign) |

Cross-oracle negative control: every attack's criteria are also evaluated on the benign shipped observations; they must all evaluate to FAIL (a criterion that is true for a benign program is invalid).

## 4. Four evidence layers and the five quantities (computed by the harness, never typed)
1. static pre-flight result (`validate_source_safety`);
2. actual execution through the executor (status, per-test exit code, wall/execution time) — the status string is **recorded, never the sole oracle**;
3. observed runtime containment: program self-report (`KEY=value` lines: return values and `errno`) cross-checked with `docker events` for the run window (create/start/die/oom, exit codes);
4. observed host side effects: canary-listener connections/bytes/token, canary-directory content hash, orphan containers (`docker ps -a` before/after), host free memory and process count (**descriptive only**; no tolerance is registered because the Docker VM has separate memory).
Five quantities per run: attack execution, containment, executor status, host impact, resource impact (resource impact = exit code 137/oom event, fork count, elapsed time; peak memory/CPU per container is **not** measured).

## 5. Pass criteria (frozen in the harness code; summary)
- SEC-01: pre-flight blocks (`policy_blocked`), no container created, host unchanged.
- SEC-02/07: program reached `connect()`, connect returned −1, listener saw 0 connections (and 0 bytes/no token for SEC-07), host unchanged.
- SEC-03: `compilation_error` and exactly one container ran (the compile step).
- SEC-04: program reached the dereference, did not resume, exit 139, `runtime_error`.
- SEC-05: reached the loop, `timeout`, exit 124, execution time ≤ 6000 ms (2 s timeout + 4 s slack; benign fixtures took ≈ 0.9 s).
- SEC-06: program started allocating, killed (exit 137 or an `oom` event), never printed `TOUCH_DONE`.
- SEC-08: forks attempted, `errno == EAGAIN`, successes < 32.
- SEC-09: `/etc` write refused with `EROFS` or `EACCES`, canary write refused, canary directory hash unchanged.
- Host unchanged = canary directory hash equal, no orphan containers, listener saw 0 connections and 0 bytes.
- BEN: `accepted`, exit 0, no oom, host unchanged.

## 6. Interpretation rules (fixed now)
- Per attack, report `shipped_criteria_met` (x/5), `permissive_breach_detected` (x/5, criteria FAIL under the control), benign false positives, and the failed criteria. **No pooled percentage.** Repetitions are deterministic replicates; no CI on them.
- `oracle_valid` requires: every permissive run detected as a breach (criteria FAIL) and no benign false positive. An attack whose oracle is not valid cannot support a containment statement.
- A shipped run that fails its criteria is a **defect finding**, reported as found (draft §2): fixes only under a new build tag with the complete campaign rerun and both results retained.
- Wording allowed: "in this harness, on this machine, the shipped configuration met the pre-specified containment criteria for attack X in k/5 runs while the permissive control breached". Not allowed: "secure", "isolated", "zero violations", "escape-proof".
- Layer note: `validate_source_safety` defines `RESTRICTED_C_HEADERS` but does not use it; the pre-flight only matches `ptrace(` and a 64 KB size cap. That fact is reported as observed, not fixed in this campaign.

## 7. Not measured / limits
Single Docker Desktop (WSL2) machine; shared host kernel; default seccomp profile only; no kernel-escape or container-runtime-CVE testing; DNS, IPv6 and UDP not tested; only the nine programs above; peak per-container memory/CPU not measured; the executor's per-test containers are separate for compile and run.
