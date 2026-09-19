# Phase 0 Closeout Audit (static) — 2026-09-19

**Status: CLOSED** (no blockers; open items are Phase-1/Phase-2 tasks or user decisions, listed in §9).
**Nature:** static audit only — reads, greps, hash verification, `git status`. No experiment or study script was executed, no model evaluated or retrained, no dependency or `.venv` change, no frozen file touched, no external message sent, no tag created. Phase 1 was **not** started. Two mechanical documentation edits were made (§10). Scientific decisions were not made; anything scientific is routed to §9 / the next-session checklist.
**Reviewer note (for the independent reviewer):** every number below marked "verified" was checked against a stored file or by a hash in this pass; items marked "read" were checked by reading the draft text only.

---

## 1. Source-of-truth check
| Check | Result |
|---|---|
| `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` internally consistent | **Yes** on the points audited: ρ 0.3812 (CI [0.1575, 0.5774]) in §C.2; R-only 0.4832; S1+R 0.4884; composite below both (stated); same values as `paper2_summary_results.csv` / `paper2_ablation_results.csv` (registry T2 assertions passed in Phase 0); Paper 3 per-seed MAE/volatility, 563, 232 match `paper3_seed_results.csv` (recomputed in Phase 0) |
| ρ = 0.3812 is the current human result | **Yes** — CURRENT §C.2, `CLAUDE.md` line 10, registry `P2-C006` |
| ρ = 0.6975 explicitly historical/superseded | **Yes** — CURRENT §C.2 ("Superseded pilot"), §H; `CLAUDE.md` line 10; supersession record; registry `P2-C009` (HISTORICAL). Every occurrence in Phase-0 documents is in a "superseded/historical" context (grep) |
| Paper 3 unit = persona, not session | **Yes** — CURRENT §D.1; `CLAUDE.md` lines 11 and 33 (both stale statements fixed); errata E-09; registry `P3-C014` (WITHDRAWN session unit) |
| Old canonical files clearly historical | **Yes in Phase-0 documents** (supersession record, CURRENT header, `CLAUDE.md` line 8, hashes recorded). **No in four other files** — see finding F1 |
| Any current document still labels superseded numbers as current | **Phase-0 documents: none found.** Pre-existing documents `docs/PROJECT_STATE.md` (lines 4, 8), `paper/README.md` (line 21), `research/README.md` (lines 84, 125) and `research/CLAUDE_RESEARCH_INDEX.md` (lines 14, 39–40) still name the old root `CANONICAL_SCIENTIFIC_TRUTH.md` as the (sole) authority, i.e. they point readers at a file that carries ρ 0.6975. These are pre-existing user/tracked files and were **not** edited (F1). `CLAUDE.md` line 8 overrides them for Claude sessions |
| Withdrawn wording appears only in withdrawn contexts | "off-the-shelf" appears in `CLAUDE.md` and CURRENT only as withdrawn wording; "secure" appears in the X1 draft only as the removed adjective |

## 2. Claim registry check (`research/claims/CLAIM_REGISTRY.csv`)
- **Total rows: 43** (20 columns; parses cleanly). By paper: Paper 3 = 16, Paper 2 = 13, Paper 1 = 10, Cross = 4. **Duplicate claim IDs: none.** All `superseded_by` targets exist.
- **By status:** VALID 22 · WITHDRAWN 15 · HISTORICAL 2 (`P2-C009`, `P3-C015`) · PENDING-REGISTRATION 3 · EXPLORATORY 1 (`P2-C012`).
- **Conflicting wording:** none found. Withdrawn wording is always paired with a superseding VALID/PENDING row or with a note giving the reason.
- **Missing fields (expected/benign):** rows with no stored artifact (`X-C001/C003/C004`, `P2-C003`, `P2-C008` script fields, `P1-C009`) leave artifact/script/config blank by design; frozen-result rows for Paper 1/2 leave `config_path` blank where no config exists.
- **Evidence-level caveat (F2):** five VALID rows rest on `AUDIT`/`CODE` evidence from the earlier audit and were **not** re-verified in Phase 0 (`X-C004`, `P2-C003`, `P2-C008`, `P2-C013`, `P1-C003`); they have no `last_verified` date. `P1-C009` (CODE) is dated.
- **Single-artifact limitation (F3):** `P2-C013` covers both metamorphic (19/21) and adversarial (11/13) results but carries one artifact hash (the metamorphic file).
- **Withdrawn rows without `superseded_by` (7):** `P2-C011`, `P3-C014`, `P1-C004`, `P1-C005`, `P1-C007`, `P1-C008`, `P1-C010` — no replacement claim exists yet (intended; Paper 1 replacements depend on X1).
- **The exactly 3 pending claims (stored artifacts do not exist):**
  | ID | Claim | Source now |
  |---|---|---|
  | `P3-C007` | Raw PPO attempted boundary actions 136 / 1 250 turns (10.9 %) | P0 replay, scratchpad only |
  | `P3-C008` | 99 action overrides / 1 250 guarded turns (7.9 %); 464 of 563 activations unchanged; 41 of 125 sessions with an override | P0 replay, scratchpad only |
  | `P3-C009` | Constant-Same + same guardrails MAE 0.673 (= PPO+G); PPO's contribution under guardrails not identified | P0 replay, scratchpad only |
