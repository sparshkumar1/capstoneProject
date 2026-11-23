# PrepAIred — Architecture and Modules Audit

Scope: read-only code inspection of `agents/orchestrator`, `agents/audio`, `services/evaluator`,
`agents/coding_executor`, `apps/backend`, `apps/web`, `data/prepaired.db`, `launch.py`, and
`requirements/*.txt`. All line numbers refer to file contents as read on 2026-11-13.

Tagging key: **VERIFIED FACT** (cites file:line/function), **OBSERVATION** (from a command/output),
**INTERPRETATION** (analysis), **RECOMMENDATION**, **UNKNOWN** (could not determine — stated explicitly).

---

## 1. `agents/orchestrator/interview_orchestrator.py`

**VERIFIED FACT.** File is 2299 lines. Module docstring (lines 1–15) describes it as "runtime
controller for a single interview session," one instance per session stored in a `SESSIONS[sid]`
dict owned by `apps/backend/main.py`. Class `InterviewOrchestrator` (line 118) is the sole class in
the file.

### 1.1 Construction and dependency wiring
- Lines 26–72: sub-agents (`HybridOrchestrator` from `agents.strategy.hybrid_orchestrator`,
  `QuestionTimer` from `agents.timing.timer`, `ScoreValidator` from `agents.validation.score_validator`,
  `SessionLogger` from `agents.orchestrator.logger`, `FEEDBACK_AGENT` from
  `agents.orchestrator.feedback_agent`) are imported behind `try/except ImportError` guards, each
  setting a `_READY` boolean. **INTERPRETATION**: this is a deliberate degrade-gracefully pattern —
  if any sub-agent module is missing/broken, the orchestrator still constructs and falls back to
  simpler logic (see §1.4 "Non-RL Recovery Path").
- `__init__` (lines 125–261) takes `session_id`, `candidate`, `config`, `evaluator_fn`,
  `select_questions_fn`. If `select_questions_fn` is not injected, it lazily imports
  `apps.backend.main.select_questions` (line 139) — i.e., the orchestrator has a soft dependency
  back on the backend module.
- Session state is a single `self._state: dict` (lines 206–261) holding ~45 keys: question
  queue/index, current/start difficulty, RL/baseline bookkeeping (`baseline_min_questions`,
  `rl_enabled`, `current_difficulty`), scores/answers histories, topic performance, coding
  performance, timing, etc. **INTERPRETATION**: this dict is the de-facto session schema; there is
  no separate dataclass/schema definition, so correctness depends on every writer agreeing on key
  names (error-prone but consistent with the "guarded sub-agent" style).
- `interview_mode` normalization (lines 167–174): `"baseline_rl"`/`"demo"` aliases collapse to
  `"demo_rl"`; `num_questions >= 15` also forces `"demo_rl"`. **VERIFIED FACT**.

### 1.2 Baseline-then-RL difficulty pipeline
- `_adapt_difficulty` (lines 1576–1716) is the central decision function, called after every
  scored turn. Two phases:
  1. **Baseline warm-up** (lines 1587–1639): for `demo_rl` mode or `baseline_min_questions > 0`,
     difficulty is set deterministically by `_baseline_phase_difficulty` (Q1=easy(2), Q2+=mid(3),
     lines 1302–1304) until `_baseline_established` (lines 1290–1300) says the signal is stable
     (≥3 answers, or 2 answers with a strong/consistent signal). RL is explicitly disabled during
     this phase (`self._state["rl_status"] = "baseline_warmup"`, line 1590).
  2. **RL/guardrail phase** (lines 1642–1716): if `self._strategy` (a `HybridOrchestrator`) is
     `ready` and `is_compatible`, `self._strategy.suggest(...)` (line 1654) supplies the raw PPO
     action. If not ready, a **"Non-RL Recovery Path"** heuristic kicks in (lines 1661–1675,
     explicitly commented "operational continuity only, not RL intelligence"): score>0.8→Harder,
     score<0.4→Easier, else Same. Guardrails `_apply_guardrails` (G4→G1→G2→G3/G5→G6, lines
     1529–1573) are applied unconditionally on top of either source, and can override the chosen
     action (e.g., G4: perf<0.30 and hesitation>0.60 forces "Easier" regardless of PPO/heuristic).
  - **OBSERVATION**: the RL policy proper is out of scope per task instructions (another agent
    covers it); what's verified here is that the orchestrator treats PPO as optional/best-effort
    and always has a non-RL fallback plus a guardrail override layer — i.e., production behavior
    does not strictly require a working PPO checkpoint to run.

### 1.3 Question queue / follow-up logic
- `_select_and_send_question` (1097–1144) and `_prepare_next_question` (1148–1188) reorder (not
  rebuild) the remaining queue to best match target difficulty/type/topic-diversity via a weighted
  penalty tuple `(type_penalty, diff_penalty+repeat_penalty+diversity_penalty, offset)` (line 1179).
- Follow-ups are injected, never substituted for primary questions. `_decide_and_inject_followup`
  (1720–1751): hard cap of 2 consecutive follow-ups; skips follow-up if score≥0.85 with no
  missing/incorrect concepts; otherwise calls `_inject_followup_question`.
- `_inject_followup_question` (1753–1843) calls the Qwen microservice at
  `http://localhost:8001/api/qwen/followup` (or `/followup`) with up to 2 retries (6s timeout each,
  lines 1789–1804); on failure it falls back to a **local** synthesizer
  `services.qwen.app._synthesize_structured_followup` (line 1809) — i.e., follow-up generation has
  its own two-tier LLM/non-LLM fallback independent of the main evaluator fallback.
- Primary-question budget accounting is explicit and documented in a comment block (lines
  820–824): `num_questions` counts primary questions only; follow-ups are added on top of the
  budget, never displace a primary question. `_no_further_turn` (841–853) and
  `_primary_budget_exhausted` (838–839) implement the termination rule.

