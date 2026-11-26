"""Build Отчет_Задание1.docx (Russian, LETI title page, A4, TNR 14)."""
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
COLLAGE = ROOT / "collage"
DOCX = REPORT / "Отчет_Задание1.docx"

TNR = "Times New Roman"

TBLPR_ORDER = [
    "tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
    "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd",
    "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook",
    "tblCaption", "tblDescription",
]


def put_tblpr(tblPr, el):
    """Insert a tblPr child at the schema-correct position."""
    tag = el.tag.split("}")[1]
    idx = TBLPR_ORDER.index(tag)
    for child in list(tblPr):
        ctag = child.tag.split("}")[1]
        if ctag in TBLPR_ORDER and TBLPR_ORDER.index(ctag) > idx:
            child.addprevious(el)
            return
    tblPr.append(el)


# ---------------------------------------------------------------- helpers

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


def add_h1(text):
    p = doc.add_paragraph(style="Heading 1")
    set_par(p, WD_ALIGN_PARAGRAPH.CENTER, 12, 8, 0, 1.0, keep_next=True)
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

# Normal style: TNR 14 everywhere
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

# Heading styles: TNR, black
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
tpar("«Задание 1. Сравнение генерации изображения на основе", bold=False)
tpar("трансформера и диффузии»", bold=False)
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
    ("Студент гр. ___", "", "Ханна М. Н."),
    ("Преподаватель ___", "", "___"),
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

# update fields on open (PAGE numbers)
settings = doc.settings.element
uf = OxmlElement("w:updateFields")
uf.set(qn("w:val"), "true")
settings.append(uf)

# ---------------------------------------------------------------- body

add_h1("1. Введение")
add_par(
    "В настоящей работе сравниваются две архитектуры генерации изображений по текстовому "
    "описанию: авторегрессионные трансформеры и диффузионные модели. В качестве представителей "
    "первой группы выбраны Google Gemini 2.5 Flash Image (Nano Banana 1) и OpenAI GPT-Image 1.5, "
    "второй — Alibaba Z-Image и ByteDance Seedream 4.0. Цель работы — проверить, как архитектура "
    "влияет на точность следования промпту, качество рендеринга текста, цветопередачу и характер "
    "артефактов. Актуальность обусловлена практическим выбором модели для рекламных макетов, "
    "инфографики и предметной визуализации, где важны не «красивость», а проверяемые параметры: "
    "количество объектов, их цвет, взаимное расположение и читаемая надпись. Исследование "
    "ограничено четырьмя моделями, одним промптом и одним изображением на модель; оценка "
    "проводилась визуально по чек-листу из 13 бинарных пунктов. Дополнительно фиксируются время "
    "генерации и фактическая стоимость каждого запроса — это позволяет судить о практической "
    "применимости модели. Такой дизайн не претендует на "
    "статистическую значимость, но даёт воспроизводимый срез поведения архитектур на задаче с "
    "жёсткими ограничениями."
)

add_h1("2. Использованный промпт и обоснование выбора")
add_par(
    "Промпт составлен на английском языке, поскольку все четыре модели лучше следуют "
    "англоязычным инструкциям. Он дословно одинаков для всех генераций:"
)
add_par(
    "A clean product-style still life on a light oak table: exactly three yellow lemons arranged "
    "in a row on the left, exactly two blue ceramic cups standing side by side to the right of the "
    "lemons, and a small wooden sign behind the cups with the black capital letters \"LETI 2026\". "
    "Soft daylight from the left, plain pale-grey background, sharp focus, no other objects.",
    size=12, italic=True, indent=0
)
add_par("Перевод на русский язык:")
add_par(
    "Аккуратный предметный натюрморт на светлом дубовом столе: ровно три жёлтых лимона в ряд "
    "слева, ровно две синие керамические чашки рядом друг с другом справа от лимонов и небольшая "
    "деревянная табличка позади чашек с чёрными заглавными буквами «LETI 2026». Мягкий дневной "
    "свет слева, однотонный бледно-серый фон, резкий фокус, никаких других объектов.",
    size=12, italic=True, indent=0
)
add_par("Промпт содержит следующие проверяемые элементы:")
add_bullet("объект 1 — три жёлтых лимона, расположенные слева;")
add_bullet("объект 2 — две синие керамические чашки, стоящие справа от лимонов;")
add_bullet("объект 3 — одна деревянная табличка позади чашек;")
add_bullet("надпись «LETI 2026» чёрными заглавными буквами;")
add_bullet("взаимное расположение: лимоны слева → чашки справа → табличка сзади.")
add_par(
    "Такая схема позволяет проверять каждый пункт бинарно, без субъективных оценок «красиво / "
    "некрасиво». Количество задано для всех трёх объектов, поэтому модель не может «угадать» "
    "число предметов. Цвета названы явно, что отделяет ошибку цветопередачи от стилистического "
    "решения. Короткая надпись проверяет точность рендеринга текста — традиционно слабое место "
    "генеративных моделей. Сцена намеренно выбрана бытовой, без фантазийных существ и сложного "
    "света, чтобы снизить влияние стилевых предпочтений модели и оставить только проверяемые "
    "параметры. Один и тот же промпт дословно передаётся всем четырём моделям, что обеспечивает "
    "корректность сравнения архитектур."
)

