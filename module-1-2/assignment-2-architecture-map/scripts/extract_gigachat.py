import re

import requests

url = "https://arxiv.org/html/2506.09440v1"
r = requests.get(url, timeout=90, headers={"User-Agent": "Mozilla/5.0"})
text = re.sub(r"<[^>]+>", " ", r.text)
text = re.sub(r"\s+", " ", text)
for key in ["decoder", "architecture", "GPT", "autoregressive"]:
    print("=" * 20, key)
    n = 0
    for m in re.finditer(key, text, flags=re.I):
        s = max(0, m.start() - 260)
        e = min(len(text), m.end() + 320)
        print(f"...{text[s:e]}...")
        n += 1
        if n >= 3:
            break
