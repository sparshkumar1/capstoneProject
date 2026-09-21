"""Automated half of the PDF visual-QA gate (the rendered pages must ALSO be inspected by eye; this script does not replace that).

Usage:  PYTHONPATH=<dir with pymupdf> python pdf_qa_check.py <pdf> --mode blinded|master|line|noauthors [--pages N] [--margin PT]

Checks: page count; every text word and image inside the printable area; overlapping words; placeholder / draft-text patterns;
author names (blinded: none allowed anywhere incl. metadata; master: each name exactly once); repeated long lines; metadata and XMP;
raw-byte scan for personal strings. Exit code 1 if any check fails."""
import argparse, re, sys
import pymupdf

AUTHORS = ["Dr. Uma D", "Naveen S Khadd", "Sparsh Kumar", "Athreya Shashidhara", "Manasa S A"]
IDENT = ["Uma", "Khadd", "Sparsh", "Athreya", "Manasa", "PES", "sparshkumar", "spars", "gmail", "pes.edu", "prepaired4", "capstoneProject"]
PLACEHOLDER = re.compile(r"AUTHOR CONFIRMATION|\bTBD\b|\bTODO\b|PLACEHOLDER|INSERT HERE|CHECK THIS|\[VERIFY|\[ADD |\[AI-use|\[CITATION|\[AUTHOR|\bFIXME\b|Claude|ChatGPT|Gemini|Codex|Antigravity", re.I)

ap = argparse.ArgumentParser()
ap.add_argument("pdf"); ap.add_argument("--mode", choices=["blinded", "master", "line", "noauthors"], required=True)
ap.add_argument("--pages", type=int, default=None); ap.add_argument("--margin", type=float, default=30.0)
a = ap.parse_args()

fails = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ((" - " + detail) if detail else ""))
    if not ok: fails.append(name)

d = pymupdf.open(a.pdf)
print("file:", a.pdf, "| pages:", d.page_count)
if a.pages is not None:
    check("page count == %d" % a.pages, d.page_count == a.pages, str(d.page_count))

full = ""
oob, overl, imgs_out = [], [], []
for pn, p in enumerate(d, 1):
    R = p.rect
    words = p.get_text("words")
    full += p.get_text() + "\n"
    for w in words:
        x0, y0, x1, y1, t = w[:5]
        if x0 < a.margin or y0 < a.margin or x1 > R.width - a.margin or y1 > R.height - a.margin:
            oob.append((pn, t, round(x0), round(y0), round(x1), round(y1)))
    # overlapping words (different words whose boxes intersect by > 25% of the smaller box)
    ws = sorted(words, key=lambda w: (w[1], w[0]))
    for i in range(len(ws)):
        for j in range(i + 1, len(ws)):
            if ws[j][1] > ws[i][3]: break
            ax0, ay0, ax1, ay1 = ws[i][:4]; bx0, by0, bx1, by1 = ws[j][:4]
            iw = min(ax1, bx1) - max(ax0, bx0); ih = min(ay1, by1) - max(ay0, by0)
            if iw > 0 and ih > 0 and iw * ih > 0.25 * min((ax1 - ax0) * (ay1 - ay0), (bx1 - bx0) * (by1 - by0)):
                overl.append((pn, ws[i][4], ws[j][4]))
    for img in p.get_image_info():
        b = img["bbox"]
        if b[0] < 0 or b[1] < 0 or b[2] > R.width or b[3] > R.height:
            imgs_out.append((pn, b))
check("all text inside printable area (margin %.0f pt)" % a.margin, not oob, str(oob[:5]))
check("no overlapping words", not overl, str(overl[:5]))
check("images inside page", not imgs_out, str(imgs_out[:3]))

hits = sorted(set(m.group(0) for m in PLACEHOLDER.finditer(full)))
check("no placeholder/draft/AI-tool strings in rendered text", not hits, str(hits))

lines = [l.strip() for l in full.split("\n") if len(l.strip()) >= 60]
dups = sorted(set(l for l in lines if lines.count(l) > 1))
check("no repeated long lines", not dups, str(dups[:3]))

meta = d.metadata; xmp = d.get_xml_metadata() or ""
print("metadata:", {k: v for k, v in meta.items() if v})
raw = open(a.pdf, "rb").read()
if a.mode == "blinded":
    found = [s for s in IDENT if re.search(r"(?<![A-Za-z])" + re.escape(s) + r"(?![A-Za-z])", full, re.I)]
    check("blinded: no author/affiliation/account strings in text", not found, str(found))
    mfound = [s for s in IDENT if re.search(r"(?<![A-Za-z])" + re.escape(s) + r"(?![A-Za-z])", str(meta) + xmp, re.I)]
    check("blinded: no identifying strings in metadata/XMP", not mfound, str(mfound))
    rfound = [s for s in IDENT if re.search(rb"(?<![A-Za-z])" + re.escape(s.encode()) + rb"(?![A-Za-z])", raw, re.I)]
    check("blinded: no identifying strings anywhere in the file bytes", not rfound, str(rfound))
    check("blinded: /Author and /Title empty", not meta.get("author") and not meta.get("title"))
    check("blinded: no personal Windows paths in bytes", b"C:\\Users" not in raw and b"Downloads" not in raw)
elif a.mode == "noauthors":
    check("no author names expected or present", not any(n in full for n in AUTHORS))
    check("no personal Windows paths in bytes", b"C:\\Users" not in raw)
else:
    for n in AUTHORS:
        c = full.count(n)
        check("master: author '%s' appears exactly once" % n, c == 1, "count=%d" % c)
    if a.mode == "master":
        check("master: 'PES University' appears exactly five times (one per author)", full.count("PES University") == 5, str(full.count("PES University")))
    else:
        check("line: 'PES University' appears (single affiliation line)", full.count("PES University") >= 1, str(full.count("PES University")))
    check("master: 'Professor' appears exactly once", full.count("Professor") == 1, str(full.count("Professor")))
    check("master: no personal Windows paths in bytes", b"C:\\Users" not in raw)
    check("master: no e-mail address in text", not re.search(r"[\w.]+@[\w.]+\.\w+", full))

print("RESULT:", "FAIL (" + "; ".join(fails) + ")" if fails else "ALL AUTOMATED CHECKS PASS")
sys.exit(1 if fails else 0)
