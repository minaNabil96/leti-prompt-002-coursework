# Prompt for AI Agent — Module 3, Assignment 3: Image Animation — Three Animations, Three Effects

> Paste everything below this line into opencode desktop.

---

# TASK

You are an autonomous coding/agent assistant running in **opencode desktop** with full filesystem and shell access on my machine. Complete LETI coursework **Module 3, Assignment 3** end-to-end, using the **Polza.ai** API for image generation and video animation. Produce the final deliverables in `./deliverable/`.

## 1. Context (read this first)

I am a student at **St. Petersburg Electrotechnical University «ЛЭТИ» (LETI)**, course **«Применение генеративных нейронных моделей в мультимедиа»** (Prompt-002, осень 2026), **Кафедра ИС** (Информационные системы). This assignment is from **Module 3** of the course.

**IMPORTANT — department correction:** My department is **«Кафедра ИС»**, NOT «Кафедра связи с общественностью». The title page MUST say `Кафедра ИС`. (Previous assignments had the wrong department name — this one must be correct.)

**Original assignment (Russian, verbatim):**

> **Задание 3 (Модуль 3). Оживление изображений: три анимации — три эффекта**
> Срок сдачи — 4 декабря 2026, 02:59 MSK. Срок взаимного оценивания — 11 декабря 2026.
>
> **Шаг 1.** Подберите три исходника:
> - портрет (свой или с согласия человека; допускается сгенерированный ИИ портрет);
> - пейзаж или городская среда с элементами, которые естественно движутся (вода, облака, листва, огонь);
> - изображение на ваш выбор — для креативного эксперимента (картина, историческое фото из открытого архива, собственный рисунок).
>
> Требование к исходникам: хорошее освещение, чёткость, один явный главный объект. Укажите источник и лицензию каждого.
>
> **Шаг 2.** Создайте по одной анимации в любом доступном сервисе оживления изображений, соблюдая три уровня интенсивности:
> - портрет — минимальное движение (моргание, лёгкий поворот, улыбка);
> - пейзаж — средняя интенсивность (один-два движущихся элемента);
> - свободный выбор — максимальные значения, экспериментируйте.
>
> **Шаг 3.** Заполните таблицу настроек (по каждой работе):
>
> | Работа | Сервис | Скорость анимации | Плавность переходов | Глубина эффекта | Что именно двигалось | Что пошло не так |
> |---|---|---|---|---|---|---|
> | Портрет | | | | | | |
> | Пейзаж | | | | | | |
> | Свободная | | | | | | |
>
> **Шаг 4.** Рефлексия (150–250 слов): какие эмоции вызывает каждая работа; как изменилось восприятие по сравнению со статичным изображением; где движение усилило смысл, а где разрушило; как бы вы использовали такую анимацию в учебном, музейном или медиапроекте.
>
> **Шаг 5.** Загрузите: 3 исходника, 3 анимации (или ссылки), таблицу, рефлексию, скриншоты интерфейса с настройками.

**Today is 2026-11-25. Deadline is 2026-12-04 02:59 MSK** (in ~9 days). Peer review is due 2026-12-11.

## 2. Source images, models, and cost plan (FIXED — do not change)

### 2.1 Three source images

| # | Type | Source | License | How obtained |
|---|---|---|---|---|
| S1 | **Портрет** (portrait) | AI-generated via Polza.ai | Собственное (сгенерировано ИИ) | Generate with `tongyi-mai/z-image` |
| S2 | **Пейзаж** (landscape with moving elements) | AI-generated via Polza.ai | Собственное (сгенерировано ИИ) | Generate with `tongyi-mai/z-image` |
| S3 | **Картина** (painting — free choice) | Vincent van Gogh, «The Starry Night» (1889) | Public domain | Download from Wikimedia Commons |

**S1 generation prompt:** «A professional portrait of a young woman with short dark hair, soft natural lighting, neutral grey background, looking directly at the camera, photorealistic, high detail»

**S2 generation prompt:** «A serene mountain lake at sunset with gentle pink clouds, calm water with subtle reflections, pine trees on the shore, warm golden light, photorealistic landscape»

