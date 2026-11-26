# Prompt for AI Agent — Module 3, Assignment 4: Short Film (Короткометражный ролик)

> Paste everything below this line into opencode desktop.

---

# TASK

You are an autonomous coding/agent assistant running in **opencode desktop** with full filesystem and shell access on my machine. Complete LETI coursework **Module 3, Assignment 4** end-to-end, using the **Polza.ai** API for all generative components and **FFmpeg** (local) for video editing. Produce the final deliverables in `./deliverable/`.

## 1. Context

I am a student at **St. Petersburg Electrotechnical University «ЛЭТИ» (LETI)**, course **«Применение генеративных нейронных моделей в мультимедиа»** (Prompt-002, осень 2026), **Кафедра ИС**. This is Module 3, Assignment 4.

**Original assignment (Russian, verbatim):**

> **Задание 4 (Модуль 3). Короткометражный ролик**
> Срок сдачи — 4 декабря 2026, 02:59 MSK. Срок взаимного оценивания — 11 декабря 2026.
>
> Создать короткометражный ролик на самостоятельно выбранную тему, в котором все ключевые компоненты созданы или существенно преобразованы с помощью генеративных моделей.
>
> - **Сценарий / раскадровка:** разработан при участии текстовой LLM; раскадровка минимум на 6 сцен.
> - **Визуальный ряд:** не менее 5 сгенерированных сцен (image-to-video / text-to-video / анимация сгенерированных изображений).
> - **Закадровый голос или диалог:** синтезирован TTS-инструментом; текст — осмысленный, связанный с сюжетом.
> - **Музыка:** сгенерирована нейросетью, соответствует настроению ролика.
> - **Звуковые эффекты (опционально):** сгенерированные или подобранные SFX.
> - **Монтаж:** единый стиль, переходы, сведение звука (голос не перекрывается музыкой), титры.
>
> **К сдаче:**
> 1. Готовый ролик — MP4, не ниже 1080p, со ссылкой на просмотр.
> 2. Производственный отчёт (PDF, 3–6 стр.): идея и целевая аудитория, раскадровка, перечень использованных инструментов на каждом этапе, ключевые промпты и их итерации (минимум 3 примера «было → стало»), описание проблем и способов их решения, таблица «что сгенерировано / что взято извне».

**Today is 2026-11-26. Deadline is 2026-12-04 02:59 MSK.** Peer review: 2026-12-11.

## 2. Film concept (FIXED)

### Title: «Рождение образа» (Birth of an Image)
### Genre: Micro-documentary (микродокументалка)
### Duration: ~25–30 seconds
### Theme: How AI transforms a text prompt into a visual artwork — a meta-documentary about the creative process of generative AI.

**Why this topic:**
- Directly relevant to the course (generative neural networks in multimedia)
- Allows abstract/artistic visuals that work well with any video model
- Voiceover can be in Russian (meaningful, connected to the visuals)
- Shows the AI-creation pipeline itself (script → images → video → music — all AI-generated)

### Target audience: Students and educators interested in AI-generated media.

### Storyboard (6 scenes):

| # | Scene | Visual | Duration | Voiceover (Russian) |
|---|-------|--------|----------|---------------------|
| 1 | «Текст» | Abstract text fragments floating in dark space, letters assembling into words | 4 sec | «Всё начинается с текста. Несколько слов — и нейросеть уже видит образ.» |
| 2 | «Зарождение» | A seed of light grows into swirling colors, like a nebula forming | 5 sec | «Из шума рождается структура. Пиксель за пикселем — emerges форма.» |
| 3 | «Форма» | A face or silhouette emerges from abstract colors, half-formed | 5 sec | «Сначала — силуэт. Потом — детали. Лицо, которого не существует.» |
| 4 | «Цвет» | Colors flow and merge, creating a vibrant abstract landscape | 5 sec | «Палитра выбирает настроение. Тёплые тона — или холодные?» |
| 5 | «Движение» | The image comes alive: elements move, the scene breathes | 5 sec | «И наконец — движение. Статика становится мгновением.» |
| 6 | «Результат» + титры | Final composite image, title «Рождение образа», credits | 4 sec | «Так из текста рождается образ. Это и есть генеративное искусство.» |

