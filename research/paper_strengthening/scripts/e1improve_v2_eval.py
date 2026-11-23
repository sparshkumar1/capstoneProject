"""
E1-Improve V2 evaluation (Task 3/4). Tests, per checkpoint, every
predeclared gate condition from E1_IMPROVE_V2_PROTOCOL.md section 3 on
EVAL_SEEDS_DEV only, on the identical 24-cell grid used throughout E1.

For every (checkpoint, gate, cell, eval_seed) episode, a FRESH gated policy
and activation counter are built (research/paper_strengthening/scripts/
e1improve_v2_gates.py::make_gated_policy_v2) so the counter's 10-entry log
corresponds exactly to that one episode's 10 steps -- letting "gate fired",
"raw proposal replaced" (== gate fired, by construction) and "post-shield
override" (final action != the raw proposal that was actually used) be
computed and cross-checked per step, not just inferred from pooled MAE.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
X3A_DIR = REPO / "research" / "confirmatory" / "X3-A"
if str(X3A_DIR) not in sys.path:
    sys.path.insert(0, str(X3A_DIR))
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import x3a_lib  # noqa: E402
from e1_simulate_adapter import simulate_diverse, diverse_candidate_factory  # noqa: E402
from e1_diverse_persona_env import ARM_GRIDS, x3a_target_difficulty  # noqa: E402
from e1_train_condition_b import load_config  # noqa: E402
from e1improve_v2_gates import make_gated_policy_v2, GATES  # noqa: E402
from rl.guardrails import ACTION_NAMES  # noqa: E402  (frozen; for action-name lookups only)

cfg = load_config()
TRAINING_SEEDS = cfg["training_seeds"]
DEV_EVAL_SEEDS = cfg["development_eval_seeds"]
EVAL_GRID = ARM_GRIDS["B2"]

REPO_ROOT = REPO
E1_PRIMARY_ROOT = REPO / "research" / "paper_strengthening" / "results" / "e1_training"
E1_TRACE_ROOT = REPO / "research" / "paper_strengthening" / "results" / "e1improve_checkpoint_trace"
CONDITION_A_ROOT = REPO / "research" / "experiments" / "paper3" / "checkpoints"
OUT_DIR = REPO / "research" / "paper_strengthening" / "results" / "e1improve_v2_eval"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DUMMY_ENV_LOG = OUT_DIR / "_v2_eval_env_dummy_log.csv"

GATE_CONDITIONS = {
    "none": [],
    "G6-nervous": ["G6-nervous"],
    "G4-full": ["G4-full"],
    "G1-full": ["G1-full"],
    "G2-full": ["G2-full"],
    "G5-full": ["G5-full"],
    "G6-full": ["G6-full"],
    "combo-all": ["G6-nervous", "G4-full", "G1-full", "G2-full", "G5-full", "G6-full"],
}


def load_ppo_condition(ckpt_dir: Path):
    model, vn = x3a_lib.load_ppo(str(ckpt_dir), str(DUMMY_ENV_LOG))
    return x3a_lib.PPOPolicy(model, vn)


def load_trace_checkpoint(seed: int, step: int):
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
    from rl.env.interview_env import InterviewEnv
    d = E1_TRACE_ROOT / "B2" / f"seed_{seed}"
    model = PPO.load(str(d / f"b2_seed{seed}_{step}_steps.zip"))
    vn = VecNormalize.load(str(d / f"b2_seed{seed}_vecnormalize_{step}_steps.pkl"),
                            DummyVecEnv([lambda: InterviewEnv(log_file=str(DUMMY_ENV_LOG))]))
    vn.training = False
    vn.norm_reward = False
    return x3a_lib.PPOPolicy(model, vn)


def run_episode(policy_or_gated, target, eval_seed, skill, k, is_gated_tuple=None):
    if is_gated_tuple is not None:
        gated_fn, counter = is_gated_tuple
        res = simulate_diverse(gated_fn, diverse_candidate_factory(skill, k), target, eval_seed, shield_on=True)
        return res, counter["log"]
    res = simulate_diverse(policy_or_gated.act, diverse_candidate_factory(skill, k), target, eval_seed, shield_on=True)
    return res, None


def run_condition(base_policy, gate_names, checkpoint_label: str, gate_label: str, training_seed):
    rows = []
    for skill, k in EVAL_GRID:
        target = x3a_target_difficulty(skill)
        for eval_seed in DEV_EVAL_SEEDS:
            if gate_names is None:
                res, log = run_episode(base_policy, target, eval_seed, skill, k)
                n_fired = n_replaced = n_overridden = 0
            else:
                gated_fn, counter = make_gated_policy_v2(base_policy, gate_names)
                res, log = run_episode(None, target, eval_seed, skill, k, is_gated_tuple=(gated_fn, counter))
                final_action_ints = [
                    {"Easier": 0, "Same": 1, "Harder": 2}[a] for a in res["final_actions"]
                ]
                n_fired = sum(1 for e in log if e["gate_fired"])
                n_replaced = n_fired  # by construction, replacement == firing
                n_overridden = sum(
                    1 for e, fa in zip(log, final_action_ints) if fa != e["used_raw"]
                )
            rows.append({
                "checkpoint": checkpoint_label, "gate": gate_label, "training_seed": training_seed,
                "skill": skill, "k": k, "eval_seed": eval_seed, "target": target,
                "mae": res["mae_x"], "oracle_agreement": res["oracle_agreement"],
                "gate_fired_steps": n_fired, "raw_replaced_steps": n_replaced,
                "post_shield_overridden_steps": n_overridden, "final_actions": res["final_actions"],
            })
    return rows


def aggregate(rows, group_keys):
    buckets = defaultdict(list)
    for r in rows:
        buckets[tuple(r[k] for k in group_keys)].append(r)
    out = []
    for key, items in buckets.items():
        entry = dict(zip(group_keys, key))
        entry["n"] = len(items)
        entry["mae_mean"] = float(np.mean([i["mae"] for i in items]))
        entry["mae_sd"] = float(np.std([i["mae"] for i in items]))
        entry["oracle_agreement_mean"] = float(np.mean([i["oracle_agreement"] for i in items]))
        entry["total_gate_fired_steps"] = int(sum(i["gate_fired_steps"] for i in items))
        entry["total_post_shield_overridden_steps"] = int(sum(i["post_shield_overridden_steps"] for i in items))
        out.append(entry)
    return out


def main():
    all_rows = []

    checkpoints = {
        "ConditionA": (CONDITION_A_ROOT, "frozen", TRAINING_SEEDS),
        "B2@16384": (E1_TRACE_ROOT, "trace16384", TRAINING_SEEDS),
        "B2@24576": (E1_PRIMARY_ROOT, "primary24576", TRAINING_SEEDS),
    }

    for ckpt_label, (root, kind, seeds) in checkpoints.items():
        for seed in seeds:
            if kind == "frozen":
                base_policy = load_ppo_condition(root / f"seed_{seed}")
            elif kind == "trace16384":
                base_policy = load_trace_checkpoint(seed, 16384)
            elif kind == "primary24576":
                base_policy = load_ppo_condition(root / "B2" / f"seed_{seed}")
            for gate_label, gate_names in GATE_CONDITIONS.items():
                names = None if gate_label == "none" else gate_names
                print(f"Running {ckpt_label} seed={seed} gate={gate_label}...")
                all_rows += run_condition(base_policy, names, ckpt_label, gate_label, seed)

    # B0 control-verification pass: G6-nervous only, per protocol section 4
    b0_root = E1_PRIMARY_ROOT / "B0"
    for seed in TRAINING_SEEDS:
        base_policy = load_ppo_condition(b0_root / f"seed_{seed}")
        for gate_label in ("none", "G6-nervous"):
            names = None if gate_label == "none" else GATE_CONDITIONS[gate_label]
            print(f"Running B0(control) seed={seed} gate={gate_label}...")
            all_rows += run_condition(base_policy, names, "B0(control)", gate_label, seed)

    # Standalone Heuristic+G reference (no training seed)
    heuristic = x3a_lib.make_policy("heuristic")
    print("Running Heuristic+G standalone...")
    for skill, k in EVAL_GRID:
        target = x3a_target_difficulty(skill)
        for eval_seed in DEV_EVAL_SEEDS:
            res = simulate_diverse(heuristic, diverse_candidate_factory(skill, k), target, eval_seed, shield_on=True)
            all_rows.append({
                "checkpoint": "Heuristic+G", "gate": "n/a", "training_seed": None,
                "skill": skill, "k": k, "eval_seed": eval_seed, "target": target,
                "mae": res["mae_x"], "oracle_agreement": res["oracle_agreement"],
                "gate_fired_steps": 0, "raw_replaced_steps": 0, "post_shield_overridden_steps": 0,
                "final_actions": res["final_actions"],
            })

    if DUMMY_ENV_LOG.exists():
        DUMMY_ENV_LOG.unlink()

    raw_path = OUT_DIR / "e1improve_v2_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_rows, f, indent=2)

    pooled = aggregate(all_rows, ["checkpoint", "gate"])
    per_seed = aggregate(all_rows, ["checkpoint", "gate", "training_seed"])
    per_cell = aggregate(all_rows, ["checkpoint", "gate", "skill", "k"])

    summary = {
        "pooled_by_checkpoint_gate": pooled,
        "per_seed_by_checkpoint_gate": per_seed,
        "per_cell_by_checkpoint_gate": per_cell,
    }
    summary_path = OUT_DIR / "e1improve_v2_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nRaw: {raw_path}\nSummary: {summary_path}\n")
    print("Pooled MAE by (checkpoint, gate):")
    for r in sorted(pooled, key=lambda x: (x["checkpoint"], x["gate"])):
        print(f"  {r['checkpoint']:>14s} / {r['gate']:>12s}: mae_mean={r['mae_mean']:.4f} "
              f"fired={r['total_gate_fired_steps']:4d} overridden={r['total_post_shield_overridden_steps']:4d} n={r['n']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
