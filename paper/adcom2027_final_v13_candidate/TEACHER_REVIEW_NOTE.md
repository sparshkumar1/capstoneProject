# Briefing Note for Teacher Review (5 October 2026)
**Manuscript:** *Bounded-Authority Agents in an Orchestrated Interview-Practice System: Coordination, Arbitration and Fault Containment*  
**Target Venue:** 31st International Conference on Advanced Computing and Communications (ADCoM 2027)  
**Proceedings Series:** Springer Communications in Computer and Information Science (CCIS)  
**Candidate Directory:** `paper/adcom2027_final_v8_candidate/`  
**Compiled Paper PDF:** `ADCOM2027_PREPAIred_v8_complete_blind.pdf` (20 pages, Springer CCIS format)  
**Date of Briefing:** 3 October 2026 (Internal completion deadline met)

---

## 1. What This Paper Contributes

This paper investigates how to extend an automated technical-interview practice system with **stateful, bounded-authority agents** without sacrificing architectural dependability or state consistency:
1. **Bounded-Authority Architecture:** Introduces a Strategy Agent (weakness ledger, difficulty proposals, follow-up probes) and a Coaching Agent (hints, feedback depth, emphasis) that interact via unidirectional peer messaging. Crucially, **neither agent has state-write authority**; typed proposals pass through schema validation, authority checks, and deterministic arbitration, with the central orchestrator (Hub) alone committing session state.
2. **Empirical Evaluation Across 4 Rigorous Studies:**
   - **Experiment XA (Coordination & Ablation, 160 sessions/condition):** Demonstrates that adding agents changes difficulty trajectories in 100% of sessions (reducing reversals from 11.74 to 9.87) while committed scores remain 100% authoritative and transitions valid.
   - **Experiment XB (Fault Containment, 1,760 sessions):** Evaluates 11 fault classes (crashes, timeouts, NaN confidence, forbidden key injection, stale state, ungrounded plans). Shows 100% containment ceiling across all variants, but reveals that safeguards discriminate sharply: arbitration prevents guardrail bypass (38/40 bypassed without arbitration vs 0/40 with), while lexical grounding prevents ungrounded concept emphasis (40/40 leaked without check vs 0/40 with).
   - **Experiment XC (Threshold Sensitivity):** Confirms that setting the arbitration threshold $\tau=0$ collapses the Strategy Agent into a near-constant policy, isolating the effect of confidence gating from the guardrail layer.
   - **Experiment XD & RQ4 (Audit Corrections):** Rebuilds a flawed historical grounding audit, demonstrating that 17 prior rejections were evaluation artefacts, while disclosing that paraphrased unsupported credit is accepted in 57/57 cases.
3. **Rigorous Scientific Integrity:** Fully discloses that agents are rule-based, PPO is not multi-agent RL, evaluations use replayed evaluator outputs on 64 constructed answers, and no claims of human pedagogical gain or placement efficacy are made.

---

## 2. Technical Quality Assurance Status

- **Page Count:** **Exactly 20 pages** (complies with the maximum 20-page budget in the ADCoM 2027 CFP).
- **Bibliography:** Exactly 20 references, including foundational systems and dependability literature (Saltzer & Schroeder 1975, Avižienis et al. 2004, Wooldridge & Jennings 1995).
- **Claim Verification:** Automated verification script (`verification/verify_paper.py`) recomputes **69 out of 69 quantitative claims** directly from raw JSONL/CSV experiment logs; all 69 pass.
- **Double-Blind Compliance:** Automated audit (`scripts/blind_audit.py`) passes with **0 identifying hits** (no names, institutions, repository links, or project keywords in text, figures, or PDF metadata).
- **Typography & Layout:** All tables fit flush within text margins; 100% scalable Type 1 fonts embedded; zero margin overflows.

---

## 3. Four Concrete Discussion Items for Your Feedback

We specifically request your guidance on the following four decisions:

### Discussion Item 1: The Shared 64-Answer Dataset (Originality & Ethics)
- **Context:** Both this manuscript and a peer's concurrent paper evaluate models against the same 64 constructed answer payloads across 8 technical question categories.
- **The Issue:** While automated plagiarism tools (e.g. CrossCheck) report 0% text overlap, submitting two papers relying on the same unpublished dataset without formal attribution creates dual-submission / publication ethics risk under Springer and COPE guidelines.
- **Options for Discussion:**
  1. *Public Repository Archival (Recommended):* Upload the 64-answer evaluation suite to Zenodo or OSF with an open DOI. Both papers independently cite this benchmark as a shared, open evaluation dataset.
  2. *Cross-Citation / Disclosed Sister Submission:* Disclose in the submission cover letter that this paper evaluates multi-agent orchestration while the sister paper evaluates evaluator scoring validity.
  3. *Independent Dataset Generation:* Record a distinct evaluation set specifically for this multi-agent paper.

### Discussion Item 2: Conference Track Alignment
- **CFP Options:**
  - *Track 2: Agent-Native Development and Lifecycle Engineering* (**Recommended Primary Fit**): Focuses on agent architecture, orchestration, state contracts, and lifecycle fault tolerance.
  - *Track 5: Preemptive Agentic Security and Resilience* (Secondary Fit): Focuses on fault containment, circuit breakers, and adversarial/malformed input handling.
- **Question:** Does Track 2 best match the paper’s contribution, or does Track 5 provide a more targeted audience?

### Discussion Item 3: Merged-Agent Feasibility Study
- **Context:** We prepared a complete, pre-registered experimental protocol (`MERGED_AGENT_EXPERIMENT.md`) to empirically test whether Strategy and Coaching should be merged into a single agent.
- **Status:** The experiment was deliberately **not executed** to preserve baseline stability and avoid rushing unapproved code changes before your review.
- **Question:** Would you recommend executing this ~35-minute experiment for camera-ready inclusion, or is the current 20-page paper complete as-is with the design noted as future work?

### Discussion Item 4: Modesty and Scope of Claims
- **Context:** The paper maintains an unflinching limitations section (Section 9), explicitly stating that the system was tested on replayed outputs without live LLMs or human candidates.
- **Question:** Does the paper strike the right balance between rigorous engineering contribution and appropriate scientific humility?
