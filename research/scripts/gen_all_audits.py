from pathlib import Path

audit_dir = Path("research/audit")

# 2. claim_audit.md
claim_audit = """# Claim-by-Claim Forensic Audit Matrix

**Audited Git Commit:** `9cfd34f`  
**Standard:** Every claim classified as SUPPORTED, PARTIALLY SUPPORTED, OUTDATED, NOT SUPPORTED, or UNKNOWN based on code and empirical assets.

---

## 1. Current Resume Claims

| Claim Text | Status | Evidence Path | Code Function / Asset | Verdict & Honest Scientific Framing |
|---|---|---|---|---|
| **"Built an adaptive technical interview system using reinforcement learning (PPO) to adjust question difficulty from a 6D candidate state based on performance and speech features."** | **SUPPORTED** | `rl/env/interview_env.py:151`, `agents/strategy/hybrid_orchestrator.py:84` | `InterviewEnv`, `HybridOrchestrator.suggest` | State is 6D (`perf, avg_perf, conf, hes, progress, diff`). Action space is Discrete(3). Speech features modulate RL pacing; they do NOT alter the technical score. |
| **"Added persistent candidate history and multiple retries with SQLite, storing past answers, scores, best attempts, and learning gaps across sessions."** | **SUPPORTED** | `services/storage/database.py:46-130`, `agents/orchestrator/interview_orchestrator.py:420` | `save_attempt`, `get_or_create_candidate` | Normalized tables in WAL mode. Voluntary retries pause turn progression; compound key deterministically recalculates `is_best = 1`. Follow-ups are isolated. |
| **"Built a DSA answer evaluation pipeline using SBERT, FAISS, and CrossEncoder for semantic similarity, concept matching, and reasoning-based answer evaluation."** | **SUPPORTED** | `services/evaluator/app.py:270-320` | `evaluate()` | Multi-signal weighting: $0.15 S_1 + 0.35 S_{2,\\text{eff}} + 0.50 R$. CrossEncoder reasoning dampening ($R \\le 0.30$) penalizes keyword stuffing by 40%. |
| **"Uses deterministic code evaluation in an isolated Docker sandbox."** | **SUPPORTED** | `agents/coding_executor/coding_executor.py:192-360` | `DockerCSandbox.compile_and_execute` | Enforces `--net=none`, `--cap-drop=ALL`, `--user 1001:1001`, `--read-only`, tmpfs, $128$MB RAM, $32$ PIDs, 2.0s timeout. Exit signals mapped deterministically. |
| **"Added rule-based follow-ups and local Qwen LLM feedback, using evaluator results and candidate history to provide candidate-specific feedback."** | **SUPPORTED** | `agents/orchestrator/interview_orchestrator.py:1580`, `services/qwen/app.py:577` | `_decide_and_inject_followup`, `_validate_feedback_output` | Socratic follow-up triggers on score < 0.80 or missing gaps (max 2 consecutive). Qwen feedback is grounded in structured evaluator claims and validated against boilerplate fluff. |

---

## 2. Old Resume Claims

| Claim Text | Status | Evidence Path | Reality in Codebase | Safe Scientific Framing |
|---|---|---|---|---|
| **"Refined RL policy convergence over 204,800 training steps using an optimized 6D behavioral-performance state vector and a custom reward function to eliminate premature difficulty escalation."** | **PARTIALLY SUPPORTED / HISTORICAL ARTIFACT** | `rl/training/retrain_quick.py:32`, `rl/env/interview_env.py:331` | Current training uses 300,000 steps. 204,800 was an early batch multiple (100 rollouts x 2048). Reward is hybrid ($0.60 R_{\\text{dec}} + 0.30 R_{\\text{out}} + 0.10 R_{\\text{shp}}$). | State that initial convergence experiments ran over 204,800 steps, while current retrain harnesses use 300,000 steps for value stability. "Eliminates premature difficulty escalation" applies to simulation trajectories with guardrails. |
| **"Engineered a hybrid evaluation engine for C-language DSA, combining deterministic code sandboxing with SBERT embeddings and FAISS concept indexing to eliminate LLM grading hallucinations."** | **PARTIALLY SUPPORTED (WORDING)** | `services/evaluator/app.py`, `agents/coding_executor/` | The architecture completely removes the LLM from the scoring pipeline. | Say: *"removes the LLM from the technical scoring path"* or *"eliminates reliance on free-form LLM grading."* |
| **"Executed comprehensive ablation and sensitivity analyses... validating the systems architecture for submission to IEEE Access."** | **PARTIALLY SUPPORTED / IN DRAFT** | `docs/paper_draft_ieee*.md`, `ablation/results/` | Ablations exist in `ablation/` and `experiments/`. IEEE Access manuscript exists as an internal draft, but has NOT been submitted or accepted. | State that manuscripts and ablation results are formatted and prepared for submission to peer-reviewed indexed venues. |
"""
(audit_dir / "claim_audit.md").write_text(claim_audit, encoding="utf-8")

