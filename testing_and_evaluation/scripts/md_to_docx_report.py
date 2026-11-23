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
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path(__file__).resolve().parent.parent.parent
REPORT_DIR = ROOT / "final_deliverables" / "02_University_Project_Report"
OUT_PATH = ROOT / "final_deliverables" / "02_University_Project_Report" / "PrepAIred_Phase3_Report.docx"

FONT = "Times New Roman"

FILES_IN_ORDER = [
    "00_Front_Matter.md",
    "01_Chapter1_Introduction.md",
    "02_Chapter2_Problem_Definition.md",
    "03_Chapter3_Literature_Review.md",
    "04_Chapter4_PRS.md",
    "05_Chapter5_HLD.md",
    "06_Chapter6_LLD.md",
    "07_Chapter7_System_Design_Detailed.md",
    "08_Chapter8_Proposed_Methodology.md",
    "09_Chapter9_Implementation_and_Pseudocode.md",
    "10_Chapter10_Experimentation_Results_and_Discussion.md",
    "11_Chapter11_Conclusion_and_Future_Work.md",
    "12_Bibliography.md",
]


def set_doc_defaults(doc: Document) -> None:
    section = doc.sections[0]
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


INLINE_PATTERN = re.compile(r"(\*\*.+?\*\*|\*.+?\*|`.+?`)")


def add_body_paragraph(doc: Document, text: str, bullet: bool = False, numbered: bool = False, number: int | None = None) -> None:
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
        elif part.startswith("`") and part.endswith("`"):
            run = p.add_run(part[1:-1])
            run.font.name = "Consolas"
        else:
            run = p.add_run(part)
        run.font.name = FONT if not (part.startswith("`") and part.endswith("`")) else "Consolas"
        run.font.size = Pt(12)


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


def add_table(doc: Document, rows: list[list[str]]) -> None:
    if not rows:
        return
    n_cols = len(rows[0])
    table = doc.add_table(rows=len(rows), cols=n_cols)
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r, row in enumerate(rows):
        for c, cell_text in enumerate(row):
            if c >= n_cols:
                continue
            cell = table.cell(r, c)
            cell.text = ""
            p = cell.paragraphs[0]
            run = p.add_run(cell_text.strip())
            run.font.name = FONT
            run.font.size = Pt(10)
            if r == 0:
                run.bold = True
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
        add_body_paragraph(doc, " ".join(para_lines))
        numbered_list_counter = 0
        i = j


def main() -> int:
    doc = Document()
    set_doc_defaults(doc)

    for fname in FILES_IN_ORDER:
        path = REPORT_DIR / fname
        if not path.exists():
            print(f"WARNING: missing {path}, skipping")
            continue
        convert_file(doc, path)
        doc.add_page_break()

    doc.save(str(OUT_PATH))
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
