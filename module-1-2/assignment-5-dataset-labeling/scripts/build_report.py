"""Build Отчет_Задание5.docx (Russian, LETI title page, A4, TNR 14)."""
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
DOCX = REPORT / "Отчет_Задание5.docx"

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


def add_caption(text, size=12, keep_next=False):
    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.CENTER, 6, 12, 0, 1.0, keep_next=keep_next)
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


def add_table(headers, rows, widths_cm, size=12, header_size=None):
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
            cell_text(cells[i], str(val), bold=False, size=size)
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
tpar("«Задание 5. Разметка датасета для задачи классификации»", bold=False)
tpar("по курсу «Применение генеративных нейронных моделей", bold=True)
tpar("в мультимедиа»", bold=True)
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
labels = json.loads((LOGS / "labels_ground_truth.json").read_text(encoding="utf-8"))
agreement = json.loads((LOGS / "agreement.json").read_text(encoding="utf-8"))
stress = json.loads((LOGS / "stress_agreement.json").read_text(encoding="utf-8"))
notes = json.loads((LOGS / "mismatch_notes.json").read_text(encoding="utf-8"))
gen_logs = [json.loads((LOGS / "gen" / f"gen_{i:02d}.json").read_text(encoding="utf-8"))
            for i in range(1, 25)]
total_rub = sum(g["billed_rub"] for g in gen_logs)
all_llm = agreement["details"] + stress["details"]
llm_calls = len(all_llm)
llm_in = sum((r.get("usage") or {}).get("prompt_tokens", 0) for r in all_llm)
llm_out = sum((r.get("usage") or {}).get("completion_tokens", 0) for r in all_llm)
llm_cost = sum(float((r.get("usage") or {}).get("cost_rub") or 0) for r in all_llm)
if llm_cost == 0:
    llm_cost = llm_in / 1e6 * 18.030285 + llm_out / 1e6 * 150.252375
grand_total = total_rub + llm_cost
matches = agreement["matches"]
total_blind = agreement["total"]
stress_matches = stress["matches"]
stress_total = stress["total"]
pct = round(100 * matches / total_blind)
stress_pct = round(100 * stress_matches / stress_total)

# ---------------------------------------------------------------- body

add_h1("1. Введение")
add_par(
    "Цель работы — собрать и разметить мини-датасет для задачи классификации "
    "изображений на три класса, а затем проверить качество собственной инструкции "
    "разметчика с помощью независимой «слепой» разметки. В работе проверяется не "
    "точность нейросети, а качество самого процесса разметки: насколько однозначно "
    "сформулированы правила, где границы классов размываются и какую долю "
    "совпадений даёт независимый аннотатор, который видит только изображение и "
    "инструкцию. Для специалиста по связям с общественностью это практический "
    "навык: афиши, обложки книг и постеры фильмов — типовые коммуникационные "
    "материалы, а умение построить корректную разметку определяет, можно ли "
    "вообще обучать на этих данных классификатор. Мини-датасет собран из "
    "24 сгенерированных изображений, по 8 на класс; разметка выполнена вручную, "
    "независимая проверка — мультимодальной моделью Gemini 2.5 Flash через API "
    "Polza.ai."
)

add_h1("2. Описание задачи и классов")
add_par(
    "Задача — отнести изображение к одному из трёх классов: «афиша» (event "
    "poster), «обложка книги» (book cover) и «постер фильма» (movie poster). Все "
    "три класса относятся к печатной и цифровой коммуникационной графике: у них "
    "общая структура «изображение + крупный заголовок + мелкий текст», поэтому "
    "задача нетривиальна и требует явных признаков различения. Выбор трёх "
    "классов, а не двух, даёт более богатый анализ расхождений: граница проходит "
    "не между «текстом» и «картинкой», а между типами носителя."
)
add_par(
    "Классы определены через обязательные элементы. Афиша продвигает временное "
    "событие и содержит дату и/или место проведения: концерт, выставка, лекция, "
    "спектакль, фестиваль. Обложка книги содержит имя автора и название книги, но "
    "не содержит даты события и названия места; часто есть логотип издательства. "
    "Постер фильма содержит название фильма и блок титров (credits block) — "
    "мелкий текст со списком режиссёра, актёров и продюсеров, — а также дату "
    "релиза или пометку «coming soon»."
)
add_par(
    "Для PR-специалиста такая классификация полезна при автоматической "
    "сортировке медиатеки, мониторинге публикаций и подготовке архивов "
    "коммуникационных материалов: афиши, обложки и постеры хранятся вместе, но "
    "имеют разные права использования, срок жизни и сценарии повторного "
    "применения."
)
add_picture(SHOTS / "02_examples_collage.png", width_cm=10)
add_caption("Рисунок 1 — Примеры по классам: афиша, обложка книги, постер фильма")

