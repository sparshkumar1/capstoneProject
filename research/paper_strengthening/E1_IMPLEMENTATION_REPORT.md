# E1 Implementation Report — Protocol V4, Scripts and Tests

**Status: implementation complete for the code and tests described below. No training executed, no confirmatory evaluation run, no PPO checkpoint loaded, no D1, no reward/state/action/scoring change, no tags/commit/push.** Everything here supports the later, separately-approved development run; nothing in this pass is a result.

## 1. New files created and their SHA-256

| File | SHA-256 |
|---|---|
| `research/paper_strengthening/scripts/e1_config.json` | `75dda898ecd03bb95bf68a0610408c2a479a66e1275daf011c740b17a1727553` |
| `research/paper_strengthening/scripts/e1_diverse_persona_env.py` | `3fda0e840808dfb7fa03333d04c83fefb4a27732a831933e4b51de12bb1db7ad` |
| `research/paper_strengthening/scripts/e1_simulate_adapter.py` | `0b038b4252da7c090ca6e5190f467b241422b827e45291833a363d06596a96f1` |
| `research/paper_strengthening/scripts/e1_train_condition_b.py` | `daf094c46a1c670f149363c18af322de9efc59a4a984d45bc7f2abd54c9c53ab` |
| `research/paper_strengthening/scripts/tests/test_e1_diverse_persona.py` | `ce6d956c804f41b1a1ee47cb841442516dc3acbda19880e2573ce7652d32a213` |

`e1_config.json` holds every hyperparameter, seed list, grid, and output path referenced by the code — no hyperparameter is hard-coded separately from it, per the reproducibility requirement.

## 2. What each file does (mapped to V4's implementation plan, §5/§7)

