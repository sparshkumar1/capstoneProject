import { useState, useEffect, useCallback } from "react";
import Login from "./Login";
import Dashboard from "./Dashboard";
import WeaknessMap from "./WeaknessMap";
import Analytics from "./Analytics";
import TopicSelector from "./TopicSelector";
import InterviewRoom from "./InterviewRoom";
import Report from "./Report";
import AdminDashboard from "./AdminDashboard";
import Demo from "./Demo";
import { ThemeContext, SessionContext } from "./contexts";
import "./App.css";

const CANDIDATE_KEY = "prepaired.candidate";
const PAGES = ["login", "demo", "dashboard", "weakness", "analytics", "topics", "interview", "report", "admin"];

function loadTheme() {
  try {
    return localStorage.getItem("theme") || "dark";
  } catch {
    return "dark";
  }
}

function loadCandidate() {
  try {
    const raw = localStorage.getItem(CANDIDATE_KEY);
    const parsed = raw ? JSON.parse(raw) : null;
    return parsed && parsed.id ? parsed : null;
  } catch {
    return null;
  }
}

export default function App() {
  const [theme, setTheme] = useState(loadTheme);
  const [candidate, setCandidateState] = useState(loadCandidate);
  const [page, setPage] = useState(() => (loadCandidate() ? "dashboard" : "login"));
  const [session, setSession] = useState(null);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem("theme", theme);
    } catch {
      // Ignore storage failures in sandboxed/embedded browsers.
    }
  }, [theme]);

  // Keep the signed-in candidate across reloads so the dashboard is the home screen.
  const setCandidate = useCallback((value) => {
    setCandidateState(value);
    try {
      if (value && value.id) localStorage.setItem(CANDIDATE_KEY, JSON.stringify(value));
      else localStorage.removeItem(CANDIDATE_KEY);
    } catch {
      // Ignore storage failures.
    }
  }, []);

  const signOut = useCallback(() => {
    setCandidate(null);
    setSession(null);
    setPage("login");
  }, [setCandidate]);

  const navigate = (p) => {
    if (!candidate && ["dashboard", "weakness", "analytics"].includes(p)) {
      setPage("login");
      return;
    }
    setPage(p);
    window.scrollTo?.(0, 0);
  };

  const current = PAGES.includes(page) ? page : "login";

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <SessionContext.Provider value={{ session, setSession, candidate, setCandidate, signOut }}>
        <div className="app-root">
          {current === "login" && <Login navigate={navigate} />}
          {current === "demo" && <Demo navigate={navigate} />}
          {current === "dashboard" && <Dashboard navigate={navigate} />}
          {current === "weakness" && <WeaknessMap navigate={navigate} />}
          {current === "analytics" && <Analytics navigate={navigate} />}
          {current === "topics" && <TopicSelector navigate={navigate} />}
          {current === "interview" && <InterviewRoom navigate={navigate} />}
          {current === "report" && <Report navigate={navigate} />}
          {current === "admin" && <AdminDashboard navigate={navigate} />}
        </div>
      </SessionContext.Provider>
    </ThemeContext.Provider>
  );
}
