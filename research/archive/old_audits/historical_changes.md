# ARCHIVED / SUPERSEDED — NOT A SOURCE OF CURRENT FACTS
> **Superseded by:** Current audits in 
esearch/audit/ and 
esearch/CANONICAL_SCIENTIFIC_TRUTH.md  
> **Date Archived:** 2026-09-17  
> **Reason:** Early exploratory audit report superseded by consolidated forensic audits. Preserved for historical record.  

---

# Historical Architecture Evolution and Specification Shifts

**Scope:** Chronological audit of design transitions from initial research prototypes to current frozen production code.

---

## 1. Summary of Major Transitions

| Architectural Dimension | Initial Concept / Capstone Draft | Frozen Current Implementation (`9cfd34f`) | Rationale for Transition |
|---|---|---|---|
| **RL Action Space** | 5 discrete actions: `{Easier, Same, Harder, Hint, Followup}` | **3 discrete actions:** `{0: Easier, 1: Same, 2: Harder}` | Hints and Socratic follow-ups are pedagogical interventions on the current concept, not global curriculum difficulty shifts. Decoupling them to deterministic orchestrator rules stabilized MDP state transitions. |
| **RL Training Steps** | 204,800 steps (or 500,000 in early notes) | **300,000 steps** (`rl/training/retrain_quick.py`) | 300,000 steps ensures asymptotic stability of the GAE critic value function over synthetic persona distributions while requiring <3 minutes of CPU training time. |
| **RL Training Persona** | Vaguely claimed human recording transcripts | **100% Synthetic Personas** (`rl/training/simulated_candidate.py`) | Real candidate interview dataset of sequential multi-turn trajectories does not exist. Grounded in mathematical response models: $P(\text{correct}) = \sigma(8.0 \times (\text{skill} - \text{diff}))$. |
| **Evaluator Formula** | $0.24 S_1 + 0.43 S_2 + 0.33 R$ | **$0.15 S_1 + 0.35 S_{2,\text{eff}} + 0.50 R$** | Empirical weight ablation demonstrated that giving CrossEncoder 50% weight is essential to detect deep technical reasoning and penalize shallow lexical keyword-stuffing. |
| **Feedback LLM** | Remote Ollama server running Qwen-7B | **Local `Qwen2.5-1.5B-Instruct`** weights | Eliminated remote API network latency, external dependencies, and reduced inference latency to <2.5s on local CPU, while retaining structured schema compliance. |
| **Persistence Layer** | Volatile in-memory dictionary / mock JSON | **SQLite 3.50 in WAL Mode** (`data/prepaired.db`) | In-memory storage lost attempt history across browser refreshes and crashes. SQLite provides durable ACID storage with composite indexed lookups for candidate learning trajectories. |
| **Attempt Retries** | Full interview reset or queue re-enqueue | **In-turn Retry with Score Rollback** | Allows candidates to iteratively correct misconceptions on the same turn without artificially exhausting the 15-question interview quota or triggering premature PPO difficulty updates. |
| **Best Answer Selection** | Max raw score in memory | **Compound Tie-Breaking in SQLite** | In-memory max score did not account for missing concept counts or chronological progression. New deterministic sort key: `(validated_score, -len(missing), attempt_number)`. |
