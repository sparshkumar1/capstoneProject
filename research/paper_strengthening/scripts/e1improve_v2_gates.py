"""
E1-Improve V2 -- expanded gate predicates, all copied verbatim from
rl/guardrails.py::apply_canonical_guardrails / x3a_lib.py::shield (read-only
dependencies, re-verified unchanged: sha256 c4198975227a03f9a672e982d0a3aa62ea60c41331c51ef55285410c409666ba
and 3badbb39dbf4974a53899ab013c9d0091f40aad718d34fc1b7502e6d4771e506 respectively).
No new threshold is introduced anywhere in this file.

Per E1_IMPROVE_V2_PROTOCOL.md section 2: G4/G1/G2/G5/G6-full's own firing
predicates are each a region where shield() returns a constant action
independent of the raw proposal -- gating on them is a provable no-op on
final MAE. They are still implemented and tested here (not skipped) so that
prediction is verified empirically, not merely asserted.
"""


def diff_norm_from_ctx(ctx) -> float:
    """ctx['current'] is on [1,5] (matches x3a_lib.simulate/simulate_diverse's
    convention); shield() itself receives current/5.0, so diff_norm ==
    ctx['current']/5.0 exactly -- reproduced here only for gate predicates
    that need it directly, not as a new definition."""
    return float(ctx["current"]) / 5.0


def gate_g4_full(ctx) -> bool:
    perf, hes = ctx["perf"], float(ctx["obs"][3])
    return perf < 0.30 and hes > 0.60


def gate_g1_full(ctx) -> bool:
    perf = ctx["perf"]
    diff_norm = diff_norm_from_ctx(ctx)
    return perf < 0.30 and 0.4 <= diff_norm <= 0.7


def gate_g2_full(ctx) -> bool:
    perf = ctx["perf"]
    conf, hes = float(ctx["obs"][2]), float(ctx["obs"][3])
    return conf < 0.30 and hes > 0.70 and perf < 0.80


def gate_g5_full(ctx) -> bool:
    perf, avg = ctx["perf"], ctx["avg"]
    return 0.40 < perf < 0.65 and avg < 0.60


def gate_g6_full(ctx) -> bool:
    perf = ctx["perf"]
    conf, hes = float(ctx["obs"][2]), float(ctx["obs"][3])
    diff_norm = diff_norm_from_ctx(ctx)
    gap = perf - diff_norm
    nervous = (0.80 < perf < 0.95 and hes > 0.65) or (conf < 0.40 and hes > 0.60)
    return perf >= 0.90 and gap > 0.25 and not nervous


def gate_g6_nervous(ctx) -> bool:
    """The control gate -- identical predicate to e1improve_hybrid_gate.py's
    original V1 gate, reproduced here (not imported) only so every gate in
    this module shares the same ctx-based signature; verified identical by
    test_e1improve_v2_gates.py."""
    perf = ctx["perf"]
    conf, hes = float(ctx["obs"][2]), float(ctx["obs"][3])
    return perf >= 0.90 and conf < 0.40 and hes > 0.60


GATES = {
    "G4-full": gate_g4_full,
    "G1-full": gate_g1_full,
    "G2-full": gate_g2_full,
    "G5-full": gate_g5_full,
    "G6-full": gate_g6_full,
    "G6-nervous": gate_g6_nervous,
}


def make_gated_policy_v2(ppo_policy, gate_names):
    """Deterministic, order-independent OR-combination: if ANY named gate's
    predicate is true for the current pre-shield state, use the Heuristic's
    raw proposal; otherwise use ppo_policy's raw proposal. Returns
    (gated_fn, activation_counter) where activation_counter is a mutable
    dict tracking, per call: gate_fired (bool), raw_replaced (bool, always
    == gate_fired), ppo_raw, heuristic_raw, used_raw -- appended to
    activation_counter['log'] so callers can compute post-shield override
    counts by comparing used_raw to the final action returned by shield()
    separately."""
    import x3a_lib  # local import: frozen, read-only dependency

    heuristic = x3a_lib.make_policy("heuristic")
    predicates = [GATES[name] for name in gate_names]
    counter = {"log": []}

    def gated(ctx):
        fired = any(p(ctx) for p in predicates)
        ppo_raw = int(ppo_policy.act(ctx))
        heur_raw = int(heuristic(ctx))
        used = heur_raw if fired else ppo_raw
        counter["log"].append({
            "step": ctx["step"], "gate_fired": fired,
            "ppo_raw": ppo_raw, "heuristic_raw": heur_raw, "used_raw": used,
        })
        return used

    return gated, counter
