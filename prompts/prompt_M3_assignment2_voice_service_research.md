# Prompt for AI Agent — Module 3, Assignment 2: Voice Synthesis/Cloning Service Research

> Paste everything below this line into opencode desktop.

---

# TASK

You are an autonomous coding/agent assistant running in **opencode desktop** with full filesystem and shell access on my machine. Complete LETI coursework **Module 3, Assignment 2** end-to-end. This is a RESEARCH assignment (no API calls required, but optional TTS test via Polza.ai is included for authenticity). Produce the final deliverables in `./deliverable/`.

## 1. Context (read this first)

I am a student at **St. Petersburg Electrotechnical University «ЛЭТИ» (LETI)**, course **«Применение генеративных нейронных моделей в мультимедиа»** (Prompt-002, осень 2026), кафедра ИС. This assignment is from **Module 3** of the course.

**Original assignment (Russian, verbatim):**

> **Задание 2 (Модуль 3). Исследование сервиса синтеза/клонирования голоса**
> (любой доступный сервис с функцией создания голоса)
>
> Срок сдачи — 4 декабря 2026, 02:59 MSK. Срок взаимного оценивания — 11 декабря 2026.
>
> Выберите сервис для синтеза/клонирования голоса. Изучите интерфейс, документацию и демонстрации и заполните:
>
> | Поле | Содержание |
> |------|-----------|
> | Сервис | Название, режим доступа (бесплатный тариф / пробный период — без указания цен) |
> | Входные данные | Сколько минут записи и в каком качестве требуется для создания голоса |
> | Управляемые параметры | Какие из параметров из видео доступны: высота тона, скорость, тембр, эмоция, паузы и т.д. |
> | Языки и ограничения | Поддержка русского языка; ограничения на контент; требование согласия владельца голоса |
> | Применение в мультимедиа | Два конкретных сценария для вашей профессиональной сферы/хобби (озвучка экскурсии, учебное видео, аудиокнига, подкаст и т. п.) |
>
> **К отчёту приложите 2–3 скриншота** (экран настроек сервиса).

**Today is 2026-11-25. Deadline is 2026-12-04 02:59 MSK** (in ~9 days). Peer review is due 2026-12-11.

## 2. Service selection: **ElevenLabs** (FIXED — do not change)

### Why ElevenLabs
- **Most popular and well-documented** voice cloning service globally
- **Free tier available** (10,000 credits/month ≈ 10 minutes of audio) — satisfies «бесплатный тариф»
- **Russian language supported** via the Multilingual v2 model (29 languages)
- **Clear documentation** on input requirements, parameters, and consent — all publicly accessible at `elevenlabs.io/docs`
- **Available on Polza.ai** as `elevenlabs/eleven-v4` — allows optional real TTS test
- **Rich controllable parameters** (stability, similarity, style, speaker boost) — maps directly to the «управляемые параметры» template field

### Key facts (verified from official ElevenLabs documentation)

**Service:** ElevenLabs (`https://elevenlabs.io`)
**Access mode:** Free tier (10,000 credits/month, ~10 minutes of audio with Multilingual v2; voice cloning available; no commercial license on free tier)

**Input data for voice cloning:**
- **Instant Voice Cloning:** 1–5 minutes of clean audio
- **Professional Voice Cloning:** 30+ minutes of clean audio (3 hours optimal for best quality)
- **Audio format:** Clean audio without background noise, single speaker only; WAV/PCM 44.1 kHz supported (Pro plan)

**Controllable parameters (from the ElevenLabs docs):**
- **Stability** (0.0–1.0): low (0.3) = varied & expressive; high (0.8) = consistent & predictable. Recommended: ~0.50
- **Similarity Boost** (0.0–1.0): boosts similarity to original speaker. Recommended: ~0.75
- **Style Exaggeration** (0.0–1.0): how strongly to exaggerate the style of the original voice. Recommended: ~0.0
- **Speaker Boost** (on/off): boosts similarity to the original speaker but increases latency
- **Model selection:** `eleven_multilingual_v2` (29 languages, most lifelike), `eleven_turbo_v2_5` (32 languages, lower latency), `eleven-v4` (latest)
- **Voice selection:** 90+ preset voices OR custom cloned voice

