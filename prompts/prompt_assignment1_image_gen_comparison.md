# Prompt for AI Agent — Coursework Assignment 1: Transformer vs Diffusion Image Generation

> Paste everything below this line into opencode desktop.

---

# TASK

You are an autonomous coding/agent assistant running in **opencode desktop** with full filesystem and shell access on my machine. Complete the following coursework assignment for me, end-to-end, and produce the final deliverables in `./deliverable/`.

## 1. Context (read this first)

I am a student at **St. Petersburg Electrotechnical University «ЛЭТИ» (LETI)**, course **Prompt-002, осень 2026**, кафедра ИС. The assignment below is taken verbatim from the course LMS page on `open.etu.ru`.

**Original assignment (Russian):**

> **Задание 1. Сравнение генерации изображения на основе трансформера и диффузии**
> Срок сдачи — 12 ноября 2026, 23:55 MSK. Срок взаимного оценивания — 19 ноября 2026.
>
> С помощью сервиса **ArtGenerationME** (или аналога) сгенерируйте на нескольких разных моделях (на основе трансформера и диффузии) изображение по **одному промпту**.
>
> Оцените: 1) точность соответствия промпту; 2) наличие артефактов; 3) разницу в генерации моделей на основе трансформера и диффузии.
>
> **Рекомендация к промпту:** включите в него проверяемые элементы — 2–3 объекта, их количество и цвет, взаимное расположение и короткую надпись. Так точность соответствия промпту можно оценить объективно.
>
> **Обязательные скриншоты:**
> - по одному скриншоту генерации на каждую модель — должно быть видно название модели, промпт и результат;
> - общий коллаж всех результатов для сравнения рядом.
>
> **Структура отчёта:**
> - использованный промпт и обоснование его выбора;
> - таблица: модель → архитектура (трансформер / диффузия) → основание вывода → соответствие промпту (1–5) → выявленные артефакты;
> - вывод: чем систематически различаются результаты моделей двух архитектур и для каких задач какую из них вы бы выбрали.
>
> **Submission step:** «Приложите отчет и отправьте на проверку.»

**Today is 2026-11-06. Deadline is 2026-11-12 23:55 MSK. Do not miss it.**

## 2. Deliverables

Everything goes under `./image-gen-comparison/`. Final deliverables (copy to `./deliverable/` at the end):

1. `Отчет_Задание1.docx` — the report, **in Russian**, A4, Times New Roman 12 pt body / 14 pt bold headings, 2 cm margins.
2. `Отчет_Задание1.pdf` — PDF rendering of the same report.
3. `collage.png` — 2×2 (or 1×4) comparison collage of the four generated images, with Cyrillic labels.
4. `screenshots/` — the four raw per-model screenshots (browser viewport showing model name + prompt + result) plus four `img_only_*.png` files (the bare generated images used in the collage).
5. `logs/` — work log, prompt file, analysis file, generation-method file.

## 3. Working directory layout

Create this structure at the start:

```
./image-gen-comparison/
├── screenshots/      # raw browser screenshots + bare images
├── collage/          # final collage.png
├── report/           # .docx + .pdf
├── logs/             # prompt.md, generation-method.md, analysis.md, worklog.md, HUMAN_ACTION_REQUIRED.md (if needed)
└── deliverable/      # final copies only
```

## 4. Step-by-step procedure

### Step 1 — Design the test prompt

Design **one** prompt in English (image models work best in English) that satisfies the assignment's "checkable elements" rule. It must contain ALL of:

- 2 or 3 distinct, named objects (e.g. «a wooden chair», «a red apple», «a white coffee cup»)
- explicit **quantity** per object (e.g. «two red apples», «one cup»)
- explicit **color** per object
- explicit **relative position** (e.g. «the apples are on the chair, the cup is to the right of the chair»)
- a **short, legible inscription** that must appear in the image (e.g. a wooden sign reading «LETI 2026»)

Avoid cliché diffusion-friendly subjects (no «astronaut on horse», no «cyberpunk city»). Pick a scene where text and precise object counts matter — that is what stresses the two architectures differently.

Save it as `./logs/prompt.md` with:
- the English prompt (one paragraph, ready to paste),
- a Russian translation,
- a 4–6 sentence justification explaining why each checkable element was chosen and why it makes compliance objectively measurable.

### Step 2 — Generate four images (two diffusion, two transformer)

Target model set (substitute only if a model is genuinely unavailable; document any substitution in `./logs/generation-method.md`):

