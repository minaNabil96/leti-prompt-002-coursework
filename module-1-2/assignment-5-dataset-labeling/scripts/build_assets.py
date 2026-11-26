"""Build the four screenshot composites for Assignment 5."""
import json
import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots"
IMAGES = ROOT / "images"
LOGS = ROOT / "logs"

TNR = r"C:\Windows\Fonts\times.ttf"
TNRB = r"C:\Windows\Fonts\timesbd.ttf"
DARK = (26, 26, 26)
GREY = (240, 240, 240)
INK = (20, 20, 20)
MUTED = (90, 90, 90)
LINE = (170, 170, 170)
ZEBRA = (250, 250, 250)


def font(size, bold=False):
    return ImageFont.truetype(TNRB if bold else TNR, size)


def cell_note(text):
    t = (text or "").strip()
    return "—" if t.lower() in ("", "нет", "no", "—") else t


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


def title_bar(draw, w, text, size=30):
    draw.rectangle([0, 0, w, 78], fill=DARK)
    fnt = font(size, True)
    draw.text(((w - draw.textlength(text, font=fnt)) / 2, 20), text, font=fnt, fill=(255, 255, 255))


def build_table_composite():
    labels = json.loads((LOGS / "labels_ground_truth.json").read_text(encoding="utf-8"))
    headers = ["ID", "Файл", "Класс", "Источник", "Лицензия", "Разметчик", "Комментарий"]
    units = [8, 14, 18, 34, 32, 16, 42]
    W = 1800
    inner = W - 40
    widths = [int(inner * u / sum(units)) for u in units]
    widths[-1] += inner - sum(widths)
    f_hdr = font(17, True)
    f_body = font(15)
    pad = 8
    line_h = 21

    # measure rows
    tmp = Image.new("RGB", (10, 10))
    dm = ImageDraw.Draw(tmp)
    heights = []
    for item in labels:
        vals = [item["id"], item["file"], item["class"], item["source"],
                item["license"], item["annotator"], item["comment"]]
        n = 1
        for val, w in zip(vals, widths):
            n = max(n, len(wrap(dm, val, f_body, w - 2 * pad)))
        heights.append(n * line_h + 2 * pad)

    hdr_h = 44
    H = 78 + 24 + hdr_h + sum(heights) + 24
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    title_bar(d, W, "Таблица разметки: 24 объекта, 3 класса")

    x0, y = 20, 102
    # header
    x = x0
    d.rectangle([x0, y, x0 + inner, y + hdr_h], fill=GREY, outline=INK, width=1)
    for h, w in zip(headers, widths):
        d.text((x + pad, y + 10), h, font=f_hdr, fill=INK)
        x += w
        d.line([x, y, x, y + hdr_h], fill=INK, width=1)
    y += hdr_h

    for ridx, item in enumerate(labels):
        vals = [item["id"], item["file"], item["class"], item["source"],
                item["license"], item["annotator"], item["comment"]]
        rh = heights[ridx]
        if ridx % 2:
            d.rectangle([x0, y, x0 + inner, y + rh], fill=ZEBRA)
        x = x0
        for val, w in zip(vals, widths):
            lines = wrap(d, val, f_body, w - 2 * pad)
            yy = y + pad
            for ln in lines:
                d.text((x + pad, yy), ln, font=f_body, fill=INK)
                yy += line_h
            x += w
            d.line([x, y, x, y + rh], fill=LINE, width=1)
        d.line([x0, y + rh, x0 + inner, y + rh], fill=LINE, width=1)
        y += rh
    d.rectangle([x0, 102, x0 + inner, y], outline=INK, width=2)
    img.save(SHOTS / "01_labeling_table.png")
    print("01_labeling_table.png", img.size)


def build_collage():
    picks = [
        ("афиша", ["P01", "P04", "P07"]),
        ("обложка книги", ["P09", "P13", "P16"]),
        ("постер фильма", ["P17", "P20", "P22"]),
    ]
    cell_w, gap, outer, title_h = 520, 16, 20, 78
    img_h = int(cell_w * 4 / 3)
    cap_h = 40
    W = outer * 2 + 3 * cell_w + 2 * gap
    H = title_h + outer + 40 + 3 * (img_h + cap_h + 10) + outer
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(canvas)
    title_bar(d, W, "Примеры по классам: Афиша | Обложка книги | Постер фильма", 28)

    f_head = font(24, True)
    f_cap = font(18)
    gt = {x["id"]: x["class"] for x in json.loads(
        (LOGS / "labels_ground_truth.json").read_text(encoding="utf-8"))}
    for col, (cls, ids) in enumerate(picks):
        x = outer + col * (cell_w + gap)
        y = title_h + outer
        head = cls.capitalize()
        d.text((x + (cell_w - d.textlength(head, font=f_head)) / 2, y), head, font=f_head, fill=INK)
        d.line([x, y + 34, x + cell_w, y + 34], fill=DARK, width=2)
        y += 46
        for pid in ids:
            im = Image.open(IMAGES / f"img_{int(pid[1:]):02d}.png").convert("RGB")
            im = im.resize((cell_w, img_h), Image.LANCZOS)
            canvas.paste(im, (x, y))
            d.rectangle([x, y + img_h, x + cell_w, y + img_h + cap_h], fill=(246, 246, 246))
            cap = f"{pid} — {gt[pid]}"
            d.text((x + 10, y + img_h + 10), cap, font=f_cap, fill=INK)
            y += img_h + cap_h + 10
    canvas.save(SHOTS / "02_examples_collage.png")
    print("02_examples_collage.png", canvas.size)


