"""Build Отчет_Задание4.docx (Russian, LETI title page, A4, TNR 14)."""
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
DOCX = REPORT / "Отчет_Задание4.docx"

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


def add_block(text, size=12, left=0.75, before=3, after=6, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    set_par(p, align, before, after, 0, 1.0)
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
tpar("«Задание 4. Анализ открытого мультимедийного датасета»", bold=False)
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
meta = json.loads((LOGS / "dataset_metadata.json").read_text(encoding="utf-8-sig"))
examples = json.loads((LOGS / "examples.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- body

add_h1("1. Введение")
add_par(
    "Цель работы — разобрать открытый мультимедийный датасет по его карточке и реальным "
    "примерам: понять объём и формат данных, способ их создания, качество разметки, "
    "лицензию и ограничения, а затем определить, какие нейросети на этих данных обучать "
    "можно, а какие — нельзя. Для практической работы с генеративными моделями такой "
    "разбор обязателен: качество будущей модели ограничено качеством и репрезентативностью "
    "датасета, а не только архитектурой. В качестве объекта выбран MS COCO (Common Objects "
    "in Context) — один из самых известных наборов «изображение + текст», который "
    "одновременно является учебным примером смешанного способа создания данных: фотографии "
    "собраны автоматически с Flickr, а подписи, рамки и маски созданы людьми через "
    "краудсорсинг. Работа проверяет, насколько карточка датасета позволяет восстановить его "
    "происхождение и где документированные ограничения расходятся с реальными примерами."
)

add_h1("2. Карточка датасета")
add_par(
    "Карточка датасета открыта на платформе Hugging Face Datasets по адресу "
    "https://huggingface.co/datasets/HuggingFaceM4/COCO (дата обращения — 19.11.2026). "
    "Карточка содержит краткое описание, объём, сведения о лицензии и ссылку на "
    "оригинальную публикацию. Метаданные получены через публичный API Hugging Face "
    "(GET /api/datasets/HuggingFaceM4/COCO, HTTP 200); файл сохранён в "
    "logs/dataset_metadata.json."
)
add_picture(SHOTS / "01_dataset_card.png", width_cm=13.5)
add_caption("Рисунок 1 — Карточка датасета MS COCO (Hugging Face)")
add_par(
    "По данным карточки, датасет содержит 330 000 изображений, из которых более 200 000 "
    "размечено, 1,5 млн аннотаций объектов, 80 категорий объектов, 91 категорию фона, "
    "5 подписей на изображение и 250 000 человек с размеченными ключевыми точками. "
    "Лицензия в тегах карточки — cc-by-4.0; дата последнего обновления на Hugging Face — "
    "15 декабря 2022 года; на момент обращения у датасета 1 822 загрузки и 34 лайка."
)

add_h1("3. Паспорт датасета")
add_caption("Таблица 1 — Паспорт датасета MS COCO", keep_next=True)
add_table(
    ["Поле", "Значение"],
    [
        ["Название", "MS COCO (Common Objects in Context); карточка HuggingFaceM4/COCO"],
        ["Задача", "Image captioning, object detection, instance segmentation, keypoints, "
                   "panoptic segmentation, image-text matching; совместно с COCO-VQA — visual question answering"],
        ["Тип данных", "Изображения + текстовые подписи (мультимедиа: image-text pairs), "
                       "а также рамки, попиксельные маски и ключевые точки"],
        ["Объём", "330 000 изображений (>200 000 размечено), 1,5 млн аннотаций объектов, "
                  "80 категорий объектов, 91 категория фона, 5 подписей на изображение, "
                  "250 000 человек с keypoints"],
        ["Формат", "JPEG (изображения) + JSON (аннотации); на Hugging Face — Python-скрипт "
                   "загрузки и файлы репозитория"],
        ["Способ создания", "Смешанный: автоматический сбор изображений с Flickr + ручная "
                            "разметка через Amazon Mechanical Turk"],
        ["Разметка", "Ручная, краудсорсинг: 5 подписей на изображение, bounding boxes, "
                     "segmentation masks, keypoints; контроль — квалификационные задания, "
                     "несколько исполнителей на объект, консенсус и выборочная проверка"],
        ["Лицензия", "Аннотации — CC-BY 4.0; изображения — исходные лицензии Flickr "
                     "(преимущественно CC-BY / CC-BY-SA)"],
        ["Ограничения", "Географическая и культурная предвзятость (Flickr), только 80 категорий, "
                        "гендерная предвзятость, эстетическая предвзятость, шум в подписях"],
        ["Год", "2014 (исходный релиз); 2017 (обновление COCO 2017)"],
    ],
    widths_cm=[3.2, 13.8],
    size=12,
)

add_h1("4. Примеры данных")
add_par(
    "Просмотрены 20 реальных изображений COCO val2017, отобранных равномерно по "
    "отсортированному списку идентификаторов, вместе с официальными подписями (по пять "
    "подписей на изображение, всего 100). Скачанные файлы лежат в screenshots/ "
    "(example_01.jpg … example_20.jpg), структурированные записи — в logs/examples.json."
)
add_picture(SHOTS / "02_data_examples.png", width_cm=14)
add_caption("Рисунок 2 — 20 примеров из MS COCO: изображения с подписями")
add_par(
    "Выборка получилась разнообразной по сюжетам: интерьер столовой, японские дорожные "
    "указатели, слоны и жирафы в зоопарке, ресторанная еда, люди с ноутбуком и телефонами, "
    "поезд, фруктовый фургон, чёрно-белая уличная сцена, десерты с британскими флагами, "
    "автобус у мотеля, овцы, детский день рождения, пляж, теннис, бейсбол, пончик и "
    "кайтсёрфинг. Средняя длина первой подписи — 10,4 слова (от 8 до 14), размер файлов — "
    "от 41 до 315 КБ. Подписи в основном точно называют главный объект, но иногда "
    "упрощают сцену: например, японский знак приоритета пешеходов назван «stop sign», а "
    "междугородный автобус — «old multi colored volvo»."
)

add_h1("5. Способ создания")
add_par(
    "По классификации из лекций датасет относится к категории «смешанный»: в нём сочетаются "
    "автоматический сбор данных и ручная разметка людьми. Изображения не снимались "
    "специально для COCO — они собраны с Flickr по запросам к 80 категориям объектов и их "
    "синонимам. Это автоматический компонент: машина отбирает готовые фотографии из "
    "открытого фотохостинга."
)
add_par(
    "Ручной компонент — разметка на Amazon Mechanical Turk. Исполнители писали по пять "
    "подписей к каждому изображению, обводили объекты рамками, создавали попиксельные маски "
    "для instance segmentation и отмечали ключевые точки людей. Контроль качества включал "
    "квалификационные задания, несколько исполнителей на одно изображение, согласование "
    "результатов и выборочную проверку. Поэтому датасет нельзя назвать ни чисто ручным "
    "(изображения собраны автоматически), ни чисто автоматическим (разметка создана людьми)."
)
add_par(
    "Происхождение и процедура описаны в оригинальной публикации: Lin T.-Y. et al. "
    "Microsoft COCO: Common Objects in Context. ECCV 2014, arXiv:1405.0312. При этом "
    "карточка на Hugging Face не дублирует эти сведения: разделы «Source Data», "
    "«Annotation process» и «Who are the annotators?» содержат пометку "
    "«[More Information Needed]»."
)
add_picture(SHOTS / "03_limitations.png", width_cm=14)
add_caption("Рисунок 3 — Раздел об ограничениях и предвзятости")

add_h1("6. Обучаемые и необучаемые модели", page_break=True)
add_h2("6.1. Модели, которые можно обучить или дообучить")
add_bullet(
    "Модель image captioning (BLIP, Show-Attend-Tell): пять независимых подписей на "
    "изображение дают прямую супервизию «изображение → текст».",
)
add_bullet(
    "Детектор объектов (YOLO, Faster R-CNN, DETR): для 80 категорий размечены bounding boxes — "
    "стандартная супервизия для object detection.",
)
add_bullet(
    "Модель instance segmentation (Mask R-CNN): попиксельные маски позволяют учить не только "
    "класс, но и точную форму объекта.",
)
add_bullet(
    "Модель image-text matching / CLIP-подобная: пары «изображение — подпись» подходят для "
    "контрастивного обучения согласованию визуального и текстового пространств.",
)
add_bullet(
    "Модель visual question answering: совместно с COCO-VQA датасет даёт вопросы и ответы "
    "к изображениям для обучения VQA.",
)
add_par(
    "Дополнительно на COCO можно дообучать pose estimation по keypoints людей и panoptic "
    "segmentation по 91 классу фона."
)
add_h2("6.2. Модели, которые точно нельзя обучить")
add_bullet(
    "Текстовую языковую модель (GPT-подобную): подписи короткие (в среднем около десяти слов) "
    "и описывают только визуальную сцену; связного текстового корпуса на миллиарды слов здесь нет.",
)
add_bullet(
    "Аудиомодель (распознавание речи, синтез музыки): в COCO нет аудио; нужны LibriSpeech, "
    "Common Voice или аналогичные наборы.",
)
add_bullet(
    "Видеомодель (распознавание действий, генерация видео): изображения статичны, временного "
    "измерения нет; нужны Kinetics, HowTo100M и другие видеоданные.",
)
add_bullet(
    "Генеративную модель изображений «с нуля»: 330 тыс. фотографий с ограниченной стилистикой "
    "несопоставимы с миллиардами пар LAION-5B; на одном COCO получится слабая модель, хотя "
    "как небольшая часть обучающего набора COCO полезен.",
)
add_bullet(
    "Модель генерации кода: в датасете нет исходного кода и инструкций к нему.",
)
add_par(
    "Это иллюстрирует принцип «специфика задачи» (лекция 2.5): данные должны соответствовать "
    "той задаче, для которой обучается модель. COCO силён в визуальном понимании, но не "
    "заменяет текстовые, аудио-, видео- и кодовые корпуса."
)

add_h1("7. Потенциальные источники смещения")
add_h2("7.1. Географическая и культурная предвзятость")
add_par(
    "Из 20 просмотренных изображений 12 явно относятся к западной или англоязычной среде: "
    "домашняя столовая, упакованный сэндвич с кофе, британский поезд, табличка «STOP "
    "PEDESTRIANS», десерты с британскими флагами, автобус с надписью «LUKSUSBUSS» у мотеля, "
    "овцы на пастбище, детский день рождения, теннис, бейсбол, пончик и кайтсёрфинг. Ещё "
    "2 кадра явно незападные: японские дорожные указатели и испаноязычная вывеска «COCO "
    "FRIOS». Остальные 6 не имеют однозначных культурных маркеров (зоопарк, еда, толпа, "
    "пляж). Таким образом, около 60 % выборки — западная повседневность, а доля незападных "
    "сцен мала."
)
add_par(
    "Причина — источник данных: Flickr смещён в сторону западных, англоязычных и "
    "обеспеченных пользователей. Это нарушает репрезентативность выборки (лекция 2.3): "
    "датасет не отражает реальное распределение сцен мира. Аналогия — инцидент Google "
    "Photos с ошибочной классификацией темнокожих людей, вызванный недостаточной "
    "представленностью группы в обучающих данных. Практическое следствие: модель, обученная "
    "на COCO, будет хуже распознавать незападную еду, архитектуру, одежду и дорожные знаки."
)
add_h2("7.2. Смещение набора категорий")
add_par(
    "Вторая проблема — структурная: размечены только 80 категорий объектов. В просмотренных "
    "кадрах регулярно встречаются объекты вне этого списка: японские дорожные знаки и "
    "таблички с иероглифами, вывески «COCO FRIOS», «HOTEL» и «LUKSUSBUSS», британские флаги "
    "на десертах, свечи на торте, роллы и лапша, кофейный напиток, кайт, сетка теннисного "
    "корта, бейсбольная форма и шлем, здание мотеля как целое. Детектор, обученный только "
    "на COCO, эти объекты «не видит»."
)
add_par(
    "Это иллюстрация однородности данных (лекция 2.4): покрытие ограничено заранее заданным "
    "списком классов, и увеличение объёма внутри этих классов не исправляет ситуацию. Для "
    "связей с общественностью ограничение критично: логотипы, бренды, упаковка, элементы "
    "интерфейсов и текстовые плашки — именно то, что часто нужно распознавать в социальных "
    "медиа, — в COCO не размечены."
)
add_par(
    "Дополнительно подписи иногда неточны: в примере #2 японский знак приоритета пешеходов "
    "назван «stop sign», а в примере #13 главный объект — автобус — назван «old multi "
    "colored volvo». Это подтверждает принцип «1000 точных примеров лучше миллиона "
    "зашумлённых» (лекция 2.4): объём не заменяет точность разметки."
)

add_h1("8. Правовой аспект")
add_par(
    "Лицензионная структура COCO неоднородна. Аннотации — подписи, рамки, маски и ключевые "
    "точки — распространяются по лицензии CC-BY 4.0 (Creative Commons Attribution 4.0); это "
    "указано в условиях использования cocodataset.org и в теге карточки Hugging Face. "
    "Изображения загружены с Flickr и сохраняют исходные лицензии Flickr; команда COCO "
    "отбирала снимки с открытыми лицензиями, преимущественно CC-BY и CC-BY-SA, но конкретная "
    "лицензия зависит от конкретной фотографии."
)
add_par(
    "CC-BY разрешает учебное и коммерческое использование, изменение и распространение при "
    "обязательной атрибуции. Для изображений под CC-BY-SA действует условие ShareAlike: "
    "изменённая версия такого изображения при распространении должна быть лицензирована под "
    "той же лицензией; на веса модели, обученной на изображениях, это условие по "
    "распространённой трактовке не распространяется, но правовой статус весов остаётся "
    "спорным."
)
add_par(
    "Обязательная атрибуция: «Microsoft COCO: Common Objects in Context. Lin et al., ECCV "
    "2014. arXiv:1405.0312». В учебном проекте этого достаточно; при публикации самих "
    "фотографий нужно проверить лицензию каждого файла. Для коммерческого продукта с "
    "публикацией изображений или спорным использованием весов рекомендуется юридическая "
    "экспертиза."
)
add_par(
    "В России открытые лицензии признаются гражданским законодательством: статья 1286.1 "
    "ГК РФ (часть 4) регулирует открытую лицензию на использование произведения. Лицензии "
    "Creative Commons рассматриваются как допустимые условия использования, поэтому "
    "CC-BY-данные можно использовать в российском учебном и коммерческом проекте при "
    "указании автора и соблюдении условий лицензии."
)

# ---------------------------------------------------------------- appendices

add_h1("Приложение А. Метаданные датасета (JSON)", page_break=True)
add_par(
    "Ниже приведён полный ответ API Hugging Face для датасета HuggingFaceM4/COCO "
    "(GET /api/v1/datasets/HuggingFaceM4/COCO), сохранённый в logs/dataset_metadata.json. "
    "Форматирование добавлено для читаемости, значения не изменены.",
    size=12, after=6,
)
meta_pretty = json.dumps(meta, ensure_ascii=False, indent=2)
add_block(meta_pretty, size=9, left=0.3, align=WD_ALIGN_PARAGRAPH.LEFT)

add_h1("Приложение Б. Журнал работ", page_break=True)
add_par(
    "Инструменты: Python 3.13.17, Pillow 13.0.0, requests 2.34.2, python-docx, LibreOffice "
    "(конвертация DOCX → PDF), curl.exe для загрузки файлов. Платные API не использовались; "
    "ключ Polza.ai не требовался. Дата работы — 19.11.2026, время московское."
)
add_caption("Таблица 2 — Хронология выполнения работы", keep_next=True)
add_table(
    ["Время (MSK)", "Действие"],
    [
        ["15:40", "Создана структура dataset-analysis/; проверены Python и доступ к Hugging Face."],
        ["15:42", "Загружены карточка и README датасета HuggingFaceM4/COCO."],
        ["15:43", "Проверены просмотрщик и резервные мирроры; зафиксированы ответы 404/401/501."],
        ["15:44", "Загружен captions_val2017.json: 25 014 аннотаций, 5 000 изображений."],
        ["15:46", "Скачаны 20 реальных изображений (3,38 МБ) с официального хоста COCO."],
        ["15:50", "Собраны композиты 01_dataset_card.png, 02_data_examples.png, 03_limitations.png."],
        ["15:55", "Заполнены limitations.md, creation_method.md, model_analysis.md, bias_analysis.md, legal_analysis.md."],
        ["16:05", "Собраны DOCX и PDF отчёта, выполнена самопроверка вёрстки."],
    ],
    widths_cm=[2.6, 14.4],
    size=12,
)
add_par(
    "Доступ к примерам: просмотрщик Hugging Face не поддерживает HuggingFaceM4/COCO "
    "(датасет выполняется через Python-скрипт), миррор nielsr/coco-100 недоступен, "
    "просмотрщик merve/coco вернул ошибку 501. Замена датасета не потребовалась: подписи "
    "взяты из официального captions_val2017.json (репозиторий merve/coco на Hugging Face), "
    "изображения — с официального хоста images.cocodataset.org. Подробности — "
    "logs/access_notes.md и logs/worklog.md.",
    before=6,
)

doc.core_properties.title = "Отчет. Задание 4. Анализ открытого мультимедийного датасета"
doc.core_properties.subject = "Применение генеративных нейронных моделей в мультимедиа, задание 4"
doc.core_properties.author = "Ханна М. Н."

REPORT.mkdir(parents=True, exist_ok=True)
doc.save(DOCX)
print("saved", DOCX)
