"""Derive the canonical numbers printed in the report from the raw logs.

Writes logs/computed_stats.json so that the report text, the work log and the
cost table can be checked against one machine-readable source.
"""
import json
import pathlib
import statistics

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"

conv = json.loads((LOGS / "conversation.json").read_text(encoding="utf-8"))
tts = json.loads((LOGS / "tts_results.json").read_text(encoding="utf-8"))
pros = json.loads((LOGS / "prosody.json").read_text(encoding="utf-8"))
stt = json.loads((LOGS / "stt_check.json").read_text(encoding="utf-8"))
ui = json.loads((LOGS / "ui_repeat.json").read_text(encoding="utf-8"))

files = pros["by_file"]
durations = [f["duration_s"] for f in files]
ratios = [f["speech_ratio"] for f in files]
medians = [f["f0_median_hz"] for f in files]
spans = [f["f0_span_semitones"] for f in files]
speech_total = sum(f["speech_s"] for f in files)
pause_total = sum(f["pause_total_s"] for f in files)
pause_count = sum(f["pause_count"] for f in files)
words = sum(f["words"] for f in files)

cost_llm = round(conv["totals"]["cost_rub"], 4)
cost_tts = round(tts["totals"]["cost_rub"], 4)
cost_stt = round(stt["totals"]["cost_rub"], 4)
cost_ui = round(sum(ui["costs_rub"]), 4)
calibration = 0.0095

stats = {
    "llm": {
        "model": conv["llm_model"],
        "temperature": conv["temperature"],
        "requests": len(conv["turns"]),
        "prompt_tokens": conv["totals"]["prompt_tokens"],
        "completion_tokens": conv["totals"]["completion_tokens"],
        "cost_rub": cost_llm,
    },
    "tts": {
        "model": tts["model"],
        "voice": tts["voice"],
        "files": len(tts["files"]),
        "chars": tts["totals"]["chars"],
        "api_duration_s": round(tts["totals"]["duration_s"], 2),
        "cost_rub": cost_tts,
    },
    "stt": {
        "model": stt["model"],
        "files": len(stt["files"]),
        "duration_s": round(stt["totals"]["duration_s"], 2),
        "minutes": round(stt["totals"]["duration_s"] / 60, 2),
        "cost_rub": cost_stt,
        "similarity_min": round(min(f["similarity"] for f in stt["files"]), 2),
        "similarity_max": round(max(f["similarity"] for f in stt["files"]), 2),
    },
    "prosody": {
        "files": len(files),
        "duration_s": round(sum(durations), 2),
        "durations_s": [round(d, 1) for d in durations],
        "speech_s": round(speech_total, 1),
        "speech_ratio_min": round(min(ratios), 3),
        "speech_ratio_max": round(max(ratios), 3),
        "pause_count": pause_count,
        "pause_mean_s": round(pause_total / pause_count, 2),
        "pause_max_s": round(max(f["pause_max_s"] for f in files), 2),
        "words": words,
        "syllables": sum(f["syllables"] for f in files),
        "wpm": round(words / (speech_total / 60), 1),
        "f0_median_hz": round(float(statistics.median(medians)), 1),
        "f0_median_mean_hz": round(sum(medians) / len(medians), 1),
        "f0_median_per_file_hz": [round(m, 1) for m in medians],
        "f0_median_min_hz": round(min(medians)),
        "f0_median_max_hz": round(max(medians)),
        "f0_span_semitones_min": round(min(spans), 1),
        "f0_span_semitones_max": round(max(spans), 1),
    },
    "cost": {
        "llm_rub": cost_llm,
        "tts_rub": cost_tts,
        "stt_rub": cost_stt,
        "ui_repeat_rub": cost_ui,
        "calibration_rub": calibration,
        "budget_rub": 15.0,
    },
}
stats["cost"]["reported_rub"] = round(cost_llm + cost_tts + cost_stt + cost_ui, 4)
stats["cost"]["total_rub"] = round(cost_llm + cost_tts + cost_stt + cost_ui + calibration, 4)
stats["cost"]["remainder_rub"] = round(15.0 - stats["cost"]["reported_rub"], 4)
stats["cost"]["tts_share_pct"] = round(cost_tts / stats["cost"]["reported_rub"] * 100)
stats["ui_repeat"] = {
    "model": ui["model"],
    "model_display": ui["model_display"],
    "requests": ui["requests"],
    "date": ui["date"],
    "started_msk": ui["started_msk"],
    "finished_msk": ui["finished_msk"],
    "cost_rub": cost_ui,
    "source": ui["source"],
}

out = LOGS / "computed_stats.json"
out.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(out)
print(json.dumps(stats, ensure_ascii=False, indent=1))
