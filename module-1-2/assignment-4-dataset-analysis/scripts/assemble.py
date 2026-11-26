"""Assemble final Assignment 4 deliverables."""
import hashlib
import pathlib
import shutil
import zipfile

BASE = pathlib.Path(__file__).resolve().parents[2]
A4 = BASE / "dataset-analysis"
REPORT = A4 / "report"
SHOTS = A4 / "screenshots"
LOGS = A4 / "logs"
A4_DELIV = A4 / "deliverable"
ROOT_DELIV = BASE / "deliverable"
FINAL = BASE / "Итоговые_отчеты"

DOCX = REPORT / "Отчет_Задание4.docx"
PDF = REPORT / "Отчет_Задание4.pdf"

LOG_FILES = [
    "dataset_metadata.json",
    "dataset_metadata_parsed.json",
    "dataset_readme.md",
    "examples.json",
    "examples_raw.json",
    "limitations.md",
    "worklog.md",
    "creation_method.md",
    "model_analysis.md",
    "bias_analysis.md",
    "legal_analysis.md",
    "access_notes.md",
    "viewer_error.json",
]


def copy_report(dst_dir):
    dst_dir.mkdir(parents=True, exist_ok=True)
    for src in (DOCX, PDF):
        shutil.copy2(src, dst_dir / src.name)


def copy_logs(dst):
    dst.mkdir(parents=True, exist_ok=True)
    for name in LOG_FILES:
        shutil.copy2(LOGS / name, dst / name)


def copy_shots(dst):
    dst.mkdir(parents=True, exist_ok=True)
    for p in sorted(SHOTS.glob("*.png")):
        shutil.copy2(p, dst / p.name)
    for p in sorted(SHOTS.glob("example_*.jpg")):
        shutil.copy2(p, dst / p.name)


# 1. dataset-analysis/deliverable (flat report + folders, like Assignment 3)
if A4_DELIV.exists():
    shutil.rmtree(A4_DELIV)
copy_report(A4_DELIV)
copy_shots(A4_DELIV / "screenshots")
copy_logs(A4_DELIV / "logs")

# 2. root deliverable/ – do not touch existing A2/A3 artifacts
copy_report(ROOT_DELIV)
copy_shots(ROOT_DELIV / "Задание4_screenshots")
copy_logs(ROOT_DELIV / "Задание4_logs")
zip_path = ROOT_DELIV / "Задание4_screenshots.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for p in sorted((ROOT_DELIV / "Задание4_screenshots").iterdir()):
        zf.write(p, p.name)

# 3. consolidated reports folder
copy_report(FINAL)

# 4. hashes
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

print("SHA256:")
for label, p in [
    ("source docx", DOCX),
    ("source pdf", PDF),
    ("dataset-analysis/deliverable docx", A4_DELIV / DOCX.name),
    ("dataset-analysis/deliverable pdf", A4_DELIV / PDF.name),
    ("root deliverable docx", ROOT_DELIV / DOCX.name),
    ("root deliverable pdf", ROOT_DELIV / PDF.name),
    ("Итоговые_отчеты docx", FINAL / DOCX.name),
    ("Итоговые_отчеты pdf", FINAL / PDF.name),
]:
    print(f"{sha(p)[:16]}  {p.stat().st_size:>9}  {label}")

print("\nScreenshots in A4 deliverable:",
      len(list((A4_DELIV / 'screenshots').glob('*'))))
print("Logs in A4 deliverable:", len(list((A4_DELIV / 'logs').glob('*'))))
print("Root Задание4_screenshots:", len(list((ROOT_DELIV / 'Задание4_screenshots').glob('*'))))
print("Root Задание4_logs:", len(list((ROOT_DELIV / 'Задание4_logs').glob('*'))))
print("Zip size:", zip_path.stat().st_size)
