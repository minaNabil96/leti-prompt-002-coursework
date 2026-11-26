"""Assignment 4 — download 20 real MS COCO val2017 images with official captions.

The Hugging Face dataset viewer does not support HuggingFaceM4/COCO (it runs
arbitrary Python code), and the nielsr/coco-100 mirror is unavailable. We
therefore use the official COCO endpoints:
  - captions: captions_val2017.json (downloaded from the merve/coco HF mirror)
  - images:   http://images.cocodataset.org/val2017/<id>.jpg
"""
import json
import pathlib
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
SHOTS = ROOT / "screenshots"

captions_path = LOGS / "captions_val2017.json"
data = json.loads(captions_path.read_text(encoding="utf-8"))
print("annotations:", len(data["annotations"]), "images:", len(data["images"]))

by_image = {}
for ann in data["annotations"]:
    by_image.setdefault(ann["image_id"], []).append(ann["caption"])

image_ids = sorted(by_image)
# Evenly spaced across the file for scene variety; deterministic and reproducible.
step = len(image_ids) // 20
picked = [image_ids[i * step] for i in range(20)]

meta_by_id = {im["id"]: im for im in data["images"]}

examples = []
sess = requests.Session()
sess.headers["User-Agent"] = "LETI-coursework/1.0 (dataset analysis)"
for idx, img_id in enumerate(picked, 1):
    info = meta_by_id[img_id]
    fname = info["file_name"]
    url = f"http://images.cocodataset.org/val2017/{fname}"
    out = SHOTS / f"example_{idx:02d}.jpg"
    if not out.exists() or out.stat().st_size < 5000:
        r = sess.get(url, timeout=60)
        r.raise_for_status()
        out.write_bytes(r.content)
    captions = by_image[img_id]
    examples.append({
        "id": idx,
        "coco_image_id": img_id,
        "file_name": fname,
        "image_path": f"example_{idx:02d}.jpg",
        "source_url": url,
        "width": info["width"],
        "height": info["height"],
        "image_size_kb": round(out.stat().st_size / 1024, 1),
        "captions": captions,
        "caption": captions[0],
    })
    print(f"#{idx:02d} {fname} {info['width']}x{info['height']} {out.stat().st_size//1024} KB | {captions[0][:70]}")
    time.sleep(0.2)

(LOGS / "examples.json").write_text(json.dumps(examples, ensure_ascii=False, indent=2),
                                    encoding="utf-8")
(LOGS / "examples_raw.json").write_text(json.dumps({
    "source": "COCO val2017 official annotations (captions_val2017.json)",
    "selection": "20 images evenly spaced across sorted image ids",
    "images": examples,
}, ensure_ascii=False, indent=2), encoding="utf-8")
print("saved logs/examples.json")
