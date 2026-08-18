# Stage 19 — Master Submission Checklist & Rejection Risk Matrix

**Document ID:** `STAGE-19-SUBMISSION-CHECKLIST`
**System:** PrepAIred Automated Technical Interview & Adaptive Assessment Platform
**Target Manuscript:** [`docs/paper_draft_ieee.md`](paper_draft_ieee.md)
**Target Venue Category:** Intelligent Tutoring Systems / Applied AI in Education (IEEE TLT, AIED, EDM, ICALT)

---

## 1. Top 10 Rejection Risks & Mitigation Matrix

| Rank | Potential Rejection Risk | Risk Severity | Concrete Evidence & Repository Reality | Implemented Paper Mitigation | Requires New Experiment? |
|:---:|---|:---:|---|---|:---:|
| **1** | *"No longitudinal human learning gain study."* | **HIGH** | Efficacy evaluated on simulated candidate personas (EXP-1, EXP-4) and pilot benchmark (EXP-2). | Explicitly scoped human validation to evaluator reliability on $n=20$ items ($\alpha = 0.8255$); longitudinal student retention trials framed as documented future work. | **`NO`** (Honest framing suffices for systems track). |
| **2** | *"Evaluator benchmark size is small ($n=20$ items)."* | **MEDIUM** | 20 curated technical answers graded by 3 blinded experts (140 scorings, $\alpha = 0.8255$). | Documented as a pilot calibration benchmark; reported exact standard errors and bootstrap CIs. | **`NO`** (Adequate for initial system validation). |
| **3** | *"PPO algorithm is standard; novelty is questionable."* | **MEDIUM** | Standard PPO with 6D continuous state and 3 discrete actions. | Positioned the contribution as an *integrated adaptive assessment framework* with hybrid guardrail shielding rather than pure RL algorithmic theory. | **`NO`** |
| **4** | *"LLM feedback evaluation uses lexical overlap proxies."* | **MEDIUM** | EXP-3 measures verbatim token overlap and rubric string matching. | Acknowledged in Threats to Validity as an automated lexical proxy rather than human pedagogical perception. | **`NO`** |
| **5** | *"Unquantized 7B LLM is too heavy for local consumer CPUs."* | **LOW** | Local CPU inference suffers from virtual memory thrashing (>22 min/turn). | Explicitly documented CPU limitations and demonstrated sub-50ms non-LLM structured recovery as an instant local alternative. | **`NO`** |
| **6** | *"Pseudoreplication in simulation runs."* | **LOW** | 10 seeds evaluated across 5 fixed synthetic candidate personas. | Explicitly defined the experimental unit as *simulated candidate sessions* and reported seed-level variance. | **`NO`** |
| **7** | *"Keyword stuffing resistance may not generalize."* | **LOW** | Evaluator tested on synthetic keyword-stuffed and semantic adversarial answers. | Formulated anti-keyword dampening ($S_{2,\text{eff}}$) and reported CrossEncoder reasoning entailment weights. | **`NO`** |
| **8** | *"Overclaiming terms (improves, superior) in text."* | **LOW** | Word-level claim audit conducted in Stage 17/19. | All occurrences calibrated to explicit statistical tests or weakened to simulation boundaries. | **`NO`** |
| **9** | *"Lack of reproducible code/checkpoints."* | **NONE** | Full repository includes one-click reproduction script (`scripts/reproduce_paper.py`) and raw datasets. | One-click reproduction documented in `REPRODUCIBILITY.md` and root `README.md`. | **`NO`** |
| **10** | *"Data fabrication or irreproducible numbers."* | **NONE** | 100% of numerical values in manuscript trace directly to raw JSON/CSV files. | Master traceability matrix provided in `PAPER_RESULTS_TRACEABILITY.md`. | **`NO`** |

---

## 2. Final Venue Submission Checklist

- [x] **Authoritative Manuscript Complete:** All 29 required sections present and structured in [`docs/paper_draft_ieee.md`](paper_draft_ieee.md).
- [x] **Tables Populated:** All 12 structured tables (Tables I–XII) contain verified empirical data.
- [x] **Publication Figures Generated:** All 8 high-resolution figures (Figures 1–8) rendered at 300 DPI in `research/results/figures/`.
- [x] **Traceability Parity:** 100% of numerical claims traceable to raw machine-readable data via [`docs/PAPER_RESULTS_TRACEABILITY.md`](PAPER_RESULTS_TRACEABILITY.md).
- [x] **Claims Calibration:** All 16 claim rows in [`docs/CLAIMS_CHECK.md`](CLAIMS_CHECK.md) aligned with evidence.
- [x] **Reproducibility Harness:** One-click script [`scripts/reproduce_paper.py`](../scripts/reproduce_paper.py) verified on Python 3.12.
- [x] **Security & Privacy Clean:** 0 API keys, passwords, or candidate PII.
- [x] **Portability Clean:** 0 hardcoded local machine paths.
- [x] **Automated Tests Passing:** 178 backend tests passed, 7 frontend tests passed (100% pass rate).

---

## 3. Final Publication Readiness Verdict

```
================================================================================
FINAL VERDICT: READY FOR SUBMISSION
(Recommended Track: Intelligent Tutoring Systems / Applied AI in Education)
================================================================================
```
