import json
import pathlib

import requests

BASE = "https://polza.ai/api/v1"
KEY = pathlib.Path(__file__).resolve().parent.parent.joinpath(".polza_key").read_text().strip()
H = {"Authorization": f"Bearer {KEY}"}

items = requests.get(f"{BASE}/models", headers=H, timeout=60).json()
if isinstance(items, dict):
    items = items.get("data", items)

rows = []
for m in items:
    if not isinstance(m, dict) or m.get("type") != "image":
        continue
    pricing = None
    tp = m.get("top_provider") or {}
    pr = tp.get("pricing") or {}
    tiers = pr.get("tiers") or []
    if tiers:
        pricing = tiers[0].get("cost_rub")
    rows.append((m.get("id"), m.get("name"), pricing))

rows.sort(key=lambda r: (float(r[2] or 1e9), r[0]))
print(f"image models: {len(rows)}")
for rid, name, price in rows:
    print(f"{str(price):>10}  {rid:<46} {name}")
