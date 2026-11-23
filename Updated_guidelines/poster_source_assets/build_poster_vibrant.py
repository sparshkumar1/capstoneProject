# -*- coding: utf-8 -*-
"""Build a visually vibrant/stylised variant of the PrepAIred capstone
poster: same content and section structure as build_poster.py (same
bullets, numbers, authors, order), but with a bold gradient header,
gradient section pills, tinted card panels with accent bars, circular
photo medallions with coloured rings, and a soft decorative background
-- an A1 landscape (841x594mm) print-size PPTX."""
import os
from pptx import Presentation
from pptx.util import Mm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from pptx.enum.dml import MSO_FILL
from PIL import Image

ROOT = r"D:\Capstone_29_AUG\capstoneProject"
ASSETS = r"D:\SystemTemp\claude\D--Capstone-29-AUG-capstoneProject\61cf1d3f-347b-40af-bbc4-adb241563c4c\scratchpad"
PHOTOS = ROOT + r"\Updated_guidelines\Photos"
CROP_CACHE = ASSETS + r"\poster_photo_crops"
LOGO = ROOT + r"\final_deliverables\07_Final_Semester_Report\assets\pes_logo.png"
OUT_PPTX = ROOT + r"\Updated_guidelines\PrepAIred_Poster_Vibrant.pptx"

os.makedirs(CROP_CACHE, exist_ok=True)

# ---- vibrant palette ----
INDIGO = RGBColor(0x2D, 0x1B, 0x69)
MAGENTA = RGBColor(0xC3, 0x1C, 0x7A)
ORANGE = RGBColor(0xFF, 0x7A, 0x1A)
TEAL = RGBColor(0x00, 0xB4, 0xA6)
TEAL_DK = RGBColor(0x00, 0x7A, 0x87)
LIME = RGBColor(0x7E, 0xD9, 0x57)
LIME_DK = RGBColor(0x2E, 0x9E, 0x3A)
VIOLET = RGBColor(0x9B, 0x5D, 0xE0)
VIOLET_DK = RGBColor(0x5B, 0x2A, 0x9E)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
TEXT_DARK = RGBColor(0x25, 0x1E, 0x33)
CARD_TINT = {
    "teal": RGBColor(0xE6, 0xFB, 0xF9),
    "lime": RGBColor(0xF0, 0xFC, 0xE9),
    "violet": RGBColor(0xF6, 0xF0, 0xFC),
}
RING_CYCLE = [TEAL_DK, ORANGE, MAGENTA, VIOLET_DK, LIME_DK]

PAGE_W = Mm(841)
PAGE_H = Mm(594)

prs = Presentation()
prs.slide_width = PAGE_W
prs.slide_height = PAGE_H
slide = prs.slides.add_slide(prs.slide_layouts[6])


def set_fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def set_alpha(shape, pct):
    """pct = opacity 0-100 (100 = fully opaque)."""
    sp = shape.fill.fore_color._xFill
    srgb = sp.find(qn("a:srgbClr"))
    if srgb is None:
        return
    for a in srgb.findall(qn("a:alpha")):
        srgb.remove(a)
    alpha = srgb.makeelement(qn("a:alpha"), {"val": str(int(pct * 1000))})
    srgb.append(alpha)


def no_shadow(shape):
    el = shape._element.spPr
    if el.find(qn("a:effectLst")) is None:
        el.append(el.makeelement(qn("a:effectLst"), {}))


def soft_shadow(shape):
    """Subtle drop shadow for a modern card/medallion look."""
    spPr = shape._element.spPr
    existing = spPr.find(qn("a:effectLst"))
    if existing is not None:
        spPr.remove(existing)
    effectLst = spPr.makeelement(qn("a:effectLst"), {})
    shadow = effectLst.makeelement(qn("a:outerShdw"), {
        "blurRad": "90000", "dist": "38000", "dir": "5400000", "rotWithShape": "0",
    })
    clr = shadow.makeelement(qn("a:srgbClr"), {"val": "1A1A2E"})
    alpha = clr.makeelement(qn("a:alpha"), {"val": "38000"})
    clr.append(alpha)
    shadow.append(clr)
    effectLst.append(shadow)
    spPr.append(effectLst)


