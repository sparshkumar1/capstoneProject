"""
Regression tests for e1improve_v2_gates.py (E1-Improve V2). Covers:
  - each gate predicate's exact boundary behavior
  - the combo-all OR-combination's order-independence
  - the predeclared "shield-dominated no-op" theorem (E1_IMPROVE_V2_PROTOCOL.md
    section 2), verified directly against the live, unmodified
    x3a_lib.shield() -- not merely asserted from reading the source.
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

import x3a_lib  # noqa: E402
from e1improve_v2_gates import (  # noqa: E402
    gate_g4_full, gate_g1_full, gate_g2_full, gate_g5_full, gate_g6_full, gate_g6_nervous,
    make_gated_policy_v2, GATES,
)
from e1improve_hybrid_gate import make_gated_policy as make_gated_policy_v1  # noqa: E402


def _ctx(perf, conf, hes, avg=None, current=3.0):
    obs = np.array([perf, avg if avg is not None else perf, conf, hes, 0.1, current / 5.0], dtype=np.float32)
    return {"obs": obs, "perf": perf, "avg": avg if avg is not None else perf, "current": current, "step": 1, "eval_seed": 1001}


# ---------------------------------------------------------------------------
# Predicate boundary tests (clear margins, avoiding float32-boundary noise)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("perf,hes,expected", [
    (0.29, 0.61, True), (0.31, 0.61, False), (0.29, 0.59, False),
])
def test_g4_full_boundary(perf, hes, expected):
    assert gate_g4_full(_ctx(perf=perf, conf=0.5, hes=hes)) == expected


@pytest.mark.parametrize("perf,current,expected", [
    (0.29, 2.5, True),   # diff_norm=0.5, inside [0.4,0.7]
    (0.29, 1.5, False),  # diff_norm=0.3, outside
    (0.29, 4.0, False),  # diff_norm=0.8, outside
    (0.31, 2.5, False),  # perf too high
])
def test_g1_full_boundary(perf, current, expected):
    assert gate_g1_full(_ctx(perf=perf, conf=0.5, hes=0.5, current=current)) == expected


@pytest.mark.parametrize("conf,hes,perf,expected", [
    (0.29, 0.71, 0.79, True), (0.31, 0.71, 0.79, False), (0.29, 0.69, 0.79, False), (0.29, 0.71, 0.81, False),
])
def test_g2_full_boundary(conf, hes, perf, expected):
    assert gate_g2_full(_ctx(perf=perf, conf=conf, hes=hes)) == expected


@pytest.mark.parametrize("perf,avg,expected", [
    (0.50, 0.59, True), (0.39, 0.59, False), (0.66, 0.59, False), (0.50, 0.61, False),
])
def test_g5_full_boundary(perf, avg, expected):
    assert gate_g5_full(_ctx(perf=perf, conf=0.5, hes=0.5, avg=avg)) == expected


def test_g6_full_boundary_fires_when_strong_and_not_nervous():
    # perf=0.95, current=3.0 -> diff_norm=0.6, gap=0.35>0.25; conf/hes chosen to avoid both nervous clauses
    assert gate_g6_full(_ctx(perf=0.95, conf=0.90, hes=0.10, current=3.0)) is True


def test_g6_full_does_not_fire_when_nervous_conf_hes_clause_holds():
    assert gate_g6_full(_ctx(perf=0.95, conf=0.20, hes=0.80, current=3.0)) is False


def test_g6_nervous_fires_exactly_where_g6_full_excludes_via_conf_hes_clause():
    ctx = _ctx(perf=0.95, conf=0.20, hes=0.80, current=3.0)
    assert gate_g6_full(ctx) is False
    assert gate_g6_nervous(ctx) is True


def test_g6_nervous_matches_v1_gate_exactly():
    """V2's reproduced G6-nervous predicate must agree with V1's original
    e1improve_hybrid_gate.py implementation on every case -- they are the
    same control condition, defined in two files for module-structure
    reasons only. Uses two stub policies that disagree on every state, so
    "which raw proposal survives" is a direct, unambiguous witness of
    whether each implementation's gate fired."""
    class _StubA:
        def act(self, ctx):
            return 0  # Easier

    for perf, conf, hes in [(0.95, 0.2, 0.8), (0.85, 0.2, 0.8), (0.95, 0.5, 0.8), (0.95, 0.2, 0.5), (0.90, 0.39, 0.61)]:
        ctx = _ctx(perf=perf, conf=conf, hes=hes)
        expected_fires = (perf >= 0.90) and (conf < 0.40) and (hes > 0.60)
        assert gate_g6_nervous(ctx) == expected_fires

        v1_gated = make_gated_policy_v1(_StubA())
        v1_action = v1_gated(ctx)
        # When the gate fires, V1 substitutes the Heuristic's proposal (not StubA's constant 0=Easier)
        heuristic_action = x3a_lib.make_policy("heuristic")(ctx)
        if expected_fires:
            assert v1_action == heuristic_action
        else:
            assert v1_action == 0  # StubA's raw proposal, unchanged


