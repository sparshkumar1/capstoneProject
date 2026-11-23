# Research Positioning, Related Work & ADCoM Track Alignment (Phase Two)
**Project:** PREPAIred — ADCoM 2027  
**Candidate Working Directory:** `paper/adcom2027_final_v9_candidate/`  
**Date:** 3 October 2026  
**Auditor:** Principal Research Engineer & Methodological Reviewer  

---

## 1. Research Gap & Core Problem Definition

Many modern LLM-based applications label their components "multi-agent" simply because distinct functional roles (e.g. evaluator, feedback generator, difficulty adapter) are invoked sequentially by a central controller. However, true multi-agent systems—even under weak notions of agency (Wooldridge & Jennings 1995: autonomy, social ability, reactivity, pro-activeness)—introduce stateful, asynchronous interactions where unconstrained agent outputs can silently corrupt application state, bypass safety guardrails, or hallucinate pedagogical feedback.

### The Specific Research Problem
When stateful advisory agents (e.g. a Strategy Agent proposing difficulty adaptations and follow-up probes from a private weakness ledger, and a Coaching Agent tailoring feedback depth and tone) are integrated into a high-stakes spoken technical interview practice system:
1. *Who owns authoritative state?* Can advisory agents overwrite evaluator scores or violate interview bounds?
2. *How are agent failures contained?* What happens when an agent outputs malformed JSON, times out, injects stale version numbers, or hallucinates ungrounded concepts?
3. *What coordination mechanisms keep the record faithful?* Does deterministic arbitration and schema validation protect system invariants without sacrificing adaptive difficulty?

---

## 2. ADCoM 2027 Track Alignment

The call for papers for the 31st International Conference on Advanced Computing and Communications (ADCoM 2027, Springer CCIS) identifies three tracks relevant to agentic systems:

### Primary Fit: **Track 2 — Agent-Native Development and Lifecycle Engineering**
- **Track Scope:** Covers architectural frameworks, runtime governance, contract engineering, lifecycle dependability, and state management for agent-native systems.
- **Alignment Rationale:** This manuscript’s primary contribution is an empirical systems study of **bounded-authority agent architecture and runtime governance**. It demonstrates how explicit write-authority partitioning, deterministic arbitration, typed contracts, and optimistic concurrency versioning maintain state consistency under 1,760 injected fault scenarios. This directly addresses lifecycle engineering for agent systems.

### Secondary Fit: **Track 5 — Preemptive Agentic Security and Resilience**
- **Track Scope:** Covers fault tolerance, adversarial resilience, guardrail enforcement, and failure containment in agent networks.
- **Alignment Rationale:** The manuscript provides a detailed fault-containment matrix (Table 2 and Table 6) evaluating 11 fault classes (adversarial valid proposals, circuit breakers, timeout handling, forbidden-key injection). It specifically demonstrates how arbitration prevents guardrail bypass (38/40 bypassed without arbitration vs 0/40 with arbitration).

### Non-Recommended Fit: Track 3 — Core Multi-Agent Systems and Collaborative Reasoning
- **Rationale for Non-Alignment:** Track 3 emphasizes decentralized multi-agent learning, game-theoretic negotiation, and emergent social reasoning. The PREPAIred architecture is explicitly centralized (the Hub is the sole state writer), the agents are rule-based rather than negotiating LLMs, and PPO is centralized single-agent RL. Claiming a Track 3 fit would misrepresent the system.

---

## 3. Novelty Matrix: State of the Art vs PREPAIred

| Related Work | Architectural Model | Evaluation Setting | Fault / Adversarial Model | What PREPAIred v8 Adds | Remaining Gap |
|:---|:---|:---|:---|:---|:---|
| **AutoGen** (Wu et al. 2023) | Conversational, peer-to-peer message passing | Collaborative coding / conversational tasks | None (assumes honest, compliant agents) | Bounded authority matrix, deterministic arbitration, strict state-writer isolation | Fully decentralized agent negotiation |
| **MetaGPT** (Hong et al. 2024) | Standard Operating Procedure (SOP) pipeline | Software engineering benchmarks | None | Fault injection at service seams; empirical evaluation of guardrail bypass | Automatic SOP synthesis |
| **MAST Taxonomy** (Cemri et al. 2025) | Taxonomical survey of multi-agent LLM failures | Literature review and failure catalog | Observational failures in multi-agent LLM systems | Empirical implementation and ablation of safeguards designed to contain MAST-style failures | Dynamic multi-turn negotiation |
| **Huang et al.** (ICML 2025) / **MAS-FIRE** (Jia et al. 2026) | Multi-agent collaboration with faulty agents | Mathematical reasoning, synthetic tasks | Prompt rewriting, message drop, adversarial injection | Real-world spoken interview pipeline architecture; integration of learned evaluator + frozen PPO + deterministic guardrails | Multi-model agent ensembles |
| **Zara** (Yazdani et al. 2025) / **Virtual Interviewers** (Gomez et al. 2025) | Monolithic LLM-based technical interview coach | Student mock interviews, human surveys | None | Authority separation; fault containment; empirical isolation of threshold effects | Live candidate learning efficacy studies |

