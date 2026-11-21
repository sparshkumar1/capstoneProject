import { useState, useEffect, useContext } from "react";
import { SessionContext } from "./contexts";
import Topbar from "./Topbar";
import ScoreRing from "./ScoreRing";
import { api } from "./api";
import { LineChart, formatDate } from "./ui";
import "./AdminDashboard.css";

const FILTERS = ["all", "today", "this_week", "this_month"];
const SORT_OPTS = [
  { value: "date_desc", label: "Newest First" },
  { value: "date_asc", label: "Oldest First" },
  { value: "score_desc", label: "Highest Score" },
  { value: "score_asc", label: "Lowest Score" },
];

export default function AdminDashboard({ navigate }) {
  useContext(SessionContext);
  const [sessions, setSessions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("all");
  const [sort, setSort] = useState("date_desc");
  const [search, setSearch] = useState("");
  const [selectedSession, setSelectedSession] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [page, setPage] = useState(1);
  const PAGE_SIZE = 10;
  const [candidateDrill, setCandidateDrill] = useState(null);
  const [candidateDrillLoading, setCandidateDrillLoading] = useState(false);
  const [candidateDrillError, setCandidateDrillError] = useState("");

  const fetchDashboardData = () => {
    setLoading(true);
    setError(null);
    Promise.all([
      api.getAllSessions({ filter, sort }),
      api.getAdminStats(),
    ]).then(([sData, sStats]) => {
      setSessions(Array.isArray(sData?.sessions) ? sData.sessions : Array.isArray(sData) ? sData : []);
      setStats(sStats || null);
    }).catch(err => {
      setError(err.message || "Failed to load admin session data from server.");
    }).finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchDashboardData();
  }, [filter, sort]);

  const openDetail = async (sess) => {
    setSelectedSession({ ...sess, loading: true });
    setDetailLoading(true);
    try {
      const detail = await api.getSessionDetail(sess.id);
      setSelectedSession(detail);
    } catch {
      setSelectedSession(sess);
    } finally {
      setDetailLoading(false);
    }
  };

  const openCandidate = async (sess) => {
    const key = sess.candidate_id || sess.candidate_email;
    if (!key) return;
    setCandidateDrill({ candidate_name: sess.candidate_name, candidate_email: sess.candidate_email });
    setCandidateDrillLoading(true);
    setCandidateDrillError("");
    try {
      const data = await api.getCandidateSessions(key);
      setCandidateDrill(data);
    } catch (err) {
      setCandidateDrillError(err.message || "Could not load this candidate's sessions.");
    } finally {
      setCandidateDrillLoading(false);
    }
  };

  const filtered = sessions.filter(s => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      s.candidate_name?.toLowerCase().includes(q) ||
      s.candidate_email?.toLowerCase().includes(q) ||
      s.id?.toLowerCase().includes(q) ||
      s.topics?.join(",").toLowerCase().includes(q)
    );
  });

  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);

  return (
    <div className="admin-page page">
      <Topbar navigate={navigate} />

      <div className="admin-content">
        {/* Header */}
        <div className="admin-header fade-up">
          <div>
            <div className="badge badge-accent" style={{ marginBottom: 10 }}>Admin Dashboard</div>
            <h1>Interview Sessions</h1>
            <p style={{ color: "var(--text-2)", marginTop: 6, fontSize: 14 }}>
              Monitor all candidate sessions, scores, and behavioural patterns.
            </p>
          </div>
          <button type="button" className="btn btn-ghost" onClick={() => navigate("login") }>
            ← Back to Login
          </button>
        </div>

        {/* Stats strip */}
        {stats && <StatsStrip stats={stats} />}

        {/* Error notification */}
        {error && (
          <div className="card admin-error-banner fade-up" style={{
            padding: "16px 20px",
            marginBottom: 20,
            background: "rgba(255, 79, 106, 0.1)",
            border: "1px solid rgba(255, 79, 106, 0.3)",
            borderRadius: 12,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span style={{ fontSize: 20 }}>⚠️</span>
              <span style={{ color: "var(--danger)", fontSize: 13 }}>{error}</span>
            </div>
            <button type="button" className="btn btn-sm btn-primary" onClick={fetchDashboardData}>
              🔄 Retry
            </button>
          </div>
        )}

        {/* Controls */}
        <div className="admin-controls fade-up stagger-2">
          <input
            className="input"
            style={{ maxWidth: 280 }}
            placeholder="🔍  Search candidate, topic, ID…"
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }}
          />

          <div className="pill-tabs" style={{ width: "auto" }}>
            {FILTERS.map(f => (
              <button type="button" key={f}
                className={`pill-tab ${filter === f ? "active" : ""}`}
                onClick={() => { setFilter(f); setPage(1); }}>
                {{ all: "All", today: "Today", this_week: "This Week", this_month: "This Month" }[f]}
              </button>
            ))}
          </div>

          <select className="input select" style={{ maxWidth: 180, width: "auto" }}
            value={sort} onChange={e => setSort(e.target.value)}>
            {SORT_OPTS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>

        {/* Table */}
        <div className="card sessions-table fade-up stagger-3">
          <div className="table-header">
            <div className="th">Candidate</div>
            <div className="th">Topics</div>
            <div className="th">Score</div>
            <div className="th">Difficulty</div>
            <div className="th">Duration</div>
            <div className="th">Date</div>
            <div className="th">Status</div>
            <div className="th" />
          </div>

          {loading ? (
            Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="table-row skeleton" style={{ height: 56, marginBottom: 1 }} />
            ))
          ) : paginated.length === 0 ? (
            <div className="empty-table">
              <div style={{ fontSize: 32, marginBottom: 10 }}>🔍</div>
              <p>No sessions found.</p>
            </div>
          ) : paginated.map((sess) => (
            <SessionRow key={sess.id} sess={sess} onClick={() => openDetail(sess)} onCandidateClick={() => openCandidate(sess)} />
          ))}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="pagination fade-up">
            <button type="button" className="btn btn-ghost btn-sm"
              disabled={page === 1} onClick={() => setPage(p => p - 1)}>← Prev</button>
            <span style={{ fontSize: 13, color: "var(--text-2)" }}>
              Page {page} of {totalPages}
            </span>
            <button type="button" className="btn btn-ghost btn-sm"
              disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>Next →</button>
          </div>
        )}
      </div>

      {/* Session detail drawer */}
      {selectedSession && (
        <SessionDrawer
          session={selectedSession}
          loading={detailLoading}
          onClose={() => setSelectedSession(null)}
        />
      )}

      {/* Candidate drill-down drawer */}
      {candidateDrill && (
        <CandidateDrawer
          data={candidateDrill}
          loading={candidateDrillLoading}
          error={candidateDrillError}
          onClose={() => setCandidateDrill(null)}
          onOpenSession={(sess) => { setCandidateDrill(null); openDetail(sess); }}
        />
      )}
    </div>
  );
}

