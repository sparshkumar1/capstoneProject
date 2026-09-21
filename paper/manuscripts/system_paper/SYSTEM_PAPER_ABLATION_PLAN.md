# System paper — ablation plan (PROPOSED; nothing run)

Only ablations that the implementation can support are listed. The final matrix must stay small.

## What the implementation allows today
- **Text/content only** vs **text + audio confidence**: the audio confidence score is the only audio signal that reaches adaptation (via `last_confidence_score`). When it is missing the observation falls back to the performance score. An ablation can therefore switch that input to its fallback.
- **Hesitation** cannot be ablated meaningfully now: the runtime value is `1 − confidence`, not the hesitation scorer's output (`SYSTEM_PAPER_RESEARCH_AUDIT.md`). An ablation of "hesitation" would ablate a transform of confidence. Wiring the real scorer is a change that needs approval and creates a training/runtime mismatch with the frozen checkpoint.
- **Video/engagement** cannot be ablated: not implemented.
- **Guardrail on/off** and **policy type** (constant / rule-based / PPO): possible only after the runtime condition switches exist; the guardrail contribution was examined in simulation in P3, not with people.

## Suggested small matrix (if the study goes ahead)
| Ablation | Purpose | Prerequisite |
|---|---|---|
| Policy: constant vs rule-based vs PPO (with the same guardrail) | Is a learned controller needed? | runtime switches |
| Audio confidence input: on vs replaced by the fallback | Does the audio channel change decisions or outcomes? | study design fixed; logged |
Anything beyond this needs its own justification and sample size; do not add ablations to enlarge the paper.

## Reporting rule
An ablation that changes decisions in logged sessions but not outcomes is reported as such. If the audio input rarely changes the chosen action, say so with the count. No multimodal claim beyond audio + text.
