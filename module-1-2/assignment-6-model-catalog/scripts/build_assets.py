"""Build the 10 screenshot composites for Assignment 6."""
import json
import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
SHOTS = ROOT / "screenshots"
LOGS = ROOT / "logs"
META = LOGS / "model_metadata"
DEMO = LOGS / "demo_results"
SHOTS.mkdir(exist_ok=True)

TNR = r"C:\Windows\Fonts\times.ttf"
TNRB = r"C:\Windows\Fonts\timesbd.ttf"
DARK = (26, 26, 26)
GREY = (240, 240, 240)
INK = (20, 20, 20)
MUTED = (90, 90, 90)
LINE = (170, 170, 170)
BLUE = (214, 230, 245)
GREEN = (219, 238, 223)
ORANGE = (250, 230, 204)
PILL = (232, 238, 246)


def font(size, bold=False):
    return ImageFont.truetype(TNRB if bold else TNR, size)


def wrap(draw, text, fnt, max_w):
    lines = []
    for para in str(text).split("\n"):
        if not para.strip():
            lines.append("")
            continue
        cur = ""
        for word in para.split():
            test = (cur + " " + word).strip()
            if draw.textlength(test, font=fnt) <= max_w or not cur:
                cur = test
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


def title_bar(draw, w, text, size=30, h=78):
    draw.rectangle([0, 0, w, h], fill=DARK)
    fnt = font(size, True)
    draw.text(((w - draw.textlength(text, font=fnt)) / 2, (h - size) / 2 - 4),
              text, font=fnt, fill=(255, 255, 255))


def sub_bar(draw, w, text, y, h=44, size=20, fill=GREY):
    draw.rectangle([0, y, w, y + h], fill=fill)
    draw.text((30, y + (h - size) / 2 - 2), text, font=font(size), fill=INK)


def bottom_bar(draw, w, h, text, size=17):
    draw.rectangle([0, h - 44, w, h], fill=GREY)
    draw.text((30, h - 44 + 10), text, font=font(size), fill=MUTED)


def load(mid):
    return json.loads((META / f"{mid}_parsed.json").read_text(encoding="utf-8"))


def star(d, cx, cy, r, fill=(190, 150, 30), outline=None):
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=fill, outline=outline)


