# Provenance

Search date: 2026-09-21 (single session; individual timestamps were not logged). Tools: WebSearch (US-only web search), WebFetch (page fetch with small-model summarisation), built-in browser pane (one ScienceDirect page; reading page text and metadata via the DOM), a local PDF-to-text conversion of one downloaded PDF. No other search source. "Novelty impact" is my assessment; "unresolved" lists what I could not confirm.

## Searches run (39 WebSearch calls and 33 WebFetch attempts in total; numbered entries below group related calls, so the numbering is not a call count)
### Paper 3 target
1. "A simulation framework for benchmarking reinforcement learning policies in adaptive mock-interview tutoring" (exact title) -> no direct hit
2. doi.org/10.1016/j.simpat.2026.103316 fetch -> redirect to linkinghub; ScienceDirect direct fetch HTTP 403
3. adaptive mock-interview tutoring reinforcement learning simulation framework Simulation Modelling Practice and Theory 2026 -> no direct hit
4. "10.1016/j.simpat.2026.103316" -> no hit
5. simulation framework benchmarking RL policies adaptive mock interview tutoring PPO DQN IRT simulated learner -> related items (Axak 2025 etc.)
6. Browser pane: sciencedirect.com/science/article/abs/pii/S1569190X26000651 -> page opened; abstract, highlights, intro, contributions, snippets read; metadata (volume 151, article 103316, online 2026/07/09, pub date 2026/09/01) read from meta tags. **Selected: mandatory target. Full text: paywalled.**
7. Kadam Banerjee Christopher ... mock-interview tutoring RL -> confirms existence/date; a search summary omitted one author, so the author list was taken from the page.
### Paper 1
8. benchmark quantifying frontier LLM container sandbox escape capabilities 2026 -> arXiv:2603.02277; ICML 2026 listings
9. comparative security study AI code sandboxes isolation 2026 arXiv -> arXiv:2606.08433, 2607.05743, 2606.18532
10. fault-tolerant sandboxing for AI coding agents transactional filesystem rollback arXiv 2025 -> arXiv:2512.12806
11-13. Fetches of arXiv abs pages 2603.02277, 2606.08433, 2512.12806 (all opened)
14-16. Fetches of 2606.18532, 2607.05743, 2504.00018 (opened)
17. fault injection resilience LLM agent application timeouts outages graceful degradation empirical 2025 2026 -> MAS-FIRE, ReliabilityBench, others
18. LLM agent runtime containment deterministic control plane authority separation ... -> arXiv:2606.26924, 2602.09947 (plus blog/vendor pages, excluded as scholarly evidence)
19. Docker container isolation untrusted code online judge ... -> practitioner pages excluded; arXiv:2506.02043 noted (snippet only)
20-23. Fetches of 2602.19843, 2601.06112, 2602.09947, 2606.26924 (opened)
24-26. Fetches of 2606.03090, 2503.18813; search LLM tutoring feedback separated from deterministic scoring (snippet-level, no source selected)
27-29. Compliance Paradox search (snippet + earlier abstract); Docker under Siege search (snippet); LLM inference server failure / fallback studies (snippet only; not opened)
30-31. Search automated assessment platform LLM outage fail-closed (no relevant scholarly hit; recorded as search-negative); seccomp Docker default profile ptrace search (practitioner pages only)
32. Fetch docs.docker.com/engine/security/seccomp/ -> ptrace sentence, 44 blocked syscalls
### Paper 2
33. EACL 2026 biases in LLM judges verbosity position bias -> EACL 2026 Findings paper found
34. metamorphic testing NLP LLM evaluation survey ... -> arXiv:2511.02108 etc.
35. automatic short answer grading survey 2025 2026 LLM vs fine-tuned ... -> multiple (2605.07647, 2605.00238 ...)
36-39. Fetches: aclanthology 2026.findings-eacl.70; arXiv 2606.19544; 2605.07647; 2511.02108 (all opened)
40. Filighera Steuer Rensing fooling ASAG -> Springer chapter and related; Baldwin JEM 2025
41. answer length bias automated scoring keyword stuffing BABEL -> AES gaming context (Wikipedia/other snippets excluded as evidence)
42. cross-encoder NLI short answer grading -> generic (no direct hit)
43-44. Fetches: JEM page (HTTP 403); arXiv 2505.00061 (opened)
45. SBERT ... Mohler ... cross-encoder -> general
46. Williamson Xi Breyer framework -> metadata confirmed
47. LLM technical interview answer scoring agreement -> arXiv:2512.14561 synthesis
48. automated short answer scoring penalizes concise correct answers ... -> generic ASAG (no direct hit; recorded as search-negative)
49-51. Fetches: arXiv 2512.14561, 2410.02736, 2306.05685 (opened)
### Paper 3 (other)
52. Axak PPO adaptive difficulty tutoring ... -> CEUR paper (PDF downloaded, text extracted with pypdf and read in part)
53. shielding RL Alshiekh ... -> AAAI 2018 metadata via dblp listing (dblp fetch blocked)
54. RL in education systematic literature review Riedmann ... -> IJAIED review (metadata)
55. RL computerized adaptive testing item selection DQN vs Fisher information -> BRM 2024, Deep CAT (2502.19275)
56. adaptive mock interview LLM question difficulty adaptation ... -> no direct policy-benchmark hit
57. Agarwal statistical precipice -> confirmed
58-60. Fetches: PubMed 39271633 (blocked, cookie page); arXiv 2502.19275 (opened); Elo/Pelanek search (metadata)
61. Lakens equivalence tests primer -> metadata
62-64. Fetches: arXiv 2604.04237 (opened); AAMAS 2025 PDF (binary saved; not read); search RL tutoring no better than random/fixed baseline
65-67. Fetch nature.com Sci Rep (redirect); PMC12774889 (opened); searches: LLM interview practice adaptive question selection (context), automated scoring open-ended technical answers bias, safe RL action masking/guard layer (snippet only).

