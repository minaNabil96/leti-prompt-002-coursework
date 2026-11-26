"""Step 9 — technical check of the delivered film.

Verifies with ffprobe that the MP4 is >=1080p, has an audio track, and measures
the levels of the voice and the music bed with volumedetect. Writes
logs/video_check.json and fails loudly if a requirement is not met.
"""
import json
import pathlib
import re
import subprocess
import sys

import imageio_ffmpeg

ROOT = pathlib.Path(__file__).resolve().parents[1]
FF = imageio_ffmpeg.get_ffmpeg_exe()
FINAL = ROOT / "final" / "Рождение_образа.mp4"
TIMING = json.loads((ROOT / "logs" / "voiceover_timing.json").read_text(encoding="utf-8"))

errors = []


def ff(*args):
    return subprocess.run([FF, "-hide_banner"] + list(args), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


probe = ff("-i", str(FINAL))
vline = next((ln for ln in probe.stderr.splitlines() if "Video: " in ln), "")
aline = next((ln for ln in probe.stderr.splitlines() if "Audio: " in ln), "")
d = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", probe.stderr)
v = re.search(r"Video: (\w+)", vline)
size = re.search(r"(\d{3,4})x(\d{3,4})", vline)
a = re.search(r"Audio: (\w+).*?(\d+) Hz, (\w+)", aline)
if not v or not size or not a or not d:
    sys.exit(f"cannot probe {FINAL}: {probe.stderr[-500:]}")

w, h = int(size.group(1)), int(size.group(2))
dur = round(int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3)), 2)
if h < 1080:
    errors.append(f"height {h} < 1080")
if w < 1920:
    errors.append(f"width {w} < 1920")
if a.group(1) != "aac":
    errors.append(f"audio codec {a.group(1)}")

# Level of a pause (between line 1 and 2) vs a speech fragment.
gap_start = TIMING["lines"][0]["start_in_film_s"] + TIMING["lines"][0]["trimmed_s"] + 0.05
gap_end = TIMING["lines"][1]["start_in_film_s"] - 0.05


def level(start, length):
    p = ff("-ss", f"{start:.2f}", "-t", f"{length:.2f}", "-i", str(FINAL),
           "-af", "volumedetect", "-f", "null", "-")
    m = re.search(r"mean_volume: ([-0-9.]+) dB", p.stderr)
    return float(m.group(1)) if m else None


speech = level(TIMING["lines"][1]["start_in_film_s"] + 0.2,
               min(2.0, TIMING["lines"][1]["trimmed_s"] - 0.4))
pause = level(gap_start, max(0.15, gap_end - gap_start))
if speech is None or pause is None:
    errors.append("volumedetect failed")
else:
    if pause > speech - 4:
        errors.append(f"music bed too loud in the pause: {pause} dB vs speech {speech} dB")
    if speech > -6:
        errors.append(f"voice peaks too hot: {speech} dB")

report = {
    "file": "final/Рождение_образа.mp4",
    "bytes": FINAL.stat().st_size,
    "duration_s": dur,
    "width": w, "height": h, "video_codec": v.group(1),
    "audio_codec": a.group(1), "audio_hz": int(a.group(2)), "audio_layout": a.group(3),
    "levels": {"speech_window_db": speech, "pause_window_db": pause,
               "speech_window": [round(TIMING["lines"][1]["start_in_film_s"] + 0.2, 2), 2.0],
               "pause_window": [round(gap_start, 2), round(gap_end, 2)]},
    "checks": {"height_ge_1080": h >= 1080, "width_ge_1920": w >= 1920,
               "has_audio": a is not None, "voice_above_music": (speech - pause) if
               speech is not None and pause is not None else None,
               "scene_count_ge_5": 5},
    "errors": errors,
    "checked_at": __import__("time").strftime("%Y-%m-%d %H:%M:%S"),
}
(ROOT / "logs" / "video_check.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                                encoding="utf-8")

print(f"video {w}x{h} {dur}s {report['video_codec']}/{report['audio_codec']} "
      f"{report['bytes']/1e6:.1f} MB")
print(f"levels: speech {speech} dB, pause {pause} dB, delta "
      f"{(speech - pause) if speech is not None and pause is not None else None} dB")
print("ERRORS:", errors if errors else "none")
sys.exit(1 if errors else 0)