def build_task_filter():
    catalog = json.loads((META / "_catalog.json").read_text(encoding="utf-8"))
    counts = catalog["task_samples"]
    W = 1600
    img = Image.new("RGB", (W, 900), (255, 255, 255))
    d = ImageDraw.Draw(img)
    title_bar(d, W, "Каталог моделей Hugging Face: фильтр по задачам", 30)
    sub_bar(d, W, "URL: https://huggingface.co/models  →  вкладка Models, фильтр Pipeline tag",
            78, 44, 20)

    cols = [
        ("Компьютерное зрение", BLUE, [
            ("object-detection", True),
            ("image-classification", True),
            ("face-recognition", False),
            ("image-segmentation", False),
        ]),
        ("Генерация контента", GREEN, [
            ("text-to-image", False),
            ("text-to-audio", True),
            ("text-generation", True),
            ("code-generation", False),
        ]),
        ("Анализ данных", ORANGE, [
            ("text-classification", True),
            ("token-classification", True),
            ("sentiment-analysis", False),
            ("tabular-classification", False),
        ]),
    ]

    col_w = 500
    gap = 30
    x0 = (W - (3 * col_w + 2 * gap)) // 2
    top = 160
    f_head = font(24, True)
    f_pill = font(21)
    f_cnt = font(17)
    for ci, (name, color, tags) in enumerate(cols):
        x = x0 + ci * (col_w + gap)
        head_lines = wrap(d, name, f_head, col_w - 20)
        head_h = 46 * len(head_lines) + 16
        d.rectangle([x, top, x + col_w, top + head_h], fill=color, outline=INK, width=2)
        yy = top + 8
        for ln in head_lines:
            tw = d.textlength(ln, font=f_head)
            d.text((x + (col_w - tw) / 2, yy), ln, font=f_head, fill=INK)
            yy += 46
        d.text((x + 12, top + head_h - 30), "направление", font=font(15), fill=MUTED)

        y = top + head_h + 22
        for tag, selected in tags:
            c = counts.get(tag, {})
            n = c.get("exact") or c.get("sampled")
            label = tag
            tw = d.textlength(label, font=f_pill)
            pill_w = tw + (92 if selected else 62)
            fill = (255, 246, 200) if selected else PILL
            outline = (190, 150, 30) if selected else (150, 160, 175)
            d.rounded_rectangle([x + 10, y, x + 10 + pill_w, y + 46], radius=22,
                                fill=fill, outline=outline, width=2)
            if selected:
                star(d, x + 34, y + 23, 12)
            d.text((x + (58 if selected else 36), y + 9), label, font=f_pill, fill=INK)
            cnt = f"{n} мод." if n else ""
            if n == 1000:
                cnt = ">1 000 мод."
            d.text((x + 24 + pill_w, y + 14), cnt, font=f_cnt, fill=MUTED)
            y += 62

    # legend
    ly = top + 46 + 22 + 4 * 62 + 10
    star(d, x0 + 14, ly + 14, 13)
    d.text((x0 + 34, ly + 2),
           "— задачи, по которым отобраны модели M1–M6 (по две на направление)",
           font=font(19), fill=INK)
    d.text((x0, ly + 44),
           "Счётчики — ответ /api/models?filter=<tag>&limit=1000: «>1 000» означает, "
           "что API вернул ровно лимит выборки; 98 — точное число.",
           font=font(17), fill=MUTED)

    note_y = ly + 96
    d.rectangle([x0, note_y, x0 + 3 * col_w + 2 * gap, note_y + 96], fill=(248, 248, 248),
                outline=LINE, width=1)
    d.text((x0 + 18, note_y + 12), "Как отбирались модели:", font=font(19, True), fill=INK)
    d.text((x0 + 18, note_y + 46),
           "в каждом направлении выбраны две модели с разной узкой специализацией; "
           "фильтр по pipeline tag сужает каталог",
           font=font(19), fill=INK)
    d.text((x0 + 18, note_y + 70),
           "до нужной задачи, после чего сравнивались карточки, лицензии и размер.",
           font=font(19), fill=INK)

    H = note_y + 96 + 70
    img = img.crop((0, 0, W, H))
    d = ImageDraw.Draw(img)
    bottom_bar(d, W, H, "Источник: huggingface.co/models — открытый каталог моделей; "
                        "метаданные получены через /api/models", 17)
    img.save(SHOTS / "01_task_filter.png")
    print("01_task_filter.png", img.size)


CARD_FIELDS = [
    ("Задача", "task"),
    ("Тип входа", "input_type"),
    ("Тип выхода", "output_type"),
    ("Данные обучения", "training_data"),
    ("Размер", "model_size"),
    ("Лицензия", "license"),
    ("Пример использования", "example_use"),
    ("Ограничения", "limitations"),
    ("Загрузок", "downloads"),
    ("Лайков", "likes"),
]


