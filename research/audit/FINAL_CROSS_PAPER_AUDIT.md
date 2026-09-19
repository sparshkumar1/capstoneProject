# PREPAIred — Final Cross-Paper Scientific Integrity & Readiness Audit

**Audit Date:** September 19, 2026  
**Auditor:** Antigravity Advanced Agentic Research Auditor  
**Scope:** Repository-wide verification across Paper 1 (Systems), Paper 2 (Evaluator), and Paper 3 (Adaptive RL)  
**Status:** **AUDIT COMPLETE**  
**Overall Verdict:** **`READY_FOR_CLAUDE`**

---

## 1. Frozen Paper Snapshots Verification

The repository state for each paper was verified against cryptographic hashes and immutable Git checkpoints:

| Paper Milestone | Authoritative Commit / Tag | Result Directory | Key Frozen Artifact | Hash / Status | Integrity Verdict |
|:---|:---|:---|:---|:---|:---:|
| **Paper 1: Systems & Security** | Commit `375f4f869c47907d7c222d27df3b4f9e09dc8941` | `research/results/paper1/` | `paper1_systems_raw.json` | 100% Intact | **PASS** |
| **Paper 2: Evaluator Alignment** | Commit `375f4f869c47907d7c222d27df3b4f9e09dc8941` | `research/results/paper2/` | `final_human_gold.csv` | `363dbe6d848a04fe...` | **PASS** |
| **Paper 3: Adaptive RL** | Commit `b7cad49b6b7a5446...` (Tag `v1.0-paper3-complete`) | `research/results/paper3/` | `paper3_raw_results.json` | `2773caa0ca4c7be9...` | **PASS** |

All underlying files exist, are accessible, and maintain complete internal consistency.

---

## 2. Paper 1 Factual Consistency Audit

- **Code Execution Security:** Verified 9/9 (100.0%) negative C security test vectors (`SEC-01` to `SEC-09`) contained by pre-flight static policies or Docker cgroup boundaries.
- **Fault Recovery:** Verified 10/10 (100.0%) predefined fault scenarios (`FLT-01` to `FLT-10`) recovered gracefully without state corruption.
- **Concurrency & ACID Isolation:** Verified across 1, 5, 10, and 25 concurrent sessions: **0 lock errors**, **0 isolation violations**.
- **Latency Measurements:** Warm multi-component evaluator executes in **1960.8 ms** mean (median: 404.6 ms, P95: 2098.6 ms); SQLite commit indexing executes in **17.2 ms**; ScoreValidator executes in **0.004 ms**.
- **Qwen Isolation:** Verified 5/5 boundary invariants (`QWN-01` to `QWN-05`); Qwen has zero scoring, difficulty, or attempt-ranking authority.
- **Multimodal Separation:** Acoustic prosody is 100% insulated from technical scoring.
- **Regression Pass Count at Snapshot:** Verified backend test suite at snapshot commit `375f4f86` passed **213 tests, 1 skipped, 0 failed**.
- **Defensible Framing Checks:**
  - ✅ Manuscript-facing summaries do **NOT** claim "universal fault tolerance"; framing is strictly *"All 10 evaluated failure modes recovered without state corruption."*
  - ✅ Docker containerization is correctly characterized as **defense-in-depth OS process containment** sharing the host kernel, **not an inviolable security boundary**.
  - ✅ Concurrency performance on SQLite WAL is characterized as tested behavior under load, **not general unbounded production scalability**.

---

## 3. Paper 2 Factual Consistency Audit

- **Human Gold Benchmark Hash:** Verified bitwise identical:
  `SHA-256: 363dbe6d848a04fe18be5ef1d30b6bbf63b54248fe758e5e6bd4c27a26c06ce2`
- **Sample Size & Stratification:** Verified $N = 64$ authentic explanations across 10 DSA/systems topics:
  - Exactly 54 consensus cases (`gold_method = "mean_of_three"`).
  - Exactly 10 expert blind adjudicated cases (`gold_method = "expert_adjudication"`).
