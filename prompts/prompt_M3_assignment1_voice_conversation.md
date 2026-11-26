# Prompt for AI Agent — Module 3, Assignment 1: Voice Conversation with AI Assistant

> Paste everything below this line into opencode desktop.

---

# TASK

You are an autonomous coding/agent assistant running in **opencode desktop** with full filesystem and shell access on my machine. Complete LETI coursework **Module 3, Assignment 1** end-to-end, using the **Polza.ai** API for both conversation (LLM) and voice synthesis (TTS). Produce the final deliverables in `./deliverable/`.

## 1. Context (read this first)

I am a student at **St. Petersburg Electrotechnical University «ЛЭТИ» (LETI)**, course **«Применение генеративных нейронных моделей в мультимедиа»** (Prompt-002, осень 2026), кафедра ИС. This assignment is from **Module 3** of the course.

**Original assignment (Russian, verbatim):**

> **Задание 1 (Модуль 3). Голосовая беседа с ассистентом**
> (Алиса, Siri, Маруся, голосовой режим чат-бота или другой доступный)
>
> Срок сдачи — 4 декабря 2026, 02:59 MSK. Срок взаимного оценивания — 11 декабря 2026.
>
> Проведите беседу не менее 10 реплик с вашей стороны по единой теме (например, планирование поездки, выбор книги, объяснение научного явления). В середине беседы намеренно смените тему, затем вернитесь к исходной.
>
> **Заполните шаблон:**
>
> | Поле | Содержание |
> |------|-----------|
> | Ассистент и тема | Название ассистента, тема беседы, число реплик |
> | Удержание контекста | Помнил ли ассистент сказанное 3–5 реплик назад? Приведите пример реплики-проверки и ответ |
> | Реакция на смену темы | Что произошло при резком переходе и при возврате к исходной теме |
> | Адаптация под стиль | Менялась ли манера ответов, если вы говорили коротко/развёрнуто, официально/неформально |
> | Качество речи | Оцените по 5-балльной шкале: естественность интонации, паузы, ударения в сложных словах (замок/замок, числа, даты). Приведите 1 пример ошибки нормализации или просодики, если была |
> | Этапы TTS из видео | Какой из четырёх этапов (нормализация, фонетический анализ, просодический анализ, генерация) показался самым слабым и почему |
>
> **К отчёту приложите 2–3 скриншота** (экран беседы, экран настроек сервиса).

**Today is 2026-11-25. Deadline is 2026-12-04 02:59 MSK** (in ~9 days). Peer review is due 2026-12-11.

### Choice of assistant: voice-mode chat-bot via Polza.ai

The assignment explicitly allows «голосовой режим чат-бота или другой доступный». We use:
- **LLM for conversation:** `google/gemini-2.5-flash` via Polza.ai — generates the assistant's text responses
- **TTS for voice synthesis:** `google/gemini-3.8-flash-lite-tts` via Polza.ai — converts text responses to speech (cheapest Russian-capable TTS on Polza at 60.59 ₽/1M input tokens; supports customizable tone, tempo, and emotion)

Both are accessed via the same `POLZA_API_KEY` and `https://polza.ai/api/v1` endpoint.

## 2. Conversation design (FIXED — do not change)

### Topic: «Планирование поездки в Казань» (planning a trip to Kazan)

**Why this topic:** practical, allows detailed responses with numbers (prices, distances), dates (travel dates), named entities (attractions, restaurants) — all of which stress-test TTS normalization and prosody.

### 12 user remarks (above the minimum 10)

