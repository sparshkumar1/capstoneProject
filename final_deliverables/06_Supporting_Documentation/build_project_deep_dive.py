# -*- coding: utf-8 -*-
"""Builds 'PrepAIred: Project Deep-Dive & Viva Reference' -- a long-form,
plain-language walkthrough of the whole codebase: what each major file does,
real (not reconstructed) code snippets from the live repository with
explanations, the defects found and fixed this phase, and per-component
test/results summaries. Companion to the formal dissertation
(final_deliverables/07_Final_Semester_Report/) and the short Q&A-style
Viva_Preparation_Document.md in this same folder -- this document is the
long explanatory one meant to be read start to end before a review."""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = r"D:\Capstone_29_AUG\capstoneProject\final_deliverables\06_Supporting_Documentation\PrepAIred_Project_Deep_Dive.docx"

NAVY = RGBColor(0x1D, 0x28, 0x63)
TEXT_DARK = RGBColor(0x20, 0x20, 0x20)
GREY = RGBColor(0x5A, 0x5A, 0x5A)
TITLE_FONT = "Arial"
BODY_FONT = "Calibri"
CODE_FONT = "Consolas"

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
for m in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
    setattr(sec, m, Cm(2.2))

style = doc.styles["Normal"]
style.font.name = BODY_FONT
style.font.size = Pt(11)
style.font.color.rgb = TEXT_DARK
style.paragraph_format.space_after = Pt(8)
style.paragraph_format.line_spacing = 1.18


def add_title(text, subtitle=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = TITLE_FONT, Pt(26), True, NAVY
    if subtitle:
        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r2 = p2.add_run(subtitle)
        r2.font.name, r2.font.size, r2.font.color.rgb = BODY_FONT, Pt(13), GREY


def add_heading(text, level=1):
    p = doc.add_heading(level=level)
    r = p.add_run(text)
    r.font.name = TITLE_FONT
    r.font.color.rgb = NAVY
    r.font.bold = True
    r.font.size = Pt({1: 18, 2: 14, 3: 12}.get(level, 11))
    p.paragraph_format.space_before = Pt(14 if level == 1 else 10)
    p.paragraph_format.space_after = Pt(6)
    return p


def add_p(text, bold=False, italic=False, size=11, bullet=False, color=None):
    p = doc.add_paragraph(style="List Bullet" if bullet else None)
    r = p.add_run(text)
    r.font.name = BODY_FONT
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color or TEXT_DARK
    return p


def add_code(lines, caption=None):
    if caption:
        cp = doc.add_paragraph()
        cr = cp.add_run(caption)
        cr.font.name, cr.font.size, cr.font.italic, cr.font.color.rgb = BODY_FONT, Pt(9.5), True, GREY
        cp.paragraph_format.space_after = Pt(2)
    for line in lines.split("\n"):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        stripped = len(line) - len(line.lstrip(" "))
        content = "\u00a0" * stripped + line[stripped:]
        run = p.add_run(content if content.strip() else "\u00a0")
        run.font.name = CODE_FONT
        run.font.size = Pt(9)
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), "F2F2F4")
        pPr.append(shd)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)


def add_table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Light Grid Accent 1"
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        r = p.add_run(h)
        r.font.bold = True
        r.font.size = Pt(9.5)
        r.font.name = BODY_FONT
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            r = p.add_run(str(val))
            r.font.size = Pt(9.5)
            r.font.name = BODY_FONT
    doc.add_paragraph().paragraph_format.space_after = Pt(6)


def page_break():
    doc.add_page_break()


# =====================================================================
# TITLE PAGE
# =====================================================================
add_title(
    "PrepAIred: Project Deep-Dive & Viva Reference",
    "A complete, plain-language walkthrough of the codebase \u2014 what every major file does, "
    "the real code behind each claim, and the test results behind every number.",
)
doc.add_paragraph()
add_p(
    "How to use this document: read it top to bottom before a review. Each major component gets its own "
    "section with (1) what it does in plain language, (2) the exact files involved, (3) a real, unedited "
    "snippet from the live code with a line-by-line explanation, and (4) what was actually tested and what "
    "the results were. Every code snippet here is copied directly from the repository, not reconstructed "
    "from memory \u2014 if you open the file at the path shown, you will see the same lines.",
    italic=True,
)
add_p(
    "Companion documents: the formal dissertation is in final_deliverables/07_Final_Semester_Report/ "
    "(PrepAIred_Phase3_Final_Report.pdf); a shorter question-and-answer style prep sheet is "
    "Viva_Preparation_Document.md in this same folder. This document is the long explanatory one.",
    italic=True,
)
page_break()

# =====================================================================
# SECTION 1 -- WHAT THIS PROJECT DOES
# =====================================================================
add_heading("1. What This Project Does (Plain Language)", 1)
add_p(
    "PrepAIred is a web app that runs a mock technical interview. A candidate answers questions out loud "
    "(spoken) or writes C code, and the system does three things no static question bank (like a plain "
    "LeetCode-style practice list) does: it scores the answer on meaning, not just keywords; it explains "
    "what was missing or wrong in plain language; and it picks the next question's difficulty based on how "
    "the candidate is actually doing \u2014 not a fixed, pre-set sequence."
)
add_p(
    "Three ingredients make that possible, and each one is a separate, inspectable piece of code, not a "
    "single black box:"
)
add_p("A semantic evaluator that reads the meaning of an answer, not just whether it contains the right words.", bullet=True)
add_p("A reinforcement-learning (RL) policy, wrapped in hard safety rules, that decides whether the next question should be easier, the same, or harder.", bullet=True)
add_p("A local language model (Qwen 2.5) that turns the evaluator's raw numbers into a written explanation \u2014 but never changes the score itself.", bullet=True)
add_p(
    "Everything in this document is checked against the actual code as it exists right now in this "
    "repository \u2014 including two real bugs that were found and fixed during this phase, which are "
    "walked through in detail in Section 9, because that is exactly the kind of thing a reviewer tends to "
    "ask about."
)

