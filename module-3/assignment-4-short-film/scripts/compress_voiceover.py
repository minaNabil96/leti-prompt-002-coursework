"""Step 2c — fit the voiceover to the scene durations.

The LLM storyboard (iteration 4) produced 706 characters of voiceover, which is
about 45 s of Russian speech — far longer than the 24 s of generated video.
This step asks the same model for a compressed version (one call), so the
final text is still LLM-authored and the «было → стало» pair is documented.

Writes scripts/voiceover.json and appends iteration 5 to the prompt logs.
"""
import json
import pathlib
import re
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJ = ROOT.parent
API = "https://polza.ai/api/v1"
KEY = (PROJ / "ref-analysis" / ".polza_key").read_text(encoding="utf-8").strip()
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
MODEL = "google/gemini-2.5-flash"
LOGS = ROOT / "logs"

# Russian speech at a calm documentary pace is about 14-15 characters per second.
CHARS_PER_SEC = 14.5

story = json.loads((ROOT / "scripts" / "storyboard.json").read_text(encoding="utf-8"))
scenes = story["scenes"]

# Scene 6 is the title card: it gets its own 4 s, the generated scenes keep theirs.
budget = {s["n"]: int(s["duration_sec"] * CHARS_PER_SEC) - 4 for s in scenes}
budget[6] = int(4 * CHARS_PER_SEC) - 6

lines = "\n".join(f"{s['n']}. ({s['duration_sec']} с, до {budget[s['n']]} знаков) "
                  f"{s['voiceover']}" for s in scenes)

PROMPT = (
    "Ниже — закадровый текст короткометражного ролика «Рождение образа» и "
    "хронометраж каждой сцены. Текст не влезает в хронометраж: его нужно сжать.\n\n"
    "Перепиши каждую реплику так, чтобы она звучала за указанное время "
    "в спокойном документальном темпе (примерно 14–15 знаков в секунду). "
    "Требования: сохрани смысл и порядок сцен; одно короткое предложение на сцену; "
    "не более указанного числа знаков; числа — словами; без латиницы; "
    "без обращений к зрителю; сохрани единый тон — вдохновляющий, задумчивый.\n\n"
    f"Исходный текст:\n{lines}\n\n"
    "Ответ строго в формате JSON: {\"lines\":[{\"scene_number\":1,\"text\":\"...\"}]}"
)

RUN = {"iteration": 5, "label": "сжатие закадрового текста под хронометраж",
       "prompt": PROMPT, "model": MODEL, "temperature": 0.4,
       "requested_at": time.strftime("%Y-%m-%d %H:%M:%S")}

log_path = LOGS / "prompt_iterations.json"
log = json.loads(log_path.read_text(encoding="utf-8"))
existing = [r for r in log["runs"] if r.get("iteration") == 5]

if existing:
    rec = existing[0]
    print("iteration 5 already present, reusing (no new call)")
else:
    t0 = time.time()
    r = requests.post(f"{API}/chat/completions", headers=HEADERS, timeout=180, json={
        "model": MODEL, "temperature": 0.4, "max_tokens": 1200,
        "messages": [{"role": "user", "content": PROMPT}]})
    rec = dict(RUN)
    rec.update({"http": r.status_code, "elapsed_sec": round(time.time() - t0, 2)})
    if not r.ok:
        raise SystemExit(f"HTTP {r.status_code}: {r.text[:500]}")
    j = r.json()
    rec["text"] = j["choices"][0]["message"]["content"]
    rec["usage"] = j.get("usage")
    rec["cost_rub"] = float((j.get("usage") or {}).get("cost_rub", 0) or 0)
    rec["response_id"] = j.get("id")
    log["runs"].append(rec)
    log["total_cost_rub"] = round(sum(x.get("cost_rub", 0) or 0 for x in log["runs"]), 4)
    log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"iteration 5: HTTP 200 {len(rec['text'])} chars, {rec['cost_rub']:.4f} RUB")


def parse_json(text):
    m = re.search(r"```(?:json)?\s*(.+?)```", text or "", re.S)
    raw = m.group(1) if m else (text or "")
    i, j = raw.find("{"), raw.rfind("}")
    if i < 0 or j <= i:
        return None
    try:
        return json.loads(raw[i:j + 1])
    except json.JSONDecodeError:
        return None


data = parse_json(rec.get("text")) or {}
by_n = {}
for item in data.get("lines", []):
    try:
        by_n[int(item.get("scene_number"))] = (item.get("text") or "").strip()
    except (TypeError, ValueError):
        continue

out = {"model": MODEL, "iteration": 5, "chars_per_sec_assumed": CHARS_PER_SEC,
       "created": time.strftime("%Y-%m-%d %H:%M:%S"),
       "budget_per_scene": budget, "lines": []}
for s in scenes:
    text = by_n.get(s["n"]) or s["voiceover"]
    out["lines"].append({"n": s["n"], "scene": s["scene"], "duration_sec": s["duration_sec"],
                         "text": text, "chars": len(text),
                         "fits": len(text) <= budget[s["n"]],
                         "was": s["voiceover"]})
total_chars = sum(x["chars"] for x in out["lines"])
out["total_chars"] = total_chars
out["estimated_speech_sec"] = round(total_chars / CHARS_PER_SEC, 1)
(ROOT / "scripts" / "voiceover.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

md_path = LOGS / "prompt_iterations.md"
md = [f"# Итерации промптов сценария и раскадровки", "",
      f"Модель — `{MODEL}`, температура 0,7 (итерации 1–4) и 0,4 (итерация 5). "
      f"Все промпты отправлены реально; суммарная стоимость — {log['total_cost_rub']:.4f} ₽.", ""]
for r_ in log["runs"]:
    md += [f"## Итерация {r_['iteration']} ({r_['label']})", "",
           f"Стоимость: {r_.get('cost_rub', 0):.4f} ₽, {r_.get('elapsed_sec', 0)} с.", "",
           "**Промпт:**", "", f"> {r_['prompt']}", "", "**Ответ модели:**", "",
           "```", (r_.get("text") or r_.get("error", ""))[:2000], "```", ""]
md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

print(f"\nvoiceover: {total_chars} chars, ~{out['estimated_speech_sec']} s of speech "
      f"(was {sum(len(x['was']) for x in out['lines'])} chars)")
for x in out["lines"]:
    flag = "ok " if x["fits"] else "OVER"
    print(f"  {x['n']}. {x['chars']:3d}/{budget[x['n']]:3d} {flag} {x['text']}")
print(f"TOTAL prompt cost so far: {log['total_cost_rub']:.4f} RUB")
