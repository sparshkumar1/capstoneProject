# SCORING.md — Authoritative Scoring & Final Evaluation Specification

**Document Version:** 1.1.0 (Stage 6 Clarification & Audit)
**System:** PrepAIred Automated Technical Interview Pipeline

---

## 1. Architecture & Core Philosophy

The PrepAIred evaluation pipeline implements **Technical Correctness Dominance**:
1. **Authoritative Technical Scoring Anchor:** Technical accuracy, concept coverage, and semantic reasoning are evaluated by the authoritative Stage 1 Multi-Task Cross-Encoder evaluator to produce $S_{\text{tech}} \in [0.0, 1.0]$. Concept coverage and reasoning are **internal inputs** to $S_{\text{tech}}$ and are **not double-counted** in final score aggregation.
2. **Timing as an Auxiliary Modifier ($f_{\text{time}}$):** Response timing modifies the technical score through a bounded additive term $f_{\text{time}}(\tau, S_{\text{tech}}) \in [-0.10, +0.03]$. Timing can never compensate for incorrect or incomplete answers.
3. **Transparent Metric Reporting:** Component scores (Technical, Concept Coverage, Reasoning, Communication, Timing Quality, and Coding Performance) are preserved individually in candidate state and the final report (`component_breakdown`) for transparent review and research ablation studies.

---

## 2. Component Definitions & Roles

| Component Name | Symbol | Source Engine | Range | Role in System |
|---|---|---|---|---|
| **Authoritative Technical Score** | $S_{\text{tech}}$ | Cross-Encoder Evaluator | $[0.0, 1.0]$ | **Foundational Score Anchor.** Captures semantic match ($S_1$), concept coverage ($S_2$), and reasoning/entailment ($R$). |
| **Concept Coverage** | $S_{\text{concept}}$ | Evaluator Rubric / $S_2$ | $[0.0, 1.0]$ | *Descriptive analytical metric* (internal to $S_{\text{tech}}$, exposed in reports; not double-counted). |
| **Reasoning Quality** | $S_{\text{reasoning}}$ | Cross-Encoder NLI / $R$ | $[0.0, 1.0]$ | *Descriptive analytical metric* (internal to $S_{\text{tech}}$, exposed in reports; not double-counted). |
| **Communication Score** | $S_{\text{comm}}$ | Audio / Transcript Analyzer | $[0.0, 1.0]$ | *Descriptive behavioral metric* (clarity, appropriate length, low filler count). |
| **Timing Quality Score** | $S_{\text{time}}$ | `QuestionTimer` | $[0.0, 1.0]$ | *Descriptive pacing index* (measures candidate time efficiency on $[0, 1]$; not added directly to score). |
| **Timing Modifier** | $f_{\text{time}}$ | `QuestionTimer` | $[-0.10, +0.03]$ | **Additive modulation term** applied to $S_{\text{tech}}$ to yield $S_{\text{final}}$. |
| **Coding Performance** | $S_{\text{code}}$ | Docker / Process Sandbox | $[0.0, 1.0]$ | *Test case pass rate* ($N_{\text{passed}} / N_{\text{total}}$) for coding questions. |

---

## 3. Mathematical Formulation of the Final Evaluation Score

### 3.1 Per-Question Final Score ($S_{\text{final}, i}$)

For question $i$, let $S_{\text{tech}, i} \in [0.0, 1.0]$ be the authoritative evaluator score, and let $\tau_i = \frac{t_{\text{elapsed}, i}}{t_{\text{allowed}, i}}$ be the normalized response time ratio.

$$S_{\text{final}, i} = \text{clip}\Big( S_{\text{tech}, i} + f_{\text{time}}(\tau_i, S_{\text{tech}, i}),\ 0.0,\ 1.0 \Big)$$

### 3.2 Timing Score vs. Timing Modifier

To avoid double-counting, the system maintains two separate timing concepts:
- **`timing_score` ($S_{\text{time}} \in [0.0, 1.0]$):** A normalized descriptive index for reporting and pacing feedback.
- **`timing_modifier` ($f_{\text{time}} \in [-0.10, +0.03]$):** The actual bounded score adjustment applied to $S_{\text{tech}}$.

#### Formulation of Timing Modifier $f_{\text{time}}(\tau_i, S_{\text{tech}, i})$:

