"""
T-N02 — Frozen PPO checkpoint inference sanity check.

Read-only script. Loads the real, frozen, deployed checkpoint
(rl/checkpoints/seed_123/{ppo_final.zip,vecnormalize.pkl}) via the actual
production wrapper (agents.strategy.hybrid_orchestrator.HybridOrchestrator),
and calls its real .suggest() method on ~10 constructed candidate states
spanning strong/weak/boundary/nervous-expert-like profiles.

Does NOT train, does NOT modify the checkpoint, does NOT touch
rl/env/interview_env.py or any frozen artifact. Only imports and calls the
existing production code path exactly as the live orchestrator would.

Run: .venv/Scripts/python.exe testing_and_evaluation/rl_evaluation/T-N02_ppo_checkpoint_sanity_check.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from agents.strategy.hybrid_orchestrator import HybridOrchestrator  # noqa: E402

SCENARIOS = [
    # (label, score, current_difficulty, session_overrides)
    ("strong_candidate_mid_diff", 0.92, 3, {"rl_perf_history": [0.85, 0.88, 0.90, 0.91], "last_confidence_score": 0.9, "last_hesitation_score": 0.1}),
    ("weak_candidate_mid_diff", 0.20, 3, {"rl_perf_history": [0.25, 0.22, 0.18, 0.20], "last_confidence_score": 0.3, "last_hesitation_score": 0.8}),
    ("boundary_score_at_0.35", 0.35, 3, {"rl_perf_history": [0.35, 0.36, 0.34], "last_confidence_score": 0.5, "last_hesitation_score": 0.5}),
    ("boundary_score_at_0.80", 0.80, 3, {"rl_perf_history": [0.78, 0.79, 0.80], "last_confidence_score": 0.7, "last_hesitation_score": 0.3}),
    ("nervous_expert_high_score_low_conf", 0.88, 4, {"rl_perf_history": [0.85, 0.86, 0.88], "last_confidence_score": 0.25, "last_hesitation_score": 0.75}),
    ("min_difficulty_floor", 0.10, 1, {"rl_perf_history": [0.10, 0.12], "last_confidence_score": 0.2, "last_hesitation_score": 0.9}),
    ("max_difficulty_ceiling", 0.95, 5, {"rl_perf_history": [0.9, 0.93, 0.95], "last_confidence_score": 0.9, "last_hesitation_score": 0.1}),
    ("mid_session_average_candidate", 0.55, 3, {"rl_perf_history": [0.50, 0.55, 0.53, 0.58], "last_confidence_score": 0.5, "last_hesitation_score": 0.5}),
    ("declining_trend", 0.30, 2, {"rl_perf_history": [0.70, 0.55, 0.40, 0.30], "last_confidence_score": 0.4, "last_hesitation_score": 0.6}),
    ("improving_trend", 0.75, 2, {"rl_perf_history": [0.30, 0.45, 0.60, 0.75], "last_confidence_score": 0.7, "last_hesitation_score": 0.3}),
]

VALID_ACTIONS = {"Easier", "Same", "Harder"}


def main() -> int:
    orch = HybridOrchestrator()
    print(f"ready={orch.ready} is_compatible={orch.is_compatible} model_path={orch.model_path} vec_path={orch.vec_path}")

    if not orch.ready or not orch.is_compatible:
        print("WARNING: PPO checkpoint did not load / is not compatible — all suggestions below will use the heuristic fallback, not the real PPO policy.")

    failures = []
    for label, score, diff, overrides in SCENARIOS:
        session = {"baseline_complete": True, "scores": [], "rl_perf_history": []}
        session.update(overrides)
        try:
            new_diff, reason, action_name = orch.suggest(score, diff, session)
        except Exception as exc:
            failures.append((label, f"EXCEPTION: {exc}"))
            print(f"[FAIL] {label}: exception {exc}")
            continue

        source = session.get("rl_source")
        ok = action_name in VALID_ACTIONS and 1 <= new_diff <= 5
        status = "OK" if ok else "FAIL"
        if not ok:
            failures.append((label, f"invalid action={action_name!r} or difficulty={new_diff}"))
        print(f"[{status}] {label}: score={score:.2f} diff={diff} -> action={action_name} new_diff={new_diff} source={source} | {reason}")

    print()
    print(f"Scenarios run: {len(SCENARIOS)}  Failures: {len(failures)}")
    if failures:
        print("FAILURES:")
        for label, msg in failures:
            print(f"  - {label}: {msg}")
        return 1
    print("All scenarios produced a valid Discrete(3) action and difficulty in [1,5].")
    return 0


if __name__ == "__main__":
    sys.exit(main())