# =====================================================================
# SECTION 2 -- THE BIG PICTURE: HOW ONE ANSWER TRAVELS THROUGH THE SYSTEM
# =====================================================================
add_heading("2. The Big Picture: How One Answer Travels Through the System", 1)
add_p(
    "Picture a candidate speaking an answer out loud. Here is exactly what happens, in order, before they "
    "see their next question:"
)
steps = [
    ("1. Browser \u2192 Backend", "The React frontend (apps/web/src/InterviewRoom.jsx) sends the answer "
     "over a WebSocket connection to the FastAPI backend (apps/backend/main.py)."),
    ("2. Backend \u2192 Orchestrator", "The backend does almost no thinking of its own \u2014 it immediately "
     "hands the message to InterviewOrchestrator (agents/orchestrator/interview_orchestrator.py), the one "
     "object that owns the entire session's state."),
    ("3. Scoring", "For a spoken answer, the orchestrator calls the semantic evaluator "
     "(services/evaluator/app.py) directly, in-process (not over the network). For C code, it calls the "
     "Docker sandbox instead (agents/coding_executor/coding_executor.py)."),
    ("4. Feedback", "The orchestrator asks FeedbackAgent (agents/orchestrator/feedback_agent.py) to build a "
     "15-field explanation. FeedbackAgent may call the local Qwen 2.5 model for the written parts, but the "
     "numeric score was already fixed in the previous step and is never touched again."),
    ("5. Difficulty decision", "The orchestrator builds a 6-number summary of the candidate's state (score, "
     "rolling average, voice confidence, hesitation, progress through the session, current difficulty), "
     "feeds it to the trained PPO policy, and then \u2014 critically \u2014 passes the policy's suggestion "
     "through six deterministic safety rules (the 'guardrails') that can override it."),
    ("6. Next question", "A rule-based question selector picks the next question at the decided difficulty "
     "level, and the result streams back to the browser."),
]
for title, body in steps:
    p = add_p(f"{title}: ", bold=True)
    p.add_run(body).font.size = Pt(11)
add_p(
    "The important thing to notice: this is one central controller (the orchestrator) calling out to several "
    "specialised, independent components and collecting their answers \u2014 not several components talking "
    "to each other. This is called a single-controller, hub-and-spoke architecture. It is explicitly not a "
    "multi-agent system (there is no second component that makes its own decisions or negotiates with "
    "another one), and this was double-checked by two separate code searches during this phase specifically "
    "because an earlier, separately-supplied document claimed otherwise."
)

page_break()
# =====================================================================
# SECTION 3 -- FILE MAP: WHAT LIVES WHERE
# =====================================================================
add_heading("3. File Map: What Lives Where", 1)
add_p(
    "This is the single most useful table for a review \u2014 if you are asked 'where is X implemented', "
    "find it here first."
)
add_table(
    ["File / Folder", "What it does"],
    [
        ["apps/backend/main.py", "FastAPI server: the WebSocket endpoint, session creation, the /api/run_code "
         "REST endpoint, and the production question-bank loader. Thin on logic \u2014 almost everything it "
         "does is call into the orchestrator."],
        ["agents/orchestrator/interview_orchestrator.py", "The hub. Owns all session state behind an asyncio "
         "lock, routes answers to the evaluator or sandbox, runs the guardrail-and-difficulty pipeline, and "
         "calls FeedbackAgent. ~2,300 lines \u2014 the largest single file in the project."],
        ["agents/orchestrator/feedback_agent.py", "Builds the 15-field feedback object. Computes the score's "
         "breakdown and calls Qwen for narrative text only."],
        ["services/evaluator/app.py", "The semantic evaluator: Sentence-BERT similarity (S1), FAISS concept "
         "coverage (S2), CrossEncoder reasoning quality (R), combined into the final weighted score."],
        ["services/qwen/app.py", "A small FastAPI microservice wrapping the local Qwen 2.5 model, used only "
         "for generating feedback text, hints, and follow-up questions."],
        ["agents/coding_executor/coding_executor.py", "Compiles and runs candidate C code inside a locked-down "
         "Docker container, compares output against stored test cases, and computes the coding score."],
        ["agents/strategy/hybrid_orchestrator.py", "Builds the 6-number RL observation vector from session "
         "state and loads/calls the trained PPO policy."],
        ["rl/env/interview_env.py", "The Gymnasium training environment used to train the PPO policy "
         "(simulation only \u2014 not used at inference time in the live app)."],
        ["rl/guardrails.py", "The canonical, documented version of the six safety rules that can override the "
         "PPO policy's decision. Used by training/simulation and by this phase's own boundary tests."],
        ["agents/question_selector/question_selector.py", "A separate, research-only question-selection module "
         "(contains randomness). Not what the live app actually uses \u2014 see Section 8."],
        ["agents/audio/", "Whisper/faster-whisper speech-to-text, plus prosody (pitch/pace) and "
         "confidence/hesitation feature extraction from the candidate's voice."],
        ["services/storage/database.py", "SQLite persistence (data/prepaired.db): sessions, attempts, scores, "
         "history."],
        ["data/questions/qns.json", "The question bank: every interview question's text, difficulty, topic, "
         "and \u2014 for coding questions \u2014 the test cases used to grade submissions."],
        ["data/rubrics/rubrics_final_clean.json", "Per-question grading rubrics: mandatory concepts, concept "
         "groups, common mistakes \u2014 what the evaluator checks an answer against."],
        ["apps/web/src/InterviewRoom.jsx", "The main frontend screen: records/sends answers, opens the "
         "WebSocket, submits code via /api/run_code before forwarding the result."],
        ["apps/web/src/Report.jsx, Dashboard.jsx, AdminDashboard.jsx", "Post-session report view, candidate "
         "dashboard, and the admin view of historical sessions."],
        ["rl/checkpoints/", "The trained PPO model files (one per training seed) actually loaded at inference "
         "time."],
        ["tests/", "The automated test suite \u2014 unit tests per component plus integration tests for full "
         "session flows."],
    ],
)

