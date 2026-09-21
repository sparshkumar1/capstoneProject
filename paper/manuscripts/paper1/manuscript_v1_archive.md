<!-- PAPER 1 MANUSCRIPT DRAFT v1 (2026-09-21). Markdown source; to be ported to the venue's official IEEE template once the venue is final. -->
<!-- Numbers trace to research/evidence/final/PAPER1_FINAL_CLAIM_MATRIX.md and the X1 artifacts cited there. No number was recomputed. -->

# Scoped Evaluation of Containment, Authority Boundaries, and Failure Handling in an LLM-Assisted Technical-Assessment System

*Authors and affiliations: withheld in this draft (anonymity requirement of the target venue is not verified).*

**Abstract—** LLM-assisted technical-assessment pipelines execute candidate code and place model-written text close to scoring, so an operator needs to know which containment, authority-boundary and failure-handling properties have actually been demonstrated. We report a scoped empirical evaluation of one implemented pipeline (a code-execution sandbox, an evidence-based answer evaluator and a local 1.5B-parameter language-model feedback service) in one environment: Windows 11, WSL2 and Docker Desktop. Three campaigns used host- or runtime-side observables and deliberately weakened controls. Nine attack programs met prespecified containment criteria in 5/5 repeated runs under the shipped configuration (one of them, ptrace, because of a literal pre-flight filter), while permissive controls breached in 5/5 runs where a control applied; for four attacks the executor status string did not distinguish contained from breached runs. Two defects found on the baseline build (an evaluator outage recorded as a 0.0 score; a compiler timeout leaving a running container) were absent on the repaired build in 5/5 repetitions. Under a fixed-evaluator test, 14 score-related observables were byte-identical across 72/72 valid benign/adversarial pairs, and a mutation control detected a deliberately injected authority path in 72/72. Scope limits are material: the ptrace attack was stopped by a literal pre-flight filter, not by demonstrated container behaviour; invalid numeric scores are sanitized to 0.0; the LLM follow-up-question channel was not tested; and the shipped 6 s model timeout is shorter than the 19–30 s local generation time. These are repeatability observations in one environment, not security or fault-tolerance guarantees.

**Keywords—** containment testing; authority boundaries; fault injection; LLM-assisted assessment; test oracles; dependability evaluation

---

## I. Introduction

An LLM-assisted technical-assessment pipeline does two things that deserve separate scrutiny. It compiles and runs code written by the person being assessed, and it places text produced by a language model in the same response path as a numeric score. An operator who deploys such a pipeline needs to know what has been demonstrated about three things: whether the code-execution environment contains what it is meant to contain, whether the language model can write to the fields that decide scores and difficulty, and what the pipeline does when a component fails.

The literature offers substantial methodology for each part. Sandbox-evaluation work runs fixed test programs or adaptive agent attackers against containers and judges success by host-side signals or by outcomes reported from inside the payload [1], [2], [3]. Work on benchmarking agent security recommends deterministic state checks and canary tokens [6], [7]. Fault-injection work introduces faults into services and LLM-agent systems and observes the outcome [8]–[10]. Studies of LLM graders report that model-written grading can be manipulated by injected instructions [11]–[13]. What these lines of work leave less explicit, for a single implemented assessment pipeline, is a property-by-property statement of what was demonstrated, with which oracle, on which build, in which environment, and where the test cannot tell.

This study addresses that narrower question. It treats the pipeline as the experimental vehicle and asks what controlled tests can support. Each concern is converted into a named property, a test condition, an oracle that does not rely on the component under test and, where possible, a deliberately weakened control that shows the oracle can register a failure. Results are reported for the shipped configuration and, where the campaigns found defects, for a baseline build and a repaired build.

We ran three campaigns against the pipeline: a containment campaign for the code sandbox (nine attack programs, X1-C), a fault-injection campaign for failure handling (X1-A), and a fixed-turn invariance test of score-related observables against language-model-written feedback (X1-B-I). Every scenario was repeated five times. The repetitions are deterministic repeatability checks, not random samples, and no inferential statistics are attached.

