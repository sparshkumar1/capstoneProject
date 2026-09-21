# P1 INDEPENDENT AUDIT (2026-09-21, audit-v2 pass)

Scope: `paper1/manuscript_v1_archive.md` (audited) → `paper1/manuscript.md` (v2, corrected). Evidence re-read for this audit: `research/confirmatory/X1/results/x1c/` and `x1c_v2/` (`results.csv`, `runs.jsonl`, `environment_and_verdicts.json`), `X1C_RESULT_NOTE.md`, `PROTOCOL_X1-C.md`, `PROTOCOL_X1-C_v2.md`, `PROTOCOL_X1-B_v3.md`, `evidence/final/DEFECT_DECISIONS_FLT03_FLT06.md`, `evidence/final/manuscript/paper1/FINAL_REPRODUCIBILITY.md`, `evidence/final/PAPER1_FINAL_CLAIM_MATRIX.md`, git tag list. No experiment, build or frozen file was touched.

## 1. New findings from independent re-reading (not in the previous audit)

| ID | Finding | Evidence | Action |
|---|---|---|---|
| P1-F1 | **SEC-05 (CPU loop) also had identical executor status in shipped and permissive runs (`timeout` in both, exit 124).** The frozen note `X1C_RESULT_NOTE.md` line 28 says the status differed by outcome for SEC-01 and SEC-03–06; the per-run data show it differed only for SEC-01 (`policy_blocked` vs `wrong_answer`) and SEC-06 (`memory_limit` vs `wrong_answer`). The locked claim (P1-C3: SEC-02/07/08/09) is not wrong but is incomplete. | `x1c/results.csv` and `x1c_v2/results.csv`: SEC-05 shipped `timeout`×5, permissive `timeout`×5 | Manuscript v2 keeps "four attacks" as the locked claim and states that for SEC-05 the status was `timeout` in both and execution time separated them (Section V-A; Fig. 1). **Frozen note not edited.** Author decision D-1: whether to promote the count to five. |
| P1-F2 | SEC-05 times in v1 ("2.53–2.56 s (A), 2.63–2.89 s (B)") are the `exec_ms` execution-time field, not `wall_s` (3.63–4.65 s for the whole call). v1 did not say which. | `runs.jsonl` `obs.exec_ms` 2843.0 vs `obs.wall_s` 4.644 | v2 labels it "execution time" and adds "Execution times are measurements on this machine and are not latency claims." |
| P1-F3 | v1 used "Build A / Build B". The record defines A = baseline SUT `release/app-repair/v1`; a **different** tag `sut/X1/build-A` exists (X1-D scope) and is not the baseline. | `PROTOCOL_X1-C.md` line 12; `FINAL_REPRODUCIBILITY.md` line 2; `git tag -l` | v2 uses "baseline SUT" / "repaired SUT" throughout, gives the tags once, and states the legacy tag is not the baseline. |
| P1-F4 | v1 abstract said "nine attack programs met criteria in 5/5 runs … while permissive controls breached in 5/5 runs where a control applied" in one clause. The nine (shipped), seven (permissive) and ten (benign) denominators were not separated. | manuscript v1 abstract | v2 abstract and Section V-A give 9 shipped, 7 permissive, benign 10/10 separately. |
| P1-F5 | v1 listed "best-answer flags and validated score" as an observable. `validated_score` is a storage field name, not a validation claim. | field name in `X1B` harness | v2: "the stored best-answer score field". |
| P1-F6 | v1 described the second-AI-tool review in the Internal-validity paragraph in a way that could be read as external corroboration. | v1 Section VII | v2: "no result or claim in this paper relies on it"; the report is not in the repository. |
| P1-F7 | v1 said "registered" in several places. Tags are local and unpushed. | tag list; `FINAL_REPRODUCIBILITY.md` | v2 uses "pre-specified" and "committed and tagged before execution; tags not pushed; author-controlled". |
| P1-F8 | SEC-01 permissive control detail: the permissive run's executor status was `wrong_answer` (the program ran and the call returned 0); manuscript says this only via "returned 0". | `results.csv` SEC-01 | unchanged; consistent. |

## 2. The 20 audit questions