- **Primary Correlation Metric:**
  - **Spearman $\rho = 0.3812$** ($p = 1.8863 \times 10^{-3}$, 95% bootstrap CI $[0.1575, 0.5774]$).
  - Pearson $r = 0.4042$ ($p = 9.2455 \times 10^{-4}$), Kendall $\tau = 0.2715$ ($p = 1.7272 \times 10^{-3}$), $\text{MAE} = 0.2920$, $\text{RMSE} = 0.3601$.
- **7-Way Component Ablation Invariant:**
  - R-only: $\rho = \mathbf{0.4832}$, $\text{MAE} = 0.2763$
  - S1 + R: $\rho = \mathbf{0.4884}$, $\text{MAE} = 0.2790$
  - Full Composite: $\rho = \mathbf{0.3812}$, $\text{MAE} = 0.2920$
  - ✅ Verified: No report or summary claims that the Full Composite outperformed R-only or S1+R. The text explicitly documents that the Full Composite trades unconstrained correlation for keyword-stuffing defense and rubric concept constraints.
- **Robustness Evidence Framing:**
  - Metamorphic tests (19/21 pass) and adversarial attacks (11/13 contained) are framed as **finite empirical engineering benchmarks**, not universal robustness guarantees.
- **Model Provenance Certification:**
  - Verified: CrossEncoder is consistently certified as **off-the-shelf `cross-encoder/ms-marco-MiniLM-L6-v2` without PREPAIred-specific fine-tuning or domain adaptation**. Local folder `tuned_model2` is identified strictly as internal path scaffolding.
- **Pre-specification Terminology:**
  - Verified: No document uses "pre-registered"; the approved terminology is **"pre-specified and frozen before human annotation"**.

---

## 4. Paper 3 Factual Consistency Audit

- **Baseline & PPO Metrics:**
  - Fixed Baseline ($d=3.0$): **$\text{MAE} = 1.200$** ($[0.920, 1.440]$) across true persona targets ($[1.0, 1.5, 3.0, 4.0, 4.5]$).
  - Heuristic Baseline: **$\text{MAE} = 0.473$** ($[0.349, 0.598]$).
  - PPO + Guardrails: **$\text{MAE} = 0.677 \pm 0.006$** across 5 independent training seeds (`42, 123, 456, 789, 999`).
- **Statistical Separation of Units:**
  - Primary Evaluation Unit: Session trajectory ($N = 25$ sessions per condition across 5 personas $\times$ 5 eval seeds).
  - Training Stability Unit: $S = 5$ seeds; $\pm 0.006$ is strictly across-seed training stability.
  - Manuscript Effect Size: **Cohen's $d \approx \mathbf{0.87}$** ($p < 0.001$).
  - Documented Artifact: $t = -195.46, d = 87.41$ is archived strictly as an audit artifact of seed-mean variance collapse and is excluded from manuscript claims.
- **Non-Superiority Trade-Off:**
  - Verified: The heuristic baseline tracks faster ($\text{MAE} = 0.473$ vs $0.677$). PPO provides significantly lower trajectory volatility ($0.088$ vs $0.160$) and multimodal adaptation. **No universal PPO superiority is claimed.**
- **Safety Shield:**
  - Verified: **0 actual out-of-bounds difficulty transitions** under guardrails ($1.0 \le d \le 5.0$). 563 total guardrail interventions across 5 seeds.
- **Dimension 4 Ablation Mechanistic Explanation:**
  - Verified: `aligned_progress`, `aligned_response_time`, and `zero_progress` collapse to identical aggregate $\text{MAE} = 0.673$ due to low marginal policy sensitivity to $s_4$ in neutral coordinates and guardrail override convergence across 10 divergent raw actions.
- **Empirical Convergence:**
  - Phrasing verified: *"Policy action-distribution stabilization and rolling-reward plateauing across five seeds within 20,000 steps"* (no claims of theoretical optimality).
- **Pacing Standard:**
  - Replaced anthropomorphic "Zone of Proximal Development" with empirical *"score-band stabilization ($0.40 \le p \le 0.70$)"*.

---

## 5. Cross-Paper Model Provenance Audit

