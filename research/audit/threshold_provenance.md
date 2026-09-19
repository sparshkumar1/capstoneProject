# Concept Matching Threshold Provenance: $\theta = 0.30$ vs $\theta = 0.42$

**Audited Commit:** `9cfd34f`  
**Purpose:** Reconcile documentation claims of $\theta = 0.42$ against the active codebase definition $\theta = 0.30$.

---

## 1. Executive Forensic Finding

1. **Active Implementation Truth ($\theta = 0.30$):**
   - In `services/evaluator/app.py:95`:
     ```python
     CONCEPT_THRESHOLD = 0.30  # single source of truth
     ```
   - Consumed directly by `concept_detection()` on lines 116 and 126 to compute both the $S_2$ ratio (`groups_covered / len(best_scores)`) and the boolean `covered` status in concept details.
   - Evaluated in `research/tables/table_eval_threshold.md` where $\theta = 0.30$ is explicitly designated as the **Selected Operating Point** yielding $\rho = 0.6975$ on the pilot human evaluation set.
2. **Historical Proposal ($\theta = 0.42$):**
   - Appears only in narrative markdown documentation (e.g. `docs/stage16_*` and early draft limitation notes).
   - Was proposed in August 2026 as a theoretical threshold calibrated on synthetic samples, but was **never committed to the evaluation engine in `services/evaluator/app.py`**.

**Scientific Decision:** The canonical, frozen threshold for all current experiments, Paper 2 tables, and production runtime is **$\mathbf{\theta = 0.30}$**.

---

## 2. Threshold Traceability Matrix

| Threshold | Code / File Location | Purpose & Consumer | Selection Method | Dataset Used | Active Status |
|:---:|:---|:---|:---|:---|:---:|
| **0.30** | `services/evaluator/app.py:95, 116, 126` | Concept coverage ($S_2$) and detail matching | Sensitivity sweep across $[0.15, 0.60]$ | Development & pilot analysis | **ACTIVE PRODUCTION & RESEARCH GROUND TRUTH** |
| **0.30** | `services/evaluator/app.py:377` | Reasoning dampening threshold ($R \le 0.30 \implies S_2 \times 0.60$) | Adversarial keyword-stuffing defense | Pilot adversarial test cases | **ACTIVE PRODUCTION & RESEARCH GROUND TRUTH** |
| **0.40** | `services/evaluator/app.py:260` | Mandatory concept threshold (`MANDATORY_THRESHOLD`) | Hard gate for critical constraints | Expert rubric authoring | **ACTIVE PRODUCTION & RESEARCH GROUND TRUTH** |
| **0.42** | `docs/paper_draft_ieee_access.md:Limitations` | Mentioned as historical calibration | Exploratory proposal | Synthetic pilot | **SUPERSEDED HISTORICAL PROPOSAL** |

---

## 3. Publication Directive for Paper 2
- Formally report $\theta = 0.30$ as the frozen operating parameter for FAISS concept detection.
- Cite the threshold sensitivity curve (`research/figures/eval_threshold_sensitivity.png`) demonstrating stability across the range $[0.25, 0.35]$.
