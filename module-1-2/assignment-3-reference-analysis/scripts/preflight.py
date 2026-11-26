"""Pre-flight for Assignment 3: key, API, models, balance, download reference."""
import json
import pathlib
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = (ROOT / ".polza_key").read_text().strip()
BASE = "https://polza.ai/api/v1"
H = {"Authorization": f"Bearer {KEY}"}

print("key prefix:", KEY[:4], "len:", len(KEY))

r = requests.get(f"{BASE}/models", headers=H, timeout=60)
print("models:", r.status_code)
models = r.json()
if isinstance(models, dict):
    models = models.get("data", models)
ids = {m.get("id") for m in models if isinstance(m, dict)}
print("model count:", len(ids))
for want in ("google/gemini-2.5-flash", "bytedance/seedream-4", "openai/gpt-4o", "tongyi-mai/z-image"):
    print(f"  {want}: {'FOUND' if want in ids else 'MISSING'}")

b = requests.get(f"{BASE}/balance", headers=H, timeout=30)
print("balance:", b.status_code, b.text[:160])

# download the reference image
SHOTS = ROOT / "screenshots"
url = ("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/"
       "Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/"
       "1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg")
ua = {"User-Agent": "LETI-coursework/1.0 (student assignment; contact: student@example.com)"}
raw = SHOTS / "reference_raw.jpg"
for attempt in range(1, 4):
    try:
        resp = requests.get(url, headers=ua, timeout=120)
        print(f"download attempt {attempt}: HTTP {resp.status_code}, {len(resp.content)} bytes")
        if resp.ok and len(resp.content) > 50_000:
            raw.write_bytes(resp.content)
            break
    except Exception as exc:  # noqa: BLE001
        print("download error:", exc)
    time.sleep(3)

from PIL import Image

im = Image.open(raw)
print("raw image:", im.format, im.size, im.mode)

im = im.convert("RGB")
scale = 1024 / max(im.size)
if scale < 1:
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
im.save(SHOTS / "reference_1024.jpg", quality=92)
print("reference_1024.jpg:", im.size)

(ROOT / "logs" / "preflight.json").write_text(json.dumps({
    "checked_at": time.strftime("%Y-%m-%d %H:%M:%S%z"),
    "models_found": sorted(x for x in ids if x in {
        "google/gemini-2.5-flash", "bytedance/seedream-4", "openai/gpt-4o", "tongyi-mai/z-image"}),
    "balance": b.json() if b.ok else b.text,
    "reference_bytes": raw.stat().st_size,
    "reference_size_1024": list(im.size),
}, ensure_ascii=False, indent=2), encoding="utf-8")
print("preflight.json written")
