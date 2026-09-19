# Complete Research Artifact End-to-End Traceability & Provenance Map

**Audited Commit:** `9cfd34f`  
**Standard:** Every figure, table, and number in all three target papers must map cleanly back to an execution script, raw machine output, and primary data input.

---

## 1. End-to-End Artifact Traceability Pipeline

```
Primary Input Data & Checkpoints
           ¦
           ?
Reproducible Experiment Script (`research/scripts/`)
           ¦
           ?
Raw Machine-Readable JSON Output (`research/raw/`)
           +--? Markdown Publication Table (`research/tables/`)
           +--? High-Resolution Publication Figure (`research/figures/`)
                     ¦
                     ?
             Target Paper Manuscript (`research/papers/`)
```

---

## 2. Complete Traceability Registry

| Exp ID | Primary Raw Inputs | Execution Script | Raw JSON Output | Formatted Result Table | Result Figure | Target Paper |
|:---:|:---|:---|:---|:---|:---|:---:|
| **EXP-EVAL-1** | `ablation/results/ratings_rater1.csv`, `ratings_proxy.csv`, `ratings_averaged.csv` | `research/scripts/run_evaluator_experiments.py` | `research/raw/eval_ablation_raw.json` | `research/tables/table_eval_ablation.md` | `research/figures/eval_ablation_comparison.png` | **Paper 2** (ICTCS 2026) |
| **EXP-EVAL-2** | `data/rubrics/rubrics_final_clean.json`, `services/evaluator/assets/` | `research/scripts/run_evaluator_experiments.py` | `research/raw/eval_adversarial_raw.json` | `research/tables/table_eval_adversarial.md` | n/a | **Paper 2** (ICTCS 2026) |
| **EXP-EVAL-3** | `logic_vectors.faiss`, `logic_metadata.pkl` | `research/scripts/run_evaluator_experiments.py` | `research/raw/eval_threshold_raw.json` | `research/tables/table_eval_threshold.md` | `research/figures/eval_threshold_sensitivity.png` | **Paper 2** (ICTCS 2026) |
| **EXP-EVAL-4** | Evaluator grade predictions vs labels | `research/scripts/run_evaluator_experiments.py` | `research/raw/eval_error_analysis_raw.json` | `research/tables/table_eval_error_analysis.md` | n/a | **Paper 2** (ICTCS 2026) |
| **EXP-EVAL-5** | `research/data/evaluator_benchmark/benchmark_cases.json` | `research/scripts/run_metamorphic_tests.py` | `research/raw/metamorphic_raw.json` (`results/metamorphic_tests.csv`) | `research/tables/metamorphic_results.md` | n/a | **Paper 2** (ICTCS 2026) |
| **EXP-RL-1** | `rl/checkpoints/seed_123/ppo_final.zip`, `vecnormalize.pkl` | `research/scripts/run_rl_experiments.py` | `research/raw/rl_policy_comparison_raw.json` | `research/tables/table_rl_policy_comparison.md` | `research/figures/rl_trajectory_comparison.png` | **Paper 3** (SmartCom 2027) |
| **EXP-RL-2** | Simulated candidate trajectories under alternate dim4 modes | `research/scripts/run_rl_experiments.py` | `research/raw/rl_dim4_impact_raw.json` | `research/tables/table_rl_dim4_analysis.md` | n/a | **Paper 3** (SmartCom 2027) |
| **EXP-RL-3** | Candidate audio prosody simulator + Gaussian acoustic noise | `research/scripts/run_rl_experiments.py` | `research/raw/rl_state_ablation_raw.json` | `research/tables/table_rl_speech_perturbation.md` | `research/figures/rl_speech_perturbation_stability.png` | **Paper 3** (SmartCom 2027) |
| **EXP-SYS-1** | `prepaired-c-sandbox:latest`, `agents/coding_executor/` | `research/scripts/run_systems_experiments.py` | `research/raw/sys_security_raw.json` | `research/tables/table_sys_security_boundary.md` | n/a | **Paper 1** (ATIS 2026) |
| **EXP-SYS-2** | Live subsystem instances (50 iterations each) | `research/scripts/run_systems_experiments.py` | `research/raw/sys_latency_benchmark_raw.json` | `research/tables/table_sys_latency_benchmark.md` | `research/figures/sys_subsystem_latency.png` | **Paper 1** (ATIS 2026) |
| **EXP-SYS-3** | Orchestrator full turn pipeline with component toggles | `research/scripts/run_systems_experiments.py` | `research/raw/sys_arch_ablation_raw.json` | `research/tables/table_sys_architectural_ablation.md` | n/a | **Paper 1** (ATIS 2026) |
| **EXP-LLM-1** | Adversarial / empty evaluator inputs to FeedbackAgent | `research/scripts/run_systems_experiments.py` | `research/raw/llm_grounding_raw.json` | `research/tables/table_llm_adversarial_grounding.md` | n/a | **Paper 1** (ATIS 2026) |
