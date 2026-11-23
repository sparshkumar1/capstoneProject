# IEEE References Verification and Citation-Consistency Record

**Correction (2026-11-13):** the claim below that all 15 references were already "independently-verified" without
error was itself inaccurate. A fresh, independent re-check (live web search against publisher/ACM/arXiv/Microsoft
Research sources, not a repeat of whatever process produced the original claim) found that 3 of the 15 entries this
document calls already-verified in fact had real errors: [2] (Mendonça et al.) had the wrong first-author initial
and was missing its volume/issue/article number; [5] (Argos) was imprecisely dated ("Microsoft Research publication,
2026" instead of its confirmed arXiv submission, 2025); [14] (Chen et al.) was cited as ICMI 2017 when the real,
DOI-confirmed paper is ICMI **2016**. All three are now fixed in `Final_IEEE_Paper_Source.tex`,
`Final_IEEE_Paper_Anonymous.docx`/`.pdf`, and `final_deliverables/02_University_Project_Report/12_Bibliography.md`
(+ its own compiled report). [13] (Naim et al.) was also completed with its subtitle and DOI (not wrong, just
incomplete). Full source-by-source verification record for all 15 entries:
`FINAL_SOURCE_OF_TRUTH_AND_RECONCILIATION.md`, Finding 3. The remaining 12 entries described below as verified were
independently re-checked this pass and did hold up as accurate.

All 15 references in `Final_IEEE_Paper_Anonymous.docx`/`.pdf` are reused, without alteration to their bibliographic details, from this project's own previously independently-verified reference lists (`final_deliverables/02_University_Project_Report/12_Bibliography.md`, itself produced by live-search re-verification of each entry, and the already-reviewed `paper/manuscripts/venue/ICETC_P1` reference set). **No new reference was introduced in this paper, and no DOI, volume, page number, or publication detail was invented** (the three corrections above were transcription/precision errors in an otherwise-real reference, not fabrications).

## In-text citation ↔ reference-list consistency check

| # | Reference | Cited in text at | Role in the paper |
|---|---|---|---|
| [1] | Karjus et al., LLM grading, arXiv:2601.16314, 2026 | §I (adaptive testing motivation), §II | Related-work: LLM scoring reliability |
| [2] | Mendonça et al., Evaluating LLMs for Automated Scoring, Applied Sciences, 2025 | §II | Related-work: LLM scoring reliability |
| [3] | Wang et al., AutoSCORE, arXiv:2509.21910, 2025 | §II | Related-work: composite/multi-component scoring architecture |
| [4] | Zhu, Du et al., MultiAgentBench, Proc. ACL, 2025 | §II | Related-work: evaluation-methodology analogy (explicitly scoped: PrepAIred is single-controller, not multi-agent) |
| [5] | Microsoft Research, Argos, 2026 | §II | Related-work: grounded-verification design motivation |
| [6] | Schulman et al., PPO, arXiv:1707.06347, 2017 | §I, §IV-B | Primary algorithm citation for the RL policy |
| [7] | Reimers & Gurevych, Sentence-BERT, Proc. EMNLP, 2019 | §IV-A, §V | Primary citation for the S1 semantic-similarity component |
| [8] | Johnson, Douze, Jégou, FAISS, IEEE Trans. Big Data, 2019 | §IV-A | Primary citation for the S2 concept-retrieval component |
| [9] | Weiss, Adaptive Testing, Applied Psych. Measurement, 1982 | §I | Foundational citation for difficulty adaptation |
| [10] | Anderson, Corbett, Koedinger, Pelletier, Cognitive Tutors, 1995 | §I, §II | Related-work: intelligent tutoring |
| [11] | Corbett & Anderson, Knowledge Tracing, 1994 | §I, §II | Related-work: intelligent tutoring |
| [12] | Graves et al., Automated Curriculum Learning, Proc. ICML, 2017 | §II | Related-work: RL curriculum/difficulty sequencing |
| [13] | Portelas et al., Curriculum Learning for Deep RL survey, Proc. IJCAI, 2020 | §II | Related-work: RL curriculum/difficulty sequencing |
| [14] | Naim et al., Automated Prediction of Job Interview Performance, Proc. IEEE FG, 2015 | §II | Related-work: multimodal interview analysis (contrast case) |
| [15] | Chen et al., Doc2Vec Interview Video Scoring, Proc. ACM ICMI, 2017 | §II | Related-work: multimodal interview analysis (contrast case) |

**Every reference in the list is cited at least once in the body text; every in-text citation number ([1]–[15]) resolves to exactly one reference-list entry.** This was checked by direct cross-reference, not assumed.

## Deliberately excluded references

Two entries from this project's earlier, broader bibliography (`12_Bibliography.md`) are **not** included here, by deliberate decision, not oversight:

- **"Wu et al. (2026)"** — the originally-cited source could not be independently matched to an exact, verifiable publication in this project's prior verification pass. Rather than cite it anyway or substitute an unverified replacement, it is omitted entirely from this paper.
- **"Auctores Online (2025)"** — could not be located under any plausible title/author in this project's prior verification pass, and "Auctores" is flagged in that prior record as a known low-oversight open-access platform name. Omitted entirely, consistent with that prior record's own recommendation.

Including either of these would have reproduced a known, previously-flagged citation-integrity gap into a new document; excluding them is the more defensible choice given the Mandatory Instructions' explicit prohibition on citing unverified references.

## Verification method

1. Each reference's author, title, venue, and year were taken verbatim from `final_deliverables/02_University_Project_Report/12_Bibliography.md`, itself the product of a prior, dedicated, live-search re-verification pass (not re-verified a second time from scratch in this pass, since no bibliographic detail was changed from that already-verified source).
2. A direct text search of `ieee_system_paper.md` (the paper's source content) was used to confirm every `[N]` citation marker in the body resolves to a reference list entry, and that no reference-list entry is orphaned (present but never cited) — both directions checked, not just one.
3. No reference's venue, year, or authors were altered from the verified source bibliography to better fit this paper's narrative — citations were selected for inclusion based on topical relevance to sections already drafted, not edited to appear more relevant than they are.

## Residual uncertainty, disclosed

- Reference [5] (Argos, Microsoft Research) is a corporate research publication rather than a peer-reviewed conference/journal paper. It was already used, without being flagged as unresolved, in this project's prior, already-reviewed IEEE draft (`paper/manuscripts/venue/ICETC_P1`), so it is reused here on the same basis — but a stricter venue-specific citation policy may still prefer a peer-reviewed substitute, which the authors should confirm against the actual target venue's citation rules before submission.
- This paper does not independently re-verify DOIs or exact page ranges beyond what the source bibliography already recorded; if the target venue requires DOI resolution for every entry, that is a remaining author task, not completed here.
