# Initial Repository and Artifact Audit (Phase Zero)
**Project:** PREPAIred — ADCoM 2027  
**Working Directory:** `paper/adcom2027_final_v9_candidate/`  
**Date:** 3 October 2026  
**Auditor:** Principal Research Engineer & Methodological Reviewer  

---

## 1. Repository Inventory & Provenance

| Property | Value / Path |
|:---|:---|
| **Absolute Repository Root** | `C:\Users\spars\Downloads\PrepAIred-recovery-review` |
| **Mirror Workspace** | `C:\Users\spars\Downloads\PrepAIred` |
| **Active Checked-Out Commit** | `4b2399c9cc8052ddf66c17f0584f74e607421b92` (`phase3/engineering`) |
| **Authoritative Multi-Agent Branch** | `recovered/final-fixes` (HEAD: `59176af2b1f4e0dfafb7770c7edc55bd434d619d`) |
| **Ancestor Freeze Commit** | `817722ca4dfa22947aa5a6a5e04b36f4e532ef65` (`recovered/adcom2027-multiagent-final`) |
| **Original Manuscript Baseline** | `paper/adcom2027_final/manuscript/main.tex` |
| **Existing v6 Candidate (Single-Agent)** | `paper/adcom2027/` (Preserved read-only) |
| **Existing v7 Candidate (Multi-Agent)** | `paper/adcom2027_final/` (Preserved read-only) |
| **Existing v8 Candidate Directory** | `paper/adcom2027_final_v8_candidate/` (Preserved read-only) |
| **Active Isolated Candidate Directory** | `paper/adcom2027_final_v9_candidate/` |

---

## 2. Forensic Investigation of Prior v8 Artifacts

Prior audit dossiers referenced two distinct compiled PDF artifacts from the v8 cycle:

### Artifact A: `ADCOM2027_PREPAIred_v8_complete_blind.pdf`
- **Location:** `paper/adcom2027_final_v8_candidate/ADCOM2027_PREPAIred_v8_complete_blind.pdf`
- **Exact File Size:** 450,635 bytes
- **Computed SHA-256:** `74A1781F87A72B217F8A9E8F10FB83C516E85C3A78C64220E0662741688E4A56`
- **Exact Page Count:** **20 pages**
- **Page Dimensions:** 612.0 × 792.0 pts (US Letter / standard TeX geometry, text width 12.2 cm)
- **Reference Count:** 20 references (includes Saltzer & Schroeder 1975 and Avižienis et al. 2004)
- **Visual Distribution:** References 15–20 occupy the top ~35% of Page 20. Zero blank pages.

### Artifact B: `ADCOM2027_multiagent_final_v8.pdf` (Earlier v8 Build)
- **Location:** Intermediate build prior to adding systems citations
- **Exact File Size:** 449,390 bytes
- **Computed SHA-256:** `29E0A425A23B904A7092CF7B52C616A11DF8AC072D797BDAB59F2EDAE20FB8DC`
- **Exact Page Count:** **19 pages**
- **Reference Count:** 18 references
- **Visual Distribution:** Reference 18 concluded at ~75% of Page 19.

### Historical v7 Artifact: `ADCOM2027_multiagent_blind.pdf`
- **Location:** `paper/adcom2027_final/ADCOM2027_multiagent_blind.pdf`
- **File Size:** 449,729 bytes
- **Computed SHA-256:** `9906864BB718F2FDA366056AA32CCF56A38E2916CD891C61C3F1294D74890041`
- **Page Count:** 19 pages (with 19.69 pt Table 1 margin protrusion on Page 4 and Prediction B2 underfull hbox on Page 12).

### Authoritative Artifact Decision
**Artifact A (`74A1781F...`) is the authoritative starting point.**  
*Rationale:*
1. It eliminates the 19.69 pt Table 1 margin protrusion and the Table 5 line-break badness present in v7.
2. It incorporates the two foundational systems references (Saltzer & Schroeder 1975 on least privilege; Avižienis et al. 2004 on dependable fault-error-failure taxonomy) specifically required by Section 8 of the Master Prompt.
3. At exactly 20 pages, it strictly conforms to the ADCoM 2027 maximum page budget (maximum 20 pages including references and appendices).

---

## 3. Working-Tree Safety Protocol

1. `paper/adcom2027/` (v6) is untouched and tracked in git.
2. `paper/adcom2027_final/` (v7) is untouched and committed at `59176af`.
3. `paper/adcom2027_final_v8_candidate/` is preserved as a static baseline.
4. All work in this cycle occurs exclusively within `paper/adcom2027_final_v9_candidate/`.
5. No git commits, pushes, merges, or external submissions will be initiated.
