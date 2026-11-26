"""Generate one image per model via the Polza.ai Media API (same prompt).

Run from the image-gen-comparison directory:
    python scripts/generate.py
Set POLZA_API_KEY, or the key is read from ../opencode.json (project config).
"""
import base64
import io
import json
import os
import pathlib
import sys
import time

import requests
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
SHOTS = ROOT / "screenshots"
API = "https://polza.ai/api/v1"

MODELS = [
    # model_id, short, display, architecture, catalog price RUB, extra input params
    ("google/gemini-2.5-flash-image", "gemini-2.5-flash-image",
     "Google Gemini 2.5 Flash Image (Nano Banana 1)", "Transformer", 2.9, {}),
    ("openai/gpt-image-1.5", "gpt-image-1.5",
     "OpenAI GPT-Image 1.5", "Transformer", 3.0, {"quality": "medium"}),
    ("tongyi-mai/z-image", "z-image",
     "Alibaba Z-Image", "Diffusion", 1.4, {}),
    ("bytedance/seedream-4", "seedream-4",
     "ByteDance Seedream 4.0", "Diffusion", 3.0, {"image_resolution": "1K"}),
]

BUDGET_PER_IMAGE = 4.0


def get_key() -> str:
    key = os.environ.get("POLZA_API_KEY")
    if key:
        return key.strip()
    cfg_path = ROOT.parent / "opencode.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    return cfg["provider"]["polza"]["options"]["apiKey"].strip()


def create_and_wait(headers, model_id, prompt, extra, poll_timeout=360):
    payload = {"model": model_id, "input": {"prompt": prompt, "aspect_ratio": "1:1", **extra}}
    t0 = time.time()
    r = requests.post(f"{API}/media", headers=headers, json=payload, timeout=180)
    if not r.ok:
        raise RuntimeError(f"create HTTP {r.status_code}: {r.text[:800]}")
    obj = r.json()
    while obj.get("status") in ("pending", "processing"):
        if time.time() - t0 > poll_timeout:
            raise RuntimeError(f"timeout waiting for {obj.get('id')}")
        time.sleep(3)
        s = requests.get(f"{API}/media/{obj['id']}", headers=headers, timeout=60)
        s.raise_for_status()
        obj = s.json()
    elapsed = time.time() - t0
    if obj.get("status") != "completed":
        raise RuntimeError(f"status={obj.get('status')} error={json.dumps(obj.get('error'), ensure_ascii=False)}")
    return obj, elapsed


def main():
    key = get_key()
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    prompt = (LOGS / "prompt_en.txt").read_text(encoding="utf-8").strip()

    for model_id, short, display, arch, price, extra in MODELS:
        img_path = SHOTS / f"img_only_{short}.png"
        log_path = LOGS / f"gen_{short}.json"
        if img_path.exists() and log_path.exists():
            print(f"[skip] {short}: image and log already exist")
            continue
        print(f"[gen ] {model_id} ...", flush=True)
        try:
            obj, elapsed = create_and_wait(headers, model_id, prompt, extra)
        except Exception as exc:  # noqa: BLE001
            print(f"[FAIL] {model_id}: {exc}", flush=True)
            (LOGS / f"gen_{short}.error.txt").write_text(str(exc), encoding="utf-8")
            sys.exit(2)

        cost = float((obj.get("usage") or {}).get("cost_rub", 0) or 0)
        if cost > BUDGET_PER_IMAGE:
            (LOGS / f"gen_{short}.error.txt").write_text(
                f"ABORT: billed {cost} RUB > {BUDGET_PER_IMAGE} RUB", encoding="utf-8")
            print(f"[ABORT] {model_id}: billed {cost} RUB > {BUDGET_PER_IMAGE}", flush=True)
            sys.exit(3)

        data = obj.get("data") or []
        if not data:
            raise RuntimeError(f"no data in response: {obj}")
        item = data[0]
        if item.get("b64_json"):
            img_bytes = base64.b64decode(item["b64_json"])
        else:
            dl = requests.get(item["url"], timeout=180)
            dl.raise_for_status()
            img_bytes = dl.content
        img_path.write_bytes(img_bytes)
        im = Image.open(io.BytesIO(img_bytes))
        record = {
            "model": model_id,
            "display_name": display,
            "arch": arch,
            "catalog_price_rub": price,
            "billed_rub": cost,
            "elapsed_sec": round(elapsed, 2),
            "image_size": list(im.size),
            "usage": obj.get("usage"),
            "response": {k: v for k, v in obj.items() if k != "data"},
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S%z"),
        }
        log_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[ ok ] {short}: {im.size}, {len(img_bytes)} bytes, {cost} RUB, {elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    main()
