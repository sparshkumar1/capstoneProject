"""Apply the audit-v2 corrections to paper3/manuscript.md. Each (old, new) pair must match exactly once."""
import re, sys
P = r"C:\Users\spars\Downloads\PrepAIred\paper\manuscripts\paper3\manuscript.md"
t = open(P, encoding="utf-8").read()
E = []
def rep(o, n): E.append((o, n))

rep("<!-- PAPER 3 MANUSCRIPT DRAFT v1 (2026-09-21). Markdown source; venue not final. Controlled decomposition / equivalence evaluation, simulation only. -->",
    "<!-- PAPER 3 MANUSCRIPT v2 (2026-09-21, independent-audit pass). Markdown source; venue not final. Controlled decomposition / equivalence evaluation, simulation only. v1 preserved as manuscript_v1_archive.md. -->")

old_abs = re.search(r"\*\*Abstract—\*\* .*?\n", t).group(0)
new_abs = ("**Abstract—** Adaptive difficulty controllers for technical-interview practice are often reported with a learned policy and a rule-based constraint layer bundled together, so the learned component's own contribution is unclear. We report a controlled comparison in simulation in which a learned proximal-policy-optimisation (PPO) difficulty controller and a state-blind Constant-Same policy run under an identical application-level rule-based guardrail. Using five frozen PPO checkpoints, 40 authored candidate personas and 20 evaluation seeds, the primary endpoint, pre-specified in the project repository, was the persona-level difference in mean absolute error (MAE) between session difficulty and an authored target difficulty, analysed with a two-way cluster bootstrap over personas and training seeds against an author-selected equivalence margin of ±0.12. The difference (PPO minus Constant-Same) was −0.0350 (95% interval [−0.0818, +0.0021]), classified equivalent within the margin; superiority (upper bound below −0.20) was not met, and the classification was unchanged in seven sensitivity estimates from three pre-specified analyses. Equivalence does not mean identical behaviour. In a five-persona replay (1250 PPO turns), the guardrail activated on 563 turns (45.0%) and changed the selected action on 99 (7.9%); the final-action sequence differed from Constant-Same in 50 of 125 sessions, the executed difficulty path in 25 and session MAE in 5; guarded PPO was more volatile than both Constant-Same and unguarded PPO. The evidence is simulation-only, with authored personas, targets and margin, and checkpoints trained against a single simulated candidate. It supports no claim of learned-policy benefit or of benefit to real learners.\n")
rep(old_abs, new_abs)

# global terminology: registered -> pre-specified (handled after replacement list; see below)

rep("We evaluated the registered contrast between PPO with the guardrail layer and Constant-Same with the same layer, using persona-level tracking error, and we report guardrail accounting, trajectory divergence and volatility alongside. The registered primary result is an equivalence classification, with a difference of −0.0350 and an interval of [−0.0818, +0.0021] against a margin of ±0.12. Secondary analyses show that the policies are not behaviourally identical.",
    "We evaluated the contrast, pre-specified in the project repository, between PPO with the guardrail layer and Constant-Same with the same layer, using persona-level tracking error, and we report guardrail accounting, trajectory divergence and volatility alongside. The primary result is an equivalence classification, with a difference of −0.0350 and an interval of [−0.0818, +0.0021] against an author-selected margin of ±0.12. Secondary analyses show that the policies are not behaviourally identical.")
rep("(2) a registered equivalence result with three registered sensitivity analyses;",
    "(2) an equivalence result under a repository-registered protocol, with three pre-specified sensitivity analyses (seven estimates);")

rep("The margins were fixed by the study team before the analysis; no literature justification for ±0.12 was found.",
    "The margin of ±0.12 and the superiority threshold of −0.20 were pre-specified and author-selected; no external empirical justification for either was identified, and none is offered here.")
rep("**Registration status.** The protocol and sensitivity analyses carry annotated git tags created before the runs; the repository was not pushed to a public registry, so registration is author-controlled and not externally time-stamped.",
    "**Registration status.** Throughout this paper, \"registered\" and \"pre-specified\" mean that the protocol, harness and sensitivity analyses were committed and marked with annotated git tags in the project repository before the runs. No external registry entry exists, the repository was not pushed to a public registry, and the tags are author-controlled and not externally time-stamped.")

# Section V-B wording on the number of analyses
rep("**Table II. Registered sensitivity analyses (difference = PPO+G minus Constant-Same+G).**",
    "**Table II. The seven sensitivity estimates from three pre-specified analyses (difference = PPO+G minus Constant-Same+G); the first row repeats the primary result.**")
