# Human Benchmark Provenance Plan (Phase 0, 2026-09-19)

**Status: plan only.** Nothing was sent, no rater was contacted, no record was created or altered. This plan covers (A) recovering documentation for the **existing** 64-case human ratings and (B) documenting the **single** new confirmatory round (X2-C) correctly from the start. Related: `P0_7_HUMAN_ETHICS_FORENSIC.md`, `INSTITUTIONAL_ETHICS_ENQUIRY_DRAFT.md`, `X2_PROTOCOL_DRAFT.md` §4.

## 0. Non-negotiable rules
1. **Never fabricate or backdate** consent, independence, blinding, qualification, timing or approval records. A statement written now is a **retrospective statement**: dated today, signed/attributed to its author, labelled "retrospective", stored beside — never in place of — the original record.
2. **Existing records only** are requested from people/institutions as *recovery*. Requesting a new attestation is allowed only if it is labelled retrospective and dated when made.
3. **The repository is silent, not negative.** The absence of a record in the repository is not evidence that something did or did not happen; no inference of misconduct is made (P0-7).
4. Frozen files (protocol, rater files, gold, checklist) are never edited; additions are new files.
5. **Personal data stay out of the repository.** Identities and contact details are stored off-repo (institution-approved storage); the repository holds only coded IDs and hashes.
6. **One new human round only** (locked). A second round requires a documented protocol amendment approved by the user.

## 1. What the repository can establish (existing round) — `AUDIT`
Frozen annotation protocol and its tag `pre-human-annotation` (commit `45845a97…`); rater package manifests and zips; the three hash-pinned rater files; adjudication guidelines, form and rationales; blinded-sheet design (no category, no model score); the final gold (`363dbe6d…6ce2`) and completion reports; Git timestamps (rater files last modified 22–53 minutes after the freeze commit; package build 12:52; identical `timestamp_received` 14:54:35 in all three files; adjudication of 10 items with rationales spans about 6.5 minutes by file times — these are file facts, not conclusions); the computed reliability statistics.

## 2. Record recovery checklist (existing round) — to be completed by the user
Status codes: **R** recovered · **M** missing (may exist elsewhere) · **X** cannot be reconstructed · **I** needs institutional determination.

| # | Record | Where it might exist | Status | Notes |
|---|---|---|---|---|
| 1 | Identity, role and relationship to the study team of each of the 3 raters and the adjudicator (coded IDs in repo; identities off-repo) | your contacts, email/chat history | M | Needed for "independent" wording |
| 2 | Qualifications/expertise of each | same | M | Do not state "expert" without it |
| 3 | The message(s)/instructions each rater actually received (with the package) | email/chat/drive | M | Original, with native metadata |
| 4 | Send and return timestamps of packages | email/chat/drive metadata | M | Determines whether "frozen before annotation" holds |
| 5 | Time spent per rater | rater statement (retrospective) | M/X | Retrospective only |
| 6 | Whether external tools or AI assisted any rating or rationale | rater statement (retrospective) | M/X | Retrospective only |
| 7 | Any consent (even informal, e.g., an email agreeing to rate) | email/chat | M | If none: **X**; do not write "consented" |
| 8 | Compensation/acknowledgement terms | messages/payments | M | Do not state without a record |
| 9 | Institutional determination (ethics/exemption/"not human-subjects research"), or correspondence | institution | I | INSTITUTIONAL DECISION REQUIRED |
| 10 | Signed `ETHICS_CHECKLIST.md`, if a signed copy exists elsewhere | your files | M | The repository copy is unsigned; it required pre-distribution sign-off |
| 11 | "Human Gate 1" approval record | your files | M | Absent in repo |
| 12 | Who authored the 64 answers and how (generation method; any editing after seeing evaluator outputs) | authoring records | M | The build script shows one authoring script; generation method not documented |
| 13 | Who the "Principal Investigator / Lead Ethics Coordinator" would be | institution/supervisor | I | |

**Cannot be reconstructed (X):** consent never obtained; independence/blinding attestations never collected; the pre-distribution checklist sign-off; actual rating times if no send/return record exists. If any of these is genuinely absent, the paper discloses it (route decided with the institution) — it does not paper over it.

