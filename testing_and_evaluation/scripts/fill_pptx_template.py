"""
Fills the real PES PPT-Template_Phase3-Review3.pptx with PrepAIred's actual
content, preserving the template's own theme/master/layout (opens and edits
the real template file, does not rebuild slides from scratch).

Strategy per slide:
 - Replace the "Title of the Project" shape's text with the real project title.
 - Replace the "name1_name2_name3_name4" footer shape's text with the real team.
 - Replace the longest remaining text-containing shape's text with new content
   (the "instructional" placeholder body on every content slide), preserving
   that shape's first run's font (name/size/color/bold) as the template for
   all new runs, so the visual style is not broken.
 - Slide 1 (title slide) and Slide 4 (blocked on user input) get bespoke
   handling instead of the generic content-replacement rule.
 - Speaker notes are added to each slide's notes pane.

Run: .venv/Scripts/python.exe testing_and_evaluation/scripts/fill_pptx_template.py
"""
import copy
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Pt
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import OxmlElement

ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATE = ROOT / "Details" / "PPT-Template_Phase3- Review3.pptx"
OUT_PATH = ROOT / "final_deliverables" / "04_Final_Presentation" / "PrepAIred_Phase3_Review3.pptx"

PROJECT_TITLE = "PrepAIred: A Reinforcement-based LLM-powered Interview Preparation System"
PROJECT_ID = "PW26_UD05 (carried from Phase-2 -- confirm)"
PROJECT_GUIDE = "Dr Uma D"
TEAM_LINE = "Sparsh Kumar, Naveen S Khadd, Manasa S A, Athreya Shashidhara"
FOOTER_TEAM = "Sparsh Kumar_Naveen S Khadd_Manasa S A_Athreya Shashidhara"

