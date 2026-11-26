"""Step 1 — pre-flight checks for М3, задание 4 (короткометражный ролик).

Verifies the key, the Python stack and FFmpeg, then fetches the live Polza.ai
catalogue and prints the candidate models for video, music and TTS with their
price tiers, so the cost plan can be checked against the real catalogue.
Writes logs/models_raw.json, logs/preflight.json, logs/session_date.txt.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJ = ROOT.parent
LOGS = ROOT / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

KEY_PATH = PROJ / "ref-analysis" / ".polza_key"
KEY = KEY_PATH.read_text(encoding="utf-8").strip()
BASE = "https://polza.ai/api/v1"
HEADERS = {"Authorization": f"Bearer {KEY}"}

INTEREST = {
    "video": ("grok-imagine-video", "seedance", "veo3", "kling", "wan-"),
    "music": ("suno", "lyria"),
    "tts": ("tts", "mai-voice"),
    "chat": ("gemini-2.5-flash",),
}

out = {"checked_at": time.strftime("%Y-%m-%d %H:%M:%S"), "key_path": str(KEY_PATH),
       "key_prefix": KEY[:4], "key_len": len(KEY)}

# --- Python stack -----------------------------------------------------------
pypkgs = {}
for mod, pip in (("requests", "requests"), ("docx", "python-docx"), ("PIL", "Pillow"),
                 ("numpy", "numpy"), ("imageio_ffmpeg", "imageio-ffmpeg"),
                 ("pymupdf", "PyMuPDF"), ("mutagen", "mutagen")):
    pypkgs[mod] = bool(importlib.util.find_spec(mod))
out["python"] = {"version": sys.version.split()[0], "packages": pypkgs,
                 "missing": [m for m, ok in pypkgs.items() if not ok]}

# --- FFmpeg -----------------------------------------------------------------
import imageio_ffmpeg  # noqa: E402

ff = imageio_ffmpeg.get_ffmpeg_exe()
ver = subprocess.run([ff, "-version"], capture_output=True, text=True, encoding="utf-8",
                     errors="replace").stdout.splitlines()[0]
out["ffmpeg"] = {"path": ff, "version": ver}
print("FFmpeg:", ver)
print("FFmpeg path:", ff)

# --- catalogue --------------------------------------------------------------
r = requests.get(f"{BASE}/models", headers=HEADERS, timeout=120)
r.raise_for_status()
(LOGS / "models_raw.json").write_bytes(r.content)
cat = r.json()
items = cat["data"] if isinstance(cat, dict) and "data" in cat else cat
out["catalogue_models"] = len(items)
print(f"catalogue: HTTP {r.status_code}, {len(items)} models")

by_id = {m.get("id"): m for m in items}
cand = {}
for kind, pats in INTEREST.items():
    ids = sorted(i for i in by_id if i and any(p in i.lower() for p in pats))
    cand[kind] = ids
out["candidates"] = cand
for kind, ids in cand.items():
    print(f"\n--- {kind} ---")
    for i in ids:
        m = by_id[i]
        pr = ((m.get("top_provider") or {}).get("pricing") or {})
        tiers = ",".join(f"{t.get('cost_rub')}[{'/'.join(t.get('conditions') or ['base'])}]"
                         for t in (pr.get("tiers") or [])) or "-"
        params = ",".join(sorted(((m.get("top_provider") or {}).get("parameters") or {}).keys()))
        print(f"  {i} | {m.get('type')} | per {pr.get('unitParam')} | {tiers}")
        print(f"      params: {params}")

(LOGS / "preflight.json").write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
date = time.strftime("%Y-%m-%d")
(LOGS / "session_date.txt").write_text(date + "\n", encoding="utf-8")
print("\nsession date:", date)
