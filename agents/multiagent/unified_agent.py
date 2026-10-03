"""Unified Technical-Coach Agent.

Implements a single, unified controller that combines both Strategy and Coaching responsibilities
into one architectural unit with joint state and internal variable passing.
Used as the genuine unified baseline (M_unified) to test Hypothesis 1 (Decision Equivalence)
and measure operational overhead against the specialized multi-agent architecture (M_split).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from agents.multiagent.contracts import (
    CoachingPlan,
    Evidence,
    ProbeRequest,
    StrategyProposal,
    TurnObservation,
)
from agents.multiagent.grounding import normalize_concept


def _ev(ref: str, value: str = "") -> Evidence:
    return Evidence(ref=ref, value=str(value)[:200])


def _conf(n_evidence: int) -> float:
    return round(min(0.95, 0.5 + 0.1 * n_evidence), 2)


class UnifiedCoachAgent:
    """Unified Controller combining Strategy and Coaching responsibilities.

    Receives the identical TurnObservation, maintains joint state across turns,
    and produces both Strategy and Coaching proposals via internal variable passing.
    """
    name = "unified_coach"

    def __init__(
        self,
        persistent_after: int = 2,
        max_probes: int = 2,
        stretch_score: float = 0.8,
        stretch_ema: float = 0.7,
        recover_score: float = 0.35,
    ):
        # Strategy configuration
        self.persistent_after = persistent_after
        self.max_probes = max_probes
        self.stretch_score = stretch_score
        self.stretch_ema = stretch_ema
        self.recover_score = recover_score

        # Joint State Ledgers
        # 1. Weakness Ledger (Strategy)
        self.miss_turns: Dict[str, Set[int]] = {}
        self.display: Dict[str, str] = {}
        self.resolved: Set[str] = set()
        self.probes: Dict[str, int] = {}
        self.ema: Optional[float] = None

        # 2. Coaching History Ledger (Coaching)
        self.concept_misses: Dict[str, int] = {}
        self.hints_given: Dict[str, int] = {}
        self.examples_given: Dict[str, int] = {}
        self.last_depth: Optional[str] = None

        # Shared visit tracking
        self._seen_turns: Set[int] = set()
        self._cached_proposals: Dict[int, Tuple[StrategyProposal, CoachingPlan]] = {}

    # ------------------------------------------------------------------ persistence
    def export_state(self) -> Dict[str, Any]:
        return {
            "miss_turns": {k: sorted(v) for k, v in self.miss_turns.items()},
            "display": dict(self.display),
            "resolved": sorted(self.resolved),
            "probes": dict(self.probes),
            "ema": self.ema,
            "concept_misses": dict(self.concept_misses),
            "hints_given": dict(self.hints_given),
            "examples_given": dict(self.examples_given),
            "last_depth": self.last_depth,
            "seen_turns": sorted(self._seen_turns),
        }

    def import_state(self, st: Dict[str, Any]) -> None:
        self.miss_turns = {k: set(v) for k, v in st.get("miss_turns", {}).items()}
        self.display = dict(st.get("display", {}))
        self.resolved = set(st.get("resolved", []))
        self.probes = dict(st.get("probes", {}))
        self.ema = st.get("ema")
        self.concept_misses = dict(st.get("concept_misses", {}))
        self.hints_given = dict(st.get("hints_given", {}))
        self.examples_given = dict(st.get("examples_given", {}))
        self.last_depth = st.get("last_depth")
        self._seen_turns = set(st.get("seen_turns", []))
        self._cached_proposals.clear()

    # ------------------------------------------------------------------ joint execution
    def open_weaknesses(self) -> List[str]:
        """Persistent, unresolved concepts, most-missed first (ties broken alphabetically for determinism)."""
        keys = [k for k, t in self.miss_turns.items() if len(t) >= self.persistent_after and k not in self.resolved]
        return sorted(keys, key=lambda k: (-len(self.miss_turns[k]), k))

    def propose_unified(self, obs: TurnObservation) -> Tuple[StrategyProposal, CoachingPlan]:
        """Executes unified pedagogical decision-making in a single joint pass."""
        if obs.turn_id in self._cached_proposals:
            return self._cached_proposals[obs.turn_id]

        first_visit = obs.turn_id not in self._seen_turns
        if first_visit:
            self._seen_turns.add(obs.turn_id)

        # 1. Update Strategy Weakness Ledger
        if first_visit:
            for c in (*obs.missing_concepts, *obs.incorrect_claims):
                k = normalize_concept(c)
                if not k:
                    continue
                self.display.setdefault(k, str(c))
                self.miss_turns.setdefault(k, set()).add(obs.turn_id)
                self.resolved.discard(k)
            for c in obs.covered_concepts:
                k = normalize_concept(c)
                if k in self.miss_turns:
                    self.resolved.add(k)
            self.ema = obs.score if self.ema is None else 0.5 * self.ema + 0.5 * obs.score

        # 2. Evaluate Strategy Decision Rules (identical to StrategyAgent)
        recent = (*obs.scores_history[-2:], obs.score)
        ev_strat: List[Evidence] = [_ev(ref="score", value=f"{obs.score:.2f}")]
        open_w = self.open_weaknesses()
        base_strat = dict(session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version)
        mean_last2 = sum(recent[-2:]) / len(recent[-2:])

        exhausted = [k for k in open_w if self.probes.get(k, 0) >= self.max_probes]
        if obs.difficulty > 1 and ((obs.score < self.recover_score and len(recent) >= 2 and mean_last2 < 0.5)
                                   or (exhausted and obs.score < 0.5)):
            ev_strat.append(_ev(ref="scores_history", value=",".join(f"{s:.2f}" for s in recent)))
            if exhausted:
                k = exhausted[0]
                ev_strat.append(_ev(ref="missing_concepts", value=self.display.get(k, k)))
            strat_proposal = StrategyProposal(
                **base_strat, difficulty_action="Easier", mode="recover", confidence=_conf(len(ev_strat)),
                rationale="sustained low scores or a weakness that survived its probes", evidence=tuple(ev_strat))
        elif [k for k in open_w if self.probes.get(k, 0) < self.max_probes and len(self.display.get(k, k)) <= 400] and obs.consecutive_followups < 2:
            probe_targets = [k for k in open_w if self.probes.get(k, 0) < self.max_probes and len(self.display.get(k, k)) <= 400]
            k = probe_targets[0]
            ev_strat.append(_ev(ref="missing_concepts", value=self.display.get(k, k)))
            ev_strat.append(_ev(ref="miss_turns", value=str(len(self.miss_turns[k]))))
            self.probes[k] = self.probes.get(k, 0) + 1
            strat_proposal = StrategyProposal(
                **base_strat, difficulty_action="Same", mode="remediate", confidence=_conf(len(ev_strat)),
                probe=ProbeRequest(concept=self.display.get(k, k), kind="persistent_weakness"),
                rationale=f"concept missed on {len(self.miss_turns[k])} turns and unresolved", evidence=tuple(ev_strat))
        elif (obs.difficulty < 5 and not open_w and obs.score >= self.stretch_score and (self.ema or 0.0) >= self.stretch_ema
                and len(recent) >= 3 and all(s >= 0.6 for s in recent)):
            ev_strat.append(_ev(ref="scores_history", value=",".join(f"{s:.2f}" for s in recent)))
            ev_strat.append(_ev(ref="ema", value=f"{self.ema:.2f}"))
            strat_proposal = StrategyProposal(
                **base_strat, difficulty_action="Harder", mode="stretch", confidence=_conf(len(ev_strat)),
                rationale="consistently strong with no open weakness", evidence=tuple(ev_strat))
        else:
            strat_proposal = StrategyProposal(
                **base_strat, difficulty_action="Same", mode="steady", confidence=0.45,
                rationale="normal progression", evidence=tuple(ev_strat), probe=None)

        # 3. Update Coaching Ledger & Evaluate Coaching Decisions (identical to CoachingAgent)
        flagged = [(c, 0) for c in obs.incorrect_claims] + [(c, 1) for c in obs.missing_concepts]
        prior = {normalize_concept(c): self.concept_misses.get(normalize_concept(c), 0) for c, _ in flagged}
        ordered = sorted(enumerate(flagged), key=lambda ix: (ix[1][1], -prior[normalize_concept(ix[1][0])], ix[0]))
        emphasize = tuple(c for c in dict.fromkeys(str(c) for _, (c, _k) in ordered) if len(c) <= 400)[:2]

        if first_visit:
            for c, _k in flagged:
                k = normalize_concept(c)
                self.concept_misses[k] = self.concept_misses.get(k, 0) + 1

        lead = normalize_concept(emphasize[0]) if emphasize else None
        repeated = bool(lead and prior.get(lead, 0) >= 1)

        coach_evs: List[Evidence] = [_ev(ref="score", value=f"{obs.score:.2f}")]
        if emphasize:
            coach_evs.append(_ev(ref="missing_concepts" if emphasize[0] in obs.missing_concepts else "incorrect_claims",
                                 value=emphasize[0]))
        if repeated:
            coach_evs.append(_ev(ref="prior_misses", value=str(prior[lead])))

        give_hint = bool(obs.missing_concepts) and obs.score < 0.6 and lead is not None and self.hints_given.get(lead, 0) < 2
        give_example = bool(lead) and prior.get(lead, 0) >= 1 and self.examples_given.get(lead, 0) < 1
        if obs.score < 0.4 or repeated:
            depth = "detailed"
        elif obs.score >= 0.85 and not obs.missing_concepts and not obs.incorrect_claims:
            depth = "brief"
        else:
            depth = "standard"
        tone = "encouraging" if (obs.score < 0.4 or obs.hesitation > 0.6 or obs.confidence < 0.35) else "neutral"
        remediation = f"revisit:{emphasize[0]}" if repeated else None

        # Internal variable passing: modulation by Strategy mode
        mode = strat_proposal.mode
        if mode == "recover":
            depth, tone = "detailed", "encouraging"
            coach_evs.append(_ev(ref="peer.mode", value="recover"))
        elif mode == "stretch" and depth == "standard":
            depth = "brief"
            coach_evs.append(_ev(ref="peer.mode", value="stretch"))
        elif mode == "remediate" and strat_proposal.probe is not None and remediation is None:
            remediation = f"revisit:{strat_proposal.probe.concept}"
            coach_evs.append(_ev(ref="peer.mode", value="remediate"))

        if first_visit:
            if give_hint and lead:
                self.hints_given[lead] = self.hints_given.get(lead, 0) + 1
            if give_example and lead:
                self.examples_given[lead] = self.examples_given.get(lead, 0) + 1
            self.last_depth = depth

        coach_plan = CoachingPlan(
            session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version,
            depth=depth, give_hint=give_hint, give_example=give_example,
            emphasize=emphasize, remediation=remediation, tone=tone,
            confidence=_conf(len(coach_evs)),
            rationale=f"depth={depth}, repeated={repeated}",
            evidence=tuple(coach_evs),
        )

        self._cached_proposals[obs.turn_id] = (strat_proposal, coach_plan)
        return strat_proposal, coach_plan

    def propose_strategy(self, obs: TurnObservation) -> StrategyProposal:
        """Compatibility accessor for Strategy Proposal."""
        s, _ = self.propose_unified(obs)
        return s

    def propose_coaching(self, obs: TurnObservation, peer: Any = None) -> CoachingPlan:
        """Compatibility accessor for Coaching Plan."""
        _, c = self.propose_unified(obs)
        return c
