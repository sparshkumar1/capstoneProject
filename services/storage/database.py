"""
database.py — SQLite Persistence Layer for PrepAIred Learning History.

Authoritative source of truth for:
- Candidate identity (cross-session email lookup)
- Multi-attempt response history (lifetime & session attempt numbering)
- Deterministic technical best-answer tracking (highest validated evaluator score)
- Evaluator-grounded comparison facts (score delta, resolved/remaining concepts)
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from services.storage.best_answer import select_best

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
# PREPAIRED_DB_PATH lets a deployment point this at a mounted persistent volume
# (e.g. the cloud deployment's persistent VM disk) instead of the repo-relative default.
DEFAULT_DB_PATH = Path(os.getenv("PREPAIRED_DB_PATH", "")) if os.getenv("PREPAIRED_DB_PATH") else ROOT_DIR / "data" / "prepaired.db"

_LOCK = threading.Lock()


def get_connection(db_path: Optional[Path | str] = None) -> sqlite3.Connection:
    """Open a SQLite connection configured for this app's concurrency model.

    Args:
        db_path (Optional[Path | str]): Database file path; defaults to
            `DEFAULT_DB_PATH` (repo-relative or `PREPAIRED_DB_PATH` env
            var). Parent directories are created if missing.

    Returns:
        sqlite3.Connection: Connection with `row_factory = sqlite3.Row`,
            WAL journal mode, and foreign keys enabled.
    """
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db(db_path: Optional[Path | str] = None) -> None:
    """Create the database schema and indices if they don't already exist.

    Creates `candidates`, `sessions`, `question_attempts`, `bookmarks`, and
    `study_goals` tables plus their indices. Idempotent (`CREATE TABLE/
    INDEX IF NOT EXISTS`).

    Args:
        db_path (Optional[Path | str]): Database file path; defaults to
            `DEFAULT_DB_PATH`.

    Returns:
        None.
    """
    with _LOCK:
        conn = get_connection(db_path)
        try:
            with conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS candidates (
                        id TEXT PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        college TEXT DEFAULT '',
                        year TEXT DEFAULT '',
                        roll TEXT DEFAULT '',
                        primary_lang TEXT DEFAULT 'C',
                        experience TEXT DEFAULT 'intermediate',
                        is_admin INTEGER DEFAULT 0,
                        created_at TEXT NOT NULL,
                        last_login_at TEXT NOT NULL
                    );
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);")

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        candidate_id TEXT NOT NULL REFERENCES candidates(id),
                        interview_mode TEXT DEFAULT 'standard',
                        c_topics TEXT DEFAULT '[]',
                        dsa_topics TEXT DEFAULT '[]',
                        duration_minutes INTEGER DEFAULT 30,
                        num_questions INTEGER DEFAULT 15,
                        start_difficulty INTEGER DEFAULT 2,
                        status TEXT DEFAULT 'created',
                        overall_score REAL DEFAULT 0.0,
                        created_at TEXT NOT NULL,
                        completed_at TEXT
                    );
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_candidate ON sessions(candidate_id);")

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS question_attempts (
                        id TEXT PRIMARY KEY,
                        candidate_id TEXT NOT NULL REFERENCES candidates(id),
                        session_id TEXT NOT NULL,
                        question_id TEXT NOT NULL,
                        question_version TEXT DEFAULT 'v1',
                        attempt_number INTEGER NOT NULL,
                        session_attempt_number INTEGER NOT NULL,
                        attempt_type TEXT NOT NULL DEFAULT 'primary',
                        parent_question_id TEXT,
                        answer_type TEXT NOT NULL DEFAULT 'verbal',
                        transcript TEXT DEFAULT '',
                        code_submitted TEXT DEFAULT '',
                        raw_score REAL NOT NULL,
                        validated_score REAL NOT NULL,
                        is_best INTEGER NOT NULL DEFAULT 0,
                        covered_concepts TEXT DEFAULT '[]',
                        missing_concepts TEXT DEFAULT '[]',
                        incorrect_claims TEXT DEFAULT '[]',
                        weakest_gap TEXT DEFAULT '',
                        strong_points TEXT DEFAULT '[]',
                        evaluation_confidence REAL DEFAULT 0.85,
                        feedback_json TEXT DEFAULT '{}',
                        created_at TEXT NOT NULL
                    );
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_attempts_candidate_question 
                    ON question_attempts(candidate_id, question_id);
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_attempts_candidate_question_best 
                    ON question_attempts(candidate_id, question_id, is_best);
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_attempts_session
                    ON question_attempts(session_id);
                    """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS bookmarks (
                        id TEXT PRIMARY KEY,
                        candidate_id TEXT NOT NULL REFERENCES candidates(id),
                        question_id TEXT NOT NULL,
                        note TEXT DEFAULT '',
                        created_at TEXT NOT NULL,
                        UNIQUE(candidate_id, question_id)
                    );
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_bookmarks_candidate
                    ON bookmarks(candidate_id);
                    """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS study_goals (
                        candidate_id TEXT PRIMARY KEY REFERENCES candidates(id),
                        target_date TEXT DEFAULT '',
                        minutes_per_day INTEGER DEFAULT 30,
                        plan_json TEXT DEFAULT '{}',
                        updated_at TEXT NOT NULL
                    );
                    """
                )
        finally:
            conn.close()


