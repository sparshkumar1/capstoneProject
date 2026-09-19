"""X3-A harness library: persona generator, policies, local shield copy (with rule ablation), session simulator.

The session loop is a generalisation of the frozen `run_session_trajectory` (research/scripts/execute_paper3_study.py:296-470)
and is validated against it by gate G-HARNESS (x3a_run.py) before any result is produced. Nothing in the frozen code is modified.
"""
import os
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from rl.env.interview_env import InterviewEnv  # noqa: E402  (frozen; imported only)
from rl.training.simulated_candidate import SimulatedCandidate  # noqa: E402
from rl.guardrails import ACTION_NAMES, ACTION_EASIER, ACTION_SAME, ACTION_HARDER  # noqa: E402

TYPES = ["normal", "nervous_expert", "lucky_guesser", "overconfident_fail", "struggling_junior"]
SKILLS = [0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
FROZEN = [("struggling_junior", 0.20, 1.0), ("overconfident_fail", 0.30, 1.5), ("normal", 0.60, 3.0),
          ("lucky_guesser", 0.80, 4.0), ("nervous_expert", 0.88, 4.5)]
RULES = ["G4", "G1", "G2", "G5", "G6"]
DELTA = {ACTION_EASIER: -1.0, ACTION_SAME: 0.0, ACTION_HARDER: 1.0}


def persona_grid():
    """Generator G1: full factorial persona type x skill; target = round(10*skill)/2 (documented authored rule)."""
    out = []
    for t in TYPES:
        for s in SKILLS:
            out.append({"persona_id": f"{t}@{s:.2f}", "stratum": "grid", "type": t, "skill": s, "target": round(10 * s) / 2.0})
    return out


def persona_frozen():
    return [{"persona_id": f"frozen:{t}", "stratum": "frozen", "type": t, "skill": s, "target": tg} for t, s, tg in FROZEN]


def shield(perf, avg_perf, conf, hes, difficulty, proposed, disabled=frozenset(), medium_min=0.4, medium_max=0.7,
           mutant=None):
    """Local copy of rl.guardrails.apply_canonical_guardrails (consecutive_failures=0, infrastructure failure False),
    with optional rule ablation (`disabled`) and test-only mutants. Equivalence with the frozen function for the full rule set
    is tested in x3a_run.py (random-state test) and through gate G-HARNESS."""
    action = int(proposed)
    diff_norm = difficulty / 5.0 if difficulty > 1.0 else difficulty
    p4 = 0.30 if mutant != "g4_thr" else 0.31
    if "G4" not in disabled and perf < p4 and hes > 0.60:
        return ACTION_EASIER, True, "g4_stuck_easier"
    if "G1" not in disabled and perf < 0.30 and medium_min <= diff_norm <= medium_max:
        return ACTION_EASIER, True, "g1_overload_protection"
    if "G2" not in disabled and conf < 0.30 and hes > 0.70 and perf < 0.80:
        return ACTION_SAME, True, "g2_anxiety_stabilizer_same"
    if "G5" not in disabled and 0.40 < perf < 0.65 and avg_perf < 0.60:
        return ACTION_SAME, True, "g5_partial_same"
    gap = perf - diff_norm
    nervous = (0.80 < perf < 0.95 and hes > 0.65) or (conf < 0.40 and hes > 0.60)
    if "G6" not in disabled and perf >= 0.90 and gap > 0.25 and not nervous:
        return ACTION_HARDER, True, "g6_strong_harder"
    return action, False, "none"


class PPOPolicy:
    def __init__(self, model, vecnorm, mode="intact", pool=None, partner=None):
        self.model, self.vn, self.mode, self.pool, self.partner = model, vecnorm, mode, pool, partner

    def act(self, ctx):
        obs = ctx["obs"]
        if self.mode == "zero":
            obs = np.zeros(6, dtype=np.float32)
        elif self.mode == "shuffle":
            obs = self.pool[(self.partner, ctx["eval_seed"], ctx["step"])]
        a, _ = self.model.predict(self.vn.normalize_obs(obs.reshape(1, -1)), deterministic=True)
        return int(a[0])


def make_policy(kind, persona_index=0, eval_seed=0, ppo=None, mutant=None):
    """returns fn(ctx)->action"""
    if kind == "const_same":
        return lambda c: ACTION_SAME
    if kind == "random":
        rs = np.random.RandomState((eval_seed * 31 + persona_index) % (2 ** 31 - 1))
        return lambda c: int(rs.randint(0, 3))
    if kind == "heuristic":
        hi = {"heur_thr": 0.60, "heur_thr_subtle": 0.76}.get(mutant, 0.75)
        lo = 0.50 if mutant == "heur_lo" else 0.40

        def h(c):
            if c["perf"] > hi and c["current"] < 5.0:
                return ACTION_HARDER
            if c["perf"] < lo and c["current"] > 1.0:
                return ACTION_EASIER
            return ACTION_SAME
        return h
    if kind == "oracle":
        return lambda c: int(InterviewEnv.oracle_action_from_obs(c["obs"]))
    if kind == "controller":
        def ctl(c):
            gap = 5.0 * c["avg"] - c["current"]
            return ACTION_HARDER if gap >= 0.5 else (ACTION_EASIER if gap <= -0.5 else ACTION_SAME)
        return ctl
    if kind == "ppo":
        return ppo.act
    raise ValueError(kind)


def simulate(policy_fn, ptype, skill, target, eval_seed, shield_on, disabled=frozenset(), max_steps=10, mutant=None):
    cand = SimulatedCandidate(skill=skill, persona=ptype, seed=eval_seed)
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
            act, ovr, gid = shield(perf, avg, conf, hes, cur / 5.0, raw, disabled, mutant=mutant)
        else:
            act, ovr, gid = raw, False, "none"
        overrides += int(act != raw)
        raw_l.append(ACTION_NAMES[raw]); fin_l.append(ACTION_NAMES[act]); gid_l.append(gid)
        nxt = cur + DELTA[act]
        if nxt < 1.0 or nxt > 5.0:
            viol += 1
        cur = float(np.clip(nxt, 1.0, 5.0))
        diffs.append(cur)
    d = np.array(diffs)
    ch = np.diff(d)
    err = np.abs(d - target)
    nz = [x for x in ch if abs(x) > 1e-4]
    sc = sum(1 for i in range(1, len(nz)) if nz[i] * nz[i - 1] < 0)
    res = {"final_difficulty": round(float(d[-1]), 3), "target_tracking_error": round(float(err.mean()), 3),
           "volatility": round(float(np.abs(ch).sum() / max_steps), 3), "oscillation_rate": round(sc / max(len(nz) - 1, 1), 3),
           "guardrail_interventions": int(sum(1 for g in gid_l if g != "none")), "constraint_violations": viol,
           "raw_actions": raw_l, "final_actions": fin_l, "guardrail_ids": gid_l,
           # unrounded values for analysis
           "mae_x": float(err.mean()), "vol_x": float(np.abs(ch).sum() / max_steps), "osc_x": sc / max(len(nz) - 1, 1),
           "overrides": overrides, "oracle_agreement": agree / max_steps, "obs_log": obs_log}
    return res


def load_ppo(ckpt_dir, env_log):
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
    model = PPO.load(str(Path(ckpt_dir) / "ppo_final.zip"))
    vn = VecNormalize.load(str(Path(ckpt_dir) / "vecnormalize.pkl"), DummyVecEnv([lambda: InterviewEnv(log_file=str(env_log))]))
    vn.training = False
    vn.norm_reward = False
    return model, vn
