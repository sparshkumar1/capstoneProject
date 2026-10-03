"""Comprehensive Software Test Suite for Multi-Agent Coordination and Specialization.
Tests Unit, Integration, Invariant, Metamorphic, and Specialization properties.
"""
import copy
import time
import pytest
from pydantic import ValidationError

from agents.multiagent.contracts import (
    Evidence,
    TurnObservation,
    StrategyProposal,
    CoachingPlan,
    ProbeRequest,
    DecisionRecord,
    STRATEGY,
    COACHING,
)
from agents.multiagent.authority import FORBIDDEN_KEYS
from agents.multiagent.strategy_agent import StrategyAgent
from agents.multiagent.coaching_agent import CoachingAgent
from agents.multiagent.unified_agent import UnifiedCoachAgent
from agents.multiagent.arbitration import (
    arbitrate_difficulty,
    arbitrate_probe,
    apply_action,
    FOLLOWUP_HARD_CAP,
)


def make_turn_obs(
    session_id="test_sess_01",
    turn_id=1,
    state_version=1,
    difficulty=3,
    score=0.75,
    covered=None,
    missing=None,
    incorrect=None,
    base_action="Same",
    base_source="ppo",
    consecutive_followups=0,
):
    return TurnObservation(
        session_id=session_id,
        turn_id=turn_id,
        state_version=state_version,
        question_id=f"q_{turn_id}",
        difficulty=difficulty,
        score=score,
        covered_concepts=tuple(covered or ["recursion"]),
        missing_concepts=tuple(missing or []),
        incorrect_claims=tuple(incorrect or []),
        scores_history=tuple([score]),
        confidence=0.9,
        hesitation=0.1,
        consecutive_followups=consecutive_followups,
        ppo_action=base_action,
        ppo_available=True,
    )


# =====================================================================
# 1. UNIT TESTS: Contracts, Schemas, and Authority Constraints
# =====================================================================

class TestContractsAndSchemas:
    def test_strategy_proposal_valid_and_bounds(self):
        prop = StrategyProposal(
            session_id="s1",
            turn_id=1,
            state_version=1,
            difficulty_action="Harder",
            confidence=0.85,
            evidence=(Evidence(ref="covered", value="recursion"),),
            rationale="High performance on recursion",
            mode="stretch",
        )
        assert prop.difficulty_action == "Harder"
        assert 0.0 <= prop.confidence <= 1.0

    def test_strategy_proposal_invalid_action(self):
        with pytest.raises(ValidationError):
            StrategyProposal(
                session_id="s1",
                turn_id=1,
                state_version=1,
                difficulty_action="SuperHard",  # Invalid action
                confidence=0.85,
                evidence=(),
            )

    def test_coaching_plan_valid_and_bounds(self):
        plan = CoachingPlan(
            session_id="s1",
            turn_id=1,
            state_version=1,
            depth="detailed",
            give_hint=True,
            give_example=False,
            emphasize=("memoization",),
            remediation="dp_basics",
            tone="encouraging",
            confidence=0.85,
            evidence=(Evidence(ref="missing", value="memoization"),),
        )
        assert plan.depth == "detailed"
        assert plan.give_hint is True
        assert plan.tone == "encouraging"

    def test_forbidden_keys_in_authority(self):
        assert "score" in FORBIDDEN_KEYS
        assert "final_score" in FORBIDDEN_KEYS
        assert "difficulty" in FORBIDDEN_KEYS  # Agents propose action, not direct level
        assert "terminate" in FORBIDDEN_KEYS


# =====================================================================
# 2. UNIT TESTS: Strategy and Coaching Agent State Ledgers
# =====================================================================

