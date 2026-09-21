"""Build the ICETC 2026 Paper 1 files from the page-economy port (venue/icetc2026/ICETC_PORT_MANUSCRIPT.md).

Outputs (all local; nothing is submitted):
  P1_ICETC_MANUSCRIPT_READY.md  author-identifying master (author block; no acknowledgment or placeholder text)
  P1_ICETC_BLINDED.md           anonymised copy for double-blind review
  build/P1_ICETC_MASTER.docx, build/P1_ICETC_BLINDED.docx   in the official IEEE Word template (template_official/template.docx)

The DOCX is produced by replacing the body of the official template with converted content that uses the template's own
paragraph styles (paper title, Author, Abstract, Keywords, heading 1/2/5, Body Text, table head, table copy,
figure caption, references). Heading, table, figure and reference numbering come from the template's numbering.
No number or sentence is changed here except the anonymisation and disclosure edits listed in ANON_EDITS."""
import re, struct, sys, zipfile, os
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "icetc2026", "ICETC_PORT_MANUSCRIPT.md")
TPL = os.path.join(HERE, "template_official", "template.docx")
FIGDIR = os.path.join(HERE, "..", "..", "figures")
os.makedirs(os.path.join(HERE, "build"), exist_ok=True)

src = open(SRC, encoding="utf-8").read()

# ---------------------------------------------------------------- variants of the markdown source
AUTHORS = [("Dr. Uma D", "Professor"), ("Naveen S Khadd", None), ("Sparsh Kumar", None), ("Athreya Shashidhara", None), ("Manasa S A", None)]
AFFIL = ("Dept. of CSE", "PES University")   # as supplied by the corresponding author; no e-mail, city or country recorded
AUTHOR_MD = "*" + "; ".join("%s%s, %s, %s" % (n, " (%s)" % d if d else "", AFFIL[0], AFFIL[1]) for n, d in AUTHORS) + "*"

ANON_EDITS = [
    ("local image `prepaired-c-sandbox`", "the project's local sandbox image"),
]

def variant(kind):
    t = src
    t = re.sub(r"<!--.*?-->\n", "", t, flags=re.S)
    t = t.replace("*Authors and affiliations: withheld in this draft (anonymity rule of the target venue not verified).*",
                  "*Anonymous authors (double-blind submission)*" if kind == "blind" else AUTHOR_MD)
    for a, b in ANON_EDITS:
        assert a in t, a
        t = t.replace(a, b)
    # No rendered copy carries an Acknowledgment or a placeholder. Any AI-use disclosure that ICETC or IEEE requires must be added by the
    # authors from confirmed facts (see P1_ICETC_READINESS.md); it is deliberately not drafted here.
    ack = r"## Acknowledgment\n\n.*?\n\n## References"
    t = re.sub(ack, "## References", t, flags=re.S)
    return t

master_md = variant("master")
blind_md = variant("blind")
for _n in ("Uma", "Khadd", "Sparsh", "Athreya", "Manasa", "PES University", "pes.edu"):
    assert _n not in blind_md, "author-identifying string in blinded copy: " + _n
open(os.path.join(HERE, "P1_ICETC_MANUSCRIPT_READY.md"), "w", encoding="utf-8").write(
    "<!-- P1 ICETC 2026 author-identifying MASTER (source for the IEEE Word build). NOT the file to upload; upload the blinded copy. Not submitted. -->\n\n" + master_md)
open(os.path.join(HERE, "P1_ICETC_BLINDED.md"), "w", encoding="utf-8").write(
    "<!-- P1 ICETC 2026 BLINDED copy (double-blind review). Not submitted. -->\n\n" + blind_md)

# ---------------------------------------------------------------- markdown -> WordprocessingML
W_NS_IDS = {"body": "7", "title": "21", "author": "14", "abstract": "12", "keywords": "29", "h1": "2", "h2": "3", "h5": "6",
            "tablehead": "28", "tablecopy": "26", "tablecolhead": "24", "figcap": "18", "ref": "22", "normal": "1"}

