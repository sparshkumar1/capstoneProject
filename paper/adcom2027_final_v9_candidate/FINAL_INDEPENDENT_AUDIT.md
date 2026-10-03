# Final independent audit — PREPAIred / ADCOM 2027 (2026-10-02)

Companion files: `FINAL_CLAIM_VERIFICATION.md`, `APPLICATION_END_TO_END_AUDIT.md`, `FINAL_SUBMISSION_CHECKLIST.md`, `FINAL_CHANGELOG.md`. Earlier reports are kept: `FINAL_AUDIT_REPORT.md`, `CLAIM_EVIDENCE_MAP.md`, `CHANGELOG_FINAL_REVIEW.md`, `SUBMISSION_CHECKLIST.md`, `OVERLAP_AUDIT.md`.
Labels: VERIFIED (I recomputed/re-ran), VERIFIED-BY-READING, SEARCH-LEVEL, NOT VERIFIED.

## 0. Verdict: CONDITIONALLY READY FOR AUTHOR REVIEW
Ready for the authors to read and decide; not ready to submit until the author-side items in §11 are done. The evidence supports the structural claims (typed bounded proposers, arbitration, containment behaviour on constructed replay data). It supports nothing about interview quality, coaching, learning, evaluator validity, or PPO improvement, and the paper says so. The official CFP, deadline, and current Springer template were not accessible, the references are only search-level verified, and the Python suite is not green in this environment.

## 1. Repository state (before any edit)
Branch `research/adcom2027-multiagent-final`, HEAD `5b3ba257…`, working tree clean, nothing pushed (`git ls-remote`: only `audit/claude-research-baseline` = `cb888f28…`, `freeze/engineering-baseline-407tests` = `54a5b739…`, `workspace/human-eval-clean-push`). All matched the reported state. Frozen files (`research/audit`, `research/papers`, `rl/checkpoints`, …) have an empty diff against `54a5b73`. Tags `prereg/MA-XA-XB/v1` (`380fb36`) and `prereg/MA-XC/v1` (`01186fb`) exist locally and are unpushed; no code changed between `380fb36` and the XC commit.

## 2. What was read
The whole manuscript (final PDF text, then the LaTeX sources), every figure and table, all 18 references, the previous audit documents, protocols (MA-XA-XB v1, MA-XC v1), configs, analysis scripts, raw run files (`xa`, `xb`, `xc` ≈ 1,920 + 1,760 + 960 rows), the multi-agent code (`contracts`, `authority`, `arbitration`, `coordinator`, `grounding`, `strategy_agent`, `coaching_render`, `runtime`, hub hooks, backend entry points), and the test files.

## 3. Official requirements (§3 of the brief)
Only the supplied brief was available. `springer.com`, `accsindia.org`, `cmt3`, Crossref return HTTP 403 from the egress proxy (policy denial; not circumvented). A web search returned snippets confirming the 31st ADCOM, Bengaluru, 10–11 June 2027; no CFP text or deadline. **Everything else (deadline, tracks, page rule, template, double-blind rule, CMT) is NOT VERIFIED and rests on the brief.**

## 4. Scientific review
### 4.1 Title and abstract
Title matches the implemented system (bounded-authority agents, centralised orchestration, coordination, arbitration, containment). Every abstract number was recomputed (160 sessions, 15.1 → 12.5, 1,760 sessions, 38/40 vs 0/40, 40/40 vs 0/40, 13/16, five XC predictions, 13/14, 17 artefacts, 57/57). No learning, superiority, decentralised or MARL claim. The abstract states "no language model ran". It says "registered experiments"; that is accurate for XA/XB (tag before run) and is qualified for XC in the body (prospectively tagged, designed after earlier results). **Remaining editorial point:** consider "pre-specified, locally tagged" instead of "registered" in the abstract, since tags have no external timestamp (author decision; not changed).

### 4.2 Introduction and contributions
Problem and RQs are clear. Contribution (i) is an engineering contribution, (ii) empirical on constructed data, (iii) corrections. The new paragraph separates architecture, mechanism, empirical findings, and future work. Novelty is not asserted beyond "structural". RQ2 asks which mechanisms are "necessary", but the results show containment at ceiling, so necessity of the safeguards for *containment* is not established — it is established only for bypass and ungrounded leakage. The body says so (§6.2).

### 4.3 Related work
Statements about [3], [9], [10], [17], [7], [14] match their abstracts as returned by search (e.g. [9]: hierarchical structure had the lowest drop, 5.5% against 10.5% and 23.7%, and an Inspector recovers up to 96.4% of errors; [10]: 15 fault types, three injection mechanisms). No full texts were read. Coverage is thin for a 20-page paper (18 references, five of them arXiv preprints, no systematic search): missing literature was not exhaustively assessed (NOT VERIFIED). The four added references (shielding, safe-RL survey, MARL survey, clustered bootstrap) exist with matching metadata at search level.