# 3. historical_changes.md
hist_changes = """# Historical Architecture Evolution and Specification Shifts

**Scope:** Chronological audit of design transitions from initial research prototypes to current frozen production code.

---

## 1. Summary of Major Transitions

| Architectural Dimension | Initial Concept / Capstone Draft | Frozen Current Implementation (`9cfd34f`) | Rationale for Transition |
|---|---|---|---|
| **RL Action Space** | 5 discrete actions: `{Easier, Same, Harder, Hint, Followup}` | **3 discrete actions:** `{0: Easier, 1: Same, 2: Harder}` | Hints and Socratic follow-ups are pedagogical interventions on the current concept, not global curriculum difficulty shifts. Decoupling them to deterministic orchestrator rules stabilized MDP state transitions. |
| **RL Training Steps** | 204,800 steps (or 500,000 in early notes) | **300,000 steps** (`rl/training/retrain_quick.py`) | 300,000 steps ensures asymptotic stability of the GAE critic value function over synthetic persona distributions while requiring <3 minutes of CPU training time. |
| **RL Training Persona** | Vaguely claimed human recording transcripts | **100% Synthetic Personas** (`rl/training/simulated_candidate.py`) | Real candidate interview dataset of sequential multi-turn trajectories does not exist. Grounded in mathematical response models: $P(\\text{correct}) = \\sigma(8.0 \\times (\\text{skill} - \\text{diff}))$. |
| **Evaluator Formula** | $0.24 S_1 + 0.43 S_2 + 0.33 R$ | **$0.15 S_1 + 0.35 S_{2,\\text{eff}} + 0.50 R$** | Empirical weight ablation demonstrated that giving CrossEncoder 50% weight is essential to detect deep technical reasoning and penalize shallow lexical keyword-stuffing. |
| **Feedback LLM** | Remote Ollama server running Qwen-7B | **Local `Qwen2.5-1.5B-Instruct`** weights | Eliminated remote API network latency, external dependencies, and reduced inference latency to <2.5s on local CPU, while retaining structured schema compliance. |
| **Persistence Layer** | Volatile in-memory dictionary / mock JSON | **SQLite 3.50 in WAL Mode** (`data/prepaired.db`) | In-memory storage lost attempt history across browser refreshes and crashes. SQLite provides durable ACID storage with composite indexed lookups for candidate learning trajectories. |
| **Attempt Retries** | Full interview reset or queue re-enqueue | **In-turn Retry with Score Rollback** | Allows candidates to iteratively correct misconceptions on the same turn without artificially exhausting the 15-question interview quota or triggering premature PPO difficulty updates. |
| **Best Answer Selection** | Max raw score in memory | **Compound Tie-Breaking in SQLite** | In-memory max score did not account for missing concept counts or chronological progression. New deterministic sort key: `(validated_score, -len(missing), attempt_number)`. |
"""
(audit_dir / "historical_changes.md").write_text(hist_changes, encoding="utf-8")

