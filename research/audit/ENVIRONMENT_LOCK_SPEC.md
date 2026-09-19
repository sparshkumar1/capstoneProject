# Environment Lock Specification — NEW RUNS ONLY (Phase 0 spec, 2026-09-19)

**Status: specification only.** No lock file was created, no package installed, no environment built and the current `.venv` was not modified. Creating any lock or environment is a Phase 1/2 action that needs explicit approval, because `CLAUDE.md` forbids changing dependencies silently.

## 1. Problem being solved
- The frozen Paper 1–3 results were not generated in a recorded, locked environment. The project `.venv` violates the pins in `requirements/*.txt` (numpy 2.5.2 vs `<2`; torch 2.11.0 vs `<2.7`; accelerate 1.13.0 vs `<1.0`), and the CrossEncoder's `config.json` is stamped by transformers 5.0.0 / sentence-transformers 5.2.3, which is not a recorded project environment (audit P0-1).
- SB3 documents that identical seeds do not guarantee identical results across PyTorch releases or platforms, so every new experiment must be tied to an exact environment (Context7, SB3 reproducibility notes; verified in the earlier pass).
- The claim registry needs an `env_lock_sha256` for every new result.

## 2. Scope and hard rules
1. **New runs only** (X1, X2, X3 and any later registered experiment). Frozen results keep `NOT_RECORDED`.
2. The current `.venv` is **never** modified, upgraded, downgraded or reinstalled. New environments live in a separate directory (proposed `envs/<lock_id>/`, git-ignored) and are rebuilt from the committed lock.
3. A lock is created **once per experiment family** before that experiment's protocol is hashed, is committed and tagged, and is **not changed** afterwards. A changed dependency = a new lock ID = a new (or re-registered) experiment.
4. If resolution conflicts with the pins in `requirements/*.txt`, the conflict is **reported** and decided by the user; pins are not loosened silently.
5. No secret enters a lock, manifest or log (no W&B API key, no tokens).

## 3. Lock profiles (decision needed at Phase 1)
| Profile | Contents | Use |
|---|---|---|
| **L-obs** (observed) | A read-only export of the versions currently in `.venv` (a `pip freeze`-style listing written to a new file; does not change the environment) | Reference for "what the frozen results probably ran on"; used to decide whether frozen numbers reproduce |
| **L-pin** (pinned) | Resolution of `requirements/*.txt` at the pinned bounds, with hashes | The intended project environment |
| **L-new** | Explicit choice per experiment family, derived from whichever of the above reproduces the frozen numbers (see §5) | The environment actually used for new runs |

Recommendation: capture L-obs first (read-only), then test whether the frozen evaluation reproduces in L-obs and in L-pin (§5), and choose L-new from that evidence.

## 4. Lock contents (per lock ID)
- `lock_id` (e.g., `LOCK-X3-2026-xx`), creation date, git commit at creation.
- Interpreter: exact Python version (3.12.x), implementation, architecture.
- OS and version; CPU model; GPU/CUDA/cuDNN (or "CPU only") and torch build tag.
- Full package list: name, exact version, wheel/sdist file hash (`--generate-hashes`), including transitive dependencies.
- Non-Python model assets by SHA-256: SBERT weights, CrossEncoder (`6a241a55…4450`), upstream CrossEncoder (`821d1aa6…`, when used), FAISS index, Qwen weights if used, SB3 checkpoints.
- Library determinism settings the run is required to use (§6).

Proposed layout (not created):
```
research/locks/<lock_id>.requirements.txt   # exact pins with hashes (input to the installer)
research/locks/<lock_id>.lock.json          # resolved package list + hashes + platform + assets
research/locks/<lock_id>.sha256             # SHA-256 of the two files above (the value stored as env_lock_sha256)
```
`env_lock_sha256` = SHA-256 of `<lock_id>.lock.json`.

## 5. Procedure (commands are proposals; none has been run)
1. **Capture** the current `.venv` versions read-only into L-obs (no installs).
2. **Resolve** L-pin with a hash-generating resolver (`uv` is available in `~/.local/bin`; `uv pip compile requirements/*.txt --generate-hashes --python 3.12`), producing a pinned, hashed requirements file.
3. **Build** a fresh environment for a lock in `envs/<lock_id>/` (`uv venv`, then an install that requires hashes, e.g. `uv pip sync --require-hashes`), separate from `.venv`.
4. **Equivalence check** (evaluation-only, approval required): in the new environment, re-evaluate a small, fixed subset of *frozen* inputs and compare against the frozen result files (hash-pinned) — for Paper 2 the 64-case scores; for Paper 3 a replay of one frozen evaluation with a frozen checkpoint. Record maximum absolute differences. If differences exceed a **pre-declared tolerance** (proposed: identical to the stored 4 decimals for the evaluator scores; identical action sequences for deterministic PPO evaluation), the environment is not adopted for experiments that rely on frozen numbers; the mismatch is reported.
5. **Commit** the lock files, record their SHA-256 in `PREREGISTRATION` and in each run manifest.
6. **Verify at run start** (mandatory): a preflight step compares installed versions and asset hashes against the lock, aborts on mismatch, and writes the outcome into the run manifest (`RUN_MANIFEST_SPEC.md`).

## 6. Determinism requirements for new runs
- Explicit seeds for Python `random`, NumPy, PyTorch, the environment (`env.reset(seed=…)`) and SB3 (`model = PPO(..., seed=…)`); evaluation with `deterministic=True`.
- Record `PYTHONHASHSEED`, thread counts (`OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `torch.get_num_threads()`), and whether `torch.use_deterministic_algorithms` is enabled (and any operation that cannot be made deterministic).
- Same seed sets across comparable conditions; report variation across training seeds.
- CPU vs GPU and OS are part of the reproducibility statement; cross-platform equality is **not** assumed.
- Explicit checkpoint saving and hashing; Weights & Biases (new runs only) logs config, seed, commit and lock hash and does not replace the manifest.

## 7. Optional hardening (not required for Phase 1)
A container image built from the lock (digest recorded in the manifest) for X1, whose system under test already uses Docker. Decide after the first lock exists.

## 8. What Phase 0 did and did not do
Did: define the mechanism and required fields. Did not: create locks, install anything, run `pip`/`uv`, or touch `.venv`.
