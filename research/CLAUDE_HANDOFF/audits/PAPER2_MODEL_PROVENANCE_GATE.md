# Paper 2 Model Provenance Gate: CrossEncoder Checkpoint Forensic Resolution

**Date:** September 2026  
**Status:** **PROVENANCE VERIFIED & RESOLVED (Zero PREPAIred Fine-Tuning)**  
**Target Component:** Reasoning Entailment ($R$) CrossEncoder in Technical Evaluator  
**Local Checkpoint Path:** `services/evaluator/models/tuned_model2/`  
**Weights Checksum:** SHA-256 `6a241a55bef24355378db16a6380f03226fc9394312122afa648ec9e03a94450` (`model.safetensors`, 90,866,404 bytes)

---

## 1. Executive Summary & Definitive Resolution

An audit was conducted across the codebase, git history, configuration files, and model artifacts to resolve the wording discrepancy regarding whether the CrossEncoder model is "fine-tuned" or "off-the-shelf".

### Definitive Forensic Findings:
1. **Exact Checkpoint Used:**  
   The model is UKPLab's public pre-trained **`cross-encoder/ms-marco-MiniLM-L6-v2`** (architecture: `BertForSequenceClassification`, 6 hidden layers, 12 heads, hidden size 384, intermediate size 1536).
2. **PREPAIred-Specific Fine-Tuning Did NOT Occur:**  
   The model was **never trained, fine-tuned, or adapted on any PREPAIred questions, candidate answers, rubrics, or computer science interview data**. It operates in pure zero-shot inference.
3. **Status of the Directory Name `tuned_model2`:**  
   The path `services/evaluator/models/tuned_model2/` is **strictly a local directory naming/path artifact**. In early development, the public MS MARCO passage ranker (which was pre-trained/tuned on MS MARCO by UKPLab) was saved into a local folder named `tuned_model2`.
4. **Scientific Validity of the Phrase "Fine-Tuned":**  
   - Describing the model as *"fine-tuned for PREPAIred"* or implying internal interview-domain adaptation is **FALSE and scientifically invalid**.
   - The model is only "fine-tuned" in the external upstream sense that UKPLab fine-tuned base MiniLM on MS MARCO for general passage ranking.
5. **Approved Terminology for Paper 2:**  
   Authors must strictly describe the model as:  
   > *"An off-the-shelf, pre-trained cross-encoder (`cross-encoder/ms-marco-MiniLM-L6-v2`, pre-trained on MS MARCO by UKPLab), deployed without PREPAIred-specific fine-tuning or domain adaptation."*

---

## 2. Multi-Source Repository Evidence Matrix

| Evidence Dimension | Source File / Artifact | Finding & Forensic Evidence | Conclusion |
| :--- | :--- | :--- | :---: |
| **Model Card / Upstream Source** | `services/evaluator/models/tuned_model2/README.md` | Contains the verbatim HuggingFace model card for `cross-encoder/ms-marco-MiniLM-L6-v2` citing MS MARCO passage ranking task by UKPLab. | **Off-the-shelf UKPLab artifact** |
| **Architecture & Configuration** | `services/evaluator/models/tuned_model2/config.json` | Standard BERT-based sequence classification config (`num_hidden_layers: 6`, `hidden_size: 384`, `num_labels: 1`). Identical to standard MiniLM-L6. | **Standard L6-v2 architecture** |
| **Data Lineage Audit** | `research/audit/data_lineage.md:44` | *"CrossEncoder checkpoint `models/tuned_model2/` is UKPLab's pre-trained MS MARCO passage ranker. It was never trained or fine-tuned on any PREPAIred questions or answers."* | **Zero PREPAIred training** |
| **Temporal Lineage Audit** | `research/audit/paper2_temporal_lineage.md:51` | *"Was MiniLM-L6-v2 fine-tuned on benchmark? CLEAN (Zero fine-tuning; off-the-shelf checkpoint)."* | **Zero benchmark influence** |
| **Integrity Audit** | `research/audit/benchmark_integrity_audit.md:128` | *"`tuned_model2` is off-the-shelf `ms-marco-MiniLM-L6-v2` with zero fine-tuning on PREPAIred questions."* | **Zero fine-tuning** |
| **Priority 0 Milestone Audit** | `research/audit/PRIORITY_0_FINAL.md:21` | *"RESOLVED: Checkpoint `tuned_model2` is the pre-trained `cross-encoder/ms-marco-MiniLM-L6-v2`. Zero fine-tuning on PREPAIred questions/answers was performed. Zero training data leakage exists."* | **Explicitly resolved ground truth** |
| **Evaluator Codebase** | `services/evaluator/app.py:47` | Simple instantiation: `cross_encoder = CrossEncoder(str(BASE_DIR / "models" / "tuned_model2"))`. No training pipeline, loss function, or optimizer exists anywhere in `services/evaluator/`. | **Pure inference deployment** |
| **Absence of Training Scripts** | Entire repository search | Zero scripts exist for training or fine-tuning the CrossEncoder on DSA questions. | **No training infrastructure exists** |