In brief, the shipped sandbox configuration met the prespecified criteria for all nine attack programs in 5/5 repetitions on both builds, with permissive controls breaching where applicable. Two failure-handling defects were found on the baseline build and were absent on the repaired build. Under the fixed-turn test, no compared observable changed across 72/72 valid adversarial pairs. Four limitations qualify these findings and are stated in Section VII. The evidence comes from one environment and does not amount to a security or fault-tolerance guarantee.

The research question is: *Which containment, authority-boundary, and failure-handling properties of an LLM-assisted technical-assessment pipeline can be demonstrated through controlled tests under a specified execution environment?* The contributions are scoped empirical evidence of four kinds: (1) containment of nine specified attack programs under one shipped configuration, with permissive controls; (2) tested failure handling for an evaluator outage and a compiler timeout, with a baseline-versus-repaired comparison; (3) a fixed-turn observation of the language-model feedback channel with mutation and static controls; and (4) an observation that executor status strings did not discriminate for four attacks, so host or runtime observables were necessary. We do not claim that the pipeline is secure, that the sandbox is universally isolating, or that language-model text cannot influence scoring.

## II. Related Work

**A. Testing containers and sandboxes for untrusted code.** Containers share the host kernel, and how well they contain code depends on configuration and threat model [3]. SandboxEscapeBench evaluates container escape by adaptive language-model agents against a nested sandbox, using retrieval of a flag string from the host filesystem as the success signal and deliberately introduced weaknesses [1]. SandboxEval provides 51 manually written test cases for environments that execute untrusted model-generated code, with outcomes derived from what the test code observes [2]. A comparative study of engine classes separates verdicts into pass, fail, partial, inconclusive and skipped and states that inconclusive is neither pass nor fail [3]. Benchmark-design commentary recommends state checks and canary tokens rather than trusting an agent's own report [6], [7], and a measurement framework proposes composing evidence into a bounded deployment claim [4]. A survey of execution-security research reports that policy-enforcement studies find high failure rates for real denylists, a figure the survey takes from a third-party study [5]. The present study applies these practices (fixed programs, host-side observables, weakened controls, repeated runs, bounded verdicts) to one shipped assessment configuration. It does not measure escape capability against adaptive attackers.

**B. Fault injection and failure handling in LLM systems.** Deliberate fault injection to observe failure behaviour is established practice for services [8]. Recent work applies fault injection or stress conditions to LLM-based multi-agent systems and agents [9], [10]. Those studies concern agent task success; the present campaign injects named faults into the request path of an assessment orchestrator and checks score and flag semantics.

**C. Authority separation and prompt injection.** Design-level separation of model output from privileged actions is an established defensive pattern [11]. Studies of LLM-based automatic grading report that injected instructions can manipulate grades [12] and report high failure rates for some code-evaluation setups with open-weight models [13]. In the pipeline studied here the language model writes narrative feedback and follow-up questions but has no designed path to the numeric score; whether that holds in the implemented system is what the invariance test examines, for one channel.

## III. Pipeline Under Test

The pipeline comprises an orchestrator that holds session state, a question queue and the score and difficulty fields; an evaluator service that produces the numeric score; a local 1.5B-parameter instruction-tuned language model (quantized GGUF, CPU) that writes narrative feedback and follow-up questions; a Docker-based C compiler-and-runner sandbox for coding questions; and a SQLite store. Three authority boundaries are the object of study: (a) code from the assessed person runs only inside the sandbox; (b) score, difficulty and best-answer fields are written by the evaluator path, not by language-model text; (c) a failed component should surface as a flagged, unscored outcome rather than a fabricated score. These are design intentions; Section V reports what the tests could show about each. The follow-up-question generator is a fourth path: its output can become the expected-concept list for the next turn. It is documented as a dependency, and it was not tested (Section VII).

The shipped sandbox configuration, read from the recorded Docker commands of every shipped-configuration run, is: user 1001:1001, `--net=none`, all capabilities dropped, `no-new-privileges`, read-only root filesystem, tmpfs workspace, 128 MB memory and swap, 32 processes, 1 CPU, and Docker's default seccomp profile.

