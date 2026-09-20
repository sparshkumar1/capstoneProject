# X1-C old vs new (containment campaign, build A vs build B)

- **Old (v1):** registered `prereg/X1-C/v1` (`21a4c9c4…`), frozen `freeze/X1-C/v1` (`77614eb7…`), SUT build A = `release/app-repair/v1` (`980747ff…`), run 2026-09-20 11:08–11:16 UTC, harness sha256 `b278da77…`, executor `coding_executor.py` sha256 `3f89551a…cf4e8`. Results in `research/confirmatory/X1/results/x1c/`.
- **New (v2):** registered `prereg/X1-C/v2` (`77cf3a57…`), SUT build B = `sut/X1/build-B` (`beb374f3…`), run 2026-09-20 14:52–15:00 UTC, harness sha256 `fe32d453…cad4c`, executor `coding_executor.py` sha256 `970a7595…a79a8f4`. Results in `research/confirmatory/X1/results/x1c_v2/`; run record `run_records/x1c_v2/RUN_RECORD.json`. Exit 0, 90 runs, 0 harness errors, no orphan containers.
- **Environment (identical in both runs):** Docker server 29.7.2, kernel 6.6.87.2-microsoft-standard-WSL2, sandbox image id `sha256:1e8e861c8a5d797c1…`, gcc 13.2.1 (Alpine), host gateway 192.168.65.254.
- **Exact code change affecting this campaign** (`git diff release/app-repair/v1 sut/X1/build-B -- agents/coding_executor`): a unique `--name prepaired-sbx-<12 hex>` is added to every `docker run`, and on `subprocess.TimeoutExpired` (compile and run steps) the executor runs `docker rm -f <name>`. Flags, limits, statuses and the pre-flight are unchanged; `sandbox_policy.py` hash is unchanged. The other build-B changes (orchestrator, feedback agent, Qwen service) are not on this campaign's code path.
- **Harness change:** only tags, SUT tag, output path and two file names (see `PROTOCOL_X1-C_v2.md`); criteria and bounds are byte-identical.

## Per-attack comparison (5 repetitions each)
| Attack | shipped met v1 | shipped met v2 | permissive breach v1 | permissive breach v2 | benign false pos v1/v2 | oracle valid v1/v2 | failed criteria v1 / v2 | changed |
|---|---|---|---|---|---|---|---|---|
| SEC-01 | 5/5 | 5/5 | 5/5 | 5/5 | 0/5/0/5 | True/True | - / - | no |
| SEC-02 | 5/5 | 5/5 | 5/5 | 5/5 | 0/5/0/5 | True/True | - / - | no |
| SEC-03 | 5/5 | 5/5 | n/a | n/a | 0/5/0/5 | True/True | - / - | no |
| SEC-04 | 5/5 | 5/5 | n/a | n/a | 0/5/0/5 | True/True | - / - | no |
| SEC-05 | 5/5 | 5/5 | 5/5 | 5/5 | 0/5/0/5 | True/True | - / - | no |
| SEC-06 | 5/5 | 5/5 | 5/5 | 5/5 | 0/5/0/5 | True/True | - / - | no |
| SEC-07 | 5/5 | 5/5 | 5/5 | 5/5 | 0/5/0/5 | True/True | - / - | no |
| SEC-08 | 5/5 | 5/5 | 5/5 | 5/5 | 0/5/0/5 | True/True | - / - | no |
| SEC-09 | 5/5 | 5/5 | 5/5 | 5/5 | 0/5/0/5 | True/True | - / - | no |

BEN v1: {'benign_criteria_met': '10/10'} | BEN v2: {'benign_criteria_met': '10/10'}

## What changed
**Outcomes:** none. Every attack's shipped-configuration result (5/5), permissive-control breach (5/5 where a control applies), benign cross-oracle false positives (0/5) and oracle validity are identical; benign control 10/10 in both. Per-attack observations reproduce (status strings, exit codes, `connect()` errno 101, `socket()` returning a descriptor, ptrace returning 0 with the pre-flight disabled, `wrong_answer` in both shipped and permissive configurations for SEC-02/07/08/09; execution-time ranges overlap: e.g. SEC-05 shipped 2.53–2.56 s in v1, 2.63–2.89 s in v2 against the 6 s bound).
**Did any scientific claim change?** No. The permitted claim is unchanged and now applies to build B: "on one Docker Desktop (WSL2) machine, for the nine specified attack programs, the shipped sandbox configuration met the pre-specified containment and host-unchanged criteria in 5 of 5 runs per attack, while a permissive control produced the breach in 5 of 5 runs where a control applies."
**Qualifiers that carry over unchanged** (`X1C_RESULT_NOTE.md`, `X1_METHOD_AUDIT.md`): the pre-flight blocks only the literal `ptrace(`; `socket()` succeeds without a network and only `connect()` fails; ptrace(TRACEME) returns 0 in the container when the pre-flight is bypassed; status strings do not distinguish contained from breached for SEC-02/07/08/09; the SEC-09 canary criterion is not discriminating in the shipped configuration and the canary directory was not reset between permissive repetitions; SEC-08 uses the configured pids constant; nine programs, one machine, one configuration; the runs are deterministic repetitions, not samples.
**Independence:** v2 was written and run by the same agent after seeing v1; it is a build-binding rerun, not an independent replication.
