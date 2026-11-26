# Prompt for AI Agent — Coursework Assignment 3: Reference → Analysis → Prompt (via Polza.ai)

> Paste everything below this line into opencode desktop.

---

# TASK

You are an autonomous coding/agent assistant running in **opencode desktop** with full filesystem and shell access on my machine. Complete LETI coursework **Assignment 3** end-to-end, using the **Polza.ai** API for all model calls. Produce the final deliverables in `./deliverable/`.

## 1. Context (read this first)

I am a student at **St. Petersburg Electrotechnical University «ЛЭТИ» (LETI)**, course **«Применение генеративных нейронных моделей в мультимедиа»** (Prompt-002, осень 2026), кафедра ИС. The assignment below is taken verbatim from the course LMS page on `open.etu.ru`.

**Original assignment (Russian, verbatim):**

> **Задание 3. Референс → анализ → промпт**
> Срок сдачи — 12 ноября 2026, 23:55 MSK. Срок взаимного оценивания — 19 ноября 2026.
>
> 1. Выберите референсное изображение с выразительным стилем (собственное, из открытой лицензии или сгенерированное ранее). Укажите источник.
> 2. Загрузите его в мультимодальный чат-бот и попросите разобрать: композицию, цветовую палитру, освещение, технику/стиль, настроение. Сохраните ответ.
> 3. Попросите составить подробный промпт для генератора изображений на новый сюжет (например, «кот под дождём» или объект из вашей профессии) в стиле референса.
> 4. Сгенерируйте изображение по данному промпту. Затем сгенерируйте тот же сюжет по короткому «наивному» промпту без анализа стиля («кот под дождём»).
> 5. Сравните два результата с референсом.
>
> **Обязательные скриншоты:**
> - референс с указанием источника;
> - диалог: анализ стиля (промпт + ответ);
> - диалог: составленный промпт;
> - две генерации (по развёрнутому и по наивному промпту).
>
> **Структура отчёта:**
> - таблица сравнения: признак стиля (палитра, свет, композиция, техника) → есть в референсе → воспроизведён в генерации 1 → в генерации 2;
> - оценка точности переноса стиля (1–5) с обоснованием;
> - какие признаки стиля модель-аналитик описала неточно и как вы бы поправили промпт вручную;
> - в каких задачах вашей сферы этот приём экономит время.
>
> **Submission step:** «Приложите отчет и отправьте на проверку.»

**Today is 2026-11-10. Deadline is 2026-11-12 23:55 MSK.** Do not miss it. Peer review is due 2026-11-19.

### Choice of service: **Polza.ai** (OpenAI-compatible aggregator)

Polza.ai is a Russian AI-model aggregator. It is OpenAI-compatible, so the agent calls it directly with the OpenAI Python SDK — no browser, no queue, no human-in-the-loop.

- Endpoint base: `https://polza.ai/api/v1`
- Auth: `Authorization: Bearer $POLZA_API_KEY` (key starts with `pza_`)
- Vision LLM calls (image + text → text): `client.chat.completions.create(model=..., messages=[{role, content: [{type:"text",...}, {type:"image_url", image_url:{url:"data:image/jpeg;base64,..."}}]}])`
- Image generation calls (text → image): `client.images.generate(model=..., prompt=..., size="1024x1024")`

## 2. Reference image, models, and cost plan (FIXED, do not change)

### 2.1 Reference image — Vincent van Gogh, «The Starry Night» (1889)

- **Source:** Wikimedia Commons, public domain (work of art pre-1900; the photograph of the painting is also licensed by the Google Art Project under CC-BY-SA or public domain).
- **Direct URL to download:** `https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg`
- **Museum:** MoMA, New York (permanent collection).
- **Why this image:** one of the most distinctive styles in art history — swirling impasto brushstrokes, dominant cobalt-blue and cadmium-yellow palette, expressive sky, cypress tree silhouette. The style is strong enough that a good prompt should reproduce recognizable features, and weak enough that a naive prompt will completely miss them. This makes the comparison pedagogically clear.
- **Rationale for "открытая лицензия":** the painting entered the public domain no later than 70 years after the author's death (Van Gogh died in 1890; PD since 1961). The agent must cite this in the report.

### 2.2 Models

