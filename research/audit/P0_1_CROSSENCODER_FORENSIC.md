# P0-1 — CrossEncoder Provenance Forensic (`services/evaluator/models/tuned_model2/`)

Forensic pass, 2026-09-19. Read-only: no model was retrained, no frozen artifact was edited, no evaluator was re-run.
Scripts and extracted blobs used for the comparison live in the session scratchpad, not in the repository.

## 0. Bottom line

**The evaluated checkpoint is a partially fine-tuned derivative of `cross-encoder/ms-marco-MiniLM-L-6-v2`. It is not off-the-shelf.**
The fine-tuning code, training data, validation data, hyperparameters and author/environment are **not recoverable from the repository, its Git history, or any file on this machine.**
The artifact is therefore **an incompletely documented derived checkpoint**, not a scientifically reproducible model artifact.

Two existing repository documents assert the opposite of the weight evidence
(`research/audit/PAPER2_MODEL_PROVENANCE_GATE.md`, `research/audit/data_lineage.md:44`, `benchmark_integrity_audit.md:128`,
`PRIORITY_0_FINAL.md:21`, `FINAL_CROSS_PAPER_AUDIT.md`, and the copies in `research/CLAUDE_HANDOFF/`). Those statements are **contradicted by the weights** and must not be carried into a manuscript.

## 1. Evidence

### 1.1 Tensor-by-tensor comparison against the upstream checkpoint (weight evidence — decisive)

Compared all 105 tensors of `tuned_model2/model.safetensors` (SHA-256 `6a241a55bef24355378db16a6380f03226fc9394312122afa648ec9e03a94450`) with the local HF cache copy of
`cross-encoder/ms-marco-MiniLM-L-6-v2` (snapshot `c5ee24cb`, SHA-256 `821d1aa69520101d…`). Parameter names differ only by LayerNorm naming (`gamma`/`beta` in the tuned file vs `weight`/`bias` upstream); I mapped these before comparing. Upstream has one extra non-parameter buffer (`position_ids`).

| Group | Tensors | Bit-identical to upstream | Max abs difference |
|---|---|---|---|
| Embeddings (word, position, type, LayerNorm) | 5 | **5 / 5** | 0 |
| Encoder layers 0, 1, 2, 3 | 16 each | **16 / 16 each** | 0 |
| Encoder layer 4 | 16 | **0 / 16** | 3.6e-3 |
| Encoder layer 5 | 16 | **0 / 16** | 6.1e-3 |
| Pooler | 2 | **0 / 2** | 2.6e-3 |
| Classifier (weight, bias) | 2 | **0 / 2** | 2.5e-3 (bias: 0.0 upstream → 1.39e-4) |

Total: 3,697,153 of 22,713,601 parameters (**16.28 %**) differ; the other 83.7 % are bit-for-bit identical.
Relative Frobenius change is small (about 1.7 % layer 4, 2.7 % layer 5, 7.3 % pooler), i.e. a low-learning-rate update.

Interpretation (mine, not stated in any repo file): a bit-exact frozen bottom (embeddings + 4 layers) with every top tensor changed is the signature of **deliberate partial fine-tuning with the lower layers frozen**. It is not what re-serialisation, format conversion, dtype casting or quantisation would produce (those would touch all tensors or change none).

### 1.2 No published upstream revision explains the difference

Using the HuggingFace Hub API I listed all 26 upstream commits of `cross-encoder/ms-marco-MiniLM-L-6-v2` (2021-04 to 2026-08). The LFS SHA-256 of `model.safetensors` is **`821d1aa69520…` for every revision that contains one**, and `pytorch_model.bin` is `3ae17b87eda3…` for every revision. The weights have never changed upstream. The tuned file (`6a241a55…`) matches **no** upstream revision.

### 1.3 A second, different fine-tuned checkpoint existed

`services/evaluator/models/1_best_model_zip/` (present in Git at commits `fe417c1` (as `Evaluator_final/Evaluator/1_best_model_zip/`) through `4e320d6`; deleted in `6885371` on 2026-08-29 as "unused legacy evaluator checkpoint") has:

- weights SHA-256 `b39a5cd7ffac23f51f31…` (≠ tuned_model2);
- identical `config.json` to `tuned_model2`;
- the same freeze pattern versus upstream (embeddings and layers 0–3 identical; layers 4–5, pooler, classifier changed);
- a **different** `best_model_info.json`: epoch 5, **global_step 1245**, val_spearman **0.7918**, val_huber 0.1119, val_rank 0.0832.

`tuned_model2/best_model_info.json` records epoch 5, **global_step 660**, val_spearman **0.785**, val_huber 0.1291, val_rank 0.0476.
The two checkpoints also differ from each other in layers 4–5, pooler and classifier. **There were at least two separate fine-tuning runs**, and the repository never says which one is "the" fine-tuned model, why `tuned_model2` was chosen, or whether it was selected using its validation Spearman.