function StatsStrip({ stats }) {
  const cards = [
    { label: "Total Sessions", value: stats.total_sessions, icon: "📋", color: "var(--accent)" },
    { label: "Avg Score", value: `${Math.round(stats.avg_score * 100)}%`, icon: "🎯", color: "var(--success)" },
    { label: "Active Today", value: stats.active_today, icon: "⚡", color: "var(--warn)" },
    { label: "Candidates", value: stats.unique_candidates, icon: "👥", color: "var(--accent-2)" },
    { label: "Avg Duration", value: `${stats.avg_duration_min}m`, icon: "⏱", color: "var(--text-2)" },
    { label: "Pass Rate", value: `${Math.round(stats.pass_rate * 100)}%`, icon: "✅", color: "var(--success)" },
  ];
  return (
    <div className="stats-strip fade-up stagger-1">
      {cards.map((c, i) => (
        <div key={i} className="card stat-strip-card">
          <div className="stat-icon" style={{ color: c.color }}>{c.icon}</div>
          <div className="stat-value" style={{ color: c.color }}>{c.value}</div>
          <div className="stat-label">{c.label}</div>
        </div>
      ))}
    </div>
  );
}

function SessionRow({ sess, onClick, onCandidateClick }) {
  const scorePct = Math.round((sess.overall_score || 0) * 100);
  const scoreColor = scorePct >= 70 ? "var(--success)" : scorePct >= 40 ? "var(--warn)" : "var(--danger)";
  const statusColor = {
    completed: "var(--success)", in_progress: "var(--accent)", abandoned: "var(--danger)", error: "var(--danger)"
  }[sess.status] || "var(--text-3)";

  return (
    <div className="table-row" onClick={onClick}>
      <div className="td">
        <div
          className="candidate-cell"
          onClick={(e) => { e.stopPropagation(); onCandidateClick?.(); }}
          title="View all sessions for this candidate"
          style={{ cursor: onCandidateClick ? "pointer" : undefined }}
        >
          <div className="avatar">
            {(sess.candidate_name?.[0] || "?").toUpperCase()}
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 13 }}>{sess.candidate_name || "Unknown"}</div>
            <div style={{ fontSize: 11, color: "var(--text-3)" }}>{sess.candidate_email}</div>
          </div>
        </div>
      </div>
      <div className="td">
        <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
          {(sess.topics || []).slice(0, 3).map(t => (
            <span key={t} className="badge badge-neutral" style={{ fontSize: 10 }}>{t}</span>
          ))}
          {(sess.topics || []).length > 3 && (
            <span className="badge badge-neutral" style={{ fontSize: 10 }}>+{sess.topics.length - 3}</span>
          )}
        </div>
      </div>
      <div className="td">
        <span style={{ fontFamily: "Syne", fontWeight: 800, fontSize: 15, color: scoreColor }}>
          {sess.overall_score !== undefined ? `${scorePct}%` : "—"}
        </span>
      </div>
      <div className="td">
        <div style={{ display: "flex", gap: 3 }}>
          {Array.from({ length: 5 }, (_, i) => (
            <div key={i} style={{
              width: 8, height: 14,
              borderRadius: 2,
              background: i < (sess.final_difficulty || 0) ? "var(--accent)" : "var(--surface-2)",
            }} />
          ))}
        </div>
      </div>
      <div className="td" style={{ fontSize: 13, color: "var(--text-2)" }}>
        {sess.duration_minutes ? `${sess.duration_minutes}m` : "—"}
      </div>
      <div className="td" style={{ fontSize: 12, color: "var(--text-3)" }}>
        {sess.created_at ? new Date(sess.created_at).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "2-digit" }) : "—"}
      </div>
      <div className="td">
        <span className="badge" style={{
          background: `color-mix(in srgb, ${statusColor} 14%, transparent)`,
          color: statusColor
        }}>
          {sess.status || "unknown"}
        </span>
      </div>
      <div className="td">
        <button type="button" className="btn btn-ghost btn-sm" onClick={(e) => { e.stopPropagation(); }}>
          View →
        </button>
      </div>
    </div>
  );
}

