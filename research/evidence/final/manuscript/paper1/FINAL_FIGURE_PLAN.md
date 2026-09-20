# Paper 1 - figure plan (no figure fabricated; all from stored artifacts)
F1 System/authority diagram (architecture): components, which paths can write score/difficulty/best-answer, and the LLM feedback and follow-up channels (follow-up marked as a dependency). Source: code reading, channel_enumeration.json (47 rows). Caption meaning: what the invariance test does and does not cover.
F2 X1-C containment matrix: rows = attacks, columns = shipped vs permissive, cell = criteria met/breach counts (A and B side by side); annotate the four attacks where status was identical. Source: environment_and_verdicts.json (both builds).
F3 X1-A scenario grid, build A vs build B: rows = scenarios, cells = criteria met (0-5) with failed criterion named; timing strip for FLT-01 and FLT-07b showing distance to bound. Source: verdicts.json, runs.jsonl seconds.
F4 X1-B valid-pair funnel: pairs run -> LLM-produced both arms -> observables equal, build A vs B; mutation-control bar. Source: summary.json, pairs.jsonl.
F5 Latency: shipped 6 s client timeout vs measured local generation time (19-30 s valid benign arm in v3; 13-21 s in the earlier pilot). Source: pairs.jsonl seconds fields. Descriptive only.