### 1.4 Answer handling, retries, scoring persistence
- `handle_voice_answer` (301–538) and `handle_code_submission` (589–787) are the two end-to-end
  turn handlers. Both: stop the timer, evaluate, update confidence from last audio analysis
  (352–356), look up lifetime attempt count + `compare_with_previous_best` from
  `services.storage.database` (373–380, cid-gated), generate feedback, compute a **timing
  modifier** via `QuestionTimer.compute_timing_modifier` (408–422), persist the attempt via
  `services.storage.database.save_attempt` (456–460), resolve "is_best" via
  `services.storage.best_answer.select_best` (885, called from `_resolve_best_answer`,
  879–912), update in-memory session state, adapt difficulty, decide on a follow-up, log the turn.
- **Fail-closed evaluator-unavailable path** (`_fail_closed_evaluator_unavailable`, 542–587): if
  the evaluator returns `decision_source == "evaluator_unavailable"`, the turn is **not** scored —
  no score/answer appended, no difficulty change, no persisted attempt, attempt count rolled back,
  timer restarted, and the candidate is told to retry (`next_action: "retry_answer"`). This is a
  deliberate "never fabricate a score" guard, consistent with CLAUDE.md's "never invent results"
  principle. **VERIFIED FACT** (lines 542–587).
- `handle_retry` (937–980) rolls back tentative state additions (`_rollback_tentative_attempt`,
  790–817) so a retried answer doesn't double-count toward `main_questions_count` or re-trigger RL.
- `_select_best_attempt` (914–934): deterministic tie-break — highest raw score, then fewest
  missing concepts, then most recent attempt — used when multiple attempts exist for one question
  before finalizing (`handle_next_question`, 1008–1020; `_finalize_session`, 2047–2059).

### 1.5 Hints and session finalize/report
- `request_hint`/`_get_hint` (1043–1051, 1488–1527): calls Qwen `/api/qwen/hint` or `/hint`;
  explicit `status: "llm_unavailable"` response if unreachable — no silent/fake hint text.
- `_finalize_session`/`_generate_report` (2042–2299): builds a full report dict (score history,
  topic scores, concept coverage, timing analysis, behaviour/communication block) purely from
  in-memory `self._state`; persists via `services.storage.database.save_session` (2082, best-effort,
  swallowed on exception).

### 1.6 Integration points / limitations
- Integration points: `apps/backend/main.py` (constructs orchestrator, injects
  `_run_integrated_evaluator` and `select_questions`), `services/storage/database.py` (SQLite
  persistence), `services/qwen/app.py` (follow-up/hint/feedback LLM), `agents/strategy/hybrid_orchestrator.py`
  (RL — out of scope here), `agents/timing/timer.py`, `agents/validation/score_validator.py`.
- **INTERPRETATION / limitation**: almost every cross-module call (DB, Qwen HTTP, RL strategy) is
  wrapped in broad `except Exception: pass`. This makes the orchestrator very resilient to missing
  services but means a silently-broken dependency (e.g., DB write always failing) would not
  surface as an error to the caller — only via logs, if a logger is attached. No explicit health
  check aggregates these per-dependency failure states for the candidate/admin UI beyond individual
  envelope fields (`llm_status`, `decision_source`, `rl_status`, `infrastructure_errors`).
- **UNKNOWN**: whether `agents/orchestrator/logger.py` (`SessionLogger`) persists to disk/DB or is
  in-memory only — not read in this pass (out of the 8 numbered scope items; flagged for the
  synthesis agent if relevant).

---

## 2. `agents/audio/` — STT / prosody / confidence; video/MediaPipe check

**VERIFIED FACT**: No video or facial-analysis code exists. `grep -i "mediapipe|cv2\.|import cv2|facial|face_landmark|VideoCapture"` across the repo (excluding `.venv`) returned **zero matches** in any `.py` file. A second grep for the literal word `video` restricted to `*.py` files also returned **zero matches**. The only hits for "video" anywhere in the repo are in Markdown docs (`docs/`, `research/`, `final_deliverables/`, `paper/`), none of which are code, and none describe an implemented component — they are prose/planning references. This directly confirms the CLAUDE.md claim: **there is no video/MediaPipe component in the codebase.**

### 2.1 Pipeline (`agents/audio/main.py`, full file read)
`run_pipeline()` (lines 34–77): records audio (`record_audio`), then **in parallel**
(`ThreadPoolExecutor`) runs `extract_prosodic_features` and `transcribe_and_align`, then computes
`analyze_linguistic_confidence` → `score` (confidence) → `score_hesitation` → `build_state_vector`
(RL state). CLI entry point at the bottom supports `--duration/--session/--difficulty/--q-index/--max-q/--reset`.

### 2.2 Transcription (`agents/audio/transcriber.py`, full file read, 262 lines)
- **VERIFIED FACT**: uses **WhisperX** (`import whisperx`, line 46) with model size `"base"`
  (`whisperx.load_model("base", device, compute_type=compute_type)`, line 167) and WhisperX's
  alignment model (`whisperx.load_align_model(language_code="en", ...)`, line 168). `faster-whisper`
  is WhisperX's backend dependency, pinned directly too (`requirements/audio.txt` line 7:
  `faster-whisper>=1.0.0`; line 8: `whisperx>=3.1.0`); the code does not import `faster_whisper`
  directly — it is consumed transitively through `whisperx`.
- Contains several compatibility shims: a `torchaudio.AudioMetaData` dataclass shim (lines 7–18)
  for a torchaudio API that no longer exists in the pinned version, a monkeypatch of
  `torch.serialization.add_safe_globals` for omegaconf types (26–43, needed for
  `torch.load(weights_only=True)` default in newer torch), and a `VoiceActivitySegmentation.__init__`
  shim for pyannote (50–53). **INTERPRETATION**: these shims are direct evidence of the
  numpy/torch/accelerate version-pin mismatch noted in CLAUDE.md's "Known gotchas" — the code has
  already had to work around library drift in the `.venv`.
- **Fallback path**: if WhisperX import fails or transcription raises, `_fallback_energy_timing`
  (91–140) computes pause/speech timing from raw audio energy (RMS framing) with **no transcript**
  (`transcript: ""`, `transcription_confidence: 0.35` fixed value, line 135) and tags
  `alignment_source` accordingly (e.g. `"<decode_source>_energy_fallback"`). This is a real,
  code-level mock/degraded mode distinct from any env var — it activates automatically whenever
  WhisperX is unavailable or throws (line 189–191, 255–258).