| # | User remark (Russian) | Style | Purpose |
|---|---|---|---|
| 1 | «Привет! Я планирую поездку в Казань на выходные. Что там обязательно нужно посмотреть?» | informal, medium | opening, set topic |
| 2 | «А какие музеи самые интересные? Можно с адресами?» | informal, short | detailed follow-up (museums + addresses → tests normalization) |
| 3 | «Сколько примерно стоит билет на поезд из Москвы в Казань в одну сторону?» | neutral, short | number-heavy response expected (price → tests TTS normalization) |
| 4 | «Посоветуй, пожалуйста, пару хороших ресторанов с татарской кухней. Желательно в центре города, недалеко от Кремля.» | formal, detailed | style test: formal + detailed |
| 5 | «А как лучше добраться от вокзала до центра — на такси или на метро?» | neutral, short | practical follow-up |
| 6 | «В какие дни Кремль открыт для туристов? Есть ли экскурсии с гидом?» | neutral, medium | date/time info expected |
| 7 | **(TOPIC SWITCH)** «Стоп, забыла спросить. Какая сейчас погода в Санкт-Петербурге? Стоит ли брать зонт?» | informal, abrupt | abrupt topic switch |
| 8 | «Спасибо. А завтра в Питере тоже будет дождь?» | informal, short | follow-up on new topic |
| 9 | **(RETURN TO TOPIC)** «Так вот, вернёмся к Казани. Ты упоминал музеи — какой из них самый популярный у туристов?» | return to original | context retention check: does assistant remember remarks 2–6? |
| 10 | «Окей. А где лучше остановиться — в гостинице возле Кремля или на улице Баумана?» | informal, medium | continued original topic |
| 11 | «Сколько будет стоить номер на двоих на две ночи в среднем?» | neutral, short | number normalization test |
| 12 | «Спасибо большое за помощь! Очень подробные ответы.» | informal, short | closing |

### Style variation plan (for «Адаптация под стиль» analysis)
- Remarks 1, 7, 8, 10, 12: **informal, short** («Привет», «Стоп», «Окей», «Спасибо»)
- Remarks 4: **formal, detailed** («Посоветуй, пожалуйста... Желательно в центре...»)
- Remarks 3, 5, 11: **neutral, short** (direct questions)
- Remarks 2, 6, 9: **neutral, medium** (follow-up questions)

This variation lets us observe whether the assistant adapts its response style.

### Context retention check
Remark 9 («Ты упоминал музеи — какой из них самый популярный?») is a **probe**: it refers back to remark 2 (museums) across a 2-remark detour (remarks 7–8 about weather). If the assistant remembers the museum discussion, it demonstrates context retention.

## 3. Models and cost plan

| Role | Polza model ID | Purpose | Cost estimate |
|---|---|---|---|
| Conversation LLM | `google/gemini-2.5-flash` | Generate 12 assistant text responses | ~3 ₽ (12 calls, ~200 tokens each) |
| TTS | `google/gemini-3.8-flash-lite-tts` | Synthesize speech for 6 key responses | ~1 ₽ (token-based, ~500 tokens per response × 6) |
| **Total** | | | **~4 ₽** (well under 100 ₽ min top-up) |

### Substitution rule
- If `google/gemini-2.5-flash` is unavailable, substitute with `openai/gpt-4o-mini` (also transformer, multimodal, Russian-capable).
- If `google/gemini-3.8-flash-lite-tts` is unavailable, substitute with `microsoft/mai-voice-2-flash` (1781 ₽/1M chars, ~2.7 ₽ for 1500 chars) or `openai/tts-1` (1818 ₽/1M chars).
- Document any substitution in `./logs/generation-method.md`.

## 4. Deliverables

Everything goes under `./voice-chat/`. Final deliverables (copy to `./deliverable/` at the end):

1. `Отчет_М3_Задание1.docx` — the report, **in Russian**, A4, Times New Roman 14 pt, 2 cm margins (formatting identical to Assignments 1–6).
2. `Отчет_М3_Задание1.pdf` — PDF rendering.
3. `screenshots/` — 3 screenshot composites:
   - `01_conversation_screen.png` — conversation screen (voice assistant chat interface, all 12 remarks)
   - `02_settings_screen.png` — settings screen (TTS model, voice, speed)
   - `03_tts_analysis.png` — TTS analysis (text + audio waveform + error points)
4. `audio/` — 6 generated TTS audio files (`response_01.mp3`, …, `response_06.mp3`).
5. `logs/` — `conversation.json`, `tts_results.json`, `analysis.md`, `worklog.md`, `cost.md`.

## 5. Working directory layout

