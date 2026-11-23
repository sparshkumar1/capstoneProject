# E1-Improve V2 — Extending the Deterministic Gate: Results

## 1. Protocol hash and exact scope

`research/paper_strengthening/E1_IMPROVE_V2_PROTOCOL.md`, SHA-256 `ab4d6d08855a6861e25c0894f1f43d3b506fe7e34c745049a3a007be4f4114b7`, local tag `explore/E1-improve/v2` on commit `72b5d03` (**not pushed**). Read-only dependencies re-verified unchanged before running: `x3a_lib.py` (`3badbb39...`), `rl/guardrails.py` (`c4198975...`) — both byte-identical to their hashes in E1's own original registration. Scope: `EVAL_SEEDS_DEV = [1001,2002,3003,4004,5005]` only, the 24-cell `(skill,k)` grid, no retraining, no reward/state/action/evaluator/target-formula/guardrail-semantics change, no confirmatory seed or held-out profile touched (verified directly: no occurrence of `21021`–`40040` in any new output file).

## 2. Exact gate predicates evaluated (Task 1.2/1.3, predeclared before any result was inspected)

| Rule | Predicate, verbatim from `shield()`/`apply_canonical_guardrails()` | Forced action when true |
|---|---|---|
| G0 | `is_infrastructure_failure` | Same — **excluded**: not a function of the 6-D observation, never true in this simulation harness |
| G4 | `perf<0.30 and hes>0.60` | Easier |
| G1 | `perf<0.30 and 0.4<=diff_norm<=0.7` | Easier |
| G2 | `conf<0.30 and hes>0.70 and perf<0.80` | Same |
| G5 | `0.40<perf<0.65 and avg_perf<0.60` | Same |
| G6 (full) | `perf>=0.90 and gap>0.25 and not nervous` | Harder |
| G6-nervous (control, = V1's existing gate) | `perf>=0.90 and conf<0.40 and hes>0.60` (G6's own exclusion sub-clause — a region where G6 does **not** fire) | n/a — raw proposal passes through |