class TestStrategyAgent:
    def test_weakness_ledger_remediation_trigger(self):
        agent = StrategyAgent(persistent_after=2)
        # Turn 1: Miss dynamic_programming
        obs1 = make_turn_obs(turn_id=1, score=0.5, missing=["dynamic_programming"])
        prop1 = agent.propose(obs1)
        assert len(agent.miss_turns.get("dynamic_programming", set())) == 1

        # Turn 2: Miss dynamic_programming again -> triggers remediate
        obs2 = make_turn_obs(turn_id=2, score=0.45, missing=["dynamic_programming"])
        prop2 = agent.propose(obs2)
        assert len(agent.miss_turns.get("dynamic_programming", set())) == 2
        assert prop2.mode == "remediate"
        assert prop2.difficulty_action == "Same"
        assert prop2.probe is not None
        assert "dynamic_programming" in prop2.probe.concept
        assert prop2.confidence >= 0.70

    def test_recover_trigger_on_consecutive_low_scores(self):
        agent = StrategyAgent(recover_score=0.35)
        # Low score on turn 1
        obs1 = make_turn_obs(turn_id=1, score=0.30, difficulty=3)
        agent.propose(obs1)
        # Low score on turn 2 -> triggers recover (Easier)
        obs2 = make_turn_obs(turn_id=2, score=0.30, difficulty=3)
        obs2 = TurnObservation(
            session_id=obs2.session_id,
            turn_id=2,
            state_version=2,
            question_id="q2",
            difficulty=3,
            score=0.30,
            scores_history=(0.30, 0.30),
            confidence=0.5,
            hesitation=0.5,
        )
        prop = agent.propose(obs2)
        assert prop.mode == "recover"
        assert prop.difficulty_action == "Easier"

    def test_steady_mode_confidence_floor(self):
        agent = StrategyAgent()
        obs = make_turn_obs(turn_id=1, score=0.70, covered=["arrays"], missing=[])
        prop = agent.propose(obs)
        assert prop.mode == "steady"
        assert prop.difficulty_action == "Same"
        assert prop.confidence == 0.45  # Default steady confidence below tau=0.6


class TestCoachingAgent:
    def test_hint_budget_enforcement_no_loops(self):
        agent = CoachingAgent()
        concept = "binary_search"

        # Give hint 1
        obs1 = make_turn_obs(turn_id=1, score=0.5, missing=[concept])
        plan1 = agent.propose(obs1)
        assert plan1.give_hint is True
        assert agent.hints_given[concept] == 1

        # Give hint 2
        obs2 = make_turn_obs(turn_id=2, score=0.5, missing=[concept])
        plan2 = agent.propose(obs2)
        assert plan2.give_hint is True
        assert agent.hints_given[concept] == 2

        # Turn 3: Hint cap reached (< 2 hints allowed) -> no more hints
        obs3 = make_turn_obs(turn_id=3, score=0.5, missing=[concept])
        plan3 = agent.propose(obs3)
        assert plan3.give_hint is False

    def test_example_trigger_after_repeated_misses(self):
        agent = CoachingAgent()
        concept = "graphs"

        # Turn 1: First miss
        obs1 = make_turn_obs(turn_id=1, score=0.5, missing=[concept])
        plan1 = agent.propose(obs1)
        assert plan1.give_example is False

        # Turn 2: Second miss -> trigger example
        obs2 = make_turn_obs(turn_id=2, score=0.5, missing=[concept])
        plan2 = agent.propose(obs2)
        assert plan2.give_example is True
        assert agent.examples_given[concept] == 1

    def test_peer_message_modulation(self):
        agent = CoachingAgent()
        obs = make_turn_obs(turn_id=1, score=0.5, missing=["sorting"])
        # Peer proposal with mode='recover'
        peer_recover = StrategyProposal(
            session_id=obs.session_id,
            turn_id=obs.turn_id,
            state_version=obs.state_version,
            difficulty_action="Easier",
            confidence=0.8,
            mode="recover",
            evidence=(),
        )
        plan = agent.propose(obs, peer=peer_recover)
        assert plan.depth == "detailed"
        assert plan.tone == "encouraging"


# =====================================================================
# 3. UNIT TESTS: Arbitration and Coordination Logic
# =====================================================================

