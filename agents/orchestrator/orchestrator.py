import argparse
import os
import pickle
import random
import sys
from pathlib import Path

import numpy as np
from stable_baselines3 import PPO


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Evaluator.evaluate import evaluate, get_rubric  # noqa: E402
from qn_ans_selector.qn_ans_selector import (  # noqa: E402
    question_bank,
    reset_session_state,
    select_next_question,
    session_state,
)
from coding_executor.coding_executor import evaluate_code_submission  # noqa: E402
from timing_agent.timer import QuestionTimer  # noqa: E402
from validation_agent.score_validator import ScoreValidator, aggregate_scores  # noqa: E402
from orchestrator_agent.conceptual_critic import ConceptualCritic  # noqa: E402
from orchestrator_agent.logger import SessionLogger  # noqa: E402


class OrchestratorAgent:
    ACTION_MAP = {
        0: "Easier",
        1: "Same",
        2: "Harder",
        3: "Hint",
        4: "Follow-up",
    }

    def __init__(
        self,
        model_path: str = "rl_agent/rl_runs/seed_123/ppo_final.zip",
        vec_path: str = "rl_agent/rl_runs/seed_123/vecnormalize.pkl",
        max_turns: int = 10,
        baseline_turns: int = 3,
        code_timeout_sec: float = 2.0,
    ):
        self.model_path = os.path.join(PROJECT_ROOT, model_path)
        self.vec_path = os.path.join(PROJECT_ROOT, vec_path)
        self.max_turns = int(max_turns)
        self.baseline_turns = int(max(0, baseline_turns))
        self.code_timeout_sec = float(code_timeout_sec)

        self.current_difficulty = 0.5
        self.turn_count = 0
        self.history = []

        self.timer = QuestionTimer()
        self.validator = ScoreValidator()
        self.critic = ConceptualCritic(mode="deterministic")
        self.logger = SessionLogger()

        self._baseline_performance = []
        self._performance_history = []

        self._load_policy()
        self._load_normalization_stats()

    def _load_policy(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"PPO model not found at: {self.model_path}")
        self.policy = PPO.load(self.model_path)

    def _load_normalization_stats(self):
        if not os.path.exists(self.vec_path):
            self.obs_mean = np.zeros(6, dtype=np.float32)
            self.obs_var = np.ones(6, dtype=np.float32)
            return

        with open(self.vec_path, "rb") as fp:
            vecnormalize = pickle.load(fp)

        self.obs_mean = np.asarray(vecnormalize.obs_rms.mean, dtype=np.float32)
        self.obs_var = np.asarray(vecnormalize.obs_rms.var, dtype=np.float32)

    def _normalize_obs(self, obs: np.ndarray) -> np.ndarray:
        eps = 1e-8
        if obs.shape[0] != self.obs_mean.shape[0]:
            if obs.shape[0] < self.obs_mean.shape[0]:
                pad = self.obs_mean.shape[0] - obs.shape[0]
                obs = np.pad(obs, (0, pad), mode="edge")
            else:
                obs = obs[: self.obs_mean.shape[0]]
        normed = (obs - self.obs_mean) / np.sqrt(self.obs_var + eps)
        return np.clip(normed, -10.0, 10.0)

    def _behavior_from_text(self, text: str) -> tuple[float, float]:
        words = text.strip().split()
        wc = len(words)
        confidence = min(wc / 50.0, 1.0)

        filler_terms = [
            "um",
            "uh",
            "hmm",
            "maybe",
            "i think",
            "not sure",
            "i guess",
        ]
        lowered = text.lower()
        filler_hits = sum(lowered.count(token) for token in filler_terms)
        hesitation = min((filler_hits / max(wc, 1)) * 5.0, 1.0)

        confidence = max(min(confidence - 0.3 * hesitation, 1.0), 0.0)
        return round(confidence, 4), round(hesitation, 4)

    def _apply_action(self, action_name: str, question: dict):
        if action_name == "Easier":
            self.current_difficulty = max(0.1, self.current_difficulty - 0.1)
        elif action_name == "Harder":
            self.current_difficulty = min(1.0, self.current_difficulty + 0.1)
        elif action_name == "Hint":
            print("Hint:", question.get("hint", "Think about edge cases and complexity."))
        elif action_name == "Follow-up":
            print("Follow-up:", question.get("follow_up", "Explain your approach trade-offs and edge cases."))

    def _register_question_in_selector_state(self, question: dict):
        topic = question.get("topic")
        qid = question.get("qid")
        if topic is not None:
            session_state["topic_count"][topic] += 1
            session_state["previous_topic"] = topic
        if qid is not None:
            session_state["questions_asked"].add(qid)

    def _pick_baseline_questions(self) -> list[dict]:
        if self.baseline_turns <= 0:
            return []

        deduped = []
        seen = set()
        for q in question_bank:
            qid = q.get("qid")
            if qid in seen:
                continue
            seen.add(qid)
            deduped.append(q)

        easy_sorted = sorted(
            deduped,
            key=lambda q: (float(q.get("difficulty", 1.0)), q.get("qid", "")),
        )

        # Keep baseline difficulty controlled by sampling only from the easiest pool.
        easy_pool_size = min(len(easy_sorted), max(self.baseline_turns * 3, self.baseline_turns))
        easy_pool = easy_sorted[:easy_pool_size]

        if len(easy_pool) <= self.baseline_turns:
            return easy_pool

        return random.sample(easy_pool, k=self.baseline_turns)

    def _seed_difficulty_from_baseline(self):
        if not self._baseline_performance:
            return
        avg_perf = sum(self._baseline_performance) / len(self._baseline_performance)
        if avg_perf < 0.35:
            self.current_difficulty = 0.3
        elif avg_perf > 0.75:
            self.current_difficulty = 0.6
        else:
            self.current_difficulty = 0.5

    def _extract_test_cases(self, question: dict, rubric: dict) -> list[dict]:
        for key in ("test_cases", "tests", "unit_tests"):
            if isinstance(question.get(key), list):
                return question[key]
            if isinstance(rubric.get(key), list):
                return rubric[key]
        return []

    def _run_single_turn(self, question: dict, adaptive_enabled: bool):
        self.turn_count += 1

        qid = question.get("qid")
        rubric = get_rubric(qid)
        if rubric is None:
            print(f"Skipping qid={qid}: rubric not found")
            return

        allowed_time = float(question.get("time_limit_sec", 60))
        snapshot = self.timer.start(allowed_time)

        print(f"\nTurn {self.turn_count}")
        print("Question:", question.get("question_text", ""))

        answer = input("Candidate answer/code: ").strip()
        timing = self.timer.stop(snapshot, attempts=1, retries=0)

        eval_result = evaluate(answer, rubric)
        critic_result = self.critic.evaluate(answer, rubric, eval_result)

        q_type = str(question.get("type", "theory")).lower()
        is_coding = "coding" in q_type

        coding_result = {
            "status": "not_applicable",
            "coding_score": None,
            "tests_total": 0,
            "tests_passed": 0,
            "test_results": [],
            "policy_reasons": [],
        }
        if is_coding:
            test_cases = self._extract_test_cases(question, rubric)
            coding_result = evaluate_code_submission(
                answer,
                test_cases=test_cases,
                timeout_sec=self.code_timeout_sec,
            )

        aggregate = aggregate_scores(
            semantic_score=eval_result["S1_semantic"],
            conceptual_score=critic_result["conceptual_score"],
            coding_score=coding_result.get("coding_score"),
            is_coding=is_coding,
        )

        validated = self.validator.validate(
            raw_score=aggregate["raw_score"],
            evidence={
                "mandatory_pass": eval_result.get("mandatory_pass", True),
                "mistake_penalty": eval_result.get("penalty", 0.0),
                "execution_status": coding_result.get("status", ""),
            },
            is_coding=is_coding,
        )

        confidence, hesitation = self._behavior_from_text(answer)
        performance = float(validated["validated_score"])
        self._performance_history.append(performance)
        avg_performance = float(sum(self._performance_history) / len(self._performance_history))

        raw_state = np.array(
            [
                performance,
                avg_performance,
                confidence,
                hesitation,
                float(timing["time_norm"]),
                self.current_difficulty,
            ],
            dtype=np.float32,
        )

        action_name = "Baseline"
        action_idx = None
        if adaptive_enabled:
            normed = self._normalize_obs(raw_state).reshape(1, -1)
            action_pred, _ = self.policy.predict(normed, deterministic=True)
            action_idx = int(np.asarray(action_pred).reshape(-1)[0])
            action_name = self.ACTION_MAP.get(action_idx, "Same")
            print("System decision:", action_name)
            self._apply_action(action_name, question)
        else:
            self._baseline_performance.append(performance)

        turn_record = {
            "turn": self.turn_count,
            "phase": "adaptive" if adaptive_enabled else "baseline",
            "qid": qid,
            "topic": question.get("topic"),
            "question_type": q_type,
            "question_text": question.get("question_text"),
            "difficulty_before": round(float(raw_state[4]), 4),
            "difficulty_after": round(float(self.current_difficulty), 4),
            "answer": answer,
            "timing": timing,
            "semantic_score": eval_result.get("S1_semantic"),
            "structural_score": eval_result.get("S2_structural"),
            "reasoning_score": eval_result.get("reasoning_score"),
            "conceptual": critic_result,
            "coding": coding_result,
            "aggregated_raw_score": aggregate.get("raw_score"),
            "final_validated_score": validated.get("validated_score"),
            "validation_trace": validated.get("validation_trace", []),
            "mandatory_pass": eval_result.get("mandatory_pass", True),
            "action": action_name,
            "action_idx": action_idx,
            "state_vector": [float(x) for x in raw_state],
        }

        self.history.append(turn_record)
        self.logger.log_turn(turn_record)
        self._register_question_in_selector_state(question)

        print("Validated score:", turn_record["final_validated_score"])

    def run(self):
        reset_session_state()
        print("\nPrepAIred orchestrator started")
        print(f"Baseline turns: {self.baseline_turns}; Max turns: {self.max_turns}")

        baseline_questions = self._pick_baseline_questions()
        for question in baseline_questions:
            if self.turn_count >= self.max_turns:
                break
            self._run_single_turn(question=question, adaptive_enabled=False)

        self._seed_difficulty_from_baseline()

        while self.turn_count < self.max_turns:
            question = select_next_question(self.current_difficulty)
            if question is None:
                print("No valid question available for current constraints; ending session.")
                break
            self._run_single_turn(question=question, adaptive_enabled=True)

        summary = self.logger.finalize(
            {
                "final_difficulty": round(float(self.current_difficulty), 4),
                "baseline_turns_used": min(self.baseline_turns, len(baseline_questions)),
            }
        )

        print("\nInterview completed")
        print("Session folder:", self.logger.session_dir)
        print("Summary:", summary)


def main():
    parser = argparse.ArgumentParser(description="PrepAIred Orchestrator Agent")
    parser.add_argument("--max-turns", type=int, default=10)
    parser.add_argument("--baseline-turns", type=int, default=3)
    parser.add_argument("--code-timeout", type=float, default=2.0)
    args = parser.parse_args()

    agent = OrchestratorAgent(
        max_turns=args.max_turns,
        baseline_turns=args.baseline_turns,
        code_timeout_sec=args.code_timeout,
    )
    agent.run()


if __name__ == "__main__":
    main()