- **What Phase 1 (X3-0) must generate for them** (not generated now): for each of the frozen 5 training seeds × 5 evaluation seeds × 5 personas × 10 turns, the evaluation-only replay of the frozen evaluation code with the frozen evaluated checkpoints, stored as a per-turn log (persona, seeds, turn, perf, avg_perf, conf, hes, difficulty, PPO raw action, final action, rule IDs fired, attempted-out-of-range flags for raw and final action) plus a summary CSV (per seed: raw and guarded attempted-boundary counts, activations, overrides; and the Constant-Same+G MAE), a run manifest, the new script with its commit, and hashes; the replay must reproduce the frozen per-seed guarded counts 26/71/41/33/61 (activations 122/101/115/120/105) before any new value is registered; then update the three rows with artifact path, SHA-256, script, commit, tier T2 and change status to VALID.

## 3. Protocol consistency check (X1/X2/X3 drafts; read, not executed)
| Item | Finding |
|---|---|
| X1 positive/mutation controls | Present and mandatory (X1 §3; fault mutants, permissive-container controls, Qwen wiring mutant) |
| Deterministic vs timing-randomised fault logic | Present (X1 §4: deterministic 5–10 repetitions as counts; timing-sensitive scenarios N ≈ 30 randomised points) |
| No Wilson inference for deterministic repetition | Present ("no CI on deterministic repetition"; Wilson only for randomised timing scenarios). Same in `PREREGISTRATION_SPEC.md` B.2 |
| Five-way security oracle | Present (X1 §6: execution, containment, status (not a pass criterion), host impact, resource impact; canaries) |
| Qwen structural + differential test; no `FeedbackValidator` | Present (X1 §5: static AST check + differential ≥ 30 prompt pairs + mutation control; QWN-04 excluded; "no `FeedbackValidator` exists and none will be added") |
| Computed PASS/FAIL | **Was implicit; sentence added (mechanical fix M1, §10).** |
| X2 mapping-free primary upstream comparison | Present (X2 §3: R-only ρ, τ-b, AUROC on raw outputs) |
| X2 composite mapping not chosen after seeing results | Present ("No composite is computed for the upstream arm unless … frozen in advance and label-free"; no MAE for upstream) |
| X2-C is one confirmatory round | Present (X2 header "no second human round", §4 stopping rule; provenance plan rule 6) |
| Leakage/selection controls | Present (question-disjoint, temporally disjoint stratum, independent authorship, no evaluator-aware filtering, score-after-freeze ordering, blind fully crossed raters). Ambiguities: F5–F7 |
| X3 persona × training-seed inference | Present (two-way cluster bootstrap; mixed-model sensitivity) |
| X3 conditions: state-shuffle, Oracle policy, proportional controller, Constant-Same+G, Random+G, Heuristic+G, rule ablations | Present in X3-A (base policy × shield crossing gives the "+G" variants; state-shuffle/constant; controller as upper reference; rule ablation) |
| BC control | Present in **X3-B only** (not X3-A) — consistent with the design, noted for the reviewer |
| δ = 0.12, m = 0.20 | Present and used in the frozen classification table (Equivalent / PPO superior / PPO adverse / Inconclusive) |
| X3-B trigger fixed before X3-A | Present (X3 §6; PREREG A.6: "the X3-B trigger and the method-level-claim decision are inside this tag") |
| No post-hoc tuning/forking | Present (stopping rules, no amendments after data, new-experiment rule, PREREG A.5) |
| **Ambiguities (not resolved here)** | F4, F5, F6, F7, F8 in §9; 18 `[FIX IN PHASE 2]` markers remain by design |

