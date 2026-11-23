"""
Regression tests for e1improve_hybrid_gate.py (E1-Improve V1, Intervention
B). Verifies the gate's threshold logic in isolation (no PPO checkpoint
needed) and its exact boundary behavior, since a silent gate-condition bug
would invalidate every reported hybrid result.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

THIS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = THIS_DIR.parent
REPO = SCRIPTS_DIR.parents[2]
for p in (str(SCRIPTS_DIR), str(REPO)):
    if p not in sys.path:
        sys.path.insert(0, p)
X3A_DIR = REPO / "research" / "confirmatory" / "X3-A"
if str(X3A_DIR) not in sys.path:
    sys.path.insert(0, str(X3A_DIR))

from e1improve_hybrid_gate import make_gated_policy, GATE_PERF_MIN, GATE_CONF_MAX, GATE_HES_MIN  # noqa: E402
import x3a_lib  # noqa: E402


class _StubPPO:
    """Always proposes Same (1); records whether .act was called."""
    def __init__(self):
        self.called = False

    def act(self, ctx):
        self.called = True
        return 1  # Same


def _ctx(perf, conf, hes):
    obs = np.array([perf, perf, conf, hes, 0.1, 0.6], dtype=np.float32)
    return {"obs": obs, "perf": perf, "avg": perf, "current": 3.0, "step": 1, "eval_seed": 1001}


def test_gate_thresholds_match_x3a_lib_shield_g6_nervous_clause():
    assert GATE_PERF_MIN == 0.90
    assert GATE_CONF_MAX == 0.40
    assert GATE_HES_MIN == 0.60


def test_gate_fires_inside_region_uses_heuristic_not_ppo():
    stub = _StubPPO()
    gated = make_gated_policy(stub)
    # perf high, current=3.0<5.0 -> heuristic proposes Harder (2)
    action = gated(_ctx(perf=0.95, conf=0.20, hes=0.80))
    assert action == 2
    assert stub.called is False, "PPO must not even be consulted when the gate fires"


def test_gate_does_not_fire_outside_region_uses_ppo():
    stub = _StubPPO()
    gated = make_gated_policy(stub)
    action = gated(_ctx(perf=0.85, conf=0.50, hes=0.30))  # below all three thresholds
    assert action == 1  # PPO's stub proposal (Same)
    assert stub.called is True


@pytest.mark.parametrize("perf,conf,hes,should_fire", [
    (0.90, 0.39, 0.61, True),    # perf==0.90 satisfies the '>=' boundary; conf/hes also satisfied -> fires
    (0.899, 0.10, 0.90, False),  # perf clearly under 0.90 -> no fire regardless of conf/hes
    (0.91, 0.41, 0.90, False),   # conf clearly above 0.40 -> fails '<' check
    (0.91, 0.39, 0.59, False),   # hes clearly below 0.60 -> fails '>' check
    (0.91, 0.39, 0.61, True),    # all three clearly satisfied -> fires
])
def test_gate_boundary_conditions(perf, conf, hes, should_fire):
    stub = _StubPPO()
    gated = make_gated_policy(stub)
    gated(_ctx(perf=perf, conf=conf, hes=hes))
    assert stub.called == (not should_fire)


def test_gate_replicates_x3a_lib_shield_g6_nervous_definition_directly():
    """Cross-checks the gate's threshold triple against a live read of
    x3a_lib.shield()'s own G6 nervous-exclusion clause, so a future edit to
    the frozen shield that changes those constants is caught here rather
    than silently diverging from the (intentionally) reused values."""
    import inspect
    src = inspect.getsource(x3a_lib.shield)
    assert "0.80 < perf < 0.95 and hes > 0.65" in src
    assert "conf < 0.40 and hes > 0.60" in src
