# PREPAIred — Master Research Validation & Publication Plan

**Target Venues:**
- **Paper 1 (Systems & Security):** *ATIS 2026* (Bengaluru) / *IEEE Access*
- **Paper 2 (Evaluator & Scoring):** *ICTCS 2026* (Ahmedabad) / *IEEE Transactions on Education (ToE)*
- **Paper 3 (RL Adaptive Pacing):** *SmartCom 2027* (Goa) / *ICMLSC 2027*

---

## 1. Research Objectives & Principles
1. **Repository as Ground Truth:** All claims, numbers, and tables must be generated from verifiable code and data artifacts in this repository.
2. **Zero Fabrication:** Never invent human participants, survey responses, or unrun benchmarks. Differentiate authentic human pilot ratings (=20$, single educator) from synthetic LLM proxies.
3. **Defense-in-Depth:** Systems security must be proven with empirical negative testing against the isolated container sandbox.
4. **Clean Decoupling:** The 3 target papers must have disjoint contributions, unique figures, distinct tables, and independent experimental baselines.

---

## 2. Priority Roadmap

| Priority | Area | Key Artifacts | Status |
|---|---|---|---|
| **Priority 0** | Baseline & Reconciliation | engineering_tests.json, current_test_manifest.md, claim_audit.md, historical_results_reconciliation.md, equation_code_audit.md | **COMPLETED** |
| **Priority 1** | Benchmark Foundation | dataset_inventory.md, data_leakage_report.md, 
esearch/annotation/, nalyze_human_ratings.py | **IN PROGRESS** |
| **Priority 2** | Evaluator Core Validation | 	able_eval_ablation.md, 	able_eval_adversarial.md, 	able_eval_threshold.md, 	able_eval_error_analysis.md | **COMPLETED** |
| **Priority 3** | Metamorphic Robustness | 
un_metamorphic_tests.py, metamorphic_tests.csv, metamorphic_results.md | **TO DO** |
| **Priority 4** | Grounding & Fallback | 	able_llm_adversarial_grounding.md, llm_grounding_raw.json | **COMPLETED** |
| **Priority 5** | RL State & Training Audit | 
l_state_alignment.md, 	able_rl_dim4_analysis.md | **IN PROGRESS** |
| **Priority 6** | RL Empirical Evaluation | 	able_rl_policy_comparison.md, 	able_rl_speech_perturbation.md, 	able_rl_guardrails.md | **COMPLETED** |
| **Priority 7** | Sandbox Security Testing | 	able_sys_security_boundary.md, 	hreat_model.md | **IN PROGRESS** |
| **Priority 8** | Systems Latency & Reliability| 	able_sys_latency_benchmark.md, 	able_sys_architectural_ablation.md, ailure_matrix.md | **COMPLETED** |
| **Priority 9** | Privacy & Ethics | speech_ethics.md, privacy_data_flow.md | **IN PROGRESS** |
| **Priority 10**| Reproducibility Package | environment_manifest.json, paper_{1,2,3}_reproduce.md | **TO DO** |
| **Priority 11**| Paper Manuscripts | 
esearch/papers/paper{1,2,3}/ structure & overlap matrix | **IN PROGRESS** |
| **Priority 12**| Peer Review Simulation | 
eviewer_simulation.md (Reviewers A, B, C, D) | **TO DO** |

---

## 3. Detailed Execution Matrix

### Paper 1: Systems Architecture & Sandbox Security (ATIS 2026)
- **Contribution:** Decoupled multimodal architecture with Socratic follow-up state machine, sub-millisecond scoring dispatch, and containerized C execution sandbox.
- **Empirical Assets:**
  - 9-vector security negative testing matrix (SEC-01 to SEC-09).
  - 50-iteration subsystem latency profiling (Audio, Evaluator, PPO, Sandbox, SQLite WAL).
  - Single-component removal resilience study (ARCH-01 to ARCH-06).

### Paper 2: Multi-Signal Technical Evaluation (ICTCS 2026)
- **Contribution:** Grounded multi-signal evaluation combining semantic similarity ($), FAISS rubric concept coverage ($), and CrossEncoder reasoning entailment ($) with reasoning-conditioned concept dampening.
- **Empirical Assets:**
  - 7-way ablation across Pilot Human (=20$), Synthetic Proxy (=20$), and Averaged (=20$) sets.
  - Threshold sweep $	heta \in [0.20, 0.70]$ validating optimal boundary $	heta = 0.42$.
  - Adversarial keyword-stuffing resistance evaluation.
  - 5-class metamorphic perturbation suite.

### Paper 3: Guardrailed PPO Adaptive Difficulty (SmartCom 2027)
- **Contribution:** 6D state representation with post-hoc pedagogical guardrails (G1-G4) preventing premature difficulty jumps, over-penalization under acoustic hesitation, and oscillation.
- **Empirical Assets:**
  - Trajectory comparison across 5 personas (Strong, Fragile Genius, Anxious Competent, Inconsistent, Weak) over 20 random seeds against Fixed and Heuristic baselines.
  - State dimension-4 impact analysis comparing training response time vs runtime turn progress.
  - Guardrail ablation proving volatility and oscillation reduction.
