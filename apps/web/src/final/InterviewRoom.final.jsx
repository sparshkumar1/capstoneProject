import { useState, useContext, useEffect, useRef } from "react";
import { SessionContext } from "../contexts";
import MonacoEditor from "../MonacoEditor";
import WaveformBar from "../WaveformBar";
import DifficultyTracker from "../DifficultyTracker";
import { useInterviewWS } from "../useInterviewWS";
import { useVoiceRecorder } from "../useVoiceRecorder";
import { api } from "../api";
import InterviewerAvatar from "./InterviewerAvatar.final";
import "../InterviewRoom.css";

const PANEL = { VOICE: "voice", CODE: "code" };

export default function InterviewRoomFinal({ navigate }) {
  const { session, candidate, setSession } = useContext(SessionContext);
  const sessionId = session?.id || "demo-session";

  const [question, setQuestion] = useState(null);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [totalQuestions] = useState(session?.num_questions || 5);
  const [feedback, setFeedback] = useState(null);
  const [hint, setHint] = useState(null);
  const [difficulty, setDifficulty] = useState(session?.start_difficulty || 3);
  const [diffHistory, setDiffHistory] = useState([session?.start_difficulty || 3]);
  const [transcript, setTranscript] = useState("");
  const [code, setCode] = useState("");
  const [codeResult, setCodeResult] = useState(null);
  const [isRunningCode, setIsRunningCode] = useState(false);
  const [panel, setPanel] = useState(PANEL.VOICE);
  const [phase, setPhase] = useState("waiting");
  const [timeLeft, setTimeLeft] = useState((session?.duration_minutes || 20) * 60);
  const [connected, setConnected] = useState(false);
  const [showStartScreen, setShowStartScreen] = useState(true);
  const [startStep, setStartStep] = useState(0);
  const timerRef = useRef(null);
  const feedbackRef = useRef(null);

  const { send } = useInterviewWS(sessionId, {
    onOpen: () => {
      setConnected(true);
      setPhase("starting");
      setStartStep(1);
      send("start", { candidate_id: candidate?.id });
    },
    onClose: () => setConnected(false),
    onQuestion: (payload) => {
      setQuestion(payload);
      setFeedback(null);
      setHint(null);
      setTranscript("");
      setCode(payload.code_template || "#include <stdio.h>\n\nint main() {\n    // Your solution here\n    return 0;\n}\n");
      setPhase("question");
      setStartStep(3);
      setQuestionIndex((i) => i + 1);
      setTimeout(() => setShowStartScreen(false), 700);
    },
    onFeedback: (payload) => {
      setFeedback(payload);
      setPhase("question");
      feedbackRef.current?.scrollIntoView({ behavior: "smooth" });
    },
    onDifficulty: ({ new_difficulty }) => {
      setDifficulty(new_difficulty);
      setDiffHistory((h) => [...h, new_difficulty]);
    },
    onHint: (payload) => setHint(payload),
    onCodeResult: (payload) => setCodeResult(payload),
    onEnd: (payload) => {
      setPhase("done");
      clearInterval(timerRef.current);
      if (payload?.report_id) {
        setSession((s) => ({ ...s, report_id: payload.report_id }));
      }
      setTimeout(() => navigate("report"), 2000);
    },
    onError: (err) => console.error("[Interview error]", err),
  });

  useEffect(() => {
    timerRef.current = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(timerRef.current);
          send("end_session", {});
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, []);

  useEffect(() => {
    if (connected && showStartScreen) setStartStep(2);
  }, [connected, showStartScreen]);

  const { isRecording, isPreparing, audioLevel, durationLabel, startRecording, stopRecording } =
    useVoiceRecorder({
      sessionId,
      onTranscript: (text) => {
        setTranscript((prev) => (prev ? `${prev} ${text}` : text));
        setPhase("evaluating");
        send("voice_answer", { transcript: text, question_id: question?.id });
      },
    });

  const handleRunCode = async () => {
    if (!code.trim()) return;
    setIsRunningCode(true);
    try {
      const result = await api.runCode(code, sessionId);
      setCodeResult(result);
      send("code_submission", {
        code,
        question_id: question?.id,
        stdout: result.stdout,
        stderr: result.stderr,
        passed: result.passed,
      });
    } catch (e) {
      setCodeResult({ error: e.message });
    } finally {
      setIsRunningCode(false);
    }
  };

  const formatTime = (s) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${String(sec).padStart(2, "0")}`;
  };

  const progress = Math.min(100, (questionIndex / totalQuestions) * 100);
  const timeWarning = timeLeft < 120;

  if (phase === "done") {
    return (
      <div className="interview-page page completion-screen">
        <div className="completion-card">
          <div className="completion-check">✓</div>
          <h2 style={{ fontFamily: "Syne", marginBottom: 8 }}>Interview Complete!</h2>
          <p className="completion-copy">Generating your report...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="interview-page page">
      {showStartScreen && (
        <div className="startup-overlay" aria-live="polite">
          <div className="startup-card">
            <div className="startup-logo brand-animate">PrepAIred | Interview Preparation Platform</div>
            <div className="startup-spinner" />
            <h3>Setting up your interview</h3>
            <p>
              {!connected
                ? "Connecting to your interview session..."
                : question
                  ? "First question is ready. Starting now..."
                  : "Preparing your first adaptive question..."}
            </p>
            <div className="startup-steps">
              <span className={`step-dot ${startStep >= 1 ? "active" : ""}`}>Connect</span>
              <span className={`step-dot ${startStep >= 2 ? "active" : ""}`}>Initialize</span>
              <span className={`step-dot ${startStep >= 3 ? "active" : ""}`}>Start</span>
            </div>
          </div>
        </div>
      )}

      {phase === "evaluating" && (
        <div className="evaluating-overlay" aria-live="polite">
          <div className="evaluating-card">
            <div className="evaluating-bars">
              <span />
              <span />
              <span />
            </div>
            <h4>Evaluating your answer</h4>
            <p>Checking technical depth, clarity, and correctness...</p>
          </div>
        </div>
      )}

      <div className="interview-topbar">
        <span className="topbar-logo brand-animate" style={{ fontSize: 16 }}>PrepAIred | Interview Preparation Platform</span>

        <div className="interview-progress-wrap">
          <div className="progress-bar" style={{ width: 200 }}>
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <span style={{ fontSize: 12, color: "var(--text-2)" }}>
            {questionIndex} / {totalQuestions}
          </span>
        </div>

        <div className="interview-topbar-right">
          <div className={`timer-pill ${timeWarning ? "warning" : ""}`}>
            <span className="timer-dot" />
            {formatTime(timeLeft)}
          </div>

          <div className={`conn-indicator ${connected ? "online" : "offline"}`}>
            {connected ? "Connected" : "Reconnecting..."}
          </div>
        </div>
      </div>

      <div className="interview-layout">
        <div className="interview-left">
          <InterviewerAvatar
            question={question}
            questionIndex={questionIndex}
            isThinking={phase === "evaluating"}
          />

          <div className="card question-card">
            {question ? (
              <>
                <div className="question-meta">
                  <span className="badge badge-accent">Q{questionIndex}</span>
                  <span className="badge badge-neutral">{question.topic}</span>
                  <span className="badge" style={{
                    background: difficulty <= 2 ? "rgba(54,217,143,0.14)" : difficulty === 3 ? "rgba(255,184,79,0.14)" : "rgba(255,79,106,0.14)",
                    color: difficulty <= 2 ? "var(--success)" : difficulty === 3 ? "var(--warn)" : "var(--danger)"
                  }}>
                    Level {difficulty}
                  </span>
                </div>

                <div className="question-text">{question.text}</div>

                <div className="question-actions">
                  <button className="btn btn-ghost btn-sm" onClick={() => send("request_hint", { question_id: question?.id })}>
                    Hint
                  </button>
                  <button className="btn btn-ghost btn-sm" onClick={() => send("skip_question", { question_id: question?.id })}>
                    Skip
                  </button>
                </div>

                {hint && (
                  <div className="hint-banner">
                    <span>{hint.text}</span>
                  </div>
                )}
              </>
            ) : (
              <div className="waiting-state">
                <div className="waiting-spinner" />
                <p>{connected ? "Loading question..." : "Connecting to interview server..."}</p>
              </div>
            )}
          </div>

          {feedback && (
            <div className="card feedback-card fade-up" ref={feedbackRef}>
              <div className="feedback-header">
                <h4>AI Feedback</h4>
                <div style={{ display: "flex", gap: 8 }}>
                  <span className="badge badge-success">Score: {Math.round((feedback.final_score || 0) * 100)}%</span>
                </div>
              </div>

              {feedback.justification && <p className="feedback-text">{feedback.justification}</p>}
            </div>
          )}
        </div>

        <div className="interview-right">
          <div className="panel-toggle">
            <div className="pill-tabs">
              <button className={`pill-tab ${panel === PANEL.VOICE ? "active" : ""}`} onClick={() => setPanel(PANEL.VOICE)}>
                Voice Answer
              </button>
              <button className={`pill-tab ${panel === PANEL.CODE ? "active" : ""}`} onClick={() => setPanel(PANEL.CODE)}>
                Code Answer
              </button>
            </div>
          </div>

          {panel === PANEL.VOICE && (
            <div className="card voice-panel">
              <div className="voice-status">
                {isRecording ? (
                  <span className="badge badge-danger" style={{ animation: "pulse-ring 1s infinite" }}>
                    Recording {durationLabel}
                  </span>
                ) : phase === "evaluating" ? (
                  <span className="badge badge-warn">Evaluating...</span>
                ) : (
                  <span className="badge badge-neutral">Ready</span>
                )}
              </div>

              <div className="waveform-container">
                <WaveformBar level={audioLevel} isActive={isRecording} />
              </div>

              <div className="voice-controls">
                {!isRecording ? (
                  <button className="btn btn-primary record-btn" onClick={startRecording} disabled={isPreparing || phase === "evaluating"}>
                    {isPreparing ? <span className="spinner" /> : "Start Recording"}
                  </button>
                ) : (
                  <button className="btn btn-danger record-btn" onClick={stopRecording}>
                    Stop and Submit
                  </button>
                )}
              </div>

              {transcript && (
                <div className="transcript-box">
                  <p style={{ fontSize: 13, color: "var(--text-2)", lineHeight: 1.6 }}>{transcript}</p>
                </div>
              )}
            </div>
          )}

          {panel === PANEL.CODE && (
            <div className="card code-panel">
              <div className="code-panel-header">
                <span style={{ fontSize: 12, color: "var(--text-3)", fontFamily: "Syne" }}>C Language - GCC Sandbox</span>
                <button className="btn btn-primary btn-sm" onClick={handleRunCode} disabled={isRunningCode}>
                  {isRunningCode ? <span className="spinner" style={{ width: 14, height: 14 }} /> : "Run Code"}
                </button>
              </div>

              <div className="editor-wrap">
                <MonacoEditor value={code} onChange={setCode} height="100%" />
              </div>

              {codeResult && (
                <div className={`code-output ${codeResult.error || codeResult.stderr ? "error" : codeResult.passed ? "passed" : "failed"}`}>
                  {codeResult.stdout && <pre className="output-pre">{codeResult.stdout}</pre>}
                  {codeResult.stderr && <pre className="output-pre error-pre">{codeResult.stderr}</pre>}
                </div>
              )}
            </div>
          )}

          <div className="sidebar-stats">
            <div className="card stat-card">
              <DifficultyTracker current={difficulty} history={diffHistory} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
