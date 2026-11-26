# Prompt for AI Agent — Coursework Assignment 5: Dataset Labeling for Classification

> Paste everything below this line into opencode desktop.

---

# TASK

You are an autonomous coding/agent assistant running in **opencode desktop** with full filesystem and shell access on my machine. Complete LETI coursework **Assignment 5** end-to-end, using the **Polza.ai** API for image generation and blind annotation. Produce the final deliverables in `./deliverable/`.

## 1. Context (read this first)

I am a student at **St. Petersburg Electrotechnical University «ЛЭТИ» (LETI)**, course **«Применение генеративных нейронных моделей в мультимедиа»** (Prompt-002, осень 2026), кафедра ИС. The assignment below is taken from the course LMS.

**Original assignment (Russian, verbatim):**

> **Задание 5. Разметка датасета для классификации**
> Срок сдачи — 12 ноября 2026, 23:55 MSK. Срок взаимного оценивания — 19 ноября 2026.
>
> 1. Выберите задачу классификации с двумя-тремя классами из вашей сферы: например, «афиша / обложка книги / постер фильма», «архитектура классицизм / модерн / конструктивизм», «текст новостной / рекламный / научный».
> 2. Соберите 24–30 объектов (по 8–10 на класс): собственные фото, открытые источники с указанием лицензии, или сгенерированные изображения/тексты.
> 3. Создайте таблицу разметки (любой табличный редактор): идентификатор, файл/текст, класс, источник, лицензия, разметчик, комментарий о сомнениях.
> 4. Напишите инструкцию разметчика (5–7 правил): по каким признакам относить к классу, что делать со спорными случаями.
> 5. Передайте 10 объектов одногруппнику (или попросите чат-бот с загрузкой изображений) разметить по вашей инструкции «вслепую». Посчитайте долю совпадений с вашей разметкой.
>
> **Обязательные скриншоты:**
> - таблица разметки целиком;
> - коллаж/список примеров по классам;
> - инструкция разметчика;
> - результат независимой разметки с подсчётом совпадений.
>
> **Структура отчёта:**
> - описание задачи и классов;
> - статистика датасета: объём по классам, сбалансированность, источники;
> - доля совпадений независимой разметки и разбор расхождений — какие правила инструкции оказались неоднозначными;
> - вывод: сколько объектов и какого разнообразия понадобилось бы для реального обучения (с опорой на цифры из видео) и какие смещения уже заложены в ваш мини-датасет.

**Today is 2026-11-10. Deadline is 2026-11-12 23:55 MSK.** Do not miss it. Peer review is due 2026-11-19.

### Course material concepts to cite (from the lectures)

From lecture 2.3 (Датасеты в ИИ):
- ImageNet: 14M+ images, hand-labeled by hundreds of thousands of workers
- ChatGPT: trained on ~300 billion words
- DALL·E: trained on 650M+ image-text pairs
- Bias example: Google Photos gorilla error (insufficient representation)

From lecture 2.4 (Специфика датасетов):
- «1000 точных примеров лучше миллиона зашумлённых» — quality > quantity
- Expert labeling (врачи для КТ-снимков)
- Edge cases / краевые случаи

From lecture 2.6 (Дообучение):
- **Fine-tuning requires 100–200 high-quality examples minimum** (for style adaptation)
- Training from scratch requires billions of tokens/words
- Stylistic homogeneity of the dataset is critical

## 2. Task, models, and cost plan (FIXED, do not change)

### 2.1 Classification task

**«Афиша / Обложка книги / Постер фильма»** (event poster / book cover / movie poster) — 3 classes.

- **Why this task:** directly relevant to PR/communications (связь с общественностью) — posters, covers, and movie posters are all communications artifacts that a PR specialist encounters. Image-based (multimedia, fits the course). Three classes with overlapping visual features (all have a title + image + text), creating realistic classification ambiguity.
- **Why 3 classes (not 2):** the assignment allows 2–3; 3 is more interesting and creates richer disagreement analysis.

### 2.2 Data collection — 24 generated images via Polza.ai

Generate **24 images** (8 per class) using `tongyi-mai/z-image` (cheapest diffusion model on Polza at 1.4 ₽/image). The generation prompt for each image specifies the intended class — this becomes the ground-truth label.

