// Interview progress numbering. `num_questions` is the PRIMARY-question budget: a follow-up is a continuation of a
// primary question and must never be displayed as an additional "Question N of M".
//
// Backend question payloads carry: turn_index (delivered-turn position, follow-ups included; legacy),
// total_questions (primary budget), is_followup, primary_question_index (primary questions only), and
// parent_question_index (set for follow-ups: the primary question they continue).

export function isFollowupPayload(payload) {
  return payload?.is_followup === true || payload?.source === "qwen_followup";
}

// Primary-question index to display. Older payloads without primary_question_index fall back to turn_index for
// primary questions and keep the previous primary index for follow-ups (never turn_index, which counts follow-ups).
export function primaryIndexFromPayload(payload, previousIndex = 1) {
  if (Number.isInteger(payload?.primary_question_index) && payload.primary_question_index > 0) {
    return payload.primary_question_index;
  }
  if (isFollowupPayload(payload)) {
    return Number.isInteger(payload?.parent_question_index) && payload.parent_question_index > 0
      ? payload.parent_question_index
      : previousIndex;
  }
  return Number.isInteger(payload?.turn_index) && payload.turn_index > 0 ? payload.turn_index : previousIndex;
}

export function questionProgressLabel({ isFollowup = false, questionIndex = 1, totalQuestions = 0 } = {}, short = false) {
  if (isFollowup) {
    return short ? `Follow-up to Q${questionIndex}` : `Follow-up to Question ${questionIndex}`;
  }
  const total = totalQuestions ? ` of ${totalQuestions}` : "";
  return short ? `Q${questionIndex}${total}` : `Question ${questionIndex}${total}`;
}
