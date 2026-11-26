import json, os, pathlib, time, requests

root = pathlib.Path(__file__).resolve().parents[1]
key = os.environ.get("POLZA_API_KEY")
if not key:
    cfg = json.loads((root.parent / "opencode.json").read_text(encoding="utf-8"))
    key = cfg["provider"]["polza"]["options"]["apiKey"]
H = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
prompt = (root / "logs" / "prompt_en.txt").read_text(encoding="utf-8").strip()

payload = {"model": "tongyi-mai/z-image",
           "input": {"prompt": prompt, "aspect_ratio": "1:1"}}
t0 = time.time()
r = requests.post("https://polza.ai/api/v1/media", headers=H, json=payload, timeout=120)
print("CREATE", r.status_code, round(time.time() - t0, 1))
print(json.dumps(r.json(), ensure_ascii=False, indent=2)[:2000])

if r.ok:
    obj = r.json()
    mid = obj.get("id")
    for i in range(100):
        if obj.get("status") in ("completed", "failed", "cancelled"):
            break
        time.sleep(3)
        s = requests.get(f"https://polza.ai/api/v1/media/{mid}", headers=H, timeout=60)
        obj = s.json()
        print("POLL", i, obj.get("status"))
    print(json.dumps(obj, ensure_ascii=False, indent=2)[:4000])
    (root / "logs" / "probe_z.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
