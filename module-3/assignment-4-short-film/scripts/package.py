"""Assemble short-film/deliverable and copy it to the project folders.

Layout (mirrors the earlier М3 assignments):
  short-film/deliverable/Отчет_М3_Задание4.docx|pdf
  short-film/deliverable/Рождение_образа.mp4
  short-film/deliverable/М3_Задание4_logs/...
  short-film/deliverable/М3_Задание4_screenshots/...

Copies:
  <project>/deliverable/            — report + film + logs + screenshots
  <project>/Итоговые_отчеты/        — report only (flat, like Задание 1-3)

Prints SHA-256 of every copy so the three locations can be compared.
"""
import hashlib
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
OUT = ROOT / "deliverable"
REPORT = ROOT / "report"
LOGS = ROOT / "logs"
SHOTS = ROOT / "screenshots"
FILM = ROOT / "final" / "Рождение_образа.mp4"

if OUT.exists():
    shutil.rmtree(OUT)
(OUT / "М3_Задание4_logs").mkdir(parents=True)
(OUT / "М3_Задание4_screenshots").mkdir()

# report
for ext in ("docx", "pdf"):
    shutil.copy2(REPORT / f"Отчет_М3_Задание4.{ext}", OUT / f"Отчет_М3_Задание4.{ext}")

# film
shutil.copy2(FILM, OUT / "Рождение_образа.mp4")

# logs: everything a reviewer may want to verify, raw API records included
log_files = [
    "cost.md", "worklog.md", "generation-method.md",
    "computed_stats.json", "scene_results.json", "video_check.json",
    "prompt_iterations.json", "prompt_iterations.md",
    "assembly.json", "voiceover_timing.json", "tts.json", "music.json",
    "models_raw.json", "preflight.json", "session_date.txt",
]
for name in log_files:
    src = LOGS / name
    if src.exists():
        shutil.copy2(src, OUT / "М3_Задание4_logs" / name)
    else:
        print("missing log:", name)
for sub in ("video", "tts"):
    (OUT / "М3_Задание4_logs" / sub).mkdir()
    for p in sorted((LOGS / sub).glob("*")):
        if p.is_file():
            shutil.copy2(p, OUT / "М3_Задание4_logs" / sub / p.name)

# screenshots + contact sheet
for p in sorted(SHOTS.glob("*.png")):
    shutil.copy2(p, OUT / "М3_Задание4_screenshots" / p.name)
shutil.copy2(LOGS / "frames" / "final_sheet.png",
             OUT / "М3_Задание4_screenshots" / "04_final_frames.png")

# ---------------------------------------------------------------- copies
dest = PROJECT / "deliverable"
for p in OUT.iterdir():
    target = dest / p.name
    if p.is_dir():
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(p, target)
    else:
        shutil.copy2(p, target)

final_dir = PROJECT / "Итоговые_отчеты"
final_dir.mkdir(exist_ok=True)
for ext in ("docx", "pdf"):
    shutil.copy2(OUT / f"Отчет_М3_Задание4.{ext}", final_dir / f"Отчет_М3_Задание4.{ext}")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


print("--- SHA-256 ---")
report_rows = []
for ext in ("docx", "pdf"):
    name = f"Отчет_М3_Задание4.{ext}"
    a, b, c = OUTPUT_PATHS = [OUT / name, dest / name, final_dir / name]
    hashes = [sha(x) for x in OUTPUT_PATHS]
    ok = len(set(hashes)) == 1
    print(f"{name}: {'OK' if ok else 'MISMATCH'} {hashes[0][:16]}")
    print(f"   deliverable/ {hashes[1][:16]}  Итоговые_отчеты/ {hashes[2][:16]}")
    report_rows.append({"file": name, "sha256": hashes[0], "match": ok,
                        "copies": [str(x) for x in OUTPUT_PATHS]})
film_hashes = [sha(FILM), sha(OUT / "Рождение_образа.mp4"),
               sha(dest / "Рождение_образа.mp4")]
print(f"Рождение_образа.mp4: {'OK' if len(set(film_hashes)) == 1 else 'MISMATCH'} "
      f"{film_hashes[0][:16]}")
print(f"   source {film_hashes[0][:16]}  deliverable {film_hashes[1][:16]}  "
      f"root {film_hashes[2][:16]}")

probe = json.loads((LOGS / "video_check.json").read_text(encoding="utf-8"))
manifest = {
    "report": report_rows,
    "film": {"file": "Рождение_образа.mp4", "bytes": FILM.stat().st_size,
             "duration_s": probe["duration_s"],
             "resolution": f"{probe['width']}x{probe['height']}",
             "codec": f"{probe['video_codec']}/{probe['audio_codec']}",
             "sha256": film_hashes[0], "match": len(set(film_hashes)) == 1},
    "logs": sorted(p.name for p in (OUT / "М3_Задание4_logs").rglob("*") if p.is_file()),
    "screenshots": sorted(p.name for p in (OUT / "М3_Задание4_screenshots").glob("*.png")),
}
(OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                                   encoding="utf-8")
shutil.copy2(OUT / "manifest.json", dest / "manifest.json")
print(f"\nfiles in deliverable: {sum(1 for p in OUT.rglob('*') if p.is_file())}")
print(f"film {probe['bytes']/1e6:.1f} MB, {probe['duration_s']} s, "
      f"{probe['width']}x{probe['height']}")