- Pause detection threshold: gaps ≥0.2s between aligned words (line 223) in the WhisperX path;
  same 0.2s threshold in the energy fallback (line 114, 120).

### 2.3 Prosody / confidence / hesitation
- `agents/audio/audio_features.py` (186 lines, **not fully read line-by-line in this pass** —
  imported and exercises `praat-parselmouth`-class prosodic features per `requirements/audio.txt`
  line 6 `praat-parselmouth>=0.4.3`). **UNKNOWN**: exact feature list not enumerated here; flagged
  for a deeper pass if needed.
- `agents/audio/confidence_scorer.py` (100 lines) and `agents/audio/hesitation_scorer.py` (76
  lines) combine prosodic + transcription + linguistic signals into `confidence_score` and a
  hesitation breakdown (`hesitation_score`, `pause_ratio`, `pause_frequency`, `long_pause_count`,
  `filler_density`, `pitch_instability` — printed in `main.py` lines 82–88).
- `agents/audio/rl_state_vector.py` (104 lines) builds the RL state vector `S = [Perf, Conf, Hes,
  Time, Diff]` per `main.py` line 90 docstring print — consistent with CLAUDE.md's 6-D state
  description (the 6th dimension, progress `t/T`, is reflected elsewhere in orchestrator state,
  not in this printed 5-tuple label — **OBSERVATION**, worth flagging to the RL-focused auditor
  since the printed label here only shows 5 of the 6 documented dimensions).

### 2.4 Dependencies
`requirements/audio.txt`: `soundfile`, `imageio-ffmpeg`, `praat-parselmouth`, `faster-whisper>=1.0.0`,
`whisperx>=3.1.0`, `pyannote.audio>=3.1.0`, `ctranslate2>=4.0.0`, `transformers<5.0.0`,
`tokenizers<1.0.0`, `nltk`, `scipy`. No video/image/MediaPipe packages present. **VERIFIED FACT.**

---

## 3. `services/evaluator/app.py`

**VERIFIED FACT**: 938 lines. Header comment (lines 1–9) self-describes as "Final Evaluator" with
"Best tuned params: semantic=0.24, concept=0.43, reasoning=0.33, threshold=0.36, bonus=0.03,
penalty=0.05" — note this header's stated weights **do not match** the weights actually used in
code (`0.15/0.35/0.50`, see below); the header appears to be a stale comment from an earlier tuning
pass. **INTERPRETATION**: flag as a documentation/code mismatch inside the file itself, independent
of any CLAUDE.md claim.

### 3.1 Formula — confirmed
`evaluate()` (lines 350–463):
- `S1 = semantic_score(...)` (136–152): mean of max cosine similarity between candidate sentence
  embeddings and rubric "semantic" vectors (SBERT `all-MiniLM-L6-v2`, loaded line 43).
- `S2, concept_details = concept_detection(...)` (97–129): fraction of rubric "concept" groups
  whose best-matching sentence similarity exceeds `CONCEPT_THRESHOLD = 0.30` (line 95).
- `reasoning_score = cross_encoder_verification(...)` (160–169): CrossEncoder raw score calibrated
  via `(raw_score - 0.20) / 0.70`, clamped to [0,1] (lines 168–169).
- `effective_S2 = S2 if reasoning_score > 0.30 else S2 * 0.60` (line 377) — **VERIFIED FACT**: this
  directly matches CLAUDE.md's "S2 ×0.6 when R≤0.30" claim (the code's condition is
  `reasoning_score > 0.30` → full S2, i.e. the discount applies when `reasoning_score <= 0.30`,
  exactly as documented).
- `base_score = 0.15*S1 + 0.35*effective_S2 + 0.50*reasoning_score` (lines 380–384) — **VERIFIED
  FACT**, exact match to CLAUDE.md's `0.15*S1 + 0.35*S2_eff + 0.50*R` formula.
- `final_score = base_score + bonus - penalty`, clamped to [0,1], then rounded to 4dp (385–395).
- Mandatory-concept cap (389–393): if `mandatory_check()` fails, `final_score = min(final_score,
  scoring_policy.get("mandatory_cap", 0.60))`.
- Grade bands (397–405): ≥0.75 Excellent, ≥0.60 Good, ≥0.40 Average, else Poor.
- `bonus_score` (177–201, weight 0.03/hit, threshold 0.50) and `mistake_penalty` (210–253, weight
  0.07/hit, reasoning/S2-based extra penalties, confidence-word penalty, capped at
  `PENALTY_CAP = 0.30`) both apply negation filtering (`"avoid", "not", "without", "instead",
  "unlike", "no "`) so e.g. "avoid X" doesn't earn bonus/penalty credit for X.

### 3.2 Models — provenance
- SBERT: `SentenceTransformer("all-MiniLM-L6-v2")` (line 43) — a genuinely off-the-shelf
  HuggingFace model, loaded by name with no local fine-tuned path. **VERIFIED FACT.**
- CrossEncoder: `CrossEncoder(str(BASE_DIR / "models" / "tuned_model2"))` (line 47) — loaded from a
  **local directory**, not a HuggingFace hub ID. This directly supports CLAUDE.md's claim that the
  CrossEncoder is "a partially fine-tuned derivative with incomplete provenance, not off-the-shelf":
  the code loads a bespoke local checkpoint (`services/evaluator/models/tuned_model2/`, confirmed
  to exist — its `tokenizer.json` surfaced in the repo-wide grep for "video" false-positive-free
  scan, confirming the directory is present on disk). **VERIFIED FACT** (path existence) +
  **INTERPRETATION** (provenance/fine-tuning completeness not further auditable from this file
  alone — no training script or dataset reference is present in `app.py` itself).