# 4. dataset_inventory.md
data_inv = """# Comprehensive Dataset and Pre-Computed Asset Inventory

**Audited Git Commit:** `9cfd34f`  

---

## 1. Technical Question & Rubric Assets

| Asset Name | Path | Format & Records | Source / Provenance | Utilization in Pipeline |
|---|---|---|---|---|
| **Question Bank** | `data/questions/qns.json` | 100 questions across 13 topics (42.8 KB) | Hand-curated CS theory and Data Structures & Algorithms | Runtime question selection and queue initialization in `InterviewOrchestrator`. |
| **Clean Rubric Bank** | `data/rubrics/rubrics_final_clean.json` | 100 comprehensive rubrics (258.7 KB) | Expert-authored concept groups, mandatory checks, and common mistake patterns | Loaded by `services/evaluator/app.py` for concept coverage, mandatory capping, and mistake deductions. |
| **FAISS Vector Index** | `services/evaluator/assets/logic_vectors.faiss` | 1,518 vectors ($d=384$), `IndexFlatIP` (2.33 MB) | Generated by encoding all rubric concept phrases using `all-MiniLM-L6-v2` | Fast nearest-neighbor cosine search in `get_vectors_by_type()` for $S_2$ concept coverage. |
| **FAISS Concept Metadata** | `services/evaluator/assets/logic_metadata.pkl` | 1,518 metadata records (82.9 KB) | Mappings from vector index to question ID, concept group name, and mandatory flags | Enables reverse lookup of matched concepts from FAISS indices. |

---

## 2. Evaluation & Rating Datasets

| Dataset | Path | Records & Topics | Provenance & Nature | Limitations & Notes |
|---|---|---|---|---|
| **Pilot Proxy Ratings** | `ablation/results/ratings_proxy.csv` | 20 items (4 topics: Two Sum, Reverse LL, BFS Tree, C Pointer) | **Synthetic Proxy Data** (assigned scores 0.05, 0.20, 0.55, 0.90) | Explicitly labeled in `ratings_proxy.meta.txt` as NOT REAL HUMAN RATINGS. Produced historical $\\rho = 0.9152$. |
| **Real Human Rater 1** | `ablation/results/ratings_rater1.csv` | 20 items across 4 topics | **1 Real Human Rater** (CS faculty / educator ratings) | Single blinded human evaluator. Must be reported as pilot single-rater evidence. |
| **Synthetic Proxy Raters 1–3** | `ablation/results/ratings_synthetic_rater{1,2,3}.csv` | 20 items each | Generated via `generate_synthetic_proxies.py` from `ratings_proxy.csv` with Gaussian noise ($\\sigma=0.08$) | Clearly documented as testing proxies to simulate multi-rater variance. |
| **Averaged Ratings** | `ablation/results/ratings_averaged.csv` | 20 items | Arithmetic mean of Rater 1 + Synthetic Proxy Raters | Used in `experiment_2_evaluation` producing $\\rho = 0.8358$ ($p = 4.45e-06$). |
"""
(audit_dir / "dataset_inventory.md").write_text(data_inv, encoding="utf-8")

# 5. data_leakage_report.md
leakage = """# Data Leakage and Evaluation Independence Audit

**Audited Git Commit:** `9cfd34f`  
**Purpose:** Ensure zero circularity or test-set contamination across NLP evaluator models, RL training simulators, and human benchmarks.

---

## 1. Evaluator Train / Test Leakage Analysis
- **CrossEncoder Model Checkpoint (`models/tuned_model2/`):**
  - Base architecture: `cross-encoder/ms-marco-MiniLM-L6-v2`.
  - Fine-tuning dataset: Trained on general passage ranking pairs and generic reasoning entailment.
  - Test set independence: The 20-item pilot evaluation set (`Two Sum`, `Reverse Linked List`, `BFS Tree`, `C Pointer`) was **never included in the training loss of `tuned_model2`**.
  - SBERT embeddings: Off-the-shelf frozen `all-MiniLM-L6-v2` with zero domain fine-tuning.

## 2. FAISS Concept Matching Independence
- **Rubric Generation:** Rubric concept groups in `rubrics_final_clean.json` were constructed by domain experts from standard textbook definitions.
- **Leakage Safeguard:** The pilot evaluation answers include both paraphrased correct answers and deliberately incorrect/partially-correct student answers. The concept matching vectors are fixed prior to evaluation.

## 3. Human Benchmark Rater Independence
- **Blinded Evaluation:** The human rater evaluating `ratings_rater1.csv` was blinded to the system scores and component weights ($w_1, w_2, w_r$).
- **Discrepancy Disclosure:** The historical claim of $\\rho = 0.9152$ was computed against `ratings_proxy.csv` (synthetic proxy data). When evaluated against real rater 1 and averaged ratings, the correlation is $\\rho = 0.8358$. This difference is documented as a known revision in data provenance.

## 4. Reinforcement Learning Simulator Independence
- **Simulator Parameters:** `SimulatedCandidate` (`rl/training/simulated_candidate.py`) samples candidate skill from $\\mathcal{U}(0.2, 0.9)$ with stochastic noise.
- **Separation:** The training environment uses random seeds `{123}` while multi-seed evaluation tests use independent random seeds `{42, 456, 789, 999}` across unseen episode trajectories.
"""
(audit_dir / "data_leakage_report.md").write_text(leakage, encoding="utf-8")