$$f_{\text{time}}(\tau_i, S_{\text{tech}, i}) = \begin{cases}
+ \min(\delta_{\text{fast}},\ \delta_{\text{fast}} \cdot S_{\text{tech}, i}) & \text{if } \tau_i \le \theta_{\text{fast}} \text{ and } S_{\text{tech}, i} \ge \theta_{\text{score}} \\
0.0 & \text{if } \theta_{\text{fast}} < \tau_i \le 1.00 \\
- \delta_{\text{overrun}} \cdot \min(1.0,\ \tau_i - 1.0) & \text{if } \tau_i > 1.00 \text{ (overtime)}
\end{cases}$$

#### Formulation of Descriptive Timing Score $S_{\text{time}}(\tau_i)$:

$$S_{\text{time}}(\tau_i) = \begin{cases}
1.00 & \text{if } \tau_i \le 0.70 \\
1.00 - 0.15 \cdot \left(\frac{\tau_i - 0.70}{0.30}\right) & \text{if } 0.70 < \tau_i \le 1.00 \quad (1.00 \to 0.85) \\
\max\Big(0.00,\ 0.85 - 0.50 \cdot (\tau_i - 1.00)\Big) & \text{if } \tau_i > 1.00 \quad (0.85 \to 0.00)
\end{cases}$$

> [!NOTE]
> $S_{\text{time}}(\tau)$ is $C^0$-continuous for all $\tau \ge 0$, smoothly degrading from $1.00$ at $\tau \le 0.70$ to $0.85$ at $\tau = 1.00$, and reaching $0.00$ at $\tau = 2.70$ ($170\%$ overtime).

### 3.3 Overall Session Aggregation

$$S_{\text{overall}} = \frac{1}{N} \sum_{i=1}^N S_{\text{final}, i}, \qquad S_{\text{raw\_technical}} = \frac{1}{N} \sum_{i=1}^N S_{\text{tech}, i}$$

---

## 4. Configurable Engineering Parameters (Not Empirically Claimed)

The timing modifier parameters are **configurable engineering defaults** designed to guarantee technical correctness dominance:

| Parameter | Default Value | Role | Empirical Status |
|---|---|---|---|
| $\delta_{\text{fast}}$ | $0.03$ ($+3\%$) | Maximum bonus for fast, highly accurate answers | *Engineering parameter* (configurable) |
| $\delta_{\text{overrun}}$ | $0.10$ ($-10\%$) | Maximum penalty for severe overtime | *Engineering parameter* (configurable) |
| $\theta_{\text{fast}}$ | $0.50$ | Fast answer cutoff ($50\%$ of allowed duration) | *Engineering parameter* (configurable) |
| $\theta_{\text{score}}$ | $0.70$ | Score threshold required to unlock speed bonus | *Engineering parameter* (configurable) |

> [!IMPORTANT]
> These parameters are explicit engineering design constraints, **not empirically validated constants** derived from human psychometric trials.

---

## 5. Invariant: Fast Wrong vs. Slower Correct

Under this formulation, an incorrect or weak answer ($S_{\text{tech}} < 0.70$) receives $f_{\text{time}} = 0.0$:

- **Candidate A (Fast + Wrong):** $S_{\text{tech}} = 0.20, \tau = 0.20 \implies f_{\text{time}} = 0.000 \implies S_{\text{final}} = \mathbf{0.200}$
- **Candidate B (Slower + Correct):** $S_{\text{tech}} = 0.90, \tau = 1.50 \implies f_{\text{time}} = -0.050 \implies S_{\text{final}} = \mathbf{0.850}$

$$\mathbf{S_{\text{final}}(\text{Fast + Wrong})} = 0.200 \ll 0.850 = \mathbf{S_{\text{final}}(\text{Slower + Correct})}$$

---

## 6. Report Structure for Research & Ablation

Reports outputted by `InterviewOrchestrator._generate_report()` retain:
```json
{
  "overall_score": 0.865,
  "raw_technical_score": 0.875,
  "component_breakdown": {
    "technical_score": 0.875,
    "concept_score": 0.860,
    "reasoning_score": 0.880,
    "communication_score": 0.910,
    "timing_score": 0.920,
    "coding_score": null,
    "final_overall": 0.865
  },
  "timing_analysis": {
    "avg_timing_score": 0.920,
    "net_timing_modifier": -0.010,
    "response_timing": [...]
  }
}
```
