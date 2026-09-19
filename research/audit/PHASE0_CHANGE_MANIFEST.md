# Phase 0 Change Manifest (2026-09-19)

**Scope.** Every file created or changed in Phase 0, why, whether it is frozen or not, and its expected scientific impact. **Expected scientific impact of every item: none** — Phase 0 changed documentation, provenance, source-of-truth and specification files only. No experiment was run, no model retrained, no code logic, dependency, evaluator, PPO, reward, guardrail or threshold changed, and no frozen artifact was touched. Locked decisions: `PHASE0_DECISION_LOCK.md`.

## 1. Files created (all new, non-frozen at creation; protocol files become frozen when tagged)
| # | Path | Why | Frozen? | Scientific impact |
|---|---|---|---|---|
| 1 | `research/audit/PHASE0_DECISION_LOCK.md` | Lock the approved decisions, prohibited actions and frozen list | New; treat as locked (changes need a dated entry + approval) | None |
| 2 | `research/audit/PHASE0_CHANGE_MANIFEST.md` | This manifest | New | None |
| 3 | `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` | Single authoritative current source of verified facts | New; controlled (changelog + approval) | None (records existing evidence) |
| 4 | `research/audit/SCIENTIFIC_TRUTH_SUPERSESSION.md` | Statement-level supersession of the two older canonical files | New | None |
| 5 | `research/audit/PHASE0_ERRATA_ADDENDUM.md` | Approved scientific corrections (P0-1…P0-7, P1-11/13/14/15, plus one new concurrency-latency discrepancy) as new files; frozen documents unchanged | New | None to stored numbers; corrects wording/interpretation |
| 6 | `research/claims/CLAIM_REGISTRY.csv` | Claim registry skeleton with 43 rows (verified, historical, withdrawn, exploratory, pending only) | New | None |
| 7 | `research/claims/README.md` | Registry schema, status vocabulary, verification structure (claim → artifact → script → hash → environment) | New | None |
| 8 | `research/audit/X1_PROTOCOL_DRAFT.md` | Paper 1 protocol draft (X1-A/B/C/D, defect policy, mutation controls) | New draft; not registered | None (no execution) |
| 9 | `research/audit/X2_PROTOCOL_DRAFT.md` | Paper 2 protocol draft (X2-A/B/C) | New draft; not registered | None |
| 10 | `research/audit/X3_PROTOCOL_DRAFT.md` | Paper 3 protocol draft (X3-0/A/B, δ, m, X3-B trigger) | New draft; not registered | None |
| 11 | `research/audit/HUMAN_BENCHMARK_PROVENANCE_PLAN.md` | Record recovery, gates, ledger, independence controls | New | None |
| 12 | `research/audit/MODEL_PROVENANCE_REQUEST.md` | Draft trainer enquiry (not sent) | New | None |
| 13 | `research/audit/INSTITUTIONAL_ETHICS_ENQUIRY_DRAFT.md` | Draft institutional/venue enquiry (not sent) | New | None |
| 14 | `research/audit/ENVIRONMENT_LOCK_SPEC.md` | Environment-lock mechanism for new runs only (no lock created) | New | None |
| 15 | `research/audit/RUN_MANIFEST_SPEC.md` | Run-manifest format (no manifest created) | New | None |
| 16 | `research/audit/PREREGISTRATION_SPEC.md` | Git-tagged protocol structure + external-registration draft material (nothing submitted, no tag created) | New | None |

Additional documentation beyond the 14 listed items, added because it was strictly necessary: **#5** (the approved errata need a home that does not edit frozen files) and **#7** (the registry needs a schema/README).

**Added after this manifest was first written (closeout session):** `research/audit/PHASE0_CLOSEOUT_AUDIT.md` (static closeout audit; new, non-frozen). One mechanical sentence was added to `X1_PROTOCOL_DRAFT.md` §1 (computed PASS/FAIL), and this paragraph was added to the manifest. See the closeout audit §10 for the record.

## 2. Files modified
| Path | Status before | Change | Frozen? | Impact |
|---|---|---|---|---|
| `CLAUDE.md` (untracked at the start of Phase 0; a user-level project file created before this session) | Untracked; not in the frozen list | Four approved edits only: (a) Source-of-truth bullet 1: `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` is the sole current authority; root and handoff canonical files historical/superseded; registry pointer; (b) bullet 3: replaced "Human evidence is 1 rater, N=20 (rho 0.6975)" with the current human result (3 raters, 64 constructed answers to 8 questions, ρ 0.3812; exploratory/initial; ρ 0.6975 a superseded pilot; provenance incomplete; never "independent experts/committee/approved"); (c) new bullet: Paper 3 statistical unit is the persona; CrossEncoder is a partially fine-tuned derivative; (d) Experiments section: "statistical unit is the session, not the seed" corrected, and one line added: no experiment without a hashed, tagged protocol and an approved run manifest. All unrelated content preserved unchanged. | No | None |

