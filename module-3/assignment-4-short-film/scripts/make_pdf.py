"""Convert the DOCX report to PDF via LibreOffice, using ASCII temp paths."""
import pathlib
import shutil
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCX = ROOT / "report" / "Отчет_М3_Задание4.docx"
PDF = ROOT / "report" / "Отчет_М3_Задание4.pdf"
SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.com"


def main():
    with tempfile.TemporaryDirectory(prefix="m3a4pdf_") as tmp:
        tmp = pathlib.Path(tmp)
        src = tmp / "report.docx"
        shutil.copy2(DOCX, src)
        subprocess.run(
            [SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(src)],
            check=True, timeout=600,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        produced = tmp / "report.pdf"
        if not produced.exists():
            raise SystemExit("PDF not produced")
        shutil.copy2(produced, PDF)
    print("saved", PDF, PDF.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
