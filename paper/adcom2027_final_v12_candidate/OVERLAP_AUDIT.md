# Venue-overlap audit — ADCOM 2027 manuscript vs ICITIIT 2027, INDIACom 2027 (and earlier ADCOM draft, ICETC Paper 1)

Compared (read from `paper/v10-venue-papers:paper/venue_submissions_2026/{ICITIIT2027,INDIACom2027}/manuscript_source.md`, title, abstract, introduction, related-work and contribution lists):
this ADCOM manuscript (`paper/adcom2027_final/manuscript/*.tex`). The ICETC Paper 1 and the earlier narrowed ADCOM draft were compared from their stored summaries only.
This is the author's decision to make; it is a comparison, not a ruling on any venue's policy, which was not retrieved.

| Aspect | ICITIIT 2027 | INDIACom 2027 | ADCOM 2027 (this) |
|---|---|---|---|
| Title / thesis | Authority separation of scoring from an LLM; evidence audit of a multimodal pipeline | Design and verification (spec-to-code) of a decoupled, evidence-gated architecture | Bounded-authority agents added to the orchestrated workflow: coordination, arbitration, fault containment |
| Research question | Does authority separation hold; how well does the cross-encoder agree with humans (length confound)? | Does the published specification match deployed code; what does the evaluator audit show? | What do stateful agents with typed proposals change, which safeguards contain agent faults, what do they cost; which earlier audit claims survive correction |
| System described | the default (agent-free) workflow | the default (agent-free) workflow | the same workflow plus a feature-flagged agent layer (default off) |
| Data | 64 constructed answers, 3 human ratings (exploratory) | same benchmark | the same 64 recorded evaluator payloads used only as replay input; no human ratings used |
| Experiments | evaluator audit vs human reference | specification verification + evaluator audit | replay ablation (1,920 sessions), agent-fault injection (1,760), rebuilt grounding probe, historical reproduction, breaker scenarios |
| Contributions | authority-separated design; evaluator audit | verified specification; audit | agent layer + authority matrix + arbitration; ablations/faults; corrections |

## Findings
1. **Distinct experiments and research question.** No experiment, table or figure is shared. The ADCOM paper uses no human-referenced evaluator result.
2. **Shared system description and thematic overlap.** All three describe the same product, its evaluator formula, the frozen PPO policy and the local LLM's role. The ADCOM paper keeps this to one paragraph, and does not name the product (blind review), but a reviewer who sees two or three of the papers could connect them. Reuse of the 64 recorded payloads as replay input is data reuse that should be disclosed to each venue.
3. **Claim interaction.** ICITIIT states that the LLM never decides whether to probe; in the ADCOM configuration a rule-based Strategy Agent may request probes (the LLM still only phrases text). The ADCOM paper therefore describes a different configuration (flag on); the other papers describe the default configuration (flag off). Authors should state this wherever both are submitted, and not reuse the phrase "never decides to probe" for the agent-enabled system.
4. **Earlier ADCOM draft.** The earlier narrowed manuscript (`paper/adcom2027/`) is superseded by this one; if both exist they must not be submitted together. The earlier draft's corrected findings appear here as Sect. 7 only.
5. **ICETC Paper 1.** Its fail-closed and fault-campaign results concern the same family of dependability questions on an earlier code version; this paper does not reuse its experiments, but overlap in topic exists.

## Not resolved here (author decisions)
- Each venue's concurrent-submission and prior-publication policy (not retrieved; the official pages were unreachable from the authoring environment).
- Whether disclosing a shared system and replay data in each submission is sufficient.
- No submission decision is made or implied.