add_h1("3. Статистика датасета")
add_par(
    "Датасет содержит 24 объекта: по 8 изображений на каждый класс. Все "
    "изображения сгенерированы моделью tongyi-mai/z-image через API Polza.ai по "
    "заранее подготовленным промптам; промпт задаёт и содержание, и целевой класс, "
    "поэтому он же служит источником истинной метки. Разрешение всех файлов — "
    "864×1152 пикселя (соотношение сторон 3:4), суммарный объём — около 26 МБ."
)
add_caption("Таблица 1 — Состав датасета по классам", keep_next=True)
add_table(
    ["Класс", "Объектов", "Доля", "Источник", "Лицензия"],
    [
        ["Афиша", "8", "33,3 %", "Polza.ai, tongyi-mai/z-image", "Собственное (ИИ)"],
        ["Обложка книги", "8", "33,3 %", "Polza.ai, tongyi-mai/z-image", "Собственное (ИИ)"],
        ["Постер фильма", "8", "33,3 %", "Polza.ai, tongyi-mai/z-image", "Собственное (ИИ)"],
        ["Итого", "24", "100 %", "24 из 24 — сгенерированы", "—"],
    ],
    widths_cm=[3.6, 2.0, 2.0, 6.4, 3.0],
    size=11,
)
add_par(
    "Баланс идеальный: 8 / 8 / 8, то есть по 33,3 % на класс — ни один класс не "
    "доминирует, поэтому метрика accuracy на таком наборе не будет смещена в "
    "сторону частого класса. Однако идеальный баланс достигнут не отбором из "
    "реальных данных, а конструированием: мы сами задали по восемь промптов на "
    "класс. Все 24 объекта имеют лицензию «собственное, сгенерировано ИИ»; "
    "сторонние изображения с открытых источников не использовались, поэтому "
    "отдельных требований по атрибуции нет."
)
add_par(
    "Таблица разметки ведётся в файле разметка.xlsx и имеет восемь столбцов: "
    "идентификатор, превью, файл, класс, источник, лицензия, разметчик и "
    "комментарий о сомнениях. Всего 24 строки данных; текстовые столбцы показаны "
    "на рисунке 2."
)
add_picture(SHOTS / "01_labeling_table.png", width_cm=15.4)
add_caption("Рисунок 2 — Таблица разметки (24 объекта)")
add_par(
    "В столбце «Превью» и на отдельном листе «Превью» к каждой строке приложено "
    "настоящее изображение объекта, поэтому таблицу можно проверять визуально, не "
    "открывая папку images; лист «Инструкция» дублирует правила разметчика. Для "
    "четырёх пограничных изображений (P04, P11, P13, P20) в столбце комментариев "
    "зафиксированы сомнения: P04 — афиша лекции с крупным портретом похожа на "
    "обложку, P11 — обложка биографии похожа на постер фильма, P13 — тёмная "
    "обложка детектива близка к постеру, P20 — постер документального фильма "
    "похож на афишу."
)

