"""Step 5 — background music with a generative music model on Polza.ai.

Tries google/lyria-3-pro-preview (8 ₽/запрос). If the request is rejected, the
script falls back to suno/sounds (2 ₽) and finally to google/lyria-3-clip-preview
(4 ₽). Every attempt is logged with its real cost, including failed ones.

Reads logs/voiceover_timing.json for the target length, writes audio/music.*
and logs/music.json.
"""
import json
import pathlib
import sys
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJ = ROOT.parent
API = "https://polza.ai/api/v1"
KEY = (PROJ / "ref-analysis" / ".polza_key").read_text(encoding="utf-8").strip()
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

TIMING = json.loads((ROOT / "logs" / "voiceover_timing.json").read_text(encoding="utf-8"))
TARGET_S = TIMING["film_planned_s"]
BUDGET_LEFT = 12.9          # 60 ₽ minus what the previous stages really cost

PROMPT = (
    "Ambient cinematic underscore for a short documentary about how artificial "
    "intelligence turns a text prompt into an image. Soft felt piano over warm "
    "analogue pads, slow evolving texture, gentle rise towards the end, no drums, "
    "no vocals, no melody hooks. Contemplative, hopeful, spacious. "
    f"Duration about {int(round(TARGET_S))} seconds."
)

ATTEMPTS = [
    {"model": "google/lyria-3-pro-preview", "price": 8.0,
     "input": {"prompt": PROMPT}},
    {"model": "suno/sounds", "price": 2.0,
     "input": {"prompt": PROMPT[:490], "soundLoop": False, "soundTempo": 70}},
    {"model": "google/lyria-3-clip-preview", "price": 4.0,
     "input": {"prompt": PROMPT}},
]


def wait(obj, timeout=300):
    t0 = time.time()
    while obj.get("status") in ("pending", "processing", "queued"):
        if time.time() - t0 > timeout:
            return obj, f"timeout id={obj.get('id')}"
        time.sleep(4)
        r = requests.get(f"{API}/media/{obj['id']}", headers=HEADERS, timeout=60)
        if not r.ok:
            return obj, f"poll HTTP {r.status_code}: {r.text[:200]}"
        obj = r.json()
    if obj.get("status") != "completed":
        return obj, f"status={obj.get('status')} {json.dumps(obj.get('error'), ensure_ascii=False)}"
    return obj, None


log_path = ROOT / "logs" / "music.json"
if log_path.exists():
    existing = json.loads(log_path.read_text(encoding="utf-8"))
    if existing.get("file"):
        print("music already generated:", existing["file"], existing.get("cost_rub"))
        sys.exit(0)

attempts = []
spent = 0.0
result = None
for at in ATTEMPTS:
    if spent + at["price"] > BUDGET_LEFT:
        print(f"skip {at['model']}: {spent + at['price']:.2f} > budget {BUDGET_LEFT}")
        continue
    payload = {"model": at["model"], "input": at["input"]}
    print(f"trying {at['model']} ({at['price']} RUB)...", flush=True)
    t0 = time.time()
    r = requests.post(f"{API}/media", headers=HEADERS, json=payload, timeout=120)
    rec = {"model": at["model"], "request": payload, "http": r.status_code,
           "requested_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    if not r.ok:
        rec["error"] = r.text[:600]
        attempts.append(rec)
        print("  rejected:", r.text[:200])
        continue
    obj, err = wait(r.json())
    rec["elapsed_sec"] = round(time.time() - t0, 1)
    rec["response"] = obj
    if err:
        rec["error"] = err
        attempts.append(rec)
        print("  failed:", err)
        continue
    cost = float((obj.get("usage") or {}).get("cost_rub", 0) or 0)
    item = obj.get("data")
    if isinstance(item, list):
        item = item[0] if item else {}
    item = item or {}
    url = item.get("url") or item.get("audio_url")
    if not url:
        rec["error"] = "no url in response"
        attempts.append(rec)
        print("  failed: no url")
        continue
    blob = requests.get(url, timeout=300).content
    ext = ".mp3" if (item.get("mime_type") or "").endswith("mp3") or ".mp3" in url else ".wav"
    out = ROOT / "audio" / f"music{ext}"
    out.write_bytes(blob)
    rec.update({"cost_rub": cost, "file": f"audio/{out.name}", "bytes": len(blob),
                "request_id": obj.get("id"), "data": item, "usage": obj.get("usage")})
    attempts.append(rec)
    spent += cost
    result = rec
    print(f"  ok: {len(blob)/1024:.0f} KB, {cost:.2f} RUB -> {out.name}")
    break

if not result:
    (ROOT / "logs" / "music_attempts.json").write_text(
        json.dumps(attempts, ensure_ascii=False, indent=2), encoding="utf-8")
    sys.exit("no music model produced a track; attempts are logged")

out_log = {"prompt": PROMPT, "target_duration_s": TARGET_S,
           "model": result["model"], "file": result["file"],
           "cost_rub": result["cost_rub"], "attempts": attempts,
           "total_attempt_cost_rub": round(sum(a.get("cost_rub", 0) or 0 for a in attempts), 4),
           "created": time.strftime("%Y-%m-%d %H:%M:%S")}
if len(attempts) > 1:
    out_log["note"] = "Предшествующие модели отказали; их стоимость учтена в total_attempt_cost_rub."
log_path.write_text(json.dumps(out_log, ensure_ascii=False, indent=2), encoding="utf-8")
print("music:", out_log["file"], out_log["cost_rub"], "RUB; attempts cost",
      out_log["total_attempt_cost_rub"], "RUB")
