# Claim → implementation → experiment → evidence

Evidence classes: REPLAY (64 recorded evaluator payloads through the real hub, Qwen stubbed down), FAULT-INJECTED, SOCKET, SYNTHETIC. No LIVE-LLM, no HUMAN evidence.
"Verified" = recomputed from raw run files by `research/multiagent/analysis/independent_check.py` or `verification/verify_paper.py` (59 checks).

| # | Paper claim | Implementation | Experiment / class | Evidence (committed) | Status |
|---|---|---|---|---|---|
| 1 | Agents change the difficulty path in all 160 sessions per condition | `strategy_agent.py`, `coordinator.decide_difficulty` | XA M1 vs B0, REPLAY | `results/xa/xa_runs.jsonl`, A7 | Verified. Sessions are dependent (8 answer sets). |
| 2 | Level changes 15.12 → 12.45, reversals 11.74 → 9.87 | same | XA | `xa_summary.csv`, `xa_paired.csv`; post hoc cluster CIs in `results/post_hoc/cluster_bootstrap.json` | Verified. Session-level CIs are too narrow; cluster CIs ([−4.50,−0.24], [−3.12,−0.27]) reported. Behaviour, not quality. |
| 3 | +0.59 turns from proactive probes | `arbitrate_probe` | XA | cluster CI [0.00, +1.76]; 1 of 8 answer sets shows an increase | Verified; paper states it is driven by one recorded session. |
| 4 | Committed scores stay authoritative; transitions valid | `runtime.commit`, hub is sole writer | XA A2/A3, XB B1 | 1,920 + 1,760 sessions, all pass | Verified. At ceiling: does not discriminate safeguards. |
| 5 | Layer transparent when no agent contributes | `runtime`, `coordinator` | XA A4 (M2 = B0); `tests/integration/test_ma_workflow.py` (k = 0, 3, 6) | paths identical in 160/160 | Verified. |
| 6 | Coaching, communication, grounding, authority ablations leave fault-free paths unchanged | `coaching_render.py`, `grounding.py`, `authority.py` | XA A5 | paths identical | Verified. Implies a merged single component would behave the same on these metrics. |
| 7 | Removing the confidence threshold alone collapses the Strategy Agent | `arbitration.arbitrate_difficulty` | XC C1 (new, registered before run), REPLAY | `results/xc/*` (τ=0: level changes 2.225, agreement 0.014, bypass 0) | Verified. XA's M4 alone could not show this (removes four checks). |
| 8 | Behaviour flat for τ in 0.5–0.8; Strategy Agent silent at τ=0.9 | confidence = min(0.95, 0.5+0.1n) | XC C2–C5 | `xc_summary.csv` | Verified. Says nothing about which τ is better. |
| 9 | Guardrail bypass 38/40 sessions without arbitration, 0/40 with | `coordinator` (arbitration off skips guardrails) | XB B3, FAULT-INJECTED | `xb_runs.jsonl` | Verified; partly by construction (M4 skips the guardrail layer), stated in the paper. |
| 10 | Ungrounded emphasis 40/40 without the check, 0/40 with | `grounding.check_plan` | XB B4 | `xb_runs.jsonl` | Verified. |
| 11 | Forbidden keys: authority check changes classification, not containment | `authority.py`, schema | XB B2 | 152 injections | Verified. |
| 12 | Well-formed but wrong proposals are not detected | none (design limit) | XB adversarial_valid (930 injections) | final source 10.8 decisions/session in full config | Verified; stated as a limitation. |
| 13 | Timeout cost ≈ configured timeout | `coordinator._call` | XB B5 | p95 154.4 ms vs 4.4 ms | Verified. |
| 14 | Breaker opens in 29/40 sessions (72.5%); B6 contradicted | per-agent `CircuitBreaker` | XB B6 | identical rate in all seven cells because they share one seeded fault schedule per (k, seed) | Verified; same-schedule explanation added to the audit report. |
| 15 | PPO unavailable: agents change the path in only 4/160 sessions (A9 contradicted) | heuristic fallback | XA M7 vs B7 | `xa_predictions.csv` | Verified. |
| 16 | Canonical vs legacy guardrails identical on replay (A10 contradicted) | `guardrail_impl` switch | XA B0c | 0/160 differ | Verified; replay has no audio, so the divergent regions are not reached. |
| 17 | 11.8% (4,728/39,930) guardrail disagreement on a grid | `rl/guardrails.py` vs inline | `tests/unit/test_guardrail_impl.py` | pinned counts | Verified. |
| 18 | Historical E1 reproduces byte-for-byte under explicit flags | `strict_evaluator_contract`, breaker flags | XE e1 | `results/xe_e1/xe_e1_reproduction.json` | Verified (752 sessions). |
| 19 | 5xx breaker semantics: far fewer HTTP attempts | `circuit_breaker.record_http` | XE b503, SOCKET | `results/xe_b503/xe_b503.json` | Verified, one session. |
| 20 | E5 breaker timings (new run, not a reproduction) | same | XE e5, SOCKET | `results/xe_e5/e5_circuit_breaker.json` | Verified; single run on one machine. |
| 21 | Rebuilt grounding probe: 17 rejections were artefacts; paraphrased credit accepted 57/57 | `_validate_feedback_output` | XD, SYNTHETIC | `results/xd/xd_grounding.json` | Verified; says nothing about LLM output. |
| 22 | The agents are rule-based, the system is centralised, PPO is not MARL | all of `agents/multiagent/` | architecture | code, `ARCHITECTURE_ASSESSMENT.md` | Verified by code reading. |
| 23 | Coaching quality, learning, evaluator validity, PPO improvement | — | none | — | NOT CLAIMED; no evidence exists. |

---
## Addendum 2026-10-02 (end-to-end audit cycle; history above preserved)
Superseding details are in `APPLICATION_END_TO_END_AUDIT.md` (addenda 1 and 2), `FINAL_CHANGELOG.md` and `FINAL_INDEPENDENT_AUDIT.md`. Summary: the multi-agent layer is now reachable in the shipped backend through the server-side `PREPAIRED_MULTIAGENT` variable (default off; commit 3dbb4ed); both end-to-end sessions (flag off/on) completed with 40 feedback events each (0 vs 40 coaching plans) using a recorded-evaluator substitute; fresh regression: frozen 306/14/23/36, HEAD 421/15/23/36 with the identical 59 failing IDs; frontend 28/28 and build OK; post hoc leave-one-cluster-out analysis added (k=1 is influential; the level-change interval excludes zero only with all eight sets or without k=1); paper 19 pages, claim audit 69/69, blind audit clean. Still open: official CFP/template, full-text reference checks and similarity check, real evaluator/live LLM/human evidence, two-agent necessity, author decisions listed in `FINAL_SUBMISSION_CHECKLIST.md`.
| Claim (2026-10-02 additions) | Evidence |
|---|---|
| Level-change interval excludes zero only with all 8 sets or without k=1; sign better supported than interval | `research/multiagent/results/post_hoc/leave_one_cluster_out.json` (script `analysis/leave_one_cluster_out.py`; post hoc) |
| Shipped backend enables the layer only via server env variable, default off | `apps/backend/main.py::_multiagent_server_config`; `tests/integration/test_ma_backend_flag.py` (12 pass) |
| Fresh test counts in Limitations | `results/e2e_audit/shipped_path/pytest_*_2026-10-02.txt` |
