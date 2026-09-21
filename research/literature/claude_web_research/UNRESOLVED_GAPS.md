# Unresolved gaps (2026-09-21)

## Must close before any comparison text is written
1. **Kadam et al. 2026 full text** (Paper 3). Unread: state definition and dimension, reward terms, heuristic rules, number of seeds, training budget, numerical results, blueprint constraint implementation, whether any post-policy safety layer exists, whether a state-blind constant baseline or equivalence analysis is included. Needs institutional/author access. Until then no sentence may state that PrepAIred's control comparison is absent from that paper; the statement is limited to "not seen in the parts read".
2. **SandboxEval full text** (Paper 1): whether it uses positive/negative controls, host observables, repeated runs. Abstract only was read this run.
3. **Part 2 of the comparative AI-sandbox study** (Paper 1): may contain behavioural tests; not yet available/opened.
4. **Re-check of all tool-extracted quotes** against the primary pages (Docker seccomp sentence, EACL abstract sentence, Norman et al. effect size, Che et al. numbers, Yan et al. 100% figures).

## Saturation status (criterion: at least one strong source per major dimension AND two consecutive different searches with no new core paper)
- Paper 1: sandbox-escape, comparative sandboxes, fault-tolerant sandboxing, fault injection into LLM systems, authority separation, grader prompt injection: each dimension has at least one strong source. The last two distinct searches (assessment-outage fail-closed; seccomp/ptrace evaluations) added no new core paper. Reasonable saturation on headline threats. Not saturated: peer-reviewed (non-preprint) sources; LLM inference-service failure studies (snippet-level only); AI interview-system dependability.
- Paper 2: EACL 2026 lead, LLM-judge bias, ASAG quality-conditioned error, gaming, metamorphic testing, agreement frameworks all have a source. The last two searches (technical-interview LLM scoring; concise-answer penalisation) produced no new core paper. **Not saturated** on: ASAG for technical/programming answers, measurement invariance and psychometric validity literature (not searched in depth), NLI/cross-encoder ASAG beyond CARRY items, and keyword stuffing specific to concept-coverage scorers.
- Paper 3: the mandatory paper, PPO/DQN tutoring, RL CAT, shielding, equivalence and RL-reporting statistics each have a source. The last two searches (LLM interview practice; safe RL action masking) produced no new core paper. **Not saturated** on: knowledge tracing + RL, curriculum RL/teacher-student, bandit-based adaptive assessment (only CARRY), Elo/IRT versus RL comparisons, and a peer-reviewed treatment of "constant policy equals learned policy" in adaptive tutoring beyond Che et al.

## Coverage shortfalls against the master prompt
- Candidate targets (30-60 initial, 15-25 serious per paper) were not reached with newly verified items; new opened sources are about 12 / 10 / 9. CARRY items were listed but not re-verified.
- Screening scores were assigned to candidate rows only at the coarse level shown in the candidate files.
- Forward citation chasing (citing papers) was not possible with the tools used; backward chasing done for the Paper 3 target only, partially.
- Backward chase of Kadam et al.'s 42 references was limited to the first entries visible on the landing page (Doroudi 2019, Riedmann 2025, Spain 2022, Zhou et al., Ausin et al., Patil 2021, Heimerl et al.). The rest are unread.
- Downloaded but unread: AAMAS 2025 "Real-World Testing Matters in RL for Education" PDF (kept in the session tool-results folder, not in the repository).

## Search-negative statements (scope-limited)
- No assessment-pipeline study of fail-closed evaluator outage or compiler-timeout container cleanup was found.
- No study naming under-scoring of concise-correct technical answers by a similarity-composite scorer was found.
- No grader-specific metamorphic-testing suite was found.
- No study using a state-blind constant action with identical guardrails and a preregistered equivalence margin for adaptive-difficulty RL was found in the parts read.
All four mean "not found by the listed queries".

## Not resolved by literature (need project decisions, not asked here)
- Whether Paper 3 should be reframed; whether to add an Elo/IRT baseline (requires a registered protocol); whether Paper 1 should cite preprints only; venue choice.

