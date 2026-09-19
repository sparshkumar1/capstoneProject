# Phase 1 Preflight Decision Memo (2026-09-19)

**Status: planning memo only.** Nothing in Phase 1 was run: no X3-0, X2-A or Paper-1 analysis, no study script executed, no result file generated, no model loaded, no environment built or modified, no existing document edited, no external message sent. Everything below comes from reading source, documents and package metadata. **No number in this memo is a new scientific result.** Reviewer: ChatGPT (methodology). Final authority: the user.

**Evidence labels.** `READ` = read from a file in this pass. `AUDIT` = earlier audit finding, not re-checked. `STATIC-CODE` = conclusion from reading source, not from executing it. `RECOMMENDATION` = my judgement for review.

---

## 0. New static findings surfaced during preflight (need ChatGPT/user attention)

| # | Finding | Evidence | Why it matters |
|---|---|---|---|
| **N1** | **The five frozen PPO checkpoints were trained against a single default candidate: skill 0.6, persona "normal".** `train_ppo_seed` builds `AlignedInterviewEnv(dim4_mode=…)` with no candidate argument; `InterviewEnv.__init__` then uses `simulated_candidate or SimulatedCandidate()`; `SimulatedCandidate.__init__` defaults are `skill=0.6, persona="normal"`; `reset()` never resamples the candidate | `STATIC-CODE`: `research/scripts/execute_paper3_study.py:211-235`; `rl/env/interview_env.py:165, 297-306`; `rl/training/simulated_candidate.py:22-27` | Resolves finding F9 of the closeout. The X3 draft's plan to flag the five frozen personas as a "training-distribution subset" is **wrong as written**: only "normal" matches the training candidate; the other four evaluation personas are out-of-distribution for the checkpoints. Also changes the reading of every frozen PPO result (PPO was never trained on struggling/overconfident/lucky/nervous candidates) |
| **N2** | **The training candidate's noise generator is unseeded** (`np.random.RandomState(None)`), so training is **not reproducible from the training seed**: `PPO(..., seed=seed)` seeds SB3/torch, and `env.reset(seed)` seeds only the environment's initial-difficulty draw; the candidate's performance/confidence/hesitation noise comes from OS entropy | `STATIC-CODE`: `simulated_candidate.py:24`; `execute_paper3_study.py:240-252`; `interview_env.py:297-306` | Retraining with the frozen seeds would **not** regenerate the frozen checkpoints. Consequence for X3-B: the candidate must be explicitly seeded, and the statement "identical seeds" cannot be made for the frozen checkpoints. Frozen checkpoints stay valid as hash-pinned artifacts |
| **N3** | The existing environment manifest `research/reproducibility/environment_manifest.json` (timestamp 2026-09-17, commit `9cfd34f`) records `transformers 4.41.2`, torch `2.11.0+cpu`, SB3 `2.7.1`, gymnasium `0.29.1`, sentence-transformers `2.7.0`, faiss `1.13.2`, Python 3.12.7 (Anaconda), 10-core i5-1235U, 15.7 GB, CPU only. The current `.venv` contains **duplicate dist-info directories** for pandas (2.3.3 and 3.0.5), scipy (1.17.1 and 1.18.0), scikit-learn (1.8.0 and 1.9.0), torch (2.11.0+cpu and 2.8.0) and transformers (4.44.2 and 4.57.6), and no 4.41.2. numpy 2.5.2, accelerate 1.13.0 are as reported before | `READ`: manifest; `.venv/Lib/site-packages` directory names | (i) The effective imported versions cannot be determined from directory names; they need an import-time probe (`importlib.metadata` plus `module.__version__`). (ii) The 2026-09-17 manifest does **not** match the current `.venv` (transformers) and predates the Paper 3 freeze commit (`b7cad49`, 2026-09-19); **no artifact records the environment in which the Paper 3 study itself was generated** |
| **N4** | **The N=20 pilot's question list is `ablation/results/ratings_rater1.csv`: 20 rows, qids 1, 3, 10, 41 (5 answers each).** These are also the four benchmark questions found in the legacy 100-question bank | `READ` | Resolves the "source of the pilot question list" prerequisite for X2-A and part of F7 |
| **N5** | The evaluator defines **grade boundaries** at `services/evaluator/app.py:397-405`: `final_score ≥ 0.75` Excellent, `≥ 0.60` Good, `≥ 0.40` Average, else Poor. There is **no explicit "accept" threshold**. `MANDATORY_THRESHOLD = 0.40` (line 260) is a concept-coverage check, not an acceptance rule | `READ` | The X2 draft's "τ_accept from the documented grade boundary" has **two** candidate values (0.60 or 0.75) and a scale problem for component comparators (see §4) — a decision for ChatGPT |
| **N6** | `research/CLAUDE_RESEARCH_INDEX.md` is stale beyond the authority pointer: line 40 gives ρ 0.6975 as the human correlation, line 41 "300,000 steps", line 51 "The sole authentic live single-educator benchmark is ρ = 0.6975" | `READ` | A one-line pointer is not sufficient for this file (§3) |
| **N7** | The frozen script has an `if __name__ == "__main__":` guard (line 1028) and an importable `run_session_trajectory(policy_mode, persona_name, dim4_mode, eval_seed, model_dir, guardrails_enabled, max_steps=10)` (line 296) | `READ` | X3-0c can import the function without running the study; but Python would write `__pycache__` into the frozen `research/scripts/` unless bytecode writing is disabled (§1, §7) |
| **N8** | `paper3_guardrail_results.csv` stores 213 rows with `condition, persona, eval_seed, guardrail_id, raw_action, final_action`: 101 rows for "PPO+Guardrails (Seed 123)" and 112 for "Historical Mismatch" | `READ` (structure and counts only) | The seed-123 rows allow a **stored-file-only** count of action overrides (raw ≠ final) for seed 123 — an independent check on the later replay (X3-0a) |

