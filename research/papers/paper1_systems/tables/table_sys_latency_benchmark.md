# Subsystem Latency & Throughput Benchmark (EXP-SYS-2)

Latency profiling across 50 iterations per subsystem on host hardware:

| Subsystem | Mean Latency | Median | P95 | P99 | Min - Max | Throughput (ops/s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Audio Signal Processing** | 0.42 ms $\pm$ 0.1 | 0.40 ms | 0.57 ms | 0.73 ms | 0.4 - 0.8 ms | 2374.6 |
| **Technical Evaluator (S1+S2+R)** | 325.13 ms $\pm$ 1097.7 | 167.59 ms | 176.23 ms | 4177.74 ms | 161.5 - 8009.2 ms | 3.1 |
| **Score Validator & Policy Rules** | 0.00 ms $\pm$ 0.0 | 0.00 ms | 0.00 ms | 0.00 ms | 0.0 - 0.0 ms | 2551019.9 |
| **PPO Policy Inference (6D)** | 0.67 ms $\pm$ 0.1 | 0.64 ms | 0.83 ms | 1.23 ms | 0.5 - 1.5 ms | 1492.0 |
| **Socratic Follow-up FSM** | 0.00 ms $\pm$ 0.0 | 0.00 ms | 0.00 ms | 0.00 ms | 0.0 - 0.0 ms | 6493481.6 |
| **Grounded Feedback Generator** | 4871.06 ms $\pm$ 26.2 | 4868.29 ms | 4901.06 ms | 4950.47 ms | 4816.2 - 4981.8 ms | 0.2 |
| **SQLite WAL Multi-Attempt Persistence** | 27.13 ms $\pm$ 4.2 | 27.77 ms | 32.02 ms | 34.82 ms | 17.5 - 36.0 ms | 36.9 |
| **Isolated Docker C Sandbox** | 2751.13 ms $\pm$ 2541.6 | 1527.73 ms | 6582.59 ms | 7581.67 ms | 1329.7 - 7831.4 ms | 0.4 |
