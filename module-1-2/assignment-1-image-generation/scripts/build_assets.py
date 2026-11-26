"""Build per-model screenshot composites and the 2x2 comparison collage."""
import json
import pathlib
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
SHOTS = ROOT / "screenshots"
COLLAGE = ROOT / "collage"
LOGS = ROOT / "logs"

FONT_REG = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"

MODELS = [
    ("gemini-2.5-flash-image", "Google Gemini 2.5 Flash Image (Nano Banana 1)",
     "Transformer", "google/gemini-2.5-flash-image", "2,9"),
    ("gpt-image-1.5", "OpenAI GPT-Image 1.5", "Transformer",
     "openai/gpt-image-1.5", "3,0"),
    ("z-image", "Alibaba Z-Image", "Diffusion",
     "tongyi-mai/z-image", "1,4"),
    ("seedream-4", "ByteDance Seedream 4.0", "Diffusion",
     "bytedance/seedream-4", "3,0"),
]

ARCH_RU = {"Transformer": "Трансформер", "Diffusion": "Диффузия"}
PROMPT_EN = (LOGS / "prompt_en.txt").read_text(encoding="utf-8").strip()


def wrap_px(text, font, max_width, draw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, text, path, max_width, start, minimum=10):
    size = start
    while size > minimum:
        f = ImageFont.truetype(path, size)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 1
    return ImageFont.truetype(path, minimum)


def build_screenshot(short, display, arch, model_id):
    img_path = SHOTS / f"img_only_{short}.png"
    im = Image.open(img_path).convert("RGB")
    im = im.resize((1024, int(im.height * 1024 / im.width)), Image.LANCZOS)

    header_h, prompt_h = 80, 60
    canvas = Image.new("RGB", (1024, header_h + prompt_h + im.height), "white")
    draw = ImageDraw.Draw(canvas)

    line = f"Model: {display}  |  Architecture: {arch}  |  Polza.ai ID: {model_id}"
    f1 = fit_font(draw, line, FONT_BOLD, 1000, 15, 10)
    draw.text((12, 24), line, font=f1, fill="black", anchor="lm")

    f2 = ImageFont.truetype(FONT_REG, 13)
    prompt_text = "Prompt: " + PROMPT_EN
    lines = wrap_px(prompt_text, f2, 1004, draw)
    while len(lines) * 16 > prompt_h - 8 and f2.size > 9:
        f2 = ImageFont.truetype(FONT_REG, f2.size - 1)
        lines = wrap_px(prompt_text, f2, 1004, draw)
    y = header_h + 5
    for ln in lines:
        draw.text((10, y), ln, font=f2, fill="#222222")
        y += f2.size + 3

    draw.line([(0, header_h - 1), (1024, header_h - 1)], fill="#cccccc", width=1)
    draw.line([(0, header_h + prompt_h - 1), (1024, header_h + prompt_h - 1)], fill="#cccccc", width=1)
    canvas.paste(im, (0, header_h + prompt_h))
    out = SHOTS / f"screenshot_{short}.png"
    canvas.save(out, "PNG")
    print("screenshot", out.name, canvas.size)
    return display, arch, out


def build_collage(items):
    cell_h = 768
    gutter, pad, caption_h = 16, 24, 42
    cell_w = 768
    width = pad * 2 + cell_w * 2 + gutter

    tmp = Image.new("RGB", (10, 10), "white")
    td = ImageDraw.Draw(tmp)
    title_font = ImageFont.truetype(FONT_BOLD, 34)
    prompt_font = ImageFont.truetype(FONT_REG, 16)
    cap_font = ImageFont.truetype(FONT_REG, 17)

    title = "Сравнение генерации: Трансформер vs Диффузия"
    prompt_label = "Промпт (EN): " + PROMPT_EN
    p_lines = wrap_px(prompt_label, prompt_font, width - pad * 2, td)
    title_block = 42 + 8 + len(p_lines) * 22 + 14

    height = pad + title_block + (cell_h + caption_h) * 2 + gutter + pad
    canvas = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(canvas)

    d.text((pad, pad), title, font=title_font, fill="#111111")
    y = pad + 42 + 8
    for ln in p_lines:
        d.text((pad, y), ln, font=prompt_font, fill="#333333")
        y += 22

    start_y = pad + title_block
    for idx, (short, display, arch, model_id, price) in enumerate(items):
        row, col = divmod(idx, 2)
        im = Image.open(SHOTS / f"img_only_{short}.png").convert("RGB")
        im = im.resize((cell_w, int(im.height * cell_w / im.width)), Image.LANCZOS)
        x = pad + col * (cell_w + gutter)
        yy = start_y + row * (cell_h + caption_h + gutter)
        canvas.paste(im, (x, yy))
        d.rectangle([x - 1, yy - 1, x + cell_w, yy + im.height], outline="#dddddd")
        cap = f"{display} — {ARCH_RU[arch]} — {price} ₽"
        f = cap_font
        while d.textlength(cap, font=f) > cell_w - 8 and f.size > 11:
            f = ImageFont.truetype(FONT_REG, f.size - 1)
        d.text((x + cell_w // 2, yy + im.height + caption_h // 2), cap,
               font=f, fill="#111111", anchor="mm")

    out = COLLAGE / "collage.png"
    canvas.save(out, "PNG")
    print("collage", out.name, canvas.size)


def main():
    items = []
    for short, display, arch, model_id, price in MODELS:
        d, a, _ = build_screenshot(short, display, arch, model_id)
        items.append((short, d, a, model_id, price))
    build_collage(items)


if __name__ == "__main__":
    main()
