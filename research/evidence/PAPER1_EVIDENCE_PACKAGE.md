# Paper 1 — Evidence Package (systems / dependability)

Date: 2026-09-20. **Status: the X1-C / X1-B / X1-A campaign was NOT run in this block.** This package therefore documents (a) the evidence that exists (X1-D and the frozen Phase-2 items), (b) the exact campaign scope and oracle definitions to be registered, (c) why the campaign is blocked, (d) claims, limitations and withdrawn claims. No result below was produced or recomputed today; each is copied from the claim registry or stored files.

## 1. Why the campaign was not run (hard gates, none satisfied)
| Required before any new confirmatory Paper 1 run | State on 2026-09-20 |
|---|---|
| Registered, hashed, **git-tagged** protocol for X1-C / X1-B / X1-A | **Absent.** Existing tags: `prereg/X1-D/v1`, `prereg/X2-B/v1`, `prereg/X2-B/v2`, `prereg/X3-A/v1`, `sut/X1/build-A`. X1-C/B/A exist only as designs in `research/audit/X1_PROTOCOL_DRAFT.md` and `PHASE_NEXT_RESEARCH_PLAN.md`. Creating the tags requires a commit of the protocol files, which the user has not requested |
| Minimum infrastructure (`run_manifest_v2.py`) **implemented and independently audited** | Implemented and self-tested on a temporary repository (`research/tools/run_manifest_v2.py --selftest` OK). **Independent (Codex) audit not performed** — no Codex access from this session |
| Protocol / tag / input hashes locked | Not applicable until a protocol is registered |
| SUT binding | Tag `sut/X1/build-A` exists (build A); an X1-C/B protocol must bind the sandbox image digest and the harness |
| Known failing-test decision recorded | Root cause triaged statically (`test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics`: commit `b7cad49` changed observation dimension 4 to turn progress; probable stale test expectation; developer intent unconfirmed). **No decision by the user is recorded** |
| Independent review of the corrected X1 designs (ChatGPT/Sparsh) | Not recorded |

Per the stop rules ("do not improvise around a failed gate"), no X1 experiment, dry run of an attack against the sandbox, or fault injection was executed.

## 2. Evidence that exists (registry; unchanged)
| ID | Statement | Scope / limit |
|---|---|---|
| X1D-C001 | Full test suite at SUT build A (`EVALUATOR_MOCK_MODE=1`, no early stop): 226 tests, 1 failure, 0 errors, 0 skipped; the failing test is the one named above | Single machine; unlocked SUT environment |
| X1D-C002 | **Warm evaluator latency** (in-process, N=100 after one cold request): median 236.129 ms [221.447, 252.454], P95 615.425 ms [448.037, 692.09], P99 803.826 ms; cold first request 3787.4 ms; asset load 1563.2 ms | **Not end-to-end interview latency.** Evaluator-only, warm, in-process; excludes STT, LLM feedback, network and UI |
| X1D-C003 | Uncontended single-writer SQLite `save_attempt`: median 12.697 ms [12.15, 13.124], P95 17.06 ms [16.081, 17.885] | Not a concurrency figure |
| P1-C001 | Earlier evaluator latency (n=20): median 404.6 ms, P95 2098.6 ms, P99 26369.4 ms; mean dominated by a cold-start-scale outlier | Raw values not stored; cold/warm not separable |
| P1-C002 | Concurrency benchmark 1/5/10/25 threads with **synthetic** database operations: 0 lock errors, 0 isolation violations; mean per-operation latency 16.3 ms → 419.5 ms | No evaluator/LLM in the loop; one machine |
| P1-C003 | Nine attack programs executed; four outcomes discriminate (SEC-01/03/04/05); five do not identify which control acted | Outcome-level only; no weakened-configuration control |
| P1-C009 | Sandbox configuration: non-root, `--net=none`, `--cap-drop=ALL`, `--read-only`, `no-new-privileges`, memory/PID limits | **DESIGN-ONLY — effectiveness not measured** |

Latency terminology (retained correction): "warm evaluator latency" ≠ "end-to-end interview latency". No end-to-end number exists for this SUT. The word "sub-second" must not be applied to the system.

