> **Note (2026-10-02):** this report is from the previous review cycle. The later independent audit (`FINAL_INDEPENDENT_AUDIT.md`, `FINAL_CLAIM_VERIFICATION.md`, `APPLICATION_END_TO_END_AUDIT.md`, `FINAL_SUBMISSION_CHECKLIST.md`, `FINAL_CHANGELOG.md`) corrected several statements made in the paper and supersedes this report where they differ (confidence values, coaching-renderer wording, deployment surface, page-inspection scope).

# Final audit report — PREPAIred multi-agent extension and ADCOM 2027 manuscript

Review date: 2026-10-02. Branch `research/adcom2027-multiagent-final` (local; nothing pushed or submitted). The HEAD commit is stated in the hand-off message; `git log --oneline 9d37a06..HEAD` lists the commits of this review cycle.
Classification: **PASS / FAIL / PARTIAL / NOT VERIFIED**. Evidence classes: REPLAY, FAULT-INJECTED, SOCKET, SYNTHETIC. There is no LIVE-LLM and no HUMAN evidence anywhere in this package.

## 0. Candid status
**Ready for author review. Not yet a confirmed submission candidate.** The system, experiments and manuscript are internally consistent and reproducible from the repository, but the authors must still verify the official ADCOM call and the current Springer CCIS template (both unreachable here), check the references against full texts, decide the overlap and concurrent-submission position, and accept that the paper contains no live-LLM or human evidence. The Python test suite is not green. No statement about acceptance is made.

## 1. Baseline state (before any edit)
| Check | Result |
|---|---|
| Branch / HEAD | `research/adcom2027-multiagent-final` at `9d37a06`; working tree clean (`git status --short` empty) — PASS |
| Frozen refs | `origin/freeze/engineering-baseline-407tests` = `54a5b739…`; `origin/audit/claude-research-baseline` = `cb888f28…` (checked with `git ls-remote`); both unchanged — PASS. `git diff --name-status 54a5b73 HEAD` over the CLAUDE.md frozen set (`research/audit`, `research/papers`, `research/results/paper3`, `research/CLAUDE_HANDOFF`, `rl/checkpoints`, `ablation/results`, canonical truth file) is empty — PASS |
| Local tags | `prereg/ADCOM-E1-E3/v1`, `prereg/ADCOM-E4/v1`, `prereg/ADCOM-E5/v1`, `prereg/MA-XA-XB/v1`; `prereg/MA-XC/v1` added in this cycle. None pushed — local tags carry no external timestamp (disclosed in the paper). |
| Code changed since the MA-XA-XB tag | `git diff --name-status 380fb36 HEAD -- . ':!paper' ':!research/multiagent/results'` was empty at the start: no agent, hub or experiment code changed after the registered runs — PASS |
| Baseline PDF | 18 pages — but visual inspection showed Tables 2–8 collected after the references (see §6) — FAIL (fixed) |

## 2. Implementation audit (Phase 2)
Files read: `agents/multiagent/{contracts,authority,arbitration,coordinator,grounding,strategy_agent,coaching_agent,coaching_render,runtime}.py`, the hub hooks, `circuit_breaker.py`, and the tests.
| Item | Result |
|---|---|
| Hub is sole writer; agents only propose | PASS. Authority matrix is code (`FORBIDDEN_KEYS`, 18 keys); `state_writes` empty for both agents; forbidden keys scanned at any depth; proposals must carry the observed state version. |
| Typed communication | PASS. Frozen pydantic models, `extra=forbid`, NaN/out-of-range rejected; every message and decision recorded with provenance and a reason code. |
| Arbitration semantics | PASS. Hard constraints → guardrails last → validated Strategy proposal (confidence ≥ τ, evidence) → PPO/labelled heuristic. PPO keeps its documented role as an input. |
| Per-agent fault handling | PASS. Timeout, crash, authority, schema, stale and duplicate each have a distinct reason code; per-agent per-session breakers; cancellation is not counted as an agent failure. A timed-out worker thread cannot be killed (documented; the breaker bounds the repeat cost). |
| State snapshot/restore, concurrency | PASS (integration tests: round-trip keeps ledgers; concurrent sessions are isolated). |
| Flag off | PASS. `test_flag_off_is_inert`; with the flag on and no agent contributing, trajectories are identical for k = 0, 3, 6 (and XA A4: 160/160). |
| "Multi-agent" claim | PARTIAL by design. By the weak notion of agency (private state, reactivity, pro-activeness, communication) the agents qualify; they are rule/ledger-based, not LLM agents, the system is centralised, and PPO is not MARL. The paper says this in the abstract, introduction, discussion and related work. |
| Dead/duplicated code | One known duplication: the deployed inline guardrail layer differs from `rl/guardrails.py`; kept for compatibility, selectable by `guardrail_impl`, tests pin the 11.8% grid disagreement. |
| Security boundary | PARTIAL. Well-formed, confident, evidenced but wrong proposals pass every check; they are bounded only by guardrails and the one-step limit (measured: the adversarial proposal was the final source of 10.8 decisions per session). Disclosed as a limitation. |
| Tests exercise real paths | PASS for integration tests (real `InterviewOrchestrator`, recorded evaluator payloads, frozen PPO); unit tests use direct objects. The evaluator and LLM are stubbed in all of them. |
No implementation change was made in this cycle: no defect was found that warranted one.