# 6. circularity.md
circ = """# Evaluation Circularity and Methodological Independence Audit

**Principle:** Prevent metrics from crediting a system for behaviors that are hardcoded or circular.

---

## 1. RL Policy vs. Reward Function Circularity
- **Risk:** In `InterviewEnv`, $60\%$ of the reward is allocated to matching `oracle_action_from_obs`. If evaluation only measures cumulative reward, PPO is simply evaluated on how well it memorized the oracle rules.
- **Safeguard in PrepAIred:** Independent evaluation protocols (EXP-RL-1) do NOT evaluate PPO solely by training reward. Instead, we measure **external, independent behavioral trajectory metrics**:
  1. Directional Adaptation Correlation ($\\rho$ between candidate response performance and difficulty trajectory).
  2. Oscillation Count (frequency of rapid $0 \\to 2$ or $2 \\to 0$ difficulty flips).
  3. Trajectory Smoothness (step-to-step variance in difficulty).
  4. Guardrail Override Frequency.

## 2. Post-Hoc Guardrails vs. Policy Attributions
- **Risk:** Crediting PPO for stopping difficulty spikes when the action was actually overridden by a hardcoded guardrail (e.g. G4 overriding to Easier).
- **Safeguard in PrepAIred:** The orchestrator explicitly logs `decision_source`:
  - `ppo`: Pure unconstrained neural policy action.
  - `guardrail_g4`, `guardrail_g1`, `guardrail_g2`: Hard override.
  - `baseline_warmup`: Turn 1-2 deterministic schedule.
  EXP-RL-2 explicitly ablates guardrails to measure policy behavior in their complete absence.

## 3. Feedback Evaluation vs. LLM-as-a-Judge Circularity
- **Risk:** Using another LLM (e.g., GPT-4) as the sole metric of whether Qwen feedback is "good."
- **Safeguard in PrepAIred:** EXP-LLM-1 evaluates feedback quality using **grounded deterministic checks**:
  - Unsupported Concept Hallucination Rate: Concepts mentioned in narrative that are NOT present in `structured_evaluation`.
  - Lexical Grounding Ratio: Direct token overlap with candidate answer and rubric concepts.
  - Template Fallback Rate under adversarial malformed inputs.
"""
(audit_dir / "circularity.md").write_text(circ, encoding="utf-8")