| Subsystem | Model Identifier | Checkpoint Location / Hash | Canonical Role | Authority Excluded |
|:---|:---|:---|:---|:---|
| **Semantic Embedding ($S_1$)** | `sentence-transformers/all-MiniLM-L6-v2` | Frozen PyTorch / HuggingFace | Rubric context embedding | No reasoning entailment |
| **Concept Index ($S_2$)** | FAISS `IndexFlatIP` (1,518 vectors) | `logic_vectors.faiss` | Concept group coverage ($\theta = 0.30$) | No subjective grading |
| **Reasoning Entailment ($R$)** | `cross-encoder/ms-marco-MiniLM-L6-v2` | `services/evaluator/models/tuned_model2/` (`6a241a55...`) | Zero-shot premise-hypothesis cross-attention | Zero PREPAIred fine-tuning |
| **Feedback LLM** | `Qwen2.5-1.5B-Instruct` | `services/qwen/models/` | Qualitative feedback & Socratic follow-ups | **Zero authority over score, difficulty, or RL actions** |
| **RL Policy** | SB3 PPO `MlpPolicy` | `checkpoints/seed_{42,123,456,789,999}/` | Macro difficulty adjustments $\{-1, 0, +1\}$ | Governed by G1–G6 guardrails |

Historical mentions of "fine-tuned CrossEncoder" (e.g. in older drafts or path names) have been formally resolved: the model was pre-trained by UKPLab on MS MARCO and used strictly off-the-shelf in zero-shot inference.

---

## 6. Threshold & Evaluator Consistency Audit

- **Concept Matching Operating Point:** $\theta = 0.30$ (`services/evaluator/app.py:95, 116, 126`). Historical mention of $\theta = 0.42$ in exploratory documentation is flagged as superseded.
- **Reasoning Dampening Shield:** $R \le 0.30 \implies S_{2,\text{eff}} = 0.60 \times S_2$ (`services/evaluator/app.py:377`).
- **Tripartite Scoring Formula:** $0.15 \cdot S_1 + 0.35 \cdot S_{2,\text{eff}} + 0.50 \cdot R$ (`services/evaluator/app.py:382`).
- **Mandatory Constraint Threshold:** $0.40$ (`services/evaluator/app.py:260`).

All current production code and experiment execution scripts consistently consume these exact parameters.

---

## 7. Human Agreement vs. Model Agreement Disentanglement

| Agreement Metric | Mathematical Formulation | Reported Value | Statistical Meaning | Conflation Risk Safeguard |
|:---|:---|:---:|:---|:---|
| **Human-Human ICC(2,1)** | Two-way random effects, single rater | **0.9528** | Absolute agreement between any single pair of human CS educators | Strictly describes human committee |
| **Human-Human ICC(2,k)** | Two-way random effects, average of $k=3$ raters | **0.9838** | Reliability of the 3-educator consensus mean score | Strictly describes human consensus |
| **Human-Human Krippendorff $\alpha$** | Interval distance metric across 3 raters | **0.9523** | Inter-coder reliability accounting for chance agreement | Strictly describes human committee |
| **Model-Human Spearman $\rho$** | Monotonic rank correlation ($N=64$) | **0.3812** | Model alignment with final educator gold standard | **CANNOT be reported as ICC or $\alpha$** |

Audit confirms complete isolation: no document or table implies that 0.3812 is an ICC or alpha metric.

---

## 8. Data Leakage & Contamination Audit

1. **Zero Weight Optimization on Gold:** Evaluator scoring weights ($0.15 / 0.35 / 0.50$) and thresholds ($\theta = 0.30$, dampening $0.30$) were fixed prior to Human Gate 1 and never calibrated or optimized against `final_human_gold.csv`.
2. **Zero Cross-Paper Pollution:**
   - Paper 3 RL simulator used synthetic candidate personas and independent seeds; PPO execution did not alter Paper 1 or Paper 2 results.
   - Paper 2 gold dataset hash remained 100% bitwise invariant throughout Paper 1 and Paper 3 execution passes.