| # | Question | Answer after audit | Where fixed / stated |
|---|---|---|---|
| 1 | Does each statement follow from exact evidence? | Yes after F1–F7 corrections. All numbers re-traced (numeric check: 0 unmatched). | throughout |
| 2 | Environment scope explicit? | Yes: abstract, Section IV, VII. | IV Environment |
| 3 | Threat model explicit? | It was implicit. Added "Threat model and scope" paragraph. | III |
| 4 | Oracle independent of executor self-report? | Yes for the containment criteria (host observables + self-report conjunction); SEC-08 references a configured constant (disclosed); SEC-03/04 rely on status (no permissive control). | IV, V-A |
| 5 | Wording implies Docker/kernel isolation? | v1 did not, but "shipped sandbox configuration" could be read that way. v2 attributes each result to a layer (Table II) and never attributes ptrace to Docker. | III, V-A |
| 6 | "Containment" application-level or sandbox-level? | Both, by attack; defined in the scope paragraph. SEC-01 is application-level; SEC-02/05/06/07/08/09 correspond to configured container settings (per the permissive control). | III, Table II |
| 7 | Applicable to all nine or only some? | Nine shipped; permissive controls exist for seven (SEC-03, SEC-04 have none). | abstract, V-A |
| 8 | Permissive results only where controls existed? | Yes; Fig. 1 marks "no control". | Fig. 1 |
| 9 | Qwen result fixed-turn only? | Yes; "matched pairs", "fixed-turn" used; sentence in bold that follow-up channel was not tested. | V-C, VII |
| 10 | Untested channels excluded? | Follow-up channel, UDP/DNS/IPv6, kernel escapes, unreachable daemon, WebSocket, audio. | III, VII |
| 11 | Repeat runs = repeatability not sampling? | Yes; "k/5 counts runs, not a rate". | I, IV |
| 12 | Same-agent bias disclosed? | Yes, twice (V-B, VII) plus AI-use disclosure. | V-B, VII, VIII |
| 13 | FLT-08/09 visible? | Yes: Table III row, V-B text, VII. | Table III |
| 14 | Build A/B labels interpreted correctly? | Fixed (F3). | IV |
| 15 | Legacy tag described as baseline? | No; explicit statement it is not. | IV |
| 16 | Timing numbers as general latency? | No; explicit non-latency sentence (F2) and 6 s vs 19–30 s stated as a mismatch, not a latency result. | V-A, V-D |
| 17 | "validated score" turned into a claim? | Renamed (F5). | Table I |
| 18 | Antigravity review treated as external evidence? | No (F6). | VII |
| 19 | "Registered" precise? | Fixed (F7). | IV |
| 20 | Qwen scoring-authority claims too strong? | The paper claims only equality of 14 measured observables across 72 valid matched pairs under the fixed-turn perturbation. | V-C, VI |

## 3. Mandatory language checks

| Requirement | Status |
|---|---|
| Distinguish nine shipped / permissive where applicable / benign | Done (abstract, V-A, Fig. 1) |
| "Measured evaluator observables were unchanged across the 72 valid matched pairs under the tested fixed-turn perturbation" and immediate statement that follow-up channel was not tested | Done, V-C (bold sentence follows directly) |
| Never "Docker prevented ptrace"; explain literal filter and bypass | Done, V-A "ptrace" paragraph |
| Oracle statement per insufficient-status attack | Done, Table II + V-A (SEC-02/07: canary listener; SEC-08: fork count vs limit; SEC-09: write errno and canary hash with caveat; SEC-05: execution time) |
| "baseline SUT" / "repaired SUT" | Done |

## 4. Reviewer 2 / Reviewer 3 second attack (Phase 14, Paper 1)

| Attack | Exact manuscript sentence that answers it | Survives? | Final safe wording / action |
|---|---|---|---|
| "Your ptrace result is a preflight filter, not Docker security." | "It is therefore not evidence of kernel-level ptrace containment, and this paper does not attribute the SEC-01 outcome to Docker." (V-A) | Yes | unchanged |
| "Executor status can say wrong_answer even when the attack succeeds." | "The executor reported `wrong_answer` in both the shipped and permissive configuration for SEC-02, SEC-07, SEC-08 and SEC-09 …; the observables in Table II decided them." (V-A) | Yes; this is a finding of the paper | unchanged |
| "Only one Windows/WSL2/Docker environment." | "No other environment was tested." (IV) and VII external validity | Survives as a stated limitation | unchanged |
| "The same agent designed and repaired the system." | "Both repairs were designed, applied and re-tested by the same AI coding agent that found the defects, so the re-test is a regression check and not an independent replication." (V-B) | Survives as stated | unchanged |
| "Qwen follow-up generation can still affect evaluator inputs." | "**The downstream follow-up-question generation channel was not tested.**" (V-C); limitation (2) | Yes | unchanged |
| "Five identical reruns are not evidence." | "k/5 counts runs meeting a criterion and is not a rate" (IV); "deterministic repeatability checks" (I) | Yes | unchanged |
| "Attacks are your own." | "Attack programs, controls and oracles were written by the study's authors." (IV) | Stated | unchanged |

## 5. Conclusion audit (Phase 13)

| Conclusion sentence | Where established |
|---|---|
| "nine fixed attack programs met prespecified criteria in 5/5 runs under the shipped configuration, and the seven permissive controls breached in 5/5 runs" | V-A, Fig. 1 |
| "Executor status alone did not identify containment for four attacks." | V-A oracle paragraph |
| "The ptrace result reflects a literal pre-flight filter." | V-A ptrace paragraph |
| "Two failure-handling defects on the baseline system were absent on the repaired system in the two tested scenarios." | V-B, Table III |
| "14 measured evaluator observables were unchanged across 72/72 valid matched pairs" | V-C, Table IV |
| "the follow-up channel and the shipped timeout were not shown to be covered" | V-C, V-D |
| No new result, literature or future evidence is introduced (future work sentence from v1 removed). | — |

## 6. Verdict
**YELLOW.** Scientifically consistent with the frozen record after the corrections above, pending: author decision D-1 (five vs four status-indistinguishable attacks), the AI-use disclosure decision, the template port, and the page-length result of the port. No RED items.
