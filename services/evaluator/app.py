#claude code
# final from claude
# ======================================================================================================
# PrepAIred — Final Evaluator
# Best tuned params: semantic=0.24, concept=0.43, reasoning=0.33, threshold=0.36, bonus=0.03, penalty=0.05
# Fixed: actual_answer field, mandatory cap applied, single concept threshold,
#        R-heavy weights, grade boundary, effective_S2 threshold,
#        confidence words, fast lookup, utf-8 encoding, bonus negation filter
# ======================================================================================================

import json
import re
import numpy as np
import math
import pickle
from collections import defaultdict
from pathlib import Path
from datetime import datetime
import uuid

# ─────────────────────────────────────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent
embedder = None
cross_encoder = None
index = None
vector_meta = None
_lookup = None
_faiss = None


def _ensure_evaluator_assets_loaded():
    global embedder, cross_encoder, index, vector_meta, _lookup, _faiss

    if _faiss is None:
        import faiss as _faiss_module
        _faiss = _faiss_module

    if embedder is None:
        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer("all-MiniLM-L6-v2")

    if cross_encoder is None:
        from sentence_transformers import CrossEncoder
        cross_encoder = CrossEncoder(str(BASE_DIR / "models" / "tuned_model2"))

    if index is None:
        index = _faiss.read_index(str(BASE_DIR / "assets" / "logic_vectors.faiss"))

    if vector_meta is None:
        with open(BASE_DIR / "assets" / "logic_metadata.pkl", "rb") as f:
            vector_meta = pickle.load(f)

    if _lookup is None:
        _lookup = defaultdict(list)
        for _i, _meta in enumerate(vector_meta):
            _lookup[(_meta["qid"], _meta["type"])].append(_i)


def get_vectors_by_type(qid, vtype):
    _ensure_evaluator_assets_loaded()
    indices = _lookup[(qid, vtype)]
    if not indices:
        return np.array([])
    return np.array([index.reconstruct(i) for i in indices])


# ─────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def split_sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


def _cosine_similarity(a, b):
    from sklearn.metrics.pairwise import cosine_similarity
    return cosine_similarity(a, b)


def embed(text_list):
    _ensure_evaluator_assets_loaded()
    emb = embedder.encode(text_list).astype("float32")
    _faiss.normalize_L2(emb)
    return emb


# ─────────────────────────────────────────────────────────────────────────────
# CONCEPT DETECTION
# FIX 3: Single threshold 0.30 used consistently for both S2 count and details
# ─────────────────────────────────────────────────────────────────────────────

CONCEPT_THRESHOLD = 0.30   # single source of truth

def concept_detection(candidate, rubric):

    sentences = split_sentences(candidate)
    if not sentences:
        return 0.0, []

    sent_emb       = embed(sentences)
    qid = rubric.get("qid")
    concept_vectors = get_vectors_by_type(qid, "concept") if qid else []
    if len(concept_vectors) == 0 and rubric.get("expected_concepts"):
        concept_vectors = embed(rubric["expected_concepts"])

    if len(concept_vectors) == 0:
        return 0.0, []

    sims        = _cosine_similarity(sent_emb, concept_vectors)
    best_scores = np.max(sims, axis=0)

    # FIX 3: same threshold for S2 count and details display
    groups_covered = int(sum(best_scores > CONCEPT_THRESHOLD))
    S2             = groups_covered / len(best_scores)

    details = []
    for i, score in enumerate(best_scores):
        best_sentence = sentences[int(np.argmax(sims[:, i]))]
        details.append({
            "concept_index"    : i,
            "matched_sentence" : best_sentence,
            "score"            : round(float(score), 3),
            "covered"          : bool(score > CONCEPT_THRESHOLD),   # FIX 3
        })

    return S2, details


# ─────────────────────────────────────────────────────────────────────────────
# SEMANTIC SCORE
# ─────────────────────────────────────────────────────────────────────────────

