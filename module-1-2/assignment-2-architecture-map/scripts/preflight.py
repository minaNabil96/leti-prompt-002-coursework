import json
import pathlib
import sys

import requests

BASE = "https://polza.ai/api/v1"
KEY = pathlib.Path(__file__).resolve().parent.parent.joinpath(".polza_key").read_text().strip()
H = {"Authorization": f"Bearer {KEY}"}

r = requests.get(f"{BASE}/models", headers=H, timeout=60)
print("models:", r.status_code)
data = r.json()
items = data.get("data") if isinstance(data, dict) else data
ids = []
for m in items or []:
    mid = m.get("id") if isinstance(m, dict) else str(m)
    ids.append(mid)
print("count:", len(ids))

for name in ["balance", "user/balance", "account/balance", "credits"]:
    try:
        rr = requests.get(f"{BASE}/{name}", headers=H, timeout=30)
        print(f"GET /{name}:", rr.status_code, rr.text[:200])
    except Exception as e:  # noqa: BLE001
        print(f"GET /{name}: ERR {e}")

want = [
    "openai/gpt-4o",
    "yandex/yandex-gpt",
    "google/gemini-2.5-flash",
    "tongyi-mai/z-image",
    "yandex/yandex-art",
    "bytedance/seedream-4",
]
print("--- wanted ids ---")
for w in want:
    print(f"{w}: {'FOUND' if w in ids else 'MISSING'}")

pathlib.Path(__file__).resolve().parent.parent.joinpath("logs", "models_all.json").write_text(
    json.dumps(sorted(ids), ensure_ascii=False, indent=1), encoding="utf-8"
)
# print fuzzy matches for missing
for w in want:
    if w not in ids:
        frag = w.split("/")[-1].split("-")[0]
        cand = [i for i in ids if frag.lower() in i.lower()]
        print("  candidates for", w, "->", cand[:15])
