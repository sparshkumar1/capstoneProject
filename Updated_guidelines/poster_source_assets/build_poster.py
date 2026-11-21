# -*- coding: utf-8 -*-
"""Build the PrepAIred capstone poster as an editable PPTX, A1 landscape
(841x594mm, true physical print size), following the official PES
University poster template layout (navy header + logo, 3-column
pill-header panels, Authors + real team/guide photos). Font sizes are
calibrated for a true A1 print read from ~1-1.5m, not for on-screen
viewing."""
import os
from pptx import Presentation
from pptx.util import Mm, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from PIL import Image

ROOT = r"D:\Capstone_29_AUG\capstoneProject"
ASSETS = r"D:\SystemTemp\claude\D--Capstone-29-AUG-capstoneProject\61cf1d3f-347b-40af-bbc4-adb241563c4c\scratchpad"
PHOTOS = ROOT + r"\Updated_guidelines\Photos"
CROP_CACHE = ASSETS + r"\poster_photo_crops"
LOGO = ROOT + r"\final_deliverables\07_Final_Semester_Report\assets\pes_logo.png"
OUT_PPTX = ROOT + r"\Updated_guidelines\PrepAIred_Poster.pptx"

os.makedirs(CROP_CACHE, exist_ok=True)

NAVY = RGBColor(0x1D, 0x28, 0x63)
CYAN = RGBColor(0x5F, 0xC1, 0xDB)
GREEN = RGBColor(0x7C, 0xBB, 0x00)
PURPLE = RGBColor(0xB0, 0x98, 0xD4)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
TEXT_DARK = RGBColor(0x20, 0x20, 0x20)
GREY_LINE = RGBColor(0x8A, 0x8A, 0x8A)

PAGE_W = Mm(841)
PAGE_H = Mm(594)

prs = Presentation()
prs.slide_width = PAGE_W
prs.slide_height = PAGE_H
slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank layout


def set_fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def no_shadow(shape):
    el = shape._element.spPr
    existing = el.find(qn("a:effectLst"))
    if existing is None:
        el.append(el.makeelement(qn("a:effectLst"), {}))


def add_rect(left, top, width, height, color, rounded=False, radius=None):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shp = slide.shapes.add_shape(shape_type, left, top, width, height)
    set_fill(shp, color)
    no_shadow(shp)
    if rounded and radius is not None:
        try:
            shp.adjustments[0] = radius
        except Exception:
            pass
    return shp


def add_text(left, top, width, height, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
             wrap=True, line_spacing=1.0, space_after=Pt(4)):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    first = True
    for para in runs:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        p.line_spacing = line_spacing
        p.space_after = space_after
        if isinstance(para, str):
            para = [(para, 15, False, False, TEXT_DARK)]
        for (text, size, bold, italic, color) in para:
            r = p.add_run()
            r.text = text
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.italic = italic
            r.font.color.rgb = color
            r.font.name = "Calibri"
    return tb


def add_bullets(left, top, width, height, items, size=19, color=TEXT_DARK, line_spacing=1.1,
                 space_after=Pt(9)):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    first = True
    for item in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.line_spacing = line_spacing
        p.space_after = space_after
        p.alignment = PP_ALIGN.LEFT
        pPr = p._p.get_or_add_pPr()
        pPr.set("marL", "285750")
        pPr.set("indent", "-285750")
        buClr = pPr.makeelement(qn("a:buClr"), {})
        srgb = pPr.makeelement(qn("a:srgbClr"), {"val": "%02X%02X%02X" % (NAVY[0], NAVY[1], NAVY[2])})
        buClr.append(srgb)
        buFont = pPr.makeelement(qn("a:buFont"), {"typeface": "Arial"})
        buChar = pPr.makeelement(qn("a:buChar"), {"char": "\u2022"})
        for el in pPr.findall(qn("a:buChar")) + pPr.findall(qn("a:buFont")) + pPr.findall(qn("a:buNone")) + pPr.findall(qn("a:buClr")):
            pPr.remove(el)
        pPr.append(buClr)
        pPr.append(buFont)
        pPr.append(buChar)
        r = p.add_run()
        r.text = item
        r.font.size = Pt(size)
        r.font.color.rgb = color
        r.font.name = "Calibri"
    return tb


def pill_header(left, top, width, height, text, color, size=22):
    shp = add_rect(left, top, width, height, color, rounded=True, radius=0.5)
    tf = shp.text_frame
    tf.word_wrap = True
    tf.margin_left = Mm(3)
    tf.margin_right = Mm(3)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = True
    r.font.color.rgb = WHITE
    r.font.name = "Calibri"
    return shp


