import { useState, useContext, useEffect, useRef } from "react";
import { SessionContext } from "./contexts";
import MonacoEditor from "./MonacoEditor";
import WaveformBar from "./WaveformBar";
import DifficultyTracker from "./DifficultyTracker";
import FeedbackCard from "./FeedbackCard";
import { useInterviewWS } from "./useInterviewWS";
import { useVoiceRecorder } from "./useVoiceRecorder";
import { api } from "./api";
import InterviewerAvatar from "./InterviewerAvatar";
import "./InterviewRoom.css";

const PANEL = { VOICE: "voice", CODE: "code" };

export default function InterviewRoom({ navigate }) {
  const { session, candidate, setSession } = useContext(SessionContext);
  const sessionId = session?.id || "";

  const [question, setQuestion]           = useState(null);
  const [questionIndex, setQuestionIndex] = useState(1);
  const [totalQuestions, setTotalQuestions] = useState(session?.num_questions || 15);
  const [feedback, setFeedback]           = useState(null);
  const [awaitingNext, setAwaitingNext]   = useState(false);
  const [difficulty, setDifficulty]       = useState(session?.start_difficulty || 3);
  const [diffHistory, setDiffHistory]     = useState([session?.start_difficulty || 3]);
  const [transcript, setTranscript]       = useState("");
  const [audioAnalysis, setAudioAnalysis] = useState(null);
  const [code, setCode]                   = useState("");
  const [codeResult, setCodeResult]       = useState(null);
  const [isRunningCode, setIsRunningCode] = useState(false);
  const [panel, setPanel]                 = useState(PANEL.VOICE);
  const [ttsActive, setTtsActive]         = useState(false);
  const ttsUtteranceRef                   = useRef(null);
  const [phase, setPhase]                 = useState("waiting");
  const [baselineDone, setBaselineDone]   = useState(session?.interview_mode !== "demo_rl");
  const [stageHint, setStageHint]         = useState(
    session?.interview_mode === "demo_rl"
      ? "Baseline phase active — RL adaptation starts after 2 baseline questions."
      : ""
  );
  const [timeLeft, setTimeLeft] = useState((session?.duration_minutes || 30) * 60);
  const [connected, setConnected]         = useState(false);
  const [showStartScreen, setShowStartScreen] = useState(true);
  const [startStep, setStartStep]         = useState(0);
  const [followUpQueued, setFollowUpQueued] = useState(false);
  const timerRef      = useRef(null);
  const feedbackRef   = useRef(null);
  const evalTimeoutRef = useRef(null);
  const phaseRef      = useRef("waiting");

  useEffect(() => { phaseRef.current = phase; }, [phase]);

  useEffect(() => {
    return () => { if ('speechSynthesis' in window) window.speechSynthesis.cancel(); };
  }, []);

  const { send } = useInterviewWS(sessionId, {
    onOpen: () => {
      setConnected(true);
      setPhase("starting");
      setStartStep(1);
      send("start", { candidate_id: candidate?.id });
    },
    onClose: () => setConnected(false),
    onQuestion: (payload) => {
      if (evalTimeoutRef.current) { clearTimeout(evalTimeoutRef.current); evalTimeoutRef.current = null; }
      setQuestion(payload);
      setFeedback(null);
      setAwaitingNext(false);
      setTranscript("");
      setAudioAnalysis(null);
      setFollowUpQueued(payload.source === "qwen_followup");
      if (payload.turn_index) {
        setQuestionIndex(payload.turn_index);
      }
      if (payload.total_questions) {
        setTotalQuestions(payload.total_questions);
      }
      setCode(payload.code_template || "#include <stdio.h>\n\nint main() {\n    // Your solution here\n    return 0;\n}\n");
      setPhase("question");
      setStartStep(3);
      setTimeout(() => setShowStartScreen(false), 500);

      // TTS read-aloud
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utt = new SpeechSynthesisUtterance(payload.text);
        utt.rate = 1.0; utt.pitch = 1.0;
        utt.onstart = () => setTtsActive(true);
        utt.onend   = () => setTtsActive(false);
        utt.onerror = () => setTtsActive(false);
        ttsUtteranceRef.current = utt;
        window.speechSynthesis.speak(utt);
      }

      // Flag Qwen follow-up questions
      if (payload.source === "qwen_followup") {
        setFollowUpQueued(true);
        setStageHint("AI generated a follow-up question based on your previous answer.");
      }
    },
    onFeedback: (payload) => {
      if (evalTimeoutRef.current) { clearTimeout(evalTimeoutRef.current); evalTimeoutRef.current = null; }
      setFeedback(payload);
      setAwaitingNext(true);
      setPhase("review");
      setTimeout(() => feedbackRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 120);
    },
    onDifficulty: ({ new_difficulty, action, reason }) => {
      setDifficulty(new_difficulty);
      setDiffHistory(h => [...h, new_difficulty]);
      if (action === "Baseline") {
        setBaselineDone(false);
        if (reason) setStageHint(reason);
      } else if (action === "Baseline->RL") {
        setBaselineDone(true);
        setStageHint(reason || "Baseline complete — RL adaptive mode is now active.");
      } else if (action === "Follow-up" && reason) {
        setStageHint(reason);
      } else if (action && baselineDone) {
        setStageHint(reason || "");
      }
    },
    onCodeResult: (payload) => setCodeResult(payload),
    onEnd: (payload) => {
      setPhase("done");
      clearInterval(timerRef.current);
      if (payload?.report_id) setSession(s => ({ ...s, report_id: payload.report_id }));
      setTimeout(() => navigate("report"), 1500);
    },
    onError: (err) => {
      if (evalTimeoutRef.current) { clearTimeout(evalTimeoutRef.current); evalTimeoutRef.current = null; }
      if (phaseRef.current === "evaluating") {
        setPhase("question");
        setStageHint("Evaluation interrupted. Submit your answer again.");
      }
      console.error("[Interview error]", err);

    },
  });

  // Session timer
  useEffect(() => {
    timerRef.current = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) { clearInterval(timerRef.current); send("end_session", {}); return 0; }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, []);

  useEffect(() => {
    if (connected && showStartScreen) setStartStep(2);
  }, [connected, showStartScreen]);

  useEffect(() => {
    return () => { if (evalTimeoutRef.current) clearTimeout(evalTimeoutRef.current); };
  }, []);

  const { isRecording, isPreparing, audioLevel, durationLabel, micError, startRecording, stopRecording } =
    useVoiceRecorder({
      sessionId,
      onTranscript: (text, _blob, analysis) => {
        setTranscript(prev => prev ? `${prev} ${text}` : text);
        setAudioAnalysis(analysis || null);
        setPhase("evaluating");
        if (evalTimeoutRef.current) clearTimeout(evalTimeoutRef.current);
        evalTimeoutRef.current = setTimeout(() => {
          if (phaseRef.current === "evaluating") {
            setPhase("question");
            setStageHint("Evaluation took too long. You can retry.");
          }
        }, 20000);
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
        tests_passed: result.tests_passed ?? (result.passed ? 1 : 0),
        tests_total:  result.tests_total  ?? 1,
      });
    } catch (e) {
      setCodeResult({ error: e.message });
    } finally {
      setIsRunningCode(false);
    }
  };

  const handleSkip = () => {

    window.speechSynthesis.cancel();
    setTtsActive(false);
    if (evalTimeoutRef.current) { clearTimeout(evalTimeoutRef.current); evalTimeoutRef.current = null; }
    setStageHint("No worries — moving to the next question.");
    send("skip_question", { question_id: question?.id });
    setAwaitingNext(false);
    setPhase("waiting");
  };

  const handleNextQuestion = () => {
    if (!awaitingNext) return;
    setAwaitingNext(false);
    setPhase("waiting");
    setStageHint("");
    send("next_question", { question_id: question?.id });
  };

  const formatTime = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
  const progress     = Math.min(100, (questionIndex / totalQuestions) * 100);
  const timeWarning  = timeLeft < 120;

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

      {/* Startup overlay */}
      {showStartScreen && (
        <div className="startup-overlay" aria-live="polite">
          <div className="startup-card">
            <div className="startup-logo brand-identity brand-animate">
              <span className="brand-mark" aria-hidden="true"><span className="brand-mark-core" /></span>
              <span className="topbar-logo">
                <span className="brand-word">Prep<span className="brand-ai">AI</span>red</span>
                <span className="brand-tag"> | Interview Preparation Platform</span>
              </span>
            </div>
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

      {/* Evaluating overlay */}
      {phase === "evaluating" && (
        <div className="evaluating-overlay" aria-live="polite">
          <div className="evaluating-card">
            <div className="evaluating-bars"><span /><span /><span /></div>
            <h4>Evaluating your answer</h4>
            <p>Checking technical depth, concept coverage, and reasoning quality...</p>
          </div>
        </div>
      )}

      {/* ── Topbar ───────────────────────────────────────────── */}
      <div className="interview-topbar">
        <span className="brand-identity brand-animate" style={{ fontSize: 16 }}>
          <span className="brand-mark" aria-hidden="true"><span className="brand-mark-core" /></span>
          <span className="topbar-logo">
            <span className="brand-word">Prep<span className="brand-ai">AI</span>red</span>
            <span className="brand-tag"> | Adaptive Interview</span>
          </span>
        </span>

        <div className="interview-progress-wrap">
          <div className="progress-bar" style={{ width: 200 }}>
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          <span style={{ fontSize: 12, color: "var(--text-2)" }}>Question {questionIndex} of {totalQuestions}</span>
        </div>

        <div className="interview-topbar-right">
          <div className={`timer-pill ${timeWarning ? "warning" : ""}`}>
            <span className="timer-dot" />
            {formatTime(timeLeft)}
          </div>
          <div className={`conn-indicator ${connected ? "online" : "offline"}`}>
            {connected ? "Connected" : "Reconnecting…"}
          </div>
        </div>
      </div>

      {/* ── Main layout ──────────────────────────────────────── */}
      <div className="interview-layout">

        {/* Left: avatar + question + feedback */}
        <div className="interview-left">
          <InterviewerAvatar
            question={question}
            questionIndex={questionIndex}
            isThinking={phase === "evaluating"}
          />

          {/* Question card */}
          <div className="card question-card">
            {question ? (
              <>
                <div className="question-meta">
                  <span className="badge badge-accent">Q{questionIndex} of {totalQuestions}</span>
                  <span className="badge badge-neutral">{question.topic}</span>

                  {followUpQueued && <span className="badge badge-accent" style={{ background: "rgba(0,229,200,0.14)", color: "var(--accent-2)" }}>Follow-up</span>}
                  {session?.interview_mode === "demo_rl" && !baselineDone && (
                    <span className="badge badge-warn">Baseline</span>
                  )}
                  {session?.interview_mode === "demo_rl" && baselineDone && (
                    <span className="badge badge-success">RL Active</span>
                  )}
                  <span className="badge" style={{
                    background: difficulty <= 2 ? "rgba(54,217,143,0.14)" : difficulty === 3 ? "rgba(255,184,79,0.14)" : "rgba(255,79,106,0.14)",
                    color: difficulty <= 2 ? "var(--success)" : difficulty === 3 ? "var(--warn)" : "var(--danger)"
                  }}>
                    Level {difficulty}
                  </span>
                  {question.type && <span className="badge badge-neutral">{question.type}</span>}
                </div>

                {stageHint && (
                  <div style={{ marginTop: 6, marginBottom: 8, padding: "7px 12px", background: "var(--bg-2)", borderRadius: 8, fontSize: 12, color: "var(--text-2)", borderLeft: "3px solid var(--accent)" }}>
                    {stageHint}
                  </div>
                )}

                <div className="question-text">{question.text}</div>

                {question.code_snippet && (
                  <pre className="code-snippet"><code>{question.code_snippet}</code></pre>
                )}
                {question.constraints && (
                  <div className="constraints-box">
                    <span style={{ fontWeight: 600, fontSize: 12, color: "var(--text-2)" }}>Constraints: </span>
                    {question.constraints}
                  </div>
                )}

                {!ttsActive && phase !== "evaluating" && (
                  <div className="question-actions">
                    <button className="btn btn-ghost btn-sm" onClick={handleSkip}>⏭ Skip Question</button>
                  </div>
                )}
                {ttsActive && (
                  <div className="question-actions" style={{ opacity: 0.6 }}>
                    <p style={{ fontSize: 12, color: "var(--text-3)" }}>🔊 Reading question aloud...</p>
                  </div>
                )}

              </>
            ) : (
              <div className="waiting-state">
                <div className="waiting-spinner" />
                <p>{connected ? "Loading question…" : "Connecting to interview server…"}</p>
              </div>
            )}
          </div>

          {/* Rich Feedback Card */}
          <div ref={feedbackRef}>
            {feedback && (
              <FeedbackCard
                feedback={feedback}
                onNext={handleNextQuestion}
                awaitingNext={awaitingNext}
              />
            )}
          </div>
        </div>

        {/* Right: answer panel + stats sidebar */}
        <div className="interview-right">
          {/* Panel toggle */}
          <div className="panel-toggle">
            <div className="pill-tabs">
              <button className={`pill-tab ${panel === PANEL.VOICE ? "active" : ""}`}
                onClick={() => setPanel(PANEL.VOICE)}>
                🎙️ Voice Answer
              </button>
              <button className={`pill-tab ${panel === PANEL.CODE ? "active" : ""}`}
                onClick={() => setPanel(PANEL.CODE)}>
                💻 Code Answer
              </button>
            </div>
          </div>

          {/* Voice panel */}
          {panel === PANEL.VOICE && (
            <div className="card voice-panel">
              <div className="voice-status">
                {isRecording ? (
                  <span className="badge badge-danger" style={{ animation: "pulse-ring 1s infinite" }}>
                    ● Recording {durationLabel}
                  </span>
                ) : phase === "evaluating" ? (
                  <span className="badge badge-warn">Evaluating…</span>
                ) : (
                  <span className="badge badge-neutral">Ready</span>
                )}
              </div>

              <div className="waveform-container">
                <WaveformBar level={audioLevel} isActive={isRecording} />
              </div>

              <div className="voice-controls">
                {!isRecording ? (
                  <button className="btn btn-primary record-btn"
                    onClick={startRecording}
                    disabled={isPreparing || phase === "evaluating" || !question}>
                    {isPreparing ? <span className="spinner" /> : "🎙️"} Start Recording
                  </button>
                ) : (
                  <button className="btn btn-danger record-btn" onClick={stopRecording}>
                    ⏹ Stop & Submit
                  </button>
                )}
              </div>

              {micError && (
                <div style={{
                  marginTop: 10,
                  padding: "10px 12px",
                  borderRadius: 10,
                  background: "rgba(255,79,106,0.12)",
                  border: "1px solid rgba(255,79,106,0.35)",
                  color: "var(--danger)",
                  fontSize: 12,
                  lineHeight: 1.45,
                }}>
                  {micError}
                </div>
              )}

              {transcript && (
                <div className="transcript-box">
                  <div style={{ fontSize: 11, color: "var(--text-3)", marginBottom: 6, fontFamily: "Syne", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                    Live Transcript
                  </div>
                  <p style={{ fontSize: 13, color: "var(--text-2)", lineHeight: 1.6 }}>
                    {transcript}
                    {isRecording && <span style={{ animation: "blink 1s infinite" }}>▌</span>}
                  </p>
                </div>
              )}

              {/* Audio confidence mini-panel */}
              {audioAnalysis && !audioAnalysis.error && (
                <div className="transcript-box" style={{ marginBottom: 0 }}>
                  <div style={{ fontSize: 11, color: "var(--text-3)", marginBottom: 8, fontFamily: "Syne", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                    Voice Analysis
                  </div>
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 8 }}>
                    <span className="badge badge-accent">
                      Confidence: {Math.round((audioAnalysis.confidence_score || 0) * 100)}%
                    </span>
                    <span className="badge badge-neutral">{audioAnalysis.label || "—"}</span>
                  </div>
                  <div style={{ fontSize: 12, color: "var(--text-2)", display: "flex", flexDirection: "column", gap: 3 }}>
                    <span>Speaking rate: {audioAnalysis?.transcription?.true_speaking_rate ?? 0} WPM</span>
                    <span>Pauses: {audioAnalysis?.transcription?.pause_count ?? 0}</span>
                    {audioAnalysis?.linguistic?.filler_count > 0 && (
                      <span style={{ color: "var(--warn)" }}>
                        Fillers detected: {audioAnalysis.linguistic.filler_count}
                      </span>
                    )}
                  </div>
                </div>
              )}

              <p className="voice-tip" style={{ marginTop: 12 }}>
                Speak clearly. Explain reasoning aloud — partial answers earn partial credit.
              </p>
            </div>
          )}

          {/* Code panel */}
          {panel === PANEL.CODE && (
            <div className="card code-panel">
              <div className="code-panel-header">
                <span style={{ fontSize: 12, color: "var(--text-3)", fontFamily: "Syne" }}>
                  C Language — GCC Sandbox
                </span>
                <button className="btn btn-primary btn-sm" onClick={handleRunCode} disabled={isRunningCode}>
                  {isRunningCode ? <span className="spinner" style={{ width: 14, height: 14 }} /> : "▶"} Run Code
                </button>
              </div>

              <div className="editor-wrap">
                <MonacoEditor value={code} onChange={setCode} height="100%" />
              </div>

              {codeResult && (
                <div className={`code-output ${codeResult.error || codeResult.stderr ? "error" : codeResult.passed ? "passed" : "failed"}`}>
                  {codeResult.passed !== undefined && (
                    <div className="output-status">
                      {codeResult.passed ? "✅ All test cases passed" : "❌ Some test cases failed"}
                    </div>
                  )}
                  {codeResult.stdout && <pre className="output-pre">{codeResult.stdout}</pre>}
                  {codeResult.stderr && <pre className="output-pre error-pre">{codeResult.stderr}</pre>}
                  {codeResult.error  && <pre className="output-pre error-pre">{codeResult.error}</pre>}
                  {codeResult.execution_time_ms && (
                    <div style={{ fontSize: 11, color: "var(--text-3)", marginTop: 6 }}>
                      ⏱ {codeResult.execution_time_ms}ms
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Sidebar stats */}
          <div className="sidebar-stats">
            <div className="card stat-card">
              <DifficultyTracker current={difficulty} history={diffHistory} />
            </div>

            <div className="card stat-card">
              <div style={{ fontSize: 11, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.05em", fontFamily: "Syne", fontWeight: 600, marginBottom: 10 }}>
                Session Progress
              </div>
              <div className="progress-bar" style={{ marginBottom: 8 }}>
                <div className="progress-fill" style={{ width: `${progress}%` }} />
              </div>
              <div style={{ fontSize: 12, color: "var(--text-2)" }}>
                {questionIndex} of {totalQuestions} questions
              </div>
              {!baselineDone && session?.interview_mode === "demo_rl" && (
                <div style={{ fontSize: 11, color: "var(--warn)", marginTop: 6 }}>
                  Baseline phase — RL activates after Q2
                </div>
              )}
              {baselineDone && session?.interview_mode === "demo_rl" && (
                <div style={{ fontSize: 11, color: "var(--success)", marginTop: 6 }}>
                  RL adaptive mode active
                </div>
              )}
            </div>

            {candidate && (
              <div className="card stat-card">
                <div style={{ fontSize: 11, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.05em", fontFamily: "Syne", fontWeight: 600, marginBottom: 10 }}>
                  Candidate
                </div>
                <div style={{ fontSize: 13, fontWeight: 600 }}>{candidate.name}</div>
                <div style={{ fontSize: 12, color: "var(--text-3)" }}>{candidate.college}</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
