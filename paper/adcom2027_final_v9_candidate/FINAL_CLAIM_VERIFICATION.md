# Final claim verification (independent audit, 2026-10-02)

Status: **VERIFIED** (recomputed or re-run by me from raw data/code in this audit), **VERIFIED-BY-READING** (code read and compared), **CORRECTED** (paper was inaccurate; fixed in this audit), **NOT VERIFIED** (could not be checked here).
Evidence classes: REPLAY / FAULT-INJECTED / SOCKET / SYNTHETIC. No LIVE-LLM, no HUMAN evidence.

| # | Claim (manuscript location) | Implementation / evidence | Status | Correction made / needed |
|---|---|---|---|---|
| 1 | Abstract: 160 sessions per condition, "the sessions reuse 8 recorded answer sets" | `results/xa/xa_runs.jsonl`: 12 conditions × 160 = 1,920 rows, 8 k × 20 seeds | VERIFIED | none |
| 2 | Abstract/§6.1: agents change difficulty path in all 160 sessions (A7) | `independent_check.py`, my own exact test | VERIFIED | none |
| 3 | §6.1: level changes 15.12 → 12.45; reversals 11.74 → 9.87; PPO agreement 0.626 → 0.400 | raw runs | VERIFIED | none |
| 4 | §6.1: cluster bootstrap level changes −2.67 [−4.50, −0.24] | my exact enumeration of all 8^8 resamples: −2.669 [−4.494, −0.219]; the paper's Monte-Carlo (B=10,000, seed 20270101) differs by ≤0.02 | VERIFIED | none |
| 5 | §6.1: extra turns +0.59, "only 1 of 8 answer sets shows an increase" | per-answer-set differences: followups [0, +4.7, 0, 0, 0, 0, 0, 0] (k=1) | VERIFIED | none |
| 6 | (not in paper before) direction of level-change effect across answer sets | per-set level-change differences [−2.55, **+4.95**, −4.05, −5.95, −2.05, −2.70, −5.50, −3.50]; reversals [−3.30, **+3.00**, …] | CORRECTED | added: decreased in 7 of 8 sets, increased in one (the same k=1 that has all the extra turns) |
| 7 | §6.1: 11.9 Strategy-over-PPO conflicts per session; 47.7 agent calls | conflicts mean 11.9375, calls 47.675 | VERIFIED | none |
| 8 | Table 3 / Table 4 values | regenerate identically from raw runs in a clean clone; `verify_paper.py` | VERIFIED | none |
| 9 | §3.2 Strategy Agent rules (recover/remediate/stretch/steady thresholds) | `strategy_agent.py` read; thresholds match (extra conditions: difficulty bounds, probe budget) | VERIFIED-BY-READING | none (abstraction) |
| 10 | §3.2: "Confidence min(0.95, 0.5+0.1n) … evidenced proposals sit at 0.6 to 0.8" (earlier text) | `_conf(len(ev))`; the score is always one evidence item. Re-run of M1 over all 160 sessions: 3,814 proposals, confidences only 0.45 (1,274), 0.70 (312), 0.80 (2,228) | CORRECTED | text now says non-steady proposals carry 0.70 or 0.80; realised distribution reported |
| 11 | (not in paper before) Strategy `stretch` rule exercised | 0 stretch proposals in 3,814 | CORRECTED | added to §6.1 and §9: the agent only held or lowered difficulty; stretch rule untested here |
| 12 | §6.3 XC: τ=0 alone reproduces M4's collapse (2.225 / 0.014) with 0 bypass | `results/xc/*`; XC predictions C1–C5 all SUPPORTED when re-derived | VERIFIED | none |
| 13 | §6.3 XC: "behaviour flat for τ 0.5–0.8 … plateau" (earlier interpretation) | follows from the two-valued realised confidence (0.45/0.70/0.80), not robustness | CORRECTED | reinterpreted in §6.3 |
| 14 | §5/§9: XC "registered … before the XC run" | tag `prereg/MA-XC/v1` (commit `01186fb`) precedes the run; XC designed after XA/XB were seen | CORRECTED | wording: "prospectively tagged experiment designed after seeing XA/XB, not a preregistration made before the earlier results" |
| 15 | §4: arbitration order (hard constraints → guardrails last → validated Strategy ≥ τ with evidence → PPO) | `arbitration.py` read | VERIFIED-BY-READING | none |
| 16 | §4: "agents never see the PPO action before they propose" | hub collects proposals during answer handling; `ppo_action` is attached to the observation only at arbitration (`runtime.difficulty`) | VERIFIED-BY-READING | none |
| 17 | §3.2: coaching renderer "adding presentation fields only" (earlier text) | `coaching_render.py`: also prepends a priority tip to, and truncates, existing `how_to_improve` / `actionable_improvements` / tip lists; protected keys never change | CORRECTED | text and Fig. 2 label corrected |
| 18 | Fig. 2 caption "The code path collects only the Strategy proposal" (ambiguous) | code-submission path: `collect(obs, coach=False)` | CORRECTED | now "On the code-submission path only the Strategy proposal is collected" |
| 19 | §6.2 B1–B6, 1,760 sessions, 38/40 vs 0/40 bypass, 40/40 vs 0/40 leak | `independent_check.py` + raw runs | VERIFIED | none |
| 20 | §6.2 B6: 29/40 sessions, same in all fault types | identical because the fault RNG is seeded by (k, seed) only | VERIFIED | explanation present in text |
| 21 | Bypass 38/40 "without arbitration" | removing arbitration also removes the guardrail layer (`coordinator.decide_difficulty`), so the metric is partly by construction | VERIFIED-BY-READING | paper already states this; unchanged |
| 22 | §7 I7 violated in 3/8 (V2) and 7/8 (full) sessions | `paper/adcom2027/results/e1_runs.jsonl`: 3 and 7 | VERIFIED | none |
| 23 | §7 b503: 160 vs 2 requests; 0.302 s vs 0.002 s per turn | `results/xe_b503/xe_b503.json` | VERIFIED | none |
| 24 | §7 e1: 752 sessions byte-identical (sha256 889bb142…) | `results/xe_e1/xe_e1_reproduction.json` | VERIFIED (stored result; I did not re-run E1) | none |
| 25 | §7 E5 seven socket scenarios, new run vs earlier | `results/xe_e5/e5_circuit_breaker.json` vs `paper/adcom2027/results/e5_circuit_breaker.json` (values in macros) | VERIFIED (read from stored files; not re-run: 16 min of real timeouts) | none |
| 26 | §7 sigmoid vs logits (1.55, −7.95 on version 6.1.0) | model weights are an LFS pointer; test skipped | NOT VERIFIED | none possible here |
| 27 | §7/§3 11.8% (4,728/39,930) and 7.4% on a full grid | pinned by `tests/unit/test_guardrail_impl.py` (passes) | VERIFIED (11.8%); 7.4% not independently recomputed | none |
| 28 | §6.4 XD counts | `results/xd/xd_grounding.json`; claim audit | VERIFIED (counts read and compared) | none |
| 29 | Abstract/§8: "13 of 16 registered predictions supported; A9, A10, B6 contradicted" | `xa_predictions.csv`, `xb_predictions.csv`; recomputed | VERIFIED | none |
| 30 | §8 "Why two agents": evidence does not show two agents are needed | A5: M3 changes no path; no single-agent baseline exists | VERIFIED (claim is a limitation) | smallest closing experiment described in FINAL_INDEPENDENT_AUDIT.md §7 (not run) |
| 31 | §9: Python suite 23 F / 36 E, "same 59 identifiers" as clean export of freeze commit | re-run here: HEAD 409 P / 15 S / 23 F / 36 E; frozen export 306 P / 14 S / 23 F / 36 E; ID sets identical (comm) | VERIFIED | none |
| 32 | §9: 81 new tests, 80 pass, 1 skipped | re-run: 80 passed, 1 skipped | VERIFIED | none |
| 33 | "the flag … behind a feature flag" / enabled mode integrated in the workflow | flag is a constructor option; **the shipped REST backend never sets it and the web client has no agent display** | CORRECTED | new limitation "Deployment surface" in §9 |
| 34 | Agent ledgers restored after restart | real-server kill/restart test: session resumed, ledgers restored; call counters and decision records restart at 0 | VERIFIED; limitation added | §9 sentence added |
| 35 | Not MARL / not decentralised / rule-based agents | code read | VERIFIED-BY-READING | none |
| 36 | Candidate learning, coaching quality, evaluator validity, PPO improvement | no evidence exists | NOT CLAIMED (correctly) | none |
| 37 | Related work statements about [3], [9], [10], [17], [7], [14] | titles/abstracts via search results: [9] (hierarchical 5.5% vs 10.5/23.7% drop; Inspector recovers up to 96.4%), [10] (15 fault types, three injection mechanisms), [17], [7], [14] consistent | VERIFIED at search level | none |