## Selection reasons and impact (abridged; full per-source notes in CORE files)
- Kadam et al. 2026: mandatory user-named target; highest novelty impact (Paper 3). Uncertainty: methods/results unread.
- SandboxEscapeBench, comparative sandbox study, fault-tolerant sandboxing: user-named recent leads; all three exist and were opened at abstract level; impact on Paper 1 wording (see NOVELTY_MATRIX).
- EACL 2026 code-judge biases: user-named lead; opened; impact on Paper 2 framing (established phenomenon family).
- Che et al. 2025 and Axak et al. 2025: found by adversarial search; change Paper 3's novelty assessment.
- Sources excluded as scholarly evidence: vendor/practitioner blogs (Northflank-type, Zylos, DEV Community, Medium, TrueFoundry etc.), Wikipedia, aggregator pages.

## Known limits of this provenance
- WebFetch answers come from a small summarising model; short quotes must be re-verified against the source.
- Several publisher pages (Wiley, Nature direct, PubMed, dblp, ScienceDirect direct) blocked automated fetch; ScienceDirect was read through the browser pane, which showed only the free portion.
- No citing-paper database was queried; forward chasing is limited to what search listings exposed.

## Gap-closure pass log (2026-09-21)
Tools: WebSearch, WebFetch (small-model summariser), the in-app browser pane, and local Bash for downloading public PDFs (arXiv and ACL Anthology PDFs and the Docker docs HTML, fetched with curl, no API, no credentials) and converting them to text for exact quote matching. No Semantic Scholar, OpenAlex, Crossref, Gemini, Deep Research or paid API. No paywall workaround. `free_pipeline/` untouched. Working copies of PDFs and text are in the session scratchpad, not the repository.

Searches and reads, grouped (about 27 further searches and 45 fetch/read/download attempts):
- Kadam et al.: two web searches for a preprint or repository (none), Zotero and repo grep (none), browser re-read of the ScienceDirect page (snippets and reference list; "View more references" expanded to 20 of 42), exact-title search for citing works (none).
- Adaptive assessment (Paper 3): the four user leads (Tang 2026; Wang et al. 2024; Qiu and Chen 2025; a 2026 RL knowledge-tracing paper found as Li et al., Sensors 2026), bandit adaptive difficulty search, adaptive interview RL search, curriculum RL/ZPD search, Doroudi and Riedmann searches; fetches of PMC and ACL Anthology pages, arXiv pages for Deep CAT, Schmucker, Jiang, UCO, PolyInterview; PDF text of Schmucker, Jiang, Olukola.
- Che et al.: search and full PMC page text read in the browser (99.9%, 6.563/6.564, 5.231, 5.213; no seed statement).
- Paper 2: searches for score-range bias, position bias, BEA 2026 rubric/hybrid, metamorphic testing, paraphrase robustness, verbosity in education; fetches of Fujinuma, Shi, AMATI, Cong, Deng, Soumik pages; PDF text of Moon, Schleifer, Norman, Li synthesis, Cho, Fujinuma.
- Paper 1: searches for Part 2 of the comparative study, AgentEscapeBench/host-side oracles, agent sandbox evaluation; PDF text of SandboxEscapeBench, SandboxEval, comparative study, RedCode, Abdelnabi, Singh, Rashidi, ReliabilityBench, MAS-FIRE, Yan, Li, Sahoo; Docker docs HTML.
- Quote audit: exact-match checks of about 60 quotations and numbers, recorded in QUOTE_AUDIT.md.

Blocked or not obtained: ScienceDirect full text (Kadam); Springer page for Wang et al. and for an engagement-aware RL question-selection chapter (redirect to cookie service); PubMed page for the AI-interviewer paper (consent wall); CaMeL PDF (returned HTML) and CALM PDF (corrupt download); JEM and Williamson pages (paywalled).
No forward-citation index was used; see P3_ADAPTIVE_ASSESSMENT_PRIOR_ART.md.

## Final-closure pass log (2026-09-21)
Tools: WebSearch, WebFetch (small-model summariser), the in-app browser pane (ScienceDirect Kadam page, Springer Riedmann page), and local Bash to download and convert public PDFs (Doroudi author version from a university web page; arXiv 2604.04237 and 2604.04251) with curl, no API and no credentials. No Semantic Scholar, OpenAlex, Crossref, Gemini, Deep Research or paid API was used.
Reads: Kadam page text re-read (no new body access); Riedmann page text; Doroudi PDF; MC-CPO and pedagogical-safety PDFs; abstract of Zhang et al. (arXiv:2601.15600); the IJRPR student review PDF. Frozen X3-A figures were confirmed by a read-only grep of the frozen evidence files (nothing edited).
Searches (about 9): Riedmann title, Doroudi title and PDF, an RL adaptive-interview-difficulty query, MC-CPO, post-hoc filter/action masking in tutoring RL, CAT RL versus heuristic, state-blind or constant baseline with equivalence in RL tutoring, technical-interview adaptive RL, exact-title citation search for Kadam, "Kaur 2024" existence. No new direct competitor found; search stopped by instruction.
Not obtained: Kadam article body; any citation index.
