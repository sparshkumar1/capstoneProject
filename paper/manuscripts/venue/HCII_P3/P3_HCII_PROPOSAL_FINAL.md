# P3 — HCII 2027 AIS paper proposal (FINAL LOCAL DRAFT — NOT SUBMITTED)

Prepared 2026-09-21, master pass the same day. The proposal text below is unchanged (762 words). Supersedes `../hcii2027/HCII_AIS_PROPOSAL_800w.md` (611-word first version, retained). Author decisions are marked AUTHOR CONFIRMATION REQUIRED. Nothing here has been submitted.

## Official requirements (re-read 2026-09-21)
Sources: https://2027.hci.international/papers.html · /deadlines.html · /ais
- Proposal limit: 800 words, references excluded. Required content: objective and significance; methods/approach; results/findings; contributions and implications.
- Review: single-blind (reviewers see author names and contact details).
- Dates: proposal **9 Oct 2026**; outcome **20 Nov 2026**; full paper **29 Jan 2027**; author registration **12 Feb 2027**; conference 25–30 Jul 2027, Berlin.
- Full paper: typically 12 pages, minimum 10, maximum 20; editable source (LaTeX or DOCX) plus PDF; Springer templates supplied later. One registration per accepted paper.
- The pages read contain no AI-use or generative-AI disclosure policy (UNVERIFIED for HCII itself; the Springer policy applies to the proceedings and was checked from summaries only — see `../../cross/AI_USE_DISCLOSURE_DRAFT.md`).

## Title
A Controlled Equivalence Study of Learned and Constant Difficulty Policies in Simulated Technical Interviews

## Proposal text (paste from here to the end marker)
<!-- PROPOSAL TEXT BEGINS -->

**Objective and significance.** Adaptive instructional systems (AIS) often adjust task difficulty with a learned policy that runs behind hand-written constraints. When the two are evaluated together, an outcome cannot be attributed to the learned component, and simpler alternatives are seldom reported under the same constraints. Simulation studies of adaptive mock-interview tutoring compare learned policies with heuristics [1], and reviews of reinforcement learning in education report inconsistent baselines and heavy reliance on simulated users [2]. In the literature we reviewed, a matched comparison against a state-blind constant action under an identical constraint layer, with an equivalence analysis and an account of how often the constraints act, is less often reported. We ask one research question: under an identical application-level rule-based guardrail, what does a learned proximal-policy-optimisation (PPO) difficulty controller add beyond a state-blind Constant-Same policy in simulated technical-interview sessions? The study is simulation-only. No learners or real candidates took part, and it makes no claim about learning effectiveness, learner outcomes or superiority of the learned policy. Its relevance to AIS is methodological: what evidence is needed before an adaptive decision can be credited to a learned component.

**Methods and approach.** A simulated candidate has a persona type and a skill, and produces performance, confidence, hesitation and response-time signals for the current difficulty. The controller observes a six-dimensional state and chooses among Easier, Same and Harder; difficulty lies between 1 and 5 and starts at 3.0. The primary stratum is 40 authored personas (five types by eight skill levels), each with an authored target difficulty; a session has ten turns. The endpoint is the persona-level difference in mean absolute error between session difficulty and target difficulty. Five frozen PPO checkpoints (five training seeds, each trained for 24,576 timesteps against one default simulated candidate) were compared with Constant-Same over 20 evaluation seeds, both under the same guardrail: six ordered rules that hold, ease or raise difficulty from score, confidence and hesitation thresholds, with no formal safety specification. The persona is the statistical unit and the training seed is a second random factor; the interval is a two-way cluster bootstrap (10,000 resamples). The equivalence margin of ±0.12 difficulty levels and the superiority threshold of −0.20 were pre-specified in the project repository and author-selected; no external empirical justification was identified. Protocol and harness were committed and tagged before the run; the tags are local and no external registry entry was made. Three further pre-specified analyses (persona-only bootstrap, seed-level t interval, leave-one-seed-out) give seven sensitivity estimates. A separate evaluation-only replay of the frozen checkpoints on five fixed personas (125 PPO sessions, 1250 turns) accounts for the guardrail and for behavioural divergence.

**Results and findings.** The difference in tracking error (PPO minus Constant-Same) was −0.0350 (95% interval −0.0818 to +0.0021; mean errors 1.0688 and 1.1039), classified equivalent within the margin. Superiority was not met, and all seven sensitivity estimates were classified equivalent. Equivalence does not mean identical behaviour or no effect. In the replay, the guardrail activated on 563 of 1250 PPO turns (45.0%); 99 activations changed the selected action (7.9% of all turns) and 464 were no-op activations. At least one override occurred in 41 of 125 sessions. Relative to Constant-Same under the same guardrail, the final-action sequence differed in 50 of 125 sessions, the executed difficulty path in 25 and session tracking error in 5; these counts follow different definitions. On the 40-persona grid, guarded PPO was more volatile than Constant-Same (difference +0.149, interval 0.067 to 0.254). Replacing PPO's observation with zeros or another persona's observation raised tracking error, so the policy reads its state, but that does not show that reading it improves tracking.

