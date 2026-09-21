"""Final-pass prose edits (2026-09-21): replaces the templated "Shows / Does not show" discussion scaffolding with plain
prose in P1, P2 and P3 and removes one sentence about an unavailable tool review from P1. Meaning, numbers and hedges are
kept; each replacement is asserted to match exactly once per file. Re-runnable: a file that no longer contains the old
paragraph is reported and skipped."""
import re, io, sys
B = r"C:\Users\spars\Downloads\PrepAIred\paper\manuscripts"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def para_edit(path, start, new):
    t = open(path, encoding="utf-8").read()
    pat = re.compile(r"^" + re.escape(start) + r".*?$", re.M)
    n = len(pat.findall(t))
    if n != 1:
        print(f"  skip ({n} matches): {start[:50]}"); return
    t = pat.sub(lambda m: new, t)
    open(path, "w", encoding="utf-8").write(t)
    print(f"  ok: {start[:50]}")

def text_edit(path, old, new):
    t = open(path, encoding="utf-8").read()
    if t.count(old) != 1:
        print(f"  skip ({t.count(old)} matches): {old[:50]}"); return
    open(path, "w", encoding="utf-8").write(t.replace(old, new)); print(f"  ok: {old[:50]}")

# ---------------------------------------------------------------- P1 (full manuscript and ICETC port)
P1_CONT = ("**Containment.** Under the tested configuration, harness and machine, each of the nine fixed programs met its criteria, and the "
           "permissive controls show that the oracles can register a breach. The result says nothing about adaptive attackers, kernel or runtime "
           "escapes, other network paths or platforms, or programs outside the nine. Host-side observables, weakened controls and repetition follow "
           "benchmark practice [1], [6], [7]; nothing here is a new escape result. A passing status would not have told an operator that SEC-01 rested "
           "on a literal filter, so a pass for a named program should be attributed to the layer that produced it.")
SENT = "A read-only methodology review by a second AI tool was relayed to the authors as a verdict; its report is not in the repository, and no result or claim in this paper relies on it. "
for f in (B + r"\paper1\manuscript.md", B + r"\venue\icetc2026\ICETC_PORT_MANUSCRIPT.md"):
    print(f)
    para_edit(f, "**Containment.** *Shows:*", P1_CONT)
    text_edit(f, SENT, "")

# ---------------------------------------------------------------- P2
f = B + r"\paper2\manuscript.md"; print(f)
para_edit(f, "**What the agreement result shows and does not show.**",
  "**Agreement with the human reference scores.** On this benchmark the composite's ranking of answers agrees only modestly with the human "
  "reference scores, somewhat more within questions than pooled, and the question-aware interval is wide. The data say nothing about agreement on "
  "natural answers, on other questions, or with raters of documented independence. Modest, context-dependent agreement is a common finding [15]. "
  "The pooled figure also hides a question-level scale offset (per-question composite means 0.066–0.542 against human means 0.385–0.492) that a "
  "single coefficient would not reveal. The benchmark has only 8 questions.")
para_edit(f, "**Why the full composite does not have the highest point estimate.**",
  "**Why the full composite does not have the highest point estimate.** R alone and S1 + R have higher Spearman point estimates than the full "
  "composite here, and the intervals for the differences include zero. That does not make the additional terms useless elsewhere: the composite "
  "includes a damping rule, a penalty and a cap intended to limit keyword-stuffing failures, and correlation with human scores does not measure "
  "that purpose. On the adversarial set the composite did not accept fewer adversarial answers than R alone. The data therefore give no support "
  "for the added complexity on this benchmark, and a design decision should wait for a benchmark in which these terms are exercised.")
para_edit(f, "**Why a word-count baseline is competitive.**",
  "**Why a word-count baseline is competitive.** A trivial signal reaches ρ = 0.4897 and AUROC = 0.8864, and the categories differ in length. "
  "This does not show that the evaluator learned length, or that length predicts quality in natural answers. A length-controlled benchmark is "
  "needed before agreement figures for this evaluator are read as evidence of content sensitivity.")
para_edit(f, "**Under-scoring of correct answers.**",
  "**Under-scoring of correct answers.** The mean composite score is below the mean human reference in every correct or partially correct "
  "category, most for concise and paraphrased answers, while verbose incorrect answers are over-scored on average. The data do not show the "
  "cause, its generality or any fairness property. Sensitivity of automatic scorers to surface form is documented [1], [3], [6], [7]; this is a "
  "measurement of it for one scorer on technical answers, with only 2–8 answers per category.")

# ---------------------------------------------------------------- P3
f = B + r"\paper3\manuscript.md"; print(f)
para_edit(f, "**Equivalence.** *Shows:*",
  "**Equivalence.** With this simulator, the shared guardrail layer and these five checkpoints, mean tracking error differed by −0.0350 between "
  "PPO and Constant-Same, and the interval lies inside ±0.12. That does not mean the two policies are the same, that PPO has no effect (three "
  "sensitivity intervals exclude zero), or that a differently trained PPO would also be equivalent. Learned policies that match simple or expert "
  "policies are reported in other settings [4]–[7], and the equivalence framing follows [12], [13]; here the pre-specified rule requires the whole "
  "95% interval inside the margin. The result limits what can be credited to the learned policy in this design, because the tracking result does "
  "not identify a contribution of the learned component beyond the guardrails. It has no practical implication for learners, since the study "
  "makes no claim about real interviews, and the ±0.12 margin has no external justification, so whether ±0.12 difficulty levels is practically "
  "small has not been evaluated.")
para_edit(f, "**Behaviour beyond the mean.** *Shows:*",
  "**Behaviour beyond the mean.** PPO reads the state (zeroing or shuffling the observation raised tracking error), is more volatile, and has its "
  "proposed action changed by the layer on 7.9% of five-persona turns. None of this shows that state dependence helps tracking, or that "
  "guardrail activation counts measure safety outcomes. The guardrail accounting rests on five authored personas.")
para_edit(f, "**Anticipated objections.**",
  "**Foreseeable objections.** Constant-Same is a strong reference here because difficulty starts at the centre of the target range; it is "
  "state-blind, and other nulls, such as an Elo or item-response baseline, were not run. The margin has no external justification. The reward "
  "includes an oracle-alignment term and the target is an authored rule; that coupling was not re-audited, although PPO was not trained to "
  "minimise the tracking error. Each checkpoint saw 24,576 timesteps against one candidate, and the effect of longer or broader training was "
  "not tested. The simulator is authored and uncalibrated, so it may bias the result, and training differs from evaluation as described in "
  "Section III. PPO does respond to the state in this simulator. Equivalence within an author-selected margin says that PPO adds little to mean "
  "tracking error for these checkpoints in this simulator; the policies still differ in action sequences, executed paths and volatility, and "
  "nothing is inferred about learners.")
