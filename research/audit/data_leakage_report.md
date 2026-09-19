# Data Leakage and Evaluation Independence Audit

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
- **Discrepancy Disclosure:** The historical claim of $\rho = 0.9152$ was computed against `ratings_proxy.csv` (synthetic proxy data). When evaluated against real rater 1 and averaged ratings, the correlation is $\rho = 0.8358$. This difference is documented as a known revision in data provenance.

## 4. Reinforcement Learning Simulator Independence
- **Simulator Parameters:** `SimulatedCandidate` (`rl/training/simulated_candidate.py`) samples candidate skill from $\mathcal{U}(0.2, 0.9)$ with stochastic noise.
- **Separation:** The training environment uses random seeds `{123}` while multi-seed evaluation tests use independent random seeds `{42, 456, 789, 999}` across unseen episode trajectories.