**8 event poster (афиша) prompts:**
1. "A poster for a rock music concert, featuring a band name in large bold text, date and venue information at the bottom, vibrant red and black colors"
2. "A poster for an art exhibition, showing a sample painting, exhibition title, gallery name, dates November 2026"
3. "A poster for a theater performance, artistic illustration of a stage, play title, date and time, venue address"
4. "A poster for a university lecture, clean design, speaker name, lecture title, date, auditorium number"
5. "A poster for a film festival, cinematic collage, festival name, dates, list of participating countries"
6. "A poster for a sports event, basketball tournament, dynamic action image, event name, dates, stadium"
7. "A poster for a food festival, illustrated food image, festival name, dates, location, entry fee"
8. "A poster for a stand-up comedy show, comedian photo, show name, date, club name and address"

**8 book cover (обложка книги) prompts:**
1. "A book cover for a fantasy novel, illustrated dragon and castle, book title 'The Last Realm', author name, publisher logo"
2. "A book cover for a science textbook, clean minimal design, title 'Quantum Physics', author names, university press logo"
3. "A book cover for a biography, portrait photo of the subject, title 'A Life in Science', author name"
4. "A book cover for a cookbook, illustrated dish, title 'Italian Kitchen', author name, photo credit"
5. "A book cover for a mystery novel, dark atmospheric image, title 'The Silent Witness', author name"
6. "A book cover for a children's book, colorful cartoon illustration, title 'The Adventures of Pip', author and illustrator names"
7. "A book cover for a self-help book, simple geometric design, title 'Focus', author name, testimonial quote"
8. "A book cover for an academic monograph, serious typographic design, title 'Media Theory', author name, university press"

**8 movie poster (постер фильма) prompts:**
1. "A movie poster for a sci-fi action film, dramatic character composition with spaceship, film title 'STELLAR', credits block at bottom listing director and cast, release date"
2. "A movie poster for a romantic comedy, two lead characters back to back, film title 'LOVE UNEXPECTED', credits block, coming soon"
3. "A movie poster for a horror film, dark eerie image, film title 'THE LAST NIGHT', credits block, release date October"
4. "A movie poster for a documentary, striking real-world image, film title 'CODE OF SILENCE', credits block, festival laurels"
5. "A movie poster for an animated family film, colorful cartoon character, film title 'SKY JUMPERS', credits block, release date"
6. "A movie poster for a thriller, intense close-up of protagonist, film title 'EDGE OF DARK', credits block, coming soon"
7. "A movie poster for a historical drama, period costume scene, film title 'THE EMPRESS', credits block, release date"
8. "A movie poster for a comedy, humorous character pose, film title 'OFFICE DISASTER', credits block, release date"

**Some prompts intentionally create ambiguity:**
- Book cover #3 (biography with portrait) could look like a movie poster
- Book cover #5 (mystery, dark atmospheric) could look like a movie poster
- Event poster #4 (university lecture, clean design) could look like a book cover
- Movie poster #4 (documentary, striking image) could look like an event poster

This ensures the blind annotator will make some mistakes, giving us interesting disagreement analysis.

### 2.3 Models

| Role | Polza model ID | Purpose | Cost |
|---|---|---|---|
| Image generator | `tongyi-mai/z-image` | Generate 24 dataset images | 24 × 1.4 = 33.6 ₽ |
| Blind annotator | `google/gemini-2.5-flash` | Label 10 images "blindly" using the instruction | ~3 ₽ (10 vision calls) |
| **Total** | | | **~37 ₽** (within 100 ₽ budget) |

### 2.4 Substitution rule

If `tongyi-mai/z-image` is unavailable, substitute with `bytedance/seedream-4` (3 ₽/image, 24 × 3 = 72 ₽). If `google/gemini-2.5-flash` is unavailable for vision, substitute with `openai/gpt-4o` (multimodal). Document any substitution in `./logs/generation-method.md`.

## 3. Deliverables

Everything goes under `./labeling/`. Final deliverables (copy to `./deliverable/` at the end):

1. `Отчет_Задание5.docx` — the report, **in Russian**, A4, Times New Roman 14 pt, 2 cm margins (formatting identical to Assignments 1–4).
2. `Отчет_Задание5.pdf` — PDF rendering.
3. `разметка.xlsx` — the labeling table (spreadsheet).
4. `screenshots/` — 4 screenshot composites:
   - `01_labeling_table.png` — full labeling table (all 24 rows)
   - `02_examples_collage.png` — collage of examples by class (3 panels)
   - `03_instruction.png` — labeling instruction (5–7 rules)
   - `04_blind_results.png` — independent labeling results with agreement count
