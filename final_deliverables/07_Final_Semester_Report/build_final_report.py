"""
Converts the 13 Markdown report chapter files into one formatted .docx,
applying the PES University Report-Guidelines.pdf formatting rules:
 - Times New Roman, 1.5 line spacing (body), justified body text
 - Margins: 2.00cm left/right/top/bottom
 - Chapter titles: centered, size 18, bold
 - Section headings: left-justified, size 16, bold
 - Subsection headings: left-justified, size 14, bold
 - Body text: size 12

Handles the subset of Markdown actually used in the source files: #/##/###
headers, **bold**, *italic*, `code`, pipe tables, bullet/numbered lists,
horizontal rules, and blank-line paragraph breaks.

Run: .venv/Scripts/python.exe testing_and_evaluation/scripts/md_to_docx_report.py
"""
import re
import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path(__file__).resolve().parent.parent.parent
REPORT_DIR = ROOT / "final_deliverables" / "07_Final_Semester_Report"
OUT_PATH = ROOT / "final_deliverables" / "07_Final_Semester_Report" / "PrepAIred_Phase3_Final_Report.docx"
LOGO_PATH = REPORT_DIR / "assets" / "pes_logo.png"

FONT = "Times New Roman"
TITLE_FONT = "Arial"

# Front-matter facts. Admin names/roles (coordinator, chairperson, registrar,
# chancellor, vice-chancellor) are taken from the official, current
# Details/Report initial Pages(Pg 1-10)/ template, not from the Phase-2 PDF,
# since those roles can rotate between semesters and the template is the
# authoritative current source. Team/title/guide are carried forward from
# the real Phase-2 submission on the assumption this
# is the same project continuing into Phase-3.
TITLE = "PrepAIred: A Reinforcement-based LLM-powered Interview Preparation System"
STUDENTS = [
    ("Sparsh Kumar", "PES1UG23CS909"),
    ("Naveen S Khadd", "PES1UG23CS924"),
    ("Manasa S A", "PES1UG24CS811"),
    ("Athreya Shashidhara", "PES1UG23CS120"),
]
GUIDE_NAME = "Dr Uma D"
GUIDE_DESIGNATION = "Professor"
COURSE_CODE = "UE23CS441A"
PHASE_LABEL = "Capstone Project Phase - 3"
PROJECT_ID = "PW26_UD05"
DATE_RANGE = "August – Dec, 2026"
SEMESTER_ORDINAL_WORD = "seventh"
SEMESTER_ORDINAL_SUP = "7th"
COORDINATOR = "Dr. Chaitra B"
CHAIRPERSON = "Dr. Shylaja S S"
REGISTRAR = "Dr. Sridhar K S"
CHANCELLOR = "Prof. Jawahar Doreswamy"
VICE_CHANCELLOR = "Dr. Suryaprasad J"

# Corrected against this report's own verified findings (2026-11-19 pass).
# The Phase-2 wording was restored verbatim in an earlier pass per explicit
# user instruction, which knowingly reintroduced three figures Chapter 10 of
# this same report independently finds do not match the verified
# implementation: 500,000 PPO steps (real: 24,576 timesteps/seed x 5 seeds,
# Ch.8 Sec. "Training provenance"; Ch.10 Sec. 10.2/10.12), "seven autonomous
# sub-agents" (real: a single-controller, hub-and-spoke architecture, not a
# multi-agent system -- Ch.1, Ch.5, Ch.10 Sec. 10.13), and "93.3% baseline
# calibration accuracy over 30 sessions" (no stored artifact; real,
# human-correlation evidence: Spearman rho = 0.3812, Ch.10 Sec. 10.12 item 8
# and the "Real evaluator human-correlation evidence" finding). This pass
# replaces all three with the figures this report itself verifies elsewhere,
# so the Abstract no longer contradicts Chapter 8/Chapter 10.
ABSTRACT_TEXT = (
    "Most existing technical interview preparation tools are static. Platforms such as "
    "LeetCode give every candidate the same sequence of questions regardless of how they are "
    "performing, offer no structured feedback, and do not capture any multimodal signal at "
    "all. PrepAIred is our attempt at closing that gap. At its core is a Proximal Policy "
    "Optimisation (PPO) agent, trained for 24,576 timesteps per seed across five seeds, that "
    "adjusts question difficulty based on how the candidate is doing. Answer quality is "
    "scored by a three-component semantic evaluator — Sentence-BERT similarity, FAISS-based "
    "concept coverage, and CrossEncoder reasoning-quality assessment — while a separate "
    "pipeline built on Whisper and Librosa pulls out prosodic signal such as confidence and "
    "hesitation from the candidate's speech. A locally hosted Qwen LLM generates hints and "
    "follow-up questions, and a dedicated FeedbackAgent turns every answer into a structured "
    "fifteen-field report covering misconception detection, concept gaps, and communication "
    "quality. All of this is coordinated by a single central InterviewOrchestrator; there is "
    "no multi-agent negotiation between separate components. Testing across three synthetic "
    "candidate profiles shows the system adapting difficulty correctly and degrading "
    "gracefully in all four critical failure scenarios we tried. Against human judgment, the "
    "composite evaluator reaches a Spearman correlation of ρ = 0.3812 — a moderate result "
    "that we report as exploratory rather than conclusive, since that is what the current "
    "evidence supports."
)

