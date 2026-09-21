# 5-Hour Execution Report — 2026-09-20

Executor: Claude. HEAD `1ca0faa` (branch `workspace/human-eval-clean-push`); no commit, tag or push was made. Nothing frozen was touched.

## Headline
Literature/positioning phases (0–3, 7-prep, 9) were completed. **Every phase that needed an independent Codex review or a registered protocol tag was stopped at its gate**, per the stop rules: O7 (Phase 4), the run-manifest audit (Phase 5) and the X1 campaign (Phase 6) were **not run**. The demo (Phase 8) was verified in software; hardware/live-browser items were not. No experiment produced a new scientific result today.

## 1. Files created
| File | SHA-256 (first 16) |
|---|---|
| `research/literature/ALTERNATIVE_PAPER_POSITIONING.md` (Phase 0) | 154a5d5db07757ce |
| `research/literature/SECOND_PASS_CLAIM_AUDIT.md` (Phases 1–2) | 54c997b12adedf06 |
| `research/literature/FINAL_RESEARCH_POSITIONING.md` (Phase 3) | e65a165ce99329d7 |
| `research/evidence/PAPER3_EVIDENCE_PACKAGE.md` | 8b6ce0d3e6c06b00 |
| `research/evidence/PAPER1_EVIDENCE_PACKAGE.md` | 27d094bc6e4758f9 |
| `research/evidence/PAPER2_X2C_PROTOCOL_PACKAGE.md` | 3d3ef9e17ed6059a |
| `research/audit/FINAL_THREE_PAPER_CLAIM_MAP.md` (Phase 9) | 234374c70dbc78b3 |
| `research/analysis/x3a_o7/x3a_o7.py` (O7 implementation, not run on frozen data) | da66bd38477ae6dd… (full: da66bd38477ae6dda27451b25a5791ef542f48ffd3c4fb2d55de13da05459c11) |
| `research/tools/run_manifest_v2.py` | c98251dda6ef8955… (full: c98251dda6ef8955d3da215a630177409030255167201f795f3d41425343aae5) |
| this report | — |
(Earlier in the session: `LITERATURE_NOVELTY_MASTER_MATRIX.md`, audit/plan/spec files.)

## 2. Files modified
None tracked by this block. (`.env.example` was modified before the block.) Runtime side effects outside git: `data/prepaired.db` (gitignored) received a test candidate `verify_block_20260920` (`verify.block@example.invalid`) and attempt rows from the e2e scripts; `apps/web/dist/` was rebuilt (gitignored).

## 3. Left unchanged intentionally
`research/tools/run_manifest.py` (legacy; SHA-256 still `5f6283cbe73446e7fd7da885321c6350da6e0e66266120cf5e1e28c4ef6fed91`), all X3-A/X2-B/X1-D harnesses and results, protocols, tags, `frozen_config.yaml`, checkpoints, `X2_PROTOCOL_DRAFT.md`, `X1_PROTOCOL_DRAFT.md`, stale README/docs, the failing test and the e2e scripts that share its assumption.

## 4. Literature verified in depth (second pass; text read this session)
APAC/Docker (Spacek 2015, whole); SandboxEval (2025 preprint; intro, test suite, Dyff evaluation, results); Riedmann 2025 (IJAIED review; abstract, methods, evaluation, baselines, discussion); Ion 2025 (PMLR; whole); Axak 2025 (CEUR; environment, training, evaluation, conclusion); Olukola & Rahimi 2026 (both preprints; conditions/ablations/safety-gap sections); Carr 2023 (results discussion); Alshiekh 2018 (framework); CodeGENCAT 2026 (introduction/datasets); Mohler 2009/2011 (dataset/evaluation); Li 2026 and Sahoo 2026 (threat-model/defence sections); Cai 2026 (PMC abstract page). Not readable (403/redirect) or not re-read: Hickman & Bell 2024, several Springer/ScienceDirect items — their status is unchanged (metadata/search-level).

## 5. Unresolved literature questions
Graceful degradation of AI-assisted assessment (P1-3); paraphrase testing, question-level clustering and uncertainty in ASAG (P2-4/5/6); technical-interview answer benchmarks (P2-8, only "not identified in the searches conducted"); other adaptive coding-interview systems and IRT/Elo baselines (P3-1/4); equivalence-margin justification and RL-evaluation-methodology literature; reproducibility/preregistration literature (portfolio G); rest of SandboxEval; multi-seed reporting frequency in educational RL.

