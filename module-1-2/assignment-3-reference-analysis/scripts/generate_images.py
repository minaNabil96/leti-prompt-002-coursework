"""Step 5 — generate both images with the SAME model, size and seed.

Only the prompt differs: detailed (composed by Gemini) vs naive ("A cat in the rain").
Uses the Polza.ai Media API (POST /api/v1/media + polling).
"""
import base64
import io
import json
import pathlib
import re
import time

import requests
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"
SHOTS = ROOT / "screenshots"
API = "https://polza.ai/api/v1"
KEY = (ROOT / ".polza_key").read_text().strip()
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

MODEL = "bytedance/seedream-4"
SEED = 42
BUDGET_PER_CALL = 5.0


def clean_prompt(raw: str) -> str:
    """Drop the chat wrapper ("Вот промпт...", "**Prompt:**") and markdown asterisks."""
    text = raw.strip()
    marker = re.search(r"\*\*Prompt:\*\*|\*\*Промпт:\*\*|Prompt:", text, re.IGNORECASE)
    if marker:
        text = text[marker.end():]
    text = text.replace("**", "").replace("*", "")
    return " ".join(text.split()).strip()


def create_and_wait(prompt, extra, poll_timeout=420):
    payload = {"model": MODEL, "input": {"prompt": prompt, "aspect_ratio": "1:1", **extra}}
    t0 = time.time()
    r = requests.post(f"{API}/media", headers=HEADERS, json=payload, timeout=180)
    if not r.ok:
        return None, None, f"create HTTP {r.status_code}: {r.text[:800]}"
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
    detailed_raw = (LOGS / "composed_prompt.txt").read_text(encoding="utf-8")
    detailed = clean_prompt(detailed_raw)
    naive = (LOGS / "naive_prompt.txt").read_text(encoding="utf-8").strip()

    (LOGS / "prompt_used_detailed.txt").write_text(detailed, encoding="utf-8")

    for label, prompt, extra in [
        ("detailed", detailed, {"image_resolution": "1K", "seed": SEED}),
        ("naive", naive, {"image_resolution": "1K", "seed": SEED}),
    ]:
        print(f"[gen ] {label}: {prompt[:80]}...", flush=True)
        obj, elapsed, err = create_and_wait(prompt, extra)
        if err and "seed" in err.lower():
            print("   seed rejected, retrying without seed", flush=True)
            extra = {k: v for k, v in extra.items() if k != "seed"}
            obj, elapsed, err = create_and_wait(prompt, extra)
        if err:
            raise RuntimeError(f"{label}: {err}")

        cost = float((obj.get("usage") or {}).get("cost_rub", 0) or 0)
        if cost > BUDGET_PER_CALL:
            raise SystemExit(f"ABORT: {label} billed {cost} RUB > {BUDGET_PER_CALL} RUB")

        data = obj.get("data") or []
        if not data:
            raise RuntimeError(f"no data in response: {obj}")
        item = data[0]
        if item.get("b64_json"):
            img_bytes = base64.b64decode(item["b64_json"])
        else:
            dl = requests.get(item["url"], timeout=240)
            dl.raise_for_status()
            img_bytes = dl.content

        img_path = SHOTS / f"img_gen_{label}.png"
        img_path.write_bytes(img_bytes)
        im = Image.open(io.BytesIO(img_bytes))

        (LOGS / f"gen_{label}.json").write_text(json.dumps({
            "label": label,
            "model": MODEL,
            "architecture": "Diffusion (rectified flow DiT, ByteDance Seedream 4.0)",
            "size_requested": "1:1 (1K, 1024x1024)",
            "seed_requested": extra.get("seed"),
            "prompt": prompt,
            "prompt_raw_response": detailed_raw if label == "detailed" else naive,
            "billed_rub": cost,
            "elapsed_sec": round(elapsed, 2),
            "image_size": list(im.size),
            "usage_obj": obj.get("usage"),
            "request_id": obj.get("id"),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S%z"),
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[ ok ] {label}: {im.size}, {len(img_bytes)} bytes, {cost} RUB, {elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    main()