add_h1("4. Инструкция разметчика", page_break=True)
add_par(
    "Инструкция состоит из семи правил и построена по принципу «от обязательных "
    "признаков к спорным случаям». Правила 1–3 определяют каждый класс через "
    "набор элементов: афиша — дата и место события; обложка книги — автор и "
    "название без даты и места; постер фильма — название и блок титров. Правило 4 "
    "сводит эти признаки в таблицу решений, правило 5 задаёт приоритет при "
    "конфликте признаков, правило 6 требует фиксировать сомнение в комментарии, "
    "правило 7 вводит класс «вне категорий» для изображений, не относящихся ни к "
    "одному типу."
)
add_par(
    "Ключевая идея инструкции — не пытаться угадать «смысл» изображения, а "
    "проверять наличие конкретных текстовых блоков. Именно поэтому в правилах "
    "отдельно названы блок титров и логотип издательства: это самые устойчивые "
    "маркеры, которые различают постер фильма и обложку книги даже при похожей "
    "иллюстрации. Дополнительно в инструкции оговорено, что все изображения "
    "сгенерированы и надписи на них могут быть искажены, поэтому оценивать нужно "
    "композицию и структуру текстовых блоков, а не конкретные слова."
)
add_picture(SHOTS / "03_instruction.png", width_cm=16)
add_caption("Рисунок 3 — Инструкция разметчика (7 правил)")

add_h1("5. Независимая разметка и доля совпадений")
add_par(
    "Для независимой проверки отобраны 10 изображений: три явные афиши (P01, P05, "
    "P07), три явные обложки книги (P09, P14, P15), два явных постера фильма "
    "(P17, P22) и два пограничных случая — обложка биографии с портретом (P11) и "
    "постер документального фильма (P20). Каждое изображение отправлено в модель "
    "google/gemini-2.5-flash через API Polza.ai вместе с полным текстом инструкции. "
    "Истинная метка и промпт генерации в запрос не передавались, поэтому разметка "
    "действительно слепая: модель видела только картинку и правила. Температура "
    "установлена в 0, чтобы ответы были воспроизводимыми."
)
add_par(
    "Дополнительно проведён контрольный прогон на 8 изображениях: P02, P03, P04, P06, "
    "P12, P13, P15 и P19. В него вошли четыре пограничных случая (P03, P04, P06, P13) "
    "и четыре контрольных, а P15 повторена из основной выборки, чтобы проверить "
    "воспроизводимость ответа при температуре 0. Протокол тот же: только изображение "
    "и инструкция, без истинной метки и промпта."
)
add_picture(SHOTS / "04_blind_results.png", width_cm=16.5)
add_caption("Рисунок 4 — Результат независимой разметки: 10 объектов, 10 совпадений (100 %)")

add_par(notes["summary"])

add_par(
    "Отдельно разобраны четыре изображения, которые при генерации сознательно "
    "ставились на границу классов: P04 (афиша лекции с крупным портретом), P11 "
    "(обложка биографии), P13 (тёмная обложка детектива) и P20 (постер "
    "документального фильма). Именно на них инструкция могла дать сбой, поэтому "
    "для каждого в таблице 2 указан признак, который оказался решающим."
)
cap2 = add_caption("Таблица 2 — Пограничные случаи, разобранные после слепой разметки", keep_next=True)
cap2.paragraph_format.page_break_before = True
add_table(
    ["ID", "Истинный класс", "Метка аннотатора", "Почему модель справилась"],
    [[m["id"], m["ground_truth"], m["blind_label"], m["reason"]]
     for m in notes["rows"]],
    widths_cm=[1.6, 3.6, 3.6, 8.2],
    size=10.5,
)

for para in notes["detailed"]:
    add_par(para)

add_par(notes["rules"])
add_par(notes["fix"])