**Deliverable (Phase 1+, after the user supplies material):** a new `HUMAN_RATING_PROVENANCE_ADDENDUM.md` (identities coded) that lists each record with status, source, date received and SHA-256 of the stored copy, plus any retrospective statements clearly labelled. No frozen file is edited.

## 3. Gates
| Gate | Content | Owner |
|---|---|---|
| **G0** Record inventory | Complete §2 as far as possible | User (with Claude preparing the addendum) |
| **G1** Institutional/venue determination | Send `INSTITUTIONAL_ETHICS_ENQUIRY_DRAFT.md` (user action, **now, in parallel with G0**); obtain the determination or a documented decision on how to proceed for (a) the existing ratings and (b) the planned confirmatory round | Institution/venue (**INSTITUTIONAL DECISION REQUIRED**) |
| **G2** Consent and ledger design for X2-C | Consent/information sheet, roles, data handling and compensation as the institution requires; ledger template (§4) approved before any distribution | User + institution |
| **G3** Documentation attached to the dataset | Ledger, hashes and statements published in the repository (coded) and described in the paper's ethics/data statement | User |
X2-C item authoring and rating do not start until G1 and G2 are complete.

## 4. Provenance ledger for the new round (X2-C)
Stored off-repo with identities; the repository holds a coded, hash-linked extract. One row per person-role per activity.

| Field | Content |
|---|---|
| `person_code` | Stable code (R1, R2, R3, ADJ, AUTH-1 …); identity mapping stored off-repo |
| `role` | rater / adjudicator / question author / reference author / answer author / generator operator |
| `relationship_to_team` | e.g., colleague, student, external (as recorded at the time) |
| `qualification_statement` | As stated by the person, dated |
| `consent_form_id`, `consent_date` | Form version and date signed **before** distribution |
| `information_sheet_version` | Version given |
| `instrument_version`, `instrument_sha256` | Rating sheet/rubric version and hash |
| `package_sha256`, `sent_utc`, `returned_utc`, `channel` | Distribution and return records (message metadata preserved) |
| `time_spent_min` | Self-reported at return |
| `tool_use_declaration` | Whether any external tool/AI was used; collected at return |
| `independence_declaration` | Declared at the time: no access to evaluator outputs, not involved in evaluator construction (or state involvement) |
| `blinding_check` | Confirmation that category/stratum/authorship/evaluator output were not visible |
| `compensation_terms` | As agreed and recorded before distribution |
| `returned_file_sha256` | Hash at receipt |
| `notes` | Anything unusual, verbatim |

## 5. Independence, blinding and authorship controls for X2-C
- Raters: not involved in building the evaluator or the benchmark items; if any involvement exists it is declared and the rater is analysed as a sensitivity subset. Adjudicator distinct from all authors.
- Blinded sheets show question, reference (if the rubric uses it) and answer only; randomised order per rater; no category, stratum, model score or authorship.
- Authors of references/answers work without evaluator access; any generator (model, prompt, seed, temperature) is recorded and outputs are **not filtered**; the authorship log and the item-freeze hash prove ordering (`X2_PROTOCOL_DRAFT.md` §4).
- Any instruction or tool used by a rater (e.g., permission to look up facts) is written into the instrument and declared.

## 6. Description of the human evidence in manuscripts
**Allowed now:** "Three raters scored 64 constructed answers to 8 questions with a frozen rubric; the rating files are hash-pinned; ICC(2,1) 0.953, ICC(2,k) 0.984, α 0.952; ten items with spread > 0.20 were adjudicated; the rest were averaged." Rater provenance documentation is incomplete (state exactly what is and is not documented).
**Not allowed without records:** "independent", "expert", "committee", "consented", "compensated", "approved", "exempt", "blinded to model output" (the blinded-sheet design supports blinding to model scores; independence of raters does not follow), "frozen before annotation" if packages may have been sent before the freeze.
After X2-C, the confirmatory set carries the ledger; the 64-case set is described as exploratory/initial with its provenance status.

## 7. Decisions needed from the user
1. Send the institutional enquiry now (and to whom).
2. Provide whatever records exist for §2 (or state that they do not).
3. Provide/approve the consent, information sheet and compensation arrangements for X2-C once the institution has answered.
4. Choose who authors questions/references/answers and who rates (independence per §5).
