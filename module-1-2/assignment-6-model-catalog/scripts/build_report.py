"""Build Отчет_Задание6.docx (Russian, LETI title page, A4, TNR 14)."""
import json
import pathlib

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, RGBColor

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "report"
SHOTS = ROOT / "screenshots"
LOGS = ROOT / "logs"
META = LOGS / "model_metadata"
DEMO = LOGS / "demo_results"
DOCX = REPORT / "Отчет_Задание6.docx"

TNR = "Times New Roman"

TBLPR_ORDER = [
    "tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
    "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd",
    "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook",
    "tblCaption", "tblDescription",
]


def put_tblpr(tblPr, el):
    tag = el.tag.split("}")[1]
    idx = TBLPR_ORDER.index(tag)
    for child in list(tblPr):
        ctag = child.tag.split("}")[1]
        if ctag in TBLPR_ORDER and TBLPR_ORDER.index(ctag) > idx:
            child.addprevious(el)
            return
    tblPr.append(el)


def _rfonts(run):
    if hasattr(run, "_element"):
        rPr = run._element.get_or_add_rPr()
    else:
        rPr = run
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rFonts.set(qn(attr), TNR)


def fmt_run(run, size=14, bold=False, italic=False, color="000000"):
    run.font.name = TNR
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)
    _rfonts(run)
    rPr = run._element.get_or_add_rPr()
    szCs = rPr.find(qn("w:szCs"))
    if szCs is None:
        szCs = OxmlElement("w:szCs")
        rPr.append(szCs)
    szCs.set(qn("w:val"), str(int(size * 2)))
    return run


def set_par(p, align=WD_ALIGN_PARAGRAPH.LEFT, before=0, after=0, indent=0,
            line=1.0, keep_next=False):
    pf = p.paragraph_format
    pf.alignment = align
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.first_line_indent = Cm(indent)
    pf.line_spacing = line
    pf.keep_with_next = keep_next
    return p


def add_par(text="", size=14, bold=False, italic=False,
            align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=0, after=3, indent=1.25,
            line=1.0, color="000000"):
    p = doc.add_paragraph()
    set_par(p, align, before, after, indent, line)
    r = p.add_run(text)
    fmt_run(r, size, bold, italic, color)
    return p


def add_h1(text, page_break=False):
    p = doc.add_paragraph(style="Heading 1")
    set_par(p, WD_ALIGN_PARAGRAPH.CENTER, 12, 8, 0, 1.0, keep_next=True)
    if page_break:
        p.paragraph_format.page_break_before = True
    r = p.add_run(text)
    fmt_run(r, 14, bold=True, color="000000")
    return p


def add_h2(text):
    p = doc.add_paragraph(style="Heading 2")
    set_par(p, WD_ALIGN_PARAGRAPH.LEFT, 10, 4, 0, 1.0, keep_next=True)
    r = p.add_run(text)
    fmt_run(r, 14, bold=True, color="000000")
    return p


def add_caption(text, size=12, keep_next=False, before=6):
    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.CENTER, before, 12, 0, 1.0, keep_next=keep_next)
    r = p.add_run(text)
    fmt_run(r, size, bold=False, italic=True)
    return p


def add_bullet(text, marker="—"):
    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.JUSTIFY, 0, 4, 1.25, 1.0)
    p.paragraph_format.left_indent = Cm(1.25)
    p.paragraph_format.first_line_indent = Cm(-0.5)
    r = p.add_run(f"{marker} {text}")
    fmt_run(r, 14)
    return p


def add_picture(path, width_cm=14):
    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.CENTER, 6, 0, 0, 1.0, keep_next=True)
    p.add_run().add_picture(str(path), width=Cm(width_cm))
    return p


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def table_borders(table, sz=4, color="000000"):
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    for old in tblPr.findall(qn("w:tblBorders")):
        tblPr.remove(old)
    put_tblpr(tblPr, borders)


