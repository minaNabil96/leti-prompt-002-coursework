"""Build Отчет_М3_Задание1.docx (Russian, LETI title page, A4, TNR 14)."""
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
SHOTS = ROOT / "screenshots"
LOGS = ROOT / "logs"
REPORT = ROOT / "report"
DOCX = REPORT / "Отчет_М3_Задание1.docx"

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


def add_caption(text, size=12, keep_next=False, before=6, after=12):
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
              align_center_cols=(), keep_together=True, cell_pad=30):
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
    for side, val in (("top", cell_pad), ("bottom", cell_pad),
                      ("left", 40), ("right", 40)):
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


def ru(v, d=2):
    return f"{v:.{d}f}".replace(".", ",")


def sp(v):
    return f"{int(v):,}".replace(",", " ")


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
tpar("Тема: Голосовая беседа с AI-ассистентом", bold=False)
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

CONV = json.loads((LOGS / "conversation.json").read_text(encoding="utf-8"))
TTS = json.loads((LOGS / "tts_results.json").read_text(encoding="utf-8"))
STT = json.loads((LOGS / "stt_check.json").read_text(encoding="utf-8"))
PROS = json.loads((LOGS / "prosody.json").read_text(encoding="utf-8"))

TURNS = CONV["turns"]
TOT_LLM = CONV["totals"]["cost_rub"]
TOT_TTS = TTS["totals"]["cost_rub"]
TOT_STT = STT["totals"]["cost_rub"]
UI = json.loads((LOGS / "ui_repeat.json").read_text(encoding="utf-8"))
TOT_UI = round(sum(UI["costs_rub"]), 4)
TOT_ALL = TOT_LLM + TOT_TTS + TOT_STT + TOT_UI

# ---------------------------------------------------------------- 1. intro

add_h1("1. Введение")
add_par(
    "Цель работы — провести голосовую беседу с AI-ассистентом, озвучить его "
    "ответы синтезом речи и оценить, насколько получившийся голос пригоден для "
    "восприятия на слух. Задание проверяет сразу две вещи: как языковая модель "
    "ведёт длинный диалог (помнит ли контекст, реагирует ли на смену темы, "
    "подстраивается ли под стиль собеседника) и как система синтеза речи "
    "читает русский текст — интонацию, паузы, ударения и имена собственные."
)
add_par(
    "Работа выполнена на платформе Polza.ai через её OpenAI-совместимый API. "
    "Беседу ведёт модель google/gemini-2.5-flash при температуре 0,7; ответы "
    "озвучивает модель google/gemini-3.8-flash-lite-tts голосом Kore. Задание "
    "допускает «голосовой режим чат-бота или другой доступный» вариант; в этом "
    "качестве использован голосовой режим чат-бота на платформе Polza.ai, "
    "поэтому замена моделей не потребовалась. Дополнительно ответы распознаны "
    "моделью openai/whisper-large-v3: это не часть задания, а способ объективно "
    "проверить, что именно слышно в синтезированных файлах."
)
add_par(
    "Тема беседы — планирование поездки в Казань на выходные. Сценарий состоит "
    "из 12 реплик пользователя: достопримечательности, музеи, билеты, "
    "рестораны, транспорт, часы работы Кремля, затем смена темы на погоду в "
    "Санкт-Петербурге (реплики 7–8) и возврат к Казани (реплики 9–12). Смена "
    "темы нужна, чтобы проверить удержание контекста: в реплике 9 пользователь "
    "спрашивает о музее, который ассистент перечислял пять реплик назад. Стиль "
    "пользователя намеренно смешанный — от коротких бытовых реплик до "
    "развёрнутых вежливых просьб."
)
add_par(
    "Все данные получены реальными запросами: 12 обращений к chat/completions, "
    "6 — к audio/speech, 6 — к audio/transcriptions; протоколы, аудио, снимки "
    "интерфейса сервиса и визуализации данных лежат в папках logs, audio и "
    "screenshots. Для снимка экрана беседы те же 12 реплик были повторены в "
    "веб-интерфейсе сервиса. Общая "
    f"стоимость — {ru(TOT_ALL)} ₽ из 15 ₽ бюджета (без учёта калибровочных "
    "запросов на 0,0095 ₽)."
)

# ---------------------------------------------------------------- 2. description