## 4. Phase-1 readiness (none executed)
| Task | Exact inputs | Expected outputs | Exploratory / confirmatory | Thresholds still to freeze | Safe to execute right after the reset? | Missing prerequisite |
|---|---|---|---|---|---|---|
| **X3-0** | Frozen: `paper3_seed_results.csv`, `paper3_baseline_results.csv`, `paper3_ablation_results.csv`, `paper3_guardrail_results.csv`, `paper3_raw_results.json`; for replay: evaluated checkpoints `research/experiments/paper3/checkpoints/*`, frozen evaluation code (`research/scripts/execute_paper3_study.py` functions, imported/copied — not edited), `rl/guardrails.py` | Stored tables: attempted boundary actions (raw/final), activations vs overrides with denominators and per-rule/persona/session breakdown, five-seed volatility table, corrected ablation rows, persona-level paired differences and SD (input to X3-A sizing), per-turn logs; new script + manifest + hashes; registry updates for `P3-C007/8/9` | Exploratory / transparent (existing data already seen) | Definitions only: activation vs override, boundary-saturated; bootstrap B and RNG seed | **Partly.** The stored-file parts (volatility table, corrected ablation rows, seed-CSV counts) yes. The replay parts (136, 99, Const-Same+G, per-turn logs) run the frozen evaluation code with checkpoints — approved as Phase-1 work but they need an explicit go-ahead and the environment decision | (a) decision on running the replay in the unlocked `.venv` with versions recorded and the run flagged "non-locked" (F12); (b) a manifest writer or a hand-filled manifest (F13); (c) output directory naming under a new path; (d) static check whether training sampled the five frozen personas (code read) |
| **X2-A** | `research/results/paper2/paper2_case_level_results.csv`; `final_human_gold.csv` (SHA `363dbe6d…6ce2`); the three hash-pinned rater files (`research/annotation/FROZEN_HUMAN_RATINGS/`); the pilot question list (qid 1, 3, 10, 41 overlap) — source file to be identified | Two-level cluster bootstrap, leave-one-question-out, per-category and within-question ρ, rater leave-one-out, adversarial false-accept (composite vs R-only vs S1 vs S1+R), signed bias by category/length, overlap vs non-overlap; new script, result files, manifest | **Exploratory / transparent** (data already seen; the cluster bootstrap is a re-estimate of the frozen estimand's uncertainty — F4) | **τ_accept** (from the evaluator's documented grade boundary — verify against `services/evaluator/app.py` before any score is looked at); adversarial-category set; B (≥ 10 000) and RNG seed; the AUROC "correct vs incorrect" rule if AUROC is included | **Yes**, once τ_accept, the category set, B and seed are written into a short pre-run note (committed before the run) | Identify the source of the pilot question list; verify the grade boundary in code |
| **Paper-1 stored-data claim/latency analysis** | `research/results/paper1/*.csv`, `paper1_systems_raw.json`, `PAPER1_FINAL_REPORT.md`, `research/scripts/execute_paper1_study.py` (read-only), `post_p1_regression_tests.md`, the P0-6 report | Claim-survival table (evidence class per claim: measured / literal PASS / design fact), latency reported as the stored percentiles with the outlier labelled, registry rows for Paper 1 replacements; **no** CIs for latency (raw per-sample values are not stored; cold vs warm cannot be separated) | Descriptive / exploratory | None (no inferential test) | **Yes** | None |

## 5. Human-benchmark readiness (X2 draft §4, `HUMAN_BENCHMARK_PROVENANCE_PLAN.md`, enquiry drafts)
| Requirement | Separated in the documents? |
|---|---|
| Old 64 = exploratory/initial vs new = confirmatory | **Yes** (decision lock, CURRENT §C.1, X2 header/§4) |
| Pilot/tuning questions vs new questions | **Yes in principle** (question-disjointness with a stored check against the legacy bank and pilot lists). **Ambiguity F7:** the exclusion list is not enumerated (N=20 pilot questions; old 8; any other set used for θ/dampening tuning) |
| Temporally disjoint questions | **Yes**, half of the questions and all their references authored after the CrossEncoder commit date. **Ambiguity F6:** the training date may precede the commit date; anchoring on the protocol-tag date would be stricter |
| Independently authored | **Yes** (authors without evaluator access, or recorded generator without filtering; references before answers; authorship log) |
| Natural/volunteer answers | **Unresolved F5:** X2 speaks of a "natural/varied stratum" (generated); volunteer-written answers appear only in earlier planning; the institutional draft states real candidates' answers are not planned. Whether volunteers are in scope is undecided |
| Constructed adversarial answers | **Yes** (constructed-contrast subset reported separately) |
| Blinded, fully crossed raters (≥ 3) | **Yes** (blind to category/stratum/authorship/evaluator output; randomised order; ledger) |
| Rater provenance | **Yes** (ledger schema; record-recovery checklist for the old round) |
| Consent/ethics records | **Yes as a gate** (G1/G2); consent/information sheet deliberately **not** drafted until the institution replies; nothing may start before G1/G2 |
| One round only | **Yes** |

