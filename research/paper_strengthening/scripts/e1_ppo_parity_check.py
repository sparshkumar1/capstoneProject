"""
E1 -- deferred PPO-policy adapter parity check (approved run, step 3 of the
E1 V4 development-phase approval message).

This is the parity check E1_IMPLEMENTATION_REPORT.md explicitly deferred:
"PPO-policy parity was deferred (would require loading a checkpoint)". It
loads an existing, frozen, already-registered X3-A checkpoint (never
retrained or modified) via x3a_lib.load_ppo(), builds x3a_lib.PPOPolicy from
it, and runs BOTH x3a_lib.simulate() (the existing X3-A evaluation
implementation) and e1_simulate_adapter.simulate_diverse() (the new E1
adapter) against the identical PPO policy object on identical fixtures,
comparing every field of the returned dict for exact equality.

Two fixture families are checked:
  (a) ordinary_candidate_factory(ptype, skill) -- a plain, unwrapped
      SimulatedCandidate -- checked against x3a_lib.simulate() directly.
      This isolates "does the adapter's loop reproduce x3a_lib.simulate()
      exactly" from any DiverseCandidate-specific behavior.
  (b) diverse_candidate_factory(skill, k=0.0) -- the E1 wrapper at k=0,
      which DiverseCandidate.answer_question() defines as an exact identity
      transform -- checked against the same x3a_lib.simulate() run for the
      matching (ptype="normal", skill) case, since DiverseCandidate always
      constructs its inner SimulatedCandidate with persona="normal".

No checkpoint is modified or retrained. No frozen file is modified. Output
is written to a new, non-gitignored path under
research/paper_strengthening/results/, not under any frozen directory.
"""
import json
import sys
from pathlib import Path

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

import x3a_lib  # noqa: E402  (frozen; imported only)
from e1_simulate_adapter import (  # noqa: E402
    simulate_diverse, ordinary_candidate_factory, diverse_candidate_factory,
)

CKPT_DIR = REPO / "research" / "experiments" / "paper3" / "checkpoints" / "seed_42"
OUT_DIR = REPO / "research" / "paper_strengthening" / "results" / "e1_parity"
OUT_DIR.mkdir(parents=True, exist_ok=True)
ISOLATED_ENV_LOG = OUT_DIR / "_parity_env_dummy_log.csv"

FIXTURE_PERSONAS = [
    ("struggling_junior", 0.20, 1.0),
    ("overconfident_fail", 0.30, 1.5),
    ("normal", 0.60, 3.0),
    ("lucky_guesser", 0.80, 4.0),
    ("nervous_expert", 0.88, 4.5),
]
EVAL_SEEDS = [1001, 2002, 5005]
SHIELD_STATES = [True, False]

FIELDS_TO_COMPARE = [
    "final_difficulty", "target_tracking_error", "volatility", "oscillation_rate",
    "guardrail_interventions", "constraint_violations", "raw_actions", "final_actions",
    "guardrail_ids", "mae_x", "vol_x", "osc_x", "overrides", "oracle_agreement",
]


def compare(a: dict, b: dict, label: str, mismatches: list):
    for f in FIELDS_TO_COMPARE:
        va, vb = a[f], b[f]
        if isinstance(va, float):
            if not np.isclose(va, vb, rtol=0, atol=0):
                mismatches.append(f"{label}: field {f} differs: {va!r} vs {vb!r}")
        elif va != vb:
            mismatches.append(f"{label}: field {f} differs: {va!r} vs {vb!r}")
    for step in a["obs_log"]:
        if not np.array_equal(a["obs_log"][step], b["obs_log"][step]):
            mismatches.append(f"{label}: obs_log[{step}] differs: {a['obs_log'][step]} vs {b['obs_log'][step]}")


def main():
    model, vn = x3a_lib.load_ppo(str(CKPT_DIR), str(ISOLATED_ENV_LOG))
    policy = x3a_lib.PPOPolicy(model, vn)

    mismatches = []
    n_checks = 0

    for ptype, skill, target in FIXTURE_PERSONAS:
        for eval_seed in EVAL_SEEDS:
            for shield_on in SHIELD_STATES:
                n_checks += 1
                label = f"ordinary/{ptype}@{skill}/seed{eval_seed}/shield={shield_on}"

                res_x3a = x3a_lib.simulate(policy.act, ptype, skill, target, eval_seed, shield_on)
                res_e1 = simulate_diverse(
                    policy.act, ordinary_candidate_factory(ptype, skill), target, eval_seed, shield_on
                )
                compare(res_x3a, res_e1, label, mismatches)

                if ptype == "normal":
                    n_checks += 1
                    label_k0 = f"diverse-k0/{ptype}@{skill}/seed{eval_seed}/shield={shield_on}"
                    res_e1_k0 = simulate_diverse(
                        policy.act, diverse_candidate_factory(skill, 0.0), target, eval_seed, shield_on
                    )
                    compare(res_x3a, res_e1_k0, label_k0, mismatches)

    result = {
        "checkpoint_used": str(CKPT_DIR.relative_to(REPO)),
        "checkpoint_sha256": {
            "ppo_final.zip": "8395b6da753f5d272c46bfad018f7a7ae6e5508be58bcd732094771911b3d465",
            "vecnormalize.pkl": "0e24cdd77e27170137ee5739d6b9258418a98bdf5a1a1bea23e8208ed85debcf",
        },
        "n_combinations_checked": n_checks,
        "n_mismatches": len(mismatches),
        "mismatches": mismatches,
        "parity_status": "PASS" if not mismatches else "FAIL",
        "note": "ordinary_candidate_factory cases compare x3a_lib.simulate() directly against the "
                "e1_simulate_adapter.simulate_diverse() loop using the same unwrapped SimulatedCandidate; "
                "diverse-k0 cases additionally check the DiverseCandidate identity-at-k=0 wrapper against "
                "the same x3a_lib.simulate() reference, using the real loaded PPO policy (not a "
                "deterministic stand-in policy as in the unit-test suite).",
    }
    out_path = OUT_DIR / "e1_ppo_parity_check.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    if ISOLATED_ENV_LOG.exists():
        ISOLATED_ENV_LOG.unlink()

    print(json.dumps({k: v for k, v in result.items() if k != "mismatches"}, indent=2))
    if mismatches:
        print("MISMATCHES:")
        for m in mismatches[:20]:
            print(" ", m)
    return 0 if not mismatches else 1


if __name__ == "__main__":
    sys.exit(main())