- FAISS: `faiss.read_index(BASE_DIR / "assets" / "logic_vectors.faiss")` (line 50) plus a pickled
  metadata list `logic_metadata.pkl` (52–54) mapping `(qid, vector_type)` → embedding row, used by
  `get_vectors_by_type` (62–67) to fetch the right rubric vectors (concept/semantic/bonus/mistake/
  mandatory) per question. All vector types are precomputed/stored, not computed live from rubric
  text at eval time (except as a fallback: `if len(...)==0 and rubric.get("expected_concepts")`
  patterns re-embed rubric text on the fly, e.g. lines 106–107, 145–146, 270–271).

### 3.3 EVALUATOR_MOCK_MODE — important discrepancy

**VERIFIED FACT / OBSERVATION (surprising)**: `services/evaluator/app.py` contains **no reference
whatsoever** to an `EVALUATOR_MOCK_MODE` environment variable (confirmed by reading the full file
and by `grep -n "EVALUATOR_MOCK_MODE"` returning no hits in this file). A repo-wide grep for
`EVALUATOR_MOCK_MODE` across all `*.py` files found it **set** (via `os.environ.setdefault(...)`,
`env=dict(os.environ, EVALUATOR_MOCK_MODE="1", ...)`, or in run-command docstrings) in exactly these
places:
- `tests/unit/test_primary_question_budget.py:10` and `tests/unit/test_best_answer_authority.py:10`
  — only inside a **docstring** telling a human how to invoke pytest; the variable is never read by
  the test body itself (both files were grepped for `MOCK` usage beyond the docstring — none found).
- `research/confirmatory/X1/x1a_harness.py:20`, `x1a_harness_v2.py:20`, `x1b_harness.py:18`,
  `x1b_harness_v3.py:18` — `os.environ.setdefault("EVALUATOR_MOCK_MODE", "1")`.
- `research/confirmatory/X1-D/x1d_run.py:87` — `os.environ.pop("EVALUATOR_MOCK_MODE", None)` (i.e.
  this harness explicitly *removes* it to force the real evaluator).
- `ADCOM2027_Track2_Final/experiments/mutation/run_mutation_testing.py:114` — sets it to `"1"` when
  spawning a subprocess.
- `.github/workflows/ci.yml:29` and `docker-compose.yml:11` — set it at the CI/container level.

A repo-wide grep for any code that actually **reads** this variable
(`os.environ.get("EVALUATOR_MOCK_MODE"`, `os.getenv("EVALUATOR_MOCK_MODE"`, or a bare `MOCK_MODE`
reference wired to it) across all non-`.venv` `*.py` files found **zero consumers**. The only
`MOCK_MODE` **global** that actually exists and is read in the running code is an unrelated flag in
`services/qwen/app.py` (lines 235, 243, 295, 731, 746, 788) that governs the **Qwen LLM** service's
own deterministic-fallback mode (set to `True` when neither a local GGUF model nor an
`ENABLE_GPU_RESEARCH_MODELS`-gated Transformers model loads — line 294–296), and a separate
`EVALUATOR_SOURCE = "mock"` string flag in `apps/backend/main.py` (lines 88–104) that is set purely
based on whether the `from services.evaluator.app import evaluate` import **succeeds**, not based on
any environment variable.

**INTERPRETATION**: `EVALUATOR_MOCK_MODE` as named and documented in CLAUDE.md and CI appears to be
**vestigial/inert** in the current codebase — it is set in several places (tests' run instructions,
CI, docker-compose, research harnesses) but nothing in the application or test code branches on it.
Either (a) it was consumed by code that has since been refactored out, (b) it's a leftover
convention copied between files without an actual implementation, or (c) there is a consumer this
pass did not find (searched all `*.py` outside `.venv`; did not search non-Python config/shell
files beyond `ci.yml`/`docker-compose.yml`, which only *set* it). **RECOMMENDATION**: the synthesis
report should flag this as a testing/infrastructure-claim discrepancy worth asking the project
owner about — tests described as running "in mock mode" for speed may, in fact, always be exercising
the real SBERT/FAISS/CrossEncoder pipeline (with associated model-load cost and non-determinism)
regardless of the env var.

### 3.4 Flask API surface
`app.py` also defines a **Flask** microservice (not FastAPI) guarded by `FLASK_AVAILABLE` (lines
561–582, with a `_DummyFlask` stub if Flask isn't installed) exposing `/health`, `/api/evaluator/
set-question`, `/api/evaluator/evaluate-answer`, `/api/evaluator/last-result`, `/api/evaluator/
current-question` (lines 595–816), with session state held in a single module-level dict
`current_session` (584–592) — i.e., this Flask surface is **single-session, in-process, not
concurrency-safe**, and appears to be a separate/legacy integration path from the one actually used
in production: the production path is `apps/backend/main.py` importing `evaluate`/`get_rubric`
directly as Python functions (line 94–95) and calling them in-process via
`InterviewOrchestrator._evaluate_verbal` → `self._evaluator_fn` (the `_run_integrated_evaluator`
closure) — **not** via HTTP to this Flask app. **INTERPRETATION**: the Flask HTTP API in
`services/evaluator/app.py` is live code but is a second, likely unused/legacy integration surface
relative to the direct-import path `launch.py` actually wires up (launch.py starts
`services/evaluator/app.py` as `python app.py` on port 5000 per its `ready_msg`/`cmd`, but
`apps/backend/main.py` never calls `http://localhost:5000` anywhere found in this pass — it imports
the module directly). **RECOMMENDATION**: verify with a `grep -rn "localhost:5000"` whether any
other component actually talks to the evaluator over HTTP; if not, the Flask server process started
by `launch.py` may be redundant/dead weight at runtime even though evaluation itself works
correctly via direct import.

---

## 4. `agents/coding_executor/` — Docker C sandbox + Qwen feedback

**VERIFIED FACT**: `agents/coding_executor/coding_executor.py` (486 lines, full file read) and
`agents/coding_executor/sandbox_policy.py` (48 lines, full file read).

### 4.1 Sandbox implementation
- `DockerCSandbox.compile_and_execute()` (lines 130–460) is the authoritative entry point, wrapped
  by module-level `evaluate_c_submission` (463–473) and `evaluate_code_submission` (476–485, a
  "drop-in compatibility wrapper").
