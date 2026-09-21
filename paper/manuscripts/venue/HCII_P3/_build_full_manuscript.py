"""Assemble the HCII-structured Paper 3 full-paper draft from paper3/manuscript.md (v2).
Re-orders and re-numbers sections, splits the study-design section into protocol and method, and adds the
research-question, implications and declarations sections. Existing numbers and sentences are reused verbatim;
no result is recomputed."""
import re
ROOT = r"C:\Users\spars\Downloads\PrepAIred\paper\manuscripts"
src = open(ROOT + r"\paper3\manuscript.md", encoding="utf-8").read()

def between(a, b):
    i = src.index(a) + len(a)
    j = src.index(b, i)
    return src[i:j].strip()

def paras(text):
    return [p.strip() for p in text.split("\n\n") if p.strip()]

abstract = re.search(r"\*\*Abstract—\*\* (.*?)\n", src).group(1)
keywords = re.search(r"\*\*Keywords—\*\* (.*?)\n", src).group(1)

intro = paras(between("## I. Introduction", "## II. Related Work"))
assert intro[-1].startswith("The research question is:")
rq_par = intro.pop()
related = between("## II. Related Work", "## III. Simulator")
sec3 = paras(between("## III. Simulator, Policies and Guardrail Layer", "## IV. Study Design"))
sim_par, pers_par, pol_par, gr_par = sec3
sec4 = paras(between("## IV. Study Design", "## V. Results"))
prim, o7, secpar, replay, reg = sec4
res = between("## V. Results", "## VI. Discussion")
parts = re.split(r"^### ", res, flags=re.M)
R = {p[0]: p for p in parts if p.strip()}          # keyed by letter
def body(letter):
    t = R[letter]
    return t.split("\n", 1)[1].strip()
disc = between("## VI. Discussion", "## VII. Threats")
lim = between("## VII. Threats to Validity and Limitations", "## VIII. Reproducibility")
repro = between("## VIII. Reproducibility and Artifact Availability", "## IX. Conclusion")
concl = between("## IX. Conclusion", "## References")
AUTHORS_MD = ("Dr. Uma D (Professor), Naveen S Khadd, Sparsh Kumar, Athreya Shashidhara, Manasa S A\n\n"
              "Dept. of CSE, PES University\n\n"
              "*(Author order, designation and affiliation as supplied by the corresponding author on 2026-09-21. E-mail addresses, ORCID iDs, city and "
              "country are not recorded here. HCII regular-paper review is single-blind, so names appear.)*")

