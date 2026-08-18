# Final Folder Structure

This is the cleaned, maintained structure for the PrepAIred repo.
It keeps the source files that are actively used by the app, tests, docs, and runtime services.

## Root

```text
PrepAIred/
├─ launch.py
├─ pyproject.toml
├─ README.md
├─ CHANGELOG.md
├─ .env.example
├─ requirements/
│  ├─ base.txt
│  ├─ backend.txt
│  ├─ evaluator.txt
│  ├─ qwen.txt
│  ├─ rl.txt
│  └─ dev.txt
├─ apps/
├─ agents/
├─ services/
├─ rl/
├─ data/
├─ docs/
├─ tests/
└─ research/
```

## Apps

```text
apps/
├─ backend/
│  ├─ main.py
│  └─ .env.example
└─ web/
   ├─ package.json
   ├─ package-lock.json
   ├─ vite.config.js
   ├─ index.html
   ├─ .eslintrc.cjs
   └─ src/
      ├─ App.jsx
      ├─ App.css
      ├─ main.jsx
      ├─ contexts.jsx
      ├─ api.js
      ├─ servicesApi.js
      ├─ useInterviewWS.js
      ├─ useVoiceRecorder.js
      ├─ InterviewRoom.jsx
      ├─ InterviewRoom.css
      ├─ InterviewerAvatar.jsx
      ├─ InterviewerAvatar.css
      ├─ Login.jsx
      ├─ Login.css
      ├─ TopicSelector.jsx
      ├─ TopicSelector.css
      ├─ Topbar.jsx
      ├─ ThemeToggle.jsx
      ├─ FeedbackCard.jsx
      ├─ FeedbackCard.css
      ├─ Report.jsx
      ├─ Report.css
      ├─ ScoreRing.jsx
      ├─ DifficultyTracker.jsx
      ├─ MonacoEditor.jsx
      ├─ TruthEarIntegration.jsx
      ├─ WaveformBar.jsx
```

## Agents

```text
agents/
├─ audio/
│  ├─ audio_features.py
│  ├─ audio_io.py
│  ├─ confidence_scorer.py
│  ├─ hesitation_scorer.py
│  ├─ main.py
│  ├─ nlp_analyzer.py
│  ├─ output_formatter.py
│  ├─ recorder.py
│  ├─ rl_state_vector.py
│  ├─ tone_analyzer.py
│  └─ transcriber.py
├─ coding_executor/
│  ├─ coding_executor.py
│  └─ sandbox_policy.py
├─ orchestrator/
│  ├─ feedback_agent.py
│  ├─ interview_orchestrator.py
│  └─ logger.py
├─ question_selector/
│  └─ question_selector.py
├─ strategy/
│  └─ hybrid_orchestrator.py
├─ timing/
│  └─ timer.py
└─ validation/
   └─ score_validator.py
```

## Services

```text
services/
├─ evaluator/
│  ├─ app.py
│  ├─ assets/
│  │  ├─ logic_metadata.pkl
│  │  ├─ logic_vectors.faiss
│  │  ├─ qns.json
│  │  └─ rubrics.json
│  └─ models/
│     ├─ 1_best_model_zip/
│     └─ tuned_model2/
└─ qwen/
   ├─ app.py
   ├─ requirements_new.txt
   └─ models/
```

## RL

```text
rl/
├─ checkpoints/
├─ env/
├─ logs/
├─ rl_final/
└─ training/
```

## Data

```text
data/
├─ questions/
│  └─ qns.json
├─ rubrics/
│  └─ rubrics_final_clean.json
├─ sessions/
├─ reports/
└─ vector_store/
```

## Docs

```text
docs/
├─ architecture/
│  └─ CORRECTED_ARCHITECTURE.md
├─ diagrams/
│  └─ corrected_architecture.md
├─ paper_draft_ieee.md
├─ paper_draft_ieee_filled.md
└─ PR_SUMMARY.md
```

## Tests

```text
tests/
├─ unit/
│  └─ test_orchestrator.py
├─ integration/
└─ ...
```

## Research

```text
research/
├─ papers/
│  ├─ paper_aied_multiagent_feedback.md
│  ├─ paper_rl_adaptive_assessment.md
│  └─ paper_systems_agentic_architecture.md
└─ capstone/
   ├─ PrepAIred_Capstone_Report_Phase2.md
   └─ *.docx
```

## Kept Runtime / Generated Folders

These stay in the repo working tree but are not part of the source-of-truth layout:

- `.venv/`
- `apps/web/node_modules/`
- `apps/web/dist/`
- `__pycache__/` folders
- `logs/`
- `orchestrator_logs/`

## Reproducibility

- **Toy mode**: Run `python tools/toy_mode.py` to reproduce key analysis and figures using synthetic ratings (no large models required). See `docs/REPRODUCIBILITY_APPENDIX.md` for details.

## Large artifacts

- Model binaries, FAISS indices and other large artifacts are excluded from the repository by default and should be hosted externally or tracked via Git LFS. See `docs/GIT_LFS_MIGRATION.md` for migration instructions and recommended patterns.
- `training_logs/`
