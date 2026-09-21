# Codex harness audit brief (independent, READ-ONLY) - prepared 2026-09-20

**Prepared by:** the main engineering/research executor (Claude), for Sparsh. **Not yet run.** Companion plan: `research/audit/PHASE_NEXT_RESEARCH_PLAN.md` (section 4).

## 0. Purpose and ground rules

You are asked to perform an **independent, read-only code audit** of six research harness files written during the 2026-09-19 autonomous sprint. They generated (or analysed) the confirmatory/exploratory results X3-A, X2-B and X1-D, and they define the run-manifest mechanism that every future confirmatory experiment will use.

1. **Read-only.** Work in a **separate git worktree**; edit nothing in the repository; do not commit, tag or push. (Repository rule: never let two agents edit the same files.) Suggested setup by Sparsh (not by you):
   `git worktree add --detach ../PrepAIred_codex_audit 1ca0faab1e32e02192a42ae5dba647ad21a4314b`
   This brief and the plan are untracked files; Sparsh provides them separately.
2. You may run **small scratch computations outside the worktree** (e.g., recomputing a statistic from a copy of a stored CSV) using any Python with numpy/scipy. Do **not** run `x3a_run.py`, `x2b_run.py`, `x1d_run.py` in confirmatory mode, do not run the test suite, do not use the project `.venv`, and do not touch `envs/` (git-ignored, absent from the worktree). Each runner refuses to start if its results directory exists, but do not rely on that.
3. **This audit does not test the science of PREPAIred, the evaluator, PPO or the simulator.** It tests whether the *harness code* could produce a result, gate or manifest that misrepresents what was measured.
4. **The audit is a new quality-control layer.** The executed X3-A, X2-B and X1-D results are frozen (protocol-tagged before execution, hashed, preserved). A finding does **not** by itself invalidate them and **no rerun is requested** by this audit. Findings on frozen experiments are classified for their consequence on claims; findings on `run_manifest.py` and on harness patterns gate **new** confirmatory experiments (X1-A/B/C, X2-C, X3-B).
5. **O1-O20 below are LEADS, not confirmed defects.** They are the executor's own reading and may be wrong. Confirm or refute each independently; do not assume they are correct, and do not limit yourself to them.
6. Claude validates every finding before any action is taken. Do not propose or make changes to frozen artifacts, tags, results, protocols or the SUT.

## 1. Files under audit (SHA-256 verified 2026-09-20, worktree commit `1ca0faab...`)

| File | Lines | SHA-256 | Used by |
|---|---|---|---|
| `research/confirmatory/X3-A/x3a_lib.py` | 159 | `3badbb39dbf4974a53899ab013c9d0091f40aad718d34fc1b7502e6d4771e506` | X3-A |
| `research/confirmatory/X3-A/x3a_run.py` | 283 | `9fa86c2ce44233386076a544a9f8b911ff76a3a7f1f322640b9dbc024bdafc0f` | X3-A |
| `research/confirmatory/X3-A/x3a_analyze.py` | 196 | `77744f2a6f1e09d464a51d696cbba11c2ed7da14ffd52557ceb1c6ad7955f4be` | X3-A |
| `research/confirmatory/X2-B/x2b_run.py` | 307 | `b78d1407511c2c8cd80163c50d25529c4c9ca511c4ed828955d8dea7e9214808` | X2-B (old-benchmark exploratory arm) |
| `research/confirmatory/X1-D/x1d_run.py` | 141 | `aa1c9534a0b65809b36e5518067303a7bd8b33aa5aaa7ff72d1d4ad1a0ab5d9f` | X1-D |
| `research/tools/run_manifest.py` | 203 | `5f6283cbe73446e7fd7da885321c6350da6e0e66266120cf5e1e28c4ef6fed91` | all three (imported) |

Each of these hashes equals the value listed in the corresponding `protocol_manifest.json` (X3-A: lib, run, analyze, run_manifest; X2-B: `x2b_run.py`, run_manifest; X1-D: `x1d_run.py`, run_manifest). Verify this yourself.

## 2. Associated protocols, manifests, tags, configs