def semantic_score(candidate, rubric):

    sentences = split_sentences(candidate)
    if not sentences:
        return 0.0

    sent_emb        = embed(sentences)
    qid = rubric.get("qid")
    semantic_vectors = get_vectors_by_type(qid, "semantic") if qid else []
    if len(semantic_vectors) == 0 and rubric.get("expected_concepts"):
        semantic_vectors = embed(rubric["expected_concepts"])

    if len(semantic_vectors) == 0:
        return 0.0

    sims = _cosine_similarity(sent_emb, semantic_vectors)
    return float(np.mean(np.max(sims, axis=0)))


# ─────────────────────────────────────────────────────────────────────────────
# CROSS ENCODER
# FIX 1: rubric["answer"] — reference answer from rubric
# ─────────────────────────────────────────────────────────────────────────────

def cross_encoder_verification(qn, candidate, rubric):
    reference = qn + " " + str(rubric.get("answer", ""))
    raw_score = float(cross_encoder.predict([(reference, candidate)])[0])

    # Calibrate continuous regression output: baseline floor is ~0.20 for unrelated/noise pairs,
    # 0.40-0.55 for partial/weak reasoning, and 0.70-0.95 for strong logical entailment.
    reasoning_score = (raw_score - 0.20) / 0.70
    return max(0.0, min(1.0, reasoning_score))


# ─────────────────────────────────────────────────────────────────────────────
# BONUS SCORE
# Added negation filter so "avoid X" does not trigger bonus for X
# ─────────────────────────────────────────────────────────────────────────────

BONUS_WEIGHT    = 0.03
BONUS_THRESHOLD = 0.50

def bonus_score(candidate, rubric):

    sentences = split_sentences(candidate)
    if not sentences:
        return 0.0

    qid = rubric.get("qid")
    bonus_vectors = get_vectors_by_type(qid, "bonus") if qid else []
    if len(bonus_vectors) == 0:
        return 0.0

    # Filter negation sentences so "avoid X" does not get bonus for X
    negation_words = ["avoid", "avoids", "not", "without", "instead", "unlike", "no "]
    filtered = [s for s in sentences
                if not any(neg in s.lower() for neg in negation_words)]
    if not filtered:
        return 0.0

    sent_emb = embed(filtered)
    sims     = _cosine_similarity(bonus_vectors, sent_emb)
    count    = int(sum(np.max(sims, axis=1) > BONUS_THRESHOLD))
    return count * BONUS_WEIGHT


# ─────────────────────────────────────────────────────────────────────────────
# MISTAKE PENALTY
# FIX 7: umm/uhh/uh added to confidence words
# Threshold 0.65 — prevents false positives on correct answers
# ─────────────────────────────────────────────────────────────────────────────

MISTAKE_THRESHOLD = 0.55
MISTAKE_WEIGHT    = 0.07
PENALTY_CAP       = 0.30

def mistake_penalty(candidate, rubric, reasoning_score, s2_score):

    penalty   = 0.0
    sentences = split_sentences(candidate)
    if not sentences:
        return 0.0

    # ── Negation filter ──────────────────────────────────────────────────────
    negation_words = ["avoid", "avoids", "not", "without", "instead", "unlike", "no "]
    filtered       = [s for s in sentences
                      if not any(neg in s.lower() for neg in negation_words)]
    if not filtered:
        filtered = sentences   # fallback — do not discard all sentences

    # ── 1. Semantic mistake detection ────────────────────────────────────────
    sent_emb        = embed(filtered)
    qid = rubric.get("qid")
    mistake_vectors = get_vectors_by_type(qid, "mistake") if qid else []

    if len(mistake_vectors) > 0:
        sims = _cosine_similarity(mistake_vectors, sent_emb)
        for row in sims:
            if np.max(row) > MISTAKE_THRESHOLD:
                penalty += MISTAKE_WEIGHT

    # ── 2. Reasoning-based penalty (only very wrong answers) ─────────────────
    if reasoning_score <= 0.25 and s2_score <= 0.25:
        penalty += 0.20   # clearly wrong on both dimensions
    elif reasoning_score < 0.30 and s2_score < 0.50:
        penalty += 0.05   # wrong answer with poor concept coverage too

    # ── 3. Confidence penalty (only when content is also weak) ───────────────
    # FIX 7: added umm / uhh / uh — most common interview hesitation words
    low_conf_words = ["maybe", "not sure", "probably", "guess", "umm", "uhh", "uh"]
    has_low_conf   = any(w in candidate.lower() for w in low_conf_words)

    if has_low_conf and s2_score < 0.50 and reasoning_score < 0.40:
        penalty += 0.03   # only penalise hesitation when content is also weak

    return min(penalty, PENALTY_CAP)


