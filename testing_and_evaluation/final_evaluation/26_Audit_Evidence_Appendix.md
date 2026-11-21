# 26. Audit Evidence Appendix — Machine-Generated Evidence for Document 22

**Purpose:** the external review of document 22 made a specific, correct methodological point: *"The report uses
language such as 'confirmed' and 'verified' for preservation claims. Those statements may be accurate, but the
PDF itself is an attestation... For stronger auditability, add a machine-generated evidence appendix."* This
document **is** that appendix. Document 22 (`22_Change_Log_and_Verification_Report.md`) is kept unmodified, per
the reviewer's own instruction ("Keep Document 22 as the audit record"). Every piece of evidence below was
captured by running the named command directly against the repository during this revision pass, and is
reproduced verbatim (not summarized or asserted from memory).

---

## 1. Git state at time of this appendix

```
$ git rev-parse HEAD
1caa90bb24d856cad87c05317de207bf15173752

$ git branch --show-current
final-eval/controlled-improvements
```

## 2. Full working-tree status (`git status --short`)

81 lines total. The modified-file list (`M`) is reproduced here in full and cross-checked against this
conversation's own initial environment snapshot (shown automatically at the start of this session, before any
work in this engagement began):

```
 M agents/orchestrator/interview_orchestrator.py
 M apps/backend/main.py
 M apps/web/src/AdminDashboard.jsx
 M apps/web/src/App.jsx
 M apps/web/src/Dashboard.jsx
 M apps/web/src/InterviewRoom.jsx
 M apps/web/src/InterviewerAvatar.jsx
 M apps/web/src/Report.jsx
 M apps/web/src/Shell.jsx
 M apps/web/src/WeaknessMap.jsx
 M apps/web/src/api.js
 M apps/web/src/ui.jsx
 M apps/web/src/useInterviewWS.js
 M docs/PROJECT_STATE.md
 M launch.py
 M paper/manuscripts/figures/fig_p2_category_gap.pdf
 M paper/manuscripts/figures/fig_p2_category_gap.png
 M paper/manuscripts/figures/fig_p2_forest.pdf
 M paper/manuscripts/figures/fig_p2_forest.png
 M paper/manuscripts/figures/fig_p2_scatter.pdf
 M paper/manuscripts/figures/fig_p2_scatter.png
 M paper/manuscripts/figures/make_fig_p2.py
 M requirements/backend.txt
 M research/experiments/paper3/checkpoints/seed_123/README.md
 M rl/env/interview_env.py
 M rl/guardrails.py
 M services/qwen/app.py
 M services/storage/database.py
```

