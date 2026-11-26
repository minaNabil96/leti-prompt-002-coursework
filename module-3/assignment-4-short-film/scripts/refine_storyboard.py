"""Step 2b — align the LLM storyboard with the fixed 6-scene concept.

The free-form iteration 3 returned its own scene list; this step sends the fixed
concept skeleton to the same model and asks for an English text-to-video prompt
plus a TTS-friendly Russian voiceover for every scene. The run is appended to
logs/prompt_iterations.json/.md and the result is written to scripts/storyboard.json.
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

# Fixed concept (film concept approved before the run).
FIXED = [
    {"n": 1, "scene": "Текст", "duration_sec": 4,
     "brief": "abstract text fragments floating in dark space, letters assembling into words",
     "voiceover": "Всё начинается с текста. Несколько слов — и нейросеть уже видит образ."},
    {"n": 2, "scene": "Зарождение", "duration_sec": 5,
     "brief": "a seed of light grows into swirling colours, like a nebula forming",
     "voiceover": "Из шума рождается структура. Пиксель за пикселем — проявляется форма."},
    {"n": 3, "scene": "Форма", "duration_sec": 5,
     "brief": "a face or silhouette emerges from abstract colours, half-formed",
     "voiceover": "Сначала — силуэт. Потом — детали. Лицо, которого не существует."},
    {"n": 4, "scene": "Цвет", "duration_sec": 5,
     "brief": "colours flow and merge, creating a vibrant abstract landscape",
     "voiceover": "Палитра выбирает настроение. Тёплые тона — или холодные?"},
    {"n": 5, "scene": "Движение", "duration_sec": 5,
     "brief": "the image comes alive: elements move, the scene breathes",
     "voiceover": "И наконец — движение. Статика становится мгновением."},
    {"n": 6, "scene": "Результат", "duration_sec": 4,
     "brief": "final composite image, title «Рождение образа» and credits",
     "voiceover": "Так из текста рождается образ. Это и есть генеративное искусство."},
]

PROMPT = (
    "Ниже — фиксированная раскадровка короткометражного ролика «Рождение образа» "
    "(микродокументалка о том, как ИИ превращает текстовый промпт в изображение). "
    "Для каждой из шести сцен напиши:\n"
    "1) visual_prompt — на английском, готовый промпт для модели text-to-video: "
    "описание кадра, движение камеры, стиль, свет, настроение; не длиннее 380 символов; "
    "без текста в кадре, без людей крупным планом, без логотипов;\n"
    "2) voiceover_ru — закадровый текст на русском: одно-два предложения, "
    "осмысленные и связанные с действием сцены, числа записаны словами, "
    "без латиницы, длина 90–160 символов.\n\n"
    "Раскадровка:\n" +
    "\n".join(f"{s['n']}. {s['scene']} ({s['duration_sec']} с): {s['brief']}. "
              f"Текущий вариант закадрового текста: «{s['voiceover']}»" for s in FIXED) +
    "\n\nСтиль всего ролика: абстрактный, художественный, переход от тьмы к свету, "
    "от хаоса к форме; кинематографичная подача, единая цветовая палитра "
    "(глубокий синий, фиолетовый, тёплое золото). "
    "Ответ строго в формате JSON: {\"scenes\":[{\"scene_number\":1,"
    "\"visual_prompt\":\"...\",\"voiceover_ru\":\"...\"}]}"
)


def ask(prompt, temperature=0.7, max_tokens=2200):
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
    m = re.search(r"```(?:json)?\s*(.+?)```", text or "", re.S)
    raw = m.group(1) if m else (text or "")
    i, j = raw.find("{"), raw.rfind("}")
    if i < 0 or j <= i:
        return None
    try:
        return json.loads(raw[i:j + 1])
    except json.JSONDecodeError:
        return None


def main():
    log_path = LOGS / "prompt_iterations.json"
    log = json.loads(log_path.read_text(encoding="utf-8"))
    if any(r.get("iteration") == 4 for r in log["runs"]):
        print("iteration 4 already present, reusing it (no new call)")
        rec = next(r for r in log["runs"] if r.get("iteration") == 4)
    else:
        rec, _ = ask(PROMPT)
        rec["iteration"] = 4
        rec["label"] = "уточнение по фиксированной раскадровке"
        log["runs"].append(rec)
        log["total_cost_rub"] = round(sum(r.get("cost_rub", 0) or 0 for r in log["runs"]), 4)
        log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"iteration 4: HTTP {rec['http']} {len(rec.get('text') or '')} chars, "
              f"{rec.get('cost_rub', 0):.4f} RUB")

    data = parse_json(rec.get("text"))
    if not data:
        raise SystemExit("iteration 4 returned no parsable JSON")

    by_n = {}
    for s in data.get("scenes", []):
        n = int(s.get("scene_number") or s.get("n") or 0)
        by_n[n] = s

    scenes = []
    for s in FIXED:
        got = by_n.get(s["n"], {})
        scenes.append({
            "n": s["n"], "scene": s["scene"], "duration_sec": s["duration_sec"],
            "brief": s["brief"],
            "visual_prompt": (got.get("visual_prompt") or "").strip(),
            "voiceover": (got.get("voiceover_ru") or s["voiceover"]).strip(),
        })
    missing = [s["n"] for s in scenes if not s["visual_prompt"]]
    total_vo = sum(len(s["voiceover"]) for s in scenes)
    out = {
        "model": MODEL,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "title": "Рождение образа",
        "genre": "микродокументалка",
        "concept": ("как ИИ превращает текстовый промпт в визуальное изображение"),
        "fixed_concept_source": "scripts/refine_storyboard.py::FIXED",
        "iterations_used": [1, 2, 3, 4],
        "total_prompt_cost_rub": log["total_cost_rub"],
        "scenes": scenes,
        "voiceover_chars": total_vo,
        "total_video_seconds": sum(s["duration_sec"] for s in scenes[:5]),
    }
    (ROOT / "scripts" / "storyboard.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # rewrite the markdown log with every iteration, including this one
    md = ["# Итерации промптов сценария и раскадровки", "",
          f"Модель — `{MODEL}`, температура 0,7. Все промпты отправлены реально; "
          f"суммарная стоимость итераций — {log['total_cost_rub']:.4f} ₽.", ""]
    for r in log["runs"]:
        md += [f"## Итерация {r['iteration']} ({r['label']})", "",
               "**Промпт:**", "", f"> {r['prompt']}", "", "**Ответ модели:**", "",
               "```", (r.get("text") or r.get("error", ""))[:2000], "```", ""]
    (LOGS / "prompt_iterations.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"storyboard: {len(scenes)} scenes, {total_vo} chars of voiceover, "
          f"video part {out['total_video_seconds']}s")
    for s in scenes:
        print(f"  {s['n']}. {s['scene']:<11} {s['duration_sec']}s "
              f"vis={len(s['visual_prompt'])}ch vo={len(s['voiceover'])}ch")
    if missing:
        print("WARNING scenes without visual prompt:", missing)
    print("voiceover:", " | ".join(s["voiceover"] for s in scenes)[:400])


if __name__ == "__main__":
    main()
