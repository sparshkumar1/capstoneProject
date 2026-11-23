# Go / no-go: ADCOM 2027 fit (written 2026-10-02, after the architecture audit and before E2/E4 results)

Venue facts used (from the CFP text supplied in the task; the official pages are unreachable from this environment and were
not verified): double-blind, Springer CCIS, ≤ 20 pages incl. references and appendices, deadline 15 Oct 2026, Microsoft CMT.
A search snippet independently gave the conference dates (10–11 June 2027, Bengaluru) and the theme "multi-agent systems and
decentralised intelligence"; page limit and deadline were **not** confirmed by search.

## Does the implemented system support a multi-agent claim?
No, not in the strong sense. It is a centrally orchestrated, role-separated pipeline (`architecture/ARCHITECTURE_INVENTORY.md`):
one hub, in-process role calls, one 1.5 B-parameter LLM used in three roles, one PPO policy. There is no peer communication,
negotiation, delegation or planning. The paper must not use the words "multi-agent system" as a contribution claim. What can
honestly be claimed is an **authority-partitioned orchestration** of heterogeneous components (learned scorer, rules, LLM,
RL policy) and an empirical account of which coordination mechanisms matter under component faults.

## Theme fit
| Theme | Fit | Reason |
|---|---|---|
| Core multi-agent systems and collaborative reasoning | weak | no collaboration or reasoning between agents; only as a contrasting case (hub-and-spoke, authority partition) |
| Agent-native development and lifecycle engineering | moderate (primary) | engineering study of coordination contracts, failure semantics, observability, ablation and regression testing of an LLM-integrated orchestrated system |
| Preemptive agentic security and resilience | moderate (secondary) | fault injection at handoffs, fail-closed semantics, integrity of the stored record, latency under a hanging dependency |
| Distributed infrastructure | marginal | service split and failure-path latency only |
| Physical AI | none | |
Chosen: primary "Agent-native development and lifecycle engineering"; secondary "Preemptive agentic security and resilience".

## Is the contribution distinct from ordinary modular software engineering?
Partly. Distinct, checkable pieces: (1) an empirically derived **write-authority matrix** (which role changes which state) showing
the LLM-facing roles cannot change scores; (2) a **mechanism × fault ablation** with pre-registered invariants and predictions
(14/14 matched, including cells where the shipped system itself violates an invariant); (3) a **before/after fix** driven by that
finding (E4, if it runs clean); (4) measured **cost of the failure path** with real sockets (E2). Not distinct: fail-closed handling,
retries, circuit breakers are standard dependability practice. Related work (MAST, resilience of faulty agents, MAS-FIRE) studies
LLM-agent systems with LLM faults; no work retrieved studies an interview-coaching pipeline with a non-LLM authoritative scorer.
This is a statement about the retrieved snippets only; no "first" claim will be made.

## Limits that bound the claims
No live LLM or evaluator can run here (weights/network). Everything is REPLAY / SOCKET / CONSTRUCTED evidence. 64 recorded
answers from 8 constructed questions. Replay candidate never improves. The system's empirical behaviour with real LLM text is
untested. No learning or coaching-quality claim is possible.

## Decision
**GO, narrowed (N2-equivalent).** Write a focused systems paper (target ≈ 12–15 pages CCIS): "authority-partitioned orchestration",
mechanism ablation under injected faults, one evidence-driven fix, cost of failure handling, and an explicit section on what is not
multi-agent. If E4 or E2 contradict the plan, report the contradiction; do not widen claims. A no-go would apply only if the
verification below failed (numbers not reproducible) or if the venue's scope were confirmed to exclude systems/dependability work,
which cannot be checked offline.

## Overlap risk (author decision, not resolved here)
Evidence from other PREPAIred manuscripts (ICETC Paper 1 containment/fault campaigns, Paper 2 evaluator data, Paper 3 PPO study)
shares the system and, for E1/E3, the stored Paper 2 evaluator outputs as replay inputs. The ADCOM paper's experiments are new,
but a reviewer comparing submissions could see topical overlap. The authors must check each venue's concurrent-submission policy.
