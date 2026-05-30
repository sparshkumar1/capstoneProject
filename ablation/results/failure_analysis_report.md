# Failure analysis report

This report highlights weak sessions, score regressions, and difficulty oscillation.

## PPO only

- Sessions: 10
- Mean final score: 0.682 ± 0.123
- Largest score drop: -0.4650 ± 0.1203
- Difficulty jump: 0.900 ± 0.196

Worst sessions by final score:
- sim_01: final_score=0.399, mean_score=0.701, volatility=0.516
- sim_04: final_score=0.511, mean_score=0.531, volatility=0.422
- sim_07: final_score=0.535, mean_score=0.545, volatility=0.000

Worst sessions by score regression:
- sim_09: drop=-0.767, jump=1.000, final_score=0.650
- sim_05: drop=-0.649, jump=1.000, final_score=1.000
- sim_07: drop=-0.626, jump=0.000, final_score=0.535

## Heuristic only

- Sessions: 10
- Mean final score: 0.539 ± 0.155
- Largest score drop: -0.3896 ± 0.0755
- Difficulty jump: 0.900 ± 0.352

Worst sessions by final score:
- sim_03: final_score=0.226, mean_score=0.468, volatility=0.422
- sim_01: final_score=0.278, mean_score=0.613, volatility=0.000
- sim_02: final_score=0.335, mean_score=0.504, volatility=0.422

Worst sessions by score regression:
- sim_08: drop=-0.617, jump=2.000, final_score=0.383
- sim_00: drop=-0.504, jump=1.000, final_score=0.402
- sim_04: drop=-0.441, jump=0.000, final_score=0.794

## Fixed difficulty

- Sessions: 10
- Mean final score: 0.368 ± 0.115
- Largest score drop: -0.2969 ± 0.0546
- Difficulty jump: 0.000 ± 0.000

Worst sessions by final score:
- sim_04: final_score=0.150, mean_score=0.445, volatility=0.000
- sim_03: final_score=0.193, mean_score=0.512, volatility=0.000
- sim_00: final_score=0.200, mean_score=0.421, volatility=0.000

Worst sessions by score regression:
- sim_06: drop=-0.449, jump=0.000, final_score=0.268
- sim_03: drop=-0.381, jump=0.000, final_score=0.193
- sim_07: drop=-0.351, jump=0.000, final_score=0.524