---

## 1. Replay environment for X3-0

### 1.1 Two different goals (do not conflate)
| Goal | Meaning | Acceptance test |
|---|---|---|
| **G-REPRO: reproduce the historical frozen result** | Show that frozen checkpoints + frozen evaluation code regenerate the *stored* frozen numbers | Exact match to stored per-seed counts: guarded attempted-boundary 26 / 71 / 41 / 33 / 61; guarded activations 122 / 101 / 115 / 120 / 105; seed-123 stored trace rows; frozen MAE/volatility to stored precision |
| **G-NEW: new analysis under a different environment** | Compute quantities the frozen study never stored (raw attempted boundary 136, overrides 99, Constant-Same+G, per-turn logs) | Not reproducible against any stored value; valid only if G-REPRO has passed in the *same* environment, and is registered as "replay of frozen code in environment E (non-locked)" |
G-NEW results may be registered only **after** G-REPRO passes in the same process/environment. A G-REPRO failure means "environment not equivalent"; it is reported and G-NEW is not registered.

### 1.2 Options
| | A. Current `.venv` | B. Clean env rebuilt from `requirements/*.txt` pins | C. Separate isolated env matching the *observed* versions (L-obs) | D. Current `.venv`, used strictly read-only with safeguards + gate |
|---|---|---|---|---|
| Reproducibility | Low as a *record*: unlocked, duplicate dist-info, pins violated | High as a lock, but for the *wrong* environment | High (locked, hashed) once built; the observed set must first be probed | Medium: environment unlocked, but every run is bracketed by a version probe, package-metadata hash before/after and the G-REPRO gate |
| Comparability to the frozen study | **Empirical support:** the P0 replay in this `.venv` reproduced the per-seed frozen counts exactly (AUDIT) | **Unknown/poor:** pins require torch `<2.7`; the only recorded environment (manifest) has torch 2.11.0+cpu and SB3 2.7.1 (outside the pins); checkpoints saved under one torch and loaded under another are not guaranteed to behave identically | Same as A if L-obs = what actually imports | Same as A |
| Practical feasibility | Immediate | Weeks of dependency debugging; contradicts recorded reality | 1–2 h plus large downloads (CPU torch); creates a new directory only | Immediate |
| Scientific risk | Silent drift; no lock hash | Reproduces a fiction; may fail to load checkpoints or change numerics | Low; extra effort delays Phase 1; must not be built from the *duplicated* dist-info blindly | Low for a deterministic discrete-action MLP replay, provided the gate passes |
| Touches `.venv`? | Risk of pyc/cache writes | No | No | Only if bytecode/cache writes are prevented (see 1.3) |

### 1.3 Recommendation (one route): **D — current `.venv`, read-only, gated — for Phase 1; build the L-obs lock (option C) in Phase 2, before any confirmatory experiment.**
Rationale: Phase 1 is exploratory/transparent stored-data work plus one evaluation-only replay of a discrete-action MLP policy; the only equivalence evidence available is the earlier exact reproduction in this `.venv`; building a new environment now would spend the session on setup and would not prove equivalence to an unrecorded environment either. The risk is contained by a **reproduction gate** and by recording the environment as *non-locked*.
Safeguards (all required):
1. `PYTHONDONTWRITEBYTECODE=1` and `python -B` for every Phase-1 process, so no `__pycache__` is written into `.venv` or the frozen `research/scripts/`; `HF_HUB_OFFLINE=1`, `WANDB_MODE=disabled` (no network, no W&B run).
2. **Before/after check of the environment:** hash a sorted listing of `.venv/Lib/site-packages` entry names and sizes (or `pip list --format=freeze` output) before and after; any difference aborts and is reported.
3. **Import-time version probe** stored in the manifest: for each of numpy, pandas, scipy, scikit-learn, torch, stable-baselines3, gymnasium, plus `python`, record both `importlib.metadata.version` and the module's `__version__` and `__file__`; flag disagreement (duplicate dist-info problem, N3).
4. Run the frozen evaluation function by import (never `main()`), from a **new** script in a new directory, with all outputs under `research/analysis/phase1/…` (never `research/results/…`).
5. **G-REPRO gate** (1.1) passes before any G-NEW value is computed or registered. If it fails: stop, report, do not register, and escalate to option C.
6. Registry rows created from this replay carry `env_lock_sha256 = NONE (non-locked; see manifest)` and a note stating "replay of frozen code in the current unlocked `.venv`".
7. X2-A and the Paper-1 analysis use only csv/numpy/pandas/scipy on stored files; they use the same non-locked environment, record versions, and set an explicit RNG seed.

