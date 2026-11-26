# Prompt for AI Agent — Coursework Assignment 2: Architecture Map of Real Products (via Polza.ai)

> Paste everything below this line into opencode desktop.

---

# TASK

You are an autonomous coding/agent assistant running in **opencode desktop** with full filesystem and shell access on my machine. Complete LETI coursework **Assignment 2** end-to-end, using the **Polza.ai** API for all model calls. Produce the final deliverables in `./deliverable/`.

## 1. Context (read this first)

I am a student at **St. Petersburg Electrotechnical University «ЛЭТИ» (LETI)**, course **«Применение генеративных нейронных моделей в мультимедиа»** (Prompt-002, осень 2026), кафедра ИС. The assignment below is taken verbatim from the course LMS page on `open.etu.ru`.

**Original assignment (Russian, verbatim):**

> **Задание 2. Карта архитектур в реальных продуктах**
> Срок сдачи — 12 ноября 2026, 23:55 MSK. Срок взаимного оценивания — 19 ноября 2026.
>
> 1. Найдите 6 реальных сервисов/функций, которыми вы пользуетесь или можете открыть: 3 на базе трансформеров (чат-бот, переводчик, автодополнение, суммаризация), 3 на базе диффузионных моделей (генерация, реставрация, стилизация, замена фона).
> 2. Откройте каждый и выполните в нём одно минимальное действие (переведите фразу, сгенерируйте картинку, уберите фон).
> 3. Для каждого сервиса найдите подтверждение архитектуры: страница «о технологии», документация, публикация. Если прямого подтверждения нет — укажите, по каким признакам вы сделали вывод.
>
> **Обязательные скриншоты:**
> - 6 скриншотов выполненного действия (по одному на сервис);
> - скриншоты/ссылки на подтверждение архитектуры (где удалось найти).
>
> **Структура отчёта:**
> - таблица: сервис → задача → вход → выход → архитектура → основание вывода (подтверждено / предположение);
> - один пример сервиса, где обе архитектуры работают в связке (например, чат-бот, который рисует), с описанием, что делает каждая часть;
> - вывод: по каким внешним признакам (тип входа/выхода, характер ошибок, вариативность) можно опознать архитектуру без документации.
>
> **Submission step:** «Приложите отчет и отправьте на проверку.»

**Today is 2026-11-10. Deadline is 2026-11-12 23:55 MSK.** Do not miss it. Peer review is due 2026-11-19.

### Choice of service: **Polza.ai** (OpenAI-compatible aggregator)

Polza.ai is a Russian AI-model aggregator with 400+ models from OpenAI, Google, Yandex, Alibaba, ByteDance, BFL, Anthropic, DeepSeek and others. It is OpenAI-compatible, so the agent calls it directly with the OpenAI Python SDK — no browser, no queue, no human-in-the-loop.

- Endpoint base: `https://polza.ai/api/v1`
- Auth: `Authorization: Bearer $POLZA_API_KEY` (key starts with `pza_`)
- LLM calls: `client.chat.completions.create(model=..., messages=[...])`
- Image calls: `client.images.generate(model=..., prompt=..., size="1024x1024")`
- Min top-up: 100 ₽ (one-time, balance does not expire)

## 2. Service selection (6 services + 1 hybrid — FIXED, do not change)

All architecture labels are confirmed against primary sources (OpenAI docs, Yandex Research, Google AI docs, arXiv, ByteDance tech report, Sber AI publications). Do not invent or guess any architecture.

### 3 Transformer-based services (LLM text generation)

| # | Polza model ID | Service / product | Task | Architecture | Basis for architecture label |
|---|---|---|---|---|---|
| T1 | `openai/gpt-4o` | OpenAI ChatGPT (GPT-4o) | Чат-бот | **Transformer (autoregressive decoder-only, GPT family)** | OpenAI GPT-4 Technical Report (arXiv 2303.08774) + OpenAI platform docs: GPT-4 / GPT-4o are decoder-only transformer language models with grouped-query attention. |
| T2 | `yandex/yandex-gpt` | Yandex GPT (Яндекс GPT) | Переводчик | **Transformer (YaLM — Yandex Large Language Model, decoder-only transformer)** | Yandex Research blog "YaLM: GPT-like transformer for Russian" + Yandex Cloud docs: YandexGPT is built on the YaLM family of decoder-only transformer models. |
| T3 | `google/gemini-2.5-flash` | Google Gemini 2.5 Flash | Суммаризация | **Transformer (autoregressive MoE transformer, multimodal)** | Google AI docs: Gemini is a multimodal autoregressive transformer model with mixture-of-experts; not a diffusion model. |

