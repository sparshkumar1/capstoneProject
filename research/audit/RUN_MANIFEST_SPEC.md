# Run Manifest Specification (Phase 0 spec, 2026-09-19)

**Status: specification only; no manifest was generated and no run performed.** Every registered run (X1/X2/X3 and any later experiment) writes one manifest **before** the first result is produced and finalises it after the last. A run without a valid manifest has no registry standing.

## 1. Format
One JSON file per run, `research/results/<experiment_id>/<run_id>/run_manifest.json`, plus a `.sha256` file. (New result directories only; nothing under an existing frozen path.) Field names below are normative; unknown values are written as `null` with a reason, never omitted or guessed.

```
{
  "manifest_version": "1.0",
  "experiment_id": "X3-A",
  "run_id": "X3-A-2026-xx-xx-001",
  "status": "started | completed | failed | aborted",
  "started_utc": "...", "finished_utc": "...",
  "protocol": {
    "protocol_file": "research/audit/X3_PROTOCOL_DRAFT.md (final name at freeze)",
    "protocol_sha256": "...", "protocol_git_tag": "prereg/X3-A/v1", "protocol_tag_commit": "..."
  },
  "code": {
    "git_commit": "...", "git_tag": "...", "git_dirty": false,
    "dirty_diff_sha256": null,
    "entrypoint": "path/to/script.py", "entrypoint_sha256": "...", "command_line": "..."
  },
  "config": {
    "config_path": "...", "config_sha256": "...", "extra_config_sha256": {"persona_table": "...", "prompt_set": "..."}
  },
  "environment": {
    "lock_id": "...", "env_lock_sha256": "...",
    "lock_verified_at_start": true, "lock_mismatches": [],
    "os": "...", "os_version": "...", "python": "3.12.x", "python_implementation": "CPython",
    "packages": {"numpy": "...", "torch": "...", "stable_baselines3": "...", "gymnasium": "...", "sentence_transformers": "...", "transformers": "...", "faiss": "...", "scipy": "..."},
    "pip_freeze_sha256": "...",
    "hardware": {"cpu": "...", "cores": 0, "ram_gb": 0, "gpu": null, "cuda": null},
    "determinism": {"pythonhashseed": "...", "omp_threads": 0, "torch_threads": 0, "torch_deterministic_algorithms": false, "notes": "..."}
  },
  "seeds": {"training": [], "evaluation": [], "bootstrap": 0, "ordering": 0, "generator": null, "env_seed_policy": "..."},
  "data": {
    "datasets": [{"name": "...", "path": "...", "sha256": "...", "version": "..."}],
    "benchmark_item_file_sha256": null, "human_gold_sha256": null
  },
  "models": [
    {"role": "crossencoder_derived", "path": "...", "sha256": "..."},
    {"role": "ppo_checkpoint", "path": "...", "sha256": "...", "training_seed": 0},
    {"role": "faiss_index", "path": "...", "sha256": "..."}
  ],
  "outputs": [{"path": "...", "sha256": "..."}],
  "logs": {"stdout_sha256": "...", "stderr_sha256": "...", "run_log": "..."},
  "wandb": {"used": false, "run_id": null, "entity_project": null},
  "deviations": [],
  "failures": [],
  "operator": "coded ID only, no personal data"
}
```

## 2. Required fields (minimum set requested for Phase 0)
git commit, tag, OS, Python, package versions, hardware, checkpoint hashes, seeds, config hashes — all present above (`code.git_commit`, `code.git_tag`, `environment.os`, `environment.python`, `environment.packages`, `environment.hardware`, `models[].sha256`, `seeds`, `config.config_sha256`). Additional mandatory fields: protocol hash and tag, lock hash, data hashes, output hashes, deviations.

## 3. Rules
1. **Written first, closed last.** `status: started` is written before any result; the protocol hash and tag must already exist and match the committed protocol, otherwise the run must not start.
2. **Clean tree.** `git_dirty` must be `false`. If it is `true`, the run is not confirmatory; the diff hash is recorded and the run is labelled exploratory.
3. **Lock check.** Installed packages and asset hashes are compared with the lock at start (`ENVIRONMENT_LOCK_SPEC.md` §5.6). Any mismatch aborts the run unless the user waives it, and then it is recorded in `lock_mismatches` and `deviations`.
4. **Deviations and failures are data.** Any departure from the protocol, any harness failure and any retry is recorded verbatim. Silent retries are prohibited.
5. **No secrets and no personal data** in the manifest (no API keys; rater identities are coded).
6. **Registry link.** Every registry row created from a run cites the manifest path and its SHA-256 (`artifact_path` for the manifest or `notes`).
7. **Immutability.** After `status: completed`, the manifest and outputs are hashed and frozen; corrections are new files.

## 4. Experiment-specific additions
- **X1:** system-under-test build tag and commit; container image digest; list of injected faults with injection times; host canary file hashes before/after; per-trial log hashes; JUnit report hash; defect-policy record (build A / build B).
- **X2:** benchmark item file hash; frozen human gold hash; rater ledger hash (coded IDs); evaluator hash set (weights, FAISS index, code commit, θ, weights, dampening); mapping rule hash (if any); order-permutation seed.
- **X3:** persona table hash and generator seed; checkpoint hashes with training seeds; reward/state/action config hash (must equal the frozen config hash unless the protocol says otherwise); per-turn log hashes; SB3/PyTorch versions; W&B run IDs (new runs only; `wandb.init()` called before the callback).

## 5. Phase 0 status
Not created. To be implemented as a small writer in Phase 1/2 after approval; the first use is the dry-run manifest on non-confirmatory fixtures.
