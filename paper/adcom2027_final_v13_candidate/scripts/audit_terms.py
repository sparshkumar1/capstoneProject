import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
patterns = [r'15--20', r'15-20', r'human', r'volunteer', r'synthetic', r'production', r'benchmark', r'recorded candidate']
files = sorted(list((ROOT / "manuscript").glob("*.tex")) + list((ROOT / "figures").glob("*.tex")) + list((ROOT / "tables").glob("*.tex")))

for pat in patterns:
    print(f"=== SEARCH: {pat} ===")
    cnt = 0
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        for lno, line in enumerate(text.splitlines(), 1):
            if re.search(pat, line, re.IGNORECASE):
                cnt += 1
                print(f"{f.name}:{lno}: {line.strip()[:140]}")
    print(f"Total occurrences of {pat}: {cnt}\n")