Nothing else was modified.

## 3. Files deliberately NOT changed
`research/CANONICAL_SCIENTIFIC_TRUTH.md`; `research/CLAUDE_HANDOFF/*`; `research/papers/*`; everything under `research/results/`, `research/experiments/`, `research/scripts/`, `research/data/`, `research/annotation/`; every file in `research/audit/` created before Phase 0; `rl/checkpoints/*`; `ablation/results/*`; `experiments/*`; `services/**` (including `tuned_model2`); `agents/**`; `apps/**`; `requirements/*` and `.venv` (dependencies unchanged); `.env.example` (pre-existing user modification, untouched by Phase 0); `docs/PROJECT_STATE.md` (untouched); `paper/` (untouched).

## 4. Actions performed that are not file changes
- Read-only: hashing (SHA-256) of 366 frozen files before and after; `git rev-parse`; CSV reads; reading of source files.
- One-off documentation script (session scratchpad, **not** a project artifact): `gen_registry.py` hashed stored files, wrote `CLAIM_REGISTRY.csv`, and asserted the stored values cited by T2 rows (563, 232, 0.186, 0.677, 64 rows/8 questions/10 categories, ρ 0.3812, median 404.564, concurrency zeros). It executed **no** experiment or study script and imported no project code.
- No external contact, no network submission, no account creation, no Zotero change, no package installation.

## 5. Verification results (Phase-0 validation)
| Check | Result |
|---|---|
| SHA-256 of 366 frozen files (`research/CANONICAL_SCIENTIFIC_TRUTH.md`, `research/papers`, `research/results`, `research/CLAUDE_HANDOFF`, `research/audit` (pre-existing), `research/experiments`, `research/data`, `research/scripts`, `rl/checkpoints`, `ablation/results`, `experiments`) before vs after | **366 / 366 identical, 0 mismatches** |
| Key hashes unchanged | gold `363dbe6d…6ce2`; CrossEncoder `6a241a55…4450`; Paper 3 `frozen_config.yaml` `d3da2184…4d9e`; root canonical `d8ac0c0a…571a4a`; handoff canonical `7714dc16…dce9` — all match the pre-Phase-0 values |
| Tracked files modified | Only `.env.example` (pre-existing before this session; not touched in Phase 0) |
| New/untracked paths | Only the Phase-0 files in §1 plus pre-existing untracked items (see §6) |
| Experiment/study scripts executed | None (only the documentation script in §4; no results directory written) |
| Registry CSV | Parsed with `csv` (43 rows, 20 columns); static T2 assertions passed |
| Dependencies / `.venv` / `requirements/*` | `git diff -- requirements` empty; `git status` for `requirements/*.txt` shows only the pre-existing untracked `tracking.txt`; `.venv/pyvenv.cfg` last modified 2026-03-16 and `.venv/Lib/site-packages` last modified 2026-09-19 10:41, i.e. before the Phase-0 work began (the master plan was written at 21:13). No package was installed or changed |
| `git status` for `research/results`, `research/experiments`, `research/scripts`, `research/data`, `research/papers`, `research/CLAUDE_HANDOFF`, `research/annotation`, `rl`, `ablation`, `experiments`, `services`, `agents`, `apps` | No changes |

## 6. Pre-existing user changes vs Phase-0 changes (from `git status` at session start)
| Pre-existing (not Phase 0) | Phase 0 |
|---|---|
| `M .env.example`; `?? .serena/`; `?? docs/PROJECT_STATE.md`; `?? paper/`; `?? requirements/tracking.txt`; `?? CLAUDE.md` (untracked file, later edited by Phase 0 per §2); earlier audit files `?? research/audit/CLAUDE_*`, `P0_*`, `P0_P1_*`, `RESEARCH_STRENGTHENING_MASTER_PLAN.md` | The 16 files in §1 and the `CLAUDE.md` edit in §2 |

## 7. Open follow-ups (not Phase 0)
Phase 1 tasks require a separate instruction (see the final report). External sends (trainer, institution) are user actions. Any lock creation, `verify_claims` script, tag or manifest writer needs approval.