### 4.4 Architecture and methodology versus code
| # | Paper said | Code does | Type | Action |
|---|---|---|---|---|
| 1 | Evidenced proposals' confidence "0.6 to 0.8" | The score is always an evidence item; non-steady proposals have 2–3 items → 0.70/0.80 (3,814 proposals: 0.45 ×1,274, 0.70 ×312, 0.80 ×2,228) | factual | fixed |
| 2 | Renderer "adds presentation fields only" | also prepends to and truncates existing tip lists; protected keys never change | factual | fixed |
| 3 | Strategy rules (remediate etc.) | extra gates: probe budget, follow-up cap, difficulty bounds | abstraction | none |
| 4 | "Behind a feature flag" | flag is a constructor option; shipped REST backend never sets it; UI has no agent display | omission | limitation added |
| 5 | Matrix: agents "cannot … call another agent" | structural (agents get only the observation and a peer proposal); no sandbox for in-process code | scope | "Trust boundary" sentence added |
| 6 | Arbitration order, τ, bounds, probe cap, PPO as input, agents propose before PPO acts | matches (`arbitration.py`, hub order) | — | none |
| 7 | Guardrail "applied last", six guardrails, 11.8% grid disagreement | matches (test pins counts) | — | none |
| 8 | Breaker: 2 failures, 60 s cooldown, per agent per session | matches; confirmed end to end (2 failures then 12 `breaker_open`) | — | none |
| 9 | Strategy rule `stretch` is part of the agent | never fires on this replay (0 of 3,814 proposals) | coverage | reported in §6.1 and §9 |
Cannot be checked: the sigmoid-versus-logits statement (weights unavailable; test skipped).

### 4.5 Experimental design and validity
| Exp. | Unit / n | Re-check | Notes |
|---|---|---|---|
| XA | 8 answer sets × 20 orders = 160 sessions per condition, 12 conditions | counts, A1–A10 recomputed with new code | dependent sessions; session-level CIs too narrow |
| XB | 8 × 5 = 40 sessions per cell; 11 faults × 4 variants | B1–B6 recomputed | containment at ceiling; M4/no_arbitration bypass partly by construction; B6 identical across fault types (shared seeded schedule) |
| XC | 8 × 20 = 160 per τ; six τ values | C1–C5 re-derived | prospectively tagged after XA/XB seen; τ plateau explained by two-valued confidence |
| XD | 64 payloads, 3 subsets | counts read | synthetic, lexical validator only |
| XE e1/b503/e5 | 752 sessions / 1 session / 7 socket scenarios | stored files read; e1 byte identity and b503, e5 numbers match the paper | e5 is a new run, not a reproduction; I did not re-run E1 or E5 |
**Pseudoreplication.** The paper now treats the 8 answer sets as the dependence unit for the headline contrasts. I reproduced the cluster interval with exact enumeration of all 8⁸ resamples: level changes −2.669 [−4.494, −0.219] (paper, Monte Carlo B=10,000 seed 20270101: −2.67 [−4.50, −0.24]); reversals −1.875 [−3.131, −0.281]; PPO agreement −0.226 [−0.285, −0.170]; follow-ups +0.588 [0.000, +1.763]. Per-answer-set differences: level changes [−2.55, **+4.95**, −4.05, −5.95, −2.05, −2.70, −5.50, −3.50]; follow-ups [0, +4.7, 0, 0, 0, 0, 0, 0]. So the "+0.59 extra turns" appears in exactly one of eight sets (k=1), and that set also has the opposite sign for level changes — now stated. Even the cluster intervals rest on 8 clusters.
**Other validity points.** No multiplicity correction (many intervals reported, all descriptive and labelled so); replay candidate never improves; no audio so divergent guardrail regions unreachable; the Strategy Agent never proposes "Harder" on this data, so level-change reductions come from holding or lowering difficulty; metrics are behaviour measures only; the registered tags have no external timestamp.
**Conclusions versus design.** Supported: the layer works as engineered on replay; arbitration/threshold produce measurable behaviour (XC isolates the threshold). Not supported (and not claimed): need for two agents, better interviews, learning, evaluator validity, PPO improvement. The causal wording in the paper ("caused by the missing threshold") is justified for XC because only τ changes in a deterministic replay.

