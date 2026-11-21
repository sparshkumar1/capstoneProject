"""
Converts the IEEE paper draft (Markdown) into a two-column .docx formatted to
approximate the IEEE conference template conventions: Times New Roman, two
columns for the body, single-column title/abstract block, 10pt body text
(standard IEEE conference size), centered title, author block, bold section
headings in Roman numerals style already present in the source text.

This approximates the official IEEE Conference-template-A4.doc layout
(two-column, Times New Roman) since that exact .doc template was not
available as a file to populate directly in this session; the official
template should still be used for final camera-ready formatting if an exact
byte-for-byte match to IEEE's own template is required for submission.

Run: .venv/Scripts/python.exe testing_and_evaluation/scripts/md_to_docx_ieee_paper.py
"""
import re
import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "final_deliverables" / "03_Research_Paper" / "PrepAIred_IEEE_Paper_Draft.md"
OUT_PATH = ROOT / "final_deliverables" / "03_Research_Paper" / "PrepAIred_IEEE_Paper_Draft.docx"

FONT = "Times New Roman"


def set_two_columns(section, num=2, space_cm=0.5):
    sectPr = section._sectPr
    cols = sectPr.find(qn("w:cols"))
    if cols is None:
        cols = OxmlElement("w:cols")
        sectPr.append(cols)
    cols.set(qn("w:num"), str(num))
    cols.set(qn("w:space"), str(int(space_cm * 567)))  # cm -> twentieths of a point approx


def style_normal(doc):
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(10)
    rpr = normal.element.get_or_add_rPr()
    rFonts = rpr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rFonts)
    rFonts.set(qn("w:ascii"), FONT)
    rFonts.set(qn("w:hAnsi"), FONT)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.0


INLINE_PATTERN = re.compile(r"(\*\*.+?\*\*|\*.+?\*|`.+?`)")


def add_para(doc, text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=10, bold=False, italic=False, bullet=False):
    p = doc.add_paragraph(style="List Bullet" if bullet else None)
    if not bullet:
        p.alignment = align
    parts = INLINE_PATTERN.split(text) if text else [""]
    for part in parts:
        if not part:
            continue
        b, i_, content = bold, italic, part
        if part.startswith("**") and part.endswith("**"):
            b, content = True, part[2:-2]
        elif part.startswith("*") and part.endswith("*"):
            i_, content = True, part[1:-1]
        elif part.startswith("`") and part.endswith("`"):
            content = part[1:-1]
        run = p.add_run(content)
        run.font.name = FONT
        run.font.size = Pt(size)
        run.bold = b
        run.italic = i_
    return p


def main() -> int:
    text = SRC.read_text(encoding="utf-8")
    lines = text.split("\n")

    doc = Document()
    style_normal(doc)
    section = doc.sections[0]
    section.left_margin = Cm(1.75)
    section.right_margin = Cm(1.75)
    section.top_margin = Cm(1.9)
    section.bottom_margin = Cm(1.9)

    i = 0
    title_written = False
    in_two_col = False

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("**Format note:**"):
            # Skip this session-authoring note from the camera-ready output
            i += 1
            continue

        if stripped == "---":
            i += 1
            continue

        if stripped.startswith("# "):
            # Paper title -- single column, large, centered
            p = add_para(doc, stripped[2:], align=WD_ALIGN_PARAGRAPH.CENTER, size=18, bold=True)
            title_written = True
            i += 1
            continue

        if stripped.startswith("**Authors:**") or stripped.startswith("**Affiliation:**"):
            add_para(doc, stripped, align=WD_ALIGN_PARAGRAPH.CENTER, size=11)
            i += 1
            continue

        if stripped.startswith("## Abstract"):
            add_para(doc, "Abstract", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, bold=True, italic=True)
            i += 1
            continue

        if stripped.startswith("**Index Terms:**"):
            add_para(doc, stripped, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=10, bold=False)
            # Switch to two columns right after Index Terms, standard IEEE layout
            if not in_two_col:
                # Insert a section break to start two-column layout from here
                new_section = doc.add_section()
                new_section.left_margin = Cm(1.75)
                new_section.right_margin = Cm(1.75)
                new_section.top_margin = Cm(1.9)
                new_section.bottom_margin = Cm(1.9)
                set_two_columns(new_section, num=2)
                in_two_col = True
            i += 1
            continue

        if stripped.startswith("## "):
            add_para(doc, stripped[3:], align=WD_ALIGN_PARAGRAPH.LEFT, size=11, bold=True)
            i += 1
            continue

        if stripped.startswith("### "):
            add_para(doc, stripped[4:], align=WD_ALIGN_PARAGRAPH.LEFT, size=10, bold=True, italic=True)
            i += 1
            continue

        if stripped.startswith("**Table"):
            add_para(doc, stripped, align=WD_ALIGN_PARAGRAPH.CENTER, size=9, bold=True)
            i += 1
            continue

        if stripped.startswith("|"):
            # simple table block -> render as plain text rows (kept minimal for this draft)
            rows = []
            j = i
            while j < len(lines) and lines[j].strip().startswith("|"):
                line = lines[j].strip()
                if not re.match(r"^\|[\s:|-]+\|$", line):
                    rows.append([c.strip() for c in line.strip("|").split("|")])
                j += 1
            if rows:
                table = doc.add_table(rows=len(rows), cols=len(rows[0]))
                table.style = "Light Grid Accent 1"
                for r, row in enumerate(rows):
                    for c, val in enumerate(row):
                        if c < len(rows[0]):
                            cell = table.cell(r, c)
                            cell.text = ""
                            run = cell.paragraphs[0].add_run(val)
                            run.font.name = FONT
                            run.font.size = Pt(8)
                            run.bold = (r == 0)
            i = j
            continue

        if stripped.startswith("- "):
            add_para(doc, stripped[2:], bullet=True, size=10)
            i += 1
            continue

        if re.match(r"^\[\d+\]", stripped):
            add_para(doc, stripped, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=9)
            i += 1
            continue

        # plain paragraph, join soft-wrapped lines
        para_lines = [stripped]
        j = i + 1
        while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith(("#", "|", "-", "[", "**Table", "---")):
            para_lines.append(lines[j].strip())
            j += 1
        add_para(doc, " ".join(para_lines), size=10)
        i = j

    doc.save(str(OUT_PATH))
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