add_h1("2. Описание беседы")
add_par(
    "Диалог вёлся в одном контексте: каждый следующий запрос содержал системный "
    "промпт и все предыдущие пары сообщений, поэтому модель видела беседу "
    "целиком. Системный промпт задавал роль голосового помощника по "
    "путешествиям, требовал дружелюбного ответа по делу, сохранения темы при её "
    "смене, подстройки длины ответа под собеседника и записи чисел, цен и дат "
    "прописью — последнее нужно для корректной озвучки."
)
add_par(
    "Реплики подобраны так, чтобы проверить разные режимы работы ассистента. "
    "Таблица 1 перечисляет их в порядке диалога."
)
add_caption("Таблица 1 — Сценарий беседы: 12 реплик пользователя", keep_next=True)
add_table(
    ["№", "Стиль реплики", "Содержание"],
    [
        ["1", "Нейтральный", "Приветствие, просьба перечислить обязательные "
                              "достопримечательности Казани."],
        ["2", "Вежливый, развёрнутый", "Какие музеи интереснее и где они "
                                       "находятся (нужны адреса)."],
        ["3", "Деловой", "Сколько стоит билет на поезд из Москвы в Казань "
                         "в одну сторону."],
        ["4", "Вежливая просьба", "Два ресторана татарской кухни в центре, "
                                  "недалеко от Кремля."],
        ["5", "Нейтральный", "Как добраться от вокзала до центра: такси "
                             "или метро."],
        ["6", "Нейтральный", "Дни работы Кремля и экскурсии с гидом."],
        ["7", "Разговорный, смена темы", "«Стоп, забыла спросить» — погода "
                                         "в Санкт-Петербурге, нужен ли зонт."],
        ["8", "Короткий", "Будет ли завтра дождь в Петербурге."],
        ["9", "Разговорный, возврат к теме", "Какой из упомянутых музеев самый "
                                             "популярный у туристов."],
        ["10", "Короткая бытовая реплика", "Где лучше остановиться: у Кремля "
                                           "или на улице Баумана."],
        ["11", "Деловой", "Сколько стоит номер на двоих на две ночи."],
        ["12", "Эмоциональный, короткий", "Благодарность за подробные ответы."],
    ],
    widths_cm=[1.0, 4.1, 11.9], size=10, header_size=10, align_center_cols=(0,),
)
add_par(
    f"Беседа заняла 35 секунд машинного времени: с {CONV['started'][11:]} до "
    f"{CONV['finished'][11:]}. Суммарно модель получила "
    f"{sp(CONV['totals']['prompt_tokens'])} входных и выдала "
    f"{sp(CONV['totals']['completion_tokens'])} выходных токенов; ответы "
    "занимают 13 170 символов, то есть в среднем около 1 100 символов на "
    "реплику. Для озвучки выбраны шесть ответов — реплики 1, 3, 6, 7, 9 и 11: "
    "они покрывают начало беседы, смену темы и возврат к ней и дают 6,4 минуты "
    "речи.",
    before=4,
)
add_par(
    "Отдельно стоит сказать о том, чего в сценарии нет. Пользователь не "
    "спрашивает о фактах, требующих доступа к интернету, кроме погоды: именно "
    "на ней и проверяется, умеет ли модель признавать отсутствие данных. Цены "
    "на билеты и отели тоже приблизительные, но здесь есть оговорка "
    "«ориентировочно» и совет проверить на сайте, что для планирования поездки "
    "приемлемо."
)

# ---------------------------------------------------------------- 3. template

add_h1("3. Заполненный шаблон")

add_h2("3.1. Ассистент и тема")
add_par(
    "Ассистент — чат-бот google/gemini-2.5-flash на платформе Polza.ai с "
    "озвучкой google/gemini-3.8-flash-lite-tts (голос Kore), работающий как "
    "голосовой помощник по путешествиям. Тема беседы — поездка в Казань на "
    "выходные; беседа состоит из 12 реплик пользователя. Пользователь прошёл "
    "по теме последовательно: достопримечательности → музеи → билеты → рестораны → "
    "транспорт → часы работы Кремля. Затем тема дважды прерывалась (погода в "
    "Петербурге) и возвращалась к Казани (музей, отель, стоимость номера)."
)
add_par(
    "Ассистент удержал рамку разговора: в каждом ответе есть привязка к Казани, "
    "конкретные объекты (Кремль, Кул-Шариф, Сююмбике, улица Баумана, Дворец "
    "земледельцев) и практические детали — адреса, ориентировочные цены, часы "
    "работы. Средний ответ — 1 098 символов, то есть около минуты речи; для "
    "голосового канала это много (см. замечания в разделе 3.4)."
)