# ── Candidate Identity ────────────────────────────────────────────────────────

def get_or_create_candidate(
    email: str,
    name: str,
    college: str = "",
    year: str = "",
    roll: str = "",
    primary_lang: str = "C",
    experience: str = "intermediate",
    is_admin: bool = False,
    db_path: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """Look up a candidate by normalized email, or create a new persistent record.

    Guarantees the same (normalized) email always returns the same
    persistent candidate ID across all sessions. On an existing match,
    updates `last_login_at` and any non-empty profile fields supplied.

    Args:
        email (str): Candidate's email; normalized (trimmed, lowercased).
            An empty value gets a generated guest email.
        name (str): Display name.
        college (str): College/institution (optional).
        year (str): Academic year (optional).
        roll (str): Roll number (optional).
        primary_lang (str): Preferred language (default "C").
        experience (str): Experience level (default "intermediate").
        is_admin (bool): Whether to grant admin status (only ever upgrades,
            never revokes, an existing record).
        db_path (Optional[Path | str]): Database file path override.

    Returns:
        Dict[str, Any]: The full candidate row (existing, updated, or
            newly created).
    """
    norm_email = (email or "").strip().lower()
    if not norm_email:
        norm_email = f"guest_{uuid.uuid4().hex[:8]}@prepaired.local"

    now_iso = datetime.now(UTC).isoformat()

    with _LOCK:
        conn = get_connection(db_path)
        try:
            with conn:
                row = conn.execute(
                    "SELECT * FROM candidates WHERE email = ?;", (norm_email,)
                ).fetchone()

                if row:
                    cid = row["id"]
                    conn.execute(
                        """
                        UPDATE candidates 
                        SET last_login_at = ?,
                            name = COALESCE(NULLIF(?, ''), name),
                            college = COALESCE(NULLIF(?, ''), college),
                            year = COALESCE(NULLIF(?, ''), year),
                            roll = COALESCE(NULLIF(?, ''), roll),
                            primary_lang = COALESCE(NULLIF(?, ''), primary_lang),
                            experience = COALESCE(NULLIF(?, ''), experience),
                            is_admin = CASE WHEN ? THEN 1 ELSE is_admin END
                        WHERE id = ?;
                        """,
                        (now_iso, name, college, year, roll, primary_lang, experience, is_admin, cid),
                    )
                    updated = conn.execute("SELECT * FROM candidates WHERE id = ?;", (cid,)).fetchone()
                    return dict(updated)

                cid = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO candidates (
                        id, email, name, college, year, roll, 
                        primary_lang, experience, is_admin, created_at, last_login_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        cid,
                        norm_email,
                        name or "Candidate",
                        college,
                        year,
                        roll,
                        primary_lang,
                        experience,
                        1 if is_admin else 0,
                        now_iso,
                        now_iso,
                    ),
                )
                created = conn.execute("SELECT * FROM candidates WHERE id = ?;", (cid,)).fetchone()
                return dict(created)
        finally:
            conn.close()