# ─────────────────────────────────────────────────────────────────────────────
# MANDATORY CHECK
# ─────────────────────────────────────────────────────────────────────────────

MANDATORY_THRESHOLD = 0.40

def mandatory_check(candidate, rubric):

    sentences = split_sentences(candidate)
    if not sentences:
        return False

    qid = rubric.get("qid")
    mandatory_vectors = get_vectors_by_type(qid, "mandatory") if qid else []
    if len(mandatory_vectors) == 0 and rubric.get("mandatory_concepts"):
        mandatory_vectors = embed(rubric["mandatory_concepts"])

    if len(mandatory_vectors) == 0:
        return True   # no mandatory concepts defined — always passes

    sent_emb = embed(sentences)
    sims     = _cosine_similarity(mandatory_vectors, sent_emb)
    presence = np.max(sims, axis=1)
    return bool(all(p > MANDATORY_THRESHOLD for p in presence))


# ─────────────────────────────────────────────────────────────────────────────
# FINAL EVALUATION
# FIX 2: mandatory_pass now applied to final_score
# FIX 4: R-heavy weights 0.15 / 0.35 / 0.50
# FIX 5: grade boundary 0.75 for Excellent
# FIX 6: effective_S2 threshold lowered to 0.30
# ─────────────────────────────────────────────────────────────────────────────

def _extract_concept_texts(rubric):
    """Extract human-readable concept texts from rubric logic markers."""
    lm = rubric.get("logic_markers_covered", {})
    concepts = []
    if isinstance(lm, dict):
        for item in lm.get("concept_groups", []):
            if isinstance(item, str):
                concepts.append(item)
            elif isinstance(item, list) and item:
                concepts.append(item[0])
    if not concepts:
        for item in rubric.get("expected_concepts", []):
            if isinstance(item, str):
                concepts.append(item)
    if not concepts:
        for item in rubric.get("semantic_coverage", []):
            if isinstance(item, str):
                concepts.append(item)
    return concepts


def _detect_misconceptions(candidate, rubric):
    """Identify specific asserted misconception texts from rubric."""
    sentences = split_sentences(candidate)
    if not sentences:
        return []

    negation_words = ["avoid", "avoids", "not", "without", "instead", "unlike", "no "]
    filtered = [s for s in sentences if not any(neg in s.lower() for neg in negation_words)]
    if not filtered:
        filtered = sentences

    sent_emb = embed(filtered)
    qid = rubric.get("qid")
    mistake_vectors = get_vectors_by_type(qid, "mistake") if qid else []
    detected = []

    mistake_texts = rubric.get("common_mistakes_addressed", []) or rubric.get("common_mistakes", [])
    if len(mistake_vectors) > 0 and len(mistake_texts) >= len(mistake_vectors):
        sims = _cosine_similarity(mistake_vectors, sent_emb)
        for idx, row in enumerate(sims):
            if np.max(row) > MISTAKE_THRESHOLD:
                detected.append(mistake_texts[idx])
    elif mistake_texts:
        m_vecs = embed(mistake_texts)
        sims = _cosine_similarity(m_vecs, sent_emb)
        for idx, row in enumerate(sims):
            if np.max(row) > MISTAKE_THRESHOLD:
                detected.append(mistake_texts[idx])
    return detected


