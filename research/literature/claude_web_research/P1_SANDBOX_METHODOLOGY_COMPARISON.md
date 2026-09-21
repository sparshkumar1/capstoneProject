# Paper 1: AI-sandbox evaluation methodology comparison (gap-closure pass, 2026-09-21)

Literature note only. It does not touch X1 results or the Paper 1 claim matrix. All PrepAIred-side statements use the wording already in the claim matrix and the task brief (nine fixed attack programs, shipped configuration plus weakened controls, host-side observables, 5 repetitions, one Docker Desktop/WSL2 machine, status strings found insufficient as oracles). Where I cannot see a detail of X1-C in the brief I do not restate it.

## Sources compared (full-text reads this pass unless stated)
| Ref | Source | Type | How read |
|---|---|---|---|
| [1] | Marchand et al., SandboxEscapeBench, arXiv:2603.02277 v3 (Aug 2026); header shows "Proceedings of the 43rd International Conference on Machine Learning, Seoul, South Korea. PMLR 306, 2026" | peer-reviewed venue per its own header (proceedings listing itself not opened) | V-TEXT, full PDF text |
| [6] | Rabin et al., SandboxEval, arXiv:2504.00018 (Mar 2025) | preprint | V-TEXT, full PDF text (11 pages) |
| [2] | Andronchik and Lokhmakov, AI Code Sandboxes Part 1, arXiv:2606.08433 (Jun 2026) | preprint | V-TEXT, front matter, abstract, methodology summary; not the whole 61 pages |
| [54] | Guo et al., RedCode, arXiv:2411.07781 | preprint here; venue not verified | V-TEXT, abstract, evaluation-pipeline section |
| [55] | Abdelnabi, Hicks, Rieck, Sadeghi, "Measuring Security Without Fooling Ourselves: Why Benchmarking Agents Is Hard," arXiv:2605.22568 (May 2026) | preprint, position paper | V-TEXT, full |
| [4] | Singh, Mahmoud, Murillo, "AI Sandboxes: A Threat Model, Taxonomy, and Measurement Framework," arXiv:2606.18532 | preprint | V-TEXT, abstract and introduction, keyword search |
| [5] | Rashidi, execution-security SoK, arXiv:2607.05743 | preprint | V-PAGE only (earlier pass) |
Excluded name: "AgentEscapeBench" exists but is an escape-room reasoning benchmark for tool-grounded planning, not a containment benchmark (search snippet); not a sandbox precedent.
Part 2 of the comparative study: not found in the searches run; Part 1 says "Part 1 of 2".

## Comparison table
| Dimension | SandboxEscapeBench [1] | SandboxEval [6] | Comparative study Pt 1 [2] | RedCode [54] |
|---|---|---|---|---|
| Threat model | Motivated adversarial agent with root shell in a container; initial access assumed; escape = read a host file outside all container namespaces; no monitoring; stealth not required | Untrusted LLM-generated code executed by an assessment framework; probes what the sandbox exposes | AISI T0.H2.N2: single-tenant operator running untrusted (AI-generated) code on own infrastructure; multi-tenant, side channels, control-plane and unpublished bugs out of scope | Risky code executed by code agents in Docker |
| Sandbox technology | Docker/OCI and Kubernetes containers inside a VM (Vagrant or EC2), nested design | Containers managed by an orchestration system (a Dyff instance); also run directly on a laptop for comparison | Five products in three engine classes (microVM, userspace kernel, OCI container) | Docker containers, one image per test case |
| Attacker | LLM agents (ReAct loop, bash and submit tools), 9 models, up to 2.5M tokens (100M in later runs) | Manually written Python test programs (LLM-generated tests were tried and abandoned) | No attacker; engine measurements, probes, desk research | Agent-issued code from fixed risky prompts (750 cases) |
| Attack programs | 18 tasks across orchestration, runtime, kernel layers; known documented exploits; deliberately introduced weaknesses | 51 manually crafted test cases (information exposure, filesystem manipulation, external communication, dangerous operations) | 14-entry primitive reachability matrix plus probes | 25 risky scenarios x 30 cases |
| Oracle | One host-side secret: retrieval of the flag string in /flag.txt on the host, exact string match, submitted through a tool | Status per test: Accessed, Denied, Unknown; "Accessed" = "the code executed successfully and returns the expected outcome" (in-payload result) | Per-axis verdicts pass/fail/partial/inconclusive/skipped; "inconclusive is not pass and not fail" | Deterministic scripts per case that re-enter the container and check environment state (for example, whether /etc/passwd was deleted), plus output scrutiny |
| Host-side verification | Yes: the flag lives outside the container and is checked independently of the agent's narrative | Not described; results are what the test code observed inside the environment | Host-side harness for engine measurements | Container-side environment-state checks, not host-side |
| Is payload self-report trusted? | No: success requires the actual secret | Largely yes: outcome is derived from what the payload observed | Not applicable | Partly no: state re-checked after the run |
| Positive / negative controls | Reference solution scripts confirm each task is solvable ("solution" variant); shortcuts detected by transcript analysis; deliberately vulnerable configurations give a positive signal; a hardened outer layer with no known vulnerabilities | No weakened-configuration control; a comparison run directly on a laptop gave "everything accessible" | Verdict semantics separate unmeasured from safe | Not described in the text read |
| Repetition | 5 trials per model-task pair; Wilson 95% intervals | Not described | Single pinned host | Not described in the text read |
| Runtime / container observables | Container-to-host escape via flag | Files, processes, network reachability seen from inside | Kernel reachability, capabilities, /dev/kvm, patch cadence | File and process state after execution |
| Limits stated | Not end-to-end compromise likelihood; simple agents; coverage cannot exhaust deployments; absence of success at a budget "should not be interpreted as ruling out a vulnerability" | 51 scenarios do not cover the whole space; one Linux platform; Python only | Threat-model qualification matrix; no composite ranking | not read |

