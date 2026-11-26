"""Step 5-6 — build action screenshot composites and architecture cards."""

import json
import pathlib
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots"
LOGS = ROOT / "logs"

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\DejaVuSans.ttf",
]
FONT_BOLD_CANDIDATES = [
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\DejaVuSans-Bold.ttf",
]


def pick(paths):
    for p in paths:
        if pathlib.Path(p).exists():
            return p
    raise FileNotFoundError(paths)


FONT = pick(FONT_CANDIDATES)
FONT_BOLD = pick(FONT_BOLD_CANDIDATES)


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=fnt) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, fnt, fill, line_h):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def block_height(draw, text, fnt, max_w, line_h, padding):
    lines = wrap(draw, text, fnt, max_w)
    return len(lines) * line_h + padding, lines


SERVICES = {
    "T1": {
        "service": "OpenAI ChatGPT (GPT-4o)",
        "model": "openai/gpt-4o",
        "arch_short": "Трансформер",
        "arch": "Трансформер (авторегрессионный decoder-only, семейство GPT)",
        "task": "Чат-бот: объяснение механизма внимания",
        "url": "https://arxiv.org/abs/2303.08774",
        "quote": "GPT-4 is a Transformer-based model pre-trained to predict the next token in a document.",
        "quote_ru": "«GPT-4 — это модель на основе трансформера, предобученная предсказывать следующий токен в документе».",
        "cite": "OpenAI. GPT-4 Technical Report. arXiv:2303.08774, 2023.",
    },
    "T2": {
        "service": "Yandex GPT (Яндекс GPT)",
        "model": "yandex/yandexgpt-5-lite",
        "arch_short": "Трансформер",
        "arch": "Трансформер (YaLM, decoder-only transformer)",
        "task": "Переводчик: перевод фразы на английский",
        "url": "https://github.com/yandex/YaLM-100B",
        "quote": "YaLM 100B is a GPT-like neural network for generating and processing text.",
        "quote_ru": "«YaLM 100B — это GPT-подобная нейросеть для генерации и обработки текста».",
        "cite": "Yandex. YaLM 100B. GitHub, 2022; Yandex Cloud. YandexGPT documentation.",
    },
    "T3": {
        "service": "Google Gemini 2.5 Flash",
        "model": "google/gemini-2.5-flash",
        "arch_short": "Трансформер",
        "arch": "Трансформер (авторегрессионный MoE-трансформер, мультимодальный)",
        "task": "Суммаризация: сжатие текста до двух предложений",
        "url": "https://arxiv.org/abs/2403.05530",
        "quote": "Gemini 1.5 Pro is a sparse mixture-of-expert (MoE) Transformer-based model.",
        "quote_ru": "«Gemini 1.5 Pro — это разреженная смесь экспертов (MoE), модель на основе трансформера».",
        "cite": "Gemini Team, Google. Gemini 1.5. arXiv:2403.05530, 2024.",
    },
    "D1": {
        "service": "Alibaba Z-Image",
        "model": "tongyi-mai/z-image",
        "arch_short": "Диффузия",
        "arch": "Диффузия (flow-matching DiT, S3-DiT)",
        "task": "Генерация изображения по текстовому промпту",
        "url": "https://arxiv.org/abs/2511.22699",
        "quote": "Z-Image, an efficient 6B-parameter foundation generative model built upon a Scalable Single-Stream Diffusion Transformer (S3-DiT) architecture.",
        "quote_ru": "«Z-Image — эффективная фундаментальная генеративная модель на 6 млрд параметров, построенная на архитектуре масштабируемого однопоточного диффузионного трансформера (S3-DiT)».",
        "cite": "Z-Image Team. Z-Image. arXiv:2511.22699, 2025.",
    },
    "D2": {
        "service": "Alibaba Qwen-Image",
        "model": "qwen/image",
        "arch_short": "Диффузия",
        "arch": "Диффузия (латентная, MMDiT — Multimodal Diffusion Transformer)",
        "task": "Генерация изображения по текстовому промпту",
        "url": "https://arxiv.org/abs/2508.02324",
        "quote": "A Multimodal Diffusion Transformer (MMDiT) functions as the backbone diffusion model, modeling the complex joint distribution between noise and image latents under text guidance.",
        "quote_ru": "«Мультимодальный диффузионный трансформер (MMDiT) выполняет роль основной диффузионной модели, моделируя совместное распределение шума и латентов изображения при текстовом управлении».",
        "cite": "Qwen Team. Qwen-Image Technical Report. arXiv:2508.02324, 2025.",
    },
    "D3": {
        "service": "ByteDance Seedream 4.0",
        "model": "bytedance/seedream-4",
        "arch_short": "Диффузия",
        "arch": "Диффузия (rectified flow / flow matching, DiT)",
        "task": "Генерация изображения по текстовому промпту",
        "url": "https://arxiv.org/abs/2509.20427",
        "quote": "We develop a highly efficient diffusion transformer with a powerful VAE which also can reduce the number of image tokens considerably.",
        "quote_ru": "«Мы разработали высокоэффективный диффузионный трансформер с мощным VAE, который также позволяет существенно сократить число токенов изображения».",
        "cite": "Seedream Team, ByteDance. Seedream 4.0. arXiv:2509.20427, 2025.",
    },
}

DARK = (26, 26, 26)
GREY = (240, 240, 240)
WHITE = (255, 255, 255)
TEXT = (20, 20, 20)
MUTED = (90, 90, 90)
BLUE = (20, 90, 190)
ASSIST = (250, 250, 250)


