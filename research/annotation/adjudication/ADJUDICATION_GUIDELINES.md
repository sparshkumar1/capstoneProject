# Human Gate 3: Blinded Adjudication Guidelines

**Status:** Awaiting Human Adjudicator Scoring  
**Audit Scope:** 10 Divergent Benchmark Cases ($\Delta_{\max} > 0.20$)  
**Reference Document:** `SCORING_RUBRIC.md`

---

## 1. Objective of Adjudication

During the independent evaluation of the 64-case benchmark dataset:
- **54 cases** achieved consensus ($\Delta_{\max} \le 0.20$) where the arithmetic mean of the three ratings is adopted as the reference score.
- **10 cases** exhibited pairwise disagreement exceeding $0.20$ ($\Delta_{\max} > 0.20$).

As the expert adjudicator, your role is to review these 10 items, examine the three independent anonymized human ratings (`Rater A`, `Rater B`, `Rater C`) and their qualitative rationales, and assign **one final adjudicated gold score** ($s \in [0.00, 1.00]$) and a brief justification for each item.

---

## 2. Adjudicator Blinding Invariant

To maintain scientific validity:
- You are provided with:
  1. The Question text
  2. The Candidate Answer text
  3. The three independent human ratings and comments (anonymized as Rater A, B, C)
  4. The standardized scoring rubric (`SCORING_RUBRIC.md`)
- **Strict Exclusions:**
  - You must NOT see or use automated model predictions, SBERT/FAISS similarity scores, CrossEncoder values, or evaluation predictions.
  - The identity, background, and academic rank of Raters A, B, and C are masked to prevent authority bias.

---

## 3. Rubric Reminders for Adjudication

Please calibrate your adjudicated scores against the standardized rubric anchor bands:
- **$[0.85, 1.00]$ — Optimal / Complete:** Fully correct algorithmic approach, optimal complexity, clear mechanics.
- **$[0.65, 0.84]$ — Correct / Suboptimal or Minor Gaps:** Sound logic with suboptimal time/space complexity or minor omitted details.
- **$[0.40, 0.64]$ — Partial / Incomplete:** Mentions correct data structure or initial steps, but procedural execution has major gaps.
- **$[0.15, 0.39]$ — Superficial / Misconception:** Severe logical flaws, invalid algorithmic assumptions, or superficial jargon.
- **$[0.00, 0.14]$ — Unacceptable / Off-Topic:** Completely incorrect, evasive, or ungrammatical keyword dumps.

### Critical Rubric Policy: Keyword Stuffing
> **Keyword Stuffing & Jargon Policy:** If an answer simply recites keywords or jargon without coherent grammatical or algorithmic structure explaining the step-by-step logic, the score **MUST NOT exceed 0.40**.

---

## 4. Instructions for Returning Adjudicated Scores

1. Open `ADJUDICATION_FORM.csv` in your preferred editor.
2. For each of the 10 cases (`BM-006`, `BM-014`, `BM-019`, `BM-022`, `BM-030`, `BM-038`, `BM-046`, `BM-051`, `BM-054`, `BM-062`):
   - Review Question, Candidate Answer, and the three rater perspectives.
   - Enter your final score in `final_adjudicated_score` (decimal in $[0.00, 1.00]$).
   - Enter a brief explanation in `adjudicator_reason`.
3. Save and return the completed file to the study administrator.
