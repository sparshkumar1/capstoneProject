# Validation of the Codex harness audit (executor's report; 2026-09-20)

**Scope.** I validated the Codex findings against the current repository (HEAD `1ca0faa`) by reading code and stored artifacts. No experiment or rerun was executed, nothing was modified, no fix was implemented, `run_manifest.py` and `run_manifest_v2.py` were not touched or created. The only read-side computations were hash comparisons and key-set counts on stored CSV/JSON files.

**Source of the Codex report.** The report is not stored in the repository. I read its final message (12,127 characters; findings table, lead dispositions, completed and not-completed checks) from the Codex session log `~/.codex/sessions/2026/09/20/rollout-2026-09-20T10-22-28-...jsonl`. Codex's classifications below are quoted from that message. Only that session file was read.

**Ground rules applied.** The audit is a new QC layer; the frozen X3-A, X2-B and X1-D results are not invalidated by it and nothing is rerun (`PHASE_NEXT_RESEARCH_PLAN.md` section 4.0).

## 1. Summary of validation

| # | Finding | Codex | My verdict | Affects | New versioned tool/harness actually required? | Frozen result reclassified? |
|---|---|---|---|---|---|---|
| 1 | O5/O20 non-atomic run-once; manifest provenance weaknesses | BLOCKING | **CONFIRMED** (window is seconds, not milliseconds; already manifested once in frozen X3-A) | Future runs; frozen X3-A has a disclosed provenance nuance | **Yes: `run_manifest_v2.py`** (v1 is hash-bound by three protocol manifests and must not be edited) | No |
| 2 | O8 no key-set assertions before paired X3-A aggregation | BLOCKING | **CONFIRMED, narrowed** (missing persona raises `KeyError`; the silent cases are training-seed set, eval-seed completeness, duplicates) | Future analyses only | No new tool; new analysis version must assert keys | No |
| 3 | O10/M3 analysis proceeds without proving a completed gated run | BLOCKING | **CONFIRMED** | Future analyses only; frozen chain verified today | No new tool; helper belongs in v2, check belongs in each new analysis | No |
| 4 | O12 X2-B self-test can emit official-looking synthetic output | BLOCKING | **CONFIRMED** as a design weakness; blocking only for reuse of the `x2b_run.py` family | Future X2-B-family runs only | New harness version only if X2-B is re-run (X2-C arm); no new tool | No |
| 5 | X2-B upstream weights bound only by an 8-hex prefix | BLOCKING | **CONFIRMED**; practical risk negligible, formal binding weak | Future X2-B-family runs only | Config + harness of the new tag only; no new tool | No (add a note) |
| 6 | O17 X1-D final manifest does not bind inputs/SUT/model | BLOCKING | **CONFIRMED, narrowed** (protocol manifest did bind 8 files at run start; models/assets and most of the SUT tree are unbound) | Future runs; frozen X1-D claims keep status with a scope note | New runner version for any repeat/new X1 experiment; v2 tool must make empty inputs an error | No |

## 2. Validation of the six BLOCKING findings