add_h1("3. Использованные модели и сервис")
add_par(
    "Сервис генерации — Polza.ai (https://polza.ai), OpenAI-совместимый API, ключ pza_…. Цены "
    "указаны по каталогу polza.ai/collections/image на 06.11.2026. Все четыре модели найдены в "
    "каталоге и отработали без замен; архитектурные метки взяты из первичных источников и "
    "приведены в таблице 1."
)
add_caption("Таблица 1 — Использованные модели и основание классификации")
add_table(
    ["Модель", "Архитектура", "Сервис / ID модели", "Основание классификации"],
    [
        ["Google Gemini 2.5 Flash Image (Nano Banana 1)", "Трансформер",
         "Polza.ai / google/gemini-2.5-flash-image",
         "Google AI Studio docs: \"Nano Banana is the name for Gemini's native image generation "
         "capabilities\" — generates ~1,290 image tokens autoregressively inside the LLM token "
         "stream; not a diffusion model."],
        ["OpenAI GPT-Image 1.5", "Трансформер",
         "Polza.ai / openai/gpt-image-1.5",
         "OpenAI docs + multiple technical analyses: gpt-image-1/1.5/2 are autoregressive "
         "token-by-token image generators (like ChatGPT text), explicitly NOT diffusion. OpenAI "
         "deprecated DALL·E 3 (which was diffusion) in favor of this autoregressive family."],
        ["Alibaba Z-Image", "Диффузия",
         "Polza.ai / tongyi-mai/z-image",
         "Z-Image arXiv paper (2511.22699) describes it as \"a powerful diffusion transformer "
         "model\"; architecture = Scalable Single-Stream Diffusion Transformer, trained with "
         "rectified flow matching."],
        ["ByteDance Seedream 4.0", "Диффузия",
         "Polza.ai / bytedance/seedream-4",
         "ByteDance Seed technical report: Seedream is a rectified-flow / flow-matching diffusion "
         "model."],
    ],
    [3.0, 2.8, 4.0, 7.2], size=12,
)

add_h1("4. Результаты генерации")
add_par(
    "Все изображения получены по одному и тому же промпту. Запрошенный размер — 1024×1024; "
    "фактический выход GPT-Image 1.5 составил 1254×1254, Seedream 4.0 — 2048×2048 (провайдер "
    "масштабирует результат, тарификация остаётся по запрошенному уровню). На скриншотах ниже "
    "видны название модели, архитектура, ID в Polza.ai и полный текст промпта."
)

