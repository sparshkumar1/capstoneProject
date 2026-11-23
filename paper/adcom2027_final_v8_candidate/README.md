# ADCOM 2027 manuscript package (multi-agent PREPAIred) — reproduction guide

Branch `research/adcom2027-multiagent-final` (local, not pushed). Frozen references, never modified: `cb888f2` (research snapshot), `54a5b73` (engineering freeze).
Superseded earlier ADCOM draft: `paper/adcom2027/` (kept for provenance; its corrections are Sect. 7 of this paper).

## Layout
- `manuscript/` LaTeX source (Springer `llncs`, `splncs04`), `refs.bib`, generated `numbers.tex`; `figures/` TikZ sources; `tables/` **generated** from results; `scripts/` generators and the blind audit; `verification/verify_paper.py` claim audit.
- Code: `agents/multiagent/` (contracts, authority, strategy_agent, coaching_agent, coaching_render, coordinator, arbitration, grounding, runtime) and the flag-gated hooks in `agents/orchestrator/interview_orchestrator.py`.
- Experiments: `research/multiagent/{configs,protocols,experiments,analysis,results}`; protocol `PROTOCOL_MA_XA_XB_v1.md`, git tag `prereg/MA-XA-XB/v1` (local).

## 1. Environment
Python 3.11 venv with numpy, scipy, pandas, torch, stable-baselines3, gymnasium, sentence-transformers, fastapi, httpx, pydantic>=2, pytest, pytest-asyncio; TeX Live with `llncs`, `latexmk`, `bibtex`, `poppler-utils` for the audits.
Note: the runs reported here used an environment outside the repository's pins (see `requirements/*.txt`; e.g. sentence-transformers 6.1.0 vs the pinned `<3.0.0`, numpy/torch newer than pinned). The explicit-activation loader makes score semantics independent of that.
The Qwen GGUF weights and the evaluator's LFS weights are **not** in the repository; no experiment here needs them (replay).

## 2. Tests
```
EVALUATOR_MOCK_MODE=1 python -m pytest -q tests
```
Observed on this branch: 409 passed, 15 skipped, 23 failed, 36 errors; the failing/erroring set (59 test identifiers) is identical to that of a clean export of the frozen commit 54a5b73, which gives 306 passed, 14 skipped, 23 failed, 36 errors (Docker sandbox, model downloads, one documented known failure), checked by comparing test IDs. Baseline before changes: 329 passed. Frontend: `cd apps/web && npm ci && npx vitest run` gives 28 passed. The historical 407-test baseline (363 unit + 16 integration + 28 frontend) was not reproduced as a whole: the Python failures above are environment-related, so no fully green run was obtained. Optional golden test: `PREPAIRED_CE_PATH=<dir with materialised tuned_model2> pytest tests/unit/test_evaluator_semantics_and_seam.py -k golden`.

## 3. Running the application
`python launch.py [--no-qwen|--no-frontend|--backend-only]`. Multi-agent mode is off by default; enable per session with config `{"multiagent_enabled": true, "multiagent": {...}}`; guardrail implementation with `{"guardrail_impl": "canonical"}` (default `legacy_inline`). Not exercised end to end in a browser here.

## 4. Experiments (commands; results are write-once)
```
export EVALUATOR_MOCK_MODE=1
python research/multiagent/experiments/xa_compare.py --out research/multiagent/results/xa
python research/multiagent/experiments/xb_faults.py  --out research/multiagent/results/xb
python research/multiagent/experiments/xd_grounding.py --out research/multiagent/results/xd
python research/multiagent/experiments/xe_historical.py --part e1   --out research/multiagent/results/xe_e1
python research/multiagent/experiments/xe_historical.py --part b503 --out research/multiagent/results/xe_b503
python research/multiagent/experiments/xe_historical.py --part e5   --out research/multiagent/results/xe_e5   # ~16 min, real timeouts
python research/multiagent/experiments/xc_threshold.py --out research/multiagent/results/xc      # protocol MA-XC v1, tag prereg/MA-XC/v1
python research/multiagent/analysis/analyze_xa.py research/multiagent/results/xa
python research/multiagent/analysis/analyze_xb.py research/multiagent/results/xb research/multiagent/results/xa
python research/multiagent/analysis/analyze_xc.py research/multiagent/results/xc research/multiagent/results/xa
python research/multiagent/analysis/independent_check.py research/multiagent/results research/multiagent/results/post_hoc/cluster_bootstrap.json   # independent recomputation + post hoc cluster bootstrap (results/post_hoc is write-once by convention)
```
Evidence classes: XA REPLAY; XB FAULT-INJECTED on replay; XC REPLAY (threshold decomposition); XD SYNTHETIC; XE e1 REPLAY (historical configuration), e5/b503 SOCKET. Latency numbers depend on the machine; counts do not.

## 5. Tables, figures, paper
```
python paper/adcom2027_final/scripts/make_authority_table.py
python paper/adcom2027_final/scripts/make_tables.py
cd paper/adcom2027_final/manuscript && latexmk -pdf main.tex
python paper/adcom2027_final/verification/verify_paper.py     # recomputes the paper's numbers from raw results
python paper/adcom2027_final/scripts/blind_audit.py           # identifying strings, markers, PDF metadata, fonts
```
## 5b. End-to-end audit tools
`research/multiagent/e2e/README.md` (real-server harness, scratch clone only); `research/multiagent/analysis/strategy_confidence_audit.py` (post hoc).

## 6. Known limitations
No live LLM, no human participants, constructed answers, replay candidate, dependent sessions, rule-based agents; local tags with no external timestamp; official ADCOM template/CFP not verifiable from the authoring environment (egress blocked); references verified through a search interface only. See Sect. 8 of the paper and `FINAL_AUDIT_REPORT.md`.
