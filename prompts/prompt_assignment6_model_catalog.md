# Prompt for AI Agent — Coursework Assignment 6: Model Catalog Analysis

> Paste everything below this line into opencode desktop.

---

# TASK

You are an autonomous coding/agent assistant running in **opencode desktop** with full filesystem and shell access on my machine. Complete LETI coursework **Assignment 6** end-to-end using the public Hugging Face API. Produce the final deliverables in `./deliverable/`.

## 1. Context (read this first)

I am a student at **St. Petersburg Electrotechnical University «ЛЭТИ» (LETI)**, course **«Применение генеративных нейронных моделей в мультимедиа»** (Prompt-002, осень 2026), кафедра ИС. The assignment below is from the course LMS.

**Original assignment (Russian, verbatim):**

> **Задание 6. Каталог моделей**
> Срок сдачи — 12 ноября 2026, 23:55 MSK. Срок взаимного оценивания — 19 ноября 2026.
>
> 1. Откройте открытый каталог моделей (например, Hugging Face Models) и используйте фильтр по задачам.
> 2. Для каждого из трёх направлений из видео — компьютерное зрение, генерация контента, анализ данных — найдите по 2 модели с разной узкой специализацией (например, детекция объектов и распознавание эмоций; генерация музыки и генерация кода; анализ тональности и классификация медицинских текстов).
> 3. Откройте карточку каждой из 6 моделей и зафиксируйте: задача, тип входа/выхода, на каких данных обучена, размер, лицензия, пример использования.
> 4. Если в карточке есть онлайн-демо — запустите его с собственным примером и заскриньте результат (минимум для 2 моделей).
>
> **Обязательные скриншоты:**
> - страница фильтра по задачам;
> - 6 карточек моделей;
> - 2 запущенных демо с результатом.
>
> **Структура отчёта:**
> - таблица 6 моделей: направление → специализация → вход → выход → данные обучения → размер → лицензия;
> - схема «дерево специализаций» (можно от руки/в любом редакторе) с размещением найденных моделей;
> - для 2 протестированных моделей: справились ли с вашим примером, что ограничивает их применение;
> - какие 2 модели из каталога вы бы включили в собственный мультимедиа-проект и для какого этапа.

**Today is 2026-11-10. Deadline is 2026-11-12 23:55 MSK.** Do not miss it. Peer review is due 2026-11-19.

### Three directions from the course lectures

From lecture 2.5 («Выбор и специализация предобученных нейросетей»), the three AI specialization trees are:

1. **Компьютерное зрение (Computer Vision):** face recognition, medical diagnostics, OCR, industrial inspection.
2. **Генерация контента (Content Generation):** code generation, image stylization, music generation.
3. **Анализ данных (Data Analysis):** financial sector (risk, fraud), scientific research (genomics, climate).

Relevant course concepts to cite:
- «Специализация инструментов» — each task has its own model (lecture 2.5)
- «Узкоспециализированная модель» vs «универсальная модель» (lecture 2.5)
- «Компромисс: точность vs скорость» (lecture 2.5)
- «Краевые случаи» — edge cases (lecture 2.4)
- «Предобученная модель» + «дообучение» (lecture 2.6)

## 2. Model selection (FIXED — do not change)

Six models, two per direction, each with a different narrow specialization:

### Direction 1: Компьютерное зрение (Computer Vision)

| # | Model ID | Specialization | Why chosen |
|---|---|---|---|
| M1 | `facebook/detr-resnet-50` | **Детекция объектов** (object detection) | DETR = DEtection TRansformer; classic CV model; 91 COCO categories; Apache 2.0; has HF Inference API demo |
| M2 | `dima806/facial_emotions_image_detection` | **Распознавание эмоций** (facial emotion recognition) | ViT-based; 6 emotion classes (angry, disgust, fear, happy, neutral, sad); MIT license; trained on FER2013 |

### Direction 2: Генерация контента (Content Generation)

| # | Model ID | Specialization | Why chosen |
|---|---|---|---|
| M3 | `facebook/musicgen-small` | **Генерация музыки** (music generation) | MusicGen; 300M params; generates audio from text prompts; CC-BY-NC-4.0; trained on licensed music data |
| M4 | `Salesforce/codegen-350M-mono` | **Генерация кода** (code generation) | CodeGen; 350M params; generates Python code from natural language; BSD-3-Clause; trained on The Stack + Pile |