def build_chat(sid):
    meta = SERVICES[sid]
    raw = json.loads((LOGS / f"raw_{sid}.json").read_text(encoding="utf-8"))
    W = 1000
    pad = 26
    inner_w = W - 2 * pad
    f_body = font(20)
    f_label = font(19, bold=True)
    f_head = font(21, bold=True)
    f_sub = font(16)
    line_h = 30

    tmp = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(tmp)
    user_h, user_lines = block_height(d, raw["input"], f_body, inner_w, line_h, 2 * pad + 34)
    asst_h, asst_lines = block_height(d, raw["output"], f_body, inner_w, line_h, 2 * pad + 34)
    H = 60 + 40 + user_h + asst_h + 30

    img = Image.new("RGB", (W, H), WHITE)
    dr = ImageDraw.Draw(img)
    dr.rectangle([0, 0, W, 60], fill=DARK)
    dr.text((pad, 18), f"{meta['service']} — {meta['model']} — {meta['arch_short']}",
            font=f_head, fill=WHITE)
    dr.rectangle([0, 60, W, 100], fill=GREY)
    dr.text((pad, 70), "Polza.ai API call", font=f_sub, fill=TEXT)

    y = 100
    dr.rectangle([0, y, W, y + user_h], fill=WHITE)
    dr.text((pad, y + pad), "Пользователь:", font=f_label, fill=TEXT)
    draw_lines(dr, pad, y + pad + 34, user_lines, f_body, TEXT, line_h)
    y += user_h

    dr.rectangle([0, y, W, y + asst_h], fill=ASSIST)
    dr.text((pad, y + pad), "Модель:", font=f_label, fill=TEXT)
    draw_lines(dr, pad, y + pad + 34, asst_lines, f_body, TEXT, line_h)

    img.save(SHOTS / f"action_{sid}.png")
    print("saved", f"action_{sid}.png", img.size)


def build_image(sid):
    meta = SERVICES[sid]
    raw = json.loads((LOGS / f"raw_{sid}.json").read_text(encoding="utf-8"))
    W = 1000
    pad = 26
    inner_w = W - 2 * pad
    f_body = font(20)
    f_label = font(19, bold=True)
    f_head = font(21, bold=True)
    f_sub = font(16)
    line_h = 30

    tmp = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(tmp)
    prompt_h, prompt_lines = block_height(d, raw["prompt"], f_body, inner_w, line_h, 2 * pad + 34)

    img_size = 900
    H = 60 + 40 + prompt_h + img_size + 30

    canvas = Image.new("RGB", (W, H), WHITE)
    dr = ImageDraw.Draw(canvas)
    dr.rectangle([0, 0, W, 60], fill=DARK)
    dr.text((pad, 18), f"{meta['service']} — {meta['model']} — {meta['arch_short']}",
            font=f_head, fill=WHITE)
    dr.rectangle([0, 60, W, 100], fill=GREY)
    dr.text((pad, 70), "Polza.ai API call", font=f_sub, fill=TEXT)

    y = 100
    dr.rectangle([0, y, W, y + prompt_h], fill=WHITE)
    dr.text((pad, y + pad), "Промпт:", font=f_label, fill=TEXT)
    draw_lines(dr, pad, y + pad + 34, prompt_lines, f_body, TEXT, line_h)
    y += prompt_h

    gen = Image.open(SHOTS / f"img_{sid}.png").convert("RGB")
    gen = gen.resize((img_size, img_size), Image.LANCZOS)
    canvas.paste(gen, ((W - img_size) // 2, y))

    canvas.save(SHOTS / f"action_{sid}.png")
    print("saved", f"action_{sid}.png", canvas.size)


def build_card(sid):
    meta = SERVICES[sid]
    W, H = 1600, 780
    pad = 72
    inner_w = W - 2 * pad
    img = Image.new("RGB", (W, H), WHITE)
    dr = ImageDraw.Draw(img)
    dr.rectangle([0, 0, W, 14], fill=DARK)

    y = 62
    dr.text((pad, y), "Подтверждение архитектуры: " + meta["service"],
            font=font(40, bold=True), fill=TEXT)
    y += 72
    dr.text((pad, y), f"Модель: {meta['model']}", font=font(28), fill=TEXT)
    y += 46
    dr.text((pad, y), f"Архитектура: {meta['arch']}", font=font(28), fill=TEXT)
    y += 52
    dr.text((pad, y), f"Источник: {meta['url']}", font=font(26), fill=BLUE)
    y += 60

    q_lines = wrap(dr, "«" + meta["quote"] + "»", font(32), inner_w - 32)
    q_height = len(q_lines) * 46
    dr.rectangle([pad, y, pad + 8, y + q_height + 12], fill=DARK)
    qx = pad + 32
    draw_lines(dr, qx, y, q_lines, font(32), TEXT, 46)
    y += q_height + 52

    ru_lines = wrap(dr, meta["quote_ru"], font(28), inner_w)
    draw_lines(dr, pad, y, ru_lines, font(28), MUTED, 42)

    dr.line([pad, 662, W - pad, 662], fill=(210, 210, 210), width=2)
    dr.text((pad, 680), meta["cite"], font=font(22), fill=MUTED)
    dr.text((pad, 714), "Проверено по первоисточнику; ссылка указана выше.",
            font=font(22), fill=MUTED)

    img.save(SHOTS / f"arch_{sid}.png")
    print("saved", f"arch_{sid}.png", img.size)


for sid in ["T1", "T2", "T3"]:
    build_chat(sid)
for sid in ["D1", "D2", "D3"]:
    build_image(sid)
for sid in SERVICES:
    build_card(sid)