| Experiment | Protocol (SHA-256) | Protocol manifest (SHA-256) | Config (SHA-256) | Tag -> commit | Run manifest(s) (SHA-256) |
|---|---|---|---|---|---|
| X3-A | `research/preregistration/X3-A/PROTOCOL.md` (`b15ecb9e72ffb53bbbb8b9265bd23c26e1bfed0642986f78cd286d1b4ecc1479`) | `.../protocol_manifest.json` (`6d70640eea23266eb86dc947f37094fdea61998e11f0f28da42ecb79eaae7a97`) | `research/confirmatory/X3-A/x3a_config.json` (`929e0e3ead0f990ac18b8de661f57e2133025c96e7228cf73a8d18404003536e`) | `prereg/X3-A/v1` -> `b00541f66c05e48512968fa9cd46b536e76f676a`; `freeze/X3-A/v1` -> `dde2ddf962cc144416a7961afc98b7521d274548` | `results/manifest_X3-A-run.json` (`17ca8a4aef2d30afe27356332ebfafab01ae8d226df496d4629e2b03d64c9a45`); `results/manifest_X3-A-analysis.json` (`203506d17d95ad7ca80c46978b76eff4b46c324c4a588c684d75ce1550755ba7`) |
| X2-B | `research/preregistration/X2-B/PROTOCOL.md` (`1f85bc5fffeb8282c39337ee07468ee824d502656b7df221a98b0409546db67d`) | v2: `68fd87dd1290e05ccfc077f2aba54a74a5a9e3a2688c0d644ce4802096a107b6` (v1: `8cdcafc189804dbf638bdba9e5a59a6511f6eab225710255e5cb381d4bffc4fd`); amendment `AMENDMENTS/AMEND-001.md` (`47c4a5ba876d199cc61365f0c4a6ee137a3cee86c00d810e35dc8458a544ed7f`) | `research/confirmatory/X2-B/x2b_config.json` (`a44afeea9d02d837086c3f605b94fd43c986bf700cbc264e6b6bfd983ec02b0f`) | `prereg/X2-B/v1` -> `51cd2941780fbc2ce59b43310437e1580c8983c9` (attempt aborted, no output); `prereg/X2-B/v2` -> `d84b91388929bd3b70455cde94ef8720232114af`; `freeze/X2-B/v1` -> `dde2ddf...` | `results/manifest_X2-B-run.json` (`9c2a58f1449a96b0aba3505a1d8d509e32102149b6df874476a9e0f435b7d910`); aborted: `results_attempt1_ABORTED_manifest_external_path_error/manifest_X2-B-run.json` |
| X1-D | `research/preregistration/X1-D/PROTOCOL.md` (`b71e391325569650b6bb012033d6089697ace9d5da017699cd49db012f11b94d`) | `.../protocol_manifest.json` (`f0dab03dc2a50bd9d19294544638e6a406594037fa351c2c9e60b4ab8071bd7c`) | `research/confirmatory/X1-D/x1d_config.json` (`efdab894405180a1073dfbb3544215564d21921e49aa28b75d12e42f3050f8c0`) | `prereg/X1-D/v1` and `sut/X1/build-A` -> `39047498d6459d59912338bfce2d4da543b1d4d6`; `freeze/X1-D/v1` -> `dde2ddf...` | `results/manifest_X1-D-run.json` (`3f0bddaae34a5a23fb97cd18e4864d72e602f31007a2a5538ce356cae4a05e9b`) |