### 2.1 O5 / O20 - non-atomic run-once and manifest provenance - **CONFIRMED**
- **Locations.** `research/confirmatory/X3-A/x3a_run.py:249-261` (existence check at 252, then `verify_lock` 255, `verify_protocol` 257, then `rm.Manifest(...)` 258); `research/tools/run_manifest.py:115-117` (`exists()` then `mkdir(exist_ok=True)`), `:190-191` (`_write` = `write_text`, non-exclusive), `:194-203` (`write_new` = per-file `exists()` then `write_text`), `:28` (`ALLOWED_ROOTS` includes `research/preregistration`), `:126-135` (protocol dict trusted; `git_dirty`/`dirty_diff_sha256` recorded, never enforced; the diff hash covers tracked files only).
- **Evidence beyond Codex.** The race window is not tiny: the directory is only created in `Manifest.__init__` after lock and protocol verification, seconds after the existence check. The frozen record shows the hazard was real: `research/preregistration/X3-A/DEVIATIONS.md` entry 2 (two launches; the first process wrote `sessions.csv`/`personas.csv` into a directory recreated by the second; `write_new` only protects the target file, not the directory).
- **Frozen X3-A check (read-only).** `manifest_X3-A-run.json` (`status: completed`, gate `G-HARNESS passed, 9/9`, started 17:46:34Z) records output hashes for `gate_G-HARNESS.csv`, `sessions.csv`, `personas.csv`; all three equal the files on disk today. The analysis manifest's input hash for `sessions.csv` equals the run manifest's recorded hash. Provenance nuance already disclosed: `sessions.csv`/`personas.csv`/manifest come from launch 1, `gate_G-HARNESS.csv` (hashed into that manifest) from launch 2; both gates were 9/9 and the run is deterministic.
- **Affects.** Future experiments (any run using the v1 tool). Frozen X3-A: documentation only.
- **New tool required?** **Yes**, `run_manifest_v2.py`, because editing v1 would break the hash chain of the three existing protocol manifests and is prohibited.
- **Minimal corrective action (not implemented).** Exclusive sentinel/lock created (`O_CREAT|O_EXCL`) in the parent directory **before** any preflight; results directory created with `exist_ok=False`; exclusive-create writes (or temp file + atomic rename); `try/finally` that records `status: aborted`; the tool itself verifies tag, protocol hash, protocol-manifest hash and dependency hashes and returns the protocol block (no caller-trusted dict); declared inputs and models are mandatory (empty list = error); tracked-diff hash plus an inventory of untracked files under the declared harness, SUT and input paths (scoped, so the flag is not saturated by unrelated untracked files); remove `research/preregistration` from the run-output allow-list.
- **Reclassification.** None. Optional registry note on the X3-A run provenance (gate file from launch 2), which `DEVIATIONS.md` already states.

### 2.2 O8 - no key-set assertions before paired X3-A aggregation - **CONFIRMED (narrowed)**
- **Location.** `x3a_analyze.py:33-44` (`cells`), `:46-48` (`diff`), `:100-107`. The persona list is a single sorted set shared by all conditions, and `acc[(c, s, p)]` raises `KeyError` if a persona is missing for a condition, so **persona** misalignment cannot be silent. What is silent: the training-seed set per condition is taken from that condition's own rows and aligned **by sorted position** in `A - B`; per-cell evaluation-seed completeness and duplicate rows are averaged without checks.
- **Frozen X3-A check (read-only, key counts only).** 63,000 rows; 0 duplicate (condition, training seed, stratum, persona, eval seed) keys; 26 conditions (15 seedless, 11 with the same five seeds 42/123/456/789/999); identical 40 grid and 5 frozen personas in every condition; one identical evaluation-seed set in every cell. The primary contrast is correctly aligned.
- **Affects.** Future analyses only. **New tool?** No; each new analysis version must assert complete, duplicate-free key sets across compared conditions and record them. **Reclassification:** none.

### 2.3 O10 / M3 - analysis without proof of a completed gated run - **CONFIRMED**
- **Location.** `x3a_analyze.py:92-100`: the manifest `protocol` block is `{"type": "prereg_git_tag", "tag": ...}` without hashes; only `sessions.csv` is added as an input; no read of `manifest_X3-A-run.json`; `--primary-stratum grid` (default) labels the output "CONFIRMATORY" for any CSV with the right columns (`:173`); analysis manifest `gate = {}`.
- **Frozen chain (verified above).** Run manifest completed, gate passed, output hash equals the analysis input hash. So the frozen chain holds; only the *enforcement* is absent.
- **Affects.** Future analyses only. **New tool?** No separate tool: a `require_completed_run(dir)` helper (status, gate, tag/protocol hashes, recorded output hash equals input hash) belongs in `run_manifest_v2.py`, and each new analysis must call it. **Reclassification:** none.

