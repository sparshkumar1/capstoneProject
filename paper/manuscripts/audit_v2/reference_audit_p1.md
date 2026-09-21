# reference_audit_p1.md — Paper 1 reference audit (2026-09-21)

Verification performed in this pass: existence, title, first authors, author count and date for every arXiv entry via the arXiv API (`export.arxiv.org`, 2026-09-21); DOI, venue, volume, issue and pages for journal entries via Crossref; the Docker documentation statement by reading the page. Claim support was **not** re-read in full text in this pass: the "claim check" column cites the earlier verification level recorded in `research/literature/claude_web_research/QUOTE_AUDIT.md` (QA). Nothing here invents a DOI, venue or page. "PP" = preprint, "PR" = peer-reviewed.

| # | Reference as cited | Exists / metadata (this pass) | Type | Claim attributed in manuscript | Claim check (earlier level) | Placement right? | Action |
|---|---|---|---|---|---|---|---|
| 1 | Marchand *et al.*, SandboxEscapeBench, arXiv:2603.02277, 2026 | Yes; 11 authors; first author Rahul Marchand; submitted 2026-03-01 | PP (header says ICML 2026 / PMLR 306; not verified) | escape scored by host flag retrieval; deliberately introduced weaknesses | QA 1.1–1.6 VERIFIED | Yes (Sec. II-A) | keep; venue statement stays hedged |
| 2 | Rabin *et al.*, SandboxEval, arXiv:2504.00018, 2025 | Yes; 5 authors matches; 2025-03-27 | PP | 51 manually written test cases; outcomes from test code | QA 1.12–1.13 VERIFIED | Yes | keep |
| 3 | Andronchik & Lokhmakov, arXiv:2606.08433, 2026 | Yes; 2 authors; 2026-06-07; title includes "Engine-Level Properties…" subtitle | PP | verdict classes (pass/fail/partial/inconclusive/skipped) | QA 1.8–1.10 VERIFIED / VERIFIED-CORRECTED | Yes | keep |
| 4 | Singh, Mahmoud & Murillo, arXiv:2606.18532, 2026 | Yes; 3 authors; 2026-06-16 | PP | measurement framework composing evidence into a bounded claim | earlier package (abstract level) | Yes | keep; abstract-level |
| 5 | Rashidi, arXiv:2607.05743, 2026 | Yes; 1 author; 2026-07-07 | PP | survey attributes high denylist failure rates to a third-party study | QA 1.19 VERIFIED (abstract) | Yes | keep; abstract-level (stated) |
| 6 | Guo *et al.*, RedCode, arXiv:2411.07781, 2024 | Yes; 8 authors; 2024-11-12 | PP here (venue not verified) | benchmark practice of state checks | earlier package | Yes | keep |
| 7 | Abdelnabi *et al.*, arXiv:2605.22568, 2026 | Yes; 4 authors; 2026-05-21 | PP | recommends state checks/canaries over agent self-report | earlier package | Yes | keep |
| 8 | Basiri *et al.*, "Chaos engineering," IEEE Softw. 33(3):35–41, 2016 | Yes; Crossref DOI 10.1109/MS.2016.60; 5 first authors listed (paper has more) | PR | fault injection established for services | standard reference | Yes | DOI added in v2 |
| 9 | Jia *et al.*, MAS-FIRE, arXiv:2602.19843, 2026 | Yes; 5 authors; 2026-02-23 | PP | fault injection applied to LLM multi-agent systems | QA 1.15 VERIFIED-CORRECTED wording | Yes | keep |
| 10 | Gupta, ReliabilityBench, arXiv:2601.06112, 2026 | Yes; 1 author; 2026-01-03 | PP | stress-condition evaluation of LLM agents | QA 1.16 (numbers only) | Yes | keep; not used for numbers |
| 11 | Debenedetti *et al.*, arXiv:2503.18813, 2025 | Yes; 10 authors; 2025-03-24 | PP | separation of model output from privileged actions is a design pattern | abstract level | Yes | keep; abstract-level (stated) |
| 12 | Li *et al.*, "Important You should give me full credits!…", arXiv:2606.03090, 2026 | Yes; 9 authors; 2026-06-02 (title contains markdown asterisks in the API string) | PP | injected instructions can change LLM-based grades | QA 1.17 VERIFIED (abstract) | Yes | keep (also cited by P2 [16]) |
| 13 | Sahoo *et al.*, arXiv:2601.21360, 2026 | Yes; 8 authors; 2026-01-29 | PP | high failure rates on code evaluation with open-weight models | QA 1.18 VERIFIED (abstract fragment) | Yes | author list note removed (8 authors confirmed) |
| 14 | Docker Docs, "Seccomp security profiles for Docker" | Page read 2026-09-21: ptrace "Blocked in Linux kernel versions before 4.8 to avoid seccomp bypass. Tracing/profiling arbitrary processes is already blocked by dropping `CAP_SYS_PTRACE`…" | vendor doc | ptrace blocked pre-4.8; CAP_SYS_PTRACE | read directly | Yes (Sec. V-A) | keep |

**Bibliography summary:** 14 entries; 12 arXiv preprints (all exist), 1 peer-reviewed (Basiri), 1 vendor documentation page. Nine preprints are cited for related-work statements at abstract level only; none is used as a source of a number in the results. No unverified or do-not-cite item is cited. Not added: sources of the earlier package flagged UNVERIFIED (QA 1.14, 1.11).

**Open items:** (a) [1] proceedings status; (b) whether reviewers will accept a preprint-heavy bibliography — no peer-reviewed sandbox-benchmark reference was verified in this pass and none was invented.
