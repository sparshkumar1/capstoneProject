"""Authority matrix: who may read what, propose what, and write what.

The matrix is data, not prose: the coordinator enforces it and `render_matrix_markdown()` generates the
table used in documentation, so the paper's Table 1 is derived from the code that enforces it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from agents.multiagent.contracts import COACHING, STRATEGY

# Keys no agent may ever emit, in any message. Seeing one is an *authority violation* (distinct from a schema error).
FORBIDDEN_KEYS = frozenset(
    {
        "score", "final_score", "raw_score", "validated_score", "scores", "grade",
        "terminate", "end_session", "session_end", "state", "state_patch", "write", "delete",
        "answers", "history", "difficulty",            # an agent proposes a difficulty *action*, never a level
        "evaluator_result", "eval_result",
    }
)


@dataclass(frozen=True)
class AuthoritySpec:
    agent: str
    reads: Tuple[str, ...]
    may_propose: Tuple[str, ...]
    state_writes: Tuple[str, ...]            # always empty: only the hub commits state
    keeps_private_state: str
    cannot: Tuple[str, ...]
    validation: Tuple[str, ...]
    escalation: str


AUTHORITY: Dict[str, AuthoritySpec] = {
    STRATEGY: AuthoritySpec(
        agent=STRATEGY,
        reads=("TurnObservation (score, evidence lists, difficulty, history, progress, budget, PPO action)",),
        may_propose=("difficulty_action (Easier/Same/Harder)", "probe request (concept, kind)", "strategy mode"),
        state_writes=(),
        keeps_private_state="weakness ledger (per-concept miss counts, probe history, trend)",
        cannot=(
            "write or overwrite any score", "set a difficulty level directly", "terminate the session",
            "edit history", "override hard constraints or guardrail overrides", "call another agent",
        ),
        validation=("schema", "authority keys", "state_version", "confidence >= tau", "evidence present"),
        escalation="invalid / stale / low-confidence / timed-out proposal is dropped; PPO proposal stands",
    ),
    COACHING: AuthoritySpec(
        agent=COACHING,
        reads=("TurnObservation (score, evidence lists, difficulty, history)", "own coaching history"),
        may_propose=("feedback depth", "hint / example flags", "concepts to emphasise", "remediation tag", "tone"),
        state_writes=(),
        keeps_private_state="coaching history (hints/examples given, repeated misconceptions)",
        cannot=(
            "alter evaluator results or scores", "cite concepts absent from the evaluator evidence",
            "request difficulty changes", "request follow-ups", "terminate the session",
        ),
        validation=("schema", "authority keys", "state_version", "grounding check on emphasised concepts"),
        escalation="invalid plan is dropped; the existing template feedback is used unchanged",
    ),
}


def authority_violation(raw: Any) -> Optional[str]:
    """Return the first forbidden key present at any depth of a raw agent output, else None."""
    stack = [raw]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for k, v in cur.items():
                if str(k).lower() in FORBIDDEN_KEYS:
                    return str(k)
                stack.append(v)
        elif isinstance(cur, (list, tuple)):
            stack.extend(cur)
    return None


def render_matrix_markdown() -> str:
    rows = ["| Agent | Reads | May propose | State writes | Private state | Cannot | Validation | On failure |",
            "|---|---|---|---|---|---|---|---|"]
    for a in AUTHORITY.values():
        rows.append(
            "| {} | {} | {} | none | {} | {} | {} | {} |".format(
                a.agent, "; ".join(a.reads), "; ".join(a.may_propose), a.keeps_private_state,
                "; ".join(a.cannot), ", ".join(a.validation), a.escalation,
            )
        )
    return "\n".join(rows)
