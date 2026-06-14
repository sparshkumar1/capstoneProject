import { useMemo, useState } from "react";
import Topbar from "./Topbar";
import "./Demo.css";

const STEPS = [
  {
    key: "question",
    title: "Question",
    badge: "Warm-up",
    copy: "PrepAIred starts with a focused question, then adapts the next turn based on how the answer lands.",
    main: "Explain how to detect a cycle in a linked list using the fast-slow pointer technique.",
    sub: "The demo uses the same interaction pattern as the full interview loop, just with a smaller, safer story.",
    accent: "var(--accent)",
  },
  {
    key: "answer",
    title: "Candidate answer",
    badge: "Observed response",
    copy: "The evaluator combines semantic, structural, and rubric-aware signals before deciding the next action.",
    main: "Use two pointers: move one step for slow and two steps for fast. If they ever meet, a cycle exists. If fast reaches null, there is no cycle.",
    sub: "This answer is concise, correct, and covers the core mechanism without over-explaining implementation details.",
    accent: "var(--accent-2)",
  },
  {
    key: "feedback",
    title: "Feedback",
    badge: "Adaptive output",
    copy: "The UI surfaces strengths, gaps, and a concrete next step so the learner knows what to improve immediately.",
    main: "Strengths: identifies the fast-slow invariant. Missing: mention cycle entry and edge cases. Next action: harder follow-up on linked-list manipulation.",
    sub: "That makes the loop feel like a real coaching session rather than a static quiz.",
    accent: "var(--success)",
  },
];

const SIGNALS = [
  { label: "Semantic coverage", value: 86, tone: "var(--accent)" },
  { label: "Structural coverage", value: 74, tone: "var(--accent-2)" },
  { label: "Confidence", value: 82, tone: "var(--success)" },
];

export default function Demo({ navigate }) {
  const [stepIndex, setStepIndex] = useState(0);
  const [difficulty, setDifficulty] = useState(3);

  const step = STEPS[stepIndex];
  const action = useMemo(() => {
    if (difficulty <= 2) return "Easier";
    if (difficulty === 3) return "Same";
    return "Harder";
  }, [difficulty]);

  return (
    <div className="demo-page page">
      <Topbar navigate={navigate} />

      <div className="demo-shell">
        <section className="demo-hero card fade-up">
          <div>
            <div className="badge badge-accent" style={{ marginBottom: 14 }}>Interactive demo</div>
            <h1>See the interview loop before you start.</h1>
            <p>
              This walkthrough shows how a question, answer, evaluator, and RL policy fit together in one adaptive cycle.
            </p>
          </div>
          <div className="demo-chip-row">
            {STEPS.map((item, index) => (
              <button
                key={item.key}
                type="button"
                className={`demo-chip ${index === stepIndex ? "active" : ""}`}
                onClick={() => setStepIndex(index)}
              >
                {index + 1}. {item.title}
              </button>
            ))}
          </div>
        </section>

        <div className="demo-grid">
          <div className="demo-stage card fade-up stagger-1">
            <div className="demo-stage-top">
              <div>
                <div className="badge badge-neutral">{step.badge}</div>
                <h2>{step.title}</h2>
              </div>
              <button type="button" className="btn btn-ghost btn-sm" onClick={() => setStepIndex((i) => (i + 1) % STEPS.length)}>
                Next step
              </button>
            </div>

            <div className="demo-question" style={{ borderColor: step.accent, boxShadow: `0 0 0 1px ${step.accent}22` }}>
              {step.main}
            </div>
            <p className="demo-copy">{step.copy}</p>
            <p className="demo-subcopy">{step.sub}</p>

            <div className="demo-action-row">
              <span className="badge badge-neutral">Suggested action: {action}</span>
              <span className="badge badge-neutral">Mode: demo interview</span>
              <span className="badge badge-neutral">State-aware feedback</span>
            </div>
          </div>

          <aside className="demo-aside fade-up stagger-2">
            <div className="card demo-metric-card">
              <h3>Live signals</h3>
              <div className="demo-signals">
                {SIGNALS.map((signal) => (
                  <SignalRow key={signal.label} signal={signal} />
                ))}
              </div>
            </div>

            <div className="card demo-metric-card">
              <h3>Difficulty control</h3>
              <p className="demo-copy" style={{ marginBottom: 18 }}>
                The policy can ask for a slightly easier, same-level, or harder follow-up depending on the current signal.
              </p>
              <input
                type="range"
                min="1"
                max="5"
                value={difficulty}
                onChange={(event) => setDifficulty(Number(event.target.value))}
                className="demo-slider"
              />
              <div className="demo-action-row" style={{ marginTop: 14 }}>
                <span className="badge badge-neutral">Current level: {difficulty}</span>
                <span className="badge badge-accent">Policy output: {action}</span>
              </div>
            </div>

            <div className="card demo-metric-card demo-cta-card">
              <h3>Ready to try the real flow?</h3>
              <p className="demo-copy">
                Move into topic selection when you want the actual adaptive interview session.
              </p>
              <div className="demo-actions">
                <button type="button" className="btn btn-primary" onClick={() => navigate("topics")}>
                  Start interview setup
                </button>
                <button type="button" className="btn btn-ghost" onClick={() => navigate("login")}>
                  Back to home
                </button>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

function SignalRow({ signal }) {
  return (
    <div className="demo-signal-row">
      <div className="demo-signal-label">{signal.label}</div>
      <div className="demo-signal-track" aria-hidden="true">
        <span style={{ width: `${signal.value}%`, background: signal.tone }} />
      </div>
      <div className="demo-signal-value" style={{ color: signal.tone }}>{signal.value}%</div>
    </div>
  );
}