add_h2("3.2. Удержание контекста")
add_par(
    "Проверка прямая: в реплике 2 ассистент перечислил музеи, в реплике 7 тема "
    "сменилась на погоду, а в реплике 9 пользователь спросил: «Ты упоминал "
    "музеи — какой из них самый популярный у туристов?». Ассистент не "
    "переспросил и не потерял список: он назвал Музей-заповедник «Казанский "
    "Кремль» и перечислил внутри него те же объекты, что и в реплике 2 (Музей "
    "естественной истории Татарстана, Музей исламской культуры, Кул-Шариф, "
    "Благовещенский собор, Сююмбике). Контекст сохранён и после вставки про "
    "Петербург."
)
add_par(
    "Дополнительно проверено удержание чисел: в реплике 11 пользователь "
    "спрашивает цену номера «на двоих на две ночи», и ассистент считает именно "
    "две ночи и двоих, а не повторяет общий прайс. Это корректная работа с "
    "параметрами, заданными ранее."
)
add_par(
    "Ограничение: контекст держится только в пределах одной сессии. Приложение "
    "не хранит историю между запусками, поэтому «память» здесь — это весь "
    "массив сообщений, который каждый раз отправляется в модель. В последней "
    f"реплике он вырос до {sp(TURNS[-1]['prompt_tokens'])} входных токенов."
)

add_h2("3.3. Реакция на смену темы")
add_par(
    "Смена темы в реплике 7 («Стоп, забыла спросить. Какая сейчас погода в "
    "Санкт-Петербурге?») обработана правильно по форме: ассистент сразу "
    "переключился, отметил сам факт отвлечения («О, мы немного отвлеклись от "
    "Казани!») и в конце ответа предложил вернуться. Уточнение в реплике 8 "
    "(«А завтра в Питере тоже будет дождь?») он понял как продолжение той же "
    "темы и не смешал его с Казанью."
)
add_par(
    "По содержанию ответ на погоду — проблемный. Ассистент сначала честно "
    "пишет, что ему «нужно посмотреть актуальные данные», но затем всё равно "
    "называет конкретные значения: «облачно с прояснениями, температура около "
    "восемнадцати градусов Цельсия» и «вероятность небольших дождей». Доступа к "
    "прогнозу у модели нет, а 18 °C в конце ноября для Петербурга "
    "неправдоподобны (климатическая норма около нуля). Это типичная "
    "галлюцинация: гладкая, уверенная и неверная. Для голосового помощника "
    "такой класс ошибок опаснее всего — пользователь не видит источника и "
    "воспринимает цифру как факт."
)
add_par(
    "Правильная реакция — явный отказ («у меня нет доступа к прогнозу») или "
    "вызов инструмента погоды. Модель формально сделала шаг в эту сторону, но "
    "тут же его отменила: оговорка создаёт видимость проверки, и градусы звучат "
    "ещё убедительнее."
)

add_h2("3.4. Адаптация под стиль собеседника")
add_par(
    "Стиль пользователя намеренно смешанный: вежливые развёрнутые просьбы "
    "(«Посоветуй, пожалуйста, пару хороших ресторанов…»), короткие бытовые "
    "реплики («Окей», «Стоп, забыла спросить»), нейтральные вопросы и "
    "эмоциональная благодарность в конце."
)
add_par("Что получилось:", after=2)
add_bullet(
    "на короткие реплики в конце диалога ассистент отвечает заметно короче: "
    "реплика 8 (44 символа) → 486 символов, реплика 12 (50 символов) → 264 "
    "символа, то есть в 5–11 раз длиннее вопроса;"
)
add_bullet(
    "на развёрнутые просьбы — структурированный ответ со списком и пояснениями "
    "(реплики 4, 6, 10, 11);"
)
add_bullet(
    "регистр подхвачен: на «Стоп, забыла спросить» ассистент отвечает "
    "по-разговорному («О, мы немного отвлеклись…»), на деловую просьбу — "
    "нейтрально и по пунктам."
)
add_par(
    "Что не получилось: общей зависимости длины ответа от длины вопроса нет. "
    "Коэффициент корреляции между длиной реплики пользователя и длиной ответа — "
    "всего 0,16, а средний ответ в 16 раз длиннее вопроса (разброс от 5 до 29). "
    "Просьба «если он говорит коротко — отвечай кратко» выполняется лишь "
    "частично: модель по умолчанию склонна к подробным ответам, что для озвучки "
    "неудобно.",
    before=4,
)
add_par(
    "Причина, скорее всего, в системном промпте: требования «по делу» и "
    "«подстрой стиль» конкурируют с привычкой модели давать исчерпывающий "
    "ответ. Для голосового сценария длину лучше ограничивать явно — числом "
    "предложений или секунд речи."
)

