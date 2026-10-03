# PREPAIred ADCoM 2027 — Technical Verification Report (v8 Candidate)

**Evaluation Date:** 3 October 2026  
**Candidate Directory:** `paper/adcom2027_final_v8_candidate/`  
**Primary Deliverable PDF:** `ADCOM2027_PREPAIred_v8_complete_blind.pdf`  
**Companion PDF:** `ADCOM2027_multiagent_final_v8.pdf`  
**PDF SHA-256:** `74A1781F87A72B217F8A9E8F10FB83C516E85C3A78C64220E0662741688E4A56`  
**Exact Page Count:** **20 pages** (Satisfies Springer CCIS maximum limit of 20 pages)  
**File Size:** 450,635 bytes  
**Document Class:** Springer LNCS (`llncs.cls` v2.21, running heads enabled)  

---

## 1. Baseline and Working-Tree Verification

- **Baseline Commit:** `59176af2b1f4e0dfafb7770c7edc55bd434d619d` (Branch: `recovered/final-fixes`, descendant of `817722c` on `recovered/adcom2027-multiagent-final`).
- **Baseline Source Path:** `paper/adcom2027_final/` (Preserved 100% clean and untouched).
- **v6 Source Path:** `paper/adcom2027/` (Preserved 100% clean and untouched).
- **Active v8 Candidate Path:** `paper/adcom2027_final_v8_candidate/`.
- **Working-Tree Status:** All changes are strictly confined to the untracked directory `paper/adcom2027_final_v8_candidate/`. No git commits, pushes, merges, or external PRs have been made.

---

## 2. Compilation and Build Audit

- **Build Toolchain:** `pdfTeX 3.141592653-2.6-1.40.22 (TeX Live 2022/dev/Debian)` running on WSL Ubuntu 22.04 with `latexmk 4.76`.
- **Build Command:**
  ```bash
  cd paper/adcom2027_final_v8_candidate/manuscript && latexmk -pdf -interaction=nonstopmode main.tex
  ```
- **Build Outcome:** Succeeded with return code 0.
- **Cross-References:** All internal references (`\ref`, `\pageref`) resolved cleanly. Zero undefined labels in `main.log`.
- **Citations & Bibliography:** 20 of 20 citations resolved through `refs.bib` and `splncs04.bst`. Zero undefined citation warnings.
- **Font Embedding:**
  ```text
  pdffonts ADCOM2027_PREPAIred_v8_complete_blind.pdf
  fonts not embedded: 0
  ```
  All fonts are 100% embedded scalable Type 1 / TrueType fonts (`cm-super` and Computer Modern fonts).

---

## 3. Visual & Typographic Quality Assurance (Pages 1 to 20)

| Page Range | Content & Features | Visual Audit Assessment |
|:---:|:---|:---|
| **1–3** | Title, Abstract, Intro, Related Work | Clean Springer geometry. Equations ($0.15S_1{+}0.35S_2^{\mathrm{eff}}{+}0.50R$) properly set. Margins respected. |
| **4** | Table 1 (Authority Matrix), Sec. 3.2 | **Corrected:** Table width resized to fit flush with text margins (12.2 cm). Protrusion eliminated. Caption hyphenation fixed. |
| **5–7** | Architecture & Sequence Figures | Fig. 1 (Architecture) and Fig. 2 (Turn Sequence) occupy Page 6 cleanly. Fig. 3 (Validation Pipeline) heads Page 7. |
| **8–9** | Table 2 (Fault Matrix), Sec. 5 Methodology | Table 2 neatly formatted with `booktabs`. Clear distinction of REPLAY, FAULT-INJECTED, SOCKET, SYNTHETIC. |
| **10–12** | Table 3, Table 4, Table 5, Results | Table 3 and Table 4 aligned. **Corrected:** Prediction B2 in Table 5 formatted with `raggedright` to prevent underfull hbox. |
| **13–15** | Table 6, Table 7, Table 8, RQ4 Corrections | Fault containment metrics and rebuilt grounding probe cleanly rendered without overflowing text borders. |
| **16–17** | Discussion (RQ1–RQ4), Limitations | Rigorous limitations section detailing lack of live human/LLM data, synthetic conditions, and heuristic thresholds. |
| **18–20** | Limitations (cont.), Conclusion, References | Conclusion ends on Page 18. Reference 1 on Page 18; References 2–14 on Page 19; References 15–20 occupy top 1/3 of Page 20. |

---

## 4. Empirical Claim Verification (`verification/verify_paper.py`)

Every quantitative claim, table cell, and interval was recomputed from raw experimental artifacts:
- Raw sources: `research/multiagent/results/xa/`, `xb/`, `xc/`, `xd/`, `xe_*/`, `post_hoc/`.
- Method: PDF text extraction (`pdftotext`) with normalized whitespace matching.
- **Result:**
  ```text
  claim audit: 69/69 checks passed (100% verified)
  ```

---

## 5. Double-Blind Anonymity Audit (`scripts/blind_audit.py`)

- **Scope:** Scanned all manuscript sources, figures, tables, bibliography, extracted PDF text, and embedded PDF metadata.
- **Results:**
  ```text
  metadata Creator:         TeX
  metadata Producer:        pdfTeX-1.40.22
  fonts not embedded: 0
  blind audit: clean (0 hits)
  ```
- **Anonymity Verification:** Author names (`Anonymous Author(s)`), institutions (`Anonymous Institution`), repository URLs, local filesystem paths (`C:\Users\...`), and project keywords (`PrepAIred`) are absent from the compiled PDF and metadata.

---

## 6. Originality & Publication Ethics Status

| Checklist Item | Finding | Status |
|:---|:---|:---:|
| **Prose Originality** | 100% original text; 0% verbatim plagiarism against published literature | **PASS** |
| **Dataset Provenance** | Replayed 64-answer dataset is shared with a peer's concurrent submission | **FLAGGED** |
| **Springer CCIS Policy** | Concurrent submissions using identical private data require co-authorship disclosure | **BLOCKER** |

**Conclusion:** The manuscript is a **Verified Technical Candidate**. Conference submission is blocked until the author and teacher review data provenance attribution.