**Contributions and implications.** The study contributes a matched-policy comparison in which the constraint layer is held fixed, an equivalence result with its pre-specified rule and margin, and a guardrail accounting that separates rule activations from action overrides and from attempted boundary actions. For evaluating adaptive instructional systems, the implication is to report constraint-layer accounting and a matched simpler baseline before attributing an outcome to a learned policy, and to read equivalence as a statement about its stated margin. Limitations bound every finding. The simulator, personas, target rule and margin are authored by the study team; the training reward contains an alignment term with an authored rule; the checkpoints were trained against one simulated candidate under training settings that differ from evaluation, and the application's deployed policy and state definition differ from the evaluated ones; no Elo, item-response or adaptive-testing baseline was run; and there are no real candidates and no learning outcomes. The full paper will present these limits alongside the results.

<!-- PROPOSAL TEXT ENDS -->

**Exact word count: 762 words** (whitespace-delimited tokens between the markers, headings' bold labels and bracketed citation markers included; limit 800, references excluded). Margin: 38 words. Reproduce with `python -c "print(len(open('proposal_text.txt',encoding='utf-8').read().split()))"` in this directory.

## References for the proposal (excluded from the count; Springer LNCS numeric style)
[1] Kadam, S., Banerjee, S., Christopher, J., Praveen Kumar, P.T.V., Satpathi, D.K.: A simulation framework for benchmarking reinforcement learning policies in adaptive mock-interview tutoring. Simul. Model. Pract. Theory 151, 103316 (2026). https://doi.org/10.1016/j.simpat.2026.103316 (abstract, highlights and contribution statements read; body not read)
[2] Riedmann, A., Schaper, P., Lugrin, B.: Reinforcement learning in education: a systematic literature review. Int. J. Artif. Intell. Educ. 35(5), 2669–2723 (2025). https://doi.org/10.1007/s40593-025-00494-6

## Keywords
adaptive difficulty; equivalence testing; reinforcement learning; simulated candidates; rule-based guardrails; technical interviews

## AIS thematic-area rationale
The AIS call (2027.hci.international/ais) lists evaluation and effectiveness measurement of adaptive instruction, advanced AI in adaptive systems, learner modelling and assessment, and professional-development application contexts. The proposal fits mainly through evaluation methodology for adaptive difficulty decisions (matched baselines, equivalence rules, accounting of the constraint layer) in a professional-skills (technical-interview) setting. It does **not** fit as a learning-effectiveness study, a learner-modelling study or a deployed-system report, and the text says so. The fit is a judgement from the scope page; no organiser has confirmed it.

## Consistency check against frozen evidence (done)
All 29 numeric tokens in the proposal were traced to `paper3/manuscript.md` and its ledger (`paper3/claim_ledger_v2.md`); the single non-verbatim token is +0.149, a rounding of the stored 0.14877. Prohibited wording checked absent: "interventions" for the 563 activations, "formal safety shield", any superiority, learning-effect or real-learner claim. The evaluation-time Same share is not stated. The ±0.12 margin is called author-selected and without external justification; registration is described as repository-registered with local tags.

## Author metadata (as supplied by the corresponding author, 2026-09-21)
1. Dr. Uma D, Professor, Dept. of CSE, PES University
2. Naveen S Khadd, Dept. of CSE, PES University
3. Sparsh Kumar, Dept. of CSE, PES University
4. Athreya Shashidhara, Dept. of CSE, PES University
5. Manasa S A, Dept. of CSE, PES University

Order and spelling are fixed. The legacy PDF states "Professor" only for Dr. Uma D and "Dept. of CSE" for the others; the words "PES University" come from the supplied instruction (the legacy PDF does not print them), so confirm the exact institution wording. No designation is given for authors 2–5. HCII review is single-blind, so names may appear in the proposal form and the full paper.

## Still to be supplied or confirmed by the authors (AUTHOR CONFIRMATION REQUIRED)
- Corresponding author, e-mail addresses, ORCID iDs, city and country (not recorded; none is invented here).
- Submission-system account (Conference Management System linked from the AIS page) and the form's own fields (title, abstract field versus proposal upload, keywords, any track selection).
- Registration/fee: UNVERIFIED (no fee found on the pages read).
- AI-use statement wording for the form, if the form asks (facts in D-4; nothing is stated in the proposal text).
- Whether the repository will be released or described as private in the full paper.
- Confirm the research-question wording and the "repository-registered" language.
