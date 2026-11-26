"""Build Отчет_М3_Задание2.docx (research of ElevenLabs, LETI title page)."""
import pathlib

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, RGBColor

ROOT = pathlib.Path(__file__).resolve().parents[1]
SHOTS = ROOT / "screenshots"
LOGS = ROOT / "logs"
REPORT = ROOT / "report"
DOCX = REPORT / "Отчет_М3_Задание2.docx"

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


def add_lead(label, text, size=14):
    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.JUSTIFY, 0, 3, 1.25, 1.0)
    r = p.add_run(label)
    fmt_run(r, size, bold=True)
    r2 = p.add_run(text)
    fmt_run(r2, size)
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


def add_caption(text, size=12, keep_next=False, before=6, after=10):
    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.CENTER, before, after, 0, 1.0, keep_next=keep_next)
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


def add_picture(path, width_cm=16.5):
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
              align_center_cols=(), keep_together=True):
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
    for side, val in (("top", 30), ("bottom", 30), ("left", 70), ("right", 70)):
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
    if keep_together:
        for row in table.rows[:-1]:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.keep_with_next = True
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
tpar("Тема: Исследование сервиса синтеза голоса", bold=False)
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

# ---------------------------------------------------------------- 1. intro

add_h1("1. Введение")
add_par(
    "Цель работы — исследовать сервис синтеза и клонирования голоса ElevenLabs: "
    "разобраться в режимах доступа, требованиях к записи, управляемых параметрах, "
    "поддержке русского языка и ограничениях, а затем предложить два сценария "
    "применения в связях с общественностью. Задание исследовательское: собственное "
    "аудио не генерировалось, выводы опираются на официальную документацию и "
    "демонстрационные страницы сервиса."
)
add_par(
    "Отдельный результат работы — ограничение доступа: сайт и API сервиса из России "
    "перенаправляют на служебную страницу «Access restricted», где Россия "
    "перечислена среди закрытых регионов. Поэтому страницы изучались по архивным "
    "копиям официального сайта (web.archive.org), и рисунки 1–3 — снимки этих "
    "архивных копий официальных страниц."
)

# ---------------------------------------------------------------- 2. template

add_h1("2. Заполненный шаблон")

add_h2("2.1. Сервис")
add_par(
    "Сервис выбран по трём признакам: известность и полнота документации, наличие "
    "клонирования голоса и поддержка русского языка. Все сведения ниже взяты со "
    "страниц elevenlabs.io (снимки от 06.12.2025 до 25.11.2026); перечень "
    "источников — в приложении А."
)
add_caption("Таблица 1 — Сервис ElevenLabs: режим доступа", keep_next=True, before=4, after=4)
add_table(
    ["Поле", "Значение"],
    [
        ("Название", "ElevenLabs"),
        ("URL", "https://elevenlabs.io"),
        ("Режим доступа",
         "Бесплатный тариф: 10 000 кредитов в месяц (≈ 10 минут озвучки), доступны "
         "синтез речи, распознавание, звуковые эффекты, Voice Design, музыка и три "
         "проекта в Studio"),
        ("Клонирование голоса",
         "В бесплатный тариф не входит: Instant Voice Cloning появляется на тарифе "
         "Starter, Professional Voice Cloning — на тарифе Creator; пробного периода "
         "для клонирования на сайте не заявлено"),
        ("Коммерческая лицензия",
         "С тарифа Starter (Commercial License); на бесплатном тарифе коммерческое "
         "использование не предусмотрено"),
        ("Доступность из России",
         "Закрыта: сайт и API перенаправляют на страницу «Access restricted», Россия "
         "входит в официальный список ограниченных регионов"),
    ],
    widths_cm=[4.4, 12.6],
)
add_par(
    "Кредиты общие для всех продуктов; на бесплатном тарифе они не переносятся на "
    "следующий месяц. Логика тарифов ступенчатая: бесплатный тариф показывает "
    "качество синтеза и библиотеку голосов, Starter добавляет коммерческую лицензию "
    "и быстрое клонирование, Creator — профессиональное клонирование с дообучением. "
    "Для учебной задачи это означает, что оценить синтез можно без оплаты, а "
    "проверить клонирование — только на платном тарифе.",
    before=6,
)
add_par(
    "Отдельно стоит зафиксировать ограничение по региону. Страница блокировки "
    "перечисляет Беларусь, Кубу, Иран, КНДР, Россию, Сирию, Крым и отдельные "
    "области Украины; там же сказано, что ограничения иногда затрагивают и "
    "соединения из других мест, если провайдер связывает IP-адрес с закрытым "
    "регионом. Практический вывод: из России сервис нельзя использовать напрямую — "
    "ни через сайт, ни через API."
)

