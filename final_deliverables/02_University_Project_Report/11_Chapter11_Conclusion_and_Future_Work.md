# Chapter 11: Conclusion and Future Work

## 11.1 Summary of Work Carried Out

Building on the Phase-2 implementation (`revised_report_v5.pdf`), this phase carried out a complete, evidence-graded verification of PrepAIred: a project-specific test strategy spanning 22 testing categories plus dedicated ML and RL evaluation; execution of the existing 25-file/28-file automated test suite to a final result of 264/283 (93.3%) passing with every remaining failure fully attributed; eleven newly authored, independently executed test scripts covering RL-policy sanity, guardrail-boundary verification, API contracts, adversarial input handling, database integrity, security configuration, compatibility, and structured UI inspection; diagnosis and correction of two genuine defects (a guardrail coverage gap and a platform-specific launcher crash), both fixed with minimal, regression-verified changes; and identification and correction of eight factual discrepancies between the Phase-2 report and the verified current implementation.

## 11.2 Verified Outcomes

The system's core technical contributions — rubric-anchored multi-component semantic evaluation, RL-driven adaptive difficulty constrained by deterministic pedagogical guardrails, structured per-turn feedback, and multi-service graceful degradation — are confirmed functioning as designed, with the two specific defects found in this phase now fixed. Ten of twelve stated project objectives are fully met by direct, current evidence (two with corrected descriptions relative to the Phase-2 report); one (the Phase-2 abstract's specific "93.3% baseline calibration" figure) is confirmed unverifiable against any stored artifact; one (sandboxed code execution) is currently blocked on an external environment dependency (the Docker daemon) rather than a code defect, with the underlying implementation independently confirmed correctly configured.

## 11.3 Main Contributions of This Phase

- A reproducible, project-specific testing and evaluation package (`testing_and_evaluation/`), with every result traceable to a stored log, script, and git commit.
- Two genuine defects found and fixed, not merely reported: a real pedagogical-safety gap in the guardrail layer, and a platform-compatibility crash in the application launcher.
- A systematic reconciliation of this project's prior documentation against its actual implementation, correcting eight specific factual discrepancies with direct evidence rather than assumption.
- An honest scope finding regarding a separate, supplied research-paper draft describing a multi-agent coordination layer, confirmed on inspection not to exist in the codebase — preventing that unverified material from being presented as evidence in this or any accompanying deliverable.

## 11.4 Limitations

Carried forward, unresolved, and newly identified limitations are stated plainly, consistent with the evidence discipline applied throughout this report:

- **Synthetic/simulation-only RL evidence.** The deployed PPO policy's training and the project's prior frozen research results are simulation-based; no claim is made about real-candidate learning outcomes.
- **No formal human-subject usability or learning-outcome study.** This remains the most significant outstanding evidentiary gap, as the Phase-2 report itself already identified.
- **Speech-transcription accuracy is not independently measured.** No verified reference-transcript dataset exists in this project; only functional (does-it-run) coverage of the audio pipeline is claimed.
- **18 of 283 automated tests remain untested-in-this-pass**, pending a running Docker daemon in the test environment; the underlying code was independently confirmed correctly configured by direct inspection, but execution-level confirmation (does the sandbox actually behave as configured under real attack/fault conditions) awaits that environment being available.
- **One pre-existing, documented test failure remains unresolved** by design, pending a decision on how to interpret it, consistent with this project's own stated policy of not silently patching known, flagged issues.
- **The CrossEncoder component's training provenance remains incomplete**, as already disclosed in this project's existing evidence record; this phase did not add new information on this point.
- **Substring-based misconception detection** (inherited from Phase-2) has high precision but low recall, as the Phase-2 report itself already disclosed; not re-evaluated quantitatively in this phase.

## 11.5 Future Work

1. **Close the Docker-dependent test gap**: start a Docker daemon in the test environment and rerun the 18 currently-blocked tests to obtain execution-level (not just configuration-level) confirmation of sandbox isolation.
2. **Resolve the one pre-existing known test failure** (`test_coding_turn_preserves_speech_confidence_and_does_not_fabricate_metrics`), a decision this phase deliberately deferred rather than resolved unilaterally.
3. **Locate or correct the two remaining unverified capstone-report figures not fully investigated in this phase** (the Chapter-6 ablation-study numbers and the evaluator-calibration/CrossEncoder-fine-tuning experiment numbers referenced in the Phase-2 report), per the discrepancy list in Chapter 10 §10.12.
4. **A formal, preregistered human-subject evaluation**, as both the Phase-2 report and this phase's testing programme independently converge on identifying as the most valuable next step for strengthening this project's evidentiary base beyond automated/synthetic testing.
5. **A real word-error-rate evaluation of the speech pipeline**, requiring a newly constructed, verified reference-transcript dataset not currently available in this project.
6. **Consider, as a separate, explicitly-scoped and preregistered future effort** (not undertaken in this phase), whether to actually build the multi-agent "bounded-authority coordination" layer described in the supplied research-paper draft (Chapter 10 §10.13) for real, which would make that paper's analytical framing genuinely applicable to this project rather than requiring its exclusion, as this phase's integrity requirements necessitated.

## 11.6 Closing Remarks

This phase's central discipline — that every claim in this report, and in the project's broader documentation, should trace to a verifiable, stored piece of evidence — produced two concrete, useful outcomes beyond simple test-count accumulation: it caught and fixed two real defects before they reached a reader or a future developer unaware of them, and it corrected eight factual inaccuracies in this project's own prior documentation before they could propagate further into a final submission, a research paper, or a presentation. This is offered as the primary methodological contribution of this phase, independent of and complementary to the verified technical contributions of the underlying system itself.