def build_card(idx, mid):
    rec = load(mid)
    W = 1600
    label_w = 350
    pad = 26
    f_label = font(22, True)
    f_val = font(21)
    line_h = 30

    tmp = Image.new("RGB", (10, 10))
    dm = ImageDraw.Draw(tmp)
    rows = []
    for label, key in CARD_FIELDS:
        val = rec.get(key)
        if key in ("downloads", "likes"):
            val = f"{val:,}".replace(",", " ") if isinstance(val, int) else "не указано"
        text = str(val)
        lines = wrap(dm, text, f_val, W - label_w - 3 * pad)
        rows.append((label, lines, max(1, len(lines)) * line_h + 22))

    head_h = 118
    H = head_h + sum(r[2] for r in rows) + 90
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    title_bar(d, W, f"Карточка модели: {rec['id']}", 26, 62)
    sub_bar(d, W, f"Направление: {rec['direction']}  |  Специализация: {rec['specialization']}",
            62, 46, 20)

    y = head_h
    for i, (label, lines, rh) in enumerate(rows):
        if i % 2 == 0:
            d.rectangle([0, y, W, y + rh], fill=(250, 250, 250))
        d.text((pad, y + 10), label, font=f_label, fill=INK)
        yy = y + 9
        for ln in lines:
            d.text((label_w + pad, yy), ln, font=f_val, fill=INK)
            yy += line_h
        d.line([0, y, W, y], fill=(215, 215, 215), width=1)
        y += rh
    d.line([0, y, W, y], fill=(215, 215, 215), width=1)

    yy = y + 14
    d.text((pad, yy), "Теги каталога: ", font=font(17, True), fill=MUTED)
    d.text((pad + 160, yy),
           f"pipeline_tag: {rec['pipeline_tag']} · library: {rec['library_name']} · "
           f"model_type: {rec['model_type']}", font=font(17), fill=MUTED)

    bottom_bar(d, W, H, f"URL: {rec['url']}   ·   метаданные Hugging Face API, "
                        f"{rec['fetched_at_utc']}", 16)
    img.save(SHOTS / f"{idx:02d}_card_{mid}.png")
    print(f"{idx:02d}_card_{mid}.png", img.size)


def build_demo_detr():
    data = json.loads((DEMO / "D1.json").read_text(encoding="utf-8"))
    src = Image.open(DEMO / "test_image.jpg").convert("RGB")
    ann = Image.open(DEMO / "D1_annotated.jpg").convert("RGB")
    W = 1800
    top = 118
    bottom = 200
    left_w = 520
    right_w = W - left_w - 90
    ann_h = int(right_w * ann.height / ann.width)
    H = top + ann_h + bottom
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    title_bar(d, W, "Демо: facebook/detr-resnet-50 — детекция объектов", 29, 66)
    sub_bar(d, W, "Запуск: локально, transformers 5.22.1 (CPU); вход — реальное фото, "
                  "лицензия CC0", 66, 46, 20)

    ry = top
    ann_big = ann.resize((right_w, ann_h), Image.LANCZOS)
    img.paste(ann_big, (W - right_w - 28, ry))
    d.rectangle([W - right_w - 28, ry, W - 28, ry + ann_h], outline=INK, width=2)

    lw = left_w
    lh = int(lw * src.height / src.width)
    small = src.resize((lw, lh), Image.LANCZOS)
    img.paste(small, (28, ry))
    d.rectangle([28, ry, 28 + lw, ry + lh], outline=INK, width=2)
    d.text((28, ry + lh + 12), "Вход: улица Амстердама,", font=font(20, True), fill=INK)
    d.text((28, ry + lh + 40), "велосипедисты и автомобили", font=font(20), fill=INK)
    d.text((28, ry + lh + 68), "(Wikimedia Commons, CC0)", font=font(18), fill=MUTED)

    d.text((W - right_w - 28, ry + ann_h + 12),
           "Выход: 28 объектов с уверенностью ≥ 0,90 (из 60 при пороге 0,50)",
           font=font(20, True), fill=INK)

    best = {}
    for r in data["detections"]:
        best[r["label"]] = max(best.get(r["label"], 0), r["score"])
    top_items = sorted(best.items(), key=lambda kv: -kv[1])[:6]
    y = ry + ann_h + 48
    d.text((W - right_w - 28, y),
           "Максимум по классам: " + ", ".join(f"{k} {v:.2f}" for k, v in top_items),
           font=font(19), fill=INK)
    d.text((W - right_w - 28, y + 34),
           f'Всего объектов: {data["count"]} при пороге 0,90; 60 при пороге 0,50; '
           f'инференс {data["inference_seconds"]} с на CPU',
           font=font(18), fill=MUTED)
    bottom_bar(d, W, H, "Модель и изображение настоящие; разметка нанесена по ответу модели",
               16)
    img.save(SHOTS / "08_demo_M1.png")
    print("08_demo_M1.png", img.size)


