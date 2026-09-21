"""Queries, relevance profiles, verification questions and contribution statements for the three PREPAIred papers.
Contribution statements restate what the frozen claim matrices already propose (no new results, no "first" claims); they are the targets of the novelty attack."""

TARGETS = {1: {"pool": 40, "core": 15}, 2: {"pool": 50, "core": 20}, 3: {"pool": 50, "core": 20}}
YEAR_FROM = 2005
PER_QUERY_LIMIT = 25
EXPAND_SEEDS = 4           # top seeds per paper for recommendations + references expansion (budgeted; each seed costs 2 S2 calls)

# Query families follow the task brief (Paper 1: 20, Paper 2: 22, Paper 3: 22). Semantic Scholar is the only retrieval source.
QUERIES = {
    1: ["fault-aware AI orchestration", "graceful degradation in AI systems", "failure isolation in interactive AI systems", "sandboxed code execution security dependability",
        "runtime containment for untrusted code", "Docker sandbox limitations", "container escape isolation evaluation", "LLM feedback containment",
        "LLM authority separation privilege", "trustworthy AI system architecture", "dependable interactive AI", "fault handling in LLM applications",
        "graceful failure in machine learning systems", "infrastructure failure handling AI pipelines", "evaluator outage handling",
        "model serving timeout reliability", "LLM system observability failure detection", "safety oracles untrusted program execution",
        "status code limitations sandbox evaluation", "prompt injection downstream tool authority propagation"],
    2: ["automatic short answer grading", "automatic answer assessment", "technical answer evaluation", "semantic grading of student answers",
        "transformer-based short answer grading", "cross-encoder answer grading", "concept coverage assessment", "reasoning-aware answer evaluation",
        "paraphrase bias in automated grading", "verbosity bias automated grading", "concise correct answer under-scoring", "keyword stuffing automated grading",
        "LLM judge bias", "educational measurement validity automated grading", "psychometric validation automated assessment", "human machine agreement answer scoring",
        "intraclass correlation Krippendorff alpha automated assessment", "measurement invariance automated grading", "metamorphic testing NLP evaluators",
        "adversarial testing automated assessment", "semantic similarity false positives", "entailment versus semantic similarity answer grading"],
    3: ["computerized adaptive testing", "adaptive testing item response theory", "computerized adaptive testing item difficulty selection", "IRT adaptive question selection",
        "reinforcement learning adaptive assessment", "reinforcement learning tutoring", "adaptive tutoring reinforcement learning", "adaptive interviews",
        "interview question difficulty adaptation", "curriculum reinforcement learning", "PPO educational applications", "heuristic adaptive difficulty",
        "controller versus learned policy adaptive systems", "Elo rating adaptive questioning", "knowledge tracing adaptive sequencing", "bandit question selection",
        "rule-based adaptive assessment", "safety shields reinforcement learning", "guardrailed reinforcement learning", "policy constraints reinforcement learning",
        "safe exploration adaptive systems", "learned adaptive difficulty versus heuristic baseline"],
}

# Adversarial queries for the novelty attack (search for work that weakens each claim)
ATTACK_QUERIES = {
    1: ["fault injection evaluation of LLM-based application", "containment evaluation of LLM code execution sandbox", "prompt injection cannot influence score invariance test",
        "failure modes LLM-assisted education system empirical", "graceful degradation LLM tutoring fallback deterministic", "LLM agent sandbox containment attack evaluation",
        "timeout resource cleanup sandbox untrusted code"],
    2: ["short answer grading compared with human raters technical questions", "length bias in automatic answer scoring", "cross-encoder versus lexical baseline short answer grading",
        "LLM judge verbosity bias measured", "question-level clustering bootstrap agreement automated scoring", "keyword stuffing gaming automated essay scoring",
        "hybrid semantic similarity concept coverage grading"],
    3: ["reinforcement learning versus constant policy adaptive difficulty equivalence", "PPO adaptive difficulty tutoring simulated learners",
        "guardrail constrained action reinforcement learning tutoring", "computerized adaptive testing versus reinforcement learning baseline comparison",
        "simulated students reinforcement learning tutoring evaluation validity", "adaptive technical interview difficulty", "Elo rating heuristic versus reinforcement learning adaptive"],
}