add_h2("3.5. Качество речи (оценка 1–5)")
add_par(
    "Оценка выставлена по прослушиванию шести файлов и подкреплена измерениями: "
    "паузы и темп считались по огибающей, тон — алгоритмом pYIN (реализация "
    "librosa), соотношение сигнал/шум (HNR) — по алгоритму, реализованному в "
    "программе Praat (пакет praat-parselmouth). Итоговая оценка — 4 из 5."
)
add_caption("Таблица 2 — Оценка качества синтезированной речи", keep_next=True)
add_table(
    ["Критерий", "Оценка", "Обоснование"],
    [
        ["Интонация", "4",
         "Мелодика живая, диапазон широкий: медиана тона 163,1 Гц (по файлам — "
         "от 159 до 170 Гц), размах p10–p90 "
         "от 9 до 13 полутонов. Но перепады между абзацами местами чрезмерны — "
         "звучит как «качели», а не как спокойная речь."],
        ["Паузы", "5",
         "138 пауз на 381,52 с, средняя 0,50 с, максимальная 1,11 с; доля речи "
         "0,75–0,82. Паузы стоят на границах фраз и перечислений, неестественных "
         "провалов и «склеек» нет."],
        ["Ударения и произношение", "4",
         "Обычные слова прочитаны верно: сверка с распознаванием даёт совпадение "
         "89–99 %. Ошибка — татарский топоним «Сююмбике»: в двух файлах из "
         "трёх, где он встречается, распознавание слышит «Сюембике», то есть "
         "вторая «ю» редуцируется, а ударение смещается."],
        ["Итог", "4",
         "Речь разборчивая и пригодная для озвучки; мешают избыточная мелодика "
         "и произношение имён собственных."],
    ],
    widths_cm=[4.2, 1.6, 11.2], size=10, header_size=10, align_center_cols=(1,),
)
add_par("Метрики по файлам приведены в таблице 3.", before=4)
add_caption("Таблица 3 — Просодические характеристики шести файлов", keep_next=True)
rows = []
for r in PROS["by_file"]:
    rows.append([
        r["file"].split("/")[-1], str(r["turn"]), ru(r["duration_s"], 1),
        str(r["pause_count"]), f"{r['pauses_per_min']:.0f}", ru(r["pause_mean_s"]),
        ru(r["pause_max_s"]), f"{r['wpm']:.0f}", f"{r['f0_median_hz']:.0f}",
        ru(r["f0_span_semitones"], 1), ru(r["hnr_voiced_db"], 1),
    ])
