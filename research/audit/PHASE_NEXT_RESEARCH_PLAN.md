# PHASE-NEXT research plan (planning only; written 2026-09-20)

**Status of this document.** Read-only planning. No experiment was run, no SUT/evaluator/PPO file, frozen artifact, result or protocol was touched, no manuscript prose was written, nothing was sent or submitted. The only file created is this one. Conference facts were read from web pages on 2026-09-20 and are stated with their verification status (section 9); anything not read from an official page is marked **UNVERIFIED**. Nothing here is a ChatGPT review or a Codex audit; observations labelled "pre-audit observation" are the executor's own reading of code and are inputs to those reviews, not findings of them.

Task labels used throughout: **[FROZEN SCIENCE]**, **[OPEN SCIENTIFIC DECISION]**, **[RESEARCH SUPPORT / INSTRUMENTATION]**, **[PRODUCT CHANGE]**, **[EXTERNAL DEPENDENCY]**, **[DOCUMENTATION ONLY]**. Section 3.1 classifies every proposed action.

**Revision 2 (2026-09-20, correction pass).** Changes from revision 1: (i) independent review is a *new* quality-control layer and does not retroactively invalidate the frozen X3-A, X2-B or X1-D results (sections 1, 4.0, 4.3); (ii) D-KFT is replaced by a root-cause triage of the failing test, with the fix/no-fix decision deferred (section 5.6); (iii) the X1-C weakened-configuration control is redefined as a predefined, documented configuration mutation (section 5.2); (iv) X1-B is split into an invariance/containment test with the candidate answer held fixed and a separate behavioural stress test (section 5.3); (v) X3-A claims are localised to analyses and references, default **no rerun** (section 7.7); (vi) Paper-1 portfolio changed to ICETC primary / ATIS fallback, and the ICETC record corrected: the 30 Aug date was superseded by the official 31 Aug notice extending to 10 Oct, so it is not an unresolved conflict, and the official CFP page lists AI-in-Education, security/privacy and assessment tracks (sections 9, 10); (vii) decision set reduced (section 13); (viii) a Paper-3 limitation (runtime vs training dimension 4) added from the frozen audit record; (ix) `CODEX_HARNESS_AUDIT_BRIEF.md` created. Nothing outside these two files was changed.

---

## 1. Executive status

| Item | State (2026-09-20) |
|---|---|
| Executed and frozen | X3-A (confirmatory), X2-B old-benchmark arm (exploratory), X1-D, X2-A, X3-0a/b/c/d, Paper-1 stored-claim analysis. Registry: 115 rows (VALID 58, WITHDRAWN 28, HISTORICAL 5, DESIGN-ONLY 9, EXPLORATORY 15). Tags `prereg/*`, `freeze/*`, `sut/X1/build-A`. |
| Not executed | X1-A, X1-B, X1-C (not constructed), X2-C and X2-B-on-X2-C (human/ethics gate), X3-B (parked; trigger not fired; D-N2 open). |
| Independent review | Not yet done: Codex audit of `x3a_lib.py`, `x3a_run.py`, `x3a_analyze.py`, `x2b_run.py`, `x1d_run.py`, `run_manifest.py`; ChatGPT review of the three tagged protocols. This is a **new quality-control layer**. It does **not** retroactively invalidate the executed X3-A, X2-B and X1-D results, which were protocol-tagged, executed, frozen, hashed and preserved and remain frozen and reviewable. It **gates (a) new confirmatory experiments** (X1-A/B/C, X2-C, X3-B) **and (b) which claims a future manuscript may use** (only claims that survive the methodology/provenance review). No frozen experiment is to be rerun merely because it lacked independent review. |
| Paper 3 | Evidence essentially complete for a scoped claim (equivalence + volatility + accounting). Remaining work: audit, review, packaging. |
| Paper 1 | Only X1-D is measured. Fault, containment and LLM-isolation claims are withdrawn or design-only until X1-A/B/C run. |
| Paper 2 | Only exploratory evidence (64 constructed answers, 8 questions). Confirmatory X2-C blocked by external human/ethics dependencies that have not started (enquiries drafted, not sent). |
| Critical path | External (institutional determination, provenance, raters) for Paper 2; audit + X1 construction for Paper 1; audit + review + packaging for Paper 3. |
| Deadline reality | Verified deadlines cluster on 30 Sep - 12 Oct 2026 (10-22 days away). Only Paper 3 could approach them, and only if the audit/review gates clear in days. No gate will be weakened to meet a date (section 11). |

---

## 2. Frozen versus open

### A. FROZEN SCIENTIFIC COMPONENTS **[FROZEN SCIENCE]**
Must remain byte-identical (verified by the 366-file baseline `research/analysis/phase1/frozen_hashes_phase0_baseline.txt` and per-experiment manifests):

| Component | Location / identifier |
|---|---|
| Core PREPAIred architecture (orchestrator, audio, evaluator service, coding executor, storage, backend, UI) | `agents/`, `services/`, `apps/`; SUT build `sut/X1/build-A` -> `3904749` |
| Technical evaluator formulation `0.15*S1 + 0.35*S2_eff + 0.50*R`, S2 x0.6 when R <= 0.30, theta, R mapping, bonus/penalty/cap rules | `services/evaluator/app.py` |
| ScoreValidator | `services/` (see `research/audit/score_validator_audit.md`) |
| CrossEncoder checkpoint | SHA-256 `6a241a55...4450` (registry `P2-C002`); upstream reference weights prefix `821d1aa6` |
| PPO state (6-D), action (Discrete 3), reward, environment and SB3 configuration | `rl/env/interview_env.py`, `rl/training/simulated_candidate.py`, `research/experiments/paper3/frozen_config.yaml` |
| Guardrail definitions G1, G2, G4, G5, G6 and counting definitions (rule activation = `overridden` flag; action override = raw != final; attempted boundary action = executed action would leave [1,5] before clipping) | `rl/guardrails.py` |
| Frozen Paper-3 checkpoints (seeds 42/123/456/789/999) | `research/experiments/paper3/checkpoints/`, tag `v1.0-paper3-complete` |
| Frozen human gold and old benchmark (64 answers, 8 questions, 3 raters) | `research/data/evaluator_benchmark/final_human_gold.csv` (`363dbe6d...6ce2`) and the hash-pinned rater files |
| Completed results | `research/confirmatory/{X3-A,X2-B,X1-D}/results/`, `research/analysis/phase1/*`, listed in `research/analysis/RESULT_HASHES_phase3.txt`; tags `freeze/*` |
| Protocols / tags | `prereg/X3-A/v1`, `prereg/X2-B/v1`+`v2`, `prereg/X1-D/v1`; `PHASE0_DECISION_LOCK.md` |
| Truth authority | `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` (rho 0.3812 current; 0.6975 superseded pilot) |
| Frozen-by-`CLAUDE.md` directories | `research/papers/*`, `research/results/*`, `research/CLAUDE_HANDOFF/*`, pre-existing `research/audit/*`, `ablation/results/*`, existing `experiments/*` |

### B. OPEN SCIENTIFIC DECISIONS **[OPEN SCIENTIFIC DECISION]** (Sparsh + ChatGPT only)
Consolidated in section 13, which is now deliberately short. In short: approval of the audit/review gate and the provisional publication portfolio; before X1-C, review of the Codex findings, of the failing-test triage (section 5.6) and of the X1-C attack/control/oracle design; before X1-B, approval of the corrected two-part design; before X2-C, D-X2-TAU, the human/authoring pathway and the institutional determination. Parked and **not** to be raised now: D-N2 and D-X3B-OP (X3-B), PPO retraining, venue formatting, exact X2-C item counts, and the identity of "ICTCS 2026" and "ICMETE 2026" (left OPEN).

### C. RESEARCH-SUPPORT / INSTRUMENTATION CHANGES **[RESEARCH SUPPORT / INSTRUMENTATION]** (safe: not the SUT)
New files only: `research/tools/run_manifest_v2.py` (new file; v1 stays hash-matched for existing tags), X1/X2 harness code under `research/confirmatory/<EXP>/`, attack programs, mutant/injector builds kept **outside** the SUT tree, canary listeners, dependency-enumeration table, adversarial prompt file, precision-simulation script, evidence-package builders, new locked environments under `envs/`, protocol/registration documents, run manifests, Codex audit brief.

### D. PRODUCT CHANGES **[PRODUCT CHANGE]**
Default: **none at this stage.** Anything below would be a product change and is NOT planned:
- changing the failing test `test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics` **or** the code it exercises (`build_rl_observation`, dimension 4). Only a root-cause triage is planned (section 5.6); a red regression test is not by itself a reason to create a new scientific build, and no build B is to be created merely to obtain a 226/226 suite;
- wiring the unused `RESTRICTED_C_HEADERS` set into `validate_source_safety` (pre-audit observation, section 5: the set is defined and never used);
- adding a `FeedbackValidator` (explicitly excluded by the locked decisions);
- any change to scoring, difficulty, guardrail semantics, evaluator weights or CrossEncoder;
- reconciling `.venv` pin conflicts (numpy 2.5.2, torch 2.11.0, accelerate 1.13.0 vs `requirements/*.txt`);
- an accept threshold for the evaluator (N5: none exists; adding one would be a product change, not an analysis choice).

---

## 3. Product versus research-support boundary (rules of engagement for the next stage)

1. All harness, mutant and injector code lives in new directories; SUT files are imported or executed, never edited. Test-only mutants are constructed at run time or in a copy that is never tagged as the SUT. Security-configuration controls are **predefined, documented configuration mutations** listed in the protocol (section 5.2), not ad-hoc manipulations.
2. A finding that would need a SUT change is **reported as a defect** under `X1_PROTOCOL_DRAFT.md` section 2 (fix only under `sut/X1/build-B`, rerun the entire relevant campaign, keep both builds). The executor never fixes on build A.
3. Changing a hashed harness file after a protocol tag requires a new tag and, if any result already exists, an amendment. `run_manifest.py` is a listed dependency in the existing X3-A, X2-B and X1-D protocol manifests, so it must **not** be edited; improvements go into a versioned new file.
4. Dry runs are allowed only on non-confirmatory fixtures, with results discarded and logged (precedent: `research/confirmatory/X3-A/DRYRUN_LOG.md`). Because the audit gates confirmatory execution, the default in this plan is "construct and dry-run mutation controls after the audit passes"; construction and documentation before that are unrestricted.

### 3.1 Action ledger (every proposed action, one label each)

