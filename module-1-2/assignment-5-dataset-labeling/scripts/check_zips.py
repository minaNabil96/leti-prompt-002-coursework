import pathlib
import zipfile

base = pathlib.Path(__file__).resolve().parents[2]
root = base / "deliverable"
final = base / "Итоговые_отчеты"

for name in ("Задание5_images.zip", "Задание5_screenshots.zip"):
    p = root / name
    with zipfile.ZipFile(p) as z:
        bad = z.testzip()
        print(name, p.stat().st_size, "files:", len(z.namelist()), "testzip:", bad)

for folder in (root / "Задание5_images", root / "Задание5_screenshots",
               base / "labeling" / "deliverable" / "images"):
    files = [q for q in folder.iterdir() if q.is_file()]
    print(folder.name, len(files))

print("root deliverable files:", sorted(q.name for q in root.iterdir()))
print("final files:", sorted(q.name for q in final.iterdir()))
print("A2 logs/screenshots kept:", (root / "logs").is_dir(), (root / "screenshots").is_dir())
