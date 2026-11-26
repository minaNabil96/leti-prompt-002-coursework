# Anti-Error Ruleset — Mandatory Addendum for All Future LETI Report Prompts

> Paste this block at the END of any LETI coursework prompt (after the "Hard constraints" section), before "Start now." It prevents the 9 error patterns found in the M3-A1 and M3-A2 repair audits.

---

## 8. Anti-error rules (mandatory — learned from M3-A1/M3-A2 audit)

These rules are NON-NEGOTIABLE. Violating any of them means the report is defective and must be fixed before delivery.

### Rule A — Real screenshots only, never composites/mockups for service UIs

**The problem:** In M3-A1 and M3-A2, the agent built Pillow-rendered "composites" and HTML "mockups" of service interfaces instead of capturing real screenshots. The assignment literally says «скриншоты (экран беседы, экран настроек сервиса)» — it means actual screen captures.

**The rule:**
1. **For service interface screenshots (экран настроек, экран беседы):** capture a REAL screenshot of the actual service UI.
   - If the service has a web UI accessible from the agent's environment: use headless Chrome / Playwright to navigate to the page and screenshot it (`--screenshot --window-size=1440,900`).
   - If direct access is blocked (e.g., ElevenLabs blocks Russia): use **web.archive.org** snapshots of the official pages. The wayback toolbar in the screenshot serves as visible provenance — this is acceptable.
   - If neither is possible: STOP and tell the user. **Never generate, simulate, embellish, or AI-generate UI images.** Never label a composite as a «скриншот».
2. **For data visualizations (tables, charts, timelines):** Pillow composites ARE acceptable — but caption them as «визуализация данных» or «диаграмма», NEVER as «скриншот».
3. **Honest labeling:** every figure caption must state what the figure actually is:
   - Real screenshot: «Рисунок N — Экран [сервиса]: [что показано] (снимок [дата])»
   - Archive screenshot: «Рисунок N — [сервис] (архивная копия официальной страницы, снимок [дата])»
   - Data composite: «Рисунок N — Визуализация данных: [что показано]» — NOT «скриншот»
4. **No simulation disclaimers needed if the screenshot is real.** If it's a composite, label it honestly — don't pretend it's a screenshot.

### Rule B — Cross-document number consistency (automated check)

**The problem:** In M3-A1, the total duration was stated as «381,2 с» in one place but the Table 3 sum was 381,5 s. Pitch was claimed as «163 Гц» but the per-file values gave a mean of 163,8. Speech-share range «0,75–0,82» didn't match the actual 0,78–0,83.

**The rule:**
1. **Before writing the report**, compute ALL statistics from the raw data in `./logs/`. Store them in `./logs/computed_stats.json`.
2. **After writing the report**, run a consistency check script:
   ```python
   # Extract every number from the .docx and verify cross-references
   # - Total durations in tables must equal the sum of per-row durations
   # - Total costs must equal the sum of per-call costs (INCLUDING calibration/test calls)
   # - Statistical claims (mean, median, range) must be reproducible from the raw data
   # - Counts (number of replies, number of images) must match across all mentions
   ```
3. **If a number appears in two places, it must be the same number** — or a footnote must explain the rounding.
4. **Never state a statistic you didn't compute.** If you can't compute it, write «не вычислялось» or omit it.

### Rule C — Template field completeness

**The problem:** In M3-A1, the «Ассистент и тема» field said «Ассистент — голосовой помощник для планирования путешествий» — a generic description that omitted the required elements (assistant name, theme, number of replies).

**The rule:**
1. For each template field, read the assignment's column header carefully — it lists exactly what sub-elements are required.
2. **Every required sub-element must appear explicitly.** Don't paraphrase into a generic sentence.
3. Example for «Ассистент и тема | Название ассистента, тема беседы, число реплик»:
   - WRONG: «Ассистент — голосовой помощник для планирования путешествий.»
   - RIGHT: «Ассистент — [exact model/service name]. Тема беседы — [topic]. Число реплик пользователя — [N].»
4. Run a checklist: for each template field, confirm every required sub-element is present as a distinct, findable string.

### Rule D — Complete cost accounting

**The problem:** In M3-A1, two calibration API calls (0,0095 ₽) were excluded from the total, creating a discrepancy between the stated total (8,97 ₽) and the actual total (8,98 ₽).

**The rule:**
1. **Every API call that was billed MUST appear in the cost table** — including calibration calls, test calls, failed-but-billed calls, and retry calls.
2. If some calls are excluded from the main table for clarity, add a footnote: «Калибровочные запросы (X шт., Y ₽) в таблицу не входят; полная стоимость сессии — Z ₽.»
3. The total stated in the introduction MUST equal the all-in total (main table + excluded calls), with a qualifier if rounding differs.

