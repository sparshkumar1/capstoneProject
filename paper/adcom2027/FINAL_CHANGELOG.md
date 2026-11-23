# PREPAIred — ADCOM 2027 AIS
# Final Scientific & Editorial Changelog

**Target Conference:** ADCOM 2027 (Springer CCIS)  
**Track:** Track 2 — Agent-Native Development and Lifecycle Engineering  
**Baseline Git Commit:** `2014e43` (Archived at `paper/adcom2027/manuscript_versions/main_baseline_2014e43.tex`)  
**Intermediate Commit:** `4b2399c` (Initial diverse-grid RL and evaluator boundary additions)  
**Final Active Candidate:** `paper/adcom2027/manuscript/main.tex` (Archived at `paper/adcom2027/manuscript_versions/main_revised_v2.tex`)  
**Compiled Candidate Binary:** `paper/adcom2027/ADCOM2027_candidate_revised.pdf` (13 pages)  

---

## 1. Itemized Record of Corrections

### Change 1: PPO Superiority Qualification (Abstract & Section 5.2)
- **Files:** `paper/adcom2027/manuscript/main.tex:20, 129`
- **Rationale:** The raw evaluation data across 5 training seeds shows that while Seeds 42 (0.3092), 123 (0.3165), 456 (0.3128), and 789 (0.4110) outperform the heuristic baseline (0.4728), Seed 999 ties the heuristic baseline at 0.4728. Phrasing that claimed unconditional superiority across all seeds was scientifically inaccurate.
- **Before (Commit `4b2399c`):**
  > *"reducing tracking error from 0.677 to 0.365 (outperforming heuristic baselines by 22.9%)."*
  > *"This significantly outperformed the fixed policy (MAE 1.2000), the baseline PPO (MAE 0.6772 ± 0.0053, a 46.2% error reduction), and the heuristic rule baseline (MAE 0.4728, a 22.9% error reduction)."*
- **After (Final Candidate):**
  > *"reducing mean tracking error across five seeds from 0.677 to 0.365 (outperforming the heuristic baseline on four of five seeds and tying on one, a 22.9% mean error reduction)."*
  > *"achieved lower mean simulated difficulty-tracking error across five seeds ($0.3645 \pm 0.0662$ vs. $0.4728$ heuristic, a $22.9\,\%$ mean error reduction), with four seeds achieving lower error ($0.3092$, $0.3165$, $0.3128$, $0.4110$) and one tying the heuristic ($0.4728$). Both outperformed the fixed policy (MAE $1.2000$) and baseline PPO (MAE $0.6772 \pm 0.0053$, a $46.2\,\%$ error reduction)."*
- **Supporting Evidence:** `research/paper_strengthening/results/e1_dev_eval/e1_dev_eval_summary.json`.

---

### Change 2: Extended Training Budget Degradation (Section 5.2 & Section 7)
- **Files:** `paper/adcom2027/manuscript/main.tex:129, 191`
- **Rationale:** Quadrupling the training budget from 24,576 to 98,304 timesteps resulted in tracking error degrading from 0.3645 to $0.3994 \pm 0.0301$. This needed to be disclosed as an observed simulation phenomenon and framed as a hypothesis (entropy decay / policy drift) rather than an unverified universal law.
- **Added Text:**
  > In Section 5.2: *"Extending the training budget to 98,304 timesteps degraded simulation tracking ($0.3994 \pm 0.0301$); we hypothesize policy drift and entropy decay against the conservative oracle reward rather than an intrinsic convergence bound."*
  > In Section 7: *"(8)... the tracking degradation observed under extended training (98k steps) is a simulation observation where entropy decay and policy drift are plausible hypotheses, and live human candidate interaction remains future work."*
- **Supporting Evidence:** `research/paper_strengthening/results/e1_dev_eval_extended/e1_dev_eval_summary.json`.

---

### Change 3: Clarification of Candidate Pacing Clock vs. Real Sockets (Section 4.1 & Section 5.5)
- **Files:** `paper/adcom2027/manuscript/main.tex:75`, `paper/adcom2027/manuscript/e5_section.tex:1`
- **Rationale:** Earlier drafts referenced "modelled candidate pacing", which created ambiguity about whether the network calls were simulated or real. Revisions explicitly distinguish between the injected breaker clock and real HTTP socket calls.
- **Before:**
  > *"E2 and E5 use real sockets to a local server bound to the hard-coded service address with real timeouts."*
  > *"The breaker's clock was advanced by a pacing P after each turn to model candidate think time, while the HTTP timeouts stayed real..."*
- **After:**
  > *"E2 and E5 use \emph{real sockets} to a local server bound to the hard-coded service address with real timeouts; in E5, pacing intervals ($P \in \{30, 60, 120\}$\,s) advance the breaker clock to model candidate think time between turns while HTTP transport timeouts remain real sockets."*
  > *"The breaker's clock was advanced by an injected pacing clock $P \in \{30, 60, 120\}$\,s after each turn to model candidate think time, while HTTP transport calls and timeouts executed against real sockets (Table~\ref{tab:e5})."*
- **Supporting Evidence:** `paper/adcom2027/experiments/e5_circuit_breaker.py`, `paper/adcom2027/results/e5_circuit_breaker.json`.

---

### Change 4: PPO Observation Space vs. Mutated Keys Discrepancy
- **Files:** `paper/adcom2027/manuscript/main.tex:45`
- **Rationale:** The code observation space is 6-dimensional (`[perf, avg_perf, conf, hes, progress, difficulty]`), whereas 14 represents the count of session dictionary keys mutated by `DifficultyPolicy`. The earlier draft erroneously claimed a "14-dimensional continuous state vector".
- **Before:**
  > *"The policy observes a 14-dimensional continuous state vector capturing rolling candidate performance..."*
- **After:**
  > *"The policy observes a 6-dimensional continuous state vector capturing turn performance, running average performance, speech confidence, hesitation, interview progress and current difficulty, and chooses discrete difficulty step adjustments in $\{-1, 0, +1\}$."*
- **Supporting Evidence:** `rl/env/interview_env.py:159, 233`, `paper/adcom2027/results/trace_state_writes.json`.

---

### Change 5: TeX Compilation and Font Expansion Resolution
- **Files:** Environment & `ADCOM2027_candidate_revised.pdf`
- **Rationale:** `latexmk` failed under Ubuntu with `! pdfTeX error (font expansion): auto expansion is only possible with scalable fonts` because `microtype` requires Type 1 scalable Computer Modern fonts.
- **Resolution:** Installed `cm-super` Type 1 fonts package in the WSL environment, enabling full compilation of `main.tex` into `paper/adcom2027/ADCOM2027_candidate_revised.pdf` (13 pages).