add_h2("2.2. Входные данные")
add_par(
    "У сервиса два режима клонирования, и требования к записи у них различаются на "
    "порядок. Ниже — данные из документации по Instant Voice Cloning и Professional "
    "Voice Cloning."
)
add_caption("Таблица 2 — Требования к записи для клонирования голоса",
            keep_next=True, before=4, after=4)
add_table(
    ["Режим", "Минимум", "Оптимум", "Формат и условия"],
    [
        ("Instant Voice Cloning", "1 минута", "1–2 минуты,\nне более 3 минут",
         "Чистая речь одного диктора без шума, реверберации и музыки; MP3 от "
         "128 кбит/с; уровень −23…−18 dB RMS, истинный пик −3 dB"),
        ("Professional Voice Cloning", "30 минут", "2–3 часа",
         "Студийная запись: XLR-микрофон, поп-фильтр, обработанная комната; "
         "WAV/PCM 44,1 кГц (тариф Pro); дообучение 3–6 часов"),
    ],
    widths_cm=[3.6, 2.4, 3.4, 7.6],
)
add_par(
    "Главный принцип, который документация подчёркивает несколько раз: качество "
    "записи важнее её длительности. Для быстрого клона рекомендуется 1–2 минуты "
    "чистого аудио, а запись дольше трёх минут уже не улучшает результат и иногда "
    "его ухудшает. Сервис копирует всё, что слышит, — темп, интонации, акцент, "
    "дыхание, щелчки и фоновый шум, поэтому «шумные» десять минут дадут худший клон, "
    "чем чистые полторы.",
    before=6,
)
add_par(
    "Требования к содержанию записи: один говорящий, без наложения голосов, "
    "постоянная манера и громкость, без выраженных скачков тона и динамики. Для "
    "профессионального клона нужна студийная запись и верификация голоса: "
    "документация прямо указывает, что профессиональный клон можно создать только "
    "для собственного голоса, даже при согласии другого человека. Пение "
    "профессиональные клоны не поддерживают."
)
add_par(
    "После загрузки записи сценарии расходятся по времени. Быстрый клон сервис "
    "создаёт за секунды, дополнительная верификация не нужна — достаточно "
    "подтвердить право и согласие на клонирование. Профессиональный клон ставится в "
    "очередь на дообучение: обычно это занимает 3–6 часов, при большой загрузке — "
    "дольше. Перед обучением нужно пройти верификацию голоса, записав контрольную "
    "фразу на том же оборудовании; при неудаче попытку можно повторить через 24 часа."
)