- Pre-flight static check: `sandbox_policy.validate_source_safety()` (line 143, implementation at
  `sandbox_policy.py` 28–47) blocks empty source, a hardcoded `ptrace(` pattern, and source >64KB.
  Explicitly documented as "auxiliary pre-flight filter; Docker containment remains the
  authoritative security boundary" (sandbox_policy.py lines 4–6).
- Docker daemon resolution supports both native Docker CLI and WSL2 Linux Docker
  (`_resolve_docker_prefix`, lines 56–94), with path translation for WSL mounts (`_to_mount_path`,
  119–128).
- Container hardening flags used for **both** the compile step (214–230) and **each** test-case run
  (324–340): `--user 1001:1001`, `--net=none`, `--cap-drop=ALL`, `--security-opt=no-new-privileges`,
  `--cpus=1.0`, `--memory=128m` + matching `--memory-swap`, `--pids-limit=32`, `--read-only` root
  filesystem with a writable `tmpfs /workspace` (32MB, exec allowed). This matches CLAUDE.md's
  description essentially exactly. **VERIFIED FACT.**
- Each **test case** runs in its own fresh container (re-compiling inside each container — line
  339: the run command re-compiles via `gcc ... && timeout {t}s /workspace/solution`), not just
  once-compile-then-reuse. **INTERPRETATION**: this is safer (no shared mutable state between test
  cases) but means compilation cost is paid once per test case at execution time in addition to the
  separate up-front compile-only step (lines 212–230) — the up-front compile step appears to be used
  purely to fail fast on compile errors before running any test timing; the real per-test run also
  compiles again. This is a minor inefficiency but not a correctness bug.
- Timeouts: default `DEFAULT_TIMEOUT_SEC = 2.0`s per test execution (line 28), with a 5s grace
  margin on the subprocess wrapper (line 349) and a hard `subprocess.run(..., timeout=...)` client-
  side kill plus `_force_remove_container` best-effort cleanup (101–113, 244, 381) if the Docker
  client itself hangs.
- Exit-code classification (365–378): 124→timeout, 137 or OOM-string-match→memory_limit,
  134/136/139→runtime_error (SIGABRT/SIGFPE/SIGSEGV).
- Mandatory-test gating (429–434): if any `is_mandatory` test case fails, score is capped at
  `min(0.30, 0.30 * pass_rate)` regardless of how many non-mandatory tests pass.
- Docker-unavailable path (166–186): returns a structured `status: "sandbox_error"` response with
  `error: "Docker sandbox daemon is unreachable. Untrusted code execution blocked to protect host."`
  — i.e., **fails closed** (refuses to execute, does not fall back to running untrusted C natively).
  **VERIFIED FACT**, and consistent with the "18 Docker-daemon-down failures" mentioned in the test
  logs surfaced during the earlier grep (`testing_and_evaluation/Phase4_Diagnosis_and_Fixes.md`),
  which is corroborating **OBSERVATION** that this fail-closed path is exercised in the test suite
  when Docker isn't running on the test machine.

### 4.2 Qwen feedback for code
- Feedback generation is **not** in `coding_executor.py` itself; it happens in
  `agents/orchestrator/interview_orchestrator.py::_evaluate_code` (1353–1426), which calls
  `FEEDBACK_AGENT.generate_code_feedback(...)` (1369–1381, imported from
  `agents.orchestrator.feedback_agent`) and falls back to a simple pass/fail template (1389–1408) if
  the feedback agent raises. `FEEDBACK_AGENT` (an instance exported from `feedback_agent.py`, not
  read in this pass for its `generate_code_feedback` method specifically, but confirmed to exist via
  the shared `generate()` verbal path — §1.5/§5 — which calls out to the Qwen microservice at
  `http://localhost:8001` with a 6s httpx timeout). **VERIFIED FACT** that the feedback LLM is local
  Qwen (not Mistral): `feedback_agent.py` line 29 hardcodes `QWEN_URL = "http://localhost:8001"`, and
  `services/qwen/app.py` (lines 248–297) loads a **GGUF Qwen model** (`PREPAIRED_GGUF_PATH`) on CPU
  by default, with an optional `Qwen/Qwen2.5-1.5B-Instruct` Transformers 4-bit fallback gated behind
  `ENABLE_GPU_RESEARCH_MODELS` (line 273–276) — no Mistral model is referenced anywhere in this
  path. **VERIFIED FACT.**
- Qwen service's own mock mode (`services/qwen/app.py` line 235, 295): if **neither** the GGUF model
  file exists **nor** the GPU research flag is set, `MOCK_MODE = True` and the service falls back to
  a "deterministic structured fallback engine" (line 296) — this is a second, independent mock
  pathway distinct from `EVALUATOR_MOCK_MODE` (see §3.3) and is actually wired into real control
  flow (`if not MOCK_MODE and "qwen_1b" in registry.models:` at line 746, `if not MOCK_MODE and
  active_key:` at line 788).

---

## 5. `apps/backend` and `apps/web` — structure, routes, implementation status

### 5.1 Backend (`apps/backend/main.py`)
**VERIFIED FACT** — FastAPI app. Route inventory (via `grep "@app\."`, confirmed line numbers):
- `GET /health` (800)
- `POST /api/login` (814)
- `GET /api/candidates/{candidate_id}/dashboard` (876)
- `GET /api/candidates/{candidate_id}/analytics` (886)
- `GET /api/candidates/{candidate_id}/weakness-map` (895)
- `GET /api/candidates/{candidate_id}/compare/{question_id}` (904)
- `POST /api/sessions` (913) — creates an `InterviewOrchestrator` and stores it in `SESSIONS[sid]`
  (confirmed via orchestrator docstring cross-reference, §1).
- `GET /api/history/{candidate_id}/{question_id}` (978), `GET /api/history/{candidate_id}` (997)
- `GET /api/sessions/{session_id}` (1011), `POST /api/sessions/{session_id}/end` (1019)
- `GET /api/reports/{session_id}` (1029), `GET /api/sessions/{session_id}/report` (1030)
- `POST /api/transcribe` (1051) — wires in the audio agent.
- `POST /api/run_code` (1164) — wires in `coding_executor`.
- `GET /api/admin/sessions` (1184), `GET /api/admin/stats` (1219), `GET /api/admin/sessions/{session_id}` (1240)
- `WS /ws/interview/{session_id}` (1252) — the main real-time interview loop.

