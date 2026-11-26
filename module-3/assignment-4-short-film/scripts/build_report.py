"""Build Отчет_М3_Задание4.docx — LETI title page, A4, TNR 14, 3-6 pages.

All numbers come from logs/computed_stats.json; prompts are quoted from
logs/prompt_iterations.json and scripts/video_prompts.json.
"""
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
REPORT.mkdir(exist_ok=True)
DOCX = REPORT / "Отчет_М3_Задание4.docx"

TNR = "Times New Roman"
S = json.loads((LOGS / "computed_stats.json").read_text(encoding="utf-8"))
PROMPTS = json.loads((LOGS / "prompt_iterations.json").read_text(encoding="utf-8"))
VP = json.loads((ROOT / "scripts" / "video_prompts.json").read_text(encoding="utf-8"))
VOICE = json.loads((ROOT / "scripts" / "voiceover.json").read_text(encoding="utf-8"))
VC = json.loads((LOGS / "video_check.json").read_text(encoding="utf-8"))

C = S["cost"]
F = S["film"]
BUDGET = S["budget_rub"]


def ru(v, d=2):
    return f"{v:.{d}f}".replace(".", ",")


def sp(v):
    return f"{int(round(v)):,}".replace(",", " ")


TBLPR_ORDER = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
               "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd",
               "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook",
               "tblCaption", "tblDescription"]


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
    rPr = run._element.get_or_add_rPr() if hasattr(run, "_element") else run
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
    if run.text and "`" in run.text:          # markdown backticks stay in text otherwise
        run.text = run.text.replace("`", "")
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


doc = Document()


def add_par(text="", size=14, bold=False, italic=False,
            align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=0, after=3, indent=1.25,
            line=1.0):
    p = doc.add_paragraph()
    set_par(p, align, before, after, indent, line)
    r = p.add_run(text)
    fmt_run(r, size, bold, italic)
    return p


def add_lead(label, text, size=14):
    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.JUSTIFY, 0, 3, 1.25, 1.0)
    fmt_run(p.add_run(label), size, bold=True)
    fmt_run(p.add_run(text), size)
    return p


def add_h1(text, page_break=False):
    p = doc.add_paragraph(style="Heading 1")
    set_par(p, WD_ALIGN_PARAGRAPH.CENTER, 10, 6, 0, 1.0, keep_next=True)
    if page_break:
        p.paragraph_format.page_break_before = True
    fmt_run(p.add_run(text), 14, bold=True)
    return p


def add_h2(text):
    p = doc.add_paragraph(style="Heading 2")
    set_par(p, WD_ALIGN_PARAGRAPH.LEFT, 8, 3, 0, 1.0, keep_next=True)
    fmt_run(p.add_run(text), 14, bold=True)
    return p


def add_caption(text, size=12, keep_next=False, before=4, after=10):
    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.CENTER, before, after, 0, 1.0, keep_next=keep_next)
    fmt_run(p.add_run(text), size, italic=True)
    return p


def add_bullet(text, marker="—", size=14):
    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.JUSTIFY, 0, 3, 1.25, 1.0)
    p.paragraph_format.left_indent = Cm(1.25)
    p.paragraph_format.first_line_indent = Cm(-0.5)
    fmt_run(p.add_run(f"{marker} "), size, bold=False)
    fmt_run(p.add_run(text), size)
    return p


def add_picture(path, width_cm, caption):
    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.CENTER, 4, 0, 0, 1.0, keep_next=True)
    p.add_run().add_picture(str(path), width=Cm(width_cm))
    add_caption(caption, before=2, after=8)
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


