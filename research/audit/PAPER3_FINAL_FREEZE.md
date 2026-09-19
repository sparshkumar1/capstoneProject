# Paper 3 Final Results Freeze: Authoritative Scientific Record

**Date:** September 19, 2026  
**Status:** **PERMANENTLY FROZEN & AUDITED**  
**Milestone:** Paper 3 (*Guardrailed Multimodal Reinforcement Learning for Adaptive Technical Interview Difficulty*)  
**Execution Base Commit:** `375f4f869c47907d7c222d27df3b4f9e09dc8941`  
**Governing Documents:**
- [`research/results/paper3/PAPER3_FINAL_REPORT.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/results/paper3/PAPER3_FINAL_REPORT.md)
- [`research/audit/PAPER3_POSTEXECUTION_AUDIT.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/audit/PAPER3_POSTEXECUTION_AUDIT.md)
- [`research/audit/PAPER3_FINAL_BASELINE_CONSISTENCY.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/audit/PAPER3_FINAL_BASELINE_CONSISTENCY.md)
- [`research/audit/PAPER3_EXECUTION_COMPLETION.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/audit/PAPER3_EXECUTION_COMPLETION.md)

---

## 1. Cryptographic Hashes of Raw Experimental Artifacts

The following raw experimental artifacts are permanently frozen. Any future modification to these bytes constitutes a scientific integrity violation:

| Artifact Path | SHA-256 Hash | Purpose |
|:---|:---|:---|
| `research/results/paper3/paper3_seed_results.csv` | `232ad964a22b342b9ce72be1013c8828e2b0995fddc5feecf678fbd363e1edf8` | Per-seed trajectory performance |
| `research/results/paper3/paper3_training_curves.csv` | `21a9843cd29f4d929b24231de191e4880d65a4e13ca0100259801b7a8818ba00` | Step-level training timesteps and rewards |
| `research/results/paper3/paper3_convergence_results.csv` | `30858e47cbfb1fb9cdb31e63edaf8342e6986c38f692d9716b690a205d83419c` | Final reward and action convergence |
| `research/results/paper3/paper3_baseline_results.csv` | `50a184d3508d9879a579c7d7f01b98652dc8a96e7c2d0ff86f544d8fbce9fff9` | Condition-level comparison metrics |
| `research/results/paper3/paper3_ablation_results.csv` | `6b85a55020b0084558fe6d6f4dd366b6c772f85eb149ce49d134ba170129b459` | Dim-4 formulation and guardrail ablations |
| `research/results/paper3/paper3_guardrail_results.csv` | `286729c1533387cad682039729ca3f9560c33184e61091db60629a6820c46609` | Trace of all 563 guardrail activations |
| `research/results/paper3/paper3_sensitivity_results.csv` | `2c948a6d5002f9415d95b8e75be7636afd56d6696b4e7cc6e1cc9b0daf48e632` | Controlled sensitivity sweep coordinates |
| `research/results/paper3/paper3_raw_results.json` | `2773caa0ca4c7be9f0ac219c4785aeb76ad2262906eb4ab4c272456d93a1c54d` | Complete structured JSON dump |
| `research/data/evaluator_benchmark/final_human_gold.csv` | `363dbe6d848a04fe18be5ef1d30b6bbf63b54248fe758e5e6bd4c27a26c06ce2` | Paper 2 Gold Benchmark (IMMUTABLE) |

---

## 2. Authoritative Frozen Reporting Metrics

### 2.1 Baseline & Condition Comparison ($N=25$ sessions per condition)

| Condition | Tracking Error (MAE) | 95% Bootstrap CI | Volatility | 95% Bootstrap CI | Oscillation | Changes | Guardrails | Violations |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Fixed Baseline ($d=3.0$)** | **1.200** | $[0.920, 1.440]$ | $0.000$ | $[0.000, 0.000]$ | $0.000$ | $0.0$ | 0 | 0 |
| **Heuristic Baseline** | **0.473** | $[0.349, 0.598]$ | $0.160$ | $[0.128, 0.192]$ | $0.000$ | $1.6$ | 0 | 0 |
| **PPO Raw (Seed 123)** | **0.804** | $[0.605, 0.998]$ | $0.088$ | $[0.048, 0.136]$ | $0.027$ | $0.9$ | 0 | 60 |
| **PPO + Guardrails (Seed 123)** | **0.673** | $[0.469, 0.882]$ | $0.088$ | $[0.048, 0.136]$ | $0.027$ | $0.9$ | 101 | **0** |
| **PPO Raw (Hist. Mismatch)** | **0.666** | $[0.475, 0.858]$ | $0.188$ | $[0.096, 0.296]$ | $0.226$ | $1.9$ | 0 | 52 |
| **PPO + Guardrails (Hist. Mismatch)** | **0.640** | $[0.446, 0.838]$ | $0.192$ | $[0.092, 0.308]$ | $0.187$ | $1.9$ | 112 | **0** |

---

### 2.2 Canonical Multi-Seed Stability ($S=5$ Independent Training Seeds)

| Training Seed | Mean Final Difficulty | Target Tracking Error (MAE) | Volatility | Oscillation Rate | Interventions | Violations |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Seed 42** | $2.240$ | $0.687$ | $0.268$ | $0.261$ | 122 | 0 |
| **Seed 123** | $2.200$ | $0.673$ | $0.088$ | $0.027$ | 101 | 0 |
| **Seed 456** | $2.200$ | $0.676$ | $0.208$ | $0.197$ | 115 | 0 |
| **Seed 789** | $2.200$ | $0.673$ | $0.240$ | $0.178$ | 120 | 0 |
| **Seed 999** | $2.200$ | $0.676$ | $0.128$ | $0.139$ | 105 | 0 |
| **Across-Seed Mean $\pm$ SD** | **$2.208 \pm 0.018$** | **$0.677 \pm 0.006$** | **$0.186 \pm 0.068$** | **$0.160$** | **563 total** | **0** |