rep("| Analysis | Difference | 95% interval | Class |",
    "| Analysis (comparison) | Difference | 95% interval (method) | Equivalence class |")
rep("| Persona-only bootstrap (checkpoints fixed) | −0.0350 | [−0.0673, −0.0052] | Equivalent |",
    "| O7-A persona-only bootstrap (checkpoints fixed; B = 10,000) | −0.0350 | [−0.0673, −0.0052] | Equivalent |")
rep("| Seed-level t interval (df = 4) | −0.0350 | [−0.0758, +0.0057] | Equivalent |",
    "| O7-B seed-level t interval (df = 4; five seed-level differences) | −0.0350 | [−0.0758, +0.0057] | Equivalent |")
rep("| Leave out seed 42 | −0.0234 | [−0.0614, +0.0092] | Equivalent |",
    "| O7-C leave out seed 42 (two-way bootstrap, four seeds) | −0.0234 | [−0.0614, +0.0092] | Equivalent |")
rep("All eight intervals lie inside ±0.12 and none has an upper bound below −0.20, so superiority was never established.",
    "All eight intervals (the primary and the seven estimates) lie inside ±0.12 and none has an upper bound below −0.20, so superiority was never established. Fig. 1 plots them against the margin.\n\n![Fig. 1](../figures/fig_p3_equivalence.png)\n\n**Fig. 1.** Primary interval (diamond) and the seven sensitivity estimates for the difference in tracking MAE, PPO with guardrail minus Constant-Same with guardrail. Shaded band: equivalence margin (−0.12, +0.12); dotted line: superiority threshold (−0.20). Sources: `x3a_decision.json`, `x3a_o7_results.json`.")

# Section V-C guardrail accounting
rep("### C. Guardrail accounting (five-persona replay)\n\n**Table III.",
    "### C. Guardrail accounting (five-persona replay)\n\nThe application-level rule-based guardrail activated on 563 of 1250 turns (45.0%). Of those activations, 99 changed the selected action (7.9% of all turns), while 464 were no-op activations. At least one actual override occurred in 41 of 125 sessions. Fig. 2 shows the accounting.\n\n![Fig. 2](../figures/fig_p3_guardrail.png)\n\n**Fig. 2.** Accounting of the 1250 PPO+guardrail turns of the five-persona replay. Top: turns with no rule match, rule matches that left the proposed action unchanged, and overrides. Bottom: the 99 overrides by proposed and final action. Source: `x3_0c_replay_turn_log.csv`.\n\n**Table III.")
rep("By direction (D): 30 turns replaced a proposed Easier by Same (a blocked decrease), 30 replaced Same by Easier, and 39 replaced a proposed Harder (34 by Easier and 5 by Same), so the layer both raised and lowered the difficulty proposed by PPO and did not act only towards easier questions.",
    "By direction (D): 30 overrides replaced a proposed Easier by Same (blocked decreases); 39 replaced a proposed Harder (blocked increases: 34 by Easier and 5 by Same); and 30 replaced Same by Easier. The layer thus both prevented and forced decreases in the proposed difficulty and did not act only towards easier questions.")
rep("The 563 activations are not interventions: 82.4% of them coincided with the proposed action.",
    "The 563 activations are not interventions: 82.4% of them (the 464 no-op activations) coincided with the proposed action.")

# Section V-D divergence
rep("Of the 125 PPO+guardrail sessions, the final-action sequence differed from that of Constant-Same+guardrails in 50, the executed difficulty path (after clipping) differed in 25, and the session tracking error differed in 5.",
    "Of the 125 PPO+guardrail sessions, the final-action sequence differed from that of Constant-Same+guardrails in 50 (40%), the executed difficulty path (after clipping) differed in 25 (20%), and the session tracking error differed in 5 (4%).")

# Section V-E volatility figure
rep("The guarded policy is therefore not smoother than the unguarded one in these data. Volatility is a secondary metric and was analysed descriptively.",
    "The guarded policy is therefore not smoother than the unguarded one in these data, and no claim of reduced volatility is made. Volatility is a secondary metric and was analysed descriptively. Fig. 3 shows the divergence counts and the stored volatility values.\n\n![Fig. 3](../figures/fig_p3_divergence_volatility.png)\n\n**Fig. 3.** (A) Number of the 125 PPO+guardrail sessions (five-persona replay) whose final-action sequence, executed difficulty path or session MAE differed from Constant-Same+guardrail; the three counts follow different definitions. (B) Volatility (mean absolute difficulty change per turn) of PPO with and without guardrails: small marks are the five training seeds, diamonds the pooled values; the dashed line is Constant-Same+guardrail. Sources: `x3_0c_followup.json`, `x3_0c_replay_summary.csv`.")

