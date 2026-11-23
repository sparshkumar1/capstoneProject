# Final audit report — ADCOM 2027 manuscript (written 2026-10-02)

## 1. Architecture found
Centrally orchestrated, role-separated pipeline; not a decentralised multi-agent system (`architecture/ARCHITECTURE_INVENTORY.md`).
Hub `InterviewOrchestrator` (`agents/orchestrator/interview_orchestrator.py:119`, `handle_voice_answer` :369), learned scorer
(`services/evaluator/app.py:451`), validator (`agents/validation/score_validator.py:55`), feedback role
(`agents/orchestrator/feedback_agent.py:77`), follow-up role (`interview_orchestrator.py:1822,1861`), PPO difficulty policy +
guardrails (`agents/strategy/hybrid_orchestrator.py:165`, `interview_orchestrator.py:1631`). One 1.5B LLM serves three roles. Measured
write authority over 186 traced turns: scorer/validator/feedback 0 state keys, follow-up 1 (queue), policy 14, hub commit 22.
Only the difficulty policy is a learned, reactive decision-maker. Indirect coupling (follow-up text → scorer question text →
committed score → policy observation) is read from code, not measured.

## 2. Track and fit
Primary "Agent-native development and lifecycle engineering", secondary "Preemptive agentic security and resilience"
(`GO_NO_GO_ADCOM_FIT.md`). Fit is moderate, not strong; "Core multi-agent systems" fit is weak and the paper says so. Decision: GO, narrowed.

## 3. Research question and contributions
Which orchestrator-level mechanisms keep the stored record faithful under component faults, and what do they cost? Contributions:
authority matrix; pre-registered mechanism × fault ablation (replay); two measured changes; failure-path latency; grounding probe.
Application/engineering contribution, not an algorithmic one (`CONTRIBUTION_AND_NOVELTY_STATEMENT.md`).

## 4. Improvements and measured effects
| Change | Evidence that motivated it | Measured effect | Cost / trade-off |
|---|---|---|---|
| Strict scorer→hub contract (config key, default on) | E1 F3: shipped system committed malformed scorer output in 160/160 sessions (None/NaN/string → 0.0; 1.7 → 1.0) | invalid commits 0 in every E4 cell (baseline: 192, 192, 192, 184, 192 commits per 8 sessions; F6 p=0.10: 144/160 baseline sessions affected, 0/160 strict); fault-free paths identical | with every call malformed no session progresses (integrity over availability); with 10 % malformed, all 160 sessions finished |
| Circuit breaker for the Qwen service | E2: hanging service 24.7 s/turn (495 s for 24 turns) | median 3.1 s (P=30 s) and 6.2 s (P=60/120 s); total 495 → 80–155 s; attempts 80 → 13–25; scores identical in all runs; healthy: never opened; recovery on first call after service returned | threshold 2 and cooldown 60 s were fixed beforehand, not tuned; first turn still pays 12.4 s; pacing P is a modelled think time (breaker clock injected) |
No change to the validator, guardrails, reward, state or action definitions, or PPO.

## 5. Experiments (exact sizes)
- Trace: 8 sessions, 186 turns (64 primary, 122 follow-up). Descriptive; run before the protocol.
- E1: 752 sessions, 18 cells; 8 sessions per deterministic cell, 20 seeds × 8 for F2/F3 cells; 14 predictions, 14 matched.
- E2: 1 session (24 turns) × 3 server modes; real sockets and timeouts.
- E3: 64 recorded scorer payloads × 7 constructed output types (applicable 64/57/10/57/57/64/64).
- E4: 8 sessions per deterministic cell; 160 sessions for F2 and F6; baseline and strict.
- E5: 1 session (24 turns) × 7 scenarios.
Key results are in the manuscript and `results/`.

## 6. Failed, inconclusive, or not run
- Not run: any live LLM, scorer, embedding, or sandbox path; any real-candidate or human evaluation; comparison with a single-agent/monolithic baseline (the pipeline has no such implementation and building one with comparable model access was not possible without the LLM); effect of follow-up coupling on scores (replay cannot measure it); PPO benefit (not an ADCOM question here).
- Inconclusive/odd: F2 seeds 0–19 gave 15/160 non-terminating V0 sessions against an analytic ~30 % per-session expectation (reported, not re-selected); server-side request counts in E2 disagreed with client attempts (96 vs 80) and a minimal check reproduced an excess (3 → 5), cause uninvestigated (client counts used); first test run had 2 failures that did not reproduce (one cause identified: missing `python-multipart`; the other, `test_evaluator_failure_produces_structured_failure_without_fabrication`, unexplained); E4 and E5 were designed after seeing E1/E2 (pre-registered before their own runs, disclosed).
- Harness limits: replay candidate never improves; follow-ups answered with the root answer; scripted "healthy" LLM responses are template content.

## 7. Tests
Branch: 23 failed, 329 passed, 14 skipped, 36 errors. Baseline snapshot `cb888f2`: 23 failed, 306 passed, 14 skipped, 36 errors. Failing sets are identical
(Docker sandbox, faiss/model downloads, plus the project's documented known failure `test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics`). New tests: 19 (contract) + 4 (breaker) pass. One existing test was changed deliberately.

## 8. Manuscript
`ADCOM2027_submission_blind.pdf`, 12 pages including references and a one-page appendix, 0.30 MB, Springer `llncs` v2.24 (`runningheads`, `splncs04`), abstract 234 words (CCIS range 150–250), 14 references, 7 tables, 2 figures. All fonts embedded; no overfull boxes; every page inspected as rendered images.

## 9. Remaining risks
Scientific: modest novelty (engineering study; most "known" predictions confirm designed behaviour); replay evidence only; no live-model evidence; small, constructed fixture; no human or learning evidence; related work from search summaries only. Formatting: official CCIS template and ADCOM instructions not verified; fonts are Computer Modern from llncs. Submission: CFP facts (15 Oct 2026, 20 pages, double-blind, CMT) rest on the text supplied in the task; the official page is unreachable here. Overlap with the authors' other manuscripts (same system, same stored scorer outputs as replay input) must be checked against concurrent-submission rules. The branch changes system behaviour (strict contract on by default); manuscripts that describe the earlier system (tested commits) must keep referring to those commits.

## 10. Readiness
Ready for author review as a narrowed engineering paper, **not** as a multi-agent or learning contribution and not confirmed submission-ready: a no-go would be warranted only if the venue rejects systems/dependability scope or the authors cannot accept replay-only evidence. Acceptance is not predictable and is not claimed.

## Author decisions required
1. Accept the narrowed framing (no multi-agent contribution claim) and the replay-only evidence, or request live-model runs on a machine with the model weights.
2. Keep or revert the two behaviour changes in the working branch (strict contract default on; breaker); decide whether the other papers' reproducibility notes must mention them.
3. Supply and verify the official ADCOM/CCIS template and CFP; re-check page limit, blind-review rules, supplementary-material rules, AI-use and data statements (none are included).
4. Decide how to handle overlap with the other submissions and whether the evaluator-output replay input counts as reuse of data.
5. Check licences of the scorer components and the LLM (not checked here) before any release of an artefact; decide whether to publish the anonymised artefact (not done).
6. Replace search-summary-based reference details by checked ones; confirm that the arXiv preprints cited have not appeared in venues.
