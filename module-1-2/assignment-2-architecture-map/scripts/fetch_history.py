import json
import pathlib

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = (ROOT / ".polza_key").read_text().strip()
H = {"Authorization": f"Bearer {KEY}"}

for path in ["history/generations", "history", "history/requests", "history/chat"]:
    r = requests.get(f"https://polza.ai/api/v1/{path}", headers=H, timeout=60)
    print(f"GET /{path}: {r.status_code}")
    if r.ok:
        data = r.json()
        text = json.dumps(data, ensure_ascii=False)
        print(text[:1200])
        (ROOT / "logs" / f"history_{path.replace('/', '_')}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print("-" * 50)
