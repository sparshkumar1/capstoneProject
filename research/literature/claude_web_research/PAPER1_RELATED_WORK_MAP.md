# Paper 1 related-work map (planning only; no manuscript text)

Numbers in brackets are BIBLIOGRAPHY.md entries. Suggested IEEE section: II Related Work.

| Subsection | Strongest sources | What each contributes | How our work differs | Suggested placement | Do NOT claim |
|---|---|---|---|---|---|
| A. Containers and sandboxes for untrusted or agent-generated code | [1] SandboxEscapeBench; [2] comparative sandbox study; [4] AI sandboxes measurement framework; [14] Docker seccomp docs; CARRY: Spacek 2015, Firecracker, gVisor cost | Containers are common but share a kernel; escape is measured with adaptive agents; engine class matters; default profile details | Evaluates one configured deployment against nine fixed programs with controls | Opening of II-A; motivates scoped claim | That Docker equals microVM isolation; resistance to adaptive attackers |
| B. Testing sandboxes for AI/assessment code | [6] SandboxEval; [5] SoK; [3] fault-tolerant sandboxing | Manual test suites for assessment environments; a survey of gaps (filters vs isolation); interception plus rollback | Host-side observables, weakened controls, oracle analysis, filter dependence | II-B | That attack programs against assessment sandboxes are new; "fault-tolerant sandbox" as our label |
| C. Fault injection and failure handling in LLM systems | [7] MAS-FIRE; [8] ReliabilityBench; V-SNIP inference-service failure studies | Fault taxonomies; timeouts and rate limits as injected faults; degradation reporting | Assessment pipeline, fail-closed no-score handling, two builds | II-C | That fault injection into LLM applications is new; "all faults handled" |
| D. Authority separation and prompt injection | [11] CaMeL; [9] deterministic boundaries; [12] and [13] grader prompt-injection | Separation principle; grader vulnerability | LLM writes feedback only; invariance test of one channel; follow-up channel untested | II-D | That separation is our invention; "Qwen can never influence scoring" |
| E. Dependability vocabulary | CARRY Avizienis et al. 2004 | Fault/error/failure terms | Scoped use | II-A intro or Section III | Formal dependability or security guarantee |
| F. AI interview-practice systems (context only) | CARRY Conversate; PolyInterview (V-SNIP) | System-level context | No user study here | II intro | System concept as a contribution |

Gaps to fill before writing: read SandboxEval full text; read Part 2 of the comparative study when available; identify at least one peer-reviewed (not preprint) source per subsection because most 2026 sources are preprints.

## Gap-closure additions (2026-09-21)
- Add to the container-escape and sandbox-evaluation subsection: benchmark design practice for host-side oracles, positive controls and repeated trials [1], [54], [55]; assessment-sandbox test suites with in-payload outcomes [6]; engine-class differences [2]; bounded-claim assurance frameworks [4].
- Position PrepAIred as a scoped application of established practice to a shipped configuration, not as a benchmark of escape capability.
