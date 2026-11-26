"""Self-check for Отчет_Задание4: docx structure + PDF render."""
import pathlib
import re

import pymupdf
from docx import Document

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCX = ROOT / "report" / "Отчет_Задание4.docx"
PDF = ROOT / "report" / "Отчет_Задание4.pdf"
A3PDF = ROOT.parent / "ref-analysis" / "report" / "Отчет_Задание3.pdf"
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
print("underscores (___):", full.count("___"))
print("Ханна М. Н.:", "Ханна М. Н." in full)
print("assignment line:", "«Задание 4. Анализ открытого мультимедийного датасета»" in full)
print("markdown leftovers **:", full.count("**"))
print("markdown leftovers |---:", "|---" in full)

print("\n=== PDF ===")
pdf = pymupdf.open(PDF)
print("pages:", pdf.page_count)
print("p1:", pdf[0].get_text().replace("\n", " ")[:320])
print("2026 on p1:", "2026" in pdf[0].get_text())
print("page2 starts:", pdf[1].get_text().replace("\n", " ")[:140])

targets = {}
for i, page in enumerate(pdf):
    t = page.get_text()
    if "Таблица 1" in t and "t1" not in targets:
        targets["t1"] = i
    if "Таблица 2" in t and "t2" not in targets:
        targets["t2"] = i
    if "Приложение А" in t:
        targets.setdefault("appA", i)
    if "Приложение Б" in t:
        targets.setdefault("appB", i)
print("targets:", targets)

pp = {1: 0, 2: 1}
for k, v in targets.items():
    pp[k] = v
pp[f"last{pdf.page_count}"] = pdf.page_count - 1
for name, idx in sorted(pp.items(), key=lambda kv: kv[1]):
    zoom = 100 / 72 if name == 1 else 78 / 72
    pix = pdf[idx].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    pix.save(OUT / f"a4_page_{name}.jpg", jpg_quality=88)
    print("rendered", f"a4_page_{name}.jpg", pix.width, "x", pix.height)

all_text = "\n".join(p.get_text() for p in pdf)
print("pdf ** occurrences:", all_text.count("**"))
print("pdf |--- occurrences:", all_text.count("|---"))

# side-by-side title pages with Assignment 3
if A3PDF.exists():
    from PIL import Image

    p3 = pymupdf.open(A3PDF)
    p4 = pymupdf.open(PDF)
    imgs = []
    for src in (p3, p4):
        pix = src[0].get_pixmap(matrix=pymupdf.Matrix(90 / 72, 90 / 72))
        imgs.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
    W = sum(i.width for i in imgs) + 20
    H = max(i.height for i in imgs)
    combo = Image.new("RGB", (W, H), (200, 200, 200))
    x = 0
    for im in imgs:
        combo.paste(im, (x, 0))
        x += im.width + 20
    combo.save(OUT / "title_compare_a3_a4.jpg", quality=90)
    print("title compare saved")
