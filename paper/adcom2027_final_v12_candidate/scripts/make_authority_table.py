"""Generate the authority table (paper Table 1) from the enforcing code agents/multiagent/authority.py."""
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from agents.multiagent.authority import AUTHORITY, FORBIDDEN_KEYS  # noqa: E402


def esc(s):
    return s.replace("&", "\\&").replace("_", "\\_").replace("%", "\\%")


rows = []
for a in AUTHORITY.values():
    rows.append("\\textbf{%s} & %s & %s & %s & %s \\\\" % (
        a.agent.capitalize(), esc("; ".join(a.may_propose)), esc(a.keeps_private_state),
        esc("; ".join(a.cannot)), esc(a.escalation)))
body = "\n\\midrule\n".join(rows)
tex = ("\\begin{tabular}{>{\\raggedright\\arraybackslash}p{1.5cm}>{\\raggedright\\arraybackslash}p{3.0cm}>{\\raggedright\\arraybackslash}p{2.6cm}>{\\raggedright\\arraybackslash}p{3.1cm}>{\\raggedright\\arraybackslash}p{2.2cm}}\n\\toprule\nAgent & May propose & Private state & Cannot & On invalid output \\\\\n\\midrule\n"
       + body + "\n\\bottomrule\n\\end{tabular}\n")
Path(__file__).resolve().parents[1].joinpath("tables/authority.tex").write_text(tex)
Path(__file__).resolve().parents[1].joinpath("tables/forbidden_keys.tex").write_text(", ".join("\\texttt{%s}" % esc(k) for k in sorted(FORBIDDEN_KEYS)))
print("written", len(AUTHORITY), "agents,", len(FORBIDDEN_KEYS), "forbidden keys")