```
./voice-chat/
├── screenshots/       # 3 composites
├── audio/             # 6 TTS mp3 files
├── report/            # .docx + .pdf
├── logs/              # all JSON and MD logs
└── deliverable/       # final copies only
```

## 6. Step-by-step procedure

### Step 1 — Pre-flight checks

1. Verify `POLZA_API_KEY` is set (`echo "${POLZA_API_KEY:0:4}"` should print `pza_`).
2. Verify Python ≥ 3.10, Pillow, python-docx, requests, openai are installed. `pip install` anything missing.
3. Probe the API: `curl -sS https://polza.ai/api/v1/models -H "Authorization: Bearer $POLZA_API_KEY" | head -c 200`.
4. Verify both model IDs exist: `google/gemini-2.5-flash` and `google/gemini-3.8-flash-lite-tts`.
5. Log all checks into `./logs/worklog.md`.

### Step 2 — Run the 12-turn conversation

Write `./scripts/run_conversation.py`:

```python
from openai import OpenAI
import json, pathlib, time

client = OpenAI(api_key=open("/path/to/.polza_key").read().strip(),
                base_url="https://polza.ai/api/v1")

SYSTEM_PROMPT = (
    "Ты — голосовой ассистент для планирования путешествий. "
    "Отвечай на русском языке, дружелюбно и по делу. "
    "Если пользователь меняет тему — отвечай на новый вопрос, "
    "но помни всё, что обсуждалось ранее, и можешь вернуться к нему. "
    "Адаптируй стиль под пользователя: если он говорит коротко — отвечай кратко; "
    "если развёрнуто — отвечай подробно. "
    "В ответах с числами, ценами и датами пиши их прописью для удобства озвучки."
)

USER_REMARKS = [
    "Привет! Я планирую поездку в Казань на выходные. Что там обязательно нужно посмотреть?",
    "А какие музеи самые интересные? Можно с адресами?",
    "Сколько примерно стоит билет на поезд из Москвы в Казань в одну сторону?",
    "Посоветуй, пожалуйста, пару хороших ресторанов с татарской кухней. Желательно в центре города, недалеко от Кремля.",
    "А как лучше добраться от вокзала до центра — на такси или на метро?",
    "В какие дни Кремль открыт для туристов? Есть ли экскурсии с гидом?",
    "Стоп, забыла спросить. Какая сейчас погода в Санкт-Петербурге? Стоит ли брать зонт?",
    "Спасибо. А завтра в Питере тоже будет дождь?",
    "Так вот, вернёмся к Казани. Ты упоминал музеи — какой из них самый популярный у туристов?",
    "Окей. А где лучше остановиться — в гостинице возле Кремля или на улице Баумана?",
    "Сколько будет стоить номер на двоих на две ночи в среднем?",
    "Спасибо большое за помощь! Очень подробные ответы.",
]

messages = [{"role": "system", "content": SYSTEM_PROMPT}]
conversation = []

for i, user_text in enumerate(USER_REMARKS, 1):
    messages.append({"role": "user", "content": user_text})
    t0 = time.time()
    r = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=messages,
        temperature=0.7
    )
    assistant_text = r.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_text})

    conversation.append({
        "turn": i,
        "user": user_text,
        "assistant": assistant_text,
        "elapsed": time.time() - t0,
        "usage": {"in": r.usage.prompt_tokens, "out": r.usage.completion_tokens}
    })
    print(f"Turn {i}: {assistant_text[:80]}...")

pathlib.Path("./logs/conversation.json").write_text(
    json.dumps(conversation, ensure_ascii=False, indent=2)
)
```

Save the full conversation to `./logs/conversation.json`.

### Step 3 — Generate TTS audio for 6 key responses

Select 6 assistant responses for TTS (the ones most likely to reveal TTS issues — numbers, dates, named entities):
- Response 1 (attractions — named entities)
- Response 3 (price — number normalization: «билет стоит около двух тысяч рублей»)
- Response 6 (dates — «Кремль работает ежедневно с 8:00 до 18:00»)
- Response 7 (weather — topic switch response)
- Response 9 (context retention — refers back to museums)
- Response 11 (price — «номер на двоих на две ночи»)