def add_rect(left, top, width, height, color, rounded=False, radius=None, alpha=None, shadow=False):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shp = slide.shapes.add_shape(shape_type, left, top, width, height)
    set_fill(shp, color)
    if alpha is not None:
        set_alpha(shp, alpha)
    if shadow:
        soft_shadow(shp)
    else:
        no_shadow(shp)
    if rounded and radius is not None:
        try:
            shp.adjustments[0] = radius
        except Exception:
            pass
    return shp


def add_gradient_rect(left, top, width, height, stops, angle=0, rounded=False, radius=None, shadow=False):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shp = slide.shapes.add_shape(shape_type, left, top, width, height)
    shp.line.fill.background()
    shp.fill.gradient()
    gs = shp.fill.gradient_stops
    for i, (pos, color) in enumerate(stops):
        if i < len(gs):
            gs[i].position = pos
            gs[i].color.rgb = color
    shp.fill.gradient_angle = angle
    if shadow:
        soft_shadow(shp)
    else:
        no_shadow(shp)
    if rounded and radius is not None:
        try:
            shp.adjustments[0] = radius
        except Exception:
            pass
    return shp


def add_circle(left, top, diameter, color, alpha=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, diameter, diameter)
    set_fill(shp, color)
    if alpha is not None:
        set_alpha(shp, alpha)
    no_shadow(shp)
    return shp


def add_text(left, top, width, height, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
             wrap=True, line_spacing=1.0, space_after=Pt(4), font="Calibri"):
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
            r.font.name = font
    return tb


def add_bullets(left, top, width, height, items, size=19, color=TEXT_DARK, bullet_color=None,
                 line_spacing=1.12, space_after=Pt(10)):
    bullet_color = bullet_color or color
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
        srgb = pPr.makeelement(qn("a:srgbClr"), {"val": "%02X%02X%02X" % (bullet_color[0], bullet_color[1], bullet_color[2])})
        buClr.append(srgb)
        buFont = pPr.makeelement(qn("a:buFont"), {"typeface": "Arial"})
        buChar = pPr.makeelement(qn("a:buChar"), {"char": "\u25CF"})
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
        r.font.bold = False
    return tb


def pill_header(left, top, width, height, text, stops, angle=0, size=23):
    shp = add_gradient_rect(left, top, width, height, stops, angle=angle, rounded=True, radius=0.5, shadow=True)
    tf = shp.text_frame
    tf.word_wrap = True
    tf.margin_left = Mm(4)
    tf.margin_right = Mm(4)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = True
    r.font.color.rgb = WHITE
    r.font.name = "Calibri"
    return shp


def card_panel(left, top, width, height, tint, accent):
    """Soft tinted rounded card with a coloured left accent bar, behind a
    content block, for a modern infographic look."""
    card = add_rect(left, top, width, height, tint, rounded=True, radius=0.06, shadow=True)
    bar = add_rect(left, top + Mm(2), Mm(3.2), height - Mm(4), accent, rounded=True, radius=0.5)
    return card, bar


def add_picture_fit(path, left, top, max_w, max_h, align="center"):
    with Image.open(path) as im:
        iw, ih = im.size
    ratio = min(max_w / iw, max_h / ih)
    w = int(iw * ratio)
    h = int(ih * ratio)
    x = left + (max_w - w) // 2 if align == "center" else left
    return slide.shapes.add_picture(path, x, top, width=w, height=h)


def cover_crop(src_path, target_w_mm, target_h_mm, cache_key):
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