**S3 download URL:** `https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg`
- Source: Wikimedia Commons, public domain (Van Gogh died 1890; PD since 1961)
- Museum: MoMA, New York

### 2.2 Animation models (image-to-video via Polza.ai)

The Polza.ai video endpoint is `/api/v1/media` (asynchronous: POST returns a task ID, then poll `/api/v1/media/$ID/operations` until completed).

**Image-to-video is supported by:** Seedance, Kling Motion Control, and Wan models (per Polza.ai documentation).

For this assignment, use **`bytedance/seedance-2-mini`** for all 3 animations (cheapest image-to-video model at 2.56 ₽/sec). The 3 intensity levels are controlled by the PROMPT, not by the model.

| Animation | Model | Duration | Prompt (motion description) | Intensity | Cost |
|---|---|---|---|---|---|
| A1 (portrait) | `bytedance/seedance-2-mini` | 5 sec | «Subtle animation: the woman blinks once slowly, tilts her head slightly to the right, and forms a gentle smile. Minimal movement, natural breathing motion.» | минимальное | ~12.8 ₽ |
| A2 (landscape) | `bytedance/seedance-2-mini` | 5 sec | «Clouds drift slowly from left to right, water surface ripples gently with reflections, pine branches sway in a light breeze. Two moving elements only, medium intensity.» | средняя | ~12.8 ₽ |
| A3 (painting) | `bytedance/seedance-2-mini` | 5 sec | «Maximum dynamic animation: the swirling sky rotates and pulses, stars twinkle brightly, the cypress tree sways dramatically, village lights flicker, the moon glows intensely. Full transformation.» | максимальное | ~12.8 ₽ |

### 2.3 Cost estimate

| Item | Model | Cost |
|---|---|---|
| S1 portrait image | `tongyi-mai/z-image` | 1.4 ₽ |
| S2 landscape image | `tongyi-mai/z-image` | 1.4 ₽ |
| S3 Van Gogh painting | Wikimedia Commons | 0 ₽ |
| A1 portrait animation | `bytedance/seedance-2-mini` (5 sec) | ~12.8 ₽ |
| A2 landscape animation | `bytedance/seedance-2-mini` (5 sec) | ~12.8 ₽ |
| A3 painting animation | `bytedance/seedance-2-mini` (5 sec) | ~12.8 ₽ |
| **Total** | | **~41 ₽** (within 100 ₽ budget) |

### 2.4 Substitution rule

If `bytedance/seedance-2-mini` doesn't support image-to-video or returns errors:
- Substitute with `bytedance/seedance-2-fast` (10.46 ₽/sec, ~52 ₽ per 5-sec clip)
- Or `kling/v2.6-motion-control` (8.25 ₽/sec, ~41 ₽ per 5-sec clip)
- Or `alibaba/wan-3.0` (23.74 ₽/sec) — most expensive, last resort

Document any substitution in `./logs/generation-method.md`.

## 3. Deliverables

Everything goes under `./image-animation/`. Final deliverables (copy to `./deliverable/` at the end):

1. `Отчет_М3_Задание3.docx` — the report, **in Russian**, A4, Times New Roman 14 pt, 2 cm margins.
2. `Отчет_М3_Задание3.pdf` — PDF rendering.
3. `sources/` — 3 source images: `source_01_portrait.png`, `source_02_landscape.png`, `source_03_painting.jpg`
4. `animations/` — 3 video files: `animation_01_portrait.mp4`, `animation_02_landscape.mp4`, `animation_03_painting.mp4`
5. `screenshots/` — 3 screenshot composites:
   - `01_sources_overview.png` — 3 source images side by side with captions
   - `02_settings_table.png` — the filled settings table (Step 3)
   - `03_interface_mockup.png` — interface mockup showing the animation settings
6. `logs/` — `generation-method.md`, `animation_results.json`, `worklog.md`, `cost.md`

## 4. Working directory layout

```
./image-animation/
├── sources/           # 3 source images
├── animations/        # 3 generated video files (.mp4)
├── screenshots/       # 3 composites
├── report/            # .docx + .pdf
├── logs/              # all JSON and MD logs
└── deliverable/       # final copies only
```

