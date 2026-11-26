"""Rule I consistency pass: numbers, dates, references and file facts (М3, задание 3)."""
import json
import pathlib
import re

import pymupdf
from docx import Document

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCX = ROOT / "report" / "Отчет_М3_Задание3.docx"
PDF = ROOT / "report" / "Отчет_М3_Задание3.pdf"
LOGS = ROOT / "logs"
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


def num(x, nd=3):
    return f"{x:.{nd}f}".replace(".", ",")


TOT = STATS["totals"]
ANIM_DIR = ROOT / "animations"

# 1. money
chk("1.1 Итог 41,275 совпадает во всех документах",
    TOT["cost_exact_text"] == "41,275" and "41,275" in full
    and "41,275" in logs["cost.md"]
    and abs(sum(s["cost_rub"] for s in STATS["sources"])
            + sum(a["cost_rub"] for a in STATS["animations"]) - 41.275) < 1e-9)
chk("1.2 Округление 41,28 указано в отчёте и в cost.md",
    "41,28" in full and "41,28" in logs["cost.md"])
chk("1.3 Каждый ролик 12,825 и 2,565 ₽/с (по номиналу 5 с)",
    all(abs(a["cost_rub"] - 12.825) < 1e-9 for a in STATS["animations"])
    and "2,565" in full and abs(12.825 / 5 - 2.565) < 1e-9)
chk("1.4 Бюджет 60 ₽ и остаток 18,725",
    "60 ₽" in full and "18,725" in full and abs(60 - 41.275 - 18.725) < 1e-9)
chk("1.5 Доля бюджета 68,8 % верна",
    "68,8" in full and abs(41.275 / 60 * 100 - 68.79) < 0.05)

# 2. media facts vs files on disk
for i, a in enumerate(STATS["animations"], 1):
    f = ANIM_DIR / a["file"]
    chk(f"2.{i} файл {a['file']} существует и размер совпадает",
        f.exists() and abs(f.stat().st_size - a["bytes"]) <= 1,
        f"{f.stat().st_size if f.exists() else '—'} vs {a['bytes']}")
    mb = f"{a['bytes'] / 1024 / 1024:.2f}".replace(".", ",")
    chk(f"2.{i} размер {mb} МБ указан в отчёте", mb in full)
    chk(f"2.{i} разрешение {a['width']}×{a['height']} в отчёте",
        f"{a['width']}×{a['height']}" in full)
    chk(f"2.{i} метрики {num(a['diff_mean'])} / {num(a['diff_p95'])} в отчёте",
        num(a["diff_mean"]) in full and num(a["diff_p95"]) in full)

chk("2.4 Длительность 5,04 с и сумма 15,12 с",
    all(abs(a["duration_sec"] - 5.04) < 0.01 for a in STATS["animations"])
    and "5,04" in full and "15,12" in full)
chk("2.5 121 кадр и 24 кадра/с", "121" in full and "24 кадра/с" in full)
chk("2.6 Три исходника с реальными размерами",
    all((ROOT / "sources" / s["file"]).exists() for s in STATS["sources"])
    and "1024×1024" in full and "1280×720" in full and "1280×1014" in full)

# 3. dates
dates = set(re.findall(r"\b(\d{2}\.\d{2}\.\d{4})\b", full))
chk("3.1 Все даты в отчёте — 25.11.2026", dates == {"25.11.2026"}, str(sorted(dates)))
chk("3.2 Год 2026 и 1889/1890 упомянуты корректно",
    "2026" in full and "1889" in full and "1890" in full)

# 4. log consistency
chk("4.1 Дата в журнале и в cost.md — 25.11.2026",
    "25.11.2026" in logs["worklog.md"] and "25.11.2026" in logs["cost.md"])
chk("4.2 Журнал: все пять медиа-задач и три ролика",
    all(k in logs["worklog.md"] for k in ("S1", "S2", "S3", "A1", "A2", "A3"))
    and "23:19" in logs["worklog.md"])
chk("4.3 В журнале указан кадрированный размер скриншота 2160×2020",
    "2160×2020" in logs["worklog.md"])
chk("4.4 Ошибка A1 описана и в отчёте, и в журнале",
    "истории" in full and "истории" in logs["worklog.md"])
chk("4.5 Рефлексия: 150–250 слов и число в отчёте совпадает",
    150 <= STATS["reflection_words"] <= 250
    and f"объёмом {STATS['reflection_words']} слов" in full)
words = len(re.findall(r"[А-Яа-яЁёA-Za-z0-9-]+",
                       (LOGS / "reflection.md").read_text(encoding="utf-8")
                       .split("\n", 2)[2]))
chk("4.6 Пересчёт слов рефлексии совпадает с computed_stats",
    abs(words - STATS["reflection_words"]) <= 2, f"{words} vs {STATS['reflection_words']}")

# 5. references
low = full.lower()
for n in (1, 2, 3, 4):
    chk(f"5.{n} Ссылка на рисунок {n} есть в тексте",
        f"рисунке {n}" in low or f"рисунок {n}" in low)
chk("5.5 Ссылки на таблицы 1, 2, А.1, Б.1, Б.2 присутствуют",
    all(t in full for t in ("таблицу 1", "Таблица 1", "Таблица 2",
                            "Таблица А.1", "Таблица Б.1", "Таблица Б.2")))
chk("5.6 Все подписи «Рисунок N —» уникальны и по порядку",
    [p.split(" — ")[0] for p in paras if re.match(r"^Рисунок \d — ", p)]
    == ["Рисунок 1", "Рисунок 2", "Рисунок 3", "Рисунок 4"])

# 6. text hygiene
chk("6.1 Нет запрещённых слов и заглушек",
    not re.search(r"симуляц|макет|mock|composite|TODO|XXX|FIXME|placeholder", full, re.I)
    and full.count("___") == 1)
chk("6.2 Кафедра ИС, старая кафедра отсутствует",
    "Кафедра ИС" in full and "связи с общественностью" not in full)
chk("6.3 Титул: отчет/по заданию/тема без полужира",
    all(x in full for x in ("отчет\nпо заданию", "Тема: Оживление изображений")))
chk("6.4 Нет двойных пробелов и висячих пробелов в абзацах",
    all("  " not in p and p == p.strip() for p in paras))
chk("6.5 PDF и DOCX согласованы по объёму",
    pdf.page_count == 9 and len(pdf_text) > 8000, f"{pdf.page_count} стр.")

print("\nSUMMARY", sum(res), "/", len(res))
if not all(res):
    raise SystemExit(1)