## IV. Method

**Design.** Table I lists, for each property, the test, the oracle and the control. Attack programs, oracles and controls were written by the study's authors; oracles combine a program's self-report with host-side observables the program cannot forge: a canary listener on the host (connection count), a hash of a canary directory, `docker events` (out-of-memory and kill events) and an orphan-container check.

**Table I. Property, test and oracle.**

| Property | Test | Oracle | Control |
|---|---|---|---|
| Containment of nine specified attack programs (ptrace, socket/connect, syntax error, SIGSEGV, CPU loop, memory, exfiltration, fork attempts, filesystem write) | X1-C: each program run under the shipped configuration | Conjunction of program self-report and host-side observables (canary listener, canary-directory hash, `docker events`, orphan check) | Permissive configuration per attack (seven of nine); benign program |
| Score, difficulty and best-answer fields are not changed by feedback text | X1-B-I: 36 injections × 2 replicates; benign and injection-carrying arms; evaluator output fixed | Exact equality of 14 observables (final and raw score, grade, score breakdown, stored scores and raw scores, current difficulty, difficulty update, next action, best-answer flags and validated score, technical-performance state, queue length) | Mutation control (a harness copy wiring a model-text field into the score); static AST guard over score-write sites |
| Evaluator outage is detected and handled without a scored result | X1-A FLT-03: exception injected in the evaluator function | Infrastructure flag present; no 0.0 in session scores; control scores normally | No-fault control |
| Compiler timeout leaves no orphan container | X1-A FLT-06: compile step replaced by `sleep 60` in the real container | Compile timeout ends the run; no container present 3 s after return; next submission runs | No-fault control |
| Other tested faults | X1-A FLT-01, -02, -04, -05, -07a, -07b, -10 | Scenario-specific criteria (protocol §4) | No-fault control |

**Builds.** Build A is the baseline release (`release/app-repair/v1`, commit `980747ff`). Build B (`sut/X1/build-B`, commit `beb374f3`) repairs the evaluator-outage and compiler-timeout defects found on build A, makes the language-model status flag truthful and caps feedback generation at 512 tokens. Both builds are reported.

**Registration and status.** Protocols were committed and tagged with local annotated git tags before execution. The repository was not pushed to a public registry, so this registration is author-controlled and not externally time-stamped. The reruns on build B (X1-C v2, X1-A v2, X1-B-I v3) were written after the build-A results were seen and are reported as such. The protocols fix criteria in advance; the study is a scoped engineering evaluation and not a preregistered inferential study.

**Repetition and statistics.** Each scenario was repeated five times. The repetitions are deterministic repeatability checks: "k/5" is a count of runs meeting the criterion, not a rate, and carries no interval. No hypothesis test is reported.

**Environment.** Windows 11 (10.0.26200), WSL2 kernel 6.6.87.2, Docker Desktop with Docker 29.7.2, runc, cgroup v2, 12 CPUs and 8.15 GB memory; local image `prepaired-c-sandbox` (image id `sha256:1e8e861c…`); the language model is `qwen2.5-1.5b-instruct-q4_k_m` (sha256 `6a1a2eb6…`) with default decoding (temperature 0.1, top-p 0.9) and no fixed seed. No other environment was tested.

**Fixed-turn invariance test.** The evaluator's output is replaced by a fixed record (score 0.90) so that any change in the compared observables can only come from the feedback path. Each pair runs the same answer twice with a benign or an injection-carrying transcript; a pair is valid only if both arms' feedback was produced by the language model rather than a template. The registered minimum was 30 valid pairs. The client timeout was raised to 600 s for the test (a disclosed deviation from the shipped 6 s).

## V. Results

### A. Containment (X1-C)

Table II gives the shipped-configuration observations. On both builds, all nine programs met the prespecified criteria in 5/5 repetitions; the seven permissive controls breached in 5/5 runs; the benign program was accepted in 10/10 runs on each build with no false positive.