**Total: 28 seconds of video + ~3 seconds of title card = ~31 seconds**

## 3. Models and cost plan

| Component | Model | Polza ID | Cost estimate |
|---|---|---|---|
| Script + storyboard (2 LLM calls) | Gemini 2.5 Flash | `google/gemini-2.5-flash` | ~2 ₽ |
| 5 video scenes (text-to-video, 4–5 sec each) | Grok Imagine Video 1.5 | `grok-imagine-video-1-5` | ~37 ₽ (23 sec × 1.62) |
| Voiceover TTS (~25 sec of speech) | Gemini 3.8 Flash Lite TTS | `google/gemini-3.8-flash-lite-tts` | ~0.5 ₽ |
| Background music (~30 sec) | Suno (cheapest tier) | `suno/...` (check catalog) | ~2–5 ₽ |
| Video editing + 1080p export | FFmpeg (local) | — | 0 ₽ |
| Production report | python-docx → PDF | — | 0 ₽ |
| **Total** | | | **~42–45 ₽** |

### Substitution rules
- If `grok-imagine-video-1-5` fails: use `bytedance/seedance-2-mini` (2.56 ₽/sec, ~59 ₽ for 23 sec — total rises to ~70 ₽)
- If TTS fails: use `microsoft/mai-voice-2-flash` (1781 ₽/1M chars, ~0.9 ₽ for 500 chars)
- If Suno music generation is unavailable: use `google/lyria-3` (8 ₽ per Pro track)

## 4. Working directory layout

```
./short-film/
├── scripts/           # LLM script, storyboard, prompts
├── scenes/            # 5 generated video clips (.mp4)
├── audio/             # voiceover.mp3, music.mp3
├── final/             # final film.mp4 (1080p)
├── report/            # production report .docx + .pdf
├── screenshots/       # real screenshots of Polza.ai UI
├── logs/              # all JSON and MD logs
└── deliverable/       # final copies only
```

## 5. Step-by-step procedure

### Step 1 — Pre-flight checks

1. Verify `POLZA_API_KEY` is set (`echo "${POLZA_API_KEY:0:4}"` → `pza_`).
2. Verify Python ≥ 3.10, Pillow, python-docx, requests, openai, ffmpeg-python are installed. `pip install` anything missing.
3. Verify FFmpeg is installed: `ffmpeg -version` (must be ≥ 4.0).
4. Probe Polza API: `curl -sS https://polza.ai/api/v1/models -H "Authorization: Bearer $POLZA_API_KEY" | head -c 200`.
5. Verify model IDs: `grok-imagine-video-1-5`, `google/gemini-2.5-flash`, `google/gemini-3.8-flash-lite-tts`, and a music model (search for `suno` or `lyria` in the model list).
6. Record the calendar date: `date +%Y-%m-%d` → save to `./logs/session_date.txt`.
7. Log all checks into `./logs/worklog.md` WITH the calendar date.

### Step 2 — Generate script and storyboard (LLM)

Write `./scripts/generate_script.py`:

```python
from openai import OpenAI
import json, pathlib, time

client = OpenAI(api_key=KEY, base_url="https://polza.ai/api/v1")

SCRIPT_PROMPT = (
    "Напиши сценарий и раскадровку для короткометражного ролика длительностью "
    "25–30 секунд на тему «Рождение образа» — как ИИ превращает текстовый промпт "
    "в визуальное изображение. Жанр: микродокументалка. "
    "Раскадровка: минимум 6 сцен. Для каждой сцены укажи: "
    "1) номер, 2) визуальное описание (для text-to-video промпта на английском), "
    "3) длительность в секундах, 4) текст закадрового голоса на русском. "
    "Стиль визуального ряда: абстрактный, художественный, переход от тьмы к свету, "
    "от хаоса к форме. Настроение: вдохновляющее, задумчивое. "
    "Ответ в формате JSON."
)

r = client.chat.completions.create(
    model="google/gemini-2.5-flash",
    messages=[{"role": "user", "content": SCRIPT_PROMPT}],
    temperature=0.7,
    response_format={"type": "json_object"}
)

script = json.loads(r.choices[0].message.content)
pathlib.Path("./scripts/storyboard.json").write_text(
    json.dumps(script, ensure_ascii=False, indent=2)
)
```