def build_demo_sentiment():
    data = json.loads((DEMO / "D2.json").read_text(encoding="utf-8"))
    scores = data["scores"]
    W = 1600

    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    quote = f"«{data['input_text']}»"
    lines = wrap(probe, quote, font(25), W - 80)
    y = 176
    y += 38 * len(lines)
    chart_y = y + 58
    by = chart_y + 48
    by += 66 * 3
    res_y = by + 18
    H = res_y + 96 + 68

    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    title_bar(d, W, "Демо: cardiffnlp/twitter-roberta-base-sentiment — анализ тональности",
              27, 66)
    sub_bar(d, W, "Запуск: локально, transformers 5.22.1 (CPU); вход — собственный текст",
            66, 44, 20)

    d.text((40, 135), "Вход:", font=font(24, True), fill=INK)
    yy = 176
    for ln in lines:
        d.text((40, yy), ln, font=font(25), fill=INK)
        yy += 38
    d.text((40, yy + 4), "Английский текст, 108 символов; тема — курс по промпт-инжинирингу",
           font=font(19), fill=MUTED)


    d.text((40, chart_y), "Выход:", font=font(24, True), fill=INK)
    d.text((150, chart_y + 2), "распределение вероятностей по трём классам",
           font=font(20), fill=MUTED)
    bar_x = 330
    bar_w = 800
    by = chart_y + 48
    colors = {"negative": (200, 60, 55), "neutral": (140, 140, 140),
              "positive": (40, 145, 80)}
    for name in ("negative", "neutral", "positive"):
        p = scores[name]
        d.text((40, by + 8), name, font=font(22, True), fill=INK)
        d.rectangle([bar_x, by, bar_x + bar_w, by + 44], fill=(238, 238, 238),
                    outline=LINE, width=1)
        d.rectangle([bar_x, by, bar_x + max(3, int(bar_w * p)), by + 44],
                    fill=colors[name])
        d.text((bar_x + bar_w + 16, by + 8), f"{p * 100:.2f} %", font=font(22), fill=INK)
        by += 66

    res_y = by + 18
    d.rectangle([40, res_y, W - 40, res_y + 96], fill=(232, 244, 236),
                outline=(40, 145, 80), width=2)
    d.text((60, res_y + 14), f"Итог: {data['predicted']} — уверенность "
                              f"{data['confidence'] * 100:.2f} %",
           font=font(26, True), fill=INK)
    d.text((60, res_y + 54),
           f"Сумма вероятностей трёх классов = "
           f"{sum(scores.values()):.4f}; инференс {data['inference_seconds']} с на CPU",
           font=font(18), fill=MUTED)

    bottom_bar(d, W, H, "Модель и текст настоящие; значения взяты из ответа пайплайна "
                        "без округления до целых", 16)
    img.save(SHOTS / "09_demo_M5.png")
    print("09_demo_M5.png", img.size)


