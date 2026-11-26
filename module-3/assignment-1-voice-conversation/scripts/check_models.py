"""Inspect the Polza.ai model catalogue for the models we need."""
import json
import pathlib

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
KEY = (ROOT / ".polza_key").read_text(encoding="utf-8").strip()

r = requests.get("https://polza.ai/api/v1/models",
                 headers={"Authorization": f"Bearer {KEY}"}, timeout=120)
r.raise_for_status()
models = r.json()["data"]
(ROOT / "logs" / "models_raw.json").write_text(
    json.dumps(models, ensure_ascii=False, indent=2), encoding="utf-8")

print("total models:", len(models))
keys = sorted({k for m in models for k in m.keys()})
print("keys:", keys)


def show(pattern):
    print(f"\n=== {pattern} ===")
    for m in models:
        mid = m.get("id", "")
        if pattern.lower() in mid.lower():
            print(" ", mid,
                  "| modality:", m.get("architecture", {}).get("modality"),
                  "| name:", (m.get("name") or "")[:60])


show("gemini-2.5-flash")
show("gemini-3.8-flash-lite")
show("tts")
show("mai-voice")

for want in ("google/gemini-2.5-flash", "google/gemini-3.8-flash-lite-tts"):
    hit = [m for m in models if m.get("id") == want]
    print(f"\n--- {want} ---")
    if not hit:
        print("NOT FOUND")
        continue
    m = hit[0]
    print(json.dumps({k: m.get(k) for k in
                      ("id", "name", "created", "description", "context_length",
                       "architecture", "pricing", "top_provider", "supported_parameters",
                       "input_modalities", "output_modalities")},
                     ensure_ascii=False, indent=2)[:2000])
