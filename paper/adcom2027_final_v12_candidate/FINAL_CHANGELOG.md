# Final changelog (independent audit, 2026-10-02; base commit `5b3ba25`)

Implementation code (`agents/`, `apps/`, `services/`, `rl/`, `tests/`) was **not changed**. Historical protocols, configs and result files were not changed. Frozen branches untouched. Validation after all edits: claim audit 65/65, blind audit 0 hits, PDF 19 pages, all 19 pages inspected, backend/frontend tests re-run (see `APPLICATION_END_TO_END_AUDIT.md`).

| File | Issue | Reason | Type | Validation |
|---|---|---|---|---|
| `manuscript/sec_arch.tex` | Confidence description said evidenced proposals "sit at 0.6 to 0.8" (via §6.3) and omitted that the score always counts as evidence | Code: `_conf(len(ev))`, realised confidences 0.70/0.80 | manuscript (factual) | `strategy_confidence_audit.py` over 160 sessions; claim audit |
| `manuscript/sec_arch.tex`, `figures/fig2_turn_flow.tex` | Renderer described as "adding presentation fields only" | `coaching_render.py` also prepends to and truncates existing tip lists | manuscript (factual) | code read; real-server payload comparison |
| `manuscript/sec_arch.tex` | Fig. 2 caption "code path collects only the Strategy proposal" ambiguous | clarity | manuscript | read |
| `manuscript/sec_results.tex` | Cluster-bootstrap sentence lacked the sign of the effect by answer set; Strategy proposal modes/confidences and absence of `stretch` unreported | exact enumeration shows 7/8 decrease, 1/8 increase (same set as the extra turns); 0 stretch proposals | manuscript (completeness) | `exact_boot.py` (all 8^8 resamples), claim audit |
| `manuscript/sec_results.tex` | XC "plateau" interpreted as robustness | plateau follows from two-valued confidence | manuscript (interpretation) | confidence distribution |
| `manuscript/sec_method.tex` | XC described as "registered" without noting it was designed after XA/XB | accuracy of pre-specification status | manuscript | commit/tag order |
| `manuscript/sec_limits.tex` | Missing: flag not exposed by shipped backend/UI; counters not restored; stretch rule untested; failure identity statement | application audit findings | manuscript (limitations) | real-server tests |
| `manuscript/sec_limits.tex`, `sec_related.tex`, `sec_carry.tex` | Condensed wording to keep a margin below the page limit | 20 pages → 19 pages | manuscript (formatting) | rebuilt PDF |
| `manuscript/sec_disc.tex` | Track fit mentioned only Track 2/3 | brief lists Track 5 containment/security topics | manuscript | read |
| `manuscript/refs.bib` | Title of [14] miscased | formatting | bibliography | PDF text |
| `scripts/make_tables.py` | New macros for the confidence distribution (thousands separators) | generated numbers | tooling | regenerated; claim audit |
| `verification/verify_paper.py` | Added checks for the new numbers (49→59→65 checks) | every new number checked against the PDF text | tooling | 65/65 |
| `research/multiagent/analysis/strategy_confidence_audit.py`, `results/post_hoc/strategy_confidence_distribution.json` | New post hoc audit (not a registered experiment): deterministic re-run of M1 over the 160 sessions counting Strategy proposals by mode and confidence | evidence for the corrections above | analysis | output matches reading of the code; JSON records commit and `dirty: true` (script untracked at run time) |
| `research/multiagent/e2e/*`, `results/e2e_audit/summary.json` | New real-server end-to-end harness and summary | application verification | tooling/results | run in a scratch clone |
| `FINAL_INDEPENDENT_AUDIT.md`, `FINAL_CLAIM_VERIFICATION.md`, `APPLICATION_END_TO_END_AUDIT.md`, `FINAL_SUBMISSION_CHECKLIST.md`, this file | Required deliverables | — | documentation | — |
| `ADCOM2027_multiagent_blind.pdf`, `manuscript/main.bbl`, `manuscript/numbers.tex`, `tables/*` | Regenerated | follow from the source edits | build outputs | rebuilt from clean source |

Earlier files kept unchanged: `FINAL_AUDIT_REPORT.md` (previous cycle; its page count and test statements remain correct, its "all pages inspected" statement referred to the earlier build), `CLAIM_EVIDENCE_MAP.md`, `CHANGELOG_FINAL_REVIEW.md`, `SUBMISSION_CHECKLIST.md`, `OVERLAP_AUDIT.md`.

## 2026-10-02 addendum
- `apps/backend/main.py`: added `_multiagent_server_config()` and applied it at both orchestrator construction sites. Issue: multi-agent mode unreachable from the shipped backend. Experimental behaviour unaffected (default off). Validated by `tests/integration/test_ma_backend_flag.py` (11 passed) and a shipped-path real-server run. First implementation change since the original multi-agent implementation.
- `tests/integration/test_ma_backend_flag.py`: new.
- Still open from the 2026-10-02 brief: leave-one-cluster-out analysis, full-suite rerun, paper wording for the new reachability and PDF rebuild/inspection, final re-audit.
- `research/multiagent/analysis/leave_one_cluster_out.py` + `results/post_hoc/leave_one_cluster_out.json`: new post hoc LOCO (exact enumeration over 7 clusters; M1-B0; not registered). Result: dropping k=1 gives level changes -3.76 [-4.81,-2.78]; dropping any other single cluster gives intervals including zero; agreement decrease excludes zero in every drop; extra turns vanish when k=1 is dropped.
- `tests/integration/test_ma_backend_flag.py`: +1 test (restore follows current server flag; no cross-session leakage); 12 pass.
- Paper: `sec_results.tex` (LOCO sentence; per-set sign sentence), `sec_limits.tex` (Deployment surface rewritten for the env-var path; Environment test counts updated to the fresh run), `verification/verify_paper.py` (LOCO checks; 69/69), PDF rebuilt: 19 pages, 0 undefined references, blind audit 0 hits, no author/title metadata.
- Experimental behaviour: none changed. Implementation code: only `apps/backend/main.py` (config helper, default off).