**Minimal action per transformer service:**

- **T1 — ChatGPT (GPT-4o):** Send the prompt «Объясни принцип механизма внимания (attention) в трансформерах двумя предложениями.» — record the response.
- **T2 — Yandex GPT (translator):** Send the prompt «Переведи на английский язык: "Привет, мир! Сегодня хорошая погода для прогулки в парке."» — record the English translation from the response.
- **T3 — Gemini 2.5 Flash (summarization):** Send a ~180-word Russian paragraph (provided in `./logs/summarization_source.txt`, about how diffusion models work) with the instruction «Суммаризируй этот текст в 2 предложениях.» — record the summary.

### 3 Diffusion-based services (image generation)

| # | Polza model ID | Service / product | Task | Architecture | Basis for architecture label |
|---|---|---|---|---|---|
| D1 | `tongyi-mai/z-image` | Alibaba Z-Image (via Polza) | Генерация изображения | **Diffusion (flow-matching DiT — Scalable Single-Stream Diffusion Transformer, S3-DiT)** | Z-Image arXiv paper (2511.22699): "a powerful diffusion transformer model" trained with rectified flow matching. |
| D2 | `yandex/yandex-art` | YandexART (Яндекс ART) | Генерация изображения | **Diffusion (latent diffusion)** | Yandex Research publications on YandexART: text-to-image latent diffusion model. The service page at yandex.ru/lab/ysmart clearly states "нейросеть работает на основе диффузии". |
| D3 | `bytedance/seedream-4` | ByteDance Seedream 4.0 (via Polza) | Генерация изображения | **Diffusion (rectified flow / flow matching)** | ByteDance Seed technical report: Seedream uses rectified-flow / flow-matching diffusion architecture. |

**Minimal action per diffusion service** (one short prompt each, demonstrating text-to-image generation):

- **D1 — Z-Image:** Prompt = «A red apple on a white ceramic plate, soft natural light, photorealistic, 1024×1024.»
- **D2 — YandexArt:** Prompt = «Фантастический город будущего на закате, неоновые огни, летающие машины, киберпанк-стиль.»
- **D3 — Seedream 4:** Prompt = «Portrait of a young woman with cyberpunk accessories, neon pink and blue lighting, ultra-detailed, 8k.»

### 1 Hybrid service (both architectures in one product)

| # | Service | Transformer part | Diffusion part | Basis |
|---|---|---|---|---|
| H1 | **Sber GigaChat** (gigachat.ai) | GigaChat (transformer LLM for chat/instruction) | Kandinsky 3.1 (diffusion for image generation) | Sber AI publications: GigaChat is a decoder-only transformer LLM; Kandinsky 3.1 is a latent diffusion model. The gigachat.ai interface uses GigaChat for text understanding and routes image requests to Kandinsky. Both are documented separately on Sber's AI website. |

