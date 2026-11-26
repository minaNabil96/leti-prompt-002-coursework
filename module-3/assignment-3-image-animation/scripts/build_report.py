"""Build Отчет_М3_Задание3.docx (image animation, LETI title page)."""
import json
import pathlib
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, RGBColor

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from content import PROMPTS, SETTINGS, SOURCE_URL  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
SHOTS = ROOT / "screenshots"
LOGS = ROOT / "logs"
REPORT = ROOT / "report"
REPORT.mkdir(exist_ok=True)
DOCX = REPORT / "Отчет_М3_Задание3.docx"

STATS = json.loads((LOGS / "computed_stats.json").read_text(encoding="utf-8"))
TOT = STATS["totals"]
COST_TEXT = TOT["cost_rub_text"]
COST_EXACT = TOT["cost_exact_text"]
DUR = TOT["duration_text"]

REFLECTION = (LOGS / "reflection.md").read_text(encoding="utf-8")
REFL_BODY = REFLECTION.split("\n", 2)[2].strip()
REFL_PARAS = [p.strip() for p in REFL_BODY.split("\n\n") if p.strip()]
REFL_WORDS = STATS["reflection_words"]

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
tpar("Тема: Оживление изображений: три анимации — три эффекта", bold=False)
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
    ("Преподаватель", "", "___"),
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
    "Цель работы — оживить три изображения разных типов и сравнить, как движение меняет "
    "их восприятие. Задание требует трёх исходников: «портрет», «пейзаж или городская среда "
    "с элементами, которые естественно движутся (вода, облака, листва, огонь)» и "
    "«изображение на ваш выбор — для креативного эксперимента». В этом качестве выбраны "
    "сгенерированный портрет, сгенерированный пейзаж с озером и картина Винсента Ван Гога "
    "«Звёздная ночь»."
)
add_par(
    "Анимация построена на трёх уровнях интенсивности: минимальном для портрета, среднем "
    "для пейзажа и максимальном для картины. Изображения созданы моделью "
    "tongyi-mai/z-image, ролики — моделью bytedance/seedance-2-mini в режиме image-to-video "
    "через API Polza.ai. Общая стоимость медиа-генерации — " + COST_TEXT + " ₽ "
    "(точная сумма — " + COST_EXACT + " ₽), бюджет задания — 60 ₽."
)

# ---------------------------------------------------------------- 2. sources

add_h1("2. Исходные изображения")
add_par(
    "Задание требует от исходников хорошего освещения, чёткости и одного явного главного "
    "объекта. Все три файла получены 25.11.2026; сама картина написана в 1889 году, поэтому "
    "датировка источников — от 1889 года до 25.11.2026."
)
add_lead(
    "S1 — портрет. ",
    "Сгенерирован по промпту «" + PROMPTS["source_01"] + "» моделью tongyi-mai/z-image; "
    "разрешение 1024×1024, стоимость 1,40 ₽. Лицензия — собственная работа, созданная ИИ; "
    "согласие человека не требуется, так как изображённого человека не существует."
)
add_lead(
    "S2 — пейзаж. ",
    "Сгенерирован по промпту «" + PROMPTS["source_02"] + "» той же моделью; разрешение "
    "1280×720, стоимость 1,40 ₽. Лицензия — собственная работа, созданная ИИ."
)
add_lead(
    "S3 — картина. ",
    "Винсент Ван Гог, «Звёздная ночь» (1889), музей MoMA, Нью-Йорк. Общественное достояние: "
    "автор умер в 1890 году, срок охраны истёк. Файл 1280×1014 (604 КБ) скачан с Wikimedia "
    "Commons (файл Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg) 25.11.2026; полный "
    "адрес — в приложении А."
)
add_picture(SHOTS / "01_sources_overview.png", width_cm=16.5)
add_caption("Рисунок 1 — Визуализация данных: три исходных изображения (S1, S2, S3)",
            before=4, after=8)
add_par(
    "Набор закрывает три разных типа движения. В портрете двигаться могут только мимика и "
    "голова, и любое лишнее движение сразу заметно. В пейзаже есть естественно подвижные "
    "элементы — облака и вода, но нет людей и техники. Картина интересна тем, что её "
    "композиция статична по замыслу: движение здесь не восстанавливает реальность, а "
    "перестраивает авторский замысел."
)