page_break()
# =====================================================================
# SECTION 4 -- DEEP DIVE: THE ORCHESTRATOR AND THE GUARDRAILS
# =====================================================================
add_heading("4. Deep Dive: The Orchestrator and the Safety Guardrails", 1)
add_p(
    "File: agents/orchestrator/interview_orchestrator.py. This is the single most important file in the "
    "project. It is a Python class, InterviewOrchestrator, with one instance per active interview session. "
    "Every piece of state \u2014 scores so far, current difficulty, how many questions asked, audio signals "
    "\u2014 lives as a dictionary inside this one object, protected by an asyncio.Lock so that two messages "
    "arriving close together can't corrupt it."
)
add_heading("4.1 The PPO + Guardrail Decision", 2)
add_p(
    "After every answer is scored, the orchestrator decides the next question's difficulty in two steps: "
    "first, the trained PPO policy proposes an action (Easier / Same / Harder) based on the 6-number state "
    "vector; second, six deterministic rules \u2014 the guardrails \u2014 get the chance to override that "
    "proposal if it would be pedagogically unsafe (for example, making things harder for someone who is "
    "visibly struggling). This two-step design is deliberate: the learned policy is never trusted on its "
    "own in production."
)
add_p("Here is the guardrail function exactly as it runs in the live, deployed orchestrator today:")
add_code(
"""def _apply_guardrails(
    self,
    action_idx: int,
    perf: float,
    avg_perf: float,
    conf: float,
    hes: float,
    diff_norm: float,
) -> int:
    consec = int(self._state.get("consecutive_followups", 0))

    # G4 - critically struggling candidate
    if perf < 0.30 and hes > 0.60:
        self._last_guardrail_name = "guardrail_G4"
        return _ACTION_NAME_TO_IDX["Easier"]

    # G1 - low performance at mid difficulty
    if perf < 0.30 and 0.4 <= diff_norm <= 0.7:
        self._last_guardrail_name = "guardrail_G1"
        return _ACTION_NAME_TO_IDX["Easier"]

    # G2 - low confidence + high hesitation
    if conf < 0.30 and hes > 0.70 and perf < 0.80:
        self._last_guardrail_name = "guardrail_G2"
        return _ACTION_NAME_TO_IDX["Easier"] if hes > 0.85 else _ACTION_NAME_TO_IDX["Same"]

    # G3/G5 collapsed into conservative same/easier behavior
    if 0.40 < perf < 0.65 and avg_perf < 0.60 and consec < 2:
        self._last_guardrail_name = "guardrail_G3"
        return _ACTION_NAME_TO_IDX["Same"]

    # G6 - strong candidate, push harder
    gap = perf - avg_perf
    nervous_expert = conf < 0.40 and hes > 0.60
    if perf >= 0.90 and gap > 0.25 and not nervous_expert:
        self._last_guardrail_name = "guardrail_G6"
        return _ACTION_NAME_TO_IDX["Harder"]

    self._last_guardrail_name = None
    return action_idx""",
    caption="agents/orchestrator/interview_orchestrator.py, lines 1532-1576",
)
add_p(
    "Read top to bottom, each 'if' is a rule, checked in priority order, and the first one that matches "
    "wins \u2014 the function returns immediately. If none match, the PPO policy's own proposed action "
    "(action_idx) is used unchanged. In plain terms: G4 and G1 catch someone clearly struggling and make it "
    "easier; G2 catches someone who sounds unsure even if their answer wasn't technically wrong; G3 holds "
    "steady for a mid-performing, trending-down candidate; G6 is the only rule that escalates difficulty, "
    "and only for a candidate who is both scoring very well and improving, unless their voice signals suggest "
    "they are a 'nervous expert' (good answer, high anxiety) in which case escalation is suppressed."
)
add_heading("4.2 An Honest, Documented Gap: Two Versions of the Same Rules", 2)
add_p(
    "There are actually two implementations of these same six rules in the codebase: the one above (the "
    "live one, used by real sessions), and a second, \u2018canonical\u2019 copy in rl/guardrails.py, used by "
    "the training/simulation environment and by this phase's own automated boundary tests. They were "
    "supposed to be identical and were found, during this phase's own audit, to have quietly drifted apart "
    "in three small but real ways. This is disclosed in full in the dissertation (Chapter 6, Chapter 10) "
    "rather than hidden, and it's a very likely review question, so it's worth knowing cold:"
)
add_table(
    ["Rule", "Canonical (rl/guardrails.py)", "Live (interview_orchestrator.py)"],
    [
        ["G5 threshold", "0.30 \u2264 perf < 0.65", "0.40 < perf < 0.65 (narrower; never updated after a fix was made to the canonical copy)"],
        ["G6 'gap' meaning", "perf - diff_norm (performance vs. the question's own difficulty)", "perf - avg_perf (performance vs. the candidate's own rolling average \u2014 a different signal)"],
        ["G6 nervous_expert", "(0.80<perf<0.95 AND hes>0.65) OR (conf<0.40 AND hes>0.60)", "only the second half of that condition \u2014 the first half is missing"],
    ],
)
add_p(
    "None of these three gaps were fixed in the live code during this phase \u2014 they are reported as "
    "open, disclosed findings rather than silently patched, because changing the live decision logic without "
    "a separate, approved experiment would risk invalidating other results. If asked 'why didn't you just "
    "fix it', the honest answer is: fixing production decision logic outside a controlled, pre-registered "
    "experiment is exactly the kind of unreviewed change this project's own process rules are designed to "
    "prevent."
)
add_code(
"""def apply_canonical_guardrails(
    perf: float, avg_perf: float, conf: float, hes: float,
    progress: float, difficulty: float, proposed_action: int,
    consecutive_failures: int = 0, is_infrastructure_failure: bool = False,
    medium_difficulty_min: float = 0.4, medium_difficulty_max: float = 0.7,
) -> Tuple[int, bool, str]:
    action = int(proposed_action)
    if is_infrastructure_failure:
        return ACTION_SAME, True, "guardrail_infra_failure_same"
    diff_norm = difficulty / 5.0 if difficulty > 1.0 else difficulty
    if perf < 0.30 and hes > 0.60:
        return ACTION_EASIER, True, "g4_stuck_easier"
    # ... (G1, G2, G5, G6 follow the same pattern)""",
    caption="rl/guardrails.py, lines 47-91 (abridged)",
)

