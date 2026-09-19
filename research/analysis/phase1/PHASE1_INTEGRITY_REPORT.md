# Phase 1 integrity report (X3-0d)

1. Frozen-file baseline (Phase-0 snapshot): 366 files, mismatches: 0 []
2. Key artifact hashes (gold, CrossEncoder, Paper-3 config, two checkpoints): mismatches []
3. Run manifests (5):
   - research\analysis\phase1\paper1\manifest_P1-STORED.json: status completed, 10 inputs, 6 outputs, gate None=None, problems: none
   - research\analysis\phase1\x2_a\manifest_X2-A.json: status completed, 5 inputs, 14 outputs, gate None=None, problems: none
   - research\analysis\phase1\x3_0\manifest_X3-0a.json: status completed, 8 inputs, 8 outputs, gate None=None, problems: none
   - research\analysis\phase1\x3_0\manifest_X3-0c-followup.json: status completed, 1 inputs, 2 outputs, gate None=None, problems: none
   - research\analysis\phase1\x3_0\manifest_X3-0c.json: status completed, 7 inputs, 7 outputs, gate G-REPRO=True, problems: none
4. Registry: 101 rows, 101 unique IDs, statuses {'VALID': 48, 'WITHDRAWN': 28, 'HISTORICAL': 5, 'DESIGN-ONLY': 9, 'EXPLORATORY': 11}; T1 artifact-hash check on 86 rows, mismatches []
   PENDING-REGISTRATION rows remaining: []
   Phase-1 rows without artifact hash: []
5. Tracked-file modifications in working tree: [' M .env.example', ' M research/claims/CLAIM_REGISTRY.csv', ' M research/claims/README.md'] (expected only pre-existing ' M .env.example' and the registry/README edit if uncommitted)
6. Ignored/cached files under research/scripts and rl (pre-existing pycache timestamps predate Phase 1): !! research/scripts/__pycache__/; !! rl/__pycache__/; !! rl/env/__pycache__/; !! rl/env/training_logs/; !! rl/rl_final/; !! rl/training/__pycache__/

RESULT: PASS (0 problems)
