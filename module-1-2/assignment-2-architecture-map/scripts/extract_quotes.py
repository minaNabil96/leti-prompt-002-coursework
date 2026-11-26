import re

import requests

PAGES = {
    "gemini15": ("https://arxiv.org/html/2403.05530v5", ["Transformer", "mixture-of-experts", "Mixture-of-Experts"]),
    "gigachat": ("https://arxiv.org/html/2506.09440v1", ["decoder-only", "Transformer", "transformer"]),
    "qwen": ("https://arxiv.org/html/2508.02324v1", ["MMDiT", "diffusion transformer", "latent"]),
    "seedream": ("https://arxiv.org/html/2509.20427v3", ["diffusion transformer", "rectified flow", "flow matching"]),
}

for name, (url, keys) in PAGES.items():
    print("=" * 30, name, "=" * 30)
    try:
        r = requests.get(url, timeout=90, headers={"User-Agent": "Mozilla/5.0"})
        text = re.sub(r"<[^>]+>", " ", r.text)
        text = re.sub(r"\s+", " ", text)
        print("status", r.status_code, "len", len(text))
        for key in keys:
            found = 0
            for m in re.finditer(re.escape(key), text, flags=re.I):
                s = max(0, m.start() - 220)
                e = min(len(text), m.end() + 260)
                print(f"[{key}] ...{text[s:e]}...")
                found += 1
                if found >= 2:
                    break
    except Exception as exc:  # noqa: BLE001
        print("ERR", exc)
    print()