Evaluator wiring (lines 42–196, read in full): `_run_integrated_evaluator()` is a thin adapter that
(1) resolves a rubric from the question payload, by qid lookup via `get_rubric`, or by synthesizing
a minimal rubric from question metadata if none exists (lines 117–143: `{"reference_answer":...,
"expected_concepts": [f"{topic} core principle"], ...}` — **INTERPRETATION**: this synthesized-rubric
fallback means a question with no curated rubric still gets scored, but against a very weak,
auto-generated standard; this is a form of graceful degradation worth flagging as a scoring-quality
caveat, not a bug), then (2) calls the real `evaluate()` function imported directly from
`services.evaluator.app` (line 94, **not** over HTTP — see §3.4), then (3) re-applies
`ScoreValidator.validate()` if available (162–170).

`EVALUATOR_READY` / `EVALUATOR_SOURCE` (88–110): set to `"services_evaluator"` if the import
succeeds, else `"mock"` with a printed `[ERROR]` — **VERIFIED FACT** that this is a load-time
import-success flag, not an env-var-gated mode (see §3.3 discrepancy).

**OBSERVATION on admin endpoints**: `admin_sessions`/`admin_stats`/`admin_session_detail` (1184–1247)
iterate the **in-process `SESSIONS` dict** (module-global, populated only by `POST /api/sessions`
calls made to this running process) rather than querying the persisted SQLite `sessions` table.
**INTERPRETATION**: this means the admin dashboard only reflects sessions created since the backend
process last restarted (no historical cross-restart view), even though `services/storage/database.py`
does persist completed sessions to disk (`save_session`, confirmed call site at orchestrator line
2082–2085). This is a plausible **partial/stubbed** implementation gap between "data is being
saved" and "admin UI reads from the saved store" — worth flagging to the synthesis report as
implemented-but-not-fully-wired.

### 5.2 Frontend (`apps/web`)
**VERIFIED FACT** — React 18 + Vite 5 SPA (`package.json`: `react@^18.3.1`, `vite@^5.4.0`,
`vitest@^2.1.8` for tests). Key source files (non-exhaustive, `apps/web/src/`):
`App.css`, `Demo.jsx`, `AdminDashboard.jsx`, `DifficultyTracker.jsx`, `FeedbackCard.css`,
`InterviewRoom.css`, `Login.css`, `MonacoEditor.jsx` (code editor — Monaco, consistent with a C
coding UI), `Report.css`, `ScoreRing.jsx`, `Topbar.jsx`, `TruthEarIntegration.jsx`,
`WaveformBar.jsx` (audio visualization), `useInterviewWS.js` (WebSocket hook — talks to
`/ws/interview/{session_id}`), `useVoiceRecorder.js`, `servicesApi.js` (confirmed: a 4-line legacy
re-export of `src/api.js`, "Legacy alias — all endpoints consolidated in src/api.js"), and `api.js`
(exports a single `api` object, line 30, consolidating all backend calls). **VERIFIED FACT**: the
frontend is a real, non-trivial SPA with distinct Interview/Report/Admin/Login/Demo views, a
WebSocket-driven live interview room, a Monaco-based code editor, and voice recording — not just a
placeholder UI. `node_modules` was excluded from inspection per instructions (10,700+ files, mostly
transitive deps — not inspected).
- **UNKNOWN**: exact content of `apps/web/src/api.js` (only confirmed its one top-level export,
  `export const api = {`, line 30) — a full endpoint-by-endpoint cross-check against the backend
  routes in §5.1 was not performed in this pass.
- `Demo.jsx` existing alongside `InterviewRoom`-style components suggests a separate demo/sandbox UI
  path distinct from the full authenticated flow — **INTERPRETATION**, not independently confirmed
  by reading `Demo.jsx`'s contents in this pass.

---

## 6. `data/prepaired.db` — schema

**OBSERVATION**: `sqlite3` CLI was not available in the shell (`command -v sqlite3` failed), so the
live `.db` file itself was not queried directly. Instead the schema was read from the authoritative
`init_db()` function in `services/storage/database.py` (lines 40–133, full section read), which is
the single source of truth for schema creation (`CREATE TABLE IF NOT EXISTS`, idempotent).

Three tables, confirmed via `grep -n "CREATE TABLE"` (lines 48, 67, 87) and full read of their
column lists:

1. **`candidates`** (48–62): `id` (TEXT PK), `email` (UNIQUE NOT NULL — the real identity key),
   `name`, `college`, `year`, `roll`, `primary_lang` (default `'C'`), `experience` (default
   `'intermediate'`), `is_admin` (INTEGER default 0), `created_at`, `last_login_at`. Indexed on
   `email` (63).
2. **`sessions`** (67–82): `id` (TEXT PK), `candidate_id` (FK→candidates.id), `interview_mode`,
   `c_topics`/`dsa_topics` (JSON-as-TEXT, default `'[]'`), `duration_minutes` (default 30),
   `num_questions` (default 15), `start_difficulty` (default 2), `status`, `overall_score` (default
   0.0), `created_at`, `completed_at`. Indexed on `candidate_id` (83).
