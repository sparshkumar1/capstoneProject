# P1 — Backup venue plan (2026-09-21; nothing submitted; no probabilities, no acceptance predictions)

## Constraint that drives the choice
ICETC notifies on **10 Nov 2026** (icetc.org). A backup used only after an ICETC rejection needs a submission deadline **after** 10 Nov, and its rules must not prohibit the earlier ICETC submission. Submitting to a second venue while ICETC is pending would be simultaneous consideration. Most venues prohibit that and ICETC's own rule was not found (UNVERIFIED), so it is not recommended.

## Assessment of the previously supplied venue pool
| Venue | Deadline | Relative to ICETC decision (10 Nov) | P1 scope | Verdict for this purpose |
|---|---|---|---|---|
| ATIS 2026 (Springer CCIS, ≤12 pp, Bengaluru 14–15 Dec) | 7 Nov 2026; notification 30 Nov | **before**; the FAQ "Can I submit work already under review elsewhere?" is listed on the page but its answer could not be read | information security; topic fit moderate to good (`venue/atis2026/ATIS_FIT_MEMO.md`) | not a sequential backup; usable only as an alternative primary, after reading the FAQ answer |
| ICMLSC 2027 | 30 Sep 2026 | before | ML/soft computing, weak | no |
| SAC 2027 AIED | 2 Oct 2026 | before | education AI; P1 is not an AIED study | no |
| SmartCom 2027 | 12 Oct 2026 | before | not assessed for P1 | no |
| HCII 2027 AIS | 9 Oct 2026 (proposal) | before | fits P3, not P1 | no |
| IEEE MLNLP 2026 | about 20 Nov (unverified) | after | NLP scope; official site unreachable | UNVERIFIED, weak scope |
| IEEE AIEI 2027 | unverified | — | official site not read | UNVERIFIED |
| ICTCS 2026, ICMETE 2026 | — | — | ICTCS is theoretical CS; ICMETE not found | no |

**The supplied pool contains no defensible sequential backup for P1.** Additional venues were researched from official pages (2026-09-21).

## Additional venues researched
| Venue | Deadline | After 10 Nov? | Fit / blocker |
|---|---|---|---|
| **CSEDU 2027** (19th Int. Conf. on Computer Supported Education, Rome, 16–18 Apr 2027) | **regular papers 17 Nov 2026**; notification 15 Jan 2027 | **yes (7 days later)** | AI in Education and Learning/Teaching Methodologies and Assessment among its four areas; details below |
| IEEE EDUCON 2027 (Timisoara, 6–9 Apr 2027) | **abstract 19 Oct 2026**; full paper 7 Dec; decisions 11 Jan 2027 | full paper yes, **abstract no** | theme includes AI and cybersecurity in digital education; 8 pages max including references; IEEE format; double-anonymous; "original work not under consideration" elsewhere. The mandatory 250-word abstract falls before the ICETC decision, and whether that counts as "under consideration" is UNVERIFIED |
| AST 2027, CAIN 2027, FORGE 2027 | 30 Oct 2026 | no | testing / AI-engineering venues; deadline precedes the ICETC decision; scope and format not read |
| EASE 2027 (research papers) | 22 Jan 2027 | yes | empirical software-engineering evaluation; fit for P1 not verified |