### 1.4 If option C is needed in the next session (fallback), create exactly:
`envs/replay-Lobs/` (git-ignored) via `python -m venv` on the Anaconda 3.12.7 base; install only the **probed effective** versions of numpy, torch (CPU), stable-baselines3, gymnasium, pandas, scipy, scikit-learn, sentence-transformers, transformers, faiss-cpu (+ their pinned dependencies) with hashes; write `research/locks/replay-Lobs.requirements.txt`, `…lock.json`, `…sha256` per `ENVIRONMENT_LOCK_SPEC.md`; then re-run G-REPRO in it. The current `.venv` is not touched. (Do not create it unless G-REPRO fails in D or the user prefers a locked record.)

---

## 2. Run-manifest writer

**Need.** Phase 1 has three analyses with many input/output hashes and a required before/after environment check; hand-written manifests would be error-prone and repetitive, and a wrong hash undermines the registry. A full generator is unnecessary.
**Recommendation (minimum robust): a small, stdlib-only helper module** (proposed `research/tools/run_manifest.py`, ≈ 80–120 lines, no third-party imports) with two calls, `start(analysis_id, inputs, seeds, config, command)` and `finish(outputs, deviations)`, invoked from each new Phase-1 script; plus the manifest JSON schema below. No CLI, no framework, not part of any frozen code. It is a new tool → needs your approval (it is code, though not scientific logic).
**Behaviours (required):** refuse to write inside any frozen path list or to overwrite an existing file; hash inputs before and after (proves read-only use); record git commit, tag(s) pointing at HEAD, dirty flag and a hash of the working-tree diff; record OS, Python, `importlib.metadata` versions **and** `__version__`/`__file__` for named packages (detect duplicate dist-info); record hardware (CPU model, cores, RAM; GPU none); record command line, start/end UTC; record environment-listing hash before/after; record seeds; record `env_lock_sha256: null` plus reason when non-locked; record pre-run-note hash where applicable; write `status: started` first and `completed/failed` at the end.
**Phase-1 schema** (subset of `RUN_MANIFEST_SPEC.md`; unchanged field names):
```
{ "manifest_version": "1.0-phase1",
  "analysis_id": "X3-0a | X3-0c | X2-A | P1-STORED",
  "status": "started|completed|failed",
  "started_utc": "", "finished_utc": "",
  "protocol": {"type": "phase1_preflight_note", "note_path": "", "note_sha256": ""},   // no protocol tag exists for exploratory Phase-1 work
  "code": {"git_commit": "", "git_tags_at_head": [], "git_dirty": false, "dirty_diff_sha256": null,
           "entrypoint": "", "entrypoint_sha256": "", "command_line": ""},
  "config": {"config_path": "", "config_sha256": ""},
  "environment": {"lock_id": null, "env_lock_sha256": null, "non_locked_reason": "…",
                  "os": "", "python": "", "packages": {"name": {"metadata": "", "module_version": "", "module_file": ""}},
                  "site_packages_listing_sha256_before": "", "site_packages_listing_sha256_after": "",
                  "hardware": {"cpu": "", "cores": 0, "ram_gb": 0, "gpu": null},
                  "env_flags": {"PYTHONDONTWRITEBYTECODE": "1", "HF_HUB_OFFLINE": "1", "WANDB_MODE": "disabled"}},
  "seeds": {"bootstrap": 0, "other": {}},
  "inputs": [{"path": "", "sha256_before": "", "sha256_after": ""}],
  "models": [{"role": "ppo_checkpoint", "path": "", "sha256": "", "training_seed": 0}],
  "outputs": [{"path": "", "sha256": ""}],
  "gate": {"name": "G-REPRO", "passed": null, "details": ""},
  "deviations": [], "failures": [] }
```
**Minimum implementation work before Phase 1:** write the helper; dry-run it on a **non-scientific dummy** (a scratchpad text file) to check hashing, refusal-to-overwrite and frozen-path refusal; no scientific data are involved. If you decline a tool: a manual manifest is acceptable only for the Paper-1 stored-data analysis (few inputs); X3-0c and X2-A should not use manual manifests (hash volume, before/after checks).

