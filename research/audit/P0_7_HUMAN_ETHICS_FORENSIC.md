# P0-7 — Human ethics / rater provenance documentation (Paper 2 human gold, N = 64)

Forensic pass, 2026-09-19. Read-only. I did **not** invent, infer or fill in consent, ethics approval, institutional review, identities, qualifications, compensation or independence. Where the repository is silent, this file says "not documented", and that is not the same as "did not happen".

## 0. Bottom line

The four questions are separate and have different answers:

| Dimension | Status | One-line reason |
|---|---|---|
| **Scientific reproducibility** of the human gold and its statistics | **Strong** | Raw rater files, protocol, benchmark and gold are hash-pinned; the frozen ICC / α / adjudication counts reproduce from the files. |
| **Rater provenance** (who, how recruited, qualifications, independence, when, how long) | **Not documented** | Raters exist only as labels "Rater 1 / Independent Technical Expert A / B"; no identities-of-record, qualifications, recruitment, instructions received, time spent, or independence attestations. Adjudicator: count, identity and qualifications not documented. |
| **Ethics / administrative documentation** (consent, voluntariness, compensation, data handling sign-off) | **Absent** | `ETHICS_CHECKLIST.md` is committed with every box unticked and both signature lines blank; no consent form, compensation record, or Gate 1 approval record exists anywhere in the repository. |
| **Institutional determination / approval** (IRB/ERB, exemption, or "not human-subjects research") | **Absent from the repository — status unknown** | The checklist's status field (`EXEMPT / APPROVED / EXPEDITED / PENDING`), protocol/exemption ID and institutional affiliation are blank. |

**Publication / documentation risk:** the manuscripts and handoff documents describe "three independent blind CS educators", "three real human annotators" and "expert blind adjudication by the educator committee", but nothing in the repository supports independence, qualifications, consent, or an institutional determination. Whether an institutional determination is *required* depends on the institution and the (still undecided) venue, which I cannot determine; but where a venue or institution asks for an ethics/consent statement, the repository cannot currently supply one. This is a USER/INSTITUTIONAL matter, not something to be repaired by editing the files.

## 1. What is documented (with sources)

| Item | Where | Notes |
|---|---|---|
| Frozen rating & adjudication protocol | `research/annotation/HUMAN_RATING_PROTOCOL.md` (SHA-256 `2f997921…8f5a29`), tag `pre-human-annotation` (commit `45845a9`) | Continuous scale [0,1]; ICC(2,1)/(2,k), Krippendorff α, adjudication if max pairwise difference > 0.20 else mean of three; "no post-hoc change". |
| Rater packages | `research/annotation/packages/RATER_{1,2,3}`, `distribution/*.zip`, `RATER_PACKAGE_MANIFEST.json` | Blinded sheet = `item_id, question_id, topic, question, candidate_answer, score_0_to_1, rater_comments` (no category label, no model scores). Roles are only labels: "Primary Technical Educator", "Independent Technical Expert A/B". |
| Raw and frozen rater files | `raw/`, `raw/incoming/`, `FROZEN_HUMAN_RATINGS/` (+ manifests) | Three identical copies per rater; SHA-256 `5c8086c6…`, `b0d15a69…`, `ce995d0e…` match the manifests. |
| Adjudication | `adjudication/ADJUDICATION_GUIDELINES.md`, `ADJUDICATION_FORM.csv`, `HUMAN_GATE_3_CASES.csv` | 10 items adjudicated with one-sentence rationales; raters masked as A/B/C. Blinding guidelines present. |
| Final gold | `research/data/evaluator_benchmark/final_human_gold.csv` (SHA-256 `363dbe6d…6c2`) | 54 `mean_of_three`, 10 `expert_adjudication`. I confirmed the counts. BM-032 has an exact 0.20 spread (a floating-point artifact) and is correctly a consensus case under the rule. |
| Rater PII | none in the repository | consistent with the checklist's de-identification intent (§3.1), but also means there is no separate record of who they are. |

## 2. What the checklist required and what exists

`research/annotation/ETHICS_CHECKLIST.md` (committed once, in `45845a9`, never modified):