## 3. Experiment and result audit (Phase 3)
Independent recomputation: `research/multiagent/analysis/independent_check.py` (new code that does not import the analysis scripts) over `results/xa/xa_runs.jsonl` and `results/xb/xb_runs.jsonl`: **all checks PASS** (design counts, A1–A8, B1–B4 reproduced; A9 and A10 contradicted exactly as reported).
| Experiment | Design verified | Result |
|---|---|---|
| XA (REPLAY) | 12 conditions × 160 sessions (8 recorded answer sets × 20 orders) = 1,920 | PASS. Outputs regenerate byte-identically (modulo line endings) from the raw runs in a clean clone. |
| XB (FAULT-INJECTED) | 11 fault types × 4 variants × 40 sessions = 1,760 | PASS. Same. |
| XC (REPLAY, new) | 6 τ values × 160 sessions = 960; protocol and tag committed before the run; metadata `dirty: false` at commit `01186fb` | PASS. All 5 registered predictions and the validity check supported. |
| XD (SYNTHETIC) | 64 payloads, 3 subsets | PASS (counts re-checked by the claim audit). |
| XE e1 | 752 sessions byte-identical to the stored historical file | PASS |
| XE b503, e5 (SOCKET) | one replay session; seven E5 scenarios | PASS as new runs, not reproductions; single run on one machine. |
| Clean-checkout re-run | `xa_compare.py --seeds 1 --only B0,M1,M4` from a clean clone: 24 sessions, 0 mismatches in difficulty/score/question paths, level changes, reversals, bypass, strategy source, follow-ups | PASS |

**Dependence of sessions (finding).** The 160 sessions per condition are 8 recorded answer sets × 20 question orders; the registered session-level bootstrap treats them as independent and gives intervals that are too narrow. A post hoc cluster bootstrap over the 8 answer sets (B = 10,000, seed 20270101) gives: level changes −2.67 [−4.50, −0.24], reversals −1.88 [−3.12, −0.27], PPO agreement −0.226 [−0.284, −0.170] (all 8 clusters share the sign), and extra turns +0.59 [0.00, +1.76], where only 1 of 8 answer sets shows an increase — the extra-turn effect comes from one recorded session. The paper now reports these next to the registered intervals, labelled post hoc. No multiplicity correction is applied or claimed; intervals are descriptive.

**Ablation isolation (finding).** XA's M4 "no arbitration" removes four things at once (confidence threshold, evidence requirement, one-step bound, guardrail layer), so the paper's earlier attribution of the collapse to the threshold was not isolated, and the "bypass" metric is partly by construction in that condition. XC (registered before it ran) changes only τ: τ = 0 reproduces M4's level changes (2.225) and PPO agreement (0.014) with no guardrail bypass, so the collapse is due to the missing threshold. Behaviour is flat for τ in 0.5–0.8 and the Strategy Agent is silent at τ = 0.9 (confidence is min(0.95, 0.5 + 0.1n), so evidenced proposals sit at 0.6–0.8 or above). The paper states what this does and does not show.

**Contradicted predictions (A9, A10, B6), explained.**
- A9 (PPO unavailable ⇒ ≥ 50% of paths differ): observed 4/160. On replay the Strategy Agent mostly agrees with the labelled non-RL heuristic.
- A10 (canonical guardrails change ≥ 1 path): observed 0/160. Replay has no audio, so confidence and hesitation stay at defaults and the divergent guardrail regions are never reached.
- B6 (breaker opens in ≥ 80% of sessions at fault rate 0.3): observed 72.5% (29/40). It is identical in all seven fault types because all share one seeded fault schedule per (k, seed) (`FaultyAgent(seed=31k+seed)`); the paper now says so.
- Ceiling effects: completion, authority and transition validity are at 100% everywhere (they are enforced by the hub), so they do not discriminate safeguards; bypass and ungrounded leakage do.
- Unfavourable results (A9, A10, B6, the null on containment, the one-session extra-turn effect) all remain in the paper.

