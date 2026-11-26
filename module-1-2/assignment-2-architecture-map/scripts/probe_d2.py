import json
import pathlib

import requests

BASE = "https://polza.ai/api/v1"
KEY = pathlib.Path(__file__).resolve().parent.parent.joinpath(".polza_key").read_text().strip()
H = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

r = requests.get(f"{BASE}/models/yandex/yandex-art", headers=H, timeout=60)
print("detail:", r.status_code)
print(r.text[:2500])
print("=" * 40)

# try OpenAI-compatible images endpoint
payload = {
    "model": "yandex/yandex-art",
    "prompt": "Фантастический город будущего на закате, неоновые огни, летающие машины, киберпанк-стиль.",
    "size": "1024x1024",
    "n": 1,
}
rr = requests.post(f"{BASE}/images/generations", headers=H, json=payload, timeout=180)
print("images/generations:", rr.status_code)
print(rr.text[:800])
