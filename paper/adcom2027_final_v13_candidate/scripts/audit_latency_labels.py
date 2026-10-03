import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
patterns = [
    ("1.04 ms", r"1\.04\s*(\\?\,)?\s*ms"),
    ("0.55 ms", r"0\.55\s*(\\?\,)?\s*ms"),
    ("1.59 ms", r"1\.59\s*(\\?\,)?\s*ms"),
    ("0.0440", r"0\.0440"),
    ("0.0401", r"0\.0401"),
    ("0.0092", r"0\.0092"),
    ("0.0038", r"0\.0038"),
    ("58.7%", r"58\.7\s*\\?\%"),
    ("schema validation overhead", r"schema\s+validation\s+overhead")
]

files = sorted(
    list((ROOT / "manuscript").glob("*.tex")) +
    list((ROOT / "tables").glob("*.tex")) +
    list((ROOT / "figures").glob("*.tex"))
)

for label, pat in patterns:
    print(f"=== SEARCH: '{label}' (regex: {pat}) ===")
    matches = []
    regex = re.compile(pat, re.IGNORECASE)
    for f in files:
        if f.name == "sec_carry.tex":
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        for lno, line in enumerate(text.splitlines(), 1):
            if regex.search(line):
                matches.append((f.name, lno, line.strip()))
    print(f"Total occurrences: {len(matches)}")
    for fname, lno, line in matches:
        print(f"  [{fname}:{lno}] {line}")
    print()
