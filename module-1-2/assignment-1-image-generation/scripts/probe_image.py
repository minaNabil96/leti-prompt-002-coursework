import json, os, pathlib, sys
from openai import OpenAI

root = pathlib.Path(__file__).resolve().parents[1]
key = os.environ.get("POLZA_API_KEY")
if not key:
    cfg = json.loads((root.parent / "opencode.json").read_text(encoding="utf-8"))
    key = cfg["provider"]["polza"]["options"]["apiKey"]

client = OpenAI(api_key=key, base_url="https://polza.ai/api/v1")
prompt = (root / "logs" / "prompt_en.txt").read_text(encoding="utf-8").strip()
r = client.images.generate(model="tongyi-mai/z-image", prompt=prompt, size="1024x1024", n=1,
                           extra_body={"aspect_ratio": "1:1"})
d = r.model_dump()
print(json.dumps({k: v for k, v in d.items() if k != "data"}, ensure_ascii=False, indent=2)[:3000])
print("DATA KEYS:", list(d["data"][0].keys()))
print("URL:", (d["data"][0].get("url") or "")[:120])
print("B64 LEN:", len(d["data"][0].get("b64_json") or ""))
