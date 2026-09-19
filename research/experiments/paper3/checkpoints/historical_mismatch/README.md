# Historical State Mismatch Checkpoints (Paper 3 Provenance)

**Archive Date:** September 2026  
**Purpose:** Preservation of historical response-time variant checkpoint.

This directory preserves the historical checkpoint trained under `dim4_mode = "aligned_response_time"`:
- Checkpoint: `seed_123/ppo_final.zip`
- Normalization: `seed_123/vecnormalize.pkl`
- Metadata: `seed_123/training_meta.json`

### Scientific Invariant
This checkpoint represents the **historical covariate shift baseline** (where Dimension 4 encoded normalized response latency).
In accordance with Paper 3 pre-flight integrity rules:
1. This checkpoint is strictly isolated under `historical_mismatch/` and MUST NOT overwrite canonical seed checkpoints.
2. Canonical seed checkpoints in `research/experiments/paper3/checkpoints/seed_{seed}` must strictly use the canonical normalized turn progress representation ($t / T$).