Other reference material: `research/analysis/RESULT_HASHES_phase3.txt` (`6e9581811abb6154c6a18645164b85891649dca269b655b3bdf970adc9558031`, 25 result-file hashes, carried in the `freeze/*` tag messages); deviation/amendment logs `research/preregistration/X3-A/DEVIATIONS.md` (`a2fe1b59...`), `research/preregistration/X2-B/DEVIATIONS.md` (`198a1dc2...`), `research/confirmatory/X3-A/DRYRUN_LOG.md` (`0cbfe73b...`); frozen locks `research/locks/LOCK-X3-2026-09-19.*`, `LOCK-X2-2026-09-19.*`; key raw outputs: `research/confirmatory/X3-A/results/sessions.csv` (`dd7eb669e1ffc60957f254e330185d69edf276d578b0b0029efdcf3880f1bcd8`, 63 000 sessions), `gate_G-HARNESS.csv`, `x3a_decision.json`; `research/confirmatory/X2-B/results/scores.csv`; `research/confirmatory/X1-D/results/{junit.xml,latency_raw.csv,pytest_console.txt}`; independent recomputation script `research/analysis/phase4_t2_verify.py` and report `PHASE4_T2_VERIFICATION.md` (recomputed point estimates only, not CIs); retained failed/aborted attempts: `research/confirmatory/X3-A/dryrun_attempt1_FAILED_*`, `dryrun_attempt2_FAILED_*`, `results_attempt1_ABORTED_process_killed`, `research/confirmatory/X2-B/results_attempt1_ABORTED_*`.

Frozen code imported (not under audit, but needed for reference checks): `rl/guardrails.py`, `rl/env/interview_env.py`, `rl/training/simulated_candidate.py`, `research/scripts/execute_paper3_study.py` (frozen `run_session_trajectory`, lines ~296-470).

## 3. Mandatory inspection list

For every file, inspect at least the following (20 items). For each, either report a finding or state "no finding" with the reasoning.

1. **Hidden hard-coded expected outcomes** - literals, constants or strings standing in for measured values; report text containing outcomes; thresholds equal to the outcome being tested.
2. **Result-dependent branching** - any path where behaviour depends on values computed from the data being analysed (thresholds, subsets, metrics, seeds, exclusions, gate tolerances).
3. **Incorrect aggregation** - grouping keys, unit of analysis (persona / question / scenario), alignment of persona x seed cells across conditions, averaging order, dropped rows.
4. **Seed / random-state handling** - global vs local RNG, shared RNG streams across analyses, seed derivation and collisions (e.g., `RandomState((eval_seed*31 + persona_index) % (2**31-1))`), determinism across identical invocations, monkeypatch state left behind on exceptions.
5. **Leakage from fixture generation** - whether the fixture used for a gate (5 frozen personas x frozen seeds; synthetic self-test items) shares information with, or fails to represent, the confirmatory inputs.
6. **Protocol / data / result contamination** - any use of stored results, labels or post-hoc information in scoring, gating or configuration; inputs modified between protocol tag and run.
7. **Mutation-control validity** - does detecting a mutant prove the *oracle/gate* can fail (sensitivity), or only that two code paths differ? Is there a coverage matrix? Are informational (non-gating) mutants hiding blind spots?
8. **Duplicate-run handling** - what stops a second run into the same output; does an aborted directory block a rerun; can two runs interleave?
9. **Aborted-run handling** - what state (manifest status, partial outputs) remains after a crash, kill or exception; is "aborted" distinguishable from "completed"?
10. **Failed-run treatment** - is a failed gate reported as such, does it prevent result generation, is the failure recorded in the manifest?
11. **Confidence-interval calculations** - percentile method, B, NaN handling, degenerate resamples, small numbers of clusters, correctness of the estimand vs the registered design.
12. **Bootstrap logic** - one-way vs two-way resampling, independence assumptions, resampling of nested units, correct handling of seedless (constant) conditions broadcast against seeded ones.
13. **Manifest generation** - what is recorded, when, and whether any recorded field is trusted from the caller.
14. **Hash generation** - what is hashed, at which moment (before/after), what is *not* hashed (untracked files, SUT tree, inputs, environment contents), whether hashes are enforced or only recorded.
15. **Protocol / version association** - the chain tag -> protocol hash -> harness hash -> run manifest -> outputs; can a result be attributed to the wrong tag, lock, input or code version?
16. **Accidental post-result information leakage** - constants, report strings, configuration or comments edited or written after results were seen (e.g., the report header string in `x2b_run.py`).
17. **Whether a false property could still make the harness report PASS** - for every gate, oracle and PASS/FAIL, construct (in words, or in a scratch copy) the smallest broken implementation that still passes; state whether it is possible.
18. **Whether an expected failure could be masked** - swallowed exceptions, `or SELFTEST` bypasses, NaN dropping, informational-only checks, tolerances, default values.
19. **Race conditions** - check-then-act sequences (existence check then create; read-modify-write of manifests), concurrent launches, non-exclusive file creation.
20. **Write-once semantics / concurrent-launch behaviour** - does the protection hold under two simultaneous processes, under a directory renamed while a process runs, and under a process killed mid-write? (A double launch actually occurred during X3-A; see `DEVIATIONS.md` entry 2. Establish whether the protection is sound, not merely whether it worked that day.)