**E5 and the "dirty" metadata (explained).** `results/xe_e5/xe_e5_meta.json` records commit `2d987bf` and `dirty: true`. The run was launched while the results directories were still untracked and while paper edits were uncommitted, so `git status --porcelain` was non-empty. `2d987bf` is a paper-only commit after the protocol tag; `git diff 380fb36 HEAD` over code (excluding `paper/` and results) was empty then, so the experiment code was identical to the tagged protocol. The XB meta file has `dirty: true` for the same reason (XA results were untracked); XA's meta is `dirty: false`. The E5 meta file also lacks a config hash because that script does not record one. The metadata was not rewritten; this explanation and the exact command are the record.

## 4. Contribution (Phase 4)
Distinguished in the paper: architecture (agents, contracts, authority matrix), mechanism (arbitration, confidence threshold, guardrails last), empirical findings (replay and fault injection on constructed data), future work (live LLM, human candidates).
- Why two agents: **not shown**. Removing the Coaching Agent changes no difficulty, score or question path (A5), so a merged component would have behaved identically on these metrics. The split is an authority/state boundary (separate ledgers, outputs and breakers). The paper says this and that a single-rules-engine baseline was not tested.
- No comparative baseline against an external multi-agent framework or interview system was built: nothing fair could be implemented within the time. No superiority claim is made.

## 5. References and originality (Phase 6)
| Item | Status |
|---|---|
| 18 references (14 existing + 4 added: shielding, safe-RL survey, MARL survey, clustered bootstrap) | PARTIAL. Titles, authors, venues, years and (where shown) DOIs checked through a web-search interface; the four additions were confirmed against search-result metadata. No full text read; no Crossref/publisher check (blocked); several are arXiv preprints. The paper says so. |
| Each citation supports its sentence | PARTIAL (checked against titles/abstracts only). |
| Missing literature | Not exhaustively assessed; no systematic search was possible. |
| Overlap with sibling manuscripts | `OVERLAP_AUDIT.md` (comparison with ICITIIT 2027 and INDIACom 2027 sources and ICETC/earlier ADCOM summaries): distinct experiments and questions; shared system description and reuse of the 64 recorded payloads as replay input. NOT VERIFIED: each venue's concurrent-submission policy and the authors' actual submission status. Authors must decide and disclose. |

## 6. Format and double-blind (Phase 7)
| Item | Status |
|---|---|
| Official ADCOM CFP, dates, template, page counting | NOT VERIFIED. Official pages (accsindia.org, springer.com, CMT, Crossref) are blocked by network policy (HTTP 403 from the egress proxy; not circumvented). A web search confirmed only the conference name, number and dates. Dates and limits come from the brief. |
| Build | `llncs` + `runningheads` + `splncs04` (bundled); built with `latexmk -pdf`; 19 pages (≤ 20); 0 undefined references; 2 small overfull boxes (≈ 20 pt) in Table 1 — PARTIAL |
| Layout defects found by visual inspection and fixed | All tables had been dumped after the references (float queue blocked by a tall table); Fig. 3 text was illegible (scaled to ~0.7); XA tables had crowded columns; Table 1/2 had wide justified gaps; one caption overlapped a table. Fixed; pages 1–17 and 19 were inspected as images after the final layout fixes (page 18, the first references page, only in an earlier build). |
| Blind audit | PASS: `scripts/blind_audit.py` 0 hits (sources, bib, PDF text, metadata, fonts embedded). Independent grep for names, e-mail, product name, paths, URLs found only DOIs in references. Residual risk: reviewers who know the authors' sibling manuscripts may infer identity from the shared setting. |
| Track fit | The paper argues agent-native lifecycle/engineering and trust/containment; not verified against the official track text. |

## 7. Tests (Phase 8)
Commands (clean export of `54a5b73` via `git archive`, and HEAD; `EVALUATOR_MOCK_MODE=1`, scratch Python 3.11 venv outside the repository pins):
```
python -m pytest tests/unit tests/integration -q -p no:cacheprovider -rfEs
```
| Tree | Result |
|---|---|
| Frozen `54a5b73` (clean export) | 306 passed, 14 skipped, 23 failed, 36 errors |
| HEAD | 409 passed, 15 skipped, 23 failed, 36 errors |
- Failing/erroring identifiers: 59 in each tree; `comm` of the sorted lists shows **no identifier only at HEAD** — no regression (PASS). An earlier recorded baseline of "329 passed" came from a different tree (the working directory at that time); the 23-test difference to the clean export was not investigated, and the identifier comparison above is the authoritative one.
- Causes observed: Docker sandbox unavailable, model downloads blocked, Git-LFS pointer weights, one documented known failure. The suite is **not green** (FAIL); the failures are environmental or pre-existing, not shown to be product defects here.
- New tests: 80 passed, 1 skipped (needs materialised cross-encoder weights) across `test_ma_contracts_arbitration`, `test_ma_agents`, `test_guardrail_impl`, `test_evaluator_semantics_and_seam`, `test_circuit_breaker_semantics`, `tests/integration/test_ma_workflow.py` — PASS.
- Frontend: `cd apps/web && npx vitest run` → 4 files, 28/28 passed — PASS.
- Multi-agent enabled and disabled paths both exercised — PASS. Live end-to-end with Docker/LLM — NOT VERIFIED (unavailable).