| # | Action | Label |
|---|---|---|
| 1 | Keep the SUT, evaluator, CrossEncoder, PPO state/action/reward/config, guardrails, checkpoints, human gold, X3-A/X2-B/X1-D results, tags and protocols unchanged | [FROZEN SCIENCE] |
| 2 | Independent Codex read-only audit of the six harness files (brief: `CODEX_HARNESS_AUDIT_BRIEF.md`) | [RESEARCH SUPPORT / INSTRUMENTATION] (run by Sparsh; findings validated by the executor) |
| 3 | ChatGPT methodology review of the three tagged protocols and of new X1 designs | [EXTERNAL DEPENDENCY] |
| 4 | Root-cause triage of the failing test (read-only; section 5.6) | [DOCUMENTATION ONLY] |
| 5 | Decide whether a build B is warranted after the triage | [OPEN SCIENTIFIC DECISION] |
| 6 | Any edit to the failing test, `build_rl_observation` or any SUT file | [PRODUCT CHANGE] (not planned) |
| 7 | `run_manifest_v2.py` (new file; v1 untouched) | [RESEARCH SUPPORT / INSTRUMENTATION] |
| 8 | X1-C construction: attack programs, oracles, canaries, weakened-configuration table, flag-parity gate, dry-run design | [RESEARCH SUPPORT / INSTRUMENTATION] |
| 9 | Approve the X1-C attack/control/oracle design | [OPEN SCIENTIFIC DECISION] |
| 10 | X1-B channel enumeration, prompt-set authoring, static check, LLM-wired mutant | [RESEARCH SUPPORT / INSTRUMENTATION] |
| 11 | Approve the corrected X1-B design (fixed-answer invariance vs behavioural stress) | [OPEN SCIENTIFIC DECISION] |
| 12 | Real Qwen service and recorded model files for X1-B | [EXTERNAL DEPENDENCY] |
| 13 | X1-A dependency-enumeration table and injector designs | [RESEARCH SUPPORT / INSTRUMENTATION] |
| 14 | Running X1-A/B/C | not before audit + review + design approval (each a confirmatory experiment) |
| 15 | X3-A claim localisation (section 7.7); no rerun | [DOCUMENTATION ONLY] |
| 16 | Paper-3 non-confirmatory evidence package | [DOCUMENTATION ONLY] |
| 17 | X3-B, PPO retraining, reward/env changes | [FROZEN SCIENCE] / parked; not proposed |
| 18 | D-X2-TAU (primary endpoint, rho_min or baseline-relative criterion, binary criterion for AUROC) | [OPEN SCIENTIFIC DECISION] |
| 19 | Institutional/ethics determination, consent, rater and author provenance, trainer/model provenance reply | [EXTERNAL DEPENDENCY] |
| 20 | X2-C item authoring, rater contact | not authorised; blocked by 19 |
| 21 | Provisional publication portfolio approval | [OPEN SCIENTIFIC DECISION] |
| 22 | Confirming unverified venue facts (MLNLP, AIEI, SAC AIED track, identity of ICTCS and ICMETE) | [EXTERNAL DEPENDENCY] |
| 23 | Three evidence-package directories and builder | [DOCUMENTATION ONLY] / [RESEARCH SUPPORT / INSTRUMENTATION] |
| 24 | D-F1 supersession banners in four stale documents | [DOCUMENTATION ONLY] |
| 25 | Manuscript text, abstracts, proposals, submissions, external emails | not authorised |

---

## 4. Independent harness audit plan (Codex; not performed here)

### 4.0 Scope and consequence of the audit
- The audit is a **new** quality-control layer, not a retroactive validity test. The executed X3-A, X2-B and X1-D results stay frozen, hashed and reviewable regardless of the audit outcome.
- **New confirmatory experiments** (X1-A/B/C, X2-C, X3-B) wait for the audit.
- **Future manuscript claims** may use only claims justified after the audit and the ChatGPT methodology/provenance review. A finding against a frozen analysis is handled by narrowing or labelling the affected claim (registry note, wording constraint); a new registered re-analysis is considered only if a *central* claim depends on the defective step, and it is never a silent rerun or an edit of a frozen result.
- The default for X3-A, X2-B and X1-D is **no rerun**.

**Audit brief:** created as `research/audit/CODEX_HARNESS_AUDIT_BRIEF.md` (path + SHA-256 of the six files and their protocol manifests and tags, the checklist below, O1-O20 as leads, the finding taxonomy, a fixed report format, and an instruction that Codex works read-only in a separate worktree; `CLAUDE.md`: never two agents editing the same files). Claude validates each Codex finding before any action. The audit itself has **not** been run.

### 4.1 Checklist applied to every harness
1. Hard-coded expected outcomes (literals standing in for measured values).
2. Result-dependent branching (any code path selecting thresholds, subsets, metrics, seeds or exclusions after seeing data).
3. Aggregation correctness (unit of analysis, grouping keys, alignment of persona/seed/question indices across conditions).
4. CI correctness (bootstrap structure vs the registered design; percentile method; NaN handling; B; RNG stream order).
5. Seed handling and random-state leakage (global RNG use, shared streams, seed collisions, monkeypatch state restored on exceptions).
6. Fixture dependence (gate passes because the fixture cannot exercise the property).
7. Mutation-control validity (does a detected mutant prove the *oracle* can fail, or only that two code paths differ?).
8. Data leakage (using labels, stored results or post-hoc information in scoring or gating).
9. Aborted-run, failed-run and duplicate-run handling (including concurrent launches).
10. Manifest and hash generation (what is hashed, when, and whether it is enforced or only recorded).
11. Protocol/version association (tag -> protocol hash -> harness hash -> run manifest).
12. Analysis separated from raw generation (analysis reads only hashed raw output).
13. Post-result information (constants, report text or configuration edited after results).
14. **Can the output pass without the underlying property being true?** (the central adversarial question; try to construct a trivial or broken implementation that still passes each gate).

### 4.2 Pre-audit observations (executor's reading; **leads, not confirmed defects**; each to be confirmed or refuted by Codex)

| # | File | Observation | Likely class |
|---|---|---|---|
| O1 | `x3a_lib.py` `shield()` | Local copy is compared with the frozen shield only for the full rule set, `consecutive_failures=0`, infrastructure failure False, default medium band; the rule-ablation (`disabled`) branches are never compared with an independent reference, only shown to change outputs. | Documentation-only unless an ablation branch is wrong; then blocking for X3-A ablation rows (descriptive only) |
| O2 | `x3a_run.py` `gate_harness` | Equivalence to the frozen loop is tested on the 5 frozen personas only; the 40-persona grid (other types x skills, other targets) has no frozen counterpart, so grid-specific code (`persona_grid`, target rule, skill/type parameter passing) is not covered by G-HARNESS. Random, Oracle-rule and Controller policies have no frozen reference. | Documentation-only if `SimulatedCandidate`/`InterviewEnv` are shared code; blocking if a persona-parameter path differs |
| O3 | `x3a_run.py` mutation controls | Gating mutants are detected via `mism > 0` on the frozen fixture; two upper-threshold heuristic mutants were invisible on the fixture and were downgraded to informational (documented in `DRYRUN_LOG.md`). A mutation coverage matrix per branch of shield/heuristic/controller does not exist. | Documentation-only for X3-A (primary contrast does not use the heuristic); blocking as a *pattern* for X1 (mutation controls must be sensitive by construction) |
| O4 | `x3a_run.py` monkeypatching | `fm.PPO` and `fm.AlignedInterviewEnv` are patched on the frozen module and restored without `try/finally`; an exception mid-gate leaves the frozen module patched in-process. | Documentation-only (process ends) |
| O5 | `x3a_run.py` run-once protection | `out_dir.exists()` check then create is not atomic and there is no lock file; a running process can write into a recreated directory (this happened: `DEVIATIONS.md` entry 2). | Blocking for new experiments (fix in v2 tool); documentation-only for X3-A (results deterministic and complete, disclosed) |
| O6 | `x3a_run.py` `verify_lock` | Checks only `name==version` lines of the lock; extra installed packages are not detected; site-packages listing is name/size/mtime of top-level entries only. | Documentation-only |
| O7 | `x3a_analyze.py` bootstrap | Independent resampling of 40 personas and 5 training seeds; percentile CI with 5 seed clusters is known to be too narrow. Reported primary CI [-0.0818, 0.0021] is far from the +/-0.12 margin (upper bound 0.0021), so the class is robust to plausible inflation, but this must be shown, not assumed. | Documentation-only if a sensitivity recomputation keeps the class; blocking (re-analysis under a new registered analysis) if not |
| O8 | `x3a_analyze.py` `cells()` | Alignment across conditions relies on sorted persona IDs and sorted seed keys with no assertion that all conditions contain identical personas and seeds. | Documentation-only if alignment verified offline on stored `sessions.csv` |
| O9 | `x3a_analyze.py` | One RNG stream is shared by all summaries; changing call order changes secondary CIs (primary is first, so stable). `--primary-stratum` is a CLI switch that can alter which stratum is primary. | Documentation-only |
| O10 | `x3a_analyze.py` | Does not check that `sessions.csv` equals the SHA-256 recorded by the run manifest (only hashes it at start and end of analysis). | Documentation-only if hashes match on inspection |
| O11 | `x3a_analyze.py` | `trigger = cls != "Equivalent"` is hard-coded (D-X3B-OP). | Documentation (already disclosed) |
| O12 | `x2b_run.py` | Self-test mode inside the production script (`--selftest`, `X2B_SELFTEST_DIR`, `g3 = ... or SELFTEST`, stub manifest). Not reachable without the flag, but a production runner containing a gate bypass is an audit target. | Documentation-only; recommend separation in v2 |
| O13 | `x2b_run.py` | Permutation null permutes gold within questions while the observed statistic is the pooled Spearman; the two are not the same estimand (the null conditions on question means). Interpretation caveat. | Documentation-only |
| O14 | `x2b_run.py` `ci()` | NaN replicates are dropped; `valid_reps` is reported. AUROC is NaN when a resample has no adversarial or no correct items. | Documentation-only |
| O15 | `x2b_run.py` | Report header text says `prereg/X2-B/v1`; manifest records v2 (disclosed). Hard-coded string in a hashed script. | Documentation-only |
| O16 | `x2b_run.py` | Pair construction (question + reference answer) is validated by G-DERIVED-REPRO (max diff <= 0.002 vs stored R) for the derived model only; the upstream arm reuses the same pair code. Strength: gate is defined before upstream output. | Documentation-only |
| O17 | `x1d_run.py` | No `add_inputs`: the manifest hashes neither the case-level CSV nor `RATER_1_COMPLETED.csv` nor the SUT tree; only the git commit and dirty flag are recorded. pytest itself may write files under the repo (checked post hoc by the 366-file baseline, not by the runner). | Documentation-only for X1-D; blocking pattern for new runs (v2 tool must hash inputs and diff the SUT tree before/after) |
| O18 | `x1d_run.py` latency | 101 requests cycle through 64 items (`i % 64`), so 37 repeated items may benefit from caches; P95/P99 bootstrap with n=100 is degenerate for P99. | Documentation-only (already labelled scope-limited) |
| O19 | `x1d_run.py` | If pytest crashes without `junit.xml`, `ET.parse` fails after latency work; manifest stays `started`. No explicit `aborted` state. | Documentation-only |
| O20 | `run_manifest.py` | `write_new` checks existence then `write_text` (non-exclusive open; race). `ALLOWED_ROOTS` includes `research/preregistration`, so a buggy runner can write into protocol directories. `git_dirty`/`dirty_diff_sha256` are recorded, never enforced, and ignore untracked files. Site-packages hash uses `sys.prefix/Lib/site-packages` (Windows layout). Protocol dict is trusted from the caller. | Blocking for new confirmatory runs *as tool behaviour* (fixed in `run_manifest_v2.py`); documentation-only for existing results |

### 4.3 Classification of findings

**BLOCK further confirmatory execution** (X1-A/B/C, X2-C, X3-B) if Codex finds any of:
- a gate, oracle or PASS/FAIL that can succeed while the property is false (14. above), or an oracle depending only on a status string;
- a mutation control that cannot fail, or whose detection is unrelated to the oracle's job;
- result-dependent selection of thresholds, subsets, metrics, seeds or exclusions;
- non-determinism or seed leakage that changes results between identical invocations;
- a protocol/lock/hash binding defect that lets results be attributed to the wrong tag, protocol, environment or input;
- non-atomic write-once protection that can overwrite raw results;
A finding of the last kinds that concerns an **already frozen** experiment does **not** block anything by itself and does not invalidate the frozen result. Its consequence is claim-level (narrow, label or, for a central claim only, consider a new registered re-analysis) and is decided by Sparsh + ChatGPT after Claude validates the finding. Example: if a wrong aggregation in a primary statistic could change a classification, the corresponding registry claim is marked incomplete until resolved.

**Documentation-only** (record in `DEVIATIONS.md`/registry notes; no rerun): wrong or stale text (O15), undisclosed limits, unrecorded environment details, sensitivity checks that leave every classification unchanged (O7 if it holds), unused code paths, cosmetic manifest gaps for finished runs (O17, O19).

**Require a new tagged harness version:** any change to a file listed in a protocol manifest that would change behaviour or outputs. Concretely: (i) `run_manifest_v2.py` (new file) with exclusive-create writes, narrowed allow-list (drop `research/preregistration`), enforced clean tree or explicit dirty-diff hash, input/SUT-tree hashing, a run lock/sentinel (O5, O17, O20); (ii) new harness versions per experiment tagged `prereg/<EXP>/vN`; (iii) only if a blocking finding affects a *central* claim of an existing result and Sparsh + ChatGPT decide so, a **new registered re-analysis** (new experiment ID, new tag), never an edit or automatic rerun of the frozen result.