3. **`question_attempts`** (87–111): `id` (TEXT PK), `candidate_id`/`session_id`/`question_id`,
   `question_version` (default `'v1'`), `attempt_number`/`session_attempt_number` (lifetime vs.
   per-session counters — matches orchestrator's `lifetime_attempt_num` logic, §1.4),
   `attempt_type` (default `'primary'`, vs. `'followup'`), `parent_question_id`, `answer_type`
   (default `'verbal'`, vs. `'code'`), `transcript`, `code_submitted`, `raw_score`/`validated_score`
   (both REAL NOT NULL), `is_best` (INTEGER default 0), `covered_concepts`/`missing_concepts`/
   `incorrect_claims`/`strong_points` (all JSON-as-TEXT), `weakest_gap`, `evaluation_confidence`
   (default 0.85), `feedback_json` (full feedback blob as TEXT), `created_at`. Three indices:
   `(candidate_id, question_id)`, `(candidate_id, question_id, is_best)`, `(session_id)` (114–131).

Connection setup (`get_connection`, 29–37) uses WAL journal mode and `PRAGMA foreign_keys=ON`, a
`threading.Lock()` guards `init_db` (26, 42), and `check_same_thread=False` is set — consistent with
a multi-threaded FastAPI/uvicorn deployment accessing one SQLite file.

**OBSERVATION**: `ls data/` shows `prepaired.db` (282,624 bytes, last modified 2026-11-03) plus two
sibling directories `data/questions/` (containing `qns.json`) and `data/rubrics/` (containing
`rubrics_final_clean.json`) — these are the curated question bank / rubric JSON files referenced by
`services/evaluator/app.py`'s `get_rubric()` (lines 479–484) and `apps/backend`'s question selector,
**not** additional SQLite tables. No standalone `schema.sql`/migrations file exists; `init_db()` in
`database.py` is the only schema definition found.

**UNKNOWN**: exact row counts / whether `question_attempts` or `sessions` currently hold production
data vs. only test-run data — not queried (sqlite3 CLI unavailable; did not attempt a Python
one-liner to avoid any risk of writing to the live DB, per read-only instructions).

---

## 7. `launch.py` and `requirements/*.txt`

### 7.1 `launch.py` (full file read, 251 lines)
**VERIFIED FACT**: confirms the exact flags described in CLAUDE.md:
- `--no-qwen` (line 182): skips the `qwen` service entry (flag-gated in `SERVICES` list, line
  64–71).
- `--no-frontend` (183): skips the `frontend` npm dev-server entry (80–88).
- `--backend-only` (184): sets both `no_qwen` and `no_frontend` to `True` (187–189).

Service start order and ports (`SERVICES` list, 53–89): evaluator (port 5000, `python app.py`,
required), qwen (port 8001, `uvicorn app:app`, optional), backend (port 8000, `uvicorn main:app
--reload`, required), frontend (port 5173, `npm run dev`, optional). Each service's readiness is
polled via log-file content matching (`_wait_ready`, 134–158), with auto-restart for crashed
non-optional services in the main loop (236–243). A documented bug-fix comment (lines 31–37)
explains a Windows-console Unicode crash fix (`sys.stdout.reconfigure(..., errors="replace")`,
38–42) — directly cross-references `testing_and_evaluation/baseline_results/T-N01_smoke_test_finding.md`,
confirming this is a real, previously-hit bug, not speculative.

**No discrepancy found** between launch.py's actual behavior/flags and CLAUDE.md's description.

### 7.2 `requirements/*.txt`
Eight files confirmed present: `audio.txt`, `backend.txt`, `base.txt`, `dev.txt`, `evaluator.txt`,
`qwen.txt`, `rl.txt`, `tracking.txt`.
- `base.txt`: `numpy>=1.26.0,<2.0.0`, `pandas<3.0.0`, `matplotlib<4.0.0`, `tqdm`, `rich`. **VERIFIED
  FACT**: this pin (`numpy<2.0.0`) directly confirms CLAUDE.md's "Known gotchas" claim that the
  live `.venv` (observed elsewhere to have `numpy 2.5.2`) **violates** this pin — the requirements
  file itself is correct/conservative; the installed `.venv` has drifted past it. This pass did not
  re-verify the live `.venv`'s actual installed numpy/torch/accelerate versions (out of scope —
  CLAUDE.md already states this as a known, unresolved issue; not re-litigated here).
- `audio.txt`: `faster-whisper>=1.0.0`, `whisperx>=3.1.0`, `pyannote.audio>=3.1.0`,
  `ctranslate2>=4.0.0`, `transformers>=4.40.0,<5.0.0`, `tokenizers>=0.19.0,<1.0.0`, `nltk`, `scipy`,
  `praat-parselmouth`, `soundfile`, `imageio-ffmpeg` — confirms STT/prosody stack, no video libs.
- `evaluator.txt`: `-r base.txt` plus `sentence-transformers>=2.3.0,<3.0.0`,
  `scikit-learn>=1.4.0,<2.0.0`, `faiss-cpu>=1.7.4,<2.0.0` — confirms SBERT/CrossEncoder (via
  sentence-transformers) + FAISS stack exactly as used in `services/evaluator/app.py`.
- **UNKNOWN**: `backend.txt`, `dev.txt`, `qwen.txt`, `rl.txt`, `tracking.txt` were not opened in
  this pass (RL requirements explicitly out of scope per task instructions; the others are lower
  priority and time-boxed out — flagged here rather than guessed at).

---

## 8. Technology Usage Table