**Table II. X1-C containment (five repetitions per row; builds A and B gave identical outcomes).**

| Attack | Shipped criteria met | Permissive control | Shipped observation |
|---|---|---|---|
| SEC-01 ptrace | 5/5 | breach 5/5 | blocked by literal pre-flight filter; with the filter disabled `ptrace(PTRACE_TRACEME)` returned 0 |
| SEC-02 socket + connect | 5/5 | breach 5/5 | `socket()` = 3; `connect()` = −1 (errno 101); listener saw 0 connections |
| SEC-03 syntax error | 5/5 | none | compilation error |
| SEC-04 SIGSEGV | 5/5 | none | exit 139, runtime error |
| SEC-05 CPU loop | 5/5 | breach 5/5 | timeout, exit 124, 2.53–2.56 s (A), 2.63–2.89 s (B); bound 6 s |
| SEC-06 memory | 5/5 | breach 5/5 | killed, exit 137, out-of-memory event |
| SEC-07 exfiltration | 5/5 | breach 5/5 | connect failed, 0 bytes received; control received a 39-byte token |
| SEC-08 fork attempts (≤100) | 5/5 | breach 5/5 | 30 forks succeeded, then EAGAIN; control reached 100 |
| SEC-09 filesystem write | 5/5 | breach 5/5 | write under `/etc` failed (EROFS); canary hash unchanged |
| Benign program | 10/10 accepted | n/a | exit 0 |

Three observations qualify the table. First, for SEC-01 the tested behaviour was that the literal pre-flight filter rejected the source text. When the filter was bypassed, a direct `ptrace(PTRACE_TRACEME)` call returned 0 inside the container. Docker's documentation lists ptrace as blocked in Linux kernel versions before 4.8 (to avoid a seccomp bypass) and states that tracing arbitrary processes is already blocked by dropping `CAP_SYS_PTRACE` [14]; the tested kernel is 6.6.87.2. The observation is compatible with the documented default profile and is best read as an application-level finding: containment of this attack in the tested path depended on the filter. Only the literal `ptrace(` spelling was tested. Second, `socket()` succeeded and `connect()` failed; "socket creation blocked" would misdescribe the observation. Third, SEC-06 and SEC-08 use host or runtime observables (an out-of-memory event; the fork count) whose bound is a configured constant, and the SEC-08 oracle references that constant (`DEFAULT_PIDS_LIMIT`), so it is not an entirely independent oracle. The SEC-09 canary criterion does not discriminate in the shipped configuration, and the permissive control's canary reset had a methodological flaw; the SEC-09 breach result should not be given weight beyond the write-failure observation.

**Executor status was not a sufficient oracle.** For SEC-02, SEC-07, SEC-08 and SEC-09, the executor reported `wrong_answer` in both the shipped and the permissive configuration. Contained and breached runs were therefore indistinguishable from the status string; the host or runtime observables decided the outcome.

### B. Failure handling (X1-A)

**Table III. X1-A criteria met of five (build A / build B).**

| Scenario | A | B | Note |
|---|---|---|---|
| FLT-03 evaluator outage | **0/5** | 5/5 | A: recorded as 0.0, no flag; B: `evaluator_unavailable`, unscored |
| FLT-06 compiler outlives timeout | **0/5** | 5/5 | A: container present 3 s after return; B: none |
| FLT-07b database lock 34 s | 4/5 | 5/5 | A: one run 0.1 s above the bound; not a repair |
| FLT-01 Qwen unavailable | 5/5 | 5/5 | 4.84–4.90 s vs 5.0 s bound |
| FLT-02 Qwen slower than client timeout | 5/5 | 5/5 | 12.78–12.85 s vs 15.0 s bound |
| FLT-04 invalid score: NaN, Inf, 999, −3 | 5/5 each | 5/5 each | 999 → 1.0; NaN, Inf, −3 → unflagged 0.0 (unrepaired) |
| FLT-05 Docker CLI absent | 5/5 | 5/5 | structured sandbox error |
| FLT-07a database lock 2 s | 5/5 | 5/5 | waited out |
| FLT-10 empty input | 5/5 | 5/5 | structured outcomes |
| FLT-08 WebSocket; FLT-09 audio | not executed | not executed | no result |