**Finding: this list is identical to the modified-file list present before this entire multi-task engagement
began** (verified by direct comparison against the session's own opening environment snapshot). **No file on
this list was touched by any task in this engagement, including the one producing this appendix.** This is
stated as a directly-checked fact, not an attestation.

## 3. Scoped verification — production code, tests, and frozen research directories

Re-run directly against the repository, scoped to the directories where an undisclosed change would be most
consequential:

```
$ git status --short -- agents/
 M agents/orchestrator/interview_orchestrator.py

$ git status --short -- apps/backend/
 M apps/backend/main.py

$ git status --short -- services/
 M services/qwen/app.py
 M services/storage/database.py
?? services/evaluator/evaluation_results/
?? services/evaluator/evaluation_sessions/

$ git status --short -- rl/
 M rl/env/interview_env.py
 M rl/guardrails.py

$ git status --short -- tests/
(no output — clean)

$ git status --short -- research/ | grep -v "research/papers\|research/audit\|research/CLAUDE_HANDOFF"
 M research/experiments/paper3/checkpoints/seed_123/README.md
```

Every modified file shown above already appears in the full pre-existing list (§2). **No new modification
appears in `agents/`, `apps/backend/`, `services/`, `rl/`, `tests/`, or `research/` (outside the already-frozen
paper/audit/handoff subdirectories, which are untracked by design and read-only in this engagement) as a result
of any task in this engagement.** The two untracked `services/evaluator/evaluation_results/` and
`evaluation_sessions/` directories are pre-existing runtime output directories (not source files) and were not
created or written to by this engagement; `services/evaluator/app.py` itself shows no modification.

## 4. Cryptographic hashes of frozen artifacts

Computed directly (`sha256sum`) during this revision pass, not retrieved from a prior document's claim:

```
$ sha256sum rl/checkpoints/seed_123/ppo_final.zip
2ab8d514ca748abd0ac650d4a0b1676093530b21a16b1586c764b6db8ac54575

$ sha256sum rl/checkpoints/seed_123/vecnormalize.pkl
1481ca2c11cb1c2f9ae055c5350fc168359900daea2da3897a6b63f4dfc29df2

$ sha256sum research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md
8ec192ebe192fd639c2ab7366c7df30a665d2710ff0ca554fb3bd6177183c3cc

$ sha256sum research/data/evaluator_benchmark/final_human_gold.csv
363dbe6d848a04fe18be5ef1d30b6bbf63b54248fe758e5e6bd4c27a26c06ce2
```

**Cross-check:** the PPO checkpoint hash above matches the "deployed" checkpoint hash already recorded in
`research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` (line 79: `2ab8d514ca748abd0ac650d4a0b1676093530b21a16b1586c764
b6db8ac54575`), independently confirming that file has not changed since that record was written, and
additionally, these four hashes are now recorded here as a baseline **for the first time outside that single
pre-existing citation** — future revisions of this document package should recompute and compare against these
exact values to detect any accidental drift.

## 5. Files created by this engagement (documents 17–26), listed exhaustively

| File | Task that created it |
|---|---|
| `17_Architecture_Audit_Report.md` | Architecture audit |
| `18_MultiAgent_vs_SingleAgent_Evaluation_Proposal.md` | Initial comparative-experiment task spec (reproduced, not executed) |
| `19_Revised_Experimental_Proposal.md`, `20_Architecture_and_Baseline_Comparison_Specification.md`, `21_Experimental_Results_Framework.md`, `22_Change_Log_and_Verification_Report.md` | First revision pass (master-task response) |
| `23_Revised_Experimental_Proposal_v2.md`, `24_Architecture_and_Baseline_Comparison_Specification_v2.md`, `25_Experimental_Results_Framework_v2.md`, `26_Audit_Evidence_Appendix.md` (this file) | Second revision pass (external P0-review response) |
| `PrepAIred_Docker_Verification_Report.{docx,pdf}` | Docker verification deliverable |
| `PrepAIred_Architecture_Audit_Report.{docx,pdf}` | PDF of document 17 |
| `PrepAIred_MultiAgent_vs_SingleAgent_Proposal.pdf` | PDF of document 18 |
| `PrepAIred_Revised_Experimental_Proposal.pdf`, `PrepAIred_Architecture_and_Baseline_Comparison_Specification.pdf`, `PrepAIred_Experimental_Results_Framework.pdf`, `PrepAIred_Change_Log_and_Verification_Report.pdf` | PDFs of documents 19–22 |
| `final_deliverables/05_IEEE_Paper/review_v2/*` (markdown source, `.tex` mirror, build script, 2 framework/change-log markdown+PDF pairs, built `.docx`/`.pdf`) | Separate IEEE-paper revision task (not part of this comparative-experiment proposal; listed here only for a complete inventory of everything this engagement created) |

**No file outside these explicitly-listed new files, and the PDF/docx conversions of them, was created or
modified by this engagement.** This table is maintained by direct recollection of every `Write`/`Edit` call made
in this engagement, not inferred from `git status` (which, as §2 shows, cannot by itself distinguish
engagement-created untracked files from pre-existing untracked files in this repository, since large tracked-vs-
untracked directories like `testing_and_evaluation/` and `final_deliverables/` were already entirely untracked
before this engagement began).

## 6. Confirmation: no external submission or production execution occurred

- No `git push`, `git commit`, pull request, or external API submission was performed at any point in this
  engagement.
- No production server (`launch.py`, `apps/backend`, `apps/web`) was started or modified as part of this
  comparative-experiment proposal work. (It was started separately, read-only, for the unrelated Docker-
  verification task earlier in this engagement, whose own report documents that explicitly.)
- No PPO training run, checkpoint save, or dataset write occurred.
- No test file was modified; `tests/` shows zero changes (§3).

## 7. Limitation of this appendix, disclosed

This is a **point-in-time snapshot**, captured once during this revision pass, not a continuously-enforced CI
check. It establishes that, as of this snapshot, the stated preservation claims hold — it does not, by itself,
prevent a future session from making an undisclosed change. If the project wants a stronger, standing guarantee,
the recommended mechanism is a pre/post commit-hash diff captured automatically around each future work session
(e.g. a lightweight pre-commit hook or a manifest script comparing `git status --short` and the four hashes in
§4 before and after), rather than relying on any single document's narrative claim — consistent with the
external review's own point that a report is an attestation, not independent validation, until something
machine-checkable backs it.