# slide_number (1-indexed) -> list of bullet strings for the main content box
SLIDE_CONTENT: dict[int, list[str]] = {
    3: [  # Abstract
        "PrepAIred: adaptive technical-interview practice system",
        "Rubric-anchored semantic evaluation + RL-driven difficulty adaptation + structured per-turn feedback",
        "Phase-3: a complete, evidence-based testing and verification programme on top of the Phase-2 implementation",
        "Headline result: 264/283 automated tests passing (93.3%)",
        "Two real defects found and fixed; eight documentation-vs-code discrepancies corrected",
    ],
    5: [  # Implementation Details
        "Orchestrator (Python, asyncio) -- sole authoritative session-state owner, lock-serialised",
        "Evaluator (Flask) -- 3-component semantic scoring: SBERT + FAISS + CrossEncoder",
        "Strategy/RL (Stable-Baselines3 PPO) -- Discrete(3) actions + 6 deterministic guardrail rules",
        "Coding sandbox (Docker) -- isolated per-submission containers",
        "Frontend (React + Vite) -- WebSocket-driven",
        "Algorithm shown: adaptive-difficulty pipeline (state build -> PPO -> guardrail override -> clamp)",
    ],
    6: [  # Project Demonstration
        "Backend + evaluator confirmed live and healthy during this phase's smoke testing",
        "Real health-check responses captured; real 125-question bank loaded",
        "Live walkthrough: start session -> verbal answer -> code answer -> feedback -> adaptive next question -> report",
        "[Live demo / recording to be run before the review]",
    ],
    7: [  # Test Plan and Strategy
        "22 testing categories classified by actual relevance to this codebase (not a generic checklist)",
        "283-test existing suite (unit+integration+e2e) + 11 new scripts this phase",
        "New: API contract, adversarial-input, DB integrity, security-config, performance, UI-structural testing",
        "Environment: Windows 11, Python 3.11.9, documented git commit",
        "Tools: pytest, Vitest, direct-against-production-code scripts (no mocking of the function under test)",
        "Benefit: found 2 real defects + 8 documentation errors a generic approach would have missed",
        "Limitation: 18 tests blocked pending a running Docker daemon (documented, not hidden)",
    ],
    8: [  # Results and Discussion
        "264/283 automated tests passing (93.3%) -- every failure fully attributed, zero unexplained",
        "FOUND & FIXED: guardrail coverage gap (perf 0.30-0.40 unguarded) -- found via direct testing of the live policy checkpoint; fixed with one threshold change; 13/13 verified; zero regressions",
        "FOUND & FIXED: launch.py crashed on Windows consoles (Unicode encoding)",
        "8 documentation-vs-code discrepancies corrected (e.g. question selection is rule-based, not FAISS; evaluator is Flask, not FastAPI)",
    ],
    9: [  # Applicability in Other Domains
        "Domains: adaptive-assessment systems pairing a learned policy with a deterministic safety layer (e-learning, medical-training simulators, automated proctoring/scoring)",
        "Common problem: safety layers are assumed correct because they're rule-based, but are rarely boundary-tested",
        "Transferable: direct-against-production testing; boundary-case construction at every rule threshold; diagnose-fix-reverify-regress discipline",
        "Limitation: requires a deterministic, inspectable guardrail function -- does not transfer to black-box policies",
    ],
    10: [  # Timeline
        "Phase-2 (Jan-May 2026): full implementation delivered",
        "Phase-3 (this phase): inspection -> test strategy -> baseline testing -> diagnosis & fixes -> results consolidation -> report/paper/PPT",
        "Project report: drafted in full (13 files) -- pending final DOCX formatting pass and 2 flagged citations",
    ],
    11: [  # Conclusion and Future Work
        "10/12 stated objectives met with direct evidence; core architecture verified functioning as designed",
        "Two real defects found and fixed this phase",
        "Future work: close the Docker-dependent test gap; resolve the 1 pre-existing known test failure",
        "Future work: formal human-subject evaluation; real WER evaluation of the audio pipeline",
        "Future work: a separate, explicitly-scoped decision on the (currently unbuilt) multi-agent coordination layer",
    ],
    13: [  # IEEE Draft
        "Status: drafted in full (content-complete, formatted to approximate the IEEE two-column layout)",
        "Rescoped to the real, verified system -- a separate draft describing an unbuilt multi-agent layer was found not to match the codebase and was explicitly excluded (research-integrity, not a downgrade)",
        "Core contribution: the guardrail-gap discovery-and-fix case study",
        "Target conferences/journals: to be discussed with guide given the paper's actual scope",
    ],
    14: [  # Any Other Information
        "The documentation-reconciliation process itself: 8 report-vs-code discrepancies found and corrected with direct evidence, as a methodological contribution independent of the code fixes",
    ],
}

SPEAKER_NOTES: dict[int, str] = {
    3: "Set context in under a minute -- this is a verification phase, not a new-feature phase. Lead with the guardrail-gap finding as the headline.",
    5: "Keep architecture-level, not a code dump. Point to the report for full pseudocode. Emphasize the guardrail-as-safety-layer framing since it pays off in Results.",
    6: "If a live demo isn't feasible in the room, use the Report.jsx screenshot or walk through the pseudocode from Slide 5 as a visual aid.",
    7: "This is the panel's highest-attention slide per the template's own instructions -- don't compress it. Walk through the diagnose-fix-reverify cycle for the guardrail gap as the concrete example.",
    8: "Strongest slide -- lead with the guardrail finding, it's the most defensible and most interesting result. Don't bury it under the pass-rate percentage.",
    9: "This slide exists in the PES template specifically -- keep it to the testing-methodology transfer, which is this phase's genuine contribution, not a generic 'AI is everywhere' claim.",
    10: "Be concrete about what's genuinely done vs pending -- don't overstate completion.",
    11: "Mirror the report's Chapter 11 -- don't introduce new claims here that aren't in the report.",
    13: "Be upfront that this is a rescoped paper, not the originally-circulated 'bounded authority' draft -- and explain briefly why: the original draft's results didn't exist in the codebase.",
}