## Recommended backup: CSEDU 2027, regular paper
- **Why P1 fits:** the assessment pipeline is the subject, and CSEDU lists AI in Education and assessment among its four areas. Fit is on the assessment-technology side; the educational relevance is thinner than at ICETC and needs one framing paragraph (no learning claim can be added).
- **Official deadline:** regular papers **17 Nov 2026**; notification 15 Jan 2027; camera-ready 27 Jan–10 Mar 2027 (varies by track).
- **Review model:** double-blind. The paper must be produced "WITHOUT any reference to any of the authors", including acknowledgments. Authors must not post the paper on preprint servers or personal sites during review.
- **Format:** SciTePress template (templates page not read); full paper up to **12 pages** (short paper 8), up to 4 extra pages at 50 € each.
- **Publication:** ISBN proceedings via SCITEPRESS; stated indexing SCOPUS, Google Scholar, DBLP, Semantic Scholar, EI and Web of Science (conference claim).
- **AI policy (read):** AI-generated content must be identified in the acknowledgments, naming the tool and the parts; AI is not an author; authors remain accountable.
- **Registration fee (stated):** author registration 650 € (non-member, early) to 760 € (late); one paper per registration.
- **Expected reframing:** re-lay the 5-page port in the SciTePress template; restore material cut for ICETC (per-attack host-observable detail, SEC-08/SEC-09 caveats, X1-A table rows), expected 8–10 pages (estimate); add one short paragraph on the assessment-pipeline relevance. No change to any number or claim.
- **Reusable as is:** all text, tables, Fig. 1, references, claim ledger, blinding work, limitations.
- **Must change:** template and page count. The acknowledgments rule conflicts with the AI-disclosure rule (anonymity "including acknowledgments" versus disclosure in the acknowledgments), so ask the chairs whether a neutral disclosure may stay in the blinded copy (UNVERIFIED). Remove any mention of ICETC.
- **Current blockers:** conversion has to happen in the 7 days between the ICETC decision and 17 Nov, so it should be prepared in advance. The CSEDU template was not opened, and no rule for a paper rejected elsewhere is stated (resubmission guidance is absent from the guidelines).
- **Submission possible after an ICETC rejection?** Yes on timing (10 Nov against 17 Nov). CSEDU prohibits simultaneous submission, so submit only after the ICETC decision is in.
- **If ICETC accepts:** no backup is needed; do not submit to CSEDU.
- **Official sources:** https://csedu.scitevents.org/callforpapers.aspx · /Guidelines.aspx · /AiTools.aspx · /RegistrationFees.aspx.

## Second option (conditional): IEEE EDUCON 2027
Smallest reformatting (IEEE, already blinded, 8 pages including references), but it needs an abstract by 19 Oct, before ICETC replies. Use only if the EDUCON chairs confirm in writing that an abstract does not count as a simultaneous submission. Source: https://educon-conference.org/2027/authors/initial-author-instructions.

## Not recommended for this purpose
ATIS 2026 (deadline precedes the ICETC decision; FAQ unreadable) and every pool venue with an earlier deadline.

## Unverified
CSEDU template and any post-rejection rule; EDUCON abstract rule; ATIS FAQ answers; ICETC's own prior-submission rule; fees other than CSEDU's.

## Status and future conversion checklist (master pass, 2026-09-21)
**This is a contingency plan only.** CSEDU 2027 has not been selected, nothing has been converted, and nothing is submitted. The SciTePress template was not opened and no page count exists for a CSEDU version, so the paper must not be described as CSEDU-ready. The plan applies only after an ICETC rejection (notification 10 Nov 2026), only if no rule of either venue blocks it, and never simultaneously with the ICETC submission.

If the decision is later made to convert, keep the scientific content exactly as in `paper1/manuscript.md` and the ICETC port, and:
1. Re-read `Guidelines.aspx`, `AiTools.aspx`, `Templates.aspx` and the current dates on the CSEDU site.
2. Apply the SciTePress template; measure the page count (limit 12; up to 4 extra pages at 50 € each).
3. Blind the paper as for ICETC, including acknowledgments; settle the AI-disclosure placement with the chairs first.
4. Restore the material that was cut for ICETC; add no educational claim and no learning-outcome claim.
5. Do not post the paper on a preprint server or personal site while it is under review.
6. Keep the same title unless the authors decide otherwise; the ICETC title is "Scoped Evaluation of Containment, Authority Boundaries, and Failure Handling in an LLM-Assisted Technical-Assessment System".