**Prompt iteration tracking (for the report's «было → стало» section):** save 3 iterations of the script prompt:
- Iteration 1 (initial): «Напиши сценарий для ролика об ИИ.» → too vague
- Iteration 2: «Напиши сценарий 30-секундного ролика о генеративном ИИ, 6 сцен.» → better but lacks visual direction
- Iteration 3 (final): the full prompt above → specific, structured, JSON output

Save all 3 iterations to `./logs/prompt_iterations.md`.

### Step 3 — Generate 5 video scenes (text-to-video)

The video API on Polza.ai is **asynchronous**: POST to `/api/v1/media` → poll `/api/v1/media/$ID/operations`.

Write `./scripts/generate_scenes.py`:

```python
import requests, json, pathlib, time

API_KEY = open("/path/to/.polza_key").read().strip()
BASE = "https://polza.ai/api/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

storyboard = json.loads(pathlib.Path("./scripts/storyboard.json").read_text())
scenes = storyboard["scenes"][:5]  # first 5 scenes

results = []
for i, scene in enumerate(scenes, 1):
    print(f"Generating scene {i}...")

    # Text-to-video request
    data = {
        "model": "grok-imagine-video-1-5",
        "prompt": scene["visual_prompt"],  # English prompt for the video model
        "duration": scene.get("duration", 4)
    }

    r = requests.post(f"{BASE}/media", headers=HEADERS, json=data)
    if r.status_code != 200:
        # Try alternative model
        data["model"] = "bytedance/seedance-2-mini"
        r = requests.post(f"{BASE}/media", headers=HEADERS, json=data)

    if r.status_code == 200:
        task_id = r.json().get("id") or r.json().get("task_id")
        print(f"  Task ID: {task_id}")

        # Poll for completion (video generation takes 30–180 sec)
        for attempt in range(90):  # up to 15 minutes
            time.sleep(10)
            r2 = requests.get(f"{BASE}/media/{task_id}/operations", headers=HEADERS)
            if r2.status_code == 200:
                ops = r2.json()
                status = ops.get("status") or ops.get("state")
                if status in ("completed", "succeeded", "done"):
                    video_url = ops.get("result", {}).get("url") or ops.get("output", {}).get("url")
                    if video_url:
                        video_bytes = requests.get(video_url).content
                        output_path = f"./scenes/scene_{i:02d}.mp4"
                        pathlib.Path(output_path).write_bytes(video_bytes)
                        print(f"  Saved: {output_path} ({len(video_bytes)} bytes)")
                        results.append({"scene": i, "status": "success",
                                       "file": output_path, "size": len(video_bytes),
                                       "task_id": task_id})
                    break
                elif status in ("failed", "error"):
                    print(f"  FAILED: {ops}")
                    results.append({"scene": i, "status": "failed",
                                   "error": str(ops), "task_id": task_id})
                    break
        else:
            results.append({"scene": i, "status": "timeout", "task_id": task_id})
    else:
        results.append({"scene": i, "status": "error",
                       "status_code": r.status_code, "response": r.text[:500]})

pathlib.Path("./logs/scene_results.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=2)
)
```

### Step 4 — Generate voiceover (TTS)

Write `./scripts/generate_voiceover.py`:

```python
from openai import OpenAI
import json, pathlib

client = OpenAI(api_key=KEY, base_url="https://polza.ai/api/v1")

storyboard = json.loads(pathlib.Path("./scripts/storyboard.json").read_text())
# Concatenate all voiceover lines into one script
full_voiceover = " ".join(scene["voiceover"] for scene in storyboard["scenes"])

response = client.audio.speech.create(
    model="google/gemini-3.8-flash-lite-tts",
    voice="alloy",  # or Kore, if available
    input=full_voiceover
)
response.stream_to_file("./audio/voiceover.mp3")
print(f"Voiceover saved: {len(full_voiceover)} chars")
```

### Step 5 — Generate background music

Write `./scripts/generate_music.py`:

```python
import requests, json, pathlib, time

API_KEY = open("/path/to/.polza_key").read().strip()
BASE = "https://polza.ai/api/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Search for music models in the catalog
# Try Suno first, then Google Lyria
MUSIC_PROMPT = "Ambient, contemplative, cinematic background music for a short documentary about AI and creativity. Soft piano with electronic textures, 30 seconds, uplifting but thoughtful mood."

data = {
    "model": "suno/v4",  # or check the catalog for the exact ID
    "prompt": MUSIC_PROMPT,
    "duration": 30
}

r = requests.post(f"{BASE}/media", headers=HEADERS, json=data)
# If suno fails, try lyria
if r.status_code != 200:
    data["model"] = "google/lyria-3"
    r = requests.post(f"{BASE}/media", headers=HEADERS, json=data)

if r.status_code == 200:
    task_id = r.json().get("id")
    # Poll for completion (music generation takes 30–60 sec)
    for attempt in range(60):
        time.sleep(10)
        r2 = requests.get(f"{BASE}/media/{task_id}/operations", headers=HEADERS)
        if r2.status_code == 200:
            ops = r2.json()
            status = ops.get("status")
            if status in ("completed", "succeeded", "done"):
                music_url = ops.get("result", {}).get("url")
                if music_url:
                    music_bytes = requests.get(music_url).content
                    pathlib.Path("./audio/music.mp3").write_bytes(music_bytes)
                    print(f"Music saved ({len(music_bytes)} bytes)")
                    break
```

### Step 6 — Edit the final video with FFmpeg

Write `./scripts/edit_video.sh`:

```bash
#!/bin/bash
set -e

# 1. Concatenate 5 scenes into one video
# Create a concat list file
cat > ./scenes/concat_list.txt << EOF
file 'scene_01.mp4'
file 'scene_02.mp4'
file 'scene_03.mp4'
file 'scene_04.mp4'
file 'scene_05.mp4'
EOF

# Concatenate scenes
ffmpeg -y -f concat -safe 0 -i ./scenes/concat_list.txt -c copy ./final/concat.mp4

# 2. Scale to 1080p (1920x1080)
ffmpeg -y -i ./final/concat.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black" -c:v libx264 -preset medium -crf 23 -c:a aac ./final/video_1080p.mp4

# 3. Add voiceover audio (ducked under music)
# First, create a mixed audio track: voiceover at full volume + music at -15dB
ffmpeg -y -i ./audio/voiceover.mp3 -i ./audio/music.mp3 \
  -filter_complex "[1:a]volume=-15dB[music];[0:a][music]amix=inputs=2:duration=first:dropout_transition=0[a]" \
  -map "[a]" ./audio/mixed_audio.mp3

# 4. Replace video audio with mixed audio
ffmpeg -y -i ./final/video_1080p.mp4 -i ./audio/mixed_audio.mp3 \
  -map 0:v -map 1:a -c:v copy -c:a aac -shortest ./final/film_with_audio.mp4

# 5. Add title card at the end (3 seconds)
# Create a title image with Pillow first, then:
ffmpeg -y -i ./final/film_with_audio.mp4 -i ./scripts/title_card.png \
  -filter_complex "[1:v]scale=1920:1080[title];[0:v][title]concat=n=2:v=1:a=0[v]" \
  -map "[v]" -map 0:a? -c:v libx264 -preset medium -crf 23 -c:a aac \
  ./final/Рождение_образа.mp4

echo "Final film: ./final/Рождение_образа.mp4"
ffprobe -v quiet -print_format json -show_streams ./final/Рождение_образа.mp4
```

**Audio mixing requirement:** «голос не перекрывается музыкой» — the voiceover must be audible. The music is at -15dB (background level) while the voiceover is at full volume. The `amix` filter combines them.

### Step 7 — Capture real screenshots of Polza.ai UI

Per the anti-error ruleset (Rule A), screenshots must be REAL captures, not composites.

```bash
# Use headless Chrome to capture real screenshots of Polza.ai
google-chrome --headless --screenshot=./screenshots/01_polza_video_catalog.png \
  --window-size=1440,900 "https://polza.ai/collections/video"

google-chrome --headless --screenshot=./screenshots/02_polza_media_api.png \
  --window-size=1440,900 "https://polza.ai/docs/api-reference/media"

# If headless Chrome is not available, try Playwright:
# python -c "from playwright.sync_api import sync_playwright; ..."
```

If neither Chrome nor Playwright is available, use `curl` to fetch the pages and save them as HTML, then note in the report that screenshots were not possible due to environment limitations (honest disclosure).

### Step 8 — Write the production report (PDF, 3–6 pages)

Use `python-docx` → convert to PDF with LibreOffice.

**Title page:** same LETI template, `Кафедра ИС`, theme: `Тема: Короткометражный ролик «Рождение образа»`.

**Body structure (3–6 pages):**

1. **Идея и целевая аудитория** (~100 слов)
   - Film title, genre, duration
   - Concept: meta-documentary about AI image generation
   - Target audience: students and educators interested in AI media

2. **Раскадровка** — table of 6 scenes (from `./scripts/storyboard.json`):
   | # | Сцена | Визуальное описание | Длительность | Закадровый текст |

3. **Перечень использованных инструментов**
   | Этап | Инструмент | Модель | Назначение |
   |---|---|---|---|
   | Сценарий | Polza.ai | gemini-2.5-flash | Текст LLM |
   | Видео | Polza.ai | grok-imagine-video-1-5 | Text-to-video |
   | Озвучка | Polza.ai | gemini-3.8-flash-lite-tts | TTS |
   | Музыка | Polza.ai | suno/v4 или lyria-3 | Music generation |
   | Монтаж | FFmpeg (локально) | — | Сведение, титры, 1080p |

4. **Ключевые промпты и итерации** — minimum 3 «было → стало» examples:
   - Example 1: script prompt (vague → specific JSON)
   - Example 2: scene 1 video prompt (initial → refined)
   - Example 3: music prompt (generic → mood-specific)

5. **Описание проблем и решений**
   - Any API errors, timeouts, model substitutions
   - Audio mixing challenges (voice vs music levels)
   - Resolution upscaling (480p → 1080p via FFmpeg)

6. **Таблица «что сгенерировано / что взято извне»**
   | Компонент | Источник | Сгенерировано ИИ / Взято извне |
   |---|---|---|
   | Сценарий | Polza.ai LLM | Сгенерировано |
   | 5 видео-сцен | Polza.ai video API | Сгенерировано |
   | Закадровый голос | Polza.ai TTS | Сгенерировано |
   | Музыка | Polza.ai music API | Сгенерировано |
   | Монтаж | FFmpeg | Локальная обработка |
   | Титры | python-docx + FFmpeg | Сгенерировано |
   | Звуковые эффекты | — | Не использовались (опционально) |

7. **Приложение** — cost table, work log with calendar dates.

### Step 9 — Self-check + anti-error rules

Run ALL checks from the anti-error ruleset (§7 below) PLUS:

1. Verify the final MP4 exists, is ≥1080p (`ffprobe` check), and has audio.
2. Verify the report is 3–6 pages.
3. Verify all 5 scenes were generated (or document failures honestly).
4. Verify voiceover is audible over music (check audio levels with `ffmpeg -af volumedetect`).
5. Verify the report has ≥3 «было → стало» prompt examples.
6. Verify «Кафедра ИС» on the title page (NOT «связи с общественностью»).
7. Verify all costs in the report match `./logs/cost.md`.

## 6. Hard constraints

- **CRITICAL: The department on the title page MUST be `Кафедра ИС`.**
- **All components must be AI-generated or AI-transformed.** No stock footage, no pre-recorded music, no human voice. Only FFmpeg processing is non-AI.
- **The final video MUST be ≥1080p** (1920×1080). Use FFmpeg scaling if the source models output lower resolution.
- **Voiceover MUST be audible** over music (music at -15dB or lower).
- **Do not invent facts.** If a scene generation fails, document it honestly.
- **Budget: ≤ 60 ₽** total Polza spend. If approaching the limit, use cheaper models.
- **Stay inside `./short-film/`** (and `./deliverable/`).
- **No placeholders** except `Студент гр. ___` and `Преподаватель ___`.
- **Student name: `Ханна М. Н.`** with spaces between initials.

## 7. Anti-error rules (mandatory — from M3-A1/M3-A2 audit)

### Rule A — Real screenshots only
Capture real Polza.ai UI screenshots with headless Chrome (Step 7). Never build mockups. If Chrome is unavailable, use web.archive.org or disclose honestly.

### Rule B — Cross-document number consistency
- Total cost in report = sum of all API calls in `./logs/cost.md`
- Scene durations in storyboard = durations in final video (verify with `ffprobe`)
- All numbers must match across tables and text

### Rule C — Template field completeness
- The «что сгенерировано / что взято извне» table must cover ALL components
- The tools table must list every tool used at every stage
- The «было → стало» section must have ≥3 examples

### Rule D — Complete cost accounting
- Include ALL API calls: 2 LLM + 5 video + 1 TTS + 1 music + any calibration/test calls
- If any calls are excluded, note: «Калибровочные запросы (N шт., M ₽) не входят в таблицу; полная стоимость — X ₽.»

### Rule E — Calendar dates in work logs
- Every work log entry includes YYYY-MM-DD (from `date +%Y-%m-%d`)
- Work log caption: «Таблица — Хронология выполнения работы ([DATE], время MSK)»

### Rule F — Accurate characterization
- Don't say components «входят в задание» — say «задание требует [X], использован [Y]»

### Rule G — Technical term accuracy
- Polza.ai = платформа, FFmpeg = программа/инструмент, Gemini = модель
- Never call software a «метод»

### Rule H — Date range verification
- If stating a date range for sources, verify all items fall within it

### Rule I — Final automated consistency pass
```python
import docx, re, subprocess

# Check the final video
result = subprocess.run(
    ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams",
     "./final/Рождение_образа.mp4"],
    capture_output=True, text=True
)
streams = json.loads(result.stdout)
video_stream = next(s for s in streams["streams"] if s["codec_type"] == "video")
width, height = int(video_stream["width"]), int(video_stream["height"])
assert height >= 1080, f"FAIL: video height {height} < 1080"
print(f"✓ Video resolution: {width}x{height}")

# Check the report
doc = docx.Document("./report/Отчет_М3_Задание4.docx")
text = "\n".join(p.text for p in doc.paragraphs)
for t in doc.tables:
    for row in t.rows:
        text += "\n" + " | ".join(c.text for c in row.cells)

errors = []
if "Кафедра связи с общественностью" in text:
    errors.append("FAIL: wrong department")
if "Кафедра ИС" not in text:
    errors.append("FAIL: department missing")
if re.search(r"симуляц|макет|mock", text, re.IGNORECASE):
    errors.append("FAIL: simulation language found")
for ph in ["TODO", "XXX", "FIXME"]:
    if ph in text:
        errors.append(f"FAIL: placeholder {ph}")

# Check ≥3 «было → стало» examples
было_стало_count = text.count("было") + text.count("→") + text.count("стало")
if было_стало_count < 6:  # at least 3 pairs × 2 keywords
    errors.append("FAIL: fewer than 3 «было → стало» examples")

# Check page count (3–6 pages)
# ... (use pdfinfo)

for e in errors:
    print(e)
if errors:
    print("\n!!! REPORT HAS ERRORS — FIX BEFORE DELIVERY !!!")
else:
    print("✓ All anti-error checks passed.")
```

Start now. Begin by creating the directory structure, then proceed through Steps 1 → 9 in order, applying all anti-error rules (§7) throughout.
