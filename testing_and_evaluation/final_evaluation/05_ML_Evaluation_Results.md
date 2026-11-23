# ML Evaluation Results — Final Evaluation Phase

## 1. Composite Evaluator — Formula Re-Verification

Re-read directly from `services/evaluator/app.py` this phase (unchanged from the prior audit, confirmed byte-identical — no drift):

```
S1 = mean over rubric "semantic" targets of max cosine similarity to any candidate sentence   (SBERT all-MiniLM-L6-v2, off-the-shelf)
S2 = fraction of rubric "concept" groups with best-match similarity > 0.30                     (FAISS-retrieved rubric vectors)
R  = clip( (CrossEncoder.predict(ref, cand) - 0.20) / 0.70, 0, 1 )                              (local checkpoint, see §3)
S2_eff = S2 if R > 0.30 else S2 * 0.60
score = 0.15*S1 + 0.35*S2_eff + 0.50*R  (+ bonus - penalty), capped at 0.60 if a mandatory concept is missing
```
Confirmed identical to the formula cited throughout the prior audit and the IEEE paper draft. No change this phase.

## 2. Reconciling the Flagged Numeric Discrepancies (ρ=0.4825 vs 0.4832, ρ=0.4897 vs 0.4884)

This phase was explicitly instructed not to cite these values again without reconciling them. The reconciliation, traced directly to the two primary source artifacts rather than any intermediate summary document:

**Source A — `research/results/paper2/paper2_ablation_results.csv`** (the frozen, primary Paper-2 ablation table):

| Configuration | Spearman ρ | 95% CI |
|---|---|---|
| R only (CrossEncoder) | **0.4832** | [0.2501, 0.6762] |
| S1 + R (0.23/0.77) | **0.4884** | [0.2624, 0.6751] |
| Full Composite (deployed, 0.15/0.35/0.50) | 0.3812 | [0.1575, 0.5774] |

