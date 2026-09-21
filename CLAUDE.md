# PrepAIred — Project Guide for Claude

Research capstone: multimodal technical-interview preparation with a guardrailed PPO difficulty controller.
Evidence over polish. Never invent results, citations, datasets or metrics, and never present a hypothesis as measured.
State: `docs/PROJECT_STATE.md` (frozen vs active vs unresolved decisions, environment mismatch). Do not resolve the listed open decisions unasked.

## Source of truth
- `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` is the sole current authority on verified metrics/formulas (edit only with a changelog entry and user approval). The older `research/CANONICAL_SCIENTIFIC_TRUTH.md` and `research/CLAUDE_HANDOFF/CANONICAL_SCIENTIFIC_TRUTH.md` are historical/superseded (see `research/audit/SCIENTIFIC_TRUTH_SUPERSESSION.md`); README badges and `docs/*` are also superseded. Claim wording/status: `research/claims/CLAIM_REGISTRY.csv`. Older reading order: `research/CLAUDE_RESEARCH_INDEX.md`, `research/audit/claim_audit.md`.
- Never cite superseded/synthetic numbers (rho 0.7400, 0.9152, 0.8358); see `research/audit/rho_provenance.md`.
- Current human result: 3 raters, 64 constructed answers to 8 questions, rho 0.3812 (case-bootstrap CI [0.158, 0.577]); exploratory/initial evidence only. rho 0.6975 (1 rater, N=20) is a superseded pilot, never the current human result. A new confirmatory benchmark is planned (`research/audit/X2_PROTOCOL_DRAFT.md`). Do not strengthen human evidence without new data. Rater provenance/ethics records are incomplete; never write "independent experts", "committee" or "approved".
- Paper 3 statistical unit is the persona (training seed as a second random factor; sessions and turns are descriptive only), not the session or the seed. The CrossEncoder is a partially fine-tuned derivative with incomplete provenance, not "off-the-shelf".

## Architecture (as it actually exists)
- `agents/orchestrator/interview_orchestrator.py`: hub for session state, question queue, follow-ups.
- `agents/audio/`: WhisperX/faster-whisper STT, prosody, confidence/hesitation. No video/MediaPipe.
- `services/evaluator/app.py`: `0.15*S1(SBERT) + 0.35*S2_eff(FAISS) + 0.50*R(CrossEncoder)`; S2 x0.6 when R<=0.30.
- `agents/coding_executor/`: Docker C sandbox. Feedback: local Qwen (not Mistral). Storage: SQLite `data/prepaired.db`. Backend `apps/backend`, UI `apps/web`.
- RL: `rl/env/interview_env.py`, `rl/training/simulated_candidate.py`, `rl/guardrails.py`; SB3 PPO. State 6-D in [0,1] (perf, avg_perf, confidence, hesitation, progress t/T, difficulty/5), action Discrete(3) easier/same/harder; spec in `research/audit/rl_state_definition.md`. Simulation-only evidence.
- Other dirs: `experiments/experiment_1..5` (legacy runners+results), `research/` (audits, papers, frozen results), `ablation/`, `scripts/`, `tests/`, `paper/` (new IEEE workspace).

## Commands (Windows; Python 3.12; venv `.venv`)
- Tests: `EVALUATOR_MOCK_MODE=1 .venv/Scripts/python.exe -m pytest -q` (full run ~6 min; run targeted tests first; one known failure, see gotchas).
- App: `python launch.py [--no-qwen|--no-frontend|--backend-only]`. Paper numbers: `scripts/reproduce_paper.py`.
- Deps: `requirements/*.txt`; CI: `.github/workflows/ci.yml` (installs pinned requirements).
- MCP CLI tools live in `~/.local/bin` (add to PATH in bash): `serena`, `uv`, `zotero-mcp`.

## Frozen-artifact protection
- Never edit, regenerate or delete: `research/CANONICAL_SCIENTIFIC_TRUTH.md`, `research/papers/*`, `research/results/paper3/*`, `research/CLAUDE_HANDOFF/*`, `research/audit/*`, `research/experiments/paper3/frozen_config.yaml`, `research/data/evaluator_benchmark/final_human_gold.csv`, `rl/checkpoints/*`, `ablation/results/*`, existing `experiments/*` results and figures. Hashes: `research/CLAUDE_HANDOFF/PAPER3_FINAL_FREEZE.md`.
- New work goes in new files/dirs. Do not change reward/state/action definitions or retrain PPO without explicit approval.

