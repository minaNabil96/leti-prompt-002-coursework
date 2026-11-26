"""Demo D1: object detection with facebook/detr-resnet-50 on a CC0 street photo.

The Hugging Face Inference API requires an account token (HTTP 401 without it) and
the online widget asks to log in, so the very same checkpoint is run locally with
transformers on CPU. Input and model are real; results are not fabricated.
"""
import json
import pathlib
import time

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEMO = ROOT / "logs" / "demo_results"
DEMO.mkdir(parents=True, exist_ok=True)

IMAGE = DEMO / "test_image.jpg"
IMAGE_URL = ("https://thumb.wikimedia.org/wikipedia/commons/thumb/2/2a/"
             "Photo_of_biking_people_with_kids_in_a_sunny_street_in_Spring_in_"
             "Amsterdam_-_street_photography_of_The_Netherlands_by_Fons_"
             "Heijnsbroek%2C_2026_-_free_street_photography_in_high_resolutions_"
             "tiff.tif/lossy-page1-960px-thumbnail.tif.jpg")
IMAGE_PAGE = ("https://commons.wikimedia.org/wiki/File:Photo_of_biking_people_"
              "with_kids_in_a_sunny_street_in_Spring_in_Amsterdam_-_street_"
              "photography_of_The_Netherlands_by_Fons_Heijnsbroek,_2026_-_free_"
              "street_photography_in_high_resolutions_tiff.tif")
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\times.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
]


def font(size):
    for p in FONT_CANDIDATES:
        if pathlib.Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()


def ensure_image():
    if IMAGE.exists():
        return
    import requests
    r = requests.get(IMAGE_URL, timeout=90,
                     headers={"User-Agent": "leti-coursework-a6/1.0"})
    r.raise_for_status()
    IMAGE.write_bytes(r.content)


def main():
    from transformers import pipeline

    ensure_image()
    img = Image.open(IMAGE).convert("RGB")
    print("input", img.size)

    t0 = time.time()
    detector = pipeline("object-detection", model="facebook/detr-resnet-50",
                        device=-1)
    load_s = time.time() - t0
    t1 = time.time()
    raw = detector(img, threshold=0.1)
    infer_s = time.time() - t1
    print("loaded in %.1fs, inference %.1fs" % (load_s, infer_s))

    rows = []
    for d in raw:
        box = d["box"]
        rows.append({
            "label": d["label"],
            "score": round(float(d["score"]), 4),
            "box": {"xmin": round(box["xmin"], 1), "ymin": round(box["ymin"], 1),
                    "xmax": round(box["xmax"], 1), "ymax": round(box["ymax"], 1)},
        })
    display_threshold = 0.9
    detections = [r for r in rows if r["score"] >= display_threshold]
    counts = {str(t): sum(1 for r in rows if r["score"] >= t)
              for t in (0.5, 0.7, 0.8, 0.9, 0.95)}
    print("counts", counts)

    (DEMO / "D1.json").write_text(json.dumps({
        "model": "facebook/detr-resnet-50",
        "run_mode": "local transformers pipeline (CPU), same checkpoint as the card",
        "reason": "HF Inference API returns HTTP 401 without a token; online widget asks to log in",
        "threshold": display_threshold,
        "counts_by_threshold": counts,
        "input_file": "test_image.jpg",
        "input_url": IMAGE_URL,
        "input_page": IMAGE_PAGE,
        "input_license": "CC0 (Wikimedia Commons, автор Fons Heijnsbroek, 2026)",
        "input_description": "Солнечная улица Амстердама: велосипедисты, грузовой велосипед с детьми, пешеходы, автомобили и дома",
        "image_size": list(img.size),
        "model_load_seconds": round(load_s, 1),
        "inference_seconds": round(infer_s, 1),
        "detections": detections,
        "detections_all": rows,
        "count": len(detections),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    annotated = img.copy()
    draw = ImageDraw.Draw(annotated)
    f = font(16)
    palette = [(220, 40, 40), (30, 110, 220), (20, 150, 90), (200, 120, 20)]
    for i, d in enumerate(detections):
        b = d["box"]
        color = palette[i % len(palette)]
        draw.rectangle([b["xmin"], b["ymin"], b["xmax"], b["ymax"]],
                       outline=color, width=3)
        text = f'{d["label"]} {d["score"]:.2f}'
        tw = draw.textlength(text, font=f)
        ty = max(0, b["ymin"] - 20)
        draw.rectangle([b["xmin"], ty, b["xmin"] + tw + 6, ty + 20], fill=color)
        draw.text((b["xmin"] + 3, ty + 1), text, fill=(255, 255, 255), font=f)
    annotated.save(DEMO / "D1_annotated.jpg", quality=92)
    print("detected", len(detections))


if __name__ == "__main__":
    main()