def rpr(bold=False, ital=False, code=False, size=None):
    x = ""
    if code: x += '<w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New"/>'
    if bold: x += "<w:b/><w:bCs/>"
    if ital: x += "<w:i/><w:iCs/>"
    if code and size is None: size = 15
    if size: x += '<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (size, size)
    return "<w:rPr>%s</w:rPr>" % x if x else ""

TOK = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\*[^*\s][^*]*?\*)")
def runs(text, bold=False, ital=False, size=None):
    out = []
    for part in TOK.split(text):
        if not part: continue
        b, i, c = bold, ital, False
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            part = part[2:-2]; b = True
        elif part.startswith("`") and part.endswith("`"):
            part = part[1:-1]; c = True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            part = part[1:-1]; i = not ital
        # nested italic inside bold or code handled one level only
        out.append('<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr(b, i, c, size), escape(part)))
    return "".join(out)

def para(style, text="", extra_ppr="", bold=False, ital=False, size=None, raw_runs=None):
    ppr = '<w:pPr><w:pStyle w:val="%s"/>%s</w:pPr>' % (W_NS_IDS[style], extra_ppr)
    return "<w:p>%s%s</w:p>" % (ppr, raw_runs if raw_runs is not None else runs(text, bold, ital, size))

def png_size(path):
    with open(path, "rb") as f:
        d = f.read(24)
    return struct.unpack(">II", d[16:24])

media = []   # (target_name, path)
def picture(path, width_in, rid, pid):
    w, h = png_size(path)
    cx = int(width_in * 914400); cy = int(cx * h / w)
    return ('<w:p><w:pPr><w:pStyle w:val="1"/><w:keepNext/><w:spacing w:before="160" w:after="0"/><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
            '<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="%d" cy="%d"/><wp:docPr id="%d" name="Figure %d"/>'
            '<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="%d" name="fig%d.png"/><pic:cNvPicPr/></pic:nvPicPr>'
            '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>') % (cx, cy, pid, pid, pid, pid, rid, cx, cy)

def table(rows, total=5000):
    ncol = len(rows[0])
    lens = [max(len(re.sub(r"[*`]", "", r[c])) for r in rows) for c in range(ncol)]
    weights = [min(max(l, 8), 60) ** 0.75 for l in lens]
    widths = [int(total * w / sum(weights)) for w in weights]
    x = ('<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>'
         '<w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/><w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
         '<w:insideH w:val="single" w:sz="2" w:space="0" w:color="808080"/></w:tblBorders><w:tblLayout w:type="fixed"/>'
         '<w:tblCellMar><w:left w:w="40" w:type="dxa"/><w:right w:w="40" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>%s</w:tblGrid>') % (
        total, "".join('<w:gridCol w:w="%d"/>' % w for w in widths))
    for ri, r in enumerate(rows):
        x += "<w:tr>" + ('<w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>' if ri == 0 else '<w:trPr><w:cantSplit/></w:trPr>')
        for ci, cell in enumerate(r):
            style = "tablecolhead" if ri == 0 else "tablecopy"
            ppr = '<w:pPr><w:pStyle w:val="%s"/>%s<w:spacing w:before="20" w:after="20"/><w:jc w:val="left"/></w:pPr>' % (W_NS_IDS[style], "" if ri == len(rows) - 1 else "<w:keepNext/>")
            x += '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/></w:tcPr><w:p>%s%s</w:p></w:tc>' % (widths[ci], ppr, runs(cell.strip(), bold=(ri == 0), size=15 if ri else 15))
        x += "</w:tr>"
    return x + "</w:tbl>"

SEC = {}
h1_count = [0]
def convert(md):
    h1_count[0] = 0
    lines = md.split("\n")
    body = []
    i = 0
    fig_no = 0
    title = None; ref_started = False
    pending_caption_kind = None
    while i < len(lines):
        ln = lines[i]
        if not ln.strip() or ln.strip() == "---" or ln.startswith("<!--"):
            i += 1; continue
        if ln.startswith("# "):
            title = ln[2:].strip(); i += 1; continue
        if ln.startswith("*Anonymous") or ln.startswith("*Dr. Uma"):
            author = ln.strip().strip("*")
            i += 1; continue
        if ln.startswith("**Abstract—**"):
            abstract = ln[len("**Abstract—**"):].strip(); i += 1; continue
        if ln.startswith("**Keywords—**"):
            keywords = ln[len("**Keywords—**"):].strip(); i += 1; continue
        if ln.startswith("## "):
            h = ln[3:].strip()
            if h in ("Acknowledgment", "References"):
                body.append(para("h5", h, extra_ppr="<w:keepNext/>"))
                ref_started = (h == "References")
            else:
                h1_count[0] += 1
                # the template's numbering tab (0.4 in) is narrower than "VIII."; widen it for that one heading so the numeral is followed by a space
                tabs = '<w:tabs><w:tab w:val="clear" w:pos="216"/><w:tab w:val="clear" w:pos="576"/><w:tab w:val="left" w:pos="700"/></w:tabs>' if h1_count[0] == 8 else ""
                body.append(para("h1", re.sub(r"^[IVX]+\.\s+", "", h), extra_ppr=tabs))
            i += 1; continue
        if ln.startswith("### "):
            body.append(para("h2", re.sub(r"^[A-Z]\.\s+", "", ln[4:].strip()))); i += 1; continue
        if ln.startswith("!["):
            fig_no += 1
            m = re.match(r"!\[.*?\]\((.*?)\)", ln)
            p = os.path.normpath(os.path.join(HERE, "..", "icetc2026", m.group(1)))
            name = "media/fig%d.png" % fig_no
            media.append((name, p))
            body.append('<w:p><w:pPr><w:pStyle w:val="1"/>%s</w:pPr></w:p>' % SEC["2col"])   # close the two-column section
            body.append(picture(p, 6.9, "rIdImg%d" % fig_no, 100 + fig_no))
            i += 1; continue
        if ln.startswith("**Fig."):
            m = re.match(r"\*\*Fig\. \d+\.\*\*\s*(.*)", ln)
            cap = para("figcap", m.group(1)).replace("</w:pPr>", SEC["1col"] + "</w:pPr>", 1)   # caption paragraph closes the one-column section
            body.append(cap); i += 1; continue
        if ln.startswith("**Table "):
            m = re.match(r"\*\*Table [IVX]+\.\s*(.*?)\*\*$", ln)
            body.append(para("tablehead", m.group(1), extra_ppr="<w:keepNext/>")); i += 1
            continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"\s*-+\s*", c) for c in cells):
                    rows.append(cells)
                i += 1
            body.append(table(rows))
            body.append('<w:p><w:pPr><w:pStyle w:val="1"/><w:spacing w:after="60" w:line="120" w:lineRule="exact"/></w:pPr></w:p>')
            continue
        if ref_started and re.match(r"\[\d+\]\s", ln):
            body.append(para("ref", re.sub(r"^\[\d+\]\s+", "", ln))); i += 1; continue
        body.append(para("body", ln)); i += 1
    return title, author, abstract, keywords, body

