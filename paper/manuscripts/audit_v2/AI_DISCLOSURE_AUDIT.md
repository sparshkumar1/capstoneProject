# AI DISCLOSURE AUDIT (2026-09-21)

Question: because substantive AI assistance was used in the research work (Paper 1) and in manuscript preparation (all papers), does any target venue policy require disclosure, and do the manuscripts comply?

## 1. Policy findings
| Publisher | Verified? | Requirement |
|---|---|---|
| IEEE conference submissions | **Yes**, IEEE Author Center page read 2026-09-21 | AI-generated content (text, figures, images, code) disclosed in the acknowledgments: system identified, sections identified, level of use explained. Editing/grammar exception: not required, recommended. |
| Springer Nature (HCII LNCS/LNAI; ATIS/ICMLSC CCIS) | Summarized from search results; page not opened in this pass | LLMs are not authors; use documented in Acknowledgements/Introduction or Methods/Declarations; AI-assisted copy editing exempt |
| ACM SAC | Not read | UNVERIFIED |
| ICETC / HCII / ATIS own rules | Not found on the pages read | UNVERIFIED |
This is not "no-disclosure": the disclosure obligation is real for any IEEE- or Springer-published outcome.

## 2. Compliance of the current drafts
| Paper | What the draft says | Gap |
|---|---|---|
| P1 | Body: same-agent design/repair/re-test disclosed (V-B, VII); Section VIII one-sentence AI-assistance disclosure; ICETC port has an Acknowledgment placeholder citing the IEEE rule | Needs system/version, sections and level of use; not final |
| P2 | none in the manuscript | Add disclosure per venue; confirm no AI role in the ratings (record silent) |
| P3 | none in the manuscript | Add disclosure; confirm extent of AI role in X3 design/execution |
The brief says the disclosure must not make AI an author, must not exaggerate AI contribution, must not hide human review, and must not claim AI "merely proofread". `cross/AI_USE_DISCLOSURE_DRAFT.md` follows those four rules; each factual item is bracketed for author confirmation.

## 3. Risk
- Non-disclosure at an IEEE venue would contradict the stated policy.
- The overlap between "AI wrote the manuscript" and "AI ran the experiments" (Paper 1) makes the same-agent limitation a disclosure item as well as a validity item; Paper 1 already treats it that way.
- The human-review statement must be true; the drafts do not assert it.

## 4. Verdict
**YELLOW.** Draft disclosure exists; wording and facts are the authors' to confirm; venue text must be re-read at submission.
