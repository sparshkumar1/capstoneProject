# 13. Change and Content Mapping Report — Phase-3 Final Semester Report

**Purpose:** per the master prompt's deliverable requirements, this document records what was retained from
`revised_report_v5.pdf` (Phase-2, the master reference), which initial pages were incorporated, which
current-semester additions were included, which sections required modification (and why), and what remains
flagged for the user's attention.

**Preservation confirmation (stated once, governing this whole document):** `Details/revised_report_v5.pdf`,
`Details/Report initial Pages(Pg 1-10)/*`, `Details/Report-  Guidelines.pdf`, and
`final_deliverables/02_University_Project_Report/*` (the previously-generated current-semester report) were all
**read, never edited.** Every file in this deliverable is new, in a new folder
(`final_deliverables/07_Final_Semester_Report/`).

---

## 1. Source-to-requirement mapping (as requested by the master prompt, §5)

| Requirement | Source file | Action taken | Location in final report |
|---|---|---|---|
| Existing Phase-2 content, structure, depth | `revised_report_v5.pdf` (48 printed pages, 8 chapters, read in full) | Preserved as the narrative/rationale backbone for chapters with a direct Phase-2 equivalent; **not** copied where already-established fact-checking (see §3 below) found it inaccurate | Chapters 1, 5, 6, 7, 8, 9, 11 |
| Required initial pages | `Details/Report initial Pages(Pg 1-10)/*.docx` (4 blank templates, read in full via `python-docx`) | Placeholder structure and acknowledgement paragraph order reused directly; placeholders filled with the Phase-2 team/guide/SRN details, carried forward on the stated assumption this is the same team continuing into Phase-3 | Front Matter |
| Current-semester (Phase-3) verification work | `final_deliverables/02_University_Project_Report/*.md` (13 files, read in full) | **This was itself the single most important source for this document.** It had already independently re-verified the codebase against Phase-2's claims and made every correction this report needed — see §2 | Chapters 2, 3, 4, 10, and the corrected facts throughout 1, 5–9, 11 |
| University formatting | `Details/Report-  Guidelines.pdf` (5 pages, read in full) | Applied via the project's own existing, proven build script (`testing_and_evaluation/scripts/md_to_docx_report.py`), copied unmodified into this folder and re-pointed at these 13 chapter files | Entire document — see the Formatting Verification Report (document 14) |

## 2. The key finding that shaped this document's strategy

Before writing anything, every chapter of the previously-generated current-semester report
(`final_deliverables/02_University_Project_Report/`) was read in full. **That report's facts were found to
already be excellent** — it had already independently re-derived and corrected every discrepancy between
Phase-2's claims and the actual codebase (multi-agent → hub-and-spoke/single-controller architecture, 5-action →
3-action RL space, FAISS-based → rule-based question selection, FastAPI → Flask for the evaluator, the G5
guardrail-boundary fix, the real PPO training provenance, and the Qwen-never-scores finding), with every claim
traced to a stored test, log, or script. **The problem the master prompt identified — that this report "does
not follow the required university format" — was, on inspection, not primarily a formatting problem but a
depth problem**: several chapters (High-Level Design, Low-Level Design, System Design, Methodology,
Implementation) were written as terse, bulleted summaries, far shorter than Phase-2's flowing, rationale-rich
prose covering the same ground. This document's strategy follows directly from that finding: **preserve every
one of the current report's corrections and evidentiary citations; restore Phase-2's narrative depth and design
rationale around them.**

## 3. What was retained from `revised_report_v5.pdf`, and what was not

### 3.1 Retained (Phase-2 prose reused, directly or lightly adapted)

