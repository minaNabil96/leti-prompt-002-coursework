"""Assemble final Assignment 6 deliverables."""
import hashlib
import pathlib
import shutil
import zipfile

BASE = pathlib.Path(__file__).resolve().parents[2]
A6 = BASE / "model-catalog"
REPORT = A6 / "report"
SHOTS = A6 / "screenshots"
LOGS = A6 / "logs"
A6_DELIV = A6 / "deliverable"
ROOT_DELIV = BASE / "deliverable"
FINAL = BASE / "Итоговые_отчеты"

DOCX = REPORT / "Отчет_Задание6.docx"
PDF = REPORT / "Отчет_Задание6.pdf"

LOG_FILES = ["analysis.md", "worklog.md", "substitution.md"]


def copy_report(dst):
    dst.mkdir(parents=True, exist_ok=True)
    for src in (DOCX, PDF):
        shutil.copy2(src, dst / src.name)


def copy_logs(dst):
    dst.mkdir(parents=True, exist_ok=True)
    for name in LOG_FILES:
        shutil.copy2(LOGS / name, dst / name)
    shutil.copytree(LOGS / "model_metadata", dst / "model_metadata",
                    dirs_exist_ok=True)
    shutil.copytree(LOGS / "demo_results", dst / "demo_results",
                    dirs_exist_ok=True)


def copy_shots(dst):
    dst.mkdir(parents=True, exist_ok=True)
    for p in sorted(SHOTS.glob("*.png")):
        shutil.copy2(p, dst / p.name)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


if A6_DELIV.exists():
    shutil.rmtree(A6_DELIV)
copy_report(A6_DELIV)
copy_shots(A6_DELIV / "screenshots")
copy_logs(A6_DELIV / "logs")

copy_report(ROOT_DELIV)
copy_shots(ROOT_DELIV / "Задание6_screenshots")
copy_logs(ROOT_DELIV / "Задание6_logs")

zip_path = ROOT_DELIV / "Задание6_screenshots.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for p in sorted((ROOT_DELIV / "Задание6_screenshots").iterdir()):
        zf.write(p, p.name)
print("zip", zip_path.name, zip_path.stat().st_size)

copy_report(FINAL)

print("SHA256:")
for label, p in [
    ("source docx", DOCX),
    ("source pdf", PDF),
    ("model-catalog/deliverable docx", A6_DELIV / DOCX.name),
    ("model-catalog/deliverable pdf", A6_DELIV / PDF.name),
    ("root deliverable docx", ROOT_DELIV / DOCX.name),
    ("root deliverable pdf", ROOT_DELIV / PDF.name),
    ("Итоговые_отчеты docx", FINAL / DOCX.name),
    ("Итоговые_отчеты pdf", FINAL / PDF.name),
]:
    print(f"{sha(p)[:16]}  {p.stat().st_size:>9}  {label}")

shots = sorted(SHOTS.glob("*.png"))
print("screenshots:", len(shots), "bytes:",
      sum(p.stat().st_size for p in shots))
print("zip sha256:", sha(zip_path)[:16])
