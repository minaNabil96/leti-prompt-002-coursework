"""Rule I consistency pass for the М3-А1 report: numbers, dates, figures, wording."""
import json
import pathlib
import re

import pymupdf
from docx import Document

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCX = ROOT / "report" / "Отчет_М3_Задание1.docx"
PDF = ROOT / "report" / "Отчет_М3_Задание1.pdf"
LOGS = ROOT / "logs"
SHOTS = ROOT / "screenshots"
STATS = json.loads((LOGS / "computed_stats.json").read_text(encoding="utf-8"))

d = Document(DOCX)
paras = [p.text for p in d.paragraphs]
cells = [c.text for t in d.tables for row in t.rows for c in row.cells]
full = "\n".join(paras + cells)
logs = {p.name: p.read_text(encoding="utf-8") for p in LOGS.glob("*.md")}
pdf = pymupdf.open(PDF)
pdf_text = "\n".join(p.get_text() for p in pdf)
res = []


def chk(name, ok, detail=""):
    res.append(ok)
    print(("PASS" if ok else "FAIL"), name, ("| " + detail) if detail else "")


def num(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


C = STATS["cost"]
P = STATS["prosody"]
T = STATS["tts"]
S = STATS["stt"]

# 1. money: one machine-readable source for every figure in the text and logs
chk("1.1 Итого 13,2666 и полная стоимость 13,2761 совпадают с протоколами",
    C["reported_rub"] == 13.2666 and C["total_rub"] == 13.2761
    and "13,2666" in full and "13,2761" in full
    and "13,2666" in logs["cost.md"])
chk("1.2 Округление 13,27 и остаток 1,7334 указаны",
    "13,27" in full and num(C["remainder_rub"], 4) in full
    and abs(15 - C["reported_rub"] - C["remainder_rub"]) < 1e-9)
chk("1.3 Компоненты 1,9649 + 6,3149 + 0,6861 + 4,3007 = 13,2666",
    abs(C["llm_rub"] + C["tts_rub"] + C["stt_rub"] + C["ui_repeat_rub"]
        - 13.2666) < 1e-9
    and all(num(v, 4) in full for v in (C["llm_rub"], C["tts_rub"], C["stt_rub"],
                                        C["ui_repeat_rub"])))
chk("1.4 Калибровка 0,0095 указана и в отчёте, и в журнале",
    "0,0095" in full and "0,0095" in logs["worklog.md"]
    and "0,0095" in logs["cost.md"])
chk("1.5 Доля TTS 48 % соответствует расчёту",
    C["tts_share_pct"] == 48 and "48 %" in full)
chk("1.6 Бюджет 15 ₽ фигурирует в отчёте и в cost.md",
    "15 ₽" in full and "15 ₽" in logs["cost.md"])

# 2. speech measurements
chk("2.1 Медиана тона 163,1 Гц и диапазон 159–170 Гц",
    num(P["f0_median_hz"], 1) == "163,1" and "163,1 Гц" in full
    and "от 159 до 170 Гц" in full
    and P["f0_median_min_hz"] == 159 and P["f0_median_max_hz"] == 170)
chk("2.2 Доля речи 0,75–0,82",
    num(P["speech_ratio_min"]) == "0,75" and num(P["speech_ratio_max"]) == "0,82"
    and "0,75–0,82" in full)
chk("2.3 Длительность 381,52 с (измерение) и 381,16 с (API) названы",
    num(P["duration_s"]) in full and num(T["api_duration_s"]) in full)
chk("2.4 138 пауз, средняя 0,50 с, максимум 1,11 с",
    "138 пауз" in full and num(P["pause_mean_s"]) in full
    and num(P["pause_max_s"]) in full
    and P["pause_count"] == 138)
chk("2.5 Минуты распознавания 6,35 в таблице Б.3",
    num(S["minutes"]) == "6,35" and "6,35 мин" in full and "6,36" not in full)
chk("2.6 Средний ответ в 16 раз длиннее вопроса",
    "в 16 раз" in full and "в 15 раз" not in full)

# 3. captions and figures
caps = [p for p in paras if re.match(r"^Рисунок \d — ", p)]
chk("3.1 Пять подписей по порядку", len(caps) == 5
    and [c.split(" — ")[0] for c in caps] == [f"Рисунок {i}" for i in range(1, 6)],
    str(len(caps)))
chk("3.2 Снимки 1–3 названы экраном беседы и экраном настроек",
    "Экран беседы" in caps[0] and caps[1].startswith("Рисунок 2 — Экран настроек")
    and caps[2].startswith("Рисунок 3 — Экран настроек"))
chk("3.3 Визуализации 4–5 подписаны «Визуализация данных»",
    caps[3].startswith("Рисунок 4 — Визуализация данных")
    and caps[4].startswith("Рисунок 5 — Визуализация данных"))
chk("3.4 Все пять файлов рисунков существуют",
    all(f.exists() for f in (
        SHOTS / "01_chat_screen_live.png",
        SHOTS / "02_settings_chat_model.png",
        SHOTS / "03_settings_tts_model.png",
        SHOTS / "01_conversation_screen.png",
        SHOTS / "03_tts_analysis.png"))
    and len(d.inline_shapes) == 5)
chk("3.5 Ни одна визуализация не названа скриншотом",
    not re.search(r"Рисунок \d — (Скриншот|скриншот)", full)
    and "композит" not in full.lower())
chk("3.6 Слово «скриншот» только в цитате задания",
    full.count("скриншот") == 1
    and "К отчёту приложите 2–3 скриншота" in full)

# 4. dates and work log
dates = set(re.findall(r"\b\d{2}\.\d{2}\.\d{4}\b", full))
chk("4.1 В отчёте только полные даты 25.11.2026 и 26.11.2026",
    dates == {"25.11.2026", "26.11.2026"},
    str(sorted(dates)))
tbl = d.tables[5]
rows = [r.cells[0].text.strip() for r in tbl.rows[1:]]
chk("4.2 Каждая строка таблицы Б.1 начинается с полной даты",
    all(re.match(r"^\d{2}\.\d{2}\.\d{4}, \d{2}:\d{2}$", r) for r in rows),
    str(rows[:2]))
chk("4.3 Подпись Б.1 содержит обе даты работы",
    "25.11.2026–26.11.2026" in full)
chk("4.4 Журнал: разделы датированы полными датами",
    "25.11.2026, 18:20" in logs["worklog.md"]
    and "26.11.2026, 00:21" in logs["worklog.md"])
chk("4.5 Журнал: каждая строка хронологии с датой",
    len(re.findall(r"^\| \d{2}\.\d{2}\.\d{4}, \d{2}:\d{2}", logs["worklog.md"], re.M)) >= 18)
chk("4.6 Дата снимков 26.11.2026 есть в подписях рисунков 2 и 3",
    "26.11.2026" in caps[1] and "26.11.2026" in caps[2])

# 5. technical wording
chk("5.1 pYIN назван алгоритмом, Praat — программой",
    "алгоритмом pYIN" in full and "в программе Praat" in full
    and "методом Praat" not in full and "методом Praat" not in logs["analysis.md"])
chk("5.2 В prosody.json указан pYIN, как в отчёте",
    json.loads((LOGS / "prosody.json").read_text(encoding="utf-8"))["method"]["pitch"]
    .startswith("librosa pYIN"))
chk("5.3 HNR — to_harmonicity_cc",
    "to_harmonicity_cc" in logs["worklog.md"])

# 6. hygiene
chk("6.1 Нет заглушек и запрещённых слов",
    not re.search(r"TODO|XXX|FIXME|placeholder|симуляц|макет|mock|композит", full, re.I)
    and full.count("___") <= 1)
chk("6.2 В тексте нет квадратных и угловых скобок",
    "[" not in full and "<" not in full)
chk("6.3 Кафедра ИС, старой кафедры нет",
    "Кафедра ИС" in full and "связи с общественностью" not in full)
chk("6.4 Титул: отчет строчными, по заданию полужирным",
    "отчет" in paras and "по заданию" in paras
    and "Тема: Голосовая беседа с AI-ассистентом" in paras)
chk("6.5 Нет двойных пробелов в абзацах",
    all("  " not in p and p == p.strip() for p in paras))
chk("6.6 Поля 2 см и A4",
    all(abs(getattr(s, m).cm - 2) < 0.01 for s in d.sections
        for m in ("top_margin", "bottom_margin", "left_margin", "right_margin"))
    and all(abs(s.page_width.mm - 210) < 0.5 for s in d.sections))

# 7. PDF
chk("7.1 PDF собран: 19 страниц", pdf.page_count == 19, f"{pdf.page_count} стр.")
chk("7.2 Нумерация со второй страницы, на титуле номера нет",
    pdf[0].get_text().strip().endswith("2026")
    and pdf[1].get_text().strip().startswith("2")
    and pdf[-1].get_text().strip().startswith(str(pdf.page_count)))
chk("7.3 PDF и DOCX совпадают по ключевым числам",
    all(num(v, 4) in pdf_text for v in (C["llm_rub"], C["tts_rub"], C["stt_rub"])))
chk("7.4 Все подписи рисунков попали в PDF",
    all(c.split(" — ")[0] in pdf_text for c in caps))

print("\nSUMMARY", sum(res), "/", len(res))
if not all(res):
    raise SystemExit(1)