3. **No Synthetic Label Substitution:** Human Gate 3 produced genuine human educator consensus; synthetic proxy ratings (`ratings_proxy.csv`) remain archived and strictly separated.
4. **Frozen Rater Files:** `RATER_1_COMPLETED.csv`, `RATER_2_COMPLETED.csv`, and `RATER_3_COMPLETED.csv` maintain identical cryptographic hashes since initial collection.

---

## 9. Result-File Consistency & Discrepancy Reconciliation

A systematic cross-check between raw JSON outputs, CSV summaries, and final report text was conducted:

| Finding ID | Artifacts Involved | Discrepancy Identified | Root Cause | Reconciled Status |
|:---|:---|:---|:---|:---|
| `DISC-01` | `paper1_summary_results.csv` vs. `paper1_latency_results.csv` | Summary CSV row 5 noted `"Warm evaluator ~40-60ms"`, while detailed CSV reported `1960.8ms` mean (`404.6ms` median). | Stale exploratory note in summary text column. | **RESOLVED**: Authoritative metric is `1960.8 ms` mean (`404.6 ms` median, `2098.6 ms` P95); documented in `FINAL_RESEARCH_MANIFEST.md`. |
| `DISC-02` | `paper3_raw_results.json` vs. `PAPER3_FINAL_REPORT.md` | Raw JSON logged $t = -195.46, d = 87.41$, while final report states Cohen's $d \approx 0.87$. | Raw calculation divided by across-seed SD ($0.006$) rather than pooled session SD ($0.609$). | **RESOLVED**: $d \approx 0.87$ is the certified manuscript effect size; raw numbers retained strictly as audit artifacts. |
| `DISC-03` | `paper3_seed_results.csv` vs. `paper3_summary_results.csv` | Seed CSV logged 26–71 `constraint_violations`, while summary table reported 0 violations. | Seed CSV counted pre-clipping proposals at difficulty boundary ($d=1$); actual post-transition state never violated $[1, 5]$. | **RESOLVED**: Formally distinguished pre-clipping proposed actions from actual post-transition trajectory violations ($0$). |

All numerical claims in manuscript handoff reports trace directly to machine-readable result files.

---

## 10. Claim-to-Evidence Matrix Status

