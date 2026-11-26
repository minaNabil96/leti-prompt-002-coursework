"""Self-check for Отчет_Задание6: docx structure + PDF render."""
import pathlib
import re

import pymupdf
from docx import Document

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCX = ROOT / "report" / "Отчет_Задание6.docx"
PDF = ROOT / "report" / "Отчет_Задание6.pdf"
SHOTS = ROOT / "screenshots"
OUT = ROOT / "logs" / "pdf_pages"
OUT.mkdir(parents=True, exist_ok=True)

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
print("theme line:", "Тема: Каталог моделей машинного обучения" in full)
print("markdown leftovers **:", full.count("**"))
print("markdown leftovers |---:", "|---" in full)

print("\n=== PDF ===")
pdf = pymupdf.open(PDF)
print("pages:", pdf.page_count)
p1 = pdf[0].get_text().replace("\n", " ")
print("p1:", p1[:400])
print("2026 on p1:", "2026" in p1)
print("page1 number absent:", not re.search(r"\n\s*1\s*\n", pdf[0].get_text()))
print("page2 starts:", pdf[1].get_text().replace("\n", " ")[:120])

for i, pg in enumerate(pdf):
    t = [x.strip() for x in pg.get_text().splitlines() if x.strip()]
    print(i + 1, "|", " / ".join(t[:2])[:100])

for i in range(pdf.page_count):
    pix = pdf[i].get_pixmap(matrix=pymupdf.Matrix(78 / 72, 78 / 72))
    pix.save(OUT / f"a6_p{i + 1}.jpg", jpg_quality=88)

all_text = "\n".join(p.get_text() for p in pdf)
print("pdf ** occurrences:", all_text.count("**"))
print("pdf |--- occurrences:", all_text.count("|---"))
for name in ("01_task_filter.png", "02_card_M1.png", "03_card_M2.png",
             "04_card_M3.png", "05_card_M4.png", "06_card_M5.png",
             "07_card_M6.png", "08_demo_M1.png", "09_demo_M5.png",
             "10_tree_diagram.png"):
    print("shot", name, (SHOTS / name).exists(),
          (SHOTS / name).stat().st_size if (SHOTS / name).exists() else 0)