add_h2("2.3. Управляемые параметры")
add_par(
    "Набор регуляторов в интерфейсе небольшой: четыре ползунка, переключатель и "
    "выбор модели с голосом. Значения и рекомендации — из страницы Voice settings."
)
add_caption("Таблица 3 — Управляемые параметры синтеза", keep_next=True, before=4, after=4)
add_table(
    ["Параметр", "Диапазон", "Что делает", "Рекомендация"],
    [
        ("Stability", "0–1",
         "Ниже — шире эмоциональный диапазон и больше разброса между генерациями; "
         "выше — ровнее, но вплоть до монотонности", "0,50"),
        ("Similarity Boost", "0–1",
         "Насколько близко синтез держится исходного голоса; при шумной записи "
         "переносит шум и артефакты", "0,75"),
        ("Style Exaggeration", "0–1",
         "Усиливает манеру оригинала, повышает задержку и снижает стабильность",
         "0,00"),
        ("Speed", "0,7–1,2",
         "Замедляет или ускоряет речь; недоступен для модели Eleven v3", "1,00"),
        ("Speaker Boost", "вкл/выкл",
         "Дополнительно усиливает сходство с оригиналом, немного повышает задержку",
         "вкл"),
        ("Clone Strength", "0–100 %",
         "Только для профессионального клона и Eleven v4: насколько выход следует "
         "тренировочным записям", "0 %"),
        ("Модель", "—",
         "Eleven v4 Turbo — 90+ языков; v3 — 70+; Multilingual v2 — 29; Flash v2.5 — "
         "32 языка и задержка менее 75 мс", "v2 для качества,\nFlash для скорости"),
        ("Голос", "—",
         "17 000+ готовых голосов, генерация по описанию (Voice Design) или "
         "клонированный голос", "—"),
    ],
    widths_cm=[3.4, 2.2, 8.2, 3.2],
)
add_par(
    "Сравнение с параметрами из видео курса показывает разницу в подходе. Высота "
    "тона отдельным регулятором не управляется: она задаётся выбранным голосом и "
    "записью, на которой обучен клон. Тембр — то же самое: это свойство голоса, а не "
    "ползунок. Скорость есть, но в узком диапазоне 0,7–1,2 и не для всех моделей. "
    "Эмоция управляется косвенно — через stability, style и, в модели v3, "
    "аудиотеги в тексте вида «[sarcastically]» или «[whispers]». Паузы задаются "
    "пунктуацией и SSML-тегами, причём документация предупреждает, что обработка "
    "пауз зависит от модели и голоса.",
    before=6,
)
add_par(
    "Иными словами, сервис управляет не отдельными акустическими признаками, а "
    "характером голоса целиком. Для PR-задач это удобно: не нужно быть звукорежиссёром, "
    "достаточно выбрать голос и двигать два ползунка. Для точной работы — например, "
    "чтобы поднять тон на полтона или выровнять паузы по хронометражу, — контроля не "
    "хватает, и это осознанный компромисс в пользу простоты."
)

add_h2("2.4. Языки и ограничения")
add_par(
    "Русский язык поддерживается во всех актуальных моделях. У Multilingual v2 "
    "заявлено 29 языков, и в списке есть русский (ru) и украинский (uk); у Flash v2.5 "
    "— 32 языка, у Eleven v3 — 70+, у Eleven v4 — 90+. Отдельная страница "
    "elevenlabs.io/text-to-speech/russian показывает русскую демонстрацию: голос "
    "Artem читает текст с эмоциональными пометками, а интерфейс предлагает выбрать "
    "русский голос и настроить скорость, stability и style. Клонированный голос "
    "может говорить на любом поддерживаемом языке, но документация предупреждает: "
    "если клон обучен на записях на другом языке, в новом языке возможен акцент."
)
add_par(
    "Ограничения на контент сформулированы в разделе о добросовестном использовании. "
    "Свой голос можно клонировать для любых целей; для чужого голоса требуется явное "
    "согласие владельца. Использование клонов для мошенничества, выдачи себя за "
    "другого человека и вводящего в заблуждение контента незаконно в большинстве "
    "юрисдикций, а коммерческое использование может требовать отдельной лицензии. "
    "При создании быстрого клона сервис просит подтвердить, что у пользователя есть "
    "право и согласие на клонирование; для профессионального клона обязательна "
    "верификация голоса."
)
add_par(
    "Техническая сторона защиты: голосовые данные шифруются и не используются для "
    "обучения без явного согласия, а системы верификации подтверждают разрешение на "
    "клонирование. Для учебного или редакционного проекта это означает простой "
    "порядок: письменное согласие спикера, понятная область использования, отдельное "
    "хранение исходных записей и пометка синтезированного аудио как синтезированного."
)
add_par(
    "Наконец, региональное ограничение — тоже часть поля «языки и ограничения». "
    "Россия входит в список закрытых регионов, поэтому бесплатный тариф и клонирование "
    "из РФ недоступны напрямую; для реального проекта понадобится либо доступ через "
    "зарубежную инфраструктуру организации, либо локальный аналог. На содержание "
    "исследования это не влияет: документация открыта в архиве, а параметры и "
    "требования описаны полностью."
)

