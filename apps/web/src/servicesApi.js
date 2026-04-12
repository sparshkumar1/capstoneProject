const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function req(method, path, body) {
  const opts = { method, headers: {} };
  if (body instanceof FormData) {
    opts.body = body;
  } else if (body) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(`${BASE}${path}`, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  login: (data) => req("POST", "/api/login", data),
  createSession: (data) => req("POST", "/api/sessions", data),
  getSession: (id) => req("GET", `/api/sessions/${id}`),
  endSession: (id) => req("POST", `/api/sessions/${id}/end`),
  getReport: (id) => req("GET", `/api/sessions/${id}/report`),
  getQuestions: (topic) => req("GET", `/api/questions?topic=${topic}`),
  getAllSessions: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return req("GET", `/api/admin/sessions${q ? "?" + q : ""}`);
  },
  getAdminStats: () => req("GET", "/api/admin/stats"),
  getSessionDetail: (id) => req("GET", `/api/admin/sessions/${id}`),
  runCode: (code, sessionId) => req("POST", "/api/run_code", { code, session_id: sessionId }),
  transcribe: (formData) => req("POST", "/api/transcribe", formData),
};