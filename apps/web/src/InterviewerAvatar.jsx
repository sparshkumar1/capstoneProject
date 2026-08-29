import { useState, useEffect, useRef } from "react";
import "./InterviewerAvatar.css";

/**
 * InterviewerAvatar
 * Props:
 *   question      - current question object { text, topic, difficulty, type }
 *   questionIndex - used to trigger re-animation on new question
 *   isThinking    - true while server is evaluating (shows "thinking" state)
 */
export default function InterviewerAvatar({ question, questionIndex, isThinking = false }) {
  const [phase, setPhase] = useState("idle");
  // phases: idle -> intro -> done -> thinking
  const [isSpeaking, setIsSpeaking] = useState(false);
  const animTimerRef = useRef(null);
  const prevIndexRef = useRef(null);

  // Trigger animation sequence whenever a new question arrives
  useEffect(() => {
    if (!question || questionIndex === prevIndexRef.current) return;
    prevIndexRef.current = questionIndex;

    // Reset
    clearTimeout(animTimerRef.current);
    setPhase("idle");
    setIsSpeaking(false);

    // Phase 1 - brief "speaking" intro when question is presented
    const t1 = setTimeout(() => {
      setPhase("intro");
      setIsSpeaking(true);
    }, 400);

    // Phase 2 - transition to awaiting candidate response
    const t2 = setTimeout(() => {
      setPhase("done");
      setIsSpeaking(false);
    }, 2200);

    animTimerRef.current = t2;

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [questionIndex, question]);

  // Thinking state overrides speaking while feedback is being generated.
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

  const orbs = isSpeaking ? 5 : isThinking ? 3 : 0;

  return (
    <div className={`interviewer-wrap phase-${phase}`}>
      {/* Avatar column */}
      <div className="interviewer-avatar-col">
        {/* Pulse rings behind avatar */}
        <div className={`avatar-rings ${isSpeaking ? "speaking" : ""} ${isThinking ? "thinking" : ""}`}>
          <div className="ring ring-1" />
          <div className="ring ring-2" />
          <div className="ring ring-3" />
        </div>

        {/* Avatar face */}
        <div className={`avatar-face ${isSpeaking ? "speaking" : ""} ${isThinking ? "thinking" : ""}`}>
          <div className="avatar-eyes">
            <div className="eye left-eye">
              <div className="pupil" />
            </div>
            <div className="eye right-eye">
              <div className="pupil" />
            </div>
          </div>
          <div className={`avatar-mouth ${isSpeaking ? "open" : ""}`}>
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
          ) : isSpeaking ? (
            <span className="speaking-label">● Speaking</span>
          ) : phase === "done" ? (
            <span className="done-label">Awaiting your answer</span>
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

      {/* Speech bubble column */}
      <div className="speech-bubble-col">
        <div className={`speech-bubble ${phase === "idle" ? "hidden" : "visible"}`}>
          <div className="bubble-tail" />

          {question && phase !== "idle" && (
            <div className="bubble-meta">
              <span className="bubble-chip chip-q">Question {questionIndex}</span>
              {question.topic && (
                <span className="bubble-chip chip-topic">
                  {question.topic.replace(/_/g, " ")}
                </span>
              )}
              {question.difficulty && (
                <span className={`bubble-chip chip-diff diff-${question.difficulty}`}>
                  {"●".repeat(question.difficulty)}{"○".repeat(5 - question.difficulty)}
                </span>
              )}
            </div>
          )}

          <div className="bubble-text">
            {phase === "intro" && (
              <span className="intro-text">Here&apos;s your next question...</span>
            )}
            {phase === "done" && (
              <span className="intro-text">Please review the question below and explain your approach.</span>
            )}
            {phase === "thinking" && (
              <span className="thinking-text">Analysing your response...</span>
            )}
          </div>

          {phase === "done" && (
            <div className="bubble-cta">
              <span className="mic-cue">Your turn — speak or write your answer</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