## 4. Leads O1-O20 (executor's pre-audit observations - NOT confirmed defects)

Line numbers refer to the hashed files above. "Likely class" is the executor's guess and is not binding.

| # | File / location | Lead (to be confirmed or refuted) | Likely class |
|---|---|---|---|
| O1 | `x3a_lib.py` `shield` (39-59) | Local shield copy compared with the frozen shield only for the full rule set, `consecutive_failures=0`, infrastructure failure False, default medium band. The `disabled` (rule-ablation) branches have no independent reference; G-HARNESS shows two mutants are *detected*, not that each ablation branch is correct | DOC-ONLY unless an ablation branch is wrong |
| O2 | `x3a_run.py` `gate_harness` (76-170) | Equivalence to the frozen loop tested on the 5 frozen personas only. The 40-persona grid (`persona_grid`, target rule `round(10*skill)/2`, other type x skill pairs) and the Random, Oracle-rule and Controller policies have no frozen counterpart | DOC-ONLY if shared code paths; BLOCKING if a persona-parameter path differs |
| O3 | `x3a_run.py` mutation controls (155-168) | Gating mutants "detected" as `mismatching_fields > 0` on the fixture; two upper-threshold heuristic mutants were invisible on the fixture and were downgraded to informational (`DRYRUN_LOG.md`). No mutation-coverage matrix per branch | DOC-ONLY for X3-A; BLOCKING as a *pattern* for future oracles |
| O4 | `x3a_run.py` (78-84, 116, 169) | `fm.PPO` and `fm.AlignedInterviewEnv` monkeypatched on the frozen module; restored without `try/finally` | DOC-ONLY |
| O5 | `x3a_run.py` `main` (248-279), `run_manifest.Manifest.__init__` | Run-once protection is check-then-create, no lock/sentinel; a live process can write into a recreated directory (occurred: `DEVIATIONS.md` entry 2) | BLOCKING for new experiments (tool behaviour); DOC-ONLY for X3-A (results deterministic, complete, disclosed) |
| O6 | `x3a_run.py` `verify_lock` (45-58) | Checks only `name==version` lines; extra installed packages undetected; site-packages hash covers top-level name/size/mtime only | DOC-ONLY |
| O7 | `x3a_analyze.py` `boot`/`summarize` (51-67) | Independent resampling of 40 personas and 5 training seeds; percentile CI with 5 seed clusters is known to be too narrow. Reported primary CI [-0.0818, 0.0021] vs equivalence margin 0.12 | DOC-ONLY if a sensitivity recomputation keeps the class; else BLOCKING for the claim (not a rerun) |
| O8 | `x3a_analyze.py` `cells` (33-44) | Alignment across conditions relies on sorted persona IDs and seed keys with no assertion that all conditions contain identical personas/seeds | DOC-ONLY if alignment verified offline |
| O9 | `x3a_analyze.py` (95-96, 93) | One RNG stream shared by all summaries (order dependence for secondary CIs); `--primary-stratum` CLI switch can change the primary stratum | DOC-ONLY |
| O10 | `x3a_analyze.py` (99) | Does not compare `sessions.csv` with the SHA-256 recorded in the run manifest | DOC-ONLY if hashes match |
| O11 | `x3a_analyze.py` (109) | `trigger = cls != "Equivalent"` hard-coded (operationalisation D-X3B-OP, disclosed) | DOC-ONLY |
| O12 | `x2b_run.py` (29-47, 154-155, 209, 33-38) | Self-test mode inside the production runner (`--selftest`, `X2B_SELFTEST_DIR`, `g3 = ... or SELFTEST`, `_StubManifest`); reachable only with the flag | DOC-ONLY; recommend separation in a future version |
| O13 | `x2b_run.py` (273-287) | Permutation null permutes gold within questions; the observed statistic is pooled Spearman: different estimands | DOC-ONLY |
| O14 | `x2b_run.py` `ci` (253-256) | NaN replicates dropped; `valid_reps` reported; AUROC NaN when a resample lacks a class | DOC-ONLY |
| O15 | `x2b_run.py` (292) | Report header says `prereg/X2-B/v1`; manifest records v2 (disclosed) | DOC-ONLY |
| O16 | `x2b_run.py` (183-210) | Pair construction validated by G-DERIVED-REPRO (max diff 0.0005 vs tolerance 0.002) for the derived model only; upstream arm reuses the same pair code | DOC-ONLY |
| O17 | `x1d_run.py` (73-78) | No `add_inputs`: the case-level CSV, `RATER_1_COMPLETED.csv` and the SUT tree are not hashed in the manifest (stored manifest shows `n_inputs = 0`, `lock_id = None`); pytest may write files under the repo | DOC-ONLY for X1-D; BLOCKING pattern for new runs |
| O18 | `x1d_run.py` (99-103, 59-66) | 101 latency requests cycle through 64 items (`i % len(trip)`), so 37 repeats may hit caches; bootstrap CIs for P95/P99 with n = 100 are degenerate at P99 | DOC-ONLY |
| O19 | `x1d_run.py` (83-84, 125) | If pytest crashes without `junit.xml`, `ET.parse` fails after latency work and the manifest stays `started`; no explicit `aborted` state | DOC-ONLY |
| O20 | `run_manifest.py` (28, 49-55, 57-65, 126-135, 194-203) | `write_new` = exists check then non-exclusive `write_text`; `ALLOWED_ROOTS` includes `research/preregistration`; `git_dirty`/`dirty_diff_sha256` recorded, never enforced, `dirty_diff_sha256` ignores untracked files; site-packages hash uses `sys.prefix/Lib/site-packages` (Windows layout); caller-supplied `protocol` dict trusted | BLOCKING for new confirmatory runs as *tool behaviour* (fix goes to a new `run_manifest_v2.py`); DOC-ONLY for existing results |

