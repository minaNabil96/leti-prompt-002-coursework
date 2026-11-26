"""Fetch metadata + README + task counts from the public Hugging Face API."""
import json
import pathlib
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
META = ROOT / "logs" / "model_metadata"
META.mkdir(parents=True, exist_ok=True)

MODELS = [
    ("M1", "facebook/detr-resnet-50"),
    ("M2", "dima806/facial_emotions_image_detection"),
    ("M3", "facebook/musicgen-small"),
    ("M4", "Salesforce/codegen-350M-mono"),
    ("M5", "cardiffnlp/twitter-roberta-base-sentiment"),
    ("M6", "d4data/biomedical-ner-all"),
]

TAGS = [
    "object-detection", "image-classification", "face-recognition",
    "image-segmentation", "text-to-image", "text-to-audio",
    "text-generation", "code-generation", "text-classification",
    "token-classification", "sentiment-analysis", "tabular-classification",
]

S = requests.Session()
S.headers["User-Agent"] = "leti-coursework-a6/1.0"


def get(url, **kw):
    for attempt in range(4):
        r = S.get(url, timeout=90, **kw)
        if r.status_code == 429:
            time.sleep(5 * (attempt + 1))
            continue
        return r
    return r


def main():
    checks = {}
    for mid, model_id in MODELS:
        r = get(f"https://huggingface.co/api/models/{model_id}")
        print(mid, model_id, r.status_code)
        checks[mid] = {"id": model_id, "status": r.status_code}
        if r.status_code != 200:
            continue
        (META / f"{mid}.json").write_text(
            json.dumps(r.json(), ensure_ascii=False, indent=2), encoding="utf-8")
        rr = get(f"https://huggingface.co/{model_id}/raw/main/README.md")
        print("  readme", rr.status_code, len(rr.content))
        checks[mid]["readme_status"] = rr.status_code
        if rr.status_code == 200:
            (META / f"{mid}_readme.md").write_text(rr.text, encoding="utf-8")
        time.sleep(0.5)

    counts = {}
    for tag in TAGS:
        r = get("https://huggingface.co/api/models",
                params={"filter": tag, "limit": 1000, "full": "false"})
        n = len(r.json()) if r.status_code == 200 else None
        exhausted = n is not None and n < 1000
        counts[tag] = {"status": r.status_code, "sampled": n,
                       "exact": n if exhausted else None}
        print("tag", tag, r.status_code, n)
        time.sleep(0.3)

    r = get("https://huggingface.co/api/models", params={"limit": 1})
    total_sample = r.json() if r.status_code == 200 else []

    (META / "_catalog.json").write_text(json.dumps({
        "fetched_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "models": checks,
        "task_samples": counts,
        "first_model_sample": total_sample,
    }, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
