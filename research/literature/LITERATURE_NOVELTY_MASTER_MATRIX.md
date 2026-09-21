# PREPAIred — Literature and Novelty Master Matrix (first pass)

Date of search: 2026-09-20. Author: Claude (engineering/research executor). Status: **planning/research artifact only**. No experiment was run, no SUT/frozen artifact was touched, no Zotero entry was created, no manuscript text is drafted here. Nothing in this file is a claim about PREPAIred's results beyond what `research/claims/CLAIM_REGISTRY.csv` already records.

## 0. How to read this file (evidence labels, limits, wording rules)

**Evidence label on every record** (this matters more than the matrix itself):

| Label | Meaning |
|---|---|
| **FT** | I downloaded/opened the paper text this session and read the relevant parts (full text, or the sections named). Fields below are from the paper. |
| **AB** | I read the abstract/landing page (arXiv, official proceedings, PMC, ACL Anthology). Fields not on that page are marked *not verified*. |
| **SN** | Only search-result summaries plus Crossref metadata (year, venue, DOI). **I did not read the paper.** Fields beyond bibliographic data and the one-line finding are marked *not verified* and must not be cited from this file without a second-pass read. |

**Peer-review status** is stated where I could establish it. arXiv items are labelled *preprint*. Several 2026 items are recent preprints; they are context, not settled literature.

**Limits of this pass (important):**
1. Tools: a US-only web search engine, page fetch, and Crossref metadata. No Scopus, Web of Science, IEEE Xplore, ACM DL or Google Scholar queries. ScienceDirect, Springer, MDPI and ACM full-text pages returned 403/login redirects for several items; those are **SN** or metadata-only.
2. One pass: about 45 web searches, about 20 page/PDF fetches, and Crossref metadata lookups. **A search that found nothing is not evidence that nothing exists.** Every "no prior work found" statement below means "not found by the queries listed in §16".
3. Numbers quoted from sources are quoted as the source reports them; I did not recompute any.
4. Search snippets and Crossref abstracts were treated as leads, not as verified content.

**Wording rules applied.** The words "first", "novel", "unique" and "state-of-the-art" are not used to describe PREPAIred. They appear only inside a cited title or where a source's own claim is being reported and marked as such. Field 13 below is labelled *Contribution (what it adds)* instead of "novel".

**Record format** (fields 1–16 from the request, compressed): 1–4 citation/year/venue/URL-DOI · 5 problem · 6 method · 7 data/simulator · 8 human evaluation · 9 baselines · 10 evaluation protocol · 11 main result · 12 stated limitation · 13 contribution · 14 overlap with PREPAIred · 15 legitimate differentiation · 16 claim we must NOT make.

**Facts about PREPAIred used for comparison** (all from the claim registry / CLAUDE.md, not from this search):
- Paper 1 evidence so far: X1-D test report and latency (226 tests, 1 failure; warm evaluator latency median 236 ms; SQLite write median 12.7 ms), a nine-program attack run of which four outcomes discriminate (P1-C003), a concurrency benchmark with synthetic database operations (P1-C002). The Docker sandbox configuration is **DESIGN-ONLY** (P1-C009: effectiveness not measured). X1-A/B/C (sandbox containment with oracle, LLM-channel invariance) are **planned, not run**.
- Paper 2 evidence: composite evaluator `0.15*S1 + 0.35*S2_eff + 0.50*R`, R = partially fine-tuned derivative of `cross-encoder/ms-marco-MiniLM-L-6-v2` (16.28 % of parameters changed, P2-C003); 64 author-constructed answers to 8 questions, 3 raters; composite Spearman ρ = 0.3812 (case-bootstrap CI [0.1575, 0.5774]; two-level cluster CI [0.1529, 0.6490]); R-only 0.4832, S1+R 0.4884; composite minus R-only −0.102, CI includes zero; metamorphic 19/21, adversarial 11/13 against **author-set** ceilings.
- Paper 3 evidence: PPO plus hand-written guardrails (G1–G6) in a simulated interview environment; persona is the statistical unit; PPO+G minus Constant-Same+G tracking-MAE difference −0.0350, CI [−0.0818, +0.0021], classified Equivalent within ±0.12; PPO more volatile than a state-blind constant action under the same guardrails; frozen checkpoints trained against one default simulated candidate; no real-user data.

---

## 1. Executive literature map

| Area | What the literature clearly covers (verified this pass) | Where PREPAIred is closest | Main risk to a contribution statement |
|---|---|---|---|
| Sandboxing untrusted code for assessment | Docker-based assignment graders since 2014 (APAC); kernel-level containment mechanisms (2002); container security frameworks (2018); microVMs (2020); runtime comparisons (gVisor/Kata/runC, 2019–2022); a test suite for sandbox environments running untrusted LLM-generated code (SandboxEval, 2025 preprint) | APAC (Docker sandbox for assignment evaluation); SandboxEval (tests whether an assessment sandbox resists hostile code) | A stock-Docker configuration is not a new containment mechanism. A contribution can only be the **evaluation protocol** (predefined weakened-configuration controls, multi-layer oracle), and it does not exist as evidence until X1-C is run. |
| Prompt injection / authority separation | Attack and defence benchmarks (Liu 2024, AgentDojo 2024); architectural separation (CaMeL 2025 preprint); privilege training (Instruction Hierarchy 2024 preprint); attacks on LLM **graders** (2024–2026, mostly preprints; one Scientific Reports 2026 paper) | Attacks on LLM-based graders and code evaluators; CaMeL/instruction-hierarchy as design analogues | In PREPAIred the LLM is **not** the scorer. The literature on grader hijacking therefore does not describe the same threat, but a reviewer will cite it. Do not claim injection resistance beyond enumerated channels. |
| Trustworthy/dependable AI in education | Reviews of ethics/governance in AI education (PRISMA reviews 2024–2025); systematic reviews of automated grading/feedback tools (Messer 2024; Paiva 2022) | Reviews frame requirements (robustness, privacy, oversight) | I found **no** paper (in this pass) that studies dependability (fault tolerance, graceful degradation) of an LLM-assisted assessment system. That is a search-negative, not a gap proof. |
| ASAG and human alignment | Mohler 2009/2011 (similarity → regression), SemEval-2013, BERT/transformer ASAG (2019–2020), graph transformers (2022), ensembles (2023), reviews, LLM-era ASAG (2025) | Same task family; Mohler is the canonical CS-answer benchmark | PREPAIred's benchmark is **64 author-constructed answers to 8 questions**; it cannot be presented as comparable to Mohler's 2,273 real student answers or to SemEval. |
| Bias/robustness of evaluators | Verbosity/length/position bias for LLM judges (2023–2025); adversarial triggers against ASAG (2020, 2024); RL-based auditing of an ASAG model (2024); behavioural/metamorphic testing (CheckList 2020) | Adversarial and metamorphic testing of an evaluator | Almost all bias literature is about **LLM judges**; PREPAIred's evaluator is a SBERT + FAISS + CrossEncoder composite. Do not import LLM-judge findings as evidence about it. |
| RL in education / adaptive difficulty | Systematic reviews (Mon 2023; Memarian 2024; Riedmann 2025); RL tutors with real learners (Ruan 2024); simulated-student PPO work (Axak 2025); safe/constrained RL for tutoring (Olukola 2026 preprints); adaptive/CAT question selection incl. RL (BOBCAT, MAB-CAT 2026) | Axak (PPO vs rule-based vs DQN in simulation); Ion 2025 (simulated coding interviews); Olukola 2026 (guardrail-like constraints) | "PPO for adaptive difficulty" and "simulated candidates" are both studied. What remains for PREPAIred is **how it is evaluated** (persona as unit, null baseline under the same guardrails), not the idea. |
| Shielded / safe RL | Shielding (Alshiekh 2018), under partial observability (Carr 2023), reviews (2023, CACM 2025) | Guardrails filtering actions | PREPAIred's guardrails are **hand-written rules with no formal safety specification or guarantee**. They must not be called a "shield" in the formal sense. |
| Interview-practice systems | LLM mock-interview systems with speech/multimodal analysis (Conversate; PolyInterview 2026 preprint; others) | Same application area | System-level "interview practice with feedback" is populated; no contribution can rest on the application alone. |

**Bottom line of the map.** Every component PREPAIred combines has prior work. Defensible differences lie in (a) the **evaluation designs** (controls that prove the test can fail; persona-level clustering; null baseline under identical guardrails; cluster-aware CIs), (b) **honest negative/inconclusive results** reported with provenance, and (c) the **specific combination** in one traceable system. These are "differs from / focuses on / studies an under-evaluated property" statements, and each is conditional on evidence listed in §3, §7, §11.

---

## 2. Paper 1 literature matrix — dependable/trustworthy AI technical-assessment systems

### 2.1 Sandboxing and containment

**P1-01 · Spacek, Sohlich, Dulik (2015) — "Docker as Platform for Assignments Evaluation"** · Procedia Engineering 100:1665–1671 (25th DAAAM Symposium, 2014) · doi:10.1016/j.proeng.2015.01.541 · [FT: entire paper]
- 5 Problem: safe automatic evaluation of student programs; earlier graders (Mooshak, CS50) are described as not focused on a safe runtime environment.
- 6 Method: APAC (Java EE) around Docker containers; SSH-based sandbox pool; default 100 MB RAM and 50 % CPU limits set via Docker REST API; plugin per language (C, C++, Java); test vectors (stdin/file/args).
- 7 Data: none reported for this version. The text says an earlier version ran in an "Algorithms and data structures" course at Tomas Bata University (2013/14). (A search-engine summary mentioned a database course at another university; **that is not in the paper text I read and is not used**.)
- 8 Human evaluation: none reported. 9 Baselines: none (other systems are reviewed narratively). 10 Protocol: architecture description; no attack testing described.
- 11 Result: working system; open source (GPLv3). 12 Limitation (stated): the sandbox is limited by Linux itself; robustness depends on each submission-processor plugin; the runtime must run inside an isolated Linux container. **No security evaluation is reported in the text I read.**
- 13 Contribution: shows Docker as an assessment sandbox with API integration and resource limits.
- 14 Overlap: Docker sandbox for untrusted student code with resource limits.
- 15 Differentiate: PREPAIred adds non-root user, `--net=none`, `--cap-drop=ALL`, read-only root, `no-new-privileges`, PID/memory limits — but these are configuration, and **effectiveness is unmeasured** until X1-C. Any differentiation is the (future) measurement, not the configuration.
- 16 Do NOT claim: that Docker-based grading of untrusted code is new; that configuration alone demonstrates safety.