Additional facts read from the stored manifests (also leads):
- **M1.** All four stored run/analysis manifests record `git_dirty = true` (the repository has long-standing untracked files), so the flag cannot show a clean tree; the accompanying `dirty_diff_sha256` covers tracked changes only.
- **M2.** Manifest commits differ from the tag commits: X3-A run `afe52656...` (tag commit `b00541f`), X3-A analysis at `51cd2941` (the `prereg/X2-B/v1` commit), X2-B run `d84b9138` (= `prereg/X2-B/v2`), X1-D `39047498` (= tags). Establish whether every recorded commit is a descendant of its protocol tag and whether the harness files at that commit equal the protocol-manifest hashes.
- **M3.** The X3-A analysis manifest has `gate = {}` and records only `sessions.csv` as input; the run manifest recorded `gate = G-HARNESS passed, 9/9`.

## 5. Suggested offline checks (no reruns; scratch only, on copies)

1. Verify every hash in each `protocol_manifest.json` and `RESULT_HASHES_phase3.txt` against the worktree, and that each protocol tag message carries the protocol and manifest hashes.
2. From `sessions.csv`, recompute difficulty trajectories, MAE, volatility, oscillation and attempted-boundary counts **from the stored `final_actions` strings and `target`** (start 3.0, +/-1, clip to [1,5]) and compare with the stored columns for all 63 000 sessions (independent of `simulate`).
3. Independently recompute the X3-A primary CI with separate code, and run seed-sensitivity variants (leave-one-seed-out; a small-cluster-corrected interval) to see whether the class `Equivalent` changes.
4. Assert persona and seed alignment across all 40 conditions in `sessions.csv`.
5. Recompute X2-B Spearman/Kendall/AUROC and the two-level bootstrap from `scores.csv` with independent code; check within-question permutation logic.
6. Recompute X1-D percentiles and CIs from `latency_raw.csv`; parse `junit.xml`.
7. For each gate, construct the smallest deliberately broken variant (in a scratch copy) that would still pass; report it.

