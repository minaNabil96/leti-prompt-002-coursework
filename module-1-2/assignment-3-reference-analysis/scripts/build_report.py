"""Build Отчет_Задание3.docx (Russian, LETI title page, A4, TNR 14)."""
import json
import pathlib
import re

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
DOCX = REPORT / "Отчет_Задание3.docx"

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


def add_block(text, size=12, left=0.75, before=3, after=6):
    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.JUSTIFY, before, after, 0, 1.0)
    p.paragraph_format.left_indent = Cm(left)
    p.paragraph_format.right_indent = Cm(left)
    r = p.add_run(text)
    fmt_run(r, size)
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
tpar("«Задание 3. Референс → анализ → промпт»", bold=False)
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

# ---------------------------------------------------------------- data
analysis = json.loads((LOGS / "analysis.json").read_text(encoding="utf-8"))
compose = json.loads((LOGS / "compose_call.json").read_text(encoding="utf-8"))
naive = (LOGS / "naive_prompt.txt").read_text(encoding="utf-8").strip()
detailed_raw = (LOGS / "composed_prompt.txt").read_text(encoding="utf-8").strip()
detailed_used = (LOGS / "prompt_used_detailed.txt").read_text(encoding="utf-8").strip()


def plain(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    return text.replace("**", "").strip()


analysis_prompt = analysis["prompt"]
analysis_text = plain(analysis["response"])
compose_prompt = compose["prompt"]
compose_text = plain(compose["response"])

# ---------------------------------------------------------------- body

add_h1("1. Введение")
add_par(
    "Цель работы — проверить на практике конвейер «референс → анализ стиля → промпт → генерация» "
    "и понять, действительно ли предварительный разбор референса мультимодальной моделью повышает "
    "качество переноса стиля по сравнению с коротким промптом. В прикладной работе с генеративными "
    "моделями качество результата определяется не только возможностями генератора, но и точностью "
    "текстового описания: один и тот же сюжет можно сгенерировать в десятках визуальных манер, и "
    "именно промпт задаёт палитру, технику, свет и настроение. Эксперимент построен как честное "
    "сравнение: обе картинки созданы одной моделью, в одном размере и с одним seed, поэтому "
    "единственная переменная — текст промпта. Если развёрнутый промпт, составленный после анализа "
    "референса, воспроизводит стиль заметно точнее наивного, значит этап анализа имеет измеримую "
    "практическую ценность и его стоит включать в производственный процесс."
)

add_h1("2. Референсное изображение")
add_par(
    "В качестве референса выбрана картина Винсента Ван Гога «Звёздная ночь» (The Starry Night), "
    "написанная в 1889 году маслом на холсте; размер полотна — 73,7 × 92,1 см. Картина находится "
    "в постоянной коллекции Музея современного искусства (MoMA) в Нью-Йорке. Изображение получено "
    "с Wikimedia Commons (проект Google Art Project) по адресу "
    "https://commons.wikimedia.org/wiki/File:Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg."
)
add_par(
    "Произведение находится в общественном достоянии: Ван Гог умер в 1890 году, и срок действия "
    "авторских прав истёк не позднее чем через 70 лет после смерти автора, то есть с 1961 года. "
    "Фотографическая репродукция Google Art Project также распространяется как свободный материал, "
    "поэтому использование изображения в учебной работе не нарушает прав."
)
add_par(
    "Выбор обусловлен силой и узнаваемостью стиля. «Звёздная ночь» соединяет несколько легко "
    "проверяемых признаков: закрученные спиральные мазки, плотное импасто, доминирующую "
    "кобальтово-синюю палитру с кадмиево-жёлтыми и кремовыми акцентами, светящиеся луну и звёзды "
    "с ореолами, силуэт кипариса на переднем плане и контраст бурного неба со спящей деревней. "
    "Эти признаки достаточно конкретны, чтобы их можно было описать словами, и достаточно "
    "выразительны, чтобы короткий промпт их гарантированно потерял. Поэтому сравнение получается "
    "наглядным."
)
add_picture(SHOTS / "01_reference.png", width_cm=14)
add_caption("Рисунок 1 — Референсное изображение: В. Ван Гог, «Звёздная ночь» (1889)")

add_h1("3. Анализ стиля и составление промпта")
add_h2("3.1. Анализ стиля мультимодальной моделью")
add_par(
    "Для анализа использована модель google/gemini-2.5-flash — мультимодальный трансформер с "
    "разреженной смесью экспертов; согласно техническому отчёту Gemini 1.5 (arXiv:2403.05530), "
    "это MoE-трансформер, принимающий на вход текст и изображение. В одном запросе модели переданы "
    "репродукция картины (1024 × 811 px) и инструкция разобрать пять аспектов: композицию, "
    "цветовую палитру, освещение, технику и стиль, настроение. Ответ получен за 6,4 секунды, "
    "израсходовано 1013 токенов."
)
add_par(
    "Ключевые наблюдения модели совпали с визуальным впечатлением. Композиция разделена на две "
    "части — динамичное небо и спокойный пейзаж внизу, а кипарис слева работает вертикальной осью, "
    "связывающей землю и небо. В палитре названы насыщенные синие и зелёные оттенки, "
    "контрастирующие с жёлтыми и оранжевыми акцентами звёзд и луны. Источниками света модель "
    "назвала звёзды, лунный полумесяц и огоньки в окнах, отметив неравномерность освещения. "
    "Техника описана как толстые энергичные мазки импасто с вихревыми линиями в небе и более "
    "короткими — внизу. Настроение охарактеризовано как одновременно тревожное и возвышенное, "
    "меланхоличное и энергичное."
)
add_picture(SHOTS / "02_dialog_analysis.png", width_cm=14)
add_caption("Рисунок 2 — Диалог: анализ стиля референса")

add_h2("3.2. Составленный промпт")
add_par(
    "Вторым запросом, продолжающим тот же диалог, модель попросили составить подробный промпт для "
    "генератора изображений на новый сюжет «кот под дождём» в стиле референса. В инструкции "
    "заданы ограничения: английский язык, 4–6 предложений, обязательное описание палитры, типа "
    "мазка, освещения, композиции и атмосферы, запрет упоминать имя художника и копировать "
    "картину. Модель вернула связный текст объёмом около 120 слов; на вызов ушло 2,8 секунды и "
    "1186 токенов."
)
add_par(
    "Составленный промпт (текст, переданный генератору, приведён полностью):"
)
add_block(detailed_used, size=12)
add_picture(SHOTS / "03_dialog_prompt.png", width_cm=14)
add_caption("Рисунок 3 — Диалог: составленный подробный промпт")
add_par(
    "Перед отправкой генератору из ответа удалена разговорная обёртка и markdown-разметка; "
    "английский текст промпта не изменялся. Исходный ответ модели сохранён в журнале и приведён "
    "в Приложении А."
)

add_h1("4. Сравнение генераций")
add_h2("4.1. Две генерации")
add_par(
    "Обе картинки созданы моделью bytedance/seedream-4 — диффузионной моделью на архитектуре "
    "rectified flow DiT (ByteDance Seedream 4.0). Условия одинаковы: соотношение сторон 1:1, "
    "разрешение 1K, seed 42; фактический размер файлов на выходе — 2048 × 2048 px. Генерация по "
    "подробному промпту заняла 11,7 секунды, по наивному — 9,8 секунды; каждая стоила 3,00 ₽. "
    "Единственное различие между вызовами — текст промпта, поэтому разницу в результате можно "
    "отнести именно к нему."
)
add_par(
    "Генерация 1 изображает чёрного кота под большим тёмным зонтом в потоке дождя. Небо "
    "закручено спиралями, выполнено в глубоких синих и зелёных тонах с мощным жёлто-оранжевым "
    "свечением, которое отражается в мокрой земле. На заднем плане читается деревня, фактура "
    "краски рельефная, мазки длинные и пастозные. Визуально это узнаваемая живопись "
    "постимпрессионизма, а не фотография."
)
add_picture(SHOTS / "04_gen_detailed.png", width_cm=13.5)
add_caption("Рисунок 4 — Генерация 1: по подробному промпту")

add_par(
    "Генерация 2 по промпту «A cat in the rain» дала фотореалистичную сцену: мокрый полосатый "
    "котёнок сидит под скамейкой на брусчатке, рядом лужи и размытые прохожие с зонтами. Кадр "
    "технически аккуратный, но нейтральный по стилю: серо-голубая палитра, мягкий пасмурный свет, "
    "оптическое размытие фона. Живописных мазков, свечения и вихревой композиции нет."
)
add_picture(SHOTS / "05_gen_naive.png", width_cm=13.5)
add_caption("Рисунок 5 — Генерация 2: по наивному промпту")

add_picture(SHOTS / "06_comparison_collage.png", width_cm=16.5)
add_caption("Рисунок 6 — Сравнительный коллаж: референс | генерация 1 | генерация 2")

add_h2("4.2. Таблица сравнения")
add_caption("Таблица 1 — Сравнение признаков стиля в референсе и двух генерациях", keep_next=True)
add_table(
    ["Признак стиля", "Есть в референсе", "Воспроизведён в генерации 1", "Воспроизведён в генерации 2"],
    [
        [
            "Цветовая палитра: кобальтово-синий, кадмиево-жёлтый, кремовый, зелёные полутона",
            "Да: синий доминирует, жёлтый и кремовый образуют звёзды и ореолы, зелёный — в кипарисе и переходах неба",
            "Да: доминируют глубокие синие и зелёные тона, ярко звучат жёлтые и оранжевые блики на небе и в отражениях",
            "Нет: палитра фотореалистичная и приглушённая — серо-голубой асфальт, бежевый кот, серый дождь",
        ],
        [
            "Освещение: ночная сцена, светящиеся луна и звёзды с ореолами, контраст света и полумрака",
            "Да: луна и звёзды — главные источники света, вокруг них концентрические ореолы, деревня в полумраке",
            "Частично: есть мощное свечение жёлтого неба и его отражение, но нет ночи, луны и звёзд — сцена закатная",
            "Нет: ровный пасмурный дневной свет, мягкие тени, свечения и ореолов нет",
        ],
        [
            "Композиция: закрученное небо на верхние две трети, вертикальный силуэт на переднем плане, деревня внизу",
            "Да: вихревое небо доминирует, кипарис слева задаёт вертикальную ось, деревня занимает нижнюю треть",
            "Частично: вихри в верхней половине, кот и зонт на переднем плане, вдали деревня; но вертикальная ось заменена зонтом",
            "Частично: кот на переднем плане и городской фон есть, но небо нейтральное, вихревой структуры нет",
        ],
        [
            "Техника: густое импасто, длинные закрученные мазки, видимая фактура краски",
            "Да: полотно построено из плотных рельефных мазков, в небе спиральные и волнистые линии",
            "Да: фактура импасто выражена отчётливо — рельефные мазки, спирали в зонте и на воде",
            "Нет: изображение фотографическое, мазков и фактуры краски нет",
        ],
        [
            "Настроение: тревожно-возвышенное, мечтательное, меланхоличное, но вибрирующее энергией",
            "Да: бурное небо и спящая деревня дают контраст беспокойства и покоя",
            "Да: драматичное свечение, вихри и одинокий чёрный кот создают то же сочетание тревоги и энергии",
            "Частично: дождь и мокрый кот передают меланхолию, но нет тревожной динамики и энергии цвета",
        ],
    ],
    widths_cm=[3.2, 4.2, 4.8, 4.8],
    size=11,
)

add_h1("5. Оценка точности переноса стиля и неточности анализа")
add_h2("5.1. Оценка точности (1–5)")
add_par(
    "Точность переноса стиля оценена по пяти признакам из таблицы 1. Генерация 1 получает 4 из 5. "
    "Палитра, импасто, вихревая динамика неба и общее настроение воспроизведены узнаваемо: "
    "изображение сразу читается как живопись в манере постимпрессионизма, а не как фотография. "
    "Балл снят за освещение и композицию: модель сделала сцену закатной, а не ночной, и не "
    "перенесла вертикальный акцент кипариса, заменив его горизонтальным зонтом. Иными словами, "
    "стиль передан сильно, но не буквально по всем пяти признакам."
)
add_par(
    "Генерация 2 получает 1 из 5. Короткий промпт «A cat in the rain» дал качественную "
    "фотореалистичную иллюстрацию, которая не имеет отношения к стилю референса: отсутствуют "
    "палитра, мазок, свечение и вихревая композиция, совпадает только сюжет. Разница между "
    "оценками — 3 балла — и есть измеримый вклад этапа анализа референса: при одной и той же "
    "модели, размере и seed только текст промпта изменил результат с фотореализма на живописный "
    "постимпрессионизм."
)
add_h2("5.2. Неточности модели-аналитика")
add_par(
    "Анализ в целом верен, но три формулировки требуют ручной правки перед использованием в "
    "промпте."
)
add_bullet(
    "Палитра описана слишком широко: модель назвала основными цветами «насыщенные синие и "
    "глубокие зелёные», а акцентами — «яркие жёлтые и оранжевые». В референсе оранжевого почти "
    "нет, зелёный не является вторым основным цветом, а светлые участки — это кремово-белые и "
    "бледно-лимонные ореолы. Ручная правка: «dominant cobalt and ultramarine blue (about two "
    "thirds of the canvas), pale lemon-yellow and cream halos, muted green only in the cypress "
    "and sky transitions, no orange».",
    marker="1.",
)
add_bullet(
    "Не описана техника ореолов. Аналитик верно указал вихревые мазки в небе, но не отметил, что "
    "свет звёзд и луны построен из концентрических колец коротких дугообразных мазков. Без этого "
    "генератор передаёт свечение градиентом, а не живописной фактурой. Ручная правка: добавить "
    "«each star and the moon is surrounded by concentric rings of short curved strokes».",
    marker="2.",
)
add_bullet(
    "Разрыв между анализом и промптом. В анализе кипарис назван главной вертикальной осью "
    "композиции, но в составленный промпт это наблюдение не попало — генерация 1 осталась без "
    "вертикального силуэта. Ручная правка: добавить «a dark vertical silhouette (tree or "
    "lamppost) anchoring the left foreground, connecting ground and sky».",
    marker="3.",
)
add_par(
    "После этих правок промпт стал бы точнее по палитре и фактуре, а композиция — ближе к "
    "референсу. Показательно, что модель хорошо описывает общее впечатление, но теряет конкретику "
    "при переносе наблюдений в инструкцию для генератора: именно этот разрыв и приходится "
    "закрывать вручную."
)

add_h1("6. Применение в сфере связи с общественностью")
add_par(
    "В работе PR-специалиста визуальный контент нужен постоянно и в едином стиле: посты, афиши, "
    "баннеры, иллюстрации к пресс-релизам, слайды презентаций. Приём «референс → анализ → промпт» "
    "экономит время именно там, где важна серийность и узнаваемость."
)
add_bullet(
    "Серия визуалов для соцсетей университета в едином стиле. Один раз разобранный референс "
    "(фирменная айдентика, удачное фото с мероприятия) превращается в промпт, по которому "
    "генерируется серия из 10–15 постов без ручного подбора фильтров. Вместо часов в графическом "
    "редакторе — один анализ и шаблон промпта, который повторяется с заменой сюжета."
)
add_bullet(
    "Баннеры и афиши мероприятий. Приём позволяет быстро перенести стиль утверждённого макета на "
    "новые форматы и сюжеты, сохраняя палитру и графику кампании. Согласование проходит быстрее, "
    "потому что первый вариант уже близок к фирменному стилю, а не является «рыбой»."
)
add_bullet(
    "Иллюстрации для пресс-релизов и лонгридов. Анализ редакционного референса даёт промпт, "
    "который держит визуальный тон публикации серийно. Это дешевле заказной иллюстрации и быстрее "
    "согласования со стоковым фото, а стиль остаётся узнаваемым от материала к материалу."
)
add_bullet(
    "Прототипирование концепций для презентаций и питч-деков. На этапе идеи важна скорость: "
    "разбор двух-трёх референсов и генерация вариантов за минуты позволяют показать заказчику "
    "визуальные направления до старта дизайна. Правки обсуждаются на уровне промпта, а не "
    "перерисовки макетов."
)
add_par(
    "Во всех четырёх сценариях ценность даёт не сама генерация, а этап анализа: он превращает "
    "субъективное «хочу похоже» в проверяемый список признаков — палитра, свет, композиция, "
    "техника, настроение. Этот список можно согласовать с заказчиком, сохранить как шаблон и "
    "переиспользовать, что снижает число итераций и риск переделок."
)

# ---------------------------------------------------------------- appendices

add_h1("Приложение А. Промпты и ответы моделей", page_break=True)
add_par("А.1. Промпт анализа стиля (передан вместе с изображением):", bold=True, indent=0)
add_block(analysis_prompt, size=12)
add_par("А.2. Полный ответ модели на запрос анализа:", bold=True, indent=0, before=6)
add_block(analysis_text, size=12)
add_par("А.3. Промпт составления подробного промпта:", bold=True, indent=0, before=6)
add_block(compose_prompt, size=12)
add_par("А.4. Полный ответ модели с составленным промптом:", bold=True, indent=0, before=6)
add_block(compose_text, size=12)
add_par("А.5. Наивный промпт (генерация 2):", bold=True, indent=0, before=6)
add_block(naive, size=12)
add_par(
    "Примечание: в Приложении А текст ответов приведён без служебной Markdown-разметки "
    "(звёздочек выделения); слова и порядок предложений не изменены. Полные ответы в исходном "
    "виде сохранены в logs/analysis.json и logs/compose_call.json.",
    size=12, italic=True, before=6,
)

add_h1("Приложение Б. Журнал работ и стоимость", page_break=True)
add_par(
    "Инструменты: Python 3.13, OpenAI SDK (openai 2.x), requests, Pillow, python-docx, "
    "LibreOffice (конвертация в PDF). Точка входа API — https://polza.ai/api/v1. Ключ взят из "
    "конфигурации проекта, поскольку переменная POLZA_API_KEY в окружении не была задана. "
    "Генерация изображений выполнена через Media API (POST /api/v1/media с опросом "
    "GET /api/v1/media/{id}), поскольку этот путь поддерживает параметр seed и разрешение "
    "для seedream-4."
)
add_par(
    "Хронология (09.11.2026, MSK): 21:50 — предполётные проверки, каталог моделей и баланс; "
    "21:52 — загрузка и подготовка референса; 21:59 — анализ стиля; 22:00 — составление промпта; "
    "22:00 — генерация 1 и генерация 2; 22:02 — сборка скриншотов; 22:05 — сравнение и оценки; "
    "22:10 — сборка отчёта и PDF. Подробный журнал — logs/worklog.md."
)
add_caption("Таблица 2 — Выполненные вызовы и фактическая стоимость", keep_next=True)
add_table(
    ["№", "Вызов", "Модель", "Архитектура", "Токены / единицы", "Списано, ₽"],
    [
        ["1", "Анализ стиля (vision)", "google/gemini-2.5-flash", "Трансформер (MoE)", "1013", "0,19"],
        ["2", "Составление промпта", "google/gemini-2.5-flash", "Трансформер (MoE)", "1186", "0,09"],
        ["3", "Генерация 1 (подробный промпт)", "bytedance/seedream-4", "Диффузия (DiT)", "1 изображение", "3,00"],
        ["4", "Генерация 2 (наивный промпт)", "bytedance/seedream-4", "Диффузия (DiT)", "1 изображение", "3,00"],
        ["", "Итого", "", "", "", "6,29"],
    ],
    widths_cm=[0.8, 3.9, 4.3, 2.9, 2.9, 2.2],
    size=11,
)
add_par(
    "Сумма подтверждена историей операций Polza.ai (GET /api/v1/history/generations): "
    "0,194432 + 0,092074 + 3,00 + 3,00 = 6,286506 ₽ ≈ 6,29 ₽. Итог не превышает бюджет 15 ₽; "
    "максимальный вызов стоил 3,00 ₽, то есть ниже порога 5 ₽, поэтому прерывание не "
    "потребовалось. Замены моделей не было: обе заявленные модели доступны и отработали штатно. "
    "Обе генерации выполнены одной моделью, в одном размере и с одним seed 42; фактический размер "
    "изображений — 2048 × 2048 px. Обоснование метода, идентификаторы запросов и параметры "
    "сохранены в logs/generation-method.md и logs/cost.md.",
    before=6,
)

doc.core_properties.title = "Отчет. Задание 3. Референс → анализ → промпт"
doc.core_properties.subject = "Применение генеративных нейронных моделей в мультимедиа, задание 3"
doc.core_properties.author = "Ханна М. Н."

REPORT.mkdir(parents=True, exist_ok=True)
doc.save(DOCX)
print("saved", DOCX)