---

## 3. Old-document supersession pointers (do not edit now)

| File | Status | Stale statement (exact location) | Proposed replacement / pointer | Sufficient as one line? | Risk | Approval |
|---|---|---|---|---|---|---|
| `docs/PROJECT_STATE.md` | **Pre-existing untracked user file** | Lines 3–4: "scientific facts live in `research/CANONICAL_SCIENTIFIC_TRUTH.md`." (Line 8 lists that file under FROZEN — still true, no change) | "…scientific facts live in `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` (the root `CANONICAL_SCIENTIFIC_TRUTH.md` is frozen historical; see `research/audit/SCIENTIFIC_TRUTH_SUPERSESSION.md`)." | Yes | Low | **User** (their file; must stay untouched unless they approve or edit it themselves) |
| `paper/README.md` | **Pre-existing untracked user file** (the IEEE paper workspace) | Line 21: "Facts about the existing system come from `research/CANONICAL_SCIENTIFIC_TRUTH.md`." | "…come from `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` and, for wording, `research/claims/CLAIM_REGISTRY.csv` (VALID rows only)." | Yes | **Medium if left** (this directory is where manuscript drafting will start) | **User** |
| `research/README.md` | Tracked; last commit `45845a9` (pre-freeze); not on the frozen list | Line 84: table row "Authoritative Scientific Truth → `CANONICAL_SCIENTIFIC_TRUTH.md`"; lines 122–125: "Authoritative Files (Use as Ground Truth): All files in `CANONICAL_SCIENTIFIC_TRUTH.md`"; line 26 table "Verified Value" section and two lines mentioning ρ 0.6975/0.7400 (not yet inspected in detail) | Add a dated banner at the top: "SUPERSEDED FOR SCIENTIFIC FACTS as of 2026-09-19: use `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`; this README's metric table may contain superseded values (e.g., ρ 0.6975)"; leave the body unchanged | A banner, yes; rewriting the body, no | Low (tracked diff; no scientific content changed) | **User** (tracked project doc) |
| `research/CLAUDE_RESEARCH_INDEX.md` | Tracked; last commit `45845a9`; not on the frozen list | Line 14: "…`CANONICAL_SCIENTIFIC_TRUTH.md` — The sole authoritative record…"; line 39: formula source; **line 40: human correlation → ρ = 0.6975**; **line 41: RL steps 300,000**; **line 51: "The sole authentic live single-educator benchmark is ρ = 0.6975"** | Top banner: "SUPERSEDED FOR SCIENTIFIC FACTS as of 2026-09-19 (see `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`); lines 14, 40, 41 and 51 are stale (ρ 0.6975 is a superseded pilot; the frozen Paper 3 study used 24 576 timesteps per seed)." Body unchanged | Banner yes; a per-line pointer is not enough because the file gives explicit superseded numbers as current (N6) | **Medium** — `CLAUDE.md` still lists this file as the "older reading order", so a session that follows it meets ρ 0.6975 as "sole authentic" | **User** |

**Recommendation.** Do this as a 5-minute documentation pass at the very start of the next session, **before** Phase-1 analysis, using banners rather than line rewrites (minimal diff, nothing frozen touched). The two untracked files are the user's own: offer the exact text and let the user apply or approve it. `CLAUDE.md` line 8 already overrides them for Claude sessions, so this is defence-in-depth, not a blocker.

---

## 4. X2-A analysis labelling

**Context that fixes the labels.** The 64-case benchmark is exploratory/initial evidence (decision lock). Its authors have already seen its results; θ = 0.30 and the dampening were chosen on a pilot that shares questions 1, 3, 10, 41 (N4); the per-question/overlap patterns were already seen as diagnostics in the audit (`AUDIT-DIAGNOSTIC`). Hence **no X2-A output can be confirmatory**; the confirmatory role belongs to X2-C. But "exploratory" is not the right label for everything: what matters is whether an output is descriptive, a sensitivity analysis of a frozen estimand, or a hypothesis-generating test.

