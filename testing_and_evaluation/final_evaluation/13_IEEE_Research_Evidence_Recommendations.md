# IEEE Research Evidence Recommendations — Final Evaluation Phase

This phase's new findings, assessed for IEEE-paper relevance against the existing `Independent_Project_Audit/04_IEEE_Evidence_Assessment.md` (not superseded, extended):

| New finding this phase | Suitable for the IEEE paper? | Reason |
|---|---|---|
| The 0.4825/0.4832, 0.4897/0.4884 reconciliation | **Yes, as a methods-rigor footnote**, not a headline result | Strengthens the paper's existing evaluator-ablation table (already planned) by pre-empting a reviewer's likely question about the two close numbers; does not change any reported value |
| Gymnasium `check_env()` passing | **Yes, as one sentence in the Methodology section** | Standard, citable evidence of environment-interface correctness; costs nothing to include, strengthens reproducibility claims |
| PPO checkpoint identity resolution | **Yes — this is now essential, not optional**, if the paper cites any Paper-3 numeric result | A reviewer who checks the repository could otherwise find the same hash mismatch and reasonably question which checkpoint the reported numbers describe. The paper should state the evaluated checkpoint's hash explicitly in a footnote or data-availability statement. |
| Qwen quality rubric findings (factually-confused corrective text; hallucinated structured-field content) | **Yes, as a disclosed limitation**, not a headline finding | Directly relevant to any claim the paper makes about Qwen's narrative-feedback role — strengthens the paper's "safety-hardened, not accuracy-optimal" framing by extending it explicitly to the feedback-text layer, not only the score |
| The hint/report-generation template-vs-LLM finding | **Yes — this is a required correction**, if the paper describes Qwen as generating hints | The IEEE paper draft produced earlier in this engagement does not describe hint generation in detail, so no direct correction to that specific document was found necessary on review — but any future revision must not add a claim that hints are LLM-generated, since this phase established they are not |
| The admin-dashboard fix | **No** — engineering reliability work, not a research claim | Appropriate for the university report's engineering/testing chapter, not the IEEE paper, consistent with the existing `Independent_Project_Audit`'s own category guidance (routine engineering fixes do not belong in the research paper) |
| The G5 guardrail-fallback consistency fix | **No**, same reasoning as above | — |
| The reward-redesign protocol (`11_Experiment_Provenance_Register.md` §3) | **No — not yet**, it is a proposal, not a result | Would become IEEE-relevant only once actually executed under its own pre-registration, as a genuinely new experiment; citing an unexecuted protocol as if it were a finding would overstate the evidence |

## Specific text-level recommendation for the existing IEEE paper draft

The paper draft produced earlier in this engagement (`final_deliverables/05_IEEE_Paper/`) already states the PPO equivalence finding correctly (§VII-B, "not statistically distinguishable from zero," citing the pre-registered margin). **One addition is recommended, not yet made to that file this phase** (out of this phase's own scope, which is testing/evaluation, not paper editing): a one-sentence footnote on the checkpoint hash, per the row above. Recorded here as a recommendation for the paper's next revision pass, not implemented.
