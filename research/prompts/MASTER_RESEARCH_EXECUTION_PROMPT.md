# PREPAIred — Active Master Research Execution Directives

**Purpose:** This document records the active operating principles, scientific constraints, and publication mandates for PREPAIred research execution.

---

## 1. Absolute Operating Rules
1. **Repository as Source of Truth:** Never invent human participants, survey responses, or unrun benchmarks. Differentiate authentic human pilot ratings (=20$, single educator) from synthetic LLM proxies.
2. **Scoring Insulation:** Speech prosody is completely excluded from technical scoring (.15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$). Speech hesitation is used solely as an anxiety-protective dampener to stabilize difficulty, never to penalize candidates.
3. **Deterministic Evaluation:** The LLM is completely excluded from the technical scoring path. Scoring is deterministic SBERT + FAISS + CrossEncoder + GCC.
4. **Defense-in-Depth:** Systems security relies on Linux kernel container primitives (--cap-drop=ALL, --net=none, non-root UID 1001, tmpfs, read-only rootfs).

---

## 2. Three-Paper Target Venues & Scopes
- **Paper 1 (Systems & Security):** Target ATIS 2026 (Bengaluru, Nov 7 deadline) / IEEE Access. Core topics: Architecture, Docker sandbox isolation, negative security tests, latency profiling, fault tolerance.
- **Paper 2 (Technical Evaluator):** Target ICTCS 2026 (Ahmedabad) / IEEE ToE. Core topics: Tripartite scoring, reasoning dampening ( \le 0.30$), threshold sensitivity ($\theta = 0.42$), metamorphic testing, human pilot benchmark ($\rho = 0.7400$).
- **Paper 3 (Adaptive RL):** Target SmartCom 2027 (Goa, Jan 2027) / ICMLSC 2027. Core topics: 6D state representation, PPO controller, 21% volatility reduction vs heuristic baselines, speech perturbation robustness, dimension 4 domain transfer.
