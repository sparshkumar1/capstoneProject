# Free literature pipeline (Semantic Scholar + Gemini 3.6 Flash as a non-grounded analyser)

New tooling only; it never reads or writes frozen evidence and never commits. Outputs go under this directory.

## Free-only guards (see `gemini.py`, `s2.py`)
- Retrieval: Semantic Scholar Academic Graph API only. Gemini is **not** a retrieval engine.
- Gemini: the only endpoint is `models/gemini-3.6-flash:generateContent`; no Deep Research, no interactions/agents, no other model.
- **Google Search grounding is intentionally disabled** (the workflow must stay free-only). `gemini._guard` refuses any request body containing `tools`, and a response carrying
  `groundingMetadata` aborts the run. The old `--ground` flag is rejected.
- Gemini only analyses text this pipeline supplies (abstract + locally selected passages of downloaded open-access PDFs). Every quote it returns is string-checked locally
  against the supplied text; unsupported items are stored as `UNVERIFIED` and are not propagated into the matrices.
- Hard call caps: 150 Gemini attempts per UTC day (all statuses counted) and 120 per process; minimum 8 s between calls. Any billing/precondition response aborts.
  The API does not reveal the billing tier, so free-tier status can only be confirmed in the Google AI Studio console.
- Key: `GEMINI_API_KEY` from the process environment only, sent in a request header, never printed, logged or stored (`fp_common.redact`). Optional free `SEMANTIC_SCHOLAR_API_KEY` (same rules).
- Semantic Scholar: cached responses, Retry-After honoured, exponential backoff with jitter, 4 attempts per request, circuit breaker after 4 consecutive give-ups (stage stops and reports).
- `state/api_ledger.jsonl` records every call (service, kind, HTTP status, prompt hash; no keys, no prompt text). `state/query_log.jsonl` records every query.

## Commands (run from the repository root)
```
.venv/Scripts/python.exe research/literature/free_pipeline/pipeline.py selftest    # offline checks, no network
.venv/Scripts/python.exe research/literature/free_pipeline/pipeline.py smoke       # 1 S2 query + 1 non-grounded Gemini call
.venv/Scripts/python.exe research/literature/free_pipeline/pipeline.py discover    # all query families + budgeted recommendation/reference expansion (resumable)
.venv/Scripts/python.exe research/literature/free_pipeline/pipeline.py rank        # candidates CSV, six 0-3 screening dimensions, core selection
.venv/Scripts/python.exe research/literature/free_pipeline/pipeline.py pdfs        # open-access PDFs only, hashed, text extracted, never overwritten
.venv/Scripts/python.exe research/literature/free_pipeline/pipeline.py verify      # Gemini extraction/questions/overlap on supplied text, quotes checked locally
.venv/Scripts/python.exe research/literature/free_pipeline/pipeline.py attack      # novelty attack proposals (abstract-only, quote-checked)
.venv/Scripts/python.exe research/literature/free_pipeline/pipeline.py matrices    # core/*.md+csv, SOURCE_VERIFICATION, PROVENANCE, attack proposals
```
Each stage accepts `--paper 1|2|3`. After `pdfs`/`verify`, rerun `rank` (only if manual overrides changed) and `matrices`.

## Layout
`candidates/PAPERn_CANDIDATES.csv`, `core/PAPERn_CORE_MATRIX.{md,csv}`, `SOURCE_VERIFICATION.md`, `PROVENANCE.md`, `NOVELTY_ATTACK.md` (reviewed judgement, hand-written from
verified evidence), `attack/` (model proposals + hit lists), `verification/` (per-paper Gemini records), `papers/` (PDFs, `PDF_INDEX.csv`, extracted text), `state/` (pools, cache, logs).
`state/manual_screening.json` (optional) records human include/exclude decisions with reasons.

## Reading the outputs
The six 0-3 screening dimensions are derived deterministically from keyword-group coverage and metadata; they only prioritise reading order and are not a quality ranking
(there is deliberately no overall score in the outputs). Novelty classes proposed by the model are leads for human review, never findings.