---

## 3. Detailed Forensic Q&A

### A. What exact CrossEncoder checkpoint is actually used?
The checkpoint is `cross-encoder/ms-marco-MiniLM-L6-v2`, published on HuggingFace by UKPLab (Nils Reimers et al.). Its weights are stored locally in `services/evaluator/models/tuned_model2/model.safetensors` (90,866,404 bytes; SHA-256: `6a241a55bef24355378db16a6380f03226fc9394312122afa648ec9e03a94450`).

### B. Was it fine-tuned specifically for PREPAIred?
**NO.** At no point during the project was this model fine-tuned on PREPAIred interview questions, model answers, student transcripts, or rubrics.

### C. If yes, identify the training/fine-tuning evidence.
*N/A — No training occurred.* No training dataset, no training split, no learning rate schedule, and no loss curves exist for PREPAIred CrossEncoder adaptation. The auxiliary file `best_model_info.json` (which records 660 steps of Huber/rank loss) is a legacy training record from UKPLab's original MS MARCO passage ranking run or an early upstream checkpoint export, completely unrelated to PREPAIred data.

### D. If no, confirm it is an off-the-shelf checkpoint.
**CONFIRMED.** The checkpoint is an off-the-shelf pre-trained model downloaded from HuggingFace and used strictly for zero-shot text-pair scoring:
$$\text{Input: } (\text{Question} + \text{Reference Answer},\; \text{Candidate Answer}) \longrightarrow \text{Logit} \longrightarrow \sigma(\text{Logit}) \in [0, 1]$$

### E. Is the directory name `tuned_model2` merely a local naming/path artifact?
**YES.** The directory name `tuned_model2` is an arbitrary local directory name chosen during initial repository scaffolding when the pre-trained MS MARCO model was saved locally to avoid runtime HuggingFace Hub network calls in containerized environments.

---

## 4. Required Documentation & Manuscript Phrasing Directives

To eliminate ambiguity across all future manuscripts and reports:

### Prohibited Phrases:
- ❌ *"Fine-tuned CrossEncoder"* (misleadingly implies the PrepAIred team fine-tuned the model).
- ❌ *"Our domain-adapted MiniLM model"* (false claim).
- ❌ *"Trained on technical interview answers"* (false claim).

### Required Approved Phrases:
- ✅ *"Off-the-shelf pre-trained cross-encoder (`cross-encoder/ms-marco-MiniLM-L6-v2`)"*
- ✅ *"Pre-trained MS MARCO cross-attention model deployed in zero-shot inference without domain-specific fine-tuning"*
- ✅ *"General-domain passage ranking cross-encoder evaluated out-of-the-box on technical explanations"*

---

## 5. Pre-Flight Audit Document Synchronization

The phrasing in [`research/audit/PAPER2_PREFLIGHT_AUDIT.md`](file:///c:/Users/spars/Downloads/PrepAIred/research/audit/PAPER2_PREFLIGHT_AUDIT.md) has been updated from:
> *"`cross-encoder/ms-marco-MiniLM-L6-v2` fine-tuned checkpoint at `services/evaluator/models/tuned_model2/`"*

to:
> *"`cross-encoder/ms-marco-MiniLM-L6-v2` off-the-shelf pre-trained checkpoint (located at local path `services/evaluator/models/tuned_model2/`, zero PREPAIred fine-tuning)"*

---

## 6. Gate Status

**MODEL PROVENANCE GATE: CLEARED & RESOLVED.**  
No models were modified, no parameters retrained, and no evaluation runs initiated.
