"""Acceptance checks for Отчет_М3_Задание3 (docx + pdf)."""
import json
import pathlib
import re

import pymupdf
from docx import Document

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCX = ROOT / "report" / "Отчет_М3_Задание3.docx"
PDF = ROOT / "report" / "Отчет_М3_Задание3.pdf"
STATS = json.loads((ROOT / "logs" / "computed_stats.json").read_text(encoding="utf-8"))

d = Document(DOCX)
paras = [p.text for p in d.paragraphs]
cells = [c.text for t in d.tables for row in t.rows for c in row.cells]
full = "\n".join(paras + cells)
pdf = pymupdf.open(PDF)
pdf_text = "\n".join(p.get_text() for p in pdf)
res = []


def chk(name, ok, detail=""):
    res.append(ok)
    print(("PASS" if ok else "FAIL"), name, ("| " + detail) if detail else "")


# 1. title page
lines = [p for p in d.paragraphs[:14] if p.text.strip()]
theme = next(p for p in lines if p.text.startswith("Тема:"))
chk("1. Тема не полужирная и точно совпадает",
    theme.text == "Тема: Оживление изображений: три анимации — три эффекта"
    and all(r.bold is False for r in theme.runs), theme.text)
otchet = next(p for p in lines if p.text.strip() == "отчет")
chk("2. «отчет» строчными, не полужирный",
    otchet.text == "отчет" and all(r.bold is False for r in otchet.runs))
chk("3. «по заданию» полужирное",
    any(p.text == "по заданию" and all(r.bold for r in p.runs) for p in lines))
chk("4. Курс двумя строками, полужирный",
    any(p.text.startswith("по курсу «Применение") and all(r.bold for r in p.runs) for p in lines)
    and any(p.text == "в мультимедиа»" and all(r.bold for r in p.runs) for p in lines))
chk("5. «Кафедра ИС» полужирным, старой кафедры нет",
    any(p.text == "Кафедра ИС" and all(r.bold for r in p.runs) for p in lines)
    and "Кафедра связи с общественностью" not in full)
chk("6. ФИО и группа на титуле", "Ханна М. Н." in "\n".join(cells)
    and "Студент гр. 1378" in "\n".join(cells))
chk("7. Тема и кафедра видны на первой странице PDF",
    "Кафедра ИС" in pdf[0].get_text()
    and "Оживление изображений" in pdf[0].get_text())


# 2. pagination
def footer_text(page):
    h = page.rect.height
    return " ".join(b[4].strip() for b in page.get_text("blocks") if b[1] > h - 70).strip()


chk("8. Page 1 footer empty", footer_text(pdf[0]) == "", repr(footer_text(pdf[0])))
chk("9. Page 2 footer is 2", footer_text(pdf[1]) == "2", repr(footer_text(pdf[1])))
last = pdf.page_count - 1
chk("10. Last page footer matches number", footer_text(pdf[last]) == str(last + 1),
    repr(footer_text(pdf[last])))

# 3. structure
heads = [p.text for p in d.paragraphs if p.style.name.startswith("Heading")]
chk("11. Структура 1–6 + приложения",
    heads[:6] == ["1. Введение", "2. Исходные изображения", "3. Создание анимаций",
                  "4. Таблица настроек", "5. Рефлексия", "6. Результаты анимаций"]
    and heads[-2:] == ["Приложение А", "Приложение Б"], str(heads))
chk("12. Подразделы 6.1–6.3 на месте",
    all(h in heads for h in ("6.1. Портрет (минимальное движение)",
                             "6.2. Пейзаж (средняя интенсивность)",
                             "6.3. Свободный выбор (максимальные значения)")))

# 4. figures and table
caps = [p for p in paras if re.match(r"^Рисунок \d — ", p)]
chk("13. Четыре рисунка и четыре подписи",
    len(d.inline_shapes) == 4 and len(caps) == 4, str([c[:50] for c in caps]))