5. `images/` — 24 generated images (`img_01.png` … `img_24.png`).
6. `logs/` — `generation-method.md`, `labels_ground_truth.json`, `labels_blind.json`, `agreement.json`, `worklog.md`, `cost.md`.

## 4. Working directory layout

```
./labeling/
├── images/            # 24 generated dataset images
├── screenshots/       # 4 composites
├── report/            # .docx + .pdf
├── logs/              # all JSON and MD logs
└── deliverable/       # final copies only
```

## 5. Step-by-step procedure

### Step 1 — Pre-flight checks

1. Verify `POLZA_API_KEY` is set (`echo "${POLZA_API_KEY:0:4}"` should print `pza_`).
2. Verify Python ≥ 3.10, Pillow, python-docx, requests, openai, openpyxl are installed. `pip install` anything missing.
3. Probe the API: `curl -sS https://polza.ai/api/v1/models -H "Authorization: Bearer $POLZA_API_KEY" | head -c 200`.
4. Log all checks into `./logs/worklog.md`.

### Step 2 — Generate 24 dataset images

Write `./scripts/generate_dataset.py`:

```python
from openai import OpenAI
import base64, requests, pathlib, time, json

client = OpenAI(api_key=open("/path/to/.polza_key").read().strip(),
                base_url="https://polza.ai/api/v1")

PROMPTS = [
    # 8 event posters (class = "афиша")
    ("афиша", "A poster for a rock music concert, featuring a band name in large bold text, date and venue information at the bottom, vibrant red and black colors"),
    ("афиша", "A poster for an art exhibition, showing a sample painting, exhibition title, gallery name, dates November 2026"),
    ("афиша", "A poster for a theater performance, artistic illustration of a stage, play title, date and time, venue address"),
    ("афиша", "A poster for a university lecture, clean design, speaker name, lecture title, date, auditorium number"),
    ("афиша", "A poster for a film festival, cinematic collage, festival name, dates, list of participating countries"),
    ("афиша", "A poster for a sports event, basketball tournament, dynamic action image, event name, dates, stadium"),
    ("афиша", "A poster for a food festival, illustrated food image, festival name, dates, location, entry fee"),
    ("афиша", "A poster for a stand-up comedy show, comedian photo, show name, date, club name and address"),
    # 8 book covers (class = "обложка книги")
    ("обложка книги", "A book cover for a fantasy novel, illustrated dragon and castle, book title 'The Last Realm', author name, publisher logo"),
    ("обложка книги", "A book cover for a science textbook, clean minimal design, title 'Quantum Physics', author names, university press logo"),
    ("обложка книги", "A book cover for a biography, portrait photo of the subject, title 'A Life in Science', author name"),
    ("обложка книги", "A book cover for a cookbook, illustrated dish, title 'Italian Kitchen', author name, photo credit"),
    ("обложка книги", "A book cover for a mystery novel, dark atmospheric image, title 'The Silent Witness', author name"),
    ("обложка книги", "A book cover for a children's book, colorful cartoon illustration, title 'The Adventures of Pip', author and illustrator names"),
    ("обложка книги", "A book cover for a self-help book, simple geometric design, title 'Focus', author name, testimonial quote"),
    ("обложка книги", "A book cover for an academic monograph, serious typographic design, title 'Media Theory', author name, university press"),
    # 8 movie posters (class = "постер фильма")
    ("постер фильма", "A movie poster for a sci-fi action film, dramatic character composition with spaceship, film title 'STELLAR', credits block at bottom listing director and cast, release date"),
    ("постер фильма", "A movie poster for a romantic comedy, two lead characters back to back, film title 'LOVE UNEXPECTED', credits block, coming soon"),
    ("постер фильма", "A movie poster for a horror film, dark eerie image, film title 'THE LAST NIGHT', credits block, release date October"),
    ("постер фильма", "A movie poster for a documentary, striking real-world image, film title 'CODE OF SILENCE', credits block, festival laurels"),
    ("постер фильма", "A movie poster for an animated family film, colorful cartoon character, film title 'SKY JUMPERS', credits block, release date"),
    ("постер фильма", "A movie poster for a thriller, intense close-up of protagonist, film title 'EDGE OF DARK', credits block, coming soon"),
    ("постер фильма", "A movie poster for a historical drama, period costume scene, film title 'THE EMPRESS', credits block, release date"),
    ("постер фильма", "A movie poster for a comedy, humorous character pose, film title 'OFFICE DISASTER', credits block, release date"),
]

for i, (cls, prompt) in enumerate(PROMPTS, 1):
    t0 = time.time()
    r = client.images.generate(model="tongyi-mai/z-image", prompt=prompt, size="1024x1024", n=1)
    d = r.data[0]
    if getattr(d, "b64_json", None):
        img_bytes = base64.b64decode(d.b64_json)
    else:
        img_bytes = requests.get(d.url).content
    pathlib.Path(f"./images/img_{i:02d}.png").write_bytes(img_bytes)
    # Log
    pathlib.Path(f"./logs/gen_{i:02d}.json").write_text(json.dumps({
        "id": f"P{i:02d}", "class": cls, "prompt": prompt,
        "elapsed": time.time()-t0, "usage": getattr(r, "usage", None)
    }, ensure_ascii=False, indent=2))
    print(f"P{i:02d} ({cls}): saved")
```