def cell_text(cell, text, bold=False, size=12, align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = cell.paragraphs[0]
    set_par(p, align, 0, 0, 0, 1.0)
    r = p.add_run(text)
    fmt_run(r, size, bold=bold)


def add_table(headers, rows, widths_cm, size=12, header_size=None,
              align_center_cols=()):
    header_size = header_size or size
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.allow_autofit = False
    table_borders(table)
    tblPr = table._tbl.tblPr
    for tag in ("w:tblLayout", "w:tblW"):
        for old in tblPr.findall(qn(tag)):
            tblPr.remove(old)
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    put_tblpr(tblPr, layout)
    tblW = OxmlElement("w:tblW")
    tblW.set(qn("w:w"), str(int(sum(widths_cm) * 566.929)))
    tblW.set(qn("w:type"), "dxa")
    put_tblpr(tblPr, tblW)

    for old in tblPr.findall(qn("w:tblCellMar")):
        tblPr.remove(old)
    cellmar = OxmlElement("w:tblCellMar")
    for side, val in (("top", 30), ("bottom", 30), ("left", 40), ("right", 40)):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        cellmar.append(el)
    put_tblpr(tblPr, cellmar)

    for i, w in enumerate(widths_cm):
        table.columns[i].width = Cm(w)
    hdr = table.rows[0]
    trPr = hdr._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    trPr.append(th)
    for i, h in enumerate(headers):
        c = hdr.cells[i]
        c.width = Cm(widths_cm[i])
        shade(c, "F2F2F2")
        cell_text(c, h, bold=True, size=header_size, align=WD_ALIGN_PARAGRAPH.CENTER)
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].width = Cm(widths_cm[i])
            al = (WD_ALIGN_PARAGRAPH.CENTER if i in align_center_cols
                  else WD_ALIGN_PARAGRAPH.LEFT)
            cell_text(cells[i], str(val), bold=False, size=size, align=al)
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit")
        trPr.append(cs)
    return table


def add_page_field(paragraph):
    run = paragraph.add_run()
    fld1 = OxmlElement("w:fldChar")
    fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld2 = OxmlElement("w:fldChar")
    fld2.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t")
    t.text = "2"
    fld3 = OxmlElement("w:fldChar")
    fld3.set(qn("w:fldCharType"), "end")
    run._r.append(fld1)
    run._r.append(instr)
    run._r.append(fld2)
    run._r.append(t)
    run._r.append(fld3)
    fmt_run(run, 12)


# ---------------------------------------------------------------- document

doc = Document()

normal = doc.styles["Normal"]
normal.font.name = TNR
normal.font.size = Pt(14)
normal.paragraph_format.space_after = Pt(0)
normal.paragraph_format.line_spacing = 1.0
_rfonts(normal.element.get_or_add_rPr())
szcs = normal.element.get_or_add_rPr().find(qn("w:szCs"))
if szcs is None:
    szcs = OxmlElement("w:szCs")
    normal.element.get_or_add_rPr().append(szcs)
szcs.set(qn("w:val"), "28")

for name in ("Heading 1", "Heading 2"):
    st = doc.styles[name]
    st.font.name = TNR
    st.font.size = Pt(14)
    st.font.bold = True
    st.font.color.rgb = RGBColor(0, 0, 0)
    _rfonts(st.element.get_or_add_rPr())

sec1 = doc.sections[0]
sec1.page_width = Mm(210)
sec1.page_height = Mm(297)
for m in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
    setattr(sec1, m, Cm(2))

# ---------------------------------------------------------------- title page


def tpar(text="", bold=False, align=WD_ALIGN_PARAGRAPH.CENTER, exact_pt=None):
    p = doc.add_paragraph()
    set_par(p, align, 0, 0, 0, 1.0)
    if exact_pt:
        p.paragraph_format.line_spacing = Pt(exact_pt)
    r = p.add_run(text)
    fmt_run(r, 14, bold=bold, italic=False)
    return p


tpar("МИНОБРНАУКИ РОССИИ", bold=True)
tpar("Санкт-Петербургский государственный электротехнический", bold=True)
tpar("университет «ЛЭТИ» им. В.И. Ульянова (Ленина)", bold=True)
tpar("Кафедра ИС", bold=True)
for _ in range(3):
    tpar(exact_pt=30)
tpar("отчет", bold=False)
tpar("по заданию", bold=True)
tpar("по курсу «Применение генеративных нейронных моделей", bold=True)
tpar("в мультимедиа»", bold=True)
tpar("Тема: Каталог моделей машинного обучения", bold=False)
for _ in range(4):
    tpar(exact_pt=40)
tpar(exact_pt=22)

