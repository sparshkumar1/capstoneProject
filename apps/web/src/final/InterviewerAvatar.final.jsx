import { useState, useEffect, useRef } from "react";
import "../InterviewerAvatar.css";

export default function InterviewerAvatarFinal({ question, questionIndex, isThinking = false }) {
  const [phase, setPhase] = useState("idle");
  const [displayedText, setDisplayedText] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const typeRef = useRef(null);
  const prevIndexRef = useRef(null);

  useEffect(() => {
    if (!question || questionIndex === prevIndexRef.current) return;
    prevIndexRef.current = questionIndex;

    clearTimeout(typeRef.current);
    setDisplayedText("");
    setPhase("idle");
    setIsSpeaking(false);

    const t1 = setTimeout(() => {
      setPhase("intro");
      setIsSpeaking(true);
    }, 600);

    const t2 = setTimeout(() => {
      setPhase("typing");
      typeQuestion(question.text);
    }, 900);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [questionIndex, question]);

  const typeQuestion = (text) => {
    let i = 0;
    setDisplayedText("");

    const tick = () => {
      i += 1;
      setDisplayedText(text.slice(0, i));
      if (i < text.length) {
        const ch = text[i - 1];
        const delay = ch === "." || ch === "?" ? 180 : ch === "," || ch === ";" ? 90 : ch === " " ? 28 : 22;
        typeRef.current = setTimeout(tick, delay);
      } else {
        setPhase("done");
        setIsSpeaking(false);
      }
    };

    typeRef.current = setTimeout(tick, 30);
  };

  useEffect(() => {
    if (isThinking) {
      clearTimeout(typeRef.current);
      setPhase("thinking");
      setIsSpeaking(false);
    }
  }, [isThinking]);

  useEffect(() => () => clearTimeout(typeRef.current), []);

  const orbs = isSpeaking ? 5 : isThinking ? 3 : 0;

  return (
    <div className={`interviewer-wrap phase-${phase}`}>
      <div className="interviewer-avatar-col">
        <div className={`avatar-rings ${isSpeaking ? "speaking" : ""} ${isThinking ? "thinking" : ""}`}>
          <div className="ring ring-1" />
          <div className="ring ring-2" />
          <div className="ring ring-3" />
        </div>

        <div className={`avatar-face ${isSpeaking ? "speaking" : ""} ${isThinking ? "thinking" : ""}`}>
          <div className="avatar-eyes">
            <div className="eye left-eye"><div className="pupil" /></div>
            <div className="eye right-eye"><div className="pupil" /></div>
          </div>
          <div className={`avatar-mouth ${isSpeaking ? "open" : ""}`}><div className="mouth-inner" /></div>
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

      <div className="speech-bubble-col">
        <div className={`speech-bubble ${phase === "idle" ? "hidden" : "visible"}`}>
          <div className="bubble-tail" />

          {question && phase !== "idle" && (
            <div className="bubble-meta">
              <span className="bubble-chip chip-q">Question {questionIndex}</span>
              {question.topic && <span className="bubble-chip chip-topic">{question.topic.replace(/_/g, " ")}</span>}
              {question.difficulty && (
                <span className={`bubble-chip chip-diff diff-${question.difficulty}`}>
                  {"●".repeat(question.difficulty)}{"○".repeat(5 - question.difficulty)}
                </span>
              )}
            </div>
          )}

          <div className="bubble-text">
            {phase === "intro" && <span className="intro-text">Here is your next question...</span>}
            {(phase === "typing" || phase === "done") && (
              <>
                <span className="typed-text">{displayedText}</span>
                {phase === "typing" && <span className="type-cursor">|</span>}
              </>
            )}
            {phase === "thinking" && <span className="thinking-text">Analysing your response...</span>}
          </div>

          {phase === "done" && (
            <div className="bubble-cta">
              <span className="mic-cue">Your turn - speak or type your answer</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
