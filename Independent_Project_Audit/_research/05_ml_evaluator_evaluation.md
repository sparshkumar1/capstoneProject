# ML Evaluator Pipeline — Independent Technical Audit

Scope: `services/evaluator/app.py` and its supporting assets/models; Qwen's role; existing
validation evidence; a pipeline-correctness assessment. Research-provenance history (the
0.3812 vs. 0.9152/0.8358/0.7400 numbers lineage) is covered by a parallel audit track; this
document treats that history only where it intersects the code/pipeline itself.

All claims are tagged: **VERIFIED FACT** (exact file/line), **OBSERVATION**, **INTERPRETATION**,
**RECOMMENDATION**, **UNKNOWN**.

---

## 1. How S1, S2, S2_eff and R are computed (exact code, models, thresholds)

**VERIFIED FACT** — Source file: `services/evaluator/app.py` (939 lines). Single module, Flask
API wrapper around a pure-function scoring pipeline (`evaluate()`), no other scoring module
imports into it.

### Models/assets loaded (`_ensure_evaluator_assets_loaded`, lines 34–59)
- `embedder = SentenceTransformer("all-MiniLM-L6-v2")` — line 43. Public SBERT model (384-dim),
  loaded by name from the `sentence-transformers` hub cache, not a local fine-tuned checkpoint.
- `cross_encoder = CrossEncoder(str(BASE_DIR / "models" / "tuned_model2"))` — line 47. Loaded from
  a **local directory**, not a hub model id. See §2.
- `index = faiss.read_index(str(BASE_DIR / "assets" / "logic_vectors.faiss"))` — line 50.
- `vector_meta` — pickle of per-vector metadata (`qid`, `type`) — lines 52–54.
- `_lookup` — a `defaultdict(list)` keyed by `(qid, type)` built once from `vector_meta` — lines
  56–59, consumed by `get_vectors_by_type()` (lines 62–67) to fetch pre-embedded rubric vectors
  (`concept`, `semantic`, `bonus`, `mistake`, `mandatory` types) for a given question id.
- `requirements/evaluator.txt` pins `sentence-transformers>=2.3.0,<3.0.0`, `faiss-cpu>=1.7.4,<2.0.0`,
  `scikit-learn>=1.4.0,<2.0.0`. **OBSERVATION**: `tuned_model2/config.json` records
  `"sentence_transformers": {"version": "5.2.3"}` (line 33 of that file) — i.e. the checkpoint's
  own metadata says it was *saved* by a sentence-transformers version two major versions ahead of
  what this repo's `requirements/evaluator.txt` pins and what `.venv` can legally install. This is
  consistent with the checkpoint having been produced outside this project's environment (see §2).

### S1 — semantic score (`semantic_score`, lines 136–152)
Sentence-split the candidate (`split_sentences`, regex `(?<=[.!?])\s+`, line 75), embed each
sentence with SBERT (`embed()`, lines 83–87, which L2-normalizes via `faiss.normalize_L2`), embed
the rubric's `"semantic"`-type vectors (falling back to embedding `rubric["expected_concepts"]` if
no pre-built vectors exist for the qid, lines 144–146), take cosine similarity
(`sklearn.metrics.pairwise.cosine_similarity`, line 79–80), and return
`mean(max(sim, axis=0))` — i.e. for each rubric target, the best-matching candidate sentence, then
averaged across targets. Returns `0.0` if no sentences or no semantic vectors exist (lines 139–140,
148–149).

