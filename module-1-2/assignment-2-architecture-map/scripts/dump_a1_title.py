import pathlib

from docx import Document
from docx.oxml.ns import qn

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOCX = ROOT / "Итоговые_отчеты" / "Отчет_Задание1.docx"
doc = Document(DOCX)

body = doc.element.body
count = 0
for child in body.iterchildren():
    tag = child.tag.split("}")[1]
    if tag == "p":
        from docx.text.paragraph import Paragraph
        p = Paragraph(child, doc)
        runs = []
        for r in p.runs:
            rPr = r._element.rPr
            bold = r.bold
            size = r.font.size.pt if r.font.size else None
            name = r.font.name
            runs.append((r.text, bold, size, name))
        print(f"P align={p.alignment} before={p.paragraph_format.space_before} after={p.paragraph_format.space_after} "
              f"indent={p.paragraph_format.first_line_indent} line={p.paragraph_format.line_spacing}")
        for text, bold, size, name in runs:
            print(f"   RUN bold={bold} size={size} font={name} text={text!r}")
        count += 1
        if count > 30:
            break
    elif tag == "tbl":
        from docx.table import Table
        t = Table(child, doc)
        print(f"TABLE rows={len(t.rows)} cols={len(t.columns)} style={t.style.name if t.style else None}")
        for ri, row in enumerate(t.rows):
            cells = []
            for c in row.cells:
                cells.append(repr(c.text))
            print("  row", ri, " | ".join(cells))
        # column widths
        print("  col widths:", [c.width for c in t.columns])
    elif tag == "sectPr":
        print("SECTION BREAK")
        break