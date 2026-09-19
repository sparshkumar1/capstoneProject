# Sprint decisions and blockers (running log; 2026-09-19)

Consequential decisions that the autonomous sprint could not or should not take are recorded here and the affected branch is parked. Nothing below was decided by the executor. Update rule: entries are appended with a timestamp; none is deleted.

## A. Decisions required from the user / ChatGPT review
| ID | Decision | Why it is open | Affects | Status |
|---|---|---|---|---|
| D-N2 | X3-B training environment: candidate RNG seeding and the training persona distribution; whether the training environment keeps the shield in the loop (finding N9) | Touches environment definitions that `CLAUDE.md` reserves to the user; the frozen training used a single unseeded candidate with guardrails on | X3-B only (X3-A uses frozen checkpoints) | **OPEN - X3-B parked** |
| D-X2-TAU | Which false-accept rule X2-C uses (fixed tau 0.60 vs 0.75 for the composite only; threshold-free AUROC; matched operating point), and rho_min | The evaluator has no explicit accept threshold (N5); X2-A results must not set it | X2-C H1/H3 | OPEN - to be fixed with the user before X2-C is tagged |
| D-F1 | Supersession pointers/banners in `docs/PROJECT_STATE.md`, `paper/README.md`, `research/README.md`, `research/CLAUDE_RESEARCH_INDEX.md` | Two are the user's untracked files; the index file states rho 0.6975 as "sole authentic" | Documentation hygiene (defence-in-depth; `CLAUDE.md` already overrides) | OPEN - exact text in `PHASE1_PREFLIGHT_DECISION_MEMO.md` section 3 |
| D-HUMAN | Institutional/venue determination, consent/ledger materials, trainer provenance reply, rater provenance records | External; drafts exist and were NOT sent | X2-C (blocked), CrossEncoder provenance wording | OPEN - external |
| D-DOCKER | Docker Desktop must be running (daemon was down at the readiness check) and the sandbox image confirmed | Environment action | X1 execution | see section B |

## B. Blockers
| ID | Blocker | Effect |
|---|---|---|
| B-1 | Docker daemon not running at the sprint start (tool-readiness check) | X1-A (Docker-dependent scenarios), X1-C blocked until it runs |
| B-2 | Human/ethics gate not satisfied (no institutional determination, consent, provenance) | X2-C blocked; no benchmark authoring or rating |
| B-3 | Zotero library empty | Literature/citation steps later (not a blocker for execution) |

## C. Decisions taken by the sprint instruction itself (recorded, not open)
- Replay used a separately built documented environment (`envs/replay-Lobs`, lock record `research/locks/replay-Lobs.*`) instead of route D of the preflight memo; the project `.venv` was not modified.
- Manifest helper `research/tools/run_manifest.py` (stdlib only) was written and dry-run on a dummy file (the sprint requires manifests; the preflight memo had flagged the helper as needing approval).
- Protocol commits/tags are created by the sprint (authorised in the sprint text); external submission is not.
- X3-B trigger: as specified in the sprint text (see the X3 final protocol).
- Equivalence: 95 % CI entirely within +/-0.12; superiority: 95 % CI entirely below -0.20 (sprint text; resolves closeout F8).

## D. Status updates during Phase 2/3
- **B-1 resolved (environment):** at Phase-2 time the Docker daemon was running (Docker 29.7.2, WSL2 backend) and the image `prepaired-c-sandbox:latest` (238 MB) was present. Docker is therefore no longer a blocker for X1-C.
- **X1-A, X1-B, X1-C: NOT finalized, NOT tagged, NOT run.** Not blocked by a scientific decision but by construction work that was not completed in the sprint window: (i) X1-A needs the dependency-enumeration table (code reference per dependency x failure mode), stubs/injectors for Qwen, evaluator, Docker daemon, compiler hang, SQLite lock contention, WebSocket reset, feature-extractor crash, and one mutant build/config per scenario; (ii) X1-B needs the hashed adversarial prompt set (>= 30 paired prompts), a real Qwen service, the AST/static check and the LLM-wired mutant; (iii) X1-C needs discriminating attack programs that print `connect()`/`errno`, `EROFS`, fork counts, OOM kills, host canaries and listeners, a permissive-configuration control, and an oracle that does not depend on the executor's status string. The executor returns per-test `stdout`/`exit_code`/`status`, so attack programs can self-report through the shipped `DockerCSandbox.compile_and_execute`; the static pre-flight filter must be reported as a separate layer. Each of these needs its own tagged protocol and the mutation-control dry run before execution (defect policy in `X1_PROTOCOL_DRAFT.md`). No confirmatory experiment was started for X1-A/B/C.
- **X1-D:** protocol tagged `prereg/X1-D/v1` with SUT tag `sut/X1/build-A`.
- **D-X3B-OP (new, for review):** the X3-B trigger operationalises "a result strong enough that a method-level PPO claim would need confirmation" as PPO-superior or PPO-adverse (class != Equivalent). It did not matter for the outcome (X3-A was Equivalent; X3-B not triggered).
- **X2-C:** not finalized (institutional/ethics gate, D-X2-TAU, item authoring not permitted before the gate); the draft stays a draft.
