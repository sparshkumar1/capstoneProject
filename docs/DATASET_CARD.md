# PrepAIred Dataset Card

## Dataset overview

This repository contains several related datasets rather than one monolithic corpus:

- `data/questions/qns.json`: the curated interview question bank,
- `services/evaluator/assets/rubrics.json`: rubric metadata used by the evaluator,
- `ablation/results/ratings_*.csv`: human and synthetic rating outputs for evaluator analysis,
- `data/sessions/` and `logs/`: runtime session traces and reports.

## Composition

The main question bank contains theory-style C and DSA prompts across topics such as arrays, linked lists, trees, graphs, dynamic programming, recursion, and bit manipulation. Each entry includes:

- question id,
- topic,
- difficulty estimate,
- question text,
- expected time limit,
- Bloom level or type metadata.

## Collection process

Questions and rubrics are curated manually for interview practice. Ratings are produced through either:

- the interactive human rater workflow,
- or synthetic proxy generation for internal validation only.

## Recommended splits

There is no train/test split in the conventional ML sense. The practical separation is:

- question bank and rubrics for runtime use,
- rating CSVs for analysis,
- synthetic CSVs only for pipeline checks.

## Licensing and reuse

Reuse the question bank and derived reports only if your intended use is compatible with the project license and any source-specific constraints. Do not mislabel synthetic ratings as human data.

## Known risks

- The question bank is domain-specific and may overrepresent interview-style prompts.
- Ratings can be sparse for some questions or topics.
- Generated outputs should be regenerated whenever the underlying question bank changes.