# ---------------------------------------------------------------- 3. animations

add_h1("3. Создание анимаций")
add_par(
    "Все три ролика сделаны через Media API платформы Polza.ai. Запрос POST /api/v1/media "
    "создаёт задачу и возвращает её идентификатор, после чего клиент опрашивает "
    "GET /api/v1/media/{id}, пока статус не станет completed; в ответе приходит ссылка на "
    "MP4. Изображение передавалось в поле images массивом объектов с типом base64, как того "
    "требует формат модели."
)
add_par(
    "Параметры генерации: модель bytedance/seedance-2-mini, режим image-to-video, "
    "длительность 5 с, разрешение 480p, соотношение сторон auto, звук выключен. Страница "
    "модели на polza.ai показывает диапазон цены от 2,56 до 6,75 ₽/с и значения по умолчанию "
    "15 с, 720p и включённый звук; в работе выбраны нижние значения, чтобы уложиться в бюджет "
    "и получить беззвучный ролик. Фактическая цена составила 12,825 ₽ за ролик, то есть "
    "2,565 ₽/с."
)
add_par(
    "Уровни интенсивности различаются только формулировкой. Для портрета промпт просит "
    "одно моргание, лёгкий наклон головы и улыбку; для пейзажа — дрейф облаков и рябь на "
    "воде; для картины — вращение вихрей, мерцание звёзд, раскачивание кипариса и огни "
    "деревни. Одна и та же модель и одни и те же параметры позволяют сравнить именно "
    "эффект промпта, а не разницу моделей."
)
add_par(
    "Замена модели не понадобилась: bytedance/seedance-2-mini принял все три изображения и "
    "вернул видео. Ошибок модерации и таймаутов не было. При первом ролике клиентский скрипт "
    "упал уже после завершения задачи — при разборе ответа, где data пришёл объектом, а не "
    "списком; файл скачан повторно по идентификатору из истории, повторной генерации и "
    "повторного списания не было."
)
add_par("Интерфейс модели с параметрами генерации показан на рисунке 2.")
add_picture(SHOTS / "03_interface_settings.png", width_cm=15.0)
add_caption("Рисунок 2 — Экран Polza.ai: карточка модели bytedance/seedance-2-mini и "
            "параметры генерации (снимок 25.11.2026)", before=4, after=8)
add_par(
    "На рисунке 2 видна карточка модели с идентификатором bytedance/seedance-2-mini и "
    "таблица параметров: prompt до 20 000 символов, aspect_ratio от 16:9 до 21:9 и auto, "
    "images от 0 до 9, duration от 4 до 15 с, generate_audio true или false, resolution "
    "480p или 720p, videos от 0 до 3. Там же указан диапазон стоимости. Это подтверждает, "
    "что выбранные значения допустимы, а интенсивность движения задаётся не отдельным "
    "регулятором, а текстом промпта."
)

# ---------------------------------------------------------------- 4. table

add_h1("4. Таблица настроек")
add_par(
    "Таблица заполнена по фактическим наблюдениям: значения скорости и разрешения взяты из "
    "метаданных файлов, формулировки о движении и артефактах — из покадрового просмотра. "
    "Столбец «Что пошло не так» не оставлен пустым ни в одной строке."
)
add_par(
    "Семь столбцов повторяют формулировку задания, поэтому таблица одновременно служит "
    "шаблоном отчёта и результатом. Скорость указана по метаданным: в запросе стояло 5 с, "
    "а контейнер содержит 121 кадр при 24 кадрах/с, то есть 5,04 с; расхождение в 0,04 с — "
    "округление длительности в контейнере, а не ошибка параметра. Плавность и глубина — "
    "качественные оценки: они описывают, сколько элементов вовлечено в движение и насколько "
    "резко меняются кадры. Столбец «Что пошло не так» заполнен по наблюдениям, а не по "
    "документации модели: у портрета это наезд камеры, у пейзажа — белая точка, у картины — "
    "дублирование звёзд и белая царапина."
)
add_caption("Таблица 1 — Настройки и результаты трёх анимаций", keep_next=True,
            before=4, after=4)