add_h2("2.5. Применение в мультимедиа")
add_par(
    "Для специальности «Связи с общественностью» выбраны два сценария, где синтез "
    "речи решает измеримую задачу, а не просто демонстрирует технологию."
)
add_lead(
    "Сценарий 1. Озвучка корпоративного подкаста университета. ",
    "Пресс-служба выпускает еженедельный подкаст о новостях ЛЭТИ: наука, приёмная "
    "кампания, мероприятия. Каждый выпуск — 6–8 минут текста, а приглашать диктора "
    "на студию каждую неделю долго и дорого. Решение: записать 1,5–2 минуты чистой "
    "речи официального представителя университета с его письменным согласием и "
    "создать быстрый клон. Текст выпуска (6 000–7 000 знаков) укладывается в лимит "
    "одной генерации Multilingual v2 (10 000 знаков), поэтому выпуск синтезируется "
    "одним запросом. Параметры: stability 0,75, similarity 0,85, style 0,00, Speaker "
    "Boost включён. Выгода — узнаваемый голос во всех выпусках, отсутствие студийных "
    "сессий и возможность сделать англоязычную версию той же моделью."
)
add_lead(
    "Сценарий 2. Аудиогид для виртуального тура по кампусу. ",
    "На сайте приёмной комиссии тур по восьми точкам: главный корпус, пятый корпус, "
    "библиотека, общежития, спортивный комплекс и другие. Нужны русская и английская "
    "версии, один приветливый голос и быстрые обновления при изменении маршрута. "
    "Решение: готовый голос из библиотеки или клон голоса студента-гида с его "
    "согласия плюс Multilingual v2 — один и тот же текст генерируется на двух языках, "
    "а правка текста не требует перезаписи. Параметры: stability 0,60, similarity "
    "0,75, style 0,00, speed 1,0, Speaker Boost включён. Выгода — около 8 минут аудио "
    "на язык, единый тембр во всех точках и обновление за минуты."
)
add_par(
    "Оба сценария укладываются в возможности сервиса, но требуют тарифа с "
    "клонированием и доступа из страны, где сервис работает. Для учебной работы это "
    "не препятствие: задание исследовательское, а все параметры подтверждены "
    "документацией."
)
add_par(
    "Общее у сценариев одно: это регулярный контент с постоянным голосом. Подкаст "
    "выходит каждую неделю, аудиогид обновляется при изменении маршрута — и именно "
    "здесь клонирование даёт эффект: голос остаётся узнаваемым, а время и стоимость "
    "производства не растут вместе с числом выпусков. Разовые задачи — рекламный "
    "ролик, поздравление, объявление — выигрывают меньше: диктора всё равно "
    "записывают один раз, и синтез экономит немного."
)
add_par(
    "Эффект измерим тремя показателями: время от готового текста до готового аудио "
    "(у диктора это дни из-за записи и монтажа, у синтеза — минуты), стоимость "
    "минуты озвучки и число перезаписей при правке текста (при синтезе правка не "
    "требует студии). Для пресс-службы важен и четвёртый показатель — доля выпусков, "
    "вышедших в срок: синтез снимает зависимость от занятости спикера."
)
add_par(
    "Риски тоже нужно назвать. Синтез ошибается в ударениях и именах собственных, "
    "поэтому текст обязан проходить редактора, а имена и аббревиатуры лучше "
    "записывать словами. Длинные периоды звучат ровнее, но скучнее коротких фраз, "
    "поэтому сценарии рассчитаны на короткие абзацы. Наконец, синтетическое аудио "
    "следует помечать, а согласие спикера и хранение исходных записей — оформить "
    "документально: без этого проект становится юридическим риском, а не "
    "производственным инструментом."
)
add_par(
    "Порядок запуска такого проекта выглядит так: выбрать голос и получить "
    "письменное согласие, записать и проверить исходник, выбрать модель под язык и "
    "длину текста, зафиксировать параметры в шаблоне, чтобы выпуски не различались, "
    "и прослушать результат перед публикацией — ударения, имена, паузы."
)

