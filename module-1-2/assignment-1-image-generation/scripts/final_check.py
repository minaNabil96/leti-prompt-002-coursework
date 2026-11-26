import os
import re
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
roots = ["deliverable", os.path.join("..", "deliverable")]
pat = re.compile(r"TODO|XXX|placeholder|【")
for root in roots:
    print("==", os.path.abspath(root))
    for dp, _dn, fn in os.walk(root):
        for f in fn:
            p = os.path.join(dp, f)
            if f.lower().endswith((".md", ".txt", ".py", ".json", ".csv")):
                with open(p, encoding="utf-8", errors="replace") as fh:
                    if pat.search(fh.read()):
                        print("HIT", p)
    d = os.path.join(root, "Отчет_Задание1.docx")
    with zipfile.ZipFile(d) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    txt = re.sub(r"<[^>]+>", " ", xml)
    print("docx forbidden hits:", pat.findall(txt))
    print("Ханна М. Н.:", "Ханна М. Н." in txt)
    print("2026:", "2026" in txt)
