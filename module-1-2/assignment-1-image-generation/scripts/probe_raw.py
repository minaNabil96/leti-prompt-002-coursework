import json, os, pathlib, time, requests

root = pathlib.Path(__file__).resolve().parents[1]
key = os.environ.get("POLZA_API_KEY")
if not key:
    cfg = json.loads((root.parent / "opencode.json").read_text(encoding="utf-8"))
    key = cfg["provider"]["polza"]["options"]["apiKey"]

prompt = (root / "logs" / "prompt_en.txt").read_text(encoding="utf-8").strip()
payload = {"model": "tongyi-mai/z-image", "prompt": prompt, "aspect_ratio": "1:1", "n": 1}
t0 = time.time()
resp = requests.post("https://polza.ai/api/v1/images/generations",
                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                     json=payload, timeout=300)
print("HTTP", resp.status_code, "elapsed", round(time.time() - t0, 1))
if resp.ok:
    d = resp.json()
    print(json.dumps({k: v for k, v in d.items() if k != "data"}, ensure_ascii=False, indent=2)[:2000])
    item = d["data"][0]
    print("DATA KEYS:", list(item.keys()))
    if item.get("b64_json"):
        import base64
        (root / "screenshots" / "img_only_z-image.png").write_bytes(base64.b64decode(item["b64_json"]))
        print("saved b64 image")
    elif item.get("url"):
        img = requests.get(item["url"], timeout=120)
        (root / "screenshots" / "img_only_z-image.png").write_bytes(img.content)
        print("saved url image", len(img.content))
    (root / "logs" / "gen_z-image.raw.json").write_text(json.dumps(d, ensure_ascii=False, indent=2)[:20000], encoding="utf-8")
else:
    print(resp.text[:1500])