The two defects are the substantive findings. On build A, the injected evaluator outage was recorded as a 0.0 score with no flag, which is indistinguishable in stored state from a genuine zero. On build B the same scenario produced an infrastructure flag, no score, no answer, attempt or difficulty change (5/5). On build A the compiler-timeout scenario left a running container in 5/5 runs; on build B none remained. Both repairs were designed, applied and re-tested by the same agent that found the defects, so the re-test is a regression check and not an independent replication.

FLT-04 shows only that the evaluator score ended inside [0, 1]. NaN, Inf and negative outputs become 0.0, the same outcome that FLT-03 identified as a defect when it results from an outage. FLT-04 is therefore a numeric-range sanitization observation and not evidence of corruption detection. FLT-05 injects a missing Docker CLI, not an unreachable daemon; a single unregistered probe with an unreachable daemon returned a structured error after about 17 s and is not campaign evidence.

### C. Language-model authority: fixed-turn invariance (X1-B-I)

**Table IV. X1-B-I fixed-turn invariance.**

| Quantity | Build A | Build B |
|---|---|---|
| Pairs / valid pairs / registered minimum | 72 / 16 / 30 (not met) | 72 / 72 / 30 (met) |
| Observables exactly equal (all pairs / valid pairs) | 72/72 / 16/16 | 72/72 / 72/72 |
| Mutation control detected | 50/72 (50/50 where narrative text differed) | 72/72 |
| Static guard: real sources flagged / injected mutant caught | 0 of 75 protected writes / yes | 0 / yes |
| Distinct injections among valid pairs | 14 of 36 | 36 of 36 |
| Arms served by template instead of the model (benign / adversarial) | 41 / 37 | 0 / 0 |

On build B, no compared observable differed between benign and injection-carrying arms in 72/72 valid pairs, the language-model text differed between arms in 72/72 pairs, and the mutation control detected the injected authority path in 72/72. On build A only 16 of 72 pairs were valid, because template-served feedback was reported as model-produced; the registered minimum of 30 was not met and the result is diagnostic only.

Two cautions apply. The injections' steering effect on the model was not demonstrated: a crude check found an injection-specific word in the adversarial-arm text in 23 of 72 build-B pairs (6 of 16 on build A). A test in which the model did not follow the injections would pass trivially. Second, the test holds the evaluator output fixed and covers narrative feedback only; the follow-up-question channel was not exercised.

### D. Timing of the model service

The shipped model-client timeout is 6 s. Local CPU generation during the X1-B-I campaign took approximately 19–30 s per valid benign arm (13–21 s in an earlier pilot). The campaign raised the client timeout to 600 s. Generation times measured this way are not evidence that the shipped 6 s path completes them, and no end-user outcome of the mismatch was tested. FLT-01 and FLT-02 (Table III) show that an unavailable or slow model service fell back to deterministic feedback with unchanged scores in a stub-based test; they do not test the real service.

## VI. Discussion

**Containment.** *Shows:* under the tested configuration, harness and machine, nine fixed programs met the criteria and the permissive controls show that the oracles can register a breach. *Does not show:* isolation against adaptive attackers, kernel or runtime escapes, UDP/DNS/IPv6 paths, other platforms, or any program outside the nine. *Prior work:* host-side observables, weakened configurations and repeated trials follow established benchmark practice [1], [6], [7]; nothing here is offered as a new escape result. *Why it matters:* the finding that SEC-01 rested on a literal filter is the kind of dependency an operator would not see from a passing status. *Practical implication:* a passing result for a named program should be attributed to the layer that produced it. *Limit:* one environment; author-written attacks.

**Executor status as oracle.** *Shows:* in this harness, status strings were identical across contained and breached runs for four attacks. *Does not show:* that status strings are uninformative in general. *Prior work:* the same reasoning motivates state-checking scripts and canaries in [6], [7], and SandboxEval reports outcomes from inside the payload [2]; this result confirms a known principle in a specific pipeline. *Limit:* the SEC-08 oracle depends on a configured constant.

