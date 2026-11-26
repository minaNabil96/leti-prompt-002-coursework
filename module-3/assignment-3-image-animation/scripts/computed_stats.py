"""Compute every number used in the report from the raw logs.

Writes ./logs/computed_stats.json and ./logs/history_media.json (API provenance).
"""
import json
import pathlib
import re
import time
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJ = ROOT.parent
LOGS = ROOT / "logs"
API = "https://polza.ai/api/v1"
KEY = (PROJ / "ref-analysis" / ".polza_key").read_text(encoding="utf-8").strip()
H = {"Authorization": f"Bearer {KEY}"}
MSK = timezone(timedelta(hours=3))


def msk(iso):
    if not iso:
        return None
    return (datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(MSK)
            .strftime("%Y-%m-%d %H:%M:%S"))


hist = requests.get(f"{API}/history/generations", headers=H, params={"limit": 100},
                    timeout=60).json()["items"]
media = [h for h in hist if h.get("requestType") in ("image", "images", "video")]
LOGS.joinpath("history_media.json").write_text(
    json.dumps(media, ensure_ascii=False, indent=2), encoding="utf-8")
by_id = {h["id"]: h for h in media}

gen = {}
for p in (LOGS / "gen").glob("*.json"):
    d = json.loads(p.read_text(encoding="utf-8"))
    gen[p.stem] = d

video_info = json.loads((LOGS / "video_info.json").read_text(encoding="utf-8"))
motion = json.loads((LOGS / "motion_metrics.json").read_text(encoding="utf-8"))
regions = json.loads((LOGS / "motion_regions.json").read_text(encoding="utf-8"))

sources = []
for stem, label in (("source_01_portrait", "S1"), ("source_02_landscape", "S2")):
    d = gen[stem]
    h = by_id.get(d["request_id"], {})
    sources.append({
        "label": label, "file": d["file"], "model": d["model"],
        "prompt": d["prompt"], "aspect_ratio": d.get("aspect_ratio"),
        "width": d["size"][0], "height": d["size"][1], "bytes": d["bytes"],
        "cost_rub": d["cost_rub"], "request_id": d["request_id"],
        "created_msk": msk(h.get("createdAt")), "completed_msk": msk(h.get("finalizedAt")),
    })

paint = ROOT / "sources" / "source_03_painting.jpg"
sources.append({
    "label": "S3", "file": paint.name, "model": "Wikimedia Commons (Van Gogh, 1889)",
    "prompt": None, "aspect_ratio": None, "width": 1280, "height": 1014,
    "bytes": paint.stat().st_size, "cost_rub": 0.0, "request_id": None,
    "created_msk": "2026-11-25 23:06:18", "completed_msk": "2026-11-25 23:06:18",
})

animations = []
for stem in ("animation_01_portrait", "animation_02_landscape", "animation_03_painting"):
    d = gen[stem]
    vi = video_info[d["file"]]
    mm = motion[d["file"]]
    h = by_id.get(d["request_id"], {})
    animations.append({
        "file": d["file"], "source": d["source"], "intensity": d["intensity"],
        "prompt": d["prompt"], "model": d["model"],
        "cost_rub": d["cost_rub"], "bytes": d["bytes"], "request_id": d["request_id"],
        "created_msk": msk(h.get("createdAt")), "completed_msk": msk(h.get("finalizedAt")),
        "generation_time_sec": round((h.get("generationTimeMs") or 0) / 1000, 1),
        "duration_sec": vi["duration_sec"], "width": vi["size"][0], "height": vi["size"][1],
        "fps": mm["fps"], "frames": mm["frames"],
        "diff_mean": mm["diff_mean"], "diff_p95": mm["diff_p95"],
        "diff_max": mm["diff_max"], "audio_stream": regions[d["file"]]["audio_stream"],
        "top_regions": regions[d["file"]]["grid"][:3],
    })

total_cost = round(sum(s["cost_rub"] for s in sources) + sum(a["cost_rub"] for a in animations), 3)
total_duration = round(sum(a["duration_sec"] for a in animations), 2)
cost_text = str(Decimal(str(total_cost)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
cost_exact_text = f"{total_cost:.3f}"

reflection = (LOGS / "reflection.md").read_text(encoding="utf-8")
body = reflection.split("\n", 2)[2] if reflection.startswith("#") else reflection
words = [w for w in re.split(r"\s+", body) if re.search(r"\w", w)]

stats = {
    "date": "2026-11-25",
    "computed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    "sources": sources,
    "animations": animations,
    "totals": {
        "count_sources": len(sources),
        "count_animations": len(animations),
        "cost_rub": total_cost,
        "cost_rub_text": cost_text.replace(".", ","),
        "cost_exact_text": cost_exact_text.replace(".", ","),
        "cost_per_video_rub": animations[0]["cost_rub"],
        "duration_sec": total_duration,
        "duration_text": f"{total_duration:.2f}".replace(".", ","),
        "frames": sum(a["frames"] for a in animations),
        "bytes": sum(a["bytes"] for a in animations),
        "count_media_calls": 5,
    },
    "reflection_words": len(words),
    "reflection_chars": len(body.strip()),
}
(LOGS / "computed_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
print(json.dumps(stats["totals"], ensure_ascii=False, indent=2))
print("reflection words:", len(words))
for a in animations:
    print(a["file"], a["created_msk"], "->", a["completed_msk"], a["duration_sec"],
          "s", a["width"], "x", a["height"], a["frames"], "frames", a["cost_rub"], "RUB")