def author_table(total=9936):
    """One borderless row of five top-aligned author cells (name, optional designation, department, university), inside the one-column title section."""
    w = total // len(AUTHORS)
    x = ('<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/><w:tblLayout w:type="fixed"/>'
         '<w:tblCellMar><w:left w:w="40" w:type="dxa"/><w:right w:w="40" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>%s</w:tblGrid><w:tr>') % (
        w * len(AUTHORS), "".join('<w:gridCol w:w="%d"/>' % w for _ in AUTHORS))
    for name, desig in AUTHORS:
        lines = [(name, True)] + ([(desig, False)] if desig else []) + [(AFFIL[0], False), (AFFIL[1], False)]
        cell = "".join('<w:p><w:pPr><w:pStyle w:val="14"/><w:spacing w:before="0" w:after="0"/><w:jc w:val="center"/></w:pPr>%s</w:p>' % runs(t, bold=b, size=20) for t, b in lines)
        x += '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/><w:vAlign w:val="top"/></w:tcPr>%s</w:tc>' % (w, cell)
    return x + "</w:tr></w:tbl>"

def build(kind, md, out):
    global media
    media = []
    z = zipfile.ZipFile(TPL)
    doc = z.read("word/document.xml").decode("utf8")
    head = doc[:doc.index("<w:body>") + len("<w:body>")]
    sects = re.findall(r"<w:sectPr.*?</w:sectPr>", doc, re.S)
    sec_title = sects[0]                       # one-column title section (first-page footer kept from the template)
    sec_body = sects[5]                        # two-column continuous body section
    SEC["2col"] = sec_body
    SEC["1col"] = sec_body.replace('<w:cols w:space="360" w:num="2"/>', '<w:cols w:space="720" w:num="1"/>')
    title, author, abstract, keywords, body = convert(md)
    title_p = para("title", title)
    close_title = '<w:p><w:pPr><w:pStyle w:val="14"/>%s</w:pPr></w:p>'
    if kind == "master":
        # table, then a one-line spacer paragraph that ends the one-column title section
        author_p = author_table() + '<w:p><w:pPr><w:pStyle w:val="14"/><w:spacing w:before="0" w:after="60"/>%s</w:pPr></w:p>' % sec_title
    else:
        author_p = para("author", author, extra_ppr='<w:spacing w:before="0" w:after="120"/>' + sec_title)      # the title section (one column) ends after the author line
    abs_p = para("abstract", "", raw_runs=runs("Abstract—" + abstract))
    kw_p = para("keywords", "", raw_runs=runs("Keywords—" + keywords))
    balance = '<w:p><w:pPr><w:pStyle w:val="1"/><w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/>%s</w:pPr></w:p>' % sec_body   # continuous break: balances the last page's columns
    new_body = title_p + author_p + abs_p + kw_p + "".join(body) + balance + '<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/></w:pPr></w:p>' + sec_body
    newdoc = head + new_body + "</w:body></w:document>"
    rels = z.read("word/_rels/document.xml.rels").decode("utf8")
    add = "".join('<Relationship Id="rIdImg%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="%s"/>' % (i + 1, n)
                  for i, (n, _) in enumerate(media))
    rels = rels.replace("</Relationships>", add + "</Relationships>")
    ct = z.read("[Content_Types].xml").decode("utf8")
    if 'Extension="png"' not in ct:
        ct = ct.replace('<Default Extension="xml"', '<Default Extension="png" ContentType="image/png"/><Default Extension="xml"', 1)
    core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>%s</dc:title><dc:creator>%s</dc:creator><cp:lastModifiedBy></cp:lastModifiedBy></cp:coreProperties>'
            % (escape(title), "Anonymous" if kind == "blind" else "AUTHOR"))
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as o:
        for n in z.namelist():
            if n.endswith("/"): continue
            data = z.read(n)
            if n == "word/document.xml": data = newdoc.encode("utf8")
            elif n == "word/_rels/document.xml.rels": data = rels.encode("utf8")
            elif n == "[Content_Types].xml": data = ct.encode("utf8")
            elif n == "docProps/core.xml": data = core.encode("utf8")
            o.writestr(n, data)
        for n, p in media:
            o.write(p, "word/" + n)
    return len(media)

print("figures embedded (master):", build("master", master_md, os.path.join(HERE, "build", "P1_ICETC_MASTER.docx")))
print("figures embedded (blinded):", build("blind", blind_md, os.path.join(HERE, "build", "P1_ICETC_BLINDED.docx")))
for k, md in (("master", master_md), ("blind", blind_md)):
    body = md.split("## References")[0]
    print(k, "words before references:", len(re.sub(r"[|*`#\-]", " ", body).split()))
