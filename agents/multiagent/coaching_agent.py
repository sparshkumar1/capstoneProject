"""Coaching Agent (rule- and history-based; NOT an LLM agent).

Objective: choose *how* to coach after an evaluated answer so that repeated explanations are not repeated verbatim and the
depth matches the candidate's situation. It never changes what the evaluator found; it chooses presentation and emphasis from
that evidence. Output is a `CoachingPlan` rendered by `coaching_render.apply_coaching_plan` (additive feedback fields only).

Private state (persists across turns):
  concept_misses   concept -> number of turns the concept was missing/incorrect
  hints_given      concept -> hints already given for it
  examples_given   concept -> examples already given for it
  last_depth       depth used on the previous coached turn

Decisions:
  emphasise   up to 2 concepts from this turn's evidence: incorrect claims first, then concepts with the most prior misses, then evaluator order
  hint        yes if concepts are missing, score < 0.6, and the lead concept has had < 2 hints (no hint loops)
  example     yes if the lead concept has been missed on >= 2 turns and no example was given for it yet (the earlier explanation did not land)
  depth       detailed if score < 0.4 or a repeated miss; brief if score >= 0.85 and nothing missing; else standard
  tone        encouraging if score < 0.4, or hesitation > 0.6, or confidence < 0.35; else neutral
  peer        a Strategy proposal (if delivered by the coordinator) modifies the plan: mode 'recover' -> detailed + encouraging,
              'stretch' -> brief, 'remediate' -> remediation tag on the probed concept
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from agents.multiagent.contracts import CoachingPlan, Evidence, TurnObservation
from agents.multiagent.grounding import normalize_concept


def _ev(ref: str, value: str = "") -> Evidence:
    return Evidence(ref=ref, value=str(value)[:200])


def _conf(n: int) -> float:
    return round(min(0.95, 0.5 + 0.1 * n), 2)


class CoachingAgent:
    name = "coaching"

    def __init__(self) -> None:
        self.concept_misses: Dict[str, int] = {}
        self.hints_given: Dict[str, int] = {}
        self.examples_given: Dict[str, int] = {}
        self.last_depth: Optional[str] = None
        self._seen_turns: set = set()

    def export_state(self) -> Dict[str, Any]:
        return {"concept_misses": dict(self.concept_misses), "hints_given": dict(self.hints_given),
                "examples_given": dict(self.examples_given), "last_depth": self.last_depth,
                "seen_turns": sorted(self._seen_turns)}

    def import_state(self, st: Dict[str, Any]) -> None:
        self.concept_misses = dict(st.get("concept_misses", {}))
        self.hints_given = dict(st.get("hints_given", {}))
        self.examples_given = dict(st.get("examples_given", {}))
        self.last_depth = st.get("last_depth")
        self._seen_turns = set(st.get("seen_turns", []))

    def propose(self, obs: TurnObservation, peer: Any = None) -> CoachingPlan:
        first_visit = obs.turn_id not in self._seen_turns
        self._seen_turns.add(obs.turn_id)
        flagged = [(c, 0) for c in obs.incorrect_claims] + [(c, 1) for c in obs.missing_concepts]
        # prior misses are read BEFORE this turn is added, so "repeated" means "also missed earlier"
        prior = {normalize_concept(c): self.concept_misses.get(normalize_concept(c), 0) for c, _ in flagged}
        ordered = sorted(enumerate(flagged), key=lambda ix: (ix[1][1], -prior[normalize_concept(ix[1][0])], ix[0]))
        emphasize = tuple(c for c in dict.fromkeys(str(c) for _, (c, _k) in ordered) if len(c) <= 400)[:2]
        if first_visit:
            for c, _k in flagged:
                k = normalize_concept(c)
                self.concept_misses[k] = self.concept_misses.get(k, 0) + 1

        lead = normalize_concept(emphasize[0]) if emphasize else None
        repeated = bool(lead and prior.get(lead, 0) >= 1)
        evidence: List[Evidence] = [_ev(ref="score", value=f"{obs.score:.2f}")]
        if emphasize:
            evidence.append(_ev(ref="missing_concepts" if emphasize[0] in obs.missing_concepts else "incorrect_claims",
                                     value=emphasize[0]))
        if repeated:
            evidence.append(_ev(ref="prior_misses", value=str(prior[lead])))

        hint = bool(obs.missing_concepts) and obs.score < 0.6 and lead is not None and self.hints_given.get(lead, 0) < 2
        example = bool(lead) and prior.get(lead, 0) >= 1 and self.examples_given.get(lead, 0) < 1
        if obs.score < 0.4 or repeated:
            depth = "detailed"
        elif obs.score >= 0.85 and not obs.missing_concepts and not obs.incorrect_claims:
            depth = "brief"
        else:
            depth = "standard"
        tone = "encouraging" if (obs.score < 0.4 or obs.hesitation > 0.6 or obs.confidence < 0.35) else "neutral"
        remediation = f"revisit:{emphasize[0]}" if repeated else None

        mode = getattr(peer, "mode", None)
        if mode == "recover":
            depth, tone = "detailed", "encouraging"
            evidence.append(_ev(ref="peer.mode", value="recover"))
        elif mode == "stretch" and depth == "standard":
            depth = "brief"
            evidence.append(_ev(ref="peer.mode", value="stretch"))
        elif mode == "remediate" and getattr(peer, "probe", None) is not None and remediation is None:
            remediation = f"revisit:{peer.probe.concept}"
            evidence.append(_ev(ref="peer.mode", value="remediate"))

        if first_visit:
            if hint and lead:
                self.hints_given[lead] = self.hints_given.get(lead, 0) + 1
            if example and lead:
                self.examples_given[lead] = self.examples_given.get(lead, 0) + 1
            self.last_depth = depth

        return CoachingPlan(
            session_id=obs.session_id, turn_id=obs.turn_id, state_version=obs.state_version, depth=depth,
            give_hint=hint, give_example=example, emphasize=emphasize, remediation=remediation, tone=tone,
            confidence=_conf(len(evidence)), rationale=f"depth={depth}, repeated={repeated}", evidence=tuple(evidence))