| # | Model | Architecture | Notes |
|---|-------|--------------|-------|
| 1 | Stable Diffusion 3.5 (or SDXL) | Diffusion | |
| 2 | FLUX.1 dev | Diffusion | if FLUX unavailable, use DALL·E 3 |
| 3 | An autoregressive transformer image model (e.g. Google Muse, Parti, LlamaGen, VAR, or any model explicitly labelled "transformer/autoregressive image" on the service) | Transformer | if none on the chosen service, use the second transformer-class model you can find and document the substitution |
| 4 | A second transformer-class model (different family from #3) | Transformer | |

#### Step 2a — Try automated generation first

Probe the environment and try, in this order, to generate the four images programmatically with the prompt from Step 1:

1. `z-ai-web-dev-sdk` CLI: `z-ai image-generation -p "<your prompt>" --size 1024x1024 -o ./screenshots/zai_<n>.png` (call once per target; if it exposes model variants, use them).
2. Any local Stable Diffusion / ComfyUI / diffusers pipeline:
   - check `pip list 2>/dev/null | grep -iE 'diffusers|torch|stable'`
   - probe `http://127.0.0.1:7860/sdapi/v1/txt2img` (Automatic1111) and `http://127.0.0.1:8188` (ComfyUI)
3. Any other locally available image-generation tool.

For each generated image, also save the bare image (used by the collage) and write a screenshot-like composite showing the model name, the prompt text, and the image — this composite counts as the "screenshot" the assignment asks for. A simple Python+Pillow script that draws a header (model name + prompt) above the image is acceptable as a "screenshot" only when no real browser screenshot is possible.

In `./logs/generation-method.md` record, per output file: tool name, exact model identifier, exact command/API call, seed, timestamp, file path.

#### Step 2b — Human fallback (use this if Step 2a produced fewer than 4 usable images)

If automated generation does not yield 4 images covering both architectures, **stop** and create `./logs/HUMAN_ACTION_REQUIRED.md` containing:

- the final English prompt (verbatim, ready to paste),
- the list of 4 target models to pick in **ArtGenerationME** (or `https://www.craiyon.com`, `https://huggingface.co/spaces/black-forest-labs/FLUX.1-schnell`, or any other service that exposes both transformer- and diffusion-based models) — with the expected architecture label for each,
- the exact filenames the human must save the screenshots as in `./screenshots/`:
  - `01_diffusion_<shortname>.png` (full browser viewport: model name + prompt + result visible)
  - `02_diffusion_<shortname>.png`
  - `03_transformer_<shortname>.png`
  - `04_transformer_<shortname>.png`
- the instruction to also save the bare generated image alone as `img_only_01.png` … `img_only_04.png` (for the collage),
- the instruction that each screenshot MUST visibly contain the model name, the prompt text and the generated image — capture the whole browser viewport, not just the image.

Print the contents of `HUMAN_ACTION_REQUIRED.md` to the terminal in a clearly delimited block, then **pause and wait** until all 8 files (4 screenshots + 4 bare images) exist in `./screenshots/`. Do not proceed to Step 3 before they are present.

### Step 3 — Build the comparison collage

Use Python + Pillow. Build a 2×2 grid (or 1×4 if aspect ratios differ too much):

- Title bar at top: **«Сравнение генерации: Трансформер vs Диффузия»**, then the prompt text in a smaller font below the title.
- Each cell = bare generated image, resized to a common height of 768 px, aspect ratio preserved, on a white background.
- Each cell has a caption strip below the image: `<short model name> — <Диффузия | Трансформер>`.
- 16 px gutters, 24 px outer padding.
- Use a Cyrillic-capable TTF font: list candidates with `fc-list | grep -iE 'noto.*sans|dejavu|liberation'` and pick the first match.
- Save as `./collage/collage.png` (PNG, 150 DPI equivalent).

### Step 4 — Analyse each of the four results

Open each bare image and produce, per model, a structured analysis saved to `./logs/analysis.md` (use Russian for the prose; YAML or markdown table is fine):

**a) Prompt compliance score (1–5, one decimal).** Run this checklist (yes = 1, no = 0):

1. object 1 present?
2. object 2 present?
3. object 3 present (or N/A if prompt has 2 objects)?
4. correct quantity of object 1?
5. correct quantity of object 2?
6. correct quantity of object 3 (if applicable)?
7. correct color of object 1?
8. correct color of object 2?
9. correct color of object 3 (if applicable)?
10. correct relative position?
11. inscription present?
12. inscription text legible?
13. inscription text spelled exactly as in the prompt?

Score = (yes_count / applicable_count) × 5, rounded to 1 decimal.

**b) Artifacts.** List every visible artifact in Russian, with location. Examples of specificity required: «на левой руке персонажа — шесть пальцев», «надпись "LETI 2026" превратилась в "LETTI 202Б"», «левое яблоко плавно переходит в край чашки». The phrase «есть артефакты» is **not acceptable** — describe them.

**c) Architecture basis.** For each model, state precisely WHY it is classified as transformer or diffusion. Cite one of: the model's official documentation, the service's stated architecture label, or a published paper/blog you can name. Do not guess. If genuinely unsure, mark the cell `требует уточнения` and explain.

### Step 5 — Write the report `Отчет_Задание1.docx`

Use `python-docx`. The report is **in Russian**. Required structure, in order:

1. **Титульный лист** — `СПбГЭТУ «ЛЭТИ»`, `Кафедра ИС`, `Курс Prompt-002, осень 2026`, `Задание 1. Сравнение генерации изображения на основе трансформера и диффузии`, `Выполнил: студент ___`, `Санкт-Петербург, 2026`. Title page is page 1, page number not shown on it.
2. **1. Введение** (~150 слов) — what is being compared, why it matters, scope and limits of this mini-study.
3. **2. Использованный промпт и обоснование выбора** — full prompt in English + Russian translation, bullet list of the checkable elements, 4–6 sentences of justification (from `./logs/prompt.md`).
4. **3. Использованные модели** — short paragraph + table:

   | Модель | Архитектура | Источник/сервис | Основание классификации |

5. **4. Результаты генерации** — four sub-sections 4.1–4.4, each embedding one screenshot at ~14 cm width, captioned `Рисунок N — Модель <X>, архитектура <Y>`.
6. **5. Сравнительный анализ** — first embed the collage as `Рисунок 5 — Сравнительный коллаж четырёх результатов`. Then the **main required table** (one row per model):

   | Модель | Архитектура (трансформер/диффузия) | Основание вывода | Соответствие промпту (1–5) | Выявленные артефакты |

   Use the data from `./logs/analysis.md`.
7. **6. Вывод** (~250 слов, two paragraphs):
   - Paragraph 1 — **systematic differences** between the two architectures. Must cover at minimum: text-rendering accuracy, color fidelity, prompt-element compliance, typical artifact types, coherence of complex multi-object scenes.
   - Paragraph 2 — **task-based recommendation**: for which concrete task types would you choose which architecture? Give at least **3** concrete task examples with reasoning (e.g. «генерация рекламного постера с длинным читаемым текстом → выбрана модель X, потому что…»).
8. **Приложение А** — full per-element prompt-compliance checklist for each of the four models (the raw yes/no answers from Step 4a).
9. **Приложение Б** — work log: tool versions, exact command lines, timestamps, seeds. From `./logs/worklog.md`.

Formatting rules:
- A4, margins 2 cm, body font Times New Roman 12 pt, headings 14 pt bold, captions 10 pt italic.
- Tables: bold header row, light grey (#F2F2F2) header shading, repeat header row on each page.
- Page numbers bottom-center, starting visibly from page 2.
- No `TODO`, `XXX`, `placeholder`, `【…】`, `___` (except the single «студент ___» field on the title page) anywhere in the final text.

### Step 6 — Self-check (mandatory)

1. Reopen the `.docx` with python-docx. Print the heading outline, table count, image count. Search the full text for `TODO|XXX|placeholder|【`. If any hit, fix it and re-save.
2. Convert to PDF: `soffice --headless --convert-to pdf --outdir ./report ./report/Отчет_Задание1.docx`. Render the first 3 pages, the page with the main comparison table, and the last page to JPEG (`pdftoppm -r 80 -jpeg`). Open them and check: no overflow, no broken table, no missing image, no Markdown leftovers (`**`, `|---|`, `#`).
3. Verify `./collage/collage.png` exists, is non-empty, and that the Cyrillic title and labels render correctly (no tofu boxes).
4. Verify all 4 screenshots + 4 bare images exist in `./screenshots/`.
5. Copy final files into `./deliverable/`.

### Step 7 — Final summary

Print a final summary listing:
- absolute paths of `Отчет_Задание1.docx`, `Отчет_Задание1.pdf`, `collage.png`, and the four screenshots;
- the score (1–5) you gave each model, with a one-line Russian reason;
- whether images were generated programmatically OR whether I need to perform the human action in `HUMAN_ACTION_REQUIRED.md`;
- the next step I should do (i.e. upload the report + collage on `open.etu.ru` before 2026-11-12 23:55 MSK, then complete peer review before 2026-11-19 23:55 MSK).

## 5. Hard constraints

- **Do not invent facts about models.** If unsure whether a specific model is transformer- or diffusion-based, run a web search (`WebSearch` / `curl`) and cite the source. If still unsure, mark `требует уточнения`.
- **Do not invent screenshots.** If you cannot generate images programmatically, use the human-fallback path (Step 2b) — never fabricate images or pretend a screenshot exists.
- **The report is in Russian.** Only the prompt itself and model/brand names may stay in English; every explanatory sentence is in Russian.
- **Stay inside the project directory.** Never write outside `./image-gen-comparison/` (and `./deliverable/`).
- **No placeholders** except the single «Выполнил: студент ___» field on the title page — that one stays blank for me to fill by hand.
- **Numbers must match.** The compliance scores in the table (Section 5) must equal the scores computed in Step 4a and shown in Приложение А.

Start now. Begin by creating the directory structure, then proceed through Steps 1 → 7 in order. If Step 2a fails, do not silently skip Step 2b — produce `HUMAN_ACTION_REQUIRED.md` and pause as instructed.
