"""Step 6 — edit the film with FFmpeg: 1080p upscale, crossfades, title card,
voiceover + music mix with ducking.

Timeline (logs/voiceover_timing.json): every scene lasts its narration line plus
a 0.35 s pause, so the picture follows the voice instead of the other way round.
Each clip gets an extra 0.25 s tail, which the 0.5 s crossfade consumes, so
scene boundaries stay exactly where the voice starts.

Output: final/Рождение_образа.mp4 (1920x1080, H.264, AAC) + logs/assembly.json.
"""
import json
import pathlib
import re
import subprocess
import sys

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
FF = imageio_ffmpeg.get_ffmpeg_exe()
WORK = ROOT / "logs" / "edit"
WORK.mkdir(parents=True, exist_ok=True)
FINAL = ROOT / "final"
FINAL.mkdir(exist_ok=True)

TIMING = json.loads((ROOT / "logs" / "voiceover_timing.json").read_text(encoding="utf-8"))
XFADE = 0.5
FPS = 30
W, H = 1920, 1080

GEORGIA = r"C:\Windows\Fonts\georgiab.ttf"
SEGOE = r"C:\Windows\Fonts\segoeui.ttf"
SEGOE_LIGHT = r"C:\Windows\Fonts\segoeuil.ttf"


def run(args, desc=""):
    p = subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error"] + args,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        print(p.stderr[-3000:])
        sys.exit(f"FAILED: {desc or ' '.join(args[:6])}")
    return p