## 6. Paper-3 readiness
- **X3-A vs X3-B are distinguished** in the X3 draft: X3-A asks what the **existing frozen checkpoints** contribute (evaluation-only; interpretation limited to "these checkpoints" and the tested environment; a superior result still needs X3-B for a method-level claim); X3-B asks what **PPO as a method** contributes under a **training-consistent environment** (retrained, ≥ 10 seeds, budget series, BC comparison).
- Simulation-only scope and "no learner/real-interview benefit" claims: stated (X3 §5 and CURRENT §D.1).
- No reward retuning, no redesign, no hyperparameter search: stated in the header, §1 and §4 ("reward, state, action and PPO hyperparameters unchanged"; "no tuning"). The training budget series in X3-B is a design factor fixed in advance, not tuning.
- Open, by design: persona generator and N, evaluation seed list, controller definition, X3-B environment definition (needs the user's confirmation), the method-level-claim decision (user, recorded before X3-A), whether training sampled the five frozen personas (F9). Equivalence via a 95 % two-sided CI within ±δ is stricter than a conventional 90 % TOST interval — to be confirmed and frozen (F8).

## 7. Paper-1 readiness
Dependency-graph-based fault enumeration (required by X1 §4; table to be built in Phase 2) · mutation controls (X1 §3) · deterministic vs randomised timing treatment (§4) · security canaries and five-way oracle (§6) · computed PASS/FAIL (M1) · defect policy (X1 §2: new tag, complete relevant campaign rerun, both builds retained) · no universal security claims ("contained in this harness"; "secure" removed) · no `FeedbackValidator` claim (feedback stated as unvalidated). **Outstanding (Phase 2, by design):** dependency-enumeration table, SLA/timeouts from design/config, exact API field names, SUT tag, mutant definitions, canary setup, adversarial prompt set, repetition counts.

## 8. Git / frozen-integrity check (static)
- **SHA-256 of 366 frozen files** (`research/CANONICAL_SCIENTIFIC_TRUTH.md`, `research/papers`, `research/results`, `research/CLAUDE_HANDOFF`, pre-existing `research/audit`, `research/experiments`, `research/data`, `research/scripts`, `rl/checkpoints`, `ablation/results`, `experiments`) compared with the snapshot taken at the start of Phase 0: **366 OK, 0 mismatches** (re-run in this closeout after the two mechanical edits).
- Human gold `363dbe6d848a04fe…`, CrossEncoder `6a241a55bef24355…`, Paper 3 `frozen_config.yaml` `d3da218479ef15f6…`: **unchanged**.
- No study/experiment script executed (only the Phase-0 documentation script that hashed and parsed stored files; it is in the scratchpad, not the repo). No files newer than the Phase-0 lock exist under `research/results` or `research/experiments`.
- Dependencies: `git diff -- requirements` empty; `requirements/tracking.txt` is a pre-existing untracked file; `.venv` untouched (site-packages last modified before Phase 0).
- `git status` for `services agents apps rl ablation experiments research/results research/experiments research/scripts research/data research/papers research/annotation research/CLAUDE_HANDOFF`: **no changes**.

`git diff --stat` (tracked files):
```
 .env.example | 6 ++++++
 1 file changed, 6 insertions(+)        (pre-existing; not touched in Phase 0 or this closeout)
```
`git status --short` (excluding the two pre-existing untracked directories `.serena/` and `paper/`):
| Category | Entries |
|---|---|
| **A. Phase-0 changes** (this and earlier Phase-0 turn) | `?? research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`; `?? research/claims/` (`CLAIM_REGISTRY.csv`, `README.md`); `?? research/audit/` : `PHASE0_DECISION_LOCK.md`, `PHASE0_CHANGE_MANIFEST.md`, `PHASE0_ERRATA_ADDENDUM.md`, `PHASE0_CLOSEOUT_AUDIT.md`, `SCIENTIFIC_TRUTH_SUPERSESSION.md`, `X1/X2/X3_PROTOCOL_DRAFT.md`, `HUMAN_BENCHMARK_PROVENANCE_PLAN.md`, `MODEL_PROVENANCE_REQUEST.md`, `INSTITUTIONAL_ETHICS_ENQUIRY_DRAFT.md`, `ENVIRONMENT_LOCK_SPEC.md`, `RUN_MANIFEST_SPEC.md`, `PREREGISTRATION_SPEC.md`; edit to `CLAUDE.md` (untracked file, 5 approved corrections) |
| **B. Pre-existing user changes (untouched)** | `M .env.example`; `?? .serena/`; `?? paper/`; `?? docs/PROJECT_STATE.md`; `?? requirements/tracking.txt`; `?? CLAUDE.md` (the file existed untracked before Phase 0; only the edit in A is Phase 0); earlier-session audit files `?? research/audit/CLAUDE_*` (5 files), `P0_*` (8 files), `P0_P1_*` (2 files), `RESEARCH_STRENGTHENING_MASTER_PLAN.md` |

## 9. Findings table
| # | Problem | Severity | Evidence | Safe to fix now? | Recommended next action |
|---|---|---|---|---|---|
| F1 | Four files still name the old root `CANONICAL_SCIENTIFIC_TRUTH.md` as the (sole) authority: `docs/PROJECT_STATE.md` (4, 8), `paper/README.md` (21), `research/README.md` (84, 125), `research/CLAUDE_RESEARCH_INDEX.md` (14, 39–40) | Medium (future session could follow the index to the stale ρ 0.6975) | grep in this audit | **No** — two are pre-existing user files (must remain untouched); two are tracked project docs | Ask the user to approve adding a one-line supersession pointer to each; until then `CLAUDE.md` line 8 governs |
| F2 | 5 VALID registry rows (`X-C004`, `P2-C003`, `P2-C008`, `P2-C013`, `P1-C003`) rest on audit-level evidence, not re-verified in Phase 0; no `last_verified` | Low–Medium | registry check §2 | No (needs re-verification work) | Phase 1: re-verify by T2 recompute and date them, or relabel scope |
| F3 | `P2-C013` bundles metamorphic and adversarial results under one artifact hash | Low | registry | Not unquestionably mechanical (row split) | Phase 1: split into two rows with their own artifacts |
| F4 | X2-A: draft says results are `EXPLORATORY` "except the cluster bootstrap", while `PREREGISTRATION_SPEC.md` A.6 says X2-A cannot be confirmatory | Low | X2 §2 vs PREREG A.6 | No (a labelling decision) | User/reviewer: label all X2-A outputs "exploratory/transparent" and let the cluster CI be VALID only as a descriptive re-estimate |
| F5 | X2-C natural vs volunteer answers undefined; ethics draft says real-candidate answers not planned | Medium | X2 §4; ethics draft | No (scientific + ethics) | Phase 2 / user decision before tagging X2 |
| F6 | Temporal-disjointness anchor is the CrossEncoder commit date (2026-04-13); training may predate it | Low–Medium | X2 §4 | No | Phase 2: consider anchoring to the protocol-tag date (all items authored after the tag) |
| F7 | Question-exclusion list (pilot, old 8, any tuning set) not enumerated | Medium | X2 §4 | No | Phase 1/2: enumerate and hash the exclusion list |
| F8 | X3 equivalence rule uses a 95 % two-sided CI within ±δ (stricter than the conventional 90 % TOST) | Low | X3 §3 | No (scientific choice) | User/reviewer to confirm before tagging |
| F9 | Whether PPO training sampled the five frozen personas is unverified; strata interpretation depends on it | Medium | X3 §3 | No | Phase 1 (X3-0): static code read of the training persona sampling |
| F10 | BC control appears only in X3-B, not X3-A | Info | X3 §3–4 | — | Reviewer awareness; consistent with design |
| F11 | X1 draft lacked an explicit "PASS/FAIL computed, never typed" rule | Low | grep | **Yes — fixed (M1)** | — |
| F12 | Phase-1 replays would run in the unlocked `.venv` (pins violated); lock not yet created | Medium | ENVIRONMENT_LOCK_SPEC | No (dependency-adjacent; user decision) | Decide: replay in `.venv` with versions recorded and the run flagged non-locked, or create L-obs/L-pin first |
| F13 | Manifest writer and `verify_claims` do not exist | Medium | RUN_MANIFEST_SPEC / claims README | No (new code; approval) | Approve a small writer/verifier, or hand-fill manifests for Phase 1 |
| F14 | 18 `[FIX IN PHASE 2]` items remain in X1/X2/X3 | Info | grep | — | Expected; Phase 2 |
| F15 | `.env.example` modified before this session (CRLF warning from git) | Info | git | No (pre-existing) | User's call |

## 10. Mechanical fixes made in this closeout (complete list)
- **M1:** `research/audit/X1_PROTOCOL_DRAFT.md` §1 — added one sentence stating PASS/FAIL is computed by the harness from asserted observable fields and logs, never typed or hard-coded. Covered by the approved "computed PASS/FAIL" requirement; documentation-only; no other change.
- **M2:** `research/audit/PHASE0_CHANGE_MANIFEST.md` — added a paragraph recording this closeout file and M1. Documentation-only.
- No other file was modified. No pre-existing user change was touched.

---

## NEXT SESSION — PHASE 1 START CHECKLIST
Do these in order. Phase 1 = stored-data analyses only; no new human data, no training, no confirmatory experiment. Nothing below has been started.

**Step 0 — Orientation (read-only, ~5 min)**
1. Read `CLAUDE.md`, `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`, `research/audit/PHASE0_DECISION_LOCK.md`, this file, and `research/claims/README.md`.
2. Re-verify frozen integrity before any work: hash the frozen paths and compare with the pre-Phase-0 list (or with the hashes in `PHASE0_DECISION_LOCK.md` §3); confirm `git status` matches §8 of this file.

**Step 1 — Get the user's decisions that Phase 1 depends on (ask before starting)**
1. F12: replay environment — run in the current `.venv` with versions recorded and the run flagged *non-locked* (recommended for Phase 1 replays), or build a lock first?
2. F13: approve a small run-manifest writer, or hand-fill manifests?
3. F1: approve adding supersession pointers to `research/README.md` and `research/CLAUDE_RESEARCH_INDEX.md` (and whether the user wants `docs/PROJECT_STATE.md`/`paper/README.md` updated by themselves)?
4. F4: confirm the labelling of X2-A outputs (all exploratory/transparent).
5. Confirm the go-ahead to run evaluation-only replays of frozen evaluation code (X3-0), which is Phase-1 work but executes code.

**Step 2 — Paper-1 stored-data claim/latency analysis (safe first; no prerequisites)**
- New directory under a new path (e.g., `research/analysis/phase1/paper1/`); read-only inputs listed in §4.
- Output: claim-survival table, latency percentile table with the outlier labelled (no CIs), proposed registry rows; manifest; hashes. Do not modify `research/results/paper1/*`.

**Step 3 — X2-A (after freezing thresholds)**
1. Identify the pilot question list source; verify the evaluator's grade boundary in `services/evaluator/app.py` (read-only) to set τ_accept; fix the adversarial-category set, B ≥ 10 000 and RNG seed.
2. Write and commit a short pre-run note recording τ_accept, categories, B, seed **before** computing anything.
3. Run the analyses listed in X2 draft §2; save scripts and results in a new directory; register outputs as `EXPLORATORY` (regenerating registry row `P2-C012`); manifest and hashes.

**Step 4 — X3-0**
1. Static read of training persona sampling (F9).
2. Stored-file parts first (volatility table, corrected ablation rows, seed-CSV counts).
3. After the go-ahead and the environment decision: the evaluation-only replay with per-turn logs; **first reproduce the frozen per-seed counts** (guarded attempted-boundary 26/71/41/33/61; activations 122/101/115/120/105); only then compute and store raw attempted boundary actions (136), overrides (99), Constant-Same+G (0.673) and the persona-level paired differences and SD.
4. Update registry rows `P3-C007`, `P3-C008`, `P3-C009` (artifact path, SHA-256, script, commit, tier T2, status → VALID) only after T2 verification.

**Step 5 — Close Phase 1**
1. Update the registry (new rows, dates); add a Phase-1 changelog line to `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` only with user approval.
2. Re-run the frozen-integrity check; produce `git status`/`git diff --stat` and separate Phase-1 from pre-existing changes.
3. Report and **stop**; Phase 2 (protocol completion, harness construction, benchmark authoring, ethics gate, environment lock, tagging) needs its own instruction.

**External actions still pending with the user (not Claude):** send `MODEL_PROVENANCE_REQUEST.md` and `INSTITUTIONAL_ETHICS_ENQUIRY_DRAFT.md`; supply rater-provenance records; decisions F5, F6, F8 and the method-level PPO-claim decision (before X3-A is tagged).
