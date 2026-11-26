"""Step 6a — trim silence from the TTS lines and measure real speech timing.

Writes audio/line_XX_trim.wav and logs/voiceover_timing.json. The assembly
script builds the timeline from this file, so every scene lasts exactly as long
as its narration line plus a small gap.
"""
import json
import pathlib
import re
import subprocess

import imageio_ffmpeg

ROOT = pathlib.Path(__file__).resolve().parents[1]
FF = imageio_ffmpeg.get_ffmpeg_exe()
AUDIO = ROOT / "audio"
LOGS = ROOT / "logs"
GAP = 0.35          # pause after each line before the next scene starts


def duration(path):
    p = subprocess.run([FF, "-hide_banner", "-i", str(path)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", p.stderr)
    if not m:
        raise SystemExit(f"no duration for {path}")
    h, mi, s = m.groups()
    return round(int(h) * 3600 + int(mi) * 60 + float(s), 3)


out = {"gap_sec": GAP, "lines": []}
t = 0.0
for n in range(1, 7):
    src = AUDIO / f"line_{n:02d}.wav"
    dst = AUDIO / f"line_{n:02d}_trim.wav"
    raw = duration(src)
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
                    "-af", "silenceremove=start_periods=1:start_threshold=-45dB:"
                           "start_silence=0.15,areverse,"
                           "silenceremove=start_periods=1:start_threshold=-45dB:"
                           "start_silence=0.15,areverse",
                    "-ar", "24000", "-ac", "1", str(dst)], check=True)
    trimmed = duration(dst)
    out["lines"].append({"line": n, "raw_s": raw, "trimmed_s": trimmed,
                         "start_in_film_s": round(t, 3),
                         "scene_slot_s": round(trimmed + GAP, 3)})
    print(f"line {n}: raw {raw:.2f}s -> trimmed {trimmed:.2f}s, starts at {t:.2f}s")
    t += trimmed + GAP

out["speech_s"] = round(sum(x["trimmed_s"] for x in out["lines"]), 3)
out["film_planned_s"] = round(t, 3)
(LOGS / "voiceover_timing.json").write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                           encoding="utf-8")
print(f"\nspeech {out['speech_s']}s, film (scenes+title) {out['film_planned_s']}s")
