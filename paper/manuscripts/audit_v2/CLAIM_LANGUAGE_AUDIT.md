# CLAIM LANGUAGE AUDIT (2026-09-21)

Method: `audit_v2/scan_language.py lang` on the v2 manuscript **bodies** (prose, tables and captions; comments and reference lists excluded). Terms: secure, security guarantee, fault-tolerant, universally contained, prompt-injection-proof, cannot affect scoring, validated, reliable, human-level, fair/fairness, unbiased, generalizable, state-of-the-art, best, first, novel, novelty, formal/safety shield, shield, negative equivalence, expert panel, gold standard, blinded, independent raters, failure-aware, measurement validity, robust, superior — plus gold, committee, guarantee, safe, safer, proven, outperform, human-like.

## 1. Every hit and its disposition
| Paper | Term | Context | Disposition |
|---|---|---|---|
| P1 | secure | "We do not claim that the pipeline is secure" | negation — keep |
| P1 | best | "best-answer fields/flags", "best-answer score field" | field name — keep |
| P2 | validated | "not externally validated" | negation — keep |
| P2 | fairness | "No fairness analysis was performed, and no fairness claim is made"; "not evaluated: fairness" | negation — keep |
| P2 | first | "breadth-first search", "depth-first search" | topic names — keep |
| P2 | expert panel / gold standard / gold | "they are not described as an expert panel, expert consensus, independent adjudication or a gold standard" | explicit negation of prohibited descriptors — keep (author may delete the whole sentence if preferred) |
| P2 | blinded | Table I row "Whether raters were blinded beyond the sheet content — not documented"; objection "Were the raters blinded …? Not documented" | documentation gap — keep |
| P2 | superior | "neither component is described as statistically superior" | negation — keep |
| P3 | validated | "not … a fully validated model of human learning" | attributed to Kadam et al. — keep |
| P3 | first | "the first row repeats the primary result"; "a first primary-run attempt was aborted" | ordinal — keep |
| P3 | shield | "in safe RL a 'shield' denotes enforcement of a formally specified safety property [9]" | prior-work terminology — keep |
| P3 | superior | class name *PPO-superior* in the registered rule | rule name — keep |
| P3 | guarantee | "no safety guarantee" (×2) | negation — keep |
| P3 | safe | "In safe reinforcement learning" | field name — keep |
| all | fault-tolerant, universally contained, prompt-injection-proof, cannot affect scoring, security guarantee, human-level, unbiased, generalizable, state-of-the-art, novel, novelty, formal/safety shield, negative equivalence, independent raters, failure-aware, measurement validity, robust, reliable, committee, proven, outperform, human-like | 0 hits in bodies | — |

**Result:** no hit is an unqualified claim. 25 hit contexts in bodies (P1 5, P2 12, P3 8; "gold" and "gold standard" are the same context); all negated, attributed, field names or ordinals. "fair" as a separate word: 0 outside "fairness".

## 2. Prohibited upgrades (each pair checked)
| Not equal to | Check | Result |
|---|---|---|
| IMPLEMENTED ≠ VALIDATED | P1 "validated score" renamed; P2 "not a validation study"; P3 "no claim of … benefit" | OK |
| SIMULATED ≠ REAL-WORLD | P3 abstract, Section VII, conclusion | OK |
| EXPLORATORY ≠ CONFIRMATORY | P2 throughout (12 occurrences of "exploratory"); the abstract says "results are exploratory diagnostics, not validation" | OK |
| POINT ESTIMATE ≠ SIGNIFICANT DIFFERENCE | P2 composite vs R-only; AUROC; P3 persona-only interval | OK |
| REPOSITORY-REGISTERED ≠ EXTERNAL PREREGISTRATION | P1 Section IV; P3 Section IV "Registration status" | OK |
| CONTAINMENT TEST PASSED ≠ SECURE SYSTEM | P1 abstract last sentence; VI closing paragraph | OK |
| HUMAN REFERENCE ≠ GOLD STANDARD | P2 Section IV | OK |
| HIGH HUMAN AGREEMENT ≠ NATURALISTIC VALIDITY | P2 Section VI-A and VII | OK |
| EQUIVALENCE WITHIN ±0.12 ≠ PPO SUPERIORITY | P3 Table I, Sections V-A, V-B, VI | OK |

## 3. Wording checks specific to this brief
| Requirement | Status |
|---|---|
| P3 never states "The guardrail layer matched on 563 of 1250 turns" | Confirmed absent (grep) |
| P3 "0 violations" | absent; "boundary-saturated attempted actions before simulator clipping" used |
| P3 "interventions" | present only in the sentence that says none of the counts is called an intervention; the 563 activations "are not interventions" |
| P2 "three-rater" | 1 occurrence, in the definitional sentence limiting it to the 54 mean-of-three cases |
| P1 "Docker prevented ptrace" | absent |
| P1 "Qwen cannot affect scoring" | absent |

## 4. Verdict
**GREEN.**
