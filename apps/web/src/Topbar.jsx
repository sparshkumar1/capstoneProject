import ThemeToggle from "./ThemeToggle";
import { useContext } from "react";
import { SessionContext } from "./contexts";

export default function Topbar({ navigate, showNav = true }) {
  const { candidate } = useContext(SessionContext);

  return (
    <header className="topbar">
      <span className="brand-identity brand-animate">
        <span className="brand-mark" aria-hidden="true">
          <span className="brand-mark-core" />
        </span>
        <span className="topbar-logo">
          <span className="brand-word">Prep<span className="brand-ai">AI</span>red</span>
          <span className="brand-tag"> | Interview Preparation Platform</span>
        </span>
      </span>
      {showNav && (
        <nav style={{ marginLeft: 40, display: "flex", gap: 8 }}>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => navigate("demo")}>Demo</button>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => navigate("topics")}>Topics</button>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => navigate("admin")}>Admin</button>
        </nav>
      )}
      <div className="topbar-right">
        {candidate && (
          <span style={{ fontSize: 13, color: "var(--text-2)", display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{
              width: 28, height: 28, borderRadius: "50%",
              background: "linear-gradient(135deg, var(--accent), var(--accent-2))",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 11, fontWeight: 700, color: "#fff", fontFamily: "Syne"
            }}>
              {candidate.name?.[0]?.toUpperCase() || "C"}
            </span>
            {candidate.name}
          </span>
        )}
        <ThemeToggle />
      </div>
    </header>
  );
}