Write `./scripts/run_tts.py`:

```python
from openai import OpenAI  # OpenAI-compatible TTS
import pathlib, json, time

client = OpenAI(api_key=open("/path/to/.polza_key").read().strip(),
                base_url="https://polza.ai/api/v1")

conversation = json.loads(pathlib.Path("./logs/conversation.json").read_text())
TTS_TURNS = [1, 3, 6, 7, 9, 11]  # responses to synthesize

tts_results = []
for turn_num in TTS_TURNS:
    text = conversation[turn_num - 1]["assistant"]
    t0 = time.time()
    try:
        # Try OpenAI-compatible TTS endpoint
        response = client.audio.speech.create(
            model="google/gemini-3.8-flash-lite-tts",
            voice="alloy",  # default voice; may be customizable
            input=text
        )
        audio_path = f"./audio/response_{turn_num:02d}.mp3"
        response.stream_to_file(audio_path)
        file_size = pathlib.Path(audio_path).stat().st_size
        tts_results.append({
            "turn": turn_num,
            "text_length": len(text),
            "audio_path": audio_path,
            "file_size_bytes": file_size,
            "elapsed": time.time() - t0,
            "status": "success"
        })
        print(f"Turn {turn_num}: TTS saved ({file_size} bytes)")
    except Exception as e:
        tts_results.append({
            "turn": turn_num,
            "text_length": len(text),
            "elapsed": time.time() - t0,
            "status": "error",
            "error": str(e)
        })
        print(f"Turn {turn_num}: TTS error — {e}")

pathlib.Path("./logs/tts_results.json").write_text(
    json.dumps(tts_results, ensure_ascii=False, indent=2)
)
```

**If the TTS endpoint format differs:** Polza.ai may use a different TTS API format. If `client.audio.speech.create()` fails, try:
```python
# Alternative: direct API call
import requests
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
data = {"model": "google/gemini-3.8-flash-lite-tts", "input": text, "voice": "alloy"}
r = requests.post("https://polza.ai/api/v1/audio/speech", headers=headers, json=data)
with open(f"./audio/response_{turn_num:02d}.mp3", "wb") as f:
    f.write(r.content)
```

If TTS is completely unavailable, note this in the report and analyze the TTS stages theoretically (based on the text content and known Russian TTS challenges).

### Step 4 — Analyze the conversation

In `./logs/analysis.md`, fill in the assignment template:

#### Поле 1: Ассистент и тема
- **Ассистент:** голосовой режим чат-бота на базе Polza.ai (LLM: google/gemini-2.5-flash, TTS: google/gemini-3.8-flash-lite-tts)
- **Тема беседы:** планирование поездки в Казань
- **Число реплик с моей стороны:** 12

#### Поле 2: Удержание контекста
- **Помнил ли ассистент сказанное 3–5 реплик назад?** Yes/No (based on response to remark 9)
- **Пример реплики-проверки:** Remark 9: «Так вот, вернёмся к Казани. Ты упоминал музеи — какой из них самый популярный у туристов?»
- **Ответ ассистента:** [quote the response to remark 9]
- **Analysis:** Did the assistant correctly reference the museums mentioned in remark 2? If yes → context retained across a 2-remark detour (remarks 7–8). If no → context lost.

#### Поле 3: Реакция на смену темы
- **При резком переходе (remark 7):** Did the assistant seamlessly answer the weather question, or did it express confusion / try to relate it to Kazan?
- **При возврате (remark 9):** Did the assistant resume the Kazan topic smoothly, referencing the prior museum discussion?
- **Quote** the relevant assistant responses.

#### Поле 4: Адаптация под стиль
Analyze whether the assistant's response style changed:
- Remarks 1, 7, 8, 10, 12 (informal/short user) → did the assistant respond briefly and casually?
- Remark 4 (formal/detailed user) → did the assistant respond in a more detailed, polite manner?
- Compare response lengths and formality levels. Provide 2 concrete examples.

#### Поле 5: Качество речи (5-балльная шкала)

