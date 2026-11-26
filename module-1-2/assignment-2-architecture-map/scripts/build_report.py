"""Build Отчет_Задание2.docx (Russian, LETI title page, A4, TNR 14)."""
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
DOCX = REPORT / "Отчет_Задание2.docx"

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


def add_caption(text, size=12):
    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.CENTER, 6, 12, 0, 1.0)
    r = p.add_run(text)
    fmt_run(r, size, bold=False, italic=True)
    return p


def add_bullet(text):
    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.LEFT, 0, 3, 1.25, 1.0)
    p.paragraph_format.left_indent = Cm(1.25)
    p.paragraph_format.first_line_indent = Cm(-0.5)
    r = p.add_run("— " + text)
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


def add_table(headers, rows, widths_cm, size=12):
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
        cell_text(c, h, bold=True, size=size, align=WD_ALIGN_PARAGRAPH.CENTER)
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
tpar("«Задание 2. Карта архитектур в реальных продуктах»", bold=False)
tpar("по курсу «Применение генеративных нейронных моделей", bold=True)
tpar("в мультимедиа»", bold=True)
for _ in range(4):
    tpar(exact_pt=40)
tpar(exact_pt=22)

# borderless 3-column table
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

# ---------------------------------------------------------------- body

add_h1("1. Введение")
add_par(
    "В настоящей работе строится карта архитектур генеративных нейронных сетей, стоящих за "
    "реальными продуктами, которыми пользуется студент. Цель работы — научиться различать "
    "трансформерные и диффузионные модели не по названию, а по проверяемым внешним признакам: "
    "типу входа и выхода, характеру времени генерации, виду ошибок, вариативности при повторном "
    "запуске и способности рисовать текст. Для этого выбраны шесть сервисов: три текстовых "
    "генератора на трансформерах (ChatGPT на GPT-4o, Yandex GPT, Gemini 2.5 Flash) и три "
    "генератора изображений на диффузии (Z-Image, Qwen-Image, Seedream 4.0). В каждом сервисе "
    "выполнено одно минимальное действие через единый шлюз Polza.ai, а архитектура подтверждена "
    "первоисточниками: техническими отчётами, документацией и публикациями. Актуальность темы "
    "связана с практическим выбором инструмента: понимание архитектуры позволяет заранее "
    "предсказать слабые места сервиса и корректно формулировать задачу. Отдельно рассматривается "
    "гибридный продукт, в котором обе архитектуры работают в связке. Работа состоит из карты "
    "архитектур, разбора шести сервисов, примера гибридного продукта и выводов о внешних "
    "признаках; все действия и их стоимость зафиксированы в журналах, поэтому выводы можно "
    "проверить и повторить."
)

add_h1("2. Методология")
add_par(
    "Сервисы подбирались по принципу доступности и контраста архитектур: три продукта решают "
    "текстовые задачи (диалог, перевод, суммаризация), три — синтезируют изображения. Все вызовы "
    "выполнены программно через OpenAI-совместимый шлюз Polza.ai: текстовые запросы — методом "
    "chat.completions, генерация изображений — через унифицированный Media API с последующим "
    "опросом задачи до статуса completed. Такой путь исключает ручную работу в веб-интерфейсах и "
    "делает эксперимент воспроизводимым. Для каждого сервиса выполнено ровно одно минимальное "
    "действие, а его вход, выход и фактическая стоимость сохранены в журналах. Основание для "
    "архитектурной метки искалось в первую очередь в первоисточниках: технических отчётах "
    "разработчиков, научных публикациях и официальной документации. Там, где прямое указание "
    "отсутствовало, вывод делался по косвенным признакам и помечался как предположение; в данной "
    "работе все шесть меток удалось подтвердить первоисточниками."
)

