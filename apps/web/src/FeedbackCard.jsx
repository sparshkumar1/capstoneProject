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

import { useState, useEffect } from "react";
import "./FeedbackCard.css";

const TREND_META = {
  improving: { icon: "↑", color: "var(--success)", label: "Improving" },
  declining:  { icon: "↓", color: "var(--danger)",  label: "Declining"  },
  stable:     { icon: "→", color: "var(--warn)",    label: "Stable"     },
};

/**
 * Strips redundant improvement tips that merely re-state missing concepts.
 * E.g., if missing_concepts includes "single pass iteration", advice like
 * "Cover missing concept: single pass iteration" is pruned.
 */
export function filterUniqueImprovementTips(improveList, missingList) {
  if (!Array.isArray(improveList) || improveList.length === 0) return [];

  const normalizedMissing = (missingList || [])
    .filter((m) => typeof m === "string" && m.trim())
    .map((m) => m.trim().toLowerCase());

  const seen = new Set();
  const result = [];

  for (const item of improveList) {
    if (!item || typeof item !== "string") continue;
    const trimmed = item.trim();
    if (!trimmed) continue;

    // Strip common repetitive prefixes
    const stripped = trimmed
      .replace(/^(cover\s+missing\s+concept\s*:?|missing\s+concept\s*:?|cover\s*:?|review\s*:?)\s*/i, "")
      .trim();

    const lowerStripped = stripped.toLowerCase();

    // Check if stripped tip duplicates any missing concept
    const isMissingDuplicate = normalizedMissing.some((m) => {
      if (lowerStripped === m) return true;
      if (lowerStripped === `cover ${m}`) return true;
      if (lowerStripped === `review ${m}`) return true;
      if (lowerStripped === `address ${m}`) return true;
      return false;
    });

    if (isMissingDuplicate) {
      continue;
    }

    if (!seen.has(lowerStripped)) {
      seen.add(lowerStripped);
      result.push(trimmed);
    }
  }

  return result;
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

  // 1. If narrative feedback provided, validate grounding and lack of score leaks
  const rawNarrative = (typeof feedback.narrative_feedback === "string" ? feedback.narrative_feedback : "").trim();
  const covered = Array.isArray(feedback.covered_concepts) ? feedback.covered_concepts : [];
  const missing = Array.isArray(feedback.missing_concepts) ? feedback.missing_concepts : [];
  const errors = Array.isArray(feedback.incorrect_or_incomplete) ? feedback.incorrect_or_incomplete : [];
  const strong = Array.isArray(feedback.strong_points) ? feedback.strong_points : [];
  const rawImprove = Array.isArray(feedback.how_to_improve) ? feedback.how_to_improve : [];
  const improve = filterUniqueImprovementTips(rawImprove, missing);
  const commTips = Array.isArray(feedback.communication_tips) ? feedback.communication_tips : [];
  const transcript = (typeof feedback.transcript === "string" ? feedback.transcript : "").trim();

  const isScoreTemplate = /Grade\s+[A-Za-z0-9+-]+/i.test(rawNarrative) && /Semantic/i.test(rawNarrative);

  if (rawNarrative && !isScoreTemplate) {
    const sanitized = rawNarrative
      .replace(/\bGrade\s+[A-Za-z0-9+-]+(?:\s*\(\d+%\))?/gi, "")
      .replace(/\bScore(?:\s*(?:change|delta|improved by|decreased by))?:\s*[+-]?\d+(?:\.\d+)?%?/gi, "")
      .replace(/\b[+-]?\d+(?:\.\d+)?%/g, "")
      .replace(/\b(?:Semantic|Reasoning|Concept coverage|Confidence)\s+\d+%?/gi, "")
      .replace(/\b(?:improved|decreased)\s+by\s+[+-]?\d+%?/gi, "")
      .replace(/\bScore\s+[+-]?\d+(?:\.\d+)?\b/gi, "")
      .replace(/\s{2,}/g, " ")
      .trim();

    // Contradiction check: LLM must not claim missing concepts were correctly covered
    const hasContradiction = missing.some((m) => {
      const lowM = m.toLowerCase();
      return (
        sanitized.toLowerCase().includes(`correctly explained ${lowM}`) ||
        sanitized.toLowerCase().includes(`correctly covered ${lowM}`)
      );
    });

    // Grounding check: ensure narrative is grounded in topic or covered/missing concepts
    const isGrounded =
      (covered.length === 0 && missing.length === 0) ||
      covered.some((c) => sanitized.toLowerCase().includes(c.toLowerCase())) ||
      missing.some((m) => sanitized.toLowerCase().includes(m.toLowerCase()));

    if (!hasContradiction && isGrounded && sanitized.length > 20) {
      return sanitized;
    }
  }

  // 2. Extract structured evaluation facts for dynamic qualitative synthesis
  const wordCount = transcript ? transcript.split(/\s+/).filter(Boolean).length : 0;
  const isCoding = feedback.test_cases_passed !== undefined || feedback.tests_total !== undefined;

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

export default function FeedbackCard({ feedback, onNext, awaitingNext, onRetry }) {
  if (!feedback) return null;

  const [showBestAnswer, setShowBestAnswer] = useState(false);

  useEffect(() => {
    setShowBestAnswer(false);
  }, [feedback?.attempt_number, feedback?.transcript]);

  const strong = Array.isArray(feedback.strong_points) ? feedback.strong_points : [];
  const errors = Array.isArray(feedback.incorrect_or_incomplete) ? feedback.incorrect_or_incomplete : [];
  const missing = Array.isArray(feedback.missing_concepts) ? feedback.missing_concepts : [];
  const covered = Array.isArray(feedback.covered_concepts) ? feedback.covered_concepts : [];
  const rawImprove = Array.isArray(feedback.how_to_improve) ? feedback.how_to_improve : [];
  const improve = filterUniqueImprovementTips(rawImprove, missing);
  const commTips = Array.isArray(feedback.communication_tips) ? feedback.communication_tips : [];
  const transcript = typeof feedback.transcript === "string" ? feedback.transcript : "";
  const source = typeof feedback.decision_source === "string" ? feedback.decision_source : "evaluator";
  const aiSummary = generateQualitativeSummary(feedback);
  const comparison = feedback.comparison && typeof feedback.comparison === "object" ? feedback.comparison : null;
  const attemptNum = typeof feedback.attempt_number === "number" ? feedback.attempt_number : 1;
  const hasPreviousComparable = Boolean(comparison && comparison.has_previous_best);

  // Best-answer status is backend-authoritative: the backend reports an eligible (correct / partially correct)
  // best attempt via `authoritative_best_answer` + `best_answer`. Nothing is inferred from the current answer.
  const backendBest =
    feedback.authoritative_best_answer === true && feedback.best_answer && typeof feedback.best_answer === "object"
      ? feedback.best_answer
      : null;
  const isNewBest = feedback.is_best === true && backendBest !== null;
  const authoritativeBestAnswer = backendBest && typeof backendBest.answer === "string" ? backendBest.answer : "";

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
          {attemptNum > 1 && (
            <span className="badge badge-accent" style={{ fontWeight: 600, fontSize: "11px" }}>
              Attempt #{attemptNum}
            </span>
          )}
          {source && (
            <span className="badge badge-neutral" style={{ fontSize: 10 }}>{source}</span>
          )}
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

      {/* ── Retry / Best-Answer Status Section ──────────────── */}
      {hasPreviousComparable && backendBest && (
        <div className="fc-section fc-best-status-section" style={{ background: "rgba(255,255,255,0.02)", borderLeft: isNewBest ? "3px solid var(--success)" : "3px solid var(--warn)" }}>
          <SectionHeader
            icon={isNewBest ? "🏆" : "🔄"}
            title="Retry / Best-Answer Status"
            color={isNewBest ? "var(--success)" : "var(--warn)"}
          />

          <div style={{ marginTop: "8px" }}>
            {isNewBest ? (
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                  <span className="badge badge-success" style={{ fontWeight: 700, fontSize: "12px", padding: "3px 10px" }}>
                    ✓ New Best Answer
                  </span>
                </div>
                <p style={{ margin: "4px 0 0 0", fontSize: "13px", color: "var(--text-1)", lineHeight: 1.5 }}>
                  Your latest answer is now your best attempt for this question.
                </p>
              </div>
            ) : (
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                  <span className="badge badge-neutral" style={{ fontWeight: 600, fontSize: "12px", padding: "3px 10px" }}>
                    Your Previous Best Answer Remains Best
                  </span>
                </div>
                <p style={{ margin: "4px 0 0 0", fontSize: "13px", color: "var(--text-2)", lineHeight: 1.5 }}>
                  Your latest attempt did not replace your previous best answer.
                </p>
              </div>
            )}

            {/* Grounded Improvements (from structured comparison only) */}
            {comparison?.resolved_concepts && comparison.resolved_concepts.length > 0 && (
              <div style={{ marginTop: "12px" }}>
                <span style={{ fontSize: "12px", color: "var(--success)", fontWeight: 600 }}>What improved:</span>
                <ul className="fc-check-list" style={{ marginTop: "4px" }}>
                  {comparison.resolved_concepts.map((c, i) => (
                    <li key={i} className="fc-check-item" style={{ fontSize: "12px" }}>
                      <span className="fc-check-icon">✓</span>
                      <span>Covered {c}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Still to improve (if not best and remaining concepts exist) */}
            {!isNewBest && comparison?.remaining_concepts && comparison.remaining_concepts.length > 0 && (
              <div style={{ marginTop: "10px" }}>
                <span style={{ fontSize: "12px", color: "var(--warn)", fontWeight: 600 }}>Still to improve:</span>
                <div className="fc-pills" style={{ marginTop: "4px" }}>
                  {comparison.remaining_concepts.map((m, i) => (
                    <span key={i} className="badge badge-warn">○ {m}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Authoritative Best Answer Inline Disclosure */}
            {authoritativeBestAnswer && (
              <div style={{ marginTop: "12px" }}>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => setShowBestAnswer((prev) => !prev)}
                  aria-expanded={showBestAnswer}
                  aria-controls="fc-best-answer-panel"
                  style={{ display: "inline-flex", alignItems: "center", gap: "6px", fontSize: "12px" }}
                >
                  <span>{showBestAnswer ? "Hide Best Answer ▴" : "View Best Answer ▾"}</span>
                </button>

                {showBestAnswer && (
                  <div
                    id="fc-best-answer-panel"
                    style={{
                      marginTop: "10px",
                      padding: "12px 14px",
                      background: "var(--bg-2)",
                      borderRadius: "8px",
                      border: "1px solid var(--border)",
                      fontSize: "13px",
                      lineHeight: 1.6,
                      color: "var(--text-1)",
                    }}
                  >
                    <div style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.04em", color: "var(--accent-2)", marginBottom: "6px" }}>
                      Authoritative Best Answer
                    </div>
                    {authoritativeBestAnswer.includes("\n") || authoritativeBestAnswer.includes(";") ? (
                      <pre className="code-snippet" style={{ margin: 0, fontSize: "12px" }}><code>{authoritativeBestAnswer}</code></pre>
                    ) : (
                      <div style={{ fontStyle: "italic", color: "var(--text-2)" }}>
                        &quot;{authoritativeBestAnswer}&quot;
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Transcript ──────────────────────────────────────── */}
      {transcript && (
        <div className="fc-transcript">
          <span className="fc-transcript-label">Your answer</span>
          <p className="fc-transcript-text">&quot;{transcript}&quot;</p>
        </div>
      )}

      {/* ── Action Buttons ──────────────────────────────────── */}
      <div className="fc-footer" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
          {onRetry && (
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={onRetry}
              disabled={!awaitingNext}
              style={{ display: "inline-flex", alignItems: "center", gap: "6px", fontWeight: 600 }}
            >
              <span>↻</span> Try Again
            </button>
          )}
          <span className="fc-footer-hint" style={{ fontSize: "11px", color: "var(--text-3)" }}>
            Apply the feedback and answer again.
          </span>
        </div>
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