# Chapter No., Title -- used for both the page-break chapter loop and the
# Table of Contents table. Page numbers are filled in afterwards by
# patch_toc_page_numbers.py once real pagination exists.
CHAPTERS = [
    ("1", "INTRODUCTION", "01_Chapter1_Introduction.md"),
    ("2", "PROBLEM DEFINITION", "02_Chapter2_Problem_Definition.md"),
    ("3", "LITERATURE REVIEW", "03_Chapter3_Literature_Review.md"),
    ("4", "PROJECT REQUIREMENTS SPECIFICATION (PRS)", "04_Chapter4_PRS.md"),
    ("5", "HIGH-LEVEL DESIGN (HLD)", "05_Chapter5_HLD.md"),
    ("6", "LOW-LEVEL DESIGN (LLD)", "06_Chapter6_LLD.md"),
    ("7", "SYSTEM DESIGN (DETAILED)", "07_Chapter7_System_Design_Detailed.md"),
    ("8", "PROPOSED METHODOLOGY", "08_Chapter8_Proposed_Methodology.md"),
    ("9", "IMPLEMENTATION AND PSEUDOCODE", "09_Chapter9_Implementation_and_Pseudocode.md"),
    ("10", "EXPERIMENTATION, RESULTS AND DISCUSSION", "10_Chapter10_Experimentation_Results_and_Discussion.md"),
    ("11", "CONCLUSION AND FUTURE WORK", "11_Chapter11_Conclusion_and_Future_Work.md"),
    ("12", "REFERENCES/BIBLIOGRAPHY", "12_Bibliography.md"),
]

FILES_IN_ORDER = [fname for (_, _, fname) in CHAPTERS]

# Figure/table catalog for List of Figures / List of Tables. Each entry's
# `search_text` must exactly match the caption text actually rendered in
# the chapter body (see 05/06/07/08/10_Chapter*.md), so the COM patch pass
# can locate it unambiguously and is not satisfied by its own short-form
# entry in the List of Figures/Tables page itself.
FIGURES = [
    ("5.1", "High-level system architecture: a single orchestrator coordinating "
            "specialised, bounded-authority components (hub-and-spoke, not a "
            "multi-agent topology).",
     "Figure 5.1. High-level system architecture"),
    ("8.1", "Evaluator pipeline: S1/S2/R combined through the weighted formula and "
            "keyword-stuffing defense described above.",
     "Figure 8.1. Evaluator pipeline"),
    ("8.2", "RL decision flow: state vector to PPO policy to guardrail-checked "
            "final action (full guardrail detail: Chapter 6, Section 6.3; Table 6.1).",
     "Figure 8.2. RL decision flow"),
]
TABLES = [
    ("4.1", "Functional requirements."),
    ("4.2", "Non-functional requirements."),
    ("5.1", "Technology stack (verified against code)."),
    ("6.1", "Guardrail rules, in evaluation priority order (verified against "
            "`rl/guardrails.py::apply_canonical_guardrails`)."),
    ("6.2", "FeedbackAgent structured-feedback output fields (representative, "
            "verified against `agents/orchestrator/feedback_agent.py`)."),
    ("7.1", "Graceful-degradation fallback behaviour."),
    ("8.1", "RL state-vector components."),
    ("8.2", "RL action space (verified `Discrete(3)` against "
            "`agents/strategy/hybrid_orchestrator.py`)."),
    ("10.1", "Full automated test suite — baseline and final results."),
    ("10.2", "Code changes made and regression-verified."),
    ("10.3", "New evaluation evidence."),
    ("10.4", "RL/guardrail ablation — difficulty-tracking MAE (five-seed mean)."),
]


def set_doc_defaults(doc: Document) -> None:
    section = doc.sections[0]
    # Rule 1: "A4 size bond paper (210*297)". python-docx's bundled default
    # template defaults to US Letter (21.59x27.94cm) -- must be set explicitly.
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)

    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(12)
    # Ensure east-asian font fallback doesn't override Times New Roman
    rpr = normal.element.get_or_add_rPr()
    rFonts = rpr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rFonts)
    rFonts.set(qn("w:ascii"), FONT)
    rFonts.set(qn("w:hAnsi"), FONT)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


# ---------------------------------------------------------------------------
# Front matter: a bespoke, structure-faithful reproduction of
# Details/Report initial Pages(Pg 1-10)/*.docx (the official blank template)
# with Phase-3 data filled in, instead of running the generic Markdown
# converter over 00_Front_Matter.md. The generic converter cannot express
# this page's requirements (Arial front-page font, borderless roster/
# signature tables, a real page break between each of Title/Certificate/
# Declaration/Acknowledgement/Abstract/ToC/LoF/LoT, a centered institutional
# heading size) -- which is why the previous build looked wrong.
# ---------------------------------------------------------------------------

def fm_para(doc, text="", size=12, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.CENTER,
            space_before=0, space_after=0, font=TITLE_FONT):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.0
    if text:
        run = p.add_run(text)
        run.font.name = font
        run.font.size = Pt(size)
        run.bold = bold
        run.italic = italic
    return p


