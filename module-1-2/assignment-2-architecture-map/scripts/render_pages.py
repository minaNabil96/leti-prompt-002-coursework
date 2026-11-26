import pathlib

import pymupdf

ROOT = pathlib.Path(__file__).resolve().parents[1]
PDF = ROOT / "report" / "Отчет_Задание2.pdf"
OUT = ROOT / "logs" / "pdf_pages"
pdf = pymupdf.open(PDF)

for page_no in [3, 4, 5, 6, 9, 10, 11, 13, 14]:
    idx = page_no - 1
    pix = pdf[idx].get_pixmap(matrix=pymupdf.Matrix(78 / 72, 78 / 72))
    path = OUT / f"a2_full_{page_no}.jpg"
    pix.save(path, jpg_quality=85)
    print("rendered", path.name, pix.width, "x", pix.height)
