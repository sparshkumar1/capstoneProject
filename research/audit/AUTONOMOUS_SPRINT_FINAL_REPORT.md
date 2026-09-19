# Autonomous sprint - final report (2026-09-19)

## 1. Phases completed
| Phase | Status | Report |
|---|---|---|
| 1 Stored-data analyses (1A Paper 1; 1B X2-A; 1C X3-0a/b/c/d) | Complete; integrity PASS | `PHASE1_COMPLETION_REPORT.md` |
| 2 Protocols / preregistration / construction | **Partial by design** (X3-A, X2-B old-benchmark arm, X1-D finalized and tagged; X1-A/B/C, X2-C, X3-B not) | `PHASE2_COMPLETION_REPORT.md` |
| Hard confirmatory gate | Applied per experiment; passed for X3-A (15/15), X2-B (exploratory arm), X1-D | `research/preregistration/X3-A/HARD_GATE_CHECK.md` |
| 3 Confirmatory execution | X3-A, X2-B (old arm), X1-D executed | `PHASE3_EXECUTION_REPORT.md` |
| 4 Freeze + registry | Complete for the executed experiments | `PHASE4_FREEZE_REPORT.md` |
| 5 Adversarial readiness review | Complete | `FINAL_PUBLICATION_READINESS_REVIEW.md` |

## 2. Experiments actually executed
**X2-A** (exploratory sensitivity, old benchmark), **X3-0a/b/c/d** (stored/static/replay accounting), **Paper-1 stored analysis**, **X3-A** (confirmatory, pre-registered), **X2-B old-benchmark arm** (exploratory), **X1-D** (test report + latency). A manifest, protocol note or tag precedes each; none was rerun after inspection.

## 3. Experiments not executed (and why)
X3-B: trigger not fired (and D-N2 open). X2-C and the X2-B arm on X2-C: human/ethics gate. X1-A, X1-B, X1-C: construction not completed (needs dependency enumeration, injectors/mutants, prompt set, discriminating attack programs, oracles); Docker was available. No experiment was invented to fill time.

## 4. Blockers and open decisions (`SPRINT_DECISIONS_AND_BLOCKERS.md`)
D-N2 (X3-B training environment: candidate seeding, persona distribution, shield-in-loop), D-X2-TAU (X2-C false-accept rule, rho_min), D-F1 (supersession banners in four stale docs), D-HUMAN (institution, consent, provenance, trainer reply), D-X3B-OP (trigger operationalisation, for review). External/human: enquiries drafted and **not sent**; no rater contact; no ethics inference.

## 5. Result directories, tags, hashes
- `research/analysis/phase1/{paper1,x2_a,x3_0}/`; `research/confirmatory/{X3-A,X2-B,X1-D}/results/` (aborted attempts retained beside them); `research/locks/` (3 lock families); `envs/` (git-ignored: `replay-Lobs`, `LOCK-X3-2026-09-19`, `LOCK-X2-2026-09-19`).
- Tags (commit): `prereg/X3-A/v1` (`b00541f`), `prereg/X2-B/v1` (`51cd294`), `prereg/X2-B/v2` (`d84b913`), `prereg/X1-D/v1` and `sut/X1/build-A` (`3904749`), `freeze/X3-A/v1`, `freeze/X2-B/v1`, `freeze/X1-D/v1` (`dde2ddf`); frozen Paper 3: `v1.0-paper3-complete`. Result hashes: `research/analysis/RESULT_HASHES_phase3.txt`; per-artifact hashes in each manifest and in the registry. Nothing was pushed.

## 6. Claim-registry changes (43 -> 115 rows; VALID 58, WITHDRAWN 28, HISTORICAL 5, DESIGN-ONLY 9, EXPLORATORY 15)
`P3-C007/8/9` PENDING -> VALID (replay); `P2-C012` -> HISTORICAL (reproduced by X2A-C002/C006); `P1-C009` -> DESIGN-ONLY; new: `P1S-C001..041`, `X2A-C001..009`, `P3-C017..024`, `X3A-C001..007`, `X2B-C001..004`, `X1D-C001..003`. Status vocabulary extended (DESIGN-ONLY; PHASE1-* labels).

## 7. Negative and null results (preserved)
PPO+G is equivalent to Constant-Same+G (Delta -0.035 [-0.082, +0.002]) and more volatile; the shield did not improve Constant-Same tracking on the 40-persona grid; a length-only baseline matches the derived CrossEncoder on the old benchmark; the composite is not observed safer than R-only; the composite's cluster CI is wide [0.153, 0.649]; the Paper-1 fault, Qwen and 9/9 security tables are withdrawn; 1 of 226 tests fails.

## 8. Defects and deviations
Test-suite failure (known, unfixed by policy). Harness/process only: X3-A dry-run mutants invisible on the fixture (2 attempts), two concurrent launches (entry 2 corrects entry 1 in `DEVIATIONS.md`), X2-B manifest path defect (AMEND-001, tag v2). Analysis-level: none changed after data. Stated limitations: replay lock lacks wheel hashes; project `.venv` unlocked with pin conflicts; X2-B report header text says "v1" while the manifest records v2.

## 9. Integrity verification
Frozen baseline 366/366 identical (re-checked after every phase, last after X1-D); key hashes (gold, CrossEncoder, Paper-3 config, both seed-123 checkpoints) unchanged; 9 manifests completed, inputs/outputs re-hashed; registry T1 100 rows, T2 13/13 recomputations PASS. Tracked working-tree change: only the pre-existing `.env.example`. Project `.venv` not modified (no install, no bytecode). Pre-existing `__pycache__` under `research/scripts` and `rl` predate the sprint.

## 10. Tools actually used, and fallbacks
Read/Grep/Bash/PowerShell and Write/Edit (all code navigation used direct Read/Grep, **not** Serena: no need arose, nothing was unavailable); Git (commits, annotated tags, ancestry checks); `uv` (hash-pinned lock resolution and environment builds); SB3 2.7.1 / Gymnasium 0.29.1 / PyTorch 2.11.0+cpu in locked environments (evaluation only); scikit-learn/transformers/sentence-transformers in `LOCK-X2`; pytest/JUnit (X1-D); Docker only checked (daemon up, image present). **Not used:** W&B (no training), Context7 (SB3 API notes from the earlier readiness check were sufficient; no new API needed), Superpowers skills, claude-md-management, Zotero, Codex, Antigravity, Gemini/NotebookLM. Fallback: none required. Note: the sprint asks for a Codex audit after substantial implementation - **not done**; the new harnesses (`x3a_lib.py`, `x3a_run.py`, `x3a_analyze.py`, `x2b_run.py`, `x1d_run.py`, `run_manifest.py`) have had no independent code review.

## 11. Exact next action
1. **You (decision):** review `SPRINT_DECISIONS_AND_BLOCKERS.md` (D-N2, D-X2-TAU, D-F1, D-X3B-OP); send the drafted institutional and trainer enquiries if you agree.
2. **ChatGPT (methodology review):** the tagged protocols (`research/preregistration/{X3-A,X2-B,X1-D}/PROTOCOL.md`), the X3-A grid-persona generator and controller definition, and the readiness review.
3. **Codex/independent audit** of the new harness code before any further confirmatory run.
4. **Next experiment (if approved):** construct and tag X1-C first (Docker is available; the executor returns per-test stdout/exit codes so attack programs can self-report), then X1-B/X1-A; X2-C only after the institutional gate.
5. Manuscript drafting starts only after step 1-2 and only from VALID/EXPLORATORY registry rows with the wording in the readiness review.

STOP: no manuscript text was written; nothing external was sent.
