"""Region-level motion analysis: which part of the frame actually moves.

Splits every clip into a 3x3 grid at 384x384 and reports the mean absolute
frame-to-frame difference per cell, plus the audio-stream presence.
"""
import json
import pathlib
import re
import subprocess

import imageio_ffmpeg
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
FF = imageio_ffmpeg.get_ffmpeg_exe()
W = H = 384

out = {}
for mp4 in sorted((ROOT / "animations").glob("*.mp4")):
    p = subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", str(mp4),
                        "-vf", f"scale={W}:{H}", "-pix_fmt", "gray", "-f", "rawvideo", "-"],
                       capture_output=True, timeout=300)
    buf = np.frombuffer(p.stdout, dtype=np.uint8)
    n = buf.size // (W * H)
    frames = buf[: n * W * H].reshape(n, H, W).astype(np.int16)
    diff = np.abs(np.diff(frames, axis=0)).mean(axis=0)  # average diff map

    grid = []
    labels = ["верх-лево", "верх-центр", "верх-право",
              "центр-лево", "центр", "центр-право",
              "низ-лево", "низ-центр", "низ-право"]
    for r in range(3):
        for c in range(3):
            cell = diff[r * H // 3:(r + 1) * H // 3, c * W // 3:(c + 1) * W // 3]
            grid.append({"cell": labels[r * 3 + c], "diff": round(float(cell.mean()), 3)})

    info = subprocess.run([FF, "-hide_banner", "-i", str(mp4)],
                          capture_output=True, text=True, errors="replace").stderr
    audio = bool(re.search(r"Stream #\d+:\d+.*Audio:", info))
    size = re.search(r"Video: .*?, (\d+)x(\d+)", info)

    out[mp4.name] = {
        "audio_stream": audio,
        "size": [int(size.group(1)), int(size.group(2))] if size else None,
        "grid": sorted(grid, key=lambda x: -x["diff"]),
    }
    print("=" * 60)
    print(mp4.name, "audio:", audio)
    for g in out[mp4.name]["grid"]:
        print(f"  {g['cell']:13s} {g['diff']:.3f}")

(ROOT / "logs" / "motion_regions.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