## Experiments, reproducibility, W&B
- Every experiment: config file (no hard-coded hyperparameters) + committed code + explicit seed + dataset version + stored results. Record the git commit with the run.
- Multiple PPO seeds, the same seed sets across comparable conditions, report variation. Paper 3 statistical unit is the persona (training seed is a second random factor); sessions/turns are descriptive only.
- No new experiment (X1/X2/X3) starts without a hashed, git-tagged protocol (`research/audit/PREREGISTRATION_SPEC.md`) and an approved run manifest (`research/audit/RUN_MANIFEST_SPEC.md`); nothing is changed after seeing results without registering a new experiment. Locked decisions: `research/audit/PHASE0_DECISION_LOCK.md`.
- W&B is ready but unused: `wandb` 0.30.0 in `.venv`, `wandb.integration.sb3` imports, logged in (`requirements/tracking.txt`, `WANDB_*` in `.env.example`). Never store the API key in the repo. Name runs like `ppo_full_seed42`; log config, seed, git commit and dataset version explicitly and configure checkpoint saving explicitly (W&B does not guarantee reproducibility by itself). Verify SB3 callback APIs with Context7. Do not attach W&B to frozen code.
- Never delete checkpoints/results without approval. Simulated-candidate results make no real-user claims.

## IEEE paper requirement
- The final paper must be prepared for IEEE-style submission. Target format: IEEE. Target venue: TBD.
- Workspace: `paper/` (see `paper/README.md`), separate from code and from frozen Paper 1/2/3. Use the venue's official IEEE template once chosen; do not invent page limits or submission rules.
- IEEE reference/figure/table/equation conventions. References only from Zotero or verified sources. Every number traces to stored evidence. Never make claims stronger than the evidence.
- The full composite evaluator correlates below R-only and S1+R; frame it as safety-hardened.

## AI tool division of labor
- Claude Code: primary builder. Serena: semantic code navigation (prefer over reading whole files). Context7: current library docs (SB3, Gymnasium, wandb, transformers). Superpowers: substantial multi-step features only. claude-md-management: keep this file concise.
- Zotero MCP (read-only local API): sources/citations. GitHub MCP: not configured yet (needs a PAT).
- Separate services, not connected to Claude: Gemini Pro (large-context triage), NotebookLM (source-grounded literature synthesis), ChatGPT Think (adversarial methodology/reviewer critique), Codex (independent code audit; Claude validates its findings before fixing), Antigravity (independent parallel work).
- Codex and Antigravity share the repo: never let two agents edit the same files at once; use separate branches/worktrees.
- Major architecture/experiment changes: state what/why/affected components/reproducibility impact and get approval first.

## Token/context rules
- Don't read the whole repo or `docs/` (large, partly superseded, e.g. `INTERVIEW_PREPARATION_GUIDE.md` ~75KB). Read targeted files/symbols.
- Ignore `orchestrator_logs/`, `scratch/`, `research/archive`, `docs/archive`, `apps/web/node_modules`, `prepaired-c-sandbox.tar`, `.venv`.
- Use subagents for broad investigations; keep implementation and paper sessions separate.

## Known gotchas
- Branch `workspace/human-eval-clean-push` is ahead of origin; default branch `main`; CI runs on `main` and `workspace/**`.
- `.venv` violates pins: numpy 2.5.2 (`<2`), torch 2.11.0 (`<2.7`), accelerate 1.13.0 (`<1.0`). Reconciliation is pending; do not change silently (details in `docs/PROJECT_STATE.md`).
- Known failing test (unresolved, not to be fixed until decided): `tests/unit/test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics` (`obs[4]` 0.0 vs expected 0.22). The last full run used `-x`, so tests after it were not run.
- README headline numbers and badges (e.g. "178 tests", "100% Traceable") can be stale; check the canonical doc.
- MCP servers (serena, zotero, context7) are registered in the user-level Claude config (local scope), not in the repo. Serena writes `.serena/` (cache is gitignored inside it).