figures = [
    ("gemini-2.5-flash-image", "4.1. Google Gemini 2.5 Flash Image (Nano Banana 1) — трансформер",
     "Рисунок 1 — Модель Google Gemini 2.5 Flash Image, архитектура «трансформер»",
     "Модель точно воспроизвела количество и цвет объектов, а также надпись «LETI 2026», однако "
     "разместила табличку между лимонами и чашками, а не позади чашек, и разбила надпись на две "
     "строки. Балл соответствия — 4,6."),
    ("gpt-image-1.5", "4.2. OpenAI GPT-Image 1.5 — трансформер",
     "Рисунок 2 — Модель OpenAI GPT-Image 1.5, архитектура «трансформер»",
     "Все 13 пунктов чек-листа выполнены: три лимона, две синие чашки, табличка позади них и "
     "точная надпись одной строкой. Балл соответствия — 5,0; замечания касаются масштаба таблички "
     "и отсутствия видимой опоры."),
    ("z-image", "4.3. Alibaba Z-Image — диффузия",
     "Рисунок 3 — Модель Alibaba Z-Image, архитектура «диффузия»",
     "Сцена полностью соответствует промпту, включая позицию таблички и точную надпись. "
     "Артефакты локальны: прямоугольные блики на кромках чашек и зелёная линия на левой чашке. "
     "Балл соответствия — 5,0."),
    ("seedream-4", "4.4. ByteDance Seedream 4.0 — диффузия",
     "Рисунок 4 — Модель ByteDance Seedream 4.0, архитектура «диффузия»",
     "Все элементы промпта выполнены; изображение самое детальное по фактуре. Заметны тёмная "
     "стойка-опора за правой чашкой, шов текстуры под надписью и несогласованность освещения "
     "чашек. Балл соответствия — 5,0."),
]
for short, head, caption, note in figures:
    add_h2(head)
    add_picture(SHOTS / f"screenshot_{short}.png", 14)
    add_caption(caption)
    add_par(note)

add_h1("5. Сравнительный анализ")
add_par(
    "На рисунке 5 четыре результата сведены рядом в едином масштабе. В таблице 2 — обязательная "
    "сравнительная таблица с баллами и выявленными артефактами."
)
add_picture(COLLAGE / "collage.png", 16)
add_caption("Рисунок 5 — Сравнительный коллаж четырёх результатов")
doc.add_page_break()
add_caption("Таблица 2 — Сравнение моделей по архитектуре, соответствию промпту и артефактам")

basis = {
    "gemini": "Google AI Studio docs: \"Nano Banana is the name for Gemini's native image generation "
              "capabilities\" — generates ~1,290 image tokens autoregressively inside the LLM token "
              "stream; not a diffusion model.",
    "gpt": "OpenAI docs + multiple technical analyses: gpt-image-1/1.5/2 are autoregressive "
           "token-by-token image generators (like ChatGPT text), explicitly NOT diffusion. OpenAI "
           "deprecated DALL·E 3 (which was diffusion) in favor of this autoregressive family.",
    "z": "Z-Image arXiv paper (2511.22699) describes it as \"a powerful diffusion transformer model\"; "
         "architecture = Scalable Single-Stream Diffusion Transformer, trained with rectified flow "
         "matching.",
    "seed": "ByteDance Seed technical report: Seedream is a rectified-flow / flow-matching diffusion "
            "model.",
}
add_table(
    ["Модель", "Архитектура", "Основание вывода", "Соответствие промпту (1–5)", "Выявленные артефакты"],
    [
        ["Google Gemini 2.5 Flash Image (Nano Banana 1)", "Трансформер", basis["gemini"], "4,6",
         "Табличка между лимонами и чашками, а не позади чашек; надпись разбита на две строки; "
         "размытые кромки чашек; восковая поверхность лимонов; отсутствие контактной тени под "
         "табличкой."],
        ["OpenAI GPT-Image 1.5", "Трансформер", basis["gpt"], "5,0",
         "Табличка непропорционально крупная и без видимой опоры; ручка левой чашки почти "
         "смыкается с правой чашкой; яркий блик на третьем лимоне."],
        ["Alibaba Z-Image", "Диффузия", basis["z"], "5,0",
         "Прямоугольные белые блики на кромках чашек; зелёная линия на левой чашке; металлические "
         "плодоножки; правая чашка обрезает край таблички."],
        ["ByteDance Seedream 4.0", "Диффузия", basis["seed"], "5,0",
         "Тёмная стойка-опора за правой чашкой; шов текстуры под надписью; тёмное пятно на левой "
         "чашке; несогласованное освещение чашек."],
    ],
    [2.8, 2.8, 4.8, 2.8, 3.8], size=12,
)