**P1-02 · Peterson, Bishop, Pandey (2002) — "A Flexible Containment Mechanism for Executing Untrusted Code"** · 11th USENIX Security Symposium · https://www.usenix.org/conference/11th-usenix-security-symposium/flexible-containment-mechanism-executing-untrusted-code · [SN]
- 5–6 (per summaries): analysis of sandbox design options and a kernel-level facility with primitives for confining untrusted programs. 7–12 not verified. 13 Contribution: a general sandbox framework analysis. 14 Overlap: conceptual (containment of untrusted programs). 15 Differentiate: none at mechanism level; PREPAIred uses off-the-shelf container primitives. 16 Do NOT claim: a new containment mechanism.

**P1-03 · Sun, Safford, Zohar, Pendarakis, Gu, Jaeger (2018) — "Security Namespace: Making Linux Security Frameworks Available to Containers"** · USENIX Security 2018, pp. 1423–1439 · https://www.usenix.org/conference/usenixsecurity18/presentation/sun · [FT: abstract, introduction, evaluation excerpts]
- 5: containers share one kernel and cannot use kernel security frameworks (integrity measurement, MAC) independently. 6: a "security namespace" kernel abstraction; instantiated for IMA and AppArmor for Docker. 7: prototype measurements on Linux. 8/9: n/a. 10: security-effectiveness demonstrations plus system-call and workload overhead measurements. 11: less than 0.7 % system-call latency overhead in a typical container; at most 3.5 % with many namespaces (as stated in the text). 12: generality of the abstraction left for future work (stated).
- 13: per-container security policy control. 14: shared-kernel container isolation is the trust base PREPAIred inherits. 15: PREPAIred does not use security namespaces or a MAC layer; it can only state which Docker flags it sets. 16: Do NOT claim MAC/LSM-level container protection.

**P1-04 · Agache et al. (2020) — "Firecracker: Lightweight Virtualization for Serverless Applications"** · NSDI 2020 · https://www.usenix.org/conference/nsdi20/presentation/agache · [FT: introduction, design/security sections, evaluation excerpts]
- 5: multi-tenant serverless needs strong isolation with container-like density/start-up. 6: a minimal VMM on KVM with a jailer (chroot/namespaces/cgroups/seccomp). 7: AWS Lambda/Fargate production context. 9: QEMU, Cloud Hypervisor (boot time, memory overhead). 11/12: stated design omissions (no BIOS, no arbitrary kernel boot, no legacy device emulation, no VM migration).
- 13: microVM isolation with small attack surface. 14: alternative isolation tier for untrusted code; motivates "shared-kernel containers are a weaker boundary". 15: none at mechanism level. 16: Do NOT imply PREPAIred has VM-grade isolation; do not present Docker as equivalent to a microVM.

**P1-05 · Young, Zhu, Caraza-Harter, Arpaci-Dusseau, Arpaci-Dusseau (2019) — "The True Cost of Containing: A gVisor Case Study"** · HotCloud 2019 · https://www.usenix.org/conference/hotcloud19/presentation/young · [SN]
- Reported: syscall ≥ 2.2× slower than traditional containers; open/close on an external tmpfs 216× slower. Other fields not verified. 14: cost of stronger sandboxing versus runC. 15: PREPAIred can justify stock Docker on measured latency grounds only if it measures it. 16: Do NOT claim gVisor-level isolation or dismiss it without stating the trade-off.

**P1-06 · Wang et al. (2022) — "Performance and isolation analysis of RunC, gVisor and Kata Containers runtimes"** · Cluster Computing 25:1497–1513 · doi:10.1007/s10586-021-03517-8 · [SN]
- Reported: runC and Kata have lower overhead; gVisor degrades I/O and syscalls but showed the best isolation in their tests. Method/data not verified. 14/15/16 as P1-05.

**P1-07 · Rabin, Hostetler, McGregor, Weir, Judd (2025) — "SandboxEval: Towards Securing Test Environment for Untrusted Code"** · arXiv:2504.00018 (**preprint; authors label it a preliminary working paper**) · https://arxiv.org/abs/2504.00018 · [AB]
- 5: LLM-generated (possibly malicious) code run inside assessment infrastructure. 6: manually crafted test cases covering sensitive-information exposure, filesystem manipulation, external communication and other dangerous operations. 7: applied to Dyff (an open-source AI-evaluation framework). 8/9: not verified. 11: the suite describes operational constraints and informs hardening (per abstract). 12: preliminary.
- 13: a test suite for judging whether a code-execution environment is hardened. 14: **closest prior work to the X1-C idea** (attack programs vs an assessment sandbox). 15: possible differences (to verify against the full paper): PREPAIred's predefined weakened-configuration controls (one documented flag changed at a time) and four-layer oracle (static pre-flight, execution, runtime containment via self-report + `docker events`, host side-effects). **I have not read SandboxEval's protocol, so I cannot say it lacks negative controls.** 16: Do NOT claim a sandbox-testing framework as a contribution without differentiating from SandboxEval.

### 2.2 Automated programming assessment and reviews

**P1-08 · Paiva, Leal, Figueira (2022) — "Automated Assessment in Computer Science Education: A State-of-the-Art Review"** · ACM TOCE 22(3), Art. 34 · doi:10.1145/3513140 · [SN] — review of automated assessment tools; other fields not verified. 14: framing of automated programming assessment. 16: Do NOT claim a gap in "secure execution" without reading how this review treats it.

**P1-09 · Messer, Brown, Kölling (2024) — "Automated Grading and Feedback Tools for Programming Education: A Systematic Review"** · ACM TOCE 24(1) · doi:10.1145/3636515 · [SN] — 121 papers (2017–2021) categorised by skills assessed, approach, paradigm, automation degree, evaluation technique; typical tools run unit tests; feedback often limited to pass/fail and expected-vs-actual output. 14: shows the field's evaluation norms. 15: PREPAIred's system is a technical-**interview** practice system (spoken/text answers + code), not a course autograder. 16: Do NOT claim novelty of "feedback beyond pass/fail" without checking this review's coverage.

### 2.3 Prompt injection, authority separation, containment of LLMs

**P1-10 · Greshake, Abdelnabi, Mishra, Endres, Holz, Fritz (2023) — "Not what you've signed up for…"** · AISec '23 (ACM) · doi:10.1145/3605764.3623985 · [SN] — indirect prompt injection into LLM-integrated applications; taxonomy of impacts (data theft, worming, etc.). 14: an LLM-integrated application that ingests untrusted text. 15: PREPAIred's untrusted channels (candidate answers, code output, speech transcripts) must be enumerated (planned in X1-B). 16: Do NOT say the system is "immune".

**P1-11 · Liu, Jia, Geng, Jia, Gong (2024) — "Formalizing and Benchmarking Prompt Injection Attacks and Defenses"** · USENIX Security 2024, pp. 1831–1847 · https://www.usenix.org/conference/usenixsecurity24/presentation/liu-yupei · [SN] — formal framework; 5 attacks × 10 defences × 10 LLMs × 7 tasks; public platform. 14: methodology for attack/defence evaluation. 15: none required. 16: Do NOT invent a new attack taxonomy for X1-B without stating how it differs.

**P1-12 · Debenedetti et al. (2024) — AgentDojo** · NeurIPS 2024 Datasets & Benchmarks · https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html · [SN] — 97 tasks, 629 security cases for agents with tools over untrusted data. (Author list not verified beyond the title/venue.) 14: agent-tool/authority setting. 15: PREPAIred has no tool-using agent. 16: Do NOT claim agent-security results.

**P1-13 · Wallace et al. (2024) — "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions"** · arXiv:2404.13208 (**preprint**) · [SN] — privilege levels (system > user > tool outputs); applied to GPT-3.5. 14: authority-separation concept. 15: PREPAIred's separation is architectural (LLM has no write path to score/difficulty), not model training. 16: Do NOT describe PREPAIred as implementing an instruction hierarchy.

**P1-14 · Debenedetti et al. (2025) — "Defeating Prompt Injections by Design" (CaMeL)** · arXiv:2503.18813 v2, 24 Jun 2025 (**preprint**) · [SN] — privileged/quarantined LLM plus interpreter tracking data flow and capabilities; 77 % of AgentDojo tasks solved with provable security (as reported). (Author list not verified.) 14: **closest architectural analogue** to "LLM output cannot change scoring/difficulty". 15: PREPAIred's claim would be an invariance **test** of a simple architecture, not a provable-security mechanism. 16: Do NOT claim provable security or formal data-flow guarantees.

**P1-15 · Raina, Liusie, Gales (2024) — "Is LLM-as-a-Judge Robust? … Universal Adversarial Attacks on Zero-shot LLM Assessment"** · EMNLP 2024 · https://aclanthology.org/2024.emnlp-main.427/ · [SN] — short universal phrases inflate LLM judge scores; transferable; absolute scoring more susceptible than comparative. (Also cited in §6 for Paper 2.) 16: Do NOT claim scoring is immune to universal triggers unless the composite evaluator is tested (Paper 2 territory).

### 2.4 Attacks on LLM-based grading (closest to "AI assessment security")

**P1-16 · Cai (2026) — "Prompt injection attacks on educational large language models for higher and vocational education"** · Scientific Reports 16, Art. 15594, 31 Mar 2026 · PMC13187012 · [AB]
- 5: grade manipulation/rubric bypass through adversarial student submissions to LLM graders/tutors. 6: attack framework (prompt decomposition, role-consistent vectors, rubric-aligned injection). 7: Llama-3.1-8B-Instruct, Qwen2.5-7B-Instruct, Mistral-7B-Instruct-v0.3 on ASAP, SciEntsBank, EduBench, MMLU-Edu. 8: none stated. 11: attack success rates 0.73–0.82; grade inflation ratio 1.22–1.37; effective under common defences and limited query budgets. 12 (stated): public/partial-rubric visibility, published datasets not deployed systems, local pipelines.
- 13: rubric-aligned, pedagogically plausible injection against educational LLMs. 14: Qwen-family local model in the feedback path; SciEntsBank overlap with Paper 2 data family. 15: in PREPAIred the LLM writes feedback and follow-ups but does not score; the test is whether LLM input/output can move score/difficulty/ranking. 16: Do NOT claim "prompt injection in AI assessment" as a new threat; do NOT claim the local Qwen path is safe.

