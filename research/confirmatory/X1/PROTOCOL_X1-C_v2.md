# X1-C v2 protocol — containment campaign rerun on build B (Paper 1)

Registered by commit + annotated tag `prereg/X1-C/v2` BEFORE the v2 run. Harness `x1c_harness_v2.py`.
**This is a rerun, not a blind replication.** The v1 results (`prereg/X1-C/v1`, `freeze/X1-C/v1`, build A = `release/app-repair/v1`) were seen before v2 was written and are retained unchanged.

## 1. Why a rerun
The FLT-06 repair (X1-A defect: compile timeout left the container running) changed `agents/coding_executor/coding_executor.py` (unique `--name` on every `docker run`; `docker rm -f` on client-side timeout). The executor is the SUT of X1-C, so the v1 result belongs to build A. Build B = commit tagged `sut/X1/build-B` (see `research/evidence/final/DEFECT_DECISIONS_FLT03_FLT06.md`). The build also contains the FLT-03 orchestrator repair and two Qwen-path repairs, none of which touch the executor path exercised here.

## 2. Design, criteria, controls, interpretation rules
**Identical to `PROTOCOL_X1-C.md` (v1)**: same nine attack programs, same permissive controls, same criteria and bounds (including `CPU_BOUND_MS = 6000`, `REPS = 5`, `SANDBOX_TIMEOUT_S = 2.0`), same cross-oracle negative control, same interpretation rules, same "not measured" list. The v2 harness differs from the v1 harness **only** in: protocol tag, SUT tag (`sut/X1/build-B`), output directory (`results/x1c_v2`), the two file names checked against the tag, and docstring text. The diff is reproducible with `diff x1c_harness.py x1c_harness_v2.py`.
Known weaknesses recorded in `research/evidence/final/X1_METHOD_AUDIT.md` (e.g. SEC-09's canary criterion is not discriminating in the shipped configuration; SEC-08 uses the configured pids constant; SEC-01 tests only the literal `ptrace(` pattern) are **not repaired** here, so that v1 and v2 are comparable; they stay stated limitations.

## 3. Additional record for v2
The executed `docker run` command lines are stored per run as in v1; they now contain `--name prepaired-sbx-<hex>`. Orphan-container detection (`docker ps -a` before/after) is unchanged and is the check that the added cleanup did not leave or remove anything unexpected.

## 4. Outcome reporting
Old-vs-new table per attack (`X1-C-old-vs-new.md`): v1 result, v2 result, changed outcomes, whether any claim changed. A shipped-configuration criterion failing in v2 is a defect finding reported as found.
