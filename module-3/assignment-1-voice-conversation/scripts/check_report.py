import pathlib

import fitz
from docx import Document

ROOT = pathlib.Path(__file__).resolve().parents[1]
docx = ROOT / "report" / "Отчет_М3_Задание1.docx"
pdf = ROOT / "report" / "Отчет_М3_Задание1.pdf"

d = Document(docx)
print("paragraphs", len(d.paragraphs), "tables", len(d.tables),
      "sections", len(d.sections), "images", len(d.inline_shapes))
for i, s in enumerate(d.sections):
    print("section", i, "margins cm",
          round(s.top_margin.cm, 2), round(s.bottom_margin.cm, 2),
          round(s.left_margin.cm, 2), round(s.right_margin.cm, 2),
          "page mm", round(s.page_width.mm, 1), round(s.page_height.mm, 1))

f = fitz.open(pdf)
print("pdf pages", f.page_count)
p1 = f[0]
print("page size", round(p1.rect.width, 1), round(p1.rect.height, 1))
for i in range(min(3, f.page_count)):
    t = f[i].get_text()
    print("--- page", i + 1, "chars", len(t))
    print(t[:300].replace("\n", " | "))
print("--- last page")
print(f[f.page_count - 1].get_text()[:400].replace("\n", " | "))
fonts = set()
for i in range(f.page_count):
    for b in f[i].get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                fonts.add((s["font"], round(s["size"], 1)))
print("fonts", sorted(fonts))
