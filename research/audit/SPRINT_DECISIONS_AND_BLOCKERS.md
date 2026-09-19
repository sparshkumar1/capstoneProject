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