add_h1("6. Вывод")
add_par(
    "Систематические различия проявились не в количестве объектов и не в цвете — эти параметры "
    "все четыре модели выполнили одинаково, — а в способе обращения с композицией и текстом. "
    "Трансформеры (Gemini, GPT-Image) работают с изображением как с последовательностью "
    "семантических токенов: они точно держат надпись и общий смысл сцены, но могут "
    "перекомпоновать её (Gemini перенёс надпись на две строки и поставил табличку между "
    "объектами) и упростить материальность. Диффузионные модели (Z-Image, Seedream) оптимизируют "
    "пиксельное правдоподобие: они дают более фактурные лимоны и глазурь, но именно в местах "
    "контакта объектов появляются локальные геометрические и световые артефакты — блики-"
    "«штрих-коды», лишние стойки, несогласованные отражения. По точности следования промпту "
    "различия оказались небольшими: 4,6 у Gemini против 5,0 у остальных; по фотореалистичности "
    "диффузионные модели выигрывают, по типографике и управляемости раскладкой — трансформеры."
)
add_par(
    "Для генерации рекламного постера с длинным читаемым текстом и точной иерархией выбираем "
    "GPT-Image 1.5: он единственный воспроизвёл надпись одной строкой с ровными интервалами и не "
    "допустил смысловых сдвигов. Для предметной съёмки и карточек товара на маркетплейсе, где "
    "важны фактура кожицы, глазури и реалистичный свет, лучше подходят Z-Image или Seedream 4.0; "
    "Z-Image дешевле (1,4 ₽) и быстрее (9,4 с), Seedream даёт более высокое разрешение "
    "(2048×2048). Для быстрых концепт-листов и раскадровок с большим числом вариантов и жёстким "
    "набором объектов выбираем Gemini 2.5 Flash Image: он дешёвый, быстрый и семантически точный, "
    "но требует проверки раскладки — в нашем тесте он единственный нарушил позицию объекта. Для "
    "инфографики со стрелками, подписями и строгой сеткой разумно использовать GPT-Image 1.5, а "
    "для художественных иллюстраций с мягким светом — диффузионные Seedream или Z-Image. Таким "
    "образом, выбор определяется не «лучшей моделью вообще», а приоритетом: текст и управляемая "
    "композиция — трансформеры, фотореализм и фактура — диффузия."
)

# ---------------------------------------------------------------- appendix A

doc.add_page_break()
add_h1("Приложение А")
add_par(
    "Полный чек-лист соответствия промпту (сырые ответы «да / нет»). Балл рассчитан по формуле "
    "(число «да» / 13) × 5 с округлением до 0,1."
)
add_caption("Таблица 3 — Поэлементная проверка соответствия промпту")
check_rows = [
    ["1", "Объект 1 (лимоны) присутствует", "Да", "Да", "Да", "Да"],
    ["2", "Объект 2 (чашки) присутствует", "Да", "Да", "Да", "Да"],
    ["3", "Объект 3 (табличка) присутствует", "Да", "Да", "Да", "Да"],
    ["4", "Количество лимонов = 3", "Да", "Да", "Да", "Да"],
    ["5", "Количество чашек = 2", "Да", "Да", "Да", "Да"],
    ["6", "Количество табличек = 1", "Да", "Да", "Да", "Да"],
    ["7", "Цвет лимонов — жёлтый", "Да", "Да", "Да", "Да"],
    ["8", "Цвет чашек — синий", "Да", "Да", "Да", "Да"],
    ["9", "Материал/цвет таблички — дерево", "Да", "Да", "Да", "Да"],
    ["10", "Расположение: лимоны слева, чашки справа, табличка позади чашек", "Нет", "Да", "Да", "Да"],
    ["11", "Надпись присутствует", "Да", "Да", "Да", "Да"],
    ["12", "Надпись читается", "Да", "Да", "Да", "Да"],
    ["13", "Надпись точно «LETI 2026»", "Да", "Да", "Да", "Да"],
    ["", "Итого «да»", "12/13", "13/13", "13/13", "13/13"],
    ["", "Балл", "4,6", "5,0", "5,0", "5,0"],
]
add_table(
    ["№", "Проверяемый элемент", "Gemini 2.5", "GPT-Image 1.5", "Z-Image", "Seedream 4.0"],
    check_rows, [1.2, 4.8, 2.75, 2.75, 2.75, 2.75], size=12,
)

