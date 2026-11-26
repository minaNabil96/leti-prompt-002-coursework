import json
import pathlib

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = (ROOT / ".polza_key").read_text().strip()
H = {"Authorization": f"Bearer {KEY}"}

MODELS = {
    "openai/gpt-4o",
    "yandex/yandexgpt-5-lite",
    "google/gemini-2.5-flash",
    "tongyi-mai/z-image",
    "qwen/image",
    "bytedance/seedream-4",
}

items = []
for offset in range(0, 5000, 100):
    r = requests.get(
        "https://polza.ai/api/v1/history/generations",
        headers=H,
        params={"limit": 100, "offset": offset},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    page = data.get("items", [])
    items.extend(page)
    if len(page) < 100:
        break

# The endpoint may ignore offset and return the same page; dedupe by request id.
uniq = {}
for x in items:
    uniq[x.get("id")] = x
items = list(uniq.values())

print("unique history items:", len(items))
rows = [x for x in items if x.get("model") in MODELS]
rows.sort(key=lambda x: x.get("createdAt", ""))
print("matched calls:", len(rows))
total = 0.0
for x in rows:
    cost = float(x.get("cost") or 0)
    total += cost
    print(
        f"{x.get('createdAt')}  {x.get('model'):<28} {x.get('requestType'):<6} "
        f"{x.get('status'):<10} {cost:.4f} RUB  id={x.get('id')}"
    )
print(f"TOTAL matched: {total:.6f} RUB")

out = {
    "matched_calls": rows,
    "total_rub": round(total, 6),
    "all_models": sorted({x.get("model") for x in items}),
}
(ROOT / "logs" / "history_filtered.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
