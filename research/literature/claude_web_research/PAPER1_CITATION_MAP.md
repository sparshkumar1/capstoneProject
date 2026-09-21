# Paper 1 citation map: planned claim -> supporting -> challenging -> wording

Wordings are the matrix's scoped wordings; nothing here overrides `PAPER1_FINAL_CLAIM_MATRIX.md`.

| Planned claim | Supporting source(s) | Challenging source(s) | Recommended wording |
|---|---|---|---|
| Nine attack programs were contained under the tested harness | [6] SandboxEval (test-suite approach) | [1] SandboxEscapeBench; [2] comparative study | "...under a predefined harness with fixed, non-adaptive programs on one machine" |
| Containers are a common but contested isolation choice | [2]; CARRY Firecracker/gVisor | [1] | "Shared-kernel containers ... we do not claim VM-grade isolation" |
| SEC-01 depended on the preflight filter | [14] Docker seccomp docs; [5] SoK | none found | "consistent with Docker's documentation that the default profile blocks ptrace only on kernels before 4.8" (re-check quote) |
| Evaluator-outage handled fail-closed on the repaired build | [7], [8] (fault injection precedent) | none directly | "In one injected outage scenario ..." |
| Compiler-timeout cleanup | [3] (related rollback idea) | [3] term collision | "container terminated in 5/5 on the repaired build" |
| LLM feedback did not move measured observables (fixed-turn test) | [11], [9] (separation principle) | [12], [13] (LLM-mediated grading is vulnerable); HIGH-2 | "did not alter measured observables in 72/72 valid pairs; follow-up channel untested" |
| Architecture separates LLM from scoring | [11], [9], [10] | none | "follows an established pattern" |
| Dependability framing | CARRY Avizienis 2004 | [1], [2], [5] | "scoped dependability evaluation; no security guarantee" |

## Gap-closure additions (2026-09-21)
| Claim | Support | Challenge | Wording note |
|---|---|---|---|
| Host-side observables judge containment | [1] host flag; [54] state checks; [55] canaries | none | "following practice in [1], [54]" |
| Weakened controls demonstrate detectability | [1] deliberately introduced weaknesses and reference-solution variants | none | do not present as new |
| Status strings insufficient (P1-C3) | [54], [55] | [6] uses in-payload status | present as confirmation |
| SEC-01 filter dependence | [14] Docker sentence (full sentence), [5] denylist fragility (third-party figure) | none | quote the whole Docker sentence |
| Scoped claims | [2] verdict semantics; [4] weakest-link rule | none | |