---

## 5. Paper 1 - X1-C / X1-B / X1-A

### 5.1 Dependency graph

```
Codex audit (run_manifest, harness pattern)  ---->  run_manifest_v2 (new tool, tagged)
ChatGPT review of X1 draft (pairing in X1-B, oracle defs) ---->  protocol drafts
                                                            |
  Failing-test root-cause triage (5.6; read-only) -> Sparsh + ChatGPT decide if a build B is warranted -> SUT tag (build A retained unless B is chosen)
                                                            |
 X1-C: attack programs + oracles + permissive control + canaries + flag-parity gate ----> dry-run mutation controls ----> tag prereg/X1-C/v1 ----> run ----> freeze
 X1-B: prompt set (>=30 pairs, hashed) + Qwen service + AST check + LLM-wired mutant --> dry-run --> tag --> run --> freeze
 X1-A: dependency-enumeration table (frozen) + injectors + one mutant per scenario ----> dry-run --> tag --> run --> freeze
 X1-D: DONE (tag prereg/X1-D/v1)
 All three -> evidence package -> (Paper-1 manuscript only after gate list in 5.5)
```
Recommended order (unchanged from the sprint report): X1-C (Docker available, self-reporting programs), then X1-B, then X1-A (largest enumeration).

### 5.2 X1-C - Security oracle campaign

| Field | Content |
|---|---|
| Scientific question | For each attack program: did the payload execute, was the effect contained, and did the host stay unchanged, with the executor's status string recorded but not decisive? |
| Status | Not constructed. Frozen predecessor results are withdrawn (`P1-C006`) or partial (`P1-C003`: 4 of 9 outcomes discriminate). |
| Changes SUT? | No. Instrumentation only. Anything the run reveals about the SUT is a reported defect (build B only). |
| Exact blockers | (1) Codex audit; (2) ChatGPT review of the oracle and permissive-control definitions; (3) construction work; (4) Sparsh + ChatGPT review of the failing-test triage (5.6): the triage indicates the failure does not touch the sandbox path, so it is not expected to block X1-C, but the build decision is theirs; (5) Docker Desktop/WSL2 must be running at construction and run time. No human-subject dependency. |
| Can be prepared now | Attack programs, oracle code, canary listener/hash setup, argv-capture wrapper, flag-parity gate, dry-run design, `run_manifest_v2`, draft protocol text. Not the dry run's confirmatory use and not any tagged run. |

**Verified facts from the code (pre-audit observations, for the four-layer separation):**
- `agents/coding_executor/sandbox_policy.py`: the static pre-flight filter rejects empty source, source > 64 KB, and the regex `ptrace(`. `RESTRICTED_C_HEADERS` (sys/socket.h, netinet/in.h, arpa/inet.h, netdb.h, sys/ptrace.h, sys/syscall.h, linux/futex.h) is **defined but never referenced** (grep over `agents/` finds only its definition). A program including `sys/socket.h` therefore passes the pre-flight filter; only Docker flags stand between it and the network. The docstring itself says the filter is auxiliary and Docker is the boundary.
- `agents/coding_executor/coding_executor.py`: shipped flags on both compile and run containers: `--user 1001:1001 --net=none --cap-drop=ALL --security-opt=no-new-privileges --cpus --memory=128m --memory-swap=128m --pids-limit=32 --read-only --tmpfs /workspace:rw,exec,size=32m -v <hosttmp>:/input:ro`. Containers are not named. gcc runs *inside* the container (compile-time attacks are in scope). `case_status` is derived partly from string heuristics (`"oom"`, `"malloc failed"` in stderr/stdout) and exit codes 124/137.
- Per-test `stdout`, `exit_code`, `status` are returned, so attack programs can self-report through the shipped `compile_and_execute`.

**Four layers, each measured separately (the oracle must not be a function of the status string alone):**

| Layer | What it is | Observable (independent of the executor status) | Note |
|---|---|---|---|
| 1. Static pre-flight | `validate_source_safety` | Return of the function called directly on the attack source (blocked/allowed + reasons); `status == "policy_blocked"` from the executor is the same fact, recorded as agreement check | Report per attack whether the pre-flight alone stops it. Attacks blocked here have **not** tested Layer 2, so each containment-intent attack needs a variant that passes Layer 1 (e.g., raw `syscall()` without the literal `ptrace(`); the `ptrace` literal is retained as the Layer-1 test |
| 2. Actual sandbox execution | Program compiled and run in the container | Self-report markers printed by the program before and after each attempt (`connect()` return + `errno`, `fopen` result + `errno`, `fork` count until `EAGAIN`, allocation progress), captured `stdout`/`exit_code`; a marker proving the payload line was reached | Distinguishes "blocked by control" from "harmless/never reached" (the defect behind `P1-C003`) |
| 3. Observed runtime containment | Control actually prevented the effect | Program-observed failure (`ECONNREFUSED`/`ENETUNREACH`, `EROFS`, `EAGAIN`, SIGKILL); host-side independent observer: `docker events` stream (oom, die, exit code) captured by the harness during the run, plus `docker ps -a` before/after (orphan containers, e.g. after host-side timeout of the compile step, which kills the CLI, not necessarily the container) | Peak memory/PIDs versus limits from the program's own counters and events |
| 4. Host/system side effects | Anything outside the container changed | Canary files (hash before/after) placed in the host directory mounted at `/input` and in a sibling host directory; local TCP listener bound on the host that must receive nothing; before/after listings of docker containers, networks, volumes, and the temp mount directory | Docker Desktop runs containers in a WSL2 VM sharing one Linux kernel: only tested attack classes are covered; no claim of kernel-escape resistance; no "secure" |

**Positive control = a predefined, documented weakened configuration (revised).** The design is a two-arm comparison in which everything except one documented security setting is identical:

```
NORMAL (shipped) CONFIGURATION  -> attack program A -> expected: effect contained (observable)
PREDEFINED WEAKENED CONFIGURATION W_k -> the same attack program A -> expected: observable violation
```
- **Predefined table, fixed in the protocol before any run:** each row W_k names exactly **one** security-configuration change, the attack class it is meant to un-contain, and the *observable* violation that must appear (e.g., W1: network mode `none` -> a bridge network with a **local** canary listener, expected observable: the listener receives the connection and the program reports `connect()` == 0; W2: writable bind mount of a host canary directory instead of `:ro`, expected: canary hash changes; W3: no `--pids-limit`, expected: the fork attack exceeds 32 children; W4: no `--memory` limit, expected: allocation exceeds 128 MB with no OOM event; W5: `--read-only` removed, expected: write outside `/workspace` succeeds). No row is added, edited or selected after seeing behaviour.
- **Mechanism:** the harness records the exact `docker run` argv the shipped SUT builds (flag-parity gate: it must equal a frozen expected list), and each W_k is the recorded argv with that single documented change applied. This keeps every other flag, image, user, tmpfs, mount and timeout identical to the shipped path; it is a *configuration* mutation, not an edit of the SUT or of the attack, and the mutation is logged verbatim as a raw output.
- **Validity criteria for the control (Codex and ChatGPT review each):** (i) W_k is a genuine weakening of a documented control (not an unrelated change); (ii) the same attack source (same hash) and the same harness/oracle are used in both arms; (iii) an **observable** violation is measured (program self-report, listener receipt, canary hash, `docker events`), never the executor status string; (iv) if the violation is not observed under W_k, the oracle for that attack is declared invalid, not the attack "contained"; (v) a status string alone can never yield PASS; a disagreement between the status string and the computed outcome is itself reported.
- **What the control does and does not show:** it shows the oracle is *able to observe* the violation when the control is removed (sensitivity of the measurement). It does not show the shipped configuration is secure beyond the tested attacks. Controls run only against local canaries.

**Negative/no-fault controls:** benign programs (compute-only, allowed I/O to `/workspace`) that must report "no breach, contained-action attempts absent", proving the oracle does not fire spuriously; empty and oversized submissions for Layer 1.

**Attack set:** the nine existing attacks re-written to be discriminating (`P0_P1_DECISION_PLAN.md` section 8.4), plus candidate additions to be reviewed by ChatGPT: compile-time include of a container-internal sensitive path and of `/dev/zero`; compile bomb (macro/recursion) to test the compile step's 10 s host timeout and orphan container; write to `/input` (read-only mount) and to a host-visible canary; fork bomb bounded by `--pids-limit`; memory bomb; CPU spin to timeout; stdout flood (`MAX_OUTPUT_BYTES`); `ptrace` literal (Layer 1) and an unfiltered ptrace/syscall variant (Layer 2). Repetitions: 5 per attack per configuration (deterministic attacks; report counts, no CI on repetition).

**Hashes/manifests/protocol/review:** attack sources and oracle code hashed in the protocol manifest; `run_manifest_v2` (input hashing, docker version/image digest, argv capture stored as raw output); tag `prereg/X1-C/v1` on the reviewed protocol; SUT tag (`sut/X1/build-A` or `-B`); locked environment for the harness; independent review = Codex audit of the harness and ChatGPT review of the protocol before tagging.

### 5.3 X1-B - Qwen authority isolation

| Field | Content |
|---|---|
| Question | Can LLM output alter evaluator score, orchestrator difficulty state or attempt ranking (`is_best`)? |
| Status | Not constructed. Frozen predecessor (`P1-C005`) withdrawn: no LLM output was ever inspected; `FeedbackValidator` does not exist and stays excluded. |
| Changes SUT? | No (harness-copy mutant only). |
| Exact blockers | Codex audit; ChatGPT review of the pairing design (below); **a real Qwen service and model files must be available and recorded (hash, decoding settings)** - an external/environment dependency not yet confirmed; adversarial prompt file authored and hashed *before* any run. |
| Can be prepared now | Static AST/pattern check design; prompt-set authoring (>= 30 adversarial prompts, each with a paired control); hash of the file; Qwen availability check (read-only inspection, no experiment); mutant harness copy. |

**Design correction (revision 2).** `X1_PROTOCOL_DRAFT.md` section 5 pairs each adversarial prompt with a "benign control" and asserts score/difficulty/`is_best` are identical. If the pair differs in the *candidate answer*, the evaluator score legitimately differs, so an invariance claim is confounded. X1-B is therefore split into **two experiment classes that are never merged into one headline result**:

| | **X1-B-I: invariance / containment test** | **X1-B-S: behavioural stress test** |
|---|---|---|
| Candidate answer | **Held FIXED** (same answer, same session state, byte-identical) | May vary (adversarial content may sit in the answer, e.g., prompt injection through the answer) |
| What varies | Only what the LLM receives or emits: model-facing prompt/context/input channels, and the LLM output (real Qwen with an adversarial payload vs a fixed benign/null response) | The adversarial prompt/answer content |
| Question | Does the relevant output (evaluator score bytes, orchestrator difficulty state, `is_best`/ranking) stay within the pre-specified invariance criterion (exact equality) when only the LLM-facing side changes? | Does the system stay within predefined safety/structural constraints (no unhandled exception, score within [0,1] and equal to what the evaluator returns with the LLM stage disabled for that answer, difficulty transitions only via the existing decision path, no write to score/difficulty/ranking from an LLM field, structured feedback status)? Score changes caused by a changed answer are legitimate and are **not** invariance failures |
| Pairing | Each fixed answer x (baseline LLM-facing context vs perturbed context) pair; >= 30 pairs | Each adversarial prompt paired with a benign control **for descriptive contrast only**; >= 30 pairs; the comparison criterion is the structural constraint, not equality across different answers |
| Pass criterion | Computed from logged observables; exact equality per pair | Computed from logged observables against the constraints; per-item counts |
| Headline | May support "no LLM path to score/difficulty/ranking in the tested build" (bounded) | May support "the system stayed within the structural constraints under the tested adversarial inputs"; never an invariance claim |

