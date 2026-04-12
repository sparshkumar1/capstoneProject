/**
 * FeedbackCard — rich per-turn feedback panel for PrepAIred.
 *
 * Renders all 15 FeedbackAgent fields:
 *   final_score, grade, score_breakdown,
 *   strong_points, incorrect_or_incomplete, missing_concepts,
 *   how_to_improve, communication_tips, covered_concepts,
 *   trend, trend_note, justification, transcript,
 *   decision_source, vague_points
 */

import "./FeedbackCard.css";

const GRADE_COLOR = {
  A: "var(--success)",
  B: "var(--accent-2)",
  C: "var(--warn)",
  D: "#ff8c4f",
  F: "var(--danger)",
};

const TREND_META = {
  improving: { icon: "↑", color: "var(--success)", label: "Improving" },
  declining:  { icon: "↓", color: "var(--danger)",  label: "Declining"  },
  stable:     { icon: "→", color: "var(--warn)",    label: "Stable"     },
};

function ScoreBar({ label, value, color }) {
  const pct = Math.round((value ?? 0) * 100);
  return (
    <div className="fc-bar-row">
      <span className="fc-bar-label">{label}</span>
      <div className="fc-bar-track">
        <div
          className="fc-bar-fill"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      <span className="fc-bar-pct" style={{ color }}>{pct}%</span>
    </div>
  );
}

function SectionHeader({ icon, title, color }) {
  return (
    <div className="fc-section-header">
      <span className="fc-section-icon" style={{ background: `color-mix(in srgb, ${color} 14%, transparent)` }}>
        {icon}
      </span>
      <span className="fc-section-title">{title}</span>
    </div>
  );
}

