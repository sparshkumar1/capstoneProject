# P0 / P1 — decisions for you (2026-09-19)

Nothing has been run, changed or fixed. Detail and evidence: `P0_P1_DECISION_PLAN.md`. "Rerun" = a new experiment; wording/analysis corrections need none.

## 0. How the issues sort

| Bucket | Issues |
|---|---|
| **1. MUST FIX** (a claim is false or unsupported as written; needed before any manuscript) | P0-1 "off-the-shelf"; P0-3 "0 violations"; P0-4 "563 interventions"; P0-5 "0.088 vs 0.160"; P0-2 PPO attribution; P0-6 "10/10, 5/5, 9/9, 213"; P0-7 provenance wording |
| **2. CAN FIX WITHOUT RERUN** | P0-3, P0-4, P0-5; the wording side of P0-1, P0-2, P0-6, P0-7; P1-1, 2, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15 |
| **3. SHOULD RERUN** | None strictly. Closest: re-measure latency (P1-8) if a "warm latency" claim stays |
| **4. OPTIONAL STRONGER EXPERIMENT** | P0-1 upstream-checkpoint sensitivity; P0-2 PPO contribution study; P0-6 fault / Qwen / security campaign; P0-7 new human round (only if records fail) |
| **5. FUTURE WORK** | Outcome-based reward (P1-5); training-consistent environment (P1-4); more benchmark questions (P1-1); length/paraphrase-robust scoring (P1-2) |
| **6. USER / INSTITUTION** | User: every P0, P1-12. **Institution: P0-7 only** |

---

## P0-1 CrossEncoder provenance (Paper 2)

- **We know:** the model is a partially fine-tuned derivative of `ms-marco-MiniLM-L-6-v2` (layers 0–3 and embeddings identical; layers 4–5, pooler, head changed). "Off-the-shelf" is false. The evaluator's R mapping `(raw − 0.20)/0.70` also presupposes the derivative's output range. The file is hash-pinned, so results are reproducible *as a file*.
- **We don't know:** who trained it, on what data, with which split, why this run and not the deleted sibling; whether the 8 benchmark questions/references were in training.
- **You can choose:** A disclose · B recover records · C re-fine-tune from scratch · D switch to upstream and rerun · E both checkpoints as a sensitivity study.
- **My recommendation:** A now, plus B in parallel (cheap and decisive). E only if B fails and you want a leakage-free reference. Not C or D.
- **If you choose:** A → no numbers change; leakage stated as undetermined. B → may allow a "documented fine-tune" statement; if it shows overlap, a caveat is required. C → a new model, new labelled data needed, everything R-related changes. D → all R-dependent results change; needs a pre-specified R mapping first. E → adds one evaluation-only arm (1–3 days), existing results stay primary. **No option needs new human ratings.**

## P0-2 PPO contribution (Paper 3)

- **We know:** constant-Same + guardrails (MAE 0.673) equals PPO + guardrails (0.673–0.687); 5 of 125 sessions differ. Guardrails explain the whole improvement over fixed (1.200 → ≈0.67). Raw PPO helps modestly and inconsistently (0.804–1.138) for two low-skill personas. The heuristic (0.473) beats all PPO variants.
- **We don't know:** whether PPO adds anything on a larger persona set, or in a training-consistent environment.
- **You can choose:** A reframe · B new controlled study · C guardrail/adaptive-control paper · D change scope/title.
- **My recommendation:** A + C for the manuscript. Run B Stage 1 (evaluation-only, existing checkpoints, ≥ 24 pre-specified personas) only if you want a PPO claim. Stage 2 (retraining) only after Stage 1 and your approval.
- **If you choose:** A/C → publishable as a simulation study with a negative PPO finding; no new work. B → a pre-registered answer either way; I expect Stage 1 to show no PPO contribution. D → only if the reframed paper has no standalone question.

## P0-3 Out-of-bounds (Paper 3)

- **We know:** "0 violations" is a hard-coded literal and a simulator invariant that holds for every policy. Frozen files already show 232 attempted out-of-range actions (guarded) vs 136 (raw); all at the floor, i.e. no-ops. Guardrails do not block them.
- **We don't know:** anything about real safety harm (no outcome data).
- **You can choose:** wording of the replacement (recommended: "boundary-saturated actions" 10.9 % raw / 18.6 % guarded, plus the clamp as an implementation invariant).
- **My recommendation:** analysis correction in an addendum; no rerun.
- **If you choose:** the correction → the false headline is removed at no cost. Keeping "0 violations" is not defensible.

## P0-4 Guardrail interventions (Paper 3)

- **We know:** 563 rule activations (45.0 % of 1,250 turns); 99 action changes (7.9 %); 82 % of activations left PPO's action unchanged; 41 of 125 sessions had a change; only 64 changes lowered difficulty, 30 blocked a decrease.
- **We don't know:** what would have happened on unguarded trajectories (path-dependent).
- **You can choose:** the reported measures (recommended: activation, override, no-op share, session-level, per rule and persona).
- **My recommendation:** report both numbers with their names and denominators; "rescue" language dropped.
- **If you choose:** no rerun in any case.