## 8. Reproduction
```
export EVALUATOR_MOCK_MODE=1
python research/multiagent/experiments/xa_compare.py   --out research/multiagent/results/xa
python research/multiagent/experiments/xb_faults.py    --out research/multiagent/results/xb
python research/multiagent/experiments/xc_threshold.py --out research/multiagent/results/xc
python research/multiagent/experiments/xd_grounding.py --out research/multiagent/results/xd
python research/multiagent/experiments/xe_historical.py --part e1|b503|e5 --out research/multiagent/results/xe_<part>
python research/multiagent/analysis/analyze_xa.py research/multiagent/results/xa
python research/multiagent/analysis/analyze_xb.py research/multiagent/results/xb research/multiagent/results/xa
python research/multiagent/analysis/analyze_xc.py research/multiagent/results/xc research/multiagent/results/xa
python research/multiagent/analysis/independent_check.py research/multiagent/results   # add a JSON path to write the post hoc file
python paper/adcom2027_final/scripts/make_authority_table.py && python paper/adcom2027_final/scripts/make_tables.py
(cd paper/adcom2027_final/manuscript && latexmk -pdf main.tex)
python paper/adcom2027_final/verification/verify_paper.py   # 59/59
python paper/adcom2027_final/scripts/blind_audit.py          # 0 hits
```
Result files are write-once: delete a target directory (never in the committed history) to re-run. Latency values depend on the machine and are not expected to match. Required: Python 3.11, numpy, scipy, pandas, torch, stable-baselines3, gymnasium, pydantic ≥ 2, pytest, pytest-asyncio, TeX Live with `latexmk`, `pdftotext`/`pdfinfo`; no model weights beyond the committed PPO checkpoint. The Qwen GGUF and evaluator LFS weights are not needed.

## 9. Remaining blockers and author decisions
1. Verify the official ADCOM CFP, deadline, page counting and the current Springer CCIS template (NOT VERIFIED).
2. Verify every reference against full texts/publisher pages and check each citation supports its sentence (PARTIAL).
3. Decide the sibling-manuscript overlap and concurrent-submission position; supply author information outside the blinded PDF (NOT VERIFIED).
4. Live-LLM and human evidence do not exist; the paper makes no claim that needs them. Any claim about coaching quality, learning, evaluator validity or PPO improvement needs new studies.
5. Python suite is not green here (environmental/pre-existing failures).
6. Registered local tags have no external timestamp; consider an external registry deposit.
7. XC was designed after seeing XA/XB (disclosed); with 8 recorded answer sets, even cluster intervals are coarse.

Companion files: `CLAIM_EVIDENCE_MAP.md`, `CHANGELOG_FINAL_REVIEW.md`, `SUBMISSION_CHECKLIST.md`, `OVERLAP_AUDIT.md`, `README.md`.

---
## Addendum 2026-10-02 (end-to-end audit cycle; history above preserved)
Superseding details are in `APPLICATION_END_TO_END_AUDIT.md` (addenda 1 and 2), `FINAL_CHANGELOG.md` and `FINAL_INDEPENDENT_AUDIT.md`. Summary: the multi-agent layer is now reachable in the shipped backend through the server-side `PREPAIRED_MULTIAGENT` variable (default off; commit 3dbb4ed); both end-to-end sessions (flag off/on) completed with 40 feedback events each (0 vs 40 coaching plans) using a recorded-evaluator substitute; fresh regression: frozen 306/14/23/36, HEAD 421/15/23/36 with the identical 59 failing IDs; frontend 28/28 and build OK; post hoc leave-one-cluster-out analysis added (k=1 is influential; the level-change interval excludes zero only with all eight sets or without k=1); paper 19 pages, claim audit 69/69, blind audit clean. Still open: official CFP/template, full-text reference checks and similarity check, real evaluator/live LLM/human evidence, two-agent necessity, author decisions listed in `FINAL_SUBMISSION_CHECKLIST.md`.