add_table(
    ["Работа", "Сервис", "Скорость анимации", "Плавность переходов",
     "Глубина эффекта", "Что именно двигалось", "Что пошло не так"],
    [(s["work"], s["service"].replace(", ", ",\n"), s["speed"], s["smooth"], s["depth"],
      s["moved"], s["wrong"]) for s in SETTINGS],
    widths_cm=[2.0, 3.8, 1.9, 2.0, 2.25, 2.4, 2.45],
    size=9,
    header_size=9,
)
add_picture(SHOTS / "02_settings_table.png", width_cm=16.5)
add_caption("Рисунок 3 — Визуализация данных: таблица настроек по трём работам",
            before=6, after=8)
add_par(
    "Рисунок 3 повторяет таблицу 1 в виде изображения; текстовый вариант выше удобнее для "
    "чтения, изображение — для быстрого сравнения строк. Числа в обеих формах совпадают: "
    "5 с и 24 кадра/с, по 121 кадру на ролик."
)

# ---------------------------------------------------------------- 5. reflection

add_h1("5. Рефлексия")
refl_intro = add_par("Ниже — рефлексия объёмом " + str(REFL_WORDS) + " слов.")
refl_intro.paragraph_format.keep_with_next = True
for para in REFL_PARAS:
    add_par(para)

# ---------------------------------------------------------------- 6. results

add_h1("6. Результаты анимаций")
add_par(
    "Все три ролика получены: длительность 5,04 с каждый, 24 кадра/с, по 121 кадру, общая "
    "длительность " + DUR + " с, звуковой дорожки нет. Средняя покадровая разница составила "
    "1,414 у портрета, 0,778 у пейзажа и 4,032 у картины: уровень, заданный промптом, и "
    "измеренная подвижность совпали не полностью — самым спокойным оказался именно пейзаж, "
    "а портрет подвижнее из-за наезда камеры."
)
add_picture(SHOTS / "04_frames_montage.png", width_cm=13.5)
add_caption("Рисунок 4 — Визуализация данных: кадры трёх анимаций (0,20–4,84 с)", before=4, after=8)

add_h2("6.1. Портрет (минимальное движение)")
add_par(
    "Файл animation_01_portrait.mp4, 640×640, 1,39 МБ, 5,04 с. Движение читается: глаза закрываются "
    "и открываются, голова слегка наклоняется, в конце появляется улыбка. Освещение и фон "
    "остаются ровными, лицо не распадается на части. Однако модель добавила незапрошенный "
    "наезд камеры: к финалу лицо занимает почти весь кадр, плечи обрезаны, а черты лица "
    "слегка меняются между кадрами. Для портрета это заметный недостаток: зритель следит "
    "не за морганием, а за изменением пропорций. По сетке 3×3 сильнее всего меняется "
    "верхняя центральная область (2,313): там волосы и лоб, которые сдвигает наезд камеры."
)
add_h2("6.2. Пейзаж (средняя интенсивность)")
add_par(
    "Файл animation_02_landscape.mp4, 864×496, 1,31 МБ, 5,04 с. Облака меняют форму и смещаются "
    "вправо, вода рябит, отражения перестраиваются; сильнее всего движение в нижней части "
    "кадра, где расположена вода. Деревья и склоны остаются почти неподвижными, хотя "
    "покачивание ветвей было в промпте. К концу ролика в левом верхнем углу появляется "
    "белая точка-артефакт. В целом это самый убедительный из трёх результатов: движение "
    "небольшое, но согласованное, и пейзаж не теряет узнаваемости. По сетке 3×3 максимум "
    "приходится на нижнюю правую область (2,116), то есть на воду, а не на небо."
)
add_h2("6.3. Свободный выбор (максимальные значения)")
add_par(
    "Файл animation_03_painting.mp4, 752×560, 2,74 МБ, 5,04 с. Вихри неба вращаются, звёзды и луна "
    "растут и мерцают, кипарис раскачивается, огни деревни вспыхивают; композиция при этом "
    "плывёт и приближается. Движение захватывает весь кадр, и это самый зрелищный ролик. "
    "Цена эффекта — потеря авторской геометрии: звёзды дублируются и меняют размер, у "
    "правого края появляется белая царапина, исходная рама картины обрезана, насыщенность "
    "повышена. «Звёздная ночь» перестаёт быть застывшей конструкцией и становится "
    "аттракционом — что и требовалось на максимальном уровне, но именно здесь движение "
    "разрушает смысл сильнее всего. По сетке 3×3 максимум приходится на нижнюю правую "
    "область (7,462): там деревня, поле и склон, которые сдвигает общий панорамирующий "
    "эффект."
)

