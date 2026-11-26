"""Copy final deliverables into deliverable/, root deliverable/ and Итоговые_отчеты/."""
import hashlib
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORK = ROOT.parent
REPORT = ROOT / "report"
DOCX = REPORT / "Отчет_М3_Задание3.docx"
PDF = REPORT / "Отчет_М3_Задание3.pdf"
DEST = ROOT / "deliverable"

ROOT_DELIV = WORK / "deliverable"
FINAL = WORK / "Итоговые_отчеты"
TAG = "М3_Задание3"


def sha(p):
    h = hashlib.sha256()
    h.update(pathlib.Path(p).read_bytes())
    return h.hexdigest().upper()


def copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


# 1. image-animation/deliverable — полный комплект
DEST.mkdir(exist_ok=True)
copy(DOCX, DEST / DOCX.name)
copy(PDF, DEST / PDF.name)
for sub in ("sources", "animations", "screenshots", "logs"):
    tgt = DEST / sub
    if tgt.exists():
        shutil.rmtree(tgt)
    tgt.mkdir()
    for f in sorted((ROOT / sub).iterdir()):
        if f.is_file():
            copy(f, tgt / f.name)

# 2. root deliverable — отчёт + каталоги артефактов + архив снимков
copy(DOCX, ROOT_DELIV / DOCX.name)
copy(PDF, ROOT_DELIV / PDF.name)
for sub, name in (("sources", f"{TAG}_sources"), ("animations", f"{TAG}_animations"),
                  ("screenshots", f"{TAG}_screenshots")):
    tgt = ROOT_DELIV / name
    if tgt.exists():
        shutil.rmtree(tgt)
    tgt.mkdir()
    for f in sorted((ROOT / sub).iterdir()):
        if f.is_file():
            copy(f, tgt / f.name)

zip_base = ROOT_DELIV / f"{TAG}_screenshots"
if (zip_base.with_suffix(".zip")).exists():
    (zip_base.with_suffix(".zip")).unlink()
shutil.make_archive(str(zip_base), "zip", ROOT / "screenshots")

# 3. Итоговые_отчеты — только отчёт
copy(DOCX, FINAL / DOCX.name)
copy(PDF, FINAL / PDF.name)

print("source hashes")
print("  docx", sha(DOCX), DOCX.stat().st_size)
print("  pdf ", sha(PDF), PDF.stat().st_size)
print("copies")
for p in (DEST / DOCX.name, DEST / PDF.name, ROOT_DELIV / DOCX.name,
          ROOT_DELIV / PDF.name, FINAL / DOCX.name, FINAL / PDF.name):
    print("  ", p.relative_to(WORK), sha(p), p.stat().st_size)
print("dirs")
for d in (DEST, ROOT_DELIV / f"{TAG}_sources", ROOT_DELIV / f"{TAG}_animations",
          ROOT_DELIV / f"{TAG}_screenshots"):
    print("  ", d.relative_to(WORK), sum(1 for f in d.rglob("*") if f.is_file()), "файлов")
print("  zip", (ROOT_DELIV / f"{TAG}_screenshots.zip").stat().st_size)