### 1.4 `best_model_info.json` is a genuine training-run record, not an upstream artifact

Fields: `epoch`, `global_step`, `train_huber_loss`, `train_rank_loss`, `train_total_loss`, `val_huber_loss`, `val_rank_loss`, `val_total_loss`, `val_spearman`, `val_p_value`.
A joint **Huber (regression) + pairwise rank** objective with validation Spearman is a custom score-regression fine-tune. It is not an MS MARCO ranking record: the upstream model card documents no such record, and the upstream weights never changed (§1.2).
`PAPER2_MODEL_PROVENANCE_GATE.md` explains this file as "a legacy training record from UKPLab's original MS MARCO passage ranking run". That explanation has **no supporting evidence**; the file's two-run history (§1.3) and the weight differences (§1.1) contradict it.

### 1.5 Environment stamps show it was produced outside the project environment

`config.json` records `transformers_version: 5.0.0` and `sentence_transformers.version: 5.2.3`. The project `.venv` has `sentence-transformers 2.7.0` and `transformers 4.44.2` (and upstream's config says `4.4.2`). So the checkpoint was serialised by a **different environment** than the one in this repository (likely a hosted notebook — the repo documents Colab use for other experiments, but nothing documents it for this model; this is an inference).
The safetensors header also uses `LayerNorm.gamma/beta` names where upstream uses `weight/bias`, another sign of a different save path.

### 1.6 Supporting files add no provenance information

- `tuned_model2/README.md` is **byte-identical to upstream revision `c5ee24cb` (2025-08-29)**. It is just a copied model card. Its `base_model: cross-encoder/ms-marco-MiniLM-L12-v2` line is upstream's own metadata, **not** a statement about this fine-tune; it is also the origin of the repo's "MiniLM-L-12 / 12-layer" wording, which is wrong (config: 6 layers, hidden 384, i.e. an L6 architecture).
- `config.json`, tokenizer files: architecture only.
- `services/evaluator/app.py:46-47` simply does `CrossEncoder(str(BASE_DIR/"models"/"tuned_model2"))`; the repo has **no training script, dataset, loss config or notebook** for it. I searched all branches and all history for training-related file names, the `Huber|rank_loss|val_spearman|best_model_info` keywords, and for commit messages mentioning fine-tuning; nothing exists. The only hits are the artifacts themselves and the audit documents.
- The Git history of the model directory: first tracked as `Evaluator_final/Evaluator/1_best_model_zip` (`fe417c1`, 2026-04-10), then as `services/evaluator/models/tuned_model2` (`166ab55`, 2026-04-13). The working-tree file's sha256 equals the LFS pointer oid and the raw blob at `166ab55`, so the file has not changed since; the later file mtime (2026-04-17) is a materialisation artifact (my inference). The `.zip` in the sibling name suggests the run was downloaded as an archive, consistent with §1.5.

### 1.6b Repository statements about the model are mutually inconsistent

| Statement | Where |
|---|---|
| "off-the-shelf … zero fine-tuning … directory name is a scaffolding artifact" | PAPER2_MODEL_PROVENANCE_GATE, data_lineage:44, benchmark_integrity_audit:128, PRIORITY_0_FINAL:21, FINAL_CROSS_PAPER_AUDIT, CLAUDE_HANDOFF/* (incl. MANUSCRIPT_AUTHORING_GUIDELINES) |
| "Trained on general passage ranking pairs and generic reasoning entailment" (unsupported; no such dataset identified) | data_leakage_report.md:11 |
| "Fine-tuned CrossEncoder" | docs/EVALUATION.md:24,61; PREPAIRED_COMPLETE_BOOKLET.md; experiments/experiment_2_evaluation/README.md; CANONICAL_SCIENTIFIC_TRUTH.md:27 |
| "fine-tuned … on technical interview answer pairs" (unsupported) | docs/archive/superseded/paper/paper_draft_ieee_filled.md:92 |

The weight evidence supports "fine-tuned" (partially) and refutes "off-the-shelf / zero fine-tuning". It does **not** support any specific claim about *what* it was fine-tuned on (the two "fine-tuned on X" statements above have no evidence either).

## 2. Direct answers

1. **Was the evaluated checkpoint actually fine-tuned?** Yes, by the weight evidence (§1.1–1.4). Layers 4–5, pooler and classifier were changed; embeddings and layers 0–3 were frozen.
2. **When / by what code?** Not recoverable. Earliest repository evidence is 2026-04-10 (`fe417c1`, sibling checkpoint) and 2026-04-13 (`166ab55`, this checkpoint). The training code is absent; the config indicates an environment with transformers 5.0.0 / sentence-transformers 5.2.3, which is not the project environment. Author and platform are not documented.
3. **What training data?** Unknown. Objective is Huber + pairwise rank on a regression target with a validation split; the label source (human, LLM-generated, rubric-derived, synthetic) is unknown. `val_spearman` 0.785 refers to an unidentified validation set.
4. **Is the data recoverable?** Not from the repository, its history, `.cache`, or any file on this machine (no jsonl/csv/trainer_state/optimizer/checkpoint files found). It could exist off-machine (notebook environment, cloud drive, the original zip) — to be asked of whoever ran the training.
5. **Can the fine-tuning be reproduced?** No. There is no code, data, seed, hyperparameters, or split. The result could at best be approximated by a new fine-tune, which would be a *different* model.
6. **What can we honestly claim?** See §3.
7. **Reproducible artifact?** **Incompletely documented derived checkpoint.** The artifact itself is pinned (SHA-256, LFS pointer, verified byte-identical at `166ab55`), so any evaluation *of this exact file* is reproducible given the file. Its *construction* is not.

## 3. What can and cannot be claimed

**Supportable (with the hash):**
- "R is computed by a cross-encoder checkpoint derived from `cross-encoder/ms-marco-MiniLM-L-6-v2` (6-layer, 384-hidden BERT, one output). Relative to the public upstream weights, the embeddings and encoder layers 0–3 are unchanged and encoder layers 4–5, the pooler and the classifier head were modified by a fine-tuning procedure whose data, code and hyperparameters are not available. The checkpoint is identified by SHA-256 `6a241a55…4450`."
- "Paper 2 validates this exact frozen checkpoint as a black-box scorer against a human gold set." (This remains true and reproducible from the hash.)
- The checkpoint file is byte-identical to the one committed on 2026-04-13.

**Not supportable — do not write:**
- "off-the-shelf", "pre-trained only", "zero-shot", "no PREPAIred fine-tuning", "no domain adaptation" (refuted by weights).
- "fine-tuned on interview data / on technical interview answer pairs / on passage-ranking and entailment pairs" (no evidence of the data).
- "12-layer MiniLM-L12" (config is 6 layers).
- Any train/test independence or "zero data leakage" claim for the checkpoint (undecidable, see §4).
- Reporting `val_spearman 0.785` or the loss values as performance evidence (validation set unidentified).
- "tuned_model2 is a naming artifact" (contradicted).

## 4. Leakage status: undecidable, not "clean"

- Timing: the benchmark (`benchmark_cases.json`, 64 cases, 8 questions) first appears in Git on **2026-09-19**, five months after the checkpoint (April 2026). This makes it unlikely that the exact benchmark *answers* were in the training set, but Git dates alone are not proof.
- Overlap risk: 4 of the 8 benchmark questions appear verbatim in the legacy 100-question evaluator bank (`qns.json` qids 1, 3, 10, 41; the other four were not found in that legacy bank by text match). The bank's rubrics (`rubrics.json`, with reference answers) were the evaluator's own data at the time. Whether the fine-tune used that bank is unknown, so question- and reference-level leakage **cannot be excluded or confirmed**.
- The human gold (Sept 2026) postdates the checkpoint and could not have been used for training it. The N=20 pilot era ρ values (0.6975, etc.) are not evidence about this (they used the same checkpoint but the pilot labels' relation to training is unknown).

## 5. What would resolve it (recommendations only — USER DECISION REQUIRED)

1. **Ask the person who trained it** (or search their Colab/Kaggle/Drive/download history) for: the notebook/script, the dataset file(s), the split, hyperparameters, the run that produced `1_best_model_zip` and the one that produced `tuned_model2`, and the selection rationale. Add them as a new provenance file (do not edit frozen files).
2. **If recovered:** document the data source, labelling method, and check overlap of training/validation items against the 8 benchmark questions and their references; then the "fine-tuned, disclosed" claim can be made with a leakage statement.
3. **If not recoverable:** disclose as in §3, and consider a **robustness run of Paper 2's evaluator with the verified upstream checkpoint (`821d1aa6…`)** as R to bound the effect of the undocumented fine-tune. This requires a new evaluation (no retraining), so it needs explicit approval.
4. Correct or supersede the "off-the-shelf" statements in a new errata file; do not edit the frozen handoff documents.

## 6. Classification

`CONFIRMED` (as a provenance defect) + `EVIDENCE_GAP` (training data and code unrecoverable) + `DOCUMENTATION_ERROR` (audit documents assert "off-the-shelf").

## 7. Limits of this analysis

- The upstream comparison used one cached snapshot (`c5ee24cb`), but §1.2 shows all upstream weight revisions share the same hash, so the comparison holds for every published version.
- I did not verify whether the un-hyphenated id `cross-encoder/ms-marco-MiniLM-L6-v2` (used in docs) resolves to the same repo as `…L-6-v2` (used by the cache/API). Both refer to an L6 model in the docs.
- The "outside environment" and "download of an archive" points are inferences from version stamps and a folder name, not recorded facts.
