# Reproducibility statement
- Base commit `cb888f2`; work branch `adcom2027/multiagent`; protocol tags `prereg/ADCOM-E1-E3/v1`, `prereg/ADCOM-E4/v1`, `prereg/ADCOM-E5/v1` (local, not pushed; the tags give no external timestamp).
- Environment: `results/ENVIRONMENT.txt` (Python 3.11.15, numpy 2.4.6, torch 2.14.1, stable-baselines3 2.9.0; 4 CPU cores; no GPU). The repository's pinned requirements are not satisfied by this environment (as in the project's own development environment); results do not depend on a pin that was checked.
- Deterministic: E1, E3, E4 (replay; fault schedules from `numpy.random.default_rng(seed)`, seeds 0–19). Timing-dependent: E2, E5 (real sockets; medians depend on the machine).
- Inputs: `research/results/paper2/paper2_evaluator_raw.json` (recorded scorer outputs; sha256 in `results/RUN_LEDGER.md`), `research/data/evaluator_benchmark/benchmark_dataset.csv`, frozen PPO checkpoint shipped with the repository.
- Not executable here and therefore not part of any result: the scorer, the embedding models, the LLM, the Docker sandbox.
- Re-run: see `README.md` (commands). Numbers in the manuscript are macros generated from `results/*` by `verification/make_numbers.py`; `verification/verify_adcom.py` recomputes them independently.