**P1-17 · Li, Filippov, Lin, He, Yang, Chu, Liu, Tang, Cui (2026) — "'**Important** You should give me full credits!': Exploring Prompt Injection Attacks on LLM-Based Automatic Grading Systems"** · arXiv (cs.CR/cs.AI), v1 2 Jun 2026, v3 4 Sep 2026 (**preprint**) · https://arxiv.org/abs/2606.03090 · [AB] — attacks and defences under rubric-based grading; concludes current LLM-based grading systems remain highly vulnerable. Datasets/defences not on the abstract page (not verified). 14/15/16 as P1-16.

**P1-18 · Sahoo, Prasad, Majhi, Neekhra, Sinha, Mandal, Chamola, Kumar (2026) — "The Compliance Paradox: Semantic-Instruction Decoupling in Automated Academic Code Evaluation"** · arXiv:2601.21360, 29 Jan 2026 (**preprint**) · [AB] — adversarial directives embedded in syntactically neutral code regions (SPACI, AST-ASIP); 9 models, 25,000 submissions, Python/C/C++/Java; failure rates above 95 % for high-capacity open-weight models (as reported). **The predecessor arXiv:2512.10415 ("How to Trick Your AI TA") was withdrawn by its authors on 3 Feb 2026 in favour of this one; do not cite the withdrawn version.** 14: **closest work to LLM code evaluation security.** 15: PREPAIred executes code in a sandbox and scores with a test harness/evaluator; if the LLM does not grade code, this attack class targets a different component. To be confirmed by the X1-B channel enumeration. 16: Do NOT claim resistance to code-comment injection without a test.

**P1-19 · Li, Liu (2025) — "Towards Secure AI in Education: A Case Study on Automatic Short Answer Grading"** · Communications in Computer and Information Science, doi:10.1007/978-3-031-99261-2_39 · [SN, metadata only] — appears relevant to both Paper 1 and 2; content not verified.

### 2.5 Dependability and system context

**P1-20 · Avizienis, Laprie, Randell, Landwehr (2004) — "Basic Concepts and Taxonomy of Dependable and Secure Computing"** · IEEE TDSC 1(1) · doi:10.1109/TDSC.2004.2 · [SN, metadata only; content is well known but not re-read] — the standard vocabulary (fault/error/failure, availability, reliability, safety, integrity). 14: vocabulary for "dependability" in Paper 1. 15: use it to define what "dependable" means in claims. 16: Do NOT use "dependable" or "trustworthy" without stating which attribute is tested.

**P1-21 · Interview-practice systems (context; each [AB] unless stated)**
- Daryanto et al. (2024/2025), "Conversate: Supporting Reflective Learning in Interview Practice…", arXiv:2410.05570 [AB]. LLM-simulated interviews with dialogic feedback; abstract reports no empirical result; venue not stated on the fetched page (DOI pattern suggests CHI proceedings — **unverified**).
- Wen et al. (2026), "PolyInterview: An LLM-based Platform for Immersive Mock Interview Practice with Comprehensive Multimodal Assessment", arXiv:2607.10310, 11 Jul 2026 (**preprint**) [AB]. 101 accounts, 1,564 sessions, 7,665 generated questions; question–job alignment reported for 93.7 % of sessions; ten expert evaluators; baselines not specified on the page. Closest **system-level** overlap.
- "Evaluating Speech-to-Text × LLM × Text-to-Speech Combinations for AI Interview Systems", arXiv:2507.16835 [SN, preprint].
- 14: same application area (LLM interview practice with speech). 15: none at system level; PREPAIred's system contains no video/MediaPipe and no user study. 16: Do NOT claim the system concept, multimodal analysis, or adaptive follow-ups as contributions.

**Search-negative (this pass): dependability of LLM-assisted assessment.** A query on fault tolerance/graceful degradation/fallback for AI-based educational assessment returned general dependable-systems and neural-fault-tolerance material, and non-scholarly pages, but no paper about an assessment pipeline that degrades from an LLM path to a non-LLM path. Treat as "not found", pending §16 queries.

**Excluded as scholarly evidence** (blog/vendor/aggregator material seen in results): container-isolation comparison blog posts (Northflank, Edera, PandaStack, etc.), a Medium post on online-judge sandboxing, a personal blog on Gradescope autograder hardening, a Wharton "Generative AI Labs" technical report page on hidden prompt injection in grading (may have a citable formal counterpart — second-pass check). These are pointers only.

---

## 3. Paper 1 closest-prior-work analysis

For each candidate contribution: **the exact prior work that comes closest**, and what remains.

| # | Candidate contribution (as it might be phrased) | Closest prior work | What that work does | What remains different / open | Condition |
|---|---|---|---|---|---|
| C1-a | An assessment-sandbox containment evaluation with **predefined weakened-configuration controls** and a **four-layer oracle** (static, execution, runtime self-report + `docker events`, host side effects) | SandboxEval (Rabin 2025, preprint); APAC (2015, no attack evaluation in text read) | SandboxEval: manually crafted tests of exposure, filesystem, communication for LLM-code environments; APAC: describes Docker sandbox | Whether either uses negative controls (a deliberately weakened sandbox that the oracle must flag) — **not verified**; PREPAIred-specific flag set | **X1-C must be run**; SandboxEval full text must be read first |
| C1-b | **Authority separation** verified as exact invariance of score/difficulty/ranking under LLM-facing input/output variation (X1-B-I), plus structural constraints when the answer may vary (X1-B-S) | CaMeL (2025 preprint) for architectural separation; Instruction Hierarchy (2024 preprint); Liu 2024; AgentDojo 2024 | Defence mechanisms and attack benchmarks for LLMs that ingest untrusted data | An **invariance test of a deliberately simple architecture** in which the LLM is not the scorer, on a channel list derived from the code | **X1-B must be run**; channel enumeration must be complete |
| C1-c | **Graceful-degradation** behaviour of an LLM-assisted assessment pipeline (fallback to `non_llm_structured_recovery`), measured latency and failure handling | None found on this exact subject (§2.5); dependable-computing vocabulary (Avizienis 2004) | — | Whether degradation is **measured** rather than described; only X1-D latency/test numbers exist so far | Needs an explicit fault-injection design; do not claim from X1-D alone |
| C1-d | A **trace-linked** evaluation record (frozen protocol tags, hashes, manifests) for a system paper | No peer-reviewed close match found in this pass (search not run for reproducibility-tooling literature — see §15) | — | This is a process property; reviewers may see it as engineering hygiene | Only stated as a method feature |
| C1-e | The system itself: multimodal technical-interview practice with local LLM, sandbox, adaptive difficulty | Conversate (2024), PolyInterview (2026 preprint), other mock-interview systems (SN) | Interview-practice platforms with LLM questions and speech feedback | Nothing defensible on system existence | Do not present as a contribution |

---

## 4. Paper 1 candidate contribution statements (hypothesis phrasing; each with its dependency)

These are **candidate** statements to be tested against the evidence, using the permitted vocabulary. None is a claim today.

1. *"We evaluate whether a container-based sandbox for untrusted candidate code contains a predefined set of attack programs, using weakened-configuration controls to show that the oracle can detect failure."* — extends the sandbox-testing approach of SandboxEval and the Docker grading design of APAC. **Depends on X1-C; currently no evidence.**
2. *"We test whether the LLM-facing channels of an interview-practice system can alter scoring, difficulty selection or ranking, in a system where the LLM does not compute the score."* — differs from the grader-attack literature (Cai 2026; Li 2026; Sahoo 2026) in which the LLM is the scorer; related architecturally to CaMeL. **Depends on X1-B and the channel enumeration.**
3. *"We report latency, test-suite and concurrency measurements of a local, LLM-assisted assessment pipeline and document a known failing test with its root-cause triage."* — combines previously studied components; supported today by X1-D-C001…C003 and P1-C001/C002 (with their stated limits: n=20 evaluator run; synthetic DB operations).
4. *"We document which security-related behaviours of the shipped sandbox configuration were and were not discriminated by the attack programs run so far."* — supported by P1-C003 (4 of 9 outcomes discriminate). Honest scoping, not a positive security result.

## 5. Paper 1 — claims we must avoid

| Claim | Why prior work or our evidence blocks it |
|---|---|
| "Secure" / "safe" / "sandboxed against untrusted code" as a result | P1-C009 is DESIGN-ONLY; effectiveness not measured; five of nine attack outcomes do not identify which control acted |
| Docker-based safe execution for assessment as new | APAC (2015) and the many Docker autograders (search results, non-scholarly) |
| A new sandboxing/containment mechanism | Peterson 2002; Sun 2018; Firecracker 2020; gVisor/Kata studies |
| "Prompt-injection-proof", "immune", "guaranteed" | CaMeL-type guarantees are formal; PREPAIred tests are enumerated-channel tests. Speech-audit "guarantee" wording is already withdrawn (P1-C010) |
| Defence against grader-hijacking attacks | Those attacks target LLMs that grade; if the LLM does not grade, the claim is about a different threat; if any LLM output reaches scoring, the literature (Cai 2026; Li 2026; Sahoo 2026) applies directly |
| Prompt injection in AI assessment as an unstudied threat | It is a documented (mostly preprint, one Scientific Reports) threat |
| Fault tolerance / graceful degradation demonstrated | Only latency and test counts exist; degrade behaviour is described, not injected/measured |
| "Trustworthy AI in education" compliance | Reviews define multi-dimensional requirements (privacy, fairness, oversight…); PREPAIred's ethics/rater provenance records are incomplete (CLAUDE.md) |
| Interview-practice system, multimodal analysis, or adaptive follow-up as a contribution | Conversate, PolyInterview and others |
| Multimodal (video) capability | The system has no video/MediaPipe (CLAUDE.md); title/wording "Multimodal" is a flagged stale item |


---

## 6. Paper 2 literature matrix — technical/short-answer evaluation, human alignment, bias, robustness

### 6.1 Foundational ASAG

**P2-01 · Mohler, Mihalcea (2009) — "Text-to-Text Semantic Similarity for Automatic Short Answer Grading"** · EACL 2009, pp. 567–575 · https://aclanthology.org/E09-1065/ · [FT: data-set and evaluation sections]
- 5: grade short student answers against a reference answer using unsupervised text similarity. 6: knowledge-based and corpus-based similarity measures; a step that uses student answers to improve the grader. 7: introductory computer-science data set built for this paper: 3 assignments × 7 questions × 30 student answers = 630 answers. 8: two human judges, integer 0–5 scale (an annotator-agreement correlation of 0.6443 appears in the results table; a second column value is not interpreted here). 9: unsupervised methods proposed earlier (per abstract) and simple baselines. 10: Pearson correlation of system vs human grades. 11: outperforms prior unsupervised methods (abstract). 12: not extracted in this pass. The text explicitly discusses whether Pearson or Spearman is a proper metric for this task.
- 13: a public CS short-answer benchmark plus a similarity-based grading study. 14: same task family (grade technical answers by semantic similarity to a reference). 15: PREPAIred's human study is **rho against a 3-rater consensus** on 64 author-constructed answers; the value is in cluster-aware uncertainty and negative findings, not in scale. 16: Do NOT compare PREPAIred's ρ to Mohler-family numbers as if same benchmark or scale.

