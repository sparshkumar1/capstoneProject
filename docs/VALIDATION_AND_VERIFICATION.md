# PrepAIred — Validation and Verification (V&V) Package (Stage 23)

**Document ID:** `VALIDATION-AND-VERIFICATION-STG23`
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform
**Target Manuscript:** [`docs/paper_draft_ieee.md`](paper_draft_ieee.md)
**Execution Date:** 2026-08-17
**Purpose:** Formal Tripartite Separation of Software Verification, Experimental Validation, and Human Validation

---

## 1. The Tripartite V&V Framework

PrepAIred establishes an explicit, transparent boundary separating software correctness from empirical mechanism testing and human participant validation:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. SYSTEM VERIFICATION ("Did we build the software correctly?")             │
│    - Automated Test Suites: 177 backend passed, 1 skipped, 7 frontend passed│
│    - Microservice API Contracts & Structured JSON Schemas                   │
│    - Docker Sandbox Cgroups (128MB RAM, 32 PIDs, 2.0s, --net=none)          │
│    - Offline Speech Pipeline: WAV decoding, energy alignment, prosody       │
│    - Qwen 1.5B GGUF local CPU engine & deterministic fallback attribution   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. EXPERIMENTAL VALIDATION ("Does the mechanism behave as hypothesized?")   │
│    - EXP-1: PPO adaptive difficulty progression in simulation (n=150 runs)  │
│    - EXP-2: Multi-component evaluator rank correlation with ground-truth   │
│    - EXP-3: Generative Qwen-7B vs. Structured Feedback trade-offs (Tesla T4)│
│    - EXP-4: Deduplication & trajectory divergence in simulation (n=60 runs) │
│    - EXP-5: Leave-one-out subsystem isolation & behavioral decoupling (n=70)│
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. HUMAN VALIDATION ("Do real people benefit from the platform?")           │
│    - [HUMAN VALIDATED]: Inter-rater reliability among 3 blinded human       │
│      experts on 20-sample pilot benchmark (Krippendorff alpha = 0.8255).    │
│    - [NOT YET VALIDATED / FUTURE WORK]: Candidate interview skill           │
│      improvement, hiring success rates, anxiety reduction, and longitudinal │
│      classroom learning gains.                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Tier 1 — Software System Verification Matrix

| Component Verified | Verification Method | Pass Criteria | Observed Execution Result | Status |
|---|---|---|---|:---:|
| **Evaluator Pipeline** | Unit Tests + 8 Standalone Cases | Bounds $[0, 1]$, anti-keyword dampening, mandatory cap | $S_1 \in [0, 1], S_2 \in [0, 1], R \in [0, 1]$, cap enforced at $0.60$ | **`VERIFIED`** |
| **Strategy & PPO Policy** | Gymnasium Invariants + SB3 | 6D state $[0, 1]^6$, discrete actions $\{0, 1, 2\}$, G1–G6 overrides | State bounded, policy weights loaded from `ppo_final.zip` | **`VERIFIED`** |
| **Docker C Sandbox** | Subprocess Execution Harness | Memory $\le 128\text{MB}$, PIDs $\le 32$, timeout $2.0\text{s}$, network disabled | Fork bombs killed, segfaults trapped, valid solutions scored | **`VERIFIED`** |
| **Offline Speech Pipeline**| WAV Test Harness (`verify_offline_speech.py`) | Timestamps, WPM, hesitation, confidence extracted | Ingested 48k samples, speech 2.43s, hes 0.26, conf 0.81 | **`VERIFIED`** |
| **Live Microphone Stream** | Physical Hardware Input | Real-time audio stream | Microphone hardware unavailable in automated CLI | **`NOT VERIFIED (HARDWARE)`** |
| **Qwen 1.5B GGUF Engine** | `llama-cpp-python` Integration | Load $<5\text{s}$, generation $<5\text{s}$, contract match | Loaded in 1.02s, mean latency 2.195s, 100% JSON contract match | **`VERIFIED`** |
| **Question Selector** | 3-Level Deduplication Engine | ID, normalized string, and Jaccard token overlap $\ge 0.75$ | $0.0\%$ repetition across multi-turn sessions | **`VERIFIED`** |
| **Production E2E Multi-Turn**| Integrated Interview Flow | Multi-turn closed-loop trace | Session `test_e2e_20260817_204726` completed, report generated | **`VERIFIED`** |

---

## 3. Tier 2 — Experimental Validation Summary

- **EXP-1 (Adaptive Difficulty Controller):** Validated in simulation ($n=150$ runs). PPO with safety guardrails produced statistically significant positive adaptation correlation ($\rho = +0.1572 \pm 0.08$) compared to Fixed ($\rho = 0.0, p = 6.15 \times 10^{-4}$) and Rule-Based ($\rho = -0.2572, p = 5.30 \times 10^{-8}$).
- **EXP-2 (Evaluator Component Decomposition):** Validated on 20 curated technical answers graded by 3 blinded human raters ($n=140$ scorings). The Full Pipeline achieved strong rank agreement ($\rho = 0.8358, p = 4.46 \times 10^{-6}, \text{MAE} = 0.2585$).
- **EXP-3 (Formative Feedback Tri-Condition Benchmark):** Validated on NVIDIA Tesla T4 GPU ($n=60$ evaluations). Generative Qwen-7B exhibited higher lexical transcript grounding ($0.2496$ vs. $0.0383, p = 2.56 \times 10^{-3}$), while deterministic structured recovery achieved strictly superior rubric gap coverage ($100.0\%$ vs. $72.5\%, p = 9.11 \times 10^{-4}$) at sub-50ms latency.
- **EXP-4 (Personalization & Deduplication):** Validated in simulation ($n=60$ sessions). 3-level deduplication completely eliminated question repetition ($0.0\%$ vs. $6.0\%, p < 0.001$), with distinct difficulty trajectory divergence ($d = 14.21$) between candidate ability profiles.
- **EXP-5 (Leave-One-Out Subsystem Ablation):** Validated across 7 isolated conditions ($n=70$ sessions). Subsystems operated orthogonally without cascading crashes.

---

## 4. Tier 3 — Human Validation Boundaries

```
================================================================================
CRITICAL HUMAN VALIDATION BOUNDARY
================================================================================
[HUMAN VALIDATED]:
- Blinded human expert ratings on the 20-sample pilot benchmark
  (Krippendorff alpha = 0.8255 across 3 independent human raters).

[NOT YET VALIDATED (EXPLICITLY DOCUMENTED AS FUTURE WORK)]:
- Candidate interview skill improvement.
- Candidate hiring success rates.
- Long-term knowledge retention.
- Candidate anxiety reduction.
- Longitudinal classroom educational efficacy.
================================================================================
```
