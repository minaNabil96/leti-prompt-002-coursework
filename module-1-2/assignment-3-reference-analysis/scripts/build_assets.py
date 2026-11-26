"""Build the 6 screenshot composites for Assignment 3."""
import json
import pathlib
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots"
LOGS = ROOT / "logs"

FONT_REG = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FONT_IT = r"C:\Windows\Fonts\ariali.ttf"

DARK = (26, 26, 26)
GREY = (240, 240, 240)
USER_BG = (255, 255, 255)
BOT_BG = (250, 250, 250)
INK = (20, 20, 20)
MUTED = (90, 90, 90)


def font(size, kind="reg"):
    path = {"reg": FONT_REG, "bold": FONT_BOLD, "it": FONT_IT}[kind]
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    out = []
    for para in text.split("\n"):
        if not para.strip():
            out.append("")
            continue
        words, cur = para.split(), ""
        for w in words:
            test = (cur + " " + w).strip()
            if draw.textlength(test, font=fnt) <= max_w or not cur:
                cur = test
            else:
                out.append(cur)
                cur = w
        if cur:
            out.append(cur)
    return out


def strip(draw, width, height, text, bg, fg, fnt, pad=24):
    draw.rectangle([0, 0, width, height], fill=bg)
    y = (height - fnt.size) // 2 - 2
    draw.text((pad, y), text, font=fnt, fill=fg)


