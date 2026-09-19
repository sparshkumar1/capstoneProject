# Peer Review Simulation & Defensive Audit

Simulated peer review across four distinct technical domains to evaluate manuscript robustness, anticipate objections, and formulate concrete defenses.

---

## Reviewer A: Systems & Security Specialist (Target: ATIS 2026 / IEEE Access)

### Critique 1: Static Pre-flight Filter Inadequacy
> *"The authors claim pre-flight security filtering blocks dangerous code, but C syntax allows header aliasing, macro obfuscation, and runtime syscall invocation. How can the authors guarantee containment?"*
- **Empirical Defense:** We explicitly document in Table 2 (`EXP-SYS-1`, `SEC-02`) that static regex filtering alone allowed socket headers to pass (`accepted`). Our core claim is that static checks are merely latency optimizations to reject trivial probes early; the **actual containment boundary** relies entirely on kernel primitives: `--cap-drop=ALL`, `--net=none`, non-root UID 1001, tmpfs `/workspace`, and `--read-only` rootfs. The failure of SEC-02 at Layer 1 was completely mitigated at Layer 3, demonstrating true defense-in-depth.

### Critique 2: Sandbox Fork-Bomb & Latency Overhead
> *"Docker container startup incurs significant latency (>1.5s per compilation). In a multi-candidate setting, does this scale?"*
- **Empirical Defense:** Our latency profiling (Table 1, `EXP-SYS-2`) confirms container startup is the primary bottleneck (median 1527 ms). However, code execution in PREPAIred occurs only on dedicated coding turns, not conversational conceptual turns (which evaluate in 167 ms). Process exhaustion is strictly bounded by `--pids-limit=32` and 128MB RAM, preventing any container from starving the host OS.

---

## Reviewer B: NLP & Evaluation Specialist (Target: ICTCS 2026 / IEEE ToE)

### Critique 1: Human Evaluation Benchmark Size ($N=20$)
> *"Evaluating answer scoring on only 20 answers across 4 questions is too small to establish statistical significance or generalizability."*
- **Empirical Defense:** We explicitly treat the 20-item set as a rigorous pilot validation and report exact bootstrap 95% confidence intervals ($\rho \in [0.458, 0.910]$). We openly differentiate authentic single-educator ratings from synthetic proxy ratings. Furthermore, we supplement the pilot study with a 5-relation metamorphic testing suite (`EXP-EVAL-5`) evaluating semantic invariance, monotonicity, and falsification across controlled transformations, proving algorithmic robustness without relying solely on sample size.

### Critique 2: Vulnerability to Sophisticated Keyword Stuffing
> *"While ungrammatical word bags might be penalized, what happens when candidates embed keywords inside grammatically coherent but vacuous sentences?"*
- **Empirical Defense:** Our metamorphic testing (`META-02`, `META-03`) uncovered that structured keyword collocations can achieve partial reasoning scores ($R \approx 0.46 - 0.52$). However, our ScoreValidator rules cap the final score unless mandatory concepts pass the semantic alignment threshold, ensuring candidates cannot reach 'Good' or 'Excellent' grades purely through ungrounded keyword injection.

---

## Reviewer C: Reinforcement Learning Specialist (Target: SmartCom 2027 / ICMLSC)

### Critique 1: High Alignment in Heuristic vs PPO
> *"The heuristic baseline achieves higher score-difficulty alignment ($r=0.962$) than PPO ($r=0.303$). Why is PPO necessary?"*
- **Empirical Defense:** In educational assessment, high instantaneous alignment ($r=0.962$) is actually a **failure mode**: the heuristic violently escalates difficulty after a single lucky answer and plunges it after a single slip, resulting in high volatility ($0.573$) and jarring difficulty whiplash. PPO balances challenge and candidate persistence, significantly reducing volatility by 21% ($0.451$ vs $0.573$, $p < 0.01$) and preventing candidate discouragement.

### Critique 2: Dimension 4 Training vs Runtime Discrepancy
> *"The training simulator populated dimension 4 with normalized response time, whereas runtime uses session progress. Does this covariate shift invalidate the learned policy?"*
- **Empirical Defense:** We conducted a formal counterfactual transfer experiment (`EXP-RL-2`). When the policy is tested under `runtime_progress`, action agreement with the training regime is **80.50%**, and the mean final difficulty discrepancy is negligible ($0.020$ units). This demonstrates that the policy treats dimension 4 as a pacing progression prior, maintaining stability under runtime transfer.

---

## Reviewer D: Education & AI Ethics Specialist (Target: IEEE ToE / HCII)

### Critique 1: Demographic Bias in Speech Prosody
> *"Using speech hesitation and confidence to modulate interview pacing risks penalizing non-native speakers, neurodiverse candidates, or individuals with speech differences."*
- **Empirical Defense:** We enforce two inviolable architectural invariants:
  1. **Scoring Insulation:** Speech features are completely isolated from technical grading ($0.15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$). A hesitant candidate receives the exact same score as a fluent speaker giving the same explanation.
  2. **Asymmetric Anxiety Protection:** Guardrail G2 uses hesitation exclusively to *prevent difficulty escalation* when a candidate is anxious, never to increase difficulty or lower scores.

### Critique 2: Hallucination in Automated Feedback
> *"LLM-generated feedback can invent nonexistent errors or hallucinate feedback that contradicts the candidate's actual answer."*
- **Empirical Defense:** In PREPAIred, the LLM is completely excluded from technical scoring. Feedback generation is strictly grounded in structured claims produced by the deterministic evaluator. Furthermore, `FeedbackAgent` validates LLM outputs against boilerplate fluff and contradiction, automatically falling back to deterministic templates if the LLM output deviates from evaluator evidence (`EXP-LLM-1`).
