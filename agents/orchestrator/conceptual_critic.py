class ConceptualCritic:
    """Conceptual critic with deterministic fallback and LLM-ready interface."""

    def __init__(self, mode: str = "deterministic", llm_callable=None):
        self.mode = mode
        self.llm_callable = llm_callable

    def evaluate(self, candidate_text: str, rubric: dict, evaluation_result: dict) -> dict:
        if self.mode == "llm" and callable(self.llm_callable):
            try:
                payload = self.llm_callable(candidate_text, rubric, evaluation_result)
                payload["source_mode"] = "llm"
                return payload
            except Exception:
                # Safe fallback keeps the interview session running.
                pass

        return self._deterministic_fallback(rubric, evaluation_result)

    def _deterministic_fallback(self, rubric: dict, evaluation_result: dict) -> dict:
        details = evaluation_result.get("concept_details", [])
        concept_groups = rubric.get("logic_markers", {}).get("concept_groups", [])

        total = max(len(details), len(concept_groups))
        if total == 0:
            return {
                "conceptual_score": 0.0,
                "covered_concepts": [],
                "missed_concepts": [],
                "reasoning_notes": "No concept groups found in rubric.",
                "source_mode": "deterministic",
            }

        covered = []
        missed = []

        for idx in range(total):
            if idx < len(concept_groups) and concept_groups[idx]:
                label = " / ".join(str(x) for x in concept_groups[idx])
            else:
                label = f"concept_{idx}"

            is_covered = bool(idx < len(details) and details[idx].get("covered", False))
            if is_covered:
                covered.append(label)
            else:
                missed.append(label)

        conceptual_score = len(covered) / total
        note = (
            "Coverage derived from rubric concept group matches."
            if missed
            else "All rubric concept groups were covered."
        )

        return {
            "conceptual_score": round(float(conceptual_score), 4),
            "covered_concepts": covered,
            "missed_concepts": missed,
            "reasoning_notes": note,
            "source_mode": "deterministic",
        }
