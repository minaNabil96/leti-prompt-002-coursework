"""Probe the three videos (ffmpeg from imageio-ffmpeg) and extract frames."""
import json
import pathlib
import re
import subprocess

import imageio_ffmpeg
from PIL import Image

ROOT = pathlib.Path(r".\image-animation")
FF = imageio_ffmpeg.get_ffmpeg_exe()
FR = ROOT / "logs" / "frames"
FR.mkdir(parents=True, exist_ok=True)

info = {}
for mp4 in sorted((ROOT / "animations").glob("*.mp4")):
    p = subprocess.run([FF, "-hide_banner", "-i", str(mp4)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    txt = p.stderr
    dur = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", txt)
    vid = re.search(r"Video: (\w+).*?, (\d+)x(\d+).*?(?:, ([\d.]+) fps)?", txt)
    seconds = None
    if dur:
        h, m, s = dur.groups()
        seconds = round(int(h) * 3600 + int(m) * 60 + float(s), 3)
    info[mp4.name] = {
        "duration_sec": seconds,
        "codec": vid.group(1) if vid else None,
        "size": [int(vid.group(2)), int(vid.group(3))] if vid else None,
        "fps": vid.group(4) if vid else None,
        "bytes": mp4.stat().st_size,
    }
    print(mp4.name, info[mp4.name])

    # 5 frames: 0.2 s, 25%, 50%, 75%, last
    for i, frac in enumerate((0.04, 0.25, 0.5, 0.75, 0.96)):
        t = max(0.0, (seconds or 5) * frac)
        out = FR / f"{mp4.stem}_f{i}.png"
        subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-ss", f"{t:.2f}",
                        "-i", str(mp4), "-frames:v", "1", "-y", str(out)],
                       capture_output=True, timeout=120)
    # contact strip
    frames = [FR / f"{mp4.stem}_f{i}.png" for i in range(5)]
    frames = [f for f in frames if f.exists()]
    if frames:
        ims = [Image.open(f).convert("RGB") for f in frames]
        w = 480
        scaled = [im.resize((w, int(im.height * w / im.width))) for im in ims]
        H = sum(s.height for s in scaled) + 10 * (len(scaled) - 1)
        strip = Image.new("RGB", (w, H), "white")
        y = 0
        for s in scaled:
            strip.paste(s, (0, y))
            y += s.height + 10
        strip.save(FR / f"{mp4.stem}_strip.png")
        print("  strip:", (FR / f"{mp4.stem}_strip.png").name, strip.size)

(ROOT / "logs" / "video_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2),
                                             encoding="utf-8")