| X2-A output | Label | Why | Notes |
|---|---|---|---|
| Question-cluster (two-level) bootstrap CI for composite/component ρ | **Diagnostic / sensitivity analysis** (re-estimate the uncertainty of an already-reported estimand under a design-appropriate resampling) | Estimand unchanged (ρ on 64 items); no new hypothesis; the frozen case-level CI treats answers as independent; the balanced 8×8 design makes cluster resampling the natural sensitivity check | May be registered as a stated sensitivity interval (T2, seed fixed); never a confirmation of validity; only 8 clusters, so the interval is coarse |
| Leave-one-question-out ρ | **Diagnostic / sensitivity** (influence analysis) | Shows dependence on individual questions | Descriptive range, no test |
| Per-category ρ / bias | **Descriptive** | n = 2–8 per category (2 and 4 in some); no reliable inference | Report n, means, signed bias; do not report within-category ρ CIs as inferences. Within-category ρ where n ≤ 4 is not computed or is flagged unreliable |
| Rater leave-one-out | **Diagnostic / sensitivity** (robustness of the gold) | Ten items were adjudicated (`gold_method = expert_adjudication`) | **Must fix before running:** how adjudicated items are treated (recommended: recompute each LOO gold from the two remaining raw rater files for all 64 items and report separately with and without the ten adjudicated items) |
| Adversarial false-accept (composite vs R-only vs S1 vs S1+R) | **Exploratory, pre-specified** (the rule is fixed before computing; the data are seen data) — **hypothesis-generating for X2-C H3** | It tests the only stated reason to ship the composite (it correlates below R-only); on seen, constructed data it cannot confirm anything | Parameters used in X2-C must be **fixed in the same pre-run note, not tuned on X2-A output** |
| Overlap vs non-overlap questions | **Exploratory / post-hoc descriptive** | Four clusters per side; question difficulty also differs; pattern already seen; not evidence of leakage or tuning bias | Point estimates only, no CI/test; explicitly not a held-out validation |

**Recommended protocol wording (replace X2 draft §2 "Outputs" sentence before X2-A is run):**
> "All X2-A analyses are performed on data whose primary results were already known to the authors (the frozen 64-case benchmark), and on a pilot-overlapping question set. None is confirmatory. The question-cluster bootstrap and leave-one-question-out and rater leave-one-out analyses are *sensitivity analyses of the frozen estimand*; per-category and overlap/non-overlap results are *descriptive*; the adversarial false-accept analysis is *exploratory with a pre-specified rule* and generates the hypothesis (H3) that is tested confirmatorily only in X2-C. Every rule, threshold, category set, resampling method, number of resamples and random seed used below is fixed and hashed in a pre-run note before any X2-A output is computed. No parameter of X2-C is chosen from X2-A output."

**What must be frozen before X2-A (pre-run note, committed and hashed first):**
1. The acceptance rule for false-accept, chosen from the code-defined boundaries (N5): candidate **τ = 0.60 ("Good")** primary and **0.75 ("Excellent")** as sensitivity — *decision for ChatGPT* — and the definition of "false accept": an item in the adversarial set with the evaluator's `final_score ≥ τ`.
2. **Scale caveat (decision for ChatGPT):** a fixed τ applies naturally to the deployed composite `final_score`; applying the same τ to R-only or S1 (different score scales) favours whichever scores lower on average. Options: (a) fixed τ for the composite only; (b) **threshold-free AUROC** for adversarial vs correct items for every scorer (recommended as co-primary); (c) matched operating point — for each scorer, the τ that accepts a pre-specified fraction of the "correct" categories (a *rule*, not a tuned value).
3. The adversarial category set (draft: keyword_stuffed, misconception, contradictory, incorrect, verbose_wrong) and the "correct" reference set (concise_correct, verbose_correct, suboptimal_correct, paraphrase), fixed as category names (construction labels, not results).
4. Resampling: two-level cluster bootstrap (resample the 8 questions, then answers within question), percentile interval, **B = 10 000**, an explicit RNG seed (declared), interval type; how ties in Spearman are handled (average ranks).
5. Rater-LOO treatment of adjudicated items (above).
6. The overlap sets: pilot qids {1, 3, 10, 41} (source `ablation/results/ratings_rater1.csv`) vs {7, 15, 22, 50}.
7. The full output list and the rule "all analyses computed in one run; no iteration or re-running after inspection"; output directory `research/analysis/phase1/x2_a/` (new).

---

## 5. X3-0 approval boundary and execution order

**Classification of X3-0 outputs**
| Output | Type | Depends on training-persona logic? | Needs replay environment? |
|---|---|---|---|
| Per-seed guarded attempted-boundary counts (26/71/41/33/61 = 232), activations (122/…/105 = 563), five-seed volatility, MAE per seed | Pure recomputation from stored `paper3_seed_results.csv` | No | No |
| Corrected ablation rows (P1-14) | Pure recomputation from stored ablation/baseline CSVs | No | No |
| Seed-123 action overrides (raw ≠ final), by persona, and activations by rule for seed 123 and historical mismatch | Pure recomputation from stored `paper3_guardrail_results.csv` (N8) | No | No |
| Raw attempted boundary actions (136), overrides across five seeds (99), 464 unchanged activations, 41 of 125 sessions, Constant-Same+G MAE (0.673), per-persona MAE, per-turn logs | **Requires replaying code** (frozen checkpoints + `run_session_trajectory`) | No (evaluation personas are the frozen five) | **Yes** |
| Persona-level paired differences and SD for X3-A sizing | Needs Constant-Same+G per persona → replay | No | Yes |
| Statement of what training sampled (N1, N2) | Static code reading | This *is* that logic | No |