def rrect(d, box, radius, fill, outline, width=2):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def build_tree():
    W, H = 2000, 1040
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    title_bar(d, W, "Дерево специализаций AI-моделей", 38, 90)

    f_root = font(42, True)
    f_dir = font(38, True)
    f_spec = font(34)
    f_model = font(31, True)
    f_badge = font(24, True)

    rbox = [780, 112, 1220, 200]
    rrect(d, rbox, 18, DARK, DARK)
    tw = d.textlength("AI-модели", font=f_root)
    d.text((1000 - tw / 2, 134), "AI-модели", font=f_root, fill=(255, 255, 255))

    dirs = [
        ("Компьютерное зрение", BLUE, (120, 150, 205), 360, [
            ("Детекция объектов", "M1", ["facebook/", "detr-resnet-50"]),
            ("Распознавание эмоций", "M2",
             ["dima806/", "facial_emotions_", "image_detection"]),
        ]),
        ("Генерация контента", GREEN, (110, 160, 125), 1000, [
            ("Генерация музыки", "M3", ["facebook/", "musicgen-small"]),
            ("Генерация кода", "M4", ["Salesforce/", "codegen-350M-mono"]),
        ]),
        ("Анализ данных", ORANGE, (200, 150, 70), 1640, [
            ("Анализ тональности", "M5",
             ["cardiffnlp/", "twitter-roberta-", "base-sentiment"]),
            ("Медицинский NER", "M6", ["d4data/", "biomedical-ner-all"]),
        ]),
    ]

    bus_y = 226
    d.line([1000, 200, 1000, bus_y], fill=MUTED, width=4)
    d.line([360, bus_y, 1640, bus_y], fill=MUTED, width=4)

    dir_top, dir_h = 250, 84
    spec1_top, spec_h = 372, 66
    model1_top, model_h = 486, 150
    spec2_top = 684
    model2_top = 798

    for name, fill, edge, cx, specs in dirs:
        d.line([cx, bus_y, cx, dir_top], fill=MUTED, width=4)
        dbox = [cx - 310, dir_top, cx + 310, dir_top + dir_h]
        rrect(d, dbox, 16, fill, edge)
        tw = d.textlength(name, font=f_dir)
        d.text((cx - tw / 2, dir_top + 20), name, font=f_dir, fill=INK)

        for i, (spec, mid, id_lines) in enumerate(specs):
            spec_top = spec1_top if i == 0 else spec2_top
            model_top = model1_top if i == 0 else model2_top

            d.line([cx, spec_top - 34, cx, spec_top], fill=MUTED, width=4)
            sbox = [cx - 250, spec_top, cx + 250, spec_top + spec_h]
            rrect(d, sbox, 14, (255, 255, 255), edge)
            tw = d.textlength(spec, font=f_spec)
            d.text((cx - tw / 2, spec_top + 12), spec, font=f_spec, fill=INK)

            d.line([cx, spec_top + spec_h, cx, model_top], fill=MUTED, width=4)
            mbox = [cx - 300, model_top, cx + 300, model_top + model_h]
            rrect(d, mbox, 14, fill, edge)
            d.text((cx - 286, model_top + 10), mid, font=f_badge, fill=MUTED)
            n = len(id_lines)
            yy = model_top + 40 + (108 - 36 * n) // 2
            for ln in id_lines:
                tw = d.textlength(ln, font=f_model)
                d.text((cx - tw / 2, yy), ln, font=f_model, fill=INK)
                yy += 36

    ly = 986
    d.line([60, ly, W - 60, ly], fill=(215, 215, 215), width=1)
    d.text((60, ly + 6), "Цвет:", font=font(22, True), fill=INK)
    for i, (label, fill, edge) in enumerate(
            [("компьютерное зрение", BLUE, (120, 150, 205)),
             ("генерация контента", GREEN, (110, 160, 125)),
             ("анализ данных", ORANGE, (200, 150, 70))]):
        x = 170 + i * 420
        d.rectangle([x, ly + 8, x + 30, ly + 34], fill=fill, outline=edge, width=2)
        d.text((x + 42, ly + 4), label, font=font(22), fill=INK)
    d.text((1420, ly + 6),
           "Уровни: направление → специализация → модель каталога",
           font=font(21), fill=MUTED)

    img.save(SHOTS / "10_tree_diagram.png")
    print("10_tree_diagram.png", img.size)


def main():
    build_task_filter()
    for idx, mid in enumerate(["M1", "M2", "M3", "M4", "M5", "M6"], start=2):
        build_card(idx, mid)
    build_demo_detr()
    build_demo_sentiment()
    build_tree()


if __name__ == "__main__":
    main()
