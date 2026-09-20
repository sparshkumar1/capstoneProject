# Final claim / evidence / limitation audit (2026-09-20)

Per-paper CLAIM → EVIDENCE → LIMITATION → PERMITTED WORDING tables: `PAPER1_FINAL_CLAIM_MATRIX.md`, `PAPER2_FINAL_CLAIM_MATRIX.md`, `PAPER3_FINAL_CLAIM_MATRIX.md` (each also lists unsupported statements). Numbers were verified against artifacts in `FINAL_STATISTICAL_AUDIT.md`.

## Sentence-level tests applied to every strong statement
1. Evidence exists (artifact path and hash in the matrix). 2. Evidence is scoped (build, environment, N, exploratory vs registered). 3. Sample size visible in the row. 4. Uncertainty visible (interval or "deterministic repetition, no interval"). 5. Alternative explanations named in the Limitation column. 6. No stronger wording than the evidence.

## Flagged-word scan
A script scanned all `*CLAIM_MATRIX.md`, `manuscript/*/*.md` and `research/literature/FINAL_*.md` files for: prove(s), guarantee, secure, robust, superior, reliable, trustworthy, novel, first, state-of-the-art, fault-tolerant, isolated. Result: 64 hits. **50 sit in prohibition, negation or limitation context** (e.g. "Never write: secure, isolated, fault-tolerant…", "not a security guarantee"). **14 are the ordinal "first"** ("first build", "first pass", "read first"), none a novelty claim. One positive use of "robust" ("robust to three registered sensitivity analyses") was replaced by "classification unchanged under three registered sensitivity analyses". No unqualified use of the other words remains. The scan is a lexical check and does not replace reading each sentence at manuscript time.

## Wording rules carried into the manuscript (from this sprint's audits)
- Paper 1: "failure-aware", "contained in this harness for these nine programs", "protocol committed and tagged before execution (local, unpushed)"; never "secure", "isolated", "fault-tolerant", "preregistered" alone, "the LLM cannot influence scoring".
- Paper 2: "exploratory", "diagnostic", "measurement validity"; never "validated", "human-equivalent", "independent experts", "composite superior".
- Paper 3: "equivalent within the registered ±0.12 margin", "no superiority under the registered margin", "rule-based guardrail (not a shield)"; never "PPO superior", "no effect", "guardrails eliminate violations".
- All papers: repair-and-retest by the same agent is a regression check, not an independent replication; the frozen tags are local.