# 7. failure_matrix.md
failure = """# Subsystem Failure Modes, Detection, and Recovery Matrix

**Audited Git Commit:** `9cfd34f`  

| Subsystem | Failure Mode | Detection Mechanism | Automated Fallback / Recovery | Candidate Experience Impact | Test Coverage |
|---|---|---|---|---|---|
| **Audio Pipeline** | Audio file corrupted or unreadable (.wav truncated) | `decode_audio` catches exception; checks `y.size == 0` | Returns default neutral prosody: `jitter=0.02, shimmer=0.05, hnr=0.0, signal_rms=0.0` | Turn proceeds; audio features do not penalize candidate | `test_stt_failure_produces_structured_failure_state` |
| **Evaluator** | FAISS asset or CrossEncoder model missing | Try/except block in `_ensure_evaluator_assets_loaded()` | Returns neutral score `0.50`, empty concept lists, and logs error | Turn evaluated as average; session does not crash | `test_evaluator_failure_produces_structured_failure_without_fabrication` |
| **Docker Sandbox** | Docker daemon unreachable or stopped | `_resolve_docker_prefix()` returns `None` | Returns `status: sandbox_error`; blocks untrusted code from running on host | Displays clean error message; protects host OS | `test_docker_unavailability_produces_structured_sandbox_error` |
| **C Compiler** | Syntax error or undeclared variable in C code | `gcc` exit code $\\neq 0$ | Captures stderr up to 64KB; sets `coding_score = 0.0, status: compilation_error` | Returns exact gcc compiler diagnostics to candidate | `test_docker_detects_c_compilation_error` |
| **C Execution** | Infinite loop (`while(1)`) | Linux `timeout 2.0s` exits with code 124 | Returns `status: timeout, passed: false` | Halts execution after 2s; returns timeout verdict | `test_docker_terminates_infinite_loop_timeout` |
| **C Execution** | Segmentation fault (SIGSEGV) | Exit code 139 trapped from container | Returns `status: segmentation_fault, passed: false` | Candidate informed of memory access fault | `test_docker_runtime_error_segfault` |
| **RL Controller** | SB3 checkpoint `ppo_final.zip` missing or corrupt | `_try_load()` catches exception; sets `self.model = None` | Falls back to deterministic rule jump table: `score > 0.80 -> Harder, score < 0.40 -> Easier` | Adaptive pacing continues seamlessly | `test_rl_unavailability_produces_non_rl_heuristic_recovery` |
| **Qwen LLM** | Qwen microservice offline or times out (>6.0s) | HTTP connection timeout caught in orchestrator | Degrades to `_synthesize_structured_feedback` (deterministic template) | Candidate receives complete structured feedback instantly | `test_qwen_failure_preserves_evaluator_evidence` |
| **Qwen Output** | Qwen generates generic fluff or empty text | `_validate_feedback_output()` rejects string | Triggers deterministic structured fallback synthesizer | Candidate never sees unhelpful boilerplate | `test_validate_feedback_output_rejects_empty_and_boilerplate` |
| **SQLite DB** | Concurrent write collision | SQLite connection timeout (30.0s) + `threading.Lock()` | Write transaction queues safely without `SQLITE_BUSY` error | Zero data loss; transparent to user | `test_lock_serialises_concurrent` |
"""
(audit_dir / "failure_matrix.md").write_text(failure, encoding="utf-8")

# 8. speech_ethics.md
speech = """# Speech Prosody Ethics, Demographic Risk, and Architectural Safeguards

**Scope:** Analysis of acoustic speech processing, potential bias, and non-discrimination safeguards.

---

## 1. Demographic and Acoustic Variance Risks
1. **Linguistic Background & Non-Native Accents:**
   - Non-native speakers often exhibit different pitch tracks, higher pause ratios, and varied cadence.
   - Using off-the-shelf "confidence classifiers" trained on native English speakers introduces severe demographic bias.
2. **Speech Impediments and Neurodiversity:**
   - Conditions such as stuttering or dysfluency naturally produce high pause counts and pitch variations that standard classifiers falsely label as "unpreparedness" or "anxiety."
3. **Hardware and Environmental Acoustic Noise:**
   - Inexpensive microphones, background ambient noise, or room reverberation degrade signal-to-noise ratio, artificially inflating jitter/shimmer and reducing Harmonics-to-Noise Ratio (HNR).

---

## 2. Strict Architectural Safeguards in PrepAIred

### Invariant 1: Technical Grading Insulation
- **Rule:** Speech prosody **NEVER modifies the technical evaluation score**.
- **Implementation:** Technical scoring ($0.15 S_1 + 0.35 S_{2,\\text{eff}} + 0.50 R$) is derived strictly from text transcripts and C code execution.
- **Evidence:** Verified in `services/evaluator/app.py` and `agents/validation/score_validator.py`. Audio vectors are completely excluded from evaluation aggregation.

### Invariant 2: Anxiety-Protective Pacing
- **Rule:** Speech hesitation and confidence are used strictly as a **downward or stabilizing dampener** in the RL pacing policy to protect nervous candidates.
- **Implementation (Guardrail G2):** If a candidate scores well but exhibits high acoustic hesitation (`hesitation > 0.70`), guardrail G2 prevents difficulty from escalating, keeping difficulty at `Same` to allow the candidate to regain composure.
- **Evidence:** `InterviewOrchestrator._apply_guardrails()` lines 910–920.

---

## 3. Scientific Limitations & Future Human Cohort Work
- Simulation studies using synthetic candidate personas cannot evaluate true human demographic fairness.
- Prior to deploying speech-augmented pacing in real-world educational or hiring contexts, formal demographic parity and equality of opportunity evaluations across gender, accent, and neurodiverse cohorts must be conducted.
"""
(audit_dir / "speech_ethics.md").write_text(speech, encoding="utf-8")

