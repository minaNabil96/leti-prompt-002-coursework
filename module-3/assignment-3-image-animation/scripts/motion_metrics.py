"""Objective motion metrics per animation (frame-to-frame difference)."""
import json
import pathlib
import subprocess

import imageio_ffmpeg
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 320, 320

out = {}
for mp4 in sorted((ROOT / "animations").glob("*.mp4")):
    p = subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", str(mp4),
                        "-vf", f"scale={W}:{H}", "-pix_fmt", "gray", "-f", "rawvideo", "-"],
                       capture_output=True, timeout=300)
    buf = np.frombuffer(p.stdout, dtype=np.uint8)
    n = buf.size // (W * H)
    frames = buf[: n * W * H].reshape(n, H, W).astype(np.int16)
    d = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2))
    out[mp4.name] = {
        "frames": int(n),
        "fps": 24,
        "duration_sec": round(n / 24, 2),
        "diff_mean": round(float(d.mean()), 3),
        "diff_max": round(float(d.max()), 3),
        "diff_std": round(float(d.std()), 3),
        "diff_p95": round(float(np.percentile(d, 95)), 3),
        "diff_first_sec": round(float(d[:24].mean()), 3),
        "diff_last_sec": round(float(d[-24:].mean()), 3),
    }
    print(mp4.name, out[mp4.name])

(ROOT / "logs" / "motion_metrics.json").write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                                   encoding="utf-8")
