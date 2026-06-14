# Human Rater Pack

Use this sheet to recruit and brief 2 to 4 external raters for the evaluator study.

## Goal

Collect at least 60 rated items in total across raters. Each rater should review the same answer set independently and save one CSV.

## What each rater sees

- Question text
- Candidate answer
- A 0 to 10 quality rating

Raters should not see the system score while scoring.

## Rater instructions

1. Open the web rater.
2. Read the question and answer carefully.
3. Score the answer on correctness, completeness, and clarity.
4. Skip only if the item is impossible to judge.
5. Save one CSV per rater.

## Suggested command

```powershell
python ablation\web_rater.py --answers ablation\data\ablation_answers.json --out ablation\results\ratings_rater2.csv
```

Repeat with `ratings_rater3.csv`, `ratings_rater4.csv`, and so on.

## Collection checklist

- Keep one file per rater.
- Use anonymous rater IDs in filenames.
- Preserve the raw CSVs.
- Do not merge files before the averaging step.
- Re-run the averaging and analysis pipeline after every new rater.

## After collection

```powershell
python ablation\run_human_eval_pipeline.py --no-synthetic --ratings `
  ablation\results\ratings_rater1.csv `
  ablation\results\ratings_rater2.csv `
  ablation\results\ratings_rater3.csv
```

Then regenerate the summary tables and figures from `ablation\results\`.
