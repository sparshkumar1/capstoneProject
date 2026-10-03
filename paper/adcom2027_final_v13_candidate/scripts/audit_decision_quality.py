import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
phrases = [
    "decision quality",
    "quality of decisions",
    "superior decisions",
    "better decisions",
    "optimal decisions",
    "improved decisions",
    "correct decisions",
    "decision correctness",
    "quality"
]

files = sorted(
    list((ROOT / "manuscript").glob("*.tex")) +
    list((ROOT / "tables").glob("*.tex")) +
    list((ROOT / "figures").glob("*.tex"))
)

for p in phrases:
    print(f"=== SEARCH: '{p}' ===")
    matches = []
    regex = re.compile(r"\b" + re.escape(p) + r"\b", re.IGNORECASE)
    for f in files:
        if f.name == "sec_carry.tex":
            continue
        txt = f.read_text(encoding="utf-8", errors="ignore")
        for lno, line in enumerate(txt.splitlines(), 1):
            if regex.search(line):
                matches.append((f.name, lno, line.strip()))
    print(f"Total occurrences: {len(matches)}")
    for fname, lno, line in matches:
        print(f"  [{fname}:{lno}] {line}")
    print()
