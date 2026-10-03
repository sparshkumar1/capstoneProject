"""Typed message contracts for the PREPAIred multi-agent layer.

Agents never receive the mutable session dict and never return state. They receive an immutable
`TurnObservation` and return a proposal (`StrategyProposal`, `CoachingPlan`). Everything is validated
before use; unknown fields are rejected (`extra="forbid"`), so an agent cannot smuggle a score or a
termination request through a free-form field.
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Literal, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field

DifficultyAction = Literal["Easier", "Same", "Harder"]
ACTIONS: Tuple[str, ...] = ("Easier", "Same", "Harder")

STRATEGY = "strategy"
COACHING = "coaching"
PPO = "ppo"
GUARDRAIL = "guardrail"
ARBITRATOR = "arbitrator"
COORDINATOR = "coordinator"

Confidence = Field(ge=0.0, le=1.0, allow_inf_nan=False)


class _Frozen(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Evidence(_Frozen):
    """Pointer into the observation that supports a decision (e.g. ref='missing_concepts', value='hash collisions')."""

    ref: str = Field(min_length=1, max_length=120)
    value: str = Field(default="", max_length=200)


class TurnObservation(_Frozen):
    """Immutable snapshot of one committed turn, built by the hub. The only thing agents may read."""

    session_id: str
    turn_id: int = Field(ge=0)
    state_version: int = Field(ge=0)
    question_id: str
    topic: str = ""
    difficulty: int = Field(ge=1, le=5)
    score: float = Field(ge=0.0, le=1.0, allow_inf_nan=False)
    covered_concepts: Tuple[str, ...] = ()
    missing_concepts: Tuple[str, ...] = ()
    incorrect_claims: Tuple[str, ...] = ()
    weakest_gap: str = ""
    is_followup: bool = False
    scores_history: Tuple[float, ...] = ()
    progress: float = Field(default=0.0, ge=0.0, le=1.0, allow_inf_nan=False)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, allow_inf_nan=False)
    hesitation: float = Field(default=0.5, ge=0.0, le=1.0, allow_inf_nan=False)
    primary_remaining: int = Field(default=0, ge=0)
    consecutive_followups: int = Field(default=0, ge=0)
    baseline_complete: bool = True
    infrastructure_failure: bool = False
    ppo_action: Optional[DifficultyAction] = None       # input proposal from the learned policy, if available
    ppo_available: bool = False


class ProbeRequest(_Frozen):
    concept: str = Field(min_length=1, max_length=400)    # evaluator claims can be sentence-length; never clipped (grounding compares the full string)
    kind: Literal["gap", "misconception", "persistent_weakness"]


class StrategyProposal(_Frozen):
    """What the Strategy Agent may ask for. It cannot carry a score, a termination, or a state write."""

    session_id: str
    turn_id: int = Field(ge=0)
    state_version: int = Field(ge=0)
    difficulty_action: DifficultyAction
    probe: Optional[ProbeRequest] = None
    mode: Literal["steady", "remediate", "stretch", "recover"] = "steady"
    confidence: float = Confidence
    rationale: str = Field(default="", max_length=300)
    evidence: Tuple[Evidence, ...] = Field(default=(), max_length=12)


class CoachingPlan(_Frozen):
    """What the Coaching Agent may ask for. It cannot alter the evaluator result."""

    session_id: str
    turn_id: int = Field(ge=0)
    state_version: int = Field(ge=0)
    depth: Literal["brief", "standard", "detailed"] = "standard"
    give_hint: bool = False
    give_example: bool = False
    emphasize: Tuple[str, ...] = Field(default=(), max_length=6)    # concepts, validated against evidence
    remediation: Optional[str] = Field(default=None, max_length=420)
    tone: Literal["neutral", "encouraging"] = "neutral"
    confidence: float = Confidence
    rationale: str = Field(default="", max_length=300)
    evidence: Tuple[Evidence, ...] = Field(default=(), max_length=12)


class AgentMessage(_Frozen):
    """Envelope recorded for every inter-component message (traceability)."""

    message_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    session_id: str
    turn_id: int
    sender: str
    recipient: str
    message_type: Literal["observation", "proposal", "decision"]
    state_version: int
    confidence: Optional[float] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)


class DecisionRecord(_Frozen):
    """One accept/reject/modify outcome with the reason; the unit the paper's tables are built from."""

    session_id: str
    turn_id: int
    state_version: int
    decision: Literal["difficulty", "probe", "coaching", "agent_call"]
    proposer: str
    proposed: str
    status: Literal["accepted", "rejected", "modified"]
    final: str = ""
    reason_code: str
    detail: str = ""
    latency_ms: Optional[float] = None
    created_at: float = Field(default_factory=time.time)