### 2.4 O12 - X2-B self-test can produce official-looking synthetic output - **CONFIRMED (design weakness)**
- **Locations.** `x2b_run.py:29-30` (`--selftest` and `X2B_SELFTEST_DIR`; missing env var raises `KeyError`), `:33-38` (`_StubManifest`), `:154-155` (stub manifest, `protocol = {"type": "selftest"}`), `:189-202` (synthetic reference texts, candidates, gold and scores), `:209` (`g3 = (maxdiff <= 0.002) or SELFTEST`), `:301` (the report text describes the frozen 64-answer arm with no self-test banner).
- **Nuance.** It needs an explicit flag, an environment variable and a not-yet-existing directory, and it produces no manifest, so it is detectable; but a synthetic result set can be placed under any chosen directory (including a would-be `results/`, which would also pre-empt the real run) with a forced-true derived gate and no banner.
- **Frozen check.** `manifest_X2-B-run.json` is `completed`, protocol tag `prereg/X2-B/v2`, gate `G-DERIVED-REPRO passed (max abs diff 0.000500)` computed from real data, five inputs plus the upstream model entry. The frozen X2-B run was not a self-test.
- **Affects.** Future X2-B-family runs only (the X2-B arm on X2-C). It does **not** block X1-A/B/C or X3-B. **New tool?** No; a new harness version for X2-C must move self-test code to a separate file (or force a `SELFTEST` banner, `selftest: true` manifest field, and refuse output under any `research/confirmatory/**/results*` path). **Reclassification:** none.

### 2.5 X2-B upstream model SHA-256 enforced only by prefix - **CONFIRMED**
- **Location.** `x2b_run.py:160-168` (`h_up.startswith(CFG["models"]["upstream"]["sha256_model_prefix"])`); `x2b_config.json` holds `"sha256_model_prefix": "821d1aa6"` (8 hex characters); the derived model uses the full hash. `PROTOCOL.md` also cites only the prefix.
- **Frozen check.** The completed manifest records the actual full digest `821d1aa69520101d6e0737f78a042ae25b19e5cb9160701909d10434f4aeb0ae` for the snapshot `c5ee24cb16019beea0893ab7796b1df96625c6b8` (the snapshot revision is in the configured path). Accidental substitution is negligible; the registered binding is nonetheless formally weak. Comparison of the recorded digest with the publisher's file identifier is an external check that was not made here.
- **Affects.** Future X2-B-family runs. **New tool?** No; register the full digest (and the model config/tokenizer files) in the new tag's config. **Reclassification:** none; add a note to `X2B-C001/C002` (EXPLORATORY already) that the upstream identity was registered by prefix and recorded by full digest.

### 2.6 O17 - X1-D final manifest does not bind inputs, SUT or models - **CONFIRMED (narrowed)**
- **Locations.** `x1d_run.py:35-48` (`verify_protocol`; the returned block has `protocol_sha256` but no `protocol_manifest_sha256`, unlike X3-A/X2-B), `:73-74` (no `add_inputs`, no `add_model`), `:91-94` (data actually read). Stored manifest: `inputs: []`, `models: []`, `lock_id: null` (by design, "unlocked").
- **Nuance.** `protocol_manifest.json` lists eight hashed dependencies that were asserted at run start: config, runner, `run_manifest.py`, `paper2_case_level_results.csv`, `RATER_1_COMPLETED.csv`, `services/evaluator/app.py`, `services/storage/database.py`, and the failing test file. So the case-level and rater inputs *were* bound by the protocol manifest and the tag message. **Not bound:** evaluator assets and models (CrossEncoder, SBERT, FAISS index, rubrics), the rest of the SUT tree, the rest of the test files, and any working-tree change beyond the recorded (saturated) dirty flag.
- **Frozen consequence.** X1D-C001..C003 stay VALID. Model/asset identity for the latency claim rests on the frozen hashes (e.g., `P2-C002`) and the post-run integrity checks (`PHASE4_INTEGRITY_REPORT.md`), not on the X1-D manifest; add a scope note.
- **Affects.** Future runs. **New tool?** A new runner version for any repeat or new X1 experiment; the v2 tool should make an empty input list an error. **Reclassification:** none.

