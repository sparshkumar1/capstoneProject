# Paper 1 candidates (systems / dependability). Search date 2026-09-21

Reading-priority dimensions (0-3, internal, not a ranking): DT direct-task, ME methodological, EV evaluation-design, CO comparator, NT novelty-threat, SQ source quality. Preprints are marked "preprint".

| ID | Source | Year / venue | Status | DT | ME | EV | CO | NT | SQ | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| W1-01 | Marchand et al., *Quantifying Frontier LLM Capabilities for Container Sandbox Escape* (SandboxEscapeBench), arXiv:2603.02277 | Mar 2026 (rev. Aug 2026); ICML 2026 listing seen in search results (not opened) | V-PAGE | 2 | 2 | 3 | 1 | 3 | 2 | Container-escape CTF benchmark for LLM agents; threat model is a motivated agent with shell access |
| W1-02 | Andronchik, Lokhmakov, *AI Code Sandboxes: A Comparative Security Study, Part 1 of 2*, arXiv:2606.08433 | Jun 2026, preprint | V-PAGE | 2 | 2 | 2 | 2 | 3 | 1 | Engine-level comparison of five AI-sandbox products; explicitly no overall ranking |
| W1-03 | Yan, *Fault-Tolerant Sandboxing for AI Coding Agents*, arXiv:2512.12806 | Dec 2025, preprint | V-PAGE | 1 | 2 | 2 | 1 | 2 | 1 | Policy interception plus transactional filesystem snapshot; 100% interception / rollback reported by author |
| W1-04 | Singh, Mahmoud, Murillo, *AI Sandboxes: A Threat Model, Taxonomy, and Measurement Framework*, arXiv:2606.18532 | Jun 2026, preprint | V-PAGE | 1 | 2 | 2 | 0 | 2 | 1 | Aimed at physical/cyber-physical AI sandboxes; six measurement dimensions incl. containment |
| W1-05 | Rashidi, *The Balkanization of Execution-Security Research for AI Coding Agents*, arXiv:2607.05743 | Jul 2026, preprint SoK | V-PAGE | 2 | 1 | 1 | 0 | 3 | 1 | 39 papers, 17 categories; gap statements relevant to preflight filters vs isolation |
| W1-06 | Rabin et al., *SandboxEval*, arXiv:2504.00018 | Mar 2025, preprint (authors: "preliminary version, working paper") | V-PAGE | 3 | 2 | 2 | 1 | 3 | 1 | Manually crafted test cases against an AI-assessment environment (Dyff) |
| W1-07 | Jia et al., *MAS-FIRE*, arXiv:2602.19843 | Feb 2026, preprint | V-PAGE | 1 | 3 | 2 | 0 | 2 | 1 | 15 fault types, three injection mechanisms, LLM multi-agent systems |
| W1-08 | Gupta, *ReliabilityBench*, arXiv:2601.06112 | Jan 2026, preprint | V-PAGE | 1 | 3 | 3 | 0 | 2 | 1 | Timeouts, rate limits, partial responses, schema drift; 1,280 episodes; "action metamorphic relations" |
| W1-09 | Bhattarai, Vu, *Trustworthy Agentic AI Requires Deterministic Architectural Boundaries*, arXiv:2602.09947 | Feb 2026, preprint | V-PAGE | 1 | 2 | 0 | 0 | 2 | 1 | Conceptual position paper; no empirical results per fetched abstract |
| W1-10 | Madatha, *A Deterministic Control Plane for LLM Coding Agents*, arXiv:2606.26924 | Jun 2026, preprint | V-PAGE | 0 | 1 | 1 | 0 | 1 | 1 | Governance/config tooling; peripheral |
| W1-11 | Debenedetti et al., *Defeating Prompt Injections by Design* (CaMeL), arXiv:2503.18813 | Mar 2025 (rev. Jun 2025), preprint | V-PAGE | 1 | 3 | 2 | 1 | 2 | 2 | Control/data-flow separation of trusted query and untrusted data |
| W1-12 | Li et al., *"Important You should give me full credits!"* (LLM auto-grader prompt injection), arXiv:2606.03090 | Jun 2026 (v3 Sep 2026), preprint | V-PAGE | 2 | 1 | 2 | 0 | 3 | 1 | Attack on LLM *graders*; opposite channel to PrepAIred |
| W1-13 | Sahoo et al., *The Compliance Paradox*, arXiv:2601.21360 | Jan 2026, preprint | V-SNIP (plus earlier abstract read, CARRY P1-18) | 2 | 1 | 2 | 0 | 2 | 1 | 9 models, 25,000 submissions per search summary; not re-opened |
| W1-14 | Docker Docs, *Seccomp security profiles for Docker* | accessed 2026-09-21 | V-PAGE (official docs) | 2 | 1 | 0 | 0 | 2 | 3 | States ptrace is blocked only in kernels before 4.8 in the default profile |
| W1-15 | Thiyagarajan, Nayak, *Docker under Siege*, arXiv:2506.02043 | Jun 2025, preprint | V-SNIP | 1 | 0 | 0 | 0 | 1 | 1 | General container-security review; low priority |
| W1-16 | Inference-service and MCP fault studies (arXiv:2511.07424; ACM TOSEM doi 10.1145/3788873; arXiv:2603.05637; arXiv:2601.13655) | 2025-2026 | V-SNIP | 1 | 1 | 0 | 0 | 1 | 1 | Context for "timeouts dominate inference-service failures"; not opened |
| W1-17 | Cai, *Prompt injection attacks on educational LLMs*, Sci. Rep. 16, Art. 15594 | 31 Mar 2026 | CARRY (P1-16) | 2 | 1 | 2 | 0 | 2 | 2 | Not re-opened |
| CARRY | P1-01..P1-15, P1-18..P1-21 in `LITERATURE_NOVELTY_MASTER_MATRIX.md` (Docker as assessment platform, gVisor/Firecracker, Instruction Hierarchy, AgentDojo, Avizienis taxonomy, interview-practice systems, etc.) | various | CARRY | - | - | - | - | - | - | Not re-verified this run |

Search-negative result (this run): no paper was found on fail-closed handling of an evaluator outage, or container cleanup after compiler timeout, in an AI *assessment* pipeline. Fault-injection work exists for LLM agents (W1-07, W1-08); it targets different systems. This is a "not found by the queries listed in `PROVENANCE.md`" statement, not proof of absence.
