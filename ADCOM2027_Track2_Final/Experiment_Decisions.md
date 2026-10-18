# Experiment / Content Decisions — ADCOM 2027 Track-2 Paper

Companion to `Research_Audit.md`. Applies the decision rule from the task brief — *"only add a new section,
experiment, baseline, metric, figure, table, or implementation change if, after inspecting the code, evidence,
venue requirements and scientific rationale, doing so genuinely improves the paper; otherwise record why not"* —
to every item the brief asked about. Nothing below has been executed. No approval has been requested or given for
any new experiment, per CLAUDE.md's preregistration requirement.

---

## 0. The decision this project actually needs first

`main.pdf` describes a Strategy Agent + Coaching Agent bounded-authority coordination layer and four experiment
campaigns (XA coordination/ablation, XB fault injection, XC threshold decomposition, XD grounding probe) that do
not exist in the `capstoneProject` repository (see `Research_Audit.md` §0). The user has confirmed this is
"genuinely not built yet" and has asked me not to invent content to paper over the gap. Before any of the
itemized decisions below are actionable, one upstream choice is needed — I am not making it, only naming it:

- **Option A — Build it.** Implement a real Strategy+Coaching bounded-authority layer on top of the existing
  single-policy orchestrator, then design and preregister XA–XD (or equivalents) properly, run them, and write
  the paper from real results. Large engineering + experiment effort; matches the task brief's ambition; requires
  the CLAUDE.md-mandated preregistration/approval steps for every new experiment.
- **Option B — Rescope the paper.** Keep `main.pdf`'s analytical frame (coordination vs. specialization vs.
  arbitration vs. authority as separable constructs) but apply it to what actually exists: the single PPO policy,
  its guardrails, and the already-frozen Paper 1–3 evidence (containment/fault-injection, evaluator diagnostics,
  PPO-vs-guardrail equivalence). This produces a smaller, fully truthful Track-2 paper reusing audited material.
- **Option C — Something else** (e.g. a much smaller, honest MAS pilot: build just enough of a second agent to
  run one real ablation, rather than the full four-campaign study).

Everything below assumes **no decision has been made yet** and is written to be useful under any of the three.

---

## 1. Introduction restructure (brief §4)
**Decision: RUN/WRITE FIRST only after Option A/B/C is chosen.** The restructuring itself (problem → existing
partial solutions table → gap → RQs → approach → contributions → scope) is good practice and low-risk to apply
to whichever system turns out to be the real subject. Drafting it now would require picking RQs that match either
a fictional or a real system — premature.
**Note on RQs:** the brief's suggested RQ1–RQ3 (behavioral testing / specialization / mechanism necessity) are
written for the Option-A system. Under Option B they would need to be rewritten around the single-policy system
and its existing guardrail/fault-injection evidence (which already exists in Papers 1 and 3).

## 2. Abstract rewrite (brief §5)
**Decision: DO NOT ADD (yet).** The brief's abstract spec requires the exact numbers this audit found don't exist
(160 sessions, −2.67 [−4.50,−0.24], 1,280/1,280, 57/57). Writing this abstract now would be writing the thing the
user explicitly asked me not to do ("don't add imaginary things").

## 3. System name usage (brief §6)
**Decision: KEEP AS-IS.** "PrepAIred" is the real system name (confirmed in `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`
and `CLAUDE.md`). No action needed regardless of Option A/B/C; just don't over-brand every paragraph.

## 4. Bloom taxonomy section (brief §7)
**Decision: ADD NOW (as a short, accurate paragraph), but only the verified facts.**
Verified facts (Research_Audit.md §1.2), safe to write today regardless of Option A/B/C:
- Schema: `qid, question_text, topic, difficulty, type, time_limit_sec, bloom_level`.
- Bloom bands are `L1`–`L6` (six, coded), not a named 5-band scheme — do not assume Understand/Apply/Analyze/
  Evaluate/Create.
- Bloom level is descriptive metadata; question selection uses the question's own numeric `difficulty` field only;
  no evidence Bloom affects selection, evaluation, RL state, or follow-up generation.
