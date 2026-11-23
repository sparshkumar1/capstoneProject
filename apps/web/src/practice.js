import { api } from "./api";

/**
 * Create a targeted practice session through the existing /api/sessions endpoint.
 * `topics` are question-bank topic names (e.g. "Arrays"); `focusQuestionIds` pins specific questions at the
 * front of the queue. Difficulty adaptation, follow-ups and the RL controller run exactly as in a normal session.
 */
export async function startPractice({ candidate, topics = [], focusQuestionIds = [], numQuestions = 6, durationMinutes = 15 }) {
  if (!candidate?.id) throw new Error("Sign in to start a practice session.");
  const uniqueTopics = [...new Set(topics.filter(Boolean))];
  return api.createSession({
    candidate_id: candidate.id,
    c_topics: [],
    dsa_topics: uniqueTopics,
    duration_minutes: durationMinutes,
    num_questions: Math.min(Math.max(numQuestions, 3), 10),
    interview_mode: "standard",
    focus_question_ids: focusQuestionIds,
  });
}

/** Repeat the setup of the candidate's most recent session (taken from the dashboard API). */
export async function repeatLastSetup({ candidate, config }) {
  if (!candidate?.id || !config) throw new Error("No previous session setup found.");
  return api.createSession({
    candidate_id: candidate.id,
    c_topics: config.c_topics || [],
    dsa_topics: config.dsa_topics || [],
    duration_minutes: config.duration_minutes || 30,
    num_questions: config.num_questions || 15,
    interview_mode: config.interview_mode || "standard",
  });
}
