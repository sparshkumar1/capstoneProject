import { render, screen, act } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import {
  isFollowupPayload,
  primaryIndexFromPayload,
  questionProgressLabel,
} from "../questionProgress";
import InterviewerAvatar from "../InterviewerAvatar";
import InterviewRoom from "../InterviewRoom";
import { SessionContext } from "../contexts";

// Capture the websocket handlers InterviewRoom registers so tests can push backend payloads into it.
const ws = vi.hoisted(() => ({ handlers: null }));
vi.mock("../useInterviewWS", () => ({
  useInterviewWS: (_id, handlers) => {
    ws.handlers = handlers;
    return { send: vi.fn() };
  },
}));
vi.mock("../useVoiceRecorder", () => ({
  useVoiceRecorder: () => ({
    isRecording: false, isPreparing: false, audioLevel: 0, durationLabel: "0:00", micError: "",
    startRecording: vi.fn(), stopRecording: vi.fn(),
  }),
}));
vi.mock("../MonacoEditor", () => ({ default: () => null }));
vi.mock("../api", () => ({ api: {} }));

// Payload shapes exactly as produced by InterviewOrchestrator._decorate_question_payload
const primary = (n, turn) => ({ id: `q${n}`, text: `Primary question ${n}`, topic: "pointers", difficulty: 3,
  type: "verbal", turn_index: turn, total_questions: 15, is_followup: false, primary_question_index: n,
  parent_question_index: null });
const followup = (n, turn) => ({ id: `fu_${turn}`, text: `Follow-up probing question ${n}`, topic: "pointers",
  difficulty: 3, type: "verbal", source: "qwen_followup", parent_question_id: `q${n}`, turn_index: turn,
  total_questions: 15, is_followup: true, primary_question_index: n, parent_question_index: n });

describe("primary-question progress vs follow-ups", () => {
  it("helpers: follow-up keeps its parent's primary index and is never numbered as a new question", () => {
    expect(isFollowupPayload(followup(1, 2))).toBe(true);
    expect(isFollowupPayload(primary(2, 3))).toBe(false);
    expect(primaryIndexFromPayload(primary(2, 3), 1)).toBe(2);       // turn_index (3) is NOT used
    expect(primaryIndexFromPayload(followup(1, 2), 1)).toBe(1);
    // legacy payload without the new fields: follow-up must not advance the primary index
    expect(primaryIndexFromPayload({ source: "qwen_followup", turn_index: 3 }, 2)).toBe(2);
    expect(primaryIndexFromPayload({ turn_index: 4 }, 3)).toBe(4);
    expect(questionProgressLabel({ isFollowup: false, questionIndex: 1, totalQuestions: 15 })).toBe("Question 1 of 15");
    expect(questionProgressLabel({ isFollowup: true, questionIndex: 1, totalQuestions: 15 })).toBe("Follow-up to Question 1");
  });

  it("InterviewerAvatar: a follow-up is labelled 'Follow-up to Question N', never 'QN of 15'", () => {
    const { rerender } = render(<InterviewerAvatar question={primary(1, 1)} questionIndex={1} totalQuestions={15} />);
    expect(screen.getByText("Q1 of 15")).toBeInTheDocument();
    rerender(<InterviewerAvatar question={followup(1, 2)} questionIndex={1} totalQuestions={15} isFollowup={true} />);
    expect(screen.getByText("Follow-up to Q1")).toBeInTheDocument();
    expect(screen.queryByText(/Q\d+ of 15/)).not.toBeInTheDocument();
    rerender(<InterviewerAvatar question={primary(2, 3)} questionIndex={2} totalQuestions={15} />);
    expect(screen.getByText("Q2 of 15")).toBeInTheDocument();
  });

  it("InterviewRoom: Q1 -> follow-up to Q1 -> Q2 shows 'Question 1 of 15', 'Follow-up to Question 1', 'Question 2 of 15'", () => {
    render(
      <SessionContext.Provider value={{ session: { id: "s1", num_questions: 15, duration_minutes: 30 },
        candidate: { id: "c" }, setSession: vi.fn(), setCandidate: vi.fn() }}>
        <InterviewRoom navigate={vi.fn()} />
      </SessionContext.Provider>
    );
    const topbar = () => document.querySelector(".interview-progress-wrap").textContent;

    act(() => ws.handlers.onQuestion(primary(1, 1)));
    expect(topbar()).toContain("Question 1 of 15");

    act(() => ws.handlers.onQuestion(followup(1, 2)));         // turn_index 2, but it is NOT Question 2
    expect(topbar()).toContain("Follow-up to Question 1");
    expect(topbar()).not.toMatch(/Question \d+ of 15/);

    act(() => ws.handlers.onQuestion(primary(2, 3)));          // turn_index 3, primary Question 2
    expect(topbar()).toContain("Question 2 of 15");
    expect(topbar()).not.toContain("Follow-up");

    // long session: 16th delivered turn (a follow-up to Question 15) never reads "Question 16 of 15"
    act(() => ws.handlers.onQuestion(primary(15, 15)));
    expect(topbar()).toContain("Question 15 of 15");
    act(() => ws.handlers.onQuestion(followup(15, 16)));
    expect(topbar()).toContain("Follow-up to Question 15");
    expect(document.body.textContent).not.toMatch(/Question 16/);
  });
});