page_break()
# =====================================================================
# SECTION 5 -- DEEP DIVE: THE SEMANTIC EVALUATOR
# =====================================================================
add_heading("5. Deep Dive: The Semantic Evaluator (S1 / S2 / R)", 1)
add_p(
    "File: services/evaluator/app.py. This is what scores a spoken/typed verbal answer. The core idea: no "
    "single similarity check can tell 'uses the right vocabulary' apart from 'actually answers the "
    "question', so three different, independent checks are combined with fixed weights."
)
add_table(
    ["Component", "What it measures", "Weight"],
    [
        ["S1 \u2014 Sentence-BERT", "Plain semantic similarity between the candidate's answer and a model answer. The weakest signal on its own \u2014 easily fooled by shared vocabulary without correct reasoning.", "0.15"],
        ["S2 \u2014 FAISS concept coverage", "Which specific rubric concepts (from the question's grading rubric) are actually present in the answer, using a FAISS similarity index.", "0.35"],
        ["R \u2014 CrossEncoder", "A fine-tuned CrossEncoder model judging reasoning quality \u2014 whether the explanation itself makes sense, not just whether the right words appear.", "0.50"],
    ],
)
add_p("Here is the exact scoring code:")
add_code(
"""S1 = semantic_score(candidate_text, rubric)
S2, concept_details = concept_detection(candidate_text, rubric)
reasoning_score = cross_encoder_verification(qn, candidate_text, rubric)

bonus = bonus_score(candidate_text, rubric)
penalty = mistake_penalty(candidate_text, rubric, reasoning_score, S2)
mandatory_pass = mandatory_check(candidate_text, rubric)

# Dampen S2 when reasoning is weak (prevents keyword stuffing)
effective_S2 = S2 if reasoning_score > 0.30 else S2 * 0.60

base_score = (
    0.15 * S1 +
    0.35 * effective_S2 +
    0.50 * reasoning_score
)

final_score = base_score + bonus - penalty
final_score = max(0.0, min(1.0, final_score))""",
    caption="services/evaluator/app.py, lines 356-387",
)
add_p(
    "The single most important line to understand is effective_S2. Without it, a candidate could 'stuff' an "
    "answer with every rubric keyword, score high on S2 (concept coverage) despite having no real reasoning, "
    "and inflate their final score. The fix: if the CrossEncoder's reasoning score is weak (0.30 or below), "
    "the concept-coverage component is cut to 60% of its value before the weighted sum is computed. This is "
    "the project's keyword-stuffing defense, and it is the reason the full composite evaluator deliberately "
    "scores lower on raw correlation with human raters than a simpler R-only score would (see Section 11) "
    "\u2014 it is trading a bit of correlation for resistance to gaming."
)
add_heading("5.1 Verbal vs. Code: Two Separate Scoring Paths", 2)
add_p(
    "A common point of confusion worth clearing up directly: spoken/typed verbal answers go through "
    "services/evaluator/app.py (above). C code submissions never touch this file at all \u2014 they go "
    "through a completely separate path, the Docker sandbox described in Section 9. The two paths share "
    "nothing except that both eventually produce a single final_score in [0, 1]."
)

page_break()
# =====================================================================
# SECTION 6 -- DEEP DIVE: REINFORCEMENT LEARNING (PPO)
# =====================================================================
add_heading("6. Deep Dive: The Reinforcement-Learning Policy (PPO)", 1)
add_p(
    "Files: rl/env/interview_env.py (training environment, simulation only), agents/strategy/"
    "hybrid_orchestrator.py (loads the trained model and builds its input at inference time), rl/checkpoints/ "
    "(the actual trained model files)."
)
add_heading("6.1 Training Configuration", 2)
add_table(
    ["Setting", "Value"],
    [
        ["Algorithm", "Proximal Policy Optimisation (PPO), Stable-Baselines3, MlpPolicy"],
        ["Training steps", "24,576 timesteps per seed"],
        ["Seeds", "5 independent training seeds: 42, 123, 456, 789, 999"],
        ["State (observation)", "6 numbers, each in [0, 1]: last score, rolling-average score, voice confidence, hesitation, session progress (t/T), current difficulty / 5"],
        ["Action space", "Discrete(3): Easier / Same / Harder"],
        ["Deployed at inference", "One checkpoint per seed in rl/checkpoints/; the live app loads a specific seed's checkpoint, not an ensemble"],
    ],
)
add_p("How the 6-number state vector gets built at inference time, including a subtlety worth knowing:")
add_code(
"""# 5. Normalized Turn Progress Ratio (t / T in [0.0, 1.0])
raw_progress = session.get("progress")
if raw_progress is None:
    raw_progress = session.get("turn_progress")
if raw_progress is None and ("turn_idx" in session or "current_turn" in session):
    turn_idx = session.get("current_turn") or session.get("turn_idx")
    total_turns = (session.get("total_turns") or session.get("total_questions")
                   or session.get("max_steps") or 10)
    raw_progress = float(turn_idx) / float(total_turns)
if raw_progress is None:
    # Fallback to last_time_norm or scores length
    if "last_time_norm" in session and session["last_time_norm"] is not None:
        raw_progress = session.get("last_time_norm")
    else:
        scores_len = len(session.get("scores", []))
        total_turns = session.get("total_questions") or session.get("total_turns") or 10
        raw_progress = float(scores_len) / float(total_turns) if total_turns > 0 else 0.0""",
    caption="agents/strategy/hybrid_orchestrator.py, lines 116-139",
)
add_p(
    "In an ordinary live session, session['progress'] is always set directly by the orchestrator, so this "
    "reads as simply 'how far through the interview are we' (current question number / total questions). "
    "The fallback chain only matters in the unusual case where that key is missing \u2014 and the very last "
    "fallback, last_time_norm, is actually a different quantity (how long the candidate took to answer "
    "their previous question, not session progress at all). This is a disclosed, not-yet-removed design "
    "wrinkle, not a hidden one \u2014 see Section 12."
)
add_heading("6.2 Does the Learned Policy Actually Help?", 2)
add_p(
    "This is the single most important, most honest finding of this whole phase, and it is very likely to "
    "come up: no, not on its own. The guardrail layer \u2014 the deterministic rules in Section 4, not the "
    "learned PPO policy \u2014 is what actually drives almost all of the measured improvement. The full "
    "results are in Section 11.3; the short version is that a simple rule-based heuristic with no learning "
    "at all already beats the full RL-plus-guardrail system on the project's own difficulty-tracking metric."
)

