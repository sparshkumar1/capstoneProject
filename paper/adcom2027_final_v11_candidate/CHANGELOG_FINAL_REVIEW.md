# Change log — final review cycle (after 9d37a06)

| Change | Why | Files |
|---|---|---|
| New experiment XC (threshold decomposition and sensitivity), protocol written and tagged `prereg/MA-XC/v1` before any run, then run once | XA's M4 removes four checks at once, so the paper's attribution of the collapse to the confidence threshold was not isolated | `research/multiagent/protocols/PROTOCOL_MA_XC_v1.md`, `configs/ma_xc_v1.json`, `experiments/xc_threshold.py`, `analysis/analyze_xc.py`, `results/xc/*` |
| Independent recomputation of XA/XB from raw runs (new code) plus a post hoc cluster bootstrap over the 8 recorded answer sets | The 160 sessions per condition are 8 answer sets × 20 orders (dependent); session-level intervals were too narrow, and the extra-turn effect is driven by one answer set | `research/multiagent/analysis/independent_check.py`, `results/post_hoc/cluster_bootstrap.json` |
| Paper text: XC subsection and method paragraph, cluster-bootstrap sentence in XA, M4 wording, "why two agents" paragraph, kind-of-contribution paragraph, post hoc disclosure in limitations, abstract, contributions | Make claims match the evidence and state what is and is not isolated | `manuscript/sec_*.tex`, `main.tex` |
| Four references added (shielding, safe RL survey, MARL survey, clustered bootstrap) and cited where they support a specific statement | Positioning of the guardrail layer, the "not MARL" statement and the statistics | `manuscript/refs.bib`, `sec_related.tex`, `sec_method.tex` |
| Layout: float placement (all tables had been collected after the references), Fig. 3 redrawn (text was illegible), tables made legible, authority and fault tables left-aligned, minus signs | Defects found in visual inspection | `manuscript/main.tex`, `figures/fig3_validation.tex`, `scripts/make_tables.py`, `scripts/make_authority_table.py` |
| Claim audit extended (XC, post hoc, E5): 49 → 59 checks | Every new number is checked against the PDF text | `verification/verify_paper.py` |
| Audit documents rewritten/added | Required deliverables | `FINAL_AUDIT_REPORT.md`, `CLAIM_EVIDENCE_MAP.md`, `SUBMISSION_CHECKLIST.md`, this file |

Not changed: agent, hub, evaluator, PPO and persistence code; all historical protocols, configs and result files (write-once); frozen branches.

---
## Addendum 2026-10-02 (end-to-end audit cycle; history above preserved)
Superseding details are in `APPLICATION_END_TO_END_AUDIT.md` (addenda 1 and 2), `FINAL_CHANGELOG.md` and `FINAL_INDEPENDENT_AUDIT.md`. Summary: the multi-agent layer is now reachable in the shipped backend through the server-side `PREPAIRED_MULTIAGENT` variable (default off; commit 3dbb4ed); both end-to-end sessions (flag off/on) completed with 40 feedback events each (0 vs 40 coaching plans) using a recorded-evaluator substitute; fresh regression: frozen 306/14/23/36, HEAD 421/15/23/36 with the identical 59 failing IDs; frontend 28/28 and build OK; post hoc leave-one-cluster-out analysis added (k=1 is influential; the level-change interval excludes zero only with all eight sets or without k=1); paper 19 pages, claim audit 69/69, blind audit clean. Still open: official CFP/template, full-text reference checks and similarity check, real evaluator/live LLM/human evidence, two-agent necessity, author decisions listed in `FINAL_SUBMISSION_CHECKLIST.md`.
