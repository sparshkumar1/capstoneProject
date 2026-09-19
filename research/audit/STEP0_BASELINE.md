# PREPAIred Step 0 Baseline

Date/time: 2026-09-19 11:30:40 IST
Repository root: C:/Users/spars/Downloads/PrepAIred
Branch: workspace/human-eval-clean-push
HEAD BEFORE CHECKPOINT: 9cfd34f278de8cc6b2810a4855b571b6b7264495

## Git status

### Summary:
- Modified files: 34
  - Product & UI: `apps/web/src/FeedbackCard.jsx`, `apps/web/src/InterviewRoom.jsx`, `apps/web/src/InterviewerAvatar.jsx`, `apps/web/src/InterviewerAvatar.css`, `apps/web/src/__tests__/ui_fixes.test.jsx`, `services/qwen/app.py`, `tests/unit/test_qwen_specific_feedback.py`
  - Config: `.gitignore`
  - Documentation & Archival Banners: `INTERVIEW_PREPARATION_GUIDE.md`, `docs/paper_draft_ieee.md`, and 26 milestone docs in `docs/`
- Tracked deleted files: 28
  - Archived to `research/archive/` and `research/papers/archived/` (`submission/` package, old monolithic paper drafts, outdated summary markdown files)
- Untracked research artifacts:
  - Canonical truth & index: `research/CANONICAL_SCIENTIFIC_TRUTH.md`, `research/CLAUDE_RESEARCH_INDEX.md`, `research/PLAN.md`, `research/README.md`
  - Directories: `research/annotation/`, `research/archive/`, `research/audit/`, `research/data/`, `research/experiments/`, `research/figures/`, `research/papers/`, `research/prompts/`, `research/raw/`, `research/reproducibility/`, `research/results/`, `research/scripts/`, `research/tables/`
  - Baseline records: `research_baseline_20260919_111311.txt` (local temporary record at repository root)

## Existing tests

### Backend:
Command: `pytest tests/`
Result: `204 passed, 1 skipped, 4 warnings in 383.87s` (100% pass rate of active tests)
- 0 failures
- 1 expected skip (`test_whisperx_dependency_gated_execution` - optional CPU dependency gate)

### Frontend:
Command: `npm run test:ci` (in `apps/web`)
Result: `20 passed in 5.39s` (2 test suites, 20 test cases, 100% pass rate)

### Frontend build:
Command: `npm run build` (in `apps/web`)
Result: `vite build` completed successfully in 999ms with zero errors. All chunks rendered cleanly.

## Research package

Present: YES
- 217 total files across 16 subdirectories in `research/`
- Full 5-priority research validation artifacts, multi-seed PPO checkpoints (seeds 42, 123, 456, 789, 999), 64-case human evaluation benchmark, fault injection and latency benchmarks, and publication outlines.

## Critical files verified

All confirmed present in both local repository and backup:
- [x] `research/CANONICAL_SCIENTIFIC_TRUTH.md`
- [x] `research/CLAUDE_RESEARCH_INDEX.md`
- [x] `research/PLAN.md`
- [x] `research/audit/`
- [x] `research/annotation/`
- [x] `research/data/`
- [x] `research/experiments/`
- [x] `research/papers/`
- [x] `research/reproducibility/`
- [x] `apps/`
- [x] `services/`
- [x] `tests/`

## Backup

Backup path: `C:\Users\spars\Downloads\PREPAIred_STEP0_BACKUP_20260919_111311`
Backup verification: Robocopy exit code 1 (success), all critical paths verified via `Test-Path` returning `True`.
Backup timestamp: `20260919_111311`
Backup supplementary artifacts:
- `tracked_worktree_changes.patch` (2,529,353 bytes)
- `untracked_files.txt` (9,430 bytes)
- `git_status.txt` (3,754 bytes)
- `prepaired-c-sandbox.tar` (66,174,464 bytes)

## Notes
- `prepaired-c-sandbox.tar` (66,174,464 bytes, 2026-08-31) was identified as a historical Docker sandbox image export. It is preserved intact on disk and in the external backup, and ignored by Git via `*.tar` in `.gitignore`.
- Git whitespace check (`git diff --check`) noted trailing whitespace in historical documentation headers added during documentation disclaimer tagging; preserved as-is per instructions.
- No secrets, credentials, tokens, or private keys exist in tracked or untracked file sets.