# Springer LNCS numeric reference style (final check against the Springer template at the camera-ready stage); metadata unchanged from the IEEE-style list.
refs = """[1] Kadam, S., Banerjee, S., Christopher, J., Praveen Kumar, P.T.V., Satpathi, D.K.: A simulation framework for benchmarking reinforcement learning policies in adaptive mock-interview tutoring. Simul. Model. Pract. Theory 151, 103316 (2026). https://doi.org/10.1016/j.simpat.2026.103316 (publisher landing page read: abstract, highlights and contribution statements; article body not read)
[2] Riedmann, A., Schaper, P., Lugrin, B.: Reinforcement learning in education: a systematic literature review. Int. J. Artif. Intell. Educ. 35(5), 2669–2723 (2025). https://doi.org/10.1007/s40593-025-00494-6
[3] Doroudi, S., Aleven, V., Brunskill, E.: Where's the reward? A review of reinforcement learning for instructional sequencing. Int. J. Artif. Intell. Educ. 29(4), 568–620 (2019). https://doi.org/10.1007/s40593-019-00187-x
[4] Sanz Ausin, M., Maniktala, M., Barnes, T., Chi, M.: Exploring the impact of simple explanations and agency on batch deep reinforcement learning induced pedagogical policies. In: Artificial Intelligence in Education (AIED 2020). LNCS, pp. 472–485. Springer (2020). https://doi.org/10.1007/978-3-030-52237-7_38
[5] Schmucker, R., Pachapurkar, N., Bala, S., Shah, M., Mitchell, T.: Learning to optimize feedback for one million students: insights from multi-armed and contextual bandits in large-scale online tutoring. arXiv:2508.00270 (2025), preprint
[6] Jiang, J., Hong, K., Kuczynski, E., Pottie, G.: Simulated human learning in a dynamic, partially-observed, time-series environment. arXiv:2511.15032 (2025), preprint
[7] Che, L., Guo, P., Isleem, H.F., Wang, Z.: The necessity of multimodal feedback for learning effective pedagogical policies with reinforcement learning. Sci. Rep. 16 (2025). https://doi.org/10.1038/s41598-025-29892-5 (article number not verified)
[8] Olukola, O., Rahimi, N.: MC-CPO: mastery-conditioned constrained policy optimization for pedagogically safe intelligent tutoring systems. arXiv:2604.04251 (2026), preprint
[9] Alshiekh, M., Bloem, R., Ehlers, R., Könighofer, B., Niekum, S., Topcu, U.: Safe reinforcement learning via shielding. In: Proc. AAAI Conf. Artif. Intell. 32(1) (2018). https://doi.org/10.1609/aaai.v32i1.11797 (cited for terminology only; the definition was not reopened in this study)
[10] Agarwal, R., Schwarzer, M., Castro, P.S., Courville, A.C., Bellemare, M.G.: Deep reinforcement learning at the edge of the statistical precipice. In: Advances in Neural Information Processing Systems, vol. 34 (2021)
[11] Henderson, P., Islam, R., Bachman, P., Pineau, J., Precup, D., Meger, D.: Deep reinforcement learning that matters. In: Proc. AAAI Conf. Artif. Intell. 32(1) (2018). https://doi.org/10.1609/aaai.v32i1.11694
[12] Schuirmann, D.J.: A comparison of the two one-sided tests procedure and the power approach for assessing the equivalence of average bioavailability. J. Pharmacokinet. Biopharm. 15, 657–680 (1987). https://doi.org/10.1007/BF01068419
[13] Lakens, D., Scheel, A.M., Isager, P.M.: Equivalence testing for psychological research: a tutorial. Adv. Methods Pract. Psychol. Sci. 1(2), 259–269 (2018). https://doi.org/10.1177/2515245918770963
[14] Pelánek, R.: Applications of the Elo rating system in adaptive educational systems. Comput. Educ. 98, 169–179 (2016). https://doi.org/10.1016/j.compedu.2016.03.017"""

# --- split the primary-comparison paragraph into protocol (Section 7) and method (Section 8) ---
prim_protocol = ("**Primary comparison (X3-A).** The contrast is PPO with guardrails minus Constant-Same with guardrails, "
    "over 40 personas, 20 evaluation seeds and 5 training seeds. The unit is the persona: for each persona, session tracking error is "
    "averaged over the 20 evaluation seeds, and the PPO term is averaged over the 5 training seeds. The estimate is the mean of "
    "persona-level differences over the 40 personas. Sessions and turns are descriptive. A follow-up retraining experiment (X3-B) was "
    "to run only if the class were not equivalent; it was not triggered.")
assert "The estimate is the mean of persona-level differences over the 40 personas." in prim
assert "A follow-up retraining experiment (X3-B)" in prim
prim_method = ("**Interval and classification rule.** The interval is a two-way cluster bootstrap that resamples the 40 personas and the "
    "5 training seeds with replacement (B = 10,000, seed 42, 95% percentile). The pre-specified classification rule is: *equivalent* if the "
    "interval lies entirely inside (−0.12, +0.12); *PPO-superior* if its upper bound is below −0.20; *PPO-adverse* if its lower bound is "
    "above +0.12; otherwise inconclusive. The margin of ±0.12 and the superiority threshold of −0.20 were pre-specified and author-selected; "
    "no external empirical justification for either was identified, and none is offered here. Equivalence within the margin means that the "
    "whole interval lies inside it; it is not evidence that the difference is zero.")