def make_ellipse(picture):
    """Clip a picture shape to a perfect circle/ellipse via its XML geometry
    -- python-pptx has no high-level API for this, so it is set directly.
    OOXML requires spPr's children in schema order (xfrm, then geometry,
    then fill/line/effects); inserting at the wrong position silently
    breaks rendering (PowerPoint drops the picture fill), so the
    replacement geometry goes back at the exact index the old one came
    from, not index 0."""
    spPr = picture._element.spPr
    insert_at = len(spPr)
    for tag in ("a:prstGeom", "a:custGeom"):
        existing = spPr.find(qn(tag))
        if existing is not None:
            insert_at = list(spPr).index(existing)
            spPr.remove(existing)
            break
    geom = spPr.makeelement(qn("a:prstGeom"), {"prst": "ellipse"})
    geom.append(geom.makeelement(qn("a:avLst"), {}))
    spPr.insert(insert_at, geom)


# =====================================================================
# BACKGROUND -- soft gradient wash + decorative blobs
# =====================================================================
add_gradient_rect(0, 0, PAGE_W, PAGE_H, [(0.0, RGBColor(0xFB, 0xFA, 0xFF)), (1.0, RGBColor(0xF3, 0xFB, 0xFA))], angle=45)
add_circle(PAGE_W - Mm(120), PAGE_H - Mm(160), Mm(260), VIOLET, alpha=7)
add_circle(Mm(-60), PAGE_H - Mm(80), Mm(180), TEAL, alpha=8)
add_circle(PAGE_W - Mm(40), Mm(60), Mm(140), ORANGE, alpha=9)

# =====================================================================
# HEADER -- bold multi-stop gradient band
# =====================================================================
HEADER_H = Mm(90)
add_gradient_rect(0, 0, PAGE_W, HEADER_H,
                   [(0.0, INDIGO), (0.55, MAGENTA), (1.0, ORANGE)], angle=0)

logo_card_w, logo_card_h = Mm(146), Mm(74)
logo_card = add_rect(Mm(9), Mm(8), logo_card_w, logo_card_h, WHITE, rounded=True, radius=0.12, shadow=True)
add_picture_fit(LOGO, Mm(17), Mm(18), Mm(130), Mm(54))

add_text(logo_card_w + Mm(28), Mm(10), PAGE_W - logo_card_w - Mm(45), Mm(20),
         [[("PrepAIred: A Reinforcement-based LLM-powered", 41, True, False, WHITE)]],
         align=PP_ALIGN.CENTER, line_spacing=1.0, font="Calibri")
add_text(logo_card_w + Mm(28), Mm(28), PAGE_W - logo_card_w - Mm(45), Mm(20),
         [[("Interview Preparation System", 41, True, False, WHITE)]],
         align=PP_ALIGN.CENTER, line_spacing=1.0)
add_text(logo_card_w + Mm(28), Mm(58), PAGE_W - logo_card_w - Mm(45), Mm(14),
         [[("Department of Computer Science and Engineering", 23, True, False, WHITE)]],
         align=PP_ALIGN.CENTER)
add_text(logo_card_w + Mm(28), Mm(75), PAGE_W - logo_card_w - Mm(45), Mm(13),
         [[("PES University, RR Campus, Bengaluru \u2013 560085.", 18, False, False, WHITE)]],
         align=PP_ALIGN.CENTER)

# A thin bright accent strip under the header for extra pop
add_rect(0, HEADER_H, PAGE_W, Mm(3.2), LIME)

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
CONTENT_TOP = Mm(104)

PILL_H = Mm(20)
PAD = Mm(7)
BULLET_SIZE = 19
BULLET_SPACE = Pt(10)
TEAL_STOPS = [(0.0, TEAL_DK), (1.0, TEAL)]
LIME_STOPS = [(0.0, LIME_DK), (1.0, LIME)]
VIOLET_STOPS = [(0.0, VIOLET_DK), (1.0, VIOLET)]