## 3. Findings that remain non-blocking (validated)

| Lead | Codex | Validation and reasoning |
|---|---|---|
| **O3** limited mutation coverage | DOC-ONLY | **Agree.** The gating mutants prove the *gated* property (intact-loop equivalence) can fail; descriptive ablations are not gated (`X3A-C006` is descriptive). I **withdraw** my plan's "BLOCKING as a pattern" wording for O3: it is a design requirement for new harnesses (a per-branch mutation-coverage matrix reviewed with each new protocol), not a blocker on any existing result. |
| **O4** no `try/finally` around monkeypatches | DOC-ONLY | **Agree.** The process exits on exception; no completed-result false-pass path (`x3a_run.py:78-84,116,169`). Use `try/finally` in new harnesses. |
| **O6** lock check does not inventory extra packages; coarse site-packages hash | DOC-ONLY | **Agree.** The manifest does not claim a per-file hash (`run_manifest.py:57-65,139-150`); document the limitation; new locked environments should carry wheel hashes. |
| **O14** NaN bootstrap replicates dropped | DOC-ONLY | **Agree, and I checked the stored file:** `metrics_point_ci.csv` has `valid_reps = 10000` for derived, upstream, TF-IDF, BM25, token-overlap, length-only, `ref_R_mapped` and the composite; only the reference column `ref_S2_eff` has 9,991. All primary derived-minus-upstream contrasts have 10,000 valid replicates (`paired_differences.csv`). No effect on X2B-C001..C004. |
| **O19** crash leaves manifest at `started` | DOC-ONLY | **Agree.** `x1d_run.py:83-85,125`: a missing `junit.xml` raises before `finish()`; `started` is distinguishable from `completed`, so it cannot report success. v2 should write `aborted` in `finally`. |

Other lead dispositions: I accept Codex's REFUTED for O2 (the gate never claimed to validate the grid generator), O9 (primary summary is computed first), O11 (disclosed operationalisation), O16 (same pair construction), and for O13 I accept that the null recomputes the same pooled statistic (my point was only that the null conditions on question structure: an interpretation caveat, not a harness issue). For O18 I accept that the P99 bootstrap is not degenerate but wide and unstable at n = 100, which is a measurement-scope limitation already labelled. O1, O15 and M1 are confirmed documentation-only.

## 4. O7 - what ChatGPT must review (no new analysis done)

Codex marked O7 INCONCLUSIVE (statistical interpretation, out of harness scope). ChatGPT should review the following; nothing has been recomputed.

**Object.** The pre-registered primary contrast: persona x training-seed matrix D (40 grid personas x 5 checkpoints) of MAE(`PPO | G`) minus MAE(`Constant-Same | G`), persona-level means over 20 evaluation seeds; two-way independent resampling of personas and seeds, B = 10,000, `default_rng(42)`, percentile 95% CI (`x3a_analyze.py:51-67`). Registered result: point -0.0350, CI [-0.0818, +0.0021], class Equivalent for margin +/-0.12.