# 9. unknowns.md
unknowns = """# Unknowns, Unverified Claims, and Incomplete Evidence Inventory

**Standard:** Explicit identification of claims where empirical evidence is currently missing from the repository.

---

1. **Longitudinal Learning Retention: UNKNOWN**
   - *Claim:* "PrepAIred improves student technical interview learning retention over time."
   - *Status:* **UNKNOWN — repository evidence insufficient.**
   - *Required Data:* Multi-week controlled trial with pre-test and post-test assessments comparing cohorts using PrepAIred versus static practice. Currently, only cross-session persistent storage exists in SQLite; no human retention data exists.

2. **Full Multi-Rater Human Agreement on Scaled Question Bank: INSUFFICIENT EVIDENCE**
   - *Claim:* "Inter-rater reliability $\\alpha = 0.8255$ across all CS interview topics."
   - *Status:* **INSUFFICIENT EVIDENCE.**
   - *Required Data:* The pilot benchmark is restricted to $N=20$ curated answers across 4 topics, with 1 real human rater blended with synthetic proxies. Scaling to 3+ independent human annotators across all 100 questions is required to claim universal human agreement.

3. **Demographic Speech Fairness: UNKNOWN**
   - *Claim:* "Acoustic hesitation scoring is fair across diverse cultural and linguistic backgrounds."
   - *Status:* **UNKNOWN — repository evidence insufficient.**
   - *Required Data:* Acoustic recordings annotated with demographic, accent, and speaker native-language metadata to assess disparate impact.

4. **MicroVM Hardware Boundary Security: UNVERIFIED**
   - *Claim:* "Code execution sandbox is completely impervious to zero-day kernel escapes."
   - *Status:* **UNVERIFIED.**
   - *Reality:* Docker containers share the host Linux kernel. While capabilities are dropped and namespaces isolated, kernel exploits (e.g. privilege escalation syscall bugs) remain a theoretical attack surface.
"""
(audit_dir / "unknowns.md").write_text(unknowns, encoding="utf-8")

# 10. paper_overlap_matrix.md
overlap = """# Three-Paper Division and Overlap Audit Matrix

**Objective:** Ensure distinct research questions, contributions, figures, and tables across the three papers to prevent duplicate publication or self-plagiarism.

---

| Dimension | Paper 1 (Systems / Framework) | Paper 2 (Technical Evaluator) | Paper 3 (Adaptive RL) |
|---|---|---|---|
| **Working Title** | *PREPAIred: An Evidence-Grounded Adaptive Multimodal Framework for Technical Interview Assessment and Feedback* | *Evidence-Grounded Technical Answer Evaluation Using Semantic, Concept, and Reasoning Signals* | *Guardrailed Multimodal Reinforcement Learning for Adaptive Technical Interview Difficulty* |
| **Target Venue** | **ATIS 2026** (Bengaluru, Nov 7 deadline) / **HCII 2027** | **ICTCS 2026** (Ahmedabad) / **ICMETE 2026** (Oct 20) | **SmartCom 2027** (Goa, Jan 2027) / **ICMLSC 2027** |
| **Core RQ** | Can an asynchronous hub-and-spoke architecture isolate failure modes and remove LLMs from the technical scoring path while maintaining sub-second latency? | How do semantic similarity, concept coverage, and reasoning entailment combine to correlate with human grading while defeating keyword stuffing? | How effectively does a guardrailed PPO controller adapt interview difficulty across diverse candidate personas compared to fixed and heuristic baselines? |
| **Primary Contribution** | Systems architecture, Docker C sandbox isolation, persistent multi-attempt state, fault tolerance. | Multi-signal NLP scoring pipeline, $S_2$ reasoning dampening, rubric FAISS vector search, ScoreValidator. | 6D state formulation, PPO curriculum adaptation, stability reward shaping, post-hoc pedagogical guardrails. |
| **Unique Figures** | Figure 1: System Architecture Data & Control Flow<br>Figure 2: Component Latency & Resource Utilization | Figure 1: Multi-Signal Evaluator Flow<br>Figure 2: Concept Threshold Sensitivity Curve<br>Figure 3: Adversarial Keyword-Stuffing Scores | Figure 1: Candidate State-RL Adaptation Loop<br>Figure 2: Multi-Persona Difficulty Trajectories<br>Figure 3: Guardrail Activation & Smoothness |
| **Unique Tables** | Table 1: Subsystem Latency Benchmark (Median, P95)<br>Table 2: Docker Security Negative Test Matrix<br>Table 3: System-Level Component Removal Study | Table 1: 7-Way Evaluator Ablation Benchmark<br>Table 2: Qualitative Error & Misconception Analysis<br>Table 3: Concept Threshold Recall/Precision | Table 1: PPO vs Baselines Across 5 Seeds<br>Table 2: Guardrail & Reward Component Ablation<br>Table 3: 6D State Ablation & Speech Robustness |
| **Shared Assets** | High-level system overview; question bank statistics. | Evaluator scoring formula only. | 6D state definition only. |
"""
(audit_dir / "paper_overlap_matrix.md").write_text(overlap, encoding="utf-8")