assert "B = 10,000, seed 42, 95% percentile" in prim and "none is offered here" in prim

rq_new = ("The research question is: *Under an identical rule-based guardrail layer, what does a learned PPO difficulty controller add beyond a "
    "simpler state-blind Constant-Same policy in simulated technical-interview trajectories?* It is answered by one pre-specified primary "
    "contrast (PPO with guardrails minus Constant-Same with guardrails; tracking error against an authored target) and by secondary, "
    "descriptive accounts of guardrail activity, behavioural divergence and volatility.\n\n"
    "The contribution is controlled decomposition and equivalence evidence: (1) a matched-policy comparison under identical guardrails; "
    "(2) an equivalence result under a repository-registered protocol, with three pre-specified sensitivity analyses (seven estimates); "
    "(3) guardrail accounting that separates rule activations from action overrides and from attempted boundary actions; and (4) an explicit "
    "list of what the simulation cannot support. Equivalence within a margin is not evidence of no difference. The paper does not claim "
    "learned-policy superiority, learner benefit, real-candidate validity or a safety guarantee, and it proposes no new application, "
    "algorithm, simulator or benchmark.")

intro_close = ("Section 3 states the research question and the contribution; Sections 4–8 describe the simulator, the policies, the guardrail, "
    "the protocol and the equivalence method; Section 9 gives the results; Sections 10–12 discuss them, their limits and their implications "
    "for adaptive instructional systems.")

implications = """## 12 Implications for Adaptive Instructional Systems and HCI

The study is a simulation, so its implications concern how adaptive instructional systems are evaluated and reported, not how learners respond. Five points follow, each tied to a result above.

**Report the constraint layer as part of the result.** When a learned difficulty policy runs behind rules, activation, override and boundary counts are findings. In the replay, the layer activated on 45.0% of turns but changed the selected action on 7.9%, and 464 of the 563 activations coincided with the proposed action; describing all activations as interventions would misstate how much the layer acted on the policy. The count of sessions with at least one override (41 of 125) is a further, separate quantity.

**Include a matched, simpler baseline.** A state-blind constant action under the same layer set a reference that the learned policy did not measurably beat on the pre-specified endpoint. An adaptive system evaluated without such a baseline leaves open whether the constraint layer, the simulator or the learned component produced the outcome.

**State the margin and where it comes from.** An equivalence classification is conditional on its margin. Here the margin (±0.12 difficulty levels) is author-selected, and whether such a difference matters to a learner is a question for learning-science and human-centred evaluation, which this study does not address.

**Look beyond the mean.** Equal mean tracking error coexisted with different action sequences (50 of 125 sessions), executed paths that differed in 25, and higher volatility of guarded PPO (+0.14877 on the grid). A learner or candidate experiences the sequence of questions and not the mean, so path shape and volatility are relevant to interaction design. Whether they are perceived by, or matter to, real users was not studied.

**Human-centred evaluation remains open.** No learners, real candidates, usability measures or learning outcomes are reported. Before any claim about a deployed adaptive system, the evaluation would need real candidates, ethical review appropriate to the setting and learner-centred outcome measures; none of these is implied by the present results, and the demonstration policy in the application differs from the evaluated checkpoints (Section 11).
"""

declarations = """## Declarations (drafts; AUTHOR CONFIRMATION REQUIRED for every bracket)

**Authors and affiliations.** As on the title page. E-mail addresses, ORCID iDs, city and country are not recorded here [AUTHOR CONFIRMATION REQUIRED].

**Ethics.** This study used simulated candidates only: no human participants and no personal data were involved in the reported experiments. [Confirm with the authors and, if required, the venue.]

**Use of AI tools.** [PLACEHOLDER: AUTHOR CONFIRMATION REQUIRED. The tool(s), version(s), sections affected and level of author review are not established in the repository record and are not stated here. The Springer Nature and HCII wording must be checked at submission time; see `cross/AI_DISCLOSURE_FACT_CHECK.md`.]

**Data and code availability.** The repository is not publicly released in this draft. [Release decision: AUTHOR CONFIRMATION REQUIRED.]

**Competing interests.** [AUTHOR CONFIRMATION REQUIRED.]
"""