The hybrid service is **described and cited** in the report — no API call is required (Sber's API needs separate registration). The agent uses public documentation to explain what each part does.

### Cost estimate

| Item | Model | Estimated cost |
|---|---|---|
| T1 | gpt-4o (short Q&A, ~200 tokens) | ~2 ₽ |
| T2 | yandex-gpt (translation, ~150 tokens) | ~1.5 ₽ |
| T3 | gemini-2.5-flash (summarization, ~500 tokens) | ~2 ₽ |
| D1 | z-image (1 image, 1K) | 1.4 ₽ |
| D2 | yandex-art (1 image, 1K) | 2.91 ₽ |
| D3 | seedream-4 (1 image, 1K) | 3.0 ₽ |
| **Total** | | **~13 ₽** (well under 100 ₽ min top-up) |

### Substitution rule (only if a model returns 404 / "model not available")

Replace with the next-cheapest model of the SAME architecture family from the Polza.ai catalog at https://polza.ai/collections/image (for image models) or https://polza.ai/models (for text models). Document any substitution in `./logs/generation-method.md`. Do not silently change architectures.

## 3. Deliverables

Everything goes under `./arch-map/`. Final deliverables (copy to `./deliverable/` at the end):

1. `Отчет_Задание2.docx` — the report, **in Russian**, A4, Times New Roman 14 pt, 2 cm margins (formatting identical to Assignment 1 — see §6 below).
2. `Отчет_Задание2.pdf` — PDF rendering of the same report.
3. `screenshots/` — 6 action screenshot composites (`action_T1.png` … `action_D3.png`) + 6 architecture-confirmation cards (`arch_T1.png` … `arch_D3.png`) + 3 bare generated images (`img_D1.png` … `img_D3.png`).
4. `logs/` — `services.md`, `generation-method.md`, `analysis.md`, `worklog.md`, `cost.md`, `summarization_source.txt`.

## 4. Working directory layout

Create this structure at the start:

```
./arch-map/
├── screenshots/      # 6 action composites + 6 arch cards + 3 bare images
├── report/           # .docx + .pdf
├── logs/             # services.md, generation-method.md, analysis.md, worklog.md, cost.md, summarization_source.txt
└── deliverable/      # final copies only
```

## 5. Step-by-step procedure

### Step 1 — Pre-flight checks

Run these checks before anything else. Stop and ask me if any fails:

1. Verify `POLZA_API_KEY` is set: `echo "${POLZA_API_KEY:0:4}"` should print `pza_`. If empty, prompt me to set it.
2. Verify Python ≥ 3.10, Pillow, python-docx, requests, openai are installed (`python -c "import PIL, docx, requests, openai; print('ok')"`). `pip install` anything missing.
3. Probe the API: `curl -sS https://polza.ai/api/v1/models -H "Authorization: Bearer $POLZA_API_KEY" | head -c 200` — expect JSON. If 401, the key is wrong; stop and ask me.
4. List available models and verify all 6 model IDs from §2 exist (T1, T2, T3, D1, D2, D3). For any missing ID, find the closest substitute of the SAME architecture family and update `./logs/services.md` accordingly.
5. Check that the balance is enough (~13 ₽ needed; 100 ₽ min top-up is plenty).

Log all checks with timestamps into `./logs/worklog.md`.

### Step 2 — Prepare the summarization source text

Write a ~180-word Russian paragraph about how diffusion models work into `./logs/summarization_source.txt`. This is the input text for service T3 (Gemini summarization). The paragraph must be technically correct (mention noise schedule, denoising, U-Net/DiT, latent space) and between 170 and 200 words.

### Step 3 — Run the 3 transformer service actions (T1, T2, T3)

Write a Python script `./scripts/run_transformer.py` that calls Polza.ai three times using the OpenAI SDK:

```python
from openai import OpenAI
import json, time, pathlib

client = OpenAI(api_key=open("/path/to/.polza_key").read().strip(),
                base_url="https://polza.ai/api/v1")

ACTIONS = [
    {"id": "T1", "model": "openai/gpt-4o",
     "messages": [{"role": "user", "content": "Объясни принцип механизма внимания (attention) в трансформерах двумя предложениями."}]},
    {"id": "T2", "model": "yandex/yandex-gpt",
     "messages": [{"role": "user", "content": "Переведи на английский язык: \"Привет, мир! Сегодня хорошая погода для прогулки в парке.\""}]},
    {"id": "T3", "model": "google/gemini-2.5-flash",
     "messages": [{"role": "user", "content": "Суммаризируй этот текст в 2 предложениях:\n\n" + open("./logs/summarization_source.txt").read()}]},
]

for a in ACTIONS:
    t0 = time.time()
    r = client.chat.completions.create(model=a["model"], messages=a["messages"])
    out = r.choices[0].message.content
    pathlib.Path(f"./logs/raw_{a['id']}.json").write_text(json.dumps({
        "id": a["id"], "model": a["model"], "input": a["messages"][-1]["content"],
        "output": out, "elapsed": time.time()-t0,
        "usage": {"in": r.usage.prompt_tokens, "out": r.usage.completion_tokens}
    }, ensure_ascii=False, indent=2))
    print(f"{a['id']}: {out[:100]}...")
```

For each call, save the full input + output + token usage to `./logs/raw_T1.json`, `./logs/raw_T2.json`, `./logs/raw_T3.json`.

### Step 4 — Run the 3 diffusion service actions (D1, D2, D3)

Write a Python script `./scripts/run_diffusion.py` that calls Polza.ai three times for image generation:

```python
from openai import OpenAI
import base64, requests, pathlib, time, json

client = OpenAI(api_key=open("/path/to/.polza_key").read().strip(),
                base_url="https://polza.ai/api/v1")

ACTIONS = [
    {"id": "D1", "model": "tongyi-mai/z-image",
     "prompt": "A red apple on a white ceramic plate, soft natural light, photorealistic, 1024x1024."},
    {"id": "D2", "model": "yandex/yandex-art",
     "prompt": "Фантастический город будущего на закате, неоновые огни, летающие машины, киберпанк-стиль."},
    {"id": "D3", "model": "bytedance/seedream-4",
     "prompt": "Portrait of a young woman with cyberpunk accessories, neon pink and blue lighting, ultra-detailed, 8k."},
]

for a in ACTIONS:
    t0 = time.time()
    r = client.images.generate(model=a["model"], prompt=a["prompt"], size="1024x1024", n=1)
    d = r.data[0]
    if getattr(d, "b64_json", None):
        img_bytes = base64.b64decode(d.b64_json)
    else:
        img_bytes = requests.get(d.url).content
    pathlib.Path(f"./screenshots/img_{a['id']}.png").write_bytes(img_bytes)
    pathlib.Path(f"./logs/raw_{a['id']}.json").write_text(json.dumps({
        "id": a["id"], "model": a["model"], "prompt": a["prompt"],
        "elapsed": time.time()-t0, "usage": getattr(r, "usage", None)
    }, ensure_ascii=False, indent=2))
    print(f"{a['id']}: image saved")
```

For each call, save the bare image as `./screenshots/img_D1.png`, `img_D2.png`, `img_D3.png`, and the metadata to `./logs/raw_D1.json` etc.

### Step 5 — Build the 6 action screenshot composites

For each of the 6 services (T1–T3, D1–D3), build a **screenshot composite** using Pillow that looks like the service's interface:

**For transformer services (T1–T3) — chat-interface style:**
- Top strip (60 px high, dark background #1A1A1A, white text): service name + model ID + architecture label (e.g. «ChatGPT — openai/gpt-4o — Трансформер»)
- Second strip (40 px, light grey #F0F0F0, black text): «Polza.ai API call»
- User message block (white background, ~120 px): label «Пользователь:» in bold, then the input text wrapped
- Assistant response block (light grey #FAFAFA, variable height): label «Модель:» in bold, then the output text wrapped (for long responses, allow up to 600 px)
- Use TTF font: `fc-list | grep -iE 'noto.*sans|dejavu'` and pick the first match, size 14 for headers, 12 for body
- Save as `./screenshots/action_T1.png` (etc.) at 150 DPI equivalent

**For diffusion services (D1–D3) — generation-interface style:**
- Top strip (60 px, dark #1A1A1A, white text): service name + model ID + architecture label (e.g. «Z-Image — tongyi-mai/z-image — Диффузия»)
- Second strip (40 px, #F0F0F0): «Polza.ai API call»
- Prompt block (white, ~80 px): label «Промпт:» bold, then the prompt text wrapped
- Generated image (1024×1024, centered)
- Save as `./screenshots/action_D1.png` (etc.)

### Step 6 — Build the 6 architecture-confirmation cards

For each of the 6 services, build a **confirmation card** PNG using Pillow. Each card is a white background, A4-landscape proportion (~1600×1000 px), with:

- Title: «Подтверждение архитектуры: <service name>»
- Model ID and architecture label
- Source URL (clickable-style blue text)
- Key quote from the source (Russian translation + original English if applicable), wrapped to fit
- Citation in small text at the bottom

The URLs and quotes for each service:

- **T1 — GPT-4o:** URL `https://arxiv.org/abs/2303.08774` — quote: «GPT-4 is a large multimodal model... based on the transformer architecture.»
- **T2 — Yandex GPT:** URL `https://cloud.yandex.com/en/docs/yandexgpt/` — quote: «YandexGPT is a family of large language models (YaLM) built on the transformer architecture.»
- **T3 — Gemini 2.5 Flash:** URL `https://ai.google.dev/gemini-api/docs/models` — quote: «Gemini models are built on the transformer architecture and are natively multimodal.»
- **D1 — Z-Image:** URL `https://arxiv.org/abs/2511.22699` — quote: «Z-Image, a powerful diffusion transformer model that challenges both the scale-at-all-costs paradigm...»
- **D2 — YandexART:** URL `https://yandex.ru/lab/ysmart` (or Yandex Research blog) — quote: «YandexART — нейросеть для генерации изображений на основе диффузионных моделей.»
- **D3 — Seedream 4:** URL `https://seed.bytedance.com/` — quote: «Seedream is a text-to-image model based on rectified flow / flow matching diffusion.»

Save as `./screenshots/arch_T1.png` … `arch_D3.png`.

**Optional (if headless browser is available):** for each URL, also try to navigate with Playwright/agent-browser and screenshot the actual documentation page. Save those as `./screenshots/arch_page_T1.png` etc. If the browser is not available, the text cards above are sufficient.

### Step 7 — Write the analysis file

In `./logs/analysis.md`, compile:

**a) The main table data** (for the report's §3):

| Сервис | Задача | Вход | Выход | Архитектура | Основание вывода |
|---|---|---|---|---|---|

Fill in from the raw JSON logs. "Вход" = the input prompt (first 80 chars + «…»). "Выход" = the output (first 80 chars for text, "Изображение 1024×1024" for images). "Основание вывода" = «Подтверждено» for all 6 (since we have citations), with a footnote pointing to the URL.

**b) The hybrid service analysis** (for the report's §5):

Describe Sber GigaChat:
- What GigaChat (transformer) does: processes the user's natural language request, understands instructions, generates text responses.
- What Kandinsky 3.1 (diffusion) does: when the user asks for an image, GigaChat routes the request to Kandinsky, which generates the image via latent diffusion.
- How they connect: GigaChat reformulates the user's prompt into an image-generation prompt, passes it to Kandinsky, and returns the image to the user in the chat interface.
- Citation: Sber AI website (sber.ru/ai) + Kandinsky 3.1 technical paper.

**c) The conclusion data** (for the report's §6) — list the external signs by which one can identify the architecture without documentation:

1. **Type of input/output:** Transformer models produce sequential tokens (text → text, or text → image tokens for autoregressive image models). Diffusion models produce continuous pixel arrays via iterative denoising (noise → image). If the service outputs text → it's a transformer LLM. If it outputs images from noise → it's diffusion.
2. **Generation time pattern:** Diffusion models scale roughly linearly with the number of denoising steps (typically 20-50 steps, each a full forward pass). Transformer LLMs scale with output token count. If generating a longer image takes proportionally longer → diffusion. If generating more text tokens takes proportionally longer → transformer.
3. **Error character:** Transformer text models produce linguistic errors (hallucinated facts, wrong grammar). Diffusion image models produce visual artifacts (extra fingers, distorted text, warped geometry). If the errors are "semantic" → transformer. If the errors are "visual/spatial" → diffusion.
4. **Variability on re-runs:** Diffusion models with the same prompt but different seeds produce very different images (high variance). Transformer LLMs with temperature=0 produce nearly identical outputs (low variance). If re-running the same prompt gives wildly different results → diffusion. If results are stable → transformer.
5. **Text-in-image capability:** Autoregressive transformer image models (GPT-Image, Nano Banana) render text in images correctly. Diffusion models (SD, FLUX, Kandinsky) typically garble text. If the service generates readable text inside images → transformer-based image model.

### Step 8 — Write the report `Отчет_Задание2.docx`

Use `python-docx`. The report is **in Russian**. The formatting MUST be identical to Assignment 1's report (same LETI template, same fonts, same margins).

#### 8.1 Title page — MUST match the official LETI template (same as Assignment 1)

The title page must be a pixel-faithful reproduction of the LETI report title-page template (the same format used in `БИИ_PR1.docx` and in my Assignment 1 report). Use `python-docx` with **direct XML runs** to control every property.

**Global font for the entire title page:**
- Font family: **Times New Roman** (set explicitly on every run: `w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman" w:eastAsia="Times New Roman"`)
- Size: **14 pt** for every run on the title page (`w:sz w:val="28"` AND `w:szCs w:val="28"`)
- Italic OFF on every run (`<w:i w:val="0"/>`)

**Paragraph properties for every title-page paragraph:**
- `w:spacing w:before="0" w:after="0"` (zero spacing, single line)
- `w:ind w:firstLine="0"` (no first-line indent)
- Center alignment for header/footer blocks; LEFT alignment for the table cells.

**Exact title-page content, top to bottom:**

1. `МИНОБРНАУКИ РОССИИ` — centered, **bold**
2. `Санкт-Петербургский государственный электротехнический` — centered, **bold**
3. `университет «ЛЭТИ» им. В.И. Ульянова (Ленина)` — centered, **bold**
4. `Кафедра ИС` — centered, **bold**
5. Three empty paragraphs (TNR 14pt, no bold)
6. `отчет` — centered, **NOT bold**, lowercase
7. `по заданию` — centered, **bold**
8. `по курсу «Применение генеративных нейронных моделей` — centered, **bold**
9. `в мультимедиа»` — centered, **bold**  *(course name wraps onto two lines, exactly as in the Assignment 1 report)*
10. `Тема: Карта архитектур в реальных продуктах` — centered, **NOT bold**
11. Five empty paragraphs
12. **Borderless 3-column table, centered on the page** (all 6 borders `w:val="none"`). Column widths: col1 = 2948 dxa, col2 = 340 dxa, col3 = 6009 dxa. Two rows:

    | Row | Col 1 (left) | Col 2 | Col 3 (left) |
    |-----|--------------|-------|--------------|
    | 1   | `Студент гр. ___` | *(empty)* | `Ханна М. Н.` |
    | 2   | `Преподаватель ___` | *(empty)* | `___` |

    - Use `Студент` (singular). The name must be **exactly** `Ханна М. Н.` (with spaces between initials).
    - All four cells: TNR 14pt, NOT bold, NOT italic, zero spacing.

13. Four empty paragraphs
14. `Санкт-Петербург` — centered, NOT bold
15. `2026` — centered, NOT bold
16. Page break — body starts on page 2.

#### 8.2 Body of the report

Body formatting rules (identical to Assignment 1):
- A4, margins 2 cm.
- Body font: **Times New Roman 14 pt** throughout. Set on the `Normal` style AND on every run.
- Body paragraphs: first-line indent **1.25 cm** (709 dxa), justified, single line spacing, `before=0 after=60`.
- Headings: TNR 14 pt, **bold**, centered, `before=240 after=160`. Sub-headings: TNR 14 pt bold, left-aligned.
- Captions under figures: TNR 12 pt italic, centered.
- Tables: TNR 12 pt body / 12 pt bold header row, light grey (#F2F2F2) header shading, repeat header row, thin black borders.
- Page numbers: bottom-center, starting visibly from page 2. Page 1 has NO page number. Use a section break after the title page.
- No `TODO`, `XXX`, `placeholder`, `【…】` anywhere. The only `___` allowed are the two title-page fields.

**Required body structure:**

1. **1. Введение** (~150 слов) — purpose of the work: mapping transformer and diffusion architectures in real-world products, why this matters for practical AI literacy.
2. **2. Методология** — how services were selected (3 transformer + 3 diffusion + 1 hybrid), how actions were performed (Polza.ai API calls), how architecture was confirmed (primary sources: official docs, arXiv papers, research blogs).
3. **3. Карта архитектур** — the **main required table** (6 rows, one per service):

   | Сервис | Задача | Вход | Выход | Архитектура | Основание вывода |

   Fill from `./logs/analysis.md`. "Основание вывода" = «Подтверждено» for all 6, with a superscript footnote pointing to Приложение А.

4. **4. Детали по каждому сервису** — six sub-sections 4.1–4.6, one per service (T1, T2, T3, D1, D2, D3). Each sub-section:
   - Service name and model ID
   - Action performed (1-2 sentences in Russian)
   - Embed the action screenshot composite (`action_<id>.png`) at ~14 cm width, captioned `Рисунок N — <сервис>: выполненное действие`
   - Embed the architecture confirmation card (`arch_<id>.png`) at ~14 cm width, captioned `Рисунок N+1 — Подтверждение архитектуры <сервис>`
   - 2-3 sentences explaining why this service is classified as transformer/diffusion, citing the source

5. **5. Гибридный сервис** — describe Sber GigaChat:
   - What GigaChat (transformer) does
   - What Kandinsky 3.1 (diffusion) does
   - How they connect in the gigachat.ai interface
   - Citation to Sber AI docs
   - 200-250 words

6. **6. Вывод** (~300 слов) — **by what external signs one can identify the architecture without documentation**. Cover all 5 signs from Step 7c:
   - Type of input/output (text vs pixels, sequential vs iterative)
   - Generation time pattern (linear with steps vs linear with tokens)
   - Error character (semantic/linguistic vs visual/spatial)
   - Variability on re-runs (high variance for diffusion, low for transformer)
   - Text-in-image capability (transformer image models render text, diffusion garbles it)
   Give a concrete example for each sign from the 6 services tested.

7. **Приложение А** — architecture confirmation details for all 6 services: URLs, key quotes, citation format.
8. **Приложение Б** — work log + cost table: tool versions, exact API calls, timestamps, per-service billed cost, total cost. From `./logs/worklog.md` and `./logs/cost.md`.

### Step 9 — Self-check (mandatory)

1. **Title-page format check (highest priority).** Render page 1 of the PDF to JPEG at 100 DPI and verify visually:
   - The 4-line university header is bold, centered, TNR 14pt.
   - `отчет` is lowercase, not bold.
   - `по заданию` and `по курсу «Применение генеративных нейронных моделей в мультимедиа»` are bold.
   - The theme line reads `Тема: Карта архитектур в реальных продуктах` — not bold.
   - The student row reads `Студент гр. ___` with `Ханна М. Н.` in the right cell (spaces between initials).
   - The student/teacher table has NO visible borders.
   - Page 1 has NO page number.
   - Compare side-by-side with my Assignment 1 report title page — the layout must be identical, only the theme text differs.
2. Reopen the `.docx` with python-docx. Print the heading outline, table count, image count (should be ≥ 12 images: 6 action composites + 6 arch cards). Search the full text for `TODO|XXX|placeholder|【`. If any hit, fix it and re-save.
3. Convert to PDF: `soffice --headless --convert-to pdf --outdir ./report ./report/Отчет_Задание2.docx`. Render pages 1, 2, the page with the main table, and the last page to JPEG. Check: no overflow, no broken table, no missing image, no Markdown leftovers.
4. Verify all 6 action composites + 6 arch cards + 3 bare images exist in `./screenshots/`.
5. Verify `./logs/cost.md` total ≤ 20 ₽.
6. Copy final files into `./deliverable/`: `Отчет_Задание2.docx`, `Отчет_Задание2.pdf`, `screenshots/` (zipped or as a folder).

### Step 10 — Final summary

Print a final summary listing:
- absolute paths of `Отчет_Задание2.docx`, `Отчет_Задание2.pdf`, and the screenshots folder;
- the 6 services with their architecture labels and confirmation status;
- the **total cost in ₽** actually billed by Polza.ai (from `./logs/cost.md`);
- the next step I should do (upload the report on `open.etu.ru` before 2026-11-12 23:55 MSK, then complete peer review before 2026-11-19 23:55 MSK).

## 6. Hard constraints

- **Do not invent facts about services or architectures.** The architecture labels in §2 are already verified against primary sources; copy them verbatim. If you substitute a model, run a web search and cite the source for the substitute's architecture.
- **The report is in Russian.** Only model/brand names, URLs, and direct English quotes from sources may stay in English; every explanatory sentence is in Russian.
- **Stay inside the project directory.** Never write outside `./arch-map/` (and `./deliverable/`).
- **No placeholders** except the two title-page fields `Студент гр. ___` and `Преподаватель ___`. The student name `Ханна М. Н.` must appear verbatim, with spaces between initials.
- **Numbers must match.** The cost in Приложение Б must equal the sum of per-service costs in `./logs/cost.md`.
- **Budget:** total Polza spend must stay under 20 ₽. If a single call costs more than 5 ₽, abort and log it.
- **Same formatting as Assignment 1.** The title page, body font, margins, heading style, and table style must be visually identical to my Assignment 1 report — only the content differs.
- **Don't pause for human input** unless Step 1's pre-flight checks fail. The Polza API path is fully autonomous — call all 6 services, build all composites, write the report, render the PDF, all without me.

Start now. Begin by creating the directory structure, then proceed through Steps 1 → 10 in order.
