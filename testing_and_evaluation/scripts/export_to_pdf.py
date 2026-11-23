"""
Exports the generated .docx (Word) and .pptx (PowerPoint) deliverables to PDF
using the locally installed Microsoft Office via COM automation, so they can
be genuinely visually inspected (page-by-page) rather than only structurally
verified.

Run: .venv/Scripts/python.exe testing_and_evaluation/scripts/export_to_pdf.py
"""
import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parent.parent.parent

DOCX_JOBS = [
    ROOT / "final_deliverables" / "02_University_Project_Report" / "PrepAIred_Phase3_Report.docx",
    ROOT / "final_deliverables" / "03_Research_Paper" / "PrepAIred_IEEE_Paper_Draft.docx",
]
PPTX_JOBS = [
    ROOT / "final_deliverables" / "04_Final_Presentation" / "PrepAIred_Phase3_Review3.pptx",
]

WORD_PDF_FORMAT = 17  # wdFormatPDF
PPT_PDF_FORMAT = 32   # ppSaveAsPDF


def export_word():
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    try:
        for path in DOCX_JOBS:
            out = path.with_suffix(".pdf")
            doc = word.Documents.Open(str(path))
            doc.SaveAs(str(out), FileFormat=WORD_PDF_FORMAT)
            doc.Close(False)
            print(f"Exported {out}")
    finally:
        word.Quit()


def export_ppt():
    ppt = win32.gencache.EnsureDispatch("PowerPoint.Application")
    try:
        for path in PPTX_JOBS:
            out = path.with_suffix(".pdf")
            pres = ppt.Presentations.Open(str(path), WithWindow=False)
            pres.SaveAs(str(out), PPT_PDF_FORMAT)
            pres.Close()
            print(f"Exported {out}")
    finally:
        try:
            ppt.Quit()
        except Exception:
            pass


def main() -> int:
    export_word()
    export_ppt()
    return 0


if __name__ == "__main__":
    sys.exit(main())
