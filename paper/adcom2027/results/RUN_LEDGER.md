# Run ledger — ADCOM 2027 work

Generated 2026-10-02T06:55:02+00:00; branch `adcom2027/multiagent`; base `cb888f2`; HEAD `a99e11159859bfff6e9b925446802f4d8b5d9570`.

## Tags (local, unpushed; no external timestamp)
- `prereg/ADCOM-E1-E3/v1` -> 53d1bf65dd74; protocol sha256 375a103f35c23cd866769d49c922de70301843e7df9a31a0c6adfa26b7d92b25
- `prereg/ADCOM-E4/v1` -> 28f2c8036919; protocol (with amendment A2) sha256 203e8423080a2a2b9e372460418c6466b5732da96cf0f125e397f01f41a527ab
- `prereg/ADCOM-E5/v1` -> a99e11159859; protocol (with amendments A1-A3) sha256 44afaea535cac663ada509d4b9932169c47d2d558ed1de747966ce41b43a2e25

## Inputs (sha256)
- `research/results/paper2/paper2_evaluator_raw.json`: 8309e5255056e2ae73a04c5d3cb4b2be77e5766029be02834f3a5cacc43774c8
- `research/data/evaluator_benchmark/benchmark_dataset.csv`: 969ce1c999956f61f1367962805852734445894844778df1db77aa636961916c

## Scripts and results (sha256)
- `protocol/PROTOCOL_ADCOM_E1_E3_v1.md`: 44afaea535cac663ada509d4b9932169c47d2d558ed1de747966ce41b43a2e25
- `experiments/analyze_e1.py`: 018ad6c896b7111d00b36a3591aa6d734ce19a44be659044ab0bacf20e0d891f
- `experiments/analyze_e3.py`: b0bd7f3f5eac194d65463447d8245f291044424b345a53724733b0e80cd13046
- `experiments/analyze_e4.py`: c4dee3c9e16a42c647f9816489c32cee68cf802e95e7cbf084b33806069f128a
- `experiments/e1_ablation_faults.py`: 3d3e0052d662acda1242eccd9f5eb509b383d8bcd6f46901d646f090a9b34a41
- `experiments/e2_handoff_cost.py`: a7af76f18162203b4ab6cda909725343664f159ab6fafbdffc7ceb5f5155050a
- `experiments/e3_grounding_probe.py`: 8730b415db33566720075e9aada7ff97cab66a5cc39707b824c5b4039efda18e
- `experiments/e4_strict_contract.py`: 2c8ad5e4fc4d57a72e13ac75449ea1ad996ce7202eb4d1cebd3c84d944c2bbda
- `experiments/e5_circuit_breaker.py`: 015e3b45227292dbcb8ccd9087ba8bb22a4f675c8f9874f60f10185f17f91601
- `experiments/harness.py`: bc17c68520bc9d08c3f8a752b1a85124b7c93c66f84de2932608221aed789bda
- `experiments/trace_state_writes.py`: 2d19c61443fd749219eec29134f345f3dabbf736a7da910eae42c05f5d3baec5
- `results/ENVIRONMENT.txt`: dbd3456fbfc5be17057b91af161e8d8d54a765f2a59db9034eaeaaab4c8737c5
- `results/e1_cells.csv`: c636c7a12cafc95688624c990b1e2203613f83656b827096407b5015ecab6969
- `results/e1_decision_sources.json`: 2523a41d5266c2dd042639b46fd5e0d7900c063df2184a4aef63ae37808ef6d9
- `results/e1_meta.json`: 2add1bb6a2f58c3c623ba3f9d1bf51eb997ed39b3fa02539705aced7c7a7e326
- `results/e1_predictions.csv`: f08f2dd10668c2d93159abdd5408f860b8cd28003a28e42891820e84852ff43e
- `results/e1_reversals_exploratory.csv`: 755644254b7193f42ec2913489a3c7563e2728934ff6fb792bce798d3322071e
- `results/e1_runs.jsonl`: 889bb142814e82cd274ace94af013d01c46a9e9c5253c3b7add9ae550c81cc86
- `results/e2_handoff_cost.json`: ae45222ebd1ba04c873aa9a588082a52ab0077b7665cf5ef18e05ee70cb58c76
- `results/e3_evidence_overlap.json`: ed1a06e1554958b0701df066a4e5a7b7211ead29694de5c174166b576ae36ccf
- `results/e3_grounding.json`: 257ed1f7594e7cd7613dc3fcbb3887eeb6ad63fe89ed12c6a6b2fa7b99874fbe
- `results/e4_cells.csv`: 56472d94ed6d64ded86f673966b270f456bc116834464a7e2ee086025b4a3eac
- `results/e4_f0_identity.json`: 32498ea07f367d5d0f37f3819ac2b7bff70b2a8f9f32ff93d1949a949b9dba0d
- `results/e4_runs.jsonl`: 9d76ca52ded9b42618bda983d46aba14975327d613aa742664ff75b30561a776
- `results/e5_circuit_breaker.json`: 45e503704132d5b885fea4aa166a291c1bfb64ebae787f244328f7f869386d1a
- `results/trace_state_writes.json`: fb0404d5ae505a2400f45864368f0fd670b0bdce79f33b9a6f581b88051f49c2
- `figures/fig1_architecture.pdf`: f4edf20acd32fa2f9fd7d1ba3025cbdae5a3db5fd6418856ce24610df956422b
- `figures/fig2_difficulty_paths.pdf`: 582a67dbe6efc4fb08200d3ee00090df476c068dc4732f0f83bb81e2b4b76ddd
- `figures/make_fig1_architecture.py`: 8f53a296488bb2f90aee8c3ce706cc6982999164b6551dfe6e5b2396069d39ca
- `figures/make_fig2_paths.py`: a1c78ed6ccd39380db89c5f01727d75415a504637a1fbfae586e97a5bbc04d92
- `verification/make_ledger.py`: 3995dd350acae51667366b9a3e940e91fbdba8f23b4c73f3aecc3bdbe56bfd8f
- `verification/make_numbers.py`: f3a5d0e55b24517e579dd2246b5d42934869b8287e3fec3e348e910079a9eb91
- `verification/make_tables.py`: 827607f913c592caba9f4849b1d73b3023535b396564cc1f9e6cf0e976cf7d75
- `verification/verify_adcom.py`: aecf212a9c65ef49bcb138cc766d9accf76c4d490d7effdb344192ce6fbf14bf