CONTRIBUTIONS = {
    1: [("P1-C1", "A claim-scoped fault-injection campaign on an LLM-assisted interview pipeline, with no-fault and oracle-perturbation controls"),
        ("P1-C2", "A containment campaign for a Docker code sandbox with permissive controls and host-side observables"),
        ("P1-C3", "A fixed-evaluator invariance test of score observables against LLM-authored feedback text with a mutation control"),
        ("P1-C4", "Reporting of two defects found and repaired with old-vs-new evidence across two builds"),
        ("P1-C5", "An architecture that combines a code sandbox, deterministic evaluator scoring and an LLM feedback component whose output does not enter the score, evaluated as a system")],
    2: [("P2-C1", "Exploratory agreement of a composite evidence-grounded scorer with human raters on technical interview answers"),
        ("P2-C2", "Question-cluster (two-level) bootstrap intervals for scorer-human agreement"),
        ("P2-C3", "Evidence that a length-only baseline is competitive and the full composite is below simpler components"),
        ("P2-C4", "Category diagnostics showing under-scoring of correct/partial answers and over-scoring of verbose-wrong answers"),
        ("P2-C5", "A hybrid scorer combining sentence-embedding similarity, retrieval-based concept coverage and a cross-encoder reasoning score with a keyword-stuffing guard")],
    3: [("P3-C1", "A registered equivalence test of a PPO difficulty controller versus a state-blind constant action under identical guardrails, in simulation"),
        ("P3-C2", "A guardrail layer with full intervention accounting (explicitly not a formal shield)"),
        ("P3-C3", "Persona-level analysis with training seed as a second random factor, including volatility comparison"),
        ("P3-C4", "Registered sensitivity analyses (O7) that leave the equivalence classification unchanged"),
        ("P3-C5", "A six-dimensional state combining performance, confidence and hesitation signals with progress and difficulty for adaptive interview difficulty control")],
}

PROFILES = {   # group -> (weight, terms)
    1: {"task": (3, ["fault", "failure", "graceful degradation", "resilien", "dependab", "reliab", "fallback", "outage", "fault injection", "chaos"]),
        "method": (2, ["sandbox", "container", "isolation", "containment", "orchestrat", "runtime", "untrusted code", "privilege", "authority"]),
        "baseline": (1, ["prompt injection", "control", "mutation", "invariance", "oracle"]),
        "eval": (2, ["empirical", "evaluation", "experiment", "case study", "campaign", "measured", "benchmark"]),
        "domain": (2, ["llm", "language model", "tutor", "education", "interview", "assessment", "ai system", "machine learning"])},
    2: {"task": (3, ["short answer", "answer grading", "automatic scoring", "automated scoring", "answer evaluation", "essay scoring", "asag", "grading"]),
        "method": (2, ["cross-encoder", "cross encoder", "sentence-bert", "sbert", "semantic similarity", "embedding", "retrieval", "llm judge", "llm-as-a-judge"]),
        "baseline": (2, ["length", "verbosity", "lexical", "bm25", "tf-idf", "baseline"]),
        "eval": (3, ["human rater", "agreement", "kappa", "correlation", "spearman", "validity", "bias", "invariance", "psychometric", "paraphrase", "robust"]),
        "domain": (1, ["technical", "interview", "programming", "computer science", "student"])},
    3: {"task": (3, ["adaptive test", "adaptive difficulty", "adaptive assessment", "computerized adaptive", "adaptive question", "adaptive interview", "difficulty adjust", "tutoring"]),
        "method": (3, ["reinforcement learning", "ppo", "proximal policy", "policy gradient", "bandit", "shield", "guardrail", "safe reinforcement", "constrained"]),
        "baseline": (3, ["elo", "item response", "irt", "heuristic", "baseline", "rule-based", "staircase", "constant"]),
        "eval": (2, ["equivalence", "simulated", "simulation", "student model", "learner model", "statistical", "confidence interval", "evaluation"]),
        "domain": (1, ["student", "learner", "education", "interview", "assessment"])},
}

QUESTIONS = {
    "Q1": "Does this paper actually evaluate automatic technical-answer grading against human ratings? Answer with evidence.",
    "Q2": "Did this study use real users, simulated users, or both?",
    "Q3": "What baselines were actually compared?",
    "Q4": "Does this paper claim reinforcement learning improves adaptive assessment or adaptive tutoring?",
    "Q5": "Does this paper evaluate guardrails, safety layers or shields?",
    "Q6": "Does this paper report answer-length or verbosity bias?",
    "Q7": "What statistical uncertainty analysis was actually performed?",
    "Q8": "What limitation is explicitly acknowledged?",
    "Q9": "Does this paper evaluate behaviour under injected faults, outages or attacks (fault injection, containment, sandbox escape, prompt injection)?",
    "Q10": "Does this paper claim general/universal security or fault tolerance, or does it evaluate only specific attacks or faults?",
    "Q11": "Does this paper compare a learned policy against a heuristic or rule-based adaptive-difficulty baseline?",
    "Q12": "Does this paper use an IRT/CAT formulation, an Elo-style rating, or another heuristic controller for difficulty selection?",
}
QUESTION_SETS = {1: ["Q9", "Q10", "Q3", "Q7", "Q8"], 2: ["Q1", "Q6", "Q3", "Q7", "Q8"], 3: ["Q4", "Q5", "Q11", "Q12", "Q2", "Q7", "Q8"]}