## 5. Step-by-step procedure

### Step 1 — Pre-flight checks

1. Verify `POLZA_API_KEY` is set (`echo "${POLZA_API_KEY:0:4}"` should print `pza_`).
2. Verify Python ≥ 3.10, Pillow, python-docx, requests, openai are installed.
3. Probe the API: `curl -sS https://polza.ai/api/v1/models -H "Authorization: Bearer $POLZA_API_KEY" | head -c 200`.
4. Verify `tongyi-mai/z-image` and `bytedance/seedance-2-mini` exist in the model list.
5. Log all checks into `./logs/worklog.md`.

### Step 2 — Prepare the 3 source images

**S1 — Portrait (generate via Polza.ai):**
```python
from openai import OpenAI
import base64, requests, pathlib

client = OpenAI(api_key=KEY, base_url="https://polza.ai/api/v1")
r = client.images.generate(
    model="tongyi-mai/z-image",
    prompt="A professional portrait of a young woman with short dark hair, soft natural lighting, neutral grey background, looking directly at the camera, photorealistic, high detail",
    size="1024x1024", n=1
)
# Save the image
d = r.data[0]
if getattr(d, "b64_json", None):
    img_bytes = base64.b64decode(d.b64_json)
else:
    img_bytes = requests.get(d.url).content
pathlib.Path("./sources/source_01_portrait.png").write_bytes(img_bytes)
```

**S2 — Landscape (generate via Polza.ai):** same process, prompt = «A serene mountain lake at sunset with gentle pink clouds, calm water with subtle reflections, pine trees on the shore, warm golden light, photorealistic landscape»

**S3 — Van Gogh painting (download from Wikimedia):**
```bash
curl -sSL -o ./sources/source_03_painting.jpg \
  "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg"
```

Verify all 3 images exist and are valid (open with Pillow, check size > 50 KB).

### Step 3 — Generate 3 animations via Polza.ai Media API

The video generation API is **asynchronous** on Polza.ai. Write `./scripts/generate_animations.py`:

```python
import requests, json, pathlib, time, base64

API_KEY = open("/path/to/.polza_key").read().strip()
BASE = "https://polza.ai/api/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Prepare image-to-video requests
# The image can be passed as a URL or base64 data URI
def image_to_data_url(path):
    ext = path.split(".")[-1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}[ext]
    b64 = base64.b64encode(pathlib.Path(path).read_bytes()).decode()
    return f"data:{mime};base64,{b64}"

ANIMATIONS = [
    {
        "name": "portrait",
        "source": "./sources/source_01_portrait.png",
        "prompt": "Subtle animation: the woman blinks once slowly, tilts her head slightly to the right, and forms a gentle smile. Minimal movement, natural breathing motion.",
        "output": "./animations/animation_01_portrait.mp4"
    },
    {
        "name": "landscape",
        "source": "./sources/source_02_landscape.png",
        "prompt": "Clouds drift slowly from left to right, water surface ripples gently with reflections, pine branches sway in a light breeze. Two moving elements only, medium intensity.",
        "output": "./animations/animation_02_landscape.mp4"
    },
    {
        "name": "painting",
        "source": "./sources/source_03_painting.jpg",
        "prompt": "Maximum dynamic animation: the swirling sky rotates and pulses, stars twinkle brightly, the cypress tree sways dramatically, village lights flicker, the moon glows intensely. Full transformation.",
        "output": "./animations/animation_03_painting.mp4"
    }
]

results = []
for anim in ANIMATIONS:
    print(f"Generating {anim['name']}...")

    # Check API docs for exact image-to-video format
    # Try with image as data URL first
    data = {
        "model": "bytedance/seedance-2-mini",
        "prompt": anim["prompt"],
        "image": image_to_data_url(anim["source"]),
        "duration": 5
    }

    # POST the generation request
    r = requests.post(f"{BASE}/media", headers=HEADERS, json=data)
    if r.status_code != 200:
        print(f"  Error: {r.status_code} {r.text[:200]}")
        # Try alternative format: image_url instead of image
        data["image_url"] = data.pop("image")
        r = requests.post(f"{BASE}/media", headers=HEADERS, json=data)

    if r.status_code == 200:
        task_id = r.json().get("id") or r.json().get("task_id")
        print(f"  Task ID: {task_id}")

        # Poll for completion (video generation takes 30-180 seconds)
        for attempt in range(60):  # up to 5 minutes
            time.sleep(10)
            r2 = requests.get(f"{BASE}/media/{task_id}/operations", headers=HEADERS)
            if r2.status_code == 200:
                ops = r2.json()
                status = ops.get("status") or ops.get("state")
                if status in ("completed", "succeeded", "done"):
                    # Get the video URL
                    video_url = ops.get("result", {}).get("url") or ops.get("output", {}).get("url")
                    if video_url:
                        video_bytes = requests.get(video_url).content
                        pathlib.Path(anim["output"]).write_bytes(video_bytes)
                        print(f"  Saved: {anim['output']} ({len(video_bytes)} bytes)")
                        results.append({"name": anim["name"], "status": "success",
                                       "file": anim["output"], "size": len(video_bytes),
                                       "task_id": task_id, "elapsed_attempts": attempt + 1})
                    break
                elif status in ("failed", "error"):
                    print(f"  Generation failed: {ops}")
                    results.append({"name": anim["name"], "status": "failed",
                                   "error": str(ops), "task_id": task_id})
                    break
                else:
                    print(f"  Status: {status} (attempt {attempt+1})")
        else:
            print(f"  Timeout after 60 attempts")
            results.append({"name": anim["name"], "status": "timeout", "task_id": task_id})
    else:
        results.append({"name": anim["name"], "status": "error",
                       "status_code": r.status_code, "response": r.text[:500]})

pathlib.Path("./logs/animation_results.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=2)
)
```