def evaluate(qn, candidate, rubric):
    _ensure_evaluator_assets_loaded()

    candidate_text = str(candidate).strip()
    sentences = split_sentences(candidate_text)

    S1 = semantic_score(candidate_text, rubric)
    S2, concept_details = concept_detection(candidate_text, rubric)
    reasoning_score = cross_encoder_verification(qn, candidate_text, rubric)

    bonus = bonus_score(candidate_text, rubric)
    penalty = mistake_penalty(candidate_text, rubric, reasoning_score, S2)
    mandatory_pass = mandatory_check(candidate_text, rubric)

    # Attach concept texts to concept details
    concept_texts = _extract_concept_texts(rubric)
    for i, detail in enumerate(concept_details):
        if i < len(concept_texts):
            detail["concept_text"] = concept_texts[i]
        else:
            detail["concept_text"] = f"Concept {i + 1}"

    # Dampen S2 when reasoning is weak (prevents keyword stuffing)
    effective_S2 = S2 if reasoning_score > 0.30 else S2 * 0.60

    base_score = (
        0.15 * S1 +
        0.35 * effective_S2 +
        0.50 * reasoning_score
    )

    final_score = base_score + bonus - penalty
    final_score = max(0.0, min(1.0, final_score))

    # Apply mandatory cap if mandatory concept was missed
    if not mandatory_pass:
        scoring_policy = rubric.get("scoring_policy", {})
        mandatory_cap = scoring_policy.get("mandatory_cap", 0.60)
        final_score = min(final_score, mandatory_cap)

    final_score = round(final_score, 4)

    # Grade determination
    if final_score >= 0.75:
        grade = "Excellent"
    elif final_score >= 0.60:
        grade = "Good"
    elif final_score >= 0.40:
        grade = "Average"
    else:
        grade = "Poor"

    # Concept breakdown
    correct_claims = [d["concept_text"] for d in concept_details if d.get("covered")]
    missing_concepts = [d["concept_text"] for d in concept_details if not d.get("covered")]
    incorrect_claims = _detect_misconceptions(candidate_text, rubric)

    # Weakest gap & strong points
    if missing_concepts:
        weakest_gap = missing_concepts[0]
    elif incorrect_claims:
        weakest_gap = f"Misconception: {incorrect_claims[0]}"
    elif not mandatory_pass:
        weakest_gap = "Omitted mandatory requirement specified in rubric"
    elif reasoning_score < 0.50:
        weakest_gap = "Reasoning depth and mechanistic explanation"
    else:
        weakest_gap = "None — comprehensive answer"

    strong_points = correct_claims[:3] if correct_claims else ["General topic familiarity"]

    # Separate diagnostic metrics (NEVER added as positive bonus to technical score)
    depth = round(min(1.0, (len(sentences) / 4.0) * 0.35 + S2 * 0.65), 3)

    filler_words = ["umm", "uhh", "uh", "maybe", "like", "sort of", "i guess"]
    filler_count = sum(1 for w in filler_words if w in candidate_text.lower())
    communication = round(max(0.2, min(1.0, 1.0 - filler_count * 0.15 + (0.1 if len(sentences) >= 2 else 0.0))), 3)

    eval_confidence = round(0.85 + 0.10 * (1.0 if len(sentences) >= 2 else 0.5), 3)

    return {
        "question_text": qn,
        "candidate_answer": candidate_text,
        "expected_concepts": concept_texts,
        "candidate_claims": sentences,
        "correct_claims": correct_claims,
        "incorrect_claims": incorrect_claims,
        "missing_concepts": missing_concepts,
        "weakest_gap": weakest_gap,
        "strong_points": strong_points,
        "reasoning_quality": round(reasoning_score, 3),
        "technical_correctness": final_score,
        "concept_coverage": round(S2, 3),
        "relevance": round(S1, 3),
        "depth": depth,
        "communication": communication,
        "evaluation_confidence": eval_confidence,
        "S1_semantic": round(S1, 3),
        "S2_structural": round(S2, 3),
        "reasoning_score": round(reasoning_score, 3),
        "bonus": round(bonus, 3),
        "penalty": round(penalty, 3),
        "mandatory_pass": mandatory_pass,
        "final_score": final_score,
        "question_score": final_score,
        "grade": grade,
        "concept_details": concept_details,
        "decision_source": "evaluator_cross_encoder",
    }


# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# FIX 9: encoding="utf-8" on all file opens — prevents crash on Windows
#        with Unicode characters in rubric text (em dashes, quotes etc.)
# ─────────────────────────────────────────────────────────────────────────────

with open(BASE_DIR / "assets" / "qns.json", encoding="utf-8") as f:
    questions = json.load(f)

with open(BASE_DIR / "assets" / "rubrics.json", encoding="utf-8") as f:
    rubrics = json.load(f)


def get_rubric(qid):
    qid_norm = str(qid)
    for r in rubrics:
        if str(r.get("qid")) == qid_norm:
            return r
    return None

"""
j = 10
i = 0

while j < 16:

    while i <= 6:

        question = questions[j]
        qid      = question["qid"]

        print("\\n============================")
        print("Question:")
        qn = question["question_text"]
        print(qn)
        print("============================")

        rubric = get_rubric(qid)

        if rubric is None:
            print(f"[WARNING] No rubric found for qid={qid}, skipping.")
            i += 1
            continue

        candidate = input("\\nYour Answer (type 'finish' to stop):\\n")

        if candidate.lower() == "finish":
            print("\\nInterview ended.")
            break

        result = evaluate(qn, candidate, rubric)

        print("\\nEvaluation Result")
        print("---------------------")
        for k, v in result.items():
            print(k, ":", v)

        i += 1

    i  = 0
    j += 1
"""









# ============================================================================
# API INTEGRATION: QUESTION SELECTOR + AUDIO AGENT
# ============================================================================
#
# FLOW:
#   1. Question Selector → /api/evaluator/set-question
#      Sends: qid, question_text, topic, difficulty, blooms_level
#      Stored in current_session: question metadata + rubric
#
#   2. Audio Agent → /api/evaluator/evaluate-answer
#      Sends: transcript (candidate's spoken answer)
#      Uses: qn (from current_session) + rubric (from current_session) + transcript
#      Calls: evaluate(qn, transcript, rubric)
#      Returns: {S1, S2, reasoning, bonus, penalty, final_score, grade, ...}
#
# EVALUATE FUNCTION SIGNATURE:
#   evaluate(qn, candidate, rubric) → result
#   where:
#     qn = question text (used by cross_encoder_verification)
#     candidate = candidate's answer transcript (from audio)
#     rubric = evaluation rubric (concept/semantic/mistake vectors)
#
# ============================================================================

try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

    class _DummyFlask:
        def __init__(self, *_args, **_kwargs):
            pass

        def route(self, *_args, **_kwargs):
            def _decorator(func):
                return func
            return _decorator

    Flask = _DummyFlask
    request = None

    def jsonify(payload):
        return payload

app = Flask(__name__) if FLASK_AVAILABLE else Flask()

# Session storage for current question and rubric
current_session = {
    "session_id": None,
    "question": None,           # Full question metadata from selector
    "rubric": None,             # Evaluation rubric for concept matching
    "qid": None,                # Question ID
    "timestamp": None,
    "last_result": None
}


# ─────────────────────────────────────────────────────────────────────────────
# API ENDPOINT 1: SET CURRENT QUESTION (from intelligent selector)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/evaluator/set-question", methods=["POST"])
def set_current_question():
    """
    Accept question and rubric from intelligent question selector
    
    Input JSON:
    {
        "qid": "100",
        "question_text": "...",
        "topic": "Arrays",
        "difficulty": 0.5,
        "blooms_level": "Apply",
        "session_id": "uuid"
    }
    
    Returns: confirmation with session details
    """
    try:
        data = request.json
        qid = data.get("qid")
        
        if not qid:
            return {"error": "Missing qid"}, 400
        
        # Get rubric for this question
        rubric = get_rubric(qid)
        if not rubric:
            return {"error": f"No rubric found for qid={qid}"}, 404
        
        # Store in session
        session_id = data.get("session_id") or str(uuid.uuid4())
        
        current_session.update({
            "session_id": session_id,
            "question": data,
            "rubric": rubric,
            "qid": qid,
            "timestamp": datetime.now().isoformat(),
            "last_result": None
        })
        
        # Save to JSON for persistence
        _save_session_to_json()
        
        return {
            "status": "success",
            "message": f"Question {qid} loaded for evaluation",
            "session_id": session_id,
            "question_text": data.get("question_text"),
            "topic": data.get("topic"),
            "difficulty": data.get("difficulty"),
            "blooms_level": data.get("blooms_level")
        }, 200
        
    except Exception as e:
        return {"error": str(e), "status": "failed"}, 500