def duration(path):
    p = subprocess.run([FF, "-hide_banner", "-i", str(path)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", p.stderr)
    h, mi, s = m.groups()
    return round(int(h) * 3600 + int(mi) * 60 + float(s), 3)


# ---------------------------------------------------------------- timeline
lines = [dict(l, slot=l["scene_slot_s"]) for l in TIMING["lines"]]
total = TIMING["film_planned_s"]
print(f"film length: {total}s, {len(lines)} blocks")

# ---------------------------------------------------------------- title card
last = ROOT / "scenes" / "scene_05.mp4"
frame = WORK / "last_frame.png"
run(["-ss", str(max(0.0, duration(last) - 0.5)), "-i", str(last), "-frames:v", "1",
     str(frame)], "last frame")
bg = Image.open(frame).convert("RGB").resize((W, H), Image.LANCZOS)
bg = bg.filter(ImageFilter.GaussianBlur(26))
bg = Image.eval(bg, lambda v: int(v * 0.55))

# vignette
vig = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([-W * 0.25, -H * 0.35, W * 1.25, H * 1.35], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(180))
black = Image.new("RGB", (W, H), (0, 0, 0))
bg = Image.composite(bg, black, vig)

draw = ImageDraw.Draw(bg)
title_font = ImageFont.truetype(GEORGIA, 132)
sub_font = ImageFont.truetype(SEGOE_LIGHT, 44)
cred_font = ImageFont.truetype(SEGOE, 30)

title = "Рождение образа"
tw = draw.textlength(title, font=title_font)
draw.text(((W - tw) / 2, 380), title, font=title_font, fill=(247, 239, 224))

sub = "к о р о т к о м е т р а ж н ы й   р о л и к"
sw = draw.textlength(sub, font=sub_font)
draw.text(((W - sw) / 2, 560), sub, font=sub_font, fill=(198, 196, 214))

cred = ("Сценарий и раскадровка — Gemini 2.5 Flash ·  видео — Grok Imagine Video 1.5\n"
        "голос — Gemini 3.8 Flash Lite TTS ·  музыка — Lyria 3 ·  монтаж — FFmpeg")
for i, row in enumerate(cred.split("\n")):
    rw = draw.textlength(row, font=cred_font)
    draw.text(((W - rw) / 2, 760 + i * 46), row, font=cred_font, fill=(168, 168, 190))

draw.text((120, H - 96), "2026", font=cred_font, fill=(150, 150, 170))
title_png = WORK / "title_card.png"
bg.save(title_png)
print("title card:", title_png.name)

# ---------------------------------------------------------------- scene clips
clips = []
for ln in lines:
    n = ln["line"]
    slot = ln["slot"]  # narration + pause
    target = round(slot + XFADE / 2, 3)
    if n <= 5:
        src = ROOT / "scenes" / f"scene_{n:02d}.mp4"
        src_len = duration(src)
        speed = target / src_len
        vf = (f"setpts={speed:.6f}*PTS,fps={FPS},"
              f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
              f"crop={W}:{H},unsharp=5:5:0.55:5:5:0.0,setsar=1")
        out = WORK / f"clip_{n:02d}.mp4"
        run(["-i", str(src), "-an", "-vf", vf, "-t", f"{target:.3f}",
             "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p",
             str(out)], f"scene {n}")
        clips.append({"n": n, "file": str(out), "source": f"scenes/scene_{n:02d}.mp4",
                      "source_s": src_len, "target_s": target,
                      "stretch": round(speed, 4)})
        print(f"  clip {n}: {src_len}s -> {target}s (x{speed:.2f})")
    else:
        out = WORK / f"clip_{n:02d}.mp4"
        fade_out = max(0.0, target - 0.8)
        vf = (f"scale={W}:{H},fps={FPS},setsar=1,"
              f"fade=t=in:st=0:d=0.5,fade=t=out:st={fade_out:.3f}:d=0.8")
        run(["-loop", "1", "-i", str(title_png), "-t", f"{target:.3f}", "-vf", vf,
             "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p",
             str(out)], "title card clip")
        clips.append({"n": n, "file": str(out), "source": "logs/edit/title_card.png",
                      "source_s": None, "target_s": target, "stretch": None})
        print(f"  clip {n} (title): {target}s")

# ---------------------------------------------------------------- crossfades
filt = []
cur = "0:v"
for i in range(1, len(clips)):
    prev = f"x{i-1}" if i > 1 else "0:v"
    nxt = f"{i}:v"
    label = f"x{i}"
    # dissolve centred on the boundary: offset = boundary - half the fade
    offset = round(sum(c["target_s"] - XFADE / 2 for c in clips[:i]) - XFADE / 2, 3)
    filt.append(f"[{prev}][{nxt}]xfade=transition=fade:duration={XFADE}:offset={offset:.3f}[{label}]")
    cur = label

inputs = []
for c in clips:
    inputs += ["-i", c["file"]]

run(inputs + ["-filter_complex", ";".join(filt), "-map", f"[{cur}]",
              "-c:v", "libx264", "-preset", "medium", "-crf", "18",
              "-pix_fmt", "yuv420p", "-r", str(FPS), str(WORK / "video_silent.mp4")],
    "crossfade chain")
video_len = duration(WORK / "video_silent.mp4")
print(f"video (crossfaded): {video_len}s")

# ---------------------------------------------------------------- audio mix
amix_parts = []
for ln in lines:
    delay = int(round(ln["start_in_film_s"] * 1000))
    amix_parts.append(f"[{ln['line']}:a]aresample=48000,"
                      f"aformat=sample_fmts=fltp:channel_layouts=stereo,"
                      f"adelay={delay}|{delay},volume=1.0[v{ln['line']}]")
voice_labels = "".join(f"[v{ln['line']}]" for ln in lines)
voice_mix = (f"{voice_labels}amix=inputs={len(lines)}:normalize=0:dropout_transition=0,"
             f"volume=1.0[voice]")

music_idx = len(lines)
fade_out_st = max(0.0, total - 3.0)
# The generated track is 66 s: the first seconds are a quiet intro and it fades
# out after 60 s, so the usable 33 s window is 24-57 s.
music_chain = (f"[{music_idx}:a]atrim=start=24:end={24 + total:.3f},asetpts=PTS-STARTPTS,"
               f"aresample=48000,"
               f"aformat=sample_fmts=fltp:channel_layouts=stereo,"
               f"afade=t=in:st=0:d=1.0,afade=t=out:st={fade_out_st:.3f}:d=3.0,"
               f"volume=0.15[music]")

# Voice stays at full level; the bed sits about 16 dB below it. A fixed bed was
# chosen over sidechain ducking: a first mix with sidechaincompress=threshold 0.02
# dropped the music to -44 dB in every pause between phrases.
mix = (f"[voice]apad=whole_dur={total:.3f}[voicep];"
       f"[voicep][music]amix=inputs=2:normalize=0:duration=longest,"
       f"alimiter=limit=0.95,atrim=0:{total:.3f}[aout]")

audio_inputs = []
for ln in lines:
    audio_inputs += ["-i", str(ROOT / "audio" / f"line_{ln['line']:02d}_trim.wav")]
audio_inputs += ["-i", str(ROOT / "audio" / "music.mp3")]

audio_filter = ";".join(amix_parts + [voice_mix, music_chain, mix])
run(audio_inputs + ["-filter_complex", audio_filter, "-map", "[aout]",
                    "-c:a", "pcm_s16le", str(WORK / "audio_mix.wav")], "audio mix")
print("audio mix:", duration(WORK / "audio_mix.wav"), "s")

# ---------------------------------------------------------------- final mux
out_name = "Рождение_образа.mp4"
run(["-i", str(WORK / "video_silent.mp4"), "-i", str(WORK / "audio_mix.wav"),
     "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
     "-ar", "48000", "-shortest", "-movflags", "+faststart",
     str(FINAL / out_name)], "final mux")

final = FINAL / out_name
print(f"\nFINAL: {final} {final.stat().st_size/1e6:.1f} MB {duration(final)}s")

# ---------------------------------------------------------------- verify
probe = subprocess.run([FF, "-hide_banner", "-i", str(final)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace").stderr
vstream = re.search(r"Video: (\w+).*?, (\d+)x(\d+).*?, ([\d.]+) fps", probe)
astream = re.search(r"Audio: (\w+).*?, (\d+) Hz, (\w+)", probe)
info = {"file": f"final/{out_name}", "duration_s": duration(final),
        "bytes": final.stat().st_size,
        "video": {"codec": vstream.group(1), "width": int(vstream.group(2)),
                  "height": int(vstream.group(3)), "fps": float(vstream.group(4))} if vstream else None,
        "audio": {"codec": astream.group(1), "sample_rate": int(astream.group(2)),
                  "layout": astream.group(3)} if astream else None,
        "timeline": [{"line": l["line"], "start_s": l["start_in_film_s"],
                      "slot_s": l["slot"]} for l in lines],
        "crossfade_s": XFADE, "fps": FPS,
        "clips": clips, "film_planned_s": total, "video_stream_s": video_len,
        "music": {"file": "audio/music.mp3", "gain": 0.15,
                  "ducking": "none — fixed bed at -16.5 dB"},
        "title_card": {"file": "logs/edit/title_card.png",
                       "text": ["Рождение образа",
                                "Сценарий и раскадровка — Gemini 2.5 Flash · видео — Grok Imagine Video 1.5",
                                "голос — Gemini 3.8 Flash Lite TTS · музыка — Lyria 3 · монтаж — FFmpeg"]},
        "created": __import__("time").strftime("%Y-%m-%d %H:%M:%S")}
(ROOT / "logs" / "assembly.json").write_text(json.dumps(info, ensure_ascii=False, indent=2),
                                             encoding="utf-8")
print(json.dumps(info["video"], ensure_ascii=False), json.dumps(info["audio"], ensure_ascii=False))