export default function FeedbackCard({ feedback, onNext, awaitingNext }) {
  if (!feedback) return null;

  const score   = feedback.final_score ?? 0;
  const grade   = feedback.grade ?? "—";
  const pct     = Math.round(score * 100);
  const gradeColor = GRADE_COLOR[grade] ?? "var(--text-2)";
  const trend   = feedback.trend ?? "stable";
  const trendMeta = TREND_META[trend] ?? TREND_META.stable;
  const sb      = feedback.score_breakdown ?? {};
  const strong  = feedback.strong_points ?? [];
  const errors  = feedback.incorrect_or_incomplete ?? [];
  const missing = feedback.missing_concepts ?? [];
  const covered = feedback.covered_concepts ?? [];
  const improve = feedback.how_to_improve ?? [];
  const commTips = feedback.communication_tips ?? [];
  const trendNote = feedback.trend_note ?? "";
  const justification = feedback.justification ?? "";
  const transcript    = feedback.transcript ?? "";
  const source        = feedback.decision_source ?? "evaluator";

  return (
    <div className="feedback-card-rich fade-up">
      {/* ── Header row ─────────────────────────────────────── */}
      <div className="fc-header">
        <div className="fc-header-left">
          <div className="fc-grade-ring" style={{ borderColor: gradeColor, color: gradeColor }}>
            {grade}
          </div>
          <div>
            <div className="fc-score-big" style={{ color: gradeColor }}>{pct}%</div>
            <div className="fc-source">{source}</div>
          </div>
        </div>

        <div className="fc-header-right">
          {trendNote && (
            <div className="fc-trend-chip" style={{ color: trendMeta.color, borderColor: trendMeta.color }}>
              <span className="fc-trend-icon">{trendMeta.icon}</span>
              {trendMeta.label}
            </div>
          )}
          {feedback.decision_source && (
            <span className="badge badge-neutral" style={{ fontSize: 10 }}>{source}</span>
          )}
        </div>
      </div>

      {trendNote && (
        <p className="fc-trend-note">{trendNote}</p>
      )}

      {/* ── Score Breakdown ─────────────────────────────────── */}
      <div className="fc-section">
        <SectionHeader icon="📊" title="Score Breakdown" color="var(--accent)" />
        <div className="fc-bars">
          <ScoreBar label="Semantic relevance"  value={sb.semantic_similarity} color="var(--accent)" />
          <ScoreBar label="Concept coverage"    value={sb.concept_coverage}    color="var(--accent-2)" />
          <ScoreBar label="Reasoning quality"   value={sb.reasoning_quality}   color="#a855f7" />
          <ScoreBar label="Confidence signal"   value={sb.confidence_signal}   color="var(--warn)" />
          <ScoreBar label="Overall"             value={sb.overall ?? score}    color={gradeColor} />
        </div>
      </div>

      {/* ── Strong Points ───────────────────────────────────── */}
      {strong.length > 0 && (
        <div className="fc-section">
          <SectionHeader icon="💪" title="What You Got Right" color="var(--success)" />
          <ul className="fc-check-list">
            {strong.map((s, i) => (
              <li key={i} className="fc-check-item">
                <span className="fc-check-icon">✓</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ── Covered vs Missing Concepts ─────────────────────── */}
      {(covered.length > 0 || missing.length > 0) && (
        <div className="fc-section">
          <SectionHeader icon="🧩" title="Concepts" color="var(--accent-2)" />
          <div className="fc-concepts-row">
            {covered.length > 0 && (
              <div className="fc-concept-group">
                <span className="fc-concept-group-label" style={{ color: "var(--success)" }}>Covered</span>
                <div className="fc-pills">
                  {covered.map((c, i) => (
                    <span key={i} className="badge badge-success">{c}</span>
                  ))}
                </div>
              </div>
            )}
            {missing.length > 0 && (
              <div className="fc-concept-group">
                <span className="fc-concept-group-label" style={{ color: "var(--danger)" }}>Missing</span>
                <div className="fc-pills">
                  {missing.map((m, i) => (
                    <span key={i} className="badge badge-danger">{m}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Misconceptions / Errors ─────────────────────────── */}
      {errors.length > 0 && (
        <div className="fc-section">
          <SectionHeader icon="⚠️" title="Incorrect or Incomplete" color="var(--danger)" />
          <div className="fc-error-list">
            {errors.map((e, i) => (
              <div key={i} className={`fc-error-item ${e.severity === "major" ? "major" : "minor"}`}>
                <div className="fc-error-top">
                  <span className="fc-error-said">"{e.what_was_said}"</span>
                  <span className={`badge ${e.severity === "major" ? "badge-danger" : "badge-warn"}`}>
                    {e.severity}
                  </span>
                </div>
                <div className="fc-error-fix">
                  <span className="fc-fix-arrow">→</span>
                  {e.correction}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── How to Improve ──────────────────────────────────── */}
      {improve.length > 0 && (
        <div className="fc-section">
          <SectionHeader icon="🎯" title="How to Improve" color="var(--accent)" />
          <ol className="fc-improve-list">
            {improve.map((tip, i) => (
              <li key={i} className="fc-improve-item">
                <span className="fc-improve-num">{i + 1}</span>
                <span>{tip}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* ── Communication Tips ──────────────────────────────── */}
      {commTips.length > 0 && (
        <div className="fc-section">
          <SectionHeader icon="🎙️" title="Delivery & Communication" color="var(--accent-2)" />
          <ul className="fc-comm-list">
            {commTips.map((tip, i) => (
              <li key={i} className="fc-comm-item">
                <span className="fc-comm-dot" />
                {tip}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ── Justification / Narrative ───────────────────────── */}
      {justification && (
        <div className="fc-section fc-justification">
          <SectionHeader icon="🤖" title="AI Summary" color="var(--text-3)" />
          <p className="fc-just-text">{justification}</p>
        </div>
      )}

      {/* ── Transcript ──────────────────────────────────────── */}
      {transcript && (
        <div className="fc-transcript">
          <span className="fc-transcript-label">Your answer</span>
          <p className="fc-transcript-text">"{transcript}"</p>
        </div>
      )}

      {/* ── Next button ─────────────────────────────────────── */}
      <div className="fc-footer">
        <span className="fc-footer-hint">Review this feedback, then continue when ready.</span>
        <button
          className="btn btn-primary btn-sm"
          onClick={onNext}
          disabled={!awaitingNext}
        >
          Next Question →
        </button>
      </div>
    </div>
  );
}