Retained in both classes: **real Qwen service** (localhost service; model files and decoding settings recorded and hashed), a **hashed adversarial prompt set** authored before any run, the **AST/static check**, the **LLM-wired mutant** in a harness copy (the differential/invariance test must fail on it), differential/structural validation, and a no-fault negative control. The strengthening property for B-I is that the mutant, which alters the score path from an LLM field, produces a detected violation while the shipped build does not.

**Prerequisite: LLM channel enumeration (construction work, read-only code inspection).** Before the prompt set is fixed, enumerate every channel that carries data *to* the LLM and *from* it. Pre-audit observations (leads, not findings): `agents/orchestrator/feedback_agent.py` posts a payload to a local Qwen service (`QWEN_URL = http://localhost:8001`, timeout 6 s) and consumes many fields of the response into the feedback structure; the orchestrator also recognises LLM-originated follow-up questions (`source == "qwen_followup"`), so LLM output can enter the question queue, which must be shown to have no path to score, difficulty or ranking (or reported if it does). Channels that alter the candidate answer belong to B-S; channels that leave it unchanged belong to B-I.

**Status:** X1-B is **not to be tagged or executed** until Sparsh + ChatGPT approve this corrected two-part design (decision before X1-B, section 13).

### 5.4 X1-A - Fault-injection core

| Field | Content |
|---|---|
| Question | Does the SUT handle each enumerated dependency failure without losing state, fabricating a score, or hanging? |
| Status | Not constructed. Only mocked-failure unit tests exist; FLT-02/06/08/09 have no test (`FINAL_PUBLICATION_READINESS_REVIEW.md`). |
| Changes SUT? | No. Injectors are stubs, socket/process manipulation and config redirection in the harness. |
| Exact blockers | Codex audit; ChatGPT review; the dependency-enumeration table (code reference per dependency x failure mode) must be complete and frozen *before* any behaviour is observed; SLA/timeout values must come from code/config, not from observed behaviour; exact field names confirmed against the SUT commit. |
| Can be prepared now | The enumeration table (pure code reading), injector designs, mutant definitions (one per scenario), timing-jitter/seed design. |

**Dependency-enumeration matrix (rows to be filled with code references; columns = failure mode {unavailable, slow past timeout, malformed/invalid output}):**
Qwen service; evaluator service (503/timeout/NaN-Inf/out-of-range); evaluator assets (SBERT, FAISS index, CrossEncoder missing/corrupt at load); Docker daemon; compiler hang/timeout; SQLite (lock contention shorter/longer than busy timeout; disk error); WebSocket (mid-evaluation reset); speech STT (WhisperX/faster-whisper missing or failing); prosody/feature extractor crash; RL policy/checkpoint load; filesystem (unwritable data dir); empty input. Candidate scenarios FLT-01..FLT-10 from the draft map onto these rows; rows not covered by any FLT are added *from the enumeration*, not from observed behaviour.

**Planned injections (verified against `X1_PROTOCOL_DRAFT.md` section 4):** FLT-01 Qwen down; FLT-02 Qwen slow (stub sleeping past timeout); FLT-03 evaluator 503 (infrastructure-failure flag true, no 0.0 stored as a candidate failure); FLT-04 NaN/Inf/out-of-range score (never stored raw); FLT-05 Docker daemon unreachable (structured error, no false "accepted"); FLT-06 compiler hang (terminated, no orphan process/container); FLT-07 DB write-lock contention (acknowledged writes == stored rows); FLT-08 WebSocket reset (attempt fully recorded or absent, never partial); FLT-09 feature-extractor crash (neutral fallback flagged as fallback, technical score unaffected); FLT-10 empty input. Each needs: no-fault control, one mutant (handler disabled/bypassed) that must FAIL the same criteria, oracle computed from logged observables (never a typed PASS), repetitions 5-10 (deterministic) or ~30 randomised injection points with Wilson 95% interval (timing-sensitive); unit of analysis = the scenario.

### 5.5 Minimum evidence before a Paper-1 manuscript can legitimately be drafted **[OPEN SCIENTIFIC DECISION, bundled with the X1-C design review]**
Executor's recommendation for the bar (reviewed together with the X1-C design; not a separate decision item):
1. Codex audit cleared (no blocking finding) and ChatGPT review of every protocol used.
2. **X1-C completed** (computed oracles; permissive control detected; Layers 1-4 reported separately) - required for any containment wording.
3. **X1-A completed for the enumerated classes** with mutants failing - required if "fault-tolerant"/"failure-aware behaviour verified" appears; otherwise the paper may only state that structured failure handling exists by design plus the mocked-failure tests.
4. **X1-B completed** if any LLM-isolation claim is made; otherwise the paper states isolation by construction (signature/AST check) and feedback unvalidated, with no measured claim.
5. X1-D as executed (test failure and latency scope disclosed); a new locked environment recorded for the X1-A/B/C runs.
6. Registry rows for all of the above, no "secure", no "9/9", no literal PASS.
A design-plus-X1-D-only paper is possible but would carry no measured resilience or containment claim; whether that is publishable is a Sparsh + ChatGPT judgement.

### 5.6 Root-cause triage of the known failing test **[DOCUMENTATION ONLY]** (replaces the former "fix or not?" decision)
Method: static reading of the test, the function it exercises, git history and the stored X1-D console output. Nothing was executed or modified; the test was not re-run in this pass.