**Can the replay be split?** Yes: 0a, 0b and 0d are independent of the environment; only 0c needs it, and 0c has an internal gate (G-REPRO before G-NEW).

**Execution order**
| Step | Inputs | Expected output | Scientific data generated? | Reproducibility requirement | Stop condition |
|---|---|---|---|---|---|
| **X3-0a** (stored-file-only) | `paper3_seed_results.csv`, `paper3_baseline_results.csv`, `paper3_ablation_results.csv`, `paper3_summary_results.csv`, `paper3_guardrail_results.csv` (read-only; hashes recorded before/after) | Tables: 232 / 563 by seed, five-seed volatility and MAE, corrected ablation rows, seed-123 overrides and activations by rule/persona; new output dir `research/analysis/phase1/x3_0/` | Recomputation of stored values (no new data) | Deterministic; T2; manifest | Any recomputed value differing from the stored per-seed values; any input hash change |
| **X3-0b** (static code) | The three source locations in N1/N2 (and any other training path found by search) | A short dated note (in the output dir) stating what training used (single candidate skill 0.6 "normal"; unseeded candidate RNG) with file:line references | No | Line references re-checkable | A second code path that samples personas is found (then the note must say so and N1 is qualified) |
| **X3-0c** (replay) | Evaluated checkpoints `research/experiments/paper3/checkpoints/seed_{42,123,456,789,999}/{ppo_final.zip,vecnormalize.pkl}` (hashes recorded); `run_session_trajectory` imported from the frozen script (never `main`, no bytecode writes); frozen personas and seed lists; frozen guardrail module | Per-turn logs (persona, seeds, turn, perf, avg_perf, conf, hes, difficulty, raw action, final action, rule id, attempted-out-of-range flags for raw and final action); per-seed summary; **G-REPRO** report; then raw 136, overrides 99, unchanged 464, sessions 41/125, Constant-Same+G MAE, per-persona MAE | **Yes — new derived data** (evaluation-only, in a non-locked environment) | Section 1.3 safeguards; G-REPRO passes first; explicit seeds; manifest | G-REPRO fails; environment listing changes; any write outside the new directory; the per-persona result being used to change any protocol parameter |
| **X3-0d** (integrity) | Frozen hash list (366 files + registry), `git status` | Pass/fail report; registry rows `P3-C007/8/9` updated only if 0c passed and T2-verified | No | Compare with the Phase-0 snapshot | Any frozen hash mismatch (halt and report) |

**Recommendation on approval boundary.** **X3-0a, X3-0b and X3-0d can start immediately after the reset** (no code from the project is executed; no environment question). **X3-0c needs your explicit go-ahead and ChatGPT's confirmation of route D (§1)**, because it executes project code and generates new derived data. Planned artifacts for the three pending registry rows (so none lacks one): `P3-C007`/`P3-C008` → `research/analysis/phase1/x3_0/replay_summary.csv` and `replay_turn_log.csv`; `P3-C009` → `…/replay_summary.csv` (Constant-Same+G rows) plus the manifest.

---

## 6. Phase-1 master execution order (recommended)
1. **Decisions and documentation pass** (§3 pointers if approved; ChatGPT decisions in §"Decisions ChatGPT should review"). ~10 min.
2. **Manifest helper** (§2) written and dry-run on a dummy file (if approved). ~15 min.
3. **Paper-1 stored-data claim/latency analysis** — independent of everything, no environment risk, quick, and it exercises the manifest helper on a low-stakes task.
4. **X3-0a + X3-0b** — stored-file-only and static; sets up the gate values for 0c.
5. **X2-A** — after the pre-run note is frozen (§4) and ChatGPT's decisions on τ/AUROC are known; pure stored-data statistics in one run.
6. **X3-0c + X3-0d** — last, because it is the only step that executes project code and generates new derived data; run once, in a fresh process, gated.

Rationale: scientific value is highest for X3-0 (fixes the P0-2/3/4 registry rows and feeds X3-A sizing) and X2-A (feeds X2-C design), but both depend on frozen decisions or approvals; ordering the no-risk stored-data steps first uses the session's early context on work that cannot contaminate, avoids repeated environment setup (0a/0b/Paper-1/X2-A share one non-locked `.venv` process style; 0c runs once), and delays any code execution until the gate and approvals are in place. **No result from a later step may change a parameter fixed for an earlier step** (§7).

---

## 7. Preflight safety check (issues found)