- **`e1_diverse_persona_env.py`** — `DiverseCandidate` (the confidence/hesitation decoupling wrapper, composing an unmodified `SimulatedCandidate` rather than subclassing it), the B0/B2 grid definitions, `episode_seed()`, `grid_cell_for_episode()`, `make_candidate()`, and the three held-out profiles with `x3a_target_difficulty()`.
- **`e1_simulate_adapter.py`** — `simulate_diverse()`, the new adapter V4 identified as necessary because `x3a_lib.py::simulate()` hardcodes candidate construction. Reuses `x3a_lib.shield()`, `x3a_lib.make_policy()`, `x3a_lib.ACTION_NAMES`/`DELTA`, and `InterviewEnv.oracle_action_from_obs` unmodified; reimplements only the loop shape.
- **`e1_train_condition_b.py`** — `build_env_class()` (a new `_DiversePersonaAlignedEnv` subclassing the frozen `AlignedInterviewEnv`, overriding only `reset()`'s candidate construction, per V4 §1.2) and `train_condition_b_seed()` (the training driver, reading all hyperparameters from `e1_config.json`). **Not called anywhere in this pass** — defined and tested via reset()/step() only.
- **`tests/test_e1_diverse_persona.py`** — 52 tests, detailed below.

## 3. Tests performed and exact results

**52/52 passed**, `.venv/Scripts/python.exe -m pytest research/paper_strengthening/scripts/tests/test_e1_diverse_persona.py -v`, 5.5s wall time, zero PPO training, zero checkpoint loads.

| Requirement (from your instruction) | Test(s) | Result |
|---|---|---|
| Exact identity of the wrapper at k=0 | `test_wrapper_k0_is_exact_identity` (3 cases), `test_wrapper_k0_returns_inner_dict_unmodified_object` | PASS — bit-exact match to an unwrapped `SimulatedCandidate`; k=0 literally returns the inner dict, not a rebuilt copy |
| Correct, bounded confidence/hesitation transform for k>0 | `test_transform_matches_formula_and_stays_bounded` (15 cases: 3 skills × 5 k values incl. k=1.0 boundary) | PASS — exact formula match, values stay in [0,1] at every tested point |
| Rejects out-of-range k | `test_k_out_of_range_rejected` | PASS |
| Unchanged performance and response_time | `test_perf_and_response_time_unchanged` (3 k values) | PASS — identical to the unwrapped candidate for every k |
| Deterministic episode-seed and grid cycling | `test_episode_seed_formula_exact`, `test_grid_cycling_deterministic_and_wraps`, `test_grid_cycling_unknown_arm_raises` | PASS — formula exact; both arms' 24-cell cycle confirmed to repeat identically on a second pass and wrap correctly at index 24 |
| Matching base candidate seeds and skill exposure, B0 vs B2 | `test_b0_b2_identical_skill_sequence_and_seed_at_every_episode` (3 training seeds × 48 episodes), `test_b0_skill_exposure_matches_b2_exactly`, `test_b0_k_always_zero_across_full_cycle`, `test_b2_k_grid_exposure_matches_declared_grid` | PASS — identical seed and skill at every corresponding episode; each of the 6 skill values appears exactly 4× per 24-cell cycle in both arms; each of B2's 4 k-values appears exactly 6× |
| Correct environment reset and termination | `test_env_reset_assigns_correct_candidate_and_terminates`, `test_env_b0_never_exposes_nonzero_k` | PASS — `reset()` assigns the exact predicted (skill, k, seed) each episode, episode counter increments correctly, episodes terminate at exactly `max_steps` |
| Correct metric calculations and action handling | `test_adapter_parity_with_x3a_lib_simulate_ordinary_candidates` (16 cases: 4 policies × 4 persona/seed/target/shield configs), `test_adapter_diverse_candidate_k0_matches_ordinary_candidate`, `test_adapter_diverse_candidate_k_positive_changes_something_or_stays_valid` | PASS — see §4 |
| Held-out profile correctness | `test_holdout_profile_targets_match_x3a_formula`, `test_holdout_profile_skills_do_not_collide_with_any_existing_grid` | PASS — targets 1.5/3.0/4.0 exactly match `x3a_lib.py`'s own formula; no skill collides with `PERSONA_TARGETS`, `X3-A`'s grid, or B0/B2's grid |

## 4. Adapter parity — exact result, no discrepancies found

The required check ("verify the new adapter reproduces `X3-A` simulation behavior... investigate and resolve any differences before treating the adapter as valid") was run across **16 combinations**: policies `const_same`, `heuristic`, `oracle`, `random` (all deterministic-given-seed, none requiring a PPO checkpoint) × personas `normal@0.60`, `struggling_junior@0.20`, `lucky_guesser@0.80` × varying eval seeds, targets, and shield on/off.

**Result: exact equality on every field** (`final_difficulty`, `target_tracking_error`, `volatility`, `oscillation_rate`, `guardrail_interventions`, `constraint_violations`, `raw_actions`, `final_actions`, `guardrail_ids`, `overrides`, `oracle_agreement`, and every per-step observation array) between `x3a_lib.simulate()` and the new `simulate_diverse()` when both are given an ordinary (unwrapped) candidate. **No discrepancy was found; none required investigation or resolution.** A separate check confirms a `DiverseCandidate` with `k=0` run through the adapter also matches `x3a_lib.simulate()`'s "normal" persona exactly, as required by the k=0-identity guarantee.

**What was not tested, and why:** parity with the `ppo` policy kind (`x3a_lib.make_policy("ppo", ...)`), since that requires loading a frozen `.zip` checkpoint via `PPO.load()` — explicitly out of scope for this pass ("do not launch training... run only the permitted unit and static checks"). This is deferred to the approved development run, where it should be checked once, before trusting any PPO-based confirmatory number, exactly as the protocol's own pre-execution integrity checks already require for other components.

## 5. A defect found and fixed during testing (disclosed, not hidden)

The first version of `test_env_reset_assigns_correct_candidate_and_terminates` instantiated the new environment without an explicit `log_file`, so it fell back to `InterviewEnv`'s default log path — the same untracked, gitignored file documented in `PPO_TRAINING_EXPERIENCE_AUDIT.md` (`rl/env/training_logs/interview_data.csv`, 295,291 rows). Running the tests appended **91 rows** to that file. This was caught by checking the file's row count before and after testing (a habit carried over directly from this session's own audit of that exact file), **the 91 appended rows were removed and the file restored to its exact prior 295,291-row state** (verified byte-for-byte via `diff` against a truncated copy), and both affected tests were fixed to pass an isolated `tmp_path`-based log file. Re-running the full suite afterward confirms the file's row count is unchanged. This file is not tracked by git and is not a "frozen" artifact under CLAUDE.md's definition, but it was the subject of a documented investigation earlier in this session, so altering its row count — even accidentally, even in an untracked file — was treated as a real defect and corrected rather than left as a footnote.

## 6. Confirmation: all frozen/existing files unchanged

Checked directly, after implementation and after the fix in §5:
- `git status --porcelain` on `rl/`, `research/experiments/`, `research/analysis/`, `research/confirmatory/`, `research/preregistration/`, and `research/scripts/`: **empty — no changes anywhere in any of these trees.**
- `rl/env/training_logs/interview_data.csv` (untracked, gitignored): confirmed restored to exactly 295,291 rows.
- No `research/paper_strengthening/results/e1_training/` or `.../e1_confirmatory/` directory exists — confirming no training or evaluation was executed by this pass.
- The only new paths on disk are the five files in §1 (plus their `__pycache__` build artifacts, removed).

## 7. Reporting/evaluation flag — a required correction to how V4 will be executed, not to V4 itself

**Your instruction is correct, and it is already what V4 §4.1 specifies — flagging this explicitly because it is easy to implement wrongly.** V4's development-stage gate reads: *"If B2 shows no improvement over B0 at all, no confirmatory run is executed for either arm"* — this is a **both-or-neither** gate on whether to proceed to confirmatory evaluation at all, not a rule that could keep B2 while dropping B0. V4 §4.1 additionally states in its own words: *"B0 is never omitted from the confirmatory stage merely because development results favored B2."* No inconsistency exists between the protocol text and your instruction; the risk is purely in *implementation* — a careless driver script could still evaluate only the "winning" arm. **Recommendation, not a silent change:** given evaluation is cheap (§3's own rationale — inference only, no training), the confirmatory evaluation script should be written so that it takes **both trained arms as required, non-optional inputs** and refuses to run with only one — making the both-or-neither rule structurally impossible to violate, rather than relying on a human to remember it. This is a recommendation for how the (not-yet-written, not run in this pass) confirmatory evaluation script should be structured; it changes no criterion, threshold, or seed in the frozen protocol and does not require a new protocol version.

**On proceeding to confirmatory evaluation whenever training passes technical/stability checks, given low cost:** recommended, and already consistent with V4's own gate — the development-stage gate in §4.3 already is that check (mechanism-check improvement + no per-persona regression, on the development seeds). No amendment to V4 is needed for this; it is already the specified behavior.

**No protocol inconsistency requiring approval was found.** No change to V4's decision rules, thresholds, or seeds was made or is being proposed.

## 8. Precise commands and resource requirements for the later development run

Not executed in this pass. For the record, once approved:

```
# Training (5 seeds x 2 arms = 10 runs at the primary budget; run once per (arm, seed)):
.venv/Scripts/python.exe research/paper_strengthening/scripts/e1_train_condition_b.py --arm B0 --training_seed 42
.venv/Scripts/python.exe research/paper_strengthening/scripts/e1_train_condition_b.py --arm B2 --training_seed 42
# ... repeated for training seeds 123, 456, 789, 999
```

- **Compute:** ~84 seconds/seed at the primary budget (24,576 timesteps), matching Condition A's own recorded `elapsed_sec`; ~14 minutes total for 10 runs (2 arms × 5 seeds), CPU-only, no GPU required. The extended-budget diagnostic (98,304 steps), only if triggered, roughly quadruples whichever arm(s) need it — applied to both arms together per V4 §1.2.
- **Development evaluation:** inference-only against the existing `1001–5005` seeds; seconds, not minutes.
- **Confirmatory evaluation:** 20 seeds × both arms × Condition A × Constant-Same+G × Heuristic+G × 3 held-out profiles — inference-only, on the order of a minute or two total.
- **Disk:** two new checkpoint directories per training seed (`e1_training/B0/seed_<n>/`, `e1_training/B2/seed_<n>/`), each comparable in size to an existing `research/experiments/paper3/checkpoints/seed_*/` directory; per-step logs are small CSVs, one per (arm, seed).

## 9. Recommendation

**Implementation is complete, tested, and verified with zero unresolved discrepancies.** The one real defect found during testing (the log side-effect, §5) was caught, disclosed, and fixed rather than left implicit. No protocol amendment is required. The only remaining gap before a development run is the human-discretion risk named in §7, for which a structural fix (require both arms as inputs to the confirmatory driver) is recommended when that script is written.

**Stopping here. No training launched, no evaluation replay run, no PPO checkpoint touched, nothing tagged, committed, or pushed. Awaiting explicit approval before running `e1_train_condition_b.py` for real.**
