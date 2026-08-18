# Stage 19 — Master Claim Language Revision & Calibration Table

**Document ID:** `STAGE-19-CLAIM-REVISION-TABLE`
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform
**Target Manuscript:** [`docs/paper_draft_ieee.md`](paper_draft_ieee.md)
**Purpose:** Granular word-level audit of all potentially sensitive or overclaiming language across the entire manuscript to ensure scientific rigor and peer-review defensibility.

---

## 1. Master Word-Level Claim Calibration Matrix

| # | Checked Term / Phrase | Context in Paper | Underlying Evidence | Status | Action Taken | Scientifically Calibrated Wording in Manuscript |
|:---:|---|---|---|:---:|:---:|---|
| **1** | *"improves candidate performance"* | Abstract / Introduction | EXP-1, EXP-4 (Simulated personas only; no longitudinal human student trials) | `UNSUPPORTED FOR HUMANS` | **`WEAKENED`** | *"produces statistically distinguishable adaptive difficulty progressions in simulation ($\rho = +0.1572$)."* |
| **2** | *"superior difficulty adaptation"* | Sec. XIV-A (EXP-1) | EXP-1 Wilcoxon test vs. Fixed and Rule-based ($p < 0.001$) | `SUPPORTED IN SIMULATION` | **`CALIBRATED`** | *"achieved statistically significant positive adaptation correlation ($\rho = +0.1572 \pm 0.08$) compared to static and heuristic baselines."* |
| **3** | *"validated answer evaluator"* | Sec. XIV-B (EXP-2) | EXP-2: 20 benchmark items graded by 3 blinded human raters ($\alpha = 0.8255, \rho = 0.8358$) | `SUPPORTED ON BENCHMARK` | **`CALIBRATED`** | *"demonstrated strong correlation ($\rho = 0.8358, p = 4.46 \times 10^{-6}$) with blinded human ratings on a 20-sample pilot benchmark."* |
| **4** | *"evaluator accuracy"* | Abstract / Sec. XIV-B | EXP-2 Spearman correlation and MAE | `REPLACED WITH CORRELATION` | **`CALIBRATED`** | *"evaluator rank agreement and error metrics ($\rho = 0.8358, \text{MAE} = 0.2585$)"* (Avoided raw "accuracy" percentage). |
| **5** | *"Qwen is superior"* | Sec. XIV-C (EXP-3) | EXP-3 tri-condition benchmark on Tesla T4 GPU | `PARTIALLY SUPPORTED (GROUNDING ONLY)` | **`CALIBRATED`** | *"Qwen-7B delivers significantly higher transcript lexical grounding ($0.2496$ vs. $0.0383$), while non-LLM structured recovery achieves higher rubric gap coverage ($100.0\%$ vs. $72.5\%$) and lower latency (<0.05s)."* |
| **6** | *"personalization improves learning"* | Sec. XIV-D (EXP-4) | EXP-4 question repetition and trajectory divergence in simulation | `UNSUPPORTED FOR HUMANS` | **`WEAKENED`** | *"candidate-state selection eliminates question repetition ($0.0\%$) and produces distinct difficulty trajectory divergence ($d = 14.21$) between candidate profiles in simulation."* |
| **7** | *"guarantees sandbox security"* | Sec. XI (Docker Sandbox) | Docker cgroup limits (128MB RAM, 32 PIDs, 2.0s timeout, `--net=none`) | `SECURITY LIMITATION ACKNOWLEDGED` | **`CALIBRATED`** | *"enforces strict containerized resource governance (memory, CPU, timeout, and network isolation) to mitigate common execution hazards."* |
| **8** | *"human-validated platform"* | Abstract / Conclusion | Only human evaluator rater agreement is validated ($\alpha = 0.8255$) | `OVERCLAIM IF APPLIED TO WHOLE PLATFORM` | **`RESTRICTED`** | *"human validation was conducted for evaluator scoring reliability on pilot technical answers; whole-system human pedagogical efficacy represents future longitudinal work."* |
| **9** | *"proves multi-agent efficacy"* | Sec. XIV-E (EXP-5) | EXP-5 leave-one-out subsystem isolation | `PROOF TERMINOLOGY FORBIDDEN` | **`CALIBRATED`** | *"demonstrates clean behavioral isolation across decoupled subsystems without cross-modal crashes."* |
| **10** | *"real-time speech recognition"* | Sec. XII (WhisperX) | WhisperX forced alignment on CPU/GPU | `SUPPORTED BY IMPLEMENTATION` | **`KEPT IN CONTEXT`** | *"transcribes candidate audio and extracts speech rate (WPM) and pause metrics ($\Delta t \ge 0.45\text{s}$) using WhisperX forced alignment."* |

---

## 2. Terminology Guardrails Summary

1. **"Improves" / "Superior":** Permitted ONLY when referencing explicit statistical tests against defined baselines in controlled conditions (e.g., PPO vs. Fixed $\rho$, Qwen vs. Generic grounding). Prohibited when referencing general human student learning.
2. **"Accuracy":** Replaced with precise statistical metrics (Spearman $\rho$, Pearson $r$, MAE, RMSE).
3. **"Validated":** Restricted strictly to:
   - Evaluator inter-rater reliability on the 20-sample pilot benchmark ($\alpha = 0.8255$).
   - Docker sandbox execution limits.
   - Guardrail G1–G6 override logic.
4. **"Proves" / "Guarantees":** Completely eliminated from empirical claims.