### S2 — concept coverage (`concept_detection`, lines 97–129)
Same sentence-embedding approach against `"concept"`-type rubric vectors.
`CONCEPT_THRESHOLD = 0.30` (line 95, "single source of truth" per the comment at line 92–93,
used identically for the coverage count and the per-concept `covered` flag — this was an explicit
fix noted in the file's own changelog at lines 6–8).
`S2 = count(best_sim_per_concept > 0.30) / num_concepts` (lines 116–117). Each concept's
best-matching sentence and raw score are recorded for the `concept_details` returned to the
caller (lines 119–127).

### R — CrossEncoder "reasoning" score (`cross_encoder_verification`, lines 160–169)
```python
ref_ans = str(rubric.get("answer") or rubric.get("reference_answer") or "")
reference = (qn + " " + ref_ans).strip()
raw_score = float(cross_encoder.predict([(reference, candidate)])[0])
reasoning_score = (raw_score - 0.20) / 0.70
return max(0.0, min(1.0, reasoning_score))
```
**VERIFIED FACT**: the model's raw regression output is **linearly rescaled** by a fixed,
hand-set affine transform `(x - 0.20) / 0.70`, justified only by a code comment (lines 166–168:
"baseline floor is ~0.20 for unrelated/noise pairs, 0.40–0.55 for partial/weak reasoning,
0.70–0.95 for strong logical entailment"). **OBSERVATION**: no citation, calibration script, or
data is present in `services/evaluator/` establishing these three breakpoints; they read as
manually chosen based on informal observation of the model's output range, not a fitted
calibration. **INTERPRETATION**: this is a plausible but unverified heuristic recalibration of an
otherwise uncalibrated regression head.

### S2_eff — the "keyword-stuffing defense" (line 377)
```python
effective_S2 = S2 if reasoning_score > 0.30 else S2 * 0.60
```
**VERIFIED FACT**, `evaluate()`, line 377, with inline comment "Dampen S2 when reasoning is weak
(prevents keyword stuffing)". This is the exact `R<=0.30 → S2*0.6` rule in the task's framing
(the code's condition is `reasoning_score > 0.30` for the *undamped* branch, i.e. damping applies
when `R <= 0.30`, matching the stated spec).

### Final composite (`evaluate()`, lines 380–395)
```python
base_score = 0.15*S1 + 0.35*effective_S2 + 0.50*reasoning_score
final_score = base_score + bonus - penalty          # clamped to [0,1]
if not mandatory_pass:
    final_score = min(final_score, scoring_policy.get("mandatory_cap", 0.60))
final_score = round(final_score, 4)
```
Matches the CLAUDE.md-documented formula exactly: `0.15·S1 + 0.35·S2_eff + 0.50·R`.

### Other scoring-adjacent logic (all deterministic, no ML)
- **Bonus** (`bonus_score`, lines 180–201): `BONUS_WEIGHT=0.03` per matched "bonus" vector above
  `BONUS_THRESHOLD=0.50`, after filtering sentences containing negation words
  (`avoid, avoids, not, without, instead, unlike, "no "`) so "avoid X" doesn't earn credit for X.
- **Penalty** (`mistake_penalty`, lines 214–253): `MISTAKE_THRESHOLD=0.55`, `MISTAKE_WEIGHT=0.07`
  per matched "mistake" vector; plus a flat `+0.20` if `reasoning_score<=0.25 and S2<=0.25`, `+0.05`
  if `reasoning_score<0.30 and S2<0.50`, `+0.03` for low-confidence language
  (`maybe, not sure, probably, guess, umm, uhh, uh`) **only** when `S2<0.50 and reasoning_score<0.40`
  (so hesitation alone, on an otherwise strong answer, is never penalized — lines 245–251);
  capped at `PENALTY_CAP=0.30` (line 212, 253).
- **Mandatory check** (`mandatory_check`, lines 262–279): `MANDATORY_THRESHOLD=0.40`; if the
  rubric defines no mandatory concepts, the check **always passes** (line 274) — i.e. the cap is
  opt-in per rubric, not universal.
- **Grade bands** (lines 398–405): Excellent ≥0.75, Good ≥0.60, Average ≥0.40, else Poor.
- **Depth/communication/eval_confidence** (lines 427–433) are explicitly separate, non-scoring
  diagnostic fields; the file's own comment (line 426) states they are "NEVER added as positive
  bonus to technical score" — and indeed `final_score` (line 386) never references `depth`,
  `communication`, or `eval_confidence`.

### EVALUATOR_MOCK_MODE — what it actually does
**VERIFIED FACT**: `services/evaluator/app.py` contains **no reference to `EVALUATOR_MOCK_MODE`**
anywhere in the file (confirmed by full read + pattern search). The variable is set in
`.github/workflows/ci.yml:29` (`'1'`), `docker-compose.yml:11` (`"0"` for the standalone
microservice container), several `research/confirmatory/X1*` harness scripts
(`os.environ.setdefault("EVALUATOR_MOCK_MODE", "1")`), and is documented as the standard test
command in `CLAUDE.md` and multiple `testing_and_evaluation/*.md` files and test-file docstrings
(`tests/unit/test_best_answer_authority.py:10`, `tests/unit/test_primary_question_budget.py:10`).
A repo-wide search (`os.getenv`/`os.environ.get`/`os.environ[...]` for this exact name, and a
generic `EVALUATOR_MOCK` search across all `.py` files) found **no code path in
`services/evaluator/app.py`, `apps/backend/main.py`, or `agents/orchestrator/interview_orchestrator.py`
that reads this variable.**

What actually determines real-vs-mock, per `apps/backend/main.py` lines 88–110:
```python
EVALUATOR_READY = False
EVALUATOR_SOURCE = "mock"
try:
    from services.evaluator.app import evaluate as _prod_evaluate
    ...
    EVALUATOR_READY = True
    EVALUATOR_SOURCE = "services_evaluator"
except Exception as exc:
    EVALUATOR_READY = False
    EVALUATOR_SOURCE = "mock"
```
i.e. the backend **always attempts to import the real evaluator** (which triggers loading the
real SBERT/FAISS/CrossEncoder assets the first time `evaluate()` runs); it only falls back to
"mock" source attribution if that import raises an exception (missing dependency, missing asset
file, etc.) — not because of the `EVALUATOR_MOCK_MODE` env var. `testing_and_evaluation`'s own
`T-N06_evaluator_negative_and_edge_cases.py` docstring (lines 4–5) independently confirms this:
"Calls the real, production evaluate() function (loads the real SBERT/FAISS/CrossEncoder assets,
**same as the passing pytest suite**)" — i.e. setting `EVALUATOR_MOCK_MODE=1` for `pytest` does
**not** make the evaluator tests run against a stub; they run the real models regardless.

**OBSERVATION**: this means `EVALUATOR_MOCK_MODE` is either (a) vestigial — a hook from an earlier
implementation that has since been removed from the code while the env var lingers in CI/docs/test
docstrings, or (b) intended to gate something else entirely (e.g. a different, unfound code path,
or a convention for a future mock) that was never wired up. Either way, **the documented behavior
("mock mode" vs "real mode" controlled by this flag) does not match what the code does.**

**RECOMMENDATION**: either wire `EVALUATOR_MOCK_MODE` into `_ensure_evaluator_assets_loaded`/the
backend's import-guard explicitly (so CI truly can run without downloading/loading the real
models), or remove the stale references from `CLAUDE.md`, CI, docker-compose and test docstrings
so the documented test command matches actual behavior. This is a documentation/code-drift defect,
not a scoring-correctness defect — the real evaluator (real models) runs in CI today regardless of
the flag's value.