def add_picture_fit(path, left, top, max_w, max_h, align="center"):
    with Image.open(path) as im:
        iw, ih = im.size
    ratio = min(max_w / iw, max_h / ih)
    w = int(iw * ratio)
    h = int(ih * ratio)
    x = left + (max_w - w) // 2 if align == "center" else left
    y = top
    return slide.shapes.add_picture(path, x, y, width=w, height=h)


def cover_crop(src_path, target_w_mm, target_h_mm, cache_key):
    """Center-crop src image to exactly match the target aspect ratio (CSS
    'cover' behaviour), so a portrait photo fills its frame with no grey
    letterboxing. Cached by cache_key so repeated builds don't re-crop."""
    out_path = os.path.join(CROP_CACHE, cache_key + ".jpg")
    target_ratio = target_w_mm / target_h_mm
    with Image.open(src_path) as im:
        im = im.convert("RGB")
        iw, ih = im.size
        src_ratio = iw / ih
        if src_ratio > target_ratio:
            new_w = int(ih * target_ratio)
            left = (iw - new_w) // 2
            box = (left, 0, left + new_w, ih)
        else:
            new_h = int(iw / target_ratio)
            top = (ih - new_h) // 2
            box = (0, top, iw, top + new_h)
        im.crop(box).save(out_path, "JPEG", quality=92)
    return out_path


def vline(x, y1, y2, color=GREY_LINE, weight=Pt(1.4)):
    ln = slide.shapes.add_connector(1, x, y1, x, y2)
    ln.line.color.rgb = color
    ln.line.width = weight


# =====================================================================
# BACKGROUND
# =====================================================================
add_rect(0, 0, PAGE_W, PAGE_H, WHITE)

# =====================================================================
# HEADER
# =====================================================================
HEADER_H = Mm(88)
add_rect(0, 0, PAGE_W, HEADER_H, NAVY)

logo_box_w = Mm(150)
add_rect(0, 0, logo_box_w, HEADER_H, WHITE)
add_picture_fit(LOGO, Mm(8), Mm(14), Mm(134), Mm(60))

add_text(logo_box_w + Mm(15), Mm(10), PAGE_W - logo_box_w - Mm(30), Mm(20),
         [[("PrepAIred: A Reinforcement-based LLM-powered", 40, True, False, WHITE)]],
         align=PP_ALIGN.CENTER, line_spacing=1.0)
add_text(logo_box_w + Mm(15), Mm(28), PAGE_W - logo_box_w - Mm(30), Mm(20),
         [[("Interview Preparation System", 40, True, False, WHITE)]],
         align=PP_ALIGN.CENTER, line_spacing=1.0)
add_text(logo_box_w + Mm(15), Mm(58), PAGE_W - logo_box_w - Mm(30), Mm(14),
         [[("Department of Computer Science and Engineering", 22, True, False, WHITE)]],
         align=PP_ALIGN.LEFT)
add_text(logo_box_w + Mm(15), Mm(74), PAGE_W - logo_box_w - Mm(30), Mm(13),
         [[("PES University, RR Campus, Bengaluru \u2013 560085.", 18, False, False, WHITE)]],
         align=PP_ALIGN.LEFT)

print("Header done")

# =====================================================================
# COLUMN GEOMETRY
# =====================================================================
MARGIN = Mm(18)
GUTTER = Mm(10)
COL_W = (PAGE_W - 2 * MARGIN - 2 * GUTTER) // 3
COL1_X = MARGIN
COL2_X = COL1_X + COL_W + GUTTER
COL3_X = COL2_X + COL_W + GUTTER

CONTENT_TOP = Mm(100)

DIV1_X = COL1_X + COL_W + GUTTER // 2
# The second divider (between column 2 and column 3) is intentionally
# removed: column 2's author/photo block needs the extra visual space,
# and the hard vertical rule there was crowding the real team/guide
# photographs added in this pass.
vline(DIV1_X, CONTENT_TOP, Mm(575))

PILL_H = Mm(19)
PAD = Mm(6)
BULLET_SIZE = 19
BULLET_SPACE = Pt(9)

