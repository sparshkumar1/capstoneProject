# Paper 3 Outline: Guardrailed Multimodal Reinforcement Learning
**Target Venue:** SmartCom 2027 / ICMLSC 2027
**Title:** Guardrailed Multimodal Reinforcement Learning for Adaptive Technical Interview Difficulty

## Section 1: Introduction
- Pacing in technical interviews: Failure of fixed difficulty and hyper-volatility of heuristic rules.
- Multimodal candidate state incorporating performance and speech prosody.
- Core thesis: Guardrailed PPO optimizes difficulty pacing, reducing volatility by 21% while protecting anxious candidates.

## Section 2: Related Work
- Reinforcement learning in Intelligent Tutoring Systems (ITS).
- Adaptive difficulty and Zone of Proximal Development (ZPD).
- Prosodic speech analysis in educational assessments.

## Section 3: RL Formulation & Guardrail Safeguards
- 6D observation space: $[perf, avg\_perf, conf, hes, dim4, diff]^T$.
- Discrete action space $\\Delta d \\in \\{-1, 0, +1\\}$.
- Hybrid stability reward function: .60 R_{\\text{dec}} + 0.30 R_{\\text{out}} + 0.10 R_{\\text{shp}}$.
- Pedagogical guardrails (G1–G4) preventing premature escalation and consecutive oscillation.

## Section 4: Experimental Evaluation
- EXP-RL-1: Policy vs Baselines across 5 candidate personas over 20 random seeds.
- EXP-RL-2: Dimension 4 impact analysis (response time vs turn progress domain transfer).
- EXP-RL-3: 6D state ablation and speech acoustic perturbation sensitivity.

## Section 5: Discussion & Limitations
- Why high linear heuristic correlation (=0.962$) represents educational failure.
- Acoustic bias insulation: Hesitation used solely to stabilize, never to penalize.
