# Cloud Testing Report

**Status as of 2026-11-15: NOT YET DEPLOYED.** No Azure VM has been provisioned yet (that requires account creation only you can do — see `Deployment_Instructions.md` Part A). Nothing below is a result; it's the checklist to actually run once a public URL exists, carried over from the original migration brief's test plan. Per this project's evidence standard, no test here gets marked passed without having actually been executed and observed against the real deployed URL — do not fill this in with assumed outcomes.

| # | Test | Result | Notes |
|---|---|---|---|
| 1 | Application availability (HTTPS, loads, navigates, no localhost deps) | Not run | |
| 2 | Authentication (login, invalid admin password rejected, admin routes gated) | Not run | Specifically verify a request to `/api/admin/sessions` without `X-Admin-Token` gets 401 |
| 3 | Interview workflow (topic select → questions → answers → progress) | Not run | |
| 4 | Qwen 2.5 (real model, not mock fallback) | Not run | Check `/health` on the qwen service reports `mock_mode: false` and `models_loaded` includes the GGUF model before claiming this passed |
| 5 | Evaluation (SBERT/FAISS/CrossEncoder scores, not mock) | Not run | Check backend startup log for "Authoritative production evaluator loaded from services.evaluator.app" (confirms `EVALUATOR_READY=True`, not the mock fallback) |
| 6 | Speech processing (mic permission, upload, transcription) | Not run | Needs HTTPS for browser mic permission to work at all — can't test meaningfully without a real cert, which needs A1+A2 done first |
| 7 | Adaptive interview (RL/PPO difficulty transitions, follow-ups) | Not run | Check backend startup log for the RL checkpoint loading successfully (not the heuristic fallback) |
| 8 | Final report (score, persisted) | Not run | |
| 9 | Database persistence across restart (`docker compose restart backend`) | Not run | |
| 10 | External access (separate browser/network, confirms no local-machine dependency) | Not run | |
| 11 | Concurrent access (multiple sessions, no session mixing) | Not run | |

## Known constraint going in

Coding-question sandbox execution is **intentionally disabled** in this deployment (your decision — see `Cloud_Architecture.md`). It should return a clear `sandbox_error`, not crash or hang; verify that specific behavior rather than expecting it to execute code.

## How to fill this in

Once the VM is up and `https://<PUBLIC_DOMAIN>` resolves, work through each row from a browser/network that is not the VM itself, and replace "Not run" with "Pass" / "Fail" / "Partial" plus a one-line note on what was actually observed (error text, screenshot reference, etc.). Update the date at the top when you do.