---

## 2. CrossEncoder provenance — off-the-shelf, fine-tuned, or unknown?

**VERIFIED FACT** (code): `services/evaluator/app.py:47` loads the CrossEncoder from a local path,
`BASE_DIR / "models" / "tuned_model2"`, not a Hugging Face Hub model id. The directory's own
`README.md` is byte-for-byte the **generic upstream model card for `cross-encoder/ms-marco-*`**
(front-matter line 8: `base_model: cross-encoder/ms-marco-MiniLM-L12-v2`), but `config.json`
(lines 14, 27–28 of that file) shows `hidden_size: 384`, `num_hidden_layers: 6` — i.e. an **L6**
architecture, not L12 (which has 12 layers). The README is simply the wrong/stale upstream card
copied into the directory, not evidence about this specific checkpoint.

`tuned_model2/best_model_info.json` contains a genuine training-run record:
`epoch: 5, global_step: 660, train_huber_loss, train_rank_loss, val_huber_loss, val_rank_loss,
val_spearman: 0.785, val_p_value: 0.0`. A joint Huber + pairwise-rank objective with a validation
Spearman is **not** a standard MS MARCO ranking metric and does not appear on the upstream model
card — this is evidence of a custom fine-tuning run, not an artifact of the base model.

A prior forensic pass in this repository, `research/audit/P0_1_CROSSENCODER_FORENSIC.md` (dated
2026-09-19, read-only, tensor-by-tensor comparison against the cached upstream
`cross-encoder/ms-marco-MiniLM-L-6-v2` checkpoint), found:
- 83.7% of parameters (embeddings + encoder layers 0–3) are **bit-identical** to the public
  upstream checkpoint; encoder layers 4–5, the pooler, and the classifier head (16.28% of
  parameters) **differ** from upstream, with small-magnitude changes (max abs diff ~2.5e-3 to
  6.1e-3) consistent with a low-learning-rate fine-tune with lower layers frozen.
- No upstream revision of `cross-encoder/ms-marco-MiniLM-L-6-v2` (26 commits checked, 2021–2026)
  matches the tuned checkpoint's weights — ruling out "this is just a different release of the
  stock model."
- A second, now-deleted checkpoint (`1_best_model_zip`, removed from git in commit `6885371`) has a
  **different** weight hash, the same freeze pattern, and a **different** `best_model_info.json`
  (global_step 1245, val_spearman 0.7918) — i.e. there were at least two separate fine-tuning runs,
  and the repo does not document which one (or why `tuned_model2`) was kept.
