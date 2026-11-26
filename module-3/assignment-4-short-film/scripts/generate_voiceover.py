"""Step 4 — voiceover with google/gemini-3.8-flash-lite-tts.

Endpoint: POST /api/v1/audio/speech {"model","input","voice","response_format":"wav"}.
The API answers with base64 WAV in JSON. One call per scene line, so every line
can be placed at its own scene start during assembly.

Reads scripts/voiceover.json, writes audio/line_01.wav … line_06.wav and
logs/tts.json with per-line characters, duration and billed cost.
"""
import base64
import json
import pathlib
import subprocess
import sys
import time

import imageio_ffmpeg
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJ = ROOT.parent
API = "https://polza.ai/api/v1"
KEY = (PROJ / "ref-analysis" / ".polza_key").read_text(encoding="utf-8").strip()
MODEL = "google/gemini-3.8-flash-lite-tts"
VOICE = "Kore"          # same voice as in М3, задание 1
FF = imageio_ffmpeg.get_ffmpeg_exe()

AUDIO = ROOT / "audio"
AUDIO.mkdir(exist_ok=True)
LOGS = ROOT / "logs"

data = json.loads((ROOT / "scripts" / "voiceover.json").read_text(encoding="utf-8"))
lines = data["lines"]

out = {"model": MODEL, "voice": VOICE, "endpoint": f"{API}/audio/speech",
       "requested_format": "wav", "created": time.strftime("%Y-%m-%d %H:%M:%S"),
       "source": "scripts/voiceover.json (итерация 5 LLM)", "lines": []}
total = 0.0

for ln in lines:
    n = ln["n"]
    wav = AUDIO / f"line_{n:02d}.wav"
    log = LOGS / "tts" / f"line_{n:02d}.json"
    if wav.exists() and log.exists():
        rec = json.loads(log.read_text(encoding="utf-8"))
        total += rec.get("cost_rub", 0.0)
        print(f"line {n}: exists, skip ({rec['cost_rub']} RUB, {rec['duration_s']}s)")
        out["lines"].append(rec)
        continue

    text = ln["text"]
    t0 = time.time()
    r = requests.post(f"{API}/audio/speech", headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        json={"model": MODEL, "input": text, "voice": VOICE,
              "response_format": "wav"}, timeout=300)
    dt = time.time() - t0
    if not r.ok:
        sys.exit(f"line {n}: HTTP {r.status_code} {r.text[:400]}")
    payload = r.json()
    wav.write_bytes(base64.b64decode(payload["audio"]))

    p = subprocess.run([FF, "-hide_banner", "-i", str(wav)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    dur = None
    for token in p.stderr.split():
        if token.startswith("Duration:"):
            break
    import re
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", p.stderr)
    if m:
        h, mi, s = m.groups()
        dur = round(int(h) * 3600 + int(mi) * 60 + float(s), 3)

    usage = payload.get("usage") or {}
    cost = float(usage.get("cost_rub") or 0.0)
    rec = {"line": n, "scene": ln["scene"], "file": f"audio/{wav.name}",
           "text": text, "chars": len(text), "voice": VOICE,
           "model": payload.get("model", MODEL),
           "api_duration_s": payload.get("duration"), "duration_s": dur,
           "slot_sec": ln["duration_sec"], "cost_rub": round(cost, 6),
           "usage": usage, "request_seconds": round(dt, 2),
           "requested_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    (LOGS / "tts").mkdir(parents=True, exist_ok=True)
    log.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    total += cost
    out["lines"].append(rec)
    print(f"line {n}: {len(text):3d} chars {dur:5.2f}s {cost:.4f} RUB in {dt:.1f}s")

out["totals"] = {"lines": len(out["lines"]),
                 "chars": sum(x["chars"] for x in out["lines"]),
                 "duration_s": round(sum(x["duration_s"] or 0 for x in out["lines"]), 3),
                 "cost_rub": round(total, 6)}
(LOGS / "tts.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("total:", out["totals"])
print(f"whole assignment so far: {46.6996 + total:.4f} RUB")