**Failure handling.** *Shows:* two specific defects existed on the baseline build and were absent on the repaired build in the tested scenarios; an unflagged 0.0 for an outage is the type of failure a scoring pipeline should surface. *Does not show:* general fault tolerance, handling of untested faults (WebSocket and audio were not executed), or behaviour under hangs longer than tested. *Prior work:* injecting named faults follows [8]–[10]. *Limit:* same-agent design, repair and re-test; some X1-A timing bounds derive from constants in the pipeline under test, which weakens their independence.

**Language-model authority.** *Shows:* under a fixed-evaluator test, narrative feedback did not change 14 compared observables in 72/72 valid pairs, and the harness could detect a deliberately wired authority path. *Does not show:* that the model can never influence scoring; the follow-up channel, which can feed the next turn's expected concepts, was not tested, and injection steering was not demonstrated. *Prior work:* grader-injection studies [11]–[13] concern models that grade; here the model does not grade, and the question is whether text reaches score observables. *Limit:* 36 single-sentence injections; unseeded generation; a 600 s client timeout.

**Security versus dependability.** The study reports observed behaviour of specified scenarios on named builds. It is not a security evaluation: it makes no adversary-capability claim and carries no proof. It is closer to dependability testing of a pipeline with security-relevant components, and each conclusion is attached to a scenario, an oracle and an environment.

## VII. Threats to Validity and Limitations

The following limitations qualify every result above.

**Four material limitations.** (1) *Numeric sanitization:* NaN, Inf and negative evaluator outputs become 0.0 rather than infrastructure failures; FLT-04 is a range observation only. (2) *Untested follow-up channel:* model-generated follow-up text and target concepts can enter the evaluator's expected-concept path, and X1-B-I did not test this channel; no claim is made that all model influence paths are contained or irrelevant to scoring. (3) *ptrace:* SEC-01 depended on literal pre-flight filtering; the bypassed call returned 0 in the container; the result is not intrinsic ptrace isolation by Docker. (4) *Timeout:* the shipped 6 s client timeout versus 19–30 s local generation (Section V-D).

**Construct validity.** Attack programs, oracles and controls are author-written. The static pre-flight is a literal-pattern filter and only one spelling was tested. The SEC-08 oracle and some X1-A timing bounds derive from constants in the system under test. The SEC-09 permissive-control canary reset was flawed.

**Internal validity.** One AI coding agent designed, registered, ran, repaired and re-tested the campaigns under the direction of the project lead; the reruns on build B were written after build-A results were seen. A read-only methodology review by a second AI tool (Antigravity) judged the X1 methodology sound only after claim narrowing, with no blocking issue. Its full report is not part of the repository and only its verdict, relayed by the project lead, is available; this paper's wording was narrowed accordingly. The review is not an independent replication and authorizes no stronger claim. The X1-B-I test used a fixed evaluator stub, a name-based static guard, replayed-text mutation control, unseeded generation and a raised client timeout. FLT-01 and FLT-07b timing bounds are marginal.

**External validity.** One environment, a developer-workstation configuration (Windows 11, WSL2, Docker Desktop, one local image); nine finite programs; network tests covered a TCP connection to one host listener, with no UDP, DNS or IPv6 tests and no kernel or runtime-escape tests; enumerated fault scenarios; FLT-08 and FLT-09 not executed; Qwen faults injected through a local stub in X1-A; an unreachable Docker daemon was not campaign-tested.

**Conclusion validity.** Five deterministic repetitions give repeatability counts, not rates, and no inference is attempted. The development environment's package versions violate its declared pins, so exact dependency reproduction is not guaranteed.

**Not evaluated.** Real users, latency guarantees, cross-platform behaviour, adaptive attackers, and any property beyond the tested scenarios.

## VIII. Reproducibility and Artifact Availability