function SessionDrawer({ session, loading, onClose }) {
  const scorePct = Math.round((session.overall_score || 0) * 100);

  return (
    <>
      <div className="drawer-backdrop" onClick={onClose} />
      <div className="drawer">
        <div className="drawer-header">
          <div>
            <h3 style={{ fontFamily: "Syne", fontWeight: 700 }}>Session Detail</h3>
            <div style={{ fontSize: 11, color: "var(--text-3)", fontFamily: "JetBrains Mono", marginTop: 3 }}>
              {session.id}
            </div>
          </div>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose}>✕</button>
        </div>

        {loading ? (
          <div style={{ padding: 24 }}>
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="skeleton" style={{ height: 24, marginBottom: 12, borderRadius: 6 }} />
            ))}
          </div>
        ) : (
          <div className="drawer-body">
            {/* Score rings */}
            <div className="drawer-scores">
              <ScoreRing score={scorePct} size={100} label="Overall" color={scorePct >= 70 ? "var(--success)" : scorePct >= 40 ? "var(--warn)" : "var(--danger)"} />
              <ScoreRing score={Math.round((session.c_score || 0) * 100)} size={72} label="C Lang" color="var(--accent)" />
              <ScoreRing score={Math.round((session.dsa_score || 0) * 100)} size={72} label="DSA" color="var(--accent-2)" />
            </div>

            {/* Candidate info */}
            <div className="drawer-section">
              <div className="drawer-section-title">Candidate</div>
              <div className="drawer-kv">
                <span>Name</span><span>{session.candidate_name || "—"}</span>
              </div>
              <div className="drawer-kv">
                <span>Email</span><span>{session.candidate_email || "—"}</span>
              </div>
              <div className="drawer-kv">
                <span>College</span><span>{session.college || "—"}</span>
              </div>
              <div className="drawer-kv">
                <span>Year</span><span>{session.year || "—"}</span>
              </div>
            </div>

            <div className="drawer-section">
              <div className="drawer-section-title">Session</div>
              <div className="drawer-kv">
                <span>Status</span>
                <span className="badge badge-success">{session.status}</span>
              </div>
              <div className="drawer-kv">
                <span>Duration</span><span>{session.duration_minutes}m</span>
              </div>
              <div className="drawer-kv">
                <span>Questions</span><span>{session.total_questions}</span>
              </div>
              <div className="drawer-kv">
                <span>Final Difficulty</span>
                <div style={{ display: "flex", gap: 3 }}>
                  {Array.from({ length: 5 }, (_, i) => (
                    <div key={i} style={{
                      width: 10, height: 16, borderRadius: 2,
                      background: i < (session.final_difficulty || 0) ? "var(--accent)" : "var(--surface-2)",
                    }} />
                  ))}
                </div>
              </div>
            </div>

            {/* Topics */}
            {session.topics?.length > 0 && (
              <div className="drawer-section">
                <div className="drawer-section-title">Topics Covered</div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 8 }}>
                  {session.topics.map(t => (
                    <span key={t} className="badge badge-neutral">{t}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Strengths & gaps */}
            {session.strengths?.length > 0 && (
              <div className="drawer-section">
                <div className="drawer-section-title">Strengths</div>
                {session.strengths.map((s, i) => (
                  <div key={i} style={{ fontSize: 13, color: "var(--success)", padding: "5px 0", display: "flex", gap: 8, alignItems: "flex-start" }}>
                    <span style={{ marginTop: 2 }}>✓</span> <span style={{ color: "var(--text-2)" }}>{s}</span>
                  </div>
                ))}
              </div>
            )}

            {session.missing_concepts?.length > 0 && (
              <div className="drawer-section">
                <div className="drawer-section-title">Knowledge Gaps</div>
                {session.missing_concepts.map((m, i) => (
                  <div key={i} style={{ fontSize: 13, padding: "5px 0", display: "flex", gap: 8, alignItems: "flex-start" }}>
                    <span style={{ color: "var(--danger)", marginTop: 2 }}>✗</span>
                    <span style={{ color: "var(--text-2)" }}>{m}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Behaviour metrics */}
            {session.behaviour && (
              <div className="drawer-section">
                <div className="drawer-section-title">Behaviour</div>
                {[
                  ["Confidence", session.behaviour.avg_confidence],
                  ["Clarity", session.behaviour.clarity_score],
                  ["Completeness", session.behaviour.completeness],
                ].map(([label, val]) => val !== undefined && (
                  <div key={label} style={{ marginBottom: 10 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4, color: "var(--text-3)" }}>
                      <span>{label}</span>
                      <span style={{ color: "var(--accent)" }}>{Math.round(val * 100)}%</span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${Math.round(val * 100)}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {Array.isArray(session.question_results) && session.question_results.length > 0 && (
              <div className="drawer-section">
                <div className="drawer-section-title">Detailed Review</div>
                <div className="drawer-questions">
                  {session.question_results.map((q, i) => {
                    const pct = Math.round((q.score || 0) * 100);
                    const scoreColor = pct >= 70 ? "var(--success)" : pct >= 40 ? "var(--warn)" : "var(--danger)";
                    return (
                      <details key={`${q.question_id || i}-${i}`} className="drawer-question">
                        <summary className="drawer-question-summary">
                          <span className="dq-title">Q{i + 1}: {q.question_text || "Question"}</span>
                          <span className="dq-score" style={{ color: scoreColor }}>{pct}%</span>
                        </summary>

                        <div className="drawer-question-body">
                          {q.topic && <div className="dq-meta">Topic: {q.topic}</div>}
                          {q.type && <div className="dq-meta">Type: {q.type}</div>}
                          {q.feedback && (
                            <div className="dq-block">
                              <div className="dq-label">Feedback</div>
                              <p>{q.feedback}</p>
                            </div>
                          )}
                          {q.transcript && (
                            <div className="dq-block">
                              <div className="dq-label">Answer</div>
                              <p>{q.transcript}</p>
                            </div>
                          )}
                          {q.code_submitted && (
                            <div className="dq-block">
                              <div className="dq-label">Code</div>
                              <pre className="dq-code">{q.code_submitted}</pre>
                            </div>
                          )}
                        </div>
                      </details>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}

/** Aggregate, candidate-level view: all of one candidate's sessions plus a score trend,
 * reached by clicking their name/email in the flat session table (Feature: Admin
 * per-candidate drill-down). Reuses the same ScoreRing component as SessionDrawer for
 * visual consistency, and the shared ui.jsx LineChart for the trend. */
function CandidateDrawer({ data, loading, error, onClose, onOpenSession }) {
  const sessions = data?.sessions || [];
  const avgPct = data?.avg_score != null ? Math.round(data.avg_score * 100) : null;

  // Oldest-first for a left-to-right trend; the API returns newest-first.
  const trendPoints = [...sessions].reverse()
    .filter((s) => s.overall_score !== null && s.overall_score !== undefined)
    .map((s) => ({
      label: formatDate(s.created_at, { month: "short", day: "numeric" }),
      value: s.overall_score,
      detail: `${Math.round((s.overall_score || 0) * 100)}%`,
    }));

  return (
    <>
      <div className="drawer-backdrop" onClick={onClose} />
      <div className="drawer">
        <div className="drawer-header">
          <div>
            <h3 style={{ fontFamily: "Syne", fontWeight: 700 }}>{data?.candidate_name || "Candidate"}</h3>
            <div style={{ fontSize: 11, color: "var(--text-3)", marginTop: 3 }}>{data?.candidate_email}</div>
          </div>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose}>✕</button>
        </div>

        {loading ? (
          <div style={{ padding: 24 }}>
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="skeleton" style={{ height: 24, marginBottom: 12, borderRadius: 6 }} />
            ))}
          </div>
        ) : error ? (
          <div style={{ padding: 24, color: "var(--danger)", fontSize: 13 }}>{error}</div>
        ) : (
          <div className="drawer-body">
            <div className="drawer-scores">
              <ScoreRing score={avgPct ?? 0} size={100} label="Avg score"
                color={avgPct >= 70 ? "var(--success)" : avgPct >= 40 ? "var(--warn)" : "var(--danger)"} />
            </div>

            <div className="drawer-section">
              <div className="drawer-section-title">Overview</div>
              <div className="drawer-kv"><span>Total sessions</span><span>{data?.total_sessions ?? sessions.length}</span></div>
              <div className="drawer-kv"><span>Average score</span><span>{avgPct != null ? `${avgPct}%` : "—"}</span></div>
            </div>

            {trendPoints.length >= 2 && (
              <div className="drawer-section">
                <div className="drawer-section-title">Score trend</div>
                <LineChart ariaLabel={`Score trend for ${data?.candidate_name || "candidate"}`} points={trendPoints} height={140} />
              </div>
            )}

            <div className="drawer-section">
              <div className="drawer-section-title">All sessions ({sessions.length})</div>
              <div className="drawer-questions">
                {sessions.map((s) => {
                  const sPct = s.overall_score != null ? Math.round(s.overall_score * 100) : null;
                  const sColor = sPct == null ? "var(--text-3)" : sPct >= 70 ? "var(--success)" : sPct >= 40 ? "var(--warn)" : "var(--danger)";
                  return (
                    <button
                      type="button"
                      key={s.id}
                      className="drawer-question"
                      style={{ width: "100%", textAlign: "left", cursor: "pointer", font: "inherit", display: "block" }}
                      onClick={() => onOpenSession(s)}
                    >
                      <div className="drawer-question-summary">
                        <span className="dq-title">
                          {formatDate(s.created_at, { month: "short", day: "numeric", year: "numeric" })} · {(s.topics || []).slice(0, 2).map((t) => t.replace(/_/g, " ")).join(", ") || "Mixed topics"}
                        </span>
                        <span className="dq-score" style={{ color: sColor }}>{sPct != null ? `${sPct}%` : "—"}</span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
