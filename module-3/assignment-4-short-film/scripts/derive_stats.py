"""Derive the canonical numbers of the assignment from the raw logs.

Everything the report states (costs, durations, resolutions, counts) is computed
here once and written to logs/computed_stats.json; the report builder and the
checkers read only that file, so numbers cannot drift between documents.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"

BUDGET = 60.0

prompts = json.loads((LOGS / "prompt_iterations.json").read_text(encoding="utf-8"))
llm_runs = [{"iteration": r["iteration"], "label": r["label"],
             "cost_rub": round(float(r.get("cost_rub", 0) or 0), 6),
             "chars": len(r.get("text") or ""),
             "requested_at": r.get("requested_at")} for r in prompts["runs"]]
llm_total = round(sum(r["cost_rub"] for r in llm_runs), 6)

video_files = sorted(p for p in (LOGS / "video").glob("scene_*.json")
                     if "_error" not in p.name)
video = []
for p in video_files:
    d = json.loads(p.read_text(encoding="utf-8"))
    video.append({"log": p.name, "scene": d.get("scene"), "attempt": d.get("attempt", 1),
                  "rejected": bool(d.get("rejected", False)),
                  "cost_rub": round(float(d.get("cost_rub", 0) or 0), 6),
                  "duration_param": d.get("duration_param"),
                  "resolution_param": d.get("resolution_param"),
                  "elapsed_sec": d.get("elapsed_sec"), "bytes": d.get("bytes"),
                  "requested_at": d.get("requested_at"),
                  "request_id": d.get("request_id")})
video_total = round(sum(v["cost_rub"] for v in video), 6)
video_accepted = [v for v in video if not v["rejected"]]
video_rejected = [v for v in video if v["rejected"]]

tts = json.loads((LOGS / "tts.json").read_text(encoding="utf-8"))
tts_total = round(tts["totals"]["cost_rub"], 6)

music = json.loads((LOGS / "music.json").read_text(encoding="utf-8"))
music_total = round(float(music["cost_rub"]), 6)

assembly = json.loads((LOGS / "assembly.json").read_text(encoding="utf-8"))
timing = json.loads((LOGS / "voiceover_timing.json").read_text(encoding="utf-8"))

total = round(llm_total + video_total + tts_total + music_total, 6)

# scene durations in the finished film, from the assembly log
clips = assembly["clips"]
story = json.loads((ROOT / "scripts" / "storyboard.json").read_text(encoding="utf-8"))
voice = json.loads((ROOT / "scripts" / "voiceover.json").read_text(encoding="utf-8"))

scenes = []
for st, cl, l in zip(story["scenes"], clips, timing["lines"]):
    scenes.append({
        "n": st["n"], "scene": st["scene"],
        "planned_s": st["duration_sec"],
        "final_s": round(cl["target_s"] - assembly["crossfade_s"] / 2, 3),
        "stretch": cl["stretch"],
        "voiceover": next(x["text"] for x in voice["lines"] if x["n"] == st["n"]),
        "speech_s": l["trimmed_s"],
        "start_s": l["start_in_film_s"],
    })

stats = {
    "generated": assembly["created"],
    "session_date": (LOGS / "session_date.txt").read_text(encoding="utf-8").strip(),
    "budget_rub": BUDGET,
    "cost": {
        "llm": {"model": "google/gemini-2.5-flash", "calls": len(llm_runs),
                "total_rub": llm_total, "runs": llm_runs},
        "video": {"model": "grok-imagine-video-1-5", "calls": len(video),
                  "accepted_calls": len(video_accepted),
                  "rejected_calls": len(video_rejected),
                  "total_rub": video_total, "runs": video},
        "tts": {"model": "google/gemini-3.8-flash-lite-tts", "voice": tts["voice"],
                "calls": len(tts["lines"]), "chars": tts["totals"]["chars"],
                "total_rub": tts_total},
        "music": {"model": music["model"], "calls": len(music["attempts"]),
                  "total_rub": music_total},
        "total_rub": total,
        "api_calls": len(llm_runs) + len(video) + len(tts["lines"]) + len(music["attempts"]),
        "budget_used_pct": round(total / BUDGET * 100, 1),
        "budget_left_rub": round(BUDGET - total, 4),
    },
    "film": {
        "file": assembly["file"], "duration_s": assembly["duration_s"],
        "width": assembly["video"]["width"], "height": assembly["video"]["height"],
        "fps": assembly["video"]["fps"], "codec": assembly["video"]["codec"],
        "audio_codec": assembly["audio"]["codec"],
        "audio_hz": assembly["audio"]["sample_rate"],
        "bytes": assembly["bytes"],
        "crossfade_s": assembly["crossfade_s"],
        "scenes": scenes,
        "speech_s": timing["speech_s"],
        "title_card_s": round(clips[-1]["target_s"] - assembly["crossfade_s"] / 2, 3),
        "voiceover_chars": voice["total_chars"],
        "source_resolution": "736x416",
    },
    "counts": {
        "llm_prompt_iterations": len(llm_runs),
        "storyboard_scenes": len(story["scenes"]),
        "generated_video_scenes": len(video_accepted),
        "screenshots": len(list((ROOT / "screenshots").glob("*.png"))),
    },
}
(LOGS / "computed_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2),
                                         encoding="utf-8")

print(f"LLM      {len(llm_runs)} calls  {llm_total:8.4f} RUB")
print(f"VIDEO    {len(video)} calls  {video_total:8.4f} RUB "
      f"({len(video_accepted)} accepted, {len(video_rejected)} rejected)")
print(f"TTS      {len(tts['lines'])} calls  {tts_total:8.4f} RUB")
print(f"MUSIC    {len(music['attempts'])} calls  {music_total:8.4f} RUB")
print(f"TOTAL    {len(llm_runs) + len(video) + len(tts['lines']) + len(music['attempts'])} calls "
      f"{total:8.4f} RUB of {BUDGET} ({total / BUDGET * 100:.1f}%), left {BUDGET - total:.4f}")
print(f"FILM     {assembly['duration_s']}s {assembly['video']['width']}x"
      f"{assembly['video']['height']} {assembly['video']['fps']}fps "
      f"{assembly['bytes']/1e6:.1f} MB")