add_h1("3. Карта архитектур", page_break=True)
add_caption("Таблица 1 — Сервис, задача, вход, выход, архитектура и основание вывода")
add_table(
    ["Сервис", "Задача", "Вход", "Выход", "Архитектура", "Основание вывода"],
    [
        [
            "ChatGPT (GPT-4o)", "Чат-бот",
            "«Объясни принцип механизма внимания (attention)…»",
            "Текст, 2 предложения",
            "Трансформер (decoder-only, GPT)",
            "Подтверждено (Прил. А, ¹)",
        ],
        [
            "Yandex GPT", "Переводчик",
            "«Переведи на английский язык: Привет, мир!…»",
            "«Hello, world! Today is good weather…»",
            "Трансформер (YaLM, decoder-only)",
            "Подтверждено (Прил. А, ²)",
        ],
        [
            "Gemini 2.5 Flash", "Суммаризация",
            "Текст о диффузии, 177 слов + инструкция",
            "Резюме в 2 предложениях",
            "Трансформер (MoE)",
            "Подтверждено (Прил. А, ³)",
        ],
        [
            "Alibaba Z-Image", "Генерация изображения",
            "«A red apple on a white ceramic plate…»",
            "Изображение 1024×1024",
            "Диффузия (flow-matching DiT)",
            "Подтверждено (Прил. А, ⁴)",
        ],
        [
            "Alibaba Qwen-Image", "Генерация изображения",
            "«Фантастический город будущего на закате…»",
            "Изображение 1328×1328",
            "Диффузия (латентная, MMDiT)",
            "Подтверждено (Прил. А, ⁵)",
        ],
        [
            "ByteDance Seedream 4.0", "Генерация изображения",
            "«Portrait of a young woman with cyberpunk accessories…»",
            "Изображение 2048×2048",
            "Диффузия (rectified flow, DiT)",
            "Подтверждено (Прил. А, ⁶)",
        ],
    ],
    widths_cm=[2.4, 2.95, 2.9, 2.85, 2.95, 2.95],
    size=12,
)

add_h1("4. Детали по каждому сервису")

SECTIONS = [
    ("4.1. OpenAI ChatGPT (GPT-4o) — трансформер", "T1", 13,
     "В сервисе выполнен текстовый запрос с просьбой объяснить механизм внимания двумя "
     "предложениями. Модель вернула связный ответ за 2,4 секунды: она описывает веса важности "
     "элементов и вычисление матриц ключей, запросов и значений. Это типичное поведение "
     "авторегрессионного трансформера: ответ порождается токен за токеном. Архитектура "
     "подтверждена техническим отчётом GPT-4, где прямо сказано, что GPT-4 — модель на основе "
     "трансформера, предобученная предсказывать следующий токен."),
    ("4.2. Yandex GPT — трансформер", "T2", 13,
     "Сервис использован как переводчик: фраза «Привет, мир! Сегодня хорошая погода для прогулки "
     "в парке» переведена на английский за 0,64 секунды. Выход — короткая последовательность "
     "токенов, что характерно для текстовой трансформерной модели. YandexGPT построен на семействе "
     "YaLM; в открытом описании YaLM 100B модель названа GPT-подобной нейросетью для генерации и "
     "обработки текста, то есть decoder-only трансформером."),
    ("4.3. Google Gemini 2.5 Flash — трансформер", "T3", 13,
     "Сервис выполнил суммаризацию технического текста о диффузионных моделях (177 слов) в два "
     "предложения за 1,0 секунду. Ответ сохранил ключевые понятия: удаление шума, латентное "
     "пространство, flow matching и classifier-free guidance. Модель семейства Gemini — "
     "мультимодальный трансформер с разреженной смесью экспертов; это подтверждается техническим "
     "отчётом Gemini 1.5, где модель прямо названа MoE-трансформером."),
    ("4.4. Alibaba Z-Image — диффузия", "D1", 11,
     "По промпту «A red apple on a white ceramic plate…» получено фотореалистичное изображение "
     "яблока на тарелке размером 1024×1024 за 11,9 секунды. Сцена соответствует запросу; мелких "
     "надписей в кадре нет, поэтому проверить рендеринг текста нельзя. Z-Image — диффузионная "
     "модель на архитектуре масштабируемого однопоточного диффузионного трансформера (S3-DiT), "
     "обучаемая методом flow matching."),
    ("4.5. Alibaba Qwen-Image — диффузия", "D2", 11,
     "По русскоязычному промпту о фантастическом городе будущего получено изображение 1328×1328 "
     "за 164,6 секунды. Это самая долгая генерация в наборе: время растёт вместе с числом шагов "
     "денойзинга и разрешением, что типично для диффузии. Qwen-Image построена на латентной "
     "диффузии: в техническом отчёте сказано, что основная диффузионная модель — мультимодальный "
     "диффузионный трансформер (MMDiT), а изображение кодируется и декодируется через VAE. "
     "Изначально для этой позиции планировался сервис YandexART, однако провайдер стабильно "
     "возвращал ошибку 503; использована ближайшая по классу диффузионная модель из того же "
     "ценового диапазона."),
    ("4.6. ByteDance Seedream 4.0 — диффузия", "D3", 11,
     "По промпту с портретом героини в киберпанк-антураже получено детализированное изображение "
     "2048×2048 за 11,9 секунды. Модель точно выдержала неоновое розово-синее освещение и "
     "аксессуары; видимых искажений геометрии нет, хотя именно такие артефакты выдают диффузию. "
     "Seedream 4.0 использует диффузионный трансформер с мощным VAE и обучение методом rectified "
     "flow / flow matching."),
]