**IMPORTANT:** The exact API format for image-to-video on Polza.ai may differ. The agent should:
1. Check the Polza.ai documentation at `https://polza.ai/docs` for the media API format
2. Try both `"image"` and `"image_url"` field names
3. If the image is too large for base64, upload it to a temporary hosting service and pass the URL
4. If the model doesn't support image-to-video, try `kling/v2.6-motion-control` instead

**If ALL video generation attempts fail:** note this in the report and provide a detailed analysis based on the source images and expected animation behavior. The assignment allows submitting «анимации (или ссылки)» — if no animation can be generated, provide links to similar demos on the Polza.ai website or the model's demo page.

### Step 4 — Build the settings table

In `./logs/settings_table.md`, fill in the table for each animation:

| Работа | Сервис | Скорость анимации | Плавность переходов | Глубина эффекта | Что именно двигалось | Что пошло не так |
|---|---|---|---|---|---|---|
| Портрет | Polza.ai, Seedance 2 Mini | 5 сек / 25 fps | высокая (плавные переходы) | минимальная (моргание, поворот) | глаза (моргание), голова (лёгкий наклон), губы (улыбка) | [заполнить после просмотра результата] |
| Пейзаж | Polza.ai, Seedance 2 Mini | 5 сек / 25 fps | средняя | средняя (2 элемента) | облака (дрейф), вода (рябь), листва (покачивание) | [заполнить] |
| Свободная | Polza.ai, Seedance 2 Mini | 5 сек / 25 fps | низкая (резкие переходы при макс. эффекте) | максимальная (полная трансформация) | небо (вращение), звёзды (мерцание), кипарис (покачивание), огни (мерцание) | [заполнить] |

The «Что пошло не так» column should be filled based on actual observation of the generated videos. Since the agent can't watch video, it should:
- Note visual artifacts mentioned in the model's documentation
- Note known limitations of Seedance 2 Mini (low resolution 480p, possible morphing artifacts)
- Note any errors returned during generation

### Step 5 — Write the reflection (150–250 words)

In `./logs/reflection.md`, write a reflection in Russian (150–250 words) covering:

1. **Эмоции** — what emotions each animation evokes:
   - Portrait: does the subtle movement make the person feel "alive" and present?
   - Landscape: does the gentle motion create a meditative, peaceful mood?
   - Painting: does the maximal animation transform the familiar Starry Night into something new and overwhelming?