## Dated experiment ledger (2026-10-02, one working session)
| id | what | class | outcome |
|---|---|---|---|
| T0 | state-write trace, 8 sessions / 186 turns, run before the protocol | replay, descriptive | evaluator/validator/feedback wrote 0 keys; follow-up 1 key; policy 14; hub commit 22 |
| T1 | existing 7 test files, first run | tests | 2 failures (one needed `python-multipart`, one `test_evaluator_failure_produces_structured_failure_without_fabrication` of unknown cause); two further runs 145 passed. The transient failure is unexplained. |
| H1 | harness bug: follow-up of a follow-up had no recorded answer (retry exhaustion) | harness | fixed before any registered run (root-question lookup); trace re-run |
| S1 | smoke runs of E1, E3, E2 (partial), E4, E5 into a scratch directory | smoke | harness checked; the E1 smoke path of V0/session 0 prompted the exploratory reversal metric (disclosed in amendment A1) |
| E1 | 752 sessions, 18 cells (protocol v1) | replay | 14/14 predictions matched; F2 seeds 0-19 produced 15/160 non-terminating V0 sessions (analytic expectation ~30% per session; seeds 0-19 drew few triple failures; not re-selected) |
| E3 | grounding probe on 64 payloads | constructed | faithful C0 accepted 47/64 (17 payloads have the same string covered and missing); C4 paraphrase accepted 40/57 |
| E4 | strict contract before/after (amendment A2) | replay | predictions (i)-(vi) held |
| E2 | hanging/refusing/healthy server, 24 turns | socket | 24.7 / 0.69 / 0.14 s median; server-side counter disagreed with client attempts (96 vs 80), not investigated |
| E5 | circuit breaker before/after (amendment A3) | socket | predictions (i)-(v) held; P120 equals P60 because cooldown (60 s) has elapsed at every turn |
| R1 | full test suite on the branch vs the cb888f2 snapshot | tests | baseline 23 failed, 306 passed, 36 errors; branch 23 failed, 329 passed, 36 errors; identical failing sets (Docker, faiss/HF not available). One existing test encoded the old None-score behaviour and was updated deliberately |
| X1 | first full-suite attempt used -x and stopped at a missing-faiss error; a second run was killed mid-way after source edits and discarded | tests | not used |