# ---------------------------------------------------------------- 3. screenshots

add_h1("3. Скриншоты")
add_par(
    "Задание просит 2–3 скриншота экрана настроек сервиса. Прямой доступ к "
    "elevenlabs.io из России закрыт: сервис относит Россию к списку ограниченных "
    "регионов и перенаправляет посетителя на служебную страницу «Access restricted». "
    "Поэтому рисунки 1–3 — снимки архивных копий официальных страниц, полученных "
    "через сервис web.archive.org: это те же страницы сервиса, загруженные из архива. "
    "В верхней части каждого снимка видна панель архива с адресом страницы и датой "
    "снимка; дата продублирована в подписи к рисунку."
)
add_picture(SHOTS / "01_service_interface.png", width_cm=16.4)
add_caption("Рисунок 1 — Главная страница сервиса ElevenLabs (архивная копия "
            "официальной страницы, снимок 25.11.2026)", before=4, after=8)
add_par(
    "На рисунке 1 видно, как сервис подаёт себя: заголовок «Bringing technology to "
    "life» и пояснение, что платформа работает и для предприятий, и для отдельных "
    "авторов — от агентов до генератора речи. Продукты разделены на три направления "
    "— ElevenCreative, ElevenAgents и ElevenAPI, — а карусель сценариев Characters, "
    "Narration и Conversational показывает, для каких задач предлагаются голоса. Для "
    "связей с общественностью это прямо подсказывает первый сценарий: озвучка "
    "текстового материала в режиме Narration."
)
add_par(
    "Официальный снимок экрана настроек опубликован в документации (рисунок 2): "
    "панель Settings с выбором голоса Adam FM (late night radio) и модели Eleven "
    "Multilingual v2, ползунки Stability, Similarity и Style Exaggeration, "
    "переключатель Speaker boost и кнопка Reset values. Ползунок Stability сдвинут к "
    "правому краю шкалы More stable, Similarity — почти к самому краю High, Style "
    "Exaggeration стоит в крайнем левом положении None, Speaker boost включён. "
    "Числовых значений у ползунков нет, поэтому коэффициенты 0,50 и 0,75 из раздела "
    "2.5 взяты из рекомендаций документации, а не прочитаны с экрана; панель задаёт "
    "только положение шкалы."
)
add_picture(SHOTS / "02_voice_settings.png", width_cm=16.4)
add_caption("Рисунок 2 — Экран настроек голоса ElevenLabs: stability, similarity, "
            "style exaggeration, speaker boost (архивная копия официальной страницы, "
            "снимок 24.11.2026)", before=6, after=8)