- Field-name mismatch: data uses `bloom_level`; `services/evaluator/app.py` uses `blooms_level` with a hardcoded
  `"Apply"` default in one place. Worth a one-line limitation note; arguably worth a separate small code fix
  (outside this paper's scope).
- No Bloom-aware vs. non-Bloom experiment exists. State plainly: *"Bloom metadata is a descriptive
  question-levelization mechanism; no experiment in the present study establishes an adaptive or learning
  benefit."*
**Decision on a new Bloom-aware vs. non-Bloom experiment: DO NOT ADD.** Would require new question-selection logic,
a new experiment design, and preregistration — disproportionate to what it would add, and the brief itself says
only add this if it "materially strengthens" the paper, which it would not for a Track-2 testing/coordination paper.

## 5. Evaluator weight selection (brief §8–§9)
**Decision: ADD NOW (short, factual), DO NOT re-tune.**
- State plainly, per Research_Audit.md §1.3: weights are an engineering default (in-code comment "FIX 4: R-heavy
  weights"), not a documented tuning result; θ=0.30 was chosen on a pilot that overlaps the evaluation benchmark.
  Never call them optimal/tuned/learned.
- **New evaluator-weight tuning experiment (brief §9): DO NOT ADD.** The brief's own gating condition —
  "if the dataset is too small to support credible tuning, do not run it" — applies directly. The human benchmark
  is 64 answers over 8 question clusters; any grouped/leave-one-question-out split would leave far too few clusters
  per fold for a defensible search-space comparison (current/CrossEncoder-only/word-count/equal-weight/reduced-R/
  R=0), and this evaluator is not the paper's main subject (per the brief's own §10 instruction to keep it
  secondary). Running it would add effort and a new experiment-governance burden for a result that would sit in
  an appendix at best.

## 6. Evaluator validity section (brief §10)
**Decision: KEEP AS SECONDARY, reuse Paper 2's existing numbers verbatim.**
ρ_R=0.4832, ρ_composite=0.3812, ρ_S1+R=0.4884 — verified against `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`
§C.2 and `paper2_summary_results.csv`. Note: the word-count baseline value 0.4897 and the "ρ_partial=0.2434,
95% CI [-0.008, 0.507]" figures from the brief were **not found verbatim** in the canonical doc as read in this
pass (the doc gives S1-only ρ=0.2070 with a CI that includes zero, not a labeled "ρ_partial"). **Do not use the
brief's 0.4897/0.2434/[-0.008,0.507] figures without re-tracing them to a specific stored file** — they may belong
to a different analysis (e.g. a partial-correlation controlling for length) that exists but that I have not located
in this pass. Flag as `[NUMBER TO VERIFY AGAINST SOURCE FILE]` if used.

## 7. PPO simulator / synthetic candidate model (brief §11–§14)
**Decision: ADD NOW, using only the verified figures in Research_Audit.md §1.4.** This is real, frozen, already
audited (Paper 3) evidence. Explicitly label it **SIMULATED** evidence per the brief's §12, and keep the existing
canonical-truth caveat verbatim: "PPO improves tracking" is a withdrawn claim; guardrails (not PPO) account for
essentially all of the improvement over the Fixed baseline. Do not re-derive or recompute any of these numbers —
they are frozen.
**Decision on strengthening PPO evidence with new personas/seeds/baselines (brief §13): DO NOT ADD in this pass.**
This would be new-experiment work requiring preregistration and is Paper 3's territory, not this paper's; CLAUDE.md
also bars retraining PPO or changing reward/state/action definitions without explicit approval.

## 8. Existing experiments XA/XB/XC/XD, split-vs-unified, grounding probe (brief §15)
**Decision: CANNOT KEEP AS-IS — they are not evidence that exists.** This is the direct consequence of
Research_Audit.md §0. I am not "verifying raw units" for XA/XB/XC/XD as the brief requests, because there are no
raw units in the repository to verify. If Option A is chosen, these would become genuinely new experiments,
subject to full preregistration. If Option B, they are simply not part of the paper; Paper 1's already-frozen
fault-injection/containment evidence and Paper 3's already-frozen guardrail-accounting evidence are the real
analogues and can be cited directly from `research/CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md`.

## 9. Property catalogue / fault coverage table / mutation testing (brief §16–§18)
**Decision: RUN EXPERIMENT FIRST, and only under Option A or C.** These are reasonable Track-2 contributions **in
general**, and would strengthen a real coordination-layer paper. But they presuppose the coordination layer and its
authority-boundary code exist to be tested. Under Option B they would instead apply to the existing single-policy
guardrail code (`rl/guardrails.py`), which is a smaller, already-partially-covered surface (Paper 3 already reports
guardrail-activation accounting). Mutation testing specifically: only worth doing if (a) it targets real
authority/guardrail code, (b) it's reproducible and low-risk (CLAUDE.md requires care around frozen RL code), and
(c) results would be new, not a restatement of Paper 3's existing guardrail-activation numbers.

## 10. Worked trace / observability (brief §19–§20)
**Decision: DO NOT ADD under current evidence.** Brief's own instruction: "If no trace is trustworthy, do not add
one." No coordinator/arbitration trace records exist (no coordinator exists). Not applicable until Option A.

## 11. Related work expansion (brief §21)
**Decision: ADD NOW, but citation-gated.** Independent of the Option A/B/C decision, strengthening related work
on agent testing, fault injection, observability, and formal/contract-based agent verification is safe low-risk
work — but every citation must come from Zotero or be marked `[CITATION TO VERIFY]`, per CLAUDE.md. Not started in
this pass since it depends on which system the paper ends up describing (the related-work framing differs
materially between Option A's MAS-testing paper and Option B's single-policy paper).

## 12. Page budget (brief §22) / structure (brief §23)
**Decision: Deferred.** Not actionable until scope is chosen. Flagged in Research_Audit.md §2 (3.8).

## 13. Claim discipline table (brief §24)
**Decision: KEEP, it's good practice regardless of Option A/B/C.** The brief's "supports / does not support" pairs
(M1–B0, M3≡M1, split=unified, fault injection, 57/57, PPO simulator) are a sound discipline *in general* — worth
reapplying to whichever real results end up in the paper. Cannot populate the left-hand claims with fictional
results now.

---

## Summary table

| Item | Decision | Why |
|---|---|---|
| Rewrite abstract/intro with brief's exact numbers | DO NOT ADD | Numbers don't trace to any artifact |
| Bloom taxonomy paragraph (verified facts only) | ADD NOW | Real, verified, low-risk |
| Bloom-aware vs. non-Bloom experiment | DO NOT ADD | No selection-logic hook exists; disproportionate |
| Evaluator-weight provenance statement | ADD NOW | Real, verified (in-code comment + canonical doc) |
| New evaluator-weight tuning experiment | DO NOT ADD | Dataset too small (8 clusters); not the paper's subject |
| Evaluator validity (ρ figures) | KEEP AS SECONDARY | Reuse Paper 2 numbers verbatim; verify two disputed figures first |
| PPO simulator description (frozen Paper 3 figures) | ADD NOW | Real, frozen, verified |
| New PPO personas/seeds/baselines experiment | DO NOT ADD | New-experiment governance; Paper 3's territory |
| XA/XB/XC/XD results as written in main.pdf | CANNOT KEEP AS-IS | Do not exist in repo |
| Property catalogue / fault coverage table | RUN EXPERIMENT FIRST (Option A/C only) | Presupposes coordination-layer code |
| Mutation testing | RUN EXPERIMENT FIRST (Option A/C only), gated on safety/novelty | Same |
| Worked trace | DO NOT ADD | No trustworthy trace exists |
| Related-work expansion | ADD NOW (citation-gated) | Low-risk, but framing depends on Option chosen |
| Claim-discipline table structure | KEEP (as a pattern) | Good practice; cannot populate yet |
