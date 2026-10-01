# D1 Benchmark — Independent Technical Review Packet

Companion to `D1_FINAL_BLOCKER_ASSESSMENT.md` (the "why" this is blocked); this file is the "how it will be reviewed once content exists" — prepared infrastructure, not a claim that review has occurred.

## Readiness determination

**The benchmark is NOT ready for independent review**, for the same reason established across three prior passes: the statistical protocol (`SYNTHETIC_EVALUATOR_BENCHMARK_PROTOCOL_V14.md`) is finalized, but no answer-text content exists for any of the 122 in-scope questions, in any split (development, confirmatory, or cap-excluded). There is nothing yet for a reviewer to look at. This packet exists so that the moment content is authored, review can begin immediately with a ready, pre-agreed procedure — rather than having to design the review process *after* seeing the content, which would itself be a validity risk (a reviewer procedure designed around specific content is more easily gamed, consciously or not, than one fixed in advance).

## Packet contents (all below are templates/procedures, populated with zero real content)

### A. Reviewer instructions (template)

> You are reviewing a set of candidate technical-interview answers for construction validity. For each item, you will see: the question text, the topic, the intended quality category (e.g. "concise-correct", "partial", "misconception", "off-topic", "keyword-stuffed" — mirroring the categories already used in the existing 64-case human-gold benchmark, `research/data/evaluator_benchmark/README.md`), and the answer text itself. You will NOT see any evaluator score, model prediction, or confidence value for any item — you are checking the item's construction, not agreeing or disagreeing with a score.
>
> For each item, answer:
> 1. Is the answer text technically accurate *for its intended category*? (A "misconception" item should contain a real, plausible technical error — not gibberish; a "concise-correct" item should be genuinely and fully correct.)
> 2. Is the intended category an accurate description of the answer as written?
> 3. Does the answer read as a plausible thing a real candidate might say (not implausibly stilted, or an implausible error no one would actually make)?
> 4. Flag any item whose answer text appears near-duplicated (content-wise, not just wording) with another item in the same or a different split.

### B. Reviewer response template (per item)

```
item_id: <case_id>
qid: <question id>
split: <development | confirmatory | cap_excluded>
intended_category: <as provided>

Q1_technically_accurate_for_category: <yes | no | uncertain>
Q1_notes: <free text, required if "no" or "uncertain">

Q2_category_accurately_describes_answer: <yes | no>
Q2_notes: <free text, required if "no">

Q3_plausible_candidate_response: <yes | no>
Q3_notes: <free text, required if "no">

Q4_suspected_cross_item_duplication: <none | item_id(s) it resembles>

overall_recommendation: <accept as-is | accept with edit | reject>
suggested_edit: <free text, if "accept with edit">
```

### C. Disagreement recording and resolution procedure

1. Each item is reviewed independently by the reviewer (and, if more than one reviewer is available, by each reviewer independently, blind to each other's responses — see §D).
2. Any item where `overall_recommendation` is "reject" or "accept with edit" is logged in a running disagreement/edit table (item_id, reviewer, issue, resolution).
3. If multiple reviewers disagree on `overall_recommendation` for the same item, the item is adjudicated by a third party or, if unavailable, is excluded from the confirmatory split and moved to cap-excluded (never silently kept as-is over an unresolved disagreement).
4. Every edit made in response to review is logged with a before/after diff and the reviewer's stated reason — content is never silently modified after review without a record.
5. The final, reviewed, frozen dataset is hashed (matching this project's existing convention for every other confirmatory dataset — see `research/audit/PREREGISTRATION_SPEC.md`) *after* all review-driven edits are incorporated, not before.

### D. Blinding

The reviewer template (§B) deliberately excludes any evaluator score, model output, or confidence value — a reviewer checking construction validity should not be influenced by knowing how the system under study scored an item. If more than one reviewer is used, each reviews independently before any cross-comparison (§C.3), to avoid anchoring.

## What would still be needed before this packet can actually be used

1. **The content itself** — this pass did not author it, per `D1_FINAL_BLOCKER_ASSESSMENT.md`'s reasoning (self-authored-and-self-reviewed content would not satisfy this packet's own §A/§D requirements — the author and the reviewer must be different people).
2. **An actual reviewer** — a person other than the content's author, with the technical background to evaluate CS/programming answer correctness. Not identified or contacted in this pass (no mechanism to do so from within an autonomous session).
3. Once (1) and (2) exist, this packet's procedure can run as specified with no further design work.

## Status: review-ready infrastructure prepared; content and reviewer both still absent; D1 explicitly left pending, not attempted further.