page_break()
# =====================================================================
# SECTION 7 -- DEEP DIVE: FEEDBACKAGENT AND QWEN
# =====================================================================
add_heading("7. Deep Dive: FeedbackAgent and Qwen \u2014 Why the LLM Can't Fake the Score", 1)
add_p(
    "File: agents/orchestrator/feedback_agent.py. This is probably the single most-asked question in any "
    "review of an LLM-involving project: 'how do you know the AI isn't just making up the grade?' The "
    "answer here is structural, not a promise \u2014 the code makes it impossible for Qwen's output to "
    "change the score, because the score is already finalised before Qwen is even called."
)
add_code(
"""score = float(eval_result.get("final_score", 0.5))
raw = eval_result.get("raw") or {}
s1 = float(raw.get("S1_semantic", score))
s2 = float(raw.get("S2_structural", score))
r  = float(raw.get("reasoning_score", score))
# ... (score_breakdown dict built here, from `score`) ...

# -- Query Qwen Feedback Microservice --------------------------------
qwen_res = await self._query_qwen_feedback(
    transcript=transcript, question=question, eval_result=eval_result,
    candidate_state={"confidence": conf, "hesitation": hesitation_rate, "turn": turn_number},
    history=session_history or [], attempt_number=attempt_number, comparison=comparison,
)

if qwen_res:
    return {
        "final_score": round(score, 4),   # <-- same `score` variable from before the call
        "grade": grade,
        "score_breakdown": score_breakdown,
        "what_was_correct": qwen_res.get("what_was_correct", covered_concepts[:5]),
        "how_to_answer": qwen_res.get("how_to_answer", ""),
        "narrative_feedback": qwen_res.get("narrative_feedback", ""),
        # ... every other field below this line comes from qwen_res (TEXT only) ...
    }""",
    caption="agents/orchestrator/feedback_agent.py, lines 99-103 and 160-191 (abridged)",
)
add_p(
    "Walk through it in order: 'score' is set on line 99, from the evaluator's own final_score, before "
    "qwen_res even exists. Qwen is then called. In the returned dictionary, 'final_score' reuses that same "
    "pre-existing 'score' variable \u2014 it is never read back out of qwen_res. Every other field in that "
    "dictionary (what_was_correct, how_to_answer, narrative_feedback, etc.) does come from Qwen's response, "
    "because those are the written explanation, not the number. If Qwen's microservice is down or returns "
    "nothing, qwen_res is falsy and a deterministic, template-based feedback dictionary is returned instead "
    "(visible further down in the same function) \u2014 the session never silently loses its feedback."
)
add_p(
    "This was independently re-verified twice during this phase, by two separate code-path traces, "
    "specifically because an earlier, stale piece of the project's own documentation implied Qwen performed "
    "a 'scope-limited adjustment' to the score \u2014 wording that has since been corrected in the "
    "dissertation precisely because it was misleading."
)

page_break()
# =====================================================================
# SECTION 8 -- DEEP DIVE: AUDIO AND QUESTION SELECTION
# =====================================================================
add_heading("8. Deep Dive: Audio Signals and Question Selection", 1)
add_heading("8.1 Audio: Confidence and Hesitation", 2)
add_p(
    "Folder: agents/audio/. Whisper (or faster-whisper) converts speech to text; a separate prosody pass "
    "looks at pitch, pace, and pauses to estimate two numbers per turn: a confidence score and a hesitation "
    "score, both in [0, 1]. These are computed acoustic/linguistic proxies, not a clinically validated "
    "measurement of how confident someone actually feels \u2014 the dissertation is explicit about this "
    "distinction, and it matters: these numbers feed directly into the guardrail rules in Section 4."
)
add_p(
    "When no audio is available for a turn (e.g. a typed-only answer, or the audio pipeline failing), the "
    "system does not invent a plausible-looking number \u2014 it falls back to a fixed neutral default:"
)
add_code(
"""self._state = {
    ...
    "last_confidence_score": 0.5,
    ...
}""",
    caption="agents/orchestrator/interview_orchestrator.py, line 254 (session-state initialisation)",
)
add_p(
    "0.5 is the exact midpoint of the [0, 1] range \u2014 a deliberate 'I don't know' value, not a fabricated "
    "measurement. This directly matches NFR-3 in the dissertation's own requirements table: the system must "
    "never fabricate a metric when the underlying signal is unavailable."
)
add_heading("8.2 Question Selection: Two Modules, Only One Is Live", 2)
add_p(
    "There are two different question-selection implementations in this codebase, and only one of them is "
    "actually used by the running app \u2014 a distinction worth knowing cold, because it was a real "
    "documentation error in an earlier version of this project's own report."
)
add_code(
"""def select_questions(
    c_topics: list, dsa_topics: list, num: int, difficulty: int = 2,
    exclude_ids: Optional[set] = None, candidate_state: Optional[dict] = None,
) -> list:
    \"\"\"Personalized question selection with 3-level duplicate prevention
    and baseline Easy/Easy-Medium start.\"\"\"
    ...""",
    caption="apps/backend/main.py, lines 641-648 -- the PRODUCTION selector, zero randomness",
)
add_code(
"""return random.choice(candidate_topics)
...
return random.choice(candidates)""",
    caption="agents/question_selector/question_selector.py, lines 276 & 303 -- a SEPARATE, research-only "
            "module with real randomness, not called by the live app",
)
add_p(
    "The production path (apps/backend/main.py::select_questions) is a deterministic nearest-difficulty-"
    "match plus topic-rotation algorithm \u2014 no randomness at all, which matters for claims about "
    "reproducible question selection. The second file (agents/question_selector/question_selector.py) does "
    "contain real randomness, but it exists only as a separate research/baseline artifact and is never "
    "imported by the live orchestrator in normal operation. Confusing the two was a real, now-corrected "
    "error in an earlier draft of the project documentation."
)