# --- assemble ---
o = []
o.append("<!-- P3 HCII 2027 AIS FULL-PAPER DRAFT (content-complete; NOT converted to the Springer template; NOT author-verified; NOT submitted). "
         "Assembled 2026-09-21 by venue/HCII_P3/_build_full_manuscript.py from paper3/manuscript.md v2; all numbers reused verbatim from the traced ledger. -->\n")
o.append("# A Controlled Equivalence Study of Learned and Constant Difficulty Policies in Simulated Technical Interviews\n")
o.append(AUTHORS_MD + "\n")
o.append("**Abstract.** " + abstract + "\n")
o.append("**Keywords:** " + keywords + "\n")
o.append("---\n")
o.append("## 1 Introduction\n\n" + "\n\n".join(intro) + "\n\n" + intro_close + "\n")
o.append("## 2 Related Work\n\n" + related + "\n")
o.append("## 3 Research Question and Contribution\n\n" + rq_new + "\n")
o.append("## 4 The Simulator\n\n" + sim_par + "\n\n" + pers_par + "\n")
o.append("## 5 Policy Definitions\n\n" + pol_par + "\n")
o.append("## 6 The Application-Level Rule-Based Guardrail\n\n" + gr_par + "\n")
o.append("## 7 Experimental Protocol\n\n" + prim_protocol + "\n\n" + secpar + "\n\n" + replay + "\n\n" + reg + "\n")
o.append("## 8 Equivalence and Sensitivity Method\n\n" + prim_method + "\n\n" + o7 + "\n")
o.append("## 9 Results\n")
o.append("### 9.1 Primary equivalence result\n\n" + body("A") + "\n")
o.append("### 9.2 Sensitivity results\n\n" + body("B") + "\n")
o.append("### 9.3 Guardrail accounting (five-persona replay)\n\n" + body("C") + "\n")
o.append("### 9.4 Behavioural divergence (five-persona replay)\n\n" + body("D") + "\n")
o.append("### 9.5 Volatility\n\n" + body("E") + "\n")
o.append("### 9.6 Secondary contrasts (descriptive)\n\n" + body("F") + "\n")
o.append("### 9.7 Action distribution\n\n" + body("G") + "\n")
o.append("## 10 Discussion\n\n" + disc + "\n")
o.append("## 11 Limitations and Threats to Validity\n\n" + lim + "\n")
o.append(implications)
o.append("## 13 Reproducibility and Artifact Availability\n\n" + repro + "\n")
o.append("## 14 Conclusion\n\n" + concl + "\n")
o.append(declarations)
import re as _re
o.append("## References\n\n" + _re.sub(r"\n+(?=\[\d+\] )", "\n\n", refs.strip()) + "\n")   # one paragraph per reference, so no renderer can merge entries
t = "\n".join(o)

# --- renumber tables and cross-references ---
for a, b in (("Table III", "Table 3"), ("Table II", "Table 2"), ("Table IV", "Table 4"), ("Table I", "Table 1")):
    t = t.replace(a, b)
t = t.replace("Sections V-C and V-D uses", "Sections 9.3 and 9.4 use")
t = t.replace("Sections V-C and V-D", "Sections 9.3 and 9.4")
t = t.replace("(Section III)", "(Sections 4–6)")
t = t.replace("Section III", "Sections 4–6")
t = t.replace("../figures/", "../../figures/")
open(ROOT + r"\venue\HCII_P3\P3_FULL_MANUSCRIPT_READY.md", "w", encoding="utf-8").write(t)

body_txt = re.sub(r"<!--.*?-->", "", t, flags=re.S)
main = body_txt.split("## Declarations")[0]
print("words excl. declarations/references:", len(main.split()))
print("abstract words:", len(abstract.split()))
print("leftover 'Section' refs:", sorted(set(re.findall(r"Sections? [IVX0-9][\w\.\-–, and]*", t))))