# ----------------------------- COLUMN 1 (teal) -----------------------------
y = CONTENT_TOP
pill_header(COL1_X, y, COL_W, PILL_H, "PROBLEM STATEMENT", TEAL_STOPS)
y2 = y + PILL_H + PAD
card_panel(COL1_X, y2, COL_W, Mm(66), CARD_TINT["teal"], TEAL_DK)
add_bullets(COL1_X + Mm(10), y2 + Mm(8), COL_W - Mm(16), Mm(60), [
    "Fixed question pools at fixed difficulty \u2014 no adaptation to the candidate.",
    "Feedback is a bare score \u2014 no explanation of what was missing or wrong.",
    "No multimodal signals: vocal confidence and hesitation are ignored.",
], size=BULLET_SIZE, bullet_color=TEAL_DK, space_after=BULLET_SPACE)

y = Mm(200)
pill_header(COL1_X, y, COL_W, PILL_H, "KEY FEATURES", TEAL_STOPS)
y2 = y + PILL_H + PAD
card_panel(COL1_X, y2, COL_W, Mm(118), CARD_TINT["teal"], TEAL_DK)
add_bullets(COL1_X + Mm(10), y2 + Mm(8), COL_W - Mm(16), Mm(108), [
    "Specialised, orchestrator-coordinated architecture \u2014 a single, central InterviewOrchestrator hub drives every stage, not an ad hoc script.",
    "3-component rubric-anchored evaluator with a keyword-stuffing defense.",
    "PPO-driven adaptive difficulty under 6 deterministic guardrails.",
    "Whisper speech transcription with prosodic confidence/hesitation capture.",
    "15-field structured feedback; Docker-sandboxed C code execution.",
], size=BULLET_SIZE, bullet_color=TEAL_DK, space_after=BULLET_SPACE)

y = Mm(352)
pill_header(COL1_X, y, COL_W, PILL_H, "RESULTS AND DISCUSSION", TEAL_STOPS)
y2 = y + PILL_H + PAD
card_panel(COL1_X, y2, COL_W, Mm(90), CARD_TINT["teal"], TEAL_DK)
add_bullets(COL1_X + Mm(10), y2 + Mm(8), COL_W - Mm(16), Mm(80), [
    "Test suite: 264/283 passing (93.3%); frontend 28/28 (100%).",
    "Evaluator vs. 3 human raters, 64 answers: Spearman \u03c1 = 0.3812.",
    "Safety-hardened by design: \u03c1=0.38 vs. R-alone \u03c1=0.48 \u2014 trades raw correlation for keyword-stuffing resistance.",
], size=BULLET_SIZE, bullet_color=TEAL_DK, space_after=BULLET_SPACE)
chart_card_y = Mm(477)
card_panel(COL1_X, chart_card_y, COL_W, Mm(100), WHITE, ORANGE)
add_picture_fit(f"{ASSETS}/chart_ablation.png", COL1_X + Mm(8), chart_card_y + Mm(6), COL_W - Mm(16), Mm(86))
add_text(COL1_X, Mm(581), COL_W, Mm(10),
         [[("RL + guardrails cut difficulty-tracking error (MAE) nearly in half vs. the raw PPO policy.", 14.5, False, True, TEXT_DARK)]],
         align=PP_ALIGN.CENTER)

def draw_circle_photo(px, py, diameter_mm, fname, caption_lines, ring_color, cache_key):
    diameter = Mm(diameter_mm)
    ring = add_circle(px - Mm(1.6), py - Mm(1.6), diameter + Mm(3.2), ring_color)
    soft_shadow(ring)
    cropped = cover_crop(os.path.join(PHOTOS, fname), diameter_mm, diameter_mm, cache_key=cache_key)
    pic = slide.shapes.add_picture(cropped, px, py, width=diameter, height=diameter)
    make_ellipse(pic)
    white_ring = slide.shapes.add_shape(MSO_SHAPE.OVAL, px - Mm(0.3), py - Mm(0.3), diameter + Mm(0.6), diameter + Mm(0.6))
    white_ring.fill.background()
    white_ring.line.color.rgb = WHITE
    white_ring.line.width = Pt(3.0)
    no_shadow(white_ring)

    cap_runs = [[(caption_lines[0], 16.5, True, False, TEXT_DARK)]]
    if len(caption_lines) > 1:
        cap_runs.append([(caption_lines[1], 13.5, False, True, ring_color)])
    add_text(px - Mm(8), py + diameter + Mm(4), diameter + Mm(16), Mm(16),
              cap_runs, align=PP_ALIGN.CENTER, line_spacing=1.0, space_after=Pt(1))


