# PrepAIred Model Card

## Model overview

PrepAIred is a multi-component interview preparation system rather than a single model. The production loop combines:

- a question bank and rubric-driven evaluator,
- an RL-based difficulty policy with a 3-action space,
- a validation layer for score correction,
- a sandboxed code executor,
- optional audio and Qwen-assisted helper services.

## Intended use

The system is intended for technical interview practice, especially C language and DSA style questions. It is designed to:

- adapt question difficulty during a mock interview,
- provide structured feedback after each turn,
- surface missing concepts and reasoning gaps,
- help users rehearse speaking, coding, and explanation quality.

## Not intended for

- hiring decisions,
- automated ranking of candidates without human review,
- high-stakes assessment,
- unrestricted free-form code execution outside the sandbox.

## Training and tuning data

The RL agent uses the interview environment and reward shaping defined in the repo. The evaluator uses the curated rubric assets under `services/evaluator/assets/` and the question bank in `data/questions/qns.json`.

## Performance notes

Authoritative performance evaluations and statistical findings are grounded in the pre-registered research results under `research/results/`, the scientific manuscript [`docs/paper_draft_ieee.md`](paper_draft_ieee.md), and the numerical traceability ledger [`docs/PAPER_RESULTS_TRACEABILITY.md`](PAPER_RESULTS_TRACEABILITY.md).


## Limitations

- The system is optimized for structured interview prompts, not open-ended tutoring.
- Scores and feedback remain approximate and should be reviewed when used for research reporting.
- Synthetic evaluation data is useful for pipeline validation but must not be presented as human judgment.

## Ethical considerations

- Do not expose personal data unnecessarily in shared artifacts.
- Do not use the system as an automated decision engine for employment.
- Keep rater data and transcripts anonymized when sharing externally.