| Technology / Library | Where used (file:line / function) | Status | Evidence tag |
|---|---|---|---|
| WhisperX (STT) | `agents/audio/transcriber.py:46,167-168` (`whisperx.load_model("base", ...)`) | **Fully implemented**, with automatic energy-based fallback (`_fallback_energy_timing`, lines 91-140) if unavailable/erroring | VERIFIED FACT |
| faster-whisper | `requirements/audio.txt:7`; consumed transitively via WhisperX, not imported directly | Implemented (indirect dependency) | VERIFIED FACT |
| pyannote.audio (VAD) | `agents/audio/transcriber.py:47-53` (shim for `VoiceActivitySegmentation.__init__`) | Implemented, with a compatibility monkeypatch | VERIFIED FACT |
| praat-parselmouth (prosody) | `requirements/audio.txt:6`; used in `agents/audio/audio_features.py` (not line-audited in depth) | Implemented (not deeply verified) | OBSERVATION / UNKNOWN (depth) |
| MediaPipe / OpenCV (video) | — | **Not present anywhere in the codebase** (0 matches repo-wide) | VERIFIED FACT |
| SentenceTransformers — SBERT `all-MiniLM-L6-v2` | `services/evaluator/app.py:43` | Fully implemented, off-the-shelf HF model | VERIFIED FACT |
| SentenceTransformers — CrossEncoder | `services/evaluator/app.py:47` (`CrossEncoder(.../models/tuned_model2)`) | Fully implemented; **local fine-tuned checkpoint**, not off-the-shelf | VERIFIED FACT (path) / INTERPRETATION (provenance) |
| FAISS (faiss-cpu) | `services/evaluator/app.py:37-67` (`faiss.read_index`, `get_vectors_by_type`) | Fully implemented; precomputed rubric vector index | VERIFIED FACT |
| scikit-learn (cosine similarity) | `services/evaluator/app.py:78-80` (`_cosine_similarity`) | Fully implemented | VERIFIED FACT |
| Flask (evaluator HTTP API) | `services/evaluator/app.py:561-938` | Implemented but likely **unused/legacy**: production path uses direct Python import, not HTTP, from `apps/backend/main.py:94-95` | INTERPRETATION |
| EVALUATOR_MOCK_MODE env var | Set in CI/docker-compose/test docstrings/research harnesses; **never read** by any app or test code found | **Vestigial / not wired to any behavior** | VERIFIED FACT (no consumer found) |
| Qwen (GGUF, local LLM) | `services/qwen/app.py:248-270` (`registry.load_gguf_model`) | Fully implemented primary path; CPU GGUF model, path via `PREPAIRED_GGUF_PATH` | VERIFIED FACT |
| Qwen (Transformers 4-bit, GPU) | `services/qwen/app.py:272-292` | Implemented but gated behind `ENABLE_GPU_RESEARCH_MODELS` env flag — research-only path | VERIFIED FACT |
| Qwen MOCK_MODE (deterministic fallback) | `services/qwen/app.py:235,294-296,746,788` | Fully implemented fallback, triggers automatically if no model loads | VERIFIED FACT |
| Mistral | — | **Not found anywhere** in the codebase searched | VERIFIED FACT (absence) |
| Docker C sandbox | `agents/coding_executor/coding_executor.py:130-460` | Fully implemented, hardened (`--net=none`, `--cap-drop=ALL`, non-root, read-only + tmpfs, resource limits); fails closed if Docker unreachable | VERIFIED FACT |
| Sandbox static pre-check | `agents/coding_executor/sandbox_policy.py:28-47` | Implemented, explicitly described as non-authoritative, auxiliary | VERIFIED FACT |
| SQLite (`prepaired.db`) | `services/storage/database.py:29-133` (schema), various `save_attempt`/`save_session`/`compare_with_previous_best` calls from orchestrator | Fully implemented for write path; **admin read path in `apps/backend/main.py` reads in-memory `SESSIONS` dict instead of the DB** (lines 1184-1247) | VERIFIED FACT + INTERPRETATION (partial wiring gap) |
| FastAPI backend | `apps/backend/main.py` (19 routes incl. 1 WebSocket) | Fully implemented | VERIFIED FACT |
| React + Vite frontend | `apps/web/` (package.json, ~20 source files) | Fully implemented SPA with live interview room, admin dashboard, Monaco code editor, voice recorder | VERIFIED FACT |
| PPO / RL (`rl/`) | `rl/env/interview_env.py`, `rl/training/simulated_candidate.py`, `rl/guardrails.py`, `rl/training/retrain_quick.py` | Present; **out of deep-audit scope per task instructions** (another agent covers RL) — confirmed only existence/location | VERIFIED FACT (existence only) |
| Guardrails (post-PPO override) | `agents/orchestrator/interview_orchestrator.py:1529-1573` (`_apply_guardrails`, G1/G2/G3/G4/G6) | Fully implemented, applied unconditionally after PPO or heuristic action selection | VERIFIED FACT |
| Non-RL heuristic fallback | `agents/orchestrator/interview_orchestrator.py:1661-1675` | Fully implemented, explicitly labeled "operational continuity only, not RL intelligence" | VERIFIED FACT |
| Baseline warm-up phase | `agents/orchestrator/interview_orchestrator.py:1280-1304,1587-1639` | Fully implemented, deterministic (Q1=easy, Q2+=mid) until signal stabilizes | VERIFIED FACT |

---

## Summary of notable findings for synthesis

1. **No video/MediaPipe/cv2 component exists anywhere in the codebase** — confirmed by exhaustive
   grep, not just absence-of-evidence. Directly corroborates CLAUDE.md.
2. **`EVALUATOR_MOCK_MODE` appears to be a dead/vestigial env var** — set in CI, docker-compose, and
   several test/research harnesses, but no application or test code anywhere in the repo actually
   reads it. The real evaluator-availability switch in production is an import-success flag
   (`EVALUATOR_SOURCE` in `apps/backend/main.py`), not this env var.
3. **The evaluator's Flask HTTP API (`services/evaluator/app.py`) looks like a legacy/unused
   integration surface** — the backend calls `evaluate()`/`get_rubric()` as direct Python imports,
   not over HTTP to the Flask server that `launch.py` starts on port 5000.
4. **Admin dashboard reads from an in-memory session dict, not the persisted SQLite store** —
   `apps/backend/main.py`'s `/api/admin/*` routes iterate the process-local `SESSIONS` dict, while
   actual persistence goes through `services/storage/database.py`'s `sessions`/`question_attempts`
   tables. These two views can diverge (e.g., after a backend restart).
5. **The evaluator-unavailable and Docker-unavailable paths both fail closed** (no score fabricated,
   no untrusted code executed) rather than silently degrading — a genuinely evidence-respecting
   design choice consistent with the project's "never invent results" principle.
6. **The CrossEncoder is confirmed loaded from a local directory (`models/tuned_model2`)**, not a
   HuggingFace hub ID, supporting CLAUDE.md's "partially fine-tuned derivative, not off-the-shelf"
   characterization — though this pass could not independently verify the *degree* of fine-tuning
   or its training provenance from `app.py` alone.
7. **The evaluator weighting formula `0.15*S1 + 0.35*S2_eff + 0.50*R` with the `S2×0.6` discount at
   `R≤0.30` is confirmed exactly** in `services/evaluator/app.py` lines 377-384, matching CLAUDE.md
   verbatim — despite the file's own stale header comment claiming different "best tuned params."