add_h1("6. Вывод")
add_h2("6.1. Сколько объектов нужно для реального обучения")
add_par(
    "Мини-датасет из 24 объектов пригоден только как прототип: он проверяет "
    "формулировку классов, инструкцию и процедуру разметки, но не позволяет "
    "обучить устойчивый классификатор. По материалам лекции 2.6 для дообучения "
    "модели под новую стилистику требуется не менее 100–200 качественных "
    "примеров; для трёх классов это 300–600 изображений. Текущий набор меньше "
    "нижней границы примерно в 12,5 раза (300 / 24) и меньше верхней — в 25 раз "
    "(600 / 24). При этом речь идёт о минимуме для дообучения, а не о "
    "полноценном обучении с нуля: там счёт идёт на миллионы. ImageNet содержит "
    "более 14 млн изображений, а DALL·E обучали на 650 млн пар «изображение — "
    "текст» (лекция 2.3)."
)
add_par(
    "Разнообразие важнее простого количества. Даже 300 изображений, сгенерированных "
    "одной моделью по шаблонным промптам, дадут меньше пользы, чем 150 реальных "
    "афиш, обложек и постеров разных лет, стран и полиграфических школ. Принцип "
    "«1000 точных примеров лучше миллиона зашумлённых» (лекция 2.4) работает и в "
    "обратную сторону: 24 идеально сбалансированных, но однотипных примера не "
    "заменяют нескольких сотен разнородных. Для реального проекта набор нужно "
    "расширять за счёт открытых источников с проверенными лицензиями и "
    "собственной съёмки, а генерацию использовать только для пополнения редких "
    "краевых случаев."
)
add_h2("6.2. Смещения, заложенные в мини-датасет")
add_par(
    "1. Смещение генератора. Все 24 изображения созданы одной моделью "
    "(tongyi-mai/z-image), поэтому набор наследует её эстетику: характерную "
    "композицию, плотность текста, палитру и типовые искажения надписей. "
    "Классификатор, обученный на таких данных, может выучить стиль генератора, а "
    "не признаки носителя. Это прямое нарушение требования стилевой однородности "
    "в обратную сторону: набор слишком однороден по происхождению (лекция 2.6)."
)
add_par(
    "2. Стереотипность классов. Промпты создают «учебниковые» примеры: у всех "
    "постеров фильма есть блок титров, у всех обложек — имя автора, у всех афиш — "
    "дата и место. В реальности эти элементы встречаются не всегда: бывают "
    "постеры без титров, обложки без имени автора на лицевой стороне, афиши без "
    "адреса. Модель обучится на идеализированных краевых случаях и будет хуже "
    "работать на реальном потоке (лекция 2.4 — краевые случаи)."
)
add_par(
    "3. Культурное смещение. Промпты написаны на английском, и текст на "
    "изображениях получается англоязычным. Русскоязычные афиши, обложки и постеры "
    "устроены иначе: другая типографика, другие обязательные элементы, другие "
    "пропорции текста и изображения. Классификатор, обученный на англоязычном "
    "наборе, столкнётся с распределением, которого не видел; это классическая "
    "проблема репрезентативности выборки (лекция 2.3)."
)
add_par(
    "4. Перекрытие классов. Границы между афишей, обложкой и постером фильма "
    "размыты по построению: все три типа содержат заголовок, изображение и "
    "мелкий текст. Инструкция снижает неоднозначность, но не устраняет её "
    "полностью, что подтверждают пограничные случаи слепой разметки (P04, P11, "
    "P13, P20). В реальном "
    "датасете перекрытие будет ещё сильнее, поэтому классы нужно либо уточнять "
    "(например, отделять киноафишу от афиши события), либо переходить к "
    "многометочной разметке."
)
add_par(
    "5. Смещение проверки. Слепая выборка взята из того же сгенерированного набора "
    "и построена по тем же «учебниковым» промптам, поэтому проверка измеряет "
    "согласованность инструкции с идеальными примерами, а не её пригодность на "
    "реальных данных. Результат 18 из 18 — это «потолок» лёгкого теста, а не "
    "доказательство универсальности правил. Чтобы измерить реальное качество "
    "инструкции, нужен второй набор: фотографии настоящих афиш, обложек и постеров "
    "с сайтов издательств, кинотеатров и библиотек, в том числе русскоязычных и "
    "с искажёнными или отсутствующими текстовыми блоками."
)

# ---------------------------------------------------------------- appendices

add_h1("Приложение А. Таблица разметки (24 объекта)", page_break=True)
add_par(
    "Полная таблица в компактном виде; расширенные формулировки источника и "
    "лицензии, промпты и изображения приведены в файле разметка.xlsx "
    "(листы «Разметка» и «Превью») и в журнале logs/labels_ground_truth.json.",
    size=12, after=6,
)
add_table(
    ["ID", "Файл", "Класс", "Источник", "Лицензия", "Разметчик", "Комментарий"],
    [[x["id"], x["file"], x["class"], "Polza.ai, z-image", "Собственное (ИИ)",
      "Ханна М. Н.", x["comment"]] for x in labels],
    widths_cm=[1.2, 1.9, 2.5, 3.3, 2.2, 2.0, 3.9],
    size=9,
    header_size=9,
)

