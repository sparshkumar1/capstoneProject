# Audit Deliverable 03: Reconstructed Scientific Contribution & Novelty Audit
**Project:** PREPAIred — ADCoM 2027 (Springer CCIS)  
**Document:** `AUDIT_03_RESEARCH_CONTRIBUTION.md`  
**Candidate Directory:** `paper/adcom2027_final_v13_candidate/`  
**Date:** 3 October 2026  
**Auditor:** Independent Scientific, Reproducibility, and Publication-Quality Reviewer  

---

## 1. System Reconstruction & Physical Component Architecture

An adversarial code inspection of `agents/multiagent/` and `research/multiagent/` establishes the actual operational implementation:

```
                            +----------------------------------------------------+
                            |         Deterministic Replay Benchmark             |
                            |   (64 Pre-recorded Evaluator Answers, 8 Clusters)  |
                            +-------------------------+--------------------------+
                                                      |
                                                      v
                                        +----------------------------+
                                        | Immutable TurnObservation  |
                                        +--------------+-------------+
                                                       |
                          +----------------------------+----------------------------+
                          |                                                         |
                          v                                                         v
           +------------------------------+                          +------------------------------+
           |        Strategy Agent        |                          |        Coaching Agent        |
           |  (Rule- & Ledger-Based)      |                          |  (Rule- & Ledger-Based)      |
           |  - miss_turns: Dict[str,Set] |                          |  - concept_misses: Dict      |
           |  - resolved: Set[str]        |                          |  - hints_given: Dict         |
           |  - probes: Dict[str, int]    |   StrategyProposal       |  - examples_given: Dict      |
           |  - ema: float (alpha=0.5)    |   Peer Message (Tone)    |  - Proposes: depth, hint,    |
           |  - Proposes: difficulty,     +------------------------->|    example, emphasis         |
           |    probe, mode, confidence   |                          +--------------+---------------+
           +--------------+---------------+                                         |
                          |                                                         | CoachingPlan
                          | StrategyProposal                                        | (Additive Feedback)
                          v                                                         v
           +------------------------------+                          +------------------------------+
           |     Threshold Arbitrator     |                          |     Session Coordinator      |
           |  - Gating: confidence >= tau |                          |  - Validates evidence refs   |
           |  - Probe Cap: <= 2 followups |                          |  - Dispatches feedback plan  |
           |  - Clamping: [1, 5] levels   |                          +------------------------------+
           +--------------+---------------+
                          |
                          v
           +------------------------------+
           |  Inline Guardrail / Clamping |
           +------------------------------+
```

### Component Details
1. **Strategy Agent (`agents/multiagent/strategy_agent.py`):**
   - **Nature:** 100% deterministic rule-based controller operating on a cross-turn weakness ledger. **NOT an LLM agent.**
   - **Ledger State:** Tracks concepts missed across turns (`miss_turns`), concepts resolved (`resolved`), probes issued (`probes`), and exponential moving average of evaluator scores (`ema`, $\alpha=0.5$).
   - **Heuristic Modes:**
     - `recover` (last 2 scores mean $<0.5$ and current $<0.35$) $\to$ Action `Easier`, confidence $0.70$–$0.90$.
     - `remediate` (concept missed $\ge 2$ distinct turns) $\to$ Action `Same`, probe that concept, confidence $0.70$–$0.90$.
     - `stretch` (current $\ge 0.8$, ema $\ge 0.7$, last 3 scores $\ge 0.6$) $\to$ Action `Harder`, confidence $0.70$–$0.90$.
     - `steady` (default) $\to$ Action `Same`, confidence $0.45$ (intentionally below $\tau=0.6$, allowing baseline policy to stand).
   - **Confidence Heuristic:** Computed as $\min(0.95, 0.5 + 0.1 \times N_{\text{evidence}})$. It is a deterministic rule-based metric, not a Bayesian calibrated posterior probability.

2. **Coaching Agent (`agents/multiagent/coaching_agent.py`):**
   - **Nature:** 100% deterministic rule-based presentation controller operating on coaching history. **NOT an LLM agent.**
   - **Ledger State:** Tracks concept miss frequency (`concept_misses`), hints given (`hints_given`, capped at 2 to prevent infinite loops), examples given (`examples_given`, capped at 1), and previous feedback depth (`last_depth`).
   - **Decisions:** Determines feedback depth (`brief`, `standard`, `detailed`), whether to give a hint, whether to give an example, and up to 2 concepts to emphasize.
   - **Peer Interaction:** Receives Strategy Agent's proposal via peer messaging; modulates tone (`encouraging` on `recover`, `neutral` otherwise) and depth (`detailed` on `recover`, `brief` on `stretch`).