def fm_runs(doc, parts, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, font=TITLE_FONT,
            space_before=0, space_after=0, line_spacing=1.5):
    """parts: list of (text, bold) tuples rendered as one paragraph, several runs."""
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    for text, bold in parts:
        run = p.add_run(text)
        run.font.name = font
        run.font.size = Pt(size)
        run.bold = bold
    return p


def _no_borders(table) -> None:
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "nil")
        borders.append(el)
    tbl_pr.append(borders)


def borderless_table(doc, rows, col_widths_cm=None, size=12, bold=True,
                      font=TITLE_FONT, cell_align=WD_ALIGN_PARAGRAPH.LEFT,
                      table_width_cm=14):
    n_cols = len(rows[0])
    table = doc.add_table(rows=len(rows), cols=n_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    _no_borders(table)
    widths = col_widths_cm or [table_width_cm / n_cols] * n_cols
    for r, row in enumerate(rows):
        for c, cell_text in enumerate(row):
            cell = table.cell(r, c)
            cell.width = Cm(widths[c])
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = cell_align
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            lines = str(cell_text).split("\n")
            for li, line in enumerate(lines):
                if li > 0:
                    p.add_run().add_break()
                run = p.add_run(line)
                run.font.name = font
                run.font.size = Pt(size)
                run.bold = bold
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_logo(doc) -> None:
    if LOGO_PATH.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(LOGO_PATH), width=Cm(4.0))


