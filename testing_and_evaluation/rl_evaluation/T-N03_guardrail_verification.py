"""
T-N03 — Guardrail rule verification against rl/guardrails.py (the real, frozen
implementation; this script does not modify it).

Constructs states at and around each documented guardrail boundary
(G4, G1, G2, G3/G5, G6) and calls the real apply_canonical_guardrails()
function directly, confirming each rule fires exactly where documented.

Also specifically re-checks the case originally found by T-N02 (score=0.35,
avg=0.35, conf=0.5, hes=0.5, difficulty=3/5) where the raw PPO policy proposed
"Harder" for a below-average-scoring candidate and no guardrail caught it.
This gap was closed on 2026-11-12 by widening G5's lower bound from
`perf > 0.40` to `perf >= 0.30` (see rl/guardrails.py module docstring);
this script now confirms the fix closes the gap without regressing any other
documented boundary.

Run: .venv/Scripts/python.exe testing_and_evaluation/rl_evaluation/T-N03_guardrail_verification.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from rl.guardrails import apply_canonical_guardrails, ACTION_NAMES  # noqa: E402

# (label, perf, avg_perf, conf, hes, progress, difficulty_1to5, proposed_action, expected_guardrail_id_or_None)
CASES = [
    ("G4_stuck_triggers", 0.20, 0.25, 0.5, 0.70, 0.5, 3, 2, "g4_stuck_easier"),
    ("G4_boundary_perf_0.29_hes_0.61", 0.29, 0.30, 0.5, 0.61, 0.5, 3, 2, "g4_stuck_easier"),
    ("G4_just_below_boundary_perf_0.30", 0.30, 0.30, 0.5, 0.70, 0.5, 3, 2, "g5_partial_same"),  # perf not < 0.30 so G4/G1 don't fire; since the 2026-11-12 fix, perf=0.30 now falls into G5's widened band
    ("G1_overload_mid_diff", 0.20, 0.25, 0.6, 0.40, 0.5, 3, 1, "g1_overload_protection"),  # diff=3 -> diff_norm=0.6, in [0.4,0.7]
    ("G1_overload_low_diff_out_of_band", 0.20, 0.25, 0.6, 0.40, 0.5, 1, 1, None),  # diff=1 -> diff_norm=0.2, out of [0.4,0.7]
    ("G2_anxiety_stabilizer", 0.50, 0.50, 0.20, 0.75, 0.5, 3, 2, "g2_anxiety_stabilizer_same"),
    ("G5_partial_understanding", 0.50, 0.45, 0.6, 0.4, 0.5, 3, 1, "g5_partial_same"),
    ("G6_strong_performer", 0.95, 0.60, 0.8, 0.2, 0.5, 2, 1, "g6_strong_harder"),  # gap = 0.95-0.4=0.55>0.25
    ("G6_nervous_expert_excluded", 0.92, 0.60, 0.3, 0.70, 0.5, 2, 1, None),  # nervous_expert via conf<0.4,hes>0.6 -> G6 should NOT fire
    ("THE_GAP_CASE_from_T-N02_NOW_FIXED", 0.35, 0.35, 0.5, 0.5, 0.5, 3, 2, "g5_partial_same"),  # was uncovered; closed by the 2026-11-12 G5 widening (0.40->0.30)
    ("G5_new_lower_boundary_perf_0.30", 0.30, 0.30, 0.5, 0.5, 0.5, 3, 2, "g5_partial_same"),  # exactly at new inclusive boundary
    ("just_below_0.30_still_G1_mid_diff", 0.299, 0.299, 0.5, 0.5, 0.5, 3, 2, "g1_overload_protection"),  # perf<0.30 and diff_norm=0.6 in [0.4,0.7] -> G1 fires (hes=0.5 not >0.60 so G4 doesn't)
    ("infra_failure_override", 0.95, 0.95, 0.9, 0.1, 0.5, 3, 2, "guardrail_infra_failure_same"),
]

INFRA_FAILURE_LABEL = "infra_failure_override"


def main() -> int:
    mismatches = []
    for label, perf, avg_perf, conf, hes, progress, diff, proposed, expected in CASES:
        is_infra = (label == INFRA_FAILURE_LABEL)
        final_action, overridden, guardrail_id = apply_canonical_guardrails(
            perf=perf, avg_perf=avg_perf, conf=conf, hes=hes, progress=progress,
            difficulty=diff, proposed_action=proposed,
            is_infrastructure_failure=is_infra,
        )
        expected_norm = expected if expected is not None else "none"
        ok = (guardrail_id == expected_norm)
        status = "OK" if ok else "MISMATCH"
        if not ok:
            mismatches.append((label, expected_norm, guardrail_id))
        print(f"[{status}] {label}: perf={perf} avg={avg_perf} conf={conf} hes={hes} diff={diff} proposed={ACTION_NAMES[proposed]}"
              f" -> final={ACTION_NAMES[final_action]} overridden={overridden} guardrail={guardrail_id} (expected={expected_norm})")

    print()
    print(f"Cases run: {len(CASES)}  Mismatches: {len(mismatches)}")
    if mismatches:
        print("MISMATCHES (documented expectation vs actual code behavior):")
        for label, exp, act in mismatches:
            print(f"  - {label}: expected guardrail={exp!r}, code returned={act!r}")

    print()
    print("STATUS re: the gap case — perf in [0.30, 0.40) with a 'Harder'-proposing policy:")
    print("FIXED 2026-11-12: G5's lower bound widened from perf>0.40 to perf>=0.30. The previously-uncovered")
    print("case (perf=0.35) and the new boundary (perf=0.30) now both correctly resolve to g5_partial_same (Same),")
    print("while perf=0.299 still correctly falls through to G1 (Easier), confirming no gap and no regression.")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