add_par(
    "На рисунке 2 видно, что регуляторы независимы по положению, но связаны по "
    "эффекту: style повышает задержку и снижает стабильность, поэтому при style "
    "больше нуля приходится поднимать stability. Значения по умолчанию — не "
    "«оптимум качества», а компромисс между выразительностью и предсказуемостью: "
    "документация прямо говорит, что результат недетерминирован, а ползунки задают "
    "лишь ширину разброса между генерациями. Для подкаста это означает, что один и "
    "тот же абзац придётся генерировать несколько раз и выбирать лучший дубль."
)
add_par(
    "В панели нет отдельного регулятора высоты тона и нет настройки паузы: тон "
    "задаётся выбранным голосом, а паузы — пунктуацией и SSML в тексте. Это "
    "подтверждает вывод раздела 2.3: сервис управляет характером голоса, а не "
    "отдельными акустическими признаками."
)
add_picture(SHOTS / "03_language_selection.png", width_cm=16.4)
add_caption("Рисунок 3 — Поддержка языков: русский и украинский в списке 29 языков "
            "модели Multilingual v2 (архивная копия официальной страницы, снимок "
            "22.10.2026)", before=6, after=8)
add_par(
    "Рисунок 3 фиксирует главное для русскоязычного проекта: страница «What languages "
    "do you support?» перечисляет 29 языков модели Multilingual v2, и в списке есть "
    "русский (ru) и украинский (uk). Ниже на той же странице начинается список Flash "
    "v2.5 с 32 языками, поэтому выбор русскоязычной модели не ограничен одним "
    "вариантом."
)
add_par(
    "Список объясняет выбор модели для сценариев. Документация называет "
    "Multilingual v2 самой естественной и устойчивой на длинных текстах, а Flash "
    "v2.5 — быстрой и дешёвой, с задержкой менее 75 мс и лимитом 40 000 знаков. Для "
    "аудиогида и подкаста важнее естественность и ровность длинных фраз, поэтому "
    "выбрана v2; Flash уместна там, где нужен отклик в реальном времени, например "
    "в голосовом боте приёмной комиссии."
)
add_par(
    "Для двуязычного проекта существенно ещё одно обстоятельство: язык не закреплён "
    "за голосом. Один и тот же выбранный голос читает русский и английский текст, "
    "поэтому русская и английская версии аудиогида звучат как один гид, а не как "
    "два разных диктора."
)

# ---------------------------------------------------------------- appendix A

add_h1("Приложение А", page_break=True)
add_par(
    "Источники — официальные страницы ElevenLabs. Прямой доступ из России закрыт: "
    "сайт перенаправляет на служебную страницу «Access restricted», поэтому страницы "
    "получены из архива Интернета (web.archive.org); "
    "дата снимка указана для каждой страницы. Обращение к источникам — 25.11.2026."
)
add_caption("Таблица А.1 — Использованные страницы и даты снимков",
            keep_next=True, before=4, after=4)
add_table(
    ["Страница", "Что взято", "Снимок"],
    [
        ("elevenlabs.io", "назначение сервиса, 17 500+ голосов, продукты",
         "25.11.2026"),
        ("elevenlabs.io/voice-cloning", "режимы клонирования, 1–5 минут и 30+ минут, "
         "вопросы согласия", "31.10.2026"),
        ("elevenlabs.io/text-to-speech/russian", "русская демонстрация, голос Artem, "
         "аудиотеги", "13.11.2026"),
        ("elevenlabs.io/pricing", "бесплатный тариф, 10 000 кредитов, состав тарифов",
         "24.11.2026"),
        ("elevenlabs.io/docs/overview/models", "линейка моделей и число языков",
         "25.11.2026"),
        ("elevenlabs.io/docs/eleven-creative/playground/text-to-speech",
         "параметры, диапазоны и рекомендации", "24.11.2026"),
        ("elevenlabs.io/docs/help-center/other/what-languages-do-you-support",
         "полные списки языков по моделям", "22.10.2026"),
        ("elevenlabs.io/docs/product-guides/voices/voice-cloning/instant-voice-cloning",
         "требования к записи для быстрого клона", "06.12.2025"),
        ("elevenlabs.io/docs/product-guides/voices/voice-cloning/professional-voice-cloning",
         "требования к записи и верификация для PVC", "22.09.2026"),
    ],
    widths_cm=[7.6, 7.0, 2.4],
    size=11,
)
add_par(
    "Дополнительно сохранена страница блокировки elevenlabs.io — она отдаётся вместо "
    "сайта при обращении из России и содержит список закрытых регионов. Все сырые "
    "HTML-файлы и их текстовые версии лежат в папке logs.",
    before=6,
)
add_par(
    "Ключевые факты, на которые опирается отчёт: бесплатный тариф — 10 000 кредитов "
    "в месяц без клонирования; быстрое клонирование — от 1 минуты записи, "
    "профессиональное — от 30 минут; параметры stability, similarity и style лежат в "
    "диапазоне 0–1, speed — 0,7–1,2; русский язык входит в 29 языков Multilingual v2 "
    "и в списки остальных моделей; клонирование чужого голоса требует согласия, "
    "профессиональный клон — только для собственного голоса."
)