def set_shape_bullets(shape, bullets: list[str], font_size_pt: float | None = None, as_bullets: bool = True) -> None:
    """
    Replace a text frame's content with `bullets`, one paragraph each.

    Earlier version cloned the original template paragraph's XML to try to
    preserve its bullet formatting -- but the template's content boxes are
    NOT uniform: some are genuinely bulleted lists, some are auto-numbered
    lists (buAutoNum, which does not re-number correctly across cloned/
    appended paragraphs), and some are plain prose paragraphs with no
    bullet at all (buNone). Cloning them produced visibly inconsistent
    results (some slides bulleted, some not, some numbered only on line 1).

    This version instead: (1) captures the template's RUN formatting (font
    name/size/color/bold) from the first run, which IS reliable: run
    properties are per-run attributes, separate from whatever list-type the
    paragraph happened to use, (2) explicitly constructs ONE consistent
    bullet pPr (a square-bullet marker, standard indent) for every new
    paragraph, so every content slide looks the same regardless of what the
    original template paragraph's list type was.
    """
    tf = shape.text_frame
    template_font = None
    if tf.paragraphs and tf.paragraphs[0].runs:
        template_font = tf.paragraphs[0].runs[0].font

    txBody = tf._txBody
    for p_el in list(txBody.findall(qn("a:p"))):
        txBody.remove(p_el)

    # If no explicit size is given and the template run had none either
    # (common for small placeholders like the footer, which inherit their
    # size from the slide layout/master), leave size_pt as None so the <a:rPr>
    # omits "sz" entirely and PowerPoint inherits the correct size --
    # forcing a fallback like 24pt here previously broke the footer, which
    # is meant to render much smaller than body-text content.
    size_pt = font_size_pt if font_size_pt is not None else (
        template_font.size.pt if template_font and template_font.size else None
    )
    font_name = template_font.name if template_font and template_font.name else "Trebuchet MS"
    color_rgb = None
    try:
        if template_font and template_font.color and template_font.color.type is not None:
            color_rgb = template_font.color.rgb
    except Exception:
        color_rgb = None

    for bullet in bullets:
        p_el = OxmlElement("a:p")
        pPr = OxmlElement("a:pPr")
        if as_bullets:
            pPr.set("marL", "342900")
            pPr.set("indent", "-342900")
            buFont = OxmlElement("a:buFont")
            buFont.set("typeface", "Arial")
            pPr.append(buFont)
            buChar = OxmlElement("a:buChar")
            buChar.set("char", "▪")  # small black square, standard PPT bullet glyph
            pPr.append(buChar)
        else:
            buNone = OxmlElement("a:buNone")
            pPr.append(buNone)
        p_el.append(pPr)

        r_el = OxmlElement("a:r")
        rPr = OxmlElement("a:rPr")
        rPr.set("lang", "en-IN")
        if size_pt is not None:
            rPr.set("sz", str(int(size_pt * 100)))
        rPr.set("dirty", "0")
        if color_rgb is not None:
            fill = OxmlElement("a:solidFill")
            clr = OxmlElement("a:srgbClr")
            clr.set("val", str(color_rgb))
            fill.append(clr)
            rPr.append(fill)
        for tag in ("a:latin", "a:ea", "a:cs"):
            f_el = OxmlElement(tag)
            f_el.set("typeface", font_name)
            rPr.append(f_el)
        r_el.append(rPr)
        t_el = OxmlElement("a:t")
        t_el.text = bullet
        r_el.append(t_el)
        p_el.append(r_el)

        txBody.append(p_el)


def replace_exact_text(shape, new_text: str) -> bool:
    if not shape.has_text_frame:
        return False
    if shape.text_frame.text.strip() == "":
        return False
    full = shape.text_frame.text
    if "Title of the Project" in full:
        set_shape_bullets(shape, [new_text], as_bullets=False)
        return True
    if "name1_name2_name3_name4" in full:
        set_shape_bullets(shape, [new_text], as_bullets=False)
        return True
    return False


