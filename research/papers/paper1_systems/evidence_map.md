# Paper 1 Evidence Map
| Claim / RQ | Evidence Asset | File Path | Metric / Finding |
|---|---|---|---|
| Container Isolation | Negative Security Matrix | 	ables/table_sys_security_boundary.md | 9/9 vectors contained; SEC-02 trapped by --net=none |
| Subsystem Latencies | Latency Benchmark | 	ables/table_sys_latency_benchmark.md | Evaluator median 167ms; PPO median 0.64ms; Docker median 1527ms |
| Fault Resilience | Component Removal Study | 	ables/table_sys_architectural_ablation.md | 100% turn completion under component failures |
| Feedback Grounding | Adversarial Grounding Test | 	ables/table_llm_adversarial_grounding.md | Deterministic fallback activated on empty/adversarial input |
