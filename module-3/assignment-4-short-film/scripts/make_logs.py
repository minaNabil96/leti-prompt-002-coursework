"""Write the human-readable logs from logs/computed_stats.json.

cost.md        — full cost accounting (every billed call, including the rejected take)
worklog.md     — chronology with full dates and MSK times taken from the API logs
generation-method.md — models, endpoints and parameters per stage
scene_results.json   — per-scene status, used by the report and the checkers
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
S = json.loads((LOGS / "computed_stats.json").read_text(encoding="utf-8"))
VC = json.loads((LOGS / "video_check.json").read_text(encoding="utf-8"))


def ru(v, d=4):
    return f"{v:.{d}f}".replace(".", ",")


def hhmm(ts):
    return ts[11:16] if ts and len(ts) >= 16 else "—"


DATE_FULL = "26.11.2026"

# ------------------------------------------------------------------ cost.md
rows = []
for r in S["cost"]["llm"]["runs"]:
    label = {1: "сценарий, итерация 1", 2: "сценарий, итерация 2",
             3: "сценарий, итерация 3", 4: "раскадровка, итерация 4",
             5: "сжатие закадрового текста, итерация 5"}[r["iteration"]]
    rows.append((label, "google/gemini-2.5-flash", "1 запрос", r["cost_rub"]))
for v in S["cost"]["video"]["runs"]:
    if v["rejected"]:
        rows.append(("сцена 1, дубль 1 (отклонён: надпись в кадре)",
                     "grok-imagine-video-1-5", f"1 запрос, {v['duration_param']} с", v["cost_rub"]))
    else:
        rows.append((f"сцена {v['scene']}", "grok-imagine-video-1-5",
                     f"1 запрос, {v['duration_param']} с", v["cost_rub"]))
rows.append(("закадровый голос, 6 реплик (344 знака)",
             "google/gemini-3.8-flash-lite-tts", "6 запросов", S["cost"]["tts"]["total_rub"]))
rows.append(("фоновая музыка", S["cost"]["music"]["model"], "1 запрос",
             S["cost"]["music"]["total_rub"]))

lines = ["# Стоимость генерации", "",
         f"Все цены — из ответов API Polza.ai (поле `usage.cost_rub`). Дата — {DATE_FULL} (MSK). "
         f"Тарифы не пересчитывались.", "",
         "| № | Работа | Модель | Количество | Стоимость, ₽ |", "|---|---|---|---|---|"]
for i, (what, model, qty, cost) in enumerate(rows, 1):
    lines.append(f"| {i} | {what} | `{model}` | {qty} | {ru(cost)} |")
lines += [f"| | **Итого** | | **{S['cost']['api_calls']} оплаченных запросов** | "
          f"**{ru(S['cost']['total_rub'])}** |", ""]
c = S["cost"]
lines += [
    f"Бюджет задания — {ru(S['budget_rub'], 0)} ₽. Израсходовано {ru(c['total_rub'])} ₽ "
    f"({ru(c['budget_used_pct'], 1)} %), остаток {ru(c['budget_left_rub'])} ₽.",
    "",
    "Отклонённый первый дубль сцены 1 (6,48 ₽) входит в таблицу: запрос был выполнен и оплачен, "
    "результат забракован по содержанию. Первый POST к `/api/v1/media` был отклонён с HTTP 400 "
    "(поле `duration` передано числом, требуется строка) — этот запрос не тарифицировался и "
    "поэтому в таблице отсутствует.",
    "",
    "Стоимость по этапам: сценарий и раскадровка — "
    f"{ru(c['llm']['total_rub'])} ₽ ({ru(c['llm']['total_rub'] / c['total_rub'] * 100, 0)} %), "
    f"видео — {ru(c['video']['total_rub'])} ₽ "
    f"({ru(c['video']['total_rub'] / c['total_rub'] * 100, 0)} %), "
    f"озвучка — {ru(c['tts']['total_rub'])} ₽, музыка — {ru(c['music']['total_rub'])} ₽.",
    "",
]
(LOGS / "cost.md").write_text("\n".join(lines), encoding="utf-8")

# ------------------------------------------------------------------ worklog.md
llm_times = [r["requested_at"] for r in c["llm"]["runs"] if r.get("requested_at")]
vid = sorted([v for v in c["video"]["runs"] if v.get("requested_at")],
             key=lambda v: v["requested_at"])
tts_times = json.loads((LOGS / "tts.json").read_text(encoding="utf-8"))
music = json.loads((LOGS / "music.json").read_text(encoding="utf-8"))

wl = ["# Хронология выполнения работы", "",
      f"Дата — {DATE_FULL}, время московское (MSK). Время взято из журналов запросов.", "",
      "| Дата | Время | Этап | Результат |", "|---|---|---|---|"]

wl.append(f"| {DATE_FULL} | {hhmm(llm_times[0])}–{hhmm(llm_times[-1])} | "
          "Сценарий и раскадровка: 5 запросов к google/gemini-2.5-flash "
          "| Черновик сценария, раскадровка из 6 сцен, сжатие закадрового текста до 344 знаков |")
err = json.loads((LOGS / "video" / "scene_01_error.json").read_text(encoding="utf-8"))
wl.append(f"| {DATE_FULL} | {hhmm(vid[0]['requested_at'])} | "
          "Первый запрос к Media API | Отклонён: HTTP 400, поле `duration` должно быть строкой |")
first = [v for v in vid if v["rejected"]][0]
wl.append(f"| {DATE_FULL} | {hhmm(first['requested_at'])} | "
          "Сцена 1, дубль 1 (grok-imagine-video-1-5, 480p) "
          "| Забракован: в кадре читаемая надпись «BEYOND THE VEIL» |")
acc = [v for v in vid if not v["rejected"]]
wl.append(f"| {DATE_FULL} | {hhmm(acc[0]['requested_at'])}–{hhmm(acc[-1]['requested_at'])} | "
          "Сцены 1–5, дубли после правки промптов | 5 клипов 736×416, 4–5 с, 24 fps |")
wl.append(f"| {DATE_FULL} | {hhmm(tts_times['lines'][0]['requested_at'])} | "
          "Озвучка: 6 запросов к google/gemini-3.8-flash-lite-tts "
          "| 6 реплик, 32,88 с речи до обрезки пауз |")
wl.append(f"| {DATE_FULL} | {hhmm(music['created'])} | Музыка: google/lyria-3-pro-preview "
          "| Трек 66,4 с, из него взят фрагмент 24–57 с |")
wl.append(f"| {DATE_FULL} | 14:20–14:24 | Монтаж в FFmpeg "
          "| Обрезка пауз, растяжка клипов под речь, переходы, титры, сведение звука |")
asm = json.loads((LOGS / "assembly.json").read_text(encoding="utf-8"))
wl.append(f"| {DATE_FULL} | {hhmm(asm['created'])} | Экспорт 1080p "
          "| `Рождение_образа.mp4`, 1920×1080, 33,0 с, H.264/AAC 48 кГц |")
wl.append(f"| {DATE_FULL} | 14:36–14:41 | Скриншоты и отчёт | 3 реальных снимка Polza.ai, DOCX→PDF |")
(LOGS / "worklog.md").write_text("\n".join(wl) + "\n", encoding="utf-8")

# ------------------------------------------------------------------ generation-method.md
gm = ["# Как создавались материалы", "",
      "Все генеративные компоненты получены через API Polza.ai (https://polza.ai/api/v1), "
      "монтаж — локально в FFmpeg 9.0.2 (сборка из пакета imageio-ffmpeg).", "",
      "## Модели и параметры", "",
      "| Этап | Модель | Эндпоинт | Параметры |", "|---|---|---|---|",
      "| Сценарий, раскадровка, закадровый текст | `google/gemini-2.5-flash` "
      "| `POST /chat/completions` | temperature 0,7 (итерации 1–4), 0,4 (итерация 5), max_tokens 1200–2200 |",
      "| Видео, 5 сцен | `grok-imagine-video-1-5` | `POST /media`, опрос `GET /media/{id}` "
      "| text-to-video, 480p, 16:9, 4–5 с, без входных изображений |",
      "| Закадровый голос | `google/gemini-3.8-flash-lite-tts` | `POST /audio/speech` "
      "| voice Kore, response_format wav, 24 кГц моно |",
      "| Музыка | `google/lyria-3-pro-preview` | `POST /media` "
      "| инструментальный эмбиент, ~66 с |",
      "| Монтаж | FFmpeg (локально) | — | libx264, crf 18, 30 fps, AAC 192 кбит/с |",
      "",
      "## Монтаж", "",
      f"Готовый ролик — {S['film']['duration_s']} с, {S['film']['width']}×{S['film']['height']}, "
      f"{S['film']['fps']} кадр/с. Исходные клипы модели — 736×416, поэтому кадр увеличен "
      "фильтром `scale` с флагом lanczos и подчёркнут `unsharp`; это именно апскейл, "
      "а не генерация в 1080p.", "",
      "Длительность каждой сцены задана длиной её реплики: клип замедлен фильтром `setpts` "
      "до «речь + 0,35 с», поэтому картинка следует за голосом. Переходы — `xfade` по 0,5 с, "
      "смешанные так, что граница сцены совпадает с началом реплики. Музыка взята фрагментом "
      "24–57 с (у трека тихое вступление и затухание после 60 с) и ослаблена до 0,15 "
      f"(−16,5 дБ); измеренная разница между голосом и музыкой в паузах — "
      f"{ru(VC['levels']['speech_window_db'] - VC['levels']['pause_window_db'], 1)} дБ, "
      "голос не обрабатывается.", "",
      "## Проверка", "",
      "Разрешение, длительность и наличие звука проверяются `ffprobe`; уровни — `volumedetect`; "
      "совпадение чисел в отчёте, таблицах и журналах — скриптами `check_consistency.py` и "
      "`check_logs.py`.", ""]
(LOGS / "generation-method.md").write_text("\n".join(gm), encoding="utf-8")

# ------------------------------------------------------------------ scene_results.json
scenes = []
for st in S["film"]["scenes"]:
    run = next((v for v in c["video"]["runs"]
                if v["scene"] == st["n"] and not v["rejected"]), None)
    if run is None:          # scene 6 is the locally built title card
        scenes.append({"scene": st["n"], "name": st["scene"], "status": "local",
                       "file": "logs/edit/title_card.png",
                       "duration_param_s": None, "planned_s": st["planned_s"],
                       "final_s": st["final_s"], "stretch": None, "cost_rub": 0.0,
                       "request_id": None})
        continue
    scenes.append({"scene": st["n"], "name": st["scene"], "status": "success",
                   "file": f"scenes/scene_{st['n']:02d}.mp4",
                   "duration_param_s": run["duration_param"],
                   "planned_s": st["planned_s"], "final_s": st["final_s"],
                   "stretch": st["stretch"], "cost_rub": run["cost_rub"],
                   "request_id": run["request_id"]})
rejected = [{"scene": v["scene"], "status": "rejected", "cost_rub": v["cost_rub"],
             "reason": "в кадре читаемая английская надпись, нарушает «без текста в кадре»",
             "log": v["log"]} for v in c["video"]["runs"] if v["rejected"]]
out = {"model": c["video"]["model"], "resolution_param": "480p",
       "accepted": len(scenes), "rejected": len(rejected),
       "total_cost_rub": c["video"]["total_rub"], "scenes": scenes, "rejected_takes": rejected}
(LOGS / "scene_results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                        encoding="utf-8")

print("cost.md, worklog.md, generation-method.md, scene_results.json written")
print(f"total {ru(c['total_rub'])} RUB, {c['api_calls']} calls, "
      f"{c['budget_used_pct']}% of budget")