add_table(
    ["Файл", "Реплика", "Длит., с", "Пауз", "Пауз/мин", "Ср. пауза, с",
     "Макс. пауза, с", "Темп, слов/мин", "f0, Гц", "Размах, пт", "HNR, дБ"],
    rows,
    widths_cm=[2.9, 1.35, 1.35, 1.15, 1.45, 1.5, 1.6, 1.55, 1.15, 1.4, 1.2],
    size=9, header_size=8.5, align_center_cols=tuple(range(1, 11)),
)
add_par(
    "Длительности в таблице округлены до 0,1 с; итоговые значения рассчитаны "
    "по точным данным prosody.json. API синтеза сообщает для тех же файлов "
    "381,16 с; в расчётах используется измеренная длительность 381,52 с.",
    size=12, before=2,
)
add_par(
    "Средний темп — 155 слов в минуту, что близко к нормальному темпу русской "
    "речи (около 150). Разборчивость подтверждается распознаванием: similarity "
    "0,89–0,99 по нормализованному расстоянию Левенштейна. Все файлы "
    "нормализованы почти до 0 dBFS, в четырёх есть от 1 до 8 сэмплов на уровне "
    "полной шкалы — на грани клиппинга, хотя на слух это не заметно. "
    "Постоянная составляющая отсутствует (|DC| менее 0,001). Оцифровка — 24 кГц, "
    "моно.",
    before=4,
)
add_par(
    "Пример ошибки. Слово «Сююмбике» (башня Казанского Кремля) синтезировано как "
    "«Сюембике»: на слух и по распознаванию пропадает один из гласных звуков в "
    "середине слова, ударение уходит на «е». Причина — имя собственное "
    "татарского происхождения, которого нет в русском произносительном словаре "
    "модели. Слово встречается в трёх файлах (реплики 1, 6 и 9): в первом "
    "распознавание слышит его верно, в двух других — «Сюембике». Ошибка зависит "
    "от контекста, но полностью не исчезает."
)
add_par(
    "Что ошибкой не является. «Зонт взять» распознавание передало как «зонд "
    "взять». Это нормативная регрессивная ассимиляция по звонкости на стыке "
    "слов (звук «т» перед «в» озвончается), а не дефект синтеза. Расхождения в "
    "записи чисел — тоже особенность распознавания, а не синтеза."
)

add_h2("3.6. Этапы работы TTS и слабейшее звено")
add_par("Синтез шёл по стандартной цепочке:")
add_bullet(
    "Нормализация текста. Снятие разметки Markdown, списков и нумерации, "
    "раскрытие чисел, дат, сокращений и символов в слова.", marker="1."
)
add_bullet(
    "Лингвистический анализ и G2P. Разбиение на предложения и синтагмы, "
    "расстановка ударений, преобразование орфографии в фонемы.", marker="2."
)
add_bullet(
    "Просодия. Выбор длительности звуков, мелодики и пауз по синтаксису.",
    marker="3."
)
add_bullet(
    "Акустическое моделирование и вокодер. Генерация звуковой волны, "
    "нормализация громкости, выдача WAV 24 кГц.", marker="4."
)
add_par(
    "Слабейшее звено для русского языка — нормализация текста, и это видно на "
    "практике:",
    before=4, after=2,
)
add_bullet(
    "модель получила уже очищенный текст: разметку **, списки и нумерацию "
    "пришлось убирать скриптом, иначе в озвучку попали бы лишние слова и паузы;"
)
add_bullet(
    "числа пришлось заранее записать словами через системный промпт LLM («от "
    "одной тысячи пятисот до двух тысяч пятисот рублей»): на цифрах и символах "
    "«₽», «%», «СВ», «РЖД» нормализатор ошибается чаще всего;"
)
add_bullet(
    "имена собственные не из словаря («Сююмбике», «Кул-Шариф») произносятся по "
    "общим правилам и дают ошибку — это прямое следствие того, что нормализация "
    "и G2P не знают татарской фонетики;"
)
add_bullet(
    "в исходном ответе LLM было обрезанное слово «планиру»; для синтеза оно "
    "исправлено на «планируете», в протоколе сохранён исходный вариант."
)
add_par(
    "Просодия и вокодер, наоборот, отработали хорошо: паузы и темп "
    "естественные, голос ровный, артефактов не слышно. Поэтому усилия при "
    "промышленном использовании нужно направлять не на акустику, а на "
    "подготовку текста: словари произношения, раскрытие сокращений, проверку "
    "чисел и единиц.",
    before=4,
)
add_caption("Таблица 4 — Сводка ответов по шести полям шаблона", keep_next=True,
            before=10)