| # | Issue | Where | Status/action |
|---|---|---|---|
| S1 | **Unfrozen thresholds/rules** in X2-A: τ (0.60 vs 0.75), scale caveat (fixed τ vs AUROC vs matched operating point), category sets, bootstrap seed and B, rater-LOO adjudication treatment, overlap sets | X2 draft §2 | Must be frozen in the pre-run note (§4 list 1–7) before running |
| S2 | X3-0 has no thresholds, but bootstrap seed/B (if any bootstrap of the persona-level SD is used) and the definition of "override", "activation", "attempted boundary action" must be written down first | X3 draft §2 | Freeze definitions in an X3-0 pre-run note; no bootstrap needed for SD over five personas (use the sample SD; state n = 5) |
| S3 | **Output-path overwrite risk:** the frozen script's default outputs are under `research/results/paper3/`; importing it must not run `main`; an unguarded write or `__pycache__` in `research/scripts/` would alter a frozen directory | `execute_paper3_study.py:520, 1028`; `research/scripts/` | Use new directory `research/analysis/phase1/…` only; `PYTHONDONTWRITEBYTECODE=1`; helper refuses frozen paths; hash check after every run (X3-0d). Verify `research/analysis/` does not already exist and is not on the frozen list (it is not) |
| S4 | **Pending registry rows had no planned artifact** (`P3-C007/8/9`); `P2-C012` likewise | `CLAIM_REGISTRY.csv` | Planned artifact paths now specified in §5/§4; to be entered in the registry only when the artifacts exist |
| S5 | **"Result" language for diagnostics:** X2 draft §2 "Interpretation" ("if the composite does not beat R-only … the paper says so") reads as if an X2-A diagnostic decides a paper statement; PREREG A.6 says X2-A is not confirmatory | X2 draft §2; PREREG A.6 | Apply the §4 wording; label as sensitivity/descriptive/exploratory; paper statements about H3 depend on X2-C |
| S6 | **Post-hoc parameter leakage risks:** (a) X2-A outputs (e.g., overlap ρ, false-accept rates) must not set X2-C's τ, categories or ρ_min; (b) X3-0 outputs (per-persona MAE, SD) will be seen before X3-A is tagged — acceptable for sample-size planning only, must be disclosed, and **must not** change δ = 0.12, m = 0.20 or the classification rule; (c) the X3-B trigger/method-level-claim decision will be made after X3-0 is known, so it is **not blind** and must be disclosed (already required in PREREG B.1) | X2/X3 drafts; PREREG | Add explicit "no parameter from Phase-1 output" statements to the pre-run notes; ChatGPT to judge whether (c) needs stronger handling |
| S7 | **The X3 draft's "training-distribution subset" statement is wrong given N1**; also the X3 draft's "whether training sampled the five frozen personas has not been verified" is now answered (single "normal" candidate) | X3 draft §3 | Correct in a later documentation pass after ChatGPT review (draft not yet tagged); do not edit now |
| S8 | **Frozen checkpoint reproducibility** claim is not supportable (N2): documents that imply "same seeds → same checkpoints" (e.g., the report's "convergence robust across five random seeds") must not be used to argue reproducibility of training | frozen report; CURRENT §D.1 | Add N1/N2 to CURRENT and the registry (after approval) |
| S9 | Existing environment manifest (N3) conflicts with the current `.venv` and postdates the CrossEncoder era; it must not be cited as the environment of the frozen Paper 3 results | `research/reproducibility/environment_manifest.json` | Note in the registry/CURRENT that no environment record exists for the Paper 3 run |
| S10 | Retained: one earlier background `find` command from the closeout may still be running in the shell; harmless (read-only) | — | Ignore |
| S11 | Registry rows relying on AUDIT evidence (F2/F3 of the closeout) still need re-verification/splitting | closeout §2 | Phase 1 low priority: re-verify `P2-C008`, `P2-C013` (split), `P1-C003`, `X-C004`, `P2-C003` |

---

## NEXT SESSION — EXACT START ORDER
1. **Orient (read-only):** read `CLAUDE.md`, `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`, `research/audit/PHASE0_DECISION_LOCK.md`, `PHASE0_CLOSEOUT_AUDIT.md` §9–10, and this memo. Recompute the frozen-file hashes against the Phase-0 snapshot (`research/audit/PHASE0_DECISION_LOCK.md` §3 hashes; the 366-file snapshot list must be rebuilt from `git ls-files` if the scratchpad is gone) and run `git status`; stop on any mismatch.
2. **Collect decisions** (from the user, informed by ChatGPT's review of "Decisions ChatGPT should review"): environment route D; manifest helper approved?; pointers approved?; X2-A labelling wording; τ / AUROC / matched-operating-point choice; rater-LOO treatment; X3-A persona-strata correction (N1); whether X3-0c may execute.
3. **Documentation pass (only if approved):** add the four banners/pointers of §3 (untracked files only with the user's OK).
4. **Write the manifest helper** (if approved) and dry-run on a scratchpad dummy file.
5. **Paper-1 stored-data claim/latency analysis** → new dir `research/analysis/phase1/paper1/`; claim-survival table, stored latency percentiles (no CIs), proposed registry rows; manifest.
6. **X3-0a and X3-0b** → `research/analysis/phase1/x3_0/` (X3-0a tables; X3-0b note on N1/N2).
7. **X2-A:** write and commit the pre-run note (§4 list) **first**; then run all X2-A analyses in one run into `research/analysis/phase1/x2_a/`; register outputs as sensitivity/descriptive/exploratory; keep `P2-C012` semantics.
8. **X3-0c (only with explicit go-ahead):** start the read-only-`.venv` protocol of §1.3; run the G-REPRO gate; if it passes, compute the G-NEW outputs; if it fails, stop and report.
9. **X3-0d:** frozen-integrity check, registry updates for `P3-C007/8/9` (only if 0c passed), Phase-1 report with `git status` / `git diff --stat` separating Phase-1 from pre-existing changes. **Stop** before Phase 2.

## DECISIONS CHATGPT SHOULD REVIEW
1. **Replay environment route D** (current `.venv`, read-only, gated by G-REPRO, non-locked) vs building an L-obs environment now — especially given N3 (duplicate dist-info, manifest mismatch) and the absence of any record of the Paper 3 generation environment.
2. **X2-A false-accept design:** τ = 0.60 vs 0.75; fixed τ for the composite only vs threshold-free AUROC vs matched-operating-point for component comparators; the definition of the "correct" and "adversarial" category sets; rater-LOO treatment of adjudicated items.
3. **X2-A labelling** (§4 table and the proposed protocol wording): is "sensitivity/diagnostic" for the cluster bootstrap and leave-one-out appropriate, and may the cluster interval be registered as VALID (scoped)?
4. **X3-A persona strata after N1:** with training on a single "normal" (skill 0.6) candidate, what estimand does X3-A answer, how should the "in-distribution" stratum be defined (one persona/skill only), and does X3-A's H1 (PPO+G vs Constant-Same+G on out-of-distribution personas) still address the intended question, or should X3-B's training-persona coverage be specified now?
5. **X3-B design consequence of N2:** the candidate RNG must be seeded and the training persona distribution specified; does this alter "reward, state, action and hyperparameters unchanged" (it changes the training environment, which needs the user's approval)?
6. **Equivalence-interval convention** (95 % two-sided CI within ±0.12 vs 90 % TOST-style) — carried from closeout F8.
7. **Non-blind X3-B trigger** (S6c): sufficient with disclosure, or should the method-level-claim decision be pre-committed before X3-0c runs?
8. **Temporal-disjointness anchor** (commit date vs protocol-tag date) and **natural/volunteer answers** for X2-C (closeout F5, F6).
9. Whether the **guardrail-override count from the stored trace** (N8) is an acceptable independent check of the replay for seed 123 only.

## THINGS ALREADY LOCKED (do not revisit without new evidence)
- Phase 0 is closed; frozen artifacts and hashes are immutable (`PHASE0_DECISION_LOCK.md` §3).
- Paper 1: "secure" removed; failure-aware/sandboxed framing; positive/mutation controls mandatory; no `FeedbackValidator`; defect policy (new tag → rerun the relevant/full campaign → retain both builds); "fault-tolerant" only if X1-A supports it; PASS/FAIL computed, never typed.
- Paper 2: the derived CrossEncoder stays frozen and retained; "off-the-shelf/zero fine-tuning" withdrawn; wording "partially fine-tuned derivative with incomplete provenance"; X2-A and X2-B approved; upstream primary comparison is mapping-independent R-only; no composite mapping invented or fitted after seeing results; **one** confirmatory human round (X2-C), question-disjoint, temporally disjoint, independently authored, protected against evaluator-aware filtering, ≥ 3 fully crossed blind raters; old 64 = exploratory/initial; no second human round.
- Paper 3: controlled decomposition, PPO a studied component (not the headline); persona (× training seed) is the statistical unit; δ = 0.12 MAE, m = 0.20 MAE; X3-B trigger frozen before X3-A; no PPO hyperparameter tuning; no reward redesign; no second simulator yet; simulation-only, no learner claims.
- Human/ethics: no fabricated or backdated consent/independence/qualification/timestamps; enquiries are user actions (drafts exist, not sent).
- Truth control: `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` is the sole current authority; old canonical files are historical; ρ = 0.3812 is the current human result; ρ = 0.6975 a superseded pilot.
- Reproducibility: new-run environment lock (Phase 2), run manifests, claim registry, no experiment without a hashed, tagged protocol.
- Frozen-integrity baseline: 366 frozen files verified identical at the Phase-0 closeout; the current `.venv` and `requirements/*` unchanged.
