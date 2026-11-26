import pathlib

from docx import Document

ROOT = pathlib.Path(__file__).resolve().parents[1]
doc = Document(ROOT / "report" / "Отчет_Задание2.docx")

sections = {}
current = "title"
for p in doc.paragraphs:
    if p.style.name == "Heading 1":
        current = p.text
        sections[current] = []
        continue
    if p.text.strip():
        sections.setdefault(current, []).append(p.text)

for name, paras in sections.items():
    words = sum(len(t.split()) for t in paras)
    if words:
        print(f"{words:4d} words | {name}")
