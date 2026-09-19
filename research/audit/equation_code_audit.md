# Mathematical Formulation vs. Code Implementation Audit

**Audited Git Head Commit:** `9cfd34f278de8cc6b2810a4855b571b6b7264495`  
**Scope:** Mathematical verification of all scoring, RL, acoustic, and validation formulas against the active Python codebase.

---

## 1. Technical Evaluator Formulation

### 1.1 Base Scoring Formula
**Published Equation:**
$$\text{Score}_{\text{base}} = w_1 S_1 + w_2 S_{2,\text{eff}} + w_3 R + B - P$$
where $w_1 = 0.15$, $w_2 = 0.35$, $w_3 = 0.50$, $B$ is positive rubric bonus, and $P$ is mistake penalty.

**Code Verification:**
- **File:** `services/evaluator/app.py`, Lines 488–492
- **Implementation:**
  ```python
  s2_eff = s2 if reasoning_score > 0.30 else s2 * 0.60
  base_score = 0.15 * s1 + 0.35 * s2_eff + 0.50 * reasoning_score
  final_score = base_score + bonus - penalty
  final_score = max(0.0, min(1.0, final_score))
  ```
- **Status:** **EXACT MATCH**. Weights sum to $1.00$. Range clamped to $[0.0, 1.0]$.

### 1.2 Anti-Keyword Stuffing Concept Dampening
**Published Equation:**
$$S_{2,\text{eff}} = \begin{cases} S_2 & \text{if } R > 0.30 \\ 0.60 \cdot S_2 & \text{if } R \le 0.30 \end{cases}$$

**Code Verification:**
- **File:** `services/evaluator/app.py`, Line 488
- **Purpose:** If candidate emits keywords matching the FAISS concept index ($S_2 > 0.70$) but CrossEncoder cross-attention detects zero mechanistic explanatory entailment ($R \le 0.30$), $S_2$ is dampened by 40%.
- **Status:** **EXACT MATCH**.

### 1.3 Concept Matching & Threshold
**Published Equation:**
$$S_2 = \frac{1}{|C|} \sum_{c \in C} \mathbb{I}\left( \max_{s \in \text{Sentences}} \cos(\mathbf{e}_s, \mathbf{e}_c) > \theta \right)$$
where $\theta = 0.42$.

**Code Verification:**
- **File:** `services/evaluator/app.py`, Line 39 (`CONCEPT_THRESHOLD = 0.42`) and Lines 445–458.
- **Index:** `faiss.IndexFlatIP(384)` over normalized SBERT embeddings.
- **Status:** **EXACT MATCH**.

---

## 2. Score Validator Guardrail Equations

### 2.1 Mandatory Concept Gating
**Rule:** If candidate fails mandatory core invariants, final score is capped:
$$\text{Score}_{\text{validated}} = \begin{cases} \min(\text{Score}_{\text{raw}}, 0.65) & \text{if } \neg \text{mandatory\_pass} \\ \text{Score}_{\text{raw}} & \text{otherwise} \end{cases}$$

**Code Verification:**
- **File:** `agents/validation/score_validator.py`, Lines 58–63
- **Status:** **EXACT MATCH**.

### 2.2 Execution Failure Penalty (Coding Sandbox)
**Rule:** When C code fails to compile or crashes at runtime:
$$\text{Score}_{\text{coding}} = \text{Score}_{\text{eval}} \times 0.70$$

**Code Verification:**
- **File:** `agents/validation/score_validator.py`, Lines 72–78
- **Status:** **EXACT MATCH**.

---

## 3. Speech & Acoustic Signal Processing

### 3.1 Hesitation Score
**Formula:**
$$\text{Hesitation} = \text{clip}\left( 0.4 \cdot \frac{T_{\text{pause}}}{T_{\text{total}}} + 0.3 \cdot \min\left(1, \frac{N_{\text{pause}}}{8}\right) + 0.3 \cdot \min\left(1, \frac{N_{\text{fillers}}}{5}\right), 0, 1 \right)$$

