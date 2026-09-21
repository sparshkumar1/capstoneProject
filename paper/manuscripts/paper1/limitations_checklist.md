# Paper 1 — limitations checklist (draft v1)

Each item must be visible to a reviewer before they discover it. "Where" = manuscript location.

| # | Limitation | In abstract | In dedicated section (VII) | Where else |
|---|---|---|---|---|
| 1 | NaN/Inf/negative evaluator outputs become 0.0 (HIGH 1) | yes | yes | V-B |
| 2 | Follow-up channel untested (HIGH 2) | yes | yes | III, V-C, VI |
| 3 | SEC-01 depended on literal pre-flight filter; TRACEME returned 0 (HIGH 3) | yes | yes | V-A, VI |
| 4 | 6 s shipped Qwen timeout vs 19–30 s local generation (HIGH 4) | yes | yes | V-D |
| 5 | One environment (developer workstation configuration) | yes | yes | IV, IX |
| 6 | Five repetitions are repeatability checks, not samples | yes ("repeated runs", "repeatability observations") | yes | I, IV |
| 7 | Author-written attacks, oracles, controls | no (space) | yes | IV |
| 8 | SEC-08 oracle and some X1-A SLAs derive from SUT constants | no | yes | V-A, VI |
| 9 | SEC-09 canary reset flaw | no | yes | V-A |
| 10 | FLT-08 WebSocket and FLT-09 audio not executed | no | yes | Table III |
| 11 | FLT-05 tests missing CLI, not unreachable daemon | no | yes | V-B |
| 12 | Same-agent design, repair and re-test; AI-authored experiments | no | yes | V-B |
| 13 | Methodology review: verdict relayed, report not in repository | no | yes | — |
| 14 | Local unpushed tags (registration author-controlled) | no | — | IV |
| 15 | Reruns on build B written after build-A results seen | no | yes | IV |
| 16 | Injection steering not demonstrated (23/72) | no | yes | V-C |
| 17 | Qwen faults via stub in X1-A | no | yes | V-D |
| 18 | No UDP/DNS/IPv6/kernel-escape tests | no | yes | — |
| 19 | Unseeded generation; 600 s client timeout in X1-B-I | no | yes | IV |
| 20 | `.venv` violates declared pins (registry X-C004) | no | yes | — |
| 21 | Not evaluated: users, latency guarantees, other platforms, adaptive attackers | no | yes | IX |

Items 7–21 are not in the abstract for reasons of length; items 1–6 (the four HIGH limitations, environment, repetition) are.
