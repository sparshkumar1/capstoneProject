# Model Provenance Enquiry — DRAFT, NOT SENT (2026-09-19)

**Status: draft for the user to review, complete and send. Claude has not contacted anyone.** Do not send on Claude's behalf. Fill the bracketed fields. Keep a copy of the sent message and every reply with its native metadata (they become provenance records; hash them when stored).

**Who to send it to:** the person who trained or supplied the evaluator's CrossEncoder checkpoint (`services/evaluator/models/tuned_model2/`). If it is not certain who that is, the first question in §3 is "who trained this?", and the message can go to the people who had access to the model-training notebooks/cloud drive in April 2026.

---

## Draft message

**Subject:** Request for records about the fine-tuned cross-encoder checkpoint used in PREPAIred (Paper 2)

Hello [NAME],

We are documenting the provenance of the cross-encoder checkpoint used as the reasoning component ("R") of the PREPAIred evaluator, because a research paper will describe it and we want the description to be accurate.

**What we found (from the files only).**
- The file is `services/evaluator/models/tuned_model2/model.safetensors`, SHA-256 `6a241a55bef24355378db16a6380f03226fc9394312122afa648ec9e03a94450`. It has been unchanged since it was committed on 2026-04-13.
- Comparing tensors with the public model `cross-encoder/ms-marco-MiniLM-L-6-v2` shows that the embeddings and encoder layers 0–3 are identical to the public model, while layers 4–5, the pooler and the classifier head differ (16.28 % of parameters). So it is a partially fine-tuned derivative, not the public model as released.
- A small file, `best_model_info.json`, records a Huber + rank objective, epoch 5, step 660, validation Spearman 0.785. A second checkpoint (step 1245, validation Spearman 0.7918) existed and was deleted on 2026-08-29.
- The training code, data, split, hyperparameters and author are not in the repository, its history, or the machines we have checked.
- The model's `config.json` is stamped with transformers 5.0.0 / sentence-transformers 5.2.3.

**Why it matters.** The paper must say what the model was trained on and whether any of the training data overlaps the evaluation benchmark (8 questions with reference answers and 64 constructed candidate answers; four of the questions also appear verbatim in the evaluator's legacy question bank). If this cannot be established, the paper will say so. We are **not** asking anyone to reconstruct or re-create anything — only to share what already exists.

**Please share whatever already exists (existing records only)**
1. Who trained the model, when, and on which machine/notebook/cloud environment.
2. The training notebook or script (as it was run), and the exact library versions used.
3. The training data files (or a description if they cannot be shared): source, how the labels were produced, number of examples, and who produced the labels.
4. The train/validation split (files or the rule and seed used) and whether it was split by question.
5. Whether any of the following were included in training or validation data: (a) the 8 benchmark questions or their reference answers, (b) any of the 64 benchmark answers, (c) the 20-answer pilot set, (d) any text from the evaluator's question bank/rubrics (please say which).
6. Hyperparameters (learning rate, batch size, epochs, loss weights, seed), base model revision, and whether the base model was the public `cross-encoder/ms-marco-MiniLM-L-6-v2`.
7. Which layers were trained or frozen, and why layers 4–5 only.
8. Why this checkpoint (step 660) was chosen over the deleted step-1245 sibling, and who decided.
9. Any other checkpoints, logs, evaluation outputs or notes (including the location of the deleted sibling if a copy exists in a backup, download archive or cloud drive).
10. Anything you are unsure about — "I don't remember" is a useful answer.

**How the answers will be used.** We will state in the paper only what the records show, label anything unrecorded as unknown, and cite your records by description (and, if you wish, by acknowledgement). We will not describe the training data unless a record supports it. If you prefer not to be named, say so.

Please reply by [DATE] if possible; a partial answer is fine. If it is easier, a short call followed by you sending the files is also fine — please still send the original files so we can hash them.

Thank you,
[YOUR NAME]

---

## Reply-tracking table (to be filled by the user)

| # | Item requested | Received? (Y/N/partial) | Date received | File (SHA-256 after storing) | Notes |
|---|---|---|---|---|---|
| 1–10 | as above | | | | |

## What Claude will do with the reply (after the user shares it)
1. Store received files under a new provenance folder (e.g., `research/provenance/crossencoder/`), hash each, and never modify originals.
2. Write a new `CROSSENCODER_PROVENANCE_ADDENDUM.md` (facts only; unknowns labelled), and update registry row `P2-C003` only with user approval.
3. Run an overlap check between recovered training/validation text and the benchmark questions/references/answers (a static text comparison, not an experiment) and report the result whichever way.
4. If the records are absent: keep the wording "partially fine-tuned derivative with incomplete provenance"; rely on X2-B (upstream sensitivity) and the temporally disjoint stratum of X2-C for the leakage question.

## Cautions for the sender
- Do not send API keys, credentials or personal data.
- Do not ask the trainer to re-run or "recreate" anything; a re-created model is a **different model** and would not be provenance.
- Do not paraphrase memories as facts in the paper; only records count.