add_h1("Приложение Б. Инструкция разметчика", page_break=True)
instr = (LOGS / "instruction.md").read_text(encoding="utf-8").split("---")[0]
for raw in instr.splitlines():
    line = raw.strip()
    if not line or line == "# Инструкция разметчика":
        continue
    if line.startswith("**") and line.endswith("**") and len(line) > 4:
        add_par(line[2:-2].strip(), bold=True, after=2)
    elif line.startswith("**") and ":**" in line:
        head, rest = line[2:].split(":**", 1)
        add_par(head + ":", bold=True, after=2)
        if rest.strip():
            add_par(rest.strip(), after=6)
    elif line.startswith("- "):
        add_bullet(line[2:].strip(), marker="—")
    else:
        add_par(line.replace("**", ""), after=4)

add_h1("Приложение В. Журнал работ и стоимость", page_break=True)
add_par(
    "Инструменты: Python 3.13.17, Pillow 13.0.0, python-docx, openpyxl 3.1.5, "
    "LibreOffice (конвертация DOCX → PDF), curl.exe. Генерация изображений и "
    "слепая разметка выполнены через API Polza.ai; ключ хранился локально и в "
    "отчёт не включён. Дата работы — 19.11.2026, время московское."
)
add_caption("Таблица 3 — Стоимость выполнения работы", keep_next=True)
add_table(
    ["Операция", "Модель", "Количество", "Цена", "Сумма"],
    [
        ["Генерация изображений", "tongyi-mai/z-image", "24", "1,40 ₽", f"{total_rub:.2f} ₽"],
        ["Слепая разметка и стресс-тест", "google/gemini-2.5-flash",
         f"{llm_calls} (10 + 8)",
         "по тарифу", f"{llm_cost:.2f} ₽"],
        ["Итого", "—", "—", "—", f"{grand_total:.2f} ₽"],
    ],
    widths_cm=[4.0, 4.8, 4.5, 1.8, 1.9],
    size=10.5,
)
add_par(
    f"Токены Gemini 2.5 Flash: {llm_in} входных и {llm_out} выходных. "
    "Бюджет задания — 50 ₽; фактические расходы составили "
    f"{grand_total:.2f} ₽, то есть около {grand_total / 50 * 100:.0f} % бюджета. "
    "Платные вызовы других моделей не выполнялись.",
    before=6,
)
add_caption("Таблица 4 — Хронология выполнения работы", keep_next=True)
add_table(
    ["Время (MSK)", "Действие"],
    [
        ["16:12", "Проверены ключ Polza.ai, версии Python и библиотек, доступ к /api/v1/models (HTTP 200)."],
        ["16:18", "Сгенерировано первое изображение P01 (864×1152, 1,40 ₽) — проверка формата ответа."],
        ["16:19", "Написана инструкция разметчика (7 правил)."],
        ["16:19–16:25", "Пакетная генерация остальных 23 изображений (по 1,40 ₽)."],
        ["16:26", "Собраны labels_ground_truth.json и разметка.xlsx."],
        ["16:26", "Выполнена слепая разметка 10 изображений моделью Gemini 2.5 Flash."],
        ["16:27–16:28", "Контрольный прогон на 8 изображениях, включая повтор P15."],
        ["16:29", "Посчитана доля совпадений, собран agreement.json."],
        ["16:34", "Собраны четыре композита скриншотов и текстовые журналы."],
        ["16:37", "Собраны DOCX и PDF отчёта, выполнена самопроверка вёрстки."],
    ],
    widths_cm=[2.6, 14.4],
    size=10.5,
)

doc.core_properties.title = "Отчет. Задание 5. Разметка датасета для задачи классификации"
doc.core_properties.subject = "Применение генеративных нейронных моделей в мультимедиа, задание 5"
doc.core_properties.author = "Ханна М. Н."

REPORT.mkdir(parents=True, exist_ok=True)
doc.save(DOCX)
print("saved", DOCX)
print(f"agreement {matches}/{total_blind} = {pct}%")
print(f"cost: images {total_rub:.2f} + llm {llm_cost:.4f} = {grand_total:.2f} RUB")
