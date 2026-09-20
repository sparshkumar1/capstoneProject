# PREPAIred — Final Research Positioning (evidence-based; not a novelty claim)

Date: 2026-09-20. Phase 3 (positioning gate). Inputs: `ALTERNATIVE_PAPER_POSITIONING.md`, `SECOND_PASS_CLAIM_AUDIT.md`, `LITERATURE_NOVELTY_MASTER_MATRIX.md`, `research/claims/CLAIM_REGISTRY.csv`. **No protocol was rewritten.** No claim of publication novelty is made; multiple framings remain viable and that is preserved.

## 1. Current baseline framing
P1 dependability/containment of an integrated AI technical-assessment system · P2 validity and robustness of technical-answer evaluation · P3 controlled comparison of learned adaptive difficulty control with simpler policies.

## 2. Does the literature materially change the framing? **Yes, for two of three papers.**
- **Paper 2**: the stored evidence (X2B-C003, exploratory: length-only Spearman 0.4897 ≥ derived CrossEncoder 0.4825 > full composite 0.3812) and the ASAG literature (composites/ensembles are established; length is a known confound) remove the architecture-centric identity. The defensible identity is *measurement validity/diagnostic*: agreement is modest and wide, a trivial baseline is competitive on the old benchmark, concise-correct and paraphrase answers are under-scored.
- **Paper 3**: the literature already covers PPO tutors vs rule-based baselines (Axak 2025) and constraint layers for educational RL (Olukola 2026, preprints); shielding papers include shielded-random references (Carr 2023). The defensible identity is *decomposition of learned-policy benefit from constraint-layer benefit*, reported as equivalence and higher volatility.
- **Paper 1**: SandboxEval (2025 preprint) already reports an uncontained comparison; grader-hijacking papers concern LLM-as-scorer. The framing survives only conditionally on X1 evidence, and "negative-control" novelty must not be claimed.

## 3. Strongest evidence-supported alternative framing(s)
1. **Measurement/evaluation-centered (portfolio B) and empirical-methodology-centered (E)** — P1 evaluation design for containment and authority separation (conditional on X1-C/B); P2 measurement validity with a length-confound diagnostic (portfolio H); P3 matched-null evaluation of a learned controller. Compatibility: clearly compatible for P2/P3, potentially compatible for P1.
2. **Systems-centered (A)** remains viable for P1 if X1 yields results and the paper is scoped as a systems paper.
3. **Two-paper consolidation (F)** and a **research-process paper (G)** remain open, unsearched or unassessed.

Not supported: "trustworthy AI" (C), "reliable adaptive technical assessment" as achievement (D).

## 4. Closest prior work (per element)
Sandbox: SandboxEval (2025 preprint), APAC (2015). Authority separation/hijacking: CaMeL (2025 preprint), Cai 2026, Li 2026, Sahoo 2026. Evaluator: Mohler 2011, Ormerod 2023, Condor & Pardos 2024, Dubois 2024/Zheng 2023 (LLM judges). Adaptive: Ion 2025 (extended abstract), Axak 2025 (CEUR), CodeGENCAT 2026 (preprint), Riedmann 2025 (review). Constraint layer: Alshiekh 2018, Carr 2023, Olukola 2026 (preprints).

## 5. Why the chosen framing is defensible
It asserts only what stored evidence and read literature support: matched-control and decomposition designs, negative/equivalence findings, and diagnostics. It does not depend on any performance, safety or novelty claim, and every element names its closest prior work (see `SECOND_PASS_CLAIM_AUDIT.md` Part C).

## 6. Claims explicitly abandoned
"first/novel/unique/state-of-the-art"; "trustworthy AI"; "reliable adaptive technical assessment" (achievement); "shield" (formal); PPO improves tracking/is superior/lowers volatility; composite improves evaluation or is best; "negative controls are new in assessment sandboxing"; interview-practice system as a contribution; "secure/fully contained/fault-tolerant/sub-second end-to-end".

## 7. Evidence still missing
X1-C/B/A results (and registered protocols); X2-C benchmark (institutional/ethics gate, independent authoring, ≥3 blind raters, length strata); O7 (specified; blocked pending independent code review — see execution report); literature: P1-3 (degradation), P2-4/5/6 (paraphrase testing, question clustering), P3-1/4 (other adaptive coding systems, IRT/Elo baselines), equivalence-margin justification, RL-evaluation-methodology literature, reproducibility/preregistration literature (for portfolio G), privacy/regulation and ethics literature, SandboxEval remainder.

## 8. Impact on each paper
- **P1**: hold contribution wording until X1-C/B; scope as systems+diagnostic if only X1-D evidence exists; replace "dependable" with the specific attribute tested.
- **P2**: shift to a diagnostic identity; the length-only baseline and concise-correct under-scoring are results, not threats to hide; X2-C must include length strata and a length-only baseline.
- **P3**: emphasise equivalence and volatility under matched guardrails; "rule-based guardrail/constraint layer" terminology; O7 is robustness only.

## 9. Impact on venue strategy
None decided here. Observations only: a measurement/diagnostic identity is compatible with education-technology and evaluation venues; a systems identity depends on X1; the two-paper consolidation would change venue count. No deadline pressure is allowed to select a framing; venue rules (including any age/indexing requirement recorded in the archived readiness audit) remain unchecked.

## 10. Cross-paper boundaries
P1 owns sandbox/authority-separation/latency measurements; P2 owns evaluator agreement, length and adversarial diagnostics; P3 owns the simulator, persona-level policy comparison and guardrail accounting. No paper restates another's numerical results beyond a citation; the system description is shared by reference.

## 11. Preserved uncertainty
Whether P1 is a systems or measurement paper; whether P2 and P3 merge; whether a process paper exists; whether X2-C is feasible. These are open decisions for the user and the independent reviewer.
