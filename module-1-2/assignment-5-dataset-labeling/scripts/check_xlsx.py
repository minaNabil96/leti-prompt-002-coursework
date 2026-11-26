"""Inspect разметка.xlsx: embedded images, then render via LibreOffice to images."""
import pathlib
import shutil
import subprocess
import tempfile

import pymupdf
from openpyxl import load_workbook

ROOT = pathlib.Path(__file__).resolve().parents[1]
XLSX = ROOT / "разметка.xlsx"
OUT = ROOT / "logs" / "xlsx_pages"
OUT.mkdir(parents=True, exist_ok=True)
SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.com"


def main():
    wb = load_workbook(XLSX)
    for ws in wb.worksheets:
        print(ws.title, "dims", ws.max_row, ws.max_column, "images", len(ws._images))
    print("main headers:", [c.value for c in wb["Разметка"][1]])

    with tempfile.TemporaryDirectory(prefix="a5xlsx_") as tmp:
        tmp = pathlib.Path(tmp)
        src = tmp / "razmetka.xlsx"
        shutil.copy2(XLSX, src)
        subprocess.run(
            [SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(src)],
            check=True, timeout=240, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        pdf_path = tmp / "razmetka.pdf"
        pdf = pymupdf.open(pdf_path)
        print("rendered pages:", pdf.page_count)
        for i in range(pdf.page_count):
            pix = pdf[i].get_pixmap(matrix=pymupdf.Matrix(100 / 72, 100 / 72))
            pix.save(OUT / f"xlsx_p{i + 1}.jpg", jpg_quality=85)
    print("saved previews to", OUT)


if __name__ == "__main__":
    main()