| Role | Polza model ID | Purpose | Architecture | Why this model |
|---|---|---|---|---|
| **Multimodal analyst** | `google/gemini-2.5-flash` | Analyze the reference image + compose the detailed prompt | Transformer (multimodal MoE) | Multimodal (accepts image_url), cheap, good at visual analysis. Confirmed transformer per Gemini tech report (arXiv 2403.05530). |
| **Image generator (BOTH generations)** | `bytedance/seedream-4` | Generate image 1 (detailed prompt) + image 2 (naive prompt) | Diffusion (rectified flow DiT) | Good style adherence; same model for both generations ensures the ONLY variable is the prompt (fair comparison). Confirmed diffusion per ByteDance Seed tech report. |

**IMPORTANT — fair comparison:** both images MUST be generated with the SAME model (`bytedance/seedream-4`), the SAME size (`1024x1024`), and ideally the SAME seed (if Polza exposes the `seed` parameter). The only difference between the two generations is the prompt. This is critical for the assignment's comparison to be valid.

### 2.3 New subject for generation

**«Кот под дождём»** (cat in the rain) — the default subject suggested in the assignment. This is a neutral, universally recognizable subject that lets the style transfer be the focus.

- **Naive prompt (generation 2):** `«Кот под дождём»` (or in English: `«A cat in the rain»`)
- **Detailed prompt (generation 1):** composed by the multimodal LLM in Step 3, based on the style analysis of the Van Gogh reference.

### 2.4 Cost estimate

| Item | Model | Estimated cost |
|---|---|---|
| Vision LLM call 1 (style analysis, ~800 tokens) | gemini-2.5-flash | ~2 ₽ |
| Vision LLM call 2 (prompt composition, ~400 tokens) | gemini-2.5-flash | ~1 ₽ |
| Image generation 1 (detailed prompt) | seedream-4 | 3.0 ₽ |
| Image generation 2 (naive prompt) | seedream-4 | 3.0 ₽ |
| **Total** | | **~9 ₽** (well under 100 ₽ min top-up) |

### 2.5 Substitution rule

Only if a model returns 404 / "model not available":
- For the multimodal analyst: substitute with `openai/gpt-4o` (also multimodal transformer).
- For the image generator: substitute with `tongyi-mai/z-image` (also diffusion, 1.4 ₽). If substituted, use the SAME substitute for BOTH generations.
- Document any substitution in `./logs/generation-method.md`. Do not silently change architectures.

## 3. Deliverables

Everything goes under `./ref-analysis/`. Final deliverables (copy to `./deliverable/` at the end):

1. `Отчет_Задание3.docx` — the report, **in Russian**, A4, Times New Roman 14 pt, 2 cm margins (formatting identical to Assignments 1 and 2 — see §6 below).
2. `Отчет_Задание3.pdf` — PDF rendering of the same report.
3. `screenshots/` — 6 screenshot composites:
   - `01_reference.png` — reference image with source caption
   - `02_dialog_analysis.png` — dialogue: style analysis (user prompt + LLM response)
   - `03_dialog_prompt.png` — dialogue: composed detailed prompt
   - `04_gen_detailed.png` — generation 1 (from the detailed prompt)
   - `05_gen_naive.png` — generation 2 (from the naive prompt)
   - `06_comparison_collage.png` — 3-panel collage: reference | gen 1 | gen 2
4. `logs/` — `reference.md`, `analysis.json`, `composed_prompt.txt`, `naive_prompt.txt`, `generation-method.md`, `worklog.md`, `cost.md`, `comparison.md`.

## 4. Working directory layout

```
./ref-analysis/
├── screenshots/      # 6 composites + 3 bare images (reference, gen1, gen2)
├── report/           # .docx + .pdf
├── logs/             # all JSON and MD logs
└── deliverable/      # final copies only
```

## 5. Step-by-step procedure

### Step 1 — Pre-flight checks

1. Verify `POLZA_API_KEY` is set: `echo "${POLZA_API_KEY:0:4}"` should print `pza_`. If empty, prompt me to set it.
2. Verify Python ≥ 3.10, Pillow, python-docx, requests, openai are installed. `pip install` anything missing.
3. Probe the API: `curl -sS https://polza.ai/api/v1/models -H "Authorization: Bearer $POLZA_API_KEY" | head -c 200` — expect JSON. If 401, stop and ask me.
4. Verify both model IDs exist: `google/gemini-2.5-flash` and `bytedance/seedream-4`.
5. Log all checks with timestamps into `./logs/worklog.md`.

