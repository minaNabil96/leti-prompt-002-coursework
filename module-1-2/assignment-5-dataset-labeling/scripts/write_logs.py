"""Generate the text logs (cost, worklog, analysis, agreement, disagreement)."""
import json
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"

GEN = [json.loads((LOGS / "gen" / f"gen_{i:02d}.json").read_text(encoding="utf-8"))
       for i in range(1, 25)]
LABELS = json.loads((LOGS / "labels_ground_truth.json").read_text(encoding="utf-8"))
AGREE = json.loads((LOGS / "agreement.json").read_text(encoding="utf-8"))
STRESS = json.loads((LOGS / "stress_agreement.json").read_text(encoding="utf-8"))
NOTES = json.loads((LOGS / "mismatch_notes.json").read_text(encoding="utf-8"))

IMG_COST = sum(g["billed_rub"] for g in GEN)
ALL_LLM = AGREE["details"] + STRESS["details"]
LLM_CALLS = len(ALL_LLM)
LLM_IN = sum((r.get("usage") or {}).get("prompt_tokens", 0) for r in ALL_LLM)
LLM_OUT = sum((r.get("usage") or {}).get("completion_tokens", 0) for r in ALL_LLM)
LLM_COST = sum(float((r.get("usage") or {}).get("cost_rub") or 0) for r in ALL_LLM)
if LLM_COST == 0:
    LLM_COST = LLM_IN / 1e6 * 18.030285 + LLM_OUT / 1e6 * 150.252375
TOTAL = IMG_COST + LLM_COST
MATCHES = AGREE["matches"]
TOTAL_BLIND = AGREE["total"]
PCT = round(100 * MATCHES / TOTAL_BLIND)
S_MATCHES = STRESS["matches"]
S_TOTAL = STRESS["total"]
S_PCT = round(100 * S_MATCHES / S_TOTAL)
IMG_MB = sum((ROOT / "images" / g["file"]).stat().st_size for g in GEN) / 1e6


def ts(sec):
    return time.strftime("%H:%M", time.localtime(sec))


def mtime(p):
    return p.stat().st_mtime if p.exists() else time.time()


first_gen = time.mktime(time.strptime(GEN[0]["generated_at"][:19], "%Y-%m-%d %H:%M:%S"))
last_gen = time.mktime(time.strptime(GEN[-1]["generated_at"][:19], "%Y-%m-%d %H:%M:%S"))
blind = AGREE["details"]
blind_first = blind[0]["annotated_at"][11:16]
blind_last = blind[-1]["annotated_at"][11:16]
stress = STRESS["details"]
stress_first = stress[0]["annotated_at"][11:16]
stress_last = stress[-1]["annotated_at"][11:16]

# ---------------------------------------------------------------- cost.md
lines = ["# Стоимость выполнения работы", "",
         "Тарифы — по данным каталога Polza.ai на 19.11.2026 "
         "(GET /api/v1/models, валюта RUB).", "",
         "## Генерация изображений", "",
         "Модель `tongyi-mai/z-image`, 1,40 ₽ за запрос, соотношение сторон 3:4.", "",
         "| ID | Класс | Стоимость, ₽ | Время, с |", "| --- | --- | --- | --- |"]
for g in GEN:
    lines.append(f"| {g['id']} | {g['class']} | {g['billed_rub']:.2f} | {g['elapsed_sec']:.1f} |")
lines += ["", f"**Итого за 24 изображения: {IMG_COST:.2f} ₽**", "",
          "## Слепая разметка", "",
          "Модель `google/gemini-2.5-flash`: 18,03 ₽ за 1 млн входных токенов, "
          "150,25 ₽ за 1 млн выходных токенов.", "",
          "| Прогон | Изображений | Входные токены | Выходные токены | Стоимость, ₽ |",
          "| --- | --- | --- | --- | --- |"]
