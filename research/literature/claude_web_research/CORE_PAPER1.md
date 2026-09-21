# Paper 1 core literature (systems / dependability), 2026-09-21

Each record: question, method, data/environment, results, stated limits, overlap, difference, threat, use, verification. "Quote" fields were returned by the fetch tool from the page and must be re-checked before print. Limits and results are as the authors state them; I did not verify them independently.

## Core 1. SandboxEscapeBench (W1-01) - strongest *recent* precedent, partial-overlap threat
- Marchand et al., arXiv:2603.02277 (Mar 2026, rev. Aug 2026); the paper's own header reads "Proceedings of the 43rd International Conference on Machine Learning, Seoul, South Korea. PMLR 306, 2026". **V-TEXT (full PDF read in the gap-closure pass); 18 tasks confirmed.**
- Question/method: measures an LLM agent's ability to break out of container sandboxes; nested sandbox with an outer layer holding the flag; Inspect AI CTF evaluation; challenge levels across orchestration, runtime and kernel layers (18 levels per a search-result summary of the abstract; the page I opened did not state a count).
- Quote (abstract, tool-extracted): "a nested sandbox architecture with the outer layer containing the flag and no known vulnerabilities." Threat model: "a motivated adversarial agent with shell access inside a container."
- Result (authors): when vulnerabilities are added, LLMs can identify and exploit them.
- Overlap with PrepAIred: Docker/OCI containers as the isolation object; escape as the measured outcome; controlled vulnerability injection is a positive-control idea.
- Difference: it evaluates *an LLM as attacker* against deliberately vulnerable containers. PrepAIred's X1-C tests nine fixed attack programs against a specific shipped configuration (plus weakened controls) inside an interview application, and never lets a model choose the attack. It measures the shipped config, not model capability.
- Threat: any framing of "container containment evaluation for AI code" as unstudied is untenable. The benchmark also shows that a fixed nine-program suite is a small, non-adaptive sample of attack space.
- Use: related work (container escape as an evaluated risk); limitation (fixed programs vs adaptive attackers). Do not imply PrepAIred measures escape resistance against capable agents.

## Core 2. AI Code Sandboxes: A Comparative Security Study, Part 1 (W1-02)
- Andronchik, Lokhmakov, arXiv:2606.08433 (Jun 2026, preprint). **V-PAGE.**
- Method: six engine-level measurements (attack surface, leakage, stackability, CVE history, patch cadence, fuzzing) over five AI-sandbox products; "no overall ranking is proposed" (corrected in the gap-closure pass; the earlier wording was not in the source).
- Finding (authors): engine classes (microVM, userspace kernel, OCI container) "separate cleanly on every architectural axis"; product pin policy is the dominant operator variable.
- Overlap: classification of OCI containers as one isolation class. Difference: it characterises products and engines; PrepAIred tests a configured deployment with attack programs. Part 2 (contents not opened) may contain behavioural tests; check before citing as engine-only.
- Threat: makes a broad "secure sandbox" claim for a stock OCI container untenable; supports the scoped wording already in the claim matrix.
- Use: motivate why isolation class matters and why results do not transfer across engines.

## Core 3. Fault-Tolerant Sandboxing for AI Coding Agents (W1-03) - closest term-level overlap
- Yan, arXiv:2512.12806 (Dec 2025, preprint). **V-PAGE.**
- Method: policy-based command interception plus transactional filesystem snapshots; testbed with Minimind-MoE and nano-vllm on Proxmox.
- Result (author): "100% interception rate for high-risk commands and a 100% success rate in rolling back failed states"; about 14.5% overhead per transaction (about 1.8 s).
- Overlap: "fault-tolerant" + "sandbox" + AI code execution; interception layer resembles a preflight filter.
- Difference: the fault model is agent-issued destructive commands and state rollback; PrepAIred's faults are evaluator outage, compiler timeout, and LLM-channel influence in an assessment pipeline. Different system, different oracles.
- Threat: a reviewer will notice the shared vocabulary. Avoid "fault-tolerant sandbox" as a title term unless distinguished. Note a self-reported 100% interception rate from a small suite is exactly the kind of claim the independent review told PrepAIred not to make.
- Use: related work on interception + rollback.

## Core 4. SandboxEval (W1-06) - strongest *direct* precedent
- Rabin, Hostetler, McGregor, Weir, Judd, arXiv:2504.00018 (Mar 2025, preprint). **V-TEXT (full PDF read in the gap-closure pass).** The earlier note that the authors call it a "preliminary version, working paper" is UNVERIFIED and withdrawn.
- Method: manually crafted test cases (sensitive-information exposure, filesystem manipulation, external communication, other dangerous operations) against an AI-assessment environment (Dyff).
- Overlap: multiple concrete test programs against an assessment sandbox; the closest prior to X1-C.
- Difference: PrepAIred adds host-side observables, predefined weakened controls, repeated runs, and a documented analysis of when status strings fail as oracles. Full text now read (gap-closure pass): SandboxEval has 51 hand-written Python test cases; outcomes are "Accessed", "Denied" or "Unknown" derived from what the test code returned; filesystem and dangerous operations use proxy checks rather than real damage; no weakened-configuration control and no repetition is described; the tests were also run directly on a research laptop, where the exfiltration and shutdown vectors succeeded. No independent host-side observer is described. See P1_SANDBOX_METHODOLOGY_COMPARISON.md.
- Threat: highest for the claim "attack programs against an assessment sandbox". The difference (host-side observables, weakened controls, repetition, old-versus-new builds) is real against SandboxEval but is established practice in SandboxEscapeBench and RedCode, so it is not a methodological novelty claim.

