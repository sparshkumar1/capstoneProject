"""Interview Strategy Agent (rule- and ledger-based; NOT an LLM agent).

Objective: keep the candidate in productive difficulty while resolving *persistent* weaknesses within the follow-up budget.
What it adds over the per-turn threshold rules and the PPO policy (whose 6-D state has no concept memory):
a private weakness ledger across turns. It proposes; the arbitrator and the hub decide.

Private state (persists across turns, exported/imported for session recovery):
  miss_turns   concept -> distinct turns in which the evaluator listed it as missing/incorrect
  resolved     concepts covered after their last miss
  probes       concept -> follow-up probes already requested
  ema          exponential moving average of scores (alpha 0.5)

Decision rules (first match wins; thresholds are constructor parameters recorded in the experiment config):
  recover    last two scores mean < 0.5 and current < recover_score, or a persistent weakness survived max_probes probes
             while the score stays < 0.5                                         -> Easier (+ no probe)
  remediate  a concept missed on >= persistent_after distinct turns and not resolved -> Same + probe that concept
  stretch    current >= stretch_score, ema >= stretch_ema, the last 3 scores all >= 0.6, no open weakness -> Harder
  steady     otherwise                                                            -> Same, confidence 0.45 (below the default tau,
                                                                                     so the PPO action stands)
Confidence = min(0.95, 0.5 + 0.1 * number of evidence items cited). It is a documented heuristic, not a calibrated probability.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from agents.multiagent.contracts import Evidence, ProbeRequest, StrategyProposal, TurnObservation
from agents.multiagent.grounding import normalize_concept


def _ev(ref: str, value: str = "") -> Evidence:
    return Evidence(ref=ref, value=str(value)[:200])


def _conf(n_evidence: int) -> float:
    return round(min(0.95, 0.5 + 0.1 * n_evidence), 2)


class StrategyAgent:
    name = "strategy"

    def __init__(self, persistent_after: int = 2, max_probes: int = 2, stretch_score: float = 0.8,
                 stretch_ema: float = 0.7, recover_score: float = 0.35):
        self.persistent_after = persistent_after
        self.max_probes = max_probes
        self.stretch_score = stretch_score
        self.stretch_ema = stretch_ema
        self.recover_score = recover_score
        self.miss_turns: Dict[str, Set[int]] = {}
        self.display: Dict[str, str] = {}
        self.resolved: Set[str] = set()
        self.probes: Dict[str, int] = {}
        self.ema: Optional[float] = None
        self._seen_turns: Set[int] = set()

    # -- persistence (session recovery) --------------------------------------------------------------
    def export_state(self) -> Dict[str, Any]:
        return {
            "miss_turns": {k: sorted(v) for k, v in self.miss_turns.items()}, "display": dict(self.display),
            "resolved": sorted(self.resolved), "probes": dict(self.probes), "ema": self.ema,
            "seen_turns": sorted(self._seen_turns),
        }

    def import_state(self, st: Dict[str, Any]) -> None:
        self.miss_turns = {k: set(v) for k, v in st.get("miss_turns", {}).items()}
        self.display = dict(st.get("display", {}))
        self.resolved = set(st.get("resolved", []))
        self.probes = dict(st.get("probes", {}))
        self.ema = st.get("ema")
        self._seen_turns = set(st.get("seen_turns", []))

    # -- ledger --------------------------------------------------------------------------------------
    def _observe(self, obs: TurnObservation) -> None:
        if obs.turn_id in self._seen_turns:
            return
        self._seen_turns.add(obs.turn_id)
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

    def open_weaknesses(self) -> List[str]:
        """Persistent, unresolved concepts, most-missed first (ties broken alphabetically for determinism)."""
        keys = [k for k, t in self.miss_turns.items() if len(t) >= self.persistent_after and k not in self.resolved]
        return sorted(keys, key=lambda k: (-len(self.miss_turns[k]), k))

    # -- decision ------------------------------------------------------------------------------------
    def propose(self, obs: TurnObservation, peer: Any = None) -> StrategyProposal:
        self._observe(obs)
        recent = (*obs.scores_history[-2:], obs.score)
        ev: List[Evidence] = [_ev(ref="score", value=f"{obs.score:.2f}")]
        open_w = self.open_weaknesses()
        base = dict(session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version)

        mean_last2 = sum(recent[-2:]) / len(recent[-2:])

        # recover: struggling now, or a weakness survived its probes
        exhausted = [k for k in open_w if self.probes.get(k, 0) >= self.max_probes]
        if obs.difficulty > 1 and ((obs.score < self.recover_score and len(recent) >= 2 and mean_last2 < 0.5)
                                   or (exhausted and obs.score < 0.5)):
            ev.append(_ev(ref="scores_history", value=",".join(f"{s:.2f}" for s in recent)))
            if exhausted:
                k = exhausted[0]
                ev.append(_ev(ref="missing_concepts", value=self.display.get(k, k)))
            return StrategyProposal(**base, difficulty_action="Easier", mode="recover", confidence=_conf(len(ev)),
                                    rationale="sustained low scores or a weakness that survived its probes", evidence=tuple(ev))

        # remediate: hold difficulty and probe the persistent weakness
        probe_targets = [k for k in open_w if self.probes.get(k, 0) < self.max_probes and len(self.display.get(k, k)) <= 400]
        if probe_targets and obs.consecutive_followups < 2:
            k = probe_targets[0]
            ev.append(_ev(ref="missing_concepts", value=self.display.get(k, k)))
            ev.append(_ev(ref="miss_turns", value=str(len(self.miss_turns[k]))))
            self.probes[k] = self.probes.get(k, 0) + 1          # the request is part of the agent's own plan
            return StrategyProposal(
                **base, difficulty_action="Same", mode="remediate", confidence=_conf(len(ev)),
                probe=ProbeRequest(concept=self.display.get(k, k), kind="persistent_weakness"),
                rationale=f"concept missed on {len(self.miss_turns[k])} turns and unresolved", evidence=tuple(ev))

        # stretch: strong, consistent, no open weakness
        if (obs.difficulty < 5 and not open_w and obs.score >= self.stretch_score and (self.ema or 0.0) >= self.stretch_ema
                and len(recent) >= 3 and all(s >= 0.6 for s in recent)):
            ev.append(_ev(ref="scores_history", value=",".join(f"{s:.2f}" for s in recent)))
            ev.append(_ev(ref="ema", value=f"{self.ema:.2f}"))
            return StrategyProposal(**base, difficulty_action="Harder", mode="stretch", confidence=_conf(len(ev)),
                                    rationale="consistently strong with no open weakness", evidence=tuple(ev))

        return StrategyProposal(**base, difficulty_action="Same", mode="steady", confidence=0.45,
                                rationale="no ledger evidence for a change", evidence=tuple(ev))