**Questions for ChatGPT.**
1. **Estimand.** Are the five checkpoints a random sample of trainings (registered "second random factor") or a fixed set? If fixed, the seed dimension should not be resampled; if random, what is the target population of trainings?
2. **Few clusters.** Percentile bootstrap intervals with 5 resampled seed clusters are known to be too narrow. Which correction is appropriate (small-cluster / t-type interval with 4 degrees of freedom on seed means, studentised or BCa interval, or a variance-component estimate)?
3. **Crossed-factor bias.** Independent resampling of two crossed factors (the "pigeonhole" bootstrap) is reported to overstate variance (reference to be verified by ChatGPT). Which direction dominates here: this upward bias or the few-cluster narrowness?
4. **Candidate sensitivity variants to approve (specification only):** persona-only cluster bootstrap on seed-averaged differences; leave-one-seed-out and jackknife across seeds; a t-based interval on the five seed-level mean differences; studentised or BCa versions of the registered bootstrap; a variance-component decomposition (persona, seed, persona x seed).
5. **Decision-rule sensitivity (arithmetic on the registered values, not a new analysis).** The class is Equivalent only if the lower limit stays above -0.12. The registered lower limit lies 0.0468 below the point estimate (-0.0350), and the point estimate lies 0.0850 above -0.12, so the interval's lower side would have to widen by about **1.8 times** to lose the class. The largest simple small-cluster factor on the seed component alone, sqrt(5/4) = 1.118, is far below that. ChatGPT should confirm this reading and decide what robustness table (if any) is worth reporting.
6. **Status of any sensitivity result.** The pre-registered classification stands; a sensitivity analysis can only be reported as a labelled robustness check, never as a replacement.

## 5. Final lists

### A. Confirmed future-run blockers
1. **Run-once / manifest provenance (O5/O20)** - blocks any new confirmatory run that would use `run_manifest.py` v1; requires `run_manifest_v2.py`.
2. **Paired-analysis key assertions (O8)** - blocks any new analysis that pairs conditions/seeds/personas until the check exists in the analysis code.
3. **Analysis-to-run linkage (O10/M3)** - blocks any new analysis labelled confirmatory until it verifies a completed, gated run manifest.
4. **X2-B harness self-test (O12) and prefix-only upstream digest** - block only the reuse of the `x2b_run.py` family (X2-B arm on X2-C); they do not block X1-A/B/C or X3-B.
5. **Input/SUT/model binding (O17)** - blocks new X1 runs unless their runners declare and hash inputs, SUT dependencies and models (the v2 tool should enforce non-empty inputs).

### B. Documentation / claim limitations only
O3, O4, O6, O14, O19 (validated above); O1 (ablation branches: `X3A-C006` remains descriptive); O15 (report header text "v1"); M1 (dirty flag saturated); the X3-A run provenance nuance (gate CSV from launch 2, disclosed); the X2-B upstream prefix registration; the X1-D binding scope; O7 pending the ChatGPT review.

### C. Frozen-result consequences
**None.** No frozen result is reclassified, invalidated or rerun. Verified read-only: all three X3-A outputs match the run manifest, the analysis input hash equals the run manifest's `sessions.csv` hash, X3-A key sets are aligned and duplicate-free, the X2-B run was a real (non-self-test) run with the real derived-reproduction gate, and NaN dropping did not touch any primary X2-B contrast. Optional documentation notes (not made): registry notes on `X3A-C006`, X2B upstream identity, X1D scope; `DEVIATIONS.md` already covers X3-A entry 2.

### D. Minimal next implementation set (not started)
1. `research/tools/run_manifest_v2.py` (new file, own tag, brief Codex re-audit before first use): the items in 2.1, plus `require_completed_run(dir)` and a `selftest` namespace rule.
2. In the analysis code of each new experiment: a shared or copied `assert_paired_keys` check (complete, duplicate-free, identical key sets) and a call to `require_completed_run`.
3. Harness-template rules for new experiments: self-test in a separate file; full digests for every model and asset; declared and hashed inputs including SUT dependencies and models; `try/finally` with `aborted` status; per-branch mutation-coverage matrix reviewed in the protocol.

### E. Items requiring Sparsh + ChatGPT decision
1. Accept the scoping of findings 4 and 5 as reuse-blocking only (not blocking X1-A/B/C or X3-B).
2. Approve the scope of the minimal implementation set (D) and whether Codex re-audits `run_manifest_v2.py` before X1-C is tagged (recommended).
3. ChatGPT's review of O7 (section 4).
4. Whether to record the optional documentation notes (registry notes; a `DEVIATIONS.md` addition) and where, since some of those files sit under tagged directories.
5. No other new scientific decision arises from this validation.
