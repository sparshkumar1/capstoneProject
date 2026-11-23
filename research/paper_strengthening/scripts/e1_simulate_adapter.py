"""
E1 -- simulation adapter, per E1_PPO_PERSONA_DIVERSITY_PROTOCOL_V4.md section 5.

research/confirmatory/X3-A/x3a_lib.py::simulate() cannot be reused unmodified
for the diverse-persona arms (B0/B2) or the held-out profiles: it hardcodes
`cand = SimulatedCandidate(skill=skill, persona=ptype, seed=eval_seed)` on its
own line, with no parameter for a custom/wrapped candidate object. It is a
frozen, tagged, gated study (prereg/X3-A/v1) and is not modified here.

This module reimplements ONLY the loop shape x3a_lib.simulate() does not
expose as a separable, reusable piece. Every other piece -- x3a_lib.shield()
(the guardrail function), x3a_lib.make_policy()/PPOPolicy (policy
construction), x3a_lib.ACTION_NAMES/DELTA, and
rl.env.interview_env.InterviewEnv.oracle_action_from_obs -- is imported and
used completely unmodified, exactly as x3a_lib.py itself uses them.

Nothing in x3a_lib.py, rl/, or research/scripts/ is modified by this file.
"""
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

X3A_DIR = REPO / "research" / "confirmatory" / "X3-A"
if str(X3A_DIR) not in sys.path:
    sys.path.insert(0, str(X3A_DIR))

import x3a_lib  # noqa: E402  (frozen library; imported only, never modified)
from rl.env.interview_env import InterviewEnv  # noqa: E402  (frozen; imported only)


def simulate_diverse(policy_fn, cand_factory, target, eval_seed, shield_on,
                      disabled=frozenset(), max_steps=10, mutant=None):
    """
    Mirrors x3a_lib.simulate()'s loop exactly (same state construction, same
    oracle-agreement bookkeeping, same shield call, same metric formulas,
    same return schema) -- the ONLY difference from x3a_lib.simulate() is
    that the candidate is obtained from `cand_factory(eval_seed)` instead of
    being hardcoded as `SimulatedCandidate(skill, ptype, eval_seed)`.

    cand_factory: callable(eval_seed) -> object with .answer_question(diff)
                  returning {"performance_score","confidence_score",
                  "hesitation","response_time"} -- the same duck-typed
                  interface InterviewEnv itself relies on.

    Returns the identical dict schema as x3a_lib.simulate().
    """
    cand = cand_factory(eval_seed)
    cur = 3.0
    diffs = [cur]
    hist = []
    raw_l, fin_l, gid_l = [], [], []
    viol = 0
    agree = 0
    overrides = 0
    obs_log = {}
    for step in range(1, max_steps + 1):
        out = cand.answer_question(cur / 5.0)
        perf, conf, hes = float(out["performance_score"]), float(out["confidence_score"]), float(out["hesitation"])
        hist.append(perf)
        avg = float(np.mean(hist[-5:]))
        obs = np.array([perf, avg, conf, hes, float(step / max_steps), cur / 5.0], dtype=np.float32)
        obs_log[step] = obs
        ctx = {"obs": obs, "perf": perf, "avg": avg, "current": cur, "step": step, "eval_seed": eval_seed}
        raw = int(policy_fn(ctx))
        agree += int(raw == int(InterviewEnv.oracle_action_from_obs(obs)))
        if shield_on:
            act, ovr, gid = x3a_lib.shield(perf, avg, conf, hes, cur / 5.0, raw, disabled, mutant=mutant)
        else:
            act, ovr, gid = raw, False, "none"
        overrides += int(act != raw)
        raw_l.append(x3a_lib.ACTION_NAMES[raw])
        fin_l.append(x3a_lib.ACTION_NAMES[act])
        gid_l.append(gid)
        nxt = cur + x3a_lib.DELTA[act]
        if nxt < 1.0 or nxt > 5.0:
            viol += 1
        cur = float(np.clip(nxt, 1.0, 5.0))
        diffs.append(cur)
    d = np.array(diffs)
    ch = np.diff(d)
    err = np.abs(d - target)
    nz = [x for x in ch if abs(x) > 1e-4]
    sc = sum(1 for i in range(1, len(nz)) if nz[i] * nz[i - 1] < 0)
    res = {
        "final_difficulty": round(float(d[-1]), 3),
        "target_tracking_error": round(float(err.mean()), 3),
        "volatility": round(float(np.abs(ch).sum() / max_steps), 3),
        "oscillation_rate": round(sc / max(len(nz) - 1, 1), 3),
        "guardrail_interventions": int(sum(1 for g in gid_l if g != "none")),
        "constraint_violations": viol,
        "raw_actions": raw_l, "final_actions": fin_l, "guardrail_ids": gid_l,
        "mae_x": float(err.mean()), "vol_x": float(np.abs(ch).sum() / max_steps),
        "osc_x": sc / max(len(nz) - 1, 1),
        "overrides": overrides, "oracle_agreement": agree / max_steps, "obs_log": obs_log,
    }
    return res


def ordinary_candidate_factory(ptype: str, skill: float):
    """Builds a plain, UNWRAPPED SimulatedCandidate -- used only for the
    parity test against x3a_lib.simulate() (never for B0/B2, which always
    use DiverseCandidate)."""
    from rl.training.simulated_candidate import SimulatedCandidate

    def factory(eval_seed):
        return SimulatedCandidate(skill=skill, persona=ptype, seed=eval_seed)
    return factory


def diverse_candidate_factory(skill: float, k: float):
    """Builds a DiverseCandidate factory for a fixed (skill, k) -- used for
    B0/B2/held-out-profile confirmatory evaluation."""
    from e1_diverse_persona_env import DiverseCandidate

    def factory(eval_seed):
        return DiverseCandidate(skill=skill, seed=eval_seed, k=k)
    return factory
