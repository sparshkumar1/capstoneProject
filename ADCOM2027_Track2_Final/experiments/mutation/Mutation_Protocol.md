# Protocol: MA-MUT v2 — test-adequacy (mutation) analysis of the bounded-authority layer

Status: written and hashed BEFORE any mutant was executed. Exploratory test-adequacy analysis. It changes no result of
XA-XD and runs only on a scratch export of branch `origin/paper/adcom2027-v13`, never on the working repository.

Amendment note (v1 -> v2, before any mutant ran): v1 specified orchestrator-level replay oracles. The first baseline attempt
showed that the flag-gated hooks of `agents/orchestrator/interview_orchestrator.py` used by XA-XD are not present in any ref of
this repository (the stored XA-XD results carry a commit from a local branch that is not in the repo). v1 therefore could not
produce a valid baseline and no mutant was executed under it. v2 moves the oracles to the coordinator interface, which is
fully present. Consequence: v2 does not re-execute XA-XD; it tests the same safeguards one level lower.

## Question
Do the available checks (unit/property suite, coordinator-level fault and property oracles, differential/golden oracles) detect
single-point defects injected into the authority, validation, arbitration and guardrail code of `agents/multiagent/`?

## Subject
`agents/multiagent/{authority,arbitration,coordinator,grounding,contracts,coaching_render}.py` at the exported commit.
One mutant = one textual replacement of one expression, listed in `run_mutation_testing.py::MUTANTS` (21 mutants).

## Oracles (a mutant is KILLED if any oracle fails; every failing oracle is recorded)
- O1 unit/property suite: `paper/adcom2027_final_v13_candidate/tests/test_coordination_and_specialization.py` (18 tests).
- O2 coordinator-level property oracle (`oracle_coordinator.py`): the 64 recorded evaluator payloads (8 clusters x 8 questions,
  recorded order) are turned into `TurnObservation`s and driven through a real `AgentCoordinator` with the real
  Strategy/Coaching agents, a stub base action (Harder if score>=0.7, Easier if <0.4, else Same) and the canonical guardrail
  module `rl/guardrails.py`. Scenarios: nominal; the 11 XB fault kinds (fault rate 0.3, seed 31*k); crash at rate 1.0 (breaker);
  duplicate answer for one state version; infrastructure failure on one turn. Initial level in {1,3,5}. Independent
  re-implemented properties, checked per turn: P1 level in [1,5] and |delta|<=1; P2 an output on a fault-injected call whose
  kind is structurally invalid (crash, timeout, malformed, forbidden_key, stale, nan_confidence) is never accepted; P3 the final
  action is not one the guardrail layer would override (bypass); P4 an accepted coaching plan emphasises only concepts present
  in the turn's evidence; P5 a probe is never injected when consecutive follow-ups >= 2; P6 an infrastructure-failure turn
  yields Same; P7 a second answer from the same agent for the same state version is rejected; P8 after two consecutive crashes
  the third call is rejected as breaker_open; P9 the coordinator raises no exception.
- O3 classification oracle (differential): per scenario, the multiset of (decision, proposer, status, reason_code) records must
  equal that of the unmutated run. Detects mutants that stay contained but change the detection mechanism.
- O4 nominal golden oracle: SHA-256 of the fault-free trajectories (levels, final actions, reason codes) must equal the
  unmutated run's.

## Pre-declared analysis
- The unmutated baseline must pass O1 and O2 (no property violation, no harness error); otherwise the run is invalid.
- Report per mutant: killed/survived and the killing oracle(s). Mutation score = killed / total; also reported excluding
  survivors judged equivalent. Survivors are inspected manually and labelled EQUIVALENT-UNDER-CORPUS (no input of the corpus
  or scenario set reaches the changed behaviour) or UNDETECTED (a real gap); labels are justified individually.
- No mutant is added, removed or edited after the first run; changes need a new protocol version.
- Limits: not formal verification; 21 hand-written mutants; one corpus; the oracles share a code base and an author with the
  system under test; O3/O4 are differential against the same code and therefore detect change, not correctness.

Amendment note 2 (v2, still before any mutant ran): the first pristine-baseline run flagged P3 for every scenario because the
oracle treated "a guardrail rule fires" as an override. P3 now means the guardrail layer would CHANGE the final action
(same definition as the XB harness). Only the pristine baseline had been executed at that point; no mutant had run.
Also: `agents/orchestrator/circuit_breaker.py` is absent from the repository; a reconstructed stand-in
(`circuit_breaker_standin.py`, interface inferred from its use) is placed in the scratch export only. Mutant MU15 therefore
tests the coordinator's use of the breaker, not the breaker implementation.