## Core 5. Execution-security SoK (W1-05)
- Rashidi, arXiv:2607.05743 (Jul 2026, preprint). **V-PAGE.** 39 papers, 17 categories.
- Gaps (author): isolation architectures lack shared benchmark evaluation; "policy-enforcement studies report failure rates from 69% to 98% of real denylists yet no isolation paper re-evaluates its own defense under that adversarial setting" (abstract, verified in the gap-closure pass; the 69.0%-98.6% figure comes from a third-party study of 1,709 scraped denylists that the SoK cites, so attribute it to that study).
- Relevance: directly supports the scoping of HIGH-3 (SEC-01 depended on literal preflight filtering). It also indicates that isolation-plus-filter studies are a recognised gap, so "combines filter, isolation and host observables" is describable as addressing a known gap, but not as unprecedented.
- Figures verified against the PDF text in the gap-closure pass (see QUOTE_AUDIT 1.19).

## Core 6. Fault-injection precedents for LLM systems (W1-07, W1-08)
- MAS-FIRE (Jia et al., arXiv:2602.19843, Feb 2026): 15 fault types, three non-invasive injection mechanisms, LLM multi-agent systems; "iterative, closed-loop designs neutralizing over 40% of faults" (abstract wording, verified in the gap-closure pass). **V-PAGE.**
- ReliabilityBench (Gupta, arXiv:2601.06112, Jan 2026): timeouts, rate limits, partial responses, schema drift; 1,280 episodes; success 96.9% to 88.1% under stress. **V-PAGE.**
- Overlap: fault injection with controls into LLM applications; timeouts. Difference: different application class, injection into tool/agent layers; outcome is task success, not "fail-closed without a scored result".
- Threat: "fault injection into LLM systems" cannot be presented as new. Use: methodological precedent for injecting timeouts/outages and for reporting degradation.

## Core 7. Authority separation and prompt injection (W1-09, W1-11, W1-12, W1-13)
- CaMeL (Debenedetti et al., arXiv:2503.18813): separates control and data flow; 77% of AgentDojo tasks with provable security vs 84% undefended (as reported). **V-PAGE.**
- Bhattarai and Vu (arXiv:2602.09947): argues deterministic architectural enforcement is necessary; conceptual, no empirical results per the abstract. **V-PAGE.**
- Grader-injection studies (Li et al., arXiv:2606.03090; Sahoo et al., arXiv:2601.21360): LLM graders "remain highly vulnerable" (Li et al., extracted); >95% failure on some open-weights models (Sahoo, snippet). **V-PAGE / V-SNIP.**
- Overlap: LLM as untrusted component; prompt injection aimed at grading. Difference: PrepAIred's LLM does not grade, so the study tests a different channel (does LLM-authored feedback text move deterministic score observables?). That channel test, as designed, was not found in the searched literature, but the architectural principle itself is established engineering practice.
- Use: motivates the architecture; the invariance test is the empirical addition, scoped by HIGH-2 (follow-up generation channel untested).

## Core 8. Docker documentation on ptrace (W1-14)
- Docker Docs, seccomp page. **V-PAGE (official).** Quote (verified against the page in the gap-closure pass): "Tracing/profiling syscall. Blocked in Linux kernel versions before 4.8 to avoid seccomp bypass. Tracing/profiling arbitrary processes is already blocked by dropping CAP_SYS_PTRACE ..."; the page also says the default profile "disables around 44 system calls out of 300+". Quote the whole sentence, not the fragment. So on modern kernels the default profile does not block ptrace. This is consistent with the observation that `ptrace(TRACEME)` returned 0 in the container once the preflight filter was bypassed, and supports the instruction not to describe SEC-01 as Docker ptrace isolation. It is an official-documentation fact about the default profile, not an evaluation of PrepAIred's own profile.

## Gap-closure pass additions (2026-09-21)
Full detail: `P1_SANDBOX_METHODOLOGY_COMPARISON.md` and `QUOTE_AUDIT.md`.
- **SandboxEscapeBench** upgraded to V-TEXT (full PDF). ICML 2026 (PMLR 306) appears in its own header. Design: host-side flag as the only success signal, reference-solution variants that prove each task is solvable, deliberately introduced weaknesses, transcript analysis for unintended shortcuts, 5 trials per model-task pair, Wilson intervals, explicit limitation that it is not an end-to-end compromise likelihood.
- **RedCode** (arXiv:2411.07781, venue not verified): deterministic evaluation scripts that re-enter the container and check environment state, motivated by unreliable LLM judgements and incomplete traces.
- **Abdelnabi et al.** (arXiv:2605.22568): benchmarks are attack surfaces; canaries and separate privilege domains; an agent reproducing a canary means its score must not be trusted.
- **Singh et al.** (arXiv:2606.18532): weakest-link rule for bounded deployment claims; threat model includes attacks on the assurance apparatus.
- **Comparative study Part 1** read at front-matter and methodology level; Part 2 was not found by search.
- No new direct precedent was found that combines fixed attack programs, weakened-flag controls, host-side observables, repetition and old-versus-new build regression for an assessment pipeline, among the sources read. This is a scope-limited absence.
- Most threatened existing claim: P1-C3 (status strings as insufficient oracles), because the same principle is stated in [54] and [55] and is implicit in [6] and [1].