Save the ground-truth labels to `./logs/labels_ground_truth.json`:
```json
[
  {"id": "P01", "file": "img_01.png", "class": "афиша", "prompt": "..."},
  ...
  {"id": "P24", "file": "img_24.png", "class": "постер фильма", "prompt": "..."}
]
```

### Step 3 — Create the labeling table (XLSX)

Write `./scripts/build_table.py` using openpyxl:

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import json

wb = Workbook()
ws = wb.active
ws.title = "Разметка"

# Headers
headers = ["ID", "Файл", "Класс", "Источник", "Лицензия", "Разметчик", "Комментарий о сомнениях"]
header_font = Font(name="Times New Roman", size=12, bold=True)
header_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                     top=Side(style='thin'), bottom=Side(style='thin'))

for col, h in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = thin_border

# Data rows
labels = json.loads(open("./logs/labels_ground_truth.json").read())
for row_idx, item in enumerate(labels, 2):
    row_data = [
        item["id"],
        item["file"],
        item["class"],
        "Сгенерировано через Polza.ai (tongyi-mai/z-image)",
        "Собственное (сгенерировано ИИ, права использования по условиям Polza.ai)",
        "Ханна М. Н.",
        ""  # fill with doubt comments for ambiguous cases
    ]
    for col, val in enumerate(row_data, 1):
        cell = ws.cell(row=row_idx, column=col, value=val)
        cell.font = Font(name="Times New Roman", size=12)
        cell.alignment = Alignment(vertical="top", wrap_text=True)
        cell.border = thin_border

# Column widths
ws.column_dimensions['A'].width = 8
ws.column_dimensions['B'].width = 16
ws.column_dimensions['C'].width = 18
ws.column_dimensions['D'].width = 36
ws.column_dimensions['E'].width = 32
ws.column_dimensions['F'].width = 16
ws.column_dimensions['G'].width = 40

wb.save("./разметка.xlsx")
```

**Doubt comments:** for the intentionally ambiguous images, fill the comment column:
- P03 (biography book cover): «Портрет + крупный шрифт — может напоминать постер фильма»
- P05 (mystery book cover): «Тёмная атмосферная иллюстрация — визуально близко к постеру фильма»
- P04 (university lecture poster): «Минималистичный дизайн с текстом — может напоминать обложку книги»
- P20 (documentary movie poster): «Реалистичное изображение + лауреаты фестиваля — может напоминать афишу»

### Step 4 — Write the labeling instruction (5–7 rules)

Save to `./logs/instruction.md` and also render as a composite image `./screenshots/03_instruction.png`.

**Инструкция разметчика (7 правил):**

```
ИНСТРУКЦИЯ РАЗМЕТЧИКА
Задача: классификация изображения на один из трёх классов:
«афиша», «обложка книги», «постер фильма».

Правило 1. АФИША (event poster).
Признаки: содержит дату и/или время события; содержит название места
(venue, адрес, зал); продвигает временное событие (концерт, выставка,
лекция, спектакль, фестиваль). Иерархия текста: название события →
дата → место.

Правило 2. ОБЛОЖКА КНИГИ (book cover).
Признаки: содержит имя автора; содержит название книги; НЕТ даты
события и НЕТ названия места; часто присутствует логотип издательства;
предназначена для физического продукта (книга).

