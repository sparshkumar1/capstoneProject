# Paper 1 — Systems, Security & Reliability Reproduction Guide

### Execution Command
```bash
python research/scripts/run_paper1_systems_study.py
```

### Verified Test Suites
1. **Authentication Tests:** 5/5 passed (rejection of unauthenticated/malformed requests).
2. **Tenant Isolation:** 3/3 passed (zero cross-candidate data leakage in REST/DB).
3. **Session State Isolation:** 2/2 passed (concurrent sessions remain mutually isolated).
4. **Prompt Injection:** 4/4 passed (adversarial instructions contained <= 0.30 score).
5. **Docker Containment:** 7/7 passed (infinite loop, OOM, fork bomb, network, filesystem containment).
6. **Fault Injection:** 10/10 passed with 100% recovery rate.
7. **SQLite Integrity:** WAL mode active, zero locking failures.