def build_instruction():
    W = 1400
    text = (LOGS / "instruction.md").read_text(encoding="utf-8").split("---")[0]
    f_bold = font(24, True)
    f_body = font(23)

    tmp = Image.new("RGB", (10, 10))
    dm = ImageDraw.Draw(tmp)
    blocks = []
    for para in text.split("\n\n"):
        lines = [ln.strip() for ln in para.strip().splitlines() if ln.strip()]
        if not lines or lines[0].startswith("# "):
            continue
        head = lines[0].replace("**", "")
        rest = [ln.replace("**", "") for ln in lines[1:]]
        hl = wrap(dm, head, f_bold, W - 100)
        rl = []
        for ln in rest:
            bullet = ln.startswith("- ")
            body = ln[2:].strip() if bullet else ln
            rl.append((bullet, wrap(dm, body, f_body, W - (200 if bullet else 140))))
        blocks.append((hl, rl))

    height = 78 + 40
    for hl, rl in blocks:
        height += len(hl) * 38
        height += sum(len(w) for _, w in rl) * 32
        height += 26

    img = Image.new("RGB", (W, height + 20), (255, 255, 255))
    d = ImageDraw.Draw(img)
    title_bar(d, W, "Инструкция разметчика (7 правил)", 32)
    y = 108
    for hl, rl in blocks:
        for line in hl:
            d.text((50, y), line, font=f_bold, fill=INK)
            y += 38
        for bullet, lines in rl:
            for j, line in enumerate(lines):
                if bullet:
                    x = 108
                    if j == 0:
                        d.text((72, y), "—", font=f_body, fill=INK)
                else:
                    x = 70
                d.text((x, y), line, font=f_body, fill=INK)
                y += 32
        y += 26
    img.save(SHOTS / "03_instruction.png")
    print("03_instruction.png", img.size)


def build_blind_results():
    data = json.loads((LOGS / "agreement.json").read_text(encoding="utf-8"))
    rows = data["details"]
    W = 1600
    headers = ["ID", "Истинный класс", "Метка аннотатора", "Совпадение"]
    widths = [150, 540, 540, 330]
    f_hdr = font(19, True)
    f_body = font(19)
    pad = 12
    line_h = 24
    tmp = Image.new("RGB", (10, 10))
    dm = ImageDraw.Draw(tmp)
    heights = []
    for r in rows:
        vals = [r["id"], r["ground_truth"], r["blind_label"],
                "да" if r["match"] else "нет"]
        n = 1
        for v, w in zip(vals, widths):
            n = max(n, len(wrap(dm, v, f_body, w - 2 * pad)))
        heights.append(n * line_h + 2 * pad)

    title = (f"Независимая разметка: 10 объектов, доля совпадений = "
             f"{data['agreement_rate']:.0%}")
    H = 78 + 30 + 44 + sum(heights) + 110 + 30
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    title_bar(d, W, title, 26)

    x0, y = 20, 108
    d.rectangle([x0, y, x0 + W - 40, y + 44], fill=GREY, outline=INK, width=1)
    x = x0
    for h, w in zip(headers, widths):
        d.text((x + pad, y + 11), h, font=f_hdr, fill=INK)
        x += w
        d.line([x, y, x, y + 44], fill=INK, width=1)
    y += 44
    for i, r in enumerate(rows):
        vals = [r["id"], r["ground_truth"], r["blind_label"],
                "да" if r["match"] else "нет"]
        rh = heights[i]
        if i % 2:
            d.rectangle([x0, y, x0 + W - 40, y + rh], fill=ZEBRA)
        x = x0
        for j, (v, w) in enumerate(zip(vals, widths)):
            lines = wrap(d, v, f_body, w - 2 * pad)
            yy = y + pad
            for ln in lines:
                color = INK
                if j == 3:
                    color = (20, 120, 40) if r["match"] else (190, 30, 30)
                d.text((x + pad, yy), ln, font=f_body, fill=color)
                yy += line_h
            x += w
            d.line([x, y, x, y + rh], fill=LINE, width=1)
        d.line([x0, y + rh, x0 + W - 40, y + rh], fill=LINE, width=1)
        y += rh
    d.rectangle([x0, 108, x0 + W - 40, y], outline=INK, width=2)

    y += 24
    d.rectangle([20, y, W - 20, y + 86], fill=GREY)
    summary = (f"Совпадений: {data['matches']}/{data['total']} "
               f"({data['agreement_rate']:.0%}). Расхождений: {data['mismatches_count']}.")
    fs = font(21, True)
    d.text((36, y + 12), summary, font=fs, fill=INK)
    stress_path = LOGS / "stress_agreement.json"
    if stress_path.exists():
        stress = json.loads(stress_path.read_text(encoding="utf-8"))
        extra = (f"Дополнительный стресс-тест на 8 пограничных изображениях: "
                 f"{stress['matches']}/{stress['total']} ({stress['agreement_rate']:.0%}).")
        d.text((36, y + 48), extra, font=font(20), fill=MUTED)
    img.save(SHOTS / "04_blind_results.png")
    print("04_blind_results.png", img.size)


if __name__ == "__main__":
    SHOTS.mkdir(parents=True, exist_ok=True)
    build_table_composite()
    build_collage()
    build_instruction()
    build_blind_results()