| Requirement | Evidence in the repository |
|---|---|
| 1.1 IRB/ERB determination or exemption (status, ID, affiliation) | **None** — blank |
| 1.2 Scope of human involvement (raters judge constructed answers; no live student data, no biometric data) | Stated as a design intent in the checklist; not attested |
| 2.1 Informed consent form (purpose, time, venues, permission to publish anonymised scores) | **None** |
| 2.2 Voluntariness / right of withdrawal | **None** |
| 2.3 Compensation or authorship/acknowledgement | **None** |
| 3.1–3.3 De-identification, secure storage with hashing, data-protection compliance | Hashing exists; de-identification present by omission; no compliance record |
| 4.1 Raters' independence & no exposure to model scores (attestation) | **None** (design-level blinding in the packages only) |
| 4.2 Raters reviewed/agreed to the frozen adjudication protocol | **None** |
| 5 Sign-off by Principal Investigator and Lead Ethics Coordinator | **Blank** |

The checklist and `rater_package_integrity.md:41` both state that the packages **must not be distributed until the checklist is signed and Human Gate 1 is explicitly approved**. No document in the repository records Gate 1 being approved or the checklist being signed (I searched all tracked docs). The rater files nevertheless exist. The sign-off may have been given elsewhere (email, paper form, verbal); the repository simply cannot show it.

## 3. Timeline (2026-09-19, IST; sources are Git times and file mtimes — mtimes can reflect copy times and are not proof of when a person worked)

| Time | Event | Source |
|---|---|---|
| 11:33:35 | rating template/guidelines committed | commit `f5f6dfe` |
| 12:52:50 | three rater package zips built | zip mtimes; `RATER_PACKAGE_MANIFEST.json created_at` |
| 13:45:00 | `FINAL_HUMAN_GATE_MANIFEST` declares `FROZEN_BEFORE_HUMAN_ANNOTATION` (round-number timestamp, i.e. declared rather than measured) | manifest |
| 13:59:41 / 13:59:49 | protocol freeze commit / tag `pre-human-annotation` | Git |
| 14:21:48 | `RATER_1_COMPLETED.csv` last modified (**22 min after the freeze commit**; 89 min after the packages were built) | file mtime |
| 14:48:05 | `RATER_2_COMPLETED.csv` (**48 min** after freeze; 115 min after build) | file mtime |
| 14:52:54 | `RATER_3_COMPLETED.csv` (**53 min** after freeze; 120 min after build) | file mtime |
| 14:54:35 | manifests written; `timestamp_received` is identical (14:54:35) for all three files, i.e. batch-stamped by a script, not an independent receipt record | `annotation_manifest.json`, frozen manifest |
| 15:00:23–15:07:01 | adjudication cases created (15:00:23), guidelines (15:00:37), `ADJUDICATION_FORM.csv` last modified 15:07:01 — **about 6.5 minutes** for 10 adjudications with rationales | mtimes |
| 15:22:50 | gold and completion report committed | commit `375f4f8` |

Reading the timeline:
- The checklist estimates **1.5–2.5 h per rater** for 64 items. If the packages were sent only after the freeze commit (13:59), the returned files appear 22–53 minutes later, i.e. roughly 20–50 s per item including a comment. If they were sent at or after their build time (12:52), the intervals (89–120 min) match the estimate, **but then rating may have begun before the freeze commit/tag**, and "frozen before annotation" could not be shown from Git. Either reading leaves something unresolved; the repository does not record when the packages were sent or received.
- The 6.5-minute adjudication interval and the "human expert committee" wording of the Gate 3 report (versus "the expert adjudicator" in the same report) leave the adjudicator's identity, number and qualifications undocumented.
- These are documentation gaps. **I am not alleging that anything was done improperly.**

## 4. What the data itself shows (objective, no inference about causes)

- Three visibly different rating styles: R2 uses only 13 distinct score values (all on a 0.05 grid); R3 uses 33 distinct values (30 % on the 0.05 grid); R1 22 distinct values. No comment is identical across raters (190 distinct of 192; 0 identical pairs). File encodings differ: R1 is plain ASCII, R2 and R3 carry a UTF-8 BOM (different save pathways).
- Pairwise agreement: Spearman 0.853 (R1–R2), 0.973 (R1–R3), 0.838 (R2–R3); Pearson 0.939–0.983; mean absolute difference 0.072–0.109. The stored ICC(2,1) 0.9528 and α 0.9523 are consistent with these.
- **The gold scores are almost entirely determined by the authors' own construction categories.** Each rater's score has η² ≈ 0.98–0.99 with the author-assigned `expected_quality_category` (e.g. concise_correct ≈ 0.86–0.97; verbose_correct 0.95–1.00; misconception/incorrect/verbose_wrong ≈ 0.05–0.19). Item means have SD 0.358 versus a mean within-item rater SD of 0.068. So the very high reliability mostly reflects a benchmark built from clearly separated categories, not agreement on naturally ambiguous answers. This does not indict the raters; it limits what "ICC 0.95" means and connects to the audit finding that "authentic explanations" should read "constructed benchmark answers". (Keyword-stuffed items are the main area of real disagreement: mean 0.32 / 0.10 / 0.38.)
- Eleven items exceed a 0.20 spread by naive float comparison; ten under the exact rule (BM-032 is exactly 0.20).

