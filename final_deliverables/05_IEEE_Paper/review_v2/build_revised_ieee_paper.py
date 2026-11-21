"""Build the revised, architecture-centred IEEE paper from
ieee_paper_specialised_architecture_v2.md into the official IEEE Word
conference template, adapted from the project's own proven builder
(paper/manuscripts/venue/ICETC_P1/build_icetc_docx.py -- READ-ONLY reuse,
not modified). Output is a NEW file; none of the existing IEEE paper
deliverables (Final_IEEE_Paper_Anonymous.docx/pdf, Final_IEEE_Paper_Source.tex)
or the original template/build script are touched.
"""
import re, struct, sys, zipfile, os
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(HERE, "ieee_paper_specialised_architecture_v2.md")
TPL = os.path.join(ROOT, "paper", "manuscripts", "venue", "ICETC_P1", "template_official", "template.docx")
FIGDIR = os.path.join(ROOT, "final_deliverables", "05_IEEE_Paper")  # figures referenced as IEEE_Figures/...
os.makedirs(os.path.join(HERE, "build"), exist_ok=True)

src = open(SRC, encoding="utf-8").read()

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
        out.append('<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr(b, i, c, size), escape(part)))
    return "".join(out)

def para(style, text="", extra_ppr="", bold=False, ital=False, size=None, raw_runs=None):
    ppr = '<w:pPr><w:pStyle w:val="%s"/>%s</w:pPr>' % (W_NS_IDS[style], extra_ppr)
    return "<w:p>%s%s</w:p>" % (ppr, raw_runs if raw_runs is not None else runs(text, bold, ital, size))

def png_size(path):
    with open(path, "rb") as f:
        d = f.read(24)
    return struct.unpack(">II", d[16:24])

media = []
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
    title = None; author = None; abstract = None; keywords = None
    ref_started = False
    while i < len(lines):
        ln = lines[i]
        if not ln.strip() or ln.strip() == "---" or ln.startswith("<!--"):
            i += 1; continue
        if ln.startswith("# "):
            title = ln[2:].strip(); i += 1; continue
        if ln.startswith("*Anonymous"):
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
                tabs = '<w:tabs><w:tab w:val="clear" w:pos="216"/><w:tab w:val="clear" w:pos="576"/><w:tab w:val="left" w:pos="700"/></w:tabs>'
                body.append(para("h1", re.sub(r"^[IVX]+\.\s+", "", h), extra_ppr=tabs))
            i += 1; continue
        if ln.startswith("### "):
            body.append(para("h2", re.sub(r"^[A-Z]\.\s+", "", ln[4:].strip()))); i += 1; continue
        if ln.startswith("!["):
            # Inline image inside the current (2-column) section, sized to the
            # column's own width -- NOT a full-page-width section break. This
            # keeps the figure anchored inside a single column, matching the
            # original paper's non-starred `figure` (single-column) convention,
            # rather than spanning both columns.
            fig_no += 1
            m = re.match(r"!\[.*?\]\((.*?)\)", ln)
            rel = m.group(1)
            p_here = os.path.normpath(os.path.join(HERE, rel))
            p = p_here if os.path.exists(p_here) else os.path.normpath(os.path.join(FIGDIR, rel))
            name = "media/fig%d.png" % fig_no
            media.append((name, p))
            body.append(picture(p, 3.0, "rIdImg%d" % fig_no, 100 + fig_no))
            i += 1; continue
        if ln.startswith("**Fig."):
            m = re.match(r"\*\*Fig\. \d+\.\*\*\s*(.*)", ln)
            body.append(para("figcap", m.group(1))); i += 1; continue
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

def build(md, out):
    global media
    media = []
    z = zipfile.ZipFile(TPL)
    doc = z.read("word/document.xml").decode("utf8")
    head = doc[:doc.index("<w:body>") + len("<w:body>")]
    sects = re.findall(r"<w:sectPr.*?</w:sectPr>", doc, re.S)
    sec_title = sects[0]
    sec_body = sects[5]
    SEC["2col"] = sec_body
    SEC["1col"] = sec_body.replace('<w:cols w:space="360" w:num="2"/>', '<w:cols w:space="720" w:num="1"/>')
    title, author, abstract, keywords, body = convert(md)
    title_p = para("title", title)
    author_p = para("author", author, extra_ppr='<w:spacing w:before="0" w:after="120"/>' + sec_title)
    abs_p = para("abstract", "", raw_runs=runs("Abstract—" + abstract))
    kw_p = para("keywords", "", raw_runs=runs("Keywords—" + keywords))
    balance = '<w:p><w:pPr><w:pStyle w:val="1"/><w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/>%s</w:pPr></w:p>' % sec_body
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
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>%s</dc:title><dc:creator>Anonymous</dc:creator><cp:lastModifiedBy></cp:lastModifiedBy></cp:coreProperties>'
            % escape(title))
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

out_path = os.path.join(HERE, "build", "PrepAIred_IEEE_Paper_SpecialisedArchitecture_v2.docx")
print("figures embedded:", build(src, out_path))
body_only = src.split("## References")[0]
print("words before references:", len(re.sub(r"[|*`#\-]", " ", body_only).split()))
print("wrote:", out_path)
