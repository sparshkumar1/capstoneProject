"""Repository-level originality/overlap scan (read-only). Compares the current manuscripts with the legacy PrepAIred paper and its
archived drafts, and with each other: shared sentences (normalised), shared word n-grams and the longest shared word runs.
It is a text-overlap screen, not a plagiarism verdict; generic technical phrases are expected to match.
Usage: python originality_scan.py [n-gram size, default 8]"""
import re, sys, io, os, subprocess, itertools, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
M = r"C:\Users\spars\Downloads\PrepAIred\paper\manuscripts"
R = r"C:\Users\spars\Downloads\PrepAIred\research\papers\archived\superseded_manuscripts"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 8

def clean(t):
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    t = t.split("## References")[0]                      # bibliography excluded: shared references are expected
    t = re.sub(r"\|.*\|", " ", t)                       # table rows
    t = re.sub(r"[*`#]", "", t)
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)          # PDF hyphenation
    return t

def pdf_text(p):
    out = os.path.join(tempfile.gettempdir(), "legacy_reading_order.txt")
    subprocess.run(["pdftotext", p, out], check=True)
    t = open(out, encoding="utf-8", errors="ignore").read()
    return t.split("REFERENCES")[0] if "REFERENCES" in t else t

corpus = {
    "P1": open(M + r"\venue\ICETC_P1\P1_ICETC_BLINDED.md", encoding="utf-8").read(),
    "P2": open(M + r"\paper2\manuscript.md", encoding="utf-8").read(),
    "P3": open(M + r"\venue\HCII_P3\P3_FULL_MANUSCRIPT_READY.md", encoding="utf-8").read(),
    "P3prop": open(M + r"\venue\HCII_P3\proposal_text.txt", encoding="utf-8").read(),
    "LEG_pdf": pdf_text(R + r"\final_prepaired_ieee_paper.pdf"),
    "LEG_tlt": open(R + r"\IEEE_TLT_MANUSCRIPT.md", encoding="utf-8").read(),
    "LEG_access": open(R + r"\paper_draft_ieee_access.md", encoding="utf-8").read(),
    "LEG_toe": open(R + r"\paper_draft_ieee_toE.md", encoding="utf-8").read(),
}
body = {k: clean(v) for k, v in corpus.items()}
def sents(t):
    t = re.sub(r"\s+", " ", t)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if len(s.split()) >= 8]
def norm(s): return re.sub(r"[^a-z0-9 ]", "", s.lower())
def words(t): return re.findall(r"[a-z0-9\-\.]+", t.lower())
S = {k: {norm(s): s for s in sents(v)} for k, v in body.items()}
W = {k: words(v) for k, v in body.items()}
G = {k: {" ".join(w[i:i + N]) for i in range(len(w) - N + 1)} for k, w in W.items()}

def longest_run(a, b, cap=40):
    """Longest word run shared by word lists a and b (via n-gram anchors), with the run text."""
    idx = {}
    for i in range(len(b) - N + 1): idx.setdefault(tuple(b[i:i + N]), []).append(i)
    best = (0, 0, 0); i = 0
    while i < len(a) - N + 1:
        hit = idx.get(tuple(a[i:i + N]))
        if hit:
            for j in hit:
                k = N
                while i + k < len(a) and j + k < len(b) and a[i + k] == b[j + k]: k += 1
                if k > best[0]: best = (k, i, j)
        i += 1
    k, i, _ = best
    return k, " ".join(a[i:i + min(k, cap)])

cur = ["P1", "P2", "P3", "P3prop"]; leg = [k for k in body if k.startswith("LEG")]
print(f"word counts: { {k: len(W[k]) for k in body} }   (n-gram size {N})\n")
print("=== current manuscripts vs legacy paper and drafts ===")
for c in cur:
    for l in leg:
        dup = set(S[c]) & set(S[l]); sh = G[c] & G[l]
        k, txt = longest_run(W[c], W[l])
        cov = 100.0 * sum(1 for i in range(len(W[c]) - N + 1) if " ".join(W[c][i:i + N]) in G[l]) / max(1, len(W[c]))
        print(f"{c:7s} vs {l:10s}: duplicate sentences {len(dup):2d}; shared {N}-grams {len(sh):3d} ({cov:.1f}% of {c} positions); longest shared run {k} words")
        if k >= 12: print(f"          run: {txt}")
        for d in sorted(dup)[:3]: print(f"          DUP: {S[c][d][:150]}")
print("\n=== current manuscripts vs each other ===")
for a, b in itertools.combinations(["P1", "P2", "P3"], 2):
    dup = set(S[a]) & set(S[b]); sh = G[a] & G[b]; k, txt = longest_run(W[a], W[b])
    print(f"{a} vs {b}: duplicate sentences {len(dup)}; shared {N}-grams {len(sh)}; longest shared run {k} words: {txt[:200]}")
    for d in sorted(dup)[:3]: print(f"          DUP: {S[a][d][:150]}")
print("\n=== proposal vs full paper (expected overlap: same study) ===")
dup = set(S["P3prop"]) & set(S["P3"]); print(f"P3prop vs P3: duplicate sentences {len(dup)}; shared {N}-grams {len(G['P3prop'] & G['P3'])}")