add_h2("6.4. Сводка измерений")
add_par(
    "Подвижность измерена по декодированным кадрам: каждый ролик приведён к 320×320 в "
    "градациях серого, затем для каждой пары соседних кадров посчитана средняя абсолютная "
    "разность яркости. Это мера движения, а не качества; по средней разнице порядок такой: "
    "пейзаж — 0,778, портрет — 1,414, картина — 4,032, и 95-й процентиль его подтверждает."
)
add_caption("Таблица 2 — Измеренная подвижность трёх роликов", keep_next=True,
            before=4, after=4)
add_table(
    ["Работа", "Разрешение", "Длительность, с", "Кадров", "Размер, МБ",
     "Средняя разница", "95-й процентиль"],
    [
        ("Портрет (A1)", "640×640", "5,04", "121", "1,39", "1,414", "2,994"),
        ("Пейзаж (A2)", "864×496", "5,04", "121", "1,31", "0,778", "0,947"),
        ("Картина (A3)", "752×560", "5,04", "121", "2,74", "4,032", "6,138"),
    ],
    widths_cm=[3.2, 2.4, 2.5, 1.6, 2.0, 2.5, 2.6],
    size=10,
    align_center_cols=(1, 2, 3, 4, 5, 6),
)

# ---------------------------------------------------------------- appendix A

add_h1("Приложение А", page_break=True)
add_par(
    "Ниже — точные параметры и тексты, отправленные в API. Промпты приведены на английском "
    "языке, как они были переданы модели."
)
add_caption("Таблица А.1 — Параметры трёх анимаций", keep_next=True, before=4, after=4)
add_table(
    ["Параметр", "A1 — портрет", "A2 — пейзаж", "A3 — картина"],
    [
        ("Модель", "bytedance/seedance-2-mini", "bytedance/seedance-2-mini",
         "bytedance/seedance-2-mini"),
        ("Режим", "image-to-video", "image-to-video", "image-to-video"),
        ("Исходник", "source_01_portrait.png", "source_02_landscape.png",
         "source_03_painting.jpg"),
        ("Длительность", "5 с", "5 с", "5 с"),
        ("Разрешение", "480p", "480p", "480p"),
        ("Соотношение сторон", "auto", "auto", "auto"),
        ("Звук", "выключен", "выключен", "выключен"),
        ("Стоимость", "12,825 ₽", "12,825 ₽", "12,825 ₽"),
    ],
    widths_cm=[4.0, 4.3, 4.3, 4.2],
    size=11,
)
add_par("Промпты анимаций:", before=8, after=4, bold=False)
for label, key in (("A1 — портрет: ", "animation_01"),
                   ("A2 — пейзаж: ", "animation_02"),
                   ("A3 — картина: ", "animation_03")):
    add_lead(label, "«" + PROMPTS[key] + "»", size=12)
add_par(
    "Промпты исходников: S1 — «" + PROMPTS["source_01"] + "»; S2 — «" +
    PROMPTS["source_02"] + "».",
    size=12, before=6
)
add_par(
    "S3 скачан с Wikimedia Commons по адресу:",
    size=12, before=4, after=0
)
p = doc.add_paragraph()
set_par(p, WD_ALIGN_PARAGRAPH.LEFT, 0, 3, 0, 1.0)
r = p.add_run(SOURCE_URL)
fmt_run(r, 10.5)

# ---------------------------------------------------------------- appendix B

add_h1("Приложение Б", page_break=True)
add_caption("Таблица Б.1 — Хронология выполнения работы (25.11.2026, время MSK)",
            keep_next=True, before=4, after=4)