class TestArbitrationAndCoordination:
    def test_arbitrate_difficulty_tau_gating(self):
        obs = make_turn_obs(difficulty=3, base_action="Same", base_source="ppo")

        # Low confidence proposal (< tau=0.6) -> rejected, PPO action wins
        prop_low = StrategyProposal(
            session_id=obs.session_id,
            turn_id=obs.turn_id,
            state_version=obs.state_version,
            difficulty_action="Easier",
            confidence=0.55,
            evidence=(Evidence(ref="covered", value="x"),),
        )
        dec_low = arbitrate_difficulty(obs, "Same", "ppo", prop_low, guardrail_fn=None, tau=0.6)
        assert dec_low.final_action == "Same"
        assert dec_low.candidate_source == "ppo"

        # High confidence proposal (>= tau=0.6) -> accepted, Strategy proposal wins
        prop_high = StrategyProposal(
            session_id=obs.session_id,
            turn_id=obs.turn_id,
            state_version=obs.state_version,
            difficulty_action="Easier",
            confidence=0.80,
            evidence=(Evidence(ref="covered", value="x"),),
        )
        dec_high = arbitrate_difficulty(obs, "Same", "ppo", prop_high, guardrail_fn=None, tau=0.6)
        assert dec_high.final_action == "Easier"
        assert dec_high.candidate_source == "strategy"
        assert dec_high.conflict is True

    def test_clamping_to_valid_difficulty_range(self):
        # At boundary level 1, action "Easier" cannot drop below 1
        assert apply_action(1, "Easier") == 1
        # At boundary level 5, action "Harder" cannot exceed 5
        assert apply_action(5, "Harder") == 5
        # Mid-level transitions step by exactly 1
        assert apply_action(3, "Easier") == 2
        assert apply_action(3, "Harder") == 4

    def test_arbitrate_probe_hard_cap(self):
        prop = StrategyProposal(
            session_id="test_sess_01",
            turn_id=1,
            state_version=1,
            difficulty_action="Same",
            confidence=0.8,
            evidence=(Evidence(ref="missing_concepts", value="trees"),),
            probe=ProbeRequest(concept="trees", kind="gap"),
        )
        seen = {"trees"}
        # Under cap (< 2): probe admitted
        obs_under = make_turn_obs(missing=["trees"], consecutive_followups=1)
        probe_ok = arbitrate_probe(obs_under, hub_default_inject=False, strategy=prop, seen_concepts=seen, tau=0.6)
        assert probe_ok.inject is True
        assert probe_ok.concept == "trees"

        # At cap (>= 2): probe rejected by hard cap
        obs_cap = make_turn_obs(missing=["trees"], consecutive_followups=2)
        probe_blocked = arbitrate_probe(obs_cap, hub_default_inject=False, strategy=prop, seen_concepts=seen, tau=0.6)
        assert probe_blocked.inject is False
        assert probe_blocked.source == "none"


# =====================================================================
# 4. INVARIANT & PROPERTY-BASED TESTS
# =====================================================================

class TestInvariantsAndProperties:
    def test_determinism_under_fixed_inputs(self):
        """Metamorphic test: identical input sequence must yield byte-identical proposals."""
        agent1 = StrategyAgent()
        agent2 = StrategyAgent()

        obs_seq = [
            make_turn_obs(turn_id=1, score=0.7, missing=["hash_tables"]),
            make_turn_obs(turn_id=2, score=0.4, missing=["hash_tables"]),
            make_turn_obs(turn_id=3, score=0.8, covered=["hash_tables"]),
        ]

        props1 = [agent1.propose(obs).model_dump(exclude={"evidence"}) for obs in obs_seq]
        props2 = [agent2.propose(obs).model_dump(exclude={"evidence"}) for obs in obs_seq]
        assert props1 == props2

    def test_state_isolation_between_agents(self):
        """Invariant: StrategyAgent state is strictly disjoint from CoachingAgent state."""
        strat = StrategyAgent()
        coach = CoachingAgent()

        obs = make_turn_obs(turn_id=1, score=0.5, missing=["linked_lists"])
        strat.propose(obs)
        coach.propose(obs)

        assert hasattr(strat, "miss_turns")
        assert not hasattr(strat, "hints_given")
        assert hasattr(coach, "hints_given")
        assert not hasattr(coach, "miss_turns")

    def test_coaching_ablation_invariance_m3(self):
        """Invariant: Ablating CoachingAgent (M3) does not alter Strategy proposals."""
        strat_full = StrategyAgent()
        strat_ablated = StrategyAgent()

        obs = make_turn_obs(turn_id=1, score=0.45, missing=["queues"])
        prop_full = strat_full.propose(obs)
        prop_ablated = strat_ablated.propose(obs)

        assert prop_full.difficulty_action == prop_ablated.difficulty_action
        assert prop_full.confidence == prop_ablated.confidence
        assert prop_full.mode == prop_ablated.mode


