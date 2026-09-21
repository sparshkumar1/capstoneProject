"""LAYOUT PREVIEW ONLY: converts a manuscript .md to a plain single-column HTML file (Times 11 pt, A4) so Word can export a PDF that is
rendered and inspected for tables, figures, headings and references. The result is NOT the venue template: its page count is meaningless
and must never be reported as the paper's length.
Usage: PYTHONPATH=<dir with markdown> python preview_md_to_html.py <in.md> <out.html>"""
import os, re, sys, markdown

src, out = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()
text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
base = os.path.dirname(os.path.abspath(src))
def fix_img(m):
    p = os.path.normpath(os.path.join(base, m.group(2)))
    return "![%s](file:///%s)" % (m.group(1), p.replace("\\", "/"))
text = re.sub(r"!\[(.*?)\]\((.*?)\)", fix_img, text)
body = markdown.markdown(text, extensions=["tables"])
body = re.sub(r"<img ", '<img style="max-width:15.5cm" ', body)
css = ("@page{size:21cm 29.7cm;margin:2.5cm}body{font-family:'Times New Roman';font-size:11pt;line-height:1.25}"
       "table{border-collapse:collapse;font-size:9pt;margin:6pt 0}td,th{border:1px solid #000;padding:2pt 4pt;vertical-align:top}"
       "h1{font-size:16pt;text-align:center}h2{font-size:13pt}h3{font-size:11pt}")
open(out, "w", encoding="utf-8").write("<html><head><meta charset='utf-8'><style>%s</style></head><body>%s</body></html>" % (css, body))
print("wrote", out)