# ----------------------------- COLUMN 2 (lime) -----------------------------
# NOTE: every y-coordinate below was computed as a running vertical budget
# (each section's top = previous section's bottom + an explicit gap) so
# that no two cards can overlap -- this column stacks five elements
# (objectives, methodology, diagram, authors, photos) in limited height.
# The photo block is two rows (guide centered alone, then the 4 students
# below), which needs more height than one row of 5, so the sections
# above it were trimmed slightly versus an earlier single-row draft.
y = CONTENT_TOP
pill_header(COL2_X, y, COL_W, PILL_H, "OBJECTIVES", LIME_STOPS)
y2 = y + PILL_H + PAD  # = 131
card_panel(COL2_X, y2, COL_W, Mm(70), CARD_TINT["lime"], LIME_DK)
add_bullets(COL2_X + Mm(10), y2 + Mm(7), COL_W - Mm(16), Mm(62), [
    "Adaptively select question difficulty via guardrail-constrained RL.",
    "Score verbal & code answers via a multi-component semantic evaluator.",
    "Capture prosodic audio signals for both scoring and feedback.",
    "Deliver structured, actionable per-answer feedback \u2014 not a score alone.",
    "Execute and evaluate candidate C code in an isolated sandbox.",
], size=17.5, bullet_color=LIME_DK, space_after=Pt(7))
# objectives card bottom = 131 + 70 = 201

y = Mm(208)  # 201 + 7mm gap
pill_header(COL2_X, y, COL_W, PILL_H, "PROPOSED METHODOLOGY", LIME_STOPS)
y2 = y + PILL_H + PAD  # = 235
card_panel(COL2_X, y2, COL_W, Mm(45), CARD_TINT["lime"], LIME_DK)
add_bullets(COL2_X + Mm(10), y2 + Mm(6), COL_W - Mm(16), Mm(38), [
    "React + Vite \u00b7 FastAPI + WebSocket \u00b7 Flask Evaluator \u00b7 SQLite.",
    "PPO (SB3, MlpPolicy): 24,576 timesteps/seed \u00d7 5 seeds; 6-D state; Discrete(3) actions.",
    "Deterministic rule-based fallback if the PPO checkpoint is unavailable.",
], size=17, bullet_color=LIME_DK, space_after=Pt(6))
# methodology bullets card bottom = 235 + 45 = 280

diag_card_y = Mm(287)  # 280 + 7mm gap
card_panel(COL2_X, diag_card_y, COL_W, Mm(80), WHITE, VIOLET_DK)
add_picture_fit(f"{ASSETS}/diagram_evaluator.png", COL2_X + Mm(8), diag_card_y + Mm(5), COL_W - Mm(16), Mm(68))
# diagram card bottom = 287 + 80 = 367
add_text(COL2_X, Mm(371), COL_W, Mm(9),  # 367 + 4mm gap
         [[("Evaluator pipeline: S1/S2/R combined with a keyword-stuffing defense.", 13, False, True, TEXT_DARK)]],
         align=PP_ALIGN.CENTER)
# caption bottom ~= 380

