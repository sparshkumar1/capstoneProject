"""Double-blind audit of the submission: scans LaTeX sources, bibliography, figures sources, extracted PDF text and PDF metadata
for identifying strings and unfinished-work markers. Exit code 1 if anything is found."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENT = [r"sparsh", r"kumar", r"prepaired4", r"gmail", r"github\.com", r"capstone", r"C:\\Users", r"/home/user", r"/root/",
         r"@[A-Za-z0-9.-]+\.(com|edu|org|in)", r"orcid", r"acknowledg", r"\bour (university|institute|lab)\b", r"PrepAIred", r"PREPAIred"]
MARKERS = [r"\bTODO\b", r"\bFIXME\b", r"PLACEHOLDER", r"\bTBD\b", r"\bDRAFT\b", r"AUTHOR NAME", r"UNIVERSITY", r"\bINTERNAL\b", r"CONFIDENTIAL", r"XXX", r"lorem"]
found = []


def scan(label, text):
    for pat in IDENT + MARKERS:
        for m in re.finditer(pat, text, flags=re.I if pat in IDENT or True else 0):
            # case-sensitive markers: only flag the upper-case forms
            if pat in MARKERS and not m.group(0).isupper() and pat not in (r"lorem",):
                continue
            ctx = text[max(0, m.start() - 30): m.end() + 30].replace("\n", " ")
            found.append((label, pat, ctx))


for p in list((ROOT / "manuscript").glob("*.tex")) + list((ROOT / "manuscript").glob("*.bib")) + list((ROOT / "figures").glob("*.tex")) + list((ROOT / "tables").glob("*.tex")):
    scan(str(p.relative_to(ROOT)), p.read_text(errors="ignore"))
pdf = ROOT / "ADCOM2027_multiagent_blind.pdf"
if pdf.exists():
    txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
    scan("pdf-text", txt)
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    print(info)
    for line in info.splitlines():
        if line.split(":")[0] in ("Author", "Creator", "Producer", "Title", "Subject", "Keywords") and ":" in line:
            val = line.split(":", 1)[1].strip()
            if val:
                print("metadata", line)
    scan("pdf-meta", info)
    fonts = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout
    non_emb = [l for l in fonts.splitlines()[2:] if l.split() and l.split()[-5] == "no"]
    print("fonts not embedded:", len(non_emb))
else:
    print("PDF not built yet")
for f in found:
    print("FOUND", f)
print("blind audit:", "FAIL" if found else "clean", f"({len(found)} hits)")
sys.exit(1 if found else 0)
