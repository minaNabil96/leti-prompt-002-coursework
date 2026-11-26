import json
import pathlib

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = (ROOT / ".polza_key").read_text().strip()
H = {"Authorization": f"Bearer {KEY}"}

out = {}
for path in ["history", "history/requests", "history/chat", "history/generations"]:
    try:
        r = requests.get(f"https://polza.ai/api/v1/{path}", headers=H,
                         params={"limit": 50}, timeout=60)
        print(f"GET /{path}: {r.status_code}")
        if r.ok:
            data = r.json()
            out[path] = data
            text = json.dumps(data, ensure_ascii=False)
            print(text[:4000])
    except Exception as exc:  # noqa: BLE001
        print(path, "ERR", exc)
    print("-" * 60)

(ROOT / "logs" / "history_raw.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