add_table(
    ["Поле шаблона", "Краткий вывод"],
    [
        ["Ассистент и тема",
         "gemini-2.5-flash (Polza.ai, голос Kore), 12 реплик; голосовой помощник "
         "по путешествиям, тема раскрыта последовательно, каждый ответ привязан "
         "к Казани и содержит практические детали."],
        ["Удержание контекста",
         "Детали из реплики 2 воспроизведены в реплике 9 после вставки про "
         "Петербург; параметры «двое на две ночи» учтены в расчёте цены."],
        ["Реакция на смену темы",
         "Переключение по форме корректное, но ответ о погоде — галлюцинация: "
         "конкретные градусы названы без доступа к данным."],
        ["Адаптация под стиль",
         "Регистр и структура подстроены; длина — нет: ответы в среднем в 16 "
         "раз длиннее вопросов, корреляция 0,16."],
        ["Качество речи",
         "4 из 5: паузы и темп естественные, мелодика избыточна, «Сююмбике» "
         "произносится неверно в двух файлах из трёх."],
        ["Этапы работы TTS",
         "Слабейшее звено — нормализация текста: разметка, числа, сокращения и "
         "имена собственные; просодия и вокодер отработали хорошо."],
    ],
    widths_cm=[4.4, 12.6], size=10, header_size=10,
)
add_par(
    "Сводка показывает главное расхождение: по форме ассистент ведёт себя "
    "почти безупречно, а слабые места сосредоточены в содержании (погода) и в "
    "подготовке текста для синтеза (имена собственные, числа). Именно туда и "
    "нужно направлять доработку, а не в акустическую модель.",
    before=6,
)

# ---------------------------------------------------------------- 4. screenshots

add_h1("4. Экран беседы и экран настроек сервиса", page_break=True)
add_par(
    "Задание просит: «К отчёту приложите 2–3 скриншота (экран беседы, экран "
    "настроек сервиса)». Ниже — три снимка интерфейса Polza.ai и две "
    "визуализации данных сессии. Снимки сделаны в браузере 26.11.2026, файлы "
    "лежат в папке screenshots."
)
add_picture(SHOTS / "01_chat_screen_live.png", width_cm=15.0)
add_caption("Рисунок 1 — Экран беседы сервиса Polza.ai: реплика 6, ответ "
            "модели, поле ввода и выбранная модель (снимок 26.11.2026)")
add_par(
    "Это снимок живого веб-интерфейса Polza.ai, раздел «Песочница/Чат»: сверху "
    "вопрос про режим работы Казанского Кремля, ниже полный ответ модели, внизу "
    "поле ввода «Спросите что хотите» и чип выбранной модели «Google: Gemini "
    "2.5 Flash». Температура, лимит токенов и прочие параметры задаются в "
    "отдельной панели «Настройки», поэтому в кадре их нет. Основная сессия "
    "работы шла через API и в истории браузера не отображается, поэтому для "
    "снимка те же 12 реплик из таблицы 1 были заново отправлены в интерфейс "
    "26.11.2026 с 01:05 до 01:08 MSK и оплачены отдельно (4,3007 ₽, таблица "
    "Б.3). Ответы интерфейса дословно не совпадают с протоколом Приложения А — "
    "это независимые генерации, — но вопросы, модель и порядок реплик те же."
)
add_picture(SHOTS / "02_settings_chat_model.png", width_cm=17.0)
add_caption("Рисунок 2 — Экран настроек: карточка модели google/gemini-2.5-flash "
            "на polza.ai (снимок 26.11.2026)")
add_par(
    "Карточка фиксирует то, что задано для языковой модели: идентификатор "
    "google/gemini-2.5-flash, каталожные цены (18,18 ₽ за 1 млн входных и "
    "151,48 ₽ за 1 млн выходных токенов), контекст 1 млн токенов и предел "
    "ответа 66 тыс. токенов. Каталожные цены ниже фактических списаний, поэтому "
    "тариф для расчёта восстановлен по калибровочным запросам (Приложение Б)."
)
add_picture(SHOTS / "03_settings_tts_model.png", width_cm=17.0)
add_caption("Рисунок 3 — Экран настроек: карточка модели "
            "google/gemini-3.8-flash-lite-tts (снимок 26.11.2026)")
add_par(
    "Карточка модели синтеза: идентификатор google/gemini-3.8-flash-lite-tts, "
    "цены 60,59 ₽ за 1 млн входных и 727,12 ₽ за 1 млн выходных токенов и "
    "контекст 33 тыс. токенов. Выбора голоса в карточке нет: голос Kore "
    "передаётся параметром voice в запросе к /audio/speech."
)
add_picture(SHOTS / "01_conversation_screen.png", width_cm=12.9)
add_caption("Рисунок 4 — Визуализация данных: протокол беседы, реплики 1, 7 и 9 "
            "и полный список из 12 реплик")