# ---------------------------------------------------------------- appendix B

doc.add_page_break()
add_h1("Приложение Б")
add_par(
    "Журнал работ и стоимость. Инструменты: Python 3.13.17, Pillow 13.0.0, python-docx 1.2.0, "
    "requests 2.34.2, openai 3.46.0, PyMuPDF 2.0, LibreOffice 26.8.2.2; ОС Windows. Генерация "
    "выполнена через Media API Polza.ai (POST /api/v1/media) с параметром aspect_ratio = 1:1; "
    "ключ pza_… проверен запросом GET /api/v1/models (HTTP 200)."
)
add_par("Ключевые команды:")
add_bullet("python scripts/generate.py — четыре генерации по одному промпту;")
add_bullet("python scripts/build_assets.py — скриншоты и коллаж;")
add_bullet("python scripts/build_report.py — сборка отчёта .docx;")
add_bullet("soffice --headless --convert-to pdf --outdir report report/Отчет_Задание1.docx;")
add_bullet("python scripts/check_report.py — проверка docx/pdf и рендер страниц.")
add_caption("Таблица 4 — Стоимость и время генерации")
add_table(
    ["Модель", "Архитектура", "Цена по каталогу (₽)", "Списано (₽)", "Время (с)"],
    [
        ["Google Gemini 2.5 Flash Image", "Трансформер", "2,90", "2,90", "11,66"],
        ["OpenAI GPT-Image 1.5", "Трансформер", "3,00", "3,00", "54,30"],
        ["Alibaba Z-Image", "Диффузия", "1,40", "1,40", "9,40"],
        ["ByteDance Seedream 4.0", "Диффузия", "3,00", "3,00", "12,55"],
        ["Итого", "—", "10,30", "10,30", "87,91"],
    ],
    [5.2, 3.0, 3.0, 2.9, 2.9], size=12,
)
add_par(
    "Бюджет 11 ₽ соблюдён: фактические списания по данным usage.cost_rub и истории Polza.ai "
    "составили 10,30 ₽. Ни одна генерация не превысила 4 ₽; превышения счёта над каталогом нет "
    "(коэффициент 1,00). Неудачные пробные запросы к OpenAI-совместимому эндпоинту завершились "
    "HTTP 400 до генерации и не тарифицировались."
)
add_caption("Таблица 5 — Журнал выполнения")
add_table(
    ["Время (MSK)", "Событие"],
    [
        ["05.11.2026 21:52", "Создана структура проекта; начаты предполётные проверки."],
        ["05.11.2026 21:53", "Проверены Python 3.13.17, Pillow, python-docx, requests; установлен openai 3.46.0. "
                              "GET /api/v1/models → HTTP 200; все четыре ID найдены в каталоге."],
        ["05.11.2026 21:54", "Z-Image: 1,40 ₽, 9,4 с, 1024×1024. Gemini 2.5 Flash Image: 2,90 ₽, 11,66 с, 1024×1024."],
        ["05.11.2026 21:55", "GPT-Image 1.5: 3,00 ₽, 54,3 с, 1254×1254. Seedream 4.0: 3,00 ₽, 12,55 с, 2048×2048."],
        ["05.11.2026 21:56", "Визуальный анализ, кропы ключевых зон, заполнение чек-листа."],
        ["05.11.2026 22:00", "Собраны четыре скриншота и коллаж; проверена кириллица."],
        ["05.11.2026 22:05", "Собран отчёт .docx, выполнена конвертация в PDF и самопроверка."],
    ],
    [4.2, 12.8], size=12,
)

# core properties
doc.core_properties.title = "Сравнение генерации изображения на основе трансформера и диффузии"
doc.core_properties.author = "Ханна М. Н."
doc.core_properties.subject = "Применение генеративных нейронных моделей в мультимедиа, задание 1"
doc.core_properties.language = "ru-RU"

REPORT.mkdir(exist_ok=True)
doc.save(DOCX)
print("saved", DOCX)
