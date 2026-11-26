"""Build the three report figures that are data visualisations (Pillow).

01_sources_overview.png  — three source images with captions
02_settings_table.png    — the filled settings table as an image
04_frames_montage.png    — five frames of every animation (visualisation)

The interface figure is a REAL browser screenshot (03_interface_settings.png),
not built here.
"""
import json
import pathlib

from PIL import Image, ImageDraw, ImageFont

from content import SETTINGS

ROOT = pathlib.Path(__file__).resolve().parents[1]
SHOTS = ROOT / "screenshots"
SRC = ROOT / "sources"
FRAMES = ROOT / "logs" / "frames"
SHOTS.mkdir(exist_ok=True)

TNR = r"C:\Windows\Fonts\times.ttf"
TNR_B = r"C:\Windows\Fonts\timesbd.ttf"
TNR_I = r"C:\Windows\Fonts\timesi.ttf"

DARK = (26, 26, 26)
GREY = (120, 120, 120)
LIGHT = (240, 240, 240)


def font(size, bold=False, italic=False):
    path = TNR_B if bold else (TNR_I if italic else TNR)
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            if not cur and draw.textlength(w, font=fnt) > max_w:
                chunk = ""
                for ch in w:
                    if draw.textlength(chunk + ch, font=fnt) <= max_w:
                        chunk += ch
                    else:
                        lines.append(chunk)
                        chunk = ch
                cur = chunk
                continue
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def title_bar(draw, w, text, h=84):
    draw.rectangle([0, 0, w, h], fill=DARK)
    f = font(38, bold=True)
    bbox = draw.textbbox((0, 0), text, font=f)
    draw.text(((w - (bbox[2] - bbox[0])) / 2, (h - (bbox[3] - bbox[1])) / 2 - 4),
              text, font=f, fill="white")


def fit(im, box_w, box_h):
    k = min(box_w / im.width, box_h / im.height)
    return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)


# ---------------------------------------------------------------- figure 1

def sources_overview():
    W = 2400
    margin, gutter, title_h = 48, 28, 84
    panel_w = (W - 2 * margin - 2 * gutter) // 3
    img_h = 600
    panels = [
        ("source_01_portrait.png", "S1: Портрет (ИИ-генерация, Polza.ai, tongyi-mai/z-image)"),
        ("source_02_landscape.png", "S2: Пейзаж (ИИ-генерация, Polza.ai, tongyi-mai/z-image)"),
        ("source_03_painting.jpg", "S3: В. Ван Гог, «Звёздная ночь» (Public domain, Wikimedia Commons)"),
    ]
    cap_font = font(26)
    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    wrapped = [wrap(dummy, cap, cap_font, panel_w - 40) for _, cap in panels]
    cap_h = max(len(w) for w in wrapped) * 34
    H = title_h + 36 + img_h + 26 + cap_h + 40
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    title_bar(d, W, "Три исходных изображения для анимации", title_h)

    y0 = title_h + 36
    for i, ((name, _), lines) in enumerate(zip(panels, wrapped)):
        x = margin + i * (panel_w + gutter)
        d.rectangle([x, y0, x + panel_w, y0 + img_h], outline=(210, 210, 210), width=2)
        pic = Image.open(SRC / name).convert("RGB")
        pic = fit(pic, panel_w - 40, img_h - 40)
        im.paste(pic, (x + (panel_w - pic.width) // 2, y0 + (img_h - pic.height) // 2))
        ty = y0 + img_h + 26
        for line in lines:
            bw = d.textlength(line, font=cap_font)
            d.text((x + (panel_w - bw) / 2, ty), line, font=cap_font, fill="black")
            ty += 34

    im.save(SHOTS / "01_sources_overview.png")
    print("01_sources_overview.png", im.size)


# ---------------------------------------------------------------- figure 2

def settings_table():
    W = 2400
    margin, title_h = 40, 84
    cols = [180, 320, 230, 280, 290, 510, 510]
    headers = ["Работа", "Сервис", "Скорость анимации", "Плавность переходов",
               "Глубина эффекта", "Что именно двигалось", "Что пошло не так"]
    keys = ["work", "service", "speed", "smooth", "depth", "moved", "wrong"]
    assert sum(cols) == W - 2 * margin

    hdr_font, body_font = font(26, bold=True), font(24)
    pad = 14
    line_h = 30
    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))

    header_lines = [wrap(dummy, h, hdr_font, w - 2 * pad) for h, w in zip(headers, cols)]
    header_h = max(len(x) for x in header_lines) * line_h + 2 * pad

    rows = []
    for row in SETTINGS:
        cells = [wrap(dummy, row[k], body_font, w - 2 * pad) for k, w in zip(keys, cols)]
        rows.append((cells, max(len(c) for c in cells) * line_h + 2 * pad))

    H = title_h + 24 + header_h + sum(h for _, h in rows) + 40
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    title_bar(d, W, "Таблица настроек анимаций", title_h)

    x0, y = margin, title_h + 24
    d.rectangle([x0, y, x0 + sum(cols), y + header_h], fill=(232, 232, 232))
    x = x0
    for w, lines in zip(cols, header_lines):
        ty = y + pad
        for line in lines:
            d.text((x + pad, ty), line, font=hdr_font, fill="black")
            ty += line_h
        x += w
    y += header_h

    for ri, (cells, rh) in enumerate(rows):
        if ri % 2:
            d.rectangle([x0, y, x0 + sum(cols), y + rh], fill=(250, 250, 250))
        x = x0
        for w, lines in zip(cols, cells):
            ty = y + pad
            for line in lines:
                d.text((x + pad, ty), line, font=body_font, fill="black")
                ty += line_h
            x += w
        y += rh

    # grid
    y = title_h + 24
    for rh in [header_h] + [h for _, h in rows]:
        d.line([x0, y, x0 + sum(cols), y], fill=(110, 110, 110), width=2)
        y += rh
    d.line([x0, y, x0 + sum(cols), y], fill=(110, 110, 110), width=2)
    x = x0
    y_end = title_h + 24 + header_h + sum(h for _, h in rows)
    for w in cols:
        d.line([x, title_h + 24, x, y_end], fill=(110, 110, 110), width=2)
        x += w
    d.line([x0 + sum(cols), title_h + 24, x0 + sum(cols), y_end], fill=(110, 110, 110), width=2)

    im.save(SHOTS / "02_settings_table.png")
    print("02_settings_table.png", im.size)