# ---------------------------------------------------------------------------
# combo-all OR-combination: order-independence
# ---------------------------------------------------------------------------

class _StubPolicy:
    def __init__(self, action=1):
        self.action = action
        self.calls = 0

    def act(self, ctx):
        self.calls += 1
        return self.action


def test_combo_all_fires_if_any_predicate_fires():
    ctx = _ctx(perf=0.29, conf=0.5, hes=0.61)  # satisfies G4-full only
    gated, counter = make_gated_policy_v2(_StubPolicy(), ["G4-full", "G1-full", "G2-full", "G5-full", "G6-full", "G6-nervous"])
    gated(ctx)
    assert counter["log"][0]["gate_fired"] is True


def test_combo_all_is_order_independent():
    ctx = _ctx(perf=0.95, conf=0.20, hes=0.80)  # satisfies G6-nervous only
    orderings = [
        ["G4-full", "G1-full", "G2-full", "G5-full", "G6-full", "G6-nervous"],
        ["G6-nervous", "G6-full", "G5-full", "G2-full", "G1-full", "G4-full"],
        ["G2-full", "G6-nervous", "G4-full", "G6-full", "G1-full", "G5-full"],
    ]
    results = []
    for order in orderings:
        gated, counter = make_gated_policy_v2(_StubPolicy(), order)
        results.append(gated(ctx))
    assert len(set(results)) == 1, "combo-all must give the same action regardless of gate-name order"


def test_combo_all_no_gate_fires_uses_ppo_raw():
    # perf=0.70 clears every gate's perf range (not <0.30, not in (0.40,0.65), not >=0.90)
    ctx = _ctx(perf=0.70, conf=0.50, hes=0.50)  # inside no gate's region
    stub = _StubPolicy(action=2)
    gated, counter = make_gated_policy_v2(stub, list(GATES.keys()))
    action = gated(ctx)
    assert counter["log"][0]["gate_fired"] is False
    assert action == 2  # PPO's (stub's) raw proposal, unchanged


# ---------------------------------------------------------------------------
# The predeclared "shield-dominated no-op" theorem, verified against the
# LIVE x3a_lib.shield() (not merely the predicate functions above)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("perf,conf,hes,avg,current,gate_fn,expected_action", [
    (0.20, 0.5, 0.70, 0.5, 3.0, gate_g4_full, 0),   # G4 -> Easier
    (0.20, 0.5, 0.50, 0.5, 2.5, gate_g1_full, 0),   # G1 -> Easier
    (0.79, 0.20, 0.80, 0.5, 3.0, gate_g2_full, 1),  # G2 -> Same
    (0.50, 0.5, 0.50, 0.50, 3.0, gate_g5_full, 1),  # G5 -> Same
    (0.95, 0.90, 0.10, 0.5, 3.0, gate_g6_full, 2),  # G6 -> Harder
])
def test_shield_forces_action_independent_of_raw_proposal(perf, conf, hes, avg, current, gate_fn, expected_action):
    """Direct empirical proof of the no-op theorem: with the gate's own
    predicate true, x3a_lib.shield() returns the SAME action for every one
    of the three possible raw proposals (Easier/Same/Harder) -- confirming
    that substituting PPO's raw proposal for the Heuristic's (or vice
    versa) cannot change the final action in this state."""
    ctx = _ctx(perf=perf, conf=conf, hes=hes, avg=avg, current=current)
    assert gate_fn(ctx) is True, "precondition: this state must actually trigger the gate being tested"
    diff_norm = current / 5.0
    outcomes = set()
    for raw_proposal in (0, 1, 2):
        action, overridden, gid = x3a_lib.shield(perf, avg, conf, hes, diff_norm, raw_proposal)
        outcomes.add(action)
        assert overridden is True
    assert outcomes == {expected_action}, (
        f"shield() must return the same forced action ({expected_action}) regardless of raw proposal; got {outcomes}"
    )


def test_g6_nervous_region_is_NOT_shield_dominated_raw_proposal_matters():
    """Contrast case: in the G6-nervous region (where NO guardrail fires),
    the raw proposal DOES determine the final action -- this is exactly why
    gating there (unlike the five -full gates above) can change MAE."""
    ctx = _ctx(perf=0.95, conf=0.20, hes=0.80, current=3.0)
    assert gate_g6_nervous(ctx) is True
    diff_norm = 3.0 / 5.0
    outcomes = set()
    for raw_proposal in (0, 1, 2):
        action, overridden, gid = x3a_lib.shield(0.95, 0.95, 0.20, 0.80, diff_norm, raw_proposal)
        assert overridden is False
        assert gid == "none"
        outcomes.add(action)
    assert outcomes == {0, 1, 2}, "raw proposal must pass through unmodified in the guardrail-free region"