**Source B — `research/confirmatory/X2-B/results/X2B_REPORT.md`** (a separate, later, explicitly-exploratory robustness-check pipeline, protocol `prereg/X2-B/v1`, using a **two-level cluster bootstrap** CI method, distinct from Source A's CI method):

| Scorer | Spearman ρ | 95% CI |
|---|---|---|
| `ref_R_mapped` (the same deployed CrossEncoder as Source A's "R only") | **0.4832** | [0.2453, 0.6956] |
| `derived_ce` (a **different**, separately-constructed scorer — not the deployed R) | 0.4825 | [0.2440, 0.6953] |
| `length_only` (trivial word-count baseline) | **0.4897** | [0.2186, 0.7080] |
| `ref_composite_deployed` (the same deployed composite as Source A's "Full Composite") | 0.3812 | [0.1529, 0.6473] |

### Finding

- **0.4832 is not in conflict with itself.** The deployed CrossEncoder's correlation is **0.4832 in both pipelines** (Source A's "R only" row and Source B's `ref_R_mapped` row refer to the identical scorer on the identical 64-case benchmark). The two pipelines' **confidence intervals differ slightly** ([0.2501,0.6762] vs [0.2453,0.6956]) purely because they use two different, independently valid CI methods (Source A's method vs Source B's explicitly-stated two-level cluster bootstrap) — **not** because the underlying data or point estimate differ. `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` and this project's other current documents use Source A's CI; this phase adopts the same convention for consistency and records Source B's CI here as a cross-check, not a replacement.
- **0.4825 is a different quantity, not a mistyped 0.4832.** Source B's own report explicitly separates `derived_ce` (0.4825) from `ref_R_mapped` (0.4832) as two distinct scorers, and defines a "primary contrast (derived minus upstream)" specifically *because* they are different things. Any document that cites "0.4825" should label it as the **X2-B exploratory "derived" cross-encoder scorer**, never as a second measurement of the deployed R. No prior project document was found, in this phase's check, to have actually conflated the two under one label — the "discrepancy" was a risk of future misreading, now closed by this explicit record.
- **0.4897 vs 0.4884 is not a discrepancy to resolve — it is the intended, correctly-reported comparison.** 0.4897 is the `length_only` trivial baseline (Source B); 0.4884 is the `S1+R` weighted composite (Source A) — two different, legitimately different configurations that happen to produce close values. Their closeness **is the finding already on record** (a trivial length-based baseline performs comparably to a more sophisticated weighted composite) — not a computational inconsistency requiring correction. The IEEE paper draft's Table I already cites both correctly, under their correct distinct labels ("Word-count baseline" and "S1 + R"), so no correction to that document was needed.

**Conclusion:** no numeric error was found anywhere in this reconciliation. All four values are internally consistent once correctly attributed to their source pipeline and configuration. This record exists so future citations use the precise, disambiguated label (pipeline + configuration), not a bare number.

## 3. CrossEncoder Provenance — Re-Verified This Phase

| Field | Value | Verification method this phase |
|---|---|---|
| Loaded from | `services/evaluator/models/tuned_model2/` (local directory, not a HuggingFace hub id) | Direct re-read of `services/evaluator/app.py:47`, unchanged |
| Weight-file SHA-256 | `6a241a55bef24355378db16a6380f03226fc9394312122afa648ec9e03a94450` | Recomputed fresh this phase, matches the value independently recomputed in the prior audit — no drift |
| Fine-tuning extent | 16.28% of parameters (encoder layers 4–5, pooler, classifier) differ from the public `cross-encoder/ms-marco-MiniLM-L-6-v2` checkpoint; 83.7% bit-identical | From `research/audit/P0_1_CROSSENCODER_FORENSIC.md` (not re-run this phase — a full tensor-level diff is outside this phase's scope and the forensic document is itself a frozen artifact); cross-checked for internal consistency against the hash above, which matches |
| Training data/procedure | **Not recoverable.** No training script, dataset file, or commit message referencing the fine-tuning run exists anywhere in git history or on disk (confirmed by the forensic document, not independently re-searched from scratch this phase) | — |
| A second, discarded checkpoint existed (`global_step=1245, val_spearman=0.7918`), removed from git in a prior commit, with no documented selection rationale for why `tuned_model2` was kept instead | Unchanged finding | — |

**Description used in this phase's documents, consistent with the evidence:** "a partially fine-tuned derivative of `cross-encoder/ms-marco-MiniLM-L-6-v2`, with incomplete training provenance." **Never** described as "fully trained," "fine-tuned on PrepAIred data," or "off-the-shelf" — none of those three descriptions is supported by the available artifacts.

## 4. Evaluator Quality Testing — What This Phase Adds Beyond Crash-Safety

The pre-existing `T-N06` script (re-run fresh, §Initial Testing Audit) establishes **output-range safety** (10/10 adversarial inputs stay in [0,1], no crash) — this is explicitly **not** the same claim as answer-evaluation quality, and this phase does not conflate them. The pre-existing `tests/unit/test_evaluator.py` (part of the full pytest suite, re-run fresh, unchanged pass status) provides narrow but genuine **output-correctness** evidence on hand-picked cases: `test_completely_correct_answer`, `test_off_topic_answer`, `test_paraphrased_correct_answer`, `test_score_ordering_invariants` (`score(correct) > score(partial) > score(wrong) >= score(off_topic)` on one fixed question), `test_keyword_stuffed_wrong_answer`.

**What remains unestablished, stated honestly rather than closed by this phase:** length-bias robustness (no test isolates length as the sole variable while holding concept content fixed — still a complete blind spot); systematic paraphrase robustness across many questions (only one hand-constructed example exists); MAE/RMSE/Pearson against a broader, naturally-elicited answer set (the only human-correlation evidence remains the existing, frozen 64-case/3-rater study — this phase did not and was not instructed to collect new human ratings). A length-bias probe was considered in scope for this phase but was not executed, because constructing a valid, non-arbitrary length-controlled answer set that doesn't itself introduce confounds requires careful rubric-specific design beyond what could be responsibly completed in this phase — it is recorded as a specific, concrete recommendation in `14_Executive_Summary.md` rather than attempted superficially.

## 5. Human-Correlation Data — Independence and Clustering Check

Re-examined `research/data/evaluator_benchmark/final_human_gold.csv` (hash re-verified this phase: `363dbe6d848a04fe18be5ef1d30b6bbf63b54248fe758e5e6bd4c27a26c06ce2`, matching the prior audit, no drift) and the two source pipelines' own stated methodology (not re-implemented from scratch this phase, since both `paper2_ablation_results.csv` and `X2B_REPORT.md` already disclose their CI methodology in a way this phase can verify without re-deriving):

- **64 answers across 8 questions** means answers are **clustered by question** (8 answers per question on average) — both source pipelines' own documentation acknowledges this. Source A's CSV does not state its CI method explicitly in-file; Source B explicitly states "two-level cluster bootstrap" and lists "8 question clusters" as a stated caution.
- **This phase's finding:** Source B's CI methodology is the more rigorous, cluster-aware one, and its point estimate for the deployed composite (0.3812) and deployed R (0.4832) match Source A's point estimates exactly — meaning the clustering structure does not appear to change the point estimates, only (modestly) the CI width. This is a positive finding for the main pipeline's point-estimate robustness, reported honestly rather than silently assumed.
- **Inter-rater reliability** (ICC/Krippendorff, reported elsewhere in this project's evidence record as 0.9528/0.9838/0.9523) was **not recomputed from raw rater files this phase** — doing so was judged lower priority than the reconciliation above, given the time available, and is recorded as deferred, not silently skipped.

## 6. Qwen's Role — Score-Separation Re-Confirmed Live (not just by static reading)

Previously established only by static code reading (`Independent_Project_Audit`) and reconfirmed this phase by actually calling the real, live Qwen service: every scored-turn feedback call observed in this phase's live testing returned a `final_score` that is a plain float, set before any Qwen call exists in the call chain (`apps/backend/main.py::_run_integrated_evaluator`), never overwritten by Qwen's response. See `07_Qwen_Feedback_Quality_Evaluation.md` for the full, newly-added quality evaluation of what Qwen actually generates.
