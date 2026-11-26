import pathlib

import pymupdf

ROOT = pathlib.Path(__file__).resolve().parents[1]
pdf = pymupdf.open(ROOT / "report" / "Отчет_Задание2.pdf")
for i in range(pdf.page_count):
    text = pdf[i].get_text().replace("\n", " | ")
    print(f"--- page {i + 1} ---")
    print(text[:300])
    print()
