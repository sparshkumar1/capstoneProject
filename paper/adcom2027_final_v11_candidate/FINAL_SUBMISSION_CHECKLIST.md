# Final submission checklist (2026-10-02) — nothing has been submitted

Status: PASS / FAIL / PARTIAL / NOT VERIFIED. "Brief" = taken from the supplied submission brief, not verified against the official source.

## Official requirements
| Item | Status | Basis |
|---|---|---|
| Conference identity (31st ADCOM, Bengaluru, 10–11 June 2027) | PARTIAL | web search result snippets only |
| Deadline 15 Oct 2026, notification 28 Feb 2027, camera-ready 25 Mar 2027 | NOT VERIFIED | brief only; the search did not surface the CFP deadline |
| Tracks, theme | NOT VERIFIED | brief only. The paper's own fit statement: Track 2 (lifecycle engineering/testing) with relation to Track 5 (containment, authority) and Track 3 (coordination/trust); author decision |
| ≤ 20 pages including references and appendices | PASS (measured) / NOT VERIFIED (official counting rules) | 19 pages built from source; free space on page 19 ≈ 3–4 lines |
| Springer CCIS template and bibliography style | NOT VERIFIED | `llncs` + `runningheads` + bundled `splncs04`; `springer.com` is blocked by the network policy (HTTP 403 at the egress proxy); the current official version was not compared. PDF page size is US Letter (612×792 pt); the official template's paper size was not checked |
| CMT portal requirements, file type, declarations | NOT VERIFIED | portal not reachable |
| Double-blind | PARTIAL | see below |
| Original, unpublished, not under review elsewhere | NOT VERIFIED | author declaration; see overlap |

## Anonymity (audit of the final PDF and sources)
| Check | Status |
|---|---|
| Author/affiliation fields in the PDF read "Anonymous Author(s)" / "Anonymous Institution" | PASS |
| Names, e-mail, institution, product name, repo URLs, local paths in LaTeX sources, bibliography, tables, figure sources and extracted PDF text | PASS: `scripts/blind_audit.py` 0 hits; independent grep also clean (only DOIs) |
| PDF metadata (Author/Title/Subject/Keywords empty; Creator TeX; fonts embedded) | PASS |
| Source comments / tracked changes | PASS (no comments with identity; plain LaTeX) |
| Acknowledgments, funding, ethics statements | PASS (none present in the review copy) |
| Self-citations | PASS (none) |
| Reference to "an earlier audit of this system" (§1, §7) | PARTIAL: describes unpublished prior work of the same authors without citation; acceptable under double-blind only if that earlier work is not concurrently under review in a way that identifies the authors — author decision |
| Supplementary repository files (`research/`, `paper/`, e2e tools) contain project names and the git history carries author identities | NOT VERIFIED/RISK: do not upload the repository as supplementary material to the review system without anonymising |
| The user brief states five authors at an institution; the review copy contains no authors | PASS; an author-information record outside the PDF is still needed for camera-ready (NOT VERIFIED: not in repository) |

## PDF integrity
| Check | Status |
|---|---|
| Built from source with `latexmk -pdf`; 19 pages | PASS |
| Undefined references / citations | PASS (0); two small overfull boxes (≈20 pt) in the authority table, visually acceptable |
| Fonts embedded | PASS |
| Every page inspected as an image in the final build (pages 1–19) | PASS (inspected by me; tables 3–4 are small but legible) |
| Figure and table placement, captions with tables, references pages | PASS after fixes made in this cycle |

## Content integrity
| Check | Status |
|---|---|
| Claim audit (`verify_paper.py`) | PASS 65/65 |
| Central numbers independently recomputed (XA/XB/XC, cluster bootstrap, 1-of-8 answer sets) | PASS |
| Abstract matches body; no learning/quality/superiority claim; not decentralised/MARL | PASS |
| No-human / no-live-LLM limitation conspicuous | PASS (abstract, intro "Not claimed", §5, §9, conclusion) |
| Two-agent necessity | stated as not shown (§8) |
| Python suite green | FAIL (59 environment-related failures, identical to frozen baseline) |
| Live LLM / human evidence | FAIL (absent; not claimed) |

## References and originality
| Check | Status |
|---|---|
| 18 references exist and metadata matches | PARTIAL: checked through search results in this audit for [1], [2], [5], [6], [7], [9], [10] (first author/title/id only), [14], [17]; [3], [4], [8], [11], [12], [13], [15], [16], [18] were checked only in the previous cycle or are classical (not re-checked this audit) |
| Full text read | NOT VERIFIED (none) |
| Each citation supports its sentence | PARTIAL (abstract level) |
| Plagiarism/similarity check | NOT PERFORMED |
| Overlap with sibling manuscripts and concurrent submission | NOT VERIFIED (`OVERLAP_AUDIT.md` is a manual comparison of sources only; venue policies not retrieved) |

## Author decisions still required
1. Verify the CFP, deadline, track and the current Springer CCIS template/page counting.
2. Confirm originality/concurrent-submission position and disclose the reuse of the 64 recorded payloads and shared system description.
3. Provide author information outside the blinded PDF; decide what supplementary material (if any) is anonymised and uploaded.
4. Decide whether the "earlier audit" statements need rewording for anonymity.
5. Decide whether to run the smallest "two-agent necessity" experiment (see `FINAL_INDEPENDENT_AUDIT.md` §7) or keep the claim as a stated limitation.
6. Decide whether the shipped backend should expose the multi-agent flag (not done; product decision).
