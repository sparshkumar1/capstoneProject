# Hard confirmatory gate - X3-A (checked 2026-09-19, before the confirmatory run)

| # | Item | Status | Evidence |
|---|---|---|---|
| 1 | Protocol file exists | PASS | `PROTOCOL.md` |
| 2 | Protocol hash exists | PASS | `protocol_manifest.json` + tag message (PROTOCOL.md b15ecb9e..., manifest 6d70640e...) |
| 3 | Git commit/tag exists | PASS | tag `prereg/X3-A/v1` -> commit b00541f |
| 4 | Hypotheses fixed | PASS | PROTOCOL section 1 |
| 5 | Endpoints fixed | PASS | section 4 |
| 6 | Unit of analysis fixed | PASS | persona (training seed second factor) |
| 7 | Sample size fixed | PASS | 40 personas x 20 seeds x 5 training seeds (section 5) |
| 8 | Seeds fixed | PASS | config (evaluation, training, bootstrap) |
| 9 | Stopping rules fixed | PASS | section 7 |
| 10 | delta / m fixed | PASS | 0.12 / 0.20 |
| 11 | Contamination controls fixed | PASS | sections 3, 7, 10 (harness gate; frozen personas excluded; disclosure of seen fixture) |
| 12 | Environment manifest ready | PASS | `LOCK-X3-2026-09-19` (hash-pinned), verified at run start; run manifest written first |
| 13 | Mutation controls pass dry-run | PASS | `dryrun/gate_G-HARNESS.csv` 9/9 (two earlier attempts failed on invisible mutants; retained in DRYRUN_LOG.md) |
| 14 | No unresolved scientific fork | PASS with recorded items | persona generator G1 and trigger operationalisation pre-specified and disclosed; X3-B requires D-N2 (user) and is not part of this run |
| 15 | Human-data gate | N/A | no human data |
