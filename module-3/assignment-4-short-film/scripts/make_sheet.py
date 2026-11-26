"""Rebuild logs/frames/final_sheet.png: one frame from each of the six scenes.

Also corrects the music record in logs/assembly.json to the chain actually used
by assemble.py (fixed bed at gain 0.15); the earlier record still described the
abandoned sidechain-ducking variant.
"""
import json
import pathlib
import subprocess
import tempfile

import imageio_ffmpeg
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
EDIT = LOGS / "edit"
FRAMES = LOGS / "frames"
FRAMES.mkdir(parents=True, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()

asm = json.loads((LOGS / "assembly.json").read_text(encoding="utf-8"))
asm["music"] = {"file": "audio/music.mp3", "gain": 0.15,
                "ducking": "none — fixed bed at -16.5 dB"}
(LOGS / "assembly.json").write_text(json.dumps(asm, ensure_ascii=False, indent=2),
                                    encoding="utf-8")

CELL_W, CELL_H = 640, 360
sheet = Image.new("RGB", (CELL_W * 3, CELL_H * 2), "black")

with tempfile.TemporaryDirectory(prefix="sheet_") as tmp:
    tmp = pathlib.Path(tmp)
    for i, clip in enumerate(asm["clips"], 1):
        at = clip["target_s"] * 0.5
        png = tmp / f"f{i}.png"
        subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-ss", f"{at:.3f}",
                        "-i", str(EDIT / f"clip_{i:02d}.mp4"), "-frames:v", "1",
                        "-vf", f"scale={CELL_W}:{CELL_H}", str(png)], check=True)
        cell = Image.open(png).convert("RGB")
        sheet.paste(cell, (((i - 1) % 3) * CELL_W, ((i - 1) // 3) * CELL_H))
        print(f"scene {i}: frame at {at:.2f}s of clip_{i:02d}.mp4")

sheet.save(FRAMES / "final_sheet.png", optimize=True)
print("saved", FRAMES / "final_sheet.png", sheet.size)