def strip_bottom(draw, y0, width, height, text, bg, fg, fnt, pad=24):
    draw.rectangle([0, y0, width, y0 + height], fill=bg)
    draw.text((pad, y0 + (height - fnt.size) // 2 - 2), text, font=fnt, fill=fg)


def build_reference():
    src = Image.open(SHOTS / "reference_1024.jpg").convert("RGB")
    target_w = 900
    img = src.resize((target_w, round(src.height * target_w / src.width)), Image.LANCZOS)
    W = 1000
    top_h, cap_h, bot_h = 60, 44, 44
    H = top_h + cap_h + img.height + bot_h + 12
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(canvas)
    strip(d, W, top_h, "Референсное изображение", DARK, (255, 255, 255), font(30, "bold"))
    d.rectangle([0, top_h, W, top_h + cap_h], fill=GREY)
    d.text((24, top_h + 10), 'Vincent van Gogh, "The Starry Night" (1889) | Public domain | Wikimedia Commons',
           font=font(20), fill=INK)
    y = top_h + cap_h + 6
    canvas.paste(img, ((W - img.width) // 2, y))
    y += img.height + 6
    d.rectangle([0, y, W, y + bot_h], fill=GREY)
    d.text((24, y + 10),
           "Источник: https://commons.wikimedia.org/wiki/File:Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
           font=font(15), fill=MUTED)
    canvas.save(SHOTS / "01_reference.png")
    print("01_reference.png", canvas.size)


def dialog(title, user_text, bot_text, out_name, bot_font=21, user_font=20):
    W = 1400
    pad = 40
    inner = W - 2 * pad
    top_h = 64
    d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    uf, bf, lf = font(user_font), font(bot_font), font(22, "bold")
    user_lines = wrap(d0, user_text, uf, inner - 20)
    bot_lines = wrap(d0, bot_text, bf, inner - 20)
    user_block = 46 + len(user_lines) * (user_font + 9) + 24
    bot_block = 46 + len(bot_lines) * (bot_font + 9) + 24
    H = top_h + 10 + user_block + 10 + bot_block + 10

    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, W, top_h], fill=DARK)
    d.text((pad, 16), title, font=font(28, "bold"), fill=(255, 255, 255))

    y = top_h + 10
    d.rectangle([8, y, W - 8, y + user_block], fill=USER_BG, outline=(220, 220, 220))
    d.text((pad, y + 12), "Пользователь:", font=lf, fill=MUTED)
    yy = y + 46
    for line in user_lines:
        d.text((pad + 10, yy), line, font=uf, fill=INK)
        yy += user_font + 9

    y += user_block + 10
    d.rectangle([8, y, W - 8, y + bot_block], fill=BOT_BG, outline=(220, 220, 220))
    d.text((pad, y + 12), "Модель:", font=lf, fill=MUTED)
    yy = y + 46
    for line in bot_lines:
        d.text((pad + 10, yy), line, font=bf, fill=INK)
        yy += bot_font + 9

    canvas.save(SHOTS / out_name)
    print(out_name, canvas.size)


def build_generation(label, title, prompt, prompt_font, out_name, out_w=1200):
    src = Image.open(SHOTS / f"img_gen_{label}.png").convert("RGB")
    side = out_w - 80
    img = src.resize((side, side), Image.LANCZOS)
    pad = 40
    d0 = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    pf = font(prompt_font)
    lines = wrap(d0, prompt, pf, out_w - 2 * pad - 20)
    prompt_block = 44 + len(lines) * (prompt_font + 8) + 20
    top_h = 60
    H = top_h + 8 + prompt_block + 12 + img.height + 24

    canvas = Image.new("RGB", (out_w, H), (255, 255, 255))
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, out_w, top_h], fill=DARK)
    d.text((pad, 14), title, font=font(26, "bold"), fill=(255, 255, 255))

    y = top_h + 8
    d.rectangle([8, y, out_w - 8, y + prompt_block], fill=USER_BG, outline=(220, 220, 220))
    d.text((pad, y + 10), "Промпт:", font=font(21, "bold"), fill=MUTED)
    yy = y + 44
    for line in lines:
        d.text((pad + 10, yy), line, font=pf, fill=INK)
        yy += prompt_font + 8

    y += prompt_block + 12
    canvas.paste(img, ((out_w - img.width) // 2, y))
    canvas.save(SHOTS / out_name)
    print(out_name, canvas.size)


def build_collage():
    panel = 600
    gutter, outer = 16, 24
    title_h = 80
    cap_h = 64
    W = outer * 2 + panel * 3 + gutter * 2
    H = title_h + outer + panel + cap_h + outer
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, W, title_h], fill=DARK)
    d.text((outer, 22), "Сравнение: референс | генерация 1 (подробный промпт) | генерация 2 (наивный промпт)",
           font=font(26, "bold"), fill=(255, 255, 255))

    items = [
        ("reference_1024.jpg", 'Референс: Ван Гог, «Звёздная ночь»'),
        ("img_gen_detailed.png", "Генерация 1 (подробный промпт)"),
        ("img_gen_naive.png", "Генерация 2 (наивный промпт)"),
    ]
    for i, (name, caption) in enumerate(items):
        im = Image.open(SHOTS / name).convert("RGB")
        im = im.copy()
        im.thumbnail((panel, panel), Image.LANCZOS)
        x = outer + i * (panel + gutter)
        y = title_h + outer
        d.rectangle([x, y, x + panel, y + panel], fill=(245, 245, 245))
        canvas.paste(im, (x + (panel - im.width) // 2, y + (panel - im.height) // 2))
        cf = font(20, "bold")
        lines = wrap(d, caption, cf, panel)
        cy = y + panel + 8
        for line in lines[:2]:
            d.text((x + (panel - d.textlength(line, font=cf)) // 2, cy), line, font=cf, fill=INK)
            cy += 24
    canvas.save(SHOTS / "06_comparison_collage.png")
    print("06_comparison_collage.png", canvas.size)


def main():
    analysis = json.loads((LOGS / "analysis.json").read_text(encoding="utf-8"))
    compose = json.loads((LOGS / "compose_call.json").read_text(encoding="utf-8"))
    for d in (analysis, compose):
        d["response"] = re.sub(r"\*\*(.+?)\*\*", r"\1", d["response"])
    naive = (LOGS / "naive_prompt.txt").read_text(encoding="utf-8").strip()
    detailed_used = (LOGS / "prompt_used_detailed.txt").read_text(encoding="utf-8").strip()

    build_reference()
    dialog("Диалог 1: Анализ стиля — google/gemini-2.5-flash",
           analysis["prompt"], analysis["response"], "02_dialog_analysis.png")
    dialog("Диалог 2: Составленный промпт — google/gemini-2.5-flash",
           compose["prompt"], compose["response"], "03_dialog_prompt.png", bot_font=23)
    build_generation("detailed", "Генерация 1: подробный промпт — bytedance/seedream-4",
                     detailed_used, 17, "04_gen_detailed.png")
    build_generation("naive", "Генерация 2: наивный промпт — bytedance/seedream-4",
                     naive, 26, "05_gen_naive.png")
    build_collage()


if __name__ == "__main__":
    main()
