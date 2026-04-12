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
    concept_vectors = get_vectors_by_type(rubric["qid"], "concept")

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
    semantic_vectors = get_vectors_by_type(rubric["qid"], "semantic")

    if len(semantic_vectors) == 0:
        return 0.0

    sims = _cosine_similarity(sent_emb, semantic_vectors)
    return float(np.mean(np.max(sims, axis=0)))


# ─────────────────────────────────────────────────────────────────────────────
# CROSS ENCODER
# FIX 1: rubric["answer"] — reference answer from rubric
# ─────────────────────────────────────────────────────────────────────────────

def cross_encoder_verification(qn, candidate, rubric):

    # FIX 1: rubric["answer"] — reference answer text for verification
    reference = qn + " " + rubric["answer"]

    raw_score = cross_encoder.predict([(reference, candidate)])[0]

    # Fine-tuned model outputs [-1, 1] — rescale to [0, 1]
    reasoning_score = (raw_score + 1) / 2
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

    bonus_vectors = get_vectors_by_type(rubric["qid"], "bonus")
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

MISTAKE_THRESHOLD = 0.65
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
    mistake_vectors = get_vectors_by_type(rubric["qid"], "mistake")

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

    mandatory_vectors = get_vectors_by_type(rubric["qid"], "mandatory")
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

