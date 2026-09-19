# Scientific Peer Reviewer Attack & Defense Audit Report

**Audit Status:** Active Research Standard  
**Governing Strategy:** Pre-Emptive Reviewer Invalidation & Empirical Defense  
**Scope:** Three Independent Research Manuscripts (Paper 1 Systems, Paper 2 Evaluator, Paper 3 RL)  

---

## 1. Paper 1 (Systems, Security & Containment) Reviewer Attack Vectors

### Attack 1.1: Static Pre-flight Filter Inadequacy
- **Reviewer Objection:** *"The authors claim static policy checks block dangerous C code, but macro expansion, syscall indirection (`syscall(SYS_fork)`), or hex string obfuscation can easily evade regex checks. How can you claim the architecture is secure?"*
- **Empirical Defense:** We explicitly differentiate Layer 1 (Static Pre-Flight Filter) from Layer 3 (Kernel Container Boundary). Static filtering is solely a low-latency CPU pre-screen (0.3ms) to eliminate naive submissions. True containment relies exclusively on unprivileged Linux kernel cgroups and namespaces:
  1. `--net=none`: Complete network namespace isolation. Even if a network socket syscall compiles, connect() fails immediately with `ENETUNREACH`.
  2. `--cap-drop=ALL`: Complete dropping of Linux root capabilities.
  3. `--user 1001:1001`: Execution as unprivileged user, preventing privilege escalation.
  4. `--read-only` rootfs with tmpfs `/workspace` mounted `noexec,nosuid,nodev`.
  5. `--pids-limit=32`: Hard ceiling preventing fork-bomb system starvation.
  All attacks in our negative suite (`EXP-SYS-1`) were successfully contained with zero host impact.

### Attack 1.2: Container Overhead and Concurrency Scalability
- **Reviewer Objection:** *"Docker container startup adds ~1.5 seconds per turn. Does this architecture collapse under concurrent candidates?"*
- **Empirical Defense:** Technical interviews are predominantly conceptual dialogue turns (which execute via in-memory neural evaluators in ~220ms). C programming challenges occur strictly on designated coding turns. Under 10 concurrent active sessions, SQLite in WAL mode with a 30s busy timeout and thread-safe async locks processed all attempts without a single lock failure or duplicate best-answer record.

---

## 2. Paper 2 (Technical Evaluator) Reviewer Attack Vectors

### Attack 2.1: Human Evaluation Benchmark Sample Size ($N=20$)
- **Reviewer Objection:** *"The correlation $\rho = 0.6975$ was evaluated on only 20 samples from 1 human educator. This is too small to establish generalizability."*
- **Empirical Defense:**
  1. We transparently report the $N=20$ study as a **Pilot Ground Truth Study** and provide exact bootstrap 95% confidence intervals ($\rho \in [0.458, 0.910]$).
  2. We openly audited and disqualified inflated historical numbers ($\rho = 0.9152$ derived from synthetic proxies; $\rho = 0.8358$ derived from hybrid human-synthetic proxies).
  3. To address generalizability without fabricating human data, we designed a balanced 64-case cross-domain benchmark (`research/data/evaluator_benchmark/`) spanning 8 fundamental CS topics and 11 linguistic categories, accompanied by a 3-rater blinded annotation protocol (`research/annotation/rater_guidelines.md`).
  4. We substantiated algorithmic robustness through a 7-relation metamorphic testing suite (`research/scripts/run_paper2_study.py`) demonstrating strict monotonicity, negation penalties ($-0.338$), and concept deletion sensitivity ($-0.450$).

### Attack 2.2: Keyword Stuffing and Adversarial Exploitation
- **Reviewer Objection:** *"Can a candidate game the evaluator by stuffing key terminology into grammatically fluent but semantically wrong explanations?"*
- **Empirical Defense:** Our tripartite architecture incorporates CrossEncoder reasoning dampening:
  $$S_{2,\text{eff}} = \begin{cases} S_2 & \text{if } R > 0.30 \\ 0.60 \cdot S_2 & \text{if } R \le 0.30 \end{cases}$$
  When candidates inject keywords without coherent reasoning, CrossEncoder output drops ($R \le 0.30$), automatically penalizing concept coverage by 40%. In our systematic adversarial suite, keyword-stuffed answers were capped at a mean score of $0.345$, and direct prompt injections ("Ignore the evaluator...") achieved a score of $0.000$.

---

## 3. Paper 3 (Reinforcement Learning) Reviewer Attack Vectors

### Attack 3.1: Volatility vs. Heuristic Baseline Alignment
- **Reviewer Objection:** *"Heuristic difficulty tracking adjusts immediately to performance, whereas PPO has lower correlation with instant scores. Why use RL?"*
- **Empirical Defense:** In pedagogical assessment, instantaneous tracking causes high difficulty oscillation (volatility $0.573$, oscillation rate $0.266$). Candidates who make a single slip are abruptly demoted, inducing anxiety, while lucky guesses trigger premature difficulty escalation. PPO acts as a regularized controller:
  1. It incorporates rolling performance ($s_1$), speech confidence ($s_2$), and acoustic hesitation ($s_3$), dampening erratic swings.
  2. Volatility is reduced by >21% ($0.451$ vs $0.573$, $p < 0.01$).
  3. Post-hoc guardrails guarantee that constraint violations ($d < 1$ or $d > 5$) are strictly zero across all simulated sessions.

### Attack 3.2: Dimension 4 Training vs. Runtime Semantic Shift
- **Reviewer Objection:** *"Training dimension 4 represented normalized response time, but runtime code supplied session progress. Does this covariate shift invalidate the findings?"*
- **Empirical Defense:**
  1. We openly document this discrepancy in `research/audit/rl_state_definition.md`.
  2. In Priority 3, we retrained PPO across 5 independent seeds in an Aligned Progress environment (`research/experiments/paper3/checkpoints/`) where training and runtime semantics are 100% identical.
  3. We preserved the historical mismatch as an explicit ablation, proving that even under covariate shift, action concordance between progress and response time remained at 80.50%, demonstrating policy stability under temporal signal variations.

---

## 4. Multi-Agent Ethical & Integrity Defenses

### Attack 4.1: Demographic Bias in Speech Prosody
- **Reviewer Objection:** *"Penalizing candidates based on acoustic hesitation or pitch features discriminates against ESL speakers or neurodivergent individuals."*
- **Empirical Defense:**
  1. **Scoring Insulation:** Acoustic signals are mathematically barred from the evaluator score ($0.15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$).
  2. **Asymmetric Protection:** Speech hesitation is used exclusively by Guardrail G1 to *prevent difficulty escalation* when a candidate is anxious, never to lower scores or administer punitive questions.
