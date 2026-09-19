# Historical Invalid Baseline Results Archive

**Archive Date:** September 2026  
**Status:** **SUPERSEDED / ARTIFACT OF UNCALIBRATED BASELINE**

This directory preserves the historical results generated when `SimulatedCandidate.skill` defaulted to `0.60` ($d^*=3.0$) across all 5 personas:
- `rl_results.csv`
- `rl_results.md`

### Identified Defect
In these historical files, the `Fixed` difficulty baseline (difficulty locked at $3.0$) was reported as:
`Tracking Error = 0.000 [0.000, 0.000]`
Because all personas defaulted to skill $0.60$, $d^*(\text{persona}) = 0.60 \times 5.0 = 3.000$, artificially producing zero baseline error.

In Paper 3, this defect was formally identified in `research/audit/paper3_reporting_audit.md` and repaired:
- True persona target difficulties ($d^* \in [1.0, 4.5]$) are explicitly passed.
- True fixed baseline tracking error is $\text{MAE}_{\text{Fixed}} = 1.200$.
These files are preserved strictly for provenance and scientific transparency.