page_break()
# =====================================================================
# SECTION 9 -- DEEP DIVE: THE CODING SANDBOX, AND TWO REAL BUGS
# =====================================================================
add_heading("9. Deep Dive: The Coding Sandbox — and Two Real Bugs Found This Phase", 1)
add_p(
    "File: agents/coding_executor/coding_executor.py. When a candidate submits C code, it is compiled and "
    "run inside an isolated, locked-down Docker container — never on the host machine directly. The "
    "container is started with a specific set of hardening flags:"
)
add_code(
    "compile_cmd = docker_prefix + [\n"
    '    "run", "--rm", "--name", compile_name,\n'
    '    "--user", "1001:1001",\n'
    '    "--net=none",\n'
    '    "--cap-drop=ALL",\n'
    '    "--security-opt=no-new-privileges",\n'
    '    f"--cpus={self.cpus}",\n'
    '    f"--memory={self.memory_mb}m",\n'
    '    f"--memory-swap={self.memory_mb}m",\n'
    '    f"--pids-limit={self.pids_limit}",\n'
    '    "--read-only",\n'
    '    "--tmpfs", "/workspace:rw,exec,size=32m,uid=1001,gid=1001,mode=1777",\n'
    '    "-v", f"{mount_src}:/input:ro",\n'
    "    self.image_name,\n"
    '    "/bin/bash", "-c",\n'
    '    "cp /input/solution.c /workspace/solution.c && gcc -O2 -Wall -Wextra -std=c11 "\n'
    '    "/workspace/solution.c -o /workspace/solution -lm",\n'
    "]",
    caption="agents/coding_executor/coding_executor.py, lines 214-230",
)
add_p(
    "In plain language: runs as a non-root user (1001:1001, not root), no network access at all "
    "(--net=none), every Linux capability dropped (--cap-drop=ALL), the root filesystem is read-only, "
    "memory/CPU/process count are all capped, and the container is destroyed immediately after. This "
    "phase's own testing verified these flags are not just present in configuration but actually exercised "
    "and effective at execution time (network isolation, memory limits, and the read-only filesystem were "
    "all directly tested, not just inspected as code)."
)
add_heading("9.1 Bug #1: Every Submission to /api/run_code Was Marked 'Correct'", 2)
add_p(
    "This was the single most serious defect found this phase, discovered while verifying the correction "
    "list against the live code rather than by reading the report in isolation."
)
add_p("Before the fix (the code as it existed at the start of this phase):", italic=True)
add_code(
    "test_cases = []\n"
    "if req.session_id and req.session_id in SESSIONS:\n"
    "    sess = SESSIONS[req.session_id]\n"
    '    curr_q = getattr(sess, "_current_question", None)   # this attribute is never set, anywhere\n'
    '    if isinstance(curr_q, dict) and curr_q.get("test_cases"):\n'
    '        test_cases = curr_q["test_cases"]\n\n'
    "result = evaluate_c_submission(req.code, test_cases=test_cases)",
    caption="apps/backend/main.py (BEFORE) -- /api/run_code",
)
add_p(
    "The orchestrator object (sess) never has an attribute called _current_question — that name does "
    "not exist anywhere in interview_orchestrator.py. So curr_q was always None, test_cases was always an "
    "empty list, and the pass/fail check downstream (passed_count == total_tests) was comparing 0 to 0 "
    "— which is always True. The practical effect: every single code submission through this endpoint "
    "was reported as 'passed', regardless of whether the code was actually correct, or even compiled."
)
add_p("After the fix:", italic=True)
add_code(
    'def _resolve_active_test_cases(sess, question_id: str = "") -> list:\n'
    '    """Server-side lookup of the active question\'s test cases. Never trust\n'
    '    client-supplied test results for scoring."""\n'
    '    if hasattr(sess, "_get_current_question"):\n'
    "        curr_q = sess._get_current_question(question_id or None)\n"
    '        if isinstance(curr_q, dict) and curr_q.get("test_cases"):\n'
    '            return curr_q["test_cases"]\n'
    "    return []",
    caption="apps/backend/main.py (AFTER)",
)
add_p(
    "And in agents/coding_executor/coding_executor.py, the acceptance check itself was tightened so that "
    "zero executed tests can never count as a pass, closing the root cause rather than only the one call "
    "site that exposed it:"
)
add_code(
    "is_accepted = (\n"
    "    total_tests > 0\n"
    "    and passed_count == total_tests\n"
    "    and mandatory_passed == mandatory_total\n"
    ")",
    caption="agents/coding_executor/coding_executor.py (AFTER) -- the total_tests > 0 clause is the fix",
)
add_heading("9.2 Bug #2 (more serious): The WebSocket Path Trusted the Client's Own Claim", 2)
add_p(
    "Fixing Bug #1 alone would not have been enough, because the primary scoring path for a code answer "
    "isn't /api/run_code at all — it's a separate WebSocket message type, code_submission, which "
    "actually drives difficulty adaptation. This path had an even more serious problem: it read whether the "
    "code passed directly from the browser's own message, with no server-side re-execution at all."
)
add_p("Before the fix:", italic=True)
add_code(
    'elif mtype == "code_submission":\n'
    "    result = await orch.handle_code_submission(\n"
    '        payload.get("code", ""),\n'
    '        payload.get("question_id", ""),\n'
    '        bool(payload.get("passed", False)),       # trusted straight from the client\n'
    '        int(payload.get("tests_passed", 0)),      # trusted straight from the client\n'
    '        int(payload.get("tests_total", 0)),       # trusted straight from the client\n'
    '        payload.get("stdout", ""),\n'
    '        payload.get("stderr", ""),\n'
    "    )\n"
    "    await dispatch_answer(result)",
    caption="apps/backend/main.py (BEFORE) -- the WebSocket code_submission handler",
)
add_p(
    "In plain terms: a candidate's browser could send a WebSocket message that simply claimed "
    '{"passed": true, "tests_passed": 10, "tests_total": 10} — with completely wrong or even empty '
    "code — and the server would accept that claim and score it as a perfect submission, because "
    "nothing on the server side ever actually ran the code to check."
)
add_p("After the fix:", italic=True)
add_code(
    'elif mtype == "code_submission":\n'
    "    from agents.coding_executor.coding_executor import evaluate_c_submission\n\n"
    '    submitted_code = payload.get("code", "")\n'
    '    submitted_qid = payload.get("question_id", "")\n'
    "    # Never trust client-supplied passed/tests_passed/tests_total: re-run\n"
    "    # the code server-side against the active question's real test cases.\n"
    "    test_cases = _resolve_active_test_cases(orch, submitted_qid)\n"
    "    sandbox_result = evaluate_c_submission(submitted_code, test_cases=test_cases)\n"
    "    result = await orch.handle_code_submission(\n"
    "        submitted_code, submitted_qid,\n"
    '        bool(sandbox_result.get("passed", False)),\n'
    '        int(sandbox_result.get("tests_passed", 0)),\n'
    '        int(sandbox_result.get("tests_total", 0)),\n'
    '        "", sandbox_result.get("compiler_output", ""),\n'
    "    )\n"
    "    await dispatch_answer(result)",
    caption="apps/backend/main.py (AFTER)",
)
add_p(
    "Now the server resolves the real test cases itself and actually runs the submitted code through the "
    "Docker sandbox before trusting any pass/fail verdict. The client-sent passed/tests_passed/tests_total "
    "fields are no longer read at all."
)
add_heading("9.3 Proof the Fix Actually Works: A Live Attack Test", 2)
add_p(
    "Both fixes were verified end-to-end against a real, running copy of the app (via FastAPI's own test "
    "client, with a real Docker daemon, not a mock), including a deliberate attack attempt:"
)
add_table(
    ["Test", "What was sent", "Server's response"],
    [
        ["Honest, correct code", "A real, working two_sum solution", "3/4 tests passed, score 0.75 (one hidden test case in the question bank has its own, separately-documented data error -- not a scoring bug)"],
        ["Honest, wrong code", "A stub that always returns -1 -1", "1/4 tests passed, score 0.25"],
        ["Forged attack", "The SAME wrong code, but the WebSocket message also claimed passed: true, tests_passed: 10, tests_total: 10", "Score 0.25 -- identical to the honest-wrong-code case. The forged claim was completely ignored."],
    ],
)
add_p(
    "That last row is the real proof: the forged claim had zero effect on the outcome. The server computed "
    "its own answer from the actual code, every time."
)