Rate the TTS on these dimensions (based on the generated audio + text analysis):

| Параметр | Оценка (1–5) | Обоснование |
|---|---|---|
| Естественность интонации | X/5 | [analysis] |
| Паузы | X/5 | [analysis] |
| Ударения в сложных словах | X/5 | [analysis] |

**Пример ошибки нормализации или просодики:**
Identify 1 concrete error from the TTS output. Likely candidates in the conversation:
- Numbers: «около 2000 рублей» — is «2000» read as «две тысячи» correctly?
- Dates: «с 8:00 до 18:00» — is «8:00» read as «восемь часов» or «восемь ноль-ноль»?
- Homographs: if any homographs appear in the responses (e.g., «замок» — castle vs lock, «мука» — flour vs torment)
- Named entities: «Казань», «Баумана» — correct stress?

If the agent can't actually listen to the audio (no audio playback capability), analyze the TEXT for points where TTS is LIKELY to err, and note: «Аудио сохранено в ./audio/response_03.mp3; анализ текста показывает, что число "2000" может быть озвучено некорректно (нормализация числительных — типичная слабая точка TTS).»

#### Поле 6: Этапы TTS из видео

The 4 stages of TTS (from the course video):
1. **Нормализация** — converting numbers, dates, abbreviations, symbols to spoken text (e.g., «2000 ₽» → «две тысячи рублей»)
2. **Фонетический анализ** — grapheme-to-phoneme conversion (how letters map to sounds)
3. **Просодический анализ** — stress assignment, intonation contours, pauses (e.g., «за́мок» vs «замо́к»)
4. **Генерация** — acoustic model producing the actual waveform (neural vocoder)

**Which stage is weakest and why:**

For Russian TTS, the weakest stages are typically:

1. **Нормализация** (often weakest) — Russian numbers, dates, and abbreviations have complex inflectional forms that depend on grammatical case, gender, and number. Examples:
   - «2000 рублей» → «две тысячи рублей» (correct) vs «две тысяч рублей» (wrong case)
   - «8:00» → «восемь часов» vs «восемь ноль-ноль» — context-dependent
   - «ул. Баумана» → «улица Баумана» — abbreviation expansion + stress on «Ба́умана»

2. **Просодический анализ** (second weakest) — Russian homograph stress:
   - «за́мок» (castle) vs «замо́к» (lock)
   - «му́ка» (flour) vs «мука́» (torment)
   - Numbers like «1234» — stress on the right syllable

3. **Фонетический анализ** — Russian is mostly phonetic (letters → sounds are regular), but there are a few edge cases (e.g., «его» → «ево́го», «сч» → «щ»).

4. **Генерация** — modern neural TTS (Gemini, MAI-Voice, etc.) is quite good at waveform generation; this is rarely the weakest stage.

**Conclusion:** For the chosen TTS model (Gemini 3.8 Flash Lite TTS), the weakest stage is **нормализация** — specifically, the handling of Russian numbers, prices, and dates that appear frequently in the trip-planning conversation. Provide the specific example from the conversation (e.g., the price in remark 3 or the dates in remark 6).

### Step 5 — Build the 3 screenshot composites

Use Python + Pillow. Cyrillic-capable TTF font.

