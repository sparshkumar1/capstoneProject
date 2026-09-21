# Paper 3 - research question and permitted contribution statements (LOCKED 2026-09-21; replaces the earlier list)
Type: controlled policy decomposition / equivalence evaluation, simulation only. Evidence: research/evidence/final/PAPER3_FINAL_CLAIM_MATRIX.md (P3-M1..M6, P3-F1..F5) and the frozen X3-A / O7 artifacts it cites. The frozen result is not modified by this document.

## Locked research question
"Under an identical rule-based guardrail layer, what does a learned PPO difficulty controller add beyond a simpler state-blind Constant-Same policy in simulated technical-interview trajectories?"

## Locked primary result and interpretation
PPO+guardrail versus Constant-Same+same guardrails [P3-M1]: Delta MAE = -0.0350, 95% CI [-0.0818, +0.0021], preregistered equivalence margin +/-0.12 MAE (two-way cluster bootstrap over 40 personas x 5 training seeds, B=10,000; the persona is the statistical unit).
Interpretation (use this wording): "Under the registered simulator and shared guardrail layer, the learned PPO controller was statistically equivalent in tracking error to the state-blind Constant-Same comparator under the preregistered +/-0.12 MAE margin."
Secondary result [P3-M3]: the learned policy exhibited higher trajectory volatility than the matched Constant-Same comparator (+0.14877 [0.0666, 0.25445]).

## Permitted contribution statements
1. A controlled decomposition: a persona-level, multi-seed simulation comparison in which the learned policy and a state-blind constant action run under the same application-level rule-based guardrail layer, so the learned policy's contribution can be separated from the guardrails'.
2. A preregistered equivalence evaluation of that comparison (registered +/-0.12 margin; superiority margin -0.20 not met), with registered secondary sensitivity analyses that leave the classification unchanged [P3-M2].
3. Descriptive intervention accounting (guardrail activations 563/1250 turns versus action overrides 99/1250) and volatility reported next to the tracking result [P3-F3, P3-M3].
4. An explicit list of what the simulator cannot support.

## Terminology (locked)
Always "application-level rule-based guardrail". Never "formal shield", "safe-RL shield", "formally verified shield" or "safety guarantee". The layer has no formal safety specification (research/literature/claude_web_research/P3_FINAL_NOVELTY_POSITION.md section 4).

## Literature position (locked)
Kadam et al. (2026, Simulation Modelling Practice and Theory 151, 103316) already establishes adaptive mock-interview tutoring with simulation, an IRT-based learner model, a finite-horizon MDP, a rule-based heuristic, DQN, PPO, PETS and MBPO (verified parts only; its body is unread, see KADAM_VERIFICATION.md). The contribution is therefore the controlled decomposition/equivalence question, not the broad application of PPO. This paper does not compare against Kadam's simulator or policies.

## Not claimed
That PPO for adaptive interviews is novel; that RL for mock interviews is novel; a new adaptive-interview simulator; a new RL interview benchmark; PPO superiority; guardrail novelty; real-learner benefit; real-interview deployment benefit; "no effect" (equivalence is not "no effect").

## Mandatory limitations that travel with these contributions
See FINAL_LIMITATIONS.md (locked list).

Cross-paper ownership (locked): Paper 1 owns containment, authority boundary, tested failure handling and operational behaviour; Paper 2 owns evaluator agreement, evaluator diagnostics, error patterns and robustness; Paper 3 owns learned-policy versus simpler-policy behaviour under shared guardrails. One paper's contribution is not reused as another paper's novelty.
