const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const CANDIDATE_STORAGE_KEY = "prepaired.candidate";

function _adminToken() {
  try {
    const raw = localStorage.getItem(CANDIDATE_STORAGE_KEY);
    return raw ? JSON.parse(raw)?.admin_token || "" : "";
  } catch {
    return "";
  }
}

async function req(method, path, body) {
  const opts = { method, headers: {} };
  if (path.startsWith("/api/admin/")) {
    const token = _adminToken();
    if (token) opts.headers["X-Admin-Token"] = token;
  }
  if (body instanceof FormData) {
    opts.body = body;
  } else if (body) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(`${BASE}${path}`, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    let errorMsg = "Request failed";
    if (typeof err.detail === "string") {
      errorMsg = err.detail;
    } else if (Array.isArray(err.detail)) {
      errorMsg = err.detail.map(d => `${d.loc ? d.loc.slice(1).join('.') : ''}: ${d.msg}`).join(', ');
    } else if (err.detail && typeof err.detail === "object") {
      errorMsg = JSON.stringify(err.detail);
    } else if (err.message) {
      errorMsg = err.message;
    }
    throw new Error(`HTTP ${res.status}: ${errorMsg}`);
  }
  return res.json();

}

export const api = {
  // Auth
  login: (data) => req("POST", "/api/login", data),

  // Sessions
  createSession: (data) => req("POST", "/api/sessions", data),
  getSession: (id) => req("GET", `/api/sessions/${id}`),
  endSession: (id) => req("POST", `/api/sessions/${id}/end`),
  getReport: (id) => req("GET", `/api/sessions/${id}/report`),

  // Questions
  getQuestions: (topic) => req("GET", `/api/questions?topic=${topic}`),

  // Learner insights (read-only, derived from stored attempts)
  getDashboard: (candidateId, tz = 0) => req("GET", `/api/candidates/${encodeURIComponent(candidateId)}/dashboard?tz_offset_minutes=${tz}`),
  getAnalytics: (candidateId, tz = 0) => req("GET", `/api/candidates/${encodeURIComponent(candidateId)}/analytics?tz_offset_minutes=${tz}`),
  getWeaknessMap: (candidateId) => req("GET", `/api/candidates/${encodeURIComponent(candidateId)}/weakness-map`),
  compareAttempts: (candidateId, questionId) =>
    req("GET", `/api/candidates/${encodeURIComponent(candidateId)}/compare/${encodeURIComponent(questionId)}`),

  // Bookmarks & notes
  getBookmarks: (candidateId) => req("GET", `/api/candidates/${encodeURIComponent(candidateId)}/bookmarks`),
  addBookmark: (candidateId, questionId, note = "") =>
    req("POST", `/api/candidates/${encodeURIComponent(candidateId)}/bookmarks`, { question_id: questionId, note }),
  removeBookmark: (candidateId, questionId) =>
    req("DELETE", `/api/candidates/${encodeURIComponent(candidateId)}/bookmarks/${encodeURIComponent(questionId)}`),

  // Server-synced study goal
  getStudyGoal: (candidateId) => req("GET", `/api/candidates/${encodeURIComponent(candidateId)}/study-goal`),
  saveStudyGoal: (candidateId, data) => req("PUT", `/api/candidates/${encodeURIComponent(candidateId)}/study-goal`, data),

  // Admin
  getAllSessions: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return req("GET", `/api/admin/sessions${q ? "?" + q : ""}`);
  },
  getAdminStats: () => req("GET", "/api/admin/stats"),
  getSessionDetail: (id) => req("GET", `/api/admin/sessions/${id}`),
  getCandidateSessions: (candidateId) => req("GET", `/api/admin/candidates/${encodeURIComponent(candidateId)}/sessions`),

  // Report PDF export (direct URL -- downloaded via an <a>/window.open, not JSON fetch)
  reportPdfUrl: (sessionId) => `${BASE}/api/sessions/${encodeURIComponent(sessionId)}/report/pdf`,

  // Code execution
  runCode: (code, sessionId) => req("POST", "/api/run_code", { code, session_id: sessionId }),

  // Transcription
  transcribe: (formData) => req("POST", "/api/transcribe", formData),
};