Правило 3. ПОСТЕР ФИЛЬМА (movie poster).
Признаки: содержит название фильма; содержит блок титров в нижней
части (credits block — мелкий текст со списком режиссёра, актёров,
продюсеров); часто присутствует «coming soon» или дата релиза;
драматичная визуальная композиция с персонажами.

Правило 4. ПРИЗНАКИ ДЛЯ РАЗЛИЧЕНИЯ.
- Дата + место (venue) → АФИША
- Имя автора → ОБЛОЖКА КНИГИ
- Блок титров (credits) → ПОСТЕР ФИЛЬМА
- Логотип издательства → ОБЛОЖКА КНИГИ
- «Coming soon» / дата релиза без места → ПОСТЕР ФИЛЬМА

Правило 5. СПОРНЫЕ СЛУЧАИ.
Если изображение имеет признаки двух классов:
- Автор + драматичная иллюстрация (без credits block) → ОБЛОЖКА КНИГИ
- Дата + драматичная иллюстрация (без автора, без credits) → АФИША
- Credits block + название без автора → ПОСТЕР ФИЛЬМА

Правило 6. ЧТО ДЕЛАТЬ СО СПОРНЫМИ СЛУЧАЯМИ.
Выберите ближайший класс по правилу 5 и обязательно отметьте сомнение
в комментарии: «сомнение: [причина]».

Правило 7. ВНЕ КАТЕГОРИЙ.
Если изображение не является ни афишей, ни обложкой, ни постером
фильма (например, пейзаж без текста) → отметьте «вне категорий»
и поясните в комментарии.
```

Build `./screenshots/03_instruction.png`:
- Title bar (60 px, dark #1A1A1A, white text): «Инструкция разметчика»
- White background, TNR ~12 pt, the full instruction text wrapped
- ~1400 × 2000 px (may span multiple "pages" visually — that's fine)

### Step 5 — Run blind annotation (10 images via Gemini 2.5 Flash)

Select 10 images for blind annotation. Choose a mix:
- 3 clearly афиша (P01, P05, P07)
- 3 clearly обложка книги (P09, P14, P15)
- 2 clearly постер фильма (P17, P22)
- 2 ambiguous cases (P03 biography book cover, P20 documentary movie poster)

Write `./scripts/blind_annotate.py`:

```python
from openai import OpenAI
import base64, pathlib, json, time

client = OpenAI(api_key=open("/path/to/.polza_key").read().strip(),
                base_url="https://polza.ai/api/v1")

INSTRUCTION = open("./logs/instruction.md").read()

# 10 image IDs to annotate blindly
BLIND_IDS = ["P01", "P03", "P05", "P07", "P09", "P14", "P15", "P17", "P20", "P22"]

results = []
for pid in BLIND_IDS:
    idx = int(pid[1:])
    img_path = f"./images/img_{idx:02d}.png"
    img_b64 = base64.b64encode(pathlib.Path(img_path).read_bytes()).decode()
    data_url = f"data:image/png;base64,{img_b64}"

    prompt = (
        f"{INSTRUCTION}\n\n"
        "Классифицируйте следующее изображение по этой инструкции. "
        "Ответьте только одной строкой в формате:\n"
        "КЛАСС: <афиша|обложка книги|постер фильма|вне категорий>\n"
        "СОМНЕНИЕ: <краткое пояснение или «нет»>"
    )

    t0 = time.time()
    r = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": data_url}}
        ]}]
    )
    response = r.choices[0].message.content
    results.append({
        "id": pid,
        "ground_truth": "",  # fill from labels_ground_truth.json
        "blind_label": response,
        "elapsed": time.time() - t0,
        "usage": {"in": r.usage.prompt_tokens, "out": r.usage.completion_tokens}
    })
    print(f"{pid}: {response[:80]}")

# Fill ground truth
gt = {item["id"]: item["class"] for item in json.loads(open("./logs/labels_ground_truth.json").read())}
for r in results:
    r["ground_truth"] = gt[r["id"]]

open("./logs/labels_blind.json", "w").write(json.dumps(results, ensure_ascii=False, indent=2))
```

### Step 6 — Compute agreement and analyze disagreements

Write `./scripts/agreement.py`:

```python
import json, re

results = json.loads(open("./logs/labels_blind.json").read())