tbl = doc.add_table(rows=2, cols=3)
tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl.autofit = False
tbl.allow_autofit = False
tblPr = tbl._tbl.tblPr
for tag in ("w:tblBorders", "w:tblLayout", "w:tblW"):
    for old in tblPr.findall(qn(tag)):
        tblPr.remove(old)
borders = OxmlElement("w:tblBorders")
for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
    el = OxmlElement(f"w:{edge}")
    el.set(qn("w:val"), "none")
    el.set(qn("w:sz"), "0")
    el.set(qn("w:space"), "0")
    el.set(qn("w:color"), "auto")
    borders.append(el)
put_tblpr(tblPr, borders)
mar = OxmlElement("w:tblCellMar")
for side, val in (("top", 20), ("bottom", 20), ("left", 70), ("right", 70)):
    el = OxmlElement(f"w:{side}")
    el.set(qn("w:w"), str(val))
    el.set(qn("w:type"), "dxa")
    mar.append(el)
put_tblpr(tblPr, mar)
layout = OxmlElement("w:tblLayout")
layout.set(qn("w:type"), "fixed")
put_tblpr(tblPr, layout)
tblW = OxmlElement("w:tblW")
tblW.set(qn("w:w"), "9297")
tblW.set(qn("w:type"), "dxa")
put_tblpr(tblPr, tblW)
widths = [2948, 340, 6009]
for i, w in enumerate(widths):
    tbl.columns[i].width = Cm(w / 566.929)
    for row in tbl.rows:
        row.cells[i].width = Cm(w / 566.929)
grid = tbl._tbl.tblGrid
for gc, w in zip(grid.gridCol_lst, widths):
    gc.set(qn("w:w"), str(w))

rows_data = [
    ("Студент гр. 1378", "", "Ханна М. Н."),
    ("", "", ""),
]
for ri, row_data in enumerate(rows_data):
    for ci, text in enumerate(row_data):
        cell = tbl.cell(ri, ci)
        p = cell.paragraphs[0]
        set_par(p, WD_ALIGN_PARAGRAPH.LEFT, 0, 0, 0, 1.0)
        r = p.add_run(text)
        fmt_run(r, 14, bold=False)

for _ in range(4):
    tpar(exact_pt=54)
tpar("Санкт-Петербург")
tpar("2026")

# ---------------------------------------------------------------- body section
sec2 = doc.add_section(WD_SECTION.NEW_PAGE)
sec2.page_width = Mm(210)
sec2.page_height = Mm(297)
for m in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
    setattr(sec2, m, Cm(2))
sec2.footer.is_linked_to_previous = False
fp = sec2.footer.paragraphs[0]
set_par(fp, WD_ALIGN_PARAGRAPH.CENTER, 0, 0, 0, 1.0)
add_page_field(fp)

settings = doc.settings.element
uf = OxmlElement("w:updateFields")
uf.set(qn("w:val"), "true")
settings.append(uf)

# ---------------------------------------------------------------- data

MODELS = {m: json.loads((META / f"{m}_parsed.json").read_text(encoding="utf-8"))
          for m in ("M1", "M2", "M3", "M4", "M5", "M6")}