# Authors / team block
y = Mm(389)  # 380 + 9mm gap
add_text(COL2_X, y, COL_W, Mm(9), [[("Authors", 20, True, False, VIOLET_DK)]], align=PP_ALIGN.CENTER)
TEAM = [
    ("Naveen S Khadd", "PES1UG23CS924"),
    ("Sparsh Kumar", "PES1UG23CS909"),
    ("Athreya Shashidhara", "PES1UG23CS120"),
    ("Manasa S A", "PES1UG24CS811"),
]
rows = [[("%s   (%s)" % (n, s), 16.5, False, False, TEXT_DARK)] for n, s in TEAM]
add_text(COL2_X, Mm(401), COL_W, Mm(32), rows, align=PP_ALIGN.CENTER, line_spacing=1.12, space_after=Pt(2))
# rows bottom ~= 401 + 30 = 431

# Guide centered alone above, then the 4 students in a row below --
# visually reads as "mentor over team", not just 5-in-a-row.
row1_y = Mm(438)  # 431 + 7mm gap
uma_d = 56
uma_x = COL2_X + (COL_W - Mm(uma_d)) // 2
draw_circle_photo(uma_x, row1_y, uma_d, "Uma_mam.jpg", ["Dr. Uma D", "Mentor"], TEAL_DK, cache_key="vibrant_row1_uma")
# row1 bottom = 438 + 56(photo) + 4(gap) + 16(caption) = 514

row2_y = Mm(522)  # 514 + 8mm gap
STUDENTS = [
    ("Naveen_photo.jpg", ["Naveen"], RING_CYCLE[1]),
    ("Sparsh_photo.jpeg", ["Sparsh"], RING_CYCLE[2]),
    ("Athreya_photo.jpeg", ["Athreya"], RING_CYCLE[3]),
    ("Manasa_Photo.jpeg", ["Manasa"], RING_CYCLE[4]),
]
student_d = 50
student_gap = Mm(14)
n_students = len(STUDENTS)
total_w = n_students * Mm(student_d) + (n_students - 1) * student_gap
start_x = COL2_X + (COL_W - total_w) // 2
for i, (fname, caption_lines, ring_color) in enumerate(STUDENTS):
    px = start_x + i * (Mm(student_d) + student_gap)
    draw_circle_photo(px, row2_y, student_d, fname, caption_lines, ring_color, cache_key=f"vibrant_row2_{i}_{fname}")
# row2 bottom = 522 + 50 + 4 + 16 = 592

# ----------------------------- COLUMN 3 (violet) -----------------------------
# Same budgeted-layout approach as column 2: architecture card bottom is
# fixed so the conclusion pill below it never overlaps.
y = CONTENT_TOP
pill_header(COL3_X, y, COL_W, PILL_H, "SYSTEM ARCHITECTURE", VIOLET_STOPS)
y2 = y + PILL_H + PAD  # = 131
arch_card_h = Mm(359)
card_panel(COL3_X, y2, COL_W, arch_card_h, WHITE, VIOLET_DK)
add_picture_fit(f"{ASSETS}/diagram_architecture.png", COL3_X + Mm(8), y2 + Mm(6), COL_W - Mm(16), arch_card_h - Mm(12))
# architecture card bottom = 131 + 359 = 490

y = Mm(498)  # 490 + 8mm gap
pill_header(COL3_X, y, COL_W, PILL_H, "CONCLUSION AND FUTURE WORK", VIOLET_STOPS)
y2 = y + PILL_H + PAD  # = 525
card_panel(COL3_X, y2, COL_W, Mm(58), CARD_TINT["violet"], VIOLET_DK)
add_bullets(COL3_X + Mm(10), y2 + Mm(8), COL_W - Mm(16), Mm(48), [
    "A verified, specialised, orchestrator-coordinated adaptive interview system pairing RL-based difficulty control with a resistance-hardened evaluator.",
    "RL/guardrail evidence is simulation-only; no human-subject usability study yet.",
    "Future work: resolve guardrail divergence, run a preregistered human study, measure real speech word-error-rate.",
], size=16.5, bullet_color=VIOLET_DK, space_after=Pt(8))

prs.save(OUT_PPTX)
print("Saved vibrant poster:", OUT_PPTX)