chk("14. Подписи честные: визуализация/снимок",
    sum("Визуализация данных" in c for c in caps) == 3
    and "снимок 25.11.2026" in caps[1], str(caps))
chk("15. Каждый рисунок на одной странице с подписью",
    all(any(f"Рисунок {n} —" in pdf[i].get_text() and pdf[i].get_images()
            for i in range(pdf.page_count)) for n in (1, 2, 3, 4)))
chk("16. Таблица 1: 7 столбцов × 3 строки данных + шапка",
    len(d.tables[1].columns) == 7 and len(d.tables[1].rows) == 4)
hdr = [c.text for c in d.tables[1].rows[0].cells]
chk("17. Все 7 заголовков совпадают с заданием",
    hdr == ["Работа", "Сервис", "Скорость анимации", "Плавность переходов",
            "Глубина эффекта", "Что именно двигалось", "Что пошло не так"], str(hdr))
data_rows = d.tables[1].rows[1:]
chk("18. Все ячейки заполнены, «что пошло не так» не пустое",
    all(c.text.strip() for r in data_rows for c in r.cells)
    and all(len(r.cells[6].text.strip()) > 30 for r in data_rows))
chk("19. Во всех строках указан точный ID модели",
    all("bytedance/seedance-2-mini" in r.cells[1].text for r in data_rows))

# 5. numbers and reflection
chk("20. Рефлексия 150–250 слов",
    150 <= STATS["reflection_words"] <= 250, str(STATS["reflection_words"]))
chk("21. Сумма стоимостей = 41,275 и совпадает с текстом",
    abs(sum(s["cost_rub"] for s in STATS["sources"])
        + sum(a["cost_rub"] for a in STATS["animations"]) - 41.275) < 1e-9
    and "41,275" in full and "41,28" in full)
chk("22. Длительности: 5,04 с × 3 = 15,12 с",
    all(abs(a["duration_sec"] - 5.04) < 0.01 for a in STATS["animations"])
    and "15,12" in full and full.count("5,04") >= 3)
chk("23. Числа из метрик совпадают с логами",
    all(f"{a['diff_mean']:.3f}".replace(".", ",") in full for a in STATS["animations"]))
chk("24. Нет запрещённых формулировок",
    not re.search(r"симуляц|макет|mock|composite", full, re.IGNORECASE))
chk("25. Нет заглушек (кроме ___ на титуле)",
    not any(t in full for t in ("TODO", "XXX", "FIXME", "placeholder", "【"))
    and full.count("___") == 1)
chk("26. Нет квадратных и угловых скобок",
    "[" not in full and "<" not in full)
chk("27. Times New Roman во всём тексте",
    {r.font.name for p in d.paragraphs for r in p.runs if r.text.strip()}
    <= {"Times New Roman"})
chk("28. A4 и поля 2 см",
    abs(d.sections[1].page_width.cm - 21) < 0.01
    and abs(d.sections[1].left_margin.cm - 2) < 0.01)

# 6. files
need = [
    "sources/source_01_portrait.png", "sources/source_02_landscape.png",
    "sources/source_03_painting.jpg",
    "animations/animation_01_portrait.mp4", "animations/animation_02_landscape.mp4",
    "animations/animation_03_painting.mp4",
    "screenshots/01_sources_overview.png", "screenshots/02_settings_table.png",
    "screenshots/03_interface_settings.png", "screenshots/04_frames_montage.png",
]
chk("29. Все исходники, ролики и визуализации на месте",
    all((ROOT / p).exists() and (ROOT / p).stat().st_size > 50_000 for p in need),
    str([p for p in need if not (ROOT / p).exists()]))
chk("30. Объём PDF 8–16 страниц", 8 <= pdf.page_count <= 16, f"{pdf.page_count} стр.")

print("\nSUMMARY", sum(res), "/", len(res))
if not all(res):
    raise SystemExit(1)
