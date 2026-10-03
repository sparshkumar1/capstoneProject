# PREPAIred ADCoM 2027 — Final Verification Report (v8 Candidate)

**Evaluation Date:** October 3, 2026  
**Candidate Directory:** `paper/adcom2027_final_v8_candidate/`  
**Target Manuscript:** `Bounded-Authority Agents in an Orchestrated Interview-Practice System: Coordination, Arbitration and Fault Containment`  
**Document Class:** Springer LNCS (`llncs.cls` v2.21, running heads enabled)  
**Primary PDF Deliverable:** `paper/adcom2027_final_v8_candidate/ADCOM2027_multiagent_final_v8.pdf`  
**PDF SHA-256:** `29E0A425A23B904A7092CF7B52C616A11DF8AC072D797BDAB59F2EDAE20FB8DC`  
**Exact Page Count:** **19 pages** (Budget: 19–20 pages max for Springer CCIS)  

---

## 1. Executive Summary & Readiness Verdict

| Audit Domain | Requirement | Result | Status |
|:---|:---|:---|:---:|
| **LaTeX Compilation** | Zero fatal errors, Type-1 fonts, zero missing styles | 19 pages, 449,390 bytes, pdflatex | **PASS** |
| **Visual & Typography** | No margin clipping, no overflow into margins, clean captions | Table 1 width fixed, Table 5 raggedright, captions clean | **PASS** |
| **Claim Verification** | 100% recomputation from raw results (`verify_paper.py`) | 69 of 69 quantitative claims verified | **PASS** |
| **Double-Blind Audit** | No names, emails, institutions, or project keywords (`blind_audit.py`) | 0 identifying strings, 0 un-embedded fonts | **PASS** |
| **Reference Integrity** | 18 valid peer-reviewed / preprint citations with verified metadata | 18 of 18 citations verified against indexes | **PASS** |
| **Merged-Agent Study** | Complete pre-registered design; zero unauthorised runs | Formally registered in `REVISION_REPORT_v8.md`; un-executed | **PASS** |
| **Publication Ethics** | Originality of 64-answer dataset shared with concurrent paper | **UNRESOLVED AUTHOR DECISION** | **BLOCKER** |

### **FINAL VERDICT: VERIFIED TECHNICAL CANDIDATE (NOT SUBMISSION-READY)**

> [!WARNING]
> This manuscript represents a **technically complete, empirically verified, and format-compliant candidate**. However, it **CANNOT be submitted** until the human authors resolve the publication ethics decision regarding the 64-answer evaluation dataset shared with a concurrent sister submission.

---

## 2. Verification Suite Results

### 2.1 Automated Claim Audit (`verification/verify_paper.py`)
- **Protocol:** Recomputed every statistical point estimate, confidence interval, table entry, and count from raw underlying JSONL, CSV, and bootstrap artifacts in `research/multiagent/results/`.
- **Audited Target:** Extracted text of built PDF (`ADCOM2027_multiagent_final_v8.pdf`).
- **Result:**
  ```text
  claim audit: 69/69 checks passed
  ```
  - XA comparison claims (level changes 15.12 to 12.45, reversals 11.74 to 9.87, PPO agreement 0.626 to 0.400, paired bootstrap intervals): **VERIFIED**
  - XB fault containment claims (1,760 sessions, 100% containment, 38/40 guardrail bypass without arbitration, 40/40 ungrounded leaks without check): **VERIFIED**
  - XC threshold sensitivity claims ($\tau \in \{0.0 \dots 0.9\}$, 5 of 5 pre-registered hypotheses supported): **VERIFIED**
  - XD grounding probe rebuild (47/47 and 64/64 unambiguous acceptances, 57/57 paraphrased unsupported credit): **VERIFIED**
  - RQ4 earlier audit corrections (13/14 predictions, malformed score narrowing, byte-reproducible historical configuration): **VERIFIED**

### 2.2 Double-Blind Compliance Audit (`scripts/blind_audit.py`)
- **Target:** All `.tex`, `.bib`, figures, tables, and the compiled binary PDF.
- **Identifier Scan:** Scanned for author names, emails, institutional affiliations, repository URLs, absolute home directory paths, grant numbers, and project identifiers (`PrepAIred`).
- **Font Audit:** Checked all embedded fonts using `pdffonts`.
- **Result:**
  ```text
  fonts not embedded: 0
  blind audit: clean (0 hits)
  ```

---

## 3. Typographic and Layout Adjustments Made in v8

1. **Table 1 (`tables/authority.tex`) Dimension Fix:**
   - *Problem in v7:* Table width was 14.5 cm (exceeding `\textwidth` of 12.2 cm by 19.69 pt), extending into the right margin.
   - *Resolution in v8:* Column widths adjusted to `1.5cm, 2.5cm, 2.3cm, 2.8cm, 2.0cm`. The table fits flush with text boundaries with zero margin clipping.
2. **Table 1 Caption Hyphenation Fix (`sec_arch.tex`):**
   - *Problem in v7:* Caption broke awkwardly across lines as `author-` and `ity; the hub commits.`.
   - *Resolution in v8:* Re-spaced file path and rephrased: `Neither agent has state-write authority; the hub commits alone.`
3. **Table 5 Prediction Column Wrapping (`tables/xb_pred.tex` & `xa_pred.tex`):**
   - *Problem in v7:* Prediction B2 generated an underfull hbox (`badness 10000`) due to inflexible justification around long programmatic variable names (`authority_violation>0`).
   - *Resolution in v8:* Converted prediction column to `>{\raggedright\arraybackslash}p{7.6cm}`.
4. **Verification Tooling Robustness (`verification/verify_paper.py` & `scripts/blind_audit.py`):**
   - *Resolution in v8:* Added multi-path PDF resolution so audit scripts seamlessly verify `ADCOM2027_multiagent_final_v8.pdf`.

---

## 4. Unresolved Blocker: The Originality & Dual-Submission Issue

### Context
All empirical evaluations in this manuscript (XA, XB, XC, XD) rely upon a replayed dataset of 64 constructed answer payloads across 8 question categories. This identical 64-answer set was concurrently utilized by a peer in another research paper.

### Why This Blocks Submission
- Plagiarism detection software tests for textual overlap; the prose of this paper is 100% original.
- However, standard academic publishing policies (including Springer CCIS and COPE guidelines) treat the concurrent submission of papers reporting experiments on the same private, unpublished dataset without formal disclosure as a dual-submission or data-sharing compliance issue.

### Clear Next Steps for Authors
1. **Public Repository Archival:** Place the 64-answer replay suite in an open repository (Zenodo, Hugging Face, or OSF) with a persistent DOI. Both papers can then independently cite this common benchmark as an external artifact.
2. **Author Alignment:** Ensure agreement between both research teams regarding authorship and priority of benchmark presentation.
3. **Submission Gate:** Once the benchmark citation approach is chosen, the manuscript can be finalized for conference submission.