def add_front_matter(doc: Document) -> None:
    title_q = f"“{TITLE}”"
    title_sq = f"‘{TITLE}’"
    roster = [(name, srn) for (name, srn) in STUDENTS]

    # ---- Title page -------------------------------------------------
    add_logo(doc)
    fm_para(doc, "Dissertation on", size=16, bold=True, italic=True, space_before=6, space_after=6)
    fm_para(doc, title_q, size=16, bold=True, space_after=10)
    fm_para(doc, "Submitted in partial fulfilment of the requirements for the award of degree of",
            size=12, italic=True, space_after=8)
    fm_para(doc, "Bachelor of Technology", size=16, bold=True, space_after=2)
    fm_para(doc, "in", size=16, bold=True, space_after=2)
    fm_para(doc, "Computer Science & Engineering", size=16, bold=True, space_after=6)
    fm_para(doc, f"{COURSE_CODE} – {PHASE_LABEL}", size=16, bold=True, space_after=6)
    fm_para(doc, f"Project_ID: {PROJECT_ID}", size=14, bold=True, space_after=10)
    fm_para(doc, "Submitted by:", size=12, bold=True, italic=True, space_after=8)
    borderless_table(doc, roster, col_widths_cm=[8, 6], size=12, bold=True,
                      cell_align=WD_ALIGN_PARAGRAPH.LEFT, table_width_cm=14)
    fm_para(doc, "Under the guidance of", size=12, italic=True, space_before=10, space_after=6)
    fm_para(doc, GUIDE_NAME, size=14, bold=True, space_after=2)
    fm_para(doc, GUIDE_DESIGNATION, size=12, space_after=12)
    fm_para(doc, DATE_RANGE, size=12, bold=True, space_after=16)
    fm_para(doc, "DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", size=12, bold=True, space_after=2)
    fm_para(doc, "FACULTY OF ENGINEERING  PES UNIVERSITY", size=12, space_after=6)
    fm_para(doc, "(Established under Karnataka Act No. 16 of 2013)", size=10, space_after=0)
    fm_para(doc, "100ft Ring Road, Bengaluru – 560 085, Karnataka, India", size=10, space_after=0)
    doc.add_page_break()

    # ---- Certificate page --------------------------------------------
    add_logo(doc)
    fm_para(doc, "PES UNIVERSITY", size=16, bold=True, space_after=2)
    fm_para(doc, "(Established under Karnataka Act No. 16 of 2013)", size=10, space_after=0)
    fm_para(doc, "100 Feet Ring Road, Bengaluru – 560 085, Karnataka, India", size=10, space_after=4)
    fm_para(doc, "FACULTY OF ENGINEERING", size=12, bold=True, space_after=6)
    fm_para(doc, "CERTIFICATE", size=20, bold=True, space_after=8)
    fm_para(doc, "This is to certify that the dissertation entitled", size=12, italic=True, space_after=4)
    fm_para(doc, title_sq, size=14, bold=True, space_after=4)
    fm_para(doc, "is a bonafide work carried out by", size=12, italic=True, space_after=8)
    borderless_table(doc, roster, col_widths_cm=[8, 6], size=12, bold=True,
                      cell_align=WD_ALIGN_PARAGRAPH.LEFT, table_width_cm=14)
    fm_runs(doc, [
        (f"in partial fulfilment for the completion of {SEMESTER_ORDINAL_WORD} semester "
         f"{PHASE_LABEL} ({COURSE_CODE}) in the Program of Study - ", False),
        ("Bachelor of Technology", True), (" in ", False),
        ("Computer Science and Engineering", True),
        (" under rules and regulations of PES University, Bengaluru during the period ", False),
        (DATE_RANGE, False),
        (". It is certified that all corrections / suggestions indicated for internal assessment "
         "have been incorporated in the report. The dissertation has been approved as it "
         f"satisfies the {SEMESTER_ORDINAL_SUP} semester academic requirements in respect of "
         "project work.", False),
    ], size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=6)
    borderless_table(doc, [
        ["Signature", "Signature", "Signature"],
        [GUIDE_NAME, CHAIRPERSON, REGISTRAR],
        [GUIDE_DESIGNATION, "Chairperson", "Registrar"],
    ], col_widths_cm=[4.6, 4.7, 4.7], size=12, bold=True,
       cell_align=WD_ALIGN_PARAGRAPH.CENTER, table_width_cm=14)
    fm_para(doc, "External Viva", size=12, bold=True, space_before=4, space_after=4)
    borderless_table(doc, [
        ["Name of the Examiners\n1. ____________________\n2. ____________________",
         "Signature with Date\n____________________\n____________________"],
    ], col_widths_cm=[8, 6], size=11, bold=False, cell_align=WD_ALIGN_PARAGRAPH.LEFT,
       table_width_cm=14)
    doc.add_page_break()

    # ---- Declaration page ---------------------------------------------
    fm_para(doc, "DECLARATION", size=16, bold=True, space_before=6, space_after=16)
    fm_runs(doc, [
        (f"We hereby declare that the {PHASE_LABEL} entitled ", False),
        (title_q, True),
        (" has been carried out by us under the guidance of ", False),
        (f"{GUIDE_NAME}, {GUIDE_DESIGNATION}", False),
        (" and submitted in partial fulfilment of the course requirements for the award of "
         "degree of ", False),
        ("Bachelor of Technology", True), (" in ", False),
        ("Computer Science and Engineering", True), (" of ", False),
        ("PES University, Bengaluru", True),
        (f" during the academic semester {DATE_RANGE}. The matter embodied in this report has "
         "not been submitted to any other university or institution for the award of any "
         "degree.", False),
    ], size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=20)
    borderless_table(doc, [[srn, name, ""] for (name, srn) in roster],
                      col_widths_cm=[5, 6, 3], size=12, bold=True,
                      cell_align=WD_ALIGN_PARAGRAPH.LEFT, table_width_cm=14)
    doc.add_page_break()

    # ---- Acknowledgement page -------------------------------------------
    fm_para(doc, "ACKNOWLEDGEMENT", size=16, bold=True, space_before=6, space_after=16)
    fm_runs(doc, [
        ("I would like to express my gratitude to Prof. ", False), (GUIDE_NAME, True),
        (", Department of Computer Science and Engineering, PES University, for his/her "
         f"continuous guidance, assistance, and encouragement throughout the development of "
         f"this {COURSE_CODE} - {PHASE_LABEL}.", False),
    ], size=12, space_after=10)
    fm_runs(doc, [
        ("I am grateful to the project coordinator, ", False), (COORDINATOR, True),
        (", for organizing, managing, and helping with the entire process.", False),
    ], size=12, space_after=10)
    fm_runs(doc, [
        ("I take this opportunity to thank ", False), (CHAIRPERSON, True),
        (", Chairperson, Department of Computer Science and Engineering, PES University, for "
         "all the knowledge and support I have received from the department. I would like to "
         "thank ", False), (REGISTRAR, True),
        (", Registrar, PES University for his help.", False),
    ], size=12, space_after=10)
    fm_runs(doc, [
        ("I am deeply grateful to ", False), (f"{CHANCELLOR}, Chancellor – PES University, "
         f"{VICE_CHANCELLOR}, Vice-Chancellor, PES University", True),
        (" for providing to me various opportunities and enlightenment every step of the way. "
         "Finally, this project could not have been completed without the continual support "
         "and encouragement I have received from my family and friends.", False),
    ], size=12, space_after=0)
    doc.add_page_break()

    # ---- Abstract page -----------------------------------------------
    fm_para(doc, "ABSTRACT", size=16, bold=True, space_before=6, space_after=16)
    fm_runs(doc, [(ABSTRACT_TEXT, False)], size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    doc.add_page_break()

    # ---- Table of Contents ---------------------------------------------
    fm_para(doc, "TABLE OF CONTENTS", size=16, bold=True, space_before=6, space_after=16)
    # Page-No. placeholders are zero-padded and prefixed uniquely
    # (TOCPAGE01..TOCPAGE12) so a later whole-document Find/Replace pass
    # can't match "TOCPAGE1" as a substring of "TOCPAGE10"/"11"/"12".
    toc_rows = [["Chapter No.", "Title", "Page No."]]
    for num, title, _fname in CHAPTERS:
        toc_rows.append([num, title, f"TOCPAGE{int(num):02d}"])
    toc_table = doc.add_table(rows=len(toc_rows), cols=3)
    toc_table.style = "Table Grid"
    toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    widths = [2.5, 9.5, 2.5]
    for r, row in enumerate(toc_rows):
        for c, text in enumerate(row):
            cell = toc_table.cell(r, c)
            cell.width = Cm(widths[c])
            # cell.text = "" (python-docx's own clearing idiom) leaves a
            # stray empty run behind; add_run() on top of it then produces
            # TWO runs in the cell, so a later run[0]-only patch misses the
            # second run. Clear the cell's paragraph runs directly instead.
            p = cell.paragraphs[0]
            for r_el in list(p.runs):
                r_el._element.getparent().remove(r_el._element)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c != 1 else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(text)
            run.font.name = TITLE_FONT
            run.font.size = Pt(11)
            run.bold = (r == 0)
    doc.add_page_break()

    # ---- List of Figures / List of Tables -------------------------------
    def grid_table(rows, col_widths, num_col_idx):
        t = doc.add_table(rows=len(rows), cols=len(col_widths))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for r, row in enumerate(rows):
            for c, text in enumerate(row):
                cell = t.cell(r, c)
                cell.width = Cm(col_widths[c])
                p = cell.paragraphs[0]
                for r_el in list(p.runs):
                    r_el._element.getparent().remove(r_el._element)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c == num_col_idx or r == 0 else WD_ALIGN_PARAGRAPH.LEFT
                run = p.add_run(text)
                run.font.name = TITLE_FONT
                run.font.size = Pt(10.5)
                run.bold = (r == 0)
        return t

    fm_para(doc, "LIST OF FIGURES", size=16, bold=True, space_before=6, space_after=16)
    lof_rows = [["Figure No.", "Description", "Page No."]]
    for idx, (num, _desc, _search) in enumerate(FIGURES, start=1):
        lof_rows.append([f"Figure {num}", _desc, f"LOFIDX{idx:02d}"])
    grid_table(lof_rows, [2.5, 9.5, 2.5], num_col_idx=2)
    doc.add_page_break()

    fm_para(doc, "LIST OF TABLES", size=16, bold=True, space_before=6, space_after=16)
    lot_rows = [["Table No.", "Title", "Page No."]]
    for idx, (num, title) in enumerate(TABLES, start=1):
        lot_rows.append([f"Table {num}", title, f"LOTIDX{idx:02d}"])
    grid_table(lot_rows, [2.5, 9.5, 2.5], num_col_idx=2)

    doc.add_section(WD_SECTION.NEW_PAGE)


def _add_page_field(paragraph) -> None:
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(fld_end)
    run.font.name = FONT
    run.font.size = Pt(10)


def _fill_footer(footer, section) -> None:
    """Rule 20: 'Footer -- Left side write Dept of CSE, Middle write Aug -
    Dec 2021 [i.e. the semester date range], Right side write page
    number.' -- a genuine three-way split, not page-number-on-its-own-line
    as an earlier version of this build had it."""
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.text = ""
    page_width = section.page_width - section.left_margin - section.right_margin
    tab_stops = p.paragraph_format.tab_stops
    tab_stops.add_tab_stop(int(page_width / 2), WD_ALIGN_PARAGRAPH.CENTER)
    tab_stops.add_tab_stop(int(page_width), WD_ALIGN_PARAGRAPH.RIGHT)
    run_l = p.add_run("Dept of CSE")
    run_l.font.name = FONT
    run_l.font.size = Pt(10)
    p.add_run("\t")
    run_c = p.add_run(DATE_RANGE.replace("–", "-"))
    run_c.font.name = FONT
    run_c.font.size = Pt(10)
    p.add_run("\t")
    _add_page_field(p)


def _fill_header(header, section) -> None:
    """Rule 20: 'Header -- Left side project title, Right side Institution
    logo.'"""
    header.is_linked_to_previous = False
    p = header.paragraphs[0]
    p.text = ""
    page_width = section.page_width - section.left_margin - section.right_margin
    p.paragraph_format.tab_stops.add_tab_stop(page_width, WD_ALIGN_PARAGRAPH.RIGHT)
    run_l = p.add_run(TITLE)
    run_l.font.name = FONT
    run_l.font.size = Pt(9)
    run_l.italic = True
    p.add_run("\t")
    if LOGO_PATH.exists():
        p.add_run().add_picture(str(LOGO_PATH), height=Cm(0.9))


def configure_chapter_section(section, is_first_chapter: bool) -> None:
    """Rule 21: 'The beginning page of the chapter should not have header,
    but it should have only footer. Header and Footer should start from
    Introduction chapter.' Implemented with Word's per-section
    'different first page' header/footer: the chapter-opening page uses
    first_page_header (left empty) / first_page_footer (filled); every
    later page in that same chapter uses header/footer (both filled).
    One Word section per chapter is required for this, since 'different
    first page' is a section-level, not a page-level, setting."""
    # Rule 1: A4, not the python-docx default of US Letter -- set explicitly
    # on every per-chapter section too, since add_section() does not reliably
    # carry page_width/page_height forward the way it does margins.
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.different_first_page_header_footer = True
    # Correction 5: the header sat almost flush against the top margin (the
    # default header_distance left only ~0.25cm before body text began,
    # reading as congested). Pulling the header frame itself up, closer to
    # the page edge, opens a genuine visual gap before the body text starts
    # at the unchanged 2.00cm top margin -- a header-distance/section
    # setting, not an inserted blank paragraph.
    section.header_distance = Cm(1.0)

    section.first_page_header.is_linked_to_previous = False
    section.first_page_header.paragraphs[0].text = ""
    _fill_footer(section.first_page_footer, section)
    _fill_header(section.header, section)
    _fill_footer(section.footer, section)

    # Bug fix: doc.add_section() clones the PRECEDING section's sectPr as its
    # starting point, so every chapter after Chapter 1 was inheriting a
    # literal copy of Chapter 1's "<w:pgNumType w:start=1>" element -- making
    # every chapter's footer restart at page 1 instead of continuing the
    # document's true page count (which the TOC/LOF/LOT page numbers, filled
    # in separately by patch_toc_page_numbers.py, correctly use). Strip any
    # inherited pgNumType from every chapter but the first so the OOXML
    # default (continue numbering from the previous section) applies.
    if not is_first_chapter:
        sect_pr = section._sectPr
        for el in sect_pr.findall(qn("w:pgNumType")):
            sect_pr.remove(el)

    if is_first_chapter:
        sect_pr = section._sectPr
        pg_num_type = OxmlElement("w:pgNumType")
        pg_num_type.set(qn("w:start"), "1")
        sect_pr.append(pg_num_type)


def add_heading(doc: Document, text: str, level: int) -> None:
    """level 1 = chapter (18pt centered), 2 = section (16pt left), 3 = subsection (14pt left)."""
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = FONT
    run.font.bold = True
    if level == 1:
        run.font.size = Pt(18)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(12)
    elif level == 2:
        run.font.size = Pt(16)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(8)
    else:
        run.font.size = Pt(14)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.0
    # Structuring fix: a heading was free to land as the last line on a
    # page, with its own section's body text starting fresh on the next
    # page -- a heading stranded from its content. keep_with_next glues a
    # heading to the paragraph immediately after it (not the whole section,
    # which keeps flowing normally across the page break beyond that first
    # paragraph), so Word pushes the heading itself down to join that
    # paragraph instead of leaving it orphaned.
    p.paragraph_format.keep_with_next = True


INLINE_PATTERN = re.compile(r"(\*\*.+?\*\*|\*.+?\*|`.+?`)")


def add_inline_runs(p, text: str, size: int = 12, bold_base: bool = False) -> None:
    """Parse **bold**/*italic*/`code` markdown inside a run of text and emit
    real Word formatting for each span, instead of leaving the literal
    asterisks/backticks in the rendered output. Shared by body paragraphs
    and table cells, which otherwise diverged (table cells used to insert
    the raw markdown-marked-up text verbatim)."""
    parts = INLINE_PATTERN.split(text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = p.add_run(part[2:-2])
            run.bold = True
        elif part.startswith("*") and part.endswith("*") and not part.startswith("**"):
            run = p.add_run(part[1:-1])
            run.italic = True
            run.bold = bold_base
        elif part.startswith("`") and part.endswith("`"):
            run = p.add_run(part[1:-1])
            run.font.name = "Consolas"
            run.bold = bold_base
        else:
            run = p.add_run(part)
            run.bold = bold_base
        run.font.name = FONT if not (part.startswith("`") and part.endswith("`")) else "Consolas"
        run.font.size = Pt(size)


def add_body_paragraph(doc: Document, text: str, bullet: bool = False, numbered: bool = False, number: int | None = None):
    style = "List Bullet" if bullet else None
    p = doc.add_paragraph(style=style)
    if numbered and number is not None:
        # Use a literal "N. " prefix instead of Word's "List Number" style,
        # which shares ONE counter across the whole document and does not
        # restart per logical list -- it was producing "5. 6. 7." instead of
        # "1. 2. 3." for every numbered list after the first one in the doc.
        text = f"{number}. {text}"
        p.paragraph_format.left_indent = Cm(0.63)
        p.paragraph_format.first_line_indent = Cm(-0.63)
    if not bullet and not numbered:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    add_inline_runs(p, text, size=12)
    return p


def add_equation(doc: Document, formula: str, number: str) -> None:
    """Rule 15: 'Important equations must be numbered in decimal form.'
    Renders a formula on its own line, centered, with its "(n)" label
    right-aligned on the same line -- the standard report/paper convention
    the guideline's own example ("Q = C.A.2 .........") follows -- instead
    of leaving the formula inline inside a prose sentence."""
    section = doc.sections[-1]
    page_width = section.page_width - section.left_margin - section.right_margin
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.0
    tab_stops = p.paragraph_format.tab_stops
    tab_stops.add_tab_stop(int(page_width / 2), WD_ALIGN_PARAGRAPH.CENTER)
    tab_stops.add_tab_stop(int(page_width), WD_ALIGN_PARAGRAPH.RIGHT)
    run = p.add_run("\t" + formula)
    run.font.name = FONT
    run.font.size = Pt(12)
    run.italic = True
    if number:
        label = p.add_run(f"\t({number})")
        label.font.name = FONT
        label.font.size = Pt(12)


def add_code_block(doc: Document, code_lines: list[str]) -> None:
    """Render a fenced ```...``` code block as monospace paragraphs, one per
    source line, preserving leading whitespace/indentation, left-aligned
    (not justified), with a light shaded background -- instead of letting
    the normal paragraph-joining logic flatten it into run-on prose."""
    for line in code_lines:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        # Preserve leading spaces by converting them to non-breaking spaces,
        # since Word paragraphs collapse/ignore plain leading whitespace runs.
        stripped_len = len(line) - len(line.lstrip(" "))
        content = " " * stripped_len + line[stripped_len:]
        run = p.add_run(content if content else " ")
        run.font.name = "Consolas"
        run.font.size = Pt(9.5)
        # Shade the paragraph for a code-block visual distinction.
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), "F2F2F2")
        pPr.append(shd)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def _row_cant_split(row) -> None:
    """Prevent a single row's content from being divided across a page
    break (a row with wrapped text could otherwise split mid-cell)."""
    trPr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    trPr.append(cant_split)


