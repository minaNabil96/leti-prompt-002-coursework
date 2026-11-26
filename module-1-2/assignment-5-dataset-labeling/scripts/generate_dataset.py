"""Assignment 5 — generate 24 dataset images via Polza.ai (tongyi-mai/z-image).

Resumable: skips images already on disk. Each call costs 1.40 RUB.
"""
import argparse
import base64
import io
import json
import pathlib
import time

import requests
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"
LOGS = ROOT / "logs"
API = "https://polza.ai/api/v1"
KEY = (ROOT / ".polza_key").read_text().strip()
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

MODEL = "tongyi-mai/z-image"
ASPECT = "3:4"
MAX_COST_PER_CALL = 2.0

PROMPTS = [
    ("афиша", "A poster for a rock music concert, featuring a band name in large bold text, date and venue information at the bottom, vibrant red and black colors"),
    ("афиша", "A poster for an art exhibition, showing a sample painting, exhibition title, gallery name, dates November 2026"),
    ("афиша", "A poster for a theater performance, artistic illustration of a stage, play title, date and time, venue address"),
    ("афиша", "A poster for a university lecture, clean design, speaker name, lecture title, date, auditorium number"),
    ("афиша", "A poster for a film festival, cinematic collage, festival name, dates, list of participating countries"),
    ("афиша", "A poster for a sports event, basketball tournament, dynamic action image, event name, dates, stadium"),
    ("афиша", "A poster for a food festival, illustrated food image, festival name, dates, location, entry fee"),
    ("афиша", "A poster for a stand-up comedy show, comedian photo, show name, date, club name and address"),
    ("обложка книги", "A book cover for a fantasy novel, illustrated dragon and castle, book title 'The Last Realm', author name, publisher logo"),
    ("обложка книги", "A book cover for a science textbook, clean minimal design, title 'Quantum Physics', author names, university press logo"),
    ("обложка книги", "A book cover for a biography, portrait photo of the subject, title 'A Life in Science', author name"),
    ("обложка книги", "A book cover for a cookbook, illustrated dish, title 'Italian Kitchen', author name, photo credit"),
    ("обложка книги", "A book cover for a mystery novel, dark atmospheric image, title 'The Silent Witness', author name"),
    ("обложка книги", "A book cover for a children's book, colorful cartoon illustration, title 'The Adventures of Pip', author and illustrator names"),
    ("обложка книги", "A book cover for a self-help book, simple geometric design, title 'Focus', author name, testimonial quote"),
    ("обложка книги", "A book cover for an academic monograph, serious typographic design, title 'Media Theory', author name, university press"),
    ("постер фильма", "A movie poster for a sci-fi action film, dramatic character composition with spaceship, film title 'STELLAR', credits block at bottom listing director and cast, release date"),
    ("постер фильма", "A movie poster for a romantic comedy, two lead characters back to back, film title 'LOVE UNEXPECTED', credits block, coming soon"),
    ("постер фильма", "A movie poster for a horror film, dark eerie image, film title 'THE LAST NIGHT', credits block, release date October"),
    ("постер фильма", "A movie poster for a documentary, striking real-world image, film title 'CODE OF SILENCE', credits block, festival laurels"),
    ("постер фильма", "A movie poster for an animated family film, colorful cartoon character, film title 'SKY JUMPERS', credits block, release date"),
    ("постер фильма", "A movie poster for a thriller, intense close-up of protagonist, film title 'EDGE OF DARK', credits block, coming soon"),
    ("постер фильма", "A movie poster for a historical drama, period costume scene, film title 'THE EMPRESS', credits block, release date"),
    ("постер фильма", "A movie poster for a comedy, humorous character pose, film title 'OFFICE DISASTER', credits block, release date"),
]


def create_and_wait(prompt, poll_timeout=300):
    payload = {"model": MODEL, "input": {"prompt": prompt, "aspect_ratio": ASPECT}}
    t0 = time.time()
    r = requests.post(f"{API}/media", headers=HEADERS, json=payload, timeout=180)
    if not r.ok:
        return None, None, f"create HTTP {r.status_code}: {r.text[:600]}"
    obj = r.json()
    while obj.get("status") in ("pending", "processing"):
        if time.time() - t0 > poll_timeout:
            return None, None, f"timeout waiting for {obj.get('id')}"
        time.sleep(3)
        s = requests.get(f"{API}/media/{obj['id']}", headers=HEADERS, timeout=60)
        s.raise_for_status()
        obj = s.json()
    if obj.get("status") != "completed":
        return None, None, f"status={obj.get('status')} error={json.dumps(obj.get('error'), ensure_ascii=False)}"
    return obj, time.time() - t0, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*", type=int)
    args = ap.parse_args()
    ids = args.ids or list(range(1, 25))

    IMAGES.mkdir(parents=True, exist_ok=True)
    (LOGS / "gen").mkdir(parents=True, exist_ok=True)
    total = 0.0
    for i in ids:
        cls, prompt = PROMPTS[i - 1]
        out = IMAGES / f"img_{i:02d}.png"
        log = LOGS / "gen" / f"gen_{i:02d}.json"
        if out.exists() and log.exists():
            print(f"P{i:02d} exists, skipping", flush=True)
            total += float(json.loads(log.read_text(encoding="utf-8")).get("billed_rub", 0))
            continue

        obj, elapsed, err = create_and_wait(prompt)
        if err:
            print(f"P{i:02d} ERROR {err}", flush=True)
            raise SystemExit(1)
        cost = float((obj.get("usage") or {}).get("cost_rub", 0) or 0)
        if cost > MAX_COST_PER_CALL:
            raise SystemExit(f"ABORT: P{i:02d} billed {cost} RUB > {MAX_COST_PER_CALL}")
        data = obj.get("data") or []
        if not data:
            raise SystemExit(f"P{i:02d}: no data")
        item = data[0]
        if item.get("b64_json"):
            img_bytes = base64.b64decode(item["b64_json"])
        else:
            dl = requests.get(item["url"], timeout=240)
            dl.raise_for_status()
            img_bytes = dl.content
        out.write_bytes(img_bytes)
        im = Image.open(io.BytesIO(img_bytes))
        rec = {
            "id": f"P{i:02d}",
            "file": out.name,
            "class": cls,
            "prompt": prompt,
            "model": MODEL,
            "aspect_ratio": ASPECT,
            "billed_rub": cost,
            "elapsed_sec": round(elapsed, 2),
            "image_size": list(im.size),
            "bytes": len(img_bytes),
            "usage_obj": obj.get("usage"),
            "request_id": obj.get("id"),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S%z"),
        }
        log.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        total += cost
        print(f"P{i:02d} {cls}: {im.size} {len(img_bytes)} B {cost} RUB {elapsed:.1f}s", flush=True)

    print(f"TOTAL {total:.2f} RUB for {len(ids)} images", flush=True)


if __name__ == "__main__":
    main()