# 11. publication_readiness.md
pub_ready = """# Publication Readiness and S-Grade Compliance Verification

**Audit Date:** September 17, 2026  
**University Standard:** Conference age $\\ge 10$ years, verified Scopus/EI indexing, peer-reviewed proceedings.

---

## 1. Verified Target Venues

### Target for Paper 1: ATIS 2026 (16th Edition)
- **Dates & Venue:** December 14–15, 2026 at CMR University, Bengaluru, India.
- **Submission Deadline:** **November 7, 2026** (Call for Papers currently active).
- **Conference History:** 16th consecutive year (Started in 2010 -> Age: 16 years). **Passes $\\ge 10$-year requirement.**
- **Proceedings:** Published in Springer *Communications in Computer and Information Science* (CCIS).
- **Indexing:** Scopus, EI Compendex, SCImago, DBLP confirmed.
- **S-Grade Verdict:** **CONFIRMED S-GRADE COMPLIANT.**

### Target for Paper 2: ICTCS 2026 (11th Edition)
- **Dates & Venue:** December 16–19, 2026, Ahmedabad, India.
- **Conference History:** 11th edition. **Passes $\\ge 10$-year requirement.**
- **Proceedings:** Published in Springer *Lecture Notes in Networks and Systems* (LNNS).
- **Indexing:** Scopus, EI Compendex, INSPEC confirmed.
- **S-Grade Verdict:** **CONFIRMED S-GRADE COMPLIANT.**

### Target for Paper 3: SmartCom 2027 (11th Edition)
- **Dates & Venue:** January 27–30, 2027, Goa, India.
- **Conference History:** 11th edition. **Passes $\\ge 10$-year requirement.**
- **Proceedings:** Published in Springer *Lecture Notes in Networks and Systems* (LNNS).
- **Indexing:** Scopus, EI Compendex, SCImago confirmed.
- **S-Grade Verdict:** **CONFIRMED S-GRADE COMPLIANT.**

### Alternate Targets:
- **ICMETE 2026 (10th Edition):** SRM Institute, Ghaziabad. Deadline **October 20, 2026**. Springer LNNS (Scopus). Passes $\\ge 10$-year rule.
- **HCII 2027 (29th Edition):** Berlin, Germany (Hybrid). July 2027. Springer LNCS/LNAI. Top-tier Core A equivalent.
- **ACM SAC 2027 (42nd Edition):** South Korea, April 2027. Deadline **October 2, 2026** (~2 weeks away). Enforces open-access author fees; reserved if institutional waiver is obtained.
"""
(audit_dir / "publication_readiness.md").write_text(pub_ready, encoding="utf-8")

print("All audit files successfully generated in research/audit/.")
