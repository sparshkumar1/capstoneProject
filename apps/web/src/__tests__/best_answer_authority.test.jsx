import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import FeedbackCard from "../FeedbackCard";

// The backend is authoritative for best-answer status. The card renders "New Best Answer" only when the backend
// reports is_best AND an eligible authoritative best answer; "Authoritative Best Answer" only from that
// backend-reported best_answer, never from the current transcript.

const NON_RESPONSIVE = "Um, I think it is blue. I had lunch earlier and the weather is nice.";

function renderCard(feedback) {
  return render(
    <FeedbackCard feedback={feedback} onNext={vi.fn()} awaitingNext={true} onRetry={vi.fn()} />
  );
}

const openBestPanel = () => {
  const btn = screen.queryByRole("button", { name: /View Best Answer ▾/i });
  if (btn) fireEvent.click(btn);
};

describe("Best-answer authority (frontend reflects backend)", () => {
  it("screenshot regression: non-responsive answer, backend reports no eligible best -> no best-answer UI", () => {
    renderCard({
      attempt_number: 2,
      is_best: false,
      authoritative_best_answer: false,
      best_answer: null,
      covered_concepts: [],
      missing_concepts: ["dereference"],
      comparison: { has_previous_best: false, previous_best_answer: null, remaining_concepts: ["dereference"] },
      transcript: NON_RESPONSIVE,
    });
    expect(screen.queryByText(/New Best Answer/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Authoritative Best Answer/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Retry \/ Best-Answer Status/i)).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /View Best Answer/i })).not.toBeInTheDocument();
  });

  it("does not present the current answer as best even if a stale is_best flag arrives without backend best_answer", () => {
    renderCard({
      attempt_number: 2,
      is_best: true,
      // backend did not report an eligible authoritative best answer
      comparison: { has_previous_best: true, previous_best_answer: null, remaining_concepts: [] },
      transcript: NON_RESPONSIVE,
    });
    expect(screen.queryByText(/New Best Answer/i)).not.toBeInTheDocument();
    openBestPanel();
    expect(screen.queryByText(/Authoritative Best Answer/i)).not.toBeInTheDocument();
    expect(document.body.textContent).not.toContain(NON_RESPONSIVE + " Authoritative");
  });

  it("incorrect latest attempt: previous valid best remains and is shown from backend best_answer, not the transcript", () => {
    renderCard({
      attempt_number: 3,
      is_best: false,
      authoritative_best_answer: true,
      best_answer: { attempt_number: 1, answer: "Pointers store memory addresses." },
      comparison: { has_previous_best: true, previous_best_answer: "Pointers store memory addresses.",
                    remaining_concepts: ["null_check"] },
      transcript: NON_RESPONSIVE,
    });
    expect(screen.queryByText(/New Best Answer/i)).not.toBeInTheDocument();
    expect(screen.getByText(/Your Previous Best Answer Remains Best/i)).toBeInTheDocument();
    openBestPanel();
    const panel = document.getElementById("fc-best-answer-panel");
    expect(panel).toBeInTheDocument();
    expect(panel).toHaveTextContent("Pointers store memory addresses.");
    expect(panel).not.toHaveTextContent("blue");
  });

  it("New Best Answer and Authoritative Best Answer appear when the backend says the submitted attempt is the eligible best", () => {
    renderCard({
      attempt_number: 2,
      is_best: true,
      authoritative_best_answer: true,
      best_answer: { attempt_number: 2, answer: "Pointers store addresses; dereference with *." },
      comparison: { has_previous_best: true, previous_best_answer: "Pointers.", resolved_concepts: ["dereference"],
                    remaining_concepts: [] },
      transcript: "Pointers store addresses; dereference with *.",
    });
    expect(screen.getByText(/✓ New Best Answer/i)).toBeInTheDocument();
    openBestPanel();
    expect(screen.getByText(/Authoritative Best Answer/i)).toBeInTheDocument();
    expect(document.getElementById("fc-best-answer-panel")).toHaveTextContent("dereference with *");
  });

  it("is_best=true without a reported authoritative best answer never shows New Best Answer", () => {
    renderCard({
      attempt_number: 2,
      is_best: true,
      authoritative_best_answer: false,
      best_answer: null,
      comparison: { has_previous_best: true, previous_best_answer: "old", remaining_concepts: [] },
      transcript: NON_RESPONSIVE,
    });
    expect(screen.queryByText(/New Best Answer/i)).not.toBeInTheDocument();
  });
});