def _row_repeat_as_header(row) -> None:
    """Mark a row to repeat at the top of each page the table continues
    onto (the guideline's 'repeated column headings' requirement for a
    table too large to fit on one page)."""
    trPr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    trPr.append(tbl_header)


TABLE_TEXT_WIDTH_CM = 17.0  # A4 (21.0cm) minus the 2.00cm left/right margins


def _set_table_fixed_layout(table, total_width_cm: float) -> None:
    """Word's default 'autofit to contents' table layout silently overrides
    any column width we set, re-widening whichever column has the longest
    unbroken token. 'fixed' layout makes our computed widths authoritative."""
    tbl_pr = table._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tbl_pr.append(layout)
    tbl_w = OxmlElement("w:tblW")
    tbl_w.set(qn("w:w"), str(int(total_width_cm * 566.93)))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_pr.append(tbl_w)


def _strip_markdown(text: str) -> str:
    return text.replace("**", "").replace("`", "")


CHAR_WIDTH_CM = 0.185   # empirical average glyph width, 10pt Times New Roman
CELL_PADDING_CM = 0.5   # Word's default left+right cell margin, combined


def _compute_col_widths_cm(rows: list[list[str]], total_width_cm: float = TABLE_TEXT_WIDTH_CM,
                            min_cm: float = 1.6) -> list[float]:
    """Correction (table sizing): a column holding one-word entries like
    'Pass'/'Fail' and a column holding full sentences were previously given
    equal width, so the short column sat mostly empty while the long one
    wrapped onto many lines -- inflating row height and how often a table
    needed to be pushed whole onto the next page, leaving a blank gap below
    the preceding content.

    Sizing by a column's single LONGEST CELL (first attempt at this fix)
    over-corrected: one column with a long multi-word sentence (expected to
    wrap across lines -- not a defect) forced every other column down to a
    bare minimum, which then wrapped a short HEADER WORD like "Priority"
    into "Priorit"/"y" -- a worse, more visible defect than the uneven
    columns this was meant to fix.

    The actual distinction that matters: wrapping a multi-word phrase across
    lines looks normal; wrapping a single word in the middle does not. So
    each column's floor is set from its longest SINGLE WORD (an identifier,
    a header, a short value -- whatever cannot be broken without looking
    broken), and only the leftover width is handed out -- proportional to
    each column's total text volume -- to let genuinely text-heavy columns
    (e.g. a "Condition" column of boolean expressions) claim the extra room
    instead of sitting artificially narrow."""
    n_cols = len(rows[0])
    longest_word_chars = [0] * n_cols
    total_chars = [0] * n_cols
    for row in rows:
        for c in range(n_cols):
            if c >= len(row):
                continue
            cleaned = _strip_markdown(row[c])
            total_chars[c] += len(cleaned)
            for word in cleaned.split():
                longest_word_chars[c] = max(longest_word_chars[c], len(word))

    floors = [max(w * CHAR_WIDTH_CM + CELL_PADDING_CM, min_cm) for w in longest_word_chars]
    total_floor = sum(floors)

    if total_floor <= total_width_cm:
        extra = total_width_cm - total_floor
        total_weight = sum(total_chars) or 1
        return [f + extra * (total_chars[c] / total_weight) for c, f in enumerate(floors)]

    # Pathological case: even every column's no-mid-word-break minimum
    # doesn't fit (e.g. many columns of long identifiers). Scale every
    # floor down proportionally rather than let the table exceed the page.
    scale = total_width_cm / total_floor
    return [f * scale for f in floors]