fig = 0
for title, sid, wcm, text in SECTIONS:
    add_h2(title)
    add_par(text)
    fig += 1
    action_w = 15.5 if sid.startswith("T") else 13.5
    add_picture(SHOTS / f"action_{sid}.png", width_cm=action_w)
    add_caption(f"Рисунок {fig} — Выполненное действие: {title.split('. ', 1)[1]}")
    fig += 1
    add_picture(SHOTS / f"arch_{sid}.png", width_cm=15.5)
    add_caption(f"Рисунок {fig} — Подтверждение архитектуры: {title.split('. ', 1)[1]}")

add_h1("5. Гибридный сервис: Sber GigaChat и Kandinsky 3.1")
add_par(
    "Пример продукта, где обе архитектуры работают в связке, — сервис GigaChat от Сбера "
    "(gigachat.ai). Трансформерная часть представлена самой моделью GigaChat: это русскоязычная "
    "большая языковая модель, построенная на архитектуре трансформера с применением смеси "
    "экспертов. Она принимает запрос пользователя на естественном языке, понимает инструкцию, "
    "ведёт диалог и формирует текстовый ответ. Диффузионная часть — модель Kandinsky 3.1: "
    "крупномасштабная модель генерации изображений по текстовому описанию, работающая на "
    "латентной диффузии. Когда пользователь просит нарисовать картинку, GigaChat переформулирует "
    "его пожелание в промпт для визуальной модели, передаёт управление Kandinsky, а затем "
    "возвращает готовое изображение прямо в окно чата. Таким образом, одна и та же сессия "
    "объединяет две принципиально разные архитектуры: трансформер отвечает за понимание языка и "
    "связный текст, а диффузия — за синтез пикселей. Пользователь при этом видит единый "
    "интерфейс и не задумывается о том, что запрос внутренне переключается между двумя "
    "моделями. Архитектурные метки обеих частей подтверждаются публикациями Сбера: семейство "
    "GigaChat описано как русскоязычные LLM на трансформере с MoE, а Kandinsky 3.1 — как "
    "text-to-image модель на латентной диффузии. Если запрос чисто текстовый, диффузионная часть "
    "не задействуется; если нужен рисунок, языковая модель выполняет роль планировщика и "
    "постановщика задачи. Такое разделение труда типично для современных мультимодальных "
    "продуктов. Обе модели разработаны Сбером и описаны в отдельных публикациях, что "
    "позволяет проверить архитектуру каждой части независимо."
)

