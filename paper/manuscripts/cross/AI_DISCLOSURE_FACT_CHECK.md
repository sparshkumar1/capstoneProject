# AI-USE DISCLOSURE — fact check (2026-09-21)

Extends `AI_USE_DISCLOSURE_DRAFT.md` and `audit_v2/AI_DISCLOSURE_AUDIT.md`. Nothing here is final wording; every unconfirmed fact is marked.

## 1. Policies re-checked this session
| Venue / publisher | Policy as read | Source | Status |
|---|---|---|---|
| IEEE (ICETC proceedings) | AI-generated content (text, figures, images, code) shall be disclosed in the acknowledgments, naming the AI system and the sections and level of use; editing/grammar use outside the policy, disclosure recommended | IEEE Author Center submission policies (read earlier today) | verified; ICETC's own AI rule not found |
| Springer Nature (HCII proceedings, LNCS/LNAI) | landing page: AI "may support but not replace scholarly judgement"; human accountability cannot be transferred; authors must disclose AI use in manuscript preparation and research. Sub-pages on manuscript preparation, the exemption for copy editing and image rules were not readable | springernature.com/gp/policies/editorial-policies | principle verified; detail UNVERIFIED |
| HCII 2027 | no AI policy on papers.html, deadlines.html or the AIS page | 2027.hci.international | not found |
| CSEDU 2027 (P1 backup) | AI-generated content must be identified in the acknowledgments with tool and parts; AI not an author; authors accountable; submitted manuscripts must not be run through public AI platforms for review tasks; AI-generated figures need tool and prompt in the caption | csedu.scitevents.org/AiTools.aspx | verified |
| ICETC, ATIS, SAC | own rules not found | — | UNVERIFIED |

## 2. Facts that are established (from the repository and this task)
- AI system: Anthropic Claude models through the Claude Code agent.
- P1 manuscript already states that one AI coding agent designed, ran, repaired and re-tested the X1 campaigns.
- In this task the agent traced numbers, drafted and revised the text, tables, figure code, ledgers and audits; it ran no experiment and altered no frozen result.
- A second AI tool's read-only review of P1 was relayed as a verdict only; its report is not in the repository.
- Figure code (`figures/make_fig_p*.py`) is AI-written; the figures re-plot stored results only.

## 3. Facts NOT established (author confirmation required)
1. Exact model names, versions and dates for each phase.
2. Which sections, tables, figures and code the authors consider AI-generated.
3. The extent and dates of human review of each section.
4. AI involvement in designing and executing X2 and X3 (Papers 2 and 3); not reviewed in this pass.
5. Whether other AI tools (Codex, Antigravity, ChatGPT, Gemini, NotebookLM) produced text that entered any paper.
6. Whether any AI tool was used by Paper 2 raters (unknown from the record).
7. Whether the disclosure text may stay in the blinded copy for double-blind venues (ICETC unspecified; CSEDU requires anonymity even in acknowledgments).

## 4. What each prepared file currently says
| File | Disclosure text | Status |
|---|---|---|
| `venue/ICETC_P1/P1_ICETC_BLINDED.*` | no acknowledgments, no disclosure text (master-pass decision) | open policy question; needs D-4 |
| `venue/ICETC_P1/P1_ICETC_MANUSCRIPT_READY.md` (master) | bracketed placeholder only | placeholder |
| `venue/HCII_P3/P3_FULL_MANUSCRIPT_READY.md` | Declarations section with a bracketed placeholder | placeholder |
| `venue/HCII_P3/P3_HCII_PROPOSAL_FINAL.md` | none (proposal text has no disclosure field known) | check the form |
| Paper 2 | none; venue held | — |

## 5. Rule followed
No model version, date, affected section or degree of involvement was invented. Where unknown, the text says UNCONFIRMED or AUTHOR CONFIRMATION REQUIRED. Re-read the exact policy on the venue's page at submission time.

## Master-pass update (2026-09-21)
Rule applied: scientific prose carries no AI-tool mention merely because drafting, coding, auditing or editing help occurred; disclosure lives in the venue's disclosure place and stays a placeholder until the authors confirm the facts. Nothing states that no AI was used, and no version, date, section or review extent is asserted.
- **Blinded ICETC PDF:** no acknowledgments and no disclosure text (ICETC's own rule not found; IEEE's policy for IEEE-published proceedings puts the disclosure in the acknowledgments). Open policy question for the organisers; disclosure is added once the authors confirm the facts.
- **Kept in the P1 body (method fact, not drafting):** the X1 campaigns were designed, run, repaired and re-tested by one AI coding agent under the project lead's direction; the independence of the re-test depends on it (Sections IV–VII).
- **Removed from the P1 body:** a sentence about a second AI tool's read-only review whose report is not in the repository; no result relied on it. The fact remains recorded in section 2 above (fourth bullet) for the authors.
- **P1 master and P3 full manuscript:** bracketed placeholders only ("AUTHOR CONFIRMATION REQUIRED"), replacing the earlier drafted text.
- **P3 proposal and P2:** no disclosure text.
- Unchanged open items: exact model names and versions, sections affected, extent and dates of human review, AI involvement in X2/X3, and whether other tools (Codex, Gemini, ChatGPT, NotebookLM, Antigravity) contributed text.
