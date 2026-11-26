"""Step 2 — script and storyboard via the text LLM (google/gemini-2.5-flash).

Three prompt iterations are really sent to the model and stored, so the report's
«было → стало» section quotes actual outputs instead of retold ones.
Writes logs/prompt_iterations.json, logs/prompt_iterations.md and
scripts/storyboard.json.
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
LOGS.mkdir(parents=True, exist_ok=True)

ITER_1 = "Напиши сценарий для ролика об ИИ."

ITER_2 = ("Напиши сценарий 30-секундного ролика о генеративном ИИ, 6 сцен.")

ITER_3 = (
    "Напиши сценарий и раскадровку для короткометражного ролика длительностью "
    "25–30 секунд на тему «Рождение образа» — как ИИ превращает текстовый промпт "
    "в визуальное изображение. Жанр: микродокументалка. "
    "Раскадровка: минимум 6 сцен. Для каждой сцены укажи: "
    "1) номер, 2) визуальное описание (для text-to-video промпта на английском), "
    "3) длительность в секундах, 4) текст закадрового голоса на русском. "
    "Стиль визуального ряда: абстрактный, художественный, переход от тьмы к свету, "
    "от хаоса к форме. Настроение: вдохновляющее, задумчивое. "
    "Ответ в формате JSON."
)

ITERATIONS = [
    {"n": 1, "label": "vague", "prompt": ITER_1},
    {"n": 2, "label": "longer brief", "prompt": ITER_2},
    {"n": 3, "label": "final structured", "prompt": ITER_3},
]


def ask(prompt, temperature=0.7, max_tokens=2000):
    body = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature, "max_tokens": max_tokens}
    t0 = time.time()
    r = requests.post(f"{API}/chat/completions", headers=HEADERS, json=body, timeout=180)
    rec = {"prompt": prompt, "http": r.status_code, "elapsed_sec": round(time.time() - t0, 2),
           "model": MODEL, "temperature": temperature,
           "requested_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    if not r.ok:
        rec["error"] = r.text[:800]
        return rec, None
    j = r.json()
    rec["text"] = j["choices"][0]["message"]["content"]
    rec["usage"] = j.get("usage")
    rec["cost_rub"] = float((j.get("usage") or {}).get("cost_rub", 0) or 0)
    rec["response_id"] = j.get("id")
    return rec, rec["text"]


def parse_json(text):
    """Model text -> dict; tolerates ``` fences and prose around the JSON."""
    if not text:
        return None
    m = re.search(r"```(?:json)?\s*(.+?)```", text, re.S)
    raw = m.group(1) if m else text
    i, j = raw.find("{"), raw.rfind("}")
    if i < 0 or j <= i:
        return None
    try:
        return json.loads(raw[i:j + 1])
    except json.JSONDecodeError:
        return None


def main():
    runs = []
    total = 0.0
    story = None
    for it in ITERATIONS:
        rec, text = ask(it["prompt"])
        rec["iteration"] = it["n"]
        rec["label"] = it["label"]
        total += rec.get("cost_rub", 0.0)
        runs.append(rec)
        print(f"iteration {it['n']}: HTTP {rec['http']} "
              f"{len(text or '')} chars, {rec.get('cost_rub', 0):.4f} RUB")
        if it["n"] == 3:
            story = parse_json(text)
    (LOGS / "prompt_iterations.json").write_text(
        json.dumps({"model": MODEL, "runs": runs, "total_cost_rub": round(total, 4)},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# Итерации промптов сценария и раскадровки", "",
          f"Модель — `{MODEL}`, температура 0,7. Все три промпта отправлены реально; "
          f"суммарная стоимость — {total:.4f} ₽.", ""]
    for rec in runs:
        md += [f"## Итерация {rec['iteration']} ({rec['label']})", "",
               "**Промпт:**", "", f"> {rec['prompt']}", "", "**Ответ модели:**", "",
               "```", (rec.get("text") or rec.get("error", ""))[:1800], "```", ""]
    (LOGS / "prompt_iterations.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    if not story:
        raise SystemExit("iteration 3 did not return parsable JSON")
    scenes = story.get("scenes") or story.get("storyboard") or []
    norm = []
    for i, s in enumerate(scenes, 1):
        if isinstance(s, str):
            continue
        vis = (s.get("visual_prompt") or s.get("visual") or s.get("визуальное_описание")
               or s.get("visual_description") or "")
        vo = (s.get("voiceover") or s.get("voiceover_ru") or s.get("закадровый_голос")
              or s.get("voice_over") or s.get("narration") or "")
        norm.append({
            "n": i,
            "scene": s.get("scene") or s.get("name") or s.get("название") or "",
            "visual_prompt": vis.strip(),
            "duration_sec": float(s.get("duration") or s.get("duration_sec")
                                  or s.get("длительность") or 5),
            "voiceover": vo.strip(),
        })
    out = {"model": MODEL, "created": time.strftime("%Y-%m-%d %H:%M:%S"),
           "iteration_used": 3, "total_prompt_cost_rub": round(total, 4),
           "title": story.get("title") or "Рождение образа",
           "scenes": norm, "raw": story}
    (ROOT / "scripts" / "storyboard.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"storyboard: {len(norm)} scenes -> scripts/storyboard.json")
    for s in norm:
        print(f"  {s['n']}. {s['scene'][:40]!r} {s['duration_sec']}s "
              f"vis={len(s['visual_prompt'])} vo={len(s['voiceover'])} chars")
    print(f"TOTAL {total:.4f} RUB")


if __name__ == "__main__":
    main()