add_table(
    ["Время", "Этап", "Результат"],
    [
        ("23:04–23:05", "Pre-flight",
         "Python 3.13.17, python-docx 1.2.0, Pillow 13.0.0; каталог API — 401 модель, обе "
         "нужные модели найдены"),
        ("23:06:16", "Баланс", "342,03694906 ₽ до генерации"),
        ("23:06:18", "S3", "Скачан файл 1280×1014, 618 432 Б, лицензия public domain"),
        ("23:06:29–23:06:50", "S1", "tongyi-mai/z-image, 1024×1024, 1,400 ₽"),
        ("23:06:38–23:07:00", "S2", "tongyi-mai/z-image, 1280×720, 1,400 ₽"),
        ("23:07:10–23:08:55", "A1", "seedance-2-mini, 640×640, 12,825 ₽; файл восстановлен "
         "из истории после сбоя разбора ответа"),
        ("23:09:23–23:11:35", "A2", "seedance-2-mini, 864×496, 12,825 ₽"),
        ("23:11:22–23:13:10", "A3", "seedance-2-mini, 752×560, 12,825 ₽"),
        ("23:13", "Контроль", "H.264, 24 кадра/с, 121 кадр, 5,04 с, без звука"),
        ("23:15–23:16", "Скриншот", "Снимок страницы модели в headless Chrome 158.0.8127.88"),
        ("23:18", "Метрики", "Покадровая разница и сетка 3×3 по трём роликам"),
        ("23:19–23:35", "Отчёт", "Собраны визуализации, DOCX, PDF; выполнена самопроверка"),
    ],
    widths_cm=[3.6, 2.8, 10.4],
    size=10.5,
)
add_caption("Таблица Б.2 — Стоимость медиа-генерации", keep_next=True, before=10, after=4)
add_table(
    ["№", "Работа", "Модель", "Количество", "Стоимость, ₽"],
    [
        ("1", "S1 — портрет", "tongyi-mai/z-image", "1 изображение, 1024×1024", "1,400"),
        ("2", "S2 — пейзаж", "tongyi-mai/z-image", "1 изображение, 1280×720", "1,400"),
        ("3", "S3 — картина", "Wikimedia Commons", "1 файл", "0,000"),
        ("4", "A1 — портрет", "bytedance/seedance-2-mini", "5 с, 480p", "12,825"),
        ("5", "A2 — пейзаж", "bytedance/seedance-2-mini", "5 с, 480p", "12,825"),
        ("6", "A3 — картина", "bytedance/seedance-2-mini", "5 с, 480p", "12,825"),
        ("", "Итого", "5 медиа-запросов", "", "41,275"),
    ],
    widths_cm=[1.0, 4.0, 5.0, 4.0, 2.8],
    size=11,
    align_center_cols=(0, 4),
)
add_par(
    "Точная сумма — " + COST_EXACT + " ₽; в тексте она округлена до " + COST_TEXT + " ₽. "
    "Бюджет задания — 60 ₽, израсходовано 68,8 %, остаток 18,725 ₽. Порог 20 ₽ на один "
    "ролик не превышен. Калибровочных и тестовых медиа-запросов не было: ровно два "
    "обращения к tongyi-mai/z-image и три — к bytedance/seedance-2-mini. Служебные "
    "обращения агента к языковой модели при подготовке отчёта не являются генерацией медиа "
    "и в смету задания не входят.",
    size=12, before=6
)
add_par(
    "Инструменты: Python 3.13.17, python-docx 1.2.0, Pillow 13.0.0, requests 2.34.2, "
    "imageio-ffmpeg 0.8.1 (ffmpeg 9.0.2), Google Chrome 158.0.8127.88 для снимка интерфейса, "
    "LibreOffice для конвертации DOCX в PDF. Все генерации выполнены 25.11.2026; "
    "стоимость взята из поля usage.cost_rub каждого ответа и сверена с историей генераций.",
    size=12
)

# ---------------------------------------------------------------- save

DOCX.parent.mkdir(exist_ok=True)
doc.save(DOCX)
print("saved", DOCX, DOCX.stat().st_size, "bytes")
print("paragraphs", len(doc.paragraphs), "tables", len(doc.tables))