add_par(
    "Рисунок 4 не является снимком интерфейса: это отрисовка протокола "
    "logs/conversation.json: слева полный список из 12 реплик с временем и "
    "числом токенов, справа выбранные ответы целиком. Реплика 1 задаёт тему, "
    "реплика 7 уводит её в Петербург, реплика 9 возвращает к Казани. По этой "
    "отрисовке удобно проверить и удержание контекста, и фактическую ошибку про "
    "погоду."
)
add_picture(SHOTS / "03_tts_analysis.png", width_cm=16.2)
add_caption("Рисунок 5 — Визуализация данных: анализ синтезированной речи — "
            "длительности файлов, осциллограмма с паузами, контур тона и метрики")
add_par(
    "Рисунок 5 собран из logs/prosody.json и показывает измерение речи на "
    "примере самого длинного файла (реплика 6, 78,2 с): сверху — длительности "
    "всех шести файлов, в середине — огибающая сигнала с отмеченными паузами, "
    "ниже — контур основного тона по секундным медианам и таблица метрик. "
    "Широкий размах тона и есть та самая избыточная мелодика, из-за которой за "
    "интонацию снижена оценка."
)

# ---------------------------------------------------------------- appendix A

add_h1("Приложение А. Полный транскрипт беседы", page_break=True)
add_par(
    "Тексты приведены дословно по logs/conversation.json; сохранены разметка "
    "списков и обрезанное слово «планиру» в первой реплике. Для синтеза это "
    "слово было исправлено на «планируете» (см. раздел 3.6)."
)


def clean_md(text):
    lines = []
    for raw in text.replace("**", "").split("\n"):
        s = raw.strip()
        if not s:
            lines.append("")
            continue
        if s.startswith("*"):
            s = "— " + s.lstrip("*").strip()
        s = " ".join(s.split())
        lines.append(s)
    return lines


for t in TURNS:
    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.LEFT, 8, 3, 0, 1.0, keep_next=True)
    r = p.add_run(f"Реплика {t['turn']} · {t['timestamp'][11:]}")
    fmt_run(r, 14, bold=True)

    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.JUSTIFY, 0, 3, 1.25, 1.0)
    r = p.add_run("Пользователь: ")
    fmt_run(r, 14, bold=True)
    r = p.add_run(t["user"])
    fmt_run(r, 14)

    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.LEFT, 0, 2, 0, 1.0, keep_next=True)
    r = p.add_run("Ассистент:")
    fmt_run(r, 14, bold=True)

    for line in clean_md(t["assistant"]):
        if not line:
            continue
        p = doc.add_paragraph()
        set_par(p, WD_ALIGN_PARAGRAPH.JUSTIFY, 0, 2, 0, 1.0)
        r = p.add_run(line)
        fmt_run(r, 14)

# ---------------------------------------------------------------- appendix B

add_h1("Приложение Б. Журнал работ и стоимость", page_break=True)
add_par(
    "Инструменты: Python 3.13.17, python-docx, Pillow, numpy, miniaudio, "
    "lameenc, mutagen, praat-parselmouth, librosa, PyMuPDF, LibreOffice."
)
add_caption("Таблица Б.1 — Хронология выполнения работы "
            "(25.11.2026–26.11.2026, время MSK)",
            keep_next=True, before=2, after=4)