**Composite 1 — `01_conversation_screen.png` (conversation interface, ~900×1800 px):**
- Simulate a voice assistant chat interface (like Alice's or a generic voice chat app):
  - Top bar (60 px, dark #1A1A1A, white text): «Голосовой ассистент • Polza.ai» + a microphone icon (drawn)
  - Chat area: alternating user (right-aligned, blue bubble) and assistant (left-aligned, grey bubble) messages
  - Each message: the full text, wrapped, ~11 pt
  - 12 user messages + 12 assistant messages = 24 bubbles
  - A microphone icon at the bottom (indicating voice mode)
- This composite may be tall — split across two images if needed (01a and 01b)

**Composite 2 — `02_settings_screen.png` (settings, ~900×1200 px):**
- Simulate a settings screen for the voice assistant:
  - Top bar: «Настройки голосового ассистента»
  - Setting rows (each with label + value):
    - «Модель разговора:» → «google/gemini-2.5-flash»
    - «Модель TTS:» → «google/gemini-3.8-flash-lite-tts»
    - «Голос:» → «alloy (нейтральный)»
    - «Скорость речи:» → «1.0×»
    - «Тон:» → «дружелюбный»
    - «Язык:» → «Русский»
    - «Температура LLM:» → «0.7»
    - «Сервис:» → «Polza.ai API»
  - Each row with a light separator line

**Composite 3 — `03_tts_analysis.png` (TTS analysis, ~1600×1200 px):**
- Title bar (60 px, dark #1A1A1A, white text): «Анализ TTS: текст → ожидаемое произношение → возможные ошибки»
- For 3 selected responses (turns 3, 6, 9), show:
  - Left column: the original text (with numbers/dates highlighted in red)
  - Middle column: the expected normalized text (how it SHOULD be read)
  - Right column: potential error points (marked with ⚠)
- Example for turn 3:
  - Original: «Билет на поезд из Москвы в Казань стоит около 2000 рублей...»
  - Expected: «Билет на поезд из Москвы в Казань стоит около двух тысяч рублей...»
  - Error risk: ⚠ «2000» → normalization (case agreement: «две тысячи» vs «две тысяч»)

### Step 6 — Write the report `Отчет_М3_Задание1.docx`

Use `python-docx`. The report is **in Russian**. Formatting identical to Assignments 1–6.

#### 6.1 Title page — MUST match the official LETI template

(Same as Assignments 1–6. Theme line: `Тема: Голосовая беседа с AI-ассистентом`. Student name: `Ханна М. Н.`.)

**Exact title-page content (lines 6–10):**
6. `отчет` — centered, NOT bold, lowercase
7. `по заданию` — centered, bold
8. `по курсу «Применение генеративных нейронных моделей` — centered, bold
9. `в мультимедиа»` — centered, bold
10. `Тема: Голосовая беседа с AI-ассистентом` — centered, NOT bold

(The rest of the title page — header, table, footer — is identical to Assignments 1–6.)

#### 6.2 Body formatting rules

(Same as Assignments 1–6: A4, margins 2 cm, TNR 14 pt throughout, first-line indent 1.25 cm, justified, headings bold centered, captions TNR 12 pt italic, page numbers from page 2, no `___` except the two title-page fields.)

#### 6.3 Required body structure

1. **1. Введение** (~120 слов) — purpose: testing a voice AI assistant's context retention, topic-switch handling, style adaptation, and TTS quality through a 12-turn conversation about planning a trip to Kazan.

2. **2. Описание беседы** — brief description:
   - Assistant: голосовой режим чат-бота (Polza.ai, Gemini 2.5 Flash + Gemini 3.8 Flash Lite TTS)
   - Topic: планирование поездки в Казань
   - Number of user remarks: 12
   - Mid-conversation topic switch: remark 7 (weather in St. Petersburg)
   - Return to topic: remark 9

3. **3. Заполненный шаблон** — the **main required content**, presented as 6 sub-sections matching the template:

   **3.1. Ассистент и тема** — table or paragraph:
   | Поле | Значение |
   |------|----------|
   | Ассистент | Голосовой режим чат-бота (Polza.ai: LLM Gemini 2.5 Flash + TTS Gemini 3.8 Flash Lite TTS) |
   | Тема беседы | Планирование поездки в Казань |
   | Число реплик | 12 |

   **3.2. Удержание контекста** — 2–3 paragraphs:
   - State whether the assistant remembered remarks from 3–5 turns ago
   - Quote the probe remark (remark 9) and the assistant's response
   - Analyze: did the assistant correctly reference the museums from remark 2?

   **3.3. Реакция на смену темы** — 2–3 paragraphs:
   - Quote remark 7 (abrupt switch) and the assistant's response
   - Quote remark 9 (return) and the assistant's response
   - Analyze: smoothness of transition and return

   **3.4. Адаптация под стиль** — 2–3 paragraphs:
   - Compare the assistant's response style across informal/short remarks vs formal/detailed remarks
   - Provide 2 concrete examples (e.g., «на реплику 1 (короткая, неформальная) ассистент ответил ...; на реплику 4 (развёрнутая, формальная) ассистент ответил ...»)

   **3.5. Качество речи** — table + paragraph:
   | Параметр | Оценка (1–5) |
   |---|---|
   | Естественность интонации | X |
   | Паузы | X |
   | Ударения в сложных словах | X |

   Then 1 paragraph with a concrete example of a normalization or prosody error (or potential error if audio analysis is theoretical).

   **3.6. Этапы TTS из видео** — 2–3 paragraphs:
   - List the 4 stages: нормализация, фонетический анализ, просодический анализ, генерация
   - State which is weakest (likely нормализация for Russian) and why
   - Provide the specific example from the conversation

4. **4. Скриншоты** — embed the 3 screenshot composites:
   - `01_conversation_screen.png` — captioned `Рисунок 1 — Экран беседы с голосовым ассистентом`
   - `02_settings_screen.png` — captioned `Рисунок 2 — Экран настроек сервиса (Polza.ai)`
   - `03_tts_analysis.png` — captioned `Рисунок 3 — Анализ этапов TTS на примере ответов с числами и датами`

5. **Приложение А** — full conversation transcript (all 12 turns, user + assistant, verbatim).

6. **Приложение Б** — work log + cost: tool versions, API calls, timestamps, TTS model used, total cost. From `./logs/worklog.md` and `./logs/cost.md`.

### Step 7 — Self-check (mandatory)

1. **Title-page format check (highest priority).** Render page 1 of the PDF to JPEG at 100 DPI and verify:
   - The theme line reads `Тема: Голосовая беседа с AI-ассистентом` — not bold.
   - `отчет` is lowercase.
   - Student name `Ханна М. Н.` with spaces between initials.
   - Page 1 has NO page number.

2. Reopen the `.docx` with python-docx. Print the heading outline, table count, image count (should be ≥ 3). Search for `TODO|XXX|placeholder|【`.

3. Convert to PDF. Render pages 1, 2, and the last page to JPEG. Check formatting.

4. Verify all 3 screenshot composites exist in `./screenshots/`, plus 6 audio files in `./audio/` (if TTS succeeded).

5. Verify the report contains all 6 template fields (3.1–3.6) filled with actual data from the conversation.

6. Copy final files into `./deliverable/`: `Отчет_М3_Задание1.docx`, `Отчет_М3_Задание1.pdf`, `screenshots/`, `audio/` (if generated).

### Step 8 — Final summary

Print a final summary listing:
- absolute paths of `Отчет_М3_Задание1.docx`, `Отчет_М3_Задание1.pdf`, screenshots, and audio files;
- the conversation topic and number of turns;
- whether the assistant retained context (yes/no) after the topic switch;
- the TTS quality scores (3 parameters);
- the weakest TTS stage identified;
- the total cost in ₽;
- the next step: upload the report on `open.etu.ru` before 2026-12-04 02:59 MSK, then complete peer review before 2026-12-11 02:59 MSK.

## 7. Hard constraints

- **The conversation must be REAL.** All 12 assistant responses must come from actual LLM API calls. Do not fabricate responses.
- **The TTS audio must be REAL** (if the TTS API works). If TTS fails, note this and analyze theoretically.
- **The template must be FILLED** with actual data from the conversation, not generic text.
- **The report is in Russian.** Only model IDs, URLs, and technical terms may stay in English.
- **Stay inside the project directory.** Never write outside `./voice-chat/` (and `./deliverable/`).
- **No placeholders** except the two title-page fields `Студент гр. ___` and `Преподаватель ___`. The student name `Ханна М. Н.` must appear verbatim, with spaces between initials.
- **Budget:** total Polza spend must stay under 15 ₽.
- **Same formatting as Assignments 1–6.** The title page, body font, margins, heading style must be visually identical.
- **Don't pause for human input** unless Step 1's pre-flight checks fail.

Start now. Begin by creating the directory structure, then proceed through Steps 1 → 8 in order.