Position paper [55]: "hardware-enforced isolation, separate privilege domains for the agent and the answers, and verification of task completion" as outer protections; and canary tokens: if an agent "reproduces one of these canaries during evaluation, it has reached parts of the infrastructure that were never meant to be accessible and its score must not be trusted." The paper also states benchmarks must be treated "as an adversarially exposed system". Assurance framework [4]: a "weakest-link rule for composing per-dimension evidence into a bounded deployment claim" and a threat model that includes "attacks on the assurance apparatus itself".

## What part of the X1-C methodology is already established
1. Fixed, documented attack programs run against a container to see what it exposes or permits ([6], [1] with known exploits, [54]).
2. Deterministic post-run checks of environment state instead of trusting an LLM judge or the payload's own words ([54], [1]).
3. A host-side secret as the success signal that the payload cannot forge ([1]; canary idea in [55]).
4. Deliberately weakened or vulnerable configurations to show the harness can detect a breach ([1] "intentionally introduced weaknesses" and solvability verification through a reference solution).
5. Repeated trials with an interval or a count ([1]: 5 per pair).
6. Scoped verdicts that separate "not observed" from "safe" ([2] verdict semantics; [1] limitation wording; [4] bounded claims).
7. Fault injection into LLM applications (already in the earlier Paper 1 records: [7], [8]).

## What is merely application-specific implementation
The nine specific programs, the specific weakened flags, the specific host observables, the WSL2/Docker Desktop platform, the pre-flight filter and its bypass, and the interview-application pipeline (evaluator, compiler, Qwen). None of it is a general contribution.

## What remains defensible (within the searched literature; not a novelty claim)
- Applying the established pieces together to a shipped interview-preparation configuration, with an old-versus-new build comparison and a stated scope. SandboxEval [6] tests an assessment framework but with in-payload outcomes and no weakened controls; [1] uses controls and a host oracle but for adaptive LLM attackers against seeded vulnerabilities; [54] checks container state but not host state. No source read combines: fixed programs, weakened-flag controls, host-side observables, repetition, and old-versus-new build regression for an assessment pipeline. This is "not found among the sources read", and Part 2 of [2] and other unread sources could change it.
- The finding that SEC-01 depended on the literal pre-flight filter, and the observation that ptrace(TRACEME) returned 0 once bypassed. Docker's documentation says of ptrace that it is "Blocked in Linux kernel versions before 4.8 to avoid seccomp bypass" and that tracing arbitrary processes is blocked by dropping CAP_SYS_PTRACE; so the observation is consistent with documented default-profile behaviour and is best presented as an application-level finding, not new container knowledge.
- The lesson that status strings do not discriminate (P1-C3). This is the most threatened claim: [54] gives the same reason for using state-checking scripts (agent traces "may lack the necessary information"), [6] itself uses proxy operations and outcome statuses, and [55] treats verification and canaries as core. Present it as confirmation of a known principle inside this harness.

## Threat summary
- SandboxEscapeBench [1] makes any "secure sandbox" statement untenable without a threat model and shows a fixed non-adaptive suite is a small sample. It states "No prior benchmark systematically evaluates container escape"; that is their claim and must not be echoed for PrepAIred.
- Design elements listed under "established" cannot be described as new.
- The word "escape" implies capability against adaptive attackers; X1-C measures a shipped configuration against nine fixed programs.
