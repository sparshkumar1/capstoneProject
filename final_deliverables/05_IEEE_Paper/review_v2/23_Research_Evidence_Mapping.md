# 23. Research Evidence Mapping — Revised IEEE Paper (Specialised Agentic Architecture)

Maps every substantive claim in `PrepAIred_IEEE_Paper_SpecialisedArchitecture_v2` to its evidence category:
**Implementation** (verified by reading the code), **Completed experiment** (a result that was actually run and
recorded), **Historical testing** (an earlier, already-frozen result reused here), **Architectural
interpretation** (a reasoned claim about what the architecture's structure enables, not itself a measured
performance number), or **Future work** (explicitly not yet done).

| Claim (paper location) | Category | Evidence source |
|---|---|---|
| Nine specialised components exist, each with a distinct responsibility (Abstract, §I, §III-A) | Implementation | Direct read of `agents/orchestrator/interview_orchestrator.py`, `agents/strategy/hybrid_orchestrator.py`, `rl/guardrails.py`, `services/evaluator/app.py`, `services/qwen/app.py`, `agents/coding_executor/coding_executor.py`, `agents/audio/*`, `agents/validation/score_validator.py`, `agents/timing/timer.py` (see `17_Architecture_Audit_Report.md`) |
| No component imports or calls another component as a peer; orchestrator-mediated only, one exception (§III-A) | Implementation | Repository-wide grep for cross-agent imports, `17_Architecture_Audit_Report.md` §4.1 |
| Component classification table, categories A–D (§III-B, Table I) | Implementation | `17_Architecture_Audit_Report.md` §3 classification matrix, re-derived from the same source reads |
| Decomposition enabled a substitution test isolating PPO's contribution from the guardrail's (§III-C) | Architectural interpretation, supported by a completed experiment | The interpretation is reasoned from the architecture; the substitution test itself is the completed RL baseline/confirmatory comparison below |
| Evaluator formula: score = 0.15·S1 + 0.35·S2,eff + 0.50·R (§IV-A) | Implementation | Direct read of `services/evaluator/app.py` (weights confirmed at source, matches `CLAUDE.md`) |
| RL state/action space, guardrail priority order (§IV-B) | Implementation | `agents/strategy/hybrid_orchestrator.py`, `rl/guardrails.py` |
| Live orchestrator's guardrail copy diverges from the canonical training/evaluation module on one boundary (§IV-B) | Implementation | `17_Architecture_Audit_Report.md` §3.3/§7.2 — direct comparison of `interview_orchestrator.py:1529-1573` vs. `rl/guardrails.py:47-121` |
| Qwen never computes or adjusts the numeric score (§IV-C, §V-B) | Implementation | `services/qwen/app.py:418,462,525,624,718,828`; `agents/orchestrator/feedback_agent.py:98,170-198` — independently re-verified in this engagement (see `20_Architecture_and_Baseline_Comparison_Specification.md` §1.3) |
| Evaluator-human correlation, rho = 0.3812, 3 raters, 64 answers (§V-A) | Historical testing (frozen) | `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §C.1/§C.2; `research/data/evaluator_benchmark/final_human_gold.csv` |
| Component-ablation correlations (cross-encoder only, S1+R, S1 only, word-count baseline) (§V-A, Table II) | Historical testing (frozen) | Same source as above |
| Difficulty-tracking MAE by condition: Fixed 1.200, Heuristic 0.473, PPO raw 0.804, PPO+guardrails 0.677 (§V-C, Table III) | Historical testing (frozen) | `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §D.2, citing `paper3_baseline_results.csv`/`paper3_seed_results.csv`/`paper3_summary_results.csv` |
| Pre-registered confirmatory equivalence test (PPO+guardrails vs. constant-"Same"+guardrails, 95% CI crosses zero) (§V-C, Fig. 3) | Completed experiment (frozen) | `research/confirmatory/X3-A/` and associated frozen results, as reused/cited in the original `Final_IEEE_Paper_Source.tex` §VII-B |
| Guardrail boundary gap in [0.30, 0.40) found and fixed; 13/13 boundary cases, zero regressions (§V-D) | Completed experiment (frozen) | `testing_and_evaluation/rl_evaluation/T-N03_guardrail_verification.py`, `testing_and_evaluation/Baseline_Record.md`, `rl/guardrails.py` module docstring (2026-11-12 fix) |
| 264/283 tests pass; 19 remaining trace to one external dependency or one pre-existing issue (§V-E, Table IV) | Historical/completed testing (frozen) | `testing_and_evaluation/final_evaluation/` test records; also independently re-verified for the Docker-dependent subset in `16_Docker_Verification_Report.md` (19/19 passing with a live daemon) |
| PPO checkpoint identity: deployed vs. evaluated checkpoints are distinct artifacts (§V-E, Table IV) | Completed experiment | `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` line 79 (hash comparison) |
| Architectural comparison (specialised vs. unified single-controller) is designed but not executed (§III-F, §VI) | Future work, explicitly disclosed as not done | `19_Revised_Experimental_Proposal.md`, `20_Architecture_and_Baseline_Comparison_Specification.md`, `21_Experimental_Results_Framework.md` (all results marked "Pending") |
| "Decomposition made the attribution finding possible to obtain" (§VI Discussion) | Architectural interpretation | Reasoned claim connecting §III-C's structural property to §V-C's completed experiment; not itself a separately measured number |
| "No claim PrepAIred is a multi-agent system of communicating peers" (§I, §VI) | Implementation (negative finding) | Same dependency-audit evidence as row 2 above |

## Claims this paper explicitly does NOT make (for review completeness)

- No real-candidate learning-outcome claim (all RL training/evaluation is simulation-based).
- No claim the evaluator is validated at publication-grade confidence (explicitly exploratory, small N).
- No claim that specialisation has been experimentally shown to outperform a unified controller.
- No claim of peer-to-peer multi-agent collaboration.
- No new reference, DOI, or bibliographic detail was introduced relative to the original paper's verified reference list (`IEEE_References_Verification.md`); all 15 entries are reused unaltered.
