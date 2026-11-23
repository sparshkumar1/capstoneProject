import csv
from pathlib import Path
R = Path(__file__).parents[1] / "results"; M = Path(__file__).parents[1] / "manuscript"
rows = list(csv.DictReader(open(R / "e1_predictions.csv")))
lines = ["\\begin{table}[h]", "\\caption{All 14 pre-registered E1 predictions. Violation = at least one session violates the invariant. Basis: ``known'' = from reading the code before the protocol, ``unsure'' = no prior expectation.}", "\\centering\\small", "\\begin{tabular}{llllccc}", "\\toprule",
         "Fault & Variant & Inv. & Basis & Predicted & Observed (sessions) & Match\\\\", "\\midrule"]
for r in rows:
    lines.append(f'{r["fault"]} & {r["variant"]} & {r["invariant"]} & {r["basis"].replace("known (full system)", "known")} & {"violation" if r["predicted_violation"]=="True" else "none"} & {r["observed_sessions_violating"]}/{r["sessions"]} & {r["match"]}\\\\')
lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
(M / "pred_table.tex").write_text("\n".join(lines) + "\n")
print(len(rows))