# Parse blind labels
def parse_label(text):
    # Extract "КЛАСС: <...>" from the response
    m = re.search(r"КЛАСС:\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
    if m:
        label = m.group(1).strip().lower()
        # Normalize
        for canonical in ["афиша", "обложка книги", "постер фильма", "вне категорий"]:
            if canonical in label:
                return canonical
    return "не удалось распарсить"

matches = 0
mismatches = []
for r in results:
    blind = parse_label(r["blind_label"])
    gt = r["ground_truth"]
    match = (blind == gt)
    r["parsed_blind"] = blind
    r["match"] = match
    if match:
        matches += 1
    else:
        mismatches.append({
            "id": r["id"],
            "ground_truth": gt,
            "blind_label": blind,
            "raw_response": r["blind_label"][:200]
        })

agreement_rate = matches / len(results)
print(f"Agreement: {matches}/{len(results)} = {agreement_rate:.0%}")

agreement_data = {
    "total": len(results),
    "matches": matches,
    "mismatches": len(mismatches),
    "agreement_rate": agreement_rate,
    "details": results,
    "mismatch_analysis": mismatches
}
open("./logs/agreement.json", "w").write(json.dumps(agreement_data, ensure_ascii=False, indent=2))
```

In `./logs/disagreement_analysis.md`, for each mismatch, analyze:
- Which instruction rule was ambiguous?
- Why did the blind annotator choose the wrong class?
- How would you fix the instruction?

### Step 7 — Build the 4 screenshot composites

Use Python + Pillow. Cyrillic-capable TTF font (`fc-list | grep -iE 'noto.*sans|dejavu'`).

**Composite 1 — `01_labeling_table.png` (full labeling table, ~1800×1400 px):**
- Title bar (60 px, dark #1A1A1A, white text): «Таблица разметки: 24 объекта, 3 класса»
- Render the table as a styled grid: 7 columns × 25 rows (header + 24 data rows)
- Column widths proportional to the XLSX column widths
- Header row: bold, light grey background
- Alternating row colors (white / #FAFAFA) for readability
- All text in TNR ~10 pt (small to fit 24 rows)
- All cells bordered

**Composite 2 — `02_examples_collage.png` (collage by class, ~1800×1800 px):**
- Title bar (60 px, dark #1A1A1A, white text): «Примеры по классам: Афиша | Обложка книги | Постер фильма»
- 3 columns (one per class), each showing 3 example images stacked vertically
- Each image: ~500 px wide, aspect preserved
- Caption strip below each image: «P01 — афиша» (etc.)
- 16 px gutters

**Composite 3 — `03_instruction.png`** — already built in Step 4.

**Composite 4 — `04_blind_results.png` (independent labeling results, ~1600×1200 px):**
- Title bar (60 px, dark #1A1A1A, white text): «Независимая разметка: 10 объектов, доля совпадений = X%»
- Table: 10 rows × 5 columns
  - Col 1: ID (P01, P03, ...)
  - Col 2: Ground truth class
  - Col 3: Blind label (parsed)
  - Col 4: Совпадение (✓ / ✗) — green ✓ for match, red ✗ for mismatch
  - Col 5: Комментарий ( сомнение from the blind annotator's response)
- Summary bar at the bottom: «Совпадений: X/10 (X%). Расхождений: Y.»

### Step 8 — Write the analysis file

In `./logs/analysis.md`, compile:

**a) Dataset statistics:**
- Total objects: 24
- Per class: 8 афиша, 8 обложка книги, 8 постер фильма
- Balance: 33.3% / 33.3% / 33.3% — perfectly balanced
- Sources: 24/24 generated via Polza.ai (tongyi-mai/z-image)
- Licenses: all "собственное (сгенерировано ИИ)"

**b) Agreement rate and disagreement analysis:**
- Total: 10 objects annotated blindly
- Matches: X/10 (X%)
- For each mismatch: which rule was ambiguous, why the annotator chose wrong, how to fix the instruction
- Identify the 1–2 rules that caused the most confusion

**c) Conclusion — how many objects for real training:**
- Per course lecture 2.6: fine-tuning requires **100–200 high-quality examples** minimum
- For a 3-class classifier: 100–200 per class = **300–600 total** for fine-tuning
- Current dataset: 24 total (8 per class) — **insufficient by ~12–25×** (need 300/24 ≈ 12.5× more for the minimum fine-tuning threshold)
- For training from scratch: would need **millions** (per lecture 2.3: ImageNet has 14M+ images, DALL·E trained on 650M+ pairs)
- Current dataset is useful only as a **prototype / proof-of-concept**, not for real training

**d) Biases already embedded in the mini-dataset:**
1. **Generation bias (смещение модели-генератора):** all 24 images generated by the same model (Z-Image), which has its own aesthetic style. A classifier trained on this dataset would learn Z-Image's style, not the true visual features of posters/covers/movie posters.
2. **Stereotype bias (стереотипизация):** the prompts create "textbook" examples — e.g., all movie posters have a credits block, all book covers have an author name. Real-world data is much messier (some movie posters don't have credits blocks, some book covers don't show the author).
3. **Cultural bias (культурное смещение):** prompts are in English; the generated text on images is likely in English. A classifier trained on this would struggle with Russian-language posters/covers. Link to lecture 2.3: «репрезентативность выборки».
4. **Class overlap bias (перекрытие классов):** the 3 classes have overlapping visual features (all have a title + image + text). In a real dataset, the boundary would be even blurrier.

### Step 9 — Write the report `Отчет_Задание5.docx`

Use `python-docx`. The report is **in Russian**. Formatting identical to Assignments 1–4.

#### 9.1 Title page — MUST match the official LETI template

(Same as Assignments 1–4. Theme line: `Тема: Разметка датасета для задачи классификации`. Student name: `Ханна М. Н.`. All other elements identical. See §8.1 of the Assignment 1–4 prompts for the exact spec — do not deviate.)

#### 9.2 Body formatting rules

(Same as Assignments 1–4: A4, margins 2 cm, TNR 14 pt throughout, first-line indent 1.25 cm, justified, headings bold centered, captions TNR 12 pt italic, page numbers from page 2, no `___` except the two title-page fields.)

#### 9.3 Required body structure

1. **1. Введение** (~150 слов) — purpose: building and labeling a mini-dataset for a 3-class image classification task relevant to PR/communications; testing labeling instruction quality via independent blind annotation; why this matters for understanding dataset construction.

2. **2. Описание задачи и классов** — describe:
   - The classification task: «Афиша / Обложка книги / Постер фильма»
   - Why this task was chosen (relevance to PR/communications)
   - The 3 classes with definitions (from the instruction rules 1–3)
   - Embed `02_examples_collage.png` at ~14 cm width, captioned `Рисунок 1 — Примеры по классам: афиша, обложка книги, постер фильма`

3. **3. Статистика датасета** — present:
   - Total: 24 objects
   - Per class: 8 / 8 / 8 (balanced)
   - Sources: all generated via Polza.ai (tongyi-mai/z-image)
   - Licenses: all "собственное (сгенерировано ИИ)"
   - Embed `01_labeling_table.png` at ~14 cm width (or full page), captioned `Рисунок 2 — Таблица разметки (24 объекта)`
   - Brief paragraph on balance and sources

4. **4. Инструкция разметчика** — present the full instruction (7 rules). Embed `03_instruction.png` at ~14 cm width, captioned `Рисунок 3 — Инструкция разметчика (7 правил)`. Brief paragraph explaining the key distinguishing features.

5. **5. Независимая разметка и доля совпадений** — present:
   - How the blind annotation was done: 10 images sent to Gemini 2.5 Flash via Polza.ai, with the instruction, "blindly" (no ground-truth label shown)
   - Embed `04_blind_results.png` at ~14 cm width, captioned `Рисунок 4 — Результат независимой разметки: 10 объектов, доля совпадений`
   - The agreement rate: X/10 = X%
   - **Разбор расхождений** — for each mismatch:
     - Which image was misclassified
     - What the ground truth was vs what the blind annotator chose
     - Which instruction rule was ambiguous
     - How the instruction could be improved
   - Identify the 1–2 rules that caused the most confusion

6. **6. Вывод** (~300 слов) — two parts:
   - **6.1. Сколько объектов нужно для реального обучения** — cite course numbers:
     - Fine-tuning: 100–200 examples per class (lecture 2.6) → 300–600 for 3 classes
     - Current dataset: 24 (8 per class) — insufficient by ~12–25×
     - Training from scratch: millions (lecture 2.3: ImageNet 14M, DALL·E 650M)
     - Current dataset is a prototype, not a training set
   - **6.2. Смещения, заложенные в мини-датасет** — list the 4 biases from Step 8d:
     1. Generation bias (all from Z-Image, same aesthetic)
     2. Stereotype bias (textbook examples, real data is messier)
     3. Cultural bias (English prompts → English text on images)
     4. Class overlap bias (overlapping visual features)
   - Link each to course concepts (lecture 2.3: репрезентативность; lecture 2.4: краевые случаи; lecture 2.6: стилевая однородность)

7. **Приложение А** — full labeling table data (all 24 rows in a docx table, if the screenshot is hard to read).

8. **Приложение Б** — full labeling instruction (verbatim text).

9. **Приложение В** — work log + cost: tool versions, API calls, timestamps, per-call cost, total cost. From `./logs/worklog.md` and `./logs/cost.md`.

### Step 10 — Self-check (mandatory)

1. **Title-page format check (highest priority).** Render page 1 of the PDF to JPEG at 100 DPI and verify visually:
   - The 4-line university header is bold, centered, TNR 14pt.
   - `отчет` is lowercase, not bold.
   - `по заданию` and `по курсу «Применение генеративных нейронных моделей в мультимедиа»` are bold.
   - The theme line reads `Тема: Разметка датасета для задачи классификации` — not bold.
   - The student row reads `Студент гр. ___` with `Ханна М. Н.` in the right cell (spaces between initials).
   - The student/teacher table has NO visible borders.
   - Page 1 has NO page number.
   - Compare side-by-side with my Assignment 4 report title page — the layout must be identical, only the theme text differs.

2. Reopen the `.docx` with python-docx. Print the heading outline, table count, image count (should be ≥ 4 images). Search the full text for `TODO|XXX|placeholder|【`. If any hit, fix it and re-save.

3. Convert to PDF: `soffice --headless --convert-to pdf --outdir ./report ./report/Отчет_Задание5.docx`. Render pages 1, 2, the page with the results table, and the last page to JPEG. Check: no overflow, no broken table, no missing image, no Markdown leftovers.

4. Verify all 4 screenshot composites exist in `./screenshots/`, plus 24 generated images in `./images/`, plus `разметка.xlsx`.

5. Verify `./logs/cost.md` total ≤ 50 ₽.

6. Copy final files into `./deliverable/`: `Отчет_Задание5.docx`, `Отчет_Задание5.pdf`, `разметка.xlsx`, `screenshots/` (zipped or as a folder), `images/` (zipped).

### Step 11 — Final summary

Print a final summary listing:
- absolute paths of `Отчет_Задание5.docx`, `Отчет_Задание5.pdf`, `разметка.xlsx`, and the screenshots folder;
- the dataset stats (24 images, 8 per class, balanced);
- the agreement rate (X/10 = X%);
- the **total cost in ₽** actually billed by Polza.ai;
- the next step I should do (upload the report on `open.etu.ru` before 2026-11-12 23:55 MSK, then complete peer review before 2026-11-19 23:55 MSK).

## 6. Hard constraints

- **Do not invent facts.** The agreement rate must come from actual blind annotation calls. The dataset statistics must match the actual generated images.
- **All 24 images must be REAL generated images** from Polza.ai, not placeholders. Each must exist as a file in `./images/`.
- **The blind annotation must be genuinely "blind".** The LLM must see ONLY the image + the instruction. Do NOT pass the ground-truth label or the generation prompt to the LLM.
- **The report is in Russian.** Only model/brand names, URLs, dataset IDs, and the English generation prompts may stay in English. Every explanatory sentence is in Russian.
- **Stay inside the project directory.** Never write outside `./labeling/` (and `./deliverable/`).
- **No placeholders** except the two title-page fields `Студент гр. ___` and `Преподаватель ___`. The student name `Ханна М. Н.` must appear verbatim, with spaces between initials.
- **Budget:** total Polza spend must stay under 50 ₽. If the image generation alone exceeds 45 ₽, abort and log it.
- **Same formatting as Assignments 1–4.** The title page, body font, margins, heading style, and table style must be visually identical to my previous reports — only the content differs.
- **Don't pause for human input** unless Step 1's pre-flight checks fail. The Polza API path is fully autonomous — generate 24 images, build the table, write the instruction, run blind annotation, compute agreement, write the report, render the PDF, all without me.

Start now. Begin by creating the directory structure, then proceed through Steps 1 → 11 in order.
