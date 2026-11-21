"""
Replaces the TOCPAGEnn / LOFIDXnn / LOTIDXnn placeholders that
build_final_report.py leaves in the Table of Contents, List of Figures, and
List of Tables with the real page numbers the content landed on, once Word
has actually paginated the document -- something python-docx cannot compute
on its own (it never lays out pages).

Run (Windows, Word installed): .venv/Scripts/python.exe final_deliverables/07_Final_Semester_Report/patch_toc_page_numbers.py
"""
import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent.parent
REPORT_DIR = ROOT / "final_deliverables" / "07_Final_Semester_Report"
DOCX_PATH = REPORT_DIR / "PrepAIred_Phase3_Final_Report.docx"

sys.path.insert(0, str(REPORT_DIR))
from build_final_report import CHAPTERS, FIGURES, TABLES  # noqa: E402

# wdActiveEndAdjustedPageNumber (not wdActiveEndPageNumber=3, the raw/
# absolute physical page count): this one respects the Chapter-1 page-number
# restart (Rule 21 -- "Header and Footer should start from Introduction
# chapter"), so the number it returns is the same one actually printed in
# that page's own footer. Using the raw count here previously made the
# TOC/LOF/LOT say e.g. "page 16" for a page whose own footer said "8".
WD_ACTIVE_END_ADJUSTED_PAGE_NUMBER = 1
WD_FIND_CONTINUE = 1


def find_page_number(doc, text: str) -> int | None:
    rng = doc.Content
    find = rng.Find
    find.ClearFormatting()
    find.Text = text
    find.Forward = True
    find.Wrap = WD_FIND_CONTINUE
    find.MatchWildcards = False
    if find.Execute():
        return rng.Information(WD_ACTIVE_END_ADJUSTED_PAGE_NUMBER)
    return None


def replace_all(doc, old: str, new: str) -> int:
    rng = doc.Content
    find = rng.Find
    find.ClearFormatting()
    find.Replacement.ClearFormatting()
    find.Text = old
    find.Replacement.Text = new
    find.Forward = True
    find.Wrap = WD_FIND_CONTINUE
    find.MatchWildcards = False
    find.Execute(Replace=2)  # wdReplaceAll
    return 1


def main() -> int:
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(str(DOCX_PATH))

        missing = []

        for num, _title, _fname in CHAPTERS:
            heading_text = None
            # Chapter heading text is "Chapter N: <Title>" per the source
            # markdown's own "# " line -- look it up by reading the file
            # rather than reconstructing it from the (upper-cased) CHAPTERS
            # title, which does not match the rendered mixed-case heading.
            md_path = REPORT_DIR / _fname
            first_line = md_path.read_text(encoding="utf-8").splitlines()[0]
            heading_text = first_line.lstrip("# ").strip()
            page = find_page_number(doc, heading_text)
            placeholder = f"TOCPAGE{int(num):02d}"
            if page is None:
                missing.append(placeholder)
                continue
            replace_all(doc, placeholder, str(page))

        for idx, (fig_num, _desc, search_text) in enumerate(FIGURES, start=1):
            page = find_page_number(doc, search_text)
            placeholder = f"LOFIDX{idx:02d}"
            if page is None:
                missing.append(placeholder)
                continue
            replace_all(doc, placeholder, str(page))

        for idx, (tbl_num, title) in enumerate(TABLES, start=1):
            search_text = f"Table {tbl_num}."
            page = find_page_number(doc, search_text)
            placeholder = f"LOTIDX{idx:02d}"
            if page is None:
                missing.append(placeholder)
                continue
            replace_all(doc, placeholder, str(page))

        doc.Save()
        doc.Close(False)

        if missing:
            print("WARNING: could not locate page numbers for:", missing)
        print("Patched TOC / List of Figures / List of Tables page numbers.")
    finally:
        word.Quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
