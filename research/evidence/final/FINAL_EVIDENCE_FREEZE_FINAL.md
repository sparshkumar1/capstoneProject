# Final evidence freeze — 2026-09-20 (supersedes the provisional freeze `freeze/EVIDENCE/2026-09-20` in emphasis; that tag and its files are unchanged)

Tag: `freeze/EVIDENCE/FINAL-2026-09-20`. Machine-readable manifest: `research/evidence/final/FINAL_HASH_MANIFEST_FINAL.json` (SHA-256 of every listed artifact, all tags with object type and commit, branch and HEAD). The manifest is built by `build_manifest_final.py` (read-only). Nothing has been pushed; all tags are local and author-controlled. **Hash caveat:** each hash is of the working-tree bytes at freeze. Trees marked `-text` in `.gitattributes` (`research/confirmatory`, `research/analysis`, `research/tools`, `research/locks`, `research/claims`, …) keep raw bytes on checkout; documents elsewhere (e.g. `research/evidence`, `research/literature`, `agents/`, `services/`, `tests/`) are `text=auto`, so a CRLF checkout on Windows changes their byte hashes while the committed blobs stay LF.

## 1. What is frozen, by evidence class
| Class | Evidence | Status |
|---|---|---|
| **Registered primary (Paper 3)** | X3-A: Δ −0.0350 [−0.0818, +0.0021], Equivalent within ±0.12 (`prereg/X3-A/v1`, `freeze/X3-A/v1`) | Confirmatory *in the sense of a design fixed in a local tag before execution*; simulation only |
| **Registered secondary (Paper 3)** | O7 sensitivity (`prereg/X3-A-O7/v1` = `5217542e13f8c556a3e3b884e47299a6380b2128`, `freeze/X3-A-O7/v1` = `4bcb96949602a255569bd60e758173d21075d058`) | Secondary robustness evidence; does not replace the primary |
| **Engineering validation, build A (Paper 1)** | X1-C v1, X1-A v1, X1-B v2 (+ aborted v1 log) on `release/app-repair/v1` | Frozen record of the first build, including two defects and an under-powered invariance run |
| **Engineering validation, build B (Paper 1)** | X1-C v2, X1-A v2, X1-B v3 on `sut/X1/build-B` (`beb374f3…`) | Frozen; same agent designed, repaired and re-tested; independent review outstanding |
| **Exploratory (Paper 2)** | 64-case benchmark analyses (P2-*, X2A-*, X2B-*), category means (computed this sprint, descriptive) | Exploratory only; provenance/ethics records incomplete |
| **Preparation, not evidence** | X2-C protocol package, precision simulation (synthetic, unregistered), literature matrices, claim matrices, manuscript-preparation files | Planning artifacts |

**Which claims are confirmatory:** none of the human-rater claims. Only the Paper 3 primary and O7 have a design fixed before execution; the X1 protocols were also committed and tagged before their runs, but each v2/v3 rerun was written after the earlier results were seen, and all are self-registered and self-audited.

## 2. Experiments and work NOT completed
X2-C confirmatory human round (blocked: no institutional/ethics route, consent, rater provenance); X3-B (not triggered, not started); X1-A FLT-08 (WebSocket) and FLT-09 (audio) (not executed); X1-B2 behavioural stress (decision recorded in `X1_B2_DECISION.md`, not run); independent methodological review of X1; Elo/IRT/CAT baseline for Paper 3; verified reading of first-pass literature items labelled SN; edits to `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` (proposals only; needs user approval and changelog).

