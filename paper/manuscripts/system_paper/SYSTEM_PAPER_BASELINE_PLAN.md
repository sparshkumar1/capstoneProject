# System paper — baseline plan (PROPOSED)

## The question a reviewer will ask
Why is a learned controller needed? P3 found the PPO+guardrail policy equivalent to Constant-Same+guardrail within a self-chosen margin in simulation; the system paper cannot assume PPO adds anything for people.

## Current state of the baselines (from the audit)
| Baseline | Exists? | Notes |
|---|---|---|
| Constant-Same (non-adaptive) | Only in the P3 simulator | No runtime switch exists |
| Simple rule-based adaptation | Only as an operational fallback (`_heuristic_action`: score > 0.80 harder, < 0.40 easier, else same) | Never evaluated as a study condition; a different, legacy rule sits in `agents/audio/rl_state_vector.py` (not on the decision path as far as searched) |
| PPO + application-level guardrail | Yes (one checkpoint, `seed_123`) | Simulation-only evidence; runtime state definition differs from training |

## Plan
1. Implement Constant-Same and the rule-based policy as **selectable runtime conditions** behind the same interface, with tests, before any claim that PPO is uniquely useful. The rule should be specified and frozen before data collection (thresholds not tuned on study data). Do not compare only against a deliberately weak rule.
2. Consider whether the guardrail applies to all conditions (as in P3, where both policies ran under the same guardrail) or only to PPO; the choice changes what the comparison means and must be stated.
3. Report all conditions under equal exposure (same questions, time and feedback).
4. If an IRT/CAT or Elo-style baseline is wanted, it is new work: none exists in the repository; do not claim superiority over such methods.
5. If only two arms are feasible, choose by the RQ the authors adopt (`SYSTEM_PAPER_RQ.md`), and say in the paper which comparisons were not run.

## Not permitted
Changing the PPO checkpoint, reward, state or action definitions, or retraining, without explicit approval and a new registered experiment.
