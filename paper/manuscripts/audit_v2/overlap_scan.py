"""Cross-paper overlap scan on manuscript bodies (read-only): duplicate sentences, shared 8-word sequences,
shared reference entries (by arXiv id / DOI), and term consistency counts."""
import re, sys, io, itertools
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
B = r"C:\Users\spars\Downloads\PrepAIred\paper\manuscripts"
raw, body, refs = {}, {}, {}
for k in ("paper1", "paper2", "paper3"):
    t = open(f"{B}\\{k}\\manuscript.md", encoding="utf-8").read()
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    b, _, r = t.partition("## References")
    body[k] = b; refs[k] = r
def sents(t):
    t = re.sub(r"\|.*\|", " ", t)
    return [re.sub(r"\s+", " ", s.strip().lower()) for s in re.split(r"(?<=[.!?])\s+", t) if len(s.split()) >= 8]
def grams(t, n=8):
    w = re.findall(r"[a-z0-9\-\.]+", re.sub(r"\|.*\|", " ", t.lower()))
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}
S = {k: set(sents(v)) for k, v in body.items()}
G = {k: grams(v) for k, v in body.items()}
for a, b in itertools.combinations(body, 2):
    dup = S[a] & S[b]; sh = G[a] & G[b]
    print(f"{a}-{b}: duplicate sentences {len(dup)}; shared 8-grams {len(sh)}")
    for d in sorted(dup)[:5]: print("   DUP:", d[:140])
    ex = sorted(sh)[:8]
    for e in ex: print("   8gram:", e)
ids = {k: set(re.findall(r"arXiv:(\d{4}\.\d{5})", v)) | set(re.findall(r"doi: ?(10\.[^\s,;)]+)", v)) for k, v in refs.items()}
for a, b in itertools.combinations(ids, 2):
    print(f"shared references {a}-{b}: {sorted(ids[a] & ids[b])}")
print("reference counts:", {k: len(re.findall(r"^\[\d+\]", v, flags=re.M)) for k, v in refs.items()})
for term in ["guardrail", "human reference score", "three-rater", "repaired SUT", "baseline SUT", "pre-specified", "registered", "exploratory", "simulation", "not independent reproduction", "not publicly released", "publicly released"]:
    print(f"term '{term}':", {k: len(re.findall(re.escape(term), v, flags=re.I)) for k, v in body.items()})
