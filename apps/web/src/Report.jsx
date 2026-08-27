import { useState, useEffect, useContext } from "react";
import { SessionContext } from "./contexts";
import Topbar from "./Topbar";
import ScoreRing from "./ScoreRing";
import { api } from "./api";
import "./Report.css";

// ── Grade / trend colours ─────────────────────────────────────────
const GRADE_COLOR = { A: "var(--success)", B: "var(--accent-2)", C: "var(--warn)", D: "#ff8c4f", F: "var(--danger)" };
const TREND_META  = {
  improving: { icon: "↑", color: "var(--success)", label: "Improving" },
  declining:  { icon: "↓", color: "var(--danger)",  label: "Declining" },
  stable:     { icon: "→", color: "var(--warn)",    label: "Stable"    },
};

// ── Mini score bar (reused everywhere) ───────────────────────────
function MiniBar({ label, value, color }) {
  const pct = Math.round((value ?? 0) * 100);
  return (
    <div className="rpt-bar-row">
      <span className="rpt-bar-label">{label}</span>
      <div className="rpt-bar-track">
        <div className="rpt-bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="rpt-bar-pct" style={{ color }}>{pct}%</span>
    </div>
  );
}

// ── Main Report page ──────────────────────────────────────────────
export default function Report({ navigate }) {
  const { session, candidate } = useContext(SessionContext);
  const [report, setReport]   = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  const fetchReport = () => {
    const id = session?.report_id || session?.id;
    if (!id) {
      setError("No session ID found. Please complete an interview session first.");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    api.getReport(id)
      .then(data => {
        if (!data || Object.keys(data).length === 0) {
          throw new Error("Report data is empty.");
        }
        setReport(data);
      })
      .catch(err => {
        setError(err.message || "Failed to load session report from server. Please retry.");
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchReport();
  }, [session]);

  if (loading) return <LoadingSkeleton />;

  if (error || !report) {
    return (
      <div className="report-page page">
        <Topbar navigate={navigate} />
        <div className="report-content" style={{ maxWidth: 640, margin: "60px auto" }}>
          <div className="card report-error-card" style={{ padding: "32px", textAlign: "center" }}>
            <div style={{ fontSize: 36, marginBottom: 12 }}>⚠️</div>
            <h2 style={{ fontFamily: "Syne", marginBottom: 8, color: "var(--danger)" }}>Report Unavailable</h2>
            <p style={{ color: "var(--text-2)", marginBottom: 24, lineHeight: 1.5 }}>
              {error || "Failed to load session report from server. Please retry."}
            </p>
            <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
              <button type="button" className="btn btn-primary" onClick={fetchReport}>
                🔄 Retry Loading
              </button>
              <button type="button" className="btn btn-ghost" onClick={() => navigate?.("topics")}>
                Start New Interview
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const r = report;

  const overallPct = Math.round((r.overall_score || 0) * 100);
  const verdict = overallPct >= 80
    ? { label: "Excellent",       color: "var(--success)", icon: "🏆" }
    : overallPct >= 60
    ? { label: "Good",            color: "var(--accent)",  icon: "⚡" }
    : overallPct >= 40
    ? { label: "Needs Work",      color: "var(--warn)",    icon: "📈" }
    : { label: "Keep Practicing", color: "var(--danger)",  icon: "💪" };

  const tabs = ["overview", "questions", "timeline", "concepts", "behaviour"];

  return (
    <div className="report-page page">
      <Topbar navigate={navigate} />

      <div className="report-content">

        {/* ── Hero ─────────────────────────────────────────── */}
        <div className="report-hero card fade-up">
          <div className="hero-left">
            <div className="badge badge-accent" style={{ marginBottom: 14 }}>Interview Complete</div>
            <h1>Your Report</h1>
            <p style={{ color: "var(--text-2)", marginTop: 8, maxWidth: 420, lineHeight: 1.6 }}>
              {candidate?.name ? `${candidate.name}, here's` : "Here's"} a detailed breakdown of your performance.
            </p>

            <div className="verdict-chip" style={{ borderColor: verdict.color, color: verdict.color }}>
              {verdict.icon} {verdict.label}
            </div>

            {r.trend_summary && (
              <div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 7 }}>
                <span style={{ fontSize: 12, color: "var(--text-3)" }}>Overall trend:</span>
                <span style={{
                  fontSize: 12, fontWeight: 700, fontFamily: "Syne",
                  color: TREND_META[r.trend_summary]?.color ?? "var(--text-2)",
                }}>
                  {TREND_META[r.trend_summary]?.icon} {TREND_META[r.trend_summary]?.label ?? r.trend_summary}
                </span>
              </div>
            )}

            <div className="report-meta">
              {r.session_date && <span>📅 {new Date(r.session_date).toLocaleDateString("en-IN", { dateStyle: "medium" })}</span>}
              {r.duration_minutes && <span>⏱ {r.duration_minutes} min</span>}
              {r.total_questions  && <span>❓ {r.total_questions} questions</span>}
            </div>
          </div>

          <div className="hero-rings">
            <ScoreRing score={overallPct} size={140} label="Overall" color={verdict.color} />
            <div className="mini-rings">
              <ScoreRing score={Math.round((r.c_score   || 0) * 100)} size={88} label="C Language" color="var(--accent)" />
              <ScoreRing score={Math.round((r.dsa_score || 0) * 100)} size={88} label="DSA"        color="var(--accent-2)" />
            </div>
          </div>
        </div>

        {/* ── Tabs ─────────────────────────────────────────── */}
        <div className="pill-tabs report-tabs fade-up stagger-1">
          {tabs.map(t => (
            <button type="button" key={t} className={`pill-tab ${activeTab === t ? "active" : ""}`}
              onClick={() => setActiveTab(t)}>
              {{ overview: "Overview", questions: "Questions", timeline: "Timeline", concepts: "Concepts", behaviour: "Behaviour" }[t]}
            </button>
          ))}
        </div>

        {activeTab === "overview"   && <OverviewTab   r={r} />}
        {activeTab === "questions"  && <QuestionsTab  r={r} />}
        {activeTab === "timeline"   && <TimelineTab   r={r} />}
        {activeTab === "concepts"   && <ConceptsTab   r={r} />}
        {activeTab === "behaviour"  && <BehaviourTab  r={r} />}

        {/* ── Actions ──────────────────────────────────────── */}
        <div className="report-actions fade-up">
          <button type="button" className="btn btn-primary btn-lg" onClick={() => navigate("topics") }>
            🔁 Start New Interview
          </button>
          <button type="button" className="btn btn-ghost btn-lg" onClick={() => navigate("admin") }>
            📊 View All Sessions
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Overview tab ──────────────────────────────────────────────────
function OverviewTab({ r }) {
  const topicScores = r.topic_scores || {};

  return (
    <div className="tab-content fade-up">
      <div className="overview-grid">

        {/* Strengths */}
        <div className="card report-card">
          <div className="report-card-header">
            <span className="report-card-icon" style={{ background: "rgba(54,217,143,0.14)" }}>💪</span>
            <h3>Strengths</h3>
          </div>
          {(r.strengths || []).length > 0
            ? (r.strengths || []).map((s, i) => (
              <div key={i} className="concept-row strength">
                <span className="concept-dot" style={{ background: "var(--success)" }} />
                <span>{s}</span>
              </div>
            ))
            : <p className="empty-msg">No specific strengths recorded yet.</p>
          }
        </div>

        {/* Gaps */}
        <div className="card report-card">
          <div className="report-card-header">
            <span className="report-card-icon" style={{ background: "rgba(255,79,106,0.14)" }}>🔍</span>
            <h3>Gaps to Address</h3>
          </div>
          {(r.missing_concepts || []).length > 0
            ? (r.missing_concepts || []).map((m, i) => (
              <div key={i} className="concept-row missing">
                <span className="concept-dot" style={{ background: "var(--danger)" }} />
                <span>{m}</span>
              </div>
            ))
            : <p className="empty-msg">No major gaps identified. 🎉</p>
          }
        </div>

        {/* Topic breakdown */}
        <div className="card report-card" style={{ gridColumn: "span 2" }}>
          <div className="report-card-header">
            <span className="report-card-icon" style={{ background: "var(--accent-glow)" }}>📊</span>
            <h3>Topic Breakdown</h3>
          </div>
          <div className="topic-scores">
            {Object.entries(topicScores).length > 0
              ? Object.entries(topicScores).map(([topic, score]) => (
                <TopicScoreRow key={topic} topic={topic} score={score} />
              ))
              : <p className="empty-msg">No per-topic breakdown available.</p>
            }
          </div>
        </div>

        {/* Study Recommendations */}
        {(r.recommendations || []).length > 0 && (
          <div className="card report-card" style={{ gridColumn: "span 2" }}>
            <div className="report-card-header">
              <span className="report-card-icon" style={{ background: "var(--accent-glow)" }}>🎯</span>
              <h3>Study Recommendations</h3>
            </div>
            {r.recommendations.map((rec, i) => (
              <div key={i} className="rec-row">
                <span className="rec-num">{i + 1}</span>
                <span>{rec}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Questions tab — full rich feedback per question ───────────────
function QuestionsTab({ r }) {
  const [expanded, setExpanded] = useState(null);
  const questions = r.question_results || [];

  return (
    <div className="tab-content fade-up">
      {questions.length === 0
        ? <div className="card" style={{ padding: 32, textAlign: "center", color: "var(--text-3)" }}>
            No question data available.
          </div>
        : questions.map((q, i) => {
          const gradeColor = GRADE_COLOR[q.grade] ?? "var(--text-2)";
          const trendM = TREND_META[q.trend] ?? TREND_META.stable;
          return (
            <div key={i} className={`card q-row ${expanded === i ? "expanded" : ""}`}>
              <div className="q-row-header" onClick={() => setExpanded(expanded === i ? null : i)}>
                <div className="q-row-left">
                  <span className="q-num">Q{i + 1}</span>
                  <div>
                    <div className="q-text">{q.question_text}</div>
                    <div style={{ display: "flex", gap: 6, marginTop: 5, flexWrap: "wrap" }}>
                      {q.topic && <span className="badge badge-neutral">{q.topic}</span>}
                      {q.type  && <span className="badge badge-neutral">{q.type}</span>}
                      <span className="badge" style={{
                        background: q.difficulty <= 2 ? "rgba(54,217,143,0.14)" : q.difficulty === 3 ? "rgba(255,184,79,0.14)" : "rgba(255,79,106,0.14)",
                        color: q.difficulty <= 2 ? "var(--success)" : q.difficulty === 3 ? "var(--warn)" : "var(--danger)"
                      }}>Lv {q.difficulty}</span>
                      {q.trend && (
                        <span style={{ fontSize: 11, color: trendM.color, fontFamily: "Syne", fontWeight: 700 }}>
                          {trendM.icon} {trendM.label}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="q-row-right">
                  <span className="badge badge-neutral" style={{ fontSize: 11 }}>Evaluated</span>
                  <span style={{ color: "var(--text-3)", fontSize: 12 }}>{expanded === i ? "▲" : "▼"}</span>
                </div>
              </div>

              {expanded === i && (
                <div className="q-detail fade-up">
                  <div className="divider" />


                  {/* Transcript */}
                  {q.transcript && (
                    <div className="q-detail-section">
                      <div className="q-detail-label">Your Answer</div>
                      <p style={{ fontStyle: "italic", color: "var(--text-2)", fontSize: 13, lineHeight: 1.6 }}>
                        &quot;{q.transcript}&quot;
                      </p>
                    </div>
                  )}

                  {/* Code submitted */}
                  {q.code_submitted && (
                    <div className="q-detail-section">
                      <div className="q-detail-label">Code Submitted</div>
                      <pre className="code-snippet">{q.code_submitted}</pre>
                    </div>
                  )}

                  {/* Strong points */}
                  {(q.strong_points || []).length > 0 && (
                    <div className="q-detail-section">
                      <div className="q-detail-label">What You Got Right</div>
                      <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: 5, marginTop: 6 }}>
                        {q.strong_points.map((s, j) => (
                          <li key={j} style={{ display: "flex", gap: 8, fontSize: 13, color: "var(--text-2)", alignItems: "flex-start" }}>
                            <span style={{ color: "var(--success)", fontWeight: 700, flexShrink: 0 }}>✓</span>
                            {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Covered concepts */}
                  {(q.covered_concepts || []).length > 0 && (
                    <div className="q-detail-section">
                      <div className="q-detail-label">Concepts Covered</div>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginTop: 6 }}>
                        {q.covered_concepts.map((c, j) => (
                          <span key={j} className="badge badge-success">{c}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Misconceptions */}
                  {(q.incorrect_or_incomplete || []).length > 0 && (
                    <div className="q-detail-section">
                      <div className="q-detail-label">Incorrect or Incomplete</div>
                      <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 6 }}>
                        {q.incorrect_or_incomplete.map((e, j) => (
                          <div key={j} style={{
                            padding: "10px 12px",
                            borderRadius: 10,
                            borderLeft: `3px solid ${e.severity === "major" ? "var(--danger)" : "var(--warn)"}`,
                            background: e.severity === "major" ? "rgba(255,79,106,0.06)" : "rgba(255,184,79,0.06)",
                          }}>
                            <div style={{ display: "flex", justifyContent: "space-between", gap: 10, marginBottom: 5 }}>
                              <span style={{ fontSize: 12, color: "var(--text-2)", fontStyle: "italic" }}>
                                &quot;{e.what_was_said}&quot;
                              </span>
                              <span className={`badge ${e.severity === "major" ? "badge-danger" : "badge-warn"}`}>
                                {e.severity}
                              </span>
                            </div>
                            <div style={{ fontSize: 13, color: "var(--text)", display: "flex", gap: 7 }}>
                              <span style={{ color: "var(--accent-2)", fontWeight: 700 }}>→</span>
                              {e.correction}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Missing concepts */}
                  {(q.missing_concepts || []).length > 0 && (
                    <div className="q-detail-section">
                      <div className="q-detail-label">Missing Concepts</div>
                      <div style={{ display: "flex", gap: 5, flexWrap: "wrap", marginTop: 6 }}>
                        {q.missing_concepts.map((m, j) => (
                          <span key={j} className="badge badge-danger">{m}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* How to improve */}
                  {(q.how_to_improve || []).length > 0 && (
                    <div className="q-detail-section">
                      <div className="q-detail-label">How to Improve</div>
                      <ol style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: 7, marginTop: 6 }}>
                        {q.how_to_improve.map((tip, j) => (
                          <li key={j} style={{ display: "flex", gap: 9, fontSize: 13, color: "var(--text-2)", alignItems: "flex-start" }}>
                            <span style={{
                              width: 20, height: 20, borderRadius: 6,
                              background: "var(--accent-glow)", color: "var(--accent)",
                              display: "flex", alignItems: "center", justifyContent: "center",
                              fontSize: 10, fontWeight: 700, fontFamily: "Syne",
                              flexShrink: 0, marginTop: 1,
                            }}>{j + 1}</span>
                            {tip}
                          </li>
                        ))}
                      </ol>
                    </div>
                  )}

                  {/* Communication tips */}
                  {(q.communication_tips || []).length > 0 && (
                    <div className="q-detail-section">
                      <div className="q-detail-label">Delivery & Communication</div>
                      <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: 6, marginTop: 6 }}>
                        {q.communication_tips.map((tip, j) => (
                          <li key={j} style={{ display: "flex", gap: 9, fontSize: 13, color: "var(--text-2)", alignItems: "flex-start" }}>
                            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--accent-2)", flexShrink: 0, marginTop: 5 }} />
                            {tip}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* AI justification */}
                  {q.feedback && (
                    <div className="q-detail-section" style={{ background: "var(--bg-2)", borderRadius: 10, padding: "10px 14px" }}>
                      <div className="q-detail-label">AI Summary</div>
                      <p style={{ color: "var(--text-2)", fontSize: 13, lineHeight: 1.6, marginTop: 6 }}>{q.feedback}</p>
                    </div>
                  )}

                  {/* Trend note */}
                  {q.trend_note && (
                    <div style={{ marginTop: 10, fontSize: 12, color: TREND_META[q.trend]?.color ?? "var(--text-3)", fontStyle: "italic" }}>
                      {TREND_META[q.trend]?.icon} {q.trend_note}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })
      }
    </div>
  );
}

// ── Timeline tab — score + difficulty progression ─────────────────
function TimelineTab({ r }) {
  const scores    = r.score_history     || r.question_results?.map(q => q.score) || [];
  const diffs     = r.difficulty_history || [];
  const questions = r.question_results  || [];

  if (scores.length === 0) {
    return (
      <div className="tab-content fade-up">
        <div className="card" style={{ padding: 40, textAlign: "center", color: "var(--text-3)" }}>
          No session data to display.
        </div>
      </div>
    );
  }

  return (
    <div className="tab-content fade-up">

      {/* Score progression chart */}
      <div className="card report-card" style={{ padding: 24 }}>
        <div className="report-card-header">
          <span className="report-card-icon" style={{ background: "var(--accent-glow)" }}>📈</span>
          <h3>Score Progression</h3>
        </div>
        <ScoreLineChart scores={scores} />
      </div>

      {/* Difficulty journey */}
      {diffs.length > 1 && (
        <div className="card report-card" style={{ padding: 24 }}>
          <div className="report-card-header">
            <span className="report-card-icon" style={{ background: "rgba(255,184,79,0.14)" }}>🎯</span>
            <h3>Difficulty Journey</h3>
          </div>
          <DifficultyChart history={diffs} />
          <div style={{ fontSize: 12, color: "var(--text-3)", marginTop: 8 }}>
            {diffs[0] === 2 && diffs.length > 2
              ? "Started at easy (baseline) → RL adapted difficulty based on your performance."
              : "Difficulty adjusted throughout the session."}
          </div>
        </div>
      )}

      {/* Per-question score table */}
      <div className="card report-card" style={{ padding: 0, overflow: "hidden" }}>
        <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--border)" }}>
          <div className="report-card-header" style={{ marginBottom: 0 }}>
            <span className="report-card-icon" style={{ background: "var(--accent-glow)" }}>📋</span>
            <h3>Question-by-Question</h3>
          </div>
        </div>
        <table className="timeline-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Topic</th>
              <th>Type</th>
              <th>Level</th>
              <th>Status</th>
              <th>Trend</th>
            </tr>
          </thead>
          <tbody>
            {questions.map((q, i) => {
              const trendM = TREND_META[q.trend] ?? TREND_META.stable;
              return (
                <tr key={i}>
                  <td className="tl-num">Q{i + 1}</td>
                  <td>{q.topic?.replace(/_/g, " ") || "—"}</td>
                  <td><span className="badge badge-neutral" style={{ fontSize: 10 }}>{q.type || "verbal"}</span></td>
                  <td>
                    <span className="badge" style={{
                      fontSize: 10,
                      background: q.difficulty <= 2 ? "rgba(54,217,143,0.14)" : q.difficulty === 3 ? "rgba(255,184,79,0.14)" : "rgba(255,79,106,0.14)",
                      color: q.difficulty <= 2 ? "var(--success)" : q.difficulty === 3 ? "var(--warn)" : "var(--danger)",
                    }}>Lv {q.difficulty ?? "—"}</span>
                  </td>
                  <td>
                    <span className="badge badge-neutral" style={{ fontSize: 11 }}>Evaluated</span>
                  </td>
                  <td style={{ color: trendM.color, fontWeight: 700, fontFamily: "Syne", fontSize: 12 }}>
                    {trendM.icon} {trendM.label}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── Concepts tab ──────────────────────────────────────────────────
function ConceptsTab({ r }) {
  const all     = r.all_concepts || {};
  const mastered = Object.entries(all).filter(([, v]) => v >= 0.70);
  const partial  = Object.entries(all).filter(([, v]) => v >= 0.40 && v < 0.70);
  const missing  = Object.entries(all).filter(([, v]) => v <  0.40);

  return (
    <div className="tab-content fade-up">
      <div className="concepts-grid">
        <ConceptGroup title="Mastered"            color="var(--success)" icon="✅" items={mastered} />
        <ConceptGroup title="Partial Understanding" color="var(--warn)"  icon="⚠️" items={partial}  />
        <ConceptGroup title="Needs Study"          color="var(--danger)" icon="📚" items={missing}  />
      </div>

      {(r.recommendations || []).length > 0 && (
        <div className="card report-card" style={{ marginTop: 16 }}>
          <div className="report-card-header">
            <span className="report-card-icon" style={{ background: "var(--accent-glow)" }}>🎯</span>
            <h3>Study Recommendations</h3>
          </div>
          {r.recommendations.map((rec, i) => (
            <div key={i} className="rec-row">
              <span className="rec-num">{i + 1}</span>
              <span>{rec}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ConceptGroup({ title, color, icon, items }) {
  return (
    <div className="card report-card">
      <div className="report-card-header">
        <span className="report-card-icon" style={{ background: `color-mix(in srgb, ${color} 15%, transparent)` }}>{icon}</span>
        <h3>{title} <span style={{ color, fontWeight: 700 }}>({items.length})</span></h3>
      </div>
      {items.length === 0
        ? <p className="empty-msg">None in this category.</p>
        : items.map(([concept], i) => (
          <div key={i} className="concept-row">
            <span className="concept-dot" style={{ background: color }} />
            <span style={{ flex: 1 }}>{concept}</span>
            <span className="badge" style={{ background: `color-mix(in srgb, ${color} 14%, transparent)`, color, fontSize: 11 }}>
              {title}
            </span>
          </div>
        ))
      }
    </div>
  );
}

// ── Behaviour tab ─────────────────────────────────────────────────
function BehaviourTab({ r }) {
  const questions = r.question_results || [];

  // Communication signals aggregated across all questions
  const allCommTips = questions.flatMap(q => q.communication_tips || []);
  const fillerMentions = allCommTips.filter(t => t.toLowerCase().includes("filler")).length;
  const hedgeMentions  = allCommTips.filter(t => t.toLowerCase().includes("hedg") || t.toLowerCase().includes("assertive")).length;

  const insights = [
    { label: "Delivery & Pacing", desc: "Monitored speaking rate, structure, and explanation clarity across verbal turns.", icon: "🎙️", color: "var(--accent)" },
    { label: "Verbal Fluency", desc: fillerMentions === 0 ? "Consistently fluent with minimal filler pauses." : `Observed filler patterns in ${fillerMentions} question(s). Practice pausing silently before answering.`, icon: "⚡", color: "var(--accent-2)" },
    { label: "Assertion & Tone", desc: hedgeMentions === 0 ? "Direct and assertive technical articulation." : `Occasional hedging phrases identified in ${hedgeMentions} turn(s). State technical invariants with direct confidence.`, icon: "🎯", color: "var(--success)" },
  ];

  return (
    <div className="tab-content fade-up">
      <div className="behaviour-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 14 }}>
        {insights.map((ins, i) => (
          <div key={i} className="card behaviour-metric" style={{ padding: "18px 20px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
              <span style={{ fontSize: 20 }}>{ins.icon}</span>
              <div className="bm-label" style={{ fontSize: 13, color: ins.color, fontWeight: 700, fontFamily: "Syne" }}>{ins.label}</div>
            </div>
            <p style={{ fontSize: 13, color: "var(--text-2)", lineHeight: 1.5, margin: 0 }}>
              {ins.desc}
            </p>
          </div>
        ))}
      </div>

      {/* Communication pattern summary */}
      {allCommTips.length > 0 && (
        <div className="card report-card" style={{ marginTop: 14 }}>
          <div className="report-card-header">
            <span className="report-card-icon" style={{ background: "var(--accent-2-glow)" }}>🎙️</span>
            <h3>Communication Patterns</h3>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div style={{ padding: "12px 14px", background: "var(--bg-2)", borderRadius: 10 }}>
              <div style={{ fontSize: 11, color: "var(--text-3)", fontFamily: "Syne", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 6 }}>
                Filler Word Issues
              </div>
              <div style={{ fontSize: 22, fontFamily: "Syne", fontWeight: 800, color: fillerMentions > 2 ? "var(--warn)" : "var(--success)" }}>
                {fillerMentions}
              </div>
              <div style={{ fontSize: 12, color: "var(--text-3)" }}>questions flagged</div>
            </div>
            <div style={{ padding: "12px 14px", background: "var(--bg-2)", borderRadius: 10 }}>
              <div style={{ fontSize: 11, color: "var(--text-3)", fontFamily: "Syne", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 6 }}>
                Hedging Language
              </div>
              <div style={{ fontSize: 22, fontFamily: "Syne", fontWeight: 800, color: hedgeMentions > 1 ? "var(--danger)" : "var(--success)" }}>
                {hedgeMentions}
              </div>
              <div style={{ fontSize: 12, color: "var(--text-3)" }}>questions flagged</div>
            </div>
          </div>
          <div style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 7 }}>
            {[...new Set(allCommTips)].slice(0, 6).map((tip, i) => (
              <div key={i} style={{ display: "flex", gap: 9, fontSize: 13, color: "var(--text-2)", alignItems: "flex-start" }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--accent-2)", flexShrink: 0, marginTop: 5 }} />
                {tip}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Chart helpers ─────────────────────────────────────────────────
function ScoreLineChart({ scores }) {
  if (scores.length < 2) return null;
  const n = scores.length;
  const W = 100;
  const H = 50;
  const padX = 4;
  const padY = 4;
  const xStep = (W - padX * 2) / (n - 1);

  const pts = scores.map((v, i) => {
    const x = padX + i * xStep;
    const y = padY + (1 - v) * (H - padY * 2);
    return `${x},${y}`;
  });

  const avg = scores.reduce((a, b) => a + b, 0) / n;
  const avgY = padY + (1 - avg) * (H - padY * 2);

  return (
    <div style={{ position: "relative" }}>
      <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none"
        style={{ width: "100%", height: 120, display: "block" }}>
        {/* Grid lines */}
        {[0.25, 0.5, 0.75].map(v => {
          const y = padY + (1 - v) * (H - padY * 2);
          return (
            <line key={v} x1={padX} y1={y} x2={W - padX} y2={y}
              stroke="var(--border)" strokeWidth="0.5" vectorEffect="non-scaling-stroke" />
          );
        })}
        {/* Average line */}
        <line x1={padX} y1={avgY} x2={W - padX} y2={avgY}
          stroke="var(--warn)" strokeWidth="0.8" strokeDasharray="2,2"
          vectorEffect="non-scaling-stroke" opacity="0.6" />
        {/* Score line */}
        <polyline points={pts.join(" ")} fill="none"
          stroke="var(--accent)" strokeWidth="1.8"
          strokeLinejoin="round" strokeLinecap="round"
          vectorEffect="non-scaling-stroke" />
        {/* Dots */}
        {scores.map((v, i) => {
          const x = padX + i * xStep;
          const y = padY + (1 - v) * (H - padY * 2);
          const color = v >= 0.7 ? "var(--success)" : v >= 0.4 ? "var(--warn)" : "var(--danger)";
          return <circle key={i} cx={x} cy={y} r="2.5" fill={color} vectorEffect="non-scaling-stroke" />;
        })}
      </svg>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "var(--text-3)", marginTop: 4 }}>
        {scores.map((v, i) => (
          <span key={i} style={{ fontFamily: "JetBrains Mono", color: v >= 0.7 ? "var(--success)" : v >= 0.4 ? "var(--warn)" : "var(--danger)" }}>
            {Math.round(v * 100)}%
          </span>
        ))}
      </div>
      <div style={{ fontSize: 11, color: "var(--warn)", marginTop: 6, textAlign: "right" }}>
        ---- avg {Math.round(avg * 100)}%
      </div>
    </div>
  );
}

function DifficultyChart({ history }) {
  const max = 5;
  const w   = 100 / (history.length - 1 || 1);
  const points = history.map((v, i) => `${i * w},${100 - (v / max) * 100}`).join(" ");
  const colors = ["var(--success)", "#7bcf6b", "var(--warn)", "#ff8c4f", "var(--danger)"];

  return (
    <div>
      <svg viewBox="0 0 100 40" preserveAspectRatio="none" style={{ width: "100%", height: 64 }}>
        <polyline points={points} fill="none" stroke="var(--accent)"
          strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round"
          vectorEffect="non-scaling-stroke" />
        {history.map((v, i) => (
          <circle key={i} cx={i * w} cy={100 - (v / max) * 100} r="2.5"
            fill={colors[v - 1] || "var(--accent)"} vectorEffect="non-scaling-stroke" />
        ))}
      </svg>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "var(--text-3)" }}>
        <span>Q1</span><span>Q{history.length}</span>
      </div>
    </div>
  );
}

// ── Small helpers ─────────────────────────────────────────────────
function TopicScoreRow({ topic, score }) {
  const pct   = Math.round(score * 100);
  const color = pct >= 70 ? "var(--success)" : pct >= 40 ? "var(--warn)" : "var(--danger)";
  return (
    <div className="topic-score-row">
      <span className="topic-score-label">{topic.replace(/_/g, " ")}</span>
      <div className="progress-bar" style={{ flex: 1, margin: "0 12px" }}>
        <div className="progress-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span style={{ fontSize: 13, fontWeight: 700, color, minWidth: 38, textAlign: "right", fontFamily: "JetBrains Mono" }}>
        {pct}%
      </span>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="report-page page">
      <div style={{ height: 60, background: "var(--surface)", borderBottom: "1px solid var(--border)" }} />
      <div className="report-content">
        <div className="skeleton" style={{ height: 200, borderRadius: 16, marginBottom: 16 }} />
        <div className="skeleton" style={{ height: 44, borderRadius: 10, maxWidth: 600, marginBottom: 20 }} />
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
          <div className="skeleton" style={{ height: 200, borderRadius: 16 }} />
          <div className="skeleton" style={{ height: 200, borderRadius: 16 }} />
        </div>
      </div>
    </div>
  );
}
