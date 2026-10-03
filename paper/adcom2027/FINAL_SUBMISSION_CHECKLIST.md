# PREPAIred — ADCOM 2027 AIS
# Final Submission-Readiness Checklist & Author Action Plan

**Conference:** 31st International Conference on Advanced Computing and Communications (ADCOM 2027)  
**Theme:** Agentic Information Systems (AIS)  
**Submission Deadline:** 15 October 2026 (Live verified on 2026-10-03 from official CFP)  
**Submission Portal:** Microsoft CMT (`https://cmt3.research.microsoft.com/ADCOM2027`)  
**Format:** Springer CCIS (Lecture Notes in Computer Science class `llncs.cls`)  
**Recommended Primary Track:** Track 2 — Agent-Native Development and Lifecycle Engineering  
**Recommended Secondary Track:** Track 5 — Preemptive Agentic Security and Resilience  

---

## 1. Compliance Verification Checklist

- [x] **Page Budget:** Exactly 13 pages (Maximum allowable for Springer CCIS regular papers is **20 pages**).
- [x] **Template & Class:** Springer `llncs.cls` (v2.21), `runningheads`, `splncs04.bst`.
- [x] **Double-Blind Anonymity (Source & PDF):**
  - Author and institution blocks blinded (`\author{Anonymous Author(s)}`, `\institute{Anonymous Institution}`).
  - Running headers blinded (`Anonymous` / `Mechanism ablation of a hub-orchestrated LLM pipeline`).
  - Automated keyword scan: Zero occurrences of `sparsh`, `github`, `university`, `capstone`, or external URL links in `.tex`, `.bib`, or PDF metadata.
  - Document metadata: Clean / blank author and affiliation tags.
- [x] **Abstract Quality & Length:**
  - Length: 222 words (Within Springer CCIS 150–250 word requirement).
  - Scope: Accurately summarizes write-authority tracing, E1 mechanism ablation, E4 strict fail-closed contract, E5 circuit-breaker latencies, and persona-diverse PPO retraining with qualified 5-seed metrics.
- [x] **Experimental Evidence & Numbers:**
  - 100% of reported numbers trace directly to raw artifact ledgers (`trace_state_writes.json`, `e1_runs.jsonl`, `e4_runs.jsonl`, `e5_circuit_breaker.json`, `e1_dev_eval_summary.json`).
  - Automated verification script (`verify_adcom.py`): **71 PASS, 0 FAIL**.
- [x] **Citations & Bibliography:**
  - 14 cited references in `refs.bib`, all formatted per `splncs04.bst`.
  - Zero uncited entries in bibliography; zero undefined citation keys in text.
- [x] **Figure & Table Integrity:**
  - Figure 1: Architectural diagram showing measured write authority (vector PDF).
  - Figure 2: Difficulty trajectories across 25 turns comparing shipped, unshielded, and heuristic variants (vector PDF).
  - Tables 1–7: All referenced sequentially in text; all numerical cells match audited macros.

---

## 2. Author Action Plan for Conference Submission

When preparing the final submission on Microsoft CMT, the authors should execute the following steps:

1. **Upload File Selection:**
   - **CRITICAL:** Upload [`paper/adcom2027/ADCOM2027_candidate_revised.pdf`](file:///C:/Users/spars/Downloads/PrepAIred-recovery-review/paper/adcom2027/ADCOM2027_candidate_revised.pdf) (13 pages, SHA-256 `f6d3c15cb...`).
   - **DO NOT UPLOAD:** The older `ADCOM2027_submission_blind.pdf` (12 pages), which lacks the retrained PPO and evaluator cross-validation results.
2. **CMT Track Selection:**
   - Primary: **Track 2: Agent-Native Development and Lifecycle Engineering**
     *(Matches the paper's focus on orchestration contracts, invariant testing, and simulation-based RL controller training).*
   - Secondary (if permitted): **Track 5: Preemptive Agentic Security and Resilience**
     *(Matches fault-injection ablation, fail-closed contracts, and circuit-breaker DOS resilience).*
3. **Subject Areas:**
   - Select: *Multi-Agent Systems*, *Agent Lifecycle Engineering*, *Fault Injection & Dependability*, *Reinforcement Learning*.
4. **CMT Metadata Entry:**
   - Title: *Which Coordination Mechanisms Keep the Record Faithful? Fault-Injection Ablation of a Hub-Orchestrated, LLM-Assisted Interview-Preparation System*
   - Abstract: Copy verbatim from [`paper/adcom2027/manuscript/main.tex`](file:///C:/Users/spars/Downloads/PrepAIred-recovery-review/paper/adcom2027/manuscript/main.tex) (Lines 20–22).
   - Author List: Add real authors in the CMT portal (CMT handles double-blind blinding for reviewers automatically; ensure the uploaded PDF contains only anonymous placeholders).
5. **Repository Synchronization (Optional):**
   - The current repository working tree on `phase3/engineering` contains uncommitted modifications to `main.tex` and `e5_section.tex`, and untracked backups in `paper/adcom2027/manuscript_versions/`.
   - If desired, author may run:
     ```bash
     git add paper/adcom2027/manuscript/main.tex paper/adcom2027/manuscript/e5_section.tex paper/adcom2027/ADCOM2027_candidate_revised.pdf
     git commit -m "docs(adcom2027): finalize revised manuscript and compiled candidate PDF with seed-qualified PPO results"
     ```

---

## 3. Disclosed Limitations & Boundary Conditions

Reviewers should be aware of the explicit boundary conditions established in Section 7 of the manuscript:
1. **Replay Fixture:** The fault campaigns used a 64-answer benchmark fixture; the replay candidate does not improve on follow-ups.
2. **Simulation Evaluation:** Adaptive difficulty policies were evaluated in simulation across 5 personas $\times$ 5 seeds; live human candidate trials remain future work.
3. **Evaluator Length Confound:** CrossEncoder scores exhibit a known length correlation ($\rho = 0.6594$), which drops to partial $\rho = 0.2434$ when controlling for word count.
4. **Mock Generative Transport:** Generative LLM responses were served via deterministic templates and local socket mocks during the fault campaigns.