**Predeclared theorem** (§2 of the protocol): G4/G1/G2/G5/G6-full's own full predicates each coincide exactly with a region where `shield()` returns a hard-coded constant action, independent of the raw proposal — gating on them **cannot** change the final action or MAE. **Verified twice, before the full grid run:** (a) by direct reading of `shield()`'s `return` statements (none reference the `proposed`/`action` argument in the four Easier/Same-forcing rules or G6's Harder-forcing branch); (b) empirically, `test_e1improve_v2_gates.py::test_shield_forces_action_independent_of_raw_proposal` calls the live, unmodified `x3a_lib.shield()` directly with all three possible raw proposals (Easier/Same/Harder) at a state satisfying each rule and confirms an identical forced action every time (5/5 parametrized cases passed). `combo-all` = logical OR of all six predicates above (deterministic, order-independent — verified by `test_combo_all_is_order_independent`, three different orderings, identical result).

## 3. Full baseline and gate comparison (pooled, all 600-episode conditions except Heuristic+G at 120)

| Checkpoint | gate=none | G6-nervous (control) | G1-full | G2-full | G4-full | G5-full | G6-full | combo-all |
|---|---|---|---|---|---|---|---|---|
| Condition A | 0.4571 | **0.4192** | 0.4571 | 0.4571 | 0.4571 | 0.4571 | 0.4571 | 0.4192 |
| B2 @ 16,384 | 0.2697 | 0.2697 | 0.2697 | 0.2697 | 0.2697 | 0.2697 | 0.2697 | 0.2697 |
| B2 @ 24,576 | 0.2735 | 0.2735 | 0.2735 | 0.2735 | 0.2735 | 0.2735 | 0.2735 | 0.2735 |
| B0 (control only) | 0.4389 | 0.4011 | — | — | — | — | — | — |
| Heuristic+G (standalone reference) | — | — | — | — | — | — | 0.2674 | — |

**Every G1-full/G2-full/G4-full/G5-full/G6-full result is bit-identical to `none`, at every checkpoint** — the predeclared theorem holds exactly, empirically, not just for the boundary-test cases but across the full 600-episode grid (confirmed per-cell, §4). `combo-all` is bit-identical to `G6-nervous` alone at every checkpoint — combining the no-op gates with `G6-nervous` adds nothing, exactly as predicted. `G6-nervous`/`combo-all` reproduce V1's already-reported numbers exactly: Condition A `0.4571→0.4192` (Δ`-0.0379`), B0 `0.4389→0.4011` (Δ`-0.0379`) — a harness-correctness check, passed.

**Gap to Heuristic+G (0.2674):** Condition A gated `0.4192` (`+0.1518` worse), B2@16384 `0.2697` (`+0.0023` worse), B2@24576 `0.2735` (`+0.0061` worse). None reaches or beats Heuristic+G with any gate tested here.

## 4. Per-seed and per-cell results

**Per-seed (Condition A, `none` vs. `G6-nervous`):** every one of the 5 training seeds improves individually — `42: 0.4386→0.4008`, `123: 0.4652→0.4273`, `456: 0.4629→0.4250`, `789: 0.4652→0.4273`, `999: 0.4538→0.4159` — consistent, not driven by one seed.

**Per-cell (Task 4, "is the improvement concentrated in one cell?"):** for Condition A, `G6-nervous`/`combo-all` change **exactly 2 of the 24 cells**, both at `skill=0.90`: `k=0.45` (`0.8818→0.6818`, `Δ-0.20`) and `k=0.60` (`1.3909→0.6818`, `Δ-0.71`); **every other cell is bit-identical to `none`.** **Answer: concentrated, but in two cells, not one** — and it is entirely absent for B2@16384/B2@24576 (G6-nervous changes zero cells there — B2's own raw policy already matches whatever the gate would substitute).

**`skill=0.80, k=0.60` cell specifically (the originally-hypothesized "lucky_guesser" cell), all conditions:** Condition A and B0 stay at `1.0000` under **every** gate tested, including `G6-nervous`/`combo-all` — confirms V1's finding again: at this cell the candidate's actual performance at the evaluation-time difficulty (`0.6`) never reaches the `0.90` gate threshold, so no gate ever fires here. B2@16384/B2@24576 are already at `0.1636` (matching Heuristic) regardless of gating — the gate is a no-op there too, but because the base policy is already correct, not because the gate is inert.

**`skill=0.90` cells specifically:** the only cells where any gate changes anything (Condition A only, `G6-nervous`/`combo-all`, `k=0.45` and `k=0.60`, both improved, §above).

## 5. Verification and test outcomes

- **89/89 tests pass**: 52 original E1 tests + 9 V1 hybrid-gate tests + 28 new V2 tests (predicate boundaries for all 5 `-full` gates, `combo-all` order-independence, `G6-nervous` cross-check against V1's own implementation, and the live-`shield()` no-op-theorem verification).
- **Every pooled/per-cell number above was recomputed directly** from `e1improve_v2_raw.json`/`e1improve_v2_summary.json`, not carried over from memory.
- **No per-cell regression `>=0.05` anywhere** for any gate relative to that checkpoint's own `none` baseline (the five `-full` gates are exactly `0.0` everywhere by the theorem; `G6-nervous`/`combo-all` only ever improve, never regress, on Condition A/B0, and are exactly `0.0` on both B2 checkpoints).
- **Gate activation counts** (Task 4's explicit ask): e.g. Condition A `G6-nervous` fires on 45/3000 steps (0.60 seconds... i.e. 45 of the 600 episodes × up to 10 steps = 6000 possible steps) with 2,373 total post-shield-overridden steps recorded across the run overall (from other, always-active guardrails, not from this gate) — the gate's own firing rate is low and concentrated, consistent with it affecting only 2 of 24 cells. `G2-full` fires far more often (3,710–4,655 steps across conditions) precisely because G2's own condition is common, but — as proven — every one of those firings is shield-overridden to the same action regardless, hence zero effect on MAE.
- **Not treated as independent replicates or statistically significant:** every number above is descriptive; no significance claim is made from development-seed results, consistent with the task's explicit instruction.

## 6. What improved, what did not, whether PPO remains behind the heuristic

**What improved:** nothing beyond what V1 already established. `G6-nervous` (retained, unmodified) remains the only gate that changes any final action, and only for Condition A/B0 (not for either B2 checkpoint, whose raw policy already covers this region). **What did not improve:** all five newly-tested full-predicate gates (`G1/G2/G4/G5/G6-full`) and their combination with `G6-nervous` (`combo-all`) — every one is **provably and empirically a bit-for-bit no-op** on final MAE at every checkpoint tested. **Per the predeclared selection rule, none of the new candidates beats `G6-nervous` on any checkpoint** (all are tied at best, several worse where `G6-nervous` itself does something) — **the existing `G6-nervous` gate is retained unchanged; this extension did not improve the system beyond what was already implemented and reported in V1.** **PPO remains behind Heuristic+G** (`0.2674`) in every tested configuration — closest approach is B2@16,384 ungated or gated (identical, `0.2697`), a gap of `0.0023`, well inside that checkpoint's own cross-seed SD (`0.0034`, from V1) and therefore not a demonstrated win.

## 7. Single most defensible next step

The five `-full` guardrail predicates are now provably exhausted as gate candidates (all are shield-dominated no-ops; re-testing them differently would not change this, since it follows from `shield()`'s own code, not from any evaluation noise). The one remaining unexplored, still-legitimate-without-new-thresholds direction is **testing gates built from combinations of the *boundary regions between* existing guardrails** (e.g., states just outside G2's `perf<0.80` cutoff, still using G2's own `conf`/`hes` numbers but not its `perf` bound) — but that would require defining a genuinely new predicate, which is explicitly out of scope for a "no new thresholds" iteration. Absent that, **the most defensible next step is outside the gate-extension family entirely**: revisit the train/eval dynamics mismatch (episode horizon, difficulty step size) identified in `E1_IMPROVE_V1_REPORT.md` §2 — explicitly deferred from this iteration by the task's own scope, and the only remaining evidence-backed lever that has not yet been tried.

## Reproduction

```bash
cd /c/Users/spars/Downloads/PrepAIred
EVALUATOR_MOCK_MODE=1 .venv/Scripts/python.exe -m pytest research/paper_strengthening/scripts/tests/ -q   # 89 passed
.venv/Scripts/python.exe research/paper_strengthening/scripts/e1improve_v2_eval.py                          # ~1-2 min, no training
```

**Files:** protocol `research/paper_strengthening/E1_IMPROVE_V2_PROTOCOL.md`; code `research/paper_strengthening/scripts/e1improve_v2_gates.py`, `e1improve_v2_eval.py`; tests `research/paper_strengthening/scripts/tests/test_e1improve_v2_gates.py`; registration `research/preregistration/E1/E1_IMPROVE_V2_manifest.json`, tag `explore/E1-improve/v2` on commit `72b5d03` (local, not pushed); results `research/paper_strengthening/results/e1improve_v2_eval/` (new, uncommitted). All prior E1/E1-Improve-V1 files and results untouched (verified via `git status` — no modifications, only pre-existing untracked directories).