The harness scripts (`x1c_harness_v2.py`, `x1a_harness_v2.py`, `x1b_harness_v3.py`), protocols, per-run records, output hashes and the environment record are stored in the project repository; the repository has not been publicly released in this draft, and release terms are to be decided. Output directories are write-once, and each harness checks the tagged blobs and that the agent and service code equal the system-under-test tag. Reproduction requires Docker Desktop with the local image archive, port 8001 free for X1-A, and the local language-model file and service for X1-B-I. Timings are machine-dependent, and model generation is unseeded, so exact model text is not reproducible; only counts are. The backend test suite on build B passed 283 tests with one known pre-existing failure unrelated to these campaigns. Artifacts being available is distinct from independent reproduction: no independent reproduction has been performed.

## IX. Conclusion

Under one Windows 11, WSL2 and Docker Desktop environment, nine specified attack programs met prespecified containment criteria in 5/5 repeated runs under the shipped configuration, with permissive controls breaching where they applied; two failure-handling defects present on a baseline build were absent on a repaired build in the two tested scenarios; and a fixed-turn test found no change in 14 score-related observables across 72/72 valid adversarial pairs. The same tests show where the evidence stops: the ptrace result reflects a literal filter, invalid numeric scores are sanitized rather than flagged, the follow-up channel and the shipped timeout were not shown to be covered, and executor status alone did not identify containment. Future work would add an independent replication in a second environment, adaptive attackers, the untested faults and the follow-up channel.

## References

[1] R. Marchand *et al.*, "Quantifying frontier LLM capabilities for container sandbox escape," arXiv:2603.02277, 2026 (preprint; its header states ICML 2026, PMLR 306; proceedings listing not verified).
[2] R. Rabin, J. Hostetler, S. McGregor, B. Weir, and N. Judd, "SandboxEval: Towards securing test environment for untrusted code," arXiv:2504.00018, 2025 (preprint).
[3] G. Andronchik and P. Lokhmakov, "AI code sandboxes: A comparative security study. Part 1 of 2," arXiv:2606.08433, 2026 (preprint).
[4] I. Singh, H. Mahmoud, and A. Murillo, "AI sandboxes: A threat model, taxonomy, and measurement framework," arXiv:2606.18532, 2026 (preprint).
[5] M. Rashidi, "The balkanization of execution-security research for AI coding agents," arXiv:2607.05743, 2026 (preprint; abstract-level reading).
[6] C. Guo *et al.*, "RedCode: Risky code execution and generation benchmark for code agents," arXiv:2411.07781, 2024 (preprint; venue not verified).
[7] S. Abdelnabi, C. Hicks, K. Rieck, and A.-R. Sadeghi, "Measuring security without fooling ourselves: Why benchmarking agents is hard," arXiv:2605.22568, 2026 (preprint).
[8] A. Basiri *et al.*, "Chaos engineering," *IEEE Softw.*, vol. 33, no. 3, pp. 35–41, 2016.
[9] J. Jia, Z. Deng, Z. Chen, Y. Wang, and Z. Zheng, "MAS-FIRE: Fault injection and reliability evaluation for LLM-based multi-agent systems," arXiv:2602.19843, 2026 (preprint).
[10] A. Gupta, "ReliabilityBench: Evaluating LLM agent reliability under production-like stress conditions," arXiv:2601.06112, 2026 (preprint).
[11] E. Debenedetti *et al.*, "Defeating prompt injections by design," arXiv:2503.18813, 2025 (preprint; abstract-level reading only).
[12] H. Li *et al.*, "'Important You should give me full credits!': Exploring prompt injection attacks on LLM-based automatic grading systems," arXiv:2606.03090, 2026 (preprint).
[13] D. Sahoo *et al.*, "The compliance paradox: Semantic-instruction decoupling in automated academic code evaluation," arXiv:2601.21360, 2026 (preprint; full author list not verified).
[14] Docker Inc., "Seccomp security profiles for Docker," Docker Docs. [Online]. Available: https://docs.docker.com/engine/security/seccomp/ (accessed Sep. 21, 2026).