- Chapter 1's opening motivation paragraphs (static tools, LeetCode/HackerRank/InterviewBit framing) — reused near-verbatim.
- The full design-rationale prose for the evaluator's three components (why S1/S2/R are weighted as they are, why each component is "most useful" for a specific failure mode) — Chapter 8, §8.1.
- The full RL methodology narrative (MDP formulation, state-vector rationale, action-space description, reward-function breakdown, training-environment description) — Chapter 8, §8.2.
- The full guardrail-rationale prose (why G4 is highest priority, why G6 is lowest, the `nervous_expert` flag's purpose) — Chapter 6, §6.3.
- The full baseline-phase protocol description (why a cold-start phase is needed, the Q1/Q2/Q3 schedule, the disambiguation trigger) — Chapter 5, §5.5.
- The full audio-analysis sub-pipeline description (the four parallel sub-pipelines, their individual outputs, the confidence/hesitation aggregation logic) — Chapter 8, §8.4.
- The full FeedbackAgent methodology narrative (score decomposition, misconception detection rationale, communication-analysis signal breakdown, trend-tracking threshold rationale, content-analysis field distinctions) — Chapter 6, §6.4.
- The full orchestrator implementation narrative (concurrency safety rationale, dependency-injection rationale, state-management rationale, idempotent-termination rationale) — Chapter 6, §6.1, and Chapter 9, §9.1.
- The React frontend implementation narrative (voice recording, code editor, difficulty indicator, hint panel, session-report sections) and the Logger implementation narrative (turn-level/session-level logging, the replay-buffer rationale, graceful degradation) — Chapter 9, §9.5–§9.6.
- Chapter 7's limitations list and Chapter 11's closing-remarks framing — genuinely honest, self-reported content, reused as a foundation and extended.

### 3.2 Explicitly NOT retained, and why (the minimum-necessary-correction rule)

Per the master prompt's own allowance ("If you believe any existing section genuinely needs modification, first
determine whether the change is necessary... record it in the change log"), the following Phase-2 content was
**not** carried forward, because the already-completed Phase-3 verification work (§2 above) found it factually
incorrect:

| Phase-2 claim | Why not retained | Replaced with |
|---|---|---|
| "Multi-agent architecture," "autonomous agents," "seven autonomous sub-agents" (pervasive, e.g. Ch.1, Ch.3.1, Ch.7.1/7.4) | Found, on direct inspection, not to exist — no component calls another as a peer; confirmed independently twice (§10.13, §10.19 of this report) | "Specialised, orchestrator-coordinated architecture" throughout |
| Five-action RL space (Easier/Same/Harder/Hint/Follow-up), Table 4.3 | `agents/strategy/hybrid_orchestrator.py` hard-codes `Discrete(3)` and rejects any other action space | Three-action space; Hint/Follow-up described as guardrail/FeedbackAgent-triggered |
| PPO "trained over 500,000 simulated steps," seeds (42,123,777) | Does not trace to any stored artifact; contradicts the project's own canonical evidence record | 24,576 steps/seed, seeds {42,123,456,789,999}, per `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` |
| Evaluator microservice uses FastAPI (Table 3.1) | `services/evaluator/app.py` is a Flask application | Corrected to Flask throughout |
| Question selection retrieves from a "FAISS VectorStore" (Fig. 3.1, Fig. 4.2) | `agents/question_selector/question_selector.py` has zero FAISS/embedding dependency | Deterministic nearest-difficulty + topic-rotation, described accurately |
| Four-level evaluator fallback chain with named modules (`qwen_integration/evaluate_upgraded.py`, etc.) | These module paths do not exist anywhere in the repository | The real mechanism: a single R-gated S2-dampening rule |
| Qwen performs "partial-credit adjustment" on the score | No code path found to support this; Qwen's `final_score` field, where present, only echoes the evaluator's own value | Qwen confined to narrative text, hints, and follow-ups |
| Chapter 6.6's four-condition ablation study (specific p-values, 400 turns) | No matching stored artifact located; numeric style resembles a separately-identified, confirmed-fictional research draft | Replaced with the real, stored, five-seed Paper-3 ablation (Fixed 1.200 / Heuristic 0.473 / PPO 0.804 / PPO+guardrails 0.677 MAE) — Chapter 10, §10.19 |
| Chapter 6.1–6.3's calibration/fine-tuning MSE and Spearman figures | No matching stored artifact located for the specific numbers (the fine-tuning *methodology* — layer freezing, dual loss, hard-negative oversampling — is retained as directionally plausible, but the outcome numbers are not reproduced in this report pending that artifact search) | Not reproduced; flagged in Chapter 11 future work, item 4 |
| Abstract's "93.3% baseline calibration accuracy over 30 sessions" | No supporting stored artifact located anywhere in the repository | Replaced with the real, stored evaluator human-correlation result (ρ=0.38, 3 raters, 64 answers) |

## 4. Current-semester additions incorporated

Beyond what the previously-generated current report already contained, this document adds genuinely new
material from later stages of this same Phase-3 engagement, not available when that report was first written:

1. **Docker-dependent test closure** (Chapter 10, §10.18) — a live-daemon verification pass confirming all 19
   previously-blocked Docker-dependent tests pass, closing (not merely explaining) the gap left open in §10.9.
2. **Independent architecture audit** (Chapter 10, §10.19) — a second, differently-scoped inspection
   independently re-confirming the hub-and-spoke/single-controller classification and additionally discovering
   the live-orchestrator-vs-canonical-guardrail divergence, now disclosed in Chapter 10 §10.3's scope note and
   Chapter 11's limitations.
3. **Real RL/guardrail ablation evidence** (Chapter 10, §10.19) — the genuine, stored, five-seed Paper-3
   tracking-MAE table, replacing the unverifiable Phase-2 ablation.
4. **Real evaluator human-correlation evidence** (Chapter 10, §10.19) — ρ=0.38, replacing the unverifiable
   Phase-2 abstract figure.
5. **A proposed (not executed) architectural-comparison research design** (Chapter 10, §10.19; Chapter 11,
   future work item 3) — included and clearly labelled as a design artifact, not a completed experiment.

## 5. Sections that required modification, and the minimum-necessary-change rule applied

Every modification in §3.2 and §4 above was made only because continuing to state the original Phase-2 claim
would have been false, or because genuinely new, real evidence existed that materially changed what could
honestly be reported. No section was rewritten "to improve its language" alone; wording was changed only where
the underlying fact changed. Chapters 2, 3, 4, and 12 required no Phase-2-depth merge at all, since Phase-2 had
no direct equivalent for 2 and 4, and the existing current-report versions of 3 and 12 were already more
rigorous than Phase-2's own versions (live-verified citations, corrected author details).

## 6. Missing information flagged for the user — not invented

- **Project ID** (`PW26_UD05`) and the **team/guide/SRN details** in the front matter are carried forward from
  Phase-2 on the assumption that this is the same project continuing into Phase-3. **Please confirm or correct**
  if anything has changed.
- **PRS/HLD/LLD department-specific templates**, if any exist beyond the standard software-engineering
  structure used in Chapters 4–6, were not supplied in `Details/` and were not invented.
- **The two remaining unverified Phase-2 figures** (Chapter 6.1–6.3's calibration/fine-tuning outcome numbers)
  were not located in any stored artifact in this repository during this pass; a further, more exhaustive search
  (e.g. of Kaggle notebook exports, if any exist outside this repository) was not performed and is flagged as
  future work rather than resolved by omission or invention.
- **Figures** (Figure 3.1 architecture diagram, Figure 4.1/4.2 pipeline diagrams, Figure 5.1/5.2 UI screenshots)
  from Phase-2 are described in this report's prose but not reproduced as image files in this Markdown source;
  the existing architecture-audit diagram (`testing_and_evaluation/final_evaluation/17_Architecture_Audit_Report.md`)
  and the IEEE paper's figures are available as accurate, current replacements if the final formatted document
  requires inline figures, and should be inserted during final typesetting into the official template.
