import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
terms = [
    "educational computing",
    "educational efficacy",
    "learning outcomes",
    "pedagogical benefit",
    "student improvement",
    "interview performance improvement",
    "learning effectiveness",
    "educational",
    "pedagogical",
    "efficacy",
    "learning"
]

files = sorted(
    list((ROOT / "manuscript").glob("*.tex")) +
    list((ROOT / "tables").glob("*.tex")) +
    list((ROOT / "figures").glob("*.tex"))
)

for t in terms:
    print(f"=== SEARCH: '{t}' ===")
    cnt = 0
    for f in files:
        if f.name == "sec_carry.tex":
            continue
        txt = f.read_text(encoding="utf-8", errors="ignore")
        for lno, l in enumerate(txt.splitlines(), 1):
            if re.search(r"\b" + re.escape(t) + r"\b", l, re.IGNORECASE):
                cnt += 1
                print(f"  [{f.name}:{lno}] {l.strip()[:140]}")
    print(f"Total: {cnt}\n")
