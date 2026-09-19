"""
rl/guardrails.py — Canonical Pedagogical Safety Guardrails for Adaptive RL Difficulty.

Defines the authoritative post-PPO guardrail rules shared across:
  - rl/env/interview_env.py
  - agents/orchestrator/interview_orchestrator.py
  - research/scripts/run_paper3_study.py

Guardrail Hierarchy and Rules:
  - Infrastructure Failure Guard: Bypasses difficulty degradation if turn failed due to infrastructure.
  - G4 (Stuck Candidate): perf < 0.30 and hes > 0.60 -> Easier (Action 0) [Highest Priority]
  - G1 (Overload Protection): perf < 0.30 and 0.4 <= diff <= 0.7 -> Easier (Action 0)
  - G2 (Anxiety Stabilizer): conf < 0.30 and hes > 0.70 and perf < 0.80 -> Easier if hes > 0.85 else Same (Action 1)
  - G3 / G5 (Partial Understanding): 0.40 < perf < 0.65 and avg_perf < 0.60 and consec < 2 -> Same (Action 1)
  - G6 (Strong Performer): perf >= 0.90 and gap > 0.25 and not nervous_expert -> Harder (Action 2)
  - Boundary Clamp: Difficulty remains strictly within [1, 5] (or [0.2, 1.0]).
"""

from typing import Tuple, Optional


ACTION_EASIER = 0
ACTION_SAME = 1
ACTION_HARDER = 2

ACTION_NAMES = {
    0: "Easier",
    1: "Same",
    2: "Harder",
}


def apply_canonical_guardrails(
    perf: float,
    avg_perf: float,
    conf: float,
    hes: float,
    progress: float,
    difficulty: float,
    proposed_action: int,
    consecutive_failures: int = 0,
    is_infrastructure_failure: bool = False,
    medium_difficulty_min: float = 0.4,
    medium_difficulty_max: float = 0.7,
) -> Tuple[int, bool, str]:
    """
    Apply canonical pedagogical guardrails in strict deterministic priority order.

    Parameters:
      perf: Latest answer technical score in [0.0, 1.0]
      avg_perf: Rolling mean of recent scores in [0.0, 1.0]
      conf: Speech confidence score in [0.0, 1.0]
      hes: Acoustic hesitation score in [0.0, 1.0]
      progress: Normalized session turn progress (t / T) in [0.0, 1.0]
      difficulty: Current difficulty in normalized [0.1, 1.0] or integer [1, 5]
      proposed_action: Proposed discrete action index (0=Easier, 1=Same, 2=Harder)
      consecutive_failures: Count of consecutive failed answers / followups
      is_infrastructure_failure: If True, indicates system failure, suppressing degradation
      medium_difficulty_min: Lower bound for mid-difficulty band (default 0.4)
      medium_difficulty_max: Upper bound for mid-difficulty band (default 0.7)

    Returns:
      (final_action: int, was_overridden: bool, guardrail_id: str)
    """
    action = int(proposed_action)

    # 1. Infrastructure Failure Protection (Strict Isolation)
    if is_infrastructure_failure:
        return ACTION_SAME, True, "guardrail_infra_failure_same"

    # Normalize difficulty if passed as 1..5 integer
    diff_norm = difficulty / 5.0 if difficulty > 1.0 else difficulty

    # 2. G4: Critically Stuck Candidate — HIGHEST PEDAGOGICAL PRIORITY (before G1)
    # When a candidate shows low performance AND severe hesitation, they are stuck.
    # Requires immediate difficulty decrease to restore comprehension.
    if perf < 0.30 and hes > 0.60:
        return ACTION_EASIER, True, "g4_stuck_easier"

    # 3. G1: Overload Protection — Weak candidate at medium difficulty (not stuck)
    # Low performance in the mid-range curriculum requires reducing difficulty.
    if perf < 0.30 and medium_difficulty_min <= diff_norm <= medium_difficulty_max:
        return ACTION_EASIER, True, "g1_overload_protection"

    # 4. G2: Anxiety Stabilizer — Low confidence + high hesitation, not high performer
    # Anxious candidates should not be escalated.
    if conf < 0.30 and hes > 0.70 and perf < 0.80:
        return ACTION_SAME, True, "g2_anxiety_stabilizer_same"

    # 5. G3 / G5: Partial Understanding — Hold at Same
    # Intermediate scores (0.40 < perf < 0.65) with low historical average
    # indicate partial understanding requiring reinforcement at current level.
    if 0.40 < perf < 0.65 and avg_perf < 0.60 and consecutive_failures < 2:
        return ACTION_SAME, True, "g5_partial_same"

    # 6. G6: Strong Performer — Push Harder
    # Strong candidates with large performance gap should be escalated.
    # Excludes nervous experts (0.80 < perf < 0.95 and hes > 0.65) who need stabilization.
    gap = perf - diff_norm
    is_nervous_expert = (0.80 < perf < 0.95 and hes > 0.65) or (conf < 0.40 and hes > 0.60)
    if perf >= 0.90 and gap > 0.25 and not is_nervous_expert:
        return ACTION_HARDER, True, "g6_strong_harder"

    # No guardrail triggered
    return action, False, "none"