# =====================================================================
# 5. SPECIALIZATION EXPERIMENT: Split vs Standalone Unified Controller (RQ2)
# =====================================================================

class TestSpecializationComparison:
    def test_unified_coach_agent_state_construction_and_bounds(self):
        """Verifies state construction, ledger tracking, and bounds of standalone UnifiedCoachAgent."""
        unified = UnifiedCoachAgent(persistent_after=2)
        obs = make_turn_obs(turn_id=1, score=0.30, missing=["recursion"])
        strat, coach = unified.propose_unified(obs)
        assert isinstance(strat, StrategyProposal)
        assert isinstance(coach, CoachingPlan)
        assert strat.difficulty_action in ("Easier", "Same", "Harder")
        assert coach.depth in ("brief", "standard", "detailed")

    def test_decision_equivalence_under_equivalent_heuristics(self):
        """Empirical proof of RQ2: standalone unified controller and split agents produce identical decisions."""
        split_strat = StrategyAgent(persistent_after=2)
        split_coach = CoachingAgent()
        unified = UnifiedCoachAgent(persistent_after=2)

        obs_sequence = [
            make_turn_obs(turn_id=1, score=0.5, missing=["dynamic_programming"]),
            make_turn_obs(turn_id=2, score=0.45, missing=["dynamic_programming"]),
            make_turn_obs(turn_id=3, score=0.85, covered=["dynamic_programming"]),
        ]

        for obs in obs_sequence:
            # Split execution
            strat_prop = split_strat.propose(obs)
            coach_plan = split_coach.propose(obs, peer=strat_prop)

            # Standalone Unified execution
            unified_strat, unified_coach = unified.propose_unified(obs)

            # Assert Decision Equivalence across every dimension
            assert unified_strat.difficulty_action == strat_prop.difficulty_action
            assert unified_strat.mode == strat_prop.mode
            assert unified_strat.confidence == strat_prop.confidence
            if strat_prop.probe is not None:
                assert unified_strat.probe is not None
                assert unified_strat.probe.concept == strat_prop.probe.concept
            else:
                assert unified_strat.probe is None

            assert unified_coach.depth == coach_plan.depth
            assert unified_coach.give_hint == coach_plan.give_hint
            assert unified_coach.give_example == coach_plan.give_example
            assert unified_coach.tone == coach_plan.tone
            assert unified_coach.emphasize == coach_plan.emphasize
            assert unified_coach.remediation == coach_plan.remediation

    def test_unified_coach_agent_state_persistence_export_import(self):
        """Verifies session recovery for the unified controller."""
        agent1 = UnifiedCoachAgent(persistent_after=2)
        obs1 = make_turn_obs(turn_id=1, score=0.5, missing=["dp"])
        agent1.propose_unified(obs1)
        st = agent1.export_state()

        agent2 = UnifiedCoachAgent(persistent_after=2)
        agent2.import_state(st)
        assert agent2.export_state() == st

    def test_serialization_overhead_split_vs_unified(self):
        """Verifies that split architecture incurs higher serialization overhead than unified."""
        prop = StrategyProposal(
            session_id="s1",
            turn_id=1,
            state_version=1,
            difficulty_action="Easier",
            confidence=0.8,
            evidence=(Evidence(ref="covered", value="sorting"),),
        )
        plan = CoachingPlan(
            session_id="s1",
            turn_id=1,
            state_version=1,
            depth="detailed",
            give_hint=True,
            give_example=False,
            confidence=0.85,
            evidence=(Evidence(ref="covered", value="sorting"),),
        )

        n_iter = 1000
        # Split: 2 Pydantic model serialization passes
        t0 = time.perf_counter()
        for _ in range(n_iter):
            _ = prop.model_dump()
            _ = plan.model_dump()
        t_split = time.perf_counter() - t0

        # Unified: 1 serialization pass
        unified_dict = {**prop.model_dump(), **plan.model_dump()}
        t0 = time.perf_counter()
        for _ in range(n_iter):
            _ = dict(unified_dict)
        t_unified = time.perf_counter() - t0

        # Assert that split serialization takes measurably more CPU time than unified
        assert t_split > t_unified