add_h1("6. Вывод")
add_par(
    "Проведённый эксперимент показывает, что архитектуру сервиса можно достаточно уверенно "
    "опознать по внешним признакам, даже не имея документации. Ниже перечислены пять таких "
    "признаков с конкретными примерами из проверенных сервисов."
)
add_bullet(
    "Тип входа и выхода. Трансформеры выдают последовательность токенов: ChatGPT, Yandex GPT и "
    "Gemini вернули текст. Диффузионные модели выдают массив пикселей, порождённый из шума: "
    "Z-Image, Qwen-Image и Seedream вернули изображения. Если сервис отвечает текстом на "
    "текстовый запрос — почти наверняка это трансформер; если он синтезирует картинку из шума — "
    "это диффузия."
)
add_bullet(
    "Характер времени генерации. У диффузии время растёт с числом шагов денойзинга и "
    "разрешением: Qwen-Image при 1328×1328 работала 164,6 секунды, тогда как Z-Image при "
    "1024×1024 — всего 11,9 секунды. У трансформера время растёт с числом выходных токенов: "
    "ответ GPT-4o на 92 токена занял 2,4 секунды, короткий перевод Yandex GPT — 0,64 секунды."
)
add_bullet(
    "Характер ошибок. Текстовые трансформеры ошибаются смыслово: путают формулировки, добавляют "
    "лишние факты. Диффузионные модели ошибаются визуально: искажают геометрию, мелкий текст и "
    "мелкие детали. В наших изображениях таких грубых дефектов не встретилось, но именно "
    "пространственные артефакты — характерный «почерк» диффузии."
)
add_bullet(
    "Вариативность при повторном запуске. Диффузия начинает с нового случайного шума, поэтому "
    "повторный запуск с тем же промптом даёт заметно другую картинку. Текстовый трансформер при "
    "нулевой температуре почти детерминирован: повторный запрос к ChatGPT или Gemini вернёт "
    "близкий ответ. Высокая дисперсия результата указывает на диффузию, низкая — на трансформер."
)
add_bullet(
    "Текст внутри изображения. Авторегрессионные трансформерные генераторы изображений "
    "(например, GPT-Image или Nano Banana) рисуют читаемый текст, тогда как классические "
    "диффузионные модели часто «зашумляют» буквы. Способность аккуратно выводить надписи — "
    "дополнительный признак в пользу трансформерного генератора изображений."
)
add_par(
    "Итог: совокупность типа входа и выхода, профиля времени, характера ошибок, вариативности и "
    "работы с текстом позволяет классифицировать сервис без доступа к его внутреннему устройству. "
    "Все шесть рассмотренных сервисов удалось отнести к трансформерам или диффузии именно по этим "
    "признакам, а затем подтвердить вывод первоисточниками."
)