# ---------------------------------------------------------------- figure 4

def frames_montage():
    W = 1950
    margin, title_h = 40, 76
    label_w, cell_w, gap = 300, 300, 16
    rows = [
        ("А1. Портрет (минимальная)", "animation_01_portrait"),
        ("А2. Пейзаж (средняя)", "animation_02_landscape"),
        ("А3. Картина (максимальная)", "animation_03_painting"),
    ]
    times = ["0,20 с", "1,26 с", "2,52 с", "3,78 с", "4,84 с"]
    lbl_font = font(26, bold=True)
    time_font = font(24)

    ims = {}
    for _, stem in rows:
        ims[stem] = [Image.open(FRAMES / f"{stem}_f{i}.png").convert("RGB") for i in range(5)]

    row_h = [int(max(im.height * cell_w / im.width for im in ims[stem])) for _, stem in rows]
    top = title_h + 50
    H = int(top + sum(row_h) + 3 * gap + 30)
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    title_bar(d, W, "Кадры трёх анимаций: пять моментов каждого ролика", title_h)

    grid_x = margin + label_w
    for i, t in enumerate(times):
        tw = d.textlength(t, font=time_font)
        d.text((grid_x + i * (cell_w + gap) + (cell_w - tw) / 2, title_h + 16),
               t, font=time_font, fill="black")

    y = top
    for (label, stem), rh in zip(rows, row_h):
        lines = wrap(d, label, lbl_font, label_w - 20)
        ty = y + (rh - len(lines) * 32) / 2
        for line in lines:
            d.text((margin, ty), line, font=lbl_font, fill="black")
            ty += 32
        for i, pic in enumerate(ims[stem]):
            ph = int(pic.height * cell_w / pic.width)
            pic = pic.resize((cell_w, ph), Image.LANCZOS)
            x = grid_x + i * (cell_w + gap)
            im.paste(pic, (x, y))
            d.rectangle([x, y, x + cell_w, y + ph], outline=(150, 150, 150), width=2)
        y += rh + gap

    im.save(SHOTS / "04_frames_montage.png")
    print("04_frames_montage.png", im.size)


if __name__ == "__main__":
    sources_overview()
    settings_table()
    frames_montage()
