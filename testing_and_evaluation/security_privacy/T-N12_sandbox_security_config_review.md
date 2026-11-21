# T-N12 — Sandbox Security Configuration Review (code-level, scoped)

**Scope:** per `Test_Strategy.md` category S (Security/privacy testing — RECOMMENDED, scoped), this is a **code-level configuration review**, not a penetration test or a claim of "secure"/"audited" — consistent with `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §E's framing: *"these are configuration facts, not measured effectiveness"*. A genuine attack-program execution test (as Paper 1 already did, 9 programs, 4 discriminating outcomes) was not repeated here, both because Paper 1's result is already frozen/real evidence and because the Docker daemon is down in this environment (so no new attack program could actually be executed to measure outcomes, only configuration could be inspected).

## What was checked

Direct code inspection of `agents/coding_executor/coding_executor.py` (the real Docker invocation — two call sites, compile phase and run phase) and `agents/coding_executor/sandbox_policy.py` (the pre-flight static source scanner).

## Findings — Docker isolation flags present in the actual `docker run` invocation (`coding_executor.py`, both compile and execute phases)

| Flag | Present? | Purpose |
|---|---|---|
| `--user 1001:1001` | Yes | Runs as non-root UID/GID inside the container |
| `--net=none` | Yes | No network access from inside the container |
| `--cap-drop=ALL` | Yes | Drops all Linux capabilities |
| `--security-opt=no-new-privileges` | Yes | Prevents privilege escalation via setuid/setgid binaries |
| `--cpus={self.cpus}` | Yes | CPU quota |
| `--memory={self.memory_mb}m` / `--memory-swap={self.memory_mb}m` | Yes | Memory limit, swap disabled beyond the same cap |
| `--pids-limit={self.pids_limit}` | Yes | Process/fork-bomb limit |
| `--read-only` | Yes | Read-only root filesystem |
| `--tmpfs /workspace:rw,exec,size=32m,uid=1001,gid=1001,mode=1777` | Yes | Bounded, size-limited writable scratch space only |
| `-v {mount}:/input:ro` | Yes | Source code mounted read-only; container cannot modify the host-side input |

**This matches `CANONICAL_SCIENTIFIC_TRUTH_CURRENT.md` §A's description exactly** ("non-root user, `--net=none`, `--cap-drop=ALL`, `--read-only`, no-new-privileges, memory and PID limits") — confirmed directly against the current code in this session, not just cited from the canonical doc.

## Findings — pre-flight static scanner (`sandbox_policy.py`)

A second, pre-compilation layer: `validate_source_safety()` rejects source code containing a `ptrace(` call pattern (direct kernel-inspection/debugging primitive, commonly used in container-escape or anti-debugging attacks) and enforces a 64KB maximum source size (denial-of-service protection against compiler memory exhaustion). The module's own docstring is explicit and accurate about this layer's limited role: *"Static scanning is an auxiliary pre-flight filter; Docker containment remains the authoritative security and isolation boundary."*

**Limitation of the static scanner, as self-documented:** it is a single regex pattern against one dangerous primitive (`ptrace`), not a comprehensive static-analysis pass. This is an honest, narrow scope — consistent with the project's own framing, not something this review is newly discovering as a weakness.

## What this review does NOT establish

- Whether these flags are *effective* against a real attack under the current Docker/kernel version on this machine — that requires actually running attack programs (as Paper 1 did), which was not repeated here (Docker daemon down).
- Whether the frontend/backend/evaluator/Qwen services have equivalent input-validation hardening — out of scope for this review (coding sandbox only).
- General input-validation testing of the WebSocket/REST layer — partially covered separately by `T-N04`/`T-N06` (evaluator API contract and adversarial-text handling), not a comprehensive security audit of those layers either.

## Conclusion

The specific, verifiable configuration claims already present in the project's canonical truth documentation are **confirmed accurate against the current code** in this session. No new vulnerability was found or claimed; no new mitigation was added. This review is a narrow, honest confirmation of existing documented facts, not a new security assessment — label it exactly that way in Task 2/3, per `CLAUDE.md`'s instruction never to claim "secure" or a comprehensive audit that wasn't performed.
