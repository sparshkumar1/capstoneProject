import { useState, useContext } from "react";
import { SessionContext } from "./contexts";
import ThemeToggle from "./ThemeToggle";
import { api } from "./servicesApi";
import "./Login.css";

const YEARS = ["1st Year", "2nd Year", "3rd Year", "4th Year", "Postgrad", "Fresher (Working)"];

export default function Login({ navigate }) {
  const { setCandidate } = useContext(SessionContext);
  const [form, setForm] = useState({
    name: "", email: "", college: "", year: "",
    admin: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [tab, setTab] = useState("candidate"); // "candidate" | "admin"

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async () => {
    if (!form.name.trim() || !form.email.trim()) {
      setError("Name and email are required.");
      return;
    }
    setLoading(true); setError("");
    try {
      const candidate = await api.login({
        ...form,
        admin: tab === "admin",
        experience: "intermediate",
      });
      setCandidate(candidate);
      if (tab === "admin") {
        navigate("admin");
      } else {
        navigate("topics");
      }
    } catch (e) {
      const message = (e?.message || "").toLowerCase();
      if (message.includes("failed to fetch") || message.includes("network")) {
        setError("Cannot reach backend API. Start the server on port 8000 and try again.");
      } else {
        setError(e.message || "Login failed. Check backend is running.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page page">
      {/* Ambient orbs */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />

      <div className="login-header">
        <div className="brand-identity brand-animate" style={{ fontSize: 22 }}>
          <span className="brand-mark" aria-hidden="true">
            <span className="brand-mark-core" />
          </span>
          <span className="topbar-logo">
            <span className="brand-word">Prep<span className="brand-ai">AI</span>red</span>
            <span className="brand-tag"> | Interview Preparation Platform</span>
          </span>
        </div>
        <ThemeToggle />
      </div>

      <div className="login-center">
        <div className="login-left fade-up">
          <h1 className="login-headline">
            Ace your<br />
            <span className="gradient-text">technical & DSA</span><br />
            interviews.
          </h1>
          <p className="login-sub">
            AI-powered adaptive interviews with real-time feedback,
            voice analysis, and live code execution. Built for serious candidates.
          </p>
          <div className="login-features">
            {["🎙️ Voice-based answers", "💻 Live coding editor", "🧠 Adaptive difficulty", "📊 Instant reports"].map(f => (
              <div key={f} className="feature-chip">{f}</div>
            ))}
          </div>
          <div className="login-actions">
            <button type="button" className="btn btn-primary" onClick={() => navigate("demo")}>
              View interactive demo
            </button>
            <button type="button" className="btn btn-ghost" onClick={() => navigate("topics")}>
              Skip to interview setup
            </button>
          </div>
        </div>

        <div className="login-right fade-up stagger-2">
          <div className="card login-card">
            <div className="pill-tabs" style={{ marginBottom: 24 }}>
              <button type="button" className={`pill-tab ${tab === "candidate" ? "active" : ""}`} onClick={() => setTab("candidate") }>
                Candidate
              </button>
              <button type="button" className={`pill-tab ${tab === "admin" ? "active" : ""}`} onClick={() => setTab("admin") }>
                Admin
              </button>
            </div>

            <div className="form-grid">
              <div className="form-group" style={{ gridColumn: "span 2" }}>
                <label className="form-label">Full Name *</label>
                <input className="input" placeholder="Arjun Mehta"
                  value={form.name} onChange={e => set("name", e.target.value)} />
              </div>

              <div className="form-group" style={{ gridColumn: "span 2" }}>
                <label className="form-label">Email *</label>
                <input className="input" type="email" placeholder="arjun@college.edu"
                  value={form.email} onChange={e => set("email", e.target.value)} />
              </div>

              {tab === "candidate" && <>
                <div className="form-group" style={{ gridColumn: "span 2" }}>
                  <label className="form-label">College / Institute</label>
                  <input className="input" placeholder="IIT Madras"
                    value={form.college} onChange={e => set("college", e.target.value)} />
                </div>

                <div className="form-group" style={{ gridColumn: "span 2" }}>
                  <label className="form-label">Year of Study</label>
                  <select className="input select" value={form.year} onChange={e => set("year", e.target.value)}>
                    <option value="">Select year</option>
                    {YEARS.map(y => <option key={y}>{y}</option>)}
                  </select>
                </div>
              </>}

              {tab === "admin" && (
                <div className="form-group" style={{ gridColumn: "span 2" }}>
                  <label className="form-label">Admin Password</label>
                  <input className="input" type="password" placeholder="••••••••"
                    value={form.adminPass || ""} onChange={e => set("adminPass", e.target.value)} />
                </div>
              )}
            </div>

            {error && (
              <div className="error-banner">
                <span>⚠️</span> {error}
              </div>
            )}

            <button type="button" className="btn btn-primary btn-lg"
              style={{ width: "100%", marginTop: 20, justifyContent: "center" }}
              onClick={handleSubmit} disabled={loading}
            >
              {loading
                ? <span className="spinner" />
                : tab === "admin" ? "Enter Dashboard →" : "Start Interview Setup →"
              }
            </button>

            <p className="login-disclaimer">
              Your responses are used solely for interview assessment. No data is shared externally.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