# ─────────────────────────────────────────────────────────────────────────────
# API ENDPOINT 2: EVALUATE ANSWER (from audio agent)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/evaluator/evaluate-answer", methods=["POST"])
def evaluate_answer():
    """
    Accept candidate answer transcript from audio agent and evaluate
    
    FLOW:
    ────────────────────────────────────────────────────────────────
    1. Audio Agent sends: {"transcript": "candidate's answer", ...}
    2. We retrieve stored question and rubric from current_session
    3. We call: evaluate(qn, transcript, rubric)
    4. We return: Full evaluation with scores
    ────────────────────────────────────────────────────────────────
    
    Input JSON:
    {
        "transcript": "The answer text from audio transcription",
        "session_id": "uuid"
    }
    
    Returns: Full evaluation result with score, grade, and analysis
    
    PARAMETER MAPPING FOR evaluate():
    ────────────────────────────────────────────────────────────────
      evaluate(qn, candidate, rubric)
        ↓        ↓     ↓        ↓
        |        |     |        └─ current_session["rubric"]
        |        |     └─ transcript (from audio agent)
        |        └─ current_session["question"]["question_text"]
        └─ Question text (required for reasoning verification)
    ────────────────────────────────────────────────────────────────
    """
    try:
        data = request.json
        transcript = data.get("transcript", "").strip()
        session_id = data.get("session_id")
        
        if not transcript:
            return {"error": "Missing transcript"}, 400
        
        if not session_id and not current_session["qid"]:
            return {"error": "No question loaded. Call set-question first."}, 400
        
        # Verify question is loaded in current session
        if not current_session["qid"]:
            return {"error": "No question in current session"}, 400
        
        # ─────────────────────────────────────────────────────────────
        # BUILD PARAMETERS FOR evaluate() FUNCTION
        # ─────────────────────────────────────────────────────────────
        qid = current_session["qid"]
        qn = current_session["question"].get("question_text", "")      # Param 1: question text
        candidate = transcript                                          # Param 2: candidate answer
        rubric = current_session["rubric"]                              # Param 3: evaluation rubric
        
        if not qn:
            return {"error": "Question text is empty"}, 400
        if not rubric:
            return {"error": "Rubric is missing"}, 400
        
        # ─────────────────────────────────────────────────────────────
        # CALL EVALUATION PIPELINE
        # ─────────────────────────────────────────────────────────────
        # This function:
        #   1. Computes S1 (semantic score) from candidate + rubric
        #   2. Computes S2 (structural/concept) from candidate + rubric
        #   3. Computes reasoning score from qn + candidate + rubric
        #   4. Computes bonus and penalty
        #   5. Applies mandatory check and weighting
        #   6. Returns final score and grade
        
        evaluation_result = evaluate(qn, candidate, rubric)
        
        # ─────────────────────────────────────────────────────────────
        # ENRICH RESULT WITH METADATA
        # ─────────────────────────────────────────────────────────────
        
        evaluation_result.update({
            "qid": qid,
            "session_id": current_session["session_id"],
            "timestamp": datetime.now().isoformat(),
            "candidate_answer": transcript,
            "question_text": qn,
            "topic": current_session["question"].get("topic"),
            "difficulty": current_session["question"].get("difficulty"),
            "blooms_level": current_session["question"].get("blooms_level")
        })
        
        current_session["last_result"] = evaluation_result
        _save_result_to_json(evaluation_result)
        
        return {
            "status": "success",
            "evaluation": evaluation_result
        }, 200
        
    except Exception as e:
        import traceback
        print(f"[EVALUATOR] Error in evaluate_answer: {e}")
        traceback.print_exc()
        return {"error": str(e), "status": "failed"}, 500