---

## 4. Bibliographic Audit of All 20 References

All 20 references cited in the v8/v9 manuscript were audited against official publisher records and verified for citation context:

1. **`wj95`** — Wooldridge, M., Jennings, N.R.: Intelligent agents: theory and practice. *Knowledge Engineering Review* 10(2), 115–152 (1995). DOI: `10.1017/S0269888900008122`. (Establishes weak agency criteria).
2. **`ss75`** — Saltzer, J.H., Schroeder, M.D.: The protection of information in computer systems. *Proceedings of the IEEE* 63(9), 1278–1308 (1975). DOI: `10.1109/PROC.1975.9939`. (Principle of least privilege and fail-safe defaults).
3. **`alrl04`** — Avižienis, A., Laprie, J.-C., Randell, B., Landwehr, C.: Basic concepts and taxonomy of dependable and secure computing. *IEEE Trans. Dependable and Secure Computing* 1(1), 11–33 (2004). DOI: `10.1109/TDSC.2004.2`. (Dependable systems fault-error-failure taxonomy).
4. **`marl`** — Buşoniu, L., Babuška, R., De Schutter, B.: A comprehensive survey of multiagent reinforcement learning. *IEEE Trans. SMC-C* 38(2), 156–172 (2008). (Distinguishes centralized PPO from MARL).
5. **`mast`** — Cemri, M., et al.: Why do multi-agent LLM systems fail? arXiv:2503.13657 (2025). (Multi-agent LLM failure modes).
6. **`cp34`** — Clopper, C.J., Pearson, E.S.: The use of confidence or fiducial limits illustrated in the case of the binomial. *Biometrika* 26(4), 404–413 (1934). (Exact binomial confidence intervals).
7. **`fw07`** — Field, C.A., Welsh, A.H.: Bootstrapping clustered data. *JRSS-B* 69(3), 369–390 (2007). DOI: `10.1111/j.1467-9868.2007.00593.x`. (Cluster-bootstrap methodology).
8. **`safe`** — García, J., Fernández, F.: A comprehensive survey on safe reinforcement learning. *JMLR* 16, 1437–1480 (2015). (Safe RL and safety envelopes).
9. **`virt`** — Gomez, N., Batham, S.S., Volonte, M., Do, T.D.: Virtual interviewers, real results... *CSCW Companion* (2025). (Interview practice domain).
10. **`metagpt`** — Hong, S., et al.: MetaGPT: Meta programming for a multi-agent collaborative framework. *ICLR* (2024). (Role-based pipeline architectures).
11. **`resil`** — Huang, J.T., et al.: On the resilience of LLM-based multi-agent collaboration with faulty agents. *ICML PMLR 267*, 26202–26226 (2025). (Fault injection in agent collaboration).
12. **`masfire`** — Jia, J., et al.: MAS-FIRE: Fault injection and reliability evaluation for LLM-based multi-agent systems. arXiv:2602.19843 (2026). (Reliability benchmarks).
13. **`nygard`** — Nygard, M.T.: Release It! Design and Deploy Production-Ready Software. Pragmatic Bookshelf (2007). (Circuit breakers and bulkheads).
14. **`sb3`** — Raffin, A., et al.: Stable-Baselines3: Reliable reinforcement learning implementations. *JMLR* 22(268) (2021). (PPO implementation framework).
15. **`ppo`** — Schulman, J., et al.: Proximal policy optimization algorithms. arXiv:1707.06347 (2017). (PPO policy baseline).
16. **`chase`** — Vaishampayan, S., Brown, C.: Will you trust me more than ChatGPT? Evaluating LLM-generated code feedback... *CHASE* (2025). (Candidate trust in automated feedback).
17. **`shield`** — Alshiekh, M., Bloem, R., Ehlers, R., et al.: Safe reinforcement learning via shielding. *AAAI* (2018). (Deterministic arbitration shielding RL decisions).
18. **`autogen`** — Wu, Q., et al.: AutoGen: Enabling next-gen LLM applications via multi-agent conversation. arXiv:2308.08155 (2023). (Conversational multi-agent baseline).
19. **`zara`** — Yazdani, N., Mahajan, A., Ansari, A.: Zara: An LLM-based candidate interview feedback system. arXiv:2507.02869 (2025). (Interview feedback baseline).
20. **`judge`** — Zheng, L., et al.: Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. *NeurIPS 36* (2023). (Biases of LLM judges).
