import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
terms = [
    "IRB",
    "ethics",
    "institutional review",
    "human participants",
    "consent",
    "exempt",
    "required"
]
files = sorted(
    list((ROOT / "manuscript").glob("*.tex")) +
    list((ROOT / "figures").glob("*.tex")) +
    list((ROOT / "tables").glob("*.tex"))
)

print(f"Auditing {len(files)} files for ethics/IRB terms...\n")

results = {}
for term in terms:
    results[term] = []
    # match case-insensitively, but check word boundaries for precision
    pat = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
    for f in files:
        # Skip carry file if present, but check active files
        lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
        for lno, line in enumerate(lines, 1):
            if pat.search(line):
                results[term].append((f.name, lno, line.strip()))

for term, occurrences in results.items():
    print(f"=== SEARCH: '{term}' (Total: {len(occurrences)}) ===")
    for fname, lno, line in occurrences:
        print(f"  [{fname}:{lno}] {line}")
    print()