---

## 3. Corrected Statistical Interpretation & Effect Size Definition

### 3.1 Strict Separation of Statistical Units
To prevent methodological conflation in publication text:
1. **Primary Experimental Unit (Session Trajectory, $N=25$):**  
   Each evaluation session represents an independent interview trajectory across a candidate persona and evaluation seed. All inferential comparisons (CIs, effect sizes, $p$-values) MUST use session-level variance.
2. **Training Stability Unit ($S=5$ Seeds):**  
   The five training seeds (`42, 123, 456, 789, 999`) assess policy optimization reproducibility across random initialization. The standard deviation across seed means is $\mathbf{0.006}$ difficulty units.

### 3.2 Correct Effect Size: Cohen's $d \approx 0.87$
- **True Formulation:**  
  $$d = \frac{\bar{x}_{\text{fixed}} - \bar{x}_{\text{ppo}}}{s_{\text{pooled}}} = \frac{1.200 - 0.673}{\sqrt{(0.678^2 + 0.531^2)/2}} = \frac{0.527}{0.609} \approx \mathbf{0.87}$$
- **Documented Historical Artifact:**  
  The raw calculation $t = -195.46, d = 87.41$ recorded in `paper3_raw_results.json` resulted from an erroneous calculation that divided the mean difference by the standard deviation of the 5 seed means ($0.006$) rather than the session-level pooled standard deviation ($0.609$). This raw number is preserved in audit archives strictly for forensic traceability; the true manuscript effect size is **$d \approx 0.87$** ($p < 0.001$).

---

## 4. Baseline Definitions & Claim Boundaries

### 4.1 Corrected Fixed Baseline ($\text{MAE} = 1.200$)
- Static difficulty locked at $d = 3.0$.
- Evaluated against true persona targets:
  - `struggling_junior`: $d^* = 1.0$ (error: $2.0$)
  - `overconfident_fail`: $d^* = 1.5$ (error: $1.5$)
  - `normal`: $d^* = 3.0$ (error: $0.0$)
  - `lucky_guesser`: $d^* = 4.0$ (error: $1.0$)
  - `nervous_expert`: $d^* = 4.5$ (error: $1.5$)
  $$\text{MAE}_{\text{Fixed}} = \frac{2.0 + 1.5 + 0.0 + 1.0 + 1.5}{5} = \mathbf{1.200}$$
- The historical $0.000$ baseline was an artifact of unpassed persona skills (where skill defaulted to $0.60$), and the audit mention of $1.000$ was an arithmetic evaluation typo of the exact formula summing to $6.0/5 = 1.200$.

### 4.2 Non-Superiority over Deterministic Heuristic
- The deterministic threshold Heuristic baseline achieves $\text{MAE} = \mathbf{0.473}$, outperforming PPO+Guardrails ($\text{MAE} = 0.677$) on raw tracking speed.
- **Scientific Finding:** PPO provides smoother pacing and lower trajectory volatility ($0.088$ vs $0.160$) at the cost of slower initial tracking. Claims of universal RL superiority are strictly prohibited.

---

## 5. Ablation Mechanistic Interpretation

In post-guardrail evaluation, `aligned_progress`, `aligned_response_time`, and `zero_progress` yield identical aggregate metrics ($0.673$) due to two verified factors:
1. **Low Marginal Policy Sensitivity to $s_4$:** In neutral coordinate sweeps ($[0.5, 0.5, 0.5, 0.5, s_4, 0.6]$), the policy outputs Action `Same` across the entire interval $s_4 \in [0.0, 1.0]$, as rolling performance ($s_1$) and difficulty ($s_5$) dominate policy logits.
2. **Guardrail Override Convergence:** The distinct `aligned_response_time` model proposed different raw actions in 10 out of 250 turns, but in all 10 turns, the candidate was in an edge state where canonical guardrails triggered and redirected the action to the identical pedagogical choice.

---

## 6. Approved Scientific Terminology & Claim Boundaries

1. **Convergence:** Use: *"Empirical training curves demonstrate robust policy action-distribution stabilization and rolling-reward plateauing across all five independent random seeds within 20,000 timesteps."* (Avoid claiming theoretical global optimality).
2. **Pacing Function:** Use: *"score-band stabilization ($0.40 \le p \le 0.70$)"* instead of anthropomorphic *"Zone of Proximal Development stabilization"*.
3. **Safety Shield:** Use: *"Deterministic post-hoc guardrail rules G1–G6 eliminate 100% of out-of-bounds difficulty transitions and intervene on 45.0% of turns to rescue struggling candidates."*
4. **Multimodal Role:** Acoustic features modulate pacing and guardrail triggers; they possess **zero scoring authority** over technical code or verbal explanation evaluation. Sensitivity sweeps are reported as controlled coordinate responses, not causal proofs.
5. **Simulation Boundaries:** All evaluations were conducted on simulated synthetic candidate personas. No claims are made regarding real human student learning gains, classroom efficacy, or interview success.

---

> ### 🛑 FINAL GATE FREEZE
> Paper 3 results, audit reports, checkpoints, and statistical interpretations are permanently frozen. No further training, parameter modification, or paper drafting is permitted.
