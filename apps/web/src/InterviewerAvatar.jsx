import { useState, useEffect, useRef } from "react";
import "./InterviewerAvatar.css";
import { questionProgressLabel } from "./questionProgress";

/**
 * InterviewerAvatar — unified top question card component for PrepAIred.
 *
 * Integrates the animated interviewer avatar (speaking/thinking animations,
 * pulse rings, audio orbs) with the complete question presentation (metadata
 * chips, question text, code snippet, constraints, prior history, and skip action)
 * inside a single, cohesive card.
 */
export default function InterviewerAvatar({
  question,
  questionIndex = 1,
  totalQuestions,
  difficulty,
  followUpQueued = false,
  isFollowup = false,
  session = null,
  baselineDone = true,
  stageHint = "",
  ttsActive = false,
  isThinking = false,
  onSkip,
  connected = true,
}) {
  const [phase, setPhase] = useState("idle");
  // phases: idle -> intro -> done -> thinking
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [showPriorBest, setShowPriorBest] = useState(false);
  const animTimerRef = useRef(null);
  const prevIndexRef = useRef(null);

  // Trigger animation sequence whenever a new question arrives
  useEffect(() => {
    // key on the question itself: a follow-up shares its parent's primary index but is a new question
    const questionKey = question?.id ?? questionIndex;
    if (!question || questionKey === prevIndexRef.current) return;
    prevIndexRef.current = questionKey;

    clearTimeout(animTimerRef.current);
    setPhase("idle");
    setIsSpeaking(false);
    setShowPriorBest(false);

    // Phase 1 - brief "speaking" intro when question is presented
    const t1 = setTimeout(() => {
      setPhase("intro");
      setIsSpeaking(true);
    }, 200);

    // Phase 2 - transition to awaiting candidate response
    const t2 = setTimeout(() => {
      setPhase("done");
      setIsSpeaking(false);
    }, 2000);

    animTimerRef.current = t2;

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [questionIndex, question]);

  // Thinking state overrides speaking while feedback is being generated
  useEffect(() => {
    if (isThinking) {
      clearTimeout(animTimerRef.current);
      setPhase("thinking");
      setIsSpeaking(false);
    }
  }, [isThinking]);

  useEffect(() => {
    return () => clearTimeout(animTimerRef.current);
  }, []);

  const avatarSpeaking = isSpeaking || ttsActive;
  const orbs = avatarSpeaking ? 5 : isThinking ? 3 : 0;

  if (!question) {
    return (
      <div className="card question-card interviewer-wrap phase-idle">
        <div className="waiting-state" style={{ width: "100%", padding: "30px 20px" }}>
          <div className="waiting-spinner" />
          <p>{connected ? "Loading question…" : "Connecting to interview server…"}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`card question-card interviewer-wrap phase-${phase}`}>
      {/* Avatar column */}
      <div className="interviewer-avatar-col">
        {/* Pulse rings behind avatar */}
        <div className={`avatar-rings ${avatarSpeaking ? "speaking" : ""} ${isThinking ? "thinking" : ""}`}>
          <div className="ring ring-1" />
          <div className="ring ring-2" />
          <div className="ring ring-3" />
        </div>

        {/* Avatar face */}
        <div className={`avatar-face ${avatarSpeaking ? "speaking" : ""} ${isThinking ? "thinking" : ""}`}>
          <div className="avatar-eyes">
            <div className="eye left-eye">
              <div className="pupil" />
            </div>
            <div className="eye right-eye">
              <div className="pupil" />
            </div>
          </div>
          <div className={`avatar-mouth ${avatarSpeaking ? "open" : ""}`}>
            <div className="mouth-inner" />
          </div>
        </div>

        <div className="avatar-label">
          {isThinking ? (
            <span className="thinking-dots">
              <span>Evaluating</span>
              <span className="dot-1">.</span>
              <span className="dot-2">.</span>
              <span className="dot-3">.</span>
            </span>
          ) : avatarSpeaking ? (
            <span className="speaking-label">● Speaking</span>
          ) : phase === "done" ? (
            <span className="done-label">Awaiting answer</span>
          ) : (
            <span className="idle-label">AI Interviewer</span>
          )}
        </div>

        {orbs > 0 && (
          <div className="sound-orbs">
            {Array.from({ length: orbs }).map((_, i) => (
              <div key={i} className={`orb-dot orb-${i + 1}`} />
            ))}
          </div>
        )}
      </div>

      {/* Unified Question speech bubble column */}
      <div className="speech-bubble-col">
        <div className="speech-bubble visible">
          <div className="bubble-tail" />

          {/* Question Metadata chips */}
          <div className="question-meta" style={{ marginBottom: "12px", display: "flex", flexWrap: "wrap", gap: "6px" }}>
            <span className="badge badge-accent">
              {questionProgressLabel({ isFollowup: isFollowup || followUpQueued, questionIndex, totalQuestions }, true)}
            </span>
            {question.topic && (
              <span className="badge badge-neutral">
                {question.topic.replace(/_/g, " ")}
              </span>
            )}
            {session?.interview_mode === "demo_rl" && !baselineDone && (
              <span className="badge badge-warn">Baseline</span>
            )}
            {session?.interview_mode === "demo_rl" && baselineDone && (
              <span className="badge badge-success">RL Active</span>
            )}
            {difficulty !== undefined && (
              <span className="badge" style={{
                background: difficulty <= 2 ? "rgba(54,217,143,0.14)" : difficulty === 3 ? "rgba(255,184,79,0.14)" : "rgba(255,79,106,0.14)",
                color: difficulty <= 2 ? "var(--success)" : difficulty === 3 ? "var(--warn)" : "var(--danger)"
              }}>
                Level {difficulty}
              </span>
            )}
            {question.type && <span className="badge badge-neutral">{question.type}</span>}
          </div>

          {/* Prior Best Answer Collapsible Disclosure */}
          {question.historical_best && (
            <div className="prior-best-wrap" style={{ margin: "6px 0 12px 0" }}>
              <button
                type="button"
                className="prior-best-banner-btn"
                onClick={() => setShowPriorBest((v) => !v)}
                aria-expanded={showPriorBest}
                aria-controls="prior-best-panel"
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "8px 12px",
                  background: "rgba(0, 229, 200, 0.08)",
                  border: "1px solid rgba(0, 229, 200, 0.3)",
                  borderRadius: showPriorBest ? "8px 8px 0 0" : "8px",
                  color: "var(--accent-2)",
                  fontSize: "12px",
                  fontFamily: "inherit",
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "background 0.2s, border-color 0.2s",
                }}
              >
                <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <span style={{ fontSize: "13px" }}>↻</span>
                  <strong>Prior Best Answer</strong>
                  <span style={{ opacity: 0.6 }}>·</span>
                  <span style={{ opacity: 0.9 }}>Answered in a previous session</span>
                </span>
                <span style={{ fontSize: "12px", fontWeight: "bold" }}>
                  {showPriorBest ? "▴" : "▾"}
                </span>
              </button>

              {showPriorBest && (
                <div
                  id="prior-best-panel"
                  className="prior-best-expanded-panel"
                  style={{
                    padding: "10px 14px",
                    background: "rgba(0, 229, 200, 0.04)",
                    border: "1px solid rgba(0, 229, 200, 0.3)",
                    borderTop: "none",
                    borderRadius: "0 0 8px 8px",
                    fontSize: "12px",
                    color: "var(--text-1)",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                    <span style={{ fontSize: "11px", fontWeight: 600, color: "var(--accent-2)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                      Your previous best answer
                    </span>
                    <button
                      type="button"
                      onClick={() => setShowPriorBest(false)}
                      style={{
                        background: "none",
                        border: "none",
                        color: "var(--text-3)",
                        fontSize: "11px",
                        cursor: "pointer",
                        padding: "2px 4px",
                      }}
                    >
                      Hide previous answer ▴
                    </button>
                  </div>
                  {question.historical_best.answer ? (
                    question.historical_best.answer.includes("\n") || question.historical_best.answer.includes(";") ? (
                      <pre className="code-snippet" style={{ margin: 0, fontSize: "12px" }}>
                        <code>{question.historical_best.answer}</code>
                      </pre>
                    ) : (
                      <p style={{ margin: 0, fontStyle: "italic", lineHeight: 1.55, color: "var(--text-2)" }}>
                        &quot;{question.historical_best.answer}&quot;
                      </p>
                    )
                  ) : (
                    <p style={{ margin: 0, fontStyle: "italic", color: "var(--text-3)" }}>
                      Previous attempt recorded.
                    </p>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Stage Hint */}
          {stageHint && (
            <div style={{ marginTop: 4, marginBottom: 10, padding: "7px 12px", background: "var(--bg-2)", borderRadius: 8, fontSize: 12, color: "var(--text-2)", borderLeft: "3px solid var(--accent)" }}>
              {stageHint}
            </div>
          )}

          {/* Evaluating State note */}
          {isThinking && (
            <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--warn)", fontStyle: "italic", fontSize: 13, marginBottom: 10 }}>
              <span className="spinner" style={{ width: 13, height: 13, borderTopColor: "var(--warn)" }} />
              <span>Analysing your response...</span>
            </div>
          )}

          {/* Actual Question text */}
          <div className="question-text" style={{ fontSize: "15px", lineHeight: "1.65", color: "var(--text)", margin: "8px 0 12px 0" }}>
            {question.text}
          </div>

          {/* Code Snippet */}
          {question.code_snippet && (
            <pre className="code-snippet"><code>{question.code_snippet}</code></pre>
          )}

          {/* Constraints */}
          {question.constraints && (
            <div className="constraints-box">
              <span style={{ fontWeight: 600, fontSize: 12, color: "var(--text-2)" }}>Constraints: </span>
              {question.constraints}
            </div>
          )}

          {/* Question Footer Actions */}
          <div className="question-actions" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 10, marginTop: 14, paddingTop: 10, borderTop: "1px solid var(--border)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              {!ttsActive && !isThinking && onSkip && (
                <button type="button" className="btn btn-ghost btn-sm" onClick={onSkip} style={{ fontSize: 12 }}>
                  ⏭ Skip Question
                </button>
              )}
              {ttsActive && (
                <span style={{ fontSize: 12, color: "var(--text-3)", display: "flex", alignItems: "center", gap: 4 }}>
                  🔊 Reading question aloud...
                </span>
              )}
            </div>
            <span className="mic-cue" style={{ fontSize: 12, color: "var(--text-3)", fontFamily: "Syne", fontWeight: 600 }}>
              Your turn — speak or write your answer
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
