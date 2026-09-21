# Paper 1 — abstract, keywords, figure/table and reference inventory (draft v1)

## Abstract
In `manuscript.md`. Word count: 242 (limit used: 250; the target venue's own abstract limit is not verified).

## Keywords (6)
containment testing; authority boundaries; fault injection; LLM-assisted assessment; test oracles; dependability evaluation

## Tables (4 in text)
| # | Reviewer question it answers | Source artifact |
|---|---|---|
| I | What property was tested, by what test, judged by which oracle and control? | protocols `PROTOCOL_X1-A_v2.md`, `PROTOCOL_X1-B_v3.md`, `PROTOCOL_X1-C_v2.md`; `x1b_harness_v3.py` (14 observables) |
| II | Which attacks were contained, what did permissive controls do, and what was observed? | `results/x1c/*`, `results/x1c_v2/*` |
| III | What failed on the baseline build, what was repaired, what was not run? | `results/x1a/verdicts.json`, `results/x1a_v2/verdicts.json` |
| IV | Was the invariance test adequately powered and could it detect an authority path? | `results/x1b/summary.json`, `results/x1b_v3/summary.json` |

Not tabulated in text (planned for appendix if the venue allows): per-run command lines, artifact hashes, environment record (`environment_and_verdicts.json`).

## Figures (0 generated yet; 2 planned, both must be generated from stored data)
| # | Content | Status | Source |
|---|---|---|---|
| F1 | Experimental and observability diagram: components, which paths can write score/difficulty/best-answer fields, where each oracle observes (host canary listener, canary hash, docker events, orphan check, in-state observables), and the follow-up channel marked "untested dependency" | NOT YET DRAWN | code reading; `channel_enumeration.json` |
| F2 | Attack–control–oracle matrix (builds A and B side by side), marking the four attacks where executor status did not discriminate and SEC-01 as filter-blocked | Could be merged with Table II; draw only if space allows | `environment_and_verdicts.json` (A and B) |

No generic system-architecture figure is planned.

## References (14 in text)
Verification levels are those recorded in `research/literature/claude_web_research/BIBLIOGRAPHY.md` and `QUOTE_AUDIT.md`; none was re-read in this pass except the venue pages. "Read" = full-text read in a previous pass.

| # | Reference | Level | Used for |
|---|---|---|---|
| 1 | Marchand et al. SandboxEscapeBench, arXiv:2603.02277 | full text read (earlier pass); preprint | benchmark design, host-side flag, weakened configurations |
| 2 | Rabin et al. SandboxEval, arXiv:2504.00018 | full text read; preprint | 51-case suite, in-payload outcomes |
| 3 | Andronchik & Lokhmakov, arXiv:2606.08433 | front matter/abstract/method read; preprint | engine classes, verdict semantics |
| 4 | Singh et al., arXiv:2606.18532 | abstract/intro read; preprint | bounded deployment claims |
| 5 | Rashidi SoK, arXiv:2607.05743 | abstract-level; preprint | denylist failure rate (third-party figure) |
| 6 | Guo et al. RedCode, arXiv:2411.07781 | abstract and method read; venue not verified | deterministic state checks |
| 7 | Abdelnabi et al., arXiv:2605.22568 | full read; preprint | canary tokens |
| 8 | Basiri et al., IEEE Softw. 33(3), 2016 | metadata verified; content not read | fault injection as practice |
| 9 | Jia et al. MAS-FIRE, arXiv:2602.19843 | abstract; preprint | fault injection in LLM agent systems |
| 10 | Gupta ReliabilityBench, arXiv:2601.06112 | numbers only checked; preprint | stress-condition evaluation |
| 11 | Debenedetti et al. CaMeL, arXiv:2503.18813 | abstract-level only; preprint | design-level separation (no numbers quoted) |
| 12 | Li et al., arXiv:2606.03090 | abstract read; preprint | grader prompt injection |
| 13 | Sahoo et al., arXiv:2601.21360 | abstract fragment; author list incomplete | code-evaluation injection failures |
| 14 | Docker Docs, seccomp | official documentation, page HTML read (accessed 2026-09-21) | default-profile ptrace behaviour |

Verified references: 14 (all with bibliographic details confirmed in earlier passes; 9 of 14 are preprints; only [8] and [14] are non-preprint, and [1] carries an ICML header not confirmed against the proceedings). No reference is cited whose entry is marked "do not cite". No DOI, page range or venue was added beyond the verified entries.

## Not used although in the package
Sultan et al. 2019 (summary only), Yan 2025 (self-reported results), Bhattarai & Vu and Madatha (unread), Avizienis et al. 2004 (not re-verified).