## 3. Commit / tag map added or used in this sprint
| Commit | Tag(s) | Content |
|---|---|---|
| `980747ff…` | `release/app-repair/v1` | build A (unchanged) |
| `beb374f3…` | `sut/X1/build-B` | build B repairs |
| `77cf3a57…` | `prereg/X1-C/v2`, `prereg/X1-A/v2` | v2 registration + method audit + defect decisions |
| `a9c6a209…` | `prereg/X1-B/v3` | v3 registration |
| `f66d8df7…` | `freeze/X1-C/v2`, `freeze/X1-A/v2`, `freeze/X1-B/v3` | v2/v3 results, run records, old-vs-new documents, B2 decision (10 committed result blobs re-checked against the run-record hashes: 0 mismatches) |
| the commit tagged `freeze/EVIDENCE/FINAL-2026-09-20` (it contains the manifest, whose `head` field is therefore its parent `f66d8df7…`) | `freeze/EVIDENCE/FINAL-2026-09-20` | claim matrices, literature files, audit, readiness, manuscript-preparation files, final manifest |
Earlier tags (`prereg/X3-A/v1`, `freeze/X3-A/v1`, `prereg/X3-A-O7/v1`, `freeze/X3-A-O7/v1`, `prereg/X1-*/v1`, `freeze/X1-*/v1`, `prereg/X1-B/v2`, `freeze/X1-B/v2`, `freeze/EVIDENCE/2026-09-20`, and all pre-sprint tags) are unmoved; the manifest lists each with its object type and commit.

## 4. Unchanged frozen data (verified at freeze)
`final_human_gold.csv` and other frozen research data, `rl/`, `ablation/`, `experiments/`, `research/results/`, `research/CLAUDE_HANDOFF/`, the registered O7 files, and every file in the provisional manifest (46 files) are byte-identical to their state before this sprint (re-hashed against `FINAL_HASH_MANIFEST.json`: 0 mismatches).

## 5. Environment manifest
- Engineering host: Windows 11, Docker Desktop (server 29.7.2, kernel 6.6.87.2-microsoft-standard-WSL2), sandbox image `sha256:1e8e861c…` (gcc 13.2.1 Alpine), Python 3.12 project `.venv` (pins violated: numpy 2.5.2, torch 2.11.0, accelerate 1.13.0 — registry X-C004), Qwen model `qwen2.5-1.5b-instruct-q4_k_m.gguf` (sha256 recorded in each X1-B `summary.json`).
- Paper 3 analyses: locked env `envs/LOCK-X3-2026-09-19` (Python 3.12.7, numpy 2.5.2, scipy 1.17.1; `research/locks/LOCK-X3-2026-09-19.lock.json`).
- Per-run environment records: `results/x1c*/environment_and_verdicts.json`, `run_records/*/RUN_RECORD.json`, `research/analysis/x3a_o7/run_record/O7_RUN_RECORD.json`.

## 6. Reproducibility instructions
- **X1-C / X1-A:** check out the registration commit named in the run record (HEAD must equal the tag commit), Docker Desktop with the local sandbox image loaded from `prepaired-c-sandbox.tar`, port 8001 free (X1-A), then `python research/confirmatory/X1/x1c_harness_v2.py --run --registered-commit <40-hex>` and the analogue for X1-A. Output directories are write-once. Timings are machine-dependent (registered SLAs are tight: FLT-01 margin ~0.1 s).
- **X1-B:** additionally the real Qwen GGUF model and the Qwen service started from the tagged code; generation is unseeded, so exact text is not reproducible, only the counts.
- **Paper 3:** locked env; `x3a_o7.py --registered-commit 5217542e13f8c556a3e3b884e47299a6380b2128` at HEAD equal to that tag commit; primary analysis data `research/confirmatory/X3-A/results/sessions.csv`. PPO retraining is not reproducible (unseeded candidate noise).
- **Paper 2:** frozen files and hashes only; no new human data exist.
- **Verification:** `python research/evidence/final/build_manifest_final.py` regenerates the manifest read-only; compare against the committed one.

## 7. Datasets
`research/data/evaluator_benchmark/final_human_gold.csv` (sha256 `363dbe6d…`; 64 author-constructed answers, 8 questions, three raters, incomplete provenance); `research/confirmatory/X3-A/results/sessions.csv` (simulated sessions); X1 result files (engineering observations).

## 8. Literature map, limitations, final tables/figures
Literature: `research/literature/FINAL_RESEARCH_POSITIONING.md`, `FINAL_REFERENCE_GAP_MATRIX.md` (Google literature tools not used). Limitations: per-paper matrices and `FINAL_LIMITATIONS.md` in `manuscript/paper*`. Tables: `manuscript/paper*/FINAL_RESULTS_TABLES.md`. Figures: plans only (`FINAL_FIGURE_PLAN.md`); no figure was generated.
