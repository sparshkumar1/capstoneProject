# System paper — ethics, consent and data-handling checklist (2026-09-21)

**Status: BLOCKED. No human-participant data may be collected.** The institution's actual requirement is not known and could not be established from the repository: no ethics determination, approval, exemption or consent record for this or any other study exists in the files searched. The only related document is an unsent draft enquiry about the earlier rating data (`research/audit/INSTITUTIONAL_ETHICS_ENQUIRY_DRAFT.md`, "DRAFT, NOT SENT"), which itself says whether a determination is required is the institution's decision. No approval is claimed anywhere in the papers; none may be invented.

## Actions that only the authors/mentor can take
1. Ask the mentor and the institution's research-ethics office (or equivalent) whether a study in which students practise interview answers with the system, with voice recording and human rating of their answers, needs review, who the principal investigator must be, the timeline, and what the consent/information sheet must contain. Record the reply with a date; do not backdate anything.
2. Decide whether participants will be members of the institution (student status can raise voluntariness and grading-relationship issues to be asked about) and whether any compensation is planned.
3. Confirm who may act as raters and how their independence from the development team is documented.

## Data-type checklist (each item to be answered before recruitment)
| Data | Present in the design? | Question to settle |
|---|---|---|
| Voice recordings | Yes: the browser records audio and `/api/transcribe` receives it; the server writes it to a temporary file (`apps/backend/main.py`, around lines 890–973) | Confirm by code review that the file is always deleted; whether any recording is to be kept for research; retention and deletion terms; whether accent or disability information is at risk (`research/audit/speech_ethics.md` records demographic-bias risks of the prosody score) |
| Transcripts and answers | Yes, stored (SQLite `data/prepaired.db`; fields not fully audited) | What is stored, how it is pseudonymized, who can read it, how long it is kept |
| Video / facial / engagement data | **No — not implemented**; do not collect | If ever added, a separate review |
| Demographics and experience level | Experience level exists in the candidate record; other demographics are not part of the current design | Collect only what the analysis needs; decide how accent/language background is handled |
| Identifiers (name, e-mail, login) | The application has a login (`Login.jsx`); its stored fields were not audited | Separate identifiers from study data; use coded IDs |
| Ratings of participant answers | Planned | Consent must cover raters seeing answers; raters' own consent and records |
| Publication of results | Planned | Consent must say results are published in aggregate; whether any data are shared |
| Withdrawal, deletion | Required | Procedure and its limit once data are anonymized |
| Data location | Local machine and repository | The repository must not hold identifiable data; `data/` handling and `.gitignore` need review before any study |

## What the manuscript may and may not say
It may state a participants' ethics/consent statement only after those facts exist. It must not say "approved", "consented" or "exempt" on the basis of anything not documented. If the study is not reviewed, the paper cannot report human-participant data.

## Related, already-known ethics limits (not new)
The confidence score was not evaluated across accents, speech differences or noise; its use to pace difficulty must be described as unvalidated for fairness (`speech_ethics.md`).