def add_table(doc: Document, rows: list[list[str]]) -> None:
    if not rows:
        return
    n_cols = len(rows[0])
    table = doc.add_table(rows=len(rows), cols=n_cols)
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    _set_table_fixed_layout(table, TABLE_TEXT_WIDTH_CM)
    col_widths_cm = _compute_col_widths_cm(rows)
    for c, w in enumerate(col_widths_cm):
        table.columns[c].width = Cm(w)
    n_rows = len(rows)
    for r, row in enumerate(rows):
        for c, cell_text in enumerate(row):
            if c >= n_cols:
                continue
            cell = table.cell(r, c)
            cell.width = Cm(col_widths_cm[c])
            cell.text = ""
            p = cell.paragraphs[0]
            # Correction 4: table cells previously got the raw markdown
            # text verbatim, so a "**bold**" cell rendered as literal
            # asterisks instead of bold. Run it through the same inline
            # markdown parser body paragraphs use.
            add_inline_runs(p, cell_text.strip(), size=10, bold_base=(r == 0))
            # Correction 2: chain every row except the last to the row
            # below it via keep-with-next, so Word treats the whole table
            # as one block wherever it still fits on a page, rather than
            # breaking between arbitrary rows. cantSplit stops a tall row's
            # own content from being divided if the table is genuinely too
            # long to fit on a single page.
            if r < n_rows - 1:
                p.paragraph_format.keep_with_next = True
        _row_cant_split(table.rows[r])
    _row_repeat_as_header(table.rows[0])
    doc.add_paragraph().paragraph_format.space_after = Pt(6)