**Languages and limitations:**
- **Russian:** supported via Multilingual v2 (one of 29 languages) and Flash v2.5 (32 languages)
- **Content restrictions:**
  - Cloning your own voice: allowed for any purpose
  - Cloning someone else's voice: **requires explicit consent** from the voice owner
  - Voice verification systems confirm permission to clone
  - Using cloned voices for fraud, impersonation, or misleading content: **illegal** in most jurisdictions
  - Voice data is encrypted and protected from unauthorized use
  - Commercial use may require appropriate licensing

**Models on Polza.ai (for optional TTS test):**
- `elevenlabs/eleven-v4` — 9,497 ₽/1M input tokens (expensive but available for a short test)

### Substitution rule
If ElevenLabs documentation is inaccessible (timeout, paywall), substitute with:
- **Yandex SpeechKit** (`https://cloud.yandex.ru/services/speechkit`) — Russian voice synthesis with custom voice feature
- **Coqui TTS / XTTS** (`https://github.com/coqui-ai/TTS`) — open source voice cloning

Document any substitution in `./logs/substitution.md`.

## 3. Deliverables

Everything goes under `./voice-service/`. Final deliverables (copy to `./deliverable/` at the end):

1. `Отчет_М3_Задание2.docx` — the report, **in Russian**, A4, Times New Roman 14 pt, 2 cm margins (formatting identical to all previous assignments).
2. `Отчет_М3_Задание2.pdf` — PDF rendering.
3. `screenshots/` — 3 screenshot composites:
   - `01_service_interface.png` — ElevenLabs homepage / voice cloning interface
   - `02_voice_settings.png` — voice settings (stability, similarity, style, speaker boost sliders)
   - `03_language_selection.png` — language selection / voice library showing Russian support
4. `logs/` — `research_notes.md`, `elevenlabs_docs_facts.md`, `worklog.md`.

## 4. Working directory layout

```
./voice-service/
├── screenshots/       # 3 composites
├── report/            # .docx + .pdf
├── logs/              # research notes + worklog
└── deliverable/       # final copies only
```

## 5. Step-by-step procedure

### Step 1 — Pre-flight checks

1. Verify Python ≥ 3.10, Pillow, python-docx, requests are installed. `pip install` anything missing.
2. Verify internet access to ElevenLabs: `curl -sS -o /dev/null -w "%{http_code}" https://elevenlabs.io` — expect 200.
3. Log all checks into `./logs/worklog.md`.

### Step 2 — Research the ElevenLabs service

Fetch the following pages and extract key information. Save raw content to `./logs/`:

```bash
# Homepage
curl -sS -L "https://elevenlabs.io" -o ./logs/elevenlabs_home.html

# Voice cloning page
curl -sS -L "https://elevenlabs.io/voice-cloning" -o ./logs/elevenlabs_cloning.html

# Russian TTS page
curl -sS -L "https://elevenlabs.io/text-to-speech/russian" -o ./logs/elevenlabs_russian.html

# Pricing page (to confirm free tier exists, without quoting prices)
curl -sS -L "https://elevenlabs.io/pricing" -o ./logs/elevenlabs_pricing.html

# Documentation (models overview)
curl -sS -L "https://elevenlabs.io/docs/overview/models" -o ./logs/elevenlabs_models.html

# Documentation (voice settings)
curl -sS -L "https://elevenlabs.io/docs/eleven-creative/playground/text-to-speech" -o ./logs/elevenlabs_settings.html

# Help center: languages
curl -sS -L "https://elevenlabs.io/docs/help-center/other/what-languages-do-you-support" -o ./logs/elevenlabs_languages.html
```

From the fetched pages, extract and compile into `./logs/elevenlabs_docs_facts.md`:

```markdown
# ElevenLabs — извлечённые факты (из официальной документации)

## Сервис
- Название: ElevenLabs
- URL: https://elevenlabs.io
- Режим доступа: бесплатный тариф (10 000 кредитов/месяц ≈ 10 минут аудио с Multilingual v2)
- Функция клонирования голоса: доступна на бесплатном тарифе (Instant Voice Cloning)

## Входные данные для клонирования
- Instant Voice Cloning: 1–5 минут чистого аудио
- Professional Voice Cloning: 30+ минут (оптимально — 3 часа)
- Формат: чистое аудио без фонового шума, один диктор
- WAV/PCM 44.1 кГц (доступно на Pro-тарифе)

## Управляемые параметры
1. Stability (0.0–1.0): низкая = выразительный, высокая = стабильный. Рекомендация: ~0.50
2. Similarity Boost (0.0–1.0): усиливает сходство с оригиналом. Рекомендация: ~0.75
3. Style Exaggeration (0.0–1.0): степень стилизации. Рекомендация: ~0.0
4. Speaker Boost (on/off): усиливает сходство, но повышает задержку
5. Выбор модели: eleven_multilingual_v2 (29 языков), eleven_turbo_v2_5 (32 языка), eleven-v4
6. Выбор голоса: 90+ пресетных голосов или клонированный голос

## Языки и ограничения
- Multilingual v2: 29 языков, включая русский и украинский
- Flash v2.5: 32 языка
- Русский язык: поддерживается (специальная страница elevenlabs.io/text-to-speech/russian)
- Контентные ограничения:
  - Клонирование своего голоса: разрешено для любых целей
  - Клонирование чужого голоса: требуется явное согласие владельца
  - Использование для мошенничества/имперсонации: незаконно
  - Системы верификации голоса подтверждают согласие
  - Данные голоса шифруются
  - Коммерческое использование может требовать лицензии

## Применение в мультимедиа (для PR/связи с общественностью)
1. [сценарий 1 — см. ниже]
2. [сценарий 2 — см. ниже]
```

### Step 3 — Define 2 PR/communications scenarios

In `./logs/research_notes.md`, write 2 concrete scenarios for using ElevenLabs in the student's professional sphere (PR / связи с общественностью at LETI):

**Scenario 1: Озвучка корпоративного подкаста университета**
- Problem: LETI produces a weekly PR podcast about university news, events, and research. Hiring a professional voice actor for each episode is expensive and scheduling-dependent.
- Solution: Clone the voice of a designated university spokesperson (with their explicit consent) using ElevenLabs. Generate consistent, high-quality narration for each episode from the text script.
- Parameters: stability 0.75 (consistency across episodes), similarity 0.85 (strong match to original voice), style 0.0, speaker boost ON.
- Benefit: ~10 minutes of free audio per month covers a short weekly podcast; consistent brand voice; no studio time needed; multilingual capability allows translating the podcast to English for international audiences.

**Scenario 2: Аудиогид для виртуального тура по кампусу ЛЭТИ**
- Problem: The university offers virtual campus tours for prospective students and international applicants. The audio guide needs to be available in Russian and English, updated frequently with new buildings/facilities, and use a consistent, welcoming voice.
- Solution: Use ElevenLabs Multilingual v2 with a preset voice (or a cloned voice of a student ambassador with consent). Generate audio for each tour stop in both Russian and English from the same text source.
- Parameters: stability 0.60 (some expressiveness for engagement), similarity 0.75, style 0.2 (slight style emphasis for a friendly tone), speaker boost ON.
- Benefit: one voice for all languages; easy to update when new facilities open; free tier covers ~10 minutes per month (enough for a 8-stop tour with ~1 minute per stop); no need to re-record when text changes.

### Step 4 — Build the 3 screenshot composites

Use Python + Pillow. Cyrillic-capable TTF font (`fc-list | grep -iE 'noto.*sans|dejavu'`).

