# Paper 1 - section outline (IEEE style; venue TBD)
1 Introduction (LLM-assisted assessment pipelines; why failure behaviour and score authority matter; scope)
2 Related work (chaos engineering / fault injection: Basiri 2016; container security context: Sultan 2019; sandbox and grader-hijack work from the first-pass matrix after verification; no novelty claim)
3 System (orchestrator, evaluator, Qwen feedback service, Docker C sandbox, storage; authority boundaries as implemented)
4 Method (threat and fault model; registered protocols X1-A/B/C, their oracles and controls; what "registered" means here: local tags, author-written, self-audited; build A vs build B)
5 Results (5.1 containment; 5.2 fault injection on build A and build B; 5.3 Qwen invariance; 5.4 defects and repairs)
6 Discussion (what the negative and positive controls show; layered facts; latency of the LLM path vs shipped timeouts)
7 Threats to validity and limitations
8 Conclusion
Appendix: build hashes, environment record, per-run command lines, artifact hashes.
