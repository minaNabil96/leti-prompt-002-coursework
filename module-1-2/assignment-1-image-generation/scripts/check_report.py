"""Self-check: docx structure + PDF render of key pages."""
import pathlib
import re

import pymupdf
from docx import Document

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCX = ROOT / "report" / "Отчет_Задание1.docx"
PDF = ROOT / "report" / "Отчет_Задание1.pdf"
OUT = ROOT / "logs" / "pdf_pages"
OUT.mkdir(exist_ok=True)

doc = Document(DOCX)
print("=== DOCX ===")
print("paragraphs:", len(doc.paragraphs), "tables:", len(doc.tables),
      "inline_images:", len(doc.inline_shapes), "sections:", len(doc.sections))
print("--- heading outline ---")
for p in doc.paragraphs:
    if p.style.name.startswith("Heading"):
        print(p.style.name, "|", p.text)

full = "\n".join(p.text for p in doc.paragraphs)
for t in doc.tables:
    for row in t.rows:
        for c in row.cells:
            full += "\n" + c.text
hits = re.findall(r"TODO|XXX|placeholder|【", full, flags=re.I)
print("forbidden hits:", hits if hits else "none")
print("underscores:", full.count("___"))

print("\n=== PDF ===")
pdf = pymupdf.open(PDF)
print("pages:", pdf.page_count)
for i, page in enumerate(pdf):
    txt = page.get_text().strip().replace("\n", " ")
    print(f"p{i+1}: {txt[:160]}")

# find pages of interest
targets = {}
for i, page in enumerate(pdf):
    t = page.get_text()
    if "Таблица 2" in t and "5" not in targets:
        targets["table2"] = i
    if "Приложение А" in t:
        targets.setdefault("appA", i)
    if "Приложение Б" in t:
        targets.setdefault("appB", i)
print("targets:", targets)

pages = {1: 0, 2: 1, 3: 2}
for k, v in targets.items():
    pages[k] = v
last = pdf.page_count
pages[f"last{last}"] = last - 1
for name, idx in sorted(pages.items(), key=lambda kv: kv[1]):
    zoom = 100 / 72 if name == 1 else 80 / 72
    pix = pdf[idx].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    path = OUT / f"page_{name}.jpg"
    pix.save(path, jpg_quality=88)
    print("rendered", path.name, pix.width, "x", pix.height)

for i, page in enumerate(pdf):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(70 / 72, 70 / 72))
    pix.save(OUT / f"page_all_{i+1:02d}.jpg", jpg_quality=85)
print("rendered all pages")
