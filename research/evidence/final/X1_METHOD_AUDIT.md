# X1 methodology audit (self-audit before treating X1 as publication evidence) — 2026-09-20

**Who audited.** The same executing agent (Claude) that wrote the X1-A/B/C protocols and harnesses re-read all three protocols, the three harnesses, the frozen result notes and the SUT code paths they touch. **This is a self-audit, not an independent review.** It removes some errors and lists the rest; it does not replace the independent (human or Codex/Antigravity) review, which is still outstanding. Ratings: **PASS**, **LIMITATION** (true, must be stated, does not invalidate the scoped claim), **HIGH RISK** (could mislead if worded loosely), **BLOCKER** (the registered claim cannot be made). Nothing here changes a registered parameter.

## 0. Cross-cutting findings (all three protocols)
| # | Finding | Rating |
|---|---|---|
| G1 | **Author = executor = registrant.** One agent wrote the attack fixtures, the oracles, the controls and the pass/fail rules, then ran them. Host-side observables (listener, canary-directory hash, `docker events`, `docker ps`) reduce, but do not remove, circularity. | HIGH RISK → stated limitation; independent review pending |
| G2 | **"Preregistered" is too strong for X1.** The protocols were committed and tagged locally before execution; the repository was never pushed, the tags are author-controlled and carry no third-party timestamp. Correct wording: "protocol committed and tagged before execution (local, unpushed)". The same caveat applies to `prereg/X3-A-O7/v1` (registered before O7 was run, but not externally timestamped). | HIGH RISK (wording) |
| G3 | X1 protocols were written after the SUT and after the author had seen the code (no blind design). SLAs and bounds were derived from SUT constants, not from independent requirements. | LIMITATION |
| G4 | Replicates are deterministic re-runs (flakiness check), not independent samples. No confidence interval is reported and none should be. "5/5" is a repeatability count, not a rate estimate. | PASS (already stated) |
| G5 | Environment binding is recorded (OS, Docker client/server, kernel, cgroup, image id, gcc, executor file hashes; git tags). The sandbox image is a local build (`prepaired-c-sandbox.tar` in the repo root, not rebuilt from a recipe in the campaign), so image reproducibility depends on that archive. | PASS / LIMITATION |
| G6 | One machine, one Docker Desktop (WSL2) install, no concurrency, in-process injection for X1-A. | LIMITATION |

## 1. X1-C (containment)
| Criterion | Finding | Rating |
|---|---|---|
| A Construct | Nets/memory/pids/timeout/read-only: the container controls are what stop these, and the criteria observe the effect (connect refused, listener sees nothing, OOM kill, EAGAIN, EROFS). Valid for the tested programs. **SEC-01 tests only the literal string `ptrace(`** — the pre-flight regex (`\bptrace\s*\(`) is a pattern filter; `syscall(SYS_ptrace, …)` or macro-obscured spellings were not tried, and the container itself does not block `PTRACE_TRACEME` (returned 0). "ptrace is contained" is not supported; "the pre-flight blocks the literal call" is. | SEC-01: HIGH RISK (wording); others PASS |
| B Oracle validity | Each oracle is a conjunction of program self-report (attacker-written, so only trustworthy for these fixtures) and host-side observations. Could an oracle pass while the property fails? **SEC-09 `canary_write_refused` is not discriminating in the shipped configuration**: `/canary` is not mounted, so `fopen` fails with ENOENT regardless of read-only. Only `/etc` EROFS is informative there; the canary-hash check matters only in the permissive control. **SEC-08 `below_pids_limit` uses `ce.DEFAULT_PIDS_LIMIT`**, i.e. the criterion moves with the configured constant (circular). | LIMITATION |
| C Control validity | Permissive controls breached in 5/5 where they apply; benign cross-oracle produced 0 false positives. Controls are called "single change" in the note; strictly, SEC-02/07 remove `--net=none` **and** add an `--add-host` alias, and SEC-09 removes `--read-only` **and** adds a bind mount. The wording "single change" should read "one control family, one or two flags". | LIMITATION (doc) |
| D Positive control | Present for SEC-01, 02, 05–09 (breach observed). **SEC-03 and SEC-04 have no permissive control** (only the benign negative control), so their oracles are validated in one direction only. | LIMITATION |
| E Sampling | 5 deterministic repetitions; nine programs. The attack set is finite and chosen by the author; results say nothing about other programs. | PASS as a repeatability check; LIMITATION for coverage |
| F Independence | Same author defined attack, expected outcome and pass/fail. See G1. | HIGH RISK → limitation |
| G Leakage/circularity | SEC-05 bound (6 s) was set from benign fixtures; SEC-08 uses the SUT constant (above). No oracle uses information unavailable to a reader of the artifacts. | LIMITATION |
| H Environment | Recorded. | PASS |
| I Reproducibility | Harness at tag, write-once output, per-run docker command lines stored; needs the local image archive and Docker Desktop. | PASS / LIMITATION |
| J Claim scope | Supported: "on one Docker Desktop (WSL2) machine, for nine specified programs, the shipped configuration met the pre-specified criteria in 5/5 runs each and the permissive controls produced the breach". Not supported: secure, isolated, ptrace contained, any statement about other programs, UDP/DNS/IPv6, kernel escapes; **status strings do not discriminate contained from breached for SEC-02/07/08/09**. | PASS with the wording constraints above |