### Step 2 — Download and prepare the reference image

```bash
curl -sSL -o ./screenshots/reference_raw.jpg \
  "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg"
```

Verify the download:
- File size > 50 KB (if smaller, the download failed — retry, or try the non-thumb URL `https://upload.wikimedia.org/wikipedia/commons/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg`).
- Open with Pillow: `Image.open("./screenshots/reference_raw.jpg")` — verify it's a valid JPEG.
- Resize to max 1024 px on the long side (to keep the base64 payload small for the API call). Save as `./screenshots/reference_1024.jpg`.

Save the source metadata to `./logs/reference.md`:
```
Title: The Starry Night
Artist: Vincent van Gogh
Year: 1889
Medium: Oil on canvas
Dimensions: 73.7 cm × 92.1 cm
Museum: Museum of Modern Art (MoMA), New York
Source: Wikimedia Commons
URL: https://commons.wikimedia.org/wiki/File:Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg
License: Public domain (Van Gogh died 1890; PD since 1961)
```

Build the reference screenshot composite `./screenshots/01_reference.png`:
- Top strip (60 px, dark #1A1A1A, white text): «Референсное изображение»
- Second strip (40 px, #F0F0F0, black text): «Vincent van Gogh, "The Starry Night" (1889) | Public domain | Wikimedia Commons»
- The reference image (centered, max 800 px wide)
- Bottom strip (40 px, #F0F0F0, small text): «Источник: https://commons.wikimedia.org/...»
- Use a Cyrillic-capable TTF font (`fc-list | grep -iE 'noto.*sans|dejavu'`).

### Step 3 — Multimodal style analysis (LLM call 1)

Write a Python script `./scripts/analyze_style.py`:

```python
from openai import OpenAI
import base64, json, pathlib, time

client = OpenAI(api_key=open("/path/to/.polza_key").read().strip(),
                base_url="https://polza.ai/api/v1")

# Encode the reference image as base64
img_b64 = base64.b64encode(pathlib.Path("./screenshots/reference_1024.jpg").read_bytes()).decode()
data_url = f"data:image/jpeg;base64,{img_b64}"

ANALYSIS_PROMPT = (
    "Перед вами знаменитая картина Винсента Ван Гога «Звёздная ночь» (1889). "
    "Проведите детальный анализ её стиля. Разберите отдельно:\n"
    "1. Композицию (расположение объектов, баланс, направление взгляда)\n"
    "2. Цветовую палитру (основные цвета, их соотношение, контрасты)\n"
    "3. Освещение (источники света, распределение светотени, яркость)\n"
    "4. Технику и стиль (мазок, фактура, импасто, направление линий)\n"
    "5. Настроение (эмоциональный тон, атмосфера)\n"
    "Отвечайте на русском языке, по каждому пункту — 2–3 предложения с конкретными деталями."
)

t0 = time.time()
r = client.chat.completions.create(
    model="google/gemini-2.5-flash",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": ANALYSIS_PROMPT},
            {"type": "image_url", "image_url": {"url": data_url}}
        ]
    }]
)
analysis_text = r.choices[0].message.content

pathlib.Path("./logs/analysis.json").write_text(json.dumps({
    "model": "google/gemini-2.5-flash",
    "prompt": ANALYSIS_PROMPT,
    "response": analysis_text,
    "elapsed": time.time() - t0,
    "usage": {"in": r.usage.prompt_tokens, "out": r.usage.completion_tokens}
}, ensure_ascii=False, indent=2))
print(analysis_text)
```

Save the full response to `./logs/analysis.json`. Build the dialogue screenshot composite `./screenshots/02_dialog_analysis.png`:
- Top strip (60 px, dark #1A1A1A, white text): «Диалог 1: Анализ стиля — google/gemini-2.5-flash»
- User message block (white, ~100 px): label «Пользователь:» bold, then the analysis prompt (wrapped, ~12 pt)
- Assistant response block (#FAFAFA, variable height up to 800 px): label «Модель:» bold, then the analysis text (wrapped, ~11 pt to fit)

### Step 4 — Compose the detailed prompt (LLM call 2, multi-turn)

Write `./scripts/compose_prompt.py` that continues the conversation:

```python
from openai import OpenAI
import base64, json, pathlib, time

client = OpenAI(api_key=..., base_url="https://polza.ai/api/v1")

img_b64 = base64.b64encode(pathlib.Path("./screenshots/reference_1024.jpg").read_bytes()).decode()
data_url = f"data:image/jpeg;base64,{img_b64}"

# Load the analysis from Step 3
analysis = json.loads(pathlib.Path("./logs/analysis.json").read_text())["response"]

COMPOSE_PROMPT = (
    "На основе вашего анализа стиля этой картины составьте подробный промпт "
    "для генератора изображений на новый сюжет: «кот под дождём». "
    "Изображение должно быть выполнено в стиле этого референса — "
    "с теми же цветовыми сочетаниями, техникой мазка, освещением и настроением. "
    "Промпт должен быть на английском языке (генераторы работают лучше на английском), "
    "содержать 4–6 предложений и включать конкретные описания: "
    "палитру, тип мазка, освещение, композицию, атмосферу. "
    "Не упоминайте имя Ван Гога и не копируйте картину — нужен новый сюжет в том же стиле."
)

t0 = time.time()
r = client.chat.completions.create(
    model="google/gemini-2.5-flash",
    messages=[
        {"role": "user", "content": [
            {"type": "text", "text": "Проанализируйте стиль этой картины."},
            {"type": "image_url", "image_url": {"url": data_url}}
        ]},
        {"role": "assistant", "content": analysis},
        {"role": "user", "content": COMPOSE_PROMPT}
    ]
)
composed_prompt = r.choices[0].message.content

pathlib.Path("./logs/composed_prompt.txt").write_text(composed_prompt)
pathlib.Path("./logs/compose_call.json").write_text(json.dumps({
    "model": "google/gemini-2.5-flash",
    "prompt": COMPOSE_PROMPT,
    "response": composed_prompt,
    "elapsed": time.time() - t0,
    "usage": {"in": r.usage.prompt_tokens, "out": r.usage.completion_tokens}
}, ensure_ascii=False, indent=2))
print(composed_prompt)
```

Save the composed prompt to `./logs/composed_prompt.txt`. Build the dialogue screenshot `./screenshots/03_dialog_prompt.png`:
- Top strip: «Диалог 2: Составленный промпт — google/gemini-2.5-flash»
- User message block: «Пользователь:» + the compose prompt instruction (wrapped)
- Assistant response block: «Модель:» + the composed prompt (wrapped, larger font ~13 pt since it's the key output)

Also write the naive prompt to `./logs/naive_prompt.txt`:
```
A cat in the rain
```

### Step 5 — Generate the two images

Write `./scripts/generate_images.py`:

```python
from openai import OpenAI
import base64, requests, pathlib, time, json

client = OpenAI(api_key=..., base_url="https://polza.ai/api/v1")

detailed_prompt = pathlib.Path("./logs/composed_prompt.txt").read_text().strip()
naive_prompt = pathlib.Path("./logs/naive_prompt.txt").read_text().strip()

# Use the SAME seed for both generations (if Polza supports it)
SEED = 42

for label, prompt in [("detailed", detailed_prompt), ("naive", naive_prompt)]:
    t0 = time.time()
    kwargs = {"model": "bytedance/seedream-4", "prompt": prompt, "size": "1024x1024", "n": 1}
    try:
        kwargs["seed"] = SEED  # may or may not be supported
    except Exception:
        pass
    r = client.images.generate(**kwargs)
    d = r.data[0]
    if getattr(d, "b64_json", None):
        img_bytes = base64.b64decode(d.b64_json)
    else:
        img_bytes = requests.get(d.url).content
    pathlib.Path(f"./screenshots/img_gen_{label}.png").write_bytes(img_bytes)
    pathlib.Path(f"./logs/gen_{label}.json").write_text(json.dumps({
        "label": label, "model": "bytedance/seedream-4",
        "prompt": prompt, "elapsed": time.time()-t0,
        "usage": getattr(r, "usage", None)
    }, ensure_ascii=False, indent=2))
    print(f"{label}: image saved ({len(img_bytes)} bytes)")
```

Build the two generation screenshot composites:

`./screenshots/04_gen_detailed.png`:
- Top strip (60 px, dark #1A1A1A, white text): «Генерация 1: подробный промпт — bytedance/seedream-4»
- Prompt block (white, ~120 px): label «Промпт:» bold + the FULL detailed prompt (wrapped, ~10 pt to fit)
- Generated image (1024×1024, centered)

`./screenshots/05_gen_naive.png`:
- Top strip: «Генерация 2: наивный промпт — bytedance/seedream-4»
- Prompt block: «Промпт:» + `A cat in the rain` (large font, ~16 pt)
- Generated image (1024×1024, centered)

### Step 6 — Build the 3-panel comparison collage

Use Pillow to build `./screenshots/06_comparison_collage.png`:
- Title bar (80 px, dark #1A1A1A, white text, ~18 pt): «Сравнение: референс | генерация 1 (подробный промпт) | генерация 2 (наивный промпт)»
- 3 panels side by side, each ~600 px wide × 600 px tall (resize each image to fit, preserve aspect, white background):
  - Panel 1: reference image — caption below: «Референс: Ван Гог, "Звёздная ночь"»
  - Panel 2: gen_detailed — caption: «Генерация 1 (подробный промпт)»
  - Panel 3: gen_naive — caption: «Генерация 2 (наивный промпт)»
- 16 px gutters, 24 px outer padding.
- Save at ~150 DPI equivalent.

### Step 7 — Style comparison analysis

In `./logs/comparison.md`, fill in the comparison table data:

**a) Main comparison table** (for the report's §4):

| Признак стиля | Есть в референсе | Воспроизведён в генерации 1 | Воспроизведён в генерации 2 |
|---|---|---|---|

Analyze the reference and both generations across these style features:
1. **Цветовая палитра** (dominant cobalt blue + cadmium yellow + touches of white/green)
2. **Освещение** (night scene, luminous moon and stars as light sources, glow effect)
3. **Композиция** (foreground cypress silhouette, village in lower third, swirling sky dominating upper 2/3)
4. **Техника/стиль** (impasto brushstrokes, swirling circular motions, thick paint texture, visible individual strokes)
5. **Настроение** (turbulent, dreamy, melancholic yet vibrant)

For each feature and each generation, write:
- «Да» or «Частично» or «Нет»
- A 1-sentence justification (e.g., «Палитра воспроизведена: доминируют синие и жёлтые тона, как в оригинале»)

**b) Style transfer accuracy score (1–5)** for each generation, with justification:
- Score for generation 1 (detailed prompt): X/5 — why
- Score for generation 2 (naive prompt): X/5 — why
- The delta between the two scores quantifies the value of the style-analysis step

**c) Inaccuracies in the analyst's description** (for the report's §5):
- Identify 2–3 style features that the multimodal LLM described inaccurately or vaguely in its analysis (Step 3)
- For each, explain what was wrong/missing and how you would manually fix the prompt
- Example: «Модель описала мазок как "короткие ритмичные" — на самом деле они длинные, закрученные, спиральные. В ручную правку промпта добавил бы: "long, swirling, spiral brushstrokes"»

**d) Time-saving applications in the student's sphere** (for the report's §6):
- The student's sphere is **PR / communications (связь с общественностью)** at LETI
- List 3–4 concrete tasks where "reference → analysis → prompt" saves time:
  1. Создание визуального контента для соцсетей университета в едином стиле (анализ брендового референса → промпт для серии постов)
  2. Производство рекламных баннеров для мероприятий в стиле фирменного дизайна
  3. Генерация иллюстраций для пресс-релизов, выдержанных в визуальной стилистике кампании
  4. Быстрое прототипирование визуальных концепций для презентаций и питч-деков
- For each: 2 sentences on HOW the technique saves time (e.g., «вместо подбора фильтров в Photoshop — один анализ референса и готовый промпт для серии из 10 изображений»)

### Step 8 — Write the report `Отчет_Задание3.docx`

Use `python-docx`. The report is **in Russian**. The formatting MUST be identical to Assignments 1 and 2.

#### 8.1 Title page — MUST match the official LETI template (same as Assignments 1 and 2)

**Global font for the entire title page:**
- Font family: **Times New Roman** (set explicitly on every run)
- Size: **14 pt** for every run (`w:sz w:val="28"` AND `w:szCs w:val="28"`)
- Italic OFF on every run

**Paragraph properties:**
- `w:spacing w:before="0" w:after="0"`, `w:ind w:firstLine="0"`
- Center alignment for header/footer blocks; LEFT alignment for table cells.

**Exact title-page content, top to bottom:**

1. `МИНОБРНАУКИ РОССИИ` — centered, **bold**
2. `Санкт-Петербургский государственный электротехнический` — centered, **bold**
3. `университет «ЛЭТИ» им. В.И. Ульянова (Ленина)` — centered, **bold**
4. `Кафедра ИС` — centered, **bold**
5. Three empty paragraphs (TNR 14pt, no bold)
6. `отчет` — centered, **NOT bold**, lowercase
7. `по заданию` — centered, **bold**
8. `по курсу «Применение генеративных нейронных моделей` — centered, **bold**
9. `в мультимедиа»` — centered, **bold**
10. `Тема: Референс → анализ → промпт` — centered, **NOT bold**
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

#### 8.2 Body formatting rules (identical to Assignments 1 and 2)

- A4, margins 2 cm.
- Body font: **Times New Roman 14 pt** throughout.
- Body paragraphs: first-line indent **1.25 cm** (709 dxa), justified, single line spacing, `before=0 after=60`.
- Headings: TNR 14 pt, **bold**, centered, `before=240 after=160`. Sub-headings: TNR 14 pt bold, left-aligned.
- Captions under figures: TNR 12 pt italic, centered.
- Tables: TNR 12 pt body / 12 pt bold header row, light grey (#F2F2F2) header shading, repeat header row, thin black borders.
- Page numbers: bottom-center, starting visibly from page 2. Page 1 has NO page number. Use a section break after the title page.
- No `TODO`, `XXX`, `placeholder`, `【…】` anywhere. The only `___` allowed are the two title-page fields.

#### 8.3 Required body structure

1. **1. Введение** (~150 слов) — purpose: testing the "reference → analysis → prompt" pipeline for style transfer; why this matters for practical use of generative models; what the experiment tests (does style analysis improve generation quality vs naive prompting).

2. **2. Референсное изображение** — describe the reference:
   - Title, artist, year, medium, museum
   - Source URL and license (public domain)
   - Why this image was chosen (distinctive style, recognizable features)
   - Embed `01_reference.png` at ~14 cm width, captioned `Рисунок 1 — Референсное изображение: В. Ван Гог, «Звёздная ночь» (1889)`

3. **3. Анализ стиля и составление промпта** — two sub-sections:
   - **3.1. Анализ стиля мультимодальной моделью** — describe the LLM used (Gemini 2.5 Flash, transformer, multimodal), the analysis prompt, and the key points of the LLM's response (composition, palette, lighting, technique, mood). Embed `02_dialog_analysis.png` at ~14 cm width, captioned `Рисунок 2 — Диалог: анализ стиля референса`.
   - **3.2. Составленный промпт** — present the full detailed prompt composed by the LLM (in a code block or monospace). Embed `03_dialog_prompt.png`, captioned `Рисунок 3 — Диалог: составленный подробный промпт`.

4. **4. Сравнение генераций** — two sub-sections:
   - **4.1. Две генерации** — describe both generations. Embed `04_gen_detailed.png` (caption `Рисунок 4 — Генерация 1: по подробному промпту`) and `05_gen_naive.png` (caption `Рисунок 5 — Генерация 2: по наивному промпту`). Embed `06_comparison_collage.png` (caption `Рисунок 6 — Сравнительный коллаж: референс | генерация 1 | генерация 2`).
   - **4.2. Таблица сравнения** — the **main required table**:

     | Признак стиля | Есть в референсе | Воспроизведён в генерации 1 | Воспроизведён в генерации 2 |

     Fill from `./logs/comparison.md` §a. One row per feature (5 rows: палитра, свет, композиция, техника, настроение).

5. **5. Оценка точности переноса стиля и неточности анализа** — two parts:
   - **5.1. Оценка точности (1–5)** — score for generation 1, score for generation 2, with 3–4 sentences of justification each. Explain the delta. Use the data from `./logs/comparison.md` §b.
   - **5.2. Неточности модели-аналитика** — list 2–3 style features the LLM described inaccurately, and for each, the manual prompt fix. Use data from `./logs/comparison.md` §c.

6. **6. Применение в сфере связи с общественностью** — discuss 3–4 concrete PR/communications tasks where "reference → analysis → prompt" saves time. Use data from `./logs/comparison.md` §d. ~250 words.

7. **Приложение А** — full prompts and responses:
   - The analysis prompt (verbatim)
   - The LLM's full analysis response (verbatim)
   - The compose prompt instruction (verbatim)
   - The LLM's composed detailed prompt (verbatim)
   - The naive prompt (verbatim)

8. **Приложение Б** — work log + cost table: tool versions, API calls, timestamps, per-call cost, total cost. From `./logs/worklog.md` and `./logs/cost.md`.

### Step 9 — Self-check (mandatory)

1. **Title-page format check (highest priority).** Render page 1 of the PDF to JPEG at 100 DPI and verify visually:
   - The 4-line university header is bold, centered, TNR 14pt.
   - `отчет` is lowercase, not bold.
   - `по заданию` and `по курсу «Применение генеративных нейронных моделей в мультимедиа»` are bold.
   - The theme line reads `Тема: Референс → анализ → промпт` — not bold. (Verify the → arrow renders correctly.)
   - The student row reads `Студент гр. ___` with `Ханна М. Н.` in the right cell (spaces between initials).
   - The student/teacher table has NO visible borders.
   - Page 1 has NO page number.
   - Compare side-by-side with my Assignment 2 report title page — the layout must be identical, only the theme text differs.

2. Reopen the `.docx` with python-docx. Print the heading outline, table count, image count (should be ≥ 6 images). Search the full text for `TODO|XXX|placeholder|【`. If any hit, fix it and re-save.

3. Convert to PDF: `soffice --headless --convert-to pdf --outdir ./report ./report/Отчет_Задание3.docx`. Render pages 1, 2, the page with the comparison table, and the last page to JPEG. Check: no overflow, no broken table, no missing image, no Markdown leftovers (`**`, `|---|`, `#`).

4. Verify all 6 screenshot composites + 3 bare images (reference, gen_detailed, gen_naive) exist in `./screenshots/`.

5. Verify `./logs/cost.md` total ≤ 15 ₽.

6. Copy final files into `./deliverable/`: `Отчет_Задание3.docx`, `Отчет_Задание3.pdf`, `screenshots/` (zipped or as a folder).

### Step 10 — Final summary

Print a final summary listing:
- absolute paths of `Отчет_Задание3.docx`, `Отчет_Задание3.pdf`, and the screenshots folder;
- the two style-transfer scores (generation 1 and generation 2), with a one-line reason each;
- the **total cost in ₽** actually billed by Polza.ai (from `./logs/cost.md`);
- the next step I should do (upload the report on `open.etu.ru` before 2026-11-12 23:55 MSK, then complete peer review before 2026-11-19 23:55 MSK).

## 6. Hard constraints

- **Do not invent facts about the reference image or the models.** The Van Gogh painting is public domain; cite the source. The architecture labels for Gemini 2.5 Flash (transformer MoE) and Seedream 4 (diffusion flow-matching) are already verified — copy them verbatim.
- **Both generations MUST use the same model (`bytedance/seedream-4`), the same size, and ideally the same seed.** The ONLY variable between the two generations is the prompt. If you use different models, the comparison is invalid and the assignment is failed.
- **The report is in Russian.** Only the composed detailed prompt (which the LLM writes in English for the image generator), the naive prompt, model/brand names, URLs, and direct English quotes from sources may stay in English. Every explanatory sentence is in Russian.
- **Stay inside the project directory.** Never write outside `./ref-analysis/` (and `./deliverable/`).
- **No placeholders** except the two title-page fields `Студент гр. ___` and `Преподаватель ___`. The student name `Ханна М. Н.` must appear verbatim, with spaces between initials.
- **Budget:** total Polza spend must stay under 15 ₽. If a single call costs more than 5 ₽, abort and log it.
- **Same formatting as Assignments 1 and 2.** The title page, body font, margins, heading style, and table style must be visually identical to my Assignment 1 and 2 reports — only the content differs.
- **Don't pause for human input** unless Step 1's pre-flight checks fail. The Polza API path is fully autonomous — download reference, analyze, compose prompt, generate both images, write the report, render the PDF, all without me.

Start now. Begin by creating the directory structure, then proceed through Steps 1 → 10 in order.
