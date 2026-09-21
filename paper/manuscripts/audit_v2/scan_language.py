"""Phase 10 (claim language) and Phase 11 (statistics language) scans on the manuscript bodies (read-only).
Bodies exclude HTML comments and the reference list. Prints counts and contexts for manual disposition."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = r"C:\Users\spars\Downloads\PrepAIred\paper\manuscripts"
PAPERS = {"P1": "paper1", "P2": "paper2", "P3": "paper3"}
LANG = ["secure", "security guarantee", "fault-tolerant", "fault tolerant", "universally contained", "prompt-injection-proof",
        "cannot affect scoring", "validated", "reliable", "human-level", "fair", "fairness", "unbiased", "generalizable",
        "state-of-the-art", "best", "first", "novel", "novelty", "formal shield", "safety shield", "shield", "negative equivalence",
        "expert panel", "gold standard", "blinded", "independent raters", "failure-aware", "measurement validity", "robust", "superior",
        "gold", "committee", "guarantee", "safe", "safer", "proves", "proven", "outperform", "human-like"]
STAT = ["significant", "significance", "p =", "CI", "confidence", "equivalent", "superior", "outperformed", "better", "worse",
        "bias", "correlation", "agreement", "reliability"]
mode = sys.argv[1] if len(sys.argv) > 1 else "lang"
terms = LANG if mode == "lang" else STAT
ctxw = 55
for tag, d in PAPERS.items():
    t = open(f"{BASE}\\{d}\\manuscript.md", encoding="utf-8").read()
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S).split("## References")[0]
    print(f"===== {tag} =====")
    for term in terms:
        pat = re.compile(r"(?<![A-Za-z])" + re.escape(term) + (r"" if term.endswith("=") else r"(?![A-Za-z])"), re.I if mode == "lang" else 0)
        hits = list(pat.finditer(t))
        if not hits:
            continue
        print(f"-- {term}: {len(hits)}")
        if mode == "lang" or len(hits) <= 6:
            for m in hits:
                s = t[max(0, m.start() - ctxw): m.end() + ctxw].replace("\n", " ")
                print(f"     ...{s}...")
