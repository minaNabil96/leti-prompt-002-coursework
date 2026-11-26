"""Assemble final Assignment 5 deliverables."""
import hashlib
import pathlib
import shutil
import zipfile

BASE = pathlib.Path(__file__).resolve().parents[2]
A5 = BASE / "labeling"
REPORT = A5 / "report"
SHOTS = A5 / "screenshots"
IMAGES = A5 / "images"
LOGS = A5 / "logs"
A5_DELIV = A5 / "deliverable"
ROOT_DELIV = BASE / "deliverable"
FINAL = BASE / "Итоговые_отчеты"

DOCX = REPORT / "Отчет_Задание5.docx"
PDF = REPORT / "Отчет_Задание5.pdf"
XLSX = A5 / "разметка.xlsx"

LOG_FILES = [
    "generation-method.md",
    "labels_ground_truth.json",
    "labels_blind.json",
    "labels_blind_stress.json",
    "agreement.json",
    "stress_agreement.json",
    "agreement.md",
    "disagreement_analysis.md",
    "analysis.md",
    "instruction.md",
    "worklog.md",
    "cost.md",
    "mismatch_notes.json",
]


def copy_report(dst):
    dst.mkdir(parents=True, exist_ok=True)
    for src in (DOCX, PDF, XLSX):
        shutil.copy2(src, dst / src.name)


def copy_logs(dst):
    dst.mkdir(parents=True, exist_ok=True)
    for name in LOG_FILES:
        p = LOGS / name
        if p.exists():
            shutil.copy2(p, dst / name)
    shutil.copytree(LOGS / "gen", dst / "gen", dirs_exist_ok=True)


def copy_shots(dst):
    dst.mkdir(parents=True, exist_ok=True)
    for p in sorted(SHOTS.glob("*.png")):
        shutil.copy2(p, dst / p.name)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


if A5_DELIV.exists():
    shutil.rmtree(A5_DELIV)
copy_report(A5_DELIV)
copy_shots(A5_DELIV / "screenshots")
shutil.copytree(IMAGES, A5_DELIV / "images", dirs_exist_ok=True)
copy_logs(A5_DELIV / "logs")

copy_report(ROOT_DELIV)
copy_shots(ROOT_DELIV / "Задание5_screenshots")
shutil.copytree(IMAGES, ROOT_DELIV / "Задание5_images", dirs_exist_ok=True)
copy_logs(ROOT_DELIV / "Задание5_logs")

for folder, zip_name in (("Задание5_screenshots", "Задание5_screenshots.zip"),
                         ("Задание5_images", "Задание5_images.zip")):
    path = ROOT_DELIV / zip_name
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted((ROOT_DELIV / folder).iterdir()):
            zf.write(p, p.name)
    print("zip", zip_name, path.stat().st_size)

copy_report(FINAL)

print("SHA256:")
for label, p in [
    ("source docx", DOCX),
    ("source pdf", PDF),
    ("source xlsx", XLSX),
    ("labeling/deliverable docx", A5_DELIV / DOCX.name),
    ("labeling/deliverable pdf", A5_DELIV / PDF.name),
    ("root deliverable docx", ROOT_DELIV / DOCX.name),
    ("root deliverable pdf", ROOT_DELIV / PDF.name),
    ("Итоговые_отчеты docx", FINAL / DOCX.name),
    ("Итоговые_отчеты pdf", FINAL / PDF.name),
]:
    print(f"{sha(p)[:16]}  {p.stat().st_size:>9}  {label}")
print("images:", len(list(IMAGES.glob('img_*.png'))),
      "total MB:", round(sum(p.stat().st_size for p in IMAGES.glob('img_*.png')) / 1e6, 1))
