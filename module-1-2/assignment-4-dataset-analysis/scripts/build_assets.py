"""Build the three screenshot composites for Assignment 4."""
import json
import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots"
LOGS = ROOT / "logs"

FONT_REG = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
DARK = (26, 26, 26)
GREY = (240, 240, 240)
INK = (20, 20, 20)
MUTED = (90, 90, 90)


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


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


def draw_center(draw, width, y, text, fnt, fill=(255, 255, 255)):
    draw.text(((width - draw.textlength(text, font=fnt)) / 2, y), text, font=fnt, fill=fill)


def build_card():
    W, H = 1600, 1400
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 80], fill=DARK)
    draw_center(d, W, 20, "Карточка датасета: MS COCO (Common Objects in Context)", font(32, True))
    d.rectangle([0, 80, W, 124], fill=GREY)
    d.text((24, 90), "Источник: Hugging Face Datasets — HuggingFaceM4/COCO", font=font(21), fill=INK)

    fields = [
        ("Название", "MS COCO (Common Objects in Context)"),
        ("Тип данных", "Изображения + текстовые подписи (image-text pairs)"),
        ("Объём", "330 000 изображений (>200 000 размечено), 1,5 млн аннотаций,\n80 категорий объектов, 5 подписей на изображение"),
        ("Формат", "JPEG (изображения) + JSON (аннотации)"),
        ("Лицензия", "CC-BY 4.0 (аннотации); изображения — Flickr CC-BY / CC-BY-SA"),
        ("Способ сбора", "Смешанный: автоматический сбор с Flickr +\nручная разметка через Amazon Mechanical Turk"),
        ("Год", "2014 (исходный релиз); 2017 (обновление COCO 2017)"),
        ("Последнее обновление", "15 декабря 2022 (карточка Hugging Face)"),
        ("Загрузок", "1 822 загрузки, 34 лайка (Hugging Face, на момент проверки)"),
        ("Задача", "Image captioning, object detection, instance segmentation,\nimage-text matching, VQA (совместно с COCO-VQA)"),
    ]
    y = 160
    label_f = font(23, True)
    value_f = font(23)
    for label, value in fields:
        d.text((60, y), label, font=label_f, fill=MUTED)
        lines = wrap(d, value, value_f, W - 540)
        yy = y
        for line in lines:
            d.text((500, yy), line, font=value_f, fill=INK)
            yy += 34
        y = max(y + 48, yy + 16)
        d.line([50, y - 8, W - 50, y - 8], fill=(232, 232, 232), width=1)

    y_end = y + 20
    d.rectangle([0, y_end, W, y_end + 44], fill=GREY)
    d.text((24, y_end + 10), "URL: https://huggingface.co/datasets/HuggingFaceM4/COCO", font=font(17), fill=MUTED)
    img = img.crop((0, 0, W, y_end + 44))
    img.save(SHOTS / "01_dataset_card.png")
    print("01_dataset_card.png", img.size)