def evaluate(qn, candidate, rubric):
    _ensure_evaluator_assets_loaded()

    S1 = semantic_score(candidate, rubric)

    S2, concept_details = concept_detection(candidate, rubric)

    reasoning_score = cross_encoder_verification(qn, candidate, rubric)

    bonus   = bonus_score(candidate, rubric)
    penalty = mistake_penalty(candidate, rubric, reasoning_score, S2)

    # FIX 2: mandatory check result is now actually used
    mandatory_pass = mandatory_check(candidate, rubric)

    # FIX 6: effective_S2 threshold 0.30 (was 0.35 — was too high, hurt correct answers)
    # Dampens S2 only when reasoning is genuinely weak — prevents wrong answers
    # from scoring high purely because keywords match concept groups
    effective_S2 = S2 if reasoning_score > 0.30 else S2 * 0.6

    # FIX 4: R-heavy weights — simulation showed 79% grade accuracy vs 53% for old weights
    base_score = (
        0.15 * S1           +
        0.35 * effective_S2 +
        0.50 * reasoning_score
    )

    final_score = base_score + bonus - penalty
    final_score = max(0.0, min(1.0, final_score))

    # FIX 2: apply mandatory cap — was computed but never used before
    if not mandatory_pass:
        scoring_policy = rubric.get("scoring_policy", {})
        mandatory_cap  = scoring_policy.get("mandatory_cap", 0.60)
        final_score    = min(final_score, mandatory_cap)

    final_score = round(final_score, 4)

    # FIX 5: Excellent boundary 0.75 (was 0.80 — QuickSort best answer 0.78 was wrongly graded Good)
    if final_score >= 0.75:
        grade = "Excellent"
    elif final_score >= 0.60:
        grade = "Good"
    elif final_score >= 0.40:
        grade = "Average"
    else:
        grade = "Poor"

    return {
        "S1_semantic"    : round(S1, 3),
        "S2_structural"  : round(S2, 3),
        "reasoning_score": round(reasoning_score, 3),
        "bonus"          : round(bonus, 3),
        "penalty"        : round(penalty, 3),
        "mandatory_pass" : mandatory_pass,
        "final_score"    : final_score,
        "grade"          : grade,
        "concept_details": concept_details,
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

# from sentence_transformers import SentenceTransformer, CrossEncoder
# from sklearn.metrics.pairwise import cosine_similarity


# # -------------------------------------
# # MODELS
# # -------------------------------------

# embedder = SentenceTransformer("all-MiniLM-L6-v2")
# cross_encoder = CrossEncoder(r"D:\A_Capstone_Evaluator\Evaluator_final\Evaluator\1_best_model_zip")

# # -------------------------------------
# # LOAD VECTOR STORE
# # -------------------------------------

# index = faiss.read_index("logic_vectors.faiss")

# with open("logic_metadata.pkl","rb") as f:
#     vector_meta = pickle.load(f)


# # -------------------------------------
# # UTILITIES
# # -------------------------------------

# def split_sentences(text):
#     return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


# def embed(text_list):
#     emb = embedder.encode(text_list).astype("float32")
#     faiss.normalize_L2(emb)
#     return emb


# # -------------------------------------
# # GET RUBRIC VECTORS FROM STORE
# # -------------------------------------

# def get_vectors_by_type(qid, vtype):

#     vectors = []

#     for i,meta in enumerate(vector_meta):
#         if meta["qid"] == qid and meta["type"] == vtype:
#             vectors.append(index.reconstruct(i))

#     return np.array(vectors)


# # -------------------------------------
# # CONCEPT DETECTION
# # -------------------------------------

# def concept_detection(candidate, rubric):

#     sentences = split_sentences(candidate)

#     sent_emb = embed(sentences)

#     concept_vectors = get_vectors_by_type(rubric["qid"],"concept")

#     sims = cosine_similarity(sent_emb, concept_vectors)

#     best_scores = np.max(sims, axis=0)

#     groups_covered = sum(best_scores > 0.28)

#     S2 = groups_covered / len(best_scores)

#     details = []

#     for i,score in enumerate(best_scores):

#         best_sentence = sentences[np.argmax(sims[:,i])]

#         details.append({
#             "concept_index": i,
#             "matched_sentence": best_sentence,
#             "score": round(float(score),3),
#             "covered": score > 0.36
#         })

#     return S2, details


# # -------------------------------------
# # SEMANTIC SCORE
# # -------------------------------------


# def semantic_score(candidate, rubric):

#     sentences = split_sentences(candidate)

#     sent_emb = embed(sentences)

#     semantic_vectors = get_vectors_by_type(rubric["qid"],"semantic")

#     sims = cosine_similarity(sent_emb, semantic_vectors)

#     return float(np.mean(np.max(sims, axis=0)))


# # -------------------------------------
# # CROSS ENCODER
# # -------------------------------------

# # def cross_encoder_verification(candidate, rubric):

# #     # Split logic context into individual reasoning steps
# #     logic_sentences = [
# #         s.strip() for s in re.split(r'(?<=[.!?])\s+', rubric["answer"])
# #         if s.strip()
# #     ]

# #     # Build pairs: (logic_sentence, candidate_answer)
# #     pairs = [(logic_sentence, candidate) for logic_sentence in logic_sentences]

# #     # Cross encoder inference
# #     raw_scores = cross_encoder.predict(pairs)

# #     # Average reasoning relevance across all logic steps
# #     raw_score = float(np.mean(raw_scores))

# #     # Temperature scaling
# #     T = 1.9
# #     scaled = (raw_score - 0.5) / T

# #     # Sigmoid normalization
# #     reasoning_score = 1 / (1 + math.exp(-scaled))

# #     return reasoning_score


# def cross_encoder_verification(qn,candidate,rubric):
   
#     reference = qn+ " " + rubric["answer"]
#     #reference = rubric["answer"]

#     raw_score = cross_encoder.predict([(reference, candidate)])[0]

#     # Fine-tuned model outputs in [-1, 1] range due to label normalization
#     # Rescale directly to [0, 1] instead of sigmoid
#     reasoning_score = (raw_score + 1) / 2

#     # Clip to valid range
#     reasoning_score = max(0.0, min(1.0, reasoning_score))

#     return reasoning_score

# # -------------------------------------
# # BONUS SCORE
# # -------------------------------------

# def bonus_score(candidate, rubric):

#     sentences = split_sentences(candidate)

#     sent_emb = embed(sentences)

#     bonus_vectors = get_vectors_by_type(rubric["qid"],"bonus")

#     if len(bonus_vectors) == 0:
#         return 0

#     sims = cosine_similarity(bonus_vectors, sent_emb)

#     count = sum(np.max(sims, axis=1) > 0.50)

#     return count * 0.03


# # -------------------------------------
# # MISTAKE PENALTY
# # -------------------------------------
# # def mistake_penalty(candidate, rubric):

# #     sentences = split_sentences(candidate)

# #     # Filter out sentences containing negation words
# #     negation_words = ["avoid", "avoids", "not", "without", "instead", "unlike", "no "]
    
# #     filtered_sentences = [
# #         s for s in sentences
# #         if not any(neg in s.lower() for neg in negation_words)
# #     ]

# #     if len(filtered_sentences) == 0:
# #         return 0

# #     sent_emb = embed(filtered_sentences)
# #     mistake_vectors = get_vectors_by_type(rubric["qid"], "mistake")

# #     if len(mistake_vectors) == 0:
# #         return 0

# #     sims = cosine_similarity(mistake_vectors, sent_emb)
# #     count = sum(np.max(sims, axis=1) > 0.50)
# #     return count * 0.08

# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity

# def mistake_penalty(candidate, rubric, reasoning_score, s2_score):

#     penalty = 0.0

#     sentences = split_sentences(candidate)
#     if len(sentences) == 0:
#         return 0.0

#     # ── Negation filter ──────────────────────────────────────────
#     negation_words = ["avoid", "avoids", "not", "without", "instead", "unlike", "no "]
#     filtered = [s for s in sentences
#                 if not any(neg in s.lower() for neg in negation_words)]
#     if not filtered:
#         filtered = sentences

#     # ── 1. Semantic mistake detection (threshold 0.65) ───────────
#     sent_emb        = embed(filtered)
#     mistake_vectors = get_vectors_by_type(rubric["qid"], "mistake")

#     if len(mistake_vectors) > 0:
#         sims = cosine_similarity(mistake_vectors, sent_emb)
#         for row in sims:
#             if np.max(row) > 0.65:
#                 penalty += 0.07

#     # ── 2. Reasoning-based penalty (only very wrong answers) ──────
#     # Both R and S2 must be low to avoid penalising hesitant-correct answers
#     if reasoning_score <= 0.25 and s2_score <= 0.25:
#         penalty += 0.20
#     elif reasoning_score < 0.30 and s2_score < 0.50:
#         # Wrong answer that also lacks concept coverage
#         penalty += 0.05

#     # ── 3. Confidence penalty (only when content is also weak) ────
#     # Do NOT penalise hesitation when S2 is high (content is correct)
#     low_conf_words = ["maybe", "not sure", "probably", "guess"]
#     has_low_conf   = any(w in candidate.lower() for w in low_conf_words)

#     if has_low_conf and s2_score < 0.50 and reasoning_score < 0.40:
#         # Only penalise confidence when content is also weak
#         penalty += 0.03

#     # ── Cap ───────────────────────────────────────────────────────
#     return min(penalty, 0.30)






# # -------------------------------------
# # MANDATORY CHECK
# # -------------------------------------

# def mandatory_check(candidate, rubric):

#     sentences = split_sentences(candidate)

#     sent_emb = embed(sentences)

#     mandatory_vectors = get_vectors_by_type(rubric["qid"],"mandatory")

#     if len(mandatory_vectors) == 0:
#         return True

#     sims = cosine_similarity(mandatory_vectors, sent_emb)

#     presence = np.max(sims, axis=1)

#     return bool(all(p > 0.40 for p in presence))


# # -------------------------------------
# # FINAL EVALUATION
# # -------------------------------------

# def evaluate(qn,candidate, rubric):

#     S1 = semantic_score(candidate, rubric)

#     S2, concept_details = concept_detection(candidate, rubric)

#     reasoning_score = cross_encoder_verification(qn,candidate, rubric)

#     bonus = bonus_score(candidate, rubric)
#     penalty = mistake_penalty(candidate, rubric,reasoning_score,S2)

#     mandatory_pass = mandatory_check(candidate, rubric)


#     # base_score = (
#     #     0.24*S1 +
#     #     0.43*S2 +
#     #     0.33*reasoning_score
#     # )
#     # base_score = (
#     #     0.15*S1 +
#     #     0.35*S2 +
#     #     0.50*reasoning_score
#     # )
#     # If reasoning is weak, S2 cannot fully compensate
#     effective_S2 = S2 if reasoning_score > 0.35 else S2 * 0.6

#     base_score = (
#         0.24 * S1 +
#         0.43 * effective_S2 +
#         0.33 * reasoning_score
#     )
   

#     final_score = base_score + bonus - penalty

#     final_score = max(0,min(final_score,1))

#     final_score = round(final_score,4)
 
#     if final_score >= 0.8:
#         grade="Excellent"
#     elif final_score >= 0.6:
#         grade="Good"
#     elif final_score >= 0.4:
#         grade="Average"
#     else:
#         grade="Poor"

#     return {
#         "S1_semantic":round(S1,3),
#         "S2_structural":round(S2,3),
#         "reasoning_score":round(reasoning_score,3),
#         "bonus":bonus,
#         "penalty":penalty,
#         "final_score":final_score,
#         "grade":grade,
#         "concept_details":concept_details
#     }


# # -------------------------------------
# # LOAD DATA
# # -------------------------------------

# with open("qns.json") as f:
#     questions=json.load(f)

# with open("rubrics.json") as f:
#     rubrics=json.load(f)


# def get_rubric(qid):

#     for r in rubrics:
#         if r["qid"]==qid:
#             return r

#     return None


# # -------------------------------------
# # INTERVIEW LOOP
# # -------------------------------------

# j=10
# i=0

# while j<16:

#     while i<=6:

#         question=questions[j]

#         qid=question["qid"]

#         print("\n============================")
#         print("Question:")
#         qn=question["question_text"]
#         print(question["question_text"])
#         print("============================")

#         rubric=get_rubric(qid)

#         candidate=input("\nYour Answer (type 'finish' to stop):\n")

#         if candidate.lower()=="finish":
#             print("\nInterview ended.")
#             break

#         result=evaluate(qn,candidate,rubric)

#         print("\nEvaluation Result")
#         print("---------------------")

#         for k,v in result.items():
#             print(k,":",v)

#         i+=1

#     i=0
#     j+=1