| Question | Finding |
|---|---|
| 1. Which test fails? | `tests/unit/test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics` (line 391). Stored failure (`research/confirmatory/X1-D/results/pytest_console.txt`): line 432, `pytest.approx(float(obs[4]), abs=1e-3) == 0.22` with `obs[4]` = 0.0. The earlier assertions (confidence 0.94, hesitation 0.06, `communication_indicators`, `coding_history[-1]["execution_time_ms"] == 1850.0`, and `obs[2]`, `obs[3]`) passed. |
| 2. Subsystem | Runtime construction of the 6-D PPO observation, `agents/strategy/hybrid_orchestrator.py::build_rl_observation`, fed from `orch._state` after `_update_session_state` on a coding-type question record. Not the coding executor or sandbox, not the evaluator, not the training environment. |
| 3. Cause (static evidence) | The test (last changed 2026-08-18, `ea15e3c`) expects dimension 4 to carry the stored verbal `last_time_norm` (0.22). `build_rl_observation` was changed in the Paper-3 freeze commit `b7cad49` (2026-09-19): dimension 4 changed from `last_time_norm` to a turn-progress ratio t/T, where `session["progress"]` takes precedence and `last_time_norm` is only a fallback when no progress key exists. The orchestrator's state initialises `"progress": 0.0` (`interview_orchestrator.py:255`, updated at line 1505), so the test's `orch._state` contains a progress key = 0.0 and dimension 4 becomes 0.0. Other tests pass because their hand-built session dicts contain no progress key and reach the `last_time_norm` fallback (e.g., `test_runtime_and_training_state_formula_consistency`). The pre-existing audit `rl_state_alignment.md` records the runtime (progress) versus training (response time) dimension-4 divergence as a documented finding. |
| Classification | **Probable stale test expectation / fallout of a documented state-definition change** (not evidence that speech metrics are fabricated: the speech assertions passed and execution time did not leak). Not a demonstrated environment or test-harness defect. **Residual uncertainty:** the developer's intent behind the `b7cad49` change cannot be established from the repository alone (the commit message is generic); whether it was deliberate or an unintended regression is a question for Sparsh. Status until confirmed: **indeterminate as to intent, probable as to mechanism.** The test name overstates what fails; any registry/manuscript wording must describe the failing assertion (dimension-4 semantics), not "fabricates metrics". |
| 4. Touches the X1-C path? | No. X1-C exercises `validate_source_safety` and `DockerCSandbox.compile_and_execute`; the failing path imports neither and the test supplies pre-computed feedback (no sandbox call). |
| 5. Affects X1-C validity? | No, on this evidence. It could only matter for an X1-A scenario whose oracle reads the RL observation (none is planned; FLT-09's oracle is the technical score and a fallback flag), and for any Paper-1 sentence about speech metrics, which must not rely on this test and must disclose it. |
| 6. Would fixing need a new SUT build? | Changing `build_rl_observation` (SUT code): **yes**, a new tagged build B, a full rerun of affected X1 campaigns under the defect policy, and it would change what the deployed PPO observes: a product change, not proposed. Changing only the test file: outside the directories the X1 protocol freezes (`apps/backend`, `services`, `agents`, `rl`) but it changes the tagged tree that X1-D reported on, so a tag decision would still be needed. Neither is proposed. |

**Conclusion.** No action now. The failure remains disclosed (`X1D-C001`). A red regression test is not by itself a reason to create a new scientific build, and a 226/226 suite is not a goal. After Sparsh and ChatGPT review this triage, they decide whether any build B is warranted (default: keep build A, report as a disclosed known failure). A confirming probe (call `build_rl_observation` with and without a progress key; no repository write) can be run on instruction; it was deliberately not run here.

---

## 6. Paper 2 - human gate, provenance, confirmatory benchmark

### 6.1 What the existing evidence is and what remains open
| Topic | Established (registry) | Remains open |
|---|---|---|
| Old benchmark N=64 | 64 constructed answers to 8 questions, 10 categories, author-built (`P2-C005`); exploratory/initial | Provenance/ethics of raters; question-disjoint replication |
| Human-human reliability | ICC(2,1) 0.9528, ICC(2,k) 0.9838, Krippendorff alpha 0.9523 (`P2-C008`) | Very high reliability on constructed contrast items does not show reliability on natural answers; rater independence undocumented |
| Evaluator-human | Composite rho 0.3812; two-level CI [0.1529, 0.6490] (`X2A-C001`); question-only CI [0.3066, 0.5888] (`X2A-C002`); within-question rho 0.5796 (`X2A-C007`) | Replication on unseen questions (X2-C) |
| Composite vs R-only | R-only 0.4832; composite below R-only and S1+R (`P2-C007`); difference -0.102 [-0.285, 0.117] (`X2A-C003`, data neither establish nor exclude a difference) | Whether the safety-hardening has any measured benefit (H3) |
| Concise-correct under-scoring, bias | Composite bias vs human -0.134; concise correct answers scored ~0.40 vs human ~0.91 (`X2A-C007`, `FINAL_PUBLICATION_READINESS_REVIEW.md`) | Length-controlled test |
| Paraphrase under-scoring | Present in the 64-case error analysis (small n per category) | Correct-paraphrase and wrong-paraphrase strata |
| Length confound | **Length-only baseline rho 0.4897 [0.2186, 0.708], AUROC 0.886 vs derived CE 0.4825 / 0.782 (`X2B-C003`, EXPLORATORY)**; BM25 0.3812, token overlap 0.4301, TF-IDF 0.245 (`X2B-C004`) | The benchmark cannot show R adds evidence beyond surface features; needs length-matched strata |
| Ablations / metamorphic / adversarial | Metamorphic 19/21, adversarial 11/13 against author-set ceilings (`P2-C013`); composite AUROC 0.7206 vs R-only 0.7821, 2 of 34 adversarial accepted at tau 0.60 (`X2A-C008/C009`, EXPLORATORY) | Ceilings are author-set; no independent adversarial criterion |
| CrossEncoder provenance | Partially fine-tuned derivative (`P2-C003`); derived vs upstream rho 0.4825 vs 0.1454, delta 0.337 [0.042, 0.606] (`X2B-C001/C002`, EXPLORATORY) | Trainer/dataset records not recovered; train/test overlap cannot be excluded |
| Question overlap | Pilot-overlap questions rho 0.709 vs 0.425 (`X2A-C006`, EXPLORATORY, historical `P2-C012`) | Disclose as tuned-on; disjoint set needed |
| Question-cluster effects | 8 clusters; leave-one-question-out 0.3517-0.4341 (`X2A-C004`) | Number of questions from a precision simulation |
| Score-threshold ambiguity | No explicit accept threshold exists (N5); tau 0.60/0.75 are documented grade boundaries read as bands, not decision rules | D-X2-TAU |

### 6.2 What the confirmatory benchmark (X2-C) must control for (no evaluator redesign)
| Control | Requirement | Reason |
|---|---|---|
| Question-disjointness | No question from the old 64-case set, the N=20 pilot, or any set used to set theta/dampening/weights; stored disjointness check | Removes circularity (`X2A-C006`) |
| Temporal separation | ~half of questions **and references** authored after the CrossEncoder commit date (2026-04-13), unpublished, not derived from the legacy bank; authoring dates recorded; ~half bank-sampled but disjoint, leakage status labelled | Separates leakage from generalisation (X2-B interpretation table) |
| Independent authorship | Answers and references by people who have never seen evaluator output; references authored before answers; coded author IDs | Removes evaluator-aware construction |
| Evaluator-unaware construction | Evaluator not run on any candidate item before the item file is frozen | No filtering on scores |
| No score-based selection | No item added, removed or reworded after any rater or evaluator output exists; ordering: freeze evaluator hashes -> author -> freeze item file -> blind rating -> freeze gold -> run evaluator once -> registered analysis | Contamination control |
| Raters | >= 3, fully crossed, blind to category/stratum/authorship/evaluator; randomised order (seeds logged); frozen rubric; adjudication rule (spread > 0.20) by a person distinct from authors | Reliability and independence |
| Natural/volunteer-style answers | Include a natural stratum only where institutionally permitted (collecting answers from volunteers is human-subject data collection: needs the determination and consent first) | Removes reliance on category construction; **cannot start before the gate** |
| Controlled contrast strata | Constructed, category-labelled subset reported separately | Adversarial validity |
| Length control | Length-matched pairs; 2x2 (correct/incorrect x concise/verbose) per question; report length-partial association | Answers the length-only result (`X2B-C003`) |
| Paraphrase strata | Correct paraphrase (lexically distant from the reference); technically wrong paraphrase (lexically close to the reference) | Separates semantic from lexical evidence |
| Provenance records | Ledger per `HUMAN_BENCHMARK_PROVENANCE_PLAN.md` collected at the time (roles, instructions version, timestamps, tool-use and independence declarations, file hashes) | Repairs P0-7 |
| Rating independence | No communication between raters; independence declaration; adjudicator role recorded | Reviewer attack |
| Consent / institutional | Determination or documented decision to proceed; consent/ledger materials approved; compensation documentation | `P2-C011` (withdrawn) must not recur |
| FAISS/S2 condition | State whether the index contains the new questions (should not for the temporally disjoint stratum) | Frozen evaluator behaviour must be documented, not altered |
| Sample size | Precision simulation from 64-case variance components before collection; target cluster-CI half-width <= 0.12 (working range 20-30 questions x 8 answers; an estimate, not a decision) | Underpowered otherwise (8 clusters) |
| One round only | No second round; incomplete round reported as incomplete unless a documented amendment is approved | Locked decision |

### 6.3 D-X2-TAU: how the confirmatory analysis should be anchored **[OPEN SCIENTIFIC DECISION]**
Paper 2 stays **HOLD / gate-dependent**; D-X2-TAU stays **OPEN**; X2-C is **not authorised**. The evaluator has no accept threshold, and the exploratory X2-A false-accept numbers (2/34 at 0.60) and the observed rho 0.3812 must not be used to choose any threshold or rho_min. Current methodological preference to analyse (not a decision): **primary = threshold-free continuous analysis**; secondary options only if independently specified: an independently justified operational threshold, AUROC where a genuine binary criterion exists, and a baseline-relative comparison against the length-only baseline. Options, in order of defensibility:

1. **Threshold-free continuous primary endpoints - recommended default.** Pooled and within-question Spearman with two-level cluster CIs; paired differences against the length-only baseline and R-only; length-partial association. No threshold to choose. Caveat: the *pass criterion* still needs an anchor (rho_min).
2. **rho_min anchoring.** The draft's suggested 0.30 (and any similar value) lies just below the observed 0.3812 and would be result-informed; it **must not be used** unless justified independently of that number (e.g., a downstream-use requirement stated before X2-C). A **baseline-relative criterion** (composite or R-only minus length-only, lower CI bound > 0, or > a pre-set margin) is defensible without an absolute number and directly answers the strongest reviewer attack. Sparsh + ChatGPT choose; the executor must not.
3. **AUROC where a true binary criterion exists.** Threshold-free; valid if "correct vs incorrect" is defined in advance from human consensus against the rubric anchors, or from construction labels in the constructed-contrast stratum only (not the natural stratum). Report within-length-bin AUROC as a control.
4. **Pairwise ranking accuracy on length-matched, a-priori ordered pairs.** Binary per pair, threshold-free, directly tests the concise-correct vs verbose-incorrect failure. Strong for the controlled strata.
5. **Operational threshold (only if independently justified).** Acceptable only if it comes from documented deployment semantics that exist independently of the data (none is currently verified) or is replaced by a **matched accept-rate comparison** (composite vs R-only at equal accepted fraction), which avoids choosing a threshold for the H3 contrast. A fixed tau (0.60 or 0.75) chosen after seeing X2-A false-accept rates is **not defensible**.

Decision needed: primary endpoint(s), whether H1 uses absolute rho_min or a baseline-relative margin and its value with a stated justification, the binary criterion for AUROC, and the H3 rule (matched accept-rate vs documented boundary). The executor can prepare the precision simulation and analysis skeleton hashes once these are fixed.

### 6.4 External dependencies before X2-C can be constructed or executed
| Dependency | Status |
|---|---|
| Institutional/ethics determination (or documented decision to proceed) for authoring, rating, and any volunteer answers | Enquiry drafted (`INSTITUTIONAL_ETHICS_ENQUIRY_DRAFT.md`), **not sent**; no institution has been identified in the repository |
| Consent, information sheet, ledger materials, compensation records | Not created (depends on determination) |
| Rater provenance/qualifications and independence declarations for the *existing* three raters (repairing the 64-case record) and recruitment of >= 3 raters for X2-C | Missing (`P0-7`); recruitment is the user's |
| Independent item authors | Needed; user's |
| Trainer/model provenance for the CrossEncoder fine-tune | Request drafted (`MODEL_PROVENANCE_REQUEST.md`), not sent; no reply |
| Venue-specific human-study requirements (ethics statements, data availability, participant-data rules) | Depend on the chosen venue; for the ten conferences none was verified on official pages in this pass (section 9) |
| Data-protection and dataset-release terms (retention, licence, whether answers may be published) | Not assessed; depends on determination |
| D-X2-TAU and the sample-size rule | Section 6.3, section 13 |

No item authoring, rater contact or benchmark construction may start before the gate is satisfied; no retrospective ethics or consent status is to be assumed for the existing raters.

---

## 7. Paper 3 - packaging (do not redesign)

**Scope rule:** frozen scientific package. No PPO tuning, no reward or environment change, no X3-B, no retraining.

### 7.1 Results valid for publication (registry, VALID)
- Frozen study design and seeds (`P3-C001`); Fixed baseline MAE 1.200, Heuristic 0.473 / volatility 0.160 (`P3-C002`); PPO+G five-seed MAE 0.677 (`P3-C003`); volatility 0.186, with 0.088 = seed 123 only (`P3-C004`); 563 activations over 1250 guarded turns (`P3-C005`); 232 attempted boundary actions guarded, 136 raw (`P3-C006/C007`); 99 action overrides, 464 of 563 activations unchanged (`P3-C008`); Constant-Same+G MAE 0.673, PPO contribution not identified in the frozen five-persona set (`P3-C009`, `P3-C022`); stored-spread definition (`P3-C020`); checkpoint hash (`P3-C016`); seed-123 guardrail files (`P3-C021`).
- Training/evaluation limitations as verified facts: single unseeded training candidate (`P3-C017/C018`), shield active in training (`P3-C019`), MAE blindness to oscillation about half-integer targets (`P3-C023`), Constant-Same+G volatility 0.080 vs PPO+G 0.186 (`P3-C024`).
- **X3-A confirmatory:** primary Delta PPO+G minus Constant-Same+G = -0.0350, 95% CI [-0.0818, 0.0021], class **Equivalent** (`X3A-C001`); volatility +0.149 [0.067, 0.254] (`X3A-C002`); shield did not improve Constant-Same tracking on the 40-persona grid (`X3A-C003`); PPO uses its state (`X3A-C004`); PPO+G beats heuristic+G and controller+G on the grid (`X3A-C005`, subject to the target-authoring caveat); G1 ablation (`X3A-C006`); frozen-stratum consistency (`X3A-C007`).

### 7.2 Limitations to state (not to hide)
Simulation only, single team-authored simulator; the target is an authored function of skill (reward/oracle coupling: `oracle_agreement` and MAE are defined on the same authored structure that the controller can exploit); 40 factorial personas are not a population sample; 5 training seeds; frozen checkpoints trained on one candidate with shield in the loop and 15 vs 10 turn mismatch; delta = 0.12 is an author-chosen pre-registered margin; unlocked original environment (replay locks recorded); training not reproducible (unseeded candidate); **training/runtime state divergence in dimension 4** (the training environment feeds normalised response time, the deployed runtime builds turn progress t/T; documented in the pre-existing `research/audit/rl_state_alignment.md`, whose EXP-RL-2 action-agreement figures were not re-verified in this pass and whose registry status was not checked). X3-A evaluates the frozen policies through the training-environment semantics, so it does not measure deployed-runtime behaviour.

### 7.3 Claims explicitly NOT supportable
PPO improves tracking (`P3-C011` withdrawn); guardrails eliminate boundary violations (`P3-C010`); PPO has lower volatility (`P3-C013`); "563 interventions" as overrides (`P3-C012`); session as statistical unit (`P3-C014`); any learner, engagement or learning-outcome claim; a method-level statement that PPO is redundant or superior beyond "these checkpoints in this simulator"; that the shield generally improves tracking (`X3A-C003`); generalisation beyond the persona generator and simulator.

### 7.4 X3-B status
Remains **parked**: trigger not fired (X3-A Equivalent), and D-N2 (seeding, persona distribution, shield-in-loop) is unresolved. Only if Sparsh wants a method-level PPO claim does X3-B return, with D-N2 and D-X3B-OP resolved first.

### 7.5 Remaining work is packaging/documentation only
Codex audit of `x3a_*` and `run_manifest.py` (gate); ChatGPT review of `prereg/X3-A/v1`; delta-sensitivity as a *descriptive* table from stored data if wanted (labelled exploratory); counting glossary; figure specifications; evidence package (section 8).

### 7.6 Paper-3 evidence-package checklist (hand-off to the manuscript stage)
- [ ] Claim map with registry IDs and allowed/forbidden wording (7.1-7.3).
- [ ] Protocol references: `prereg/X3-A/v1` -> `b00541f`, `freeze/X3-A/v1` -> `dde2ddf`, `v1.0-paper3-complete`; protocol and manifest SHA-256.
- [ ] Persona generator G1 definition, skill/type grid, target rule `round(10*skill)/2`, the frozen 5-persona stratum, seeds (train 42/123/456/789/999; eval 1001...20020; bootstrap 42, B=10000).
- [ ] Policy definitions (Constant-Same, Random, Heuristic, Oracle-rule, Controller, raw PPO, PPO+G) and shield rule list with the counting definitions.
- [ ] Result index: `sessions.csv` (63,000 sessions), decision JSON, secondary tables, strata table, condition summary, manifests, `RESULT_HASHES_phase3.txt`.
- [ ] Tables/figures specified from stored results only, each with source hash (none generated yet).
- [ ] Statistical definitions: two-way cluster bootstrap, equivalence/superiority/adverse classification, why 95% CI, secondary contrasts descriptive.
- [ ] Ablations: state-zero/shuffle, G-minus-rule; oracle-coupling and MAE-blind-to-oscillation notes.
- [ ] Seed-level results (per-seed table), volatility per seed, the 0.088 vs 0.186 correction.
- [ ] Limitations and threats (7.2), reviewer-attack list (section 12), wording constraints.
- [ ] Environment: `LOCK-X3-2026-09-19` (lock hash `c8fdfda1...`), replay lock, disclosed pin conflicts, hardware.
- [ ] Audit status: Codex outcome and ChatGPT outcome recorded (pending).

### 7.7 X3-A claim localisation (before any thought of a rerun) **[DOCUMENTATION ONLY]**
Default: **NO X3-A RERUN.** A rerun is not recommended merely because an ablation lacks an independent reference. Map: claim -> analysis -> artifact -> reference/baseline -> is an independent reference required?

| Claim | Analysis (script) | Artifact | Reference / baseline that exists | Independent reference required? | Classification and consequence |
|---|---|---|---|---|---|
| `X3A-C001` primary equivalence | Persona-level MAE difference, two-way cluster bootstrap (`x3a_analyze.py`) | `x3a_decision.json`, `sessions.csv`, manifests | Session loop equals the frozen `run_session_trajectory` on the 5 frozen personas x seeds for Constant-Same+G and PPO+G (G-HARNESS, 9/9); shield equals the frozen shield on 200 000 random/edge states (full rule set); the point difference was recomputed independently (`PHASE4_T2_VERIFICATION.md`) | Already present for the loop, shield and point estimate. **The CI has no independent recomputation** (O7, O8): to be checked in the Codex audit and by an offline sensitivity check | Central, confirmatory, frozen. Supported. Consequence only if the CI sensitivity changed the class (upper bound 0.0021 vs margin 0.12: unlikely) |
| `X3A-C002` volatility | same loop; descriptive (protocol section 5) | same | volatility is one of the fields compared in G-HARNESS | No | Descriptive, supported |
| `X3A-C003` shield vs no shield (Constant-Same) | Full rule set on/off | same | Frozen-equal shield (random-state test) | No | Descriptive, supported; CI includes zero |
| `X3A-C004` state-zero / state-shuffle | `PPOPolicy` modes (`x3a_lib.py`) | same | None (modes do not exist in frozen code) | Only if used to argue *why* PPO behaves as it does; the wording is limited to "PPO's output depends on its observation; not evidence of better tracking" | Descriptive control; not a central claim |
| `X3A-C005` vs heuristic / controller / oracle-rule | policy definitions in config and lib | same | Heuristic (raw) frozen-equal; controller and oracle-rule have no frozen counterpart; controller is a protocol-defined upper reference that exploits the persona-target rule | Optional: independent re-implementation from the protocol text (Codex) | Descriptive; not central; must carry the oracle/reward coupling caveat |
| `X3A-C006` rule ablation | Shield copy with `disabled` set | same | **None** for the ablation branches: G-HARNESS shows the gating mutants are *detected*, not that each ablation branch is correct | Only if a central claim attributes behaviour to a specific rule. None of the registered central claims does; the registered point changes for G2, G4, G5, G6 are below 0.03 MAE and the G1 intervals include zero | **Descriptive/exploratory.** Must not be used for causal or comparative rule-attribution in a manuscript; a registry note "descriptive; ablation branches not independently referenced" is recommended [DOCUMENTATION ONLY]. If ever needed, an independent reference can be built offline from the frozen `apply_canonical_guardrails` (no rerun of X3-A) |
| `X3A-C007` frozen five-persona stratum | same loop on frozen personas | same | Reproduces the X3-0 accounting; frozen replay G-REPRO 32/32 | No | Supported |

Additional cheap independent check that needs **no rerun**: recompute difficulty trajectories, MAE, volatility, oscillation and attempted-boundary counts from the stored `final_actions` strings and stored `target` in `sessions.csv` (start 3.0, +/-1 steps, clip to [1,5]) and compare with the stored columns for all 63 000 sessions; this validates metric computation for the grid personas independently of the simulator. It is a suggested Codex/executor offline check, not an experiment.
**Conclusion:** no central publication claim depends on the un-referenced ablation branches; therefore no new experiment is scientifically necessary on the present claim set. Grid-persona coverage of G-HARNESS (five frozen personas only) is a documented limitation of the gate, not a reason to rerun.

---

## 8. Evidence-package directory structures (design only; not created)

Root: `research/evidence_packages/` (new). Packages contain **pointers, indices and derived tables with hashes**, never copies or edits of frozen files. A new builder `research/evidence_packages/build_evidence_package.py` (research support) verifies every listed hash and fails if any frozen file changed.

Common layout (each `PAPER_N_EVIDENCE_PACKAGE/`):
```
00_SCOPE_AND_STATUS.md            what the paper may/may not claim; gate status (audit, review, human gate)
01_CONTRIBUTION_AND_RQS.md        contribution statement (as registered evidence allows), research questions
02_CLAIM_MAP.csv                  claim_id | paper section slot | status | allowed wording | forbidden wording | evidence label
03_PROTOCOLS.md                   tag, commit, protocol SHA-256, manifest SHA-256, deviations/amendments
04_EXPERIMENT_MATRIX.csv          experiment | confirmatory/exploratory | design | unit | seeds | environment lock | status
05_RESULTS_INDEX.csv              raw and derived result paths, SHA-256, producing script, manifest
06_TABLES/                        table specs + generation script (from stored results only) + source hashes
07_FIGURES/                       figure specs + generation script (no figure until requested)
08_STATISTICS.md                  estimands, CI methods, classification rules, multiplicity statement
09_CONTROLS_AND_ABLATIONS.md      positive/mutation controls, negative controls, ablations
10_ERROR_ANALYSIS.md              from stored results
11_LIMITATIONS_AND_THREATS.md     construct/internal/external/statistical validity
12_PROVENANCE_REPRODUCIBILITY.md  commits, tags, locks, hashes, hardware, what cannot be reproduced and why
13_REVIEWER_ATTACK_POINTS.md      attack -> registry evidence -> permitted response
14_WORDING_CONSTRAINTS.md         forbidden terms (secure, independent experts, off-the-shelf, approved...), required qualifiers
15_VENUE_REQUIREMENTS.md          verified requirements per candidate venue with verification status
16_OPEN_GATES.md                  audit / review / external dependencies remaining
MANIFEST.sha256, CHANGELOG.md
```
Paper-specific additions:
- **PAPER_1**: `17_DEPENDENCY_ENUMERATION.csv`, `18_ATTACK_ORACLE_SPECS/` (layers 1-4), `19_MUTANT_AND_CONTROL_LOG/`, `20_DEFECT_LOG_BUILD_A_B.md`, `21_TEST_REPORT_AND_LATENCY.md` (X1-D), `22_THREAT_MODEL_DESIGN_MAPPING.md` (labelled design).
- **PAPER_2**: `17_BENCHMARK_CARD_OLD_AND_X2C.md`, `18_HUMAN_STUDY_PROVENANCE_AND_ETHICS/` (only records that exist; states absences), `19_LENGTH_AND_LEXICAL_BASELINES.md`, `20_CROSSENCODER_PROVENANCE.md`, `21_ENDPOINT_DECISION_D-X2-TAU.md`, `22_PRECISION_SIMULATION.md` (after decision).
- **PAPER_3**: `17_PERSONA_GENERATOR_AND_TARGET.md`, `18_GUARDRAIL_ACCOUNTING_GLOSSARY.md`, `19_CHECKPOINT_AND_ENVIRONMENT_HASHES.md`, `20_TRAINING_EVAL_MISMATCH_FINDINGS.md` (N1, N2, N9, N10), `21_X3B_PARKED_RECORD.md`.

The packages must let a future drafting session write the manuscript **without reopening any frozen experiment**: every number must resolve through `05_RESULTS_INDEX.csv` to a hashed artifact and a registry row.

---

## 9. Conference verification table (as read on 2026-09-20)

Verification key: **OFFICIAL** = read from the conference's own page in this pass; **OFFICIAL-PARTIAL** = official page read but the item is not stated there; **SECONDARY** = third-party or search summary, not accepted as authoritative; **NOT-FETCHED** = official page could not be read (TLS certificate verification failure in this environment or fetch failure), so nothing below is confirmed for that page.

| Conference | Identity as found | Dates / place | Submission deadline(s) | Length / format | Proceedings | Special tracks / scope evidence | Verification, conflicts, flags |
|---|---|---|---|---|---|---|---|
| **ICETC 2026** | 18th Intl. Conf. on Education Technology and Computers | Porto, Portugal, 14-17 Dec 2026 | **10 Oct 2026** (notification 10 Nov; registration 20 Nov). Homepage notices: 11 Jul 2026 extended to 30 Aug; **31 Aug 2026 extended to 10 Oct**. EasyChair CFP also states 10 Oct | EasyChair CFP: no less than 5 two-column pages; extra pages USD 70/page; English; Word/LaTeX templates. The official CFP page states no page limit | Homepage: IEEE proceedings (Xplore, Ei, Scopus); selected papers Springer LNET. IEEE conference-record status not checked | Official CFP page (`icetc.org/cfp.html`) lists ten tracks. Relevant: **Track 2 Artificial Intelligence in Education** (Intelligent Tutors and Personalized Learning Systems; Adaptive Learning Platforms; Educational Data Analytics and Prediction; Generative AI for Education; AI-Powered Adaptive Learning; **AI in Assessment & Feedback**; Ethical AI in Learning); **Track 4** (Real-Time Adaptive Learning Analytics; Learning Engineering & AI-Based Instructional Design; Data Privacy & Ethical Considerations); **Track 7 Cybersecurity, Privacy, and Digital Ethics in Education** (Security of Online Learning Platforms; Preventing Cyber Threats in Educational environments; Student Data Protection; Privacy Protection; Ethical Considerations in AI Surveillance); **Track 10 Assessment and Evaluation in Education** (Design of Valid and Reliable Assessments; Feedback Strategies). Multimodal AI is **not** listed as a topic | OFFICIAL. **The 30 Aug date was superseded by the official 31 Aug notice (10 Oct); this is a historical notice, not an unresolved conflict.** Review type stated on the official CFP page: **double-blind**. Track 7 topics concern security of learning platforms and student data, not containment of untrusted code execution; Paper 1's containment evidence would sit under Track 2 and Track 7 only by analogy and must be framed accordingly. Deadline has been extended twice; a further extension is possible but **not** planned on. |
| **ATIS 2026** | 16th Intl. Conf. on Applications and Techniques in Information Security | Bengaluru, 14-15 Dec 2026 | Submission **7 Nov 2026** (opens 13 Aug; notification 30 Nov; registration 5 Dec) | Springer CCIS format, up to 12 pages; CMT3 | Springer CCIS, Scopus-indexed | Four tracks; Track 3 "Artificial Intelligence, Data Security and Cybersecurity" | OFFICIAL. No conflict found. A separate domain (`atis.conferences.academy`) appeared in search results and was not checked. Double-blind with 3 reviewers + meta-reviewer stated. |
| **ICTCS 2026** | Only official match found: 27th **Italian** Conf. on Theoretical Computer Science, Udine | 7-9 Sep 2026 | **Passed** (papers 28 Jun 2026, extended) | Regular <= 12 pages; communications <= 5; CEUR-WS format | CEUR-WS.org; special issue planned | Theoretical CS; not an AI/education conference | OFFICIAL. **Identity likely not the intended venue; flagged for the user to supply the intended name/URL.** |
| **SmartCom 2027** | 11th Intl. Conf. on **Smart Trends in Computing and Communications**, Goa (hybrid) | 27-30 Jan 2027 | Early bird 11 Sep 2026 (passed); **regular 12 Oct 2026** (notification 13 Nov; camera-ready 27 Nov) | Not stated on pages read | Springer LNNS (Scopus, EI, others) | 8 tracks incl. Intelligent Systems, Engineering Applications, Technology Trends | OFFICIAL, with **stale/inconsistent text** (2019 EasyChair links, "SmartCom26" logo, 2026 header). **Name collision:** a separate "Intl. Conf. on Smart Computing and Communication" (SmartCom 2026, 10th) exists at another site; the smartcomconference.com series was assumed. |
| **ICMETE 2026** | **No conference with this acronym found** | - | - | - | - | - | **UNVERIFIED / unidentified.** Near matches in search (e.g., ICMET 2026 Modern Educational Technology, Kumamoto, 17-20 Dec 2026; others) were not read and are **not assumed** to be intended. User to supply the name/URL. |
| **HCI International 2027** | HCII 2027 with AIS (9th Intl. Conf. on Adaptive Instructional Systems) and AI-HCI (8th) among 21 affiliated conferences | Berlin, 25-30 Jul 2027 | Regular papers: **proposal (800 words) 9 Oct 2026**; review notification 20 Nov 2026; **final submission 29 Jan 2027**; registration 12 Feb 2027 | Page limits not found on pages read | Springer (main page); not stated on deadlines page | AIS scope (official page): UI/UX for ITS; learner modeling and assessment (state detection, multimodal AI, biometric sensors); learning engineering; LLM tutors and ethical AI; STEM/professional/workforce domains; evaluation and governance | OFFICIAL. AIS-specific dates were not on the AIS page (it links to the general deadlines page). One registration per submission required. |
| **ACM SAC 2027 - AIED track** | 42nd? ACM/SIGAPP Symposium on Applied Computing (edition not read); track "Artificial Intelligence for Education" (AIED) is track 2 of 39 | Gwangju, South Korea, 5-9 Apr 2027 | Paper submission **2 Oct 2026 (EST)**; notification 13 Nov 2026; camera-ready 28 Nov 2026 | **Not verified** (track site `sites.google.com/view/aied-27` and tracks page details not readable) | ACM (open-access transition noted on page) | AIED track exists (official tracks list); track topics/chairs/deadline not read | OFFICIAL-PARTIAL. **Track-specific deadline, page limit and review model NOT-FETCHED (TLS error).** Assumption that the track follows the main 2 Oct deadline is **unverified**. |
| **ICMLSC 2027** | 11th Intl. Conf. on Machine Learning and Soft Computing, Tokyo | 29-31 Jan 2027 | Submission **30 Sep 2026**; notification 10 Nov; registration 30 Nov; camera-ready 10 Jan 2027 | Word/LaTeX templates; page limit not stated | Springer CCIS (Scopus, EI, SCImago); 3 reviewers | Topic list not on the homepage read; search summary lists ML, neural, evolutionary, intelligent search (SECONDARY) | OFFICIAL. Stale "ICMLSC 2026" banner filename (cosmetic). Submission through zmeeting.org. |
| **IEEE MLNLP 2026** | 9th Intl. Conf. on Machine Learning and Natural Language Processing, Xiamen (Jimei University), IEEE/IEEE CIS sponsorship stated by secondary sources | 26-28 Dec 2026 | **20 Nov 2026 (extended)** and notification 30 Nov - **SECONDARY only** | Not verified | Claimed IEEE Xplore/Ei/Scopus/CPCI-S - **SECONDARY** | ML + NLP incl. LLMs (SECONDARY) | **NOT-FETCHED** (official site certificate error). **Name collisions:** an AIRCC "7th Intl. Conf. on Machine Learning Techniques and NLP (MLNLP 2026)" (5 Sep 2026) and a Sydney "MLNLP 2026" (12 Sep extended) exist and must not be confused. Verify on the IEEE conference listing. |
| **IEEE AIEI 2027** | 2027 IEEE Intl. Conf. on **AI Engineering and Innovations** (not "AI in education"), Bangalore | 21-23 Jan 2027 | **30 Sep 2026** per the IEEE Systems Council event listing | Not verified | IEEE Xplore "subject to eligibility"; IEEE TEMS financial sponsor, Systems Council technical co-sponsor | Theme "AI for Technology Management, Intelligent Systems and Innovation"; sectors incl. education, cybersecurity, healthcare (Systems Council page) | Deadline from an IEEE listing page, **conference site aiengineering-conference.org NOT-FETCHED**; a second domain `aiei2027.org` surfaced in search and was also not readable - possible duplicate/imitation, verify via the IEEE conference record before any submission. Education is one listed sector, not the focus. |

---

## 10. Fit matrix and portfolio

### 10.1 Fit matrix (qualitative)
"Missing evidence" refers to what the paper lacks *for that venue's likely expectations*, not to defects of the venue.

| Conference | Paper 1 fit | Paper 2 fit | Paper 3 fit | Scope evidence | Missing evidence | Deadline | Special track | Submission constraints | Main reviewer risk | Open dependency |
|---|---|---|---|---|---|---|---|---|---|---|
| ICETC 2026 | **Coherent, and not merely an education fit:** an adaptive AI technical-assessment system with AI feedback, failure handling and containment maps onto Track 2 (adaptive learning, AI in assessment and feedback, ethical AI), Track 7 (security of platforms, privacy) and Track 10; framing = a dependable/trustworthy engineering evaluation of an adaptive AI assessment system, not a cybersecurity paper | Strong topical fit (Track 10; Track 2 AI in assessment) | Good (Track 2 adaptive learning; Track 4 adaptive analytics; simulation-only) | Official CFP page: Tracks 2, 4, 7, 10 (section 9) | No learner or pedagogical outcome evidence in any paper; Paper 1 measured resilience/containment evidence not yet produced | 10 Oct 2026 (extended twice; final official notice 31 Aug) | Tracks 2, 7, 10 | >= 5 two-column pages (EasyChair CFP); double-blind; IEEE proceedings per homepage | "Where is the educational evidence?" and, for Paper 1, "containment is not a learning outcome" | Deadline achievability (below); audit/review gates |
| ATIS 2026 | Conditional: fits Track 3 only for the containment/isolation evidence (X1-C, X1-B); the failure-aware system framing is peripheral | Weak (adversarial/metamorphic robustness is the only security-adjacent content) | Poor | Four security tracks; Track 3 AI/data security | Paper 1 has no measured containment evidence yet | 7 Nov 2026 | Track 3 | Springer CCIS, <= 12 pages, double-blind, CMT3 | Containment shown only against a Docker default-isolation setup sharing the host kernel; nine-attack scope | X1-C/B done, audit, review |
| ICTCS 2026 (as found) | None | None | None | Theoretical CS | - | Passed | - | CEUR, <= 12 pp | - | Identity unresolved |
| SmartCom 2027 | Partial (generic systems/"Engineering Applications") | Partial | Partial ("Intelligent Systems") | Track names only | Venue-specific expectations unknown; no track for education | 12 Oct 2026 | none specific | Springer LNNS; page limit not verified | Generalist scope; unclear reviewer profile | Gates |
| ICMETE 2026 | Unassessable | Unassessable | Unassessable | Not found | - | - | - | - | - | Identity unresolved |
| HCI International 2027 | Moderate/weak (AIS "evaluation and governance", UI/UX) | Moderate (AIS learner modeling and assessment; AI-HCI) | **Strong** (AIS: adaptive instructional systems, AI-driven adaptation) | AIS page read | Human-centred/user evidence absent (simulation only); Paper 2 human validity exploratory | Proposal 9 Oct 2026; final 29 Jan 2027 | AIS; AI-HCI | 800-word proposal then full paper; registration per submission | HCI audience expects users/learners | Audit/review; go-ahead for proposal prose |
| ACM SAC 2027 AIED | Moderate | Good (assessment of answers) | Good (adaptive difficulty) | Track exists (track 2) | Track topics/length not read | 2 Oct 2026 (track date unverified) | AIED | ACM format; length unverified | Short cycle; needs a complete, audited paper | Track page verification |
| ICMLSC 2027 | Poor | Moderate (evaluation model behaviour) | Moderate (RL/ML) | Topics via secondary | Unknown expectations | 30 Sep 2026 | none | Springer CCIS | Broad ML/soft-computing venue | Gates |
| IEEE MLNLP 2026 | Poor | **Good** (embedding/cross-encoder scoring, human agreement) | Poor to moderate (RL, not NLP) | Secondary only | Paper 2 confirmatory replication | 20 Nov 2026 (unverified) | none | IEEE format unverified | Paper 2 confirmatory absent | Official verification |
| IEEE AIEI 2027 | Moderate (AI system engineering; cybersecurity/education as sectors) | Moderate | Moderate | IEEE Systems Council listing | Venue expectations unknown | 30 Sep 2026 (listing) | none | IEEE Xplore eligibility | Generalist engineering venue | Official verification |

### 10.2 Portfolio (contribution first, venue second; no paper is reshaped to fit)

| Paper | Primary | Secondary | Backup | Fit rationale | Evidence to finish first | Deadline | Realistic on current evidence? | Venue framing | What would make it a bad fit |
|---|---|---|---|---|---|---|---|---|---|
| **Paper 3** (provisional) | **HCI International 2027, AIS** | ACM SAC 2027 AIED; IEEE AIEI 2027 (both only if the evidence, audit and review gates are already met by their dates; not chased) | none forced. ICMLSC 2027 (30 Sep) is **not** pursued: an ML deadline is not a reason to compress gates | AIS is the adaptive-instruction remit: adaptive difficulty control, candidate state, adaptive decisions, assessment and controlled evaluation of adaptive-policy behaviour; the science is not changed to look "HCI-like" | Codex clearance of `x3a_*`/`run_manifest`; ChatGPT review of `prereg/X3-A/v1`; Paper-3 evidence package; Sparsh's go-ahead for proposal text | HCII: proposal 9 Oct 2026 -> notification 20 Nov -> final 29 Jan 2027 (SAC: 2 Oct, track date unverified; AIEI: 30 Sep per listing, official site unread) | Yes for the *scoped* claim (equivalence, volatility, accounting; simulation-only). HCII's two-stage model leaves time for the gates between proposal and full paper. The proposal date is 19 days away and depends on the audit/review outcome | Adaptive-instructional-systems component decomposition; explicit no-learner claim; PPO as a studied component | An audience demanding user studies or learning outcomes; any wording implying PPO helps learners |
| **Paper 1** (provisional) | **ICETC 2026** (Tracks 2, 7, 10; 10 Oct) | **ATIS 2026 fallback** (Track 3; 7 Nov) | none further within the ten; if neither date is legitimately achievable the paper waits (next-cycle dates unverified) | Coherent with ICETC's official scope (adaptive learning, AI in assessment and feedback, ethical AI, security of learning platforms, privacy, assessment); framed as a **dependable/trustworthy engineering evaluation of an adaptive AI technical-assessment system**, not a cybersecurity narrative. ATIS is a valid fallback because the X1 work contains substantial containment, security, fault/dependability and deployment evidence | Codex + ChatGPT; X1-C (and X1-B; X1-A if "fault" wording is kept) executed and frozen; evidence package; the minimum-evidence bar (5.5) | ICETC 10 Oct 2026 (20 days); ATIS 7 Nov 2026 (48 days) | **Undetermined; the test is "can legitimate evidence be completed by the deadline?"**, not "how do we fit the evidence to the deadline". See 10.3 | Adaptive AI technical-assessment system; failure-aware/sandboxed (no "secure"); fault claims only if X1-A done; containment claims only if X1-C done | For ICETC: no educational or learner evidence expected by reviewers. For ATIS: a design-only or partly withdrawn-claim paper; overstating Docker default isolation; a purely cybersecurity reading |
| **Paper 2** | **HOLD / gate-dependent (X2-C)** | none | none | The evaluator paper's honest contribution is an evaluation-methodology and provenance study with a confirmatory replication; assessment-oriented venues fit (e.g., ICETC Track 10, SAC AIED, IEEE MLNLP for the NLP side), next-cycle dates **unverified** | X2-C (external gate), D-X2-TAU, human/authoring pathway, institutional determination | None of the ten listed dates is compatible with X2-C (gate not started) | **No** for a confirmatory paper on any listed date; no exploratory-only submission is proposed now | Evaluation-methodology framing; "partially fine-tuned derivative with incomplete provenance"; no validity claim | Claiming validity from 64 author-built answers; a venue requiring human-study documentation the project cannot yet supply |

### 10.3 Can legitimate Paper-1 evidence be completed by the ICETC deadline? (feasibility, not a plan to compress)
Chain that must all complete legitimately: Codex audit clears (Sparsh-run; turnaround unknown) -> ChatGPT reviews the X1-C design and the corrected X1-B design -> construction, mutation-control dry runs, tag, run and freeze for each experiment that the paper will cite -> evidence package -> a >= 5-page paper.
- X1-C has no human or external-service dependency (Docker is available) and is the most tractable inside 20 days.
- X1-B additionally needs the corrected design approved, a confirmed Qwen service with recorded model files, the channel enumeration and a hashed prompt set.
- X1-A is the largest (dependency enumeration, one mutant per scenario, timing-sensitive scenarios with about 30 randomised injection points each).
- Executor's honest estimate: **unlikely for the full X1-A/B/C set by 10 Oct; possible only for a scoped paper** limited to claims backed by completed, frozen experiments (e.g., X1-D and X1-C), and whether such a scope is publishable is the minimum-evidence judgement in 5.5 for Sparsh + ChatGPT. The deadline has been extended twice, but a further extension is not assumed.
- **Go/no-go checkpoint (about 3 Oct):** if the audit and the design approvals are not in hand by then, ICETC is not pursued and the same test is applied to ATIS (7 Nov). If neither is legitimately achievable, Paper 1 waits. No gate, mutation control or review step is dropped to move a date.

---

## 11. Deadline and dependency timeline (from 2026-09-20)

Days remaining: 30 Sep = 10; 2 Oct = 12; 9 Oct = 19; 10 Oct = 20; 12 Oct = 22; 7 Nov = 48; 20 Nov = 61; 29 Jan 2027 = 131.

```
Now-Sep 27   [User]   decisions A-set (section 13); trigger Codex audit and ChatGPT protocol review (parallel); send enquiries (critical-path for Paper 2)
             [Exec]   Codex audit brief; Paper-3 package build (packaging only); X1-C/B/A protocol drafts and enumeration table (no runs);
                      run_manifest_v2 (new file); D-F1 documentation banners if approved
Sep 28-Oct 5 [Codex/ChatGPT] outputs; [Exec] validate findings; new tags only if a finding requires them
Sep 30       ICMLSC 2027 and IEEE AIEI 2027 (listing) deadlines  -> not achievable without weakening gates; not planned
Oct 2        ACM SAC 2027                                        -> opportunistic only; needs audit+review+draft in <= 12 days; not recommended
Oct 9        HCII 2027 proposal (800 words)                       -> Paper 3 only, only after Codex clearance of x3a_* and a go-ahead
Oct 3        Paper-1 go/no-go checkpoint for ICETC (audit in hand? designs approved? X1-C tagged?)
Oct 10       ICETC 2026 (Paper 1 primary)                         -> only if legitimate evidence is complete (10.3); otherwise not pursued; extension not assumed
Oct 12       SmartCom 2027 (regular)                              -> not planned
Oct 6-Oct 24 X1-C construct -> dry-run mutation controls -> tag -> run -> freeze (needs audit clear + ChatGPT review + design approval; failing-test triage reviewed)
Oct 20-Nov 3 X1-B (corrected two-part design approved; real Qwen service) and X1-A (largest); package assembly
Nov 7        ATIS 2026 (Paper 1 fallback)                         -> same test; drafting only after gates; at risk if any X1 slip or blocking finding
Nov 20       IEEE MLNLP 2026 (unverified)                         -> not planned (Paper 2 on hold; official date unverified)
Jan 29 2027  HCII final paper (if proposal accepted)              -> time for gates between proposal and full paper
X2-C         earliest date unknown: depends on institutional determination (not requested yet), consent, raters, authors; not schedulable
```
Parallel: Paper-3 packaging, Paper-1 construction drafts, enumeration table, provenance enquiries, evidence-package scaffolding. Blocked by Codex/ChatGPT review: any **new** confirmatory execution, and manuscript claims (only claims that survive the review may be used; the existing frozen results are neither invalidated nor rerun). Blocked by external human/ethics: X2-C, natural-answer stratum, rater recruitment, provenance repair. Immediately packageable: Paper 3. **Deadline risks:** every date before 7 Nov is at risk for a well-gated paper; ATIS is at risk for Paper 1; no listed date fits Paper 2's confirmatory version. The plan takes no shortcut on gates to change that. Passed: ICTCS 2026 (Italian, 28 Jun 2026); SmartCom early-bird (11 Sep 2026).

---

## 12. Reviewer-attack checklist (concise; registry evidence in brackets)

**Paper 1**
- "10/10 faults recovered was a literal" - withdrawn [`P1-C004`]; answer only with X1-A.
- "9/9 contained: five attacks cannot tell blocked from harmless" [`P1-C003/C006`]; answer only with X1-C layers 1-4 and the permissive control.
- "Static filter is bypassable" - observation that header restrictions are unused (section 5.2); report as a finding, not hide it.
- "Isolation by inspection is not a test" [`P1-C005`]; X1-B.
- "Your own test says metrics may be fabricated" [`X1D-C001`]; disclose; the failing assertion concerns dimension-4 semantics, not fabrication (triage 5.6); any build decision is Sparsh + ChatGPT's after the triage.
- "N=1 per attack, one machine, shared kernel" - scope statements; repetitions.
- "Cold start dominates latency" [`P1-C001`, `X1D-C002`]; report cold and warm separately with N.
- "SQLite micro-benchmark, not load test" [`P1-C002`, `X1D-C003`].
- "Cannot reproduce: unlocked environment, pin violations" - state; locks for new runs.

**Paper 2**
- "Eight questions, developer-built" [`P2-C005`, `X2A-C001`].
- "Your model learned length" [`X2B-C003`].
- "Why ship the composite?" [`P2-C007`, `X2A-C003/C008`].
- "Possible train/test contamination; undocumented fine-tune" [`P2-C003`, `X2B-C001/C002`].
- "Circular validation (pilot overlap)" [`X2A-C006`].
- "Not usable as a grade: bias -0.134, no threshold" [`X2A-C007`, N5].
- "Ethics approval? independent experts?" [`P2-C011` withdrawn].
- "Ceilings for adversarial tests are author-set" [`P2-C013`].
- "Very high human reliability on constructed contrasts is not evidence for natural answers" [`P2-C008`].

**Paper 3**
- "So the learned policy is redundant" - accept, scoped [`X3A-C001`, `P3-C009`].
- "Your target is your reward / oracle coupling" [`P3-C023`, `X3A-C005`].
- "Off-distribution evaluation: trained on one candidate, shield in the loop, unseeded" [`P3-C017..C019`].
- "Headline shield benefit was five personas" [`X3A-C003`, `X3A-C007`].
- "40 factorial personas, 5 seeds: inference to what population?" - state generator and scope.
- "Why delta 0.12?" - pre-registered, report raw effect.
- "Simulation-only; single simulator" - no learner claim.
- "563 vs 99" - use counting glossary [`P3-C005/C008`].
- "Authors built simulator, harness and analysis; no independent code review" - closed only by the Codex audit.

**Cross-paper:** authors built evaluator, benchmark, simulator, harnesses and analyses; protocols were tagged before data but reviewed by no independent party; project `.venv` is unlocked.

---

## 13. Smallest decision set for Sparsh + ChatGPT

Reduced in revision 2. Decisions the executor can handle (tool versioning, construction, documentation) are not listed.

**Must decide before ANY new confirmatory experiment**
1. Approve the independent **Codex audit + ChatGPT protocol review** (Sparsh runs the external tools; brief ready).
2. Approve the **provisional publication portfolio:** Paper 1 -> ICETC primary / ATIS fallback; Paper 3 -> HCII AIS primary; Paper 2 -> hold pending X2-C.
3. Confirm that **no conference deadline overrides the audit, protocol or evidence gates.**

**Must decide before X1-C**
1. Review the **Codex findings.**
2. Review the **root-cause classification of the known failing test** (5.6) and decide whether any build B is warranted (default: keep build A, disclosed).
3. Approve the **X1-C attack / weakened-configuration control / oracle design** (5.2), together with the minimum-evidence bar for Paper 1 (5.5).

**Must decide before X1-B**
1. Approve the **corrected fixed-answer invariance design** (X1-B-I).
2. Approve the **separate behavioural stress test** (X1-B-S).

**Must decide before X2-C**
1. **D-X2-TAU** (6.3).
2. The **human/authoring pathway.**
3. The **institutional determination** (external; the decision to proceed on a documented basis is Sparsh's).

**Not to be raised now:** X3-B (D-N2, D-X3B-OP), PPO retraining, venue formatting, exact X2-C item counts, and the identity of "ICTCS 2026" and "ICMETE 2026" (both remain OPEN; no venue is invented).

**External dependencies [EXTERNAL DEPENDENCY]:** institutional/ethics determination; consent materials; rater and author recruitment and provenance; trainer/model provenance reply; a running Qwen service with recorded model files (X1-B); Codex and ChatGPT reviews; official confirmation of unreadable pages (IEEE MLNLP, IEEE AIEI, ACM SAC AIED track) and of the intended identity of ICTCS/ICMETE; Zotero population (manuscript stage only).

**Documentation-only items [DOCUMENTATION ONLY] (on instruction):** D-F1 supersession banners in the four stale documents (`docs/PROJECT_STATE.md`, `paper/README.md`, `research/README.md`, `research/CLAUDE_RESEARCH_INDEX.md`; the last states rho 0.6975 as "sole authentic"); registry note for `X3A-C006` (descriptive; ablation branches not independently referenced) and correction of the `X1D-C001` wording if the triage is accepted; disclosure notes for O15/O17/O19; evidence-package scaffolding and the Paper-3 package; the enumeration table.

---

## 14. NOT DOING

- No product redesign; no PREPAIred SUT edit (including the failing test, `build_rl_observation`, `RESTRICTED_C_HEADERS`, `FeedbackValidator`).
- No new SUT build merely to obtain a clean test suite; no chasing of 226/226.
- No evaluator redesign, no new accept threshold, no change to weights, theta, dampening or the CrossEncoder; no threshold or rho_min chosen from observed results.
- No PPO tuning, retraining, reward tuning, hyperparameter change, environment change or W&B training run.
- No X3-B (parked; trigger not fired; D-N2 open).
- No rerun of X3-A, X2-B or X1-D because they lacked independent review, or because an ablation lacks an independent reference.
- No X1-A/B/C run, and no X2-C, item authoring, rater contact or benchmark construction, before their gates.
- No confirmatory experiment before the independent harness audit is cleared.
- No edit of the existing `run_manifest.py`, frozen artifacts, tags, results or protocols.
- No manuscript prose, abstracts, proposals or submissions.
- No external submission, no email or enquiry sent.
- No invented results, citations, conference details, ethics or consent status, or provenance; no suppression of negative results.
- No Zotero population.

---

## Final section

### A. Claude recommendation
1. Run the **Codex audit and the ChatGPT protocol review in parallel now**; they gate new confirmatory work and shape which claims a manuscript may use. They do not put the frozen X3-A, X2-B or X1-D results in doubt and no rerun is planned. O1-O20 are leads, not conclusions.
2. Meanwhile do only non-confirmatory work: the Paper-3 evidence package, X1-C/B/A designs and the enumeration table, `run_manifest_v2` as a new file.
3. Review the **failing-test triage** (5.6) before X1-C; it is expected not to block X1-C.
4. Treat ICETC (Paper 1, 10 Oct) as a **go/no-go question on legitimate completion** with a checkpoint about 3 Oct; fall back to ATIS (7 Nov) under the same test; otherwise wait.
5. Aim Paper 3 at HCII AIS only after Codex clears `x3a_*` and Sparsh authorises any proposal text; do not chase ICMLSC.
6. Send the institutional and trainer enquiries when Sparsh decides: they are the critical path for Paper 2.

### B. Decisions required from Sparsh + ChatGPT
Section 13 (three before any new confirmatory experiment; three before X1-C; two before X1-B; three before X2-C).

### C. First executable action
Have Sparsh hand `research/audit/CODEX_HARNESS_AUDIT_BRIEF.md` (now written) to Codex for the read-only audit in a separate worktree, and, in parallel, submit the three tagged protocols and the corrected X1 designs to ChatGPT. The executor then validates each Codex finding before any action. Nothing has been run.