# ----------------------------- COLUMN 1 -----------------------------
y = CONTENT_TOP
pill_header(COL1_X, y, COL_W, PILL_H, "PROBLEM STATEMENT", CYAN)
y2 = y + PILL_H + PAD
add_bullets(COL1_X, y2, COL_W, Mm(70), [
    "Fixed question pools at fixed difficulty \u2014 no adaptation to the candidate.",
    "Feedback is a bare score \u2014 no explanation of what was missing or wrong.",
    "No multimodal signals: vocal confidence and hesitation are ignored.",
], size=BULLET_SIZE, space_after=BULLET_SPACE)

y = Mm(198)
pill_header(COL1_X, y, COL_W, PILL_H, "KEY FEATURES", CYAN)
y2 = y + PILL_H + PAD
add_bullets(COL1_X, y2, COL_W, Mm(110), [
    "Specialised, orchestrator-coordinated architecture \u2014 a single, central InterviewOrchestrator hub drives every stage, not an ad hoc script.",
    "3-component rubric-anchored evaluator with a keyword-stuffing defense.",
    "PPO-driven adaptive difficulty under 6 deterministic guardrails.",
    "Whisper speech transcription with prosodic confidence/hesitation capture.",
    "15-field structured feedback; Docker-sandboxed C code execution.",
], size=BULLET_SIZE, space_after=BULLET_SPACE)

y = Mm(305)  # tightened from 345: the previous gap after Key Features
             # left ~80mm of unbalanced empty space versus columns 2/3
pill_header(COL1_X, y, COL_W, PILL_H, "RESULTS AND DISCUSSION", CYAN)
y2 = y + PILL_H + PAD
add_bullets(COL1_X, y2, COL_W, Mm(100), [
    "Test suite: 264/283 passing (93.3%); frontend 28/28 (100%).",
    "Evaluator vs. 3 human raters, 64 answers: Spearman \u03c1 = 0.3812.",
    "Safety-hardened by design: \u03c1=0.38 vs. R-alone \u03c1=0.48 \u2014 trades raw correlation for keyword-stuffing resistance.",
    "Guardrails, not PPO, drive the improvement: the rule-based heuristic alone beats the full RL+guardrail system.",
], size=BULLET_SIZE, space_after=BULLET_SPACE)
add_picture_fit(f"{ASSETS}/chart_ablation.png", COL1_X, Mm(415), COL_W, Mm(120))
add_text(COL1_X, Mm(538), COL_W, Mm(14),
         [[("The heuristic alone (0.473) outperforms every PPO variant; guardrails, not the learned policy, drive the ~44% improvement over fixed difficulty (1.200\u2192 0.677). PPO's own marginal contribution is not established.", 14, False, True, TEXT_DARK)]],
         align=PP_ALIGN.CENTER)

def draw_rect_photo(px, py, w_mm, h_mm, fname, caption_lines, border_color, cache_key):
    w, h = Mm(w_mm), Mm(h_mm)
    cropped = cover_crop(os.path.join(PHOTOS, fname), w_mm, h_mm, cache_key=cache_key)
    slide.shapes.add_picture(cropped, px, py, width=w, height=h)
    frame = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, py, w, h)
    frame.fill.background()
    frame.line.color.rgb = border_color
    frame.line.width = Pt(2.25)
    frame.adjustments[0] = 0.04
    no_shadow(frame)

    cap_runs = [[(caption_lines[0], 16, True, False, TEXT_DARK)]]
    if len(caption_lines) > 1:
        cap_runs.append([(caption_lines[1], 13.5, False, True, GREY_LINE)])
    add_text(px - Mm(3), py + h + Mm(2), w + Mm(6), Mm(16),
              cap_runs, align=PP_ALIGN.CENTER, line_spacing=1.0, space_after=Pt(1))


# ----------------------------- COLUMN 2 -----------------------------
# Budgeted top-to-bottom (see build_poster_vibrant.py for the same approach):
# the photo block is two rows -- guide centered alone, then the 4 students
# below -- which needs more height than one row of 5, so sections above
# it are tighter than an earlier single-row draft.
y = CONTENT_TOP
pill_header(COL2_X, y, COL_W, PILL_H, "OBJECTIVES", GREEN)
y2 = y + PILL_H + PAD  # = 125
add_bullets(COL2_X, y2, COL_W, Mm(68), [
    "Adaptively select question difficulty via guardrail-constrained RL.",
    "Score verbal & code answers via a multi-component semantic evaluator.",
    "Capture prosodic audio signals for both scoring and feedback.",
    "Deliver structured, actionable per-answer feedback \u2014 not a score alone.",
    "Execute and evaluate candidate C code in an isolated sandbox.",
], size=17.5, space_after=Pt(7))

