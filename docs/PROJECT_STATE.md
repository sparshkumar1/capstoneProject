# Project State (tooling/infrastructure phase)

Recorded 2026-09-19 at branch `workspace/human-eval-clean-push`. This file records state and open decisions only;
scientific facts live in `research/CANONICAL_SCIENTIFIC_TRUTH.md`.

## FROZEN / AUDITED (do not modify)
- Paper 1, Paper 2, Paper 3 packages and results (`research/papers/*`, `research/results/paper3/*`, SHA-256 list in `research/CLAUDE_HANDOFF/PAPER3_FINAL_FREEZE.md`)
- `research/CANONICAL_SCIENTIFIC_TRUTH.md`
- `research/data/evaluator_benchmark/final_human_gold.csv`
- Existing validated experiment artifacts (`research/experiments/paper3/frozen_config.yaml`, `research/audit/*`, `research/CLAUDE_HANDOFF/*`, existing `experiments/*` results and figures)

## ACTIVE
- Engineering and experiment infrastructure (new configs/scripts go in new locations, never over frozen files)
- W&B integration for future runs (environment ready; no repository code uses it yet)
- AI tooling integration (Serena, Context7, Zotero MCP; GitHub MCP pending credentials)
- IEEE paper development in `paper/` (venue TBD)
- Environment reconciliation (see below)

## UNRESOLVED RESEARCH DECISIONS (intentionally not decided)
- Whether to add video/MediaPipe features
- Whether to replace Qwen with Mistral
- Whether to add ChromaDB (FAISS is currently used)
- Scope of company/domain transfer learning
- Reward methodology
- Interpretation of the failing Stage 11.5 test (`tests/unit/test_stage11_5_coding_adaptation.py::test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics`: `obs[4]` = 0.0, expected 0.22; cause unverified)
- Any other methodological change

## ENVIRONMENT RECONCILIATION ISSUE (`.venv` vs `requirements/`)
Checked with `importlib.metadata` against every `requirements/*.txt`. Only these packages violate their pins:

| File | Package | Pinned | Installed in `.venv` |
|---|---|---|---|
| `base.txt` | numpy | `>=1.26.0,<2.0.0` | 2.5.2 |
| `rl.txt`, `qwen.txt` | torch | `>=2.3.0,<2.7.0` | 2.11.0+cpu |
| `qwen.txt` | accelerate | `>=0.30.0,<1.0.0` | 1.13.0 |

Why it matters: CI installs the pinned versions, while local results and tests ran on the installed ones. Numerical behaviour,
PPO training and checkpoint loading may differ between the two, so a result reproduced under one environment is not guaranteed
under the other. Not changed in this phase. Safest next step: freeze the current `.venv` (`pip freeze` to a new file),
create a second venv from the pinned requirements, run the test suite in both, and only then decide whether to loosen the pins or
downgrade the `.venv`. Do not retrain or regenerate frozen results under either environment without an explicit decision.