## 6. Finding taxonomy (fixed)

- **BLOCKING** - blocks **new** confirmatory experiments (X1-A/B/C, X2-C, X3-B) or invalidates the statement a result is used to support. Use when: a gate/oracle/PASS-FAIL can succeed while the property is false, or an oracle depends only on a status string; a mutation control cannot fail or is unrelated to the oracle; result-dependent selection of thresholds/subsets/metrics/seeds/exclusions; non-determinism or seed leakage changing results between identical invocations; a protocol/lock/hash binding defect that can attribute results to the wrong tag, protocol, environment or input; non-atomic write-once protection that can overwrite raw results. A blocking finding concerning an **already frozen** experiment does not invalidate the frozen result; its consequence is claim-level (narrow, label, or, for a *central* claim only, consider a new registered re-analysis) and is decided by Sparsh + ChatGPT.
- **DOCUMENTATION-ONLY** - wrong or stale text, undisclosed limits, unrecorded environment detail, sensitivity checks that leave every classification unchanged, unused code, cosmetic manifest gaps for finished runs. Recorded in deviation logs / registry notes; no rerun.
- **NEW-TAG / NEW-VERSION REQUIRED** - any change to a hashed file that would alter behaviour or outputs. In particular, `run_manifest.py` is a listed dependency of three existing protocol manifests and **must not be edited**; fixes go into a new versioned tool (e.g., `run_manifest_v2.py`) tagged for new experiments only. Fixes to a harness for a future experiment require a new protocol tag and hash.

## 7. Required report format (fixed)

One Markdown table, one row per finding, in exactly these columns:

| File | Location | Finding | Classification | Reproduction | Could false property pass? | Required action |
|---|---|---|---|---|---|---|

- **File / Location:** path and line range in the hashed file.
- **Finding:** what is wrong, stated so it can be checked; say whether it confirms, refutes or is independent of a lead (O#/M#).
- **Classification:** exactly one of BLOCKING / DOCUMENTATION-ONLY / NEW-TAG-OR-VERSION-REQUIRED.
- **Reproduction:** the smallest steps or scratch code (outside the worktree) that show it.
- **Could false property pass?:** Yes/No, with the concrete false property and the broken variant that would pass.
- **Required action:** what would resolve it, and whether it affects (a) frozen results, (b) future experiments, (c) manuscript claims. Do not recommend rerunning a frozen experiment unless a finding demonstrates that a central primary result is wrong, and say so explicitly.

Also provide: (a) a list of leads O1-O20 and M1-M3 with CONFIRMED / REFUTED / INCONCLUSIVE and a one-line reason; (b) a list of files or checks you could not complete and why; (c) an explicit statement of what was **not** audited.

## 8. Already disclosed (do not report as new unless you find something beyond what is recorded)

X3-A dry-run mutant invisibility (two failed dry-run attempts, criteria not relaxed); X3-A double launch (`DEVIATIONS.md` entries 1-2); X2-B v1 aborted by an external-path defect and handled by AMEND-001 / tag v2; X2-B report header text "v1"; project `.venv` unlocked with pin conflicts (numpy 2.5.2, torch 2.11.0, accelerate 1.13.0 vs `requirements/*.txt`) and replay lock without wheel hashes; X3-A trigger operationalisation (D-X3B-OP); the known failing test `test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics` (subject of a separate root-cause triage, not part of this audit).

## 9. Out of scope

The SUT, evaluator, ScoreValidator, CrossEncoder, PPO/guardrail/reward/state/action definitions and their scientific validity; the failing test; venue selection; manuscript content; statistical *interpretation* of results; any proposal to change frozen artifacts, tags, results, protocols or the SUT.

## 10. Deliverable

A single Markdown report (fixed format above) returned to Sparsh, **not** written into the repository. Sparsh passes it to the executor, who validates each finding, and then Sparsh + ChatGPT decide on consequences.