**P2-02 · Mohler, Bunescu, Mihalcea (2011) — "Learning to Grade Short Answer Questions using Semantic Similarity Measures and Dependency Graph Alignments"** · ACL 2011, pp. 752–762 · https://aclanthology.org/P11-1076/ · [FT: data-set, evaluation, discussion excerpts]
- 5: supervised grading combining lexical similarity and dependency-graph alignment. 6: alignment features + similarity measures with SVM regression/ranking and isotonic regression. 7: 80 questions across ten assignments and two exams, 31 enrolled students, 2,273 answers, 0–5 scale. 8: two annotators; the text reports identical grades 57.7 % of the time and one point apart 22.9 %. 10: Pearson and RMSE (also median RMSE per question). 11: combined features grade more accurately than semantic measures alone (abstract). 12: the authors state that some questions produced undefined correlations and that this "casts some doubt" on Pearson/Spearman for the task.
- 13: a supervised ASAG method and a public data set (the Mohler data). 14: the correlation-with-human-grades protocol that PREPAIred also uses; the caution on correlation validity is relevant. 15: PREPAIred can legitimately report agreement metrics beyond ρ (rater ICC 0.95 and Krippendorff α 0.95, Lin's CCC, Bland–Altman) and within-question ρ. 16: Do NOT present ρ alone as "human alignment".

**P2-03 · Dzikovska et al. (2013) — "SemEval-2013 Task 7: The Joint Student Response Analysis and 8th Recognizing Textual Entailment Challenge"** · *SEM/SemEval 2013, pp. 263–274 · https://aclanthology.org/S13-2045/ · [SN] — 5-way/3-way/2-way student-response labelling; 9 teams; relates ASAG to textual entailment. Other fields not verified. 14: entailment framing of answer evaluation (PREPAIred's R component is a cross-encoder relevance scorer). 16: Do NOT describe R as validated on SemEval/SciEntsBank.

### 6.2 Neural, transformer and ensemble ASAG

**P2-04 · Sung, Dhamecha, Mukhi (2019) — "Improving Short Answer Grading Using Transformer-Based Pre-training"** · AIED 2019 (Springer) · doi:10.1007/978-3-030-23204-7_39 · [SN] — fine-tuned BERT; reports up to 10 % absolute macro-F1 gain on SemEval-2013 over prior results (as summarised). 14: transformer ASAG. 15: R is a cross-encoder derived from ms-marco (passage ranking), partially fine-tuned with incomplete provenance — a **provenance disclosure**, not a modelling advance. 16: Do NOT claim R is "off-the-shelf" or trained for ASAG per se.

**P2-05 · Camus, Filighera (2020) — "Investigating Transformers for Automatic Short Answer Grading"** · AIED 2020, LNCS 12164, pp. 43–48 · doi:10.1007/978-3-030-52240-7_8 · [SN] — compares several pre-trained transformers; RoBERTa-large best across datasets (as summarised). 14/15/16 as P2-04.

**P2-06 · Agarwal, Khurana, Grover, Mohania, Goyal (2022) — "Multi-Relational Graph Transformer for Automatic Short Answer Grading"** · NAACL 2022, pp. 2001–2012 · https://aclanthology.org/2022.naacl-main.146/ · [SN] — AMR-graph-based transformer (MitiGaTe); outperforms prior systems on the Mohler data set (as summarised). 14: current published ASAG on Mohler's data. 15: PREPAIred does not compete on this benchmark. 16: Do NOT claim comparable accuracy or benchmark standing.

**P2-07 · Ormerod, Lottridge, Harris, Patel (2023) — "Automated Short Answer Scoring Using an Ensemble of Neural Networks and Latent Semantic Analysis Classifiers"** · IJAIED (2023) · doi:10.1007/s40593-022-00294-2 · [SN] — ensemble of deep networks and an LSA model; 81 items from a national interim assessment (grades 3–8, 11; per search summary). 14: ensemble of heterogeneous scorers, like the weighted composite. 15: PREPAIred's composite weights are fixed constants (0.15/0.35/0.50) with a safety rule (S2 ×0.6 when R ≤ 0.30), not learned; the composite **correlates below R-only**. 16: Do NOT claim the composite improves accuracy; frame as safety-hardened.

**P2-08 · Reimers, Gurevych (2019) — "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks"** · EMNLP-IJCNLP 2019 · doi:10.18653/v1/d19-1410 · [metadata only] — the basis of the S1 component. 16: Do NOT attribute any evaluation result to SBERT beyond what PREPAIred measured.

**P2-09 · Haller, Aldea, Seifert, Strisciuglio (2022) — "Survey on Automated Short Answer Grading with Deep Learning: from Word Embeddings to Transformers"** · arXiv:2204.03503, 11 Mar 2022 (**preprint; marked under review at submission; later publication status not checked**) · [AB] — survey; concludes learned representations work best complementing hand-engineered features. 14: supports hybrid-feature composites as an existing pattern. 16: Do NOT claim hybrid scoring is new.

**P2-10 · Putnikovic, Jovanovic (2023) — "Embeddings for Automatic Short Answer Grading: A Scoping Review"** · IEEE Trans. Learning Technologies · doi:10.1109/TLT.2023.3253071 · [metadata only]. Second-pass read needed.

**P2-11 · Ferreira Mello et al. (2025) — "Automatic Short Answer Grading in the LLM Era: Does GPT-4 with Prompt Engineering beat Traditional Models?"** · LAK 2025 · doi:10.1145/3706468.3706481 · [SN, title/venue only; results not verified]. 14: LLM-era comparison against traditional models. 16: Do NOT claim superiority of a small cross-encoder composite over LLM graders.

### 6.3 Adversarial and robustness work on graders

**P2-12 · Filighera, Steuer, Rensing (2020) — "Fooling Automatic Short Answer Grading Systems"** · AIED 2020, LNCS · doi:10.1007/978-3-030-52237-7_15 · [SN] — universal adversarial triggers; the summary states triggers allowed passing a 50 % threshold without correct answers. 14: adversarial testing of ASAG. 15: PREPAIred's guard (S2 ×0.6 when R ≤ 0.30) and adversarial suite exist, but the suite is **13 attacks with author-set score ceilings**, not trigger optimisation. 16: Do NOT claim robustness; claim only that the tested attacks were contained against author-chosen ceilings (P2-C013).

**P2-13 · Filighera, Ochs, Steuer, Tregel (2024) — "Cheating Automatic Short Answer Grading with the Adversarial Usage of Adjectives and Adverbs"** · IJAIED 34 · doi:10.1007/s40593-023-00361-2 · [metadata only]. Second-pass read.

**P2-14 · Condor, Pardos (2024) — "Auditing an Automatic Grading Model with deep Reinforcement Learning"** · arXiv:2405.07087 (an EDM 2024 poster listing appeared in search; venue not verified from the paper) · [AB] — an RL agent revises answers to obtain high marks with minimal edits; shows high agreement with humans does not guarantee reliability. 14: **closest** to "agreement is not the whole validity story". 15: PREPAIred's two-track reporting (agreement + metamorphic/adversarial) makes the same conceptual point for a different scorer. 16: Do NOT claim the idea of adversarially auditing an ASAG model.

**P2-15 · Ribeiro, Wu, Guestrin, Singh (2020) — "Beyond Accuracy: Behavioral Testing of NLP Models with CheckList"** · ACL 2020 (Best Paper per search summary) · https://aclanthology.org/2020.acl-main.442/ · [SN] — behaviour-testing matrix (capabilities × test types: invariance, directional expectation, minimum functionality). 14: source of the metamorphic/invariance framing. 15: PREPAIred's 21 metamorphic cases (3 base × 7 relations) are a small instance. 16: Do NOT present 19/21 as evidence of general robustness.

**P2-16 · Raina, Liusie, Gales (2024)** — see P1-15 (universal adversarial phrases inflate LLM-judge scores). [SN]

**P2-17 · Automated-essay-scoring robustness (context, [SN])** — "A Robustness Analysis of Automated Essay Scoring Methods" (STIL 2024, ACL Anthology; authors not verified) and "Evaluation Toolkit For Robustness Testing Of Automatic Essay Scoring Systems" (arXiv:2007.06796, preprint; authors not verified): perturbations such as unrelated text, shuffling, repetition. Second-pass read required before any comparison.

**P2-18 · Li, Liu (2025), "Towards Secure AI in Education: A Case Study on Automatic Short Answer Grading"** — see P1-19. [SN]

### 6.4 Length/verbosity bias and LLM-as-judge bias

**P2-19 · Zheng et al. (2023) — "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"** · NeurIPS 2023 Datasets & Benchmarks · https://proceedings.neurips.cc/paper_files/paper/2023/file/91f18a1287b398d378ef22505bf41832-Paper-Datasets_and_Benchmarks.pdf · [SN] — position, verbosity and self-enhancement bias; a "repetitive list" verbosity attack; strong judges reach over 80 % agreement with human preferences (as summarised). 14: verbosity-bias concept. 15: PREPAIred's S1/S2/R are not generative judges; the relevant comparison is answer-length dependence of a **non-LLM** composite (X2A-C007 records a residual-vs-length Spearman; read the exact value from the registry). 16: Do NOT import LLM-judge findings as evidence about the composite; do NOT claim "length-bias free".

**P2-20 · Dubois, Galambosi, Liang, Hashimoto (2024) — "Length-Controlled AlpacaEval: A Simple Way to Debias Automatic Evaluators"** · arXiv:2404.04475 (**venue not verified in this pass**; I recall COLM 2024, **unverified**) · [SN] — regression-based length control for auto-annotators. 14/15/16 as P2-19.

**P2-21 · Ye et al. (2025) — "Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge"** · ICLR 2025 · https://proceedings.iclr.cc/paper_files/paper/2025/hash/fdca08d371e4b6c031397909e20043bd-Abstract-Conference.html · [SN] — 12 bias types; CALM automated bias-quantification framework. 14/15/16 as P2-19.

**P2-22 · Andersen, Mang, Goldhammer, Zehner (2025) — "Algorithmic Fairness in Automatic Short Answer Scoring"** · IJAIED · doi:10.1007/s40593-025-00495-5 · [SN] — a summary mentions higher scoring bias for non-native speakers with asymmetric overestimation; other fields not verified. 14: subgroup fairness of ASAG. 15: PREPAIred has no subgroup data. 16: Do NOT claim fairness of the evaluator.

### 6.5 Human alignment with teachers (programming/CS)

**P2-23 · Hickman, Bell (2024) — "Automated Assessment: Does It Align With Teachers' Views?"** · 19th WiPSCE (Workshop in Primary and Secondary Computing Education), doi:10.1145/3677619.3678113 · [metadata only; page returned 403] — the title targets the exact question; content unknown; its scope is primary/secondary CS education, which limits transfer to technical-interview answers. **Second-pass read is required.** 16: Do NOT cite for any finding.

**P2-24 · LLM-versus-instructor agreement for programming (context, [SN])** — e.g. "JorGPT: Instructor-Aided Grading of Programming Assignments with Large Language Models" (Future Internet 2025, 17(6):265), plus search-summary statements that results range from strong correlation to none across deployments and that LLMs often score more conservatively than instructors. These are mixed and mostly single-course studies. 14: human-alignment evidence for code grading. 15: Paper 2 concerns technical **answers** (not code), with a fixed benchmark. 16: Do NOT generalise beyond the 64-answer benchmark.

---

## 7. Paper 2 closest-prior-work analysis

| # | Candidate contribution | Closest prior work | What that work does | What remains different | Condition |
|---|---|---|---|---|---|
| C2-a | A **composite of SBERT + FAISS retrieval + CrossEncoder** with a safety rule, reported with agreement and robustness metrics | Ormerod 2023 (NN+LSA ensemble); Haller 2022 survey (hybrid features); Sung 2019 / Camus 2020 (transformers) | Hybrid/ensemble scorers optimised for accuracy | PREPAIred's composite is **safety-hardened and scores lower** than R-only (ρ 0.3812 vs 0.4832; Δ −0.102, CI includes 0); the paper is about a trade-off, not accuracy | Registry claims X2A-C003, P2-C007 |
| C2-b | **Cluster-aware uncertainty and agreement diagnostics** on a small benchmark (question-cluster bootstrap, leave-one-question-out, rater leave-one-out, within-question ρ, CCC, Bland–Altman) | Mohler 2011 (discusses Pearson/Spearman limits); Condor & Pardos 2024 (agreement ≠ reliability) | Correlation + RMSE reporting; audit via RL | Systematic question-clustered intervals on a **64-answer, 8-question** benchmark; results are exploratory | X2A-C001…C007; X2-C (confirmatory) not run |
| C2-c | **Metamorphic + adversarial checks** with score ceilings | Filighera 2020/2024; Condor & Pardos 2024; CheckList 2020; Raina 2024 | Optimisation-based or template attacks, mostly on transformers/LLMs | The suite is 21 metamorphic cases and 13 attacks, **ceilings set by the authors**; not optimisation-based | P2-C013 |
| C2-d | **Length-dependence** of a non-LLM composite | Dubois 2024; Zheng 2023; Ye 2025 (LLM judges) | Bias for generative judges | Applying residual-vs-length analysis to a retrieval + cross-encoder composite | X2A-C007 (read exact value) |
| C2-e | **Provenance disclosure**: R is a partially fine-tuned derivative (16.28 % of parameters changed vs ms-marco MiniLM), provenance incomplete | None found (a reporting practice, not a finding) | — | Reproducibility caveat | P2-C003 |
| C2-f | Human benchmark built by the study team | Mohler 2009/2011 (real student answers, two annotators; 630 and 2,273 answers) | Real learner responses | PREPAIred's data are **constructed** by the study team; rater provenance/ethics incomplete | Cannot be presented as real-learner evidence |

## 8. Paper 2 candidate contribution statements (hypothesis phrasing)

1. *"We evaluate how a safety-hardened composite of sentence-embedding similarity, retrieval and cross-encoder scores aligns with a three-rater consensus on a small constructed technical-answer benchmark, and report that adding the safety components lowers agreement relative to the cross-encoder alone."* — extends the ASAG similarity/transformer line; supported by P2-C006/C007 and X2A-C003 (interval includes zero: the data neither establish nor exclude a difference).
2. *"We report question-clustered uncertainty for that agreement and show how conclusions change between case-level and cluster-level intervals."* — differs from single-interval reporting; supported by X2A-C001/C002 ([0.1529, 0.6490] two-level; [0.3066, 0.5888] question-only; [0.1575, 0.5774] case-level).
3. *"We test a small set of metamorphic relations and adversarial inputs against author-set ceilings."* — focuses on an under-evaluated property (behaviour under perturbation) for a non-LLM composite; P2-C013 (19/21, 11/13). Descriptive scale.
4. *"We disclose the provenance of the cross-encoder component."* — a transparency statement.
5. A **confirmatory** contribution (agreement on a new benchmark; D-X2-TAU) **does not exist yet**; X2-C is not run and depends on the unresolved human/authoring pathway and institutional determination.

## 9. Paper 2 — claims we must avoid

| Claim | Why |
|---|---|
| "Validated", "accurate", "reliable" evaluator | ρ 0.3812 with wide intervals; 8 questions; exploratory only |
| "Aligned with human experts / teachers / committee" | Raters' provenance/ethics incomplete; benchmark authored by the team; never write "independent experts" |
| "Improves over R-only / S1+R" | It is lower (ρ 0.3812 vs 0.4832/0.4884); difference vs R-only CI includes 0 |
| Any comparison to Mohler/SemEval/SciEntsBank scores | Different data, scale, annotators |
| "Robust to adversarial attacks" / "bias-free" / "length-bias free" | Suite is small and author-defined; only the tested cases were contained |
| Superiority to LLM graders | Not tested; LAK 2025 compares GPT-4 vs traditional models, results not verified |
| Off-the-shelf CrossEncoder | Partially fine-tuned derivative; provenance incomplete |
| ρ 0.6975 as current | Superseded pilot (1 rater, N=20) |
| Fairness across subgroups | No subgroup data; ASAG fairness literature reports subgroup effects |
| Real-learner claims | Constructed answers only |

---

## 10. Paper 3 literature matrix — adaptive difficulty, RL in education, safe/shielded RL, simulation-only evaluation

### 10.1 Closest work: adaptive assessment/difficulty with simulated candidates or learners

**P3-01 · Ion, Asthana, Jiao, Wang, Collins-Thompson (2025) — "Adaptive Knowledge Assessment in Simulated Coding Interviews"** · Proceedings of Machine Learning Research 273:260–262 (iRAISE Workshop at AAAI 2025; a **three-page extended abstract**, not a full conference paper) · https://proceedings.mlr.press/v273/ion25a.html · [FT: whole document]
- 5: interview-style assessment of programming knowledge is hard to scale and hard to optimise without interaction data; build simulated students to compare question-selection policies before deployment. 6: knowledge components (KLI framework) mapped by GPT-4o into a prerequisite graph; **adaptive policy** picks the knowledge component that maximises information about the student's knowledge state; **fixed policy** samples components at random weighted by Beta-modelled uncertainty; GPT-4o writes the natural-language questions. 7: three simulated student profiles (beginner, intermediate, expert) over Python concepts; interview length n = 10 questions. 8: none in the reported results; in-person interviews with data-science master's students are described as under way. 9: fixed policy only. 10: F1 of the inferred expertise level, reported as F1 distributions by policy and level. 11: for expert-level students adaptive IQR F1 0.4–0.8 vs fixed 0.25–0.35; intermediate 0.3–0.6 vs 0.2–0.3; beginners overlapping (0.15–0.3), "less evidence" for adaptive questioning there. 12 (stated): preliminary; validation with real students pending.
- 13: an information-gain question-selection policy over a knowledge-component graph, evaluated on LLM-simulated students. 14: **the anchor named in the request**: simulated coding interviews and adaptive question selection. 15: PREPAIred's controller is a **learned PPO policy over difficulty (easier/same/harder)** with guardrails, judged by tracking a target difficulty (MAE) and volatility, not by expertise-classification F1; statistical unit is the persona with two-way clustering; the paper includes a null baseline. 16: Do NOT claim adaptive question selection in simulated coding interviews as new; do NOT claim to estimate student expertise; do NOT cite this as a full peer-reviewed conference paper (it is a workshop extended abstract).

**P3-02 · Axak, Kushnaryov, Tatarnykov (2025) — "Adaptive Learning Control via Proximal Policy Optimization"** · CEUR-WS Vol-4048, paper 37 (Information Control Systems & Technologies, ICST-2025, Odesa, 24–26 Sep 2025) · https://ceur-ws.org/Vol-4048/paper37.pdf · [FT: abstract, methods, evaluation, conclusion excerpts]
- 5: an intelligent tutor as RL agent and the student as environment; personalise tasks/hints. 6: custom Gym student simulator (decision time, help-request frequency, accuracy, etc.); Stable-Baselines3 PPO and DQN; rule-based tutor and random actions as comparators. 7: simulator; then **offline replay on 0.9 million ASSISTments-2017 logs** with NDCG, inverse-propensity-scored reward and doubly-robust estimates. 8: none. 9: rule-based tutor, DQN, random. 10: 50,000 timesteps per agent; the text states "a fixed random seed was used across all runs" (I did not find a multi-seed analysis or a statistical test in the sections I read); Table 1 shows values with "±" whose meaning I did not verify. 11: PPO "up to 12×" higher cumulative reward than DQN; relative to the rule-based tutor, lower help-request rate and higher task accuracy (simulation); +17 % NDCG and +4.4 % IPS reward on replay (as reported). 12: the conclusion defers deployment in authentic settings to future work.
- 13: PPO-based tutoring policy compared to rule-based and DQN in simulation with an off-policy replay check. 14: **closest published overlap for "PPO vs rule-based baseline in a simulated adaptive-instruction environment".** 15: PREPAIred differs in evaluation design — multiple training seeds as a random factor, persona as the clustered unit, equivalence margin, a **state-blind constant-action null under identical guardrails** — and reports that PPO's contribution under guardrails is not identified. 16: Do NOT claim "PPO outperforms rule-based/heuristic baselines" as a finding of interest by itself; Do NOT claim the idea of PPO for adaptive tutoring.

**P3-03 · Ruan, Nie, Steenbergen, He et al. (2024) — "Reinforcement learning tutor better supported lower performers in a math task"** · Machine Learning (2024) · doi:10.1007/s10994-023-06423-9 · [SN + Crossref abstract] — deep RL provides adaptive pedagogical support in a narrative storyline software (concept: volume); explainable-AI analysis of the policy; a search summary states it improved post-test performance/reduced completion time for low-prior-proficiency learners. Details (design, N, baselines) not verified. 14: RL tutor **with real learners**. 15: PREPAIred is simulation-only; the contrast must be stated. 16: Do NOT imply learner benefit; Do NOT cite as if evidence from this study supports PREPAIred's policy.

**P3-04 · Pérez, Dapena, Aguilar (2024) — "Emotions as implicit feedback for adapting difficulty in tutoring systems based on reinforcement learning"** · Education and Information Technologies · doi:10.1007/s10639-024-12699-8 · [SN] — RL with emotion signals and flow theory to select difficulty. Other fields not verified. 14: RL for difficulty selection in tutoring. 16: Do NOT claim RL-based difficulty adaptation as new.

**P3-05 · Alam, Fazeli, Tian, Chi (2025) — "Determining Problem Type Using Deep Reinforcement Learning in a Data-Driven Intelligent Tutor"** · Lecture Notes in Computer Science, doi:10.1007/978-3-031-98465-5_18 · [metadata only; Springer page not readable]. Second-pass read.

**P3-06 · Vesin, Mangaroska, Akhuseyinoglu, Giannakos (2022) — "Adaptive Assessment and Content Recommendation in Online Programming Courses: On the Use of Elo-rating"** · ACM TOCE 22(3), Art. 33 · doi:10.1145/3511886 · [SN] — modified Elo rating for adaptive practice/assessment and content recommendation in programming courses; a summary reports it matched students with content of appropriate difficulty. 14: heuristic/statistical difficulty matching in programming — a **non-RL baseline family**. 15: a reviewer may ask why Elo-style matching is not a baseline. 16: Do NOT claim RL is needed for difficulty matching without such a comparison.

**P3-07 · Tang, Li, Zhao (2026) — "Reinforcement learning framework for computerized adaptive testing using multi-armed bandit approach"** · Scientific Reports (2026) · PMC12929805 · [AB] — CNN ability estimator + MAB item selection + learning automata; EXAMS data set (24,000+ questions); virtual test-taker cohort; baselines NCAT, BOBCAT, MAAT; RMSE 1.53, MAE 1.21; stated limits: data dependency, compute, single-dataset generalisability. 14: RL/bandit item selection with virtual test-takers. 15: different objective (ability estimation vs difficulty tracking with guardrails). 16: Do NOT claim RL for adaptive item selection as new.

**P3-08 · BOBCAT (IJCAI 2021) and computerized adaptive testing surveys** — "BOBCAT: Bilevel Optimization-Based Computerized Adaptive Testing" (IJCAI 2021; authors not verified) and "Survey of Computerized Adaptive Testing: A Machine Learning Perspective" (arXiv:2404.00712, preprint) · [SN] — data-driven CAT baselines; NCAT learns a selection policy with RL (as summarised). 14: adaptive question selection family. 16: as P3-07.

**P3-09 · "CodeGENCAT: Generative Computerized Adaptive Testing for Open-ended Coding Problems"** · arXiv:2602.20020, 2026 (**preprint**) · [SN] — CAT for coding problems; content not verified. 14: adaptive assessment for coding. **Second-pass read is a priority** (closest by topic to "adaptive assessment of coding").

### 10.2 Reviews of RL and adaptive systems in education

**P3-10 · Riedmann, Schaper, Lugrin (2025) — "Reinforcement Learning in Education: A Systematic Literature Review"** · IJAIED · doi:10.1007/s40593-025-00494-6 · [SN; full text unreadable] — excludes study proposals/conceptual work and student modelling without instructional-decision optimisation; states that further research is needed. Number of studies and findings on simulation-vs-real evaluation **not verified**. 14: anchor review named in the request. 15: use it to check how many included studies evaluate only in simulation and whether any use guardrails. 16: Do NOT state review findings from this file.

**P3-11 · Mon, Wasfi, Hayajneh, Slim, Abu Ali (2023) — "Reinforcement Learning in Education: A Literature Review"** · Informatics 10(3):74 · doi:10.3390/informatics10030074 · [Crossref abstract] — investigates RL applications and techniques in education; compares policies induced by RL with baselines; identifies MDP, POMDP, deep RL and Markov chain techniques (per search summary); notes difficulty can be adjusted from performance. 14/15/16 as P3-10.

**P3-12 · Memarian, Doleck (2024) — "A scoping review of reinforcement learning in education"** · Computers and Education Open · doi:10.1016/j.caeo.2024.100175 · [metadata only; page 403]. (Earlier in my working notes I had assumed a different journal; the Crossref record says *Computers and Education Open*.)

**P3-13 · Adaptive-learning reviews (context, [SN])** — e.g. "Artificial intelligence in adaptive education: a systematic review of techniques for personalized learning" (Discover Education 2025, doi:10.1007/s44217-025-00908-6); a school-level adaptive-learning review reports that adaptivity mostly targets micro-level navigation, task difficulty and support, based on performance, in elementary mathematics. 14: context for adaptive difficulty. 16: Do NOT claim evidence of learning benefit.

**P3-14 · Zheng (2024) — "Dynamic difficulty adjustment using deep reinforcement learning: A review"** · Applied and Computational Engineering 71 · doi:10.54254/2755-2721/71/20241633 · [Crossref abstract] — DDA in games with DRL versus traditional methods. 14: the **games** literature on difficulty adjustment. 15: a source for heuristic/controller baselines from games. 16: Do NOT claim DDA-by-RL as new.

### 10.3 Safe and shielded RL

**P3-15 · Alshiekh, Bloem, Ehlers, Könighofer, Niekum, Topcu (2018) — "Safe Reinforcement Learning via Shielding"** · AAAI 2018, pp. 2669–2678 · https://dblp.org/rec/conf/aaai/AlshiekhBEKNT18.html (bibliographic record) · [SN] — a shield restricts the agent's actions during learning and at test time to ensure safety with respect to a specification. Method/experiments not verified. 14: **action filtering with a safety specification**. 15: PREPAIred's guardrails G1–G6 are **hand-written rules** (overload protection etc.) without a formal safety specification, safety automaton or proof; ablation shows removing G1 lowers MAE by 0.087 [−0.239, 0.038] for PPO+G. 16: Do NOT call it a "shield" with guarantees; call it rule-based guardrails.

**P3-16 · Carr, Jansen, Junges, Topcu (2023) — "Safe Reinforcement Learning via Shielding under Partial Observability"** · AAAI 2023, 37(12):14748–14756 · doi:10.1609/aaai.v37i12.26723 · [Crossref abstract] — integrates shields with deep RL under partial observability; a shield can improve convergence and final performance, and can be disabled after bootstrapping. 14: shield **inside the training loop** (PREPAIred trained PPO with guardrails on, P3-C019). 15: PREPAIred's finding that the shield did not improve the tracking of a constant Same action on the 40-persona grid (X3A-C003) differs in scope from formal-shield benefits. 16: Do NOT claim shield-induced performance benefits.

**P3-17 · Könighofer, Bloem, Jansen, Junges (2025) — "Shields for Safe Reinforcement Learning"** · Communications of the ACM · doi:10.1145/3715958 · [Crossref abstract] — reviews shielding as runtime enforcement with provable safety, the models and guarantee types, shield computation and integration techniques. 14: the review PREPAIred must cite for terminology. 16: as P3-15.

**P3-18 · Odriozola-Olalde, Zamalloa, Arana-Arexolaleiba (2023) — "Shielded Reinforcement Learning: A review of reactive methods for safe learning"** · IEEE/SICE International Symposium on System Integration (SII) 2023 · [SN]. 14/16 as P3-17.

**P3-19 · Olukola, Rahimi (2026) — "Pedagogical Safety in Educational Reinforcement Learning: Formalizing and Detecting Reward Hacking in AI Tutoring Systems"** · arXiv:2604.04237, 5 Apr 2026 (**preprint; states submission to IJAIED**) · [AB] — four-layer model of pedagogical safety (structural, progress, behavioural, alignment); Reward Hacking Severity Index; 120 sessions, four conditions, three simulated learner profiles, 18,000 interactions; engagement-optimised agent favoured a high-engagement action without learning gains; constrained architectures with prerequisite enforcement and minimum cognitive demand reduced it. 14: **guardrails/constraints for educational RL, simulation-only.** 15: PREPAIred's guardrails constrain **difficulty transitions** for a tracking objective; the evaluation includes ablation of individual rules and a state-blind null. 16: Do NOT claim pedagogical-safety constraints for RL tutors as new.

**P3-20 · Olukola, Rahimi (2026) — "MC-CPO: Mastery-Conditioned Constrained Policy Optimization for Pedagogically Safe Intelligent Tutoring Systems"** · arXiv:2604.04251 v1 5 Apr 2026, v2 8 Jun 2026 (**preprint; states under review**) · [AB] — constrained RL where feasible actions depend on mastery state; analysis of over 21 million student interactions (Junyi Academy, XES3G5M); reports +18.3 % / +54.0 % mean per-episode mastery gain over baselines (as reported); a "safety gap theorem" that post-hoc filtering of unconstrained policies can be strictly suboptimal to optimising within the feasible set (as summarised). 14: **closest formal treatment of constraints vs post-hoc filtering in educational RL**; PREPAIred's guardrails are applied both in training (P3-C019) and evaluation. 15: none at method level. 16: Do NOT claim optimal constrained learning or safety guarantees; Do NOT claim a new formulation.

### 10.4 Simulation-only evaluation and its limits

**P3-21 · "Can LLMs Reliably Simulate Real Students' Abilities in Mathematics and Reading Comprehension?"** · arXiv:2507.08232 (**preprint**; authors not verified) · [SN] — studies whether LLM-simulated students match real ability distributions. 14: validity of simulated learners. 15: PREPAIred's simulated candidates are **parametric** (a sigmoid performance model over skill and difficulty with noise in `rl/training/simulated_candidate.py`), not LLM-simulated, and were never validated against real candidates. 16: Do NOT claim the personas represent real candidates.

**P3-22 · Statement from the results of the "simulated students" search (context, [SN])** — several 2025–2026 sources report that LLM student simulators rarely test whether synthetic ability distributions match real students, that RL routing models may overfit idealised feedback in simulation, and that simulators can exhibit sycophancy. These are secondary statements from search summaries; each source needs to be read before it is cited.

**P3-23 · Kannam et al. (2024) — "Code Interviews: Design and Evaluation of a More Authentic Assessment for Introductory Programming Assignments"** · arXiv:2410.01010 (as cited in P3-01; **not read**) — human-conducted code interviews in a course. 14: source for the "interview as assessment" premise. Second-pass read.

---

## 11. Paper 3 closest-prior-work analysis

| # | Candidate contribution | Closest prior work | What that work does | What remains different | Condition |
|---|---|---|---|---|---|
| C3-a | **A learned PPO difficulty controller** for simulated technical interviews | Axak 2025 (PPO/DQN/rule-based tutor, simulator + replay); Ion 2025 (adaptive vs fixed question policy, simulated coding interviews); Pérez 2024; Ruan 2024 | RL and information-gain policies for adaptive instruction/assessment | Nothing at the idea level; the controller itself is not a contribution | Do not claim |
| C3-b | **Evaluation design**: persona as the statistical unit, training seed as a second random factor, equivalence margin (±0.12), two-way cluster bootstrap | Axak 2025 (single fixed seed in the text read) | Simulation comparison without the clustered design (from what I read) | The design is a methodological difference, contingent on the registered X3-A protocol | X3A-C001 |
| C3-c | **Null baseline under identical guardrails** (Constant-Same+G): PPO's contribution is not identified (MAE difference −0.0350, CI [−0.0818, +0.0021]; Equivalent within ±0.12; PPO more volatile) | None found comparing a learned educational policy to a state-blind constant action under the same constraint layer | — | This is the core "under-evaluated property": what the learned component adds beyond the guardrail | X3A-C001/C002; reviewer will ask if the margin ±0.12 is justified |
| C3-d | **Rule-based guardrails** evaluated by rule ablation and on a held-out persona grid | Alshiekh 2018; Carr 2023; Könighofer 2025 (formal shields); Olukola 2026 (pedagogical constraints); MC-CPO 2026 | Formal or constraint-based safe RL | Hand-written rules, no formal spec; ablation results are mostly small (G1 removal lowers MAE by 0.087, CI includes 0); shield did not improve tracking of a constant Same action | X3A-C003/C006 |
| C3-e | **Boundary-saturation and override accounting** (guardrail activations 45 %, action overrides 7.9 %, attempted out-of-range 18.6 % of guarded turns on the frozen study) | None found (search not specific) | — | Reporting how often a guardrail actually changes the policy's action | P3-C005/C006/C008 |
| C3-f | **Metric critique**: tracking MAE cannot distinguish trajectories alternating between two integer levels adjacent to a half-integer target (P3-C023) | None found | — | A measurement limitation; a hypothesis until a literature check is done | P3-C023 |
| C3-g | **Simulation-only limitation accounting** (single default training candidate; unseeded candidate noise; evaluated checkpoint differs from the deployed one) | Ion 2025 (validation pending); Olukola 2026 (simulated learners); simulated-student validity literature | Same limitation acknowledged | Explicit provenance accounting of what the frozen checkpoints were trained against | P3-C016…C019 |

## 12. Paper 3 candidate contribution statements (hypothesis phrasing)

1. *"We evaluate a learned difficulty controller against a state-blind constant action under an identical rule-based guardrail layer, with personas as the unit of analysis, and report that the learned component's contribution to tracking error is equivalent to the baseline within a pre-registered margin while being more volatile."* — differs from single-seed, baseline-vs-PPO comparisons (Axak 2025); supported by X3A-C001/C002.
2. *"We report how a hand-written guardrail layer changes a learned policy's actions and which rules matter under ablation."* — relates to shielding and constrained-RL work without formal guarantees; supported by P3-C005…C008 and X3A-C006.
3. *"We show PPO uses its observation (zeroing the observation raises MAE by 0.370 [0.091, 0.641])."* — a sanity check; supported by X3A-C004.
4. *"We account for the limits of simulation-only evidence and of the frozen training setup."* — supported by P3-C016…C019.
5. **Not available**: any statement about learning benefit, real candidates, or superiority to existing adaptive-assessment methods.

## 13. Paper 3 — claims we must avoid

| Claim | Why |
|---|---|
| RL/PPO for adaptive difficulty or adaptive question selection as new | Axak 2025; Pérez 2024; Ruan 2024; Tang 2026; BOBCAT/NCAT; Ion 2025 |
| Adaptive question selection in **simulated coding interviews** as new | Ion 2025 (extended abstract) |
| "Shielded RL" with safety guarantees | Guardrails are hand-written; no formal specification or proof; distinguish from Alshiekh 2018, Carr 2023 |
| Pedagogical-safety constraints for RL tutors as new | Olukola 2026 (two preprints) |
| PPO outperforms heuristic/proportional baselines as the headline | True on the 40-persona grid (X3A-C005), but PPO is equivalent to a constant Same action under the same guardrails; the headline would mislead |
| PPO improves difficulty adaptation / candidate learning | Simulation only; no learners; contribution unidentified under guardrails |
| Personas represent real candidates | Parametric simulated candidates, unvalidated; frozen checkpoints trained against one default candidate |
| Seed-level reproducibility of the checkpoints | Training candidate noise is unseeded (P3-C018); evaluated checkpoint differs from the deployed one (P3-C016) |
| Superiority to Elo-style/CAT methods | Not compared |
| "Statistically significant" without stating unit | Statistical unit is the persona; sessions/turns descriptive |

---

## 14. Cross-paper overlap analysis

**14.1 Literature that straddles papers (cite consistently, do not double-claim).**

| Literature | Papers it touches | Consequence |
|---|---|---|
| Attacks on LLM/ASAG graders (Filighera 2020/2024; Raina 2024; Condor & Pardos 2024; Cai 2026; Li 2026; Sahoo 2026; Li & Liu 2025) | Paper 1 (injection/authority separation) and Paper 2 (adversarial robustness of the evaluator) | The two papers must state which component is attacked: P1 = LLM feedback/follow-up channels and code sandbox; P2 = SBERT/FAISS/CrossEncoder composite. If any LLM output reaches scoring, both papers face the same reviewer critique |
| Simulated-student validity (Ion 2025; LLM student simulators) | Paper 3 (simulated personas) and Paper 1 (if the system paper reports RL behaviour) | Paper 1 should not report RL efficacy; Paper 3 owns the simulation-only caveat |
| Interview-practice systems (Conversate; PolyInterview) | All three, as related work | Only Paper 1 can legitimately position against them at system level; Papers 2 and 3 should not re-describe the system in detail |
| Reviews of automated assessment (Paiva 2022; Messer 2024; adaptive-learning reviews) | Papers 1 and 3 | Cite for framing only, not as evidence of gaps until read |
| CAT/adaptive assessment (BOBCAT, MAB-CAT, CodeGENCAT) | Paper 3, and possibly Paper 2 if item difficulty is discussed | Second-pass read required |

**14.2 Self-overlap risks visible from the literature side.**
1. The **same system** appears in all three papers. Related-work sections that describe "an LLM-based interview-practice system with speech" will look identical across papers; each paper needs its own scoped positioning.
2. The older `research/audit/paper_overlap_matrix.md` predates the current plan. It lists working titles containing "Multimodal", a Paper 1 question phrased around "sub-second latency", and venue targets that have since changed; those wordings conflict with the current registry (no video component; evaluator P95 2,098.6 ms, P99 26,369.4 ms in P1-C001; warm P95 615 ms in X1D-C002). It needs a refresh before any related-work text is drafted (not done here).
3. Paper 2's evaluator formula is a "shared asset" with Paper 1 (architecture) and Paper 3 (environment state may consume evaluator output — **not checked in this pass**); each paper must cite the others' scope rather than restate results.
4. Prompt-injection literature in Paper 1 and adversarial-ASAG literature in Paper 2 overlap in method vocabulary (universal triggers, rubric-aligned injection); use distinct terms ("channel invariance" vs "score-ceiling containment") to avoid the appearance of duplicated contributions.

**14.3 Which paper carries which contribution type (working proposal, for Sparsh/ChatGPT to decide).**

| Contribution type | Best home | Reason from the literature side |
|---|---|---|
| Sandbox containment evaluation with controls | Paper 1 | Only Paper 1 touches the sandbox literature |
| LLM-channel invariance | Paper 1 | Architecture-level; grader-attack literature is context |
| Evaluator agreement + robustness + provenance | Paper 2 | ASAG literature |
| Persona-clustered RL evaluation with a null baseline | Paper 3 | RL-in-education literature |
| System description, latency, tests | Paper 1 (supporting) | Not a contribution by itself |

---

## 15. Missing literature categories (not searched, or searched too thinly)

| Category | Why it matters | Papers |
|---|---|---|
| **Technical-interview research** (candidate anxiety/stress, whiteboard vs practice, hiring-interview assessment) | The application premise; not covered in this pass beyond the interview-practice systems | All |
| **Speech/prosody/confidence and hesitation analysis** in assessment; speech-based assessment ethics | Speech is in the system; the speech-claim audit already withdrew a "guarantee" wording | 1 |
| **Knowledge tracing and student modelling** (DKT, BKT, IRT) | The natural baseline family for adaptive difficulty; only CAT and Elo were touched | 3 |
| **RL evaluation methodology** (reporting seeds, variance, statistical precipice-type critiques; reproducibility in deep RL) | Paper 3's statistical design is a claimed strength; it needs to be positioned against the RL-methodology literature. I have candidate titles from memory that are **not verified**, so they are not listed as sources here | 3 |
| **Offline RL / off-policy evaluation in education** (partly seen in Axak 2025) | A reviewer will ask why there is no real-data replay | 3 |
| **Curriculum learning / difficulty scheduling** | Alternative framing of adaptive difficulty | 3 |
| **Equivalence testing / non-inferiority in ML** | Margin ±0.12 justification | 3 |
| **Human-rater agreement methodology** (ICC, Krippendorff, Bland–Altman, Lin's CCC; correlation validity) | Paper 2 already uses these; a citation base is needed | 2 |
| **Cross-encoder/passage-ranking models used for grading; transfer of ms-marco models** | Provenance and validity of R | 2 |
| **Dense retrieval/FAISS for answer evaluation, rubric retrieval** | S2_eff component | 2 |
| **LLM-generated/LLM-simulated candidate answers as test data** | Benchmark provenance (author-constructed) | 2 |
| **Code-execution sandbox security for LLM agents** (beyond SandboxEval) | Only one preprint was found | 1 |
| **Reproducibility/preregistration practices in ML and software-engineering research** | The frozen-protocol/hash-manifest process | All |
| **Privacy/regulation for AI in education** (EU AI Act classification of educational systems, GDPR, biometric/speech data) | Ethics/provenance records are incomplete; reviewers of education venues ask | All |
| **Ethics of constructed data and rater recruitment** | The rater provenance/ethics gap | 2 |
| **Local small-LLM reliability (Qwen 1.5B Q4_K_M) and quantisation effects on feedback quality** | The feedback path uses a small local model | 1 |
| **Fault injection / chaos engineering / graceful degradation in ML pipelines** | Only vocabulary (Avizienis 2004) was found | 1 |
| **Hostile-reviewer literature on "AI for interview prep" commercial claims** | Not scholarly; probably out of scope | — |

## 16. Recommended search queries for a second pass

Databases to use: ACM DL, IEEE Xplore, ACL Anthology, Springer Link, Google Scholar (with forward citations), dblp, arXiv (for currency), Semantic Scholar/OpenAlex API for citation graphs. Apply a date window (2018–2026 unless foundational) and record hit counts.

**Paper 1**
1. `("automated assessment" OR autograder OR "online judge") AND (sandbox OR container OR seccomp) AND (evaluation OR "attack" OR escape)`
2. `"untrusted code" AND (LLM OR "code generation") AND (sandbox OR isolation) AND benchmark`
3. `("prompt injection") AND (grading OR grader OR "student submission" OR "code review")` — forward citations of Cai 2026, Li 2026, Sahoo 2026
4. `("instruction hierarchy" OR "privilege separation" OR "dual LLM" OR "quarantined") AND (education OR assessment)`
5. `("graceful degradation" OR "fallback" OR "fault injection") AND (LLM OR "language model") AND (education OR tutoring OR assessment)`
6. `("interview practice" OR "mock interview") AND (LLM OR "large language model") AND (evaluation OR "user study")`
7. `"technical interview" AND (anxiety OR stress OR whiteboard OR "hiring")`
8. `("trustworthy AI" OR "responsible AI") AND education AND (assessment OR grading) AND ("systematic review" OR "scoping review")`
9. Forward citations of SandboxEval, APAC, and "Docker" + "assignment" + "autograder"
10. `"Gradescope" OR "PrairieLearn" OR "CodeGrade" AND security AND paper`

**Paper 2**
1. `("automatic short answer grading" OR ASAG) AND (survey OR review) AND (2023 OR 2024 OR 2025 OR 2026)`
2. `("short answer" OR "constructed response") AND ("length" OR "verbosity") AND (bias OR spurious OR shortcut)`
3. `("cross-encoder" OR "cross encoder") AND (grading OR "answer scoring" OR "student answer")`
4. `("metamorphic testing" OR "behavioral testing" OR CheckList) AND (grading OR "answer scoring" OR "essay scoring")`
5. `("LLM-as-a-judge") AND (bias OR robustness) AND (education OR grading OR rubric)`
6. `("technical interview" OR "interview answers") AND ("answer evaluation" OR "answer scoring" OR NLP)`
7. `("agreement" OR "alignment") AND ("automated grading" OR "automated assessment") AND (teacher OR instructor) AND programming`
8. `("small benchmark" OR "few items") AND ("human agreement") AND (bootstrap OR cluster) AND grading`
9. Forward citations of Mohler 2011, Filighera 2020, Condor & Pardos 2024, Ormerod 2023
10. `("SBERT" OR "sentence-BERT") AND ("short answer") AND (retrieval OR FAISS OR rubric)`

**Paper 3**
1. `("reinforcement learning") AND ("intelligent tutoring" OR "adaptive learning") AND ("simulated students" OR "simulated learners") AND (PPO OR "proximal policy")`
2. `("difficulty adjustment" OR "difficulty adaptation") AND ("reinforcement learning") AND (interview OR assessment OR quiz)`
3. `("safe reinforcement learning" OR shielding OR "action masking" OR "constrained") AND (education OR tutoring)`
4. `("knowledge tracing") AND ("reinforcement learning") AND ("question selection" OR "exercise recommendation") AND baselines`
5. `("adaptive testing") AND ("reinforcement learning") AND (coding OR programming)`; forward citations of Ion 2025, CodeGENCAT
6. `("sim-to-real" OR "simulation gap") AND (education OR tutoring) AND "reinforcement learning"`
7. `("evaluation" OR "reproducibility") AND ("deep reinforcement learning") AND (seeds OR "statistical") ` — RL-methodology literature
8. `("non-inferiority" OR "equivalence test") AND ("machine learning") AND (baseline OR policy)`
9. `("Elo" OR "item response theory") AND (difficulty OR adaptive) AND (baseline) AND ("reinforcement learning")`
10. Forward citations of Riedmann 2025, Mon 2023, Olukola 2026 (two preprints), Axak 2025

**Priority reading list for the second pass (read in full before any contribution statement is written):**
1. SandboxEval (2504.00018) — protocol and any negative controls
2. Cai 2026, Li 2026, Sahoo 2026 — exact threat models (is the LLM the scorer?) and defences tested
3. CaMeL and AgentDojo — what "authority separation" means formally, to word C1-b correctly
4. Riedmann 2025 — share of simulation-only studies; any guardrails
5. Olukola 2026 (both) — constraint formulation and evaluation design
6. Axak 2025 — the "±" values, the number of runs, whether a statistical test exists (I did not see one in the parts read)
7. CodeGENCAT (2602.20020) and BOBCAT/NCAT — adaptive assessment baselines
8. Hickman & Bell 2024 (WiPSCE) — teacher-alignment findings
9. Filighera 2020/2024 and Condor & Pardos 2024 — adversarial ASAG protocols
10. Ormerod 2023 — ensemble design and validation statistics
11. Messer 2024 and Paiva 2022 — how they treat security/sandboxing and evaluation quality
12. Ye 2025 and Dubois 2024 — bias quantification methods that could be applied to the composite

## 17. Exact literature questions that need deeper investigation

**Paper 1**
1. Does any peer-reviewed paper evaluate an assessment sandbox with **weakened-configuration (negative) controls** or an equivalent design showing the oracle can fail? (Read SandboxEval; check APAC descendants.)
2. Is there peer-reviewed work on **dependability/graceful degradation** of an LLM-assisted assessment pipeline, or only general dependable-systems literature?
3. In the grader-hijacking papers, is the LLM always the scorer? Which defences were evaluated, and would any of them apply when the LLM has no write path to the score?
4. What does the literature say about **container flags as a security boundary** (non-root, no-network, cap-drop, read-only, PID/memory limits) for untrusted student code — evidence of escapes, or of adequacy?
5. Which peer-reviewed venues publish LLM-interview-practice system papers, and what evaluation standard do they apply (user studies vs system measurements)?

**Paper 2**
6. What are the reported correlation ranges for cross-encoder or SBERT-based ASAG on CS answers, and are they measured with Pearson, Spearman or QWK? (Needed only to position, not to compare.)
7. Is there a peer-reviewed treatment of **answer-length dependence in non-LLM graders**?
8. How do ASAG papers handle **clustering by question** in uncertainty estimates? Is question-cluster bootstrap reported anywhere?
9. Are there benchmarks of **technical-interview answers** (as opposed to course short answers) with human grades?
10. What is the published guidance on **rater provenance and ethics disclosure** for small constructed benchmarks?

**Paper 3**
11. How many studies in Riedmann 2025 and Mon 2023 evaluate only in simulation, and how many report multi-seed variation?
12. Is there any educational RL work comparing a learned policy against a **state-blind constant-action** null under the same constraint layer?
13. Does the CAT/RL literature use a difficulty-**tracking** objective (target-difficulty MAE) or expertise estimation only?
14. What justification exists in the literature for equivalence margins in simulated-policy comparisons?
15. Does the Elo/IRT difficulty-matching literature supply baselines PREPAIred should have included?

## 18. Preliminary novelty hypotheses (each is a **hypothesis**, not a claim)

Each hypothesis names the closest prior work and the evidence it would need. None may be used as manuscript text until the second pass and the corresponding experiment/evidence are complete.

| ID | Hypothesis (permitted vocabulary) | Closest prior work | Evidence needed before it can be stated |
|---|---|---|---|
| H1 | The Paper 1 sandbox evaluation **differs from** prior assessment-sandbox work by including predefined weakened-configuration controls and a multi-layer oracle | SandboxEval (2025 preprint); APAC (2015) | X1-C run; SandboxEval full text read; confirm neither uses negative controls |
| H2 | Testing **exact invariance** of score/difficulty/ranking to LLM-facing input/output **studies an under-evaluated property** for systems in which the LLM does not score | CaMeL (2025 preprint); Cai 2026; Li 2026; Sahoo 2026 | X1-B run; channel enumeration; read those papers' threat models |
| H3 | Reporting **measured** degradation from an LLM path to a non-LLM path **focuses on** a property not found in the assessment literature in this pass | Avizienis 2004 (vocabulary only); none found | Fault-injection experiment; second-pass search |
| H4 | The Paper 2 composite study **extends** ASAG agreement reporting with question-clustered intervals and a documented trade-off between safety components and agreement | Mohler 2011; Ormerod 2023; Condor & Pardos 2024 | X2-C confirmatory data or explicit exploratory labelling; 2-pass check of clustering practice |
| H5 | Applying **length-residual analysis to a non-LLM composite** evaluates a property discussed mainly for LLM judges | Dubois 2024; Zheng 2023; Ye 2025 | Read X2A-C007 value; second-pass search on length effects in ASAG |
| H6 | Paper 3's **null-baseline-under-identical-guardrails** design **evaluates** what a learned policy adds beyond a constraint layer, which the RL-in-education studies read so far do not report | Axak 2025; Olukola 2026 | Read Riedmann 2025 and Olukola 2026 fully; confirm no such comparison |
| H7 | Reporting **guardrail activation vs action-override accounting** **differs from** the formal-shield literature, which reports safety guarantees rather than intervention frequency | Alshiekh 2018; Carr 2023; Könighofer 2025 | Read those papers' evaluation sections |
| H8 | The persona-clustered, two-way (persona × training seed) analysis **differs from** single-seed comparisons in the education-RL studies read | Axak 2025 | Second-pass check of how the review literature treats seeds and clustering |
| H9 | The **combination** of a sandboxed executor, a non-LLM evaluator, a guardrailed adaptive controller and a local LLM in one traceable system **combines previously studied components**; the system itself is not a contribution | Conversate; PolyInterview; APAC | None — this is a scoping statement, and it should appear as such |

**What this file does not conclude.** It does not establish that any PREPAIred contribution is absent from the literature, and it does not rank venues. Any statement of the form "we could not find prior work on X" must be accompanied by the exact queries, databases and date of the search (§16) in the manuscript's method or a supplementary note.

*End of first-pass matrix. No Zotero entries were created; no other files were modified.*