def parse_table_block(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    rows = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        line = lines[i].strip()
        if re.match(r"^\|[\s:|-]+\|$", line):
            i += 1
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
        i += 1
    return rows, i


def convert_file(doc: Document, path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    i = 0
    numbered_list_counter = 0  # resets whenever a non-numbered-list block is emitted

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("!["):
            m = re.match(r"!\[(.*?)\]\((.*?)\)", stripped)
            if m:
                img_path = REPORT_DIR / "assets" / m.group(2)
                if img_path.exists():
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.add_run().add_picture(str(img_path), width=Cm(13.5))
                    # Same structuring fix as headings: the figure's own
                    # "**Figure N.M.**" caption is the very next paragraph
                    # in every chapter file -- keep the image glued to it
                    # rather than letting the image land at the bottom of
                    # one page and its caption start the next.
                    p.paragraph_format.keep_with_next = True
                else:
                    print(f"WARNING: image not found: {img_path}")
            i += 1
            continue

        if stripped.startswith("```"):
            # Fenced code block: collect raw (non-stripped, indentation-preserving)
            # lines until the closing ``` and render as monospace paragraphs,
            # instead of letting the plain-paragraph joiner flatten it.
            code_lines: list[str] = []
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("```"):
                code_lines.append(lines[j])
                j += 1
            add_code_block(doc, code_lines)
            numbered_list_counter = 0
            i = j + 1  # skip the closing ```
            continue

        if stripped == "---":
            doc.add_paragraph()
            numbered_list_counter = 0
            i += 1
            continue
        if stripped.startswith("EQ::"):
            # Rule 15 display-equation marker: "EQ:: <formula> :: <number>"
            body = stripped[4:]
            formula_part, _, number_part = body.rpartition("::")
            add_equation(doc, formula_part.strip(), number_part.strip())
            numbered_list_counter = 0
            i += 1
            continue
        if stripped.startswith("|"):
            rows, next_i = parse_table_block(lines, i)
            add_table(doc, rows)
            numbered_list_counter = 0
            i = next_i
            continue
        if stripped.startswith("### "):
            add_heading(doc, stripped[4:], 3)
            numbered_list_counter = 0
            i += 1
            continue
        if stripped.startswith("## "):
            add_heading(doc, stripped[3:], 2)
            numbered_list_counter = 0
            i += 1
            continue
        if stripped.startswith("# "):
            add_heading(doc, stripped[2:], 1)
            numbered_list_counter = 0
            i += 1
            continue
        if stripped.startswith("- ") or stripped.startswith("* "):
            add_body_paragraph(doc, stripped[2:], bullet=True)
            numbered_list_counter = 0
            i += 1
            continue
        if re.match(r"^\d+\.\s", stripped):
            numbered_list_counter += 1
            add_body_paragraph(doc, re.sub(r"^\d+\.\s", "", stripped), numbered=True, number=numbered_list_counter)
            i += 1
            continue
        # Plain paragraph (join soft-wrapped lines until blank line)
        para_lines = [stripped]
        j = i + 1
        while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith(("#", "|", "-", "*", "---", "```")) and not re.match(r"^\d+\.\s", lines[j].strip()):
            para_lines.append(lines[j].strip())
            j += 1
        joined = " ".join(para_lines)
        p = add_body_paragraph(doc, joined)
        # Correction 2: a "**Table N.M.** ..." caption line is immediately
        # followed by the pipe-table it describes in every chapter file --
        # keep it glued to that table rather than letting a page break
        # land between the caption and the table it names.
        if re.match(r"^\*\*Table \d", joined):
            p.paragraph_format.keep_with_next = True
        numbered_list_counter = 0
        i = j


def main() -> int:
    doc = Document()
    set_doc_defaults(doc)

    # add_front_matter() ends by opening the section Chapter 1 occupies.
    # Each subsequent chapter gets its OWN section (rather than just a
    # page break), because "different first page" header/footer -- needed
    # to satisfy rule 21 (no header on a chapter's opening page, footer
    # only) -- is a per-SECTION setting in Word, not a per-page one.
    add_front_matter(doc)

    for idx, fname in enumerate(FILES_IN_ORDER):
        path = REPORT_DIR / fname
        if not path.exists():
            print(f"WARNING: missing {path}, skipping")
            continue
        configure_chapter_section(doc.sections[-1], is_first_chapter=(idx == 0))
        convert_file(doc, path)
        if idx < len(FILES_IN_ORDER) - 1:
            doc.add_section(WD_SECTION.NEW_PAGE)

    doc.save(str(OUT_PATH))
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
