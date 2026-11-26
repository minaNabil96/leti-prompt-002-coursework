import json
import pathlib

import requests

BASE = "https://polza.ai/api/v1"
KEY = pathlib.Path(__file__).resolve().parent.parent.joinpath(".polza_key").read_text().strip()
H = {"Authorization": f"Bearer {KEY}"}

r = requests.get(f"{BASE}/models", headers=H, timeout=60)
items = r.json()
if isinstance(items, dict):
    items = items.get("data", items)
by_id = {m.get("id"): m for m in items if isinstance(m, dict)}

for mid in [
    "openai/gpt-4o",
    "yandex/yandexgpt-5-lite",
    "yandex/yandexgpt-5-pro",
    "yandex/yandexgpt-5.1-pro",
    "google/gemini-2.5-flash",
    "tongyi-mai/z-image",
    "yandex/yandex-art",
    "bytedance/seedream-4",
]:
    m = by_id.get(mid)
    if not m:
        print(mid, "MISSING")
        continue
    keep = {k: m.get(k) for k in ("id", "name", "type", "modality", "pricing", "price", "cost", "context_length") if k in m}
    print(json.dumps(keep, ensure_ascii=False))