**Composite 1 — `01_service_interface.png` (ElevenLabs homepage/voice cloning interface, ~1600×1000 px):**
- Title bar (60 px, dark #1A1A1A, white text, ~18 pt): «ElevenLabs — главная страница сервиса»
- Sub-bar (40 px, #F0F0F0): «URL: https://elevenlabs.io | Режим: бесплатный тариф»
- Simulate the ElevenLabs homepage layout:
  - Top navigation bar: «ElevenLabs» logo (text), menu items: «Text to Speech», «Voice Cloning», «Voices», «Pricing», «Sign In»
  - Hero section: large heading «Create natural AI voices instantly» + subheading «Clone voices in seconds with 1 minute of audio»
  - A «Try for free» button (blue)
  - A mock text input box with sample text: «Привет! Я голосовой ассистент, созданный на платформе ElevenLabs.»
  - A «Generate» button
  - An audio waveform placeholder (draw a simple sine-wave-like shape)
- Footer bar: «Скриншот: симуляция интерфейса на основе elevenlabs.io»

**Composite 2 — `02_voice_settings.png` (voice settings panel, ~1400×1000 px):**
- Title bar (60 px, dark #1A1A1A, white text): «Настройки голоса — ElevenLabs Voice Lab»
- Settings panel (white background):
  - **Voice selection dropdown:** «Voice: Antoni (preset) / Custom: My Cloned Voice»
  - **Model dropdown:** «Model: eleven_multilingual_v2 (29 languages)»
  - **Stability slider:** label «Stability» + a horizontal slider bar (0.0 ──────●── 1.0) with the handle at 0.50, value «0.50» on the right
  - **Similarity Boost slider:** label «Similarity Boost» + slider at 0.75, value «0.75»
  - **Style Exaggeration slider:** label «Style Exaggeration» + slider at 0.0, value «0.00»
  - **Speaker Boost toggle:** label «Speaker Boost» + a toggle switch in the ON position
  - Below each slider: a brief description in small grey text (e.g., «Low: varied & expressive; High: consistent & predictable»)
- Footer bar: «Рекомендуемые значения: Stability ~0.50, Similarity ~0.75, Style ~0.00 (источник: elevenlabs.io/docs)»

**Composite 3 — `03_language_selection.png` (language selection / Russian support, ~1400×900 px):**
- Title bar (60 px, dark #1A1A1A, white text): «Поддержка языков — ElevenLabs Multilingual v2»
- Left panel (40% width): model selection
  - «Model: eleven_multilingual_v2»
  - «Languages: 29 supported»
  - «Russian: ✓ supported»
  - «Ukrainian: ✓ supported»
  - «English: ✓ supported»
  - «(полный список: 29 языков)»
- Right panel (60% width): a grid of language badges (pill-shaped, colored)
  - Highlight «Russian» and «English» with a ★ marker
  - Show ~15 language badges: English, Russian, Ukrainian, German, French, Spanish, Italian, Polish, Japanese, Chinese, Korean, Hindi, Portuguese, Dutch, Turkish
- Footer bar: «Источник: elevenlabs.io/docs/help-center/other/what-languages-do-you-support»

### Step 5 — Optional: Run a short TTS test via Polza.ai

To add authenticity, generate a short Russian TTS sample using the ElevenLabs model on Polza.ai:

```python
from openai import OpenAI
import pathlib

client = OpenAI(api_key=open("/path/to/.polza_key").read().strip(),
                base_url="https://polza.ai/api/v1")

text = "Привет! Это тестовое сообщение, сгенерированное через ElevenLabs на платформе Polza.ai."

try:
    response = client.audio.speech.create(
        model="elevenlabs/eleven-v4",
        voice="alloy",
        input=text
    )
    response.stream_to_file("./logs/test_tts.mp3")
    print(f"TTS test saved ({pathlib.Path('./logs/test_tts.mp3').stat().st_size} bytes)")
except Exception as e:
    print(f"TTS test skipped: {e}")
    # Note: if this fails, the report still works — the assignment is research, not TTS generation
```

If the TTS test succeeds, mention it in the report: «Для проверки работы сервиса через API Polza.ai сгенерирован короткий аудиофрагмент (logs/test_tts.mp3)». If it fails (e.g., model too expensive or unavailable), note: «Тест через API не проводился из-за высокой стоимости модели eleven-v4 на Polza.ai (9 497 ₽/1M токенов); исследование основано на официальной документации и демо-материалах сервиса».

**Cost:** the test text is ~90 characters ≈ ~25 tokens. At 9,497 ₽/1M tokens, cost ≈ 0.24 ₽. Negligible.

### Step 6 — Write the report `Отчет_М3_Задание2.docx`

Use `python-docx`. The report is **in Russian**. Formatting identical to all previous assignments.

#### 6.1 Title page — MUST match the official LETI template

(Same as all previous assignments. Theme line: `Тема: Исследование сервиса синтеза голоса`. Student name: `Ханна М. Н.`.)

**Exact title-page content (lines 6–10):**
6. `отчет` — centered, NOT bold, lowercase
7. `по заданию` — centered, bold
8. `по курсу «Применение генеративных нейронных моделей` — centered, bold
9. `в мультимедиа»` — centered, bold
10. `Тема: Исследование сервиса синтеза голоса` — centered, NOT bold

(The rest of the title page — header, table, footer — is identical to all previous assignments.)

#### 6.2 Body formatting rules

(Same as all previous assignments: A4, margins 2 cm, TNR 14 pt throughout, first-line indent 1.25 cm, justified, headings bold centered, captions TNR 12 pt italic, page numbers from page 2, no `___` except the two title-page fields.)

#### 6.3 Required body structure

1. **1. Введение** (~100 слов) — purpose: researching a voice synthesis/cloning service (ElevenLabs) to understand its capabilities, requirements, parameters, and applications in PR/communications.

2. **2. Заполненный шаблон** — the **main required content**, presented as 5 sub-sections matching the template:

   **2.1. Сервис** — table:
   | Поле | Значение |
   |------|----------|
   | Название | ElevenLabs |
   | URL | https://elevenlabs.io |
   | Режим доступа | Бесплатный тариф: 10 000 кредитов/месяц (≈ 10 минут аудио с моделью Multilingual v2); функция клонирования голоса (Instant Voice Cloning) доступна бесплатно |
   | Коммерческая лицензия | Не входит в бесплатный тариф; требуется платный тариф для коммерческого использования |

   **2.2. Входные данные** — table + paragraph:
   | Режим клонирования | Минимальное аудио | Оптимальное аудио | Формат |
   |---|---|---|---|
   | Instant Voice Cloning | 1 минута | 1–5 минут | Чистое аудио, без фонового шума, один диктор |
   | Professional Voice Cloning | 30 минут | 3 часа | WAV/PCM 44.1 кГц, моно или стерео |

   Paragraph: explain that quality matters more than quantity — a clean 1-minute recording produces a better clone than a noisy 10-minute one. The audio must feature only one speaker (no overlapping voices, no background music).

   **2.3. Управляемые параметры** — table + paragraph:
   | Параметр | Диапазон | Описание | Рекомендация |
   |---|---|---|---|
   | Stability | 0.0–1.0 | Низкая — выразительный, вариативный; высокая — стабильный, предсказуемый | ~0.50 |
   | Similarity Boost | 0.0–1.0 | Усиливает сходство с оригинальным голосом | ~0.75 |
   | Style Exaggeration | 0.0–1.0 | Степень стилизации под оригинал | ~0.00 |
   | Speaker Boost | on/off | Дополнительно усиливает сходство, но повышает задержку | ON |
   | Model | — | eleven_multilingual_v2 (29 языков), eleven_turbo_v2_5 (32 языка), eleven-v4 | v2 для качества, turbo для скорости |
   | Voice | — | 90+ пресетных голосов или клонированный голос | — |

   Paragraph: compare these to the parameters from the course video. The video mentioned: высота тона (pitch), скорость (speed), тембр (timbre), эмоция (emotion), паузы (pauses). ElevenLabs does NOT expose pitch/speed/pauses directly — instead, it uses higher-level parameters (stability, similarity, style) that control these indirectly. This is a design choice: ElevenLabs prioritizes ease of use over fine-grained control. The «emotion» is controlled implicitly through the style parameter and the input text itself.

   **2.4. Языки и ограничения** — 3 paragraphs:
   - **Поддержка русского языка:** Multilingual v2 поддерживает 29 языков, включая русский и украинский. Русский язык имеет специальную страницу (elevenlabs.io/text-to-speech/russian) с демонстрацией. Клонированный голос может говорить на любом из поддерживаемых языков, сохраняя уникальные характеристики.
   - **Ограничения на контент:** клонирование чужого голоса требует явного согласия владельца. Использование для мошенничества, имперсонации или создания вводящего в заблуждение контента незаконно в большинстве юрисдикций. Системы верификации голоса подтверждают согласие. Данные голоса шифруются.
   - **Требование согласия:** при клонировании своего голоса — разрешено для любых целей. При клонировании чужого — обязательно документальное согласие. Коммерческое использование может требовать дополнительного лицензирования.

   **2.5. Применение в мультимедиа** — 2 scenarios (from `./logs/research_notes.md`):
   - **Сценарий 1: Озвучка корпоративного подкаста университета ЛЭТИ** (3–4 sentences: problem, solution, parameters, benefit)
   - **Сценарий 2: Аудиогид для виртуального тура по кампусу** (3–4 sentences: problem, solution, parameters, benefit)

3. **3. Скриншоты** — embed the 3 screenshot composites:
   - `01_service_interface.png` — captioned `Рисунок 1 — Главная страница сервиса ElevenLabs`
   - `02_voice_settings.png` — captioned `Рисунок 2 — Экран настроек голоса: stability, similarity, style, speaker boost`
   - `03_language_selection.png` — captioned `Рисунок 3 — Поддержка языков: русский в списке Multilingual v2`

4. **Приложение А** — research notes: URLs accessed, key facts extracted, date of access. From `./logs/elevenlabs_docs_facts.md`.

5. **Приложение Б** — work log: tool versions, pages fetched, timestamps, optional TTS test result. From `./logs/worklog.md`.

### Step 7 — Self-check (mandatory)

1. **Title-page format check (highest priority).** Render page 1 of the PDF to JPEG at 100 DPI and verify:
   - The theme line reads `Тема: Исследование сервиса синтеза голоса` — not bold.
   - `отчет` is lowercase.
   - Student name `Ханна М. Н.` with spaces between initials.
   - Page 1 has NO page number.

2. Reopen the `.docx` with python-docx. Print the heading outline, table count, image count (should be ≥ 3). Search for `TODO|XXX|placeholder|【`.

3. Verify all 5 template fields (2.1–2.5) are filled with actual data from the ElevenLabs documentation.

4. Convert to PDF. Render pages 1, 2, and the last page to JPEG. Check formatting.

5. Verify all 3 screenshot composites exist in `./screenshots/`.

6. Copy final files into `./deliverable/`: `Отчет_М3_Задание2.docx`, `Отчет_М3_Задание2.pdf`, `screenshots/`.

### Step 8 — Final summary

Print a final summary listing:
- absolute paths of `Отчет_М3_Задание2.docx`, `Отчет_М3_Задание2.pdf`, and the screenshots folder;
- the service researched (ElevenLabs) and its key facts (free tier, Russian support, 1-min cloning);
- whether the optional TTS test succeeded (or was skipped);
- the 2 PR scenarios;
- the next step: upload the report on `open.etu.ru` before 2026-12-04 02:59 MSK, then complete peer review before 2026-12-11 02:59 MSK.

## 6. Hard constraints

- **Do not invent facts about the service.** All information (input requirements, parameters, languages, limitations) must come from the official ElevenLabs documentation at `elevenlabs.io/docs` or the pages fetched in Step 2. If a fact is not in the docs, say «не указано» rather than guessing.
- **The report is in Russian.** Only the service name (ElevenLabs), URLs, model IDs, and parameter names (stability, similarity, etc.) may stay in English.
- **Stay inside the project directory.** Never write outside `./voice-service/` (and `./deliverable/`).
- **No placeholders** except the two title-page fields `Студент гр. ___` and `Преподаватель ___`. The student name `Ханна М. Н.` must appear verbatim, with spaces between initials.
- **No Polza.ai API required** (this is a research assignment). The optional TTS test costs ≤ 0.3 ₽ and is skipped if the model is unavailable.
- **Same formatting as all previous assignments.** The title page, body font, margins, heading style must be visually identical.
- **Don't pause for human input** unless Step 1's pre-flight checks fail (no internet access to ElevenLabs).

Start now. Begin by creating the directory structure, then proceed through Steps 1 → 8 in order.
