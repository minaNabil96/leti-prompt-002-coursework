"""Acceptance checks for Отчет_М3_Задание2."""
import pathlib
import re

import pymupdf
from docx import Document

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCX = ROOT / "report" / "Отчет_М3_Задание2.docx"
PDF = ROOT / "report" / "Отчет_М3_Задание2.pdf"

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
lines = [p for p in d.paragraphs[:12] if p.text.strip()]
theme = next(p for p in lines if p.text.startswith("Тема:"))
chk("1. Тема не полужирная и точно совпадает",
    theme.text == "Тема: Исследование сервиса синтеза голоса"
    and all(r.bold is False for r in theme.runs), theme.text)
otchet = next(p for p in lines if p.text.strip() == "отчет")
chk("2. «отчет» строчными, не полужирный",
    otchet.text == "отчет" and all(r.bold is False for r in otchet.runs))
chk("3. «по заданию» полужирное",
    any(p.text == "по заданию" and all(r.bold for r in p.runs) for p in lines))
chk("4. Курс двумя строками, полужирный",
    any(p.text.startswith("по курсу «Применение") and all(r.bold for r in p.runs) for p in lines)
    and any(p.text == "в мультимедиа»" and all(r.bold for r in p.runs) for p in lines))
chk("5. ФИО «Ханна М. Н.» на титуле", "Ханна М. Н." in "\n".join(cells))

# 2. pagination
def footer_text(page):
    h = page.rect.height
    return " ".join(b[4].strip() for b in page.get_text("blocks") if b[1] > h - 70).strip()


chk("6. Page 1 footer empty", footer_text(pdf[0]) == "", repr(footer_text(pdf[0])))
chk("7. Page 2 footer is 2", footer_text(pdf[1]) == "2", repr(footer_text(pdf[1])))
chk("7b. Page 11 footer is 11", footer_text(pdf[10]) == "11", repr(footer_text(pdf[10])))

# 3. structure and content
heads = [p.text for p in d.paragraphs if p.style.name.startswith("Heading")]
chk("8. Структура: 1, 2 (2.1–2.5), 3, приложения",
    [h for h in heads if h.startswith("2.")] == ["2. Заполненный шаблон", "2.1. Сервис",
     "2.2. Входные данные", "2.3. Управляемые параметры", "2.4. Языки и ограничения",
     "2.5. Применение в мультимедиа"], str(heads))
for sec in ("Server",):
    pass
chk("9. Поле 2.1 содержит тарифы и клонирование",
    "Instant Voice Cloning" in cells.__str__() and "Starter" in full)
chk("10. Поле 2.2 содержит минуты записи",
    "1 минута" in full and "30 минут" in full and "2–3 часа" in full)
chk("11. Поле 2.3 содержит параметры и диапазоны",
    all(s in full for s in ("Stability", "Similarity Boost", "Style Exaggeration",
                            "Speed", "Speaker Boost", "0,7–1,2")))
chk("12. Поле 2.4: русский язык и согласие",
    "29 языков" in full and "согласие" in full and "незаконно" in full)
chk("13. Поле 2.5: два сценария",
    full.count("Сценарий 1.") == 1 and full.count("Сценарий 2.") == 1)

# 4. figures
figs = [p for p in paras if p.startswith("Рисунок")]
caps = [p for p in paras if re.match(r"^Рисунок \d — ", p)]
chk("14. Три рисунка и три подписи",
    len(d.inline_shapes) == 3 and len(caps) == 3, str([c[:45] for c in caps]))
chk("15. Каждый рисунок на одной странице с подписью",
    all(any(f"Рисунок {n} —" in pdf[i].get_text() and pdf[i].get_images()
            for i in range(pdf.page_count)) for n in (1, 2, 3)))

# 5. hygiene
bad = {t: full.count(t) for t in ("TODO", "XXX", "FIXME", "placeholder", "【", "___", "451")}
chk("16. Нет служебных пометок и кода 451", all(v == 0 for v in bad.values()), str(bad))
chk("17. Нет пустых разделов", all(paras[i + 1].strip() for i, p in enumerate(paras)
                                   if p.startswith("2.") and p[2:3].isdigit()))
chk("18. Числа с неразрывными пробелами",
    "\u00a0000" in full and " 000" not in full.replace("\u00a0000", ""))
chk("19. Times New Roman во всём тексте",
    {r.font.name for p in d.paragraphs for r in p.runs if r.text.strip()} <= {"Times New Roman"})
chk("20. Размер страницы A4 и поля 2 см",
    abs(d.sections[1].page_width.cm - 21) < 0.01 and abs(d.sections[1].left_margin.cm - 2) < 0.01)
chk("21. Объём PDF 8–14 страниц", 8 <= pdf.page_count <= 14, f"{pdf.page_count} стр.")

print("\nSUMMARY", sum(res), "/", len(res))