## 6. Alternative positioning results
Five required portfolios plus F (two-paper), G (process paper), H (length-confound P2) analysed with compatibility statuses, no scores. Summary: measurement/evaluation-centered (B) and empirical-methodology-centered (E) are the framings the stored evidence supports (P2 and P3 clearly compatible; P1 conditional on X1-C/B); systems-centered (A) viable for P1 only with X1 evidence; "trustworthy AI" (C) and "reliable adaptive technical assessment" as an achievement (D) are incompatible with current evidence, viable at most as research questions.

## 7. Positioning decisions supported by evidence
No "trustworthy", "reliable" (achievement), formal "shield", "novel/first"; Paper 3 as decomposition of learned-policy vs constraint-layer benefit (equivalence, higher volatility); Paper 2 as a diagnostic, not architecture-improvement; Paper 1 claims held until X1 evidence. Four hypotheses were **killed or weakened** by the second pass: "negative control is new in assessment sandboxing" (SandboxEval reports an uncontained comparison), "policy-vs-constraint separation is uncommon" (Carr 2023 shielded-random reference; Olukola ablations), "PPO vs heuristic as a contribution" (Axak 2025), "composite improves evaluation" (own registry).

## 8. Positioning decisions still open
P1 systems vs measurement-design; P2+P3 consolidation; a process/reproducibility paper; feasibility of X2-C; venue choice (no venue was selected).

## 9. Experiments actually run
None on frozen data. Run today: (a) O7 script mechanics self-test on **synthetic** data (passed; no official output); (b) `run_manifest_v2.py --selftest` in a temporary git repository (passed); (c) full backend test suite; (d) frontend tests and build; (e) three scripted demo verifications (details §11).

## 10. Experiments intentionally NOT run, with reason
| Item | Reason (gate) |
|---|---|
| **O7 R0/A/B/C** | Spec §8 (1b): independent code review by Codex required before running — **no Codex access from this session**; (2) script/spec not hashed+tagged (no commit/tag authorised). Nothing was approximated. R0 remains a hard gate |
| **X1-C, X1-B, X1-A** | No registered protocol tags; `run_manifest_v2` not independently audited; no recorded decision on the known failing test; no independent review of the corrected X1 designs |
| **X2-C / precision simulation** | Institutional/ethics gate unresolved; no human data may be created; simulation code not yet written/hashed |
| **X3-B, PPO training, tuning, second simulator, persona generator** | Prohibited/out of scope |

## 11. Exact results obtained today
**Backend suite** (`EVALUATOR_MOCK_MODE=1 .venv/Scripts/python.exe -m pytest -q`): 226 tests → **225 passed, 1 failed** in 404 s. The failure is the known `tests/unit/test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics` (identical to X1D-C001). Real Qwen inference tests ran and passed in this suite.
**Frontend**: `vitest run` 20/20 tests passed (2 files); `vite build` succeeded (index JS 107 kB; ~1.3 s).
**`verify_stage11_6_full_interview_e2e.py`** (in-process, real evaluator, real WhisperX on `tests/test_candidate_hash_table_answer.wav`, real Qwen follow-up, PPO seed_123, Docker C sandbox): Steps 1–9 OK — WhisperX transcript (12.5 s audio, confidence 0.821), evaluator score 0.0 for that fixture (a hash-table answer to a two-sum question; a fixture mismatch, not a scoring claim), Qwen follow-up generated, PPO loaded (dim 6, 3 actions), correct C code accepted (score 1.0; test execution 578 ms), partial code `wrong_answer` (pass rate 0.5), compile error classified. **Step 10 FAILED** on `assert post_code_obs[4] == st_post_code.get("last_time_norm", 0.0)` — the same root cause as the failing unit test (observation dimension 4 became turn progress in commit `b7cad49`); the script's assertion is stale relative to the deployed observation. It is **not demo-blocking** (the printed post-coding observation was `[1, 0.5, 0.5, 0.5, 0.0, 0.4]`). The legacy script was **not** edited.
**`verify_persistence_and_retries_e2e.py`**: all invariants PASS (3 attempts persisted in SQLite; best attempt logic; candidate data isolation; follow-up decoupled from the primary question).
**Live services** (`launch.py --backend-only --no-qwen`): evaluator (port 5000) and backend (port 8000) healthy within ≤ 6 s; login, session creation, `run_code` and end-session worked; Docker returned compile-error diagnostics for bad code; no orphan containers afterwards. Timings measured through `localhost` include a resolver overhead (~0.2–2 s per call; `127.0.0.1` health 2 ms), so per-call figures (~3.1 s for `run_code`, ~2 s for others) **overstate** service time and are not reported as latency claims.
**Observations recorded (not fixed):**
1. **Restart persistence is partial**: candidate identity and attempts survive a backend restart (SQLite), but **sessions and final reports do not** — `SESSIONS` and `REPORTS` are in-memory dictionaries (`apps/backend/main.py:275-276`); after restarting, `GET /api/sessions/{id}` and `GET /api/reports/{id}` returned 404 for an ended session.
2. `POST /api/run_code` with a session that has no active coding question returned `status: accepted, passed: true, tests_total: 0` for a well-formed program **and** for an infinite-loop program; with zero tests the result is vacuous. It occurs outside the normal flow (coding question active) but is relevant to X1 oracle design (executor status must never be the sole oracle).
3. `num_questions=2` was requested but the session reported 15.
**Not verified**: live microphone/browser permission (hardware); live browser UI flow (no browser session was driven); Qwen-off and Docker-off recovery as *manual* service-kill checks (the backend was run with `--no-qwen`, and Docker was not stopped; recovery paths are covered only by the unit/integration tests that passed); per-turn Qwen cold-load timing (not captured); frontend lint (not run).

