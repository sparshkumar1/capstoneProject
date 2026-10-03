# ADCOM 2027 work directory (blind review, Springer CCIS)

**Status: draft for author review, not submitted.** Branch `adcom2027/multiagent` (base `cb888f2`). Nothing pushed, merged, submitted or registered.

| Item | Value |
|---|---|
| Blinded manuscript | `ADCOM2027_submission_blind.pdf` (12 pages incl. references and appendix; limit 20 per the supplied CFP), 0.30 MB, all fonts embedded |
| Editable source | `manuscript/main.tex`, `refs.bib`, `e5_section.tex`; `numbers.tex` and `pred_table.tex` are generated |
| Template | Springer `llncs` class v2.24 (29 Jan 2024) as packaged in TeX Live, `runningheads`, `splncs04` references. **Not verified against the current official CCIS template**: the Springer and ADCOM pages are unreachable from this environment. Compare with the official Overleaf/Word template before submission. |
| Blind review | per the supplied CFP. No author, affiliation, acknowledgement, URL, system name or repository name in text, figures, PDF metadata or file names (checked by string scan of the PDF text and binary). No self-citations. |
| Verification | `verification/verify_adcom.py`: 71 checks, 71 pass (independent recount of every number from the raw result files, citation/label/macro consistency, identifier scan). |
| Tests | full suite on the branch: 23 failed, 329 passed, 36 errors; identical failing set to the `cb888f2` snapshot (23 failed, 306 passed, 36 errors; Docker, faiss and model downloads unavailable). Logs in `logs/`. |

## Directory
`GO_NO_GO_ADCOM_FIT.md` fit decision; `architecture/ARCHITECTURE_INVENTORY.md` what is multi-agent; `protocol/` registered protocol with amendments A1–A3; `experiments/` harness, E1–E5 scripts, analysis; `results/` raw and processed results, `RUN_LEDGER.md` (hashes, dated ledger incl. failures); `figures/` scripts and figures; `literature/` matrix and verification status; `verification/`; `CONTRIBUTION_AND_NOVELTY_STATEMENT.md`; `REPRODUCIBILITY_STATEMENT.md`; `FINAL_AUDIT_REPORT.md` (unresolved issues, decisions needed).

## Rebuild
`PY=<python with numpy scipy matplotlib torch stable-baselines3 fastapi httpx> ./build.sh` (regenerates figures, numbers, tables, PDF, runs the verification). Experiments are re-run with `python experiments/e1_ablation_faults.py` etc. (write-once outputs: move the old `results/e*.json*` away first). E2/E5 take about 8 and 20 minutes (real timeouts) and need port 8001 free.

## Code changes on this branch (outside `paper/adcom2027/`)
`agents/orchestrator/interview_orchestrator.py` (strict evaluator contract, breaker hooks), `agents/orchestrator/feedback_agent.py` (breaker hooks), new `agents/orchestrator/circuit_breaker.py`, new tests `tests/unit/test_evaluator_contract.py`, `tests/unit/test_circuit_breaker.py`, one existing test updated (`test_orchestrator_handles_none_evaluation_score`, deliberate behaviour change). Both changes can be switched off by config/attribute, reproducing the previous behaviour in the same code. No frozen path (`research/`, `rl/`, `ablation/`, `experiments/`, `services/`, `apps/`) was touched.
