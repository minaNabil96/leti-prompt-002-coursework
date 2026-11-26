import pathlib
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = (ROOT / ".polza_key").read_text().strip()
H = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
PAYLOAD = {
    "model": "yandex/yandex-art",
    "input": {
        "prompt": "Фантастический город будущего на закате, неоновые огни, летающие машины, киберпанк-стиль.",
        "aspect_ratio": "1:1",
    },
}

for i in range(1, 4):
    r = requests.post("https://polza.ai/api/v1/media", headers=H, json=PAYLOAD, timeout=120)
    print(f"attempt {i}: {r.status_code} {r.text[:160]}", flush=True)
    if r.ok:
        pathlib.Path(ROOT / "logs" / "d2_ok.json").write_text(r.text, encoding="utf-8")
        break
    time.sleep(60)
