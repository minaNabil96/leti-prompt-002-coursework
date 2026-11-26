"""Self-check of the assembled report (DOCX + PDF)."""
import pathlib
import re

import pymupdf
from docx import Document
from docx.shared import Pt

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCX = ROOT / "report" / "Отчет_М3_Задание2.docx"
PDF = ROOT / "report" / "Отчет_М3_Задание2.pdf"

d = Document(DOCX)
paras = [p.text for p in d.paragraphs]
cells = [c.text for t in d.tables for row in t.rows for c in row.cells]
full = "\n".join(paras + cells)

pdf = pymupdf.open(PDF)
pdf_text = "\n".join(p.get_text() for p in pdf)

print(f"paragraphs {len(paras)} tables {len(d.tables)} sections {len(d.sections)} "
      f"images {len(d.inline_shapes)}")
print(f"pdf pages {pdf.page_count}")
pg = pdf[0]
print(f"page size {pg.rect.width:.1f} {pg.rect.height:.1f}")

fonts = {}
for p in pdf:
    for f in p.get_fonts():
        fonts[f[3]] = fonts.get(f[3], 0) + 1
print("fonts", sorted(fonts))

print("\nHeadings:")
for p in d.paragraphs:
    if p.style.name.startswith("Heading"):
        print("  ", p.style.name, "|", p.text)

print("\nTitle page runs:")
for p in d.paragraphs[:12]:
    if p.text.strip():
        print("  ", repr(p.text), [(r.text[:18], r.bold) for r in p.runs])

print("\nPage 1 has number:", bool(re.fullmatch(r"\s*\d+\s*", pdf_text.split("\n")[0])))
print("Page 2 footer digits:", [l for l in pdf[1].get_text().splitlines() if l.strip().isdigit()])

print("\nTable count by caption:")
for p in paras:
    if p.startswith(("Таблица", "Рисунок")):
        print("  ", p)

print("\nPlaceholders:")
for tok in ("TODO", "XXX", "FIXME", "placeholder", "【", "___"):
    print(f"  {tok!r}: {full.count(tok)}")

print("\nTemplate fields:")
for h in ("2.1.", "2.2.", "2.3.", "2.4.", "2.5."):
    i = next((k for k, p in enumerate(paras) if p.startswith(h)), None)
    nxt = next((k for k in range(i + 1, len(paras)) if paras[k].strip()), None)
    print(f"  {h} -> {paras[nxt][:80] if nxt else 'MISSING'}")

print("\nEmpty paragraphs:", sum(1 for p in paras if not p.strip()))
print("Body font size:", {r.font.size.pt for p in d.paragraphs for r in p.runs if r.font.size})
