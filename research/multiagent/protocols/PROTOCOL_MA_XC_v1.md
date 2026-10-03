# Protocol MA-XC v1 — decomposing the arbitration ablation and threshold sensitivity (REPLAY)

Written and tagged (`prereg/MA-XC/v1`) before any XC run. It is a **new, numbered experiment** that follows protocol MA-XA-XB v1; it does not amend that protocol or change any of its results.
Branch `research/adcom2027-multiagent-final`. Config: `configs/ma_xc_v1.json`. Code: `experiments/xc_threshold.py`, `analysis/analyze_xc.py`.

## Why (scientific question)
XA's condition M4 ("no arbitration") removes four things together: the confidence threshold τ, the evidence requirement, the one-step bound clamp and the guardrail layer
(`coordinator.decide_difficulty`, `use_arbitration=False`). The paper attributed the observed collapse of M4 (level changes 2.2, PPO agreement 0.014) to the missing confidence threshold,
but M4 cannot isolate that factor. XC isolates it by changing **only τ** and keeping evidence, bound clamp and guardrails in force, and measures how sensitive the full configuration is to τ (τ was fixed at 0.6 in advance, not tuned).

## Evidence class and limits
REPLAY on the same 160 sessions per condition as XA (8 recorded-answer sessions x 20 seeded question orders), real hub, frozen PPO, Qwen stubbed down, **no LLM, no human**. The sessions are dependent;
because that dependence is now known, the **primary interval for XC is a cluster bootstrap over the 8 recorded-answer sessions** (B = 10,000, seed 20270101); session-level intervals are not reported.
Behaviour metrics only; nothing here says which τ is better for interviewing.

## Conditions (config)
Full multi-agent configuration with agent timeout 2.0 s and τ in {0.0, 0.5, 0.6, 0.7, 0.8, 0.9}. Conditions TAU0, TAU5, TAU6, TAU7, TAU8, TAU9. Order within a (k, seed) cell is a seeded shuffle.
Strategy confidence is min(0.95, 0.5 + 0.1 n) for n cited evidence items and 0.45 for *steady* proposals, so τ = 0.5 and 0.6 admit exactly the same proposals (n >= 1) and exclude *steady*; τ = 0.0 admits *steady*.

## Registered predictions (criteria in `analysis/analyze_xc.py`)
- C1 TAU0 reproduces the collapse without removing the guardrail layer: mean PPO agreement < 0.10, mean level changes per session < 5.0, and no session with guardrail bypass. *(supports attributing M4's collapse to the threshold)*
- C2 TAU6 reproduces XA's M1 difficulty, score and question paths in every session (determinism check).
- C3 TAU5 equals TAU6 in every session.
- C4 mean decisions taken from a Strategy proposal are non-increasing over τ = 0.6, 0.7, 0.8, 0.9.
- C5 at τ = 0.9 the mean strategy-sourced decisions per session is below half of that at τ = 0.6. *(uncertain)*
Completion, authority and transition validity are expected to hold in every condition (as in XA); a violation would be reported as a defect.

## Reproduction
```
export EVALUATOR_MOCK_MODE=1
python research/multiagent/experiments/xc_threshold.py --out research/multiagent/results/xc
python research/multiagent/analysis/analyze_xc.py research/multiagent/results/xc research/multiagent/results/xa
```
