"""Step 3 — five text-to-video scenes with grok-imagine-video-1-5.

Polza.ai Media API: POST /api/v1/media {"model", "input": {...}} then poll
GET /api/v1/media/{id} until status == "completed".

Budget guard: the script stops before a request whose worst-case price would
push the whole assignment above BUDGET_RUB (60 ₽ by the assignment text).
Every finished scene keeps its own JSON with the real billed cost, so re-runs
resume instead of paying twice.
"""
import argparse
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

MODEL = "grok-imagine-video-1-5"
RESOLUTION = "480p"          # 1,62 ₽/с; the film is upscaled to 1080p in FFmpeg
ASPECT = "16:9"
PRICE_PER_SEC = 1.62         # from the live catalogue (tier resolution=480p)
BUDGET_RUB = 60.0
ALREADY_SPENT = 7.8164       # LLM iterations 1-5 (1,3364) + rejected scene 1 (6,48)
VIDEO_BUDGET = 40.0          # cap for the video stage itself
MAX_WAIT = 900

STORY = json.loads((ROOT / "scripts" / "storyboard.json").read_text(encoding="utf-8"))
VOICE = json.loads((ROOT / "scripts" / "voiceover.json").read_text(encoding="utf-8"))
PROMPTS = json.loads((ROOT / "scripts" / "video_prompts.json").read_text(encoding="utf-8"))
SCENES = STORY["scenes"][:5]          # scene 6 is the title card, built locally


def create_and_wait(payload, timeout=MAX_WAIT):
    t0 = time.time()
    r = requests.post(f"{API}/media", headers=HEADERS, json=payload, timeout=180)
    if not r.ok:
        return None, None, f"create HTTP {r.status_code}: {r.text[:800]}"
    obj = r.json()
    while obj.get("status") in ("pending", "processing", "queued"):
        if time.time() - t0 > timeout:
            return obj, time.time() - t0, f"timeout id={obj.get('id')}"
        time.sleep(5)
        s = requests.get(f"{API}/media/{obj['id']}", headers=HEADERS, timeout=60)
        if not s.ok:
            return obj, time.time() - t0, f"poll HTTP {s.status_code}: {s.text[:300]}"
        obj = s.json()
    if obj.get("status") != "completed":
        return obj, time.time() - t0, (f"status={obj.get('status')} "
                                       f"{json.dumps(obj.get('error'), ensure_ascii=False)}")
    return obj, time.time() - t0, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", type=int)
    ap.add_argument("--budget-check", action="store_true")
    args = ap.parse_args()

    (ROOT / "scenes").mkdir(exist_ok=True)
    (ROOT / "logs" / "video").mkdir(parents=True, exist_ok=True)

    planned = [s for s in SCENES if not args.only or s["n"] in args.only]
    worst = sum(s["duration_sec"] for s in planned) * PRICE_PER_SEC
    print(f"planned: {len(planned)} scenes, {sum(s['duration_sec'] for s in planned)} s, "
          f"worst case {worst:.2f} RUB")
    if ALREADY_SPENT + worst > BUDGET_RUB:
        sys.exit(f"ABORT: {ALREADY_SPENT} + {worst:.2f} exceeds {BUDGET_RUB} RUB")
    if args.budget_check:
        return

    total = 0.0
    for sc in planned:
        out = ROOT / "scenes" / f"scene_{sc['n']:02d}.mp4"
        log = ROOT / "logs" / "video" / f"scene_{sc['n']:02d}.json"
        if out.exists() and log.exists():
            rec = json.loads(log.read_text(encoding="utf-8"))
            total += float(rec.get("cost_rub", 0) or 0)
            print(f"scene {sc['n']}: exists, skip ({rec.get('cost_rub')} RUB)")
            continue

        duration = int(sc["duration_sec"])
        prompt = PROMPTS["scenes"][str(sc["n"])]["final"]
        payload = {"model": MODEL, "input": {"prompt": prompt, "duration": str(duration),
                                             "resolution": RESOLUTION,
                                             "aspect_ratio": ASPECT}}
        print(f"\nscene {sc['n']} «{sc['scene']}» {duration}s:", flush=True)
        print("  prompt:", prompt, flush=True)
        obj, elapsed, err = create_and_wait(payload)
        if err:
            (ROOT / "logs" / "video" / f"scene_{sc['n']:02d}_error.json").write_text(
                json.dumps({"request": payload, "error": err, "response": obj},
                           ensure_ascii=False, indent=2), encoding="utf-8")
            print("  ERROR:", err, flush=True)
            sys.exit(2)

        cost = float((obj.get("usage") or {}).get("cost_rub", 0) or 0)
        item = obj.get("data")
        if isinstance(item, list):
            item = item[0] if item else {}
        item = item or {}
        url = item.get("url") or item.get("video_url")
        if not url:
            sys.exit(f"scene {sc['n']}: no url in {json.dumps(obj)[:600]}")
        blob = requests.get(url, timeout=600).content
        out.write_bytes(blob)
        rec = {"scene": sc["n"], "name": sc["scene"], "file": f"scenes/{out.name}",
               "model": MODEL, "prompt": prompt,
               "prompt_initial": PROMPTS["scenes"][str(sc["n"])]["initial"],
               "prompt_change_reason": PROMPTS["scenes"][str(sc["n"])]["reason"],
               "duration_param": duration,
               "resolution_param": RESOLUTION, "aspect_ratio": ASPECT,
               "cost_rub": cost, "elapsed_sec": round(elapsed, 2),
               "bytes": len(blob), "video_url": url, "request_id": obj.get("id"),
               "created": obj.get("created"), "completed_at": obj.get("completed_at"),
               "requested_at": time.strftime("%Y-%m-%d %H:%M:%S"),
               "usage": obj.get("usage"), "data": item, "request": payload,
               "voiceover": next(x["text"] for x in VOICE["lines"] if x["n"] == sc["n"])}
        log.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        total += cost
        print(f"  ok: {len(blob)/1024:.0f} KB, {cost:.4f} RUB, {elapsed:.0f}s -> {out.name}",
              flush=True)

    print(f"\nTOTAL video cost this run: {total:.2f} RUB")
    print(f"Whole assignment so far: {ALREADY_SPENT + total:.2f} RUB")


if __name__ == "__main__":
    main()
