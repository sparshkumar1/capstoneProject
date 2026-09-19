# Claude Research Index & Navigation Map

**Audited Commit:** `9cfd34f`
**Purpose:** Direct Claude, AI assistants, and human researchers to canonical, verified information and prevent the hallucination or replication of superseded historical claims.

---

## 1. Required Reading Order for AI Agents

When working on research, writing papers, verifying claims, or checking experimental results, **consult files in this exact priority sequence**:

### Stage 1: Absolute Truth & Verified Facts (READ FIRST)
1. [`research/README.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/README.md) — Master entry point and project overview.
2. [`research/CANONICAL_SCIENTIFIC_TRUTH.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/CANONICAL_SCIENTIFIC_TRUTH.md) — The sole authoritative record of verified metrics, formulas, architectures, and numbers.
3. [`research/audit/claim_audit.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/audit/claim_audit.md) — Forensic verification status of every resume and paper claim.
4. [`research/audit/evaluator_result_provenance.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/audit/evaluator_result_provenance.md) — Provenance of 0.9152 vs 0.8358 vs 0.6975 vs 0.7400.
5. [`research/audit/data_leakage_report.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/audit/data_leakage_report.md) — Dataset independence and rater blinding audit.

### Stage 2: Target Paper Packages
- **Paper 1 (Systems & Security / ATIS 2026):** [`research/papers/paper1_systems/README.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/papers/paper1_systems/README.md)
- **Paper 2 (NLP Evaluator / ICTCS 2026):** [`research/papers/paper2_evaluator/README.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/papers/paper2_evaluator/README.md)
- **Paper 3 (Adaptive RL / SmartCom 2027):** [`research/papers/paper3_rl/README.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/papers/paper3_rl/README.md)

### Stage 3: Empirical Tables & Experimental Evidence
- Component Ablation Table: [`research/tables/table_eval_ablation.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/tables/table_eval_ablation.md)
- Metamorphic Testing Results: [`research/tables/metamorphic_results.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/tables/metamorphic_results.md)
- Adversarial Keyword Stuffing: [`research/tables/table_eval_adversarial.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/tables/table_eval_adversarial.md)
- RL Policy vs Baselines: [`research/tables/table_rl_policy_comparison.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/tables/table_rl_policy_comparison.md)
- RL Dimension 4 Transfer: [`research/tables/table_rl_dim4_analysis.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/tables/table_rl_dim4_analysis.md)
- Docker Negative Security Tests: [`research/tables/table_sys_security_boundary.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/tables/table_sys_security_boundary.md)
- Subsystem Latencies: [`research/tables/table_sys_latency_benchmark.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/tables/table_sys_latency_benchmark.md)

---

## 2. Topic-to-File Canonical Routing Matrix

| If You Need Information On... | DO NOT Look In... | ALWAYS Use This Canonical Path |
|:---|:---|:---|
| **Evaluator Formula / Weights** | Old drafts in `docs/` | `services/evaluator/app.py:350-405` & `research/CANONICAL_SCIENTIFIC_TRUTH.md` |
| **Human Correlation ($\rho, r$)** | `ratings_proxy.csv` (0.9152), stale CSV (0.7400) | `research/results/paper2_final_results.md` & `research/CANONICAL_SCIENTIFIC_TRUTH.md` ($\rho = 0.6975$) |
| **RL State & Steps** | Early drafts (204,800 steps) | `rl/training/retrain_quick.py` (300,000 steps) & `research/audit/rl_state_alignment.md` |
| **Sandbox Security & Docker** | Unsubstantiated claims in `docs/` | `research/tables/table_sys_security_boundary.md` & `research/audit/threat_model.md` |
| **Engineering Test Status** | Outdated stage reports | `research/results/engineering_tests.json` & `research/audit/current_test_manifest.md` |
| **Subsystem Latencies** | Monolithic booklets | `research/tables/table_sys_latency_benchmark.md` |
| **Reproduction Instructions** | Old checklists in `submission/` | `research/reproducibility/paper_{1,2,3}_reproduce.md` |
| **Superseded Claims & History** | N/A | `research/audit/SUPERSEDED_DOCUMENTS.md` |

---

## 3. Strict Rules for AI Reasoning
1. **Never Cite $\rho = 0.9152$ or $\rho = 0.8358$ as Authentic Human Agreement:** These were synthetic proxies. Also do not cite $\rho = 0.7400$ (superseded static CSV artifact). The sole authentic live single-educator benchmark is **$\rho = 0.6975$** ($p = 0.00063$, $r = 0.7290$, $\text{MAE} = 0.2245$, $N=20$).
2. **Never Cite 204,800 PPO Steps:** The canonical training duration is 300,000 steps.
3. **Never Claim Free-Form LLM Scoring:** The LLM is strictly isolated from technical grading; scoring is deterministic SBERT + FAISS + CrossEncoder.
4. **Treat `research/archive/` and `submission/` as Historical Only:** Do not extract current evidence from archived folders.