### Direction 3: Анализ данных (Data Analysis)

| # | Model ID | Specialization | Why chosen |
|---|---|---|---|
| M5 | `cardiffnlp/twitter-roberta-base-sentiment` | **Анализ тональности** (sentiment analysis) | RoBERTa; 125M params; 3 classes (negative, neutral, positive); Apache 2.0; trained on Twitter data; has HF Inference API demo |
| M6 | `d4data/biomedical-ner-all` | **Медицинский NER** (biomedical named entity recognition) | BioBERT-based; extracts diseases, medications, anatomy from clinical text; Apache 2.0; trained on biomedical corpora |

### Two models for live demo testing

| Demo # | Model | Input type | Custom test input |
|---|---|---|---|
| D1 | `facebook/detr-resnet-50` | Image | A photo of a street scene with people and cars — use a CC0 image from Unsplash (e.g., `https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=640`) |
| D2 | `cardiffnlp/twitter-roberta-base-sentiment` | Text | "I absolutely love the new AI course on prompt engineering — it's incredibly useful and well-structured!" (English text, relevant to the student's context) |

### Substitution rule

If any model ID returns 404 or is inaccessible, substitute with a similar model in the SAME direction + specialization. Document any substitution in `./logs/substitution.md`. Do not change the direction or specialization.

## 3. Deliverables

Everything goes under `./model-catalog/`. Final deliverables (copy to `./deliverable/` at the end):

1. `Отчет_Задание6.docx` — the report, **in Russian**, A4, Times New Roman 14 pt, 2 cm margins (formatting identical to Assignments 1–5).
2. `Отчет_Задание6.pdf` — PDF rendering.
3. `screenshots/` — 9 screenshot composites:
   - `01_task_filter.png` — task filter page (HF Models with filters)
   - `02_card_M1.png` … `07_card_M6.png` — 6 model card composites
   - `08_demo_M1.png` — demo result for DETR (object detection)
   - `09_demo_M5.png` — demo result for sentiment analysis
   - `10_tree_diagram.png` — specialization tree diagram
4. `logs/` — `model_metadata/` (6 JSON files), `demo_results/` (2 JSON files), `worklog.md`.

## 4. Working directory layout

```
./model-catalog/
├── screenshots/         # 10 composites
├── report/              # .docx + .pdf
├── logs/
│   ├── model_metadata/  # M1.json ... M6.json
│   ├── demo_results/    # D1.json, D2.json
│   └── worklog.md
└── deliverable/         # final copies only
```

## 5. Step-by-step procedure

### Step 1 — Pre-flight checks

1. Verify Python ≥ 3.10, Pillow, python-docx, requests are installed. `pip install` anything missing. Also `pip install huggingface_hub` (for inference API, optional).
2. Verify internet access to Hugging Face: `curl -sS -o /dev/null -w "%{http_code}" https://huggingface.co/api/models/facebook/detr-resnet-50` — expect 200.
3. Check if `HF_TOKEN` env var is set (optional — for inference API demos). If not set, the demos will use the free tier (may be rate-limited) or fall back to card examples.
4. Log all checks into `./logs/worklog.md`.

### Step 2 — Fetch the task filter page

The Hugging Face Models page supports task filtering at `https://huggingface.co/models?pipeline_tag=<task>`. Fetch the list of available task tags:

```bash
curl -sS "https://huggingface.co/api/models?limit=1" | python -c "import sys,json; print(json.dumps(json.load(sys.stdin), indent=2))" | head -20
```

Also fetch model counts per task:
```bash
curl -sS "https://huggingface.co/api/models?filter=object-detection&limit=1" -o /dev/null -w "%{http_code}"
```

Build the task filter composite `./screenshots/01_task_filter.png`:
- Title bar (80 px, dark #1A1A1A, white text, ~20 pt): «Каталог моделей Hugging Face: фильтр по задачам»
- Sub-bar (40 px, #F0F0F0): «URL: https://huggingface.co/models»
- Three columns, one per direction:
  - **Компьютерное зрение:** list the task tags: `object-detection`, `image-classification`, `face-recognition`, `image-segmentation`
  - **Генерация контента:** `text-to-image`, `text-to-audio`, `text-generation`, `code-generation`
  - **Анализ данных:** `text-classification`, `token-classification`, `sentiment-analysis`, `tabular-classification`
- Each task tag in a pill-shaped badge (colored background)
- The selected tasks (for our 6 models) highlighted with a ★ marker
- Footer bar: «Источник: huggingface.co/models — открытый каталог, 1 000 000+ моделей»

### Step 3 — Fetch 6 model cards

For each of the 6 models, fetch:
1. Model metadata: `curl -sS "https://huggingface.co/api/models/{model_id}" -o ./logs/model_metadata/M{n}.json`
2. Model card README: `curl -sS "https://huggingface.co/{model_id}/raw/main/README.md" -o ./logs/model_metadata/M{n}_readme.md`

Parse each metadata JSON and extract:
- `id` — model ID
- `pipeline_tag` — task type (e.g., `object-detection`, `text-classification`)
- `tags` — includes license, framework, etc.
- `downloads` — total downloads
- `likes` — community likes
- `library_name` — e.g., `transformers`
- `config.model_type` — architecture type (e.g., `detr`, `vit`, `roberta`)

From the README, extract:
- Task description
- Input/output types
- Training data description
- Model size (parameters)
- License
- Example usage code
- Any limitations mentioned

For each model, compile a structured record in `./logs/model_metadata/M{n}_parsed.json`:
```json
{
  "id": "facebook/detr-resnet-50",
  "direction": "Компьютерное зрение",
  "specialization": "Детекция объектов",
  "task": "Object detection — detects and localizes objects in images",
  "input_type": "Image (RGB, any resolution)",
  "output_type": "List of bounding boxes with labels and confidence scores (91 COCO categories)",
  "training_data": "COCO 2017 dataset (118K images, 91 object categories)",
  "model_size": "41M parameters (backbone: ResNet-50 + transformer encoder-decoder)",
  "license": "Apache 2.0",
  "example_use": "Detecting objects in surveillance footage, autonomous driving, retail analytics",
  "downloads": "...",
  "likes": "...",
  "url": "https://huggingface.co/facebook/detr-resnet-50"
}
```

### Step 4 — Build 6 model card composites

For each model M1–M6, build a card composite `./screenshots/0{N}_card_M{n}.png` (~1600×1200 px):

- Title bar (60 px, dark #1A1A1A, white text): «Карточка модели: {model_id}»
- Sub-bar (40 px, #F0F0F0): «Направление: {direction} | Специализация: {specialization}»
- Two-column "card" layout (white background):
  - Left column (label, bold ~13 pt): «Задача», «Тип входа», «Тип выхода», «Данные обучения», «Размер», «Лицензия», «Пример использования», «Загрузок», «Лайков»
  - Right column (value, regular ~13 pt): the values from the parsed JSON
- Bottom bar (40 px, #F0F0F0, small): «URL: https://huggingface.co/{model_id}»
- Use TNR or Noto Sans font

### Step 5 — Run 2 live demos

#### Demo D1: Object Detection (`facebook/detr-resnet-50`)

Write `./scripts/run_demo_detr.py`:

```python
import requests, json, pathlib, base64
from PIL import Image, ImageDraw, ImageFont
import io

# Download a CC0 test image from Unsplash
img_url = "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=640"
img_bytes = requests.get(img_url, timeout=30).content
pathlib.Path("./logs/demo_results/test_image.jpg").write_bytes(img_bytes)

# Run inference via HF Inference API
API_URL = "https://api-inference.huggingface.co/models/facebook/detr-resnet-50"
headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}

response = requests.post(API_URL, headers=headers, data=img_bytes)
result = response.json()

# Save raw results
pathlib.Path("./logs/demo_results/D1.json").write_text(json.dumps({
    "model": "facebook/detr-resnet-50",
    "input_url": img_url,
    "input_description": "Urban street scene with people, cars, and buildings (Unsplash, CC0)",
    "output": result,
    "status_code": response.status_code
}, ensure_ascii=False, indent=2))

# Draw bounding boxes on the image
img = Image.open(io.BytesIO(img_bytes))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

for det in result:
    box = det["box"]
    label = det["label"]
    score = det["score"]
    x1, y1, x2, y2 = box["xmin"], box["ymin"], box["xmax"], box["ymax"]
    draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
    draw.text((x1, y1 - 16), f"{label} {score:.2f}", fill="red", font=font)

img.save("./logs/demo_results/D1_annotated.jpg")
print(f"Detected {len(result)} objects")
```

**If the HF Inference API requires a token and none is set:** fall back to using the model card's example output. Fetch the README, find the example image/results, and build the composite from those. Note in the report that the demo was run using the card's example (not live inference).

Build the demo composite `./screenshots/08_demo_M1.png`:
- Title bar (60 px, dark #1A1A1A, white text): «Демо: facebook/detr-resnet-50 — детекция объектов»
- Left panel: the original test image (with caption «Вход: уличная сцена (Unsplash, CC0)»)
- Right panel: the annotated image with bounding boxes (with caption «Выход: обнаруженные объекты с bounding boxes»)
- Bottom bar: list of detected objects with confidence scores: «person 0.98, car 0.95, bicycle 0.87, ...»

#### Demo D2: Sentiment Analysis (`cardiffnlp/twitter-roberta-base-sentiment`)

Write `./scripts/run_demo_sentiment.py`:

```python
import requests, json, pathlib

text = "I absolutely love the new AI course on prompt engineering — it's incredibly useful and well-structured!"

API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment"
headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}

response = requests.post(API_URL, headers=headers, json={"inputs": text})
result = response.json()

pathlib.Path("./logs/demo_results/D2.json").write_text(json.dumps({
    "model": "cardiffnlp/twitter-roberta-base-sentiment",
    "input_text": text,
    "output": result,
    "status_code": response.status_code
}, ensure_ascii=False, indent=2))
```

Build the demo composite `./screenshots/09_demo_M5.png`:
- Title bar (60 px, dark #1A1A1A, white text): «Демо: cardiffnlp/twitter-roberta-base-sentiment — анализ тональности»
- Input block: «Вход:» + the test text in quotes (~14 pt)
- Output block: «Выход:» + a bar chart showing the 3 sentiment scores:
  - negative: X%
  - neutral: X%
  - positive: X%
  (Use colored bars: red for negative, grey for neutral, green for positive)
- Bottom bar: «Итог: positive (X% уверенности)»

### Step 6 — Build the specialization tree diagram

Build `./screenshots/10_tree_diagram.png` using Pillow (~1800×1400 px):

- Title bar (80 px, dark #1A1A1A, white text, ~20 pt): «Дерево специализаций AI-моделей»
- Tree structure (top-down, 3 levels):

```
                    [AI-модели]
                        |
        +---------------+---------------+
        |               |              |
[Компьютерное        [Генерация      [Анализ
    зрение]           контента]       данных]
    |                   |               |
  +-+                 +-+             +-+
  | |                 | |             | |
Детек- Распо-       Музы- Код       То-  Мед.
ция   знав.         ка   ген.      нальн. NER
объ.  эмоций       ген.             анализ
  | |                 | |             | |
M1 M2               M3 M4           M5 M6
```

- Each node is a rounded rectangle with the label inside
- The 6 leaf nodes (M1–M6) are colored boxes showing the model ID
- Use distinct colors per direction: blue for CV, green for Gen, orange for Data
- Connect with lines (not arrows)
- Use a Cyrillic-capable TTF font

### Step 7 — Write the analysis files

In `./logs/analysis.md`:

**a) For the 2 tested models — did they handle the example, what limits their application:**

For D1 (DETR object detection):
- Did it detect the expected objects? (people, cars, etc.)
- What confidence scores? (above 0.5 = reliable, below = uncertain)
- Limitations:
  - Only 91 COCO categories (cannot detect objects outside these, e.g., specific logos, UI elements)
  - Trained on natural images (may fail on artistic/synthetic images)
  - Resolution sensitivity (small objects may be missed)
  - Real-time performance (DETR is slower than YOLO for real-time use)
- Course concept link: «краевые случаи» (lecture 2.4) — uncommon scenes or objects are edge cases

For D2 (sentiment analysis):
- Did it correctly identify the sentiment? (the test text is clearly positive)
- Confidence scores
- Limitations:
  - Trained on Twitter data (may not generalize to formal/academic/medical text)
  - Only 3 classes (no nuanced emotions like sarcasm, irony)
  - Language: English only (cannot analyze Russian text)
  - Context blindness (cannot detect sarcasm or mixed sentiment)
- Course concept link: «специфика задачи» (lecture 2.5) — model is specialized to Twitter-style short text

**b) Which 2 models would you include in your own multimedia project, and for which stage:**

The student's sphere is **PR/communications (связь с общественностью)** at LETI. A multimedia PR project could be: **автоматизированная система мониторинга медиаконтента** (automated media content monitoring system).

Recommended 2 models:

1. **`facebook/detr-resnet-50` (object detection)** — for the **content analysis stage**:
   - Automatically detect objects in social media images (logos, products, people, scenes)
   - Helps categorize user-generated content for brand monitoring
   - Stage: входной анализ изображений в медиатеке

2. **`cardiffnlp/twitter-roberta-base-sentiment` (sentiment analysis)** — for the **text analysis stage**:
   - Monitor sentiment of social media posts mentioning the brand/organization
   - Detect PR crises early (spike in negative sentiment)
   - Stage: анализ тональности текстовых упоминаний в соцсетях

Justification (3–4 sentences): these two models cover the two main content types in PR (images + text), are both Apache 2.0 (commercial use allowed), are lightweight enough for production (41M + 125M params), and cover complementary tasks (visual + textual analysis). Together they form the core of a media monitoring pipeline. Course concept: «специализация инструментов» (lecture 2.5) — each model does one thing well.

### Step 8 — Write the report `Отчет_Задание6.docx`

Use `python-docx`. The report is **in Russian**. Formatting identical to Assignments 1–5.

#### 8.1 Title page — MUST match the official LETI template

(Same as Assignments 1–5. Theme line: `Тема: Каталог моделей машинного обучения`. Student name: `Ханна М. Н.`. All other elements identical.)

**Exact title-page content (lines 6–10):**
6. `отчет` — centered, NOT bold, lowercase
7. `по заданию` — centered, bold
8. `по курсу «Применение генеративных нейронных моделей` — centered, bold
9. `в мультимедиа»` — centered, bold
10. `Тема: Каталог моделей машинного обучения` — centered, NOT bold

(The rest of the title page — header, table, footer — is identical to Assignments 1–5.)

#### 8.2 Body formatting rules

(Same as Assignments 1–5: A4, margins 2 cm, TNR 14 pt throughout, first-line indent 1.25 cm, justified, headings bold centered, captions TNR 12 pt italic, page numbers from page 2, no `___` except the two title-page fields.)

#### 8.3 Required body structure

1. **1. Введение** (~150 слов) — purpose: mapping the Hugging Face model catalog across three AI directions (CV, content generation, data analysis); understanding model specialization; selecting models for a PR multimedia project.

2. **2. Страница фильтра по задачам** — describe the HF Models catalog, the task filter system, and how models were selected. Embed `01_task_filter.png` at ~14 cm width, captioned `Рисунок 1 — Страница фильтра по задачам в каталоге Hugging Face`.

3. **3. Таблица 6 моделей** — the **main required table**:

   | Направление | Специализация | Модель | Вход | Выход | Данные обучения | Размер | Лицензия |

   One row per model (6 rows). Fill from the parsed metadata.

4. **4. Карточки моделей** — six sub-sections 4.1–4.6, one per model. Each:
   - Model ID and URL
   - Brief description (2–3 sentences): task, architecture, training data
   - Embed the card composite at ~14 cm width, captioned `Рисунок N — Карточка модели: {model_id}`
   - Note any limitations mentioned in the card

5. **5. Дерево специализаций** — embed `10_tree_diagram.png` at ~15 cm width, captioned `Рисунок 8 — Дерево специализаций AI-моделей с размещением найденных моделей`. Brief paragraph explaining the tree structure.

6. **6. Демонстрации моделей** — two sub-sections:
   - **6.1. Демо: детекция объектов (facebook/detr-resnet-50)** — embed `08_demo_M1.png`, captioned `Рисунок 9 — Демо: детекция объектов на тестовом изображении`. Describe: what input was used, what the model detected, confidence scores. Did it handle the example? What limits its application? (from `./logs/analysis.md` §a D1)
   - **6.2. Демо: анализ тональности (cardiffnlp/twitter-roberta-base-sentiment)** — embed `09_demo_M5.png`, captioned `Рисунок 10 — Демо: анализ тональности тестового текста`. Describe: input text, output sentiment, confidence. Did it handle the example? What limits its application? (from `./logs/analysis.md` §a D2)

7. **7. Выбор моделей для мультимедиа-проекта** — describe the 2 recommended models (from `./logs/analysis.md` §b):
   - Which 2 models: DETR + sentiment analysis
   - For which project: automated media content monitoring system for PR
   - For which stage: DETR for image analysis, sentiment for text analysis
   - Justification (3–4 sentences with course concept links)

8. **Приложение А** — full metadata for all 6 models (structured tables or JSON formatted).

9. **Приложение Б** — work log: tool versions, API calls, timestamps, any substitutions. From `./logs/worklog.md`.

### Step 9 — Self-check (mandatory)

1. **Title-page format check (highest priority).** Render page 1 of the PDF to JPEG at 100 DPI and verify visually:
   - The 4-line university header is bold, centered, TNR 14pt.
   - `отчет` is lowercase, not bold.
   - `по заданию` and `по курсу «Применение генеративных нейронных моделей в мультимедиа»` are bold.
   - The theme line reads `Тема: Каталог моделей машинного обучения` — not bold.
   - The student row reads `Студент гр. ___` with `Ханна М. Н.` in the right cell (spaces between initials).
   - Page 1 has NO page number.

2. Reopen the `.docx` with python-docx. Print the heading outline, table count, image count (should be ≥ 10 images: 1 filter + 6 cards + 2 demos + 1 tree). Search the full text for `TODO|XXX|placeholder|【`. If any hit, fix it.

3. Convert to PDF. Render pages 1, 2, the page with the main table, and the last page to JPEG. Check: no overflow, no broken table, no missing image, no Markdown leftovers.

4. Verify all 10 screenshot composites exist in `./screenshots/`.

5. Copy final files into `./deliverable/`: `Отчет_Задание6.docx`, `Отчет_Задание6.pdf`, `screenshots/` (zipped or as a folder).

### Step 10 — Final summary

Print a final summary listing:
- absolute paths of `Отчет_Задание6.docx`, `Отчет_Задание6.pdf`, and the screenshots folder;
- the 6 models with their direction + specialization;
- whether the 2 demos ran successfully (or fell back to card examples);
- the 2 recommended models for the PR multimedia project;
- the next step I should do (upload the report on `open.etu.ru` before 2026-11-12 23:55 MSK, then complete peer review before 2026-11-19 23:55 MSK).

## 6. Hard constraints

- **Do not invent facts about models.** All metadata (task, size, license, training data) must come from the actual Hugging Face model cards. If a field is not in the card, say «не указано» rather than guessing.
- **All 6 model cards must be REAL.** Fetch actual metadata from `https://huggingface.co/api/models/{id}`. If a model returns 404, use the substitution rule.
- **The 2 demos must use REAL input.** For D1, download a real CC0 image. For D2, use a real custom text. Do not fabricate demo results.
- **If the HF Inference API is unavailable** (no token, rate-limited, model not loaded): fall back to the model card's example output. Note this in the report: «демо запущено на примере из карточки модели, т.к. Inference API был недоступен».
- **The report is in Russian.** Only model IDs, URLs, and direct English quotes from model cards may stay in English.
- **Stay inside the project directory.** Never write outside `./model-catalog/` (and `./deliverable/`).
- **No placeholders** except the two title-page fields `Студент гр. ___` and `Преподаватель ___`. The student name `Ханна М. Н.` must appear verbatim, with spaces between initials.
- **No Polza.ai API needed.** This assignment uses public Hugging Face APIs only. No cost.
- **Same formatting as Assignments 1–5.** The title page, body font, margins, heading style, and table style must be visually identical to my previous reports — only the content differs.
- **Don't pause for human input** unless Step 1's pre-flight checks fail (no internet access to Hugging Face).

Start now. Begin by creating the directory structure, then proceed through Steps 1 → 10 in order.