def enable_shrink_to_fit(shape) -> None:
    tf = shape.text_frame
    tf.word_wrap = True
    try:
        tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    except Exception:
        pass


def main() -> int:
    prs = Presentation(str(TEMPLATE))
    slides = list(prs.slides)

    for i, slide in enumerate(slides):
        slide_num = i + 1
        text_shapes = [s for s in slide.shapes if s.has_text_frame and s.text_frame.text.strip()]

        # Universal: Title of the Project / footer replacement on every slide
        for shape in text_shapes:
            replace_exact_text(shape, PROJECT_TITLE if "Title of the Project" in shape.text_frame.text else FOOTER_TEAM)

        if slide_num == 1:
            for shape in slide.shapes:
                if shape.has_text_frame and shape.text_frame.text.startswith("Project Title"):
                    tf = shape.text_frame
                    lines = [
                        f"Project Title   :  {PROJECT_TITLE}",
                        f"Project ID       :  {PROJECT_ID}",
                        f"Project Guide :  {PROJECT_GUIDE}",
                        f"Project Team  :  {TEAM_LINE}",
                    ]
                    # The real title/team text is much longer than the template's
                    # blank placeholder lines, so it wraps to ~7-8 lines at the
                    # template's original 24pt and overflows past the footer bar.
                    # Shrink to 14pt and enable shrink-to-fit as a safety net.
                    set_shape_bullets(shape, lines, font_size_pt=14, as_bullets=False)
                    enable_shrink_to_fit(shape)
            continue  # slide 1 fully handled

        if slide_num == 4:
            # Blocked: needs real panel feedback. Leave template instructional
            # text in place but append a clear placeholder note instead of
            # inventing feedback.
            for shape in text_shapes:
                t = shape.text_frame.text
                if t.startswith("Provide the suggestions"):
                    set_shape_bullets(shape, [
                        "[PLACEHOLDER -- requires real Review-2 panel feedback, not generated]",
                        "What the panel said: [fill in]",
                        "What we changed / plan to change in response: [fill in]",
                    ], font_size_pt=20)
                    enable_shrink_to_fit(shape)
            continue

        if slide_num == 2:
            continue  # Outline already matches, no change needed

        if slide_num in (12, 15):
            # References slides -- leave the IEEE-format example in place
            # (already matches intent) plus a note on where the real list is.
            for shape in text_shapes:
                t = shape.text_frame.text
                if "(references)" in t:
                    set_shape_bullets(shape, [
                        "See final_deliverables/02_University_Project_Report/12_Bibliography.md",
                        "for the full IEEE-numbered reference list.",
                        "Note: 2 references ([6], [7]) are flagged unresolved -- resolve before using this slide.",
                    ], font_size_pt=20)
                    enable_shrink_to_fit(shape)
            continue

        if slide_num == 16:
            continue  # Thank You slide, no change

        # Generic content slides
        if slide_num in SLIDE_CONTENT:
            # Find the longest remaining text shape (the instructional/body box)
            candidates = [s for s in text_shapes if "Title of the Project" not in s.text_frame.text
                          and FOOTER_TEAM not in s.text_frame.text
                          and s.text_frame.text.strip() != PROJECT_TITLE]
            if candidates:
                content_shape = max(candidates, key=lambda s: len(s.text_frame.text))
                # 18pt (down from the template's 24pt default) plus shrink-to-fit,
                # since several slides' real content (7 bullets, some wrapping to
                # 2 lines) overflowed past the footer bar at the original size.
                set_shape_bullets(content_shape, SLIDE_CONTENT[slide_num], font_size_pt=18)
                enable_shrink_to_fit(content_shape)

        # Speaker notes
        if slide_num in SPEAKER_NOTES:
            notes_slide = slide.notes_slide
            notes_slide.notes_text_frame.text = SPEAKER_NOTES[slide_num]

    prs.save(str(OUT_PATH))
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