### 4.6 Why two agents?
The evidence shows only that two bounded agents can be integrated and that faults in one do not remove the other. Coaching ablation (A5) changes no difficulty/score/question path, so a merged component would behave identically on every fault-free metric. The paper states this (§8). **Smallest experiment that could address the gap (NOT run):** compare the two-agent system with a merged single agent (one class, one ledger, one breaker, same rules) on the XB Strategy-fault cells, with the number of accepted coaching plans per session as the outcome and clustering over the 8 answer sets; the prediction to register in advance is that the merged variant loses coaching under Strategy faults (single breaker) while two agents keep it. This would test fault isolation only, not interview quality.

## 5. Application (details in `APPLICATION_END_TO_END_AUDIT.md`)
Backend: 409 passed / 15 skipped / 23 failed / 36 errors; frozen export 306 / 14 / 23 / 36; the failing IDs are identical (59); causes are environmental (model downloads blocked, no Docker, evaluator weights unavailable). New tests 80 passed, 1 skipped. Frontend: build OK, 28/28. Real server (flag off/on, 12 injected faults, kill/restart recovery, trajectory equal to XA for the first 17–18 decisions) works; browser load/login/topic setup/interview room works. Not tested: real evaluator, microphone/STT, Docker coding sandbox, live LLM.

## 6. Figures and tables
Every figure and table was checked against the data/implementation and inspected in the final PDF. Defects found and fixed in the previous cycle (floats after references, illegible Fig. 3, crowded tables). This cycle: Fig. 2 step label. Residual: Tables 3–4 are set small to fit the page width (legible); 2 minor overfull boxes in Table 1; the PDF is US Letter (official size not checked). Equations: only the evaluator formula and confidence formula; both match the code.

## 7. Double-blind
PASS for the review PDF and sources (see checklist). Risks: the repository and git history carry identifying information; references to "an earlier audit of this system" describe the authors' unpublished work; sibling manuscripts describe the same system.

## 8. References and originality
SEARCH-LEVEL only (see checklist for which entries were re-checked in this audit). No similarity check performed. Overlap with the sibling manuscripts is the authors' decision.

## 9. Reproducibility and provenance
Verified: tables/macros regenerate identically; XA/XB/XC analysis outputs regenerate identical CSVs from raw runs (clean clone, previous cycle) and the independent recomputation agrees; a 24-session XA re-run reproduced every trajectory field (previous cycle); this audit re-derived key results from raw data and reproduced the XA trajectories through the real server. Latency and wall-time values are machine dependent.
**E5 provenance.** `xe_e5_meta.json` records commit `2d987bf` and `dirty: true`; the run began while the results directories were untracked and manuscript edits uncommitted. `2d987bf` is a paper-only commit after the tag and no experiment code changed from `380fb36` (checked with `git diff 380fb36 HEAD -- . ':!paper' ':!research/multiagent/results'`, empty at that time). The XB meta file is also `dirty: true`; XC's is `dirty: false`. The metadata was not rewritten.
**New analysis added in this audit** (post hoc, not registered): `strategy_confidence_audit.py` (re-runs M1 deterministically; its JSON records `dirty: true` because the script itself was untracked at run time).
A third party needs: Python 3.11 + the listed packages, the committed PPO checkpoint, no model weights; E5 needs ~16 minutes of real timeouts. Unavailable: the evaluator weights (LFS pointer), Qwen weights, Docker sandbox, any human data.

## 10. Skeptical-reviewer rejection risks
1. No live LLM, no human data, constructed answers, replay candidate: nothing about the system's purpose (interview preparation) is evaluated. 2. "Multi-agent" with rule-based agents on a centralised hub; contribution is structural and modest. 3. Two agents not shown necessary. 4. Strategy `stretch` never exercised; agent only holds/lowers difficulty. 5. 8 answer sets only; intervals coarse; effect on follow-ups from one set. 6. Many corrections to an earlier unpublished audit take space but are not citable. 7. Thin literature (18 refs, many preprints, search-level). 8. Mismatch with the track emphasis on decentralised intelligence (paper says it is centralised). 9. Official-format compliance unverified. 10. Reviewers may infer identity from the "earlier audit" language.

## 11. Remaining blockers and author decisions
Official CFP/deadline/template and page counting (NOT VERIFIED); full-text reference verification and a similarity check; originality/concurrent-submission decision and disclosure; author information record; whether to rename "registered" in the abstract; whether to run the merged-agent experiment; whether to anonymise/upload supplementary material; product decision on exposing the multi-agent flag; known test failures (59) need an environment with weights and Docker to be judged.

## 12. Git state at the end
See the hand-off message and `FINAL_CHANGELOG.md`. No push, no submission.
