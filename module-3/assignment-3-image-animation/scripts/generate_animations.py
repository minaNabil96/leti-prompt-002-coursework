"""Step 3 — animate the three sources with bytedance/seedance-2-mini (image-to-video).

Polza.ai Media API: POST /api/v1/media, poll GET /api/v1/media/{id}.
Intensity is set by the prompt: minimal (portrait), medium (landscape), maximum (painting).
"""
import argparse
import base64
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

MODEL = "bytedance/seedance-2-mini"
DURATION = "5"
RESOLUTION = "480p"
MAX_COST = 20.0

JOBS = [
    {
        "name": "animation_01_portrait",
        "source": "sources/source_01_portrait.png",
        "intensity": "минимальная",
        "prompt": ("Subtle animation: the woman blinks once slowly, tilts her head slightly to the right, "
                   "and forms a gentle smile. Minimal movement, natural breathing motion."),
    },
    {
        "name": "animation_02_landscape",
        "source": "sources/source_02_landscape.png",
        "intensity": "средняя",
        "prompt": ("Clouds drift slowly from left to right, water surface ripples gently with reflections, "
                   "pine branches sway in a light breeze. Two moving elements only, medium intensity."),
    },
    {
        "name": "animation_03_painting",
        "source": "sources/source_03_painting.jpg",
        "intensity": "максимальная",
        "prompt": ("Maximum dynamic animation: the swirling sky rotates and pulses, stars twinkle brightly, "
                   "the cypress tree sways dramatically, village lights flicker, the moon glows intensely. "
                   "Full transformation."),
    },
]


def data_b64(path):
    return base64.b64encode(path.read_bytes()).decode()


def create_and_wait(payload, timeout=900):
    t0 = time.time()
    r = requests.post(f"{API}/media", headers=HEADERS, json=payload, timeout=180)
    if not r.ok:
        return None, None, f"create HTTP {r.status_code}: {r.text[:800]}"
    obj = r.json()
    while obj.get("status") in ("pending", "processing"):
        if time.time() - t0 > timeout:
            return None, None, f"timeout id={obj.get('id')} status={obj.get('status')}"
        time.sleep(5)
        s = requests.get(f"{API}/media/{obj['id']}", headers=HEADERS, timeout=60)
        if not s.ok:
            return None, None, f"poll HTTP {s.status_code}: {s.text[:300]}"
        obj = s.json()
    if obj.get("status") != "completed":
        return obj, time.time() - t0, f"status={obj.get('status')} " \
                                      f"{json.dumps(obj.get('error'), ensure_ascii=False)}"
    return obj, time.time() - t0, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()

    (ROOT / "logs" / "gen").mkdir(parents=True, exist_ok=True)
    (ROOT / "animations").mkdir(exist_ok=True)
    total = 0.0
    for job in JOBS:
        if args.only and job["name"] not in args.only:
            continue
        out = ROOT / "animations" / (job["name"] + ".mp4")
        log = ROOT / "logs" / "gen" / (job["name"] + ".json")
        if out.exists() and log.exists():
            rec = json.loads(log.read_text(encoding="utf-8"))
            total += float(rec.get("cost_rub", 0) or 0)
            print(f"{job['name']}: exists, skip ({rec.get('cost_rub')} RUB)")
            continue

        src = ROOT / job["source"]
        payload = {
            "model": MODEL,
            "input": {
                "prompt": job["prompt"],
                "images": [{"type": "base64", "data": data_b64(src)}],
                "duration": DURATION,
                "resolution": RESOLUTION,
                "aspect_ratio": "auto",
                "generate_audio": False,
            },
        }
        sent = {"model": MODEL, "input": {**payload["input"], "images": [{"type": "base64",
                "data": f"<{len(data_b64(src))} base64 chars>"}]}}
        print(f"{job['name']}: posting...", flush=True)
        obj, elapsed, err = create_and_wait(payload)
        if err:
            (ROOT / "logs" / "gen" / (job["name"] + "_error.json")).write_text(
                json.dumps({"request": sent, "error": err, "response": obj},
                           ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"{job['name']}: ERROR {err}", flush=True)
            sys.exit(2)
        cost = float((obj.get("usage") or {}).get("cost_rub", 0) or 0)
        if cost > MAX_COST:
            sys.exit(f"ABORT {job['name']}: billed {cost} RUB > {MAX_COST}")
        item = obj.get("data")
        if isinstance(item, list):
            item = item[0] if item else {}
        item = item or {}
        url = item.get("url")
        if not url:
            sys.exit(f"{job['name']}: no video url in {obj}")
        blob = requests.get(url, timeout=600).content
        out.write_bytes(blob)
        rec = {
            "file": out.name, "model": MODEL, "source": job["source"],
            "intensity": job["intensity"], "prompt": job["prompt"],
            "duration_param": DURATION, "resolution": RESOLUTION,
            "cost_rub": cost, "elapsed_sec": round(elapsed, 2),
            "bytes": len(blob), "video_url": url, "request_id": obj.get("id"),
            "created": obj.get("created"), "completed_at": obj.get("completed_at"),
            "requested_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "usage": obj.get("usage"), "data": item, "warnings": obj.get("warnings"),
            "request": sent,
        }
        log.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        total += cost
        print(f"{job['name']}: {len(blob)} B {cost} RUB {elapsed:.1f}s -> {out.name}", flush=True)
    print(f"TOTAL {total:.2f} RUB")


if __name__ == "__main__":
    main()
