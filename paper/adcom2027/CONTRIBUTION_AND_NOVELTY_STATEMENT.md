# Contribution and novelty statement (ADCOM 2027 manuscript)
Claimed contributions (each tied to evidence in `results/`):
1. Execution-path audit of what is and is not multi-agent (`architecture/ARCHITECTURE_INVENTORY.md`) and an empirical write-authority matrix over 186 traced turns (`results/trace_state_writes.json`). Evidence class: code + replay trace.
2. Mechanism × fault ablation with pre-registered invariants/predictions (E1, 752 sessions, 14/14 predictions matched) on the real orchestrator code, replay class.
3. Two evidence-driven changes with before/after measurements: strict scorer-to-hub contract (E4) and a circuit breaker for the LLM service (E5). Replay and real-socket classes.
4. Measured failure-path latency with real sockets (E2) and a probe of the grounding check on constructed outputs (E3).
Novelty position: **application / empirical-engineering contribution, not a new coordination algorithm.** Fail-closed handling, retries and circuit breakers are established practice. Related work retrieved (summary level, full texts not read) studies fault injection in LLM-agent systems with LLM faults (MAST, Huang et al. ICML 2025, MAS-FIRE) and interview-practice systems (Zara, PolyInterview, user studies); no retrieved work ablates coordination mechanisms of an interview-coaching pipeline with a non-LLM authoritative scorer. This is a statement about the retrieved summaries; no "first" claim is made in the manuscript.
Explicitly not claimed: decentralised or negotiating agents; feedback quality, coaching value or learning; rates with a live LLM; PPO benefit.