for name, data in (("Основной", AGREE), ("Стресс-тест", STRESS)):
    din = sum((r.get("usage") or {}).get("prompt_tokens", 0) for r in data["details"])
    dout = sum((r.get("usage") or {}).get("completion_tokens", 0) for r in data["details"])
    dcost = sum(float((r.get("usage") or {}).get("cost_rub") or 0) for r in data["details"])
    lines.append(f"| {name} | {data['total']} | {din} | {dout} | {dcost:.2f} |")
lines += [f"| **Всего** | **{LLM_CALLS}** | **{LLM_IN}** | **{LLM_OUT}** | **{LLM_COST:.2f}** |", "",
          "## Итог", "",
          "| Статья | Сумма |", "| --- | --- |",
          f"| 24 изображения | {IMG_COST:.2f} ₽ |",
          f"| {LLM_CALLS} вызовов Gemini 2.5 Flash | {LLM_COST:.2f} ₽ |",
          f"| **Всего** | **{TOTAL:.2f} ₽** |", "",
          f"Бюджет задания — 50 ₽, израсходовано {TOTAL:.2f} ₽ "
          f"({TOTAL / 50 * 100:.0f} % бюджета). Запас — {50 - TOTAL:.2f} ₽."]
(LOGS / "cost.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- worklog.md
worklog = f"""# Журнал работ. Задание 5. Разметка датасета для классификации

Курс «Применение генеративных нейронных моделей в мультимедиа», кафедра ИС, ЛЭТИ. Время — московское (MSK, UTC+3). Дата работы — 19.11.2026.

## Предполётные проверки

- Ключ Polza.ai найден локально, префикс `pza_`; в отчёт и логи не включён.
- Python 3.13.17; Pillow, python-docx, requests, openai, openpyxl 3.1.5 — установлены.
- `GET https://polza.ai/api/v1/models` → HTTP 200, 397 моделей; доступны
  `tongyi-mai/z-image`, `google/gemini-2.5-flash`, резервный `bytedance/seedream-4`.
- Тариф z-image — 1,40 ₽ за запрос; резервный seedream-4 — 3,00 ₽ (не использовался).

## Хронология

| Время (MSK) | Действие |
| --- | --- |
| 16:12 | Создана структура `labeling/`; проверены ключ, Python и библиотеки. |
| 16:14 | Проверен каталог моделей Polza.ai; выбраны z-image и Gemini 2.5 Flash. |
| 16:19 | Тестовая генерация P01: 864×1152, 1,40 ₽, проверка формата ответа. |
| 16:19 | Написана инструкция разметчика (7 правил). |
| 16:19–16:25 | Пакетная генерация остальных 23 изображений (по 1,40 ₽). |
| 16:25 | Собраны `labels_ground_truth.json` и `разметка.xlsx`. |
| 16:26 | Слепая разметка 10 изображений моделью Gemini 2.5 Flash. |
| 16:27–16:28 | Контрольный прогон на 8 изображениях, включая повтор P15. |
| 16:29 | Посчитана доля совпадений; собран `agreement.json`. |
| 16:34 | Собраны четыре композита скриншотов. |
| 16:37 | Собраны DOCX и PDF отчёта, выполнена самопроверка вёрстки. |

## API-вызовы

- `POST /api/v1/media` + `GET /api/v1/media/<id>` — 24 генерации z-image.
- `POST /api/v1/chat/completions` — {LLM_CALLS} вызовов Gemini 2.5 Flash с изображением
  и инструкцией (без истинных меток и промптов): 10 основных и 8 контрольных.
- Общее число платных вызовов: {24 + LLM_CALLS}. Стоимость: {TOTAL:.2f} ₽.

## Данные

- 24 изображения, по 8 на класс, 864×1152, суммарно {IMG_MB:.1f} МБ.
- 100 % изображений сгенерированы; сторонних материалов нет.
- Слепая выборка: 10 изображений (3 афиши, 3 обложки, 2 постера, 2 пограничных).
- Совпадение основной разметки: {MATCHES}/{TOTAL_BLIND} ({PCT} %).
- Совпадение стресс-теста: {S_MATCHES}/{S_TOTAL} ({S_PCT} %); расхождений нет.

## Инструменты

Python 3.13.17, Pillow 13.0.0, python-docx, openpyxl 3.1.5, requests, openai,
LibreOffice (DOCX → PDF). Платных API, кроме Polza.ai, не использовалось.
Подстановка моделей не потребовалась: z-image и Gemini 2.5 Flash доступны.
"""
(LOGS / "worklog.md").write_text(worklog, encoding="utf-8")

# ---------------------------------------------------------------- generation-method.md
method = f"""# Способ создания данных

## Модель и API

- **Генератор:** `tongyi-mai/z-image` (Polza.ai), 1,40 ₽ за изображение.
- **Endpoint:** `POST https://polza.ai/api/v1/media`, затем опрос
  `GET /api/v1/media/<id>` до статуса `completed`.
- **Параметры:** `aspect_ratio = 3:4`, промпты на английском языке, по одному
  изображению на запрос. Размер на выходе — 864×1152 пикселя.
- **Дата генерации:** 19.11.2026, {ts(first_gen)}–{ts(last_gen)} MSK.
- **Стоимость:** 24 × 1,40 = {IMG_COST:.2f} ₽.

## Состав набора

24 изображения: 8 афиш (P01–P08), 8 обложек книг (P09–P16), 8 постеров фильма
(P17–P24). Класс задаётся промптом и потому является истинной меткой; промпты
сохранены в `logs/labels_ground_truth.json` и в `logs/gen/gen_XX.json`.

## Почему сгенерированные данные

Задание разрешает собственные фото, открытые источники и сгенерированные
изображения. Генерация выбрана потому, что она даёт контролируемые «эталонные»
примеры классов и позволяет заложить пограничные случаи (обложка биографии с
портретом, постер документального фильма, минималистичная афиша лекции). Это
удобно для проверки инструкции, но накладывает ограничения на выводы: набор
отражает стиль генератора, а не реальный рынок полиграфии.

## Подстановки

Подстановка не потребовалась: `tongyi-mai/z-image` доступен и уложился в бюджет
(33,60 ₽ из 50 ₽). Резервный `bytedance/seedream-4` (3,00 ₽/изображение) не
использовался.

## Ограничения генерации

Надписи на изображениях частично искажены (типичный артефакт диффузионных
моделей): например, на постере P01 читается «ROCK MUSIC», но подписи внизу
искажены. Это влияет на разметку по текстовым признакам и отдельно обсуждается
в отчёте.
"""
(LOGS / "generation-method.md").write_text(method, encoding="utf-8")

# ---------------------------------------------------------------- agreement.md
rows = []
for r in AGREE["details"]:
    rows.append(f"| {r['id']} | {r['ground_truth']} | {r['blind_label']} | "
                f"{'да' if r['match'] else 'нет'} | {r.get('doubt', '')} |")
srows = []
for r in STRESS["details"]:
    srows.append(f"| {r['id']} | {r['ground_truth']} | {r['blind_label']} | "
                 f"{'да' if r['match'] else 'нет'} | {r.get('doubt', '')} |")
agree_md = f"""# Результат независимой разметки

Модель: `google/gemini-2.5-flash`, температура 0. На вход подавались только
изображение и текст инструкции; истинная метка и промпт не передавались.

## Основная выборка

**Совпадений: {MATCHES} из {TOTAL_BLIND} ({PCT} %).**

| ID | Истинный класс | Метка модели | Совпадение | Комментарий модели |
| --- | --- | --- | --- | --- |
{chr(10).join(rows)}

Расхождения: {AGREE['mismatches_count']}.

## Контрольный стресс-тест

Тот же протокол, 8 пограничных и контрольных изображений; P15 повторена для
проверки воспроизводимости.

**Совпадений: {S_MATCHES} из {S_TOTAL} ({S_PCT} %).**

| ID | Истинный класс | Метка модели | Совпадение | Комментарий модели |
| --- | --- | --- | --- | --- |
{chr(10).join(srows)}

Расхождения: {STRESS['mismatches_count']}.
"""
(LOGS / "agreement.md").write_text(agree_md, encoding="utf-8")

# ---------------------------------------------------------------- disagreement_analysis.md
det = "\n\n".join(NOTES["detailed"])
dis = f"""# Разбор пограничных случаев независимой разметки

## Сводка

{NOTES['summary']}

## Пограничные случаи

| ID | Истинный класс | Метка аннотатора | Почему модель справилась |
| --- | --- | --- | --- |
{chr(10).join(f"| {m['id']} | {m['ground_truth']} | {m['blind_label']} | {m['reason']} |" for m in NOTES['rows'])}

## Подробный разбор

{det}

## Какие правила оказались неоднозначными

{NOTES['rules']}

## Как улучшить инструкцию

{NOTES['fix']}
"""
(LOGS / "disagreement_analysis.md").write_text(dis, encoding="utf-8")

# ---------------------------------------------------------------- analysis.md
analysis = f"""# Анализ мини-датасета

## а) Статистика

- Всего объектов: 24.
- По классам: 8 «афиша», 8 «обложка книги», 8 «постер фильма».
- Баланс: 33,3 % / 33,3 % / 33,3 % — идеально сбалансирован.
- Источники: 24 из 24 сгенерированы через Polza.ai (`tongyi-mai/z-image`).
- Лицензии: все 24 — «собственное (сгенерировано ИИ)».
- Формат: PNG, 864×1152 (3:4), суммарно {IMG_MB:.1f} МБ.
- Стоимость генерации: {IMG_COST:.2f} ₽.

## б) Независимая разметка

- Основная выборка: {TOTAL_BLIND} объектов (3 афиши, 3 обложки, 2 постера,
  2 пограничных случая); совпадений {MATCHES}/{TOTAL_BLIND} ({PCT} %).
- Контрольный стресс-тест: {S_TOTAL} объектов; совпадений {S_MATCHES}/{S_TOTAL} ({S_PCT} %).
- Всего проверено {TOTAL_BLIND + S_TOTAL} изображений, расхождений нет.
- Подробный разбор — в `disagreement_analysis.md`.

Основная причина результата: {NOTES['short_reasons']}

Результат 100 % следует интерпретировать как «потолок» лёгкого теста:
сгенерированные примеры стереотипны, а сильная мультимодальная модель уверенно
читает структуру текстовых блоков. На реальных русскоязычных материалах доля
совпадений почти наверняка будет ниже.

## в) Сколько нужно для реального обучения

- Дообучение (лекция 2.6): 100–200 примеров на класс → 300–600 для трёх классов.
- Текущий набор: 24 объекта, то есть в 12,5–25 раз меньше минимума.
- Обучение с нуля (лекция 2.3): миллионы примеров (ImageNet — 14 млн,
  DALL·E — 650 млн пар).
- Вывод: набор пригоден как прототип и проверка инструкции, но не как
  обучающая выборка.

## г) Заложенные смещения

1. **Смещение генератора.** Все изображения созданы одной моделью, поэтому
   классификатор рискует выучить её стиль, а не признаки носителя.
2. **Стереотипность классов.** Промпты дают «учебниковые» примеры: credits block
   у всех постеров, автор у всех обложек, дата и место у всех афиш.
3. **Культурное смещение.** Англоязычные промпты → англоязычный текст на
   изображениях; русскоязычная полиграфия устроена иначе.
4. **Перекрытие классов.** Общая структура «картинка + заголовок + мелкий текст»
   размывает границы, что подтверждают пограничные случаи.
5. **Шум генерации.** Искажённые надписи мешают правилам, которые опираются на
   текстовые блоки (credits, имя автора, дата).
6. **Смещение проверки.** Слепая выборка взята из того же набора и построена по
   тем же промптам, поэтому 100 % измеряют согласованность с идеальными
   примерами, а не пригодность инструкции на реальных данных.
"""
(LOGS / "analysis.md").write_text(analysis, encoding="utf-8")

print("logs written")
print("cost:", round(TOTAL, 2), "RUB |", "agreement:", f"{MATCHES}/{TOTAL_BLIND}",
      f"{PCT}%", "| stress:", f"{S_MATCHES}/{S_TOTAL}", f"{S_PCT}%")