- `config.json`'s `transformers_version: 5.0.0` / `sentence_transformers version: 5.2.3` stamps
  do not match this project's pinned/installed versions, consistent with the checkpoint having been
  produced in a different environment.
- No training script, dataset file, notebook, or commit message referencing fine-tuning was found
  anywhere in git history or on disk.

**VERIFIED FACT** (quoting that forensic doc's own bottom line, §0): "The evaluated checkpoint is a
partially fine-tuned derivative of `cross-encoder/ms-marco-MiniLM-L-6-v2`. It is not off-the-shelf
... The fine-tuning code, training data, validation data, hyperparameters and author/environment
are **not recoverable from the repository, its Git history, or any file on this machine**."

**Answer to the audit question**: the code/config evidence (weight-level comparison + the
`best_model_info.json` training record + environment-version mismatch) **supports** the claim
"partially fine-tuned derivative with incomplete provenance" and actively **contradicts** an
"off-the-shelf" framing. It does **not** support any specific claim about *what data* it was
fine-tuned on — that remains **UNKNOWN** (the forensic doc found two mutually contradictory
unsupported claims elsewhere in the repo about the training data: "general passage ranking pairs
and generic reasoning entailment" vs. "technical interview answer pairs" — neither has evidence).

**INTERPRETATION**: this is a legitimate provenance gap, not merely a labeling dispute. The
checkpoint used in production scoring was selected from among at least two undocumented
fine-tuning runs, by criteria that are not recorded.

---

## 3. Qwen's role — feedback only, or does it ever touch the score?

**VERIFIED FACT**: `services/evaluator/app.py` (the file that computes `final_score`) contains
**zero references to Qwen** anywhere in its 939 lines (confirmed by direct read and pattern
search for "qwen"/"Qwen"/"QWEN").

**VERIFIED FACT**: `services/qwen/app.py` is a separate FastAPI(-style) microservice
(`QWEN_URL = "http://localhost:8001"` referenced from `agents/orchestrator/feedback_agent.py:29`).
Its `MOCK_MODE` global (line 235, flipped to `True` at line 295 if no local model loads) is **its
own**, internal fallback flag — unrelated to, and not to be confused with, `EVALUATOR_MOCK_MODE`.
`services/qwen/app.py` reads `final_score`/`score` values that were computed upstream and passed
in as request fields (e.g. `ev.get("final_score", 0.5)` at lines 418, 462, 525, 605) purely to
choose feedback *wording* (e.g. which narrative template branch to use, lines 538, 653–687) and
to interpolate the already-computed score into the human-readable text (`f"- Score: {score:.2f}"`
at line 440). It never recomputes or overwrites the score. There is even an explicit safeguard
against Qwen *asserting its own* numeric claims in free text: `services/qwen/app.py:596–597`
rejects generated narrative text matching `r"\bScore:\s*\d+\.\d+"` or `r"\bSemantic\s+\d+%"`
("Score leakage rejection").

**VERIFIED FACT**: `agents/orchestrator/feedback_agent.py` (docstring lines 1–17) states the
FeedbackAgent "Combines: Evaluator scores (S1 semantic, S2 concept, R reasoning) ... Qwen narrative
(when microservice is reachable)" — i.e. the module's own stated contract is that Qwen supplies
narrative text alongside (not instead of) the deterministic scores.

**Cross-check against `testing_and_evaluation/Qwen_2.5_Evaluator_Validation_Report.md`** (an
existing project document, read for context, not taken at face value without the above
independent code checks): it makes the identical claim with additional line-level citations —
"`agents/orchestrator/feedback_agent.py` ... sets `"final_score": round(score, 4)` from the
`score` variable computed **before** the Qwen call, and never reassigns it from the Qwen response."
This is consistent with what this audit independently found in `apps/backend/main.py:146-195`
(`_run_integrated_evaluator`): `score = float(raw.get("final_score", 0.0))` is computed entirely
from the `services.evaluator.app.evaluate()` return value, before any Qwen call exists in that
function at all — `_run_integrated_evaluator` contains no Qwen reference.

**Conclusion (VERIFIED FACT, independently confirmed by this audit's own code reading, not merely
reproduced from the project's self-report)**: Qwen has **no role in computing scores used for
evaluation or RL**. Its three confirmed roles, all downstream of scoring:
1. Narrative feedback text generation (`feedback_agent.py`, triggered when score ≤0.65 per that
   module's trigger logic, per the validation report's §A — not independently re-verified by this
   audit beyond confirming the score/Qwen call ordering).
2. Contextual hints on request (`interview_orchestrator.py`'s hint-generation path →
   `POST /api/qwen/hint`).
3. Follow-up question generation when the RL/guardrail strategy layer selects "Follow-up"
   (`POST /api/qwen/followup`).

Separately, the RL state vector (`rl/env/interview_env.py`, per `CLAUDE.md`'s architecture summary
and `research/audit/rl_state_definition.md`) is 6-D: performance, avg_performance, confidence,
hesitation, progress, difficulty — all derived from the evaluator's deterministic score and the
audio pipeline's confidence/hesitation signals, not from Qwen. This audit did not re-derive the RL
state-vector wiring in depth (out of scope for this evaluator-focused pass) but found no Qwen
import in `rl/env/interview_env.py`'s neighborhood during the Qwen grep sweep across the repo.

---

## 4. `final_human_gold.csv` structure and existing validation artifacts

**VERIFIED FACT** (read-only inspection, no modification): `research/data/evaluator_benchmark/final_human_gold.csv`
has 65 lines total = 1 header + **64 data rows**, matching the claimed "64 constructed answers."
Columns: `case_id, rater1_score, rater2_score, rater3_score, max_pairwise_difference,
adjudication_required, final_gold_score, gold_method`. Row IDs run `BM-001` … `BM-064`.
`gold_method` is either `mean_of_three` or `expert_adjudication` (the latter appearing on rows with
larger `max_pairwise_difference`, e.g. `BM-006`: 0.25/0.10/0.34, diff 0.24, `expert_adjudication`).
**OBSERVATION**: this file contains only the three raters' per-case scores and the derived gold
label — **no question text, no candidate-answer text, and no model-predicted score column**. The
model's own predictions for these same 64 cases must therefore live in a separate file (not opened
in this pass, as it is outside the designated read targets) before any Spearman correlation against
this gold file can be computed; this file alone is the human-judgment half of that comparison, not
a complete benchmark artifact by itself.

**VERIFIED FACT**: `testing_and_evaluation/ml_evaluation/` contains exactly two files:
- `T-N06_evaluator_negative_and_edge_cases.py` — runs the real `evaluate()` on 10 adversarial/edge
  inputs (empty string, whitespace-only, single word, a ~16,500-character repeated-keyword string,
  garbled Unicode, SQL-injection-like text, an HTML script tag, punctuation-only, emoji spam, and
  one normal correct answer as a control) and asserts the function never raises and always returns
  a score in `[0,1]`. This is a **robustness/crash-safety** check, not an accuracy or correlation
  check — it does not assert anything about whether the *scores* are reasonable, only that they are
  bounded and the function doesn't crash.
- `T-N10_question_selector_correctness.py` — tests `agents/question_selector/question_selector.py`
  (difficulty-matching, topic-rotation, no-repeat enforcement). **This is unrelated to the
  evaluator's scoring** — its own docstring (lines 4–11) explicitly notes the question selector
  "has no FAISS/embedding dependency" and that the FAISS index is used only by the evaluator, not
  by selection. It does not validate S1/S2/R.

**VERIFIED FACT**: `testing_and_evaluation/Qwen_2.5_Evaluator_Validation_Report.md` and
`Qwen_2.5_Viva_Explanation.md` (both read in full) state the following validation inventory
explicitly and consistently with each other:
- The only quantitative score-validity evidence cited is "Spearman ρ vs. human consensus (0.38
  composite, frozen)... R-alone ρ=0.48, S1+R ρ=0.49" — consistent with the project's current
  canonical number (0.3812, rounded); **no instance of 0.9152, 0.8358, or 0.7400 was found in
  either document, or anywhere under `testing_and_evaluation/`, `final_deliverables/`, or
  `services/` in a targeted search of this audit's scope** (a repo-wide, cross-folder search for
  those exact strings was run across `testing_and_evaluation/`, `final_deliverables/`, and
  `services/`; zero matches in each).