page_break()
# =====================================================================
# SECTION 10 -- ALL DEFECTS FOUND AND FIXED THIS PHASE
# =====================================================================
add_heading("10. All Defects Found and Fixed This Phase", 1)
add_p(
    "Eight real defects were found and fixed this phase, each independently verified rather than just "
    "patched and assumed working. Two (the code-submission trust-boundary bugs) are walked through in full "
    "in Section 9; the rest are summarised here."
)
add_table(
    ["#", "Defect", "Fix", "Verified by"],
    [
        ["1", "LLM-emitted JSON string fields iterated character-by-character instead of as lists (7 call sites, services/qwen/app.py)", "New type-checked _as_str_list() coercion helper", "Reproduced live against the real model before the fix; confirmed absent after"],
        ["2", "Admin dashboard showed only in-memory sessions, losing history on every backend restart", "New read-only list_sessions() merging stored + live session data", "27 historical sessions recovered, cross-checked against a raw SQL query"],
        ["3", "Dormant inference-time guardrail fallback still used the pre-fix G5 threshold", "Synced the fallback path's boundary to match", "5/5 new boundary test cases pass"],
        ["4", "/api/run_code always accepted submissions regardless of correctness (Section 9.1)", "Real server-side test-case lookup + total_tests > 0 guard", "Live Docker end-to-end run (Section 9.3)"],
        ["5", "WebSocket code_submission trusted client-claimed pass/fail with no server-side re-execution (Section 9.2)", "Server re-runs the code itself via the Docker sandbox", "Live Docker end-to-end run including a forged-payload attack test (Section 9.3)"],
        ["6", "Production question loader never attached real test_cases to question objects at all -- found only while trying to verify fixes 4/5", "Loader now copies and translates test cases into the sandbox's expected schema", "Live Docker end-to-end run; correct/incorrect code now score differently"],
        ["7", "A guardrail coverage gap: scores in [0.30, 0.40) with moderate confidence/hesitation had no guardrail rule covering them at all", "Widened G5's lower bound from 0.40 to 0.30 in the canonical module", "13/13 new boundary test cases pass; full suite re-run, zero regressions"],
        ["8", "Windows-specific crash in launch.py right after successful service startup (unguarded Unicode character)", "Reconfigured stdout to UTF-8", "Verified the launcher starts cleanly on the target environment"],
    ],
)
add_p(
    "Three guardrail divergences described in Section 4.2 (G5 threshold, G6 'gap' definition, G6 "
    "nervous_expert condition) are deliberately NOT in this list — they remain open, disclosed findings "
    "in the live code, not yet fixed, pending a decision on whether to make the live copy import the "
    "canonical module directly rather than keep a hand-duplicated copy in sync by hand."
)