add_table(
    ["Дата и время (MSK)", "Действие"],
    [
        ["25.11.2026, 18:20", "Создана структура проекта, скопирован ключ "
                              "Polza.ai."],
        ["25.11.2026, 18:21", "Проверены Python и библиотеки; GET /models — "
                              "HTTP 200."],
        ["25.11.2026, 18:22", "Подтверждены обе модели задания, их эндпоинты, "
                              "голоса и цены."],
        ["25.11.2026, 18:23", "Начата беседа: 12 запросов, температура 0,7."],
        ["25.11.2026, 18:24", "Беседа завершена: 23 784 входных и 3 697 "
                              "выходных токенов."],
        ["25.11.2026, 18:25", "Очистка ответов от Markdown, выбор голоса Kore."],
        ["25.11.2026, 18:26", "Синтез шести ответов через audio/speech: "
                              "5 632 символа, 381,52 с."],
        ["25.11.2026, 18:27", "WAV 24 кГц перекодированы в MP3 64 кбит/с."],
        ["25.11.2026, 18:28", "Распознавание шести файлов через "
                              "whisper-large-v3."],
        ["25.11.2026, 18:30", "Измерение пауз, темпа, тона и HNR."],
        ["25.11.2026, 18:40", "Пересчёт стоимости LLM по фактическим ставкам."],
        ["25.11.2026, 18:43", "Отрисовка визуализаций данных из "
                              "JSON-протоколов."],
        ["25.11.2026, 18:45", "Написана методика получения данных."],
        ["25.11.2026, 18:50", "Собраны DOCX и PDF, проверена вёрстка."],
        ["26.11.2026, 00:21", "Снимок беседы отложен: чат требует входа в аккаунт."],
        ["26.11.2026, 00:23", "Сняты карточки обеих моделей задания на polza.ai."],
        ["26.11.2026, 00:28", "Сверка с протоколами: тон, доля речи, длина ответов."],
        ["26.11.2026, 00:38", "Переписаны раздел 4 и подписи рисунков; "
                              "пересобраны DOCX и PDF."],
        ["26.11.2026, 01:05", "Те же 12 реплик повторены в веб-интерфейсе "
                              "Polza.ai."],
        ["26.11.2026, 01:08", "Повтор завершён, снят экран беседы — рисунок 1."],
        ["26.11.2026, 01:15", "Пересобраны DOCX и PDF; сверены контрольные суммы "
                              "копий."],
    ],
    widths_cm=[4.0, 13.0], size=10, header_size=10, align_center_cols=(0,),
    cell_pad=12,
)
add_caption("Таблица Б.2 — Обращения к API", keep_next=True, before=2, after=4)
add_table(
    ["Запрос", "Количество", "Результат"],
    [
        ["GET /api/v1/models", "1", "HTTP 200, 400 моделей"],
        ["POST /api/v1/chat/completions", "12 + 2", "все HTTP 200"],
        ["POST /api/v1/audio/speech", "6", "все HTTP 200, WAV 24 кГц"],
        ["POST /api/v1/audio/transcriptions", "6", "все HTTP 200"],
        ["Веб-интерфейс, тип запроса responses", "12", "все выполнены"],
    ],
    widths_cm=[7.2, 2.6, 7.2], size=10, header_size=10, align_center_cols=(1,),
    cell_pad=12,
)
add_par(
    "Два калибровочных запроса к LLM (0,0095 ₽) в таблицу не входят.",
    before=4,
)
add_caption("Таблица Б.3 — Стоимость работы", keep_next=True, before=2,
            after=4)
add_table(
    ["Статья", "Объём", "Стоимость, ₽"],
    [
        ["LLM google/gemini-2.5-flash", "12 запросов, 23 784 + 3 697 токенов",
         ru(TOT_LLM, 4)],
        ["TTS google/gemini-3.8-flash-lite-tts", "6 файлов, 5 632 символа, "
                                                 "381,52 с", ru(TOT_TTS, 4)],
        ["STT openai/whisper-large-v3 (проверка)", "6 файлов, 6,35 мин",
         ru(TOT_STT, 4)],
        ["Повтор беседы в веб-интерфейсе (для снимка экрана)",
         "12 запросов, responses", ru(TOT_UI, 4)],
        ["Итого", "", ru(TOT_ALL, 4)],
        ["Лимит задания", "", "15,0000"],
        ["Остаток", "", ru(15 - TOT_ALL, 4)],
    ],
    widths_cm=[8.6, 6.0, 2.4], size=10, header_size=10, align_center_cols=(2,),
    cell_pad=12,
)
add_par(
    "С калибровкой полная стоимость сессии — "
    f"{ru(TOT_ALL + 0.0095, 4)} ₽ ({ru(TOT_ALL + 0.0095, 2)} ₽).",
    before=4,
)
add_par(
    "Основная статья — синтез речи ({:.0f} %): он тарифицируется по длительности, "
    "а съёмка экрана добавила 32 %. Замены моделей не потребовались, сбоев не "
    "было: все ответы API — HTTP 200.".format(TOT_TTS / TOT_ALL * 100),
    before=4,
)

doc.core_properties.title = "Отчет. Модуль 3, задание 1. Голосовая беседа"
doc.core_properties.subject = ("Применение генеративных нейронных моделей "
                               "в мультимедиа, модуль 3, задание 1")
doc.core_properties.author = "Ханна М. Н."

REPORT.mkdir(parents=True, exist_ok=True)
doc.save(DOCX)
print("saved", DOCX)
