"""Step 2 — generate the two AI source images (S1 portrait, S2 landscape).

Media API: POST /api/v1/media with {"model", "input": {...}}, then poll
GET /api/v1/media/{id} until status == completed. Each call is 1,40 RUB.
S3 (Van Gogh) is downloaded separately from Wikimedia Commons.
"""
import base64
import io
import json
import pathlib
import sys
import time

import requests
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJ = ROOT.parent
SRC = ROOT / "sources"
LOGS = ROOT / "logs" / "gen"
API = "https://polza.ai/api/v1"
KEY = (PROJ / "ref-analysis" / ".polza_key").read_text(encoding="utf-8").strip()
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

MODEL = "tongyi-mai/z-image"
MAX_COST = 2.0

JOBS = [
    ("source_01_portrait.png", "1:1",
     "A professional portrait of a young woman with short dark hair, soft natural lighting, "
     "neutral grey background, looking directly at the camera, photorealistic, high detail"),
    ("source_02_landscape.png", "16:9",
     "A serene mountain lake at sunset with gentle pink clouds, calm water with subtle reflections, "
     "pine trees on the shore, warm golden light, photorealistic landscape"),
]


def create_and_wait(prompt, aspect, timeout=420):
    payload = {"model": MODEL, "input": {"prompt": prompt, "aspect_ratio": aspect}}
    t0 = time.time()
    r = requests.post(f"{API}/media", headers=HEADERS, json=payload, timeout=180)
    if not r.ok:
        return None, None, f"create HTTP {r.status_code}: {r.text[:600]}"
    obj = r.json()
    while obj.get("status") in ("pending", "processing"):
        if time.time() - t0 > timeout:
            return None, None, f"timeout id={obj.get('id')}"
        time.sleep(3)
        obj = requests.get(f"{API}/media/{obj['id']}", headers=HEADERS, timeout=60).json()
    if obj.get("status") != "completed":
        return None, None, f"status={obj.get('status')} {json.dumps(obj.get('error'), ensure_ascii=False)}"
    return obj, time.time() - t0, None


def main():
    SRC.mkdir(exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    total = 0.0
    for name, aspect, prompt in JOBS:
        out = SRC / name
        log = LOGS / (name.replace(".png", "") + ".json")
        if out.exists() and log.exists():
            rec = json.loads(log.read_text(encoding="utf-8"))
            total += float(rec.get("cost_rub", 0))
            print(f"{name}: exists, skip ({rec.get('cost_rub')} RUB)")
            continue
        obj, elapsed, err = create_and_wait(prompt, aspect)
        if err:
            print(f"{name}: ERROR {err}", flush=True)
            sys.exit(1)
        cost = float((obj.get("usage") or {}).get("cost_rub", 0) or 0)
        if cost > MAX_COST:
            sys.exit(f"ABORT: {name} billed {cost} RUB")
        item = (obj.get("data") or [{}])[0]
        if item.get("b64_json"):
            blob = base64.b64decode(item["b64_json"])
        else:
            blob = requests.get(item["url"], timeout=240).content
        out.write_bytes(blob)
        im = Image.open(io.BytesIO(blob))
        rec = {
            "file": name, "model": MODEL, "aspect_ratio": aspect, "prompt": prompt,
            "cost_rub": cost, "elapsed_sec": round(elapsed, 2), "size": list(im.size),
            "bytes": len(blob), "request_id": obj.get("id"),
            "created": obj.get("created"), "completed_at": obj.get("completed_at"),
            "requested_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "usage": obj.get("usage"),
        }
        log.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        total += cost
        print(f"{name}: {im.size} {len(blob)} B {cost} RUB {elapsed:.1f}s", flush=True)
    print(f"TOTAL {total:.2f} RUB")


if __name__ == "__main__":
    main()