y = Mm(195)
pill_header(COL2_X, y, COL_W, PILL_H, "PROPOSED METHODOLOGY", GREEN)
y2 = y + PILL_H + PAD  # = 220
add_bullets(COL2_X, y2, COL_W, Mm(50), [
    "React + Vite \u00b7 FastAPI + WebSocket \u00b7 Flask Evaluator \u00b7 SQLite.",
    "PPO (SB3, MlpPolicy): 24,576 timesteps/seed \u00d7 5 seeds; 6-D state; Discrete(3) actions.",
    "Deterministic rule-based fallback if the PPO checkpoint is unavailable.",
], size=17, space_after=Pt(6))
add_picture_fit(f"{ASSETS}/diagram_evaluator.png", COL2_X, Mm(277), COL_W, Mm(72))
add_text(COL2_X, Mm(353), COL_W, Mm(9),
         [[("Evaluator pipeline: S1/S2/R combined with a keyword-stuffing defense.", 13, False, True, TEXT_DARK)]],
         align=PP_ALIGN.CENTER)

# Authors / team block
y = Mm(367)
add_text(COL2_X, y, COL_W, Mm(10), [[("Authors:", 20, True, False, NAVY)]], align=PP_ALIGN.CENTER)
TEAM = [
    ("Naveen S Khadd", "PES1UG23CS924"),
    ("Sparsh Kumar", "PES1UG23CS909"),
    ("Athreya Shashidhara", "PES1UG23CS120"),
    ("Manasa S A", "PES1UG24CS811"),
]
rows = [[("%s   (%s)" % (n, s), 16.5, False, False, TEXT_DARK)] for n, s in TEAM]
add_text(COL2_X, Mm(380), COL_W, Mm(32), rows, align=PP_ALIGN.CENTER, line_spacing=1.12, space_after=Pt(2))
# No separate "Guide:" text line here -- Dr Uma D's photo caption below
# ("Dr. Uma D" / "Mentor") carries that information instead.

# Guide centered alone above, then the 4 students in a row below --
# reads as "mentor over team" rather than 5-in-a-row.
row1_y = Mm(415)
uma_w, uma_h = 50, 64
uma_x = COL2_X + (COL_W - Mm(uma_w)) // 2
draw_rect_photo(uma_x, row1_y, uma_w, uma_h, "Uma_mam.jpg", ["Dr. Uma D", "Mentor"], NAVY, cache_key="main_row1_uma")
# row1 bottom = 415 + 64(photo) + 2(gap) + 16(caption) = 497

row2_y = Mm(505)  # 497 + 8mm gap
STUDENTS = [
    ("Naveen_photo.jpg", ["Naveen"]),
    ("Sparsh_photo.jpeg", ["Sparsh"]),
    ("Athreya_photo.jpeg", ["Athreya"]),
    ("Manasa_Photo.jpeg", ["Manasa"]),
]
student_w, student_h = 42, 54
student_gap = Mm(10)
n_students = len(STUDENTS)
total_w = n_students * Mm(student_w) + (n_students - 1) * student_gap
start_x = COL2_X + (COL_W - total_w) // 2
for i, (fname, caption_lines) in enumerate(STUDENTS):
    px = start_x + i * (Mm(student_w) + student_gap)
    draw_rect_photo(px, row2_y, student_w, student_h, fname, caption_lines, GREEN, cache_key=f"main_row2_{i}_{fname}")
# row2 bottom = 505 + 54 + 2 + 16 = 577

# ----------------------------- COLUMN 3 -----------------------------
y = CONTENT_TOP
pill_header(COL3_X, y, COL_W, PILL_H, "SYSTEM ARCHITECTURE", PURPLE)
y2 = y + PILL_H + PAD
add_picture_fit(f"{ASSETS}/diagram_architecture.png", COL3_X, y2, COL_W, Mm(368))

y = Mm(498)
pill_header(COL3_X, y, COL_W, PILL_H, "CONCLUSION AND FUTURE WORK", PURPLE)
y2 = y + PILL_H + PAD
add_bullets(COL3_X, y2, COL_W, Mm(85), [
    "A verified, specialised, orchestrator-coordinated adaptive interview system pairing RL-based difficulty control with a resistance-hardened evaluator.",
    "RL/guardrail evidence is simulation-only; no human-subject usability study yet.",
    "Future work: resolve guardrail divergence, run a preregistered human study, measure real speech word-error-rate.",
], size=16.5, space_after=Pt(7))

prs.save(OUT_PPTX)
print("Saved full poster:", OUT_PPTX)
