# Final publication-readiness assessment (2026-09-20)

Categories are assessed qualitatively (**Met / Partly met / Not met**); no numeric score is given. "Independent review" means review by someone other than the agent that designed and ran the work; the only review of the X1 protocols so far is the same agent's self-audit. Labels: **READY FOR MANUSCRIPT**, **READY WITH MATERIAL LIMITATIONS**, **NOT READY**.

| Category | Paper 1 (dependability / containment) | Paper 2 (evaluator diagnostics) | Paper 3 (guardrailed adaptive difficulty) |
|---|---|---|---|
| A Research question | Met (narrow, scoped) | Met as an exploratory diagnostic; not met as a validation question | Met |
| B Methodological validity | Partly met: campaigns are sound for their scoped claims but author-designed, self-audited; several HIGH-RISK wording items (`X1_METHOD_AUDIT.md`) | Partly met: small author-constructed benchmark, 8 question clusters, exploratory | Partly met: registered design, simulation only, oracle-aligned reward, authored persona rule |
| C Data provenance | Met for engineering artifacts (hashes, tags, environment, both builds) | **Not met** for human ratings (rater provenance, consent, ethics records incomplete); Partly met for model provenance (fine-tuned derivative, training data unknown) | Met for frozen artifacts; Partly met for checkpoints (not regenerable: unseeded candidate noise) |
| D Statistical analysis | Met (deterministic counts, no inference claimed) | Partly met: case and question-cluster bootstrap, no multiplicity control, intervals wide | Met for the primary and O7; secondary contrasts descriptive |
| E Baselines / controls | Met (no-fault controls, permissive controls, mutation control; perturbation controls not mutant builds) | Partly met (length-only, lexical, R-only, S1+R baselines; no independent LLM-judge baseline) | Partly met (state-blind constant-action, heuristic, controller, oracle-rule; **no Elo/IRT/CAT baseline**) |
| F Independent review | **Not met** (X1 protocols self-registered and self-audited) | Not met | Partly met (independent code-audit rounds by other tools occurred earlier in the project; whether they covered the O7 script and protocol is not re-verified here) |
| G Literature positioning | Partly met (second-pass sources verified; key first-pass items still unread; no novelty claim) | Partly met (question-cluster and non-LLM length dependence for short technical answers unresolved) | Partly met (no literature basis for ±0.12; Elo/IRT not run) |
| H Limitations | Met (documented in the matrix and audit) | Met | Met |
| I Reproducibility | Partly met (harness at tag, write-once outputs, hashes; needs local Docker image archive and a real Qwen model; unseeded generation) | Partly met (frozen files/hashes; `.venv` not locked, registry X-C004) | Met for X3-A/O7 (locked env `LOCK-X3-2026-09-19`); not for retraining |
| J Claim discipline | Met after the claim matrix (forbidden words listed; two builds reported) | Met after the claim matrix (explicit "unsupported" list) | Met after the claim matrix |

## PAPER 1
- **Research question:** In an LLM-assisted interview-practice pipeline, how does the system behave under enumerated dependency faults and attack programs, and do LLM-authored texts influence the recorded technical score observables?
- **Contribution (permitted):** a claim-scoped fault-injection campaign and a containment campaign with controls, two defects found and repaired with old-vs-new evidence on two builds, and a documented and partly tested invariance property; not a security or fault-tolerance result.
- **Evidence:** X1-C 9/9 attacks contained in both builds with controls breaching (P1-C1); X1-A 12/12 scenarios pass on build B after two real defects on build A (P1-F1/F2); X1-B-I on build B (v3): 72/72 valid pairs (minimum 30 met), 72/72 invariant, controls detected; on build A (v2) only 16 of the registered 30 valid pairs (`X1-B-old-vs-new.md`).
- **Methodological review:** self-audit only (`X1_METHOD_AUDIT.md`).
- **Remaining blockers:** independent review of the X1 protocols; wording constraints (no "secure", "fault-tolerant", "preregistered" without local/unpushed qualifier); FLT-08/09 not executed; follow-up channel untested; the shipped 6 s timeout vs local generation time.
- **Publication readiness: READY WITH MATERIAL LIMITATIONS** (conditional on the wording constraints and an independent methodological review before submission).

## PAPER 2
- **Research question:** How well does an evidence-grounded composite scorer agree with human raters on technical interview answers, and where does it fail?
- **Contribution (permitted):** exploratory agreement, question-cluster intervals, sensitivity analyses, baseline comparison (length-only competitive, composite below simpler components), and category diagnostics (all correct/partial categories under-scored, verbose-wrong over-scored).
- **Evidence:** 64 author-constructed answers, 8 questions, 3 raters; all numbers verified against frozen artifacts (`FINAL_STATISTICAL_AUDIT.md`).
- **Methodological review:** none independent.
- **Remaining blockers:** confirmatory round blocked (institutional/ethics route, consent, rater provenance, precision-target confirmation); incomplete rater provenance may itself bar some venues; no LLM-judge baseline; category diagnostics rest on 2–8 cases.
- **Publication readiness:** as an exploratory diagnostic / measurement-validity study: **READY WITH MATERIAL LIMITATIONS**; as a validation or confirmatory evaluator paper: **NOT READY**. The paper must not be framed as validation.

## PAPER 3
- **Research question:** Does a learned PPO difficulty controller add tracking benefit over a state-blind constant action once the same guardrails are applied, in simulation?
- **Contribution (permitted):** registered equivalence result (Δ −0.0350 [−0.0818, +0.0021], margin ±0.12; superiority not met), unchanged under three registered sensitivity analyses, with higher PPO volatility and full guardrail accounting.
- **Evidence:** X3-A primary and O7 (frozen, verified); five-persona frozen study (descriptive).
- **Methodological review:** independent code-audit rounds by other tools occurred earlier in the project (coverage of the O7 script not re-verified here); this sprint added none for Paper 3.
- **Remaining blockers:** no Elo/IRT/CAT baseline; ±0.12 margin unjustified by literature; reward/oracle coupling not re-audited; simulation only; equivalence must not be written as "no effect".
- **Publication readiness: READY WITH MATERIAL LIMITATIONS.**
