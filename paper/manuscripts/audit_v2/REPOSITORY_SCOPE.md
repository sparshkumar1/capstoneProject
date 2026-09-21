# REPOSITORY SCOPE (audit-v2 pass, 2026-09-21)

## 1. Repository state
| Check | Before | After |
|---|---|---|
| `git rev-parse HEAD` | `11b7fe6e4c4cfedbd5a05c7de8aab0cd2fba1e0f` (branch `workspace/human-eval-clean-push`) | unchanged |
| `git status --short` entries | 55 | 55 (identical list; `diff` of before/after empty) |
| `git diff --check` | exit 0 (only pre-existing LF→CRLF warnings on 10 tracked files edited in earlier passes) | exit 0, same warnings |
| Tracked files modified by this pass | — | 0 (the 34 modified tracked files pre-date this pass) |
| `paper/manuscripts/` files | 23 | 81 (incl. this file); all inside the already-untracked `paper/` |
No commit, push, tag, freeze, build or submission was performed.

## 2. What was audited
- The three first-draft manuscripts (`paper*/manuscript_v1_archive.md` = exact copies of the first drafts) and their support files (ledgers, reviewer audits, limitations checklists, venue notes, inventories, `PAPER2_HIGH_RISK_REVIEW.md`), plus `cross/*` reports.
- Frozen evidence, read-only, for every re-checked claim: `research/confirmatory/X1/{PROTOCOL_*, X1*_RESULT_NOTE.md, results/x1c, x1c_v2}`, `research/results/paper2/*`, `research/analysis/phase1/x2_a/*`, `research/confirmatory/X2-B/results/*`, `research/confirmatory/X3-A/results/*`, `research/analysis/x3a_o7/results/*`, `research/analysis/phase1/x3_0/*`, `research/audit/P0_4_GUARDRAIL_FORENSIC.md`, `P0_7_HUMAN_ETHICS_FORENSIC.md`, `research/evidence/final/*`, `research/literature/claude_web_research/QUOTE_AUDIT.md`.
- Official venue pages (fetched 2026-09-21): icetc.org (home, submission), easychair.org/cfp/ICETC2026, ieee-edusociety.org event page, 2027.hci.international (deadlines, papers, AIS), atis2026.com, sigapp.org SAC 2027 (home, tracks), IEEE Author Center submission policies; Docker seccomp documentation.
- References through the arXiv and Crossref APIs (existence and metadata).

## 3. Unavailable or unverified
- IEEE MLNLP 2026 official site (certificate failure), IEEE AIEI 2027 site; SAC official page-limit/blind statements (only third-party track pages seen); ICETC blind status, registration fees (all venues), remote participation; Springer policy page itself (summaries only); Antigravity review report (not in the repository); any LaTeX/Word template; any second human reviewer.
- ChatGPT review of the drafts: not received.

## 4. Historical (not used as evidence)
`research/CANONICAL_SCIENTIFIC_TRUTH.md` and other superseded documents named in `CLAUDE.md`; the first-draft support files `paper*/claim_ledger.md`, `inventory.md`, `reviewer_attack_audit.md`, `venue_fit_notes.md`, and `cross/{CROSS_PAPER_OVERLAP_REPORT, FINAL_MANUSCRIPT_AUDIT, VENUE_FIT_MATRIX}.md` remain as records of the first pass; where they conflict with v2 (table and reference counts in the inventories; "zero shared references" in the overlap report; ICETC/SAC facts in the v1 venue files; Paper 2 wording in `claim_ledger.md`/`reviewer_attack_audit.md`), the v2 files govern: `paper*/claim_ledger_v2.md`, `audit_v2/*`, `cross/VENUE_FIT_MATRIX_V2.md`, `cross/FINAL_THREE_PAPER_AUDIT_V2.md`. The v1 inventories were not regenerated (v2 counts: P1 14 references / 4 tables / 1 figure; P2 16 / 6 / 3; P3 14 / 4 / 3).

## 5. Frozen
Everything under `research/` (results, protocols, tags, checkpoints, manifests, audits), `rl/checkpoints/*`, `ablation/results/*`, benchmark files. None was written to.

## 6. Generated during this pass (all new, under `paper/manuscripts/`)
- **Manuscripts (edited in place; v1 archived):** `paper1/manuscript.md` (rewritten, v2), `paper2/manuscript.md` (38 edits), `paper3/manuscript.md` (26 edits + follow-ups); archives `paper*/manuscript_v1_archive.md`; `paper2/PAPER2_HIGH_RISK_REVIEW.md` (four safe-wording cells and the header updated).
- **Claim ledgers v2:** `paper1/claim_ledger_v2.md`, `paper2/claim_ledger_v2.md`, `paper3/claim_ledger_v2.md`; `paper1/P1_PAGE_ECONOMY_REPORT.md`.
- **Figures and provenance:** `figures/` (7 figures as PDF and PNG, 3 scripts, `_style.py`), `cross/FIGURE_PROVENANCE.md`.
- **Audit files:** `audit_v2/` — `P1_INDEPENDENT_AUDIT.md`, `P2_INDEPENDENT_HIGH_RISK_AUDIT.md`, `P3_INDEPENDENT_AUDIT.md`, `CROSS_PAPER_AUDIT.md`, `REFERENCE_AUDIT.md` (+ `reference_audit_p1/p2/p3.md`), `STATISTICS_LANGUAGE_AUDIT.md`, `CLAIM_LANGUAGE_AUDIT.md`, `FIGURE_DECISION.md`, `VENUE_GATE_AUDIT.md`, `AI_DISCLOSURE_AUDIT.md`, this file; helper scripts `_apply_p2_edits.py`, `_apply_p3_edits.py`, `_p2_swap_figs.py`, `_make_icetc_port.py`, `scan_language.py`, `overlap_scan.py` (they record exactly which edits were applied and how scans were run).
- **Venue files:** `venue/icetc2026/` (`ICETC_PORT_MANUSCRIPT.md`, `ICETC_CHECKLIST.md`, `ICETC_VENUE_FACTS.md`, `ICETC_PAGE_BUDGET.md`), `venue/atis2026/ATIS_FIT_MEMO.md`, `venue/hcii2027/` (`HCII_AIS_PROPOSAL_800w.md`, `HCII_FULL_PAPER_VENUE_NOTES.md`), `venue/paper2/` (`PAPER2_SUBMISSION_GATE.md`, `PAPER2_VENUE_GATE.md`).
- **Cross files:** `cross/FINAL_THREE_PAPER_AUDIT_V2.md`, `cross/VENUE_FIT_MATRIX_V2.md`, `cross/AI_USE_DISCLOSURE_DRAFT.md`, `cross/FIGURE_PROVENANCE.md`.

## 7. Read-only computations performed (descriptive; none creates a new scientific conclusion)
Under-scored count and category means from the case-level file; `gold_method` counts; override-direction tally from the stored turn log; SEC-05 execution time versus wall time; Spearman recomputed from the stored case-level scores only to confirm the stored 0.3812; per-run status identity in `results.csv`. The evaluation-time Same share was **not** computed.
