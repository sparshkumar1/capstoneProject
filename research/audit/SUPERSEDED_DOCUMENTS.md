# Register of Superseded & Historical Documents (DO NOT USE AS SOURCE OF CURRENT TRUTH)

**Audited Commit:** `9cfd34f`  
**Purpose:** Explicitly flag historical, monolithic, or obsolete documents to prevent accidental citation of superseded claims, ungrounded synthetic metrics, or deprecated system architectures.

---

## 1. Registry of Superseded Documents

| File Path | Original Purpose | Why It Is Superseded | Canonical Replacement | Historical Value / Notes |
|:---|:---|:---|:---|:---|
| `submission/manuscript/IEEE_TLT_MANUSCRIPT.md` | Monolithic draft for IEEE TLT | Conflates Paper 1, 2, and 3 into single draft; cites synthetic $\rho=0.9152$ and 204k steps | `research/papers/paper{1,2,3}/` | Historical snapshot of early monolithic submission attempt. |
| `submission/manuscript/paper_draft_ieee.md` | Duplicate of `IEEE_TLT_MANUSCRIPT.md` | Exact file content duplicate | `research/papers/paper{1,2,3}/` | Redundant copy. Safe to archive. |
| `docs/paper_draft_ieee_access.md` | IEEE Access draft | Unsplit manuscript; references abandoned monolithic structure | `research/papers/paper1_systems/` | Early systems-focused manuscript iteration. |
| `docs/paper_draft_ieee_toE.md` | IEEE ToE draft | Contains old evaluator numbers and synthetic multi-rater claims | `research/papers/paper2_evaluator/` | Early educational evaluator draft. |
| `final_prepaired_ieee_paper.pdf` | Compiled PDF of monolithic IEEE draft | Visual compilation of obsolete draft containing outdated tables | `research/papers/` | Compiled visual artifact for course submission. |
| `ablation/results/ratings_proxy.csv` | Synthetic proxy rater table | Synthetic proxy scores (0.05, 0.20, 0.55, 0.90) | `ablation/results/ratings_rater1.csv` | Pilot synthetic baseline. Never to be cited as human ratings. |
| `ablation/results/ratings_averaged.csv` | Average of human + synthetic proxies | Blends authentic educator with 3 Gaussian noise proxies | `ablation/results/ratings_rater1.csv` | Produced historical $\rho = 0.8358$. Superseded by pure human evaluation. |
| `docs/STAGE20_SUBMISSION_READINESS.md` | Readiness audit for old IEEE draft | Evaluates submission readiness of deprecated monolithic paper | `research/CANONICAL_SCIENTIFIC_TRUTH.md` | Historical stage gate record. |
| `docs/stage19_publication_audit.md` | Stage 19 claim revision table | Interim revision log from August 2026 | `research/audit/claim_audit.md` | Detailed changelog of claim refinements. |
| `docs/stage18_final_independent_audit.md` | Independent verification report | Pre-dates 205-test engineering suite and current 3-paper split | `research/audit/current_test_manifest.md` | Audit milestone documentation. |
| `docs/PREPAIRED_HOLY_GRAIL.md` | Monolithic project reference booklet | 54KB uncurated amalgamation of notes, logs, and stage snippets | `research/README.md` | Useful only as an archive of raw developer notes. |
| `docs/PREPAIRED_COMPLETE_BOOKLET.md` | Consolidated system documentation | Pre-dates multi-attempt WAL database and current Qwen containment | `research/CANONICAL_SCIENTIFIC_TRUTH.md` | Legacy comprehensive reference. |
| `INTERVIEW_PREPARATION_GUIDE.md` | Candidate-facing study guide | General DSA curriculum and conceptual questions | `data/questions/qns.json` | Student educational prep guide; non-authoritative for research. |

---

## 2. Invalidation Notice for Outdated Claims Found in These Files

When reading files listed in this register, **the following claims must be ignored**:
1. **IGNORE:** *"Evaluator achieves Spearman correlation $\rho = 0.9152$ against human raters."*  
   $\rightarrow$ **TRUTH:** $\rho = 0.9152$ is synthetic proxy data. The authentic human educator baseline is $\rho = 0.7400$ ($p < 0.001$).
2. **IGNORE:** *"Evaluator achieves composite correlation $\rho = 0.8358$ across 4 expert raters with $\alpha = 0.8255$."*  
   $\rightarrow$ **TRUTH:** This was an averaged composite of 1 human rater and 3 synthetic Gaussian noise proxies.
3. **IGNORE:** *"PPO policy converged over 204,800 training steps."*  
   $\rightarrow$ **TRUTH:** Current training harnesses run for 300,000 steps.
4. **IGNORE:** *"Static pre-flight AST filters eliminate 100% of malicious C code."*  
   $\rightarrow$ **TRUTH:** Empirical negative test SEC-02 bypassed static regex; containment is enforced by Linux kernel primitives (`--cap-drop=ALL`, `--net=none`, non-root UID).
