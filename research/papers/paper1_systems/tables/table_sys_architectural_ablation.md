# Architectural Component Removal & Reliability Study (EXP-SYS-3)

End-to-end turn latency and system reliability under component removal:

| Config ID | System Configuration | Active Components | Mean Turn Latency | Median | P95 | Reliability (0 Crashes) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| ARCH-01 | **Full Multimodal Architecture** | 6/6 | 5037.81 ms | 5040.28 ms | 5100.86 ms | 100.0% |
| ARCH-02 | **Text-Only Interview (No Audio)** | 5/6 | 5009.10 ms | 5001.19 ms | 5051.65 ms | 100.0% |
| ARCH-03 | **Heuristic Orchestration (No PPO)** | 5/6 | 5025.06 ms | 5014.39 ms | 5083.84 ms | 100.0% |
| ARCH-04 | **Deterministic Grounded Feedback (No Qwen LLM)** | 5/6 | 5023.04 ms | 5019.07 ms | 5064.96 ms | 100.0% |
| ARCH-05 | **Non-Coding Technical Interview (No Docker)** | 5/6 | 5028.00 ms | 5019.45 ms | 5083.08 ms | 100.0% |
| ARCH-06 | **Stateless Volatile Session (No SQLite WAL)** | 5/6 | 5018.02 ms | 5015.82 ms | 5051.34 ms | 100.0% |