page_break()
# =====================================================================
# SECTION 11 -- TEST RESULTS, COMPONENT BY COMPONENT
# =====================================================================
add_heading("11. Test Results, Component by Component", 1)
add_heading("11.1 Overall Automated Test Suite", 2)
add_table(
    ["Metric", "Result", "Notes"],
    [
        ["Backend test suite (historical headline figure)", "264 / 283 passing (93.3%)", "This is the figure reported in the dissertation's headline result, deliberately kept separate from later verification runs below"],
        ["Frontend test suite", "28 / 28 passing (100%)", "Vitest"],
        ["Every remaining failure", "Fully attributed", "18 failures traced to the Docker daemon being unavailable in that specific test run; exactly 1 to a single, pre-existing, already-documented issue (not altered this phase)"],
        ["Later, Docker-enabled verification run (this phase, after all 8 fixes)", "294 passed, 1 failed, 3 skipped", "The 1 failure is the same pre-existing, documented issue above -- zero new regressions from any fix made this phase"],
    ],
)
add_heading("11.2 Semantic Evaluator", 2)
add_table(
    ["Metric", "Result"],
    [
        ["Correlation with human raters (Spearman ρ)", "0.3812, 95% CI [0.158, 0.577] -- 3 raters, 64 constructed answers across 8 questions. Framed as moderate, exploratory evidence, not proof of human-level grading."],
        ["R-only correlation (CrossEncoder alone, no keyword-stuffing defense)", "0.4832 -- higher than the full composite. The gap is a deliberate trade: the full evaluator sacrifices some raw correlation for resistance to keyword-stuffing (Section 5)."],
        ["Adversarial-input testing", "10 constructed cases (empty input, 16.5k-character keyword spam, garbled Unicode, SQL-injection-like text, emoji spam, etc.) -- evaluator never crashed, always returned a score in [0, 1]"],
        ["CrossEncoder training provenance", "Incompletely documented -- disclosed as a partially fine-tuned derivative, not an off-the-shelf model, with incomplete training-data/hyperparameter records"],
    ],
)
add_heading("11.3 Reinforcement Learning (PPO + Guardrails)", 2)
add_table(
    ["Condition", "Difficulty-tracking MAE (lower is better)", "Notes"],
    [
        ["Fixed difficulty (no adaptation)", "1.200", "Deterministic baseline"],
        ["Rule-based heuristic (no learning)", "0.473", "Beats every PPO variant below"],
        ["PPO, raw policy (no guardrails)", "0.804", "Single seed (123) only -- not an aggregate"],
        ["PPO + guardrails", "0.677", "Five-seed mean"],
    ],
)
add_p(
    "The honest conclusion from this table, stated plainly in the dissertation: the simple heuristic alone "
    "already beats the full learned-policy-plus-guardrails system. The guardrail layer accounts for "
    "essentially all of the improvement over the fixed baseline; PPO's own marginal contribution beyond the "
    "guardrails is not statistically distinguishable from zero under a pre-registered equivalence test "
    "(registered margin ±0.12, confirmed 'Equivalent' under the primary analysis and three separate "
    "secondary sensitivity checks). The claim 'PPO improves tracking' has been explicitly withdrawn from "
    "this project's own evidence record."
)
add_heading("11.4 Coding Sandbox / Docker Security", 2)
add_table(
    ["What was tested", "Result"],
    [
        ["Network isolation, memory limits, PID limits, non-root execution, read-only filesystem, output truncation, infinite-loop termination", "All confirmed exercised and passing at execution time (not just present in configuration)"],
        ["Trust-boundary fix (Section 9)", "Live, real-Docker end-to-end verification, including a forged-payload attack test that was confirmed blocked"],
        ["Scope of the security testing", "This is runtime-verified sandbox behaviour against a defined set of attack/failure scenarios, not a claim of a complete, independent penetration-test audit"],
    ],
)
add_heading("11.5 Audio Pipeline", 2)
add_p(
    "Functional (does-it-run) coverage of the speech-to-text and prosody pipeline was verified. Word-error-"
    "rate of the transcription was not independently measured, because no verified reference-transcript "
    "dataset exists for this project -- this is stated as an open limitation, not glossed over."
)

page_break()
# =====================================================================
# SECTION 12 -- KNOWN LIMITATIONS
# =====================================================================
add_heading("12. Known Limitations (Stated Honestly)", 1)
add_p("All simulation-only; no real-candidate study.", bold=True)
add_p(
    "Every PPO/guardrail result above comes from simulated candidate personas, not real interview "
    "candidates. No claim is made about real-world learning outcomes.", bullet=False,
)
add_p("No formal human-subject usability or learning-outcome study.", bold=True)
add_p("Identified as the most significant outstanding evidentiary gap, in both the Phase-2 report and this phase.")
add_p("Three guardrail divergences remain open in the live code.", bold=True)
add_p("See Section 4.2 -- disclosed, not silently left in place.")
add_p("One pre-existing automated test still fails, by deliberate choice.", bold=True)
add_p(
    "A state-preservation test around the 6-D observation vector's obs[4] value; the underlying design "
    "ambiguity is explained in Section 6.1. Left unresolved pending a decision on how to interpret it, "
    "rather than silently patched."
)
add_p("One question-bank test case has a data error, not yet corrected in the dataset itself.", bold=True)
add_p(
    "Question C01's hidden test case 4 has a mathematically wrong expected_output ('1 2' instead of the "
    "correct '2 3', independently re-derived by hand). Reported here rather than silently worked around."
)
add_p("CrossEncoder training provenance is incomplete.", bold=True)
add_p("See Section 11.2.")

page_break()
# =====================================================================
# SECTION 13 -- QUICK-REFERENCE CHEAT SHEET
# =====================================================================
add_heading("13. Quick-Reference Cheat Sheet", 1)
add_p("The one-line answer to the questions most likely to come up in a review:")
add_table(
    ["If asked...", "The one-line answer"],
    [
        ["Is this multi-agent?", "No -- single-controller, hub-and-spoke. One orchestrator owns all state; nothing else makes its own decisions. Verified twice by separate code searches."],
        ["How does the evaluator avoid keyword stuffing?", "The concept-coverage component (S2) is cut to 60% of its value whenever the CrossEncoder's reasoning score is weak (Section 5)."],
        ["Does the LLM (Qwen) set the score?", "No -- structurally impossible. The score variable is fixed before Qwen is even called; Qwen's output only fills text fields (Section 7)."],
        ["Does PPO actually help?", "No, not on its own -- the heuristic alone beats the full RL+guardrail system; guardrails do essentially all the work (Section 6.2, 11.3)."],
        ["What's the biggest bug you found?", "A WebSocket handler that scored code submissions from a client-claimed pass/fail flag, with no server-side re-execution -- fixed and live-Docker-verified with a forged-payload attack test (Section 9.2-9.3)."],
        ["Is the Docker sandbox fully secure?", "Runtime-verified against a defined set of hardening flags and attack/failure scenarios -- not an independent penetration-test audit (Section 11.4)."],
        ["What's still unresolved?", "Three guardrail divergences, one test failure, one question-bank data error, incomplete CrossEncoder provenance -- all disclosed, none hidden (Section 12)."],
    ],
)

# =====================================================================
# SAVE
# =====================================================================
doc.save(OUT)
print("Saved:", OUT)