## 3. Campaign scope to register (design only; not executed)
- **X1-C (containment):** nine discriminating attacks × {intact configuration, one predefined weakened configuration (one documented flag change), benign control} × 5 repetitions. Four oracle layers, none sufficient alone: (1) static pre-flight (policy check of the source and configuration); (2) actual sandbox execution outcome; (3) observed runtime containment (program self-report cross-checked with `docker events` and container inspection); (4) observed host/system side effects (canary files, listeners, orphan-container listing, resource counters). The executor's PASS/FAIL string is never the sole oracle. The weakened configuration uses the same attacks and the same oracle so that the oracle demonstrably *can* fail. Record per run: execution result, containment, status, host impact, resource impact, orphan containers.
- **X1-B (authority separation), two separate experiments:** B1 fixed-answer invariance (same candidate answer; only LLM-facing context varies; exact invariance of score, difficulty and ranking is the outcome); B2 behavioural stress (candidate answer may vary; structural constraints only). Prerequisite: an enumeration of every channel through which LLM text or output can reach scoring/control code.
- **X1-A (fault campaign):** only fault classes corresponding to retained claims; no-fault control; controlled mutant/fault; observed behaviour; recovery/fallback; propagation outcome. Not enlarged to increase N.

**Closest prior work and what it rules out** (see `research/literature/SECOND_PASS_CLAIM_AUDIT.md`): SandboxEval (2025 preprint) already reports an uncontained comparison and outcome-based test categories → "negative control is new" is abandoned; APAC (2015) already uses Docker for assignment grading; grader-hijacking papers (Cai 2026; Li 2026; Sahoo 2026) treat the LLM as scorer.

## 4. Claim-per-evidence table
| Claim | Allowed today? | Evidence |
|---|---|---|
| The full suite at build A has 226 tests with one known failure | Yes | X1D-C001 |
| Warm evaluator latency (in-process) median ≈ 0.24 s, P95 ≈ 0.62 s | Yes, with the "not end-to-end" qualifier | X1D-C002 |
| SQLite single-writer save latency ≈ 13 ms median | Yes | X1D-C003 |
| Synthetic-DB concurrency showed no lock errors up to 25 threads | Yes, with scope | P1-C002 |
| Four of nine attack outcomes discriminate; sandbox effectiveness is unmeasured | Yes | P1-C003, P1-C009 |
| The sandbox contains attacks / is secure / isolated | **No** | needs X1-C |
| The LLM cannot alter scoring or difficulty | **No** | needs X1-B and channel enumeration |
| The system tolerates/recovers from faults | **No** | needs X1-A; P1-C004 withdrawn |

## 5. Known limitations
Single machine; unlocked SUT environment (`.venv` violates pins: numpy 2.5.2, torch 2.11.0, accelerate 1.13.0); the local LLM (Qwen 2.5 1.5B, Q4_K_M) and Docker were not part of X1-D; concurrency test used synthetic operations; one failing test unresolved; legacy harness weaknesses (non-atomic run-once, trusted protocol dict, no key-set assertions, X1-D manifest with `inputs: []`) are documented in `CODEX_FINDINGS_VALIDATION.md` and are the reason `run_manifest_v2.py` exists.

## 6. Withdrawn claims (registry)
P1-C004 (10/10 fault scenarios recovered), P1-C005 (5/5 Qwen boundary tests / zero authority), P1-C006 (9/9 attack vectors contained), P1-C007 (213 tests passed), P1-C008 ("secure" framing), P1-C010 (prosody 100 % insulated from scoring).

## 7. Do not claim
Fully secure; 100 % isolated; fault-tolerant in the general sense; universal container security; sub-second end-to-end latency; prompt-injection-proof; VM-grade isolation; multimodal/video capability; that Docker-based assessment or interview-practice systems are new.

## 8. Next exact actions (require user decisions)
1. Decide the known failing test (fix expectation / leave / other) and record it.
2. Approve registration of X1-C, X1-B (B1 and B2 separately) and X1-A protocols (files, hashes, tag names) — a commit + annotated tags.
3. Have `run_manifest_v2.py` audited independently (Codex), then bind SUT build A and the sandbox image digest.
4. Read SandboxEval to completion before finalising the X1-C oracle wording.
