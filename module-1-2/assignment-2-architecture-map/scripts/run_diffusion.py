"""Step 4 — diffusion service actions (D1, D2, D3) via Polza.ai Media API.

The OpenAI-compatible /images/generations endpoint rejects some models
(e.g. Z-Image needs an explicit aspect_ratio), so we use the unified
Media API POST /api/v1/media and poll until completion.

Writes ./screenshots/img_D{1,2,3}.png and ./logs/raw_D{1,2,3}.json.
"""

import base64
import io
import json
import pathlib
import time

import requests
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = (ROOT / ".polza_key").read_text().strip()
API = "https://polza.ai/api/v1"
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

ACTIONS = [
    {
        "id": "D1",
        "model": "tongyi-mai/z-image",
        "service": "Alibaba Z-Image (via Polza)",
        "task": "Генерация изображения",
        "architecture": "Diffusion (flow-matching DiT — Scalable Single-Stream Diffusion Transformer, S3-DiT)",
        "prompt": "A red apple on a white ceramic plate, soft natural light, photorealistic, 1024x1024.",
        "extra": {},
    },
    {
        "id": "D2",
        "model": "qwen/image",
        "service": "Alibaba Qwen-Image (via Polza; замена YandexART)",
        "task": "Генерация изображения",
        "architecture": "Diffusion (latent diffusion, MMDiT — Multimodal Diffusion Transformer)",
        "prompt": "Фантастический город будущего на закате, неоновые огни, летающие машины, киберпанк-стиль.",
        "extra": {},
    },
    {
        "id": "D3",
        "model": "bytedance/seedream-4",
        "service": "ByteDance Seedream 4.0 (via Polza)",
        "task": "Генерация изображения",
        "architecture": "Diffusion (rectified flow / flow matching)",
        "prompt": "Portrait of a young woman with cyberpunk accessories, neon pink and blue lighting, ultra-detailed, 8k.",
        "extra": {"image_resolution": "1K"},
    },
]

BUDGET_PER_IMAGE = 5.0
POLL_TIMEOUT = 420


def create_and_wait(model_id, prompt, extra):
    payload = {"model": model_id, "input": {"prompt": prompt, "aspect_ratio": "1:1", **extra}}
    t0 = time.time()
    r = requests.post(f"{API}/media", headers=HEADERS, json=payload, timeout=180)
    if not r.ok:
        raise RuntimeError(f"create HTTP {r.status_code}: {r.text[:800]}")
    obj = r.json()
    while obj.get("status") in ("pending", "processing"):
        if time.time() - t0 > POLL_TIMEOUT:
            raise RuntimeError(f"timeout waiting for {obj.get('id')}")
        time.sleep(3)
        s = requests.get(f"{API}/media/{obj['id']}", headers=HEADERS, timeout=60)
        s.raise_for_status()
        obj = s.json()
    elapsed = time.time() - t0
    if obj.get("status") != "completed":
        raise RuntimeError(
            f"status={obj.get('status')} error={json.dumps(obj.get('error'), ensure_ascii=False)}"
        )
    return obj, elapsed


def wait_with_retry(model_id, prompt, extra, attempts=5, pause=15):
    last = None
    for i in range(1, attempts + 1):
        try:
            return create_and_wait(model_id, prompt, extra)
        except RuntimeError as exc:
            last = exc
            text = str(exc)
            if "503" in text or "SERVICE_UNAVAILABLE" in text or "timeout" in text.lower():
                print(f"    attempt {i}/{attempts} failed: {text[:140]}; retrying in {pause}s", flush=True)
                time.sleep(pause)
                continue
            raise
    raise last


failures = 0
for action in ACTIONS:
    img_path = ROOT / "screenshots" / f"img_{action['id']}.png"
    log_path = ROOT / "logs" / f"raw_{action['id']}.json"
    if img_path.exists() and log_path.exists():
        print(f"[skip] {action['id']}: already generated", flush=True)
        continue
    print(f"[gen ] {action['id']} {action['model']} ...", flush=True)
    try:
        obj, elapsed = wait_with_retry(action["model"], action["prompt"], action["extra"])
    except RuntimeError as exc:
        failures += 1
        (ROOT / "logs" / f"raw_{action['id']}.error.txt").write_text(str(exc), encoding="utf-8")
        print(f"[FAIL] {action['id']}: {str(exc)[:200]}", flush=True)
        continue
    cost = float((obj.get("usage") or {}).get("cost_rub", 0) or 0)
    if cost > BUDGET_PER_IMAGE:
        raise SystemExit(
            f"ABORT {action['id']}: billed {cost} RUB > {BUDGET_PER_IMAGE} RUB"
        )
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
    img_path = ROOT / "screenshots" / f"img_{action['id']}.png"
    img_path.write_bytes(img_bytes)
    im = Image.open(io.BytesIO(img_bytes))
    record = {
        "id": action["id"],
        "service": action["service"],
        "model": action["model"],
        "task": action["task"],
        "architecture": action["architecture"],
        "prompt": action["prompt"],
        "elapsed": round(elapsed, 2),
        "image_size": list(im.size),
        "billed_rub": cost,
        "usage": obj.get("usage"),
        "response": {k: v for k, v in obj.items() if k != "data"},
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S%z"),
    }
    (ROOT / "logs" / f"raw_{action['id']}.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"[ ok ] {action['id']}: {im.size}, {len(img_bytes)} bytes, {cost} RUB, {elapsed:.1f}s",
        flush=True,
    )

if failures:
    raise SystemExit(f"{failures} action(s) failed; see logs/raw_*.error.txt")
