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

/**
 * Generates a dynamic, qualitative, score-free AI summary grounded in the
 * structured evaluation and candidate response.
 */
export function generateQualitativeSummary(feedback) {
  if (!feedback) return "";

  // 1. If Qwen or backend provided clean qualitative narrative feedback without score tokens:
  const rawNarrative = (feedback.narrative_feedback || "").trim();
  const hasScoreTokens = /Grade\s+[A-F]|Semantic\s+\d+%|Concept coverage\s+\d+%|Reasoning\s+\d+%|Confidence\s+\d+%|\b\d+%\b/i.test(rawNarrative);

  if (rawNarrative && !hasScoreTokens && rawNarrative.length > 25) {
    return rawNarrative;
  }

  // 2. Extract structured evaluation facts
  const covered   = Array.isArray(feedback.covered_concepts) ? feedback.covered_concepts : [];
  const missing   = Array.isArray(feedback.missing_concepts) ? feedback.missing_concepts : [];
  const errors    = Array.isArray(feedback.incorrect_or_incomplete) ? feedback.incorrect_or_incomplete : [];
  const strong    = Array.isArray(feedback.strong_points) ? feedback.strong_points : [];
  const improve   = Array.isArray(feedback.how_to_improve) ? feedback.how_to_improve : [];
  const commTips  = Array.isArray(feedback.communication_tips) ? feedback.communication_tips : [];
  const transcript = (feedback.transcript ?? "").trim();
  const wordCount = transcript ? transcript.split(/\s+/).filter(Boolean).length : 0;
  const isCoding  = feedback.test_cases_passed !== undefined || feedback.tests_total !== undefined;

  // Handle coding submission feedback
  if (isCoding) {
    const passed = feedback.passed || (feedback.test_cases_passed !== undefined && feedback.test_cases_passed === feedback.tests_total);
    if (passed) {
      return "All test cases passed successfully with clean execution in the sandbox environment.";
    }
    if (feedback.compilation_error || (feedback.stderr && feedback.stderr.includes("error:"))) {
      return "Code compilation encountered errors. Review syntax, variable declarations, and header inclusions before re-running.";
    }
    return "The solution compiled, but some test cases failed. Check edge cases, boundary conditions, and memory handling.";
  }

  // Handle verbal responses: Empty or extremely brief
  if (!transcript || wordCount < 4) {
    if (missing.length > 0) {
      return `No substantive verbal explanation was recorded. Key concepts required for this question include: ${missing.slice(0, 2).join(", ")}.`;
    }
    return "No substantive response was recorded. Provide a clear technical explanation covering the core mechanics and trade-offs.";
  }

  const parts = [];

  // Scenario 1: Misconceptions / Inaccuracies detected
  if (errors.length > 0) {
    const primaryError = errors[0];
    const quote = primaryError.what_was_said ? ` regarding "${primaryError.what_was_said}"` : " in the core logic";
    const fix = primaryError.correction ? ` ${primaryError.correction}` : "";
    parts.push(`While relevant technical terminology was used, the explanation contained an inaccuracy${quote}.${fix}`);

    if (covered.length > 0) {
      parts.push(`On the other hand, you correctly touched upon ${covered[0]}.`);
    } else if (missing.length > 0) {
      parts.push(`Ensure you also address ${missing[0]} in your explanation.`);
    }
  }
  // Scenario 2: Strong mastery (concepts covered, no gaps, no misconceptions)
  else if (missing.length === 0 && covered.length > 0) {
    if (covered.length >= 2) {
      parts.push(`Clear and comprehensive explanation addressing both ${covered[0]} and ${covered[1]}.`);
    } else {
      parts.push(`Clear and accurate explanation directly addressing ${covered[0]}.`);
    }
    if (strong.length > 0 && strong[0] && strong[0] !== "General topic familiarity") {
      parts.push(`Key strength: ${strong[0]}.`);
    }
  }
  // Scenario 3: Partial coverage (some covered, some missing)
  else if (covered.length > 0 && missing.length > 0) {
    parts.push(`You accurately identified key principles of ${covered[0]}, but did not fully explain ${missing.slice(0, 2).join(" and ")}.`);
    if (improve.length > 0) {
      parts.push(improve[0]);
    } else {
      parts.push(`Elaborating on ${missing[0]} will make your solution complete.`);
    }
  }
  // Scenario 4: Missing key concepts without explicit misconception
  else if (missing.length > 0) {
    parts.push(`The response initiated the explanation, but key conceptual elements were not adequately addressed: ${missing.slice(0, 2).join(", ")}.`);
    if (improve.length > 0) {
      parts.push(improve[0]);
    }
  }
  // Scenario 5: General fallback grounded in strong points
  else {
    if (strong.length > 0 && strong[0] && strong[0] !== "General topic familiarity") {
      parts.push(`Solid explanation highlighting ${strong[0]}.`);
    } else {
      parts.push("Technical response recorded and evaluated across core logic and reasoning depth.");
    }
  }

  // Delivery observation note if available
  if (commTips.length > 0 && wordCount >= 15 && parts.length === 1) {
    parts.push(commTips[0]);
  }

  return parts.join(" ");
}

export default function FeedbackCard({ feedback, onNext, awaitingNext }) {
  if (!feedback) return null;

  const trend   = feedback.trend ?? "stable";
  const trendMeta = TREND_META[trend] ?? TREND_META.stable;
  const strong  = feedback.strong_points ?? [];
  const errors  = feedback.incorrect_or_incomplete ?? [];
  const missing = feedback.missing_concepts ?? [];
  const covered = feedback.covered_concepts ?? [];
  const improve = feedback.how_to_improve ?? [];
  const commTips = feedback.communication_tips ?? [];
  const trendNote = feedback.trend_note ?? "";
  const transcript    = feedback.transcript ?? "";
  const source        = feedback.decision_source ?? "evaluator";
  const aiSummary     = generateQualitativeSummary(feedback);

  return (
    <div className="feedback-card-rich fade-up">
      {/* ── Qualitative Header row ─────────────────────────── */}
      <div className="fc-header">
        <div className="fc-header-left">
          <div className="fc-status-icon" style={{ fontSize: 24 }}>
            📝
          </div>
          <div>
            <div className="fc-title" style={{ fontFamily: "Syne", fontWeight: 700, fontSize: 16, color: "var(--text-1)" }}>
              Feedback & Analysis
            </div>
            <div className="fc-source" style={{ fontSize: 11, color: "var(--text-3)", marginTop: 2 }}>
              Verified via {source}
            </div>
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
                  <span className="fc-error-said">&quot;{e.what_was_said}&quot;</span>
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

      {/* ── Qualitative AI Summary ────────────────────────── */}
      {aiSummary && (
        <div className="fc-section fc-justification">
          <SectionHeader icon="🤖" title="AI Summary" color="var(--text-3)" />
          <p className="fc-just-text">{aiSummary}</p>
        </div>
      )}

      {/* ── Transcript ──────────────────────────────────────── */}
      {transcript && (
        <div className="fc-transcript">
          <span className="fc-transcript-label">Your answer</span>
          <p className="fc-transcript-text">&quot;{transcript}&quot;</p>
        </div>
      )}

      {/* ── Next button ─────────────────────────────────────── */}
      <div className="fc-footer">
        <span className="fc-footer-hint">Review this feedback, then continue when ready.</span>
        <button
          type="button"
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