def build_examples():
    examples = json.loads((LOGS / "examples.json").read_text(encoding="utf-8"))
    cols, rows = 4, 5
    cell_w, img_h, cap_h = 400, 300, 76
    gutter, outer, title_h = 12, 16, 80
    W = outer * 2 + cols * cell_w + (cols - 1) * gutter
    H = title_h + outer + rows * (img_h + cap_h) + (rows - 1) * gutter + outer
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, W, title_h], fill=DARK)
    draw_center(d, W, 20, "Примеры данных: 20 объектов из MS COCO", font(32, True))

    cap_f = font(16)
    num_f = font(17, True)
    for i, ex in enumerate(examples[:20]):
        col, row = i % cols, i // cols
        x = outer + col * (cell_w + gutter)
        y = title_h + outer + row * (img_h + cap_h + gutter)
        d.rectangle([x, y, x + cell_w, y + img_h], fill=(245, 245, 245))
        im = Image.open(SHOTS / ex["image_path"]).convert("RGB")
        im.thumbnail((cell_w, img_h), Image.LANCZOS)
        canvas.paste(im, (x + (cell_w - im.width) // 2, y + (img_h - im.height) // 2))

        d.rectangle([x + 4, y + 4, x + 52, y + 28], fill=(0, 0, 0))
        d.text((x + 9, y + 6), f"#{ex['id']}", font=num_f, fill=(255, 255, 255))

        d.rectangle([x, y + img_h, x + cell_w, y + img_h + cap_h], fill=(250, 250, 250))
        caption = ex["caption"].strip().replace("  ", " ")
        if len(caption) > 88:
            caption = caption[:85].rstrip() + "…"
        lines = wrap(d, caption, cap_f, cell_w - 16)[:3]
        yy = y + img_h + 8
        for line in lines:
            d.text((x + 8, yy), line, font=cap_f, fill=INK)
            yy += 19
    canvas.save(SHOTS / "02_data_examples.png")
    print("02_data_examples.png", canvas.size)


def build_limitations():
    W = 1600
    img = Image.new("RGB", (W, 1000), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 80], fill=DARK)
    draw_center(d, W, 20, "Раздел об ограничениях и предвзятости: MS COCO", font(30, True))

    y = 100
    d.text((50, y), "В карточке датасета на Hugging Face отдельного заполненного раздела", font=font(22), fill=INK)
    d.text((50, y + 30), "об ограничениях и предвзятости нет: в README стоит заголовок", font=font(22), fill=INK)
    d.text((50, y + 60), "«Discussion of Biases» и пометка «[More Information Needed]».", font=font(22), fill=INK)
    d.rectangle([46, y + 96, W - 46, y + 150], fill=(245, 245, 245))
    d.text((70, y + 108), "Фактический текст карточки: «### Discussion of Biases — [More Information Needed]»",
           font=font(20), fill=MUTED)

    y += 180
    d.text((50, y), "Ограничения задокументированы в оригинальной публикации и последующих исследованиях:",
           font=font(22, True), fill=INK)
    y += 42
    items = [
        ("1. Географическая и культурная предвзятость.",
         "Изображения собраны с Flickr, поэтому выборка смещена в сторону западных,\nанглоязычных и обеспеченных пользователей; сцены других культур представлены слабо."),
        ("2. Ограниченный набор категорий.",
         "Только 80 классов объектов: многие распространённые объекты, бренды, элементы\nинтерфейсов и узкие профессиональные объекты в датасете не размечены."),
        ("3. Гендерная предвзятость.",
         "Распределение людей по занятиям и ролям в подписях и аннотациях неравномерно;\nэто документировано в исследованиях гендерных смещений в MS COCO."),
        ("4. Эстетическая предвзятость.",
         "Фотографии «уровня Flickr» отобраны по критериям качества съёмки и потому\nне репрезентируют типичные бытовые, производственные и архивные изображения."),
    ]
    for head, body in items:
        lines = wrap(d, head, font(21, True), W - 120)
        for line in lines:
            d.text((60, y), line, font=font(21, True), fill=INK)
            y += 28
        for line in body.split("\n"):
            d.text((80, y), line, font=font(20), fill=INK)
            y += 26
        y += 12

    y = max(y + 10, 900)
    d.rectangle([0, y, W, y + 100], fill=(245, 245, 245))
    d.text((50, y + 12), "Источник: Lin et al., «Microsoft COCO: Common Objects in Context», ECCV 2014, arXiv:1405.0312;",
           font=font(17), fill=MUTED)
    d.text((50, y + 38), "карточка Hugging Face: huggingface.co/datasets/HuggingFaceM4/COCO;",
           font=font(17), fill=MUTED)
    d.text((50, y + 64), "анализ предвзятости: исследования гендерных и культурных смещений MS COCO (2018–2021).",
           font=font(17), fill=MUTED)
    img.save(SHOTS / "03_limitations.png")
    print("03_limitations.png", img.size)


if __name__ == "__main__":
    build_card()
    build_examples()
    build_limitations()