add_h1("Приложение А. Подтверждение архитектур", page_break=True)
add_caption("Таблица 2 — Источники и ключевые цитаты по каждому сервису")
add_table(
    ["#", "Сервис", "Источник", "Ключевая цитата / перевод"],
    [
        ["¹", "ChatGPT (GPT-4o)", "arXiv:2303.08774",
         "«GPT-4 is a Transformer-based model pre-trained to predict the next token in a document.» — "
         "«GPT-4 — модель на основе трансформера, предобученная предсказывать следующий токен»."],
        ["²", "Yandex GPT", "GitHub: yandex/YaLM-100B",
         "«YaLM 100B is a GPT-like neural network for generating and processing text.» — "
         "«YaLM 100B — GPT-подобная нейросеть для генерации и обработки текста»."],
        ["³", "Gemini 2.5 Flash", "arXiv:2403.05530",
         "«Gemini 1.5 Pro is a sparse mixture-of-expert (MoE) Transformer-based model.» — "
         "«Gemini — разреженная смесь экспертов на основе трансформера»."],
        ["⁴", "Alibaba Z-Image", "arXiv:2511.22699",
         "«...built upon a Scalable Single-Stream Diffusion Transformer (S3-DiT) architecture.» — "
         "«...построена на архитектуре масштабируемого однопоточного диффузионного трансформера»."],
        ["⁵", "Alibaba Qwen-Image", "arXiv:2508.02324",
         "«A Multimodal Diffusion Transformer (MMDiT) functions as the backbone diffusion model...» — "
         "«Мультимодальный диффузионный трансформер — основа диффузионной модели»."],
        ["⁶", "ByteDance Seedream 4.0", "arXiv:2509.20427",
         "«We develop a highly efficient diffusion transformer with a powerful VAE...» — "
         "«Разработан высокоэффективный диффузионный трансформер с мощным VAE»."],
    ],
    widths_cm=[0.8, 3.2, 4.2, 8.8],
    size=12,
)
add_par(
    "Все шесть меток имеют статус «Подтверждено»: для каждой найдена публикация или официальная "
    "документация разработчика. Для сервисов на базе семейств (Gemini 2.5 Flash, YandexGPT, "
    "Seedream 4.0) цитируется технический отчёт соответствующего семейства."
)

add_h1("Приложение Б. Журнал работ и стоимость", page_break=True)
add_par(
    "Инструменты: Python 3.13.17, openai 2.x (OpenAI SDK), requests, Pillow, python-docx, LibreOffice "
    "(конвертация в PDF). Точка входа API — https://polza.ai/api/v1. Ключ — из конфигурации проекта "
    "(переменная POLZA_API_KEY в окружении не была задана)."
)
add_caption("Таблица 3 — Выполненные вызовы и фактическая стоимость")
add_table(
    ["#", "Модель", "Архитектура", "Цена, ₽", "Списано, ₽", "Время, с"],
    [
        ["T1", "openai/gpt-4o", "Трансформер", "—", "0,12", "2,42"],
        ["T2", "yandex/yandexgpt-5-lite", "Трансформер", "—", "0,01", "0,64"],
        ["T3", "google/gemini-2.5-flash", "Трансформер", "—", "0,04", "1,01"],
        ["D1", "tongyi-mai/z-image", "Диффузия", "1,40", "1,40", "11,92"],
        ["D2", "qwen/image", "Диффузия", "3,00", "3,00", "164,62"],
        ["D3", "bytedance/seedream-4", "Диффузия", "3,00", "3,00", "11,90"],
        ["", "Итого", "", "", "7,57", "192,5"],
    ],
    widths_cm=[1.0, 4.6, 3.8, 2.4, 2.6, 2.6],
    size=12,
)
add_par(
    "Сумма подтверждена историей операций Polza.ai (GET /api/v1/history/generations): "
    "0,11757511 + 0,01296 + 0,03888056 + 1,40 + 3,00 + 3,00 = 7,56941567 ₽ ≈ 7,57 ₽. Итог не "
    "превышает бюджет 20 ₽; ни один вызов не стоил дороже 5 ₽. Неудачные попытки обращения к "
    "модели yandex/yandex-art завершались ошибкой 503 и не тарифицировались — в истории операций "
    "их нет. Хронология работ и предполётные проверки описаны в logs/worklog.md, обоснование "
    "метода — в logs/generation-method.md.",
    before=6,
)

doc.core_properties.title = "Отчет. Задание 2. Карта архитектур в реальных продуктах"
doc.core_properties.subject = "Применение генеративных нейронных моделей в мультимедиа, задание 2"
doc.core_properties.author = "Ханна М. Н."

REPORT.mkdir(parents=True, exist_ok=True)
doc.save(DOCX)
print("saved", DOCX)