def cell_text(cell, text, bold=False, size=10, align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = cell.paragraphs[0]
    set_par(p, align, 0, 0, 0, 1.0)
    fmt_run(p.add_run(text), size, bold=bold)


def add_table(headers, rows, widths_cm, size=10, align_center_cols=(), header_size=None):
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
    for side, val in (("top", 25), ("bottom", 25), ("left", 60), ("right", 60)):
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
            al = WD_ALIGN_PARAGRAPH.CENTER if i in align_center_cols else WD_ALIGN_PARAGRAPH.LEFT
            cell_text(cells[i], str(val), size=size, align=al)
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
    for row in table.rows[:-1]:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.keep_with_next = True
    return table


def add_page_field(paragraph):
    run = paragraph.add_run()
    for kind, text in (("begin", None), ("instr", " PAGE "), ("separate", None),
                       ("text", "2"), ("end", None)):
        if kind == "instr":
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = text
        elif kind == "text":
            el = OxmlElement("w:t")
            el.text = text
        else:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        run._r.append(el)
    fmt_run(run, 12)


# ---------------------------------------------------------------- styles
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
def tpar(text="", bold=False, exact_pt=None):
    p = doc.add_paragraph()
    set_par(p, WD_ALIGN_PARAGRAPH.CENTER, 0, 0, 0, 1.0)
    if exact_pt:
        p.paragraph_format.line_spacing = Pt(exact_pt)
    fmt_run(p.add_run(text), 14, bold=bold)
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
tpar("Тема: Короткометражный ролик «Рождение образа»", bold=False)
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
for gc, w in zip(tbl._tbl.tblGrid.gridCol_lst, widths):
    gc.set(qn("w:w"), str(w))
for ri, row_data in enumerate([("Студент гр. 1378", "", "Ханна М. Н."), ("", "", "")]):
    for ci, text in enumerate(row_data):
        p = tbl.cell(ri, ci).paragraphs[0]
        set_par(p, WD_ALIGN_PARAGRAPH.LEFT, 0, 0, 0, 1.0)
        fmt_run(p.add_run(text), 14)

for _ in range(4):
    tpar(exact_pt=54)
tpar("Санкт-Петербург")
tpar("2026")

# ---------------------------------------------------------------- body
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

# ---------------------------------------------------------------- section 1
add_h1("1 Идея и целевая аудитория")
add_par(
    "«Рождение образа» — микродокументалка о том, как нейросеть превращает текстовый "
    "промпт в изображение. Ролик метафорически проходит путь от тьмы и хаоса к форме "
    "и цвету: сначала в кадре только свет и пигмент, затем складывается силуэт, "
    "появляется палитра, и статичная картинка оживает. Закадровый текст ведёт зрителя "
    "по этим шести шагам.")
add_par(
    f"Жанр — микродокументалка, длительность {ru(F['duration_s'], 1)} с. Задание требует "
    "«не менее 5 сгенерированных сцен», «закадровый голос или диалог, синтезированный "
    "TTS-инструментом», «музыку, сгенерированную нейросетью» и монтаж с титрами; "
    "использованы 5 сцен text-to-video, 6 реплик TTS и отдельный музыкальный трек. "
    "Готовый файл — "
    f"`Рождение_образа.mp4`, {F['width']}×{F['height']}, H.264/AAC, "
    f"{ru(F['duration_s'], 1)} с, {ru(F['bytes'] / 1e6, 1)} МБ; он приложен к отчёту "
    "и продублирован в папке `deliverable/`. Публичная ссылка на просмотр не создавалась: "
    "ролик сдаётся файлом, доступным в `deliverable/`.")
add_par(
    "Целевая аудитория — студенты и преподаватели, интересующиеся генеративными "
    "медиа: ролик показывает сам производственный процесс и не требует "
    "специальных знаний, поэтому годится как вводный материал к курсу.")

# ---------------------------------------------------------------- section 2
add_h1("2 Раскадровка")
add_par(
    "Раскадровку предложила текстовая модель (google/gemini-2.5-flash), затем она была "
    "приведена к фиксированной концепции из шести сцен: модель написала англоязычные "
    "промпты для видео и русский закадровый текст. Плановые длительности — 4–5 с на "
    "сцену, но в готовом ролике сцена длится столько, сколько звучит её реплика, поэтому "
    "фактические значения отличаются (столбец «Длительность, с»).")

sc_rows = []
for sc in F["scenes"]:
    vis = {
        1: "Абстрактные мазки света в тёмном пространстве, складывающиеся в спираль",
        2: "Точка света разрастается в туманность из синих и золотых облаков",
        3: "Из жидкого пигмента проявляется силуэт человека без деталей лица",
        4: "Краски текут и сливаются в абстрактный пейзаж",
        5: "Пигмент приходит в движение, кадр «дышит»",
        6: "Титульная карточка: название ролика и выходные данные",
    }[sc["n"]]
    dur = f"{sc['planned_s']:.0f} / {ru(sc['final_s'], 1)}"
    sc_rows.append((str(sc["n"]), sc["scene"], vis, dur, sc["voiceover"]))
add_table(("№", "Сцена", "Визуальное описание", "Длительность, с", "Закадровый текст"),
          sc_rows, (0.9, 2.3, 5.6, 2.7, 5.5), size=9,
          align_center_cols=(0, 3))
add_caption("Таблица 1 — Раскадровка ролика «Рождение образа» (план / факт)", before=2, after=6)

# ---------------------------------------------------------------- section 3
add_h1("3 Использованные инструменты")
add_par(
    "Все генеративные компоненты получены через API Polza.ai; монтаж выполнен локально "
    "в FFmpeg 9.0.2. Модели, цены и параметры сверены с каталогом Polza.ai на дату работы.")
tools = [
    ("Сценарий и раскадровка", "Polza.ai", "`google/gemini-2.5-flash`",
     "5 запросов: черновик, раскадровка, сжатие текста"),
    ("Видео, 5 сцен", "Polza.ai", "`grok-imagine-video-1-5`",
     "text-to-video, 480p, 16:9, 4–5 с"),
    ("Закадровый голос", "Polza.ai", "`google/gemini-3.8-flash-lite-tts`",
     "6 реплик, голос Kore, 24 кГц"),
    ("Музыка", "Polza.ai", "`google/lyria-3-pro-preview`",
     "инструментальный эмбиент, 66 с"),
    ("Монтаж и титры", "FFmpeg, Pillow (локально)", "—",
     "апскейл до 1080p, переходы, сведение, титры"),
    ("Отчёт", "python-docx, LibreOffice (локально)", "—", "DOCX → PDF"),
]
add_table(("Этап", "Инструмент", "Модель", "Назначение"), tools,
          (3.3, 3.5, 5.2, 5.0), size=9)
add_caption("Таблица 2 — Инструменты по этапам", before=2, after=6)

# ---------------------------------------------------------------- section 4
add_h1("4 Ключевые промпты и их итерации")
add_par(
    "Ниже три пары «было → стало»; все ответы модели сохранены в "
    "`logs/prompt_iterations.json` и `logs/prompt_iterations.md`.")

runs = {r["iteration"]: r for r in PROMPTS["runs"]}
add_h2("4.1 Промпт сценария")
add_lead("Было (итерация 1): ", f"«{runs[1]['prompt']}»")
add_par(f"Ответ — {len(runs[1].get('text') or '')} знаков общего текста об искусственном интеллекте: "
        "ни хронометража, ни сцен, ни закадрового текста; для ролика не годится.")
add_lead("Стало (итерация 5): ",
         "промпт задаёт хронометраж каждой сцены, темп речи (14–15 знаков в секунду), "
         "запрет латиницы и чисел цифрами и требует JSON. Результат — 6 реплик общим "
         f"объёмом {VOICE['total_chars']} знака вместо {sum(len(x['was']) for x in VOICE['lines'])} "
         "в версии итерации 4.")

add_h2("4.2 Промпт сцены 1")
add_lead("Было: ", f"«{VP['scenes']['1']['initial']}»")
add_par("Первый дубль показал крупную читаемую надпись «BEYOND THE VEIL»: формулировка "
        "«assemble into words» понята буквально, а ролик русский и текста в кадре быть не должно.")
add_lead("Стало: ", f"«{VP['scenes']['1']['final']}»")
add_par("Добавлен прямой запрет «no letters, no words, no readable text», а сборка слов "
        "заменена на световую спираль. Второй дубль чистый (рисунок 1). Эта пара "
        "показывает, что было исправлено и что стало после перегенерации.")

add_h2("4.3 Промпт озвучки")
add_lead("Было (итерация 4): ",
         f"706 знаков закадрового текста — около 45 с речи при 24 с видео.")
add_lead("Стало (итерация 5): ",
         "та же модель переписала реплики под хронометраж: 344 знака, 32,9 с речи, "
         "по одному короткому предложению на сцену. Смысл и порядок сцен сохранены.")

add_picture(SHOTS / "02_polza_model_card_grok.png", 11.0,
            "Рисунок 1 — Карточка модели grok-imagine-video-1-5 на Polza.ai: тариф "
            "от 1,62 ₽ за секунду (снимок экрана)")

# ---------------------------------------------------------------- section 5
add_h1("5 Проблемы и решения")
add_bullet("Первый запрос к Media API отклонён с HTTP 400: поле `duration` передано "
           "числом, а API требует строку. Исправлено, повторный запрос прошёл.")
add_bullet("Первый дубль сцены 1 содержал английскую надпись в кадре. Промпт переписан "
           "(4.2), дубль перегенерирован; оплаченные 6,48 ₽ учтены в стоимости.")
add_bullet("Речь оказалась длиннее видео: 32,9 с против 24 с. Монтаж перестроен вокруг "
           "озвучки — каждая сцена замедлена до «реплика + 0,35 с» (коэффициент 1,04–1,36), "
           "поэтому ролик длится 33,0 с, а не 28 с по плану. Для абстрактного ряда "
           "замедление незаметно.")
add_bullet("Первый вариант сведения с ducking (`sidechaincompress`) ронял музыку до −44 дБ "
           "в паузах между фразами — слышно «провалы». Заменено на фиксированный фон "
           f"с усилением 0,15: измеренные уровни — голос {ru(VC['levels']['speech_window_db'], 1)} дБ, "
           f"музыка в паузах {ru(VC['levels']['pause_window_db'], 1)} дБ, разница "
           f"{ru(VC['levels']['speech_window_db'] - VC['levels']['pause_window_db'], 1)} дБ "
           "(проверено `volumedetect`).")
add_bullet("У музыкального трека тихое вступление и затухание после 60-й секунды, "
           "поэтому взят фрагмент 24–57 с, а не начало файла.")
add_bullet("Модель отдаёт видео 736×416. Кадр увеличен до 1920×1080 фильтром `scale` "
           "с lanczos и подчёркнут `unsharp`: это апскейл, а не генерация в 1080p — "
           "детализация выше исходной не появляется.")

add_par("Видеомодели Polza.ai с ценами за секунду — на рисунке 2; снимок сделан "
        "в публичном каталоге сервиса после работы.").paragraph_format.keep_with_next = True
add_picture(SHOTS / "01_polza_video_catalog.png", 11.0,
            "Рисунок 2 — Подборка «Нейросети для генерации видео» на Polza.ai "
            "(снимок экрана)")
# ---------------------------------------------------------------- section 6
add_h1("6 Что сгенерировано и что взято извне")
gen = [
    ("Сценарий и раскадровка", "Polza.ai, `google/gemini-2.5-flash`", "Сгенерировано"),
    ("5 видео-сцен", "Polza.ai, `grok-imagine-video-1-5`", "Сгенерировано"),
    ("Закадровый голос", "Polza.ai, `google/gemini-3.8-flash-lite-tts`", "Сгенерировано"),
    ("Музыка", "Polza.ai, `google/lyria-3-pro-preview`", "Сгенерировано"),
    ("Титры (текст и вёрстка)", "Pillow, локально", "Сделано локально, без нейросети"),
    ("Монтаж, переходы, сведение", "FFmpeg, локально", "Локальная обработка"),
    ("Звуковые эффекты", "—", "Не использовались (опциональны)"),
    ("Стоковые видео, музыка, голос", "—", "Не использовались"),
]
add_table(("Компонент", "Источник", "Статус"), gen, (4.6, 6.2, 6.2), size=10)
add_caption("Таблица 3 — Происхождение компонентов ролика", before=2, after=6)

add_par("Кадры готового ролика — на рисунке 3: пять сгенерированных сцен и титульная "
        "карточка, собранная локально.")
add_picture(LOGS / "frames" / "final_sheet.png", 15.0,
            "Рисунок 3 — Кадры готового ролика: сцены 1–5 и титульная карточка")

# ---------------------------------------------------------------- appendix
add_h1("Приложение А. Стоимость и хронология", page_break=True)
add_par(f"Все цены — из ответов API (`usage.cost_rub`), дата — 26.11.2026. "
        f"Бюджет задания — {ru(BUDGET, 0)} ₽, израсходовано {ru(C['total_rub'])} ₽ "
        f"({ru(C['budget_used_pct'], 1)} %), остаток {ru(C['budget_left_rub'])} ₽.")

cost_rows = []
for r in C["llm"]["runs"]:
    name = {1: "Сценарий, итерация 1", 2: "Сценарий, итерация 2", 3: "Сценарий, итерация 3",
            4: "Раскадровка, итерация 4", 5: "Сжатие текста, итерация 5"}[r["iteration"]]
    cost_rows.append((name, "gemini-2.5-flash", "1", ru(r["cost_rub"])))
for v in C["video"]["runs"]:
    name = ("Сцена 1, дубль 1 (отклонён)" if v["rejected"] else f"Сцена {v['scene']}")
    cost_rows.append((name, "grok-imagine-video-1-5", f"{v['duration_param']} с",
                      ru(v["cost_rub"])))
cost_rows.append(("Озвучка, 6 реплик", "gemini-3.8-flash-lite-tts", "344 зн.",
                  ru(C["tts"]["total_rub"])))
cost_rows.append(("Музыка", "lyria-3-pro-preview", "1", ru(C["music"]["total_rub"])))
cost_rows.append(("Итого", f"{C['api_calls']} оплаченных запросов", "", ru(C["total_rub"])))

table = add_table(("Работа", "Модель", "Кол-во", "Стоимость, ₽"), cost_rows,
                  (6.6, 5.6, 2.2, 2.6), size=9, align_center_cols=(2, 3))
# bold the total row
for cell in table.rows[-1].cells:
    for p in cell.paragraphs:
        for r in p.runs:
            r.bold = True
add_caption("Таблица А.1 — Стоимость генерации", before=2, after=6)

WL = [
    ("14:13–14:15", "Сценарий и раскадровка, 5 запросов к gemini-2.5-flash",
     "Раскадровка из 6 сцен, текст сжат до 344 знаков"),
    ("14:15", "Первый запрос к Media API", "HTTP 400: `duration` должен быть строкой"),
    ("14:15", "Сцена 1, дубль 1", "Забракован: надпись «BEYOND THE VEIL»"),
    ("14:16–14:18", "Сцены 1–5 после правки промптов", "5 клипов 736×416, 4–5 с"),
    ("14:18", "Озвучка, 6 запросов TTS", "32,88 с речи до обрезки пауз"),
    ("14:19", "Музыка, lyria-3-pro-preview", "Трек 66,4 с, взят фрагмент 24–57 с"),
    ("14:20–14:24", "Монтаж в FFmpeg", "Растяжка под речь, переходы, титры, сведение"),
    ("14:24", "Экспорт 1080p", "33,0 с, H.264/AAC 48 кГц"),
    ("14:36–14:41", "Скриншоты и отчёт", "3 снимка Polza.ai, DOCX → PDF"),
]
add_table(("Время", "Этап", "Результат"), WL, (2.6, 7.4, 7.0), size=9,
          align_center_cols=(0,))
add_caption("Таблица А.2 — Хронология выполнения работы (26.11.2026, время MSK)",
            before=2, after=4)

doc.save(DOCX)
print("saved", DOCX, DOCX.stat().st_size, "bytes")