# Discussion / Conclusion consistency
rep("is overridden by the layer on 7.9% of five-persona turns.", "has its proposed action changed by the layer on 7.9% of five-persona turns.")
rep("and the guardrail layer acted on 45.0% of turns while changing the proposed action on 7.9%.",
    "and the guardrail activated on 45.0% of turns while changing the selected action on 7.9%.")
rep("The demonstration policy deployed in the application differs from the training state definition, and no claim is made about the application.",
    "The demonstration policy deployed in the application is a different checkpoint from the evaluated seed-123 checkpoint and differs from the training state definition (a runtime state-definition mismatch); no claim is made about the application.")
rep("**Scope.** Simulation only: no human learners, no real-candidate evidence, and no evidence of learning outcomes. The simulator, persona structure, target difficulty rule and comparator controllers are authored. The reward contains oracle-alignment terms and the coupling to the evaluation target was not re-audited.",
    "**Scope.** Simulation only: no human learners, no real-candidate evidence, and no evidence of learning outcomes. The simulator, persona structure, target difficulty rule and comparator controllers are authored by the study team, and the reward contains an oracle-alignment term (weight 0.60) whose coupling to the authored evaluation target was not re-audited; PPO was not trained to minimise the tracking error, but the alignment may favour the target structure. The five training seeds are a hypothetical population, training and evaluation differ (Section III), and no Elo, item-response or computerized-adaptive-testing baseline was run.")

# references: verified metadata
rep("[4] M. Sanz Ausin, M. Maniktala, T. Barnes, and M. Chi, \"Exploring the impact of simple explanations and agency on batch deep reinforcement learning induced pedagogical policies,\" in *Artificial Intelligence in Education (AIED 2020)*, 2020.",
    "[4] M. Sanz Ausin, M. Maniktala, T. Barnes, and M. Chi, \"Exploring the impact of simple explanations and agency on batch deep reinforcement learning induced pedagogical policies,\" in *Artificial Intelligence in Education (AIED 2020)*, Lecture Notes in Computer Science, Springer, 2020, pp. 472–485, doi: 10.1007/978-3-030-52237-7_38.")
rep("*Sci. Rep.*, 2025 (article ID s41598-025-29892-5; volume/article number not verified).",
    "*Sci. Rep.*, vol. 16, 2025, doi: 10.1038/s41598-025-29892-5 (article number not verified).")
rep("in *Proc. AAAI Conf. Artif. Intell.*, 2018 (cited for terminology only; the definition was not reopened in this study).",
    "in *Proc. AAAI Conf. Artif. Intell.*, vol. 32, no. 1, 2018, doi: 10.1609/aaai.v32i1.11797 (cited for terminology only; the definition was not reopened in this study).")
rep("in *Proc. AAAI Conf. Artif. Intell.*, 2018.\n[12]", "in *Proc. AAAI Conf. Artif. Intell.*, vol. 32, no. 1, 2018, doi: 10.1609/aaai.v32i1.11694.\n[12]")
rep("*Int. J. Artif. Intell. Educ.*, vol. 35, pp. 2669–2723, 2025,", "*Int. J. Artif. Intell. Educ.*, vol. 35, no. 5, pp. 2669–2723, 2025,")

bad = 0
for o, n in E:
    c = t.count(o)
    if c != 1:
        print("MISMATCH (%d):" % c, o[:90].replace("\n", " ")); bad += 1
    else:
        t = t.replace(o, n)
if bad:
    sys.exit("aborting; nothing written")

# global terminology: 'registered' -> 'pre-specified' except in the definition sentence and 'repository-registered'
keep = "\"registered\" and \"pre-specified\""
t = t.replace(keep, "@@KEEP@@")
t = t.replace("repository-registered", "@@RR@@")
t = re.sub(r"\bregistered\b", "pre-specified", t)
t = re.sub(r"\bRegistered\b", "Pre-specified", t)
t = t.replace("@@KEEP@@", keep).replace("@@RR@@", "repository-registered")
open(P, "w", encoding="utf-8").write(t)
ab = re.search(r"\*\*Abstract—\*\* (.*?)\n", t).group(1)
print("applied", len(E), "edits; abstract words", len(ab.split()))
body = re.sub(r"<!--.*?-->", "", t, flags=re.S).split("## References")[0]
print("body words", len(body.split()))
for m in re.finditer(r"pre-specified", body):
    pass
print("pre-specified count", body.count("pre-specified"), "registered count", len(re.findall(r"\bregist", body)))