D1 = json.loads((DEMO / "D1.json").read_text(encoding="utf-8"))
D2 = json.loads((DEMO / "D2.json").read_text(encoding="utf-8"))
CATALOG = json.loads((META / "_catalog.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- 1. intro

add_h1("1. Введение")
add_par(
    "Цель работы — разобраться в открытом каталоге моделей Hugging Face и "
    "научиться выбирать инструмент под конкретную задачу. Каталог устроен как "
    "большая библиотека: тысячи моделей отсортированы по задачам (pipeline tag), "
    "и первое, что должен сделать специалист, — сузить поиск фильтром, а затем "
    "сравнить несколько карточек по данным обучения, размеру и лицензии. В работе "
    "рассматриваются три направления из лекции 2.5 — компьютерное зрение, "
    "генерация контента и анализ данных; в каждом выбраны две модели с разной "
    "узкой специализацией, всего шесть. Две модели проверены на собственных "
    "примерах. Отдельная задача — понять, что «модель вообще» не существует: "
    "каждый инструмент заточен под свой тип входа, свой домен и свои ограничения. "
    "Для специалиста по связям с общественностью это практический навык: от "
    "выбора модели зависит, какие данные можно анализировать и что можно "
    "показывать заказчику."
)

# ---------------------------------------------------------------- 2. filter

add_h1("2. Страница фильтра по задачам")
add_par(
    "Каталог Hugging Face открывается по адресу huggingface.co/models. Слева "
    "расположен фильтр Pipeline tag — это и есть фильтр по задачам: он оставляет "
    "в выдаче только модели, решающие выбранный тип задачи. Дополнительно можно "
    "фильтровать по библиотеке, языку, лицензии и датасету, но для этой работы "
    "достаточно фильтра по задаче."
)
add_par(
    "На рисунке 1 показаны теги по трём направлениям и отмечены те, по которым "
    "отобраны модели; счётчики получены через API каталога."
)
add_picture(SHOTS / "01_task_filter.png", width_cm=16.2)
add_caption("Рисунок 1 — Страница фильтра по задачам в каталоге Hugging Face")
add_par(
    "Модели отбирались последовательно. Сначала по каждому направлению "
    "определялись две разные специализации: в компьютерном зрении — детекция "
    "объектов и распознавание эмоций, в генерации контента — музыка и код, в "
    "анализе данных — тональность и медицинский NER. Затем по каждой "
    "специализации открывался соответствующий тег (object-detection, "
    "image-classification, text-to-audio, text-generation, text-classification, "
    "token-classification), просматривалась выдача и выбиралась модель с "
    "заполненной карточкой, понятной лицензией и разумным размером."
)
add_par(
    "Числа в счётчиках — не реклама, а результат запроса "
    "/api/models?filter=<tag>&limit=1000: для популярных задач API возвращает "
    "ровно лимит выборки, поэтому указано «> 1 000», а для тега face-recognition "
    "получено точное значение 98. Это показывает важную особенность каталога: "
    "популярные задачи переполнены моделями, и фильтр по задаче — только первый "
    "шаг, после которого всё равно нужно читать карточки."
)

# ---------------------------------------------------------------- 3. table

add_h1("3. Таблица шести моделей")
add_par(
    "В таблице 1 сведены все шесть моделей. Данные взяты из карточек и метаданных "
    "Hugging Face API; полные формулировки приведены в приложении А, а визуальные "
    "карточки — в разделе 4."
)
add_caption("Таблица 1 — Шесть моделей каталога по трём направлениям", keep_next=True)
add_table(
    ["Направление", "Специализация", "Модель", "Вход", "Выход",
     "Данные обучения", "Размер", "Лицензия"],
    [
        ["Компьютерное зрение", "Детекция объектов", "facebook/detr-resnet-50",
         "Изображение RGB", "91 класс COCO, box + score",
         "COCO 2017, 118 тыс. изобр.", "41,6 млн", "Apache 2.0"],
        ["Компьютерное зрение", "Распознавание эмоций",
         "dima806/facial_emotions_image_detection",
         "Изображение лица", "7 эмоций + вероятность",
         "25,2 тыс. изобр., 7 классов", "85,8 млн", "Apache 2.0"],
        ["Генерация контента", "Генерация музыки", "facebook/musicgen-small",
         "Текстовый промпт", "Аудио 32 кГц",
         "20 тыс. ч лицензированной музыки", "591,1 млн", "CC-BY-NC 4.0"],
        ["Генерация контента", "Генерация кода",
         "Salesforce/codegen-350M-mono", "Комментарий на английском",
         "Код на Python", "BigPython, 71,7 млрд токенов", "350 млн",
         "BSD-3-Clause"],
        ["Анализ данных", "Анализ тональности",
         "cardiffnlp/twitter-roberta-base-sentiment",
         "Текст на английском", "3 класса тональности",
         "58 млн твитов + TweetEval", "≈125 млн", "не указана"],
        ["Анализ данных", "Медицинский NER", "d4data/biomedical-ner-all",
         "Клинический текст", "107 типов сущностей",
         "MACCROBAT2018", "66,4 млн", "Apache 2.0"],
    ],
    widths_cm=[2.45, 2.5, 3.05, 1.85, 2.05, 2.05, 1.35, 1.7],
    size=9, header_size=9,
)
add_par(
    "Три наблюдения по таблице. Во-первых, размеры различаются на порядки: от "
    "41,6 млн параметров у DETR до 591,1 млн у MusicGen — и это напрямую "
    "определяет требования к железу. Во-вторых, лицензии разные: Apache 2.0 и "
    "BSD-3-Clause допускают коммерческое использование, CC-BY-NC 4.0 — нет, а у "
    "sentiment-модели лицензия вообще не указана. В-третьих, у моделей одного "
    "направления разная природа входа: изображение, текст, аудио, что и делает "
    "их взаимодополняющими."
)

# ---------------------------------------------------------------- 4. cards

add_h1("4. Карточки моделей")
add_par(
    "В этом разделе для каждой модели приведены идентификатор, краткое описание "
    "и композит карточки с основными полями. Композиты собраны из реальных "
    "метаданных Hugging Face API и текста README; поля «Загрузок» и «Лайков» "
    "зафиксированы на момент сбора данных. Ограничения, перечисленные в карточке, "
    "вынесены в отдельную строку и не смешиваются с нашими выводами."
)


def model_section(num, mid, desc, limit_note=None):
    rec = MODELS[mid]
    add_h2(f"4.{num}. {rec['id']}")
    add_par(
        f"Идентификатор: {rec['id']}. URL: {rec['url']}. Направление — "
        f"{rec['direction'].lower()}, специализация — {rec['specialization'].lower()}.",
        align=WD_ALIGN_PARAGRAPH.LEFT, after=4,
    )
    add_par(desc)
    add_picture(SHOTS / f"{num + 1:02d}_card_{mid}.png", width_cm=15.9)
    add_caption(f"Рисунок {num + 1} — Карточка модели: {rec['id']}")
    if limit_note:
        add_par(limit_note, after=6)


model_section(
    1, "M1",
    "DETR — детектор объектов на основе трансформера: сверточный backbone "
    "ResNet-50 сжимает изображение, а энкодер-декодер с 100 object queries "
    "предсказывает классы и рамки без постобработки вроде NMS. Модель обучена "
    "end-to-end на COCO 2017 (118 тыс. изображений, 91 категория) и достигает "
    "AP 42,0 на валидации. Карточка прямо ограничивает применение: поддерживается "
    "только PyTorch, а качество за пределами классов COCO не гарантируется.",
    "Для нашей задачи это означает: модель уверенно находит людей, машины и "
    "велосипеды, но не отличит логотип компании от другого логотипа — такого "
    "класса в COCO нет.",
)
model_section(
    2, "M2",
    "Компактный ViT-классификатор эмоций: базовая модель "
    "google/vit-base-patch16-224-in21k дообучена на изображениях лиц. В карточке "
    "приведён classification report на 25 170 изображениях: accuracy 0,9092, "
    "лучше всего распознаются disgust (F1 0,9954) и surprise (0,9463), хуже "
    "всего — sad (0,8511). Выход — один из семи классов: angry, disgust, fear, "
    "happy, neutral, sad, surprise.",
    "Карточка не описывает набор данных и ограничения, поэтому к переносу на "
    "другие домены (другое освещение, возраст, культурный контекст) следует "
    "относиться осторожно: метрики получены на одном наборе изображений.",
)
model_section(
    3, "M3",
    "MusicGen Small — авторегрессионная модель генерации музыки по текстовому "
    "описанию. Она работает поверх 32 кГц EnCodec-токенизатора с четырьмя "
    "кодовыми книгами и генерирует все книги за один проход, что даёт 50 "
    "авторегрессионных шагов на секунду аудио. Обучение — 20 тыс. часов "
    "лицензированной музыки из коллекций Meta Music Initiative, Shutterstock и "
    "Pond5. В карточке чекпоинт назван «Small 300M», но в файлах весов 591,1 млн "
    "параметров: 300 млн относится к языковой модели, остальное — аудиокодек.",
    "Ключевое ограничение — лицензия CC-BY-NC 4.0: коммерческое использование "
    "запрещено. Карточка также предупреждает о возможной нехватке культурного "
    "разнообразия и о том, что модель исследовательская.",
)
model_section(
    4, "M4",
    "CodeGen-350M-Mono — авторегрессионная модель синтеза программ. Она "
    "инициализирована из CodeGen-Multi 350M и дообучена на BigPython: 71,7 млрд "
    "токенов кода на Python. Вход — комментарий или начало функции на английском, "
    "выход — продолжение кода. Пример из карточки: по строке «def hello_world():» "
    "модель продолжает функцию.",
    "Карточка называет релиз исследовательским: модель не предназначена для "
    "промышленного применения без проверки, а сгенерированный код нужно "
    "тестировать — он может быть синтаксически верным и логически неверным.",
)
model_section(
    5, "M5",
    "Twitter-roBERTa-base — roberta-base, предобученная на ~58 млн твитов и "
    "дообученная на бенчмарке TweetEval для анализа тональности. Выход — три "
    "класса: negative (LABEL_0), neutral (LABEL_1), positive (LABEL_2). Модель "
    "лёгкая (около 125 млн параметров) и рассчитана на короткие сообщения, то "
    "есть именно на тот формат, который преобладает в соцсетях.",
    "В карточке не указана лицензия — это единственная модель из шести без "
    "явного разрешения на использование. Также заявлен только английский язык; "
    "для русского текста нужна другая модель.",
)
model_section(
    6, "M6",
    "Biomedical NER — DistilBERT, дообученный на корпусе MACCROBAT2018 для "
    "извлечения биомедицинских сущностей. Модель размечает 107 типов сущностей "
    "(болезни, лекарства, анатомические области и др.) в клинических описаниях "
    "случаев. Размер — 66,4 млн параметров, лицензия Apache 2.0, обучение заняло "
    "около 30 минут на одной RTX 3060 Laptop.",
    "Ограничения: только английский язык и один корпус клинических текстов; "
    "модель не является медицинским изделием, и её выводы нельзя использовать "
    "для постановки диагноза.",
)

# ---------------------------------------------------------------- 5. tree

add_h1("5. Дерево специализаций")
add_par(
    "Дерево на рисунке 8 повторяет структуру лекции 2.5: от общего понятия "
    "«AI-модели» через три направления к узким специализациям и конкретным "
    "моделям каталога. Важно, что специализация находится на среднем уровне: "
    "«компьютерное зрение» — ещё не задача, а «детекция объектов» и "
    "«распознавание эмоций» — уже разные задачи с разными входами и метриками. "
    "Именно на этом уровне и происходит выбор инструмента."
)
add_picture(SHOTS / "10_tree_diagram.png", width_cm=16.9)
add_caption("Рисунок 8 — Дерево специализаций AI-моделей с размещением "
            "найденных моделей")
add_par(
    "Дерево показывает и обратное движение: если в проекте нужна, например, "
    "оценка реакции аудитории на рекламный ролик, то сначала определяется "
    "направление (компьютерное зрение), затем специализация (распознавание "
    "эмоций), и только потом открывается карточка конкретной модели. Такой "
    "порядок экономит время: он не даёт сравнивать модели из разных задач по "
    "одной метрике."
)

# ---------------------------------------------------------------- 6. demos

add_h1("6. Демонстрации моделей")
add_par(
    "Обе демонстрации выполнены на настоящих входных данных, но не через "
    "онлайн-виджет. Причина техническая: Inference API Hugging Face без токена "
    "отвечает HTTP 401, а виджет на странице модели просит войти в аккаунт. "
    "Поэтому те же чекпоинты запущены локально через transformers на CPU; "
    "подмены модели или выдуманных ответов нет — все числа ниже взяты из "
    "сохранённых JSON-файлов."
)

add_h2("6.1. Демо: детекция объектов (facebook/detr-resnet-50)")
add_par(
    "Вход — реальное фото улицы Амстердама: велосипедисты, грузовой велосипед с "
    "детьми, пешеходы, автомобили и дома (Wikimedia Commons, CC0, 960×721 px). "
    "При первом запуске загрузка весов заняла 54,4 с, повторный запуск из "
    "локального кэша — 1,2 с, инференс — 0,8 с. При пороге 0,50 получено "
    "60 обнаружений, при 0,90 — 28; на рисунке 9 показаны только уверенные "
    "обнаружения."
)
add_picture(SHOTS / "08_demo_M1.png", width_cm=16.6)
add_caption("Рисунок 9 — Демо: детекция объектов на тестовом изображении")
add_par(
    "Модель справилась: найдены все ключевые объекты сцены — person (1,00), car "
    "(1,00), bicycle (1,00), handbag (0,97), traffic light (0,84), backpack "
    "(0,82). Ошибок класса не видно: велосипеды не названы машинами, люди не "
    "названы рюкзаками. Главная проблема — не точность, а избыточность: дальние "
    "машины дают по две-три пересекающиеся рамки, и без дополнительной "
    "фильтрации считать объекты автоматически нельзя."
)
add_par(
    "Ограничения применения: только 91 категория COCO (логотипов и товаров там "
    "нет), мелкие объекты на границе кадра, отсутствие NMS в исходном выводе и "
    "скорость — 0,8 с на изображение на CPU, для видеопотока этого мало. Это "
    "типичные «краевые случаи» из лекции 2.4: сцена обычная, но именно дальние "
    "и частично перекрытые объекты ломают аккуратный подсчёт."
)

add_h2("6.2. Демо: анализ тональности "
       "(cardiffnlp/twitter-roberta-base-sentiment)")
add_par(
    "Вход — собственный английский текст: «I absolutely love the new AI course "
    "on prompt engineering — it's incredibly useful and well-structured!». "
    "Загрузка весов при первом запуске заняла 149,6 с (скачивание чекпоинта), "
    "инференс — 0,1 с. Ответ: positive "
    "99,17 %, neutral 0,68 %, negative 0,15 %."
)
add_picture(SHOTS / "09_demo_M5.png", width_cm=15.8)
add_caption("Рисунок 10 — Демо: анализ тональности тестового текста")
add_par(
    "Модель справилась ожидаемо уверенно: текст явно положительный, и "
    "вероятность positive близка к единице. Сумма вероятностей трёх классов "
    "равна 1,0000 — выход корректно нормирован. Ограничения: только английский "
    "язык; домен твитов, а не деловых или научных текстов; три класса без "
    "сарказма и смешанной тональности; отсутствие контекста диалога; "
    "неуказанная лицензия. Это иллюстрация «специфики задачи» из лекции 2.5: "
    "модель хороша ровно там, где её обучали."
)

# ---------------------------------------------------------------- 7. choice

add_h1("7. Выбор моделей для мультимедиа-проекта")
add_par(
    "Для собственного проекта выбраны две модели: facebook/detr-resnet-50 и "
    "cardiffnlp/twitter-roberta-base-sentiment. Проект — система мониторинга "
    "медиаконтента для PR-службы: сбор публикаций с упоминаниями организации, "
    "сортировка изображений по сюжетам и оценка тональности текстов, чтобы "
    "заранее видеть кризисные всплески."
)
add_par(
    "DETR закрывает входной анализ изображений: находит людей, транспорт и "
    "обстановку на фото из публикаций, помогает сортировать медиатеку и "
    "отбирать кадры для отчётов. Лицензия Apache 2.0 допускает коммерческое "
    "использование, а 41,6 млн параметров позволяют обойтись одним сервером "
    "без GPU-кластера."
)
add_par(
    "Sentiment-модель анализирует текстовые упоминания: считает долю негатива, "
    "показывает всплески и даёт время среагировать до выхода темы в медиа. Она "
    "лёгкая и обучена на коротких сообщениях — основном формате соцсетей."
)
add_par(
    "Вместе модели покрывают два главных типа контента в PR — изображения и "
    "текст: одна отвечает на вопрос «что на картинке», другая — «как об этом "
    "говорят». Это прямое применение принципа «специализация инструментов» "
    "(лекция 2.5): каждая модель делает одну задачу хорошо, а не заменяет весь "
    "конвейер. Ограничение — лицензия sentiment-модели не указана; перед "
    "коммерческим запуском её нужно заменить или согласовать с авторами."
)

# ---------------------------------------------------------------- appendix A

add_h1("Приложение А. Полные метаданные шести моделей", page_break=True)
add_par(
    "Значения приведены по состоянию на момент сбора данных "
    f"({CATALOG['fetched_at_utc']}); источник — Hugging Face API и README "
    "карточек. Если поле в карточке отсутствует, это указано явно."
)

for i, mid in enumerate(("M1", "M2", "M3", "M4", "M5", "M6"), start=1):
    rec = MODELS[mid]
    h = add_h2(f"А.{i}. {rec['id']}")
    if mid == "M6":
        h.paragraph_format.page_break_before = True
    add_caption(f"Таблица А.{i} — Метаданные модели {rec['id']}", size=12,
                keep_next=True, before=2)
    rows = [
        ("Направление", rec["direction"]),
        ("Специализация", rec["specialization"]),
        ("Задача (pipeline_tag)", f"{rec['task']}"),
        ("Тип входа", rec["input_type"]),
        ("Тип выхода", rec["output_type"]),
        ("Данные обучения", rec["training_data"]),
        ("Размер", rec["model_size"]),
        ("Лицензия", rec["license"]),
        ("Пример использования", rec["example_use"]),
        ("Ограничения", rec["limitations"]),
        ("Загрузок", f"{rec['downloads']:,}".replace(",", " ")),
        ("Лайков", f"{rec['likes']:,}".replace(",", " ")),
        ("Теги", f"pipeline_tag: {rec['pipeline_tag']}; library: "
                 f"{rec['library_name']}; model_type: {rec['model_type']}"),
        ("URL", rec["url"]),
    ]
    add_table(["Поле", "Значение"], rows, widths_cm=[4.0, 13.0], size=10,
              header_size=10)
    add_par("", after=2)

# ---------------------------------------------------------------- appendix B

add_h1("Приложение Б. Журнал работ", page_break=True)
add_par(
    "Инструменты: Python 3.13.17, Pillow 13.0.0, python-docx 1.2.0, requests "
    "2.34.2, PyMuPDF 1.28.5, transformers 5.22.1, torch 2.15.0 (CPU), timm "
    "1.0.31, LibreOffice (конвертация DOCX → PDF). Данные получены через "
    "публичный Hugging Face API; платные сервисы не использовались."
)
add_caption("Таблица Б.1 — Обращения к Hugging Face API", keep_next=True)
add_table(
    ["Запрос", "Количество", "Результат"],
    [
        ["GET /api/models/{id}", "6", "HTTP 200, метаданные шести моделей"],
        ["GET /{id}/raw/main/README.md", "6", "HTTP 200, тексты карточек"],
        ["GET /api/models?filter=<tag>&limit=1000", "12",
         "HTTP 200, счётчики по задачам"],
        ["POST router.huggingface.co/hf-inference/...", "2",
         "HTTP 401 — нужен токен"],
    ],
    widths_cm=[7.2, 2.6, 7.2], size=10, header_size=10,
    align_center_cols=(1,),
)
add_caption("Таблица Б.2 — Хронология выполнения работы", keep_next=True, before=8)
add_table(
    ["Время (MSK)", "Действие"],
    [
        ["17:12", "Создана структура проекта, проверены Python и библиотеки."],
        ["17:13", "Проверен доступ к Hugging Face API (HTTP 200)."],
        ["17:14", "Запрошены метаданные и README шести моделей."],
        ["17:15", "Собраны счётчики по 12 задачам каталога."],
        ["17:18", "Разобраны карточки, собраны M1–M6_parsed.json."],
        ["17:20", "Inference API вернул 401 без токена."],
        ["17:22", "Виджет онлайн-демо потребовал входа в аккаунт."],
        ["17:23", "Unsplash недоступен, взято CC0-фото Wikimedia Commons."],
        ["17:25", "Локальный запуск DETR: 54,4 с загрузка, 28 объектов при 0,90."],
        ["17:27", "Локальный запуск sentiment: positive 99,17 %."],
        ["17:29", "Собраны 10 композитов скриншотов."],
        ["17:31", "Написаны analysis.md и журнал работ."],
        ["17:35", "Собраны DOCX и PDF, выполнена самопроверка вёрстки."],
    ],
    widths_cm=[2.8, 14.2], size=10, header_size=10,
)
add_par(
    "Замен моделей не потребовалось: все шесть идентификаторов существуют и "
    "доступны. Расхождения с ожидаемыми атрибутами зафиксированы в отчёте по "
    "фактическим карточкам: у модели эмоций лицензия Apache 2.0 и семь классов "
    "вместо шести, у MusicGen в весах 591,1 млн параметров, у sentiment-модели "
    "лицензия не указана.",
    before=6,
)

doc.core_properties.title = "Отчет. Задание 6. Каталог моделей"
doc.core_properties.subject = ("Применение генеративных нейронных моделей "
                               "в мультимедиа, задание 6")
doc.core_properties.author = "Ханна М. Н."

REPORT.mkdir(parents=True, exist_ok=True)
doc.save(DOCX)
print("saved", DOCX)
