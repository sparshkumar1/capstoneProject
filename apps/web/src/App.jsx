import { useState, useEffect } from "react";
import Login from "./Login";
import TopicSelector from "./TopicSelector";
import InterviewRoom from "./InterviewRoom";
import Report from "./Report";
import AdminDashboard from "./AdminDashboard";
import Demo from "./Demo";
import { ThemeContext, SessionContext } from "./contexts";
import "./App.css";

function loadTheme() {
  try {
    return localStorage.getItem("theme") || "dark";
  } catch {
    return "dark";
  }
}

export default function App() {
  const [theme, setTheme] = useState(loadTheme);
  const [page, setPage] = useState("login");
  const [session, setSession] = useState(null);
  const [candidate, setCandidate] = useState(null);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem("theme", theme);
    } catch {
      // Ignore storage failures in sandboxed/embedded browsers.
    }
  }, [theme]);

  const navigate = (p) => setPage(p);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <SessionContext.Provider value={{ session, setSession, candidate, setCandidate }}>
        <div className="app-root">
          {page === "login" && <Login navigate={navigate} />}
          {page === "demo" && <Demo navigate={navigate} />}
          {page === "topics" && <TopicSelector navigate={navigate} />}
          {page === "interview" && <InterviewRoom navigate={navigate} />}
          {page === "report" && <Report navigate={navigate} />}
          {page === "admin" && <AdminDashboard navigate={navigate} />}
          {!['login', 'demo', 'topics', 'interview', 'report', 'admin'].includes(page) && <Login navigate={navigate} />}
        </div>
      </SessionContext.Provider>
    </ThemeContext.Provider>
  );
}
