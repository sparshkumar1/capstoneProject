# Provenance (free literature pipeline)

Generated 2026-09-20T18:31:48+00:00 by `pipeline.py matrices`.

## Configuration
- Retrieval source: Semantic Scholar Academic Graph API (unauthenticated: yes)
- Gemini model: gemini-3.6-flash, NON-GROUNDED, analysis/verification of supplied text only
- Google Search grounding: NOT used (disabled in code; requests with tools are refused)
- Billing: not enabled by this tool; no paid API used; Deep Research: not used
- Gemini API key: never written to disk; ledger stores status codes and prompt hashes only

## Call counts (from `state/api_ledger.jsonl`, all dates)
- Semantic Scholar requests: 35 (HTTP 200: 1, HTTP 429: 34, other: 0)
- Gemini attempts: 1 (HTTP 200: 0, other: 1)

## Discovery log (`state/query_log.jsonl`)
| UTC time | Paper | Stage | Query | Status | Hits | New unique | Cached |
|---|---|---|---|---|---|---|---|
| 2026-09-20T18:25:03+00:00 | 1 | discover | fault-aware AI orchestration | failed |  |  |  |
| 2026-09-20T18:27:12+00:00 | 1 | discover | graceful degradation in AI systems | failed |  |  |  |
| 2026-09-20T18:29:18+00:00 | 1 | discover | failure isolation in interactive AI systems | failed |  |  |  |
| 2026-09-20T18:31:26+00:00 | 1 | discover | sandboxed code execution security dependability | failed |  |  |  |
| 2026-09-20T18:31:26+00:00 | 1 | discover | runtime containment for untrusted code | aborted_persistent_rate_limit |  |  |  |
| 2026-09-20T18:31:26+00:00 | 2 | discover | automatic short answer grading | aborted_persistent_rate_limit |  |  |  |
| 2026-09-20T18:31:26+00:00 | 3 | discover | computerized adaptive testing | aborted_persistent_rate_limit |  |  |  |

## Per-paper pools, deduplication and screening
- Paper 1: no pool retrieved
- Paper 2: no pool retrieved
- Paper 3: no pool retrieved

## PDFs
0 open-access PDFs downloaded and hashed (`papers/PDF_INDEX.csv`); unavailable/failed listed in `papers/PDF_UNAVAILABLE.csv`.

## Gemini verification
Every verification/attack call supplied only the abstract and locally selected PDF passages; quotes were string-checked locally; unverified items are stored as UNVERIFIED and excluded from matrices. See `verification/` and `attack/`.