# ─────────────────────────────────────────────────────────────────────────────
# API ENDPOINT 3: GET LAST EVALUATION RESULT
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/evaluator/last-result", methods=["GET"])
def get_last_result():
    """
    Get the evaluation result from last answered question
    
    Returns: Last evaluation result or empty if no evaluation done yet
    """
    if not current_session["last_result"]:
        return {"error": "No evaluation result available"}, 404
    
    return {
        "status": "success",
        "result": current_session["last_result"]
    }, 200


# ─────────────────────────────────────────────────────────────────────────────
# API ENDPOINT 4: GET CURRENT QUESTION
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/evaluator/current-question", methods=["GET"])
def get_current_question():
    """
    Get the currently loaded question
    
    Returns: Current question details
    """
    if not current_session["question"]:
        return {"error": "No question currently loaded"}, 404
    
    return {
        "status": "success",
        "question": current_session["question"],
        "session_id": current_session["session_id"],
        "timestamp": current_session["timestamp"]
    }, 200


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS: JSON PERSISTENCE
# ─────────────────────────────────────────────────────────────────────────────

def _save_session_to_json():
    """Save current session to JSON file"""
    try:
        out_dir = BASE_DIR / "evaluation_sessions"
        filename = out_dir / f"{current_session['session_id']}_session.json"
        import os
        os.makedirs(out_dir, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "session_id": current_session["session_id"],
                "question": current_session["question"],
                "qid": current_session["qid"],
                "timestamp": current_session["timestamp"]
            }, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Could not save session: {e}")


def _save_result_to_json(result):
    """Save evaluation result to JSON file"""
    try:
        out_dir = BASE_DIR / "evaluation_results"
        filename = out_dir / f"{current_session['session_id']}_result.json"
        import os
        os.makedirs(out_dir, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Could not save result: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# INTEGRATION HELPER: Call from question selector
# ─────────────────────────────────────────────────────────────────────────────

def load_and_prepare_question(qid, question_data, session_id=None):
    """
    Prepare question for evaluation (can be called programmatically)
    
    Args:
        qid: Question ID
        question_data: Question object from selector
        session_id: Optional session ID
    
    Returns:
        True if successful, False otherwise
    """
    rubric = get_rubric(qid)
    if not rubric:
        print(f"ERROR: No rubric found for qid={qid}")
        return False
    
    session_id = session_id or str(uuid.uuid4())
    
    current_session.update({
        "session_id": session_id,
        "question": question_data.__dict__ if hasattr(question_data, '__dict__') else question_data,
        "rubric": rubric,
        "qid": qid,
        "timestamp": datetime.now().isoformat()
    })
    
    _save_session_to_json()
    return True


def evaluate_candidate_answer(transcript, session_id=None):
    """
    Evaluate candidate answer (can be called programmatically)
    
    Args:
        transcript: Candidate's answer text
        session_id: Optional session ID
    
    Returns:
        Evaluation result dictionary
    """
    if not current_session["qid"]:
        return {"error": "No question loaded"}
    
    qid = current_session["qid"]
    qn = current_session["question"].get("question_text", "")
    rubric = current_session["rubric"]
    
    result = evaluate(qn, transcript, rubric)
    
    result.update({
        "qid": qid,
        "session_id": current_session["session_id"],
        "timestamp": datetime.now().isoformat(),
        "candidate_answer": transcript,
        "question_text": qn
    })
    
    current_session["last_result"] = result
    _save_result_to_json(result)
    
    return result


# ─────────────────────────────────────────────────────────────────────────────
# RUN FLASK APP (if executed directly)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not FLASK_AVAILABLE:
        print("Flask is not installed. API server cannot be started from this module.")
    else:
        print("Evaluator API starting on http://localhost:5000")
        print("Available endpoints:")
        print("  POST /api/evaluator/set-question - Load question from selector")
        print("  POST /api/evaluator/evaluate-answer - Evaluate answer transcript")
        print("  GET  /api/evaluator/last-result - Get last evaluation")
        print("  GET  /api/evaluator/current-question - Get current question")
        app.run(debug=True, port=5000)