2. **Изменение восприятия** — how perception changed vs the static image:
   - Portrait: static photo is a "moment"; animated is a "presence"
   - Landscape: static is a "postcard"; animated is a "memory"
   - Painting: static is a "masterpiece"; animated is an "experience"

3. **Где движение усилило/разрушило смысл:**
   - Enhanced: portrait (more intimate), landscape (more immersive)
   - Possibly destroyed: painting (Van Gogh's deliberate static composition may lose its power when over-animated)

4. **Применение** (for Кафедра ИС / Information Systems):
   - Educational: animated historical photos in online courses about AI/ML history
   - Museum: interactive exhibitions where paintings come alive
   - Media: animated thumbnails for IT tutorial videos, dynamic UI elements

### Step 6 — Build the 3 screenshot composites

Use Python + Pillow. Cyrillic-capable TTF font.

**Composite 1 — `01_sources_overview.png` (3 source images side by side, ~1800×700 px):**
- Title bar (60 px, dark #1A1A1A, white text): «Три исходных изображения для анимации»
- 3 panels side by side, each ~560 px wide:
  - Panel 1: portrait image — caption below: «S1: Портрет (ИИ-генерация, Polza.ai/z-image)»
  - Panel 2: landscape image — caption: «S2: Пейзаж (ИИ-генерация, Polza.ai/z-image)»
  - Panel 3: Van Gogh painting — caption: «S3: В. Ван Гог, «Звёздная ночь» (Public domain, Wikimedia)»
- 12 px gutters

**Composite 2 — `02_settings_table.png` (the filled settings table, ~1800×600 px):**
- Title bar (60 px, dark #1A1A1A, white text): «Таблица настроек анимаций»
- Render the table from Step 4 as a styled grid: 7 columns × 4 rows (header + 3 data rows)
- Header row: bold, light grey background
- All text TNR ~11 pt (small to fit)

**Composite 3 — `03_interface_mockup.png` (interface mockup, ~1600×1000 px):**
- Title bar (60 px, dark #1A1A1A, white text): «Интерфейс анимации: Polza.ai Media API»
- Simulate the animation settings interface:
  - Left panel: source image thumbnail + «Исходник: S1/S2/S3»
  - Right panel: settings
    - «Модель: bytedance/seedance-2-mini»
    - «Режим: image-to-video»
    - «Длительность: 5 сек»
    - «Интенсивность: минимальная / средняя / максимальная» (show all 3)
    - «Промпт движения: [the animation prompt text]»
  - Bottom: «Generate» button (blue) + a progress bar
- Show this for all 3 animations (either as 3 separate panels or as a tabbed interface mockup)

### Step 7 — Write the report `Отчет_М3_Задание3.docx`

Use `python-docx`. The report is **in Russian**. Formatting identical to all previous assignments.

#### 7.1 Title page — MUST match the official LETI template with CORRECT department

**CRITICAL:** The department is **«Кафедра ИС»**, NOT «Кафедра связи с общественностью».

**Exact title-page content:**
1. `МИНОБРНАУКИ РОССИИ` — centered, bold
2. `Санкт-Петербургский государственный электротехнический` — centered, bold
3. `университет «ЛЭТИ» им. В.И. Ульянова (Ленина)` — centered, bold
4. `Кафедра ИС` — centered, bold ← **CORRECTED**
5. Three empty paragraphs
6. `отчет` — centered, NOT bold, lowercase
7. `по заданию` — centered, bold
8. `по курсу «Применение генеративных нейронных моделей` — centered, bold
9. `в мультимедиа»` — centered, bold
10. `Тема: Оживление изображений: три анимации — три эффекта` — centered, NOT bold
11. Five empty paragraphs
12. **Borderless 3-column table** (same as all previous assignments):
    | Row | Col 1 | Col 2 | Col 3 |
    |-----|-------|-------|-------|
    | 1 | `Студент гр. ___` | (empty) | `Ханна М. Н.` |
    | 2 | `Преподаватель ___` | (empty) | `___` |
13. Four empty paragraphs
14. `Санкт-Петербург` — centered, NOT bold
15. `2026` — centered, NOT bold
16. Page break

#### 7.2 Body formatting rules

(Same as all previous assignments: A4, margins 2 cm, TNR 14 pt throughout, first-line indent 1.25 cm, justified, headings bold centered, captions TNR 12 pt italic, page numbers from page 2, no `___` except the two title-page fields.)

#### 7.3 Required body structure

1. **1. Введение** (~100 слов) — purpose: animating three images of different types (portrait, landscape, painting) at three intensity levels to study how motion changes perception.

2. **2. Исходные изображения** — describe the 3 sources:
   - S1: portrait (AI-generated, source, license)
   - S2: landscape (AI-generated, source, license)
   - S3: Van Gogh painting (public domain, source URL)
   - Embed `01_sources_overview.png` at ~15 cm width, captioned `Рисунок 1 — Три исходных изображения`

3. **3. Создание анимаций** — describe the animation process:
   - Service used: Polza.ai Media API (`bytedance/seedance-2-mini`, image-to-video)
   - Three intensity levels: minimal (portrait), medium (landscape), maximum (painting)
   - For each animation: the motion prompt, duration, result
   - Embed `03_interface_mockup.png` at ~14 cm width, captioned `Рисунок 2 — Интерфейс настройки анимации`

4. **4. Таблица настроек** — embed `02_settings_table.png` at ~15 cm width, captioned `Рисунок 3 — Таблица настроек по каждой работе`. Also present the table as a docx table (Таблица 1).

5. **5. Рефлексия** — the full reflection text (150–250 words) from `./logs/reflection.md`. Cover: emotions, perception change, where motion enhanced/destroyed meaning, applications in educational/museum/media projects (for Кафедра ИС).

6. **6. Результаты анимаций** — for each of the 3 animations:
   - **6.1. Портрет (минимальное движение)** — describe the result, what moved well, what didn't
   - **6.2. Пейзаж (средняя интенсивность)** — describe the result
   - **6.3. Свободный выбор (максимальные значения)** — describe the result
   - If the video files were generated, note their paths. If generation failed, explain why and what was expected.

7. **Приложение А** — full prompts and settings for all 3 animations (the exact text sent to the API).

8. **Приложение Б** — work log + cost: tool versions, API calls, timestamps, per-animation cost, total cost. From `./logs/worklog.md` and `./logs/cost.md`.

### Step 8 — Self-check (mandatory)

1. **Title-page format check (HIGHEST PRIORITY).** Render page 1 of the PDF to JPEG at 100 DPI and verify:
   - **The department reads `Кафедра ИС`** — NOT «Кафедра связи с общественностью». This is the most critical check.
   - The theme line reads `Тема: Оживление изображений: три анимации — три эффекта` — not bold.
   - `отчет` is lowercase.
   - Student name `Ханна М. Н.` with spaces between initials.
   - Page 1 has NO page number.

2. Reopen the `.docx` with python-docx. Print the heading outline, table count, image count (should be ≥ 3). Search for `TODO|XXX|placeholder|【`.

3. Verify the settings table (Таблица 1) has all 3 rows filled (Портрет, Пейзаж, Свободная).

4. Verify the reflection is 150–250 words.

5. Convert to PDF. Render pages 1, 2, and the last page to JPEG. Check formatting.

6. Verify all 3 source images exist in `./sources/`, all 3 animation videos exist in `./animations/` (if generation succeeded), and all 3 screenshot composites exist in `./screenshots/`.

7. Copy final files into `./deliverable/`: `Отчет_М3_Задание3.docx`, `Отчет_М3_Задание3.pdf`, `sources/`, `animations/`, `screenshots/`.

### Step 9 — Final summary

Print a final summary listing:
- absolute paths of all deliverables;
- whether each of the 3 animations was successfully generated (or which failed);
- the total cost in ₽;
- a reminder: the department on the title page is «Кафедра ИС» (verify!);
- the next step: upload everything on `open.etu.ru` before 2026-12-04 02:59 MSK, then complete peer review before 2026-12-11 02:59 MSK.

## 6. Hard constraints

- **CRITICAL: The department on the title page MUST be `Кафедра ИС`.** NOT «Кафедра связи с общественностью». Double-check this in the self-check step. If it says «связи с общественностью», the report is WRONG — fix it before delivering.
- **Do not invent facts about the animations.** If a video generation fails, document the failure honestly. Do not claim an animation was generated if it wasn't.
- **All 3 source images must be REAL.** S1 and S2 must be actually generated via Polza.ai. S3 must be actually downloaded from Wikimedia Commons. No placeholders.
- **The settings table must be FILLED** with actual data, not generic text.
- **The reflection must be 150–250 words** — count them.
- **The report is in Russian.** Only model IDs, URLs, and the English animation prompts may stay in English.
- **Stay inside the project directory.** Never write outside `./image-animation/` (and `./deliverable/`).
- **No placeholders** except the two title-page fields `Студент гр. ___` and `Преподаватель ___`. The student name `Ханна М. Н.` must appear verbatim, with spaces between initials.
- **Budget:** total Polza spend must stay under 60 ₽. If a single animation costs more than 20 ₽, abort and log it.
- **Same formatting as all previous assignments** — except the department is corrected to «Кафедра ИС».
- **Don't pause for human input** unless Step 1's pre-flight checks fail.

## 7. Anti-error rules (mandatory — learned from M3-A1/M3-A2 audit)

These rules are NON-NEGOTIABLE. They prevent the 9 error patterns found in the repair audits of previous Module 3 reports. Violating any of them means the report is defective.

### Rule A — Real screenshots only, never composites/mockups for service UIs

The assignment says «скриншоты интерфейса с настройками». This means REAL screen captures, NOT Pillow composites.

1. **For the interface/settings screenshot (`03_interface_mockup.png`):** capture a REAL screenshot of the Polza.ai web UI (the Media API playground page, or the models page showing `bytedance/seedance-2-mini`). Use headless Chrome:
   ```bash
   google-chrome --headless --screenshot=./screenshots/03_interface_real.png \
     --window-size=1440,900 "https://polza.ai/collections/video"
   ```
   Or use Playwright if available. If headless browser is unavailable, use web.archive.org snapshots of the Polza.ai video page.
2. **If neither works:** STOP and tell the user. Never generate a fake/mockup UI screenshot.
3. **For data visualizations** (the settings table, the sources overview): Pillow composites ARE acceptable — but caption them as «визуализация» or «диаграмма», NEVER as «скриншот».
4. **Figure captions must be honest:**
   - Real screenshot: «Рисунок N — Экран Polza.ai: [что показано] (снимок [дата])»
   - Data composite: «Рисунок N — Визуализация данных: [что показано]»
5. **Remove any «симуляция» / «макет» / «mock» language** from figure captions and report text. If it's a real screenshot, no disclaimer needed.

### Rule B — Cross-document number consistency

1. **Before writing the report**, compute ALL numbers from `./logs/` data. Store in `./logs/computed_stats.json`:
   - Total cost = sum of ALL API calls (image generation + video generation + any calibration/test calls)
   - Per-animation duration (from the video file metadata or API response)
   - Total duration = sum of per-animation durations
2. **After writing the report**, run a consistency check:
   - Extract every number from the .docx
   - Verify: total cost in intro = total cost in Appendix Б = sum of per-call costs in cost table
   - Verify: per-animation durations in settings table = durations in Appendix Б
   - Verify: counts (3 images, 3 animations) match everywhere
3. **If a number appears in two places, it must be the same** — or a footnote explains rounding.

### Rule C — Template field completeness

The assignment's settings table has 7 columns: Работа | Сервис | Скорость анимации | Плавность переходов | Глубина эффекта | Что именно двигалось | Что пошло не так.

1. **Every cell must be filled with specific data**, not generic text.
2. «Сервис» must state the exact model ID: «Polza.ai, bytedance/seedance-2-mini» — not just «Polza.ai».
3. «Что пошло не так» must describe a SPECIFIC issue observed (or «артефактов не обнаружено» if none) — not left empty.
4. Run a checklist: for each of the 7 columns × 3 rows, confirm the cell contains real data.

### Rule D — Complete cost accounting

1. **Include ALL API calls in the cost table:**
   - 2 image generation calls (S1 portrait, S2 landscape)
   - 3 video generation calls (A1, A2, A3)
   - Any calibration/test calls (e.g., a test image generation to verify the API works)
2. If any calls are excluded from the main table, add: «Калибровочные запросы (N шт., M ₽) в таблицу не входят; полная стоимость — X ₽.»
3. The total stated in the introduction MUST equal the all-in total.

### Rule E — Calendar dates in work logs

1. **Every work log entry MUST include the full calendar date** (YYYY-MM-DD).
2. Extract from: `date +%Y-%m-%d` at the start of the script, or from API response timestamps.
3. The work log table caption: «Таблица Б.1 — Хронология выполнения работы ([DATE], время MSK)».

### Rule F — Accurate characterization of assignment requirements

1. **Never claim something «входит в задание» unless the assignment literally requires it.**
2. The assignment lists examples («портрет», «пейзаж», «картина») — these are suggestions for the 3 image types, and the student chose specific instances.
3. When characterizing the assignment, quote the exact text: «Задание требует три исходника: портрет, пейзаж, изображение на выбор» — not «портрет входит в задание».

### Rule G — Technical term accuracy

1. **Verify every technical term:**
   - Polza.ai is a платформа/сервис, not a метод
   - Seedance is a модель, not a метод
   - Image-to-video is a режим/задача, not a метод
   - The animation technique is алгоритм/метод (e.g., «метод диффузии для генерации видео»)
2. When referencing a tool: «с помощью платформы [X]» or «через API [X]».

### Rule H — Date range verification

1. If the report states a date range for sources (e.g., «источники от [date1] до [date2]»), verify ALL items fall within it.
2. S3 (Van Gogh) is from 1889 / Wikimedia snapshot date — include it in the range.

### Rule I — Final automated consistency pass

Add to Step 8 (Self-check):

```python
# After generating the .docx, before converting to PDF:
import docx, re

doc = docx.Document("./report/Отчет_М3_Задание3.docx")
text = "\n".join(p.text for p in doc.paragraphs)
for t in doc.tables:
    for row in t.rows:
        text += "\n" + " | ".join(c.text for c in row.cells)

errors = []

# 1. No simulation/mockup language
if re.search(r"симуляц|макет|mock|composite", text, re.IGNORECASE):
    errors.append("FAIL: simulation/mockup language found — use real screenshots")

# 2. Department check
if "Кафедра связи с общественностью" in text:
    errors.append("FAIL: wrong department — must be 'Кафедра ИС'")
if "Кафедра ИС" not in text:
    errors.append("FAIL: department 'Кафедра ИС' missing")

# 3. No placeholders (except title-page ___)
for ph in ["TODO", "XXX", "FIXME"]:
    if ph in text:
        errors.append(f"FAIL: placeholder '{ph}' found")

# 4. Settings table completeness (7 columns × 3 rows)
# Check that "Что пошло не так" column has content in all 3 rows

# 5. Cost consistency
# Extract all cost numbers and verify they match

for e in errors:
    print(e)

if errors:
    print("\n!!! REPORT HAS ERRORS — FIX BEFORE DELIVERY !!!")
    exit(1)
else:
    print("✓ All anti-error checks passed.")
```

### Error-prevention summary

| Error from M3-A1/M3-A2 audit | Rule in this prompt | How to prevent |
|---|---|---|
| Screenshots were mockups, not real | A | Use headless Chrome for Polza.ai UI screenshot |
| Duration totals didn't match | B | Compute all stats from logs; cross-check |
| Pitch/statistics not reproducible | B | Never invent statistics; compute from raw data |
| Cost excluded calibration calls | D | Include ALL API calls in cost table |
| Missing calendar date in work log | E | Always include YYYY-MM-DD |
| Claimed models «входят в задание» | F | Quote assignment text accurately |
| Praat called a «метод» | G | Verify technical terms |
| Date range didn't cover one source | H | Verify all items within stated range |
| Template field missing required elements | C | Fill every cell with specific data |

Start now. Begin by creating the directory structure, then proceed through Steps 1 → 9 in order, applying all anti-error rules (§7) throughout.
