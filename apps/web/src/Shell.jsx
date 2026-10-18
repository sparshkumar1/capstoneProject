import { useContext } from "react";
import { SessionContext, ThemeContext } from "./contexts";
import { Icon } from "./ui";
import "./shell.css";

const NAV = [
  { id: "dashboard", label: "Dashboard", icon: "home" },
  { id: "topics", label: "Practice", icon: "play" },
  { id: "weakness", label: "Weakness Map", icon: "target" },
  { id: "analytics", label: "Progress", icon: "chart" },
];

function initials(name = "") {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  return ((parts[0]?.[0] || "C") + (parts[1]?.[0] || "")).toUpperCase();
}

function ThemeButton() {
  const { theme, setTheme } = useContext(ThemeContext);
  return (
    <button
      type="button"
      className="icon-btn"
      onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
      aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
      title={theme === "dark" ? "Light theme" : "Dark theme"}
    >
      <Icon name={theme === "dark" ? "sun" : "moon"} size={16} />
    </button>
  );
}

/**
 * Shared authenticated layout: sidebar on desktop, bottom tab bar on small screens.
 * `title`/`subtitle`/`actions` render the page header.
 */
export default function Shell({ page, navigate, title, subtitle, actions, children }) {
  const { candidate, signOut } = useContext(SessionContext);
  const items = candidate?.is_admin ? [...NAV, { id: "admin", label: "Admin", icon: "user" }] : NAV;

  return (
    <div className="shell page">
      <nav className="side-nav" aria-label="Main navigation">
        <div className="side-brand brand-identity">
          <span className="brand-mark" aria-hidden="true"><span className="brand-mark-core" /></span>
          <span className="brand-word">Prep<span className="brand-ai">AI</span>red</span>
        </div>
        <div className="nav-label">Workspace</div>
        {items.map((it) => (
          <button
            key={it.id}
            type="button"
            className="nav-item"
            aria-current={page === it.id ? "page" : undefined}
            onClick={() => navigate(it.id)}
          >
            <Icon name={it.icon} size={18} />
            <span>{it.label}</span>
          </button>
        ))}
        <div className="nav-spacer" />
        <div className="side-user">
          <span className="avatar" aria-hidden="true">{initials(candidate?.name)}</span>
          <div className="side-user-meta">
            <div className="side-user-name">{candidate?.name?.trim() || "Candidate"}</div>
            <div className="side-user-sub">{candidate?.email || candidate?.college || ""}</div>
          </div>
          <ThemeButton />
          <button type="button" className="icon-btn" onClick={signOut} aria-label="Sign out" title="Sign out">
            <Icon name="logout" size={16} />
          </button>
        </div>
      </nav>

      <div className="shell-main">
        <div className="mobile-top">
          <span className="brand-identity">
            <span className="brand-mark" aria-hidden="true"><span className="brand-mark-core" /></span>
            <span className="brand-word">Prep<span className="brand-ai">AI</span>red</span>
          </span>
          <span className="row">
            <ThemeButton />
            <button type="button" className="icon-btn" onClick={signOut} aria-label="Sign out"><Icon name="logout" size={16} /></button>
          </span>
        </div>
        <header className="shell-header">
          <div>
            <h1>{title}</h1>
            {subtitle && <p className="sub">{subtitle}</p>}
          </div>
          {actions && <div className="shell-actions">{actions}</div>}
        </header>
        <main className="shell-content">{children}</main>
      </div>
    </div>
  );
}
