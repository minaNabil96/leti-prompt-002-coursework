import hashlib
import pathlib
import re

from docx import Document
import pymupdf

ROOT = pathlib.Path(__file__).resolve().parents[2]
A2 = ROOT / "arch-map"
DEL_ROOT = ROOT / "deliverable"
DEL_A2 = A2 / "deliverable"

files = {
    "source_docx": A2 / "report" / "Отчет_Задание2.docx",
    "source_pdf": A2 / "report" / "Отчет_Задание2.pdf",
    "a2_docx": DEL_A2 / "Отчет_Задание2.docx",
    "a2_pdf": DEL_A2 / "Отчет_Задание2.pdf",
    "root_docx": DEL_ROOT / "Отчет_Задание2.docx",
    "root_pdf": DEL_ROOT / "Отчет_Задание2.pdf",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


for name, path in files.items():
    print(f"{name:<12} exists={path.exists()} size={path.stat().st_size if path.exists() else 0} sha={sha(path) if path.exists() else '-'}")

print("\nPDF pages:")
for name in ("source_pdf", "a2_pdf", "root_pdf"):
    print(name, pymupdf.open(files[name]).page_count)

print("\nDOCX check (root deliverable):")
doc = Document(files["root_docx"])
text = "\n".join(p.text for p in doc.paragraphs)
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            text += "\n" + cell.text
print("tables:", len(doc.tables), "images:", len(doc.inline_shapes))
print("forbidden:", re.findall(r"TODO|XXX|placeholder|【", text, flags=re.I) or "none")
print("underscores:", text.count("___"), "| name:", "Ханна М. Н." in text)
print("theme:", "Тема: Карта архитектур в реальных продуктах" in text)

print("\nScreenshots:")
for folder in (A2 / "screenshots", DEL_A2 / "screenshots", DEL_ROOT / "Задание2_screenshots"):
    pngs = sorted(p.name for p in folder.glob("*.png"))
    print(f"{folder}: {len(pngs)} files; expected 15 -> {len(pngs) == 15}")
    missing = [n for n in (
        [f"action_T{i}.png" for i in (1, 2, 3)] + [f"action_D{i}.png" for i in (1, 2, 3)]
        + [f"arch_T{i}.png" for i in (1, 2, 3)] + [f"arch_D{i}.png" for i in (1, 2, 3)]
        + [f"img_D{i}.png" for i in (1, 2, 3)]
    ) if n not in pngs]
    print("  missing:", missing or "none")

print("\nLogs in arch-map/deliverable/logs:")
print(sorted(p.name for p in (DEL_A2 / "logs").iterdir()))