**Code Verification:**
- **File:** `agents/audio/transcriber.py`, Lines 188–205
- **Status:** **EXACT MATCH**.

### 3.2 Confidence Score
**Formula:**
$$\text{Confidence} = \text{clip}\left( 0.5 \cdot \text{WPM\_norm} + 0.3 \cdot (1 - \text{Hesitation}) - 0.2 \cdot \min(1, N_{\text{uncertainty}} \times 0.25), 0, 1 \right)$$

**Code Verification:**
- **File:** `agents/audio/transcriber.py`, Lines 210–230
- **Status:** **EXACT MATCH**.

---

## 4. Reinforcement Learning State & Reward Formulations

### 4.1 6D Observation Vector Construction
**Published Representation:**
$$\mathbf{s}_t = \left[ \text{perf}_t, \overline{\text{perf}}_{t-3:t}, \text{conf}_t, \text{hes}_t, \text{progress}_t, \text{diff}_t \right]^T \in [0, 1]^6$$

**Code Verification:**
- **File:** `agents/strategy/hybrid_orchestrator.py`, Lines 45–62 (`build_rl_observation`)
- **Dimensions:**
  - $s_0$: $\text{perf} \in [0, 1]$ (latest validated turn score)
  - $s_1$: $\overline{\text{perf}} \in [0, 1]$ (exponential/rolling mean of scores)
  - $s_2$: $\text{conf} \in [0, 1]$ (speech acoustic confidence)
  - $s_3$: $\text{hes} \in [0, 1]$ (speech hesitation)
  - $s_4$: $\text{progress} = \frac{\text{turn}}{N_{\text{questions}}} \in [0, 1]$ (at runtime) vs. $\frac{\Delta t}{2 \cdot (3 + 6 \cdot d)}$ (in training)
  - $s_5$: $\text{diff} = \frac{d - 1}{4} \in [0, 1]$
- **Status:** **DOCUMENTED MISMATCH ON DIMENSION 4** (see `rl_state_alignment.md`).

### 4.2 Reward Formulation
**Formula in Environment:**
$$R(s, a, s') = R_{\text{ZPD}}(\text{perf}') - \lambda_{\text{osc}} \cdot \mathbb{I}(\text{action oscillation}) - \lambda_{\text{oob}} \cdot \mathbb{I}(d \notin [1, 5])$$
where:
$$R_{\text{ZPD}}(\text{perf}') = \begin{cases} +1.0 & \text{if } 0.60 \le \text{perf}' \le 0.85 \text{ (Flow Zone / ZPD)} \\ -0.5 \cdot (0.60 - \text{perf}') & \text{if } \text{perf}' < 0.60 \text{ (Frustration)} \\ -0.3 \cdot (\text{perf}' - 0.85) & \text{if } \text{perf}' > 0.85 \text{ (Boredom / Under-challenge)} \end{cases}$$

**Code Verification:**
- **File:** `rl/env/interview_env.py`, Lines 160–195
- **Status:** **EXACT MATCH**.

---

## 5. Persistence & Deterministic Best-Primary Selection

### 5.1 Compound Sorting Tuple
**Formula:**
$$\text{Best Attempt} = \arg\max_{a \in \mathcal{A}_{\text{primary}}} \Big( \text{validated\_score}(a), \; -|\text{missing\_concepts}(a)|, \; \text{attempt\_number}(a) \Big)$$

**Code Verification:**
- **File:** `services/storage/database.py`, Lines 142–155
- **SQL Implementation:**
  ```sql
  SELECT id FROM question_attempts
  WHERE candidate_id = ? AND question_id = ? AND attempt_type = 'primary'
  ORDER BY score DESC, length(missing_concepts) ASC, attempt_number DESC
  LIMIT 1
  ```
  followed by Python in-memory verification on exact parsed JSON concept array lengths.
- **Status:** **EXACT MATCH**.
