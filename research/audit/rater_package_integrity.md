# Human Rater Distribution Package Integrity & Equivalence Report

**Date:** September 2026  
**Status:** VERIFIED & FROZEN (Awaiting Human Gate 1 Approval)  
**Distribution Directory:** `research/annotation/distribution/`  
**Manifest:** `research/annotation/RATER_PACKAGE_MANIFEST.json`

---

## 1. Executive Verification Summary

All three standalone human evaluation packages (`PREPAIred_Rater_1_Package.zip`, `PREPAIred_Rater_2_Package.zip`, `PREPAIred_Rater_3_Package.zip`) were extracted, audited, and verified against `RATER_PACKAGE_MANIFEST.json`.

### Key Verification Findings:
1. **Cryptographic Equivalence:**
   - The primary annotation instrument (`RATING_SHEET_64_CASES.csv`) has an identical SHA-256 hash (`b1af0795f1daf4518152b2e6baed489739ceb4ce73c7cbe396c2262c93ca9023`, 21,039 bytes) across all three ZIP packages.
   - The qualitative scoring rubric (`SCORING_RUBRIC.md`) has an identical SHA-256 hash (`76d1b7426cfc8f2e73db5e1eed56b3f73d86114195c040b81abda8e20872e7c9`, 2,815 bytes) across all three ZIP packages.
2. **Intentional Differences:**
   - The only difference between packages is the salutation and rater designation in `README.md` (identifying Rater 1 as "Primary Technical Educator", Rater 2 as "Independent Technical Expert A", and Rater 3 as "Independent Technical Expert B").
3. **Absolute Blinding & Zero Leakage:**
   - No automated scores, model predictions, reference answers, or rubric concept vectors exist in the packages.
   - The rating sheet columns are strictly `['item_id', 'question_id', 'topic', 'question', 'candidate_answer', 'score_0_to_1', 'rater_comments']`.
   - Score and comments columns are completely empty strings.

---

## 2. Package Hash & File Verification Table

| Package ID | Distribution ZIP Archive | ZIP SHA-256 | ZIP Size | Contained File | File Size | File SHA-256 | Equivalence Status |
| :---: | :--- | :--- | :---: | :--- | :---: | :--- | :---: |
| **RATER_1** | `PREPAIred_Rater_1_Package.zip` | `f13569babbb23dff979333ca4a35dce8661717e3f8c2829cbda0a188469d5fa0` | 8,703 B | `README.md`<br>`SCORING_RUBRIC.md`<br>`RATING_SHEET_64_CASES.csv` | 1,009 B<br>2,815 B<br>21,039 B | `9c0b9413293482e8...`<br>`76d1b7426cfc8f2e...`<br>`b1af0795f1daf451...` | **MATCH** (Primary)<br>**IDENTICAL**<br>**IDENTICAL** |
| **RATER_2** | `PREPAIred_Rater_2_Package.zip` | `e1742099967816f23a86c87354e3291fdbaee68a591ed20a4c38d3f76b139fd5` | 8,707 B | `README.md`<br>`SCORING_RUBRIC.md`<br>`RATING_SHEET_64_CASES.csv` | 1,013 B<br>2,815 B<br>21,039 B | `2e83e9016e0b3010...`<br>`76d1b7426cfc8f2e...`<br>`b1af0795f1daf451...` | **MATCH** (Expert A)<br>**IDENTICAL**<br>**IDENTICAL** |
| **RATER_3** | `PREPAIred_Rater_3_Package.zip` | `8c7ba02e42e7ac1b9b7c624e8bb9aa6dff1c759ab986dc0dd874d57dc64f84c9` | 8,707 B | `README.md`<br>`SCORING_RUBRIC.md`<br>`RATING_SHEET_64_CASES.csv` | 1,013 B<br>2,815 B<br>21,039 B | `a293da45645bc6ae...`<br>`76d1b7426cfc8f2e...`<br>`b1af0795f1daf451...` | **MATCH** (Expert B)<br>**IDENTICAL**<br>**IDENTICAL** |

---

## 3. Human Gate 1 Hold Condition

**CRITICAL DIRECTIVE:**
In accordance with research protocol, these three ZIP files remain local in `research/annotation/distribution/`.  
**THEY MUST NOT BE TRANSMITTED, EMAILED, OR DISTRIBUTED TO RATERS UNTIL HUMAN GATE 1 IS EXPLICITLY APPROVED BY THE USER.**
