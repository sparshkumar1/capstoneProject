import re
P = r"C:\Users\spars\Downloads\PrepAIred\paper\manuscripts\paper2\manuscript.md"
t = open(P, encoding="utf-8").read()
t = t.replace("![Fig. 3](../figures/fig_p2_forest.png)\n\n**Fig. 3.**", "![Fig. 2](../figures/fig_p2_forest.png)\n\n**Fig. 2.**")
t = t.replace("![Fig. 2](../figures/fig_p2_category_gap.png)\n\n**Fig. 2.**", "![Fig. 3](../figures/fig_p2_category_gap.png)\n\n**Fig. 3.**")
open(P, "w", encoding="utf-8").write(t)
ab = re.search(r"\*\*Abstract—\*\* (.*?)\n", t).group(1)
print("abstract words", len(ab.split()))
body = re.sub(r"<!--.*?-->", "", t, flags=re.S).split("## References")[0]
print("body words", len(body.split()))
for pat in ["consensus", "gold", "three-rater", "moderate", "safer", "p = ", "0.0018863", "blind", "independent", "expert"]:
    for m in re.finditer(pat, body):
        s = body[max(0, m.start() - 70): m.end() + 60].replace("\n", " ")
        print(f"[{pat}] ...{s}...")
