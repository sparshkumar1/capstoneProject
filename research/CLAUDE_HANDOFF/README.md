# Claude Manuscript Handoff Package: Master Navigation & Instructions

**Date:** September 19, 2026  
**Status:** **AUTHORITATIVE EVIDENCE BASELINE**  
**Intended Recipient:** Claude (Manuscript Authoring Agent)  
**Primary Mandate:** Draft academic conference papers using **strictly verified Level 3 evidence** contained in this handoff directory.

---

## 1. Directory Structure

```
research/CLAUDE_HANDOFF/
├── README.md                                 # This navigation guide
├── MANUSCRIPT_AUTHORING_GUIDELINES.md        # Strict rules for terminology, claims, and formatting
├── CANONICAL_SCIENTIFIC_TRUTH.md             # Updated master scientific facts across Papers 1, 2, and 3
├── FINAL_RESEARCH_MANIFEST.md                # Human-readable manifest with hashes & commands
├── FINAL_RESEARCH_MANIFEST.json              # Machine-readable provenance manifest
├── CROSS_PAPER_CLAIM_EVIDENCE_MATRIX.csv     # 24 scientific claims with evidence and limitations
├── PAPER1_FINAL_REPORT.md                    # Systems, Security, Concurrency, Latency & Resilience
├── PAPER2_FINAL_REPORT.md                    # NLP Evaluator, Entailment Dampening & 64-Case Gold
├── PAPER3_FINAL_REPORT.md                    # Multi-Seed RL Difficulty Adaptation & Guardrails
├── PAPER3_FINAL_FREEZE.md                    # Permanent freeze record of Paper 3 metrics
├── summary_tables/                           # Curated machine-readable CSV result summaries
│   ├── paper1_summary_results.csv
│   ├── paper1_concurrency_results.csv
│   ├── paper1_latency_results.csv
│   ├── paper1_security_results.csv
│   ├── paper2_summary_results.csv
│   ├── paper2_ablation_results.csv
│   ├── paper2_adversarial_results.csv
│   ├── paper2_metamorphic_results.csv
│   ├── paper2_bootstrap_results.csv
│   ├── paper3_summary_results.csv
│   ├── paper3_baseline_results.csv
│   ├── paper3_ablation_results.csv
│   ├── paper3_seed_results.csv
│   └── paper3_convergence_results.csv
└── audits/                                   # Key forensic provenance and audit reports
    ├── PAPER2_MODEL_PROVENANCE_GATE.md       # Proof of off-the-shelf CrossEncoder
    ├── HUMAN_GATE_3_COMPLETION.md            # Proof of 64-case human gold benchmark
    ├── adversarial_threshold_provenance.md   # Provenance of 0.35/0.40 engineering thresholds
    ├── threat_model.md                       # Comprehensive 7-category threat model
    ├── rl_state_alignment.md                 # Provenance of 6D state representation
    ├── PAPER1_EXECUTION_COMPLETION.md        # Paper 1 signoff
    ├── PAPER2_EXECUTION_COMPLETION.md        # Paper 2 signoff
    └── PAPER3_EXECUTION_COMPLETION.md        # Paper 3 signoff
```

---

## 2. Priority Reading Order for Drafting

When drafting manuscripts for Papers 1, 2, or 3, follow this exact sequence:

1. **Mandatory Rules:** Read [`MANUSCRIPT_AUTHORING_GUIDELINES.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/CLAUDE_HANDOFF/MANUSCRIPT_AUTHORING_GUIDELINES.md) first to understand forbidden claims, required phrasing, and statistical boundaries.
2. **Canonical Scientific Truth:** Read [`CANONICAL_SCIENTIFIC_TRUTH.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/CLAUDE_HANDOFF/CANONICAL_SCIENTIFIC_TRUTH.md) for master parameters, scoring equations, and verified baselines.
3. **Claim Matrix:** Check [`CROSS_PAPER_CLAIM_EVIDENCE_MATRIX.csv`](file:///c:/Users/spars/Downloads/PrepAIred/research/CLAUDE_HANDOFF/CROSS_PAPER_CLAIM_EVIDENCE_MATRIX.csv) to ensure every planned claim has an exact supporting file.
4. **Target Paper Final Report:** Read the respective report (`PAPER1_FINAL_REPORT.md`, `PAPER2_FINAL_REPORT.md`, or `PAPER3_FINAL_REPORT.md`).
5. **Exact Numbers:** Extract numerical values and confidence intervals directly from `summary_tables/`.

---

## 3. Strict Prohibitions for Claude

- ❌ **Do NOT cite superseded historical numbers:**
  - Never cite $\rho = 0.8358, 0.9152, 0.7400$, or $0.6975$ as the final Paper 2 evaluator correlation. The sole canonical Paper 2 correlation is **$\rho = 0.3812$** ($N=64$).
  - Never cite $t = -195.46$ or $d = 87.41$ as the Paper 3 effect size. The valid session-level effect size is **Cohen's $d \approx 0.87$** ($p < 0.001$).
  - Never cite $\text{MAE} = 0.000$ or $1.000$ as the Paper 3 fixed baseline. The mathematically correct fixed baseline is **$\text{MAE} = 1.200$**.
- ❌ **Do NOT claim universal superiority or invulnerability:**
  - Do NOT claim Docker is an "inviolable" security boundary. It is **defense-in-depth OS process containment**.
  - Do NOT claim the system is "universally fault tolerant". Frame as: **"All 10 evaluated fault scenarios recovered cleanly."**
  - Do NOT claim PPO is universally superior to heuristics. The deterministic heuristic achieves faster tracking ($\text{MAE} = 0.473$ vs $0.677$); PPO provides lower difficulty volatility ($0.088$ vs $0.160$).
- ❌ **Do NOT claim human classroom learning gains:** All RL evaluations were conducted in simulation across synthetic personas.
