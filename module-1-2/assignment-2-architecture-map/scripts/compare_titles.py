import pathlib

import pymupdf

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "arch-map" / "logs" / "pdf_pages"
OUT.mkdir(parents=True, exist_ok=True)

pairs = [
    (ROOT / "Итоговые_отчеты" / "Отчет_Задание1.pdf", "compare_a1_p1.jpg"),
    (ROOT / "arch-map" / "report" / "Отчет_Задание2.pdf", "compare_a2_p1.jpg"),
]
for pdf_path, out_name in pairs:
    pdf = pymupdf.open(pdf_path)
    pix = pdf[0].get_pixmap(matrix=pymupdf.Matrix(100 / 72, 100 / 72))
    pix.save(OUT / out_name, jpg_quality=90)
    print(out_name, pix.width, "x", pix.height, "| pages:", pdf.page_count)