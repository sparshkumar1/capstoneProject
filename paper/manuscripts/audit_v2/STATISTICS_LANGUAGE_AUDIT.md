# STATISTICS LANGUAGE AUDIT (2026-09-21)

Method: `audit_v2/scan_language.py stat` on manuscript bodies (comments and references excluded), then manual check of each protected item against the stored analysis. Terms scanned: significant, significance, p =, CI, confidence, equivalent, superior, outperformed, better, worse, bias, correlation, agreement, reliability.

## 1. Term-by-term disposition
| Term | P1 | P2 | P3 | Disposition |
|---|---|---|---|---|
| significant / significance | 0 | 1 ("not a confirmatory significance test") | 0 in results; Related Work reports other authors' "significantly" claims | negation / attributed |
| p = | 0 | 0 in body text as a symbol; the stored value appears once as "0.0018863" with its label | 1 (attributed to prior work [4] in v1; **removed** in v2 with the unverifiable p-value) | P3: none left |
| CI | 0 | 0 (the manuscripts say "interval") | 0 | consistent |
| confidence | 0 | 0 | 3 (simulated-candidate *confidence* state variable) | field meaning, not statistical |
| equivalent | 0 | 0 | 5 | all tied to the pre-specified rule (interval inside ±0.12); one negation ("not … equivalent") |
| superior / superiority | 0 | 1 ("neither component is described as statistically superior") | 1 (class name) + "superiority not met" | negation / rule name |
| outperformed | 0 | 0 | 0 | — |
| better / worse | 0 | 1 ("higher AUROC … point estimates and the AUROC intervals overlap" — v2 replaced "better") | 3 "better" + 1 "worse" | P3: each is a negation ("does not support a claim that PPO tracks better"; "do not license the statement") or a factual comparison of comparator means in the five-persona vs grid sets ("heuristic tracked better … and worse on the grid"), reported separately |
| bias | 0 | 3 (literature on verbosity/judge bias; "Bland–Altman bias" = mean error) | 1 (the question "does the simulator bias the result?") | not a claim |
| correlation / agreement / reliability | 0 | correlation 9, agreement 24 (descriptive coefficients; "reliability coefficient" only in literature/ICC sentence) | agreement 1 (reward term) | matches analysis |

## 2. Protected items
| Item | Check | Result |
|---|---|---|
| P2 p-value | one occurrence, "case-level, nominal p-value under independent-case assumptions", clustered-within-8-questions statement adjacent, "not … evidence of evaluator validity"; absent from abstract, discussion numeric, conclusion | OK (fixed in v2) |
| P2 composite − R-only | −0.102, two-level [−0.2849, +0.1174] includes zero; text: "the data do not establish a difference"; neither component "statistically superior" | OK (fixed in v2) |
| P2 interval labels | every interval carries its type in text, Table II, Table III, IV, V and Fig. 2 caption; abstract gives the two intervals by name | OK |
| P2 length-only | "competitive", "length confound", "benchmark-level and exploratory"; no "inherently length-biased", no "learned length" | OK |
| P2 AUROC comparisons | described as point estimates with overlapping intervals; composite-vs-R AUROC difference (−0.0615 [−0.1676, 0.0659]) reported | OK |
| P2 BM25 = composite ρ | "observed and not interpreted as equivalence" | OK |
| P3 equivalence | "equivalent under the pre-specified ±0.12 margin"; equivalence ≠ no effect stated in Section V-A, VI, VII | OK |
| P3 superiority not met | stated in abstract, Table I, Section V-B | OK |
| P3 persona-only and two leave-one-seed-out intervals exclude zero | stated; "do not license the statement that PPO tracks better" | OK |
| P3 volatility | "more volatile" supported by a bootstrap interval on the grid (+0.14877 [0.0666, 0.25445]); guarded vs unguarded PPO comparisons labelled point values | OK |
| P1 | no inferential statistics; "k/5" = counts | OK |

## 3. Additional checks
- Numeric trace: 0 unmatched decimals (P1: none ≥ 3 decimals; P2 175; P3 85).
- Every "×/y" and "x of y" count in P3 (563/1250, 99/1250, 464, 41/125, 50/125, 25/125, 5/125, 30/30/34/5) matches the stored turn log and follow-up JSON.
- Not multiplicity-controlled analyses are labelled descriptive in P2 (Section V) and P3 (Section IV, Table IV).

## 4. Verdict
No statistics-language issue remains. **GREEN.**