## 12. Environment versions
Windows 11 Home; project `.venv` Python 3.12 (violates pins: numpy 2.5.2, torch 2.11.0, accelerate 1.13.0 — unchanged); Docker Server 29.7.2, image `prepaired-c-sandbox:latest` 238 MB; Node/vitest 2.1.9; locked X3 environment `envs/LOCK-X3-2026-09-19` (Python 3.12.7, numpy 2.5.2, scipy 1.17.1) — **not used today**. Qwen `models/gguf/qwen2.5-1.5b-instruct-q4_k_m.gguf`.

## 13. Hashes / tags / manifests
No new tag or manifest was created. Existing tags unchanged (`prereg/X1-D/v1`, `prereg/X2-B/v1`, `prereg/X2-B/v2`, `prereg/X3-A/v1`, `sut/X1/build-A`, `freeze/*`, `v1.0-paper3-complete`). File hashes: §1. X3-A input `sessions.csv` `dd7eb669e1ffc60957f254e330185d69edf276d578b0b0029efdcf3880f1bcd8` (not read by any script today except the header/keys inspection needed to write O7 code; no statistic was computed).

## 14–15. Tests passed / failed
Passed: backend 225; frontend 20; O7 self-test; `run_manifest_v2` self-test; persistence/retry e2e. Failed: the known unit test; e2e Step 10 (same cause).

## 16. Known infrastructure limitations
`run_manifest_v2.py` limits (recorded in every manifest): package inventory by distribution metadata, not per-file hashes; tag annotation trusted as the registration record; no protection against local tampering after completion. It has **not** been independently audited. It requires an annotated tag whose message contains the protocol's SHA-256, and byte-identical files at the tag (CRLF conversion by git autocrlf will cause an intentional mismatch). Legacy harness weaknesses (Codex findings) remain for frozen runs and are disclosed, not fixed.

## 17. Scientific blockers remaining
(1) Independent review of the O7 code and the manifest v2 tool; (2) registered X1-C/B/A protocols; (3) decision on the known failing test and on stale e2e/unit assertions; (4) institutional/ethics pathway for X2-C; (5) unresolved literature questions (§5); (6) length-only baseline versus learned components on an independently authored benchmark; (7) simulator validity for Paper 3 is outside this study's evidence.

## 18. Next exact action
1. **Run the independent Codex review** (read-only) on two files, then return the report for validation: `research/analysis/x3a_o7/x3a_o7.py` against `research/audit/X3A_O7_SENSITIVITY_SPEC.md` (checklist: no import/reuse of `x3a_analyze.py` family; draw order persona-then-seed from a fresh `default_rng(42)`; persona string-sort and numeric seed order; CSV float parsing and row order; `numpy.percentile` linear; environment/version/hash assertions; full input hash; target values read only after R0; R0 hard gate at 1e-12; fresh RNG per analysis; B = t interval with df = 4; key-set and duplicate assertions; expected persona/seed sets; no extra analyses; write-once outputs) and `research/tools/run_manifest_v2.py` against the six blocking findings in `CODEX_FINDINGS_VALIDATION.md`.
2. If Codex finds genuine issues, Claude fixes only those O7/v2 files and the review is repeated.
3. On the user's instruction: commit the O7 script + spec, create the annotated tag, and run the O7 script once in the locked environment (`envs/LOCK-X3-2026-09-19/Scripts/python.exe research/analysis/x3a_o7/x3a_o7.py`); a failed R0 stops everything.
4. In parallel the user can decide the failing test and approve X1-C/B/A protocol registration.

**Self-review note (not independent):** before stopping, I walked the O7 script through the Codex checklist above and found each item implemented as specified; this does not replace the independent review the spec requires.