**Verdict X1-C:** no methodological blocker for the narrow claim. The existing evidence supports it as written (with G1/G2). A rerun is needed **only** because the executor changed (build B, FLT-06 repair): the old result belongs to build A. No harness change is proposed; the harness is re-registered unchanged except for tags/paths.

## 2. X1-A (fault injection)
| Criterion | Finding | Rating |
|---|---|---|
| A Construct | FLT-01/02 (Qwen down/slow) valid for the client path against a **local stub**, not the real service. FLT-03 injects an exception in `_evaluator_fn`, which `_evaluate_verbal` catches — the same branch as a real evaluator outage (a `None` return or an exception); a >180 s hang was not tested. **FLT-05 is labelled "Docker daemon unreachable" but the injection makes the docker/wsl CLIs *not found* (`shutil.which` → `None`)**; a present-but-unresponsive daemon (which goes through `_resolve_docker_prefix`'s 5 s / 15 s probes) was not tested. FLT-06 replaces the compile command with `sleep 60` in the real container — valid for a hung compiler. | FLT-05: HIGH RISK (wording → "Docker CLI unavailable"); others PASS |
| B Oracle validity | FLT-04's oracle (finite, in [0, 1]) is satisfied by silently turning NaN/Inf/−3 into **0.0**; passing it does **not** mean the invalid score was handled correctly, only range-sanitised. FLT-03's oracle inspects in-memory session state, not persisted rows (the harness has no candidate id), so it cannot show whether a database attempt was written. FLT-10's `control_scores_normally` is a tautology (`== [0.9] or bool(...)`). | FLT-04: HIGH RISK (wording); FLT-03 persistence: LIMITATION; FLT-10: minor |
| C Control validity | Oracle-**perturbation** controls (a synthetic bad observation must be rejected) test the oracle only; they are not mutant builds of the SUT. | LIMITATION |
| D Positive control | The strongest evidence that the harness can detect a real fault is that it **did**: FLT-03 and FLT-06 failed against the real SUT and the diagnosis (code path) matched the observation. FLT-07b failed on a timing bound that turned out too tight. | PASS |
| E Sampling | 5 deterministic repetitions per scenario; unit of analysis is the scenario. | PASS (stated) |
| F Independence | Criteria and SLAs were written by the same agent that ran the campaign; FLT-01's 5.0 s SLA left a 0.10–0.16 s margin (4.84–4.90 s), so a slower machine could flip it. FLT-07b's 33.0 s bound sat 0.0–0.4 s from the measured distribution (32.58–33.09 s). | LIMITATION |
| G Leakage | The FLT-03 infra-flag criterion is a requirement the author added, but it matches documented intent elsewhere in the repository (earlier Paper 1 study text: "free retry allowed; turn not counted against candidate"). The orchestrator already produced an explicit `evaluator_unavailable` state and lost it downstream. | PASS (finding valid) |
| H/I | Recorded; harness at tag; write-once. | PASS |
| J Claim scope | Supportable: "failure-aware". Not: "fault-tolerant" (FLT-03/06 failed on build A; FLT-08/09 not executed). No claim for WebSocket or audio faults. | PASS with constraints |

**Verdict X1-A:** the two defects are real and material to Paper 1 (see `DEFECT_DECISIONS_FLT03_FLT06.md`). The build-A evidence remains valid as the record of build A. A rerun on build B is required; the harness is kept **unchanged** (including the 33.0 s bound and the 5.0 s SLA) so that old-vs-new is a like-for-like comparison. Known weaknesses above are carried as limitations rather than repaired post hoc.

## 3. X1-B-I (Qwen fixed-answer invariance)
| Criterion | Finding | Rating |
|---|---|---|
| A Construct | With the evaluator fixed at 0.90, the experiment asks whether LLM-authored text reaches score/difficulty/best-answer observables. **It does not test adversarial pressure**: re-reading the frozen pairs, an injection-specific word appears in the adversarial LLM text (and not the benign) in only 6 of the 16 valid pairs, mostly generic words ("answer", "should", "marks"); the "text changed in 72/72" manipulation check is confounded because the deterministic template echoes the candidate text. The 16 valid pairs cover 14 of the 36 injections. "Adversarially steered" must not be written. | HIGH RISK (wording) |
| B Oracle validity | Exact equality over 14 named observables. Anything not in the list (question selection beyond queue length, RL inputs other than `technical_performance`, the final report) is unobserved. | LIMITATION |
| C Control validity | Static guard is **name-based** (substring taint list) and scanned four files, not `apps/backend/main.py`; indirect flows through neutral names would be missed. Its injected mutant was caught. | LIMITATION |
| D Positive control | Dynamic mutant (`narrative_feedback` → score): detected in 50/72 pairs. Re-analysis of the frozen data: **50/50 among pairs whose `narrative_feedback` differs between arms, 0/22 among pairs where it is identical** — the mutant reads only that field, so the earlier "not analysed" 22 are explained and the control is fully sensitive where it can be. (The mutant arms replay recorded LLM output, so this tests the comparator, not the live pipeline.) | PASS (re-analysis, descriptive, frozen data untouched) |
| E Sampling | 72 pairs attempted, **16 valid**; the registered minimum of 30 is unmet. Replicates of one injection are not independent draws of "prompts". | **BLOCKER for the registered claim**; the result is diagnostic only |
| F Independence | Same author; fixed-stub design isolates the LLM path but by construction cannot show influence through the evaluator. | LIMITATION |
| G Leakage | None found. Validity uses the decision source, not the mislabelled `llm_status`. | PASS |
| H Environment | Model file hash, decoding parameters recorded; sampling unseeded; client timeout raised 6 s → 600 s (registered deviation). | PASS / LIMITATION |
| I Reproducibility | Prompt set and harness at tag; unseeded generation means exact text cannot be reproduced, only the statistics. | LIMITATION |
| J Claim scope | Supported only as in `X1B_RESULT_NOTE.md`. **Follow-up generation is a real channel** (Qwen text/`target_concepts` become the question and expected concepts used by the evaluator) and is outside B1. | PASS with constraints |

**Verdict X1-B-I:** the run stands as an under-powered diagnostic. The sample-size shortfall came from SUT defects (truncated JSON, mislabelled status), not from the design. Repair and rerun as a **new registered revision (v3)** with the same design and validity rule; the original result and the aborted v1 log stay as they are.

## 4. What the current evidence can support, per experiment
- **X1-C:** the narrow containment statement above (build A). Rerun on build B for the paper's build.
- **X1-A:** "failure-aware" with named defects (build A); after the rerun, the build-B result decides whether the defects are closed.
- **X1-B-I:** a diagnostic invariance observation, not the registered test.

## 5. Not audited / still owed
Independent review by a person or a separate tool; FLT-08/09; B2; any adversarial-effectiveness measurement of the injections; a real-daemon-unreachable scenario for Docker.

## 6. Addendum — exploratory probe of the FLT-05 wording gap (unregistered; single run; not evidence for any claim)
After the audit above, one unregistered probe was run to see what the FLT-05 wording gap hides: the Docker CLI present but the daemon unreachable (`DOCKER_HOST=tcp://127.0.0.1:1`, real `DockerCSandbox`, build B, run while the Qwen service was busy with the X1-B v3 campaign). The executor returned a structured `sandbox_error` ("Docker sandbox daemon is unreachable. Untrusted code execution blocked to protect host."), `passed = False`, no code executed — the failure mode is safe — but it took **16.85 s**, against the 2.0 s SLA used for the CLI-not-found scenario in X1-A, because the executor's daemon probes wait for their own timeouts (5 s and 15 s constants in `_resolve_docker_prefix`). So "Docker outage handled in ~0 s" holds only for the CLI-absent injection; for an unresponsive daemon the candidate waits on the order of 17 s before a structured error. Single run, loaded machine, not repeated: report as a limitation/observation, not as a measured latency.
