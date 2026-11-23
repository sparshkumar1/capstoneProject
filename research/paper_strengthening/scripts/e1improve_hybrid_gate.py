"""
E1-Improve V1, Intervention B: narrowly-scoped deterministic PPO+Heuristic
gated hybrid controller (no training; pure inference-time policy
composition over already-existing, already-frozen checkpoints).

Gate condition (verbatim, reused unmodified from x3a_lib.shield()'s own G6
"nervous" exclusion clause -- not a newly tuned threshold):
    perf >= 0.90 and conf < 0.40 and hes > 0.60
When this holds at a step's pre-shield state, the Heuristic's raw proposal
(x3a_lib.make_policy("heuristic")) is used instead of the wrapped PPO
policy's raw proposal; otherwise PPO's raw proposal is used unchanged.
Either way, the resulting raw action is passed through the SAME, unmodified
x3a_lib.shield() exactly as every other condition in this study.

Both PPO's policy and the heuristic read only the standard 6-D observation
([perf, avg_perf, conf, hes, progress, difficulty]) -- no persona identity,
target difficulty, or other hidden information is used anywhere in this
file, matching every other policy in x3a_lib.py.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
X3A_DIR = REPO / "research" / "confirmatory" / "X3-A"
if str(X3A_DIR) not in sys.path:
    sys.path.insert(0, str(X3A_DIR))

import x3a_lib  # noqa: E402  (frozen; imported only)

GATE_PERF_MIN = 0.90   # verbatim from x3a_lib.shield()'s G6 "nervous" clause
GATE_CONF_MAX = 0.40   # verbatim from x3a_lib.shield()'s G6 "nervous" clause
GATE_HES_MIN = 0.60    # verbatim from x3a_lib.shield()'s G6 "nervous" clause


def make_gated_policy(ppo_policy):
    """Wraps a PPOPolicy-like object (has .act(ctx)->int) with the heuristic
    fallback gate. Returns a plain fn(ctx)->int usable anywhere a raw policy
    function is expected (e.g. e1_simulate_adapter.simulate_diverse,
    x3a_lib.simulate)."""
    heuristic = x3a_lib.make_policy("heuristic")

    def gated(ctx):
        perf = ctx["perf"]
        obs = ctx["obs"]
        conf, hes = float(obs[2]), float(obs[3])
        if perf >= GATE_PERF_MIN and conf < GATE_CONF_MAX and hes > GATE_HES_MIN:
            return int(heuristic(ctx))
        return int(ppo_policy.act(ctx))

    return gated