- Both documents explicitly and repeatedly disclose that **no quantitative validation of Qwen's
  narrative-text quality exists** ("no formal, quantitative validation of Qwen's
  narrative-feedback/hint/follow-up text quality... was performed," "none is claimed to exist in
  this project's prior evidence record either").
- No calibration study, ablation study, or MAE/RMSE/accuracy/F1 metric for the evaluator or for
  Qwen's text was found or claimed in either document.

**What validation actually exists, summarized**: (a) one frozen human-rater correlation study
(ρ≈0.38 composite, exploratory per `CLAUDE.md`'s own framing), computed and stored outside
`testing_and_evaluation/` (per `CLAUDE.md`, in `research/data/evaluator_benchmark/` and
`research/results/paper3/`, not independently recomputed in this pass); (b) a 10-case crash/bounds
robustness smoke test; (c) 11 unit tests in `tests/unit/test_evaluator.py` asserting score-ordering
and threshold invariants on hand-written example answers (§5 below). There is **no** calibration
study (e.g. reliability diagram, score-vs-human-agreement by score band) and **no** formal ablation
of S1/S2/R's individual contribution beyond the two fixed comparator numbers (R-alone, S1+R) cited
above, which this audit did not re-derive.

---

## 5. Technical-quality assessment (INTERPRETATION, flagged per dimension)

All six items below are **INTERPRETATION** unless noted; each states what the code/tests actually
show, not an assumed property.

- **Concept coverage**: `tests/unit/test_evaluator.py::test_completely_correct_answer` (asserts
  `concept_coverage >= 0.75`, `missing_concepts == []`) and `::test_off_topic_answer` (asserts
  `concept_coverage == 0.0`) give **some direct evidence** that S2 behaves directionally correctly
  on two hand-picked extremes. There is no test sweeping intermediate coverage levels or checking
  S2's monotonicity/calibration against partial coverage beyond these two endpoints plus the
  ordering test (§ below). **Evidence exists, but it is narrow (hand-picked cases on one qid, qid
  "1," mostly).**

- **Length bias**: **UNKNOWN / untested.** No test, script, or code comment in
  `services/evaluator/app.py` or `tests/unit/test_evaluator.py` isolates answer length as a
  variable (e.g. same concepts stated tersely vs. verbosely). The `depth` diagnostic field (lines
  427) does scale with `len(sentences)`, but `depth` is explicitly excluded from `final_score`
  (comment at line 426, verified not referenced in the `final_score` computation). Whether S1/S2/R
  themselves are robust to padding/verbosity (a classic failure mode for embedding- and
  cross-encoder-based scorers) is not evidenced either way by anything found in this codebase.
  `test_keyword_stuffed_wrong_answer` (lines 114–128) is the closest related test, but it tests
  *keyword density with wrong logic*, not *length alone with equivalent correct content*.

- **Paraphrase handling**: **Some direct evidence exists.**
  `tests/unit/test_evaluator.py::test_paraphrased_correct_answer` (lines 213–229) constructs an
  answer to the Floyd's-cycle question using deliberately non-textbook phrasing ("two references
  traversing... at different velocities" instead of "slow/fast pointer") and asserts
  `final_score >= 0.60` and `grade in ("Good","Excellent")`. This is one hand-written example on one
  question, not a systematic paraphrase-robustness study, but it is genuine evidence the pipeline
  was specifically tested against (and apparently passes) at least one paraphrase case, consistent
  with S1/S2's embedding-based design intent (as opposed to exact keyword matching).

- **Incorrect-answer handling**: **Direct evidence exists**, and is the best-covered dimension.
  `test_completely_wrong_answer`, `test_confident_wrong_answer`, `test_off_topic_answer`, and
  `test_correct_terminology_incorrect_reasoning` all assert low scores (`<=0.35` or `<=0.45`) and
  `grade == "Poor"` for distinctly different failure modes (wrong algorithm, confidently-wrong
  content, off-topic content, correct vocabulary with inverted mechanics). The
  `mistake_penalty`/`_detect_misconceptions` machinery (lines 214–253, 319–347) is specifically
  designed around rubric-authored "mistake" vectors for this purpose, and is exercised by these
  tests (e.g. `test_completely_wrong_answer` asserts `len(incorrect_claims) > 0 or penalty > 0`).

- **Consistency**: `test_score_ordering_invariants` (lines 235–270) directly asserts
  `score(correct) > score(partial) > score(wrong) >= score(off_topic)` on one fixed question (qid
  "1"). This is evidence of **ordinal consistency on one item**, not evidence of consistency across
  different questions, rubrics, or repeated runs with (e.g.) reworded-but-equivalent inputs across
  many qids. **No test asserts run-to-run determinism explicitly** (the pipeline is built from
  deterministic operations — fixed model weights, no sampling — so determinism is an
  **INTERPRETATION** from the code's structure, not something a test directly confirms; no
  seed/temperature parameter exists to make it non-deterministic, which supports but does not
  prove the interpretation).

- **Overall pattern**: incorrect-answer handling and (to a lesser extent) paraphrase handling have
  direct, if narrow, test evidence. Length-bias robustness has **no evidence either way** —
  genuinely untested, not merely "probably fine." Concept-coverage and consistency evidence exists
  but is limited to a small number of hand-constructed cases on 1–2 of the question bank's items,
  not a systematic sweep.

---

## 6. Role classification — production app vs. evaluation/benchmarking vs. reference ratings vs. comparison-only vs. separate experiment

| Component | Production application | Evaluation/benchmarking process | Reference ratings | Comparison-only | Separate experiment |
|---|---|---|---|---|---|
| S1 (SBERT `all-MiniLM-L6-v2`) | **Yes** — `services/evaluator/app.py`, called live via `/api/evaluator/evaluate-answer` and `apps/backend/main.py::_run_integrated_evaluator` on every candidate answer. | Also used (same code) when the benchmark harness scores the 64 gold cases, since the benchmark presumably calls the same `evaluate()` (not independently re-verified in this pass; the gold CSV itself contains no model-score column, see §4). | No | No | No |
| S2 (FAISS + rubric vectors) | **Yes**, same call path. | Same as S1. | No | No | No |
| R (`tuned_model2` CrossEncoder) | **Yes**, same call path — this is the live, production scoring component, not a benchmarking-only artifact. | Same — the same frozen checkpoint is also what Paper 3's human-correlation study scored. | No (R *produces* scores; it is not itself a human reference) | No | No |
| The 64-case `final_human_gold.csv` | **No** — never loaded by `services/evaluator/app.py` or `apps/backend/main.py` in anything found in this pass. | **Yes** — this is the benchmarking/validation artifact used to compute the ρ=0.38 correlation. | **Yes** — this *is* the reference-rating file (3 human raters + aggregated gold). | No | Belongs to the frozen Paper 3 evidence package per `CLAUDE.md`'s frozen-artifact list. |
| Qwen (`services/qwen/app.py`) | **Yes**, but strictly for narrative feedback/hints/follow-ups (§3) — it is a live production microservice, not a benchmarking tool. | No evidence found of Qwen being used to *generate* or *adjudicate* benchmark labels. | No | No | No |
| `T-N06`/`T-N10` scripts | No — ad hoc read-only scripts, not part of the running app. | **Yes** — robustness/correctness checks against the real production code, run as a one-off investigation (`testing_and_evaluation/ml_evaluation/`). | No | No | Standalone, not pre-registered as X1/X2/X3 per `CLAUDE.md`'s experiment-registration rule — these appear to be ad hoc QA scripts, not a registered confirmatory experiment. |

**INTERPRETATION**: there is no conflation in the code between "the thing that scores candidates
live" and "the thing used to validate that scoring" — both use the *same* `evaluate()` function and
the *same* frozen CrossEncoder checkpoint, which is methodologically appropriate (you must validate
the exact deployed scorer, not a proxy) but also means the CrossEncoder's provenance gap (§2)
is a single point of uncertainty affecting **both** production scoring and the validation study
equally — it is not a case where an uncertain component is confined to one side of the evaluation
and a trusted component to the other.

---

## 7. Does current evidence justify a strong claim about evaluation quality? What would strengthen it? (INTERPRETATION)

**No — current evidence does not support a strong claim**, for reasons entirely consistent with
`CLAUDE.md`'s own framing ("exploratory/initial evidence only") and the two Qwen-validation
documents' own conclusions ("ρ≈0.38... explicitly framed as 'safety-hardened rather than
accuracy-optimal'"):

1. The sole quantitative human-agreement evidence is one Spearman correlation (ρ=0.3812, CI
   [0.158, 0.577]) from 3 raters on 64 constructed (not naturally occurring) answers to 8
   questions. The confidence interval is wide and the point estimate is moderate-to-weak by
   conventional correlation standards.
2. The CrossEncoder component responsible for 50% of the composite weight has an **incomplete and
   partially contradicted provenance** (§2) — its exact fine-tuning data/procedure cannot be
   audited, and a second candidate checkpoint with different weights and a different validation
   score existed and was discarded without a documented rationale. Any claim about *why* the model
   scores what it scores is limited by this gap.
3. Unit-test evidence (§5) is real but narrow: it demonstrates the pipeline behaves sensibly on a
   small number of hand-constructed, mostly single-question (qid "1") examples, which is good
   regression-test coverage but not generalizable accuracy evidence.
4. No length-bias test exists at all (§5) — a known failure mode for exactly this kind of
   embedding + cross-encoder composite, left fully unexamined.
5. The R-rescaling affine transform `(raw-0.20)/0.70` (§1) is an uncited, hand-set heuristic with
   no visible calibration procedure backing the three breakpoints it encodes.

**RECOMMENDATION** (what would meaningfully strengthen the evidence, consistent with
`CLAUDE.md`'s pre-registration requirements for any new experiment):
- A **pre-registered, larger confirmatory study** (the planned X2, per
  `research/audit/X2_PROTOCOL_DRAFT.md`) with more raters, more questions, and — critically —
  *naturally elicited* (not researcher-constructed) candidate answers, to address both the small-N
  and the construction-bias concerns in the current 64-case set.
- A **dedicated length-bias probe**: fixed rubric, several answers holding concept content
  constant while varying only length/verbosity, scored through the real `evaluate()` pipeline, to
  determine empirically whether S1/S2/R are length-sensitive — currently a complete blind spot.
- **Recovering or explicitly abandoning** the CrossEncoder's fine-tuning provenance (per
  `research/audit/P0_1_CROSSENCODER_FORENSIC.md` §5's own recommendations): either locate the
  original training notebook/data (the forensic doc suggests asking whoever ran it) and document
  train/validation overlap against the benchmark questions, or run a robustness comparison against
  the verified, unmodified upstream `cross-encoder/ms-marco-MiniLM-L-6-v2` checkpoint to bound how
  much the undocumented fine-tune actually changes scoring behavior relative to the public model —
  explicitly flagged in that document as requiring approval before execution, consistent with
  `CLAUDE.md`'s frozen-artifact and pre-registration rules.
- A **component ablation beyond the two existing comparator numbers** (R-alone ρ=0.48, S1+R
  ρ=0.49): e.g. S1-alone, S2-alone, and a sweep of the `CONCEPT_THRESHOLD`/`MISTAKE_THRESHOLD`/
  bonus-penalty constants' sensitivity, to show the chosen weights (0.15/0.35/0.50) and thresholds
  are not arbitrary relative to alternatives — none of this exists in the files inspected.
- An explicit **calibration study for the R-rescaling transform** (§1) — e.g. a documented mapping
  from a sample of raw CrossEncoder outputs on known-bad/known-partial/known-good answers to the
  three breakpoints currently hand-set in code, rather than an inline comment asserting the ranges.

---

## Appendix — files read for this audit

- `services/evaluator/app.py` (full file, 939 lines)
- `services/evaluator/models/tuned_model2/README.md`, `config.json`, `best_model_info.json`
- `requirements/evaluator.txt`
- `apps/backend/main.py` (lines ~80–250, evaluator wiring + audio-init scaffolding)
- `agents/orchestrator/feedback_agent.py` (lines 1–80, module docstring + misconception tables)
- `agents/validation/score_validator.py` (lines ~55–120, `ScoreValidator.validate`)
- `services/qwen/app.py` (MOCK_MODE block lines 232–300, 720–800 score-consumption sites)
- `tests/unit/test_evaluator.py` (full file, 271 lines)
- `testing_and_evaluation/ml_evaluation/T-N06_evaluator_negative_and_edge_cases.py` (full)
- `testing_and_evaluation/ml_evaluation/T-N10_question_selector_correctness.py` (full)
- `testing_and_evaluation/Qwen_2.5_Evaluator_Validation_Report.md` (full)
- `testing_and_evaluation/Qwen_2.5_Viva_Explanation.md` (full)
- `research/data/evaluator_benchmark/final_human_gold.csv` (read-only structural inspection: row/column
  count and sample rows; file not modified)
- `research/audit/P0_1_CROSSENCODER_FORENSIC.md` (full — pre-existing forensic analysis of the
  CrossEncoder checkpoint; cited extensively in §2 as the primary evidentiary source for
  provenance, since it performs a weight-level comparison this pass did not independently redo)
- `.github/workflows/ci.yml`, `docker-compose.yml` (EVALUATOR_MOCK_MODE usage sites)
- Targeted greps for `EVALUATOR_MOCK_MODE`, `Qwen`/`qwen`, and `0.9152`/`0.8358`/`0.7400` across
  `services/`, `agents/`, `apps/`, `tests/`, `testing_and_evaluation/`, `final_deliverables/`, and
  CI/compose config (not a full read of every matched file; matches outside this document's cited
  files were used only to route to the next file to read, not treated as evidence themselves).
