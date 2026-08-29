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

  it("generateQualitativeSummary produces dynamic, answer-specific, score-free summaries", async () => {
    const { generateQualitativeSummary } = await import("../FeedbackCard");

    // 1. Strong answer
    const strongFeedback = {
      transcript: "We use a hash table to store elements and complement targets in a single pass.",
      covered_concepts: ["Hash table lookup", "Complement calculation"],
      missing_concepts: [],
      incorrect_or_incomplete: [],
      strong_points: ["Optimal O(n) linear time complexity"],
      justification: "Grade A (95%) on arrays. Semantic 90% | Concept coverage 100% | Reasoning 95% | Confidence 85%.",
    };
    const strongSummary = generateQualitativeSummary(strongFeedback);
    expect(strongSummary).toContain("Hash table lookup");
    expect(strongSummary).toContain("Complement calculation");
    expect(strongSummary).not.toMatch(/Grade\s+[A-F]/i);
    expect(strongSummary).not.toMatch(/\b\d+%\b/);
    expect(strongSummary).not.toMatch(/Semantic/i);

    // 2. Partial answer
    const partialFeedback = {
      transcript: "Hash tables handle collisions using chaining with linked lists.",
      covered_concepts: ["Chaining with linked lists"],
      missing_concepts: ["Open addressing probing"],
      incorrect_or_incomplete: [],
      how_to_improve: ["Discuss linear and quadratic probing techniques."],
      justification: "Grade C (55%) on hashing. Semantic 50% | Concept coverage 50% | Reasoning 50% | Confidence 60%.",
    };
    const partialSummary = generateQualitativeSummary(partialFeedback);
    expect(partialSummary).toContain("Chaining with linked lists");
    expect(partialSummary).toContain("Open addressing probing");
    expect(partialSummary).not.toMatch(/Grade\s+[A-F]/i);
    expect(partialSummary).not.toMatch(/\b\d+%\b/);

    // 3. Incorrect answer with misconception
    const incorrectFeedback = {
      transcript: "Freeing memory destroys the pointer variable automatically.",
      covered_concepts: [],
      missing_concepts: ["Dangling pointer management"],
      incorrect_or_incomplete: [
        {
          what_was_said: "Freeing memory destroys the pointer variable",
          correction: "free() releases heap memory but leaves the pointer variable as a dangling reference",
          severity: "major",
        },
      ],
      justification: "Grade F (20%) on memory. Semantic 20% | Concept coverage 0% | Reasoning 10% | Confidence 40%.",
    };
    const incorrectSummary = generateQualitativeSummary(incorrectFeedback);
    expect(incorrectSummary).toContain("Freeing memory destroys the pointer variable");
    expect(incorrectSummary).toContain("dangling reference");
    expect(incorrectSummary).not.toMatch(/Grade\s+[A-F]/i);
    expect(incorrectSummary).not.toMatch(/\b\d+%\b/);

    // Verify all three summaries are distinct and answer-specific
    expect(strongSummary).not.toEqual(partialSummary);
    expect(partialSummary).not.toEqual(incorrectSummary);
    expect(strongSummary).not.toEqual(incorrectSummary);
  });
});
