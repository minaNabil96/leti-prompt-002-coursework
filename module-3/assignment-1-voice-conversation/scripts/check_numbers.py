"""Check the numeric claims made in the report text against the logs."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
conv = json.loads((LOGS / "conversation.json").read_text(encoding="utf-8"))
pros = json.loads((LOGS / "prosody.json").read_text(encoding="utf-8"))
tts = json.loads((LOGS / "tts_results.json").read_text(encoding="utf-8"))

turns = conv["turns"]
u = [len(t["user"]) for t in turns]
a = [len(t["assistant"]) for t in turns]
print("user chars", u, "total", sum(u))
print("assistant chars", a, "total", sum(a))
ratios = [x / y for x, y in zip(a, u)]
print("ratio mean", round(sum(ratios) / len(ratios), 1),
      "min", round(min(ratios), 1), "max", round(max(ratios), 1))
n = len(u)
mu, ma = sum(u) / n, sum(a) / n
cov = sum((x - mu) * (y - ma) for x, y in zip(u, a))
su = sum((x - mu) ** 2 for x in u) ** 0.5
sa = sum((y - ma) ** 2 for y in a) ** 0.5
print("pearson", round(cov / (su * sa), 2))
print("turn 8 user/assistant", len(turns[7]["user"]), len(turns[7]["assistant"]))
print("turn 12 user/assistant", len(turns[11]["user"]), len(turns[11]["assistant"]))

print("clipped", [(f["file"][-14:], f["clipped_samples"], f["peak_dbfs"], f["dc_offset"])
                  for f in pros["by_file"]])
print("files with clipping", sum(1 for f in pros["by_file"] if f["clipped_samples"] > 0))
print("clipped range", min(f["clipped_samples"] for f in pros["by_file"] if f["clipped_samples"]),
      max(f["clipped_samples"] for f in pros["by_file"]))
print("max |dc|", max(abs(f["dc_offset"]) for f in pros["by_file"]))
print("tts chars", tts["totals"]["chars"], "files", len(tts["files"]))
print("sum tts api dur", round(sum(f["api_duration_s"] for f in tts["files"]), 2))
print("started", conv["started"], "finished", conv["finished"])
print("last prompt tokens", turns[-1].get("prompt_tokens"), turns[-1].get("usage"))
