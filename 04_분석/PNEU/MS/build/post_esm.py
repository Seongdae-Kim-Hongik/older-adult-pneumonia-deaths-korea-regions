# post_esm.py — Supplement 서식: 본문 Times New Roman 10pt 단일 간격, 큰 제목 12pt 굵게, 표 안 글자 Arial(10pt 이하 유지), 표 제목 Arial 12pt 굵게.
import sys, re
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_LINE_SPACING
from docx.oxml.ns import qn
def font(r, name, size=None):
    r.font.name = name; r._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), name)
    if size: r.font.size = Pt(size)
p = sys.argv[1]; d = Document(p)
for para in d.paragraphs:
    para.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE; para.paragraph_format.space_after = Pt(4)
    t = para.text.strip(); title = bool(re.match(r"^(eTable \d+[a-z]?|eFigure \d|eMethods|eAppendix)\.", t))
    for r in para.runs:
        if title and para.style.name.startswith("Heading") or t == "Supplement": font(r, "Times New Roman", 12); r.bold = True
        elif title and t.startswith(("eTable", "eFigure")) and r.bold: font(r, "Arial", 12)
        else: font(r, "Times New Roman", 10 if (r.font.size is None or r.font.size.pt > 10) else r.font.size.pt)
for tb in d.tables:
    for row in tb.rows:
        for c in row.cells:
            for para in c.paragraphs:
                t = para.text.strip(); ttl = bool(re.match(r"^(eTable \d+[a-z]?|eAppendix)\.", t))
                for r in para.runs: font(r, "Arial", 12 if ttl else (10 if (r.font.size is None or r.font.size.pt > 10) else r.font.size.pt))
d.save(p); print("post_esm ok")