## 5. Statements in the handoff/manuscript guidance that are **not** supported by the repository

| Statement | Where | Support |
|---|---|---|
| "three independent blind CS educators" | `CANONICAL_SCIENTIFIC_TRUTH.md:50`, `MANUSCRIPT_AUTHORING_GUIDELINES.md:67` | identities, credentials, independence and blinding attestations not recorded (blinding is a *design* of the sheet, not evidence of what raters saw) |
| "three real human annotators" | `PAPER2_FINAL_REPORT.md:158` | contrast with synthetic files is documented (see §6), but "real" is not otherwise evidenced |
| "expert blind adjudication" / "human expert committee" | Gate 3 report, handoff | adjudicator number/identity/qualification/independence from the study author not recorded |
| "authentic explanations" | handoff | cases are constructed per category by the study authors (see stale-artifact audit) |

## 6. Related provenance notes

- The N = 20 pilot (ρ = 0.6975, single rater) came from `ablation/results/ratings_rater1.csv`; that rater's identity and instructions are equally undocumented. The repository also contains clearly labelled **synthetic** rater files (`ratings_synthetic_rater{1,2,3}.csv`, `ratings_proxy.csv`; their `.meta.txt` says "SYNTHETIC PROXY DATA FOR TESTING. NOT REAL HUMAN RATINGS"). They are not used in Paper 2 but are easy to confuse with the real raters; keep them clearly separated in any release.
- `ablation/HUMAN_EVAL_README.md` and `docs/HUMAN_RATER_PACK.md` recommend recording "who rated what and when" and anonymous IDs; no such manifest exists for the Paper 2 raters beyond the labels above.

## 7. What can be claimed now, and what cannot

**Supportable:** "Three raters independently scored 64 constructed benchmark answers with a frozen rubric on a [0,1] scale; the rating files are hash-pinned (SHA-256 given); inter-rater reliability was ICC(2,1) 0.953, ICC(2,k) 0.984, α 0.952; ten items exceeding the pre-specified 0.20 spread were adjudicated once by a single (or unspecified) adjudicator, and the rest were averaged." (State the number of adjudicators only once documented.)
**Not supportable now:** independence of the raters from each other and from the authors; their qualifications or expertise; blind adjudication by a *committee*; voluntary informed participation; compensation/acknowledgement terms; any ethics approval, exemption or "not human-subjects research" determination; "frozen before annotation" if the packages were sent before 13:59 (unknown).
Do not describe the study as "IRB-approved/exempt" or the raters as "independent experts" in any draft without records.

## 8. Recommended actions (USER / INSTITUTIONAL DECISION REQUIRED; none performed)

1. **Establish the facts, in writing, from the people involved:** who the three raters and the adjudicator were (identities can stay off-repo, but a private provenance record should exist), qualifications, recruitment, relationship to the authors, whether they consented and to what, compensation/acknowledgement, exact instructions received, whether they used external tools, when each package was sent and returned, and how long each spent.
2. **Establish the institutional position:** whether the institution requires an ethics/IRB determination for expert rating of constructed (non-student) answers, and if so obtain the determination or a written "not human-subjects research" statement. The venue is TBD (CLAUDE.md), so its ethics-statement requirements cannot be stated here.
3. **Sign or annotate the checklist in a NEW file** (an addendum with dates and the actual status). Do not edit the frozen `ETHICS_CHECKLIST.md`, the manifests or the rater files.
4. **If records cannot be produced:** either (a) disclose the limitation and word the manuscript as in §7, or (b) collect a new, documented human rating round (consent, roles, time logs, protocol unchanged). Option (b) is new human data collection and needs your decision; no rerun of the evaluator is needed for the documentation fix itself.
5. Record the pilot rater provenance too, or drop the pilot from any claim.

## 9. Classification

`EVIDENCE_GAP` (rater and adjudicator provenance) + `DOCUMENTATION_ERROR` ("independent / real / committee / authentic" wording without records) + **institutional/administrative status unknown** (a potential publication risk, to be resolved by the user and the institution). **No analysis rerun is required.** The scientific reproducibility of the human gold is intact.
