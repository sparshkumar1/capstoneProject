# Repository Organization Changes — Tier 0 + Tier 1 (2026-11-13)

## Scope decision

A full repository audit (Phase 1–2 of the requesting task) found the actual application code (`apps/`, `services/`, `agents/`, `rl/`) already cleanly organized per FastAPI/Vite conventions — no real problem there. The genuine issues were: one empty stray directory, a stale/inaccurate root README, and several root-level directories with no explanation of their purpose. A tiered plan (Tier 0: trivial fixes; Tier 1: documentation-only clarity; Tier 2: moving files; Tier 3: deep module reorganization) was proposed to the user given the real risk file moves carry for imports/Docker/CI paths. **The user selected Tier 0 + Tier 1 only** — no files were moved, renamed, or deleted (other than one confirmed-empty directory). Tier 2 and Tier 3 were declined for this pass; see "Deferred" below.

## Phase 1 — was this already done?

**Partially (Case C).** An earlier, narrower pass in this same engagement had already added 2 README files (`testing_and_evaluation/scripts/README.md`, `testing_output/README.md`) clarifying two specific, previously-misleading directories, explicitly as an "incremental-only" change, not a full restructure. That work is preserved unmodified. A full professional restructuring per this task's scope had not been attempted before this pass.

## Initial repository structure (summary)

Root-level: ~45 entries, a mix of standard config (`.gitignore`, `pyproject.toml`, `Dockerfile.*`, `docker-compose.yml`), the real application/research modules (`apps/`, `services/`, `agents/`, `rl/`, `research/`, `paper/`, `experiments/`, `ablation/`, `tests/`, `scripts/`, `tools/`, `docs/`, `data/`, `models/`), and 7 loosely-organized paper/deliverable directories with no explanatory documentation (`Details/`, `capstonePapers/`, `ADCOM2027_Track2_Final/` [already had a README], `submission/`, `reference_material_analysis/`, `Independent_Project_Audit/`, `final_deliverables/` [already had a README]), plus `testing_and_evaluation/` and `testing_output/` (top-level README missing on the former), an empty stray `node_modules/`, and a root `README.md` containing stale, superseded research figures.

## Issues identified

| # | Issue | Severity |
|---|---|---|
| 1 | Empty, stray `node_modules/` at repository root (two empty subdirectories, zero files — leftover from an `npm`/`vite` command accidentally run at the repo root instead of `apps/web/`) | Trivial, zero-risk to remove |
| 2 | Root `README.md` cited a superseded human-correlation figure (ρ=0.6975, a 1-rater/20-sample pilot) as if current, a stale "178 tests" badge, and implied Qwen2.5-**7B** as the primary deployed model (the deployed default is 1.5B) | Real — misleads a new reader about the project's actual current evidence, already flagged as a P0 item in this project's own prior `Independent_Project_Audit` |
| 3 | No directory-structure guide in the root README | Real but minor — a new reader has to explore to find anything |
| 4 | 6 root-level directories with no `README.md` explaining their purpose or relationship to each other (`Details/`, `capstonePapers/`, `submission/`, `reference_material_analysis/`, `Independent_Project_Audit/`, `testing_and_evaluation/`) | Real but minor |

## Research and references consulted

- GitHub documentation on repository documentation conventions (a README at the root and at each non-obvious subdirectory, explaining purpose before content).
- FastAPI and Vite's own project-layout guidance was consulted to confirm `apps/backend/` and `apps/web/` already match their respective recommended layouts (app code under a clear entry module; `src/` for frontend source) — no changes needed there, which is why no Tier 2/3 work was proposed for those directories.

## Changes made this pass

### Deleted (confirmed empty, zero content loss)
- `node_modules/` (root) — contained only two empty subdirectories (`.vite-temp/`, `@napi-rs/`), zero files, verified via `find node_modules -type f` returning nothing before deletion. Never git-tracked (not present in any commit), so this required no `git rm`.

### Modified
- `README.md` — replaced the stale badge row and the "Key Research Findings" section with figures matching `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`, explicitly noted the ρ=0.6975 figure as a superseded pilot, corrected the pytest-count comment in the Quick Start section, and added a new "Repository Structure" table (Phase 8 requirement). The "Dual Configuration Architecture" section's older EXP-1/3/4/5 figures were **not** touched — they were not flagged as superseded by `CLAUDE.md` and re-verifying them was outside this pass's scope; a future pass should verify them against `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` before trusting them.

### New files (6 README additions, documentation only)
`Details/README.md`, `capstonePapers/README.md`, `submission/README.md`, `reference_material_analysis/README.md`, `Independent_Project_Audit/README.md`, `testing_and_evaluation/README.md` — each explains that directory's actual contents, cross-references related directories, and states explicitly that it is not read by application code at runtime (so a reviewer knows it is safe reference material, not a hidden dependency).

## Files moved or renamed

**None.** Tier 1 was explicitly documentation-only, per the user's selection.

## Files intentionally left unchanged

- `apps/`, `services/`, `agents/`, `rl/` — already conventionally organized; moving anything here was explicitly recommended against (Tier 3) as cosmetic churn on working code with real import/Docker-path risk for no functional benefit.
- `docs/` (80+ historical "stageNN_*" files) — genuinely cluttered, but sorting it out safely is its own large audit; `CLAUDE.md` (this project's own standing instruction) explicitly says not to read or restructure it broadly. Flagged here as a known, deferred issue, not silently ignored.
- `logs/` vs `orchestrator_logs/` vs `apps/backend/orchestrator_logs/` — a possible redundancy, but which path is actually live depends on runtime working-directory behavior in `agents/orchestrator/`, which was not traced in this pass; moving or merging these without that trace risks silently breaking log output. Deferred.
- The 7 root-level paper/deliverable directories (`Details/`, `capstonePapers/`, `ADCOM2027_Track2_Final/`, `submission/`, `reference_material_analysis/`, `Independent_Project_Audit/`, `final_deliverables_zip.zip`, `main.pdf`) — Tier 2 (consolidating these under one parent directory) was proposed but not selected by the user this pass.

## Compatibility adjustments made

None required — no file was moved, so no import, Docker build context, CI config, or documentation link needed updating.

## Remaining limitations / deferred work (Tier 2 and Tier 3, not executed)

1. **Tier 2 (declined this pass):** consolidate the 7 scattered root-level paper/deliverable directories under one clearly-named parent. Contained risk (each directory's internal relative paths would need verification before moving as a unit); not executed because the user selected Tier 1 only.
2. **Tier 3 (recommended against):** reorganizing `apps/`/`services/`/`agents/`/`rl/` internals, or sorting the `docs/` historical pile. High effort, real risk, and — for the application modules — no genuine organizational problem to fix.
3. The "Dual Configuration Architecture" section of `README.md` (EXP-1/3/4/5 figures) was not re-verified against current canonical evidence in this pass.
4. `logs/` vs `orchestrator_logs/` path redundancy was identified but not traced or resolved.