The master claim matrix has been generated at [`research/audit/CROSS_PAPER_CLAIM_EVIDENCE_MATRIX.csv`](file:///c:/Users/spars/Downloads/PrepAIred/research/audit/CROSS_PAPER_CLAIM_EVIDENCE_MATRIX.csv):
- **Total Claims Audited:** 24 major scientific claims.
- **SUPPORTED:** 4 claims (Qwen isolation, Educator inter-rater reliability, CrossEncoder ablation dominance, Heuristic faster tracking).
- **SUPPORTED_WITH_LIMITATION:** 13 claims (Docker containment, fault recovery, concurrency, latencies, acoustic insulation, evaluator correlation, metamorphic robustness, adversarial containment, PPO tracking reduction, multi-seed stability, guardrail transitions, RL training stabilization, speech sensitivity).
- **NOT_SUPPORTED / REFUTED:** 7 claims (Universal fault tolerance, inviolable security boundary, Full composite correlation superiority, PREPAIred CrossEncoder fine-tuning, universal adversarial robustness, PPO tracking speed superiority over heuristic, Dim 4 aggregate effect, human classroom learning gains).

Every claim is accompanied by an exact evidence artifact, measured scope, and explicit limitation.

---

## 11. Reproducibility Manifest Status

Both machine-readable and human-readable manifests have been generated and validated:
- **Machine-Readable:** [`research/FINAL_RESEARCH_MANIFEST.json`](file:///c:/Users/spars/Downloads/PrepAIred/research/FINAL_RESEARCH_MANIFEST.json)
- **Human-Readable:** [`research/FINAL_RESEARCH_MANIFEST.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/FINAL_RESEARCH_MANIFEST.md)

Contains complete Git checkpoints, result directories, dataset/model/config hashes, primary metrics, experiment counts, seed counts, limitations, and reproduction commands for all three papers.

---

## 12. Claude Handoff Package Status

Curated directory created at [`research/CLAUDE_HANDOFF/`](file:///c:/Users/spars/Downloads/PrepAIred/research/CLAUDE_HANDOFF/):
- Master index: `README.md`
- Authoring rules: `MANUSCRIPT_AUTHORING_GUIDELINES.md`
- Master ground truth: `CANONICAL_SCIENTIFIC_TRUTH.md`
- Reproducibility manifests: `FINAL_RESEARCH_MANIFEST.md` and `.json`
- Claim matrix: `CROSS_PAPER_CLAIM_EVIDENCE_MATRIX.csv`
- Primary reports: `PAPER1_FINAL_REPORT.md`, `PAPER2_FINAL_REPORT.md`, `PAPER3_FINAL_REPORT.md`, `PAPER3_FINAL_FREEZE.md`
- Machine-readable tables: 14 summary CSVs across all three papers
- Key audit reports: 8 provenance and boundary audit files

Obsolete drafts, temporary logs, and unverified exploratory claims have been excluded.

---

## 13. Final Git & Repository State Verification

- **Execution Base Commit:** `375f4f869c47907d7c222d27df3b4f9e09dc8941`
- **Paper 3 Freeze Commit:** `b7cad49b6b7a54460f4eeb4ecb0292bfcb78e12f`
- **Paper 3 Annotated Tag:** `v1.0-paper3-complete`
- **Human Gold Checksum:** `363dbe6d848a04fe18be5ef1d30b6bbf63b54248fe758e5e6bd4c27a26c06ce2` (VERIFIED UNMODIFIED)
- **Paper 3 Raw Result Hashes:** All 8 CSV/JSON result files verified bitwise identical to freeze specification.
- **Paper 1 and Paper 2 Results:** Verified intact and untouched.

---

## 14. Final Research Verdicts

### Paper 1: Systems Architecture, Containment & Concurrency
**Verdict:** **`PASS-WITH-LIMITATIONS`**  
*Justification:* 9/9 negative security tests contained; 10/10 fault scenarios recovered; 0 lock errors across 1/5/10/25 concurrency loads; Qwen role strictly isolated. Limitations are explicitly stated: Docker is defense-in-depth, not microVM isolation; tested fault coverage does not prove universal fault tolerance; single-host SQLite WAL requires PostgreSQL for high distributed write loads.

### Paper 2: NLP Evaluator Alignment & Entailment Dampening
**Verdict:** **`PASS-WITH-LIMITATIONS`**  
*Justification:* 64-case human consensus benchmark established with outstanding educator reliability ($\text{ICC}(2,1) = 0.9528$, $\alpha = 0.9523$); primary correlation $\rho = 0.3812$ ($p < 0.01$); metamorphic (90.5%) and adversarial (84.6%) suites verified; CrossEncoder provenance certified as off-the-shelf zero-shot. Limitations are documented: Full Composite trades correlation for keyword defense; two adversarial attacks breached safety bounds; evaluated on DSA explanations, not free-form conversational interviews.

### Paper 3: Adaptive RL Curriculum & Guardrails
**Verdict:** **`PASS-WITH-LIMITATIONS`**  
*Justification:* All 5 pre-flight blockers resolved; multi-seed training stability verified across 5 independent seeds ($\text{SD} = 0.006$); tracking error reduced vs fixed baseline ($\text{MAE} = 0.677 \pm 0.006$ vs $1.200$, Cohen's $d \approx 0.87$); 0 actual out-of-bounds transitions under guardrails. Limitations are documented: Heuristic baseline achieves lower tracking error ($0.473$), while PPO delivers lower volatility ($0.088$ vs $0.160$); Dim 4 variants yield identical aggregate metrics; evaluated strictly in simulation on synthetic personas.

---

### Overall Research Package Verdict

# 🟢 `READY_FOR_CLAUDE`

**Certification:** The PREPAIred research package across Papers 1, 2, and 3 is complete, internally consistent, cryptographically frozen, and fully audited. The evidence package is certified ready for manuscript authoring by Claude in accordance with [`MANUSCRIPT_AUTHORING_GUIDELINES.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/CLAUDE_HANDOFF/MANUSCRIPT_AUTHORING_GUIDELINES.md).