def get_candidate_by_id(candidate_id: str, db_path: Optional[Path | str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve a candidate's profile by their persistent UUID.

    Args:
        candidate_id (str): Candidate's persistent ID.
        db_path (Optional[Path | str]): Database file path override.

    Returns:
        Optional[Dict[str, Any]]: The candidate row, or None if not found.
    """
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT * FROM candidates WHERE id = ?;", (str(candidate_id),)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ── Session Storage ───────────────────────────────────────────────────────────

def save_session(session_data: Dict[str, Any], db_path: Optional[Path | str] = None) -> None:
    """Insert a new session row, or update its status/score/completion on conflict.

    Args:
        session_data (Dict[str, Any]): Session fields — `id`,
            `candidate_id` (both required; no-op if either is empty),
            `interview_mode`, `c_topics`, `dsa_topics`, `duration_minutes`,
            `num_questions`, `start_difficulty`, `status`, `overall_score`,
            `created_at`, `completed_at`.
        db_path (Optional[Path | str]): Database file path override.

    Returns:
        None.
    """
    sid = str(session_data.get("id") or "")
    cid = str(session_data.get("candidate_id") or "")
    if not sid or not cid:
        return

    with _LOCK:
        conn = get_connection(db_path)
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO sessions (
                        id, candidate_id, interview_mode, c_topics, dsa_topics,
                        duration_minutes, num_questions, start_difficulty, status,
                        overall_score, created_at, completed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        status = excluded.status,
                        overall_score = excluded.overall_score,
                        completed_at = excluded.completed_at;
                    """,
                    (
                        sid,
                        cid,
                        str(session_data.get("interview_mode", "standard")),
                        json.dumps(session_data.get("c_topics", [])),
                        json.dumps(session_data.get("dsa_topics", [])),
                        int(session_data.get("duration_minutes", 30)),
                        int(session_data.get("num_questions", 15)),
                        int(session_data.get("start_difficulty", 2)),
                        str(session_data.get("status", "created")),
                        float(session_data.get("overall_score", 0.0)),
                        str(session_data.get("created_at") or datetime.now(UTC).isoformat()),
                        session_data.get("completed_at"),
                    ),
                )
        finally:
            conn.close()


# ── Attempt Recording & Deterministic Best-Answer Selection ───────────────────

def _decode_attempt_row(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a raw `question_attempts` row into a dict with JSON columns parsed.

    Args:
        row (sqlite3.Row): One row from `question_attempts`.

    Returns:
        Dict[str, Any]: The row as a dict, with `covered_concepts`,
            `missing_concepts`, `incorrect_claims`, `strong_points`
            (defaulting to `[]`) and `feedback_json` (defaulting to `{}`)
            parsed from their stored JSON strings.
    """
    d = dict(row)
    for key in ("covered_concepts", "missing_concepts", "incorrect_claims", "strong_points"):
        d[key] = json.loads(d.get(key) or "[]")
    d["feedback_json"] = json.loads(d.get("feedback_json") or "{}")
    return d


def _authoritative_best(conn: sqlite3.Connection, cid: str, qid: str) -> Optional[Dict[str, Any]]:
    """Derive the authoritative best primary attempt from the stored evaluations.

    Never trusts the stored `is_best` flag — recomputes from
    `services.storage.best_answer.select_best`, so a legacy flag pointing
    at an incorrect attempt gets silently corrected.

    Args:
        conn (sqlite3.Connection): Open database connection.
        cid (str): Candidate ID.
        qid (str): Question ID.

    Returns:
        Optional[Dict[str, Any]]: The best eligible primary attempt (see
            `best_answer.select_best`), or None if no primary attempt for
            this (candidate, question) is classified correct or partial.
    """
    rows = conn.execute(
        "SELECT * FROM question_attempts WHERE candidate_id = ? AND question_id = ? AND attempt_type = 'primary';",
        (cid, qid),
    ).fetchall()
    return select_best([_decode_attempt_row(r) for r in rows])


def save_attempt(
    attempt_data: Dict[str, Any],
    db_path: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """
    Record an attempt and deterministically recalculate `is_best` for this question.

    Best-Answer Invariant:
    0. Only attempts the authoritative evaluation classifies correct or partially correct are eligible
       (services/storage/best_answer.py). An incorrect attempt is never best; if no attempt is eligible,
       no attempt has is_best = 1 and current_best is None.
    1. Filtered by (candidate_id, question_id, attempt_type='primary').
    2. Highest validated_score wins.
    3. Tie-breaker 1: Fewest missing concepts.
    4. Tie-breaker 2: Most recent attempt (attempt_number DESC).
    5. At most ONE attempt has is_best = 1 (exactly one when any attempt is eligible).
    6. Follow-up attempts NEVER overwrite primary question best answer.

    Args:
        attempt_data (Dict[str, Any]): Attempt fields — `id` (optional,
            generated if absent), `candidate_id`, `session_id`,
            `question_id` (all required), `question_version`,
            `attempt_type` ("primary" or a follow-up type),
            `parent_question_id`, `answer_type`, `raw_score`,
            `validated_score`, `transcript`, `code_submitted`,
            `covered_concepts`, `missing_concepts`, `incorrect_claims`,
            `weakest_gap`, `strong_points`, `evaluation_confidence`,
            `feedback_json`, `created_at`.
        db_path (Optional[Path | str]): Database file path override.

    Returns:
        Dict[str, Any]: `attempt_id`, `attempt_number` (lifetime),
            `session_attempt_number`, `is_best` (bool, only meaningful for
            primary attempts), `previous_best` (attempt dict or None, from
            before this insert), `current_best` (attempt dict or None,
            after this insert).
    """
    aid = str(attempt_data.get("id") or uuid.uuid4())
    cid = str(attempt_data["candidate_id"])
    sid = str(attempt_data["session_id"])
    qid = str(attempt_data["question_id"])
    atype = str(attempt_data.get("attempt_type", "primary")).lower()
    parent_qid = attempt_data.get("parent_question_id")
    ans_type = str(attempt_data.get("answer_type", "verbal")).lower()
    raw_s = float(attempt_data.get("raw_score", 0.0))
    val_s = float(attempt_data.get("validated_score", raw_s))
    now_iso = str(attempt_data.get("created_at") or datetime.now(UTC).isoformat())

    covered = attempt_data.get("covered_concepts", [])
    missing = attempt_data.get("missing_concepts", [])
    incorrect = attempt_data.get("incorrect_claims", [])
    strong = attempt_data.get("strong_points", [])
    feedback = attempt_data.get("feedback_json", {})

    with _LOCK:
        conn = get_connection(db_path)
        try:
            with conn:
                # 1. Determine lifetime attempt number for this (candidate, question)
                count_row = conn.execute(
                    """
                    SELECT COUNT(*) as cnt FROM question_attempts 
                    WHERE candidate_id = ? AND question_id = ?;
                    """,
                    (cid, qid),
                ).fetchone()
                lifetime_attempt = int(count_row["cnt"]) + 1

                # 2. Determine session attempt number
                sess_count_row = conn.execute(
                    """
                    SELECT COUNT(*) as cnt FROM question_attempts 
                    WHERE candidate_id = ? AND session_id = ? AND question_id = ?;
                    """,
                    (cid, sid, qid),
                ).fetchone()
                sess_attempt = int(sess_count_row["cnt"]) + 1

                # 3. Retrieve previous best before this insertion
                prev_best = _authoritative_best(conn, cid, qid)

                # 4. Insert new attempt
                conn.execute(
                    """
                    INSERT INTO question_attempts (
                        id, candidate_id, session_id, question_id, question_version,
                        attempt_number, session_attempt_number, attempt_type, parent_question_id,
                        answer_type, transcript, code_submitted, raw_score, validated_score,
                        is_best, covered_concepts, missing_concepts, incorrect_claims,
                        weakest_gap, strong_points, evaluation_confidence, feedback_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        aid,
                        cid,
                        sid,
                        qid,
                        str(attempt_data.get("question_version", "v1")),
                        lifetime_attempt,
                        sess_attempt,
                        atype,
                        parent_qid,
                        ans_type,
                        str(attempt_data.get("transcript", "")),
                        str(attempt_data.get("code_submitted", "")),
                        round(raw_s, 4),
                        round(val_s, 4),
                        0,  # updated below
                        json.dumps(covered),
                        json.dumps(missing),
                        json.dumps(incorrect),
                        str(attempt_data.get("weakest_gap", "")),
                        json.dumps(strong),
                        float(attempt_data.get("evaluation_confidence", 0.85)),
                        json.dumps(feedback) if isinstance(feedback, (dict, list)) else str(feedback),
                        now_iso,
                    ),
                )

                # 5. Deterministically recalculate is_best if atype == 'primary'
                new_is_best = False
                current_best = None
                if atype == "primary":
                    current_best = _authoritative_best(conn, cid, qid)
                    winner_id = current_best["id"] if current_best else None   # None: nothing eligible

                    conn.execute(
                        """
                        UPDATE question_attempts
                        SET is_best = CASE WHEN id = ? THEN 1 ELSE 0 END
                        WHERE candidate_id = ? AND question_id = ? AND attempt_type = 'primary';
                        """,
                        (winner_id, cid, qid),
                    )

                    new_is_best = winner_id is not None and winner_id == aid
                    if current_best is not None:
                        current_best["is_best"] = 1
                else:
                    current_best = prev_best

                return {
                    "attempt_id": aid,
                    "attempt_number": lifetime_attempt,
                    "session_attempt_number": sess_attempt,
                    "is_best": new_is_best,
                    "previous_best": prev_best,
                    "current_best": current_best,
                }
        finally:
            conn.close()


def get_best_attempt(
    candidate_id: str,
    question_id: str,
    db_path: Optional[Path | str] = None,
) -> Optional[Dict[str, Any]]:
    """Retrieve the single authoritative best attempt for a (candidate, question) pair.

    Args:
        candidate_id (str): Candidate ID.
        question_id (str): Question ID.
        db_path (Optional[Path | str]): Database file path override.

    Returns:
        Optional[Dict[str, Any]]: The best eligible attempt (with
            `is_best` forced to 1), or None if no attempt is correct or
            partially correct.
    """
    conn = get_connection(db_path)
    try:
        res = _authoritative_best(conn, str(candidate_id), str(question_id))
        if res is not None:
            res["is_best"] = 1
        return res
    finally:
        conn.close()


def get_question_attempts(
    candidate_id: str,
    question_id: str,
    db_path: Optional[Path | str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve all historical attempts for a candidate/question pair, oldest first.

    Args:
        candidate_id (str): Candidate ID.
        question_id (str): Question ID.
        db_path (Optional[Path | str]): Database file path override.

    Returns:
        List[Dict[str, Any]]: Attempt rows ordered by `attempt_number`
            ascending, with JSON columns parsed.
    """
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT * FROM question_attempts
            WHERE candidate_id = ? AND question_id = ?
            ORDER BY attempt_number ASC;
            """,
            (str(candidate_id), str(question_id)),
        ).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["covered_concepts"] = json.loads(d.get("covered_concepts") or "[]")
            d["missing_concepts"] = json.loads(d.get("missing_concepts") or "[]")
            d["incorrect_claims"] = json.loads(d.get("incorrect_claims") or "[]")
            d["strong_points"] = json.loads(d.get("strong_points") or "[]")
            d["feedback_json"] = json.loads(d.get("feedback_json") or "{}")
            results.append(d)
        return results
    finally:
        conn.close()


def compare_with_previous_best(
    candidate_id: str,
    question_id: str,
    current_eval: Dict[str, Any],
    db_path: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """Derive objective comparison facts between the current evaluation and the previous best attempt.

    Grounded strictly in evaluator evidence (score and concept sets), with
    no LLM fabrication.

    Args:
        candidate_id (str): Candidate ID.
        question_id (str): Question ID.
        current_eval (Dict[str, Any]): Current turn's evaluation
            (`validated_score`/`final_score`, `covered_concepts`/
            `correct_claims`, `missing_concepts`, `incorrect_claims`).
        db_path (Optional[Path | str]): Database file path override.

    Returns:
        Dict[str, Any]: `has_previous_best` (bool); if True, also
            `previous_best_score`, `previous_best_answer`,
            `previous_best_attempt_number`, `score_delta`,
            `resolved_concepts` (missing->covered), `remaining_concepts`
            (still missing), `newly_missed_concepts` (covered->missing),
            `newly_introduced_errors`, and `has_improvement` (bool).
    """
    prev_best = get_best_attempt(candidate_id, question_id, db_path=db_path)
    if not prev_best:
        return {
            "has_previous_best": False,
            "previous_best_score": None,
            "previous_best_answer": "",
            "previous_best_attempt_number": None,
            "score_delta": 0.0,
            "resolved_concepts": [],
            "remaining_concepts": list(current_eval.get("missing_concepts", [])),
            "newly_missed_concepts": [],
            "newly_introduced_errors": [],
            "has_improvement": False,
        }

    prev_score = float(prev_best.get("validated_score", 0.0))
    curr_score = float(current_eval.get("validated_score", current_eval.get("final_score", 0.0)))
    score_delta = round(curr_score - prev_score, 4)

    prev_missing = set(str(c).strip().lower() for c in prev_best.get("missing_concepts", []))
    prev_covered = set(str(c).strip().lower() for c in prev_best.get("covered_concepts", []))
    prev_errors  = set(str(e).strip().lower() for e in prev_best.get("incorrect_claims", []))

    curr_covered_raw = current_eval.get("covered_concepts") or current_eval.get("correct_claims") or []
    curr_missing_raw = current_eval.get("missing_concepts") or []
    curr_errors_raw  = current_eval.get("incorrect_claims") or []

    curr_covered = set(str(c).strip().lower() for c in curr_covered_raw)
    curr_missing = set(str(c).strip().lower() for c in curr_missing_raw)
    curr_errors  = set(str(e).strip().lower() for e in curr_errors_raw)

    # Resolved = previously missing, now covered
    resolved = [c for c in curr_covered_raw if str(c).strip().lower() in prev_missing]
    # Remaining = still missing
    remaining = [c for c in curr_missing_raw if str(c).strip().lower() in prev_missing or str(c).strip().lower() in curr_missing]
    # Newly missed = previously covered, but missing now
    newly_missed = [c for c in curr_missing_raw if str(c).strip().lower() in prev_covered]
    # Newly introduced errors
    new_errors = [e for e in curr_errors_raw if str(e).strip().lower() not in prev_errors]

    has_improvement = (score_delta > 0.03) or (len(resolved) > 0 and score_delta >= -0.05)

    return {
        "has_previous_best": True,
        "previous_best_score": round(prev_score, 4),
        "previous_best_answer": prev_best.get("transcript") or prev_best.get("code_submitted") or "",
        "previous_best_attempt_number": prev_best.get("attempt_number"),
        "score_delta": score_delta,
        "resolved_concepts": resolved,
        "remaining_concepts": remaining,
        "newly_missed_concepts": newly_missed,
        "newly_introduced_errors": new_errors,
        "has_improvement": has_improvement,
    }


def list_sessions(db_path: Optional[Path | str] = None, limit: int = 500) -> List[Dict[str, Any]]:
    """Read-only listing of persisted sessions, joined with candidate profile fields.

    Lets the admin dashboard show sessions from before the current backend
    process started, not just the process-local in-memory `SESSIONS` dict
    (see `apps/backend/main.py`'s admin routes, which merge this with any
    live in-memory sessions). Only returns columns `sessions` actually
    persists (see `save_session`) — adds no new persistence or schema.

    Args:
        db_path (Optional[Path | str]): Database file path override.
        limit (int): Maximum rows to return (default 500).

    Returns:
        List[Dict[str, Any]]: Session rows (most recent `created_at`
            first), each with `candidate_name`/`candidate_email`/`college`/
            `year` joined in and a combined `topics` list (`c_topics` +
            `dsa_topics`) in place of the two separate JSON columns.
    """
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT s.id, s.candidate_id, s.interview_mode, s.c_topics, s.dsa_topics,
                   s.duration_minutes, s.num_questions, s.start_difficulty, s.status,
                   s.overall_score, s.created_at, s.completed_at,
                   c.name AS candidate_name, c.email AS candidate_email,
                   c.college AS college, c.year AS year
            FROM sessions s
            LEFT JOIN candidates c ON c.id = s.candidate_id
            ORDER BY s.created_at DESC
            LIMIT ?;
            """,
            (int(limit),),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            try:
                c_topics = json.loads(d.pop("c_topics") or "[]")
            except (TypeError, ValueError):
                c_topics = []
            try:
                dsa_topics = json.loads(d.pop("dsa_topics") or "[]")
            except (TypeError, ValueError):
                dsa_topics = []
            d["topics"] = c_topics + dsa_topics
            out.append(d)
        return out
    finally:
        conn.close()


# ── Bookmarks (Feature: Question Bookmarks & Notes) ──────────────────────────

def add_bookmark(candidate_id: str, question_id: str, note: str = "",
                  db_path: Optional[Path | str] = None) -> Dict[str, Any]:
    """Create or update (upsert) a bookmark for a candidate/question pair.

    Args:
        candidate_id (str): Candidate ID.
        question_id (str): Question ID.
        note (str): Optional free-text note (default "").
        db_path (Optional[Path | str]): Database file path override.

    Returns:
        Dict[str, Any]: The upserted bookmark row, or `{}` if it somehow
            couldn't be re-read after the upsert.
    """
    conn = get_connection(db_path)
    try:
        bookmark_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        with conn:
            conn.execute(
                """
                INSERT INTO bookmarks (id, candidate_id, question_id, note, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(candidate_id, question_id)
                DO UPDATE SET note = excluded.note;
                """,
                (bookmark_id, str(candidate_id), str(question_id), note or "", now),
            )
        row = conn.execute(
            "SELECT * FROM bookmarks WHERE candidate_id = ? AND question_id = ?;",
            (str(candidate_id), str(question_id)),
        ).fetchone()
        return dict(row) if row else {}
    finally:
        conn.close()


def remove_bookmark(candidate_id: str, question_id: str, db_path: Optional[Path | str] = None) -> bool:
    """Delete a bookmark for a candidate/question pair.

    Args:
        candidate_id (str): Candidate ID.
        question_id (str): Question ID.
        db_path (Optional[Path | str]): Database file path override.

    Returns:
        bool: True if a row was actually removed, False if none matched.
    """
    conn = get_connection(db_path)
    try:
        with conn:
            cur = conn.execute(
                "DELETE FROM bookmarks WHERE candidate_id = ? AND question_id = ?;",
                (str(candidate_id), str(question_id)),
            )
        return cur.rowcount > 0
    finally:
        conn.close()


def list_bookmarks(candidate_id: str, db_path: Optional[Path | str] = None) -> List[Dict[str, Any]]:
    """List all bookmarks for a candidate, most recent first.

    Args:
        candidate_id (str): Candidate ID.
        db_path (Optional[Path | str]): Database file path override.

    Returns:
        List[Dict[str, Any]]: Bookmark rows (`id`, `candidate_id`,
            `question_id`, `note`, `created_at`), newest first.
    """
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT id, candidate_id, question_id, note, created_at
            FROM bookmarks
            WHERE candidate_id = ?
            ORDER BY created_at DESC;
            """,
            (str(candidate_id),),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── Study goals (Feature: Server-Synced Study Goals) ─────────────────────────

def get_study_goal(candidate_id: str, db_path: Optional[Path | str] = None) -> Optional[Dict[str, Any]]:
    """Return a candidate's persisted study goal/plan.

    Args:
        candidate_id (str): Candidate ID.
        db_path (Optional[Path | str]): Database file path override.

    Returns:
        Optional[Dict[str, Any]]: The study-goal row with `plan` parsed
            from JSON, or None if the candidate has never set one.
    """
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM study_goals WHERE candidate_id = ?;",
            (str(candidate_id),),
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        try:
            d["plan"] = json.loads(d.pop("plan_json") or "{}")
        except (TypeError, ValueError):
            d["plan"] = {}
            d.pop("plan_json", None)
        return d
    finally:
        conn.close()


def save_study_goal(
    candidate_id: str,
    target_date: str = "",
    minutes_per_day: int = 30,
    plan: Optional[Dict[str, Any]] = None,
    db_path: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """Create or update (upsert) a candidate's study goal/plan.

    Args:
        candidate_id (str): Candidate ID.
        target_date (str): Target completion date, as a string (default
            "").
        minutes_per_day (int): Study-time budget per day (default 30).
        plan (Optional[Dict[str, Any]]): Arbitrary plan payload, stored as
            JSON.
        db_path (Optional[Path | str]): Database file path override.

    Returns:
        Dict[str, Any]: The upserted study-goal row (via
            `get_study_goal`), or `{}` if somehow not found after upsert.
    """
    conn = get_connection(db_path)
    try:
        now = datetime.now(UTC).isoformat()
        plan_json = json.dumps(plan or {})
        with conn:
            conn.execute(
                """
                INSERT INTO study_goals (candidate_id, target_date, minutes_per_day, plan_json, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(candidate_id)
                DO UPDATE SET target_date = excluded.target_date,
                              minutes_per_day = excluded.minutes_per_day,
                              plan_json = excluded.plan_json,
                              updated_at = excluded.updated_at;
                """,
                (str(candidate_id), target_date or "", int(minutes_per_day), plan_json, now),
            )
        return get_study_goal(candidate_id, db_path) or {}
    finally:
        conn.close()


def get_candidate_history(candidate_id: str, db_path: Optional[Path | str] = None) -> List[Dict[str, Any]]:
    """Summarize a candidate's attempt history, grouped by question.

    Args:
        candidate_id (str): Candidate ID.
        db_path (Optional[Path | str]): Database file path override.

    Returns:
        List[Dict[str, Any]]: One row per question attempted
            (`question_id`, `total_attempts`, `max_score`,
            `last_attempt_at`), most recently attempted first.
    """
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT question_id, COUNT(*) as total_attempts,
                   MAX(validated_score) as max_score,
                   MAX(created_at) as last_attempt_at
            FROM question_attempts
            WHERE candidate_id = ?
            GROUP BY question_id
            ORDER BY last_attempt_at DESC;
            """,
            (str(candidate_id),),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