### Rule E — Calendar dates in all work logs

**The problem:** In M3-A1, the work journal recorded only times (18:20–18:50) with no calendar date, weakening the report's ability to critique a weather hallucination («18 °C в конце ноября»).

**The rule:**
1. **Every work log entry MUST include the full calendar date** (YYYY-MM-DD or DD.MM.YYYY), not just the time.
2. Extract the date from: API response timestamps, file creation timestamps (`stat -c %y`), or system time (`date +%Y-%m-%d`).
3. The work log table caption must include the date: «Таблица Б.1 — Хронология выполнения работы ([DATE], время MSK)».

### Rule F — Accurate characterization of assignment requirements

**The problem:** In M3-A1, the agent wrote «Обе модели входят в задание» — but the assignment lists models as EXAMPLES («например, Алиса, Siri, Маруся...»), not requirements. The assignment says «или другой доступный».

**The rule:**
1. **Never claim something «входит в задание» (is required by the assignment) unless the assignment text literally requires it.**
2. Examples («например») are suggestions, not requirements.
3. When characterizing what the assignment requires, quote the exact assignment text.
4. If you chose a specific option from the examples, say: «Задание допускает [X]; в этом качестве использован [Y].» — not «[Y] входит в задание».

### Rule G — Technical term accuracy

**The problem:** In M3-A1, the agent called Praat a «метод» (method) — Praat is software (программа), not a method.

**The rule:**
1. **Verify every technical term before using it.**
2. Software names (Praat, librosa, FFmpeg, Audacity) are программы/инструменты, not методы.
3. Methods/algorithms (FFT, autocorrelation, neural vocoder) are методы/алгоритмы.
4. When referencing a tool, use the precise form: «по алгоритму, реализованному в программе [X]» or «с помощью библиотеки [X]».

### Rule H — Date range verification

**The problem:** In M3-A2, the report stated «снимки 22.09–25.11.2026» but one source was dated 06.12.2025 — outside the stated range.

**The rule:**
1. **Before stating a date range, verify that ALL items fall within it.**
2. If any item is outside the range, expand the range or note the exception explicitly.
3. Example: if sources span 06.12.2025 to 25.11.2026, write «снимки от 06.12.2025 до 25.11.2026» — not «22.09–25.11.2026».

### Rule I — Final automated consistency pass (mandatory before delivery)

**Add this to the self-check step of every prompt:**

```python
# FINAL CONSISTENCY CHECK — run after generating the .docx and before converting to PDF
import re, docx

doc = docx.Document("Отчет_...docx")
full_text = "\n".join(p.text for p in doc.paragraphs)
for table in doc.tables:
    for row in table.rows:
        full_text += "\n" + " | ".join(cell.text for cell in row.cells)

checks = []

# 1. No simulation/mockup labels in figure captions
if re.search(r"симуляц|макет|mock|composite", full_text, re.IGNORECASE):
    checks.append("FAIL: figure captions contain simulation/mockup language — replace with real screenshots")

# 2. No placeholder strings
for ph in ["TODO", "XXX", "FIXME", "[", "<", "___"]:
    if ph in full_text and ph != "___":  # ___ is allowed only on title page
        checks.append(f"FAIL: placeholder '{ph}' found in text")

# 3. Cross-check totals (extract all numbers and verify sums)
# ... (implementation depends on the specific report)

# 4. Template field completeness
# ... (check that each required sub-element is present)

# 5. Date consistency
# ... (verify all date ranges cover all items)

for c in checks:
    print(c)

if any("FAIL" in c for c in checks):
    print("\n!!! REPORT HAS ERRORS — FIX BEFORE DELIVERY !!!")
else:
    print("\n✓ All consistency checks passed.")
```

### Summary table of errors and prevention rules

| # | Error found in audit | Rule | Prevention |
|---|---|---|---|
| 1 | Screenshots were composites/mockups, not real captures | A | Use headless browser or web.archive.org for real screenshots |
| 2 | Total duration 381,2 vs sum 381,5 | B | Automated cross-document number consistency check |
| 3 | Pitch 163 Hz not reproducible from data | B + D | Compute all stats from raw data; never invent |
| 4 | Speech-share range 0,75–0,82 vs actual 0,78–0,83 | B | Same as above |
| 5 | Calibration cost excluded from total | D | Include ALL billed calls in cost table |
| 6 | Missing calendar date in work log | E | Always include YYYY-MM-DD in log entries |
| 7 | Claimed models «входят в задание» | F | Quote assignment text; don't overstate requirements |
| 8 | Praat called a «метод» | G | Verify technical terms: software ≠ method |
| 9 | Date range didn't cover one source | H | Verify all items fall within stated range |