# Status after the gap-closure pass (2026-09-21)
The section above is the pre-closure record and is kept as history.

## Closed
- Quote and source audit: about 60 quotations and numbers rechecked; four corrections made (QUOTE_AUDIT.md). Remaining UNVERIFIED items are listed there.
- SandboxEval full text (was gap 2): read. Its oracle is in-payload status with proxy operations; no weakened control or repetition described.
- Paper 1 methodology comparison against SandboxEscapeBench, SandboxEval, comparative study, RedCode, position paper (P1_SANDBOX_METHODOLOGY_COMPARISON.md).
- Paper 2 current-year bias pass (P2_2026_BIAS_PASS.md).
- Paper 3 adaptive-assessment prior art, four user leads assessed (P3_ADAPTIVE_ASSESSMENT_PRIOR_ART.md).

## Still open
1. **Kadam et al. full text (Paper 3): OPEN, material.** Unavailable: state dimension, IRT form, horizon and budget, reward, PPO/DQN/PETS/MBPO configuration, heuristic rules, seed count and role, results and numbers, presence of a constant or random baseline, presence of any post-policy safety layer, code/data availability. See KADAM_VERIFICATION.md. Needs institutional access, an author copy or an open-access version.
2. Part 2 of the comparative AI-sandbox study: not found; may not exist yet.
3. Forward-citation chasing: no citing-paper index available with the permitted tools; only exact-title and topic searches.
4. Abstract-level only (not full-text): Tang 2026, Qiu and Chen 2025, DRAKT, UCO, PolyInterview, Deng et al., Cong et al., Soumik, AMATI, Shi et al., Fujinuma (Anthology page), Wang et al. 2024 (metadata via search listing).
5. Not opened at all: Doroudi et al. 2019, Riedmann et al. AAMAS 2025 (PDF downloaded earlier, unread), Zoucha et al. 2025, an engagement-aware RL question-selection chapter, Williamson et al. 2012 full text, Alshiekh et al. 2018.
6. Paper 2 areas still thin: technical-domain short-answer scoring, measurement invariance, NLI/cross-encoder ASAG, concept-coverage scorers.
7. Paper 3 areas still thin: teacher-student curriculum RL (one search), Elo/IRT versus RL comparisons.
8. Open non-literature decisions unchanged: Paper 3 reframing, an Elo/IRT baseline (needs a registered protocol), venue choice, whether Paper 1 cites preprints only.

## Scope-limited search-negative statements after this pass
- No study using a state-blind constant action under the same guardrails as a learned policy with a preregistered equivalence margin, for adaptive-difficulty RL: not found in the sources read; Kadam et al. methods unread.
- No study combining fixed attack programs, weakened-flag controls, host-side observables, repetition and old-versus-new build regression for an assessment pipeline: not found among the sources read.
- No grader-specific metamorphic suite; no study naming concise-correct under-scoring of a similarity composite: not found.
All mean "not found by the listed queries".

## Final-closure status (2026-09-21)
Closed in this pass: Riedmann et al. 2025 and Doroudi et al. 2019 read (P3_RL_EDUCATION_REVIEWS.md); the Kadam elements in Table A of KADAM_VERIFICATION.md fixed as VERIFIED; a focused final gap check for Paper 3 found no materially new direct competitor (P3_FINAL_NOVELTY_POSITION.md section 6). Search stopped by instruction.
Still open and genuinely unresolved: Kadam et al. state dimension, IRT formula, horizon and budget, reward equation, PPO/DQN/PETS/MBPO hyperparameters, seed count, numerical results, any constant or random baseline, any post-policy guardrail, code or data release; Alshiekh et al. definition not reopened; forward citations of Kadam and Che could not be enumerated with the permitted tools; Part 2 of the comparative sandbox study not found; the "Kaur 2024" adaptive-interview item is unlocatable. Paper 1 and Paper 2 literature conclusions unchanged (no new search performed).