## P0-5 Volatility (Paper 3)

- **We know:** 0.088 is seed 123 only. Five-seed guarded volatility is 0.186 (0.088–0.268) vs heuristic 0.160; pooled difference +0.026 [−0.024, +0.078]. Guardrails raised volatility about 2.4× over raw PPO (0.078 → 0.186; stored −140.21 %).
- **We don't know:** why seed 123 was the "main" seed (no rationale in the frozen config).
- **You can choose:** replace the claim with a five-seed trade-off table (recommended), or drop volatility.
- **My recommendation:** trade-off table; no "smoother than the heuristic".
- **If you choose:** no rerun.

## P0-6 Paper 1 evidence

- **We know:** fault (10/10) and Qwen (5/5) tables are literal PASS strings (fault: 1 evidenced, 5 partial, 4 none; Qwen: 3 partial, 2 none). All 9 attacks really ran; only 4 outcomes discriminate. `FeedbackValidator` does not exist. "213 passed" has no log. Concurrency and latency measurements are real (scope-limited).
- **We don't know:** whether the system actually tolerates the ten faults, or isolates Qwen, under real injection.
- **You can choose:** A narrow the claims and title · B fault-injection campaign · C Qwen isolation campaign · D all, plus a discriminating security oracle and a stored test report.
- **My recommendation:** A now. Keep "fault-tolerant / secure" in the title only after D, and run it with criteria fixed in advance (plan §8; ≥ 30 trials per scenario, computed PASS, stored logs). Don't rerun the frozen script; it would reprint the same PASS strings.
- **If you choose:** A → a smaller but true paper (title options in plan §5.3). B–D → weeks of harness work; may expose real defects (e.g. the missing validator), which would then need approval to fix.

## P0-7 Human ethics / provenance (Paper 2)

- **We know:** the gold data is reproducible and hash-pinned. The repository has no rater/adjudicator identities or qualifications, no consent, no compensation record, an unsigned checklist, no Gate 1 approval, and no institutional determination. Rater files appear 22–53 min after the freeze commit; sending times aren't recorded. I infer nothing about what happened, only that the repository can't show it.
- **We don't know:** whether records exist elsewhere; whether your institution or venue requires a determination.
- **You can choose:** A proceed with a transparent limitation · B ask the venue/institution first · C collect a new documented rating round · D seek an institutional determination.
- **My recommendation:** collect existing records first, then ask the institution (**INSTITUTIONAL DECISION REQUIRED** for A/B/D), then choose A or C. Never create retrospective consent or independence statements. Any later statement must be dated and labelled retrospective.
- **If you choose:** A → wording limited to what the files show (no "independent experts", "committee", "approved"). C → the current gold becomes a pilot; new consent, logs and a larger question set.

## P1 items (short)

| # | Decision | My recommendation |
|---|---|---|
| P1-1 Benchmark clustering (8 questions × 8 constructed answers; README wrong) | approve re-analysis file | Correct the description; add question-cluster and per-category sensitivity. Clustering does not inflate ρ here (0.38; question-cluster CI [0.30, 0.59]); the limit is 8 questions |
| P1-2 Concise-answer under-scoring | none | Report as a principal limitation (human 0.91 vs model 0.40 for concise-correct) |
| P1-3 θ/dampening tuned on a pilot sharing 4 questions | approve wording | Disclose; report the non-overlap subset (ρ 0.43 vs 0.71 on the overlapping four; exploratory) |
| P1-4 Training ≠ evaluation environment | none now | Disclose; a consistent environment belongs to the P0-2 study |
| P1-5 Oracle-imitation reward | approve framing | "Imitation of a rule oracle + rule-based shield" |
| P1-6 Sensitivity prose | none | Only avg-performance and difficulty change the action at the neutral point |
| P1-7 Deployed ≠ evaluated checkpoint | none | State which checkpoint each claim uses |
| P1-8 Cold-start latency | optional re-measure | Report median/percentiles; label the 26 s outlier |
| P1-9 Weak security criteria | linked to P0-6 | Wording now; oracles only in the campaign |
| P1-10 Hedging penalty vs "acoustic insulation" | none | Reword (penalty ≤ 0.03, only when content is already weak) |
| P1-11 Wrong long commit hash | none | Errata citing the real hash `b7cad49529c3…` and the tag |
| P1-12 Stale ρ = 0.6975 in root canonical file | **choose the authoritative file** | Handoff copy authoritative; supersession note in a new file; then update `CLAUDE.md` |

## What I need from you

1. P0-1: who trained the model, and go/no-go on asking them (and on option E).
2. P0-2: reframe only, or also run the PPO study (Stage 1)?
3. P0-6: narrow Paper 1 now, or build the campaign? Keep or change the title?
4. P0-7: can you collect the rater/adjudicator/consent/timing records, and will you ask your institution?
5. P0-3/4/5 and P1: approve the replacement wording; P1-12 authoritative file.

I will not start any of this until you decide.
