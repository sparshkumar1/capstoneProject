import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import Report from "../Report";
import AdminDashboard from "../AdminDashboard";
import MonacoEditor from "../MonacoEditor";
import { ThemeContext, SessionContext } from "../contexts";
import { api } from "../api";

vi.mock("../api", () => ({
  api: {
    getReport: vi.fn(),
    getAllSessions: vi.fn(),
    getAdminStats: vi.fn(),
    login: vi.fn(),
    createSession: vi.fn(),
    getSession: vi.fn(),
    endSession: vi.fn(),
    getQuestions: vi.fn(),
    getSessionDetail: vi.fn(),
    runCode: vi.fn(),
    transcribe: vi.fn(),
  },
}));

function renderReport({ session = { id: "test-sess", report_id: "test-rep" }, candidate = { name: "Alex" }, navigate = vi.fn() } = {}) {
  return render(
    <ThemeContext.Provider value={{ theme: "dark", setTheme: vi.fn() }}>
      <SessionContext.Provider value={{ session, candidate, setSession: vi.fn(), setCandidate: vi.fn() }}>
        <Report navigate={navigate} />
      </SessionContext.Provider>
    </ThemeContext.Provider>
  );
}

function renderAdmin({ navigate = vi.fn() } = {}) {
  return render(
    <ThemeContext.Provider value={{ theme: "dark", setTheme: vi.fn() }}>
      <SessionContext.Provider value={{ session: null, candidate: null, setSession: vi.fn(), setCandidate: vi.fn() }}>
        <AdminDashboard navigate={navigate} />
      </SessionContext.Provider>
    </ThemeContext.Provider>
  );
}

describe("Stage 11.8 UI Fixes Verification", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("Report.jsx displays explicit error state on API failure without mock data", async () => {
    api.getReport.mockRejectedValueOnce(new Error("Network connection error"));

    renderReport();

    await waitFor(() => {
      expect(screen.getByText(/Report Unavailable/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Network connection error/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Retry Loading/i })).toBeInTheDocument();
    expect(screen.queryByText(/Arjun Mehta/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Overall score: 0.73/i)).not.toBeInTheDocument();
  });

  it("Report.jsx displays genuine report data when API succeeds", async () => {
    api.getReport.mockResolvedValueOnce({
      overall_score: 0.92,
      c_score: 0.95,
      dsa_score: 0.89,
      duration_minutes: 25,
      total_questions: 4,
      trend_summary: "improving",
      strengths: ["Clean pointer usage"],
      missing_concepts: [],
      covered_concepts: ["pointers", "heap"],
      question_results: [
        {
          question_text: "What is a pointer?",
          topic: "pointers",
          type: "verbal",
          difficulty: 3,
          score: 0.92,
          grade: "A",
          feedback: "Great answer",
        },
      ],
    });

    renderReport();

    await waitFor(() => {
      expect(screen.getByText(/Your Report/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Clean pointer usage/i)).toBeInTheDocument();
    expect(screen.queryByText(/Report Unavailable/i)).not.toBeInTheDocument();
  });

  it("AdminDashboard.jsx displays error banner on API failure without mock sessions", async () => {
    api.getAllSessions.mockRejectedValueOnce(new Error("Server 500 internal error"));
    api.getAdminStats.mockRejectedValueOnce(new Error("Stats endpoint unavailable"));

    renderAdmin();

    await waitFor(() => {
      expect(screen.getByText(/Server 500 internal error|Failed to load admin session data/i)).toBeInTheDocument();
    });

    // Should NOT show fake candidates
    expect(screen.queryByText("Arjun Mehta")).not.toBeInTheDocument();
    expect(screen.queryByText("Priya Sharma")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Retry/i })).toBeInTheDocument();
  });

  it("MonacoEditor.jsx gracefully activates fallback textarea when Monaco CDN times out", async () => {
    // In test environment, window.monaco is undefined
    vi.useFakeTimers();

    const onChange = vi.fn();
    render(<MonacoEditor value="int main() { return 0; }" onChange={onChange} />);

    // Fast forward past the 2.5s fallback threshold
    act(() => {
      vi.advanceTimersByTime(2600);
    });

    expect(screen.getByText(/Advanced editor unavailable. Basic code editor is active./i)).toBeInTheDocument();
    const textarea = screen.getByRole("textbox");
    expect(textarea).toHaveValue("int main() { return 0; }");

    fireEvent.change(textarea, { target: { value: "int main() { return 42; }" } });
    expect(onChange).toHaveBeenCalledWith("int main() { return 42; }");

    vi.useRealTimers();
  });
});
