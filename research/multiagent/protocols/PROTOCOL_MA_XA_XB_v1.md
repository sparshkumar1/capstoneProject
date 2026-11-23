# Protocol MA-XA-XB v1 — multi-agent PREPAIred experiments (written before any reported result)

Branch `research/adcom2027-multiagent-final`. Config: `research/multiagent/configs/ma_xa_xb_v1.json` (its sha256 is recorded in each run's meta file).
Code at the tag `prereg/MA-XA-XB/v1`: `research/multiagent/experiments/*.py`, `research/multiagent/analysis/*.py`, `agents/multiagent/*`, the hub integration.

## 0. What is and is not being tested
Evidence classes: **REPLAY** (64 recorded production-evaluator payloads for 8 constructed questions × 8 constructed answers, driven through the real
`InterviewOrchestrator`; the evaluator itself does not run), **FAULT-INJECTED** (constructed agent faults), **SOCKET** (XE: real local HTTP server and timeouts),
**SYNTHETIC/AUTHORED** (XD: constructed feedback texts). **No LLM runs** (Qwen is stubbed as down; the hub's non-LLM fallbacks serve follow-ups and feedback);
the frozen PPO checkpoint runs unless a condition disables it. The "agents" are rule/ledger-based (see `ARCHITECTURE_ASSESSMENT.md`), not LLM agents.
The replay candidate never improves and follow-ups are answered with the root answer. **Nothing here measures candidate learning, coaching quality, evaluator
validity or LLM behaviour.** Measured: coordination behaviour, state-transition integrity, containment of agent faults, and overhead.
Not run: a persona-level SYNTHETIC tracking study (Paper 3 harness): the simulator has no concept-level evidence (so the Strategy Agent's distinguishing information is absent)
and its performance midpoint coincides with the evaluation target (a coupling the earlier audit flagged), so such a result would be uninformative or biased.

## 1. XA — baseline vs multi-agent vs ablations (REPLAY)
Units: session = (recorded-answer session k ∈ 0..7) × (question-order seed 0..19; seed 0 = original order, others a seeded shuffle) = 160 sessions per condition,
identical inputs across conditions. The 160 are **dependent** (the same 64 answers are reused); all intervals are descriptive/exploratory.
Conditions (config file): B0 baseline; B7 baseline without PPO; B0c baseline with `guardrail_impl=canonical`; M1 full multi-agent; M2 −Strategy; M3 −Coaching;
M4 −arbitration; M5 −grounding; M6 −communication; M7 M1 without PPO; M8 −authority enforcement; M1c M1 with canonical guardrails. τ = 0.6, agent timeout 2.0 s.
Order of conditions within a (k, seed) cell is a seeded shuffle (latency drift control).
Metrics (fixed here): completed; authority_ok (every committed raw score equals the recorded evaluator score of that transcript); transition_ok (levels ∈ [1,5]; every RL-phase decision
changes the level by ≤ 1); turns, followups, level_changes, reversals (sign changes of non-zero level steps), ppo_agree (fraction of RL-phase decisions whose final action equals the PPO/heuristic proposal),
guardrail_fires, strategy_source (decisions taken from a Strategy proposal), guardrail_bypass (decisions whose final action the hub's guardrail layer would still override), ungrounded_leak (accepted coaching plans emphasising a concept absent from the evidence),
agent calls, valid-proposal rate, conflicts (PPO action superseded by a Strategy proposal), per-turn latency (ms; pooled-turn p50/p95), session wall time, Qwen HTTP attempts.
**Registered predictions** (criterion in the analysis script `analysis/analyze_xa.py`):
- A1 completion 100% in every condition. A2 authority_ok 100% in every condition. A3 transition_ok 100% in every condition.
- A4 M2 reproduces B0 (difficulty, score and question paths) in every session.
- A5 M3, M5, M6, M8 reproduce M1's difficulty/score/question paths in every session (fault-free).
- A6 M4 has guardrail_bypass > 0 in ≥ 1 session while M1 has 0 in all. *(uncertain: agents may coincide with the guardrails on replay data)*
- A7 M1's difficulty path differs from B0's in ≥ 50% of sessions. *(uncertain)*
- A8 median per-turn latency M1 − B0 < 50 ms. *(uncertain)*
- A9 with PPO unavailable, M7 differs from B7 in ≥ 50% of sessions. *(uncertain)*
- A10 B0c differs from B0 in ≥ 1 session. *(exploratory)*
Descriptive, no directional claim: level_changes, reversals, followups, ppo_agree, guardrail_fires; paired mean differences with percentile bootstrap CI over sessions (B = 10,000, seed 20270101).
These metrics describe behaviour (stability proxies); a lower reversal count is **not** evidence of better interviewing.

## 2. XB — agent faults × ablated safeguards (FAULT-INJECTED on REPLAY)
Units: session = 8 × 5 order seeds = 40 per cell. Faults (config): Strategy {crash, timeout, malformed, forbidden_key, stale, nan_confidence, adversarial_valid},
Coaching {crash, malformed, stale, ungrounded}; faults fire at rate 0.3 per call (seeded), except `adversarial_valid` (valid proposal opposing the evidence, every call) and
`ungrounded` (valid plan emphasising an absent concept, every call). The real agent runs on non-faulted calls. Variants: full, no_authority, no_arbitration, no_grounding. Agent timeout 0.15 s.
**Registered predictions** (`analysis/analyze_xb.py`):
- B1 variant=full: every cell completes, authority_ok and transition_ok at 100%, no guardrail bypass, no ungrounded leak.
- B2 forbidden_key: full → authority_violation > 0 and schema_violation = 0; no_authority → authority_violation = 0 and schema_violation > 0; containment 100% in both
  (i.e. the strict schema alone contains it; the authority check changes classification, not containment).
- B3 adversarial_valid: no_arbitration has guardrail_bypass > 0 in ≥ 1 session; full has 0.
- B4 ungrounded: no_grounding leaks in ≥ 1 session; full has 0 leaks and rejects plans.
- B5 strategy timeout (full): pooled p95 per-turn latency exceeds the clean M1 p95 (from XA) by ≥ 100 ms.
- B6 crash/malformed/stale/nan cells (full): ≥ 80% of sessions see the per-agent breaker open at least once. *(exploratory: a consequence of rate 0.3 and a 60 s cooldown)*
Proportions: Clopper–Pearson exact 95%. A fault is "contained" only if the session completes **and** committed scores are authoritative **and** transitions are valid.

## 3. XD — grounding probe, rebuilt (SYNTHETIC/AUTHORED on REPLAY inputs)
Re-runs the earlier E3 probe (7 constructed feedback categories checked by the real lexical validator `_validate_feedback_output`) on three fixed subsets:
ALL (64; must equal the stored E3 counts — a check), NO_OVERLAP (47: covered/missing/incorrect lists share no string), RELABELLED (64: placeholder concept texts numbered uniquely).
A structural check before the run showed that all 64 stored payloads contain placeholder text, so a planned NO_PLACEHOLDER subset (empty) was replaced by RELABELLED.
Outputs: counts per category with Clopper–Pearson intervals for the "disagrees with intended label" proportion. No prediction is registered; the aim is to separate an evidence artefact from validator behaviour.

## 4. XE — historical reproduction and breaker semantics
- e1: re-run the historical E1 under explicit `strict_evaluator_contract=false`, breaker disabled, into a new directory; report whether `e1_runs.jsonl` is byte-identical to the stored file (prediction: yes).
- e5: re-run the historical E5 scenarios (real sockets, real 6 s timeouts) with current code; reported as a **new** run next to the stored values, not as a reproduction.
- b503: a service answering HTTP 503 to every request; breaker semantics legacy (any response = success) vs fixed (5xx = failure); one replay session. Prediction: fixed semantics sends far fewer HTTP attempts and lowers per-turn latency.

## 5. Deviations and disclosures (before the tag)
- Smoke runs (XA: 12 conditions × 8 sessions × 1 seed; XB: two fault kinds; XD: structural checks; XE b503) were executed into a scratch directory to debug the harness, and their summaries were seen.
  They led to three definitional fixes made **before** the real runs: (D1) `transition_ok` restricted to RL-phase decisions for the ±1 step bound, because the original baseline-phase schedule legitimately moves more than one level;
  (D2) the empty NO_PLACEHOLDER subset was replaced by RELABELLED; (D3) trajectory paths were added to each run record for exact-equality predictions. Smoke outputs are not reported.
- The smoke data suggested (not confirmed) that A6 and A9 might be contradicted; they are kept as registered.
- Any change after the tag is a new, numbered amendment and a new experiment.

## 6. Reproduction commands
```
export EVALUATOR_MOCK_MODE=1
python research/multiagent/experiments/xa_compare.py --out research/multiagent/results/xa
python research/multiagent/experiments/xb_faults.py  --out research/multiagent/results/xb
python research/multiagent/experiments/xd_grounding.py --out research/multiagent/results/xd
python research/multiagent/experiments/xe_historical.py --part e1   --out research/multiagent/results/xe_e1
python research/multiagent/experiments/xe_historical.py --part b503 --out research/multiagent/results/xe_b503
python research/multiagent/experiments/xe_historical.py --part e5   --out research/multiagent/results/xe_e5
python research/multiagent/analysis/analyze_xa.py research/multiagent/results/xa
python research/multiagent/analysis/analyze_xb.py research/multiagent/results/xb research/multiagent/results/xa
```
Environment note: runs use the scratch venv (Python 3.11, numpy/torch/sentence-transformers outside the repository's pins); the PPO checkpoint is the frozen `rl/checkpoints/seed_123`.
