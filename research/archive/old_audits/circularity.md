# ARCHIVED / SUPERSEDED — NOT A SOURCE OF CURRENT FACTS
> **Superseded by:** Current audits in 
esearch/audit/ and 
esearch/CANONICAL_SCIENTIFIC_TRUTH.md  
> **Date Archived:** 2026-09-17  
> **Reason:** Early exploratory audit report superseded by consolidated forensic audits. Preserved for historical record.  

---

# Evaluation Circularity and Methodological Independence Audit

**Principle:** Prevent metrics from crediting a system for behaviors that are hardcoded or circular.

---

## 1. RL Policy vs. Reward Function Circularity
- **Risk:** In `InterviewEnv`, $60\%$ of the reward is allocated to matching `oracle_action_from_obs`. If evaluation only measures cumulative reward, PPO is simply evaluated on how well it memorized the oracle rules.
- **Safeguard in PrepAIred:** Independent evaluation protocols (EXP-RL-1) do NOT evaluate PPO solely by training reward. Instead, we measure **external, independent behavioral trajectory metrics**:
  1. Directional Adaptation Correlation ($\rho$ between candidate response performance and difficulty trajectory).
  2. Oscillation Count (frequency of rapid $0 \to 2$ or $2 \to 0$ difficulty flips).
  3. Trajectory Smoothness (step-to-step variance in difficulty).
  4. Guardrail Override Frequency.

## 2. Post-Hoc Guardrails vs. Policy Attributions
- **Risk:** Crediting PPO for stopping difficulty spikes when the action was actually overridden by a hardcoded guardrail (e.g. G4 overriding to Easier).
- **Safeguard in PrepAIred:** The orchestrator explicitly logs `decision_source`:
  - `ppo`: Pure unconstrained neural policy action.
  - `guardrail_g4`, `guardrail_g1`, `guardrail_g2`: Hard override.
  - `baseline_warmup`: Turn 1-2 deterministic schedule.
  EXP-RL-2 explicitly ablates guardrails to measure policy behavior in their complete absence.

## 3. Feedback Evaluation vs. LLM-as-a-Judge Circularity
- **Risk:** Using another LLM (e.g., GPT-4) as the sole metric of whether Qwen feedback is "good."
- **Safeguard in PrepAIred:** EXP-LLM-1 evaluates feedback quality using **grounded deterministic checks**:
  - Unsupported Concept Hallucination Rate: Concepts mentioned in narrative that are NOT present in `structured_evaluation`.
  - Lexical Grounding Ratio: Direct token overlap with candidate answer and rubric concepts.
  - Template Fallback Rate under adversarial malformed inputs.