3. **Arbitration & Coordination Layer (`agents/multiagent/arbitration.py`):**
   - **Threshold Gating:** If Strategy Agent's confidence exceeds threshold $\tau=0.60$ and mode $\neq \text{'steady'}$, Strategy's proposed action supersedes baseline PPO.
   - **Follow-up Probe Cap:** Strictly limits follow-up probe turns to `FOLLOWUP_HARD_CAP = 2`.
   - **Clamping & Guardrails:** Clamps difficulty transitions to step sizes of $\pm 1$ within discrete levels $[1, 5]$.

4. **Machine Learning & LLM Scope:**
   - **PPO Policy:** Pre-trained single-agent reinforcement learning policy on 6-D state vector (turn, difficulty, score, progress, confidence, hesitation). Evaluated deterministically in replay.
   - **Live LLM:** **Zero live generative language models ran in the experimental replay evaluation.** All candidate answers, scores, and concept tags were pre-recorded in 64 JSON payloads executed with `EVALUATOR_MOCK_MODE=1`.

---

## 2. Research Question Alignment Audit

The manuscript structures its empirical investigation around three tightly scoped questions:

- **RQ1 — Trajectory & Coordination Dynamics:**  
  *How does multi-agent coordination affect observed decision trajectories, difficulty transitions, and baseline PPO divergence under controlled replay conditions?*  
  **Auditor Assessment:** **FULLY SUPPORTED.** Directly evaluated via Experiment XA (160 replay sessions across 12 conditions). Establishes trajectory smoothing ($-2.67$ level changes, $-1.88$ reversals) and baseline divergence ($-0.226$ PPO agreement).

- **RQ2 — Value of Agent Specialization:**  
  *Does decomposing Strategy and Coaching into distinct bounded-authority agents offer measurable behavioral, operational, or decision-quality advantages over a unified controller?*  
  **Auditor Assessment:** **FULLY SUPPORTED WITH CRITICAL NEGATIVE FINDING.** Directly evaluated via Condition $M_3$ trajectory invariance ($160/160$ sessions identical), metamorphic decision equivalence tests ($\mathbb{P} = 1.0$), and dispatch serialization benchmarking ($+1.04$\,ms latency penalty). Establishes that specialization provides **zero algorithmic decision advantage** in deterministic settings; its benefits are purely architectural (modularity, bulkhead fault containment).

- **RQ3 — Coordination Mechanisms & Threshold Sensitivity:**  
  *Which architectural mechanisms account for the observed coordination behaviors, and under what parameter ranges do they operate?*  
  **Auditor Assessment:** **FULLY SUPPORTED.** Directly evaluated via Experiment XC (960 sessions across $\tau \in [0.0, 0.9]$), peer messaging ablation ($M_5$), and guardrail disagreement analysis. Identifies threshold gating as the primary mechanism preventing unarbitrated oscillation collapse.

---

## 3. Contribution Audit: Novelty vs Reality

| Proposed Contribution | Supported by Evidence? | Classification | Auditor Critical Evaluation |
|:---|:---:|:---:|:---|
| **1. Bounded-Authority Multi-Agent Architecture** | **YES** | Genuine Architecture Contribution | Typed Pydantic schemas, forbidden key authority boundaries, and unidirectional peer messaging between Strategy and Coaching agents. |
| **2. Trajectory Dynamics & Smoothing** | **YES** | Genuine Empirical Finding | Stateful weakness tracking alters 100% of replay trajectories, reducing rapid oscillation ($-2.67$ level changes, $-1.88$ reversals). Properly caveated as trajectory smoothing, NOT student learning. |
| **3. The Limits of Specialization (Negative Finding)** | **YES** | Genuine Scientific Contribution | Proves that agent specialization does not improve decision quality under deterministic rules ($\mathbb{P}=1.0; M_3 \equiv M_1$). Disproves the common assumption that multi-agent decomposition inherently improves decision quality. |
| **4. Threshold Gating as Stability Mechanism** | **YES** | Genuine Empirical Finding | Experiment XC demonstrates that $\tau=0.0$ leads to unarbitrated collapse ($2.225$ changes, $0.014$ agreement), while $\tau \in [0.5, 0.8]$ provides an invariant operating plateau. |
| **5. 8-Cluster Structure & Cluster $k=1$ Vulnerability** | **YES** | Genuine Methodological Finding | Transparently reports Field & Welsh cluster bootstrap CIs and identifies that proactive probing is driven entirely by Cluster $k=1$ (+4.75 turns), with zero effect in Clusters 0 and 2–7. |
| **6. Student Learning / Pedagogical Efficacy** | **NO** | Excised / Over-claim | Properly excised from manuscript. Replay evaluates pre-recorded evaluator scores; candidate skill acquisition was never measured. |
| **7. Live LLM Generation Quality** | **NO** | Unexecuted Limitation | Properly acknowledged in Limitations. No live LLM ran during replay; subjective LLM coaching differences remain unresolved. |