# ---------------------------------------------------------------- appendix B

add_h1("Приложение Б", page_break=True)
add_par(
    "Журнал работы: этапы, результат и артефакт. Точные метки времени каждого шага — "
    "в файле logs/worklog.md."
)
add_caption("Таблица Б.1 — Хронология выполнения работы (25.11.2026, время MSK)",
            keep_next=True, before=4, after=4)
add_table(
    ["Этап", "Содержание", "Артефакт"],
    [
        ("Подготовка", "Проверка окружения: Python 3.13.17, python-docx 1.2.0, "
         "Pillow 13.0.0, requests 2.34.2, beautifulsoup4 4.15.0", "worklog.md"),
        ("Проверка доступа", "elevenlabs.io перенаправляет на страницу «Access "
         "restricted»; Россия в списке ограничений", "geo_block_page.html"),
        ("Сбор источников", "Девять официальных страниц получены из web.archive.org, "
         "снимки от 06.12.2025 до 25.11.2026", "elevenlabs_*.html"),
        ("Разбор страниц", "HTML очищен до текста, девять файлов", "text/"),
        ("Конспект фактов", "Языки, требования к записи, параметры, ограничения",
         "docs_facts.md"),
        ("Сценарии", "Два сценария для связей с общественностью", "research_notes.md"),
        ("Снимки", "Реальные скриншоты архивных копий официальных страниц",
         "screenshots/"),
        ("Съёмка", "Headless Chrome: 1440×900, 1440×1000, 1440×1300, масштаб 1,5",
         "capture_archive_shots.py"),
        ("Отчёт", "Сборка DOCX, экспорт PDF, проверки вёрстки", "report/"),
    ],
    widths_cm=[3.0, 9.8, 4.2],
    size=10.5,
)
add_par("Все артефакты — в папке voice-service; скрипты лежат в scripts/.",
        size=12, italic=True, before=4)
add_par(
    "Тест синтеза через API не проводился. Задание исследовательское и не требует "
    "собственной генерации, поэтому расходовать бюджет на пробный запрос не было "
    "необходимости. Исследование опирается на документацию и демонстрации сервиса, "
    "поэтому отсутствие аудиофайла на выводы не влияет.",
    before=6,
)
add_par(
    "Проверки перед сдачей: тема на титульном листе — «Тема: Исследование сервиса "
    "синтеза голоса», слово «отчет» строчное и не полужирное; имя студента — "
    "«Ханна М. Н.»; на первой странице нет номера, нумерация начинается со второй; "
    "все пять полей шаблона заполнены фактическими данными; три рисунка на месте и "
    "подписаны; в тексте нет служебных пометок и незаполненных мест; шрифт — Times "
    "New Roman, кегль 14, поля 2 см, формат А4."
)

REPORT.mkdir(parents=True, exist_ok=True)

# keep thousands together: "10 000" must not break across lines
import re

NBSP = "\u00A0"
all_pars = list(doc.paragraphs)
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            all_pars.extend(cell.paragraphs)
for p in all_pars:
    for r in p.runs:
        if r.text and re.search(r"\d \d", r.text):
            r.text = re.sub(r"(?<=\d) (?=\d)", NBSP, r.text)

doc.save(DOCX)
print("saved", DOCX)
