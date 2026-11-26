"""Self-check of the finished assignment: report, film, numbers, logs.

Fails with a non-zero exit code if any requirement of the assignment is not met.
Every expected number is read from logs/computed_stats.json, so the check also
proves that report, cost table and logs agree with each other.
"""
import json
import pathlib
import re
import sys

import pymupdf as fitz
from docx import Document

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
DOCX = ROOT / "report" / "Отчет_М3_Задание4.docx"
PDF = ROOT / "report" / "Отчет_М3_Задание4.pdf"
S = json.loads((LOGS / "computed_stats.json").read_text(encoding="utf-8"))
C, F = S["cost"], S["film"]

errors = []
notes = []


def need(cond, msg):
    if not cond:
        errors.append(msg)


def ru(v, d=2):
    return f"{v:.{d}f}".replace(".", ",")


# ------------------------------------------------------------------ DOCX layout
d = Document(DOCX)
need(len(d.inline_shapes) >= 3, f"only {len(d.inline_shapes)} pictures in DOCX")
for i, s in enumerate(d.sections):
    need(abs(s.page_width.mm - 210) < 1 and abs(s.page_height.mm - 297) < 1,
         f"section {i}: page not A4")
    for m in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        need(abs(getattr(s, m).cm - 2) < 0.05, f"section {i}: {m} != 2 cm")

docx_text = "\n".join(p.text for p in d.paragraphs)
for t in d.tables:
    for row in t.rows:
        for cell in row.cells:
            docx_text += "\n" + cell.text

# ------------------------------------------------------------------ PDF
pdf = fitz.open(PDF)
need(3 <= pdf.page_count <= 6, f"PDF has {pdf.page_count} pages, expected 3-6")
text = "\n".join(p.get_text() for p in pdf)

for bad in ("TODO", "XXX", "FIXME", "placeholder", "___", "Кафедра связи"):
    need(bad not in text and bad not in docx_text, f"forbidden token in report: {bad}")

for must in ("Кафедра ИС", "Студент гр. 1378", "Ханна М. Н.", "Санкт-Петербург", "2026",
             "МИНОБРНАУКИ РОССИИ", "ЛЭТИ"):
    need(must in text, f"title page missing: {must}")

need(text.count("`") == 0, "markdown backticks leaked into the PDF")

# ------------------------------------------------------------------ numbers
checks = {
    "total cost": (ru(C["total_rub"]), f"cost total {ru(C['total_rub'])}"),
    "budget": (ru(S["budget_rub"], 0), f"budget {ru(S['budget_rub'], 0)}"),
    "calls": (str(C["api_calls"]), f"{C['api_calls']} calls"),
    "duration": (ru(F["duration_s"], 1), f"duration {ru(F['duration_s'], 1)}"),
    "resolution": (f"{F['width']}×{F['height']}", f"resolution {F['width']}x{F['height']}"),
}
for name, (needle, msg) in checks.items():
    need(needle in text, f"PDF does not state {msg}")

need(f"{C['api_calls']} оплаченных запросов" in text, "PDF lacks the paid-call count")
need(f"{F['voiceover_chars']}" in text, "PDF lacks the voiceover character count")

# rejected take must be visible in the cost appendix
need("отклонён" in text.lower() or "отклонен" in text.lower(),
     "rejected take is not mentioned in the report")
need(ru(next(v for v in C["video"]["runs"] if v["rejected"])["cost_rub"]) in text,
     "rejected take cost missing from the cost table")

# ------------------------------------------------------------------ logs
cost_md = (LOGS / "cost.md").read_text(encoding="utf-8")
need(ru(C["total_rub"], 4) in cost_md, "cost.md total does not match computed_stats")
need(ru(C["budget_left_rub"], 4) in cost_md, "cost.md leftover does not match")
row_sum = sum(float(re.findall(r"\| ([\d,]+) \|$", ln)[0].replace(",", "."))
              for ln in cost_md.splitlines()
              if re.search(r"\| ([\d,]+) \|$", ln))
need(abs(row_sum - C["total_rub"]) < 5e-4,
     f"cost.md rows sum to {row_sum:.4f}, expected {C['total_rub']:.4f}")

worklog = (LOGS / "worklog.md").read_text(encoding="utf-8")
need("26.11.2026" in worklog, "worklog has no full date")
need(not re.search(r"\|\s*\d{2}:\d{2}\s*\|\s*[^|]*\|\s*$", worklog, re.M),
     "worklog has rows without a result")
need(not re.search(r"\b\d{2}\.\d{2}\.\d{2}\b(?!\d)", worklog.replace("26.11.2026", "")),
     "worklog has a short date instead of DD.MM.YYYY")

video_check = json.loads((LOGS / "video_check.json").read_text(encoding="utf-8"))
need(video_check["height"] >= 1080 and video_check["width"] >= 1920,
     "delivered film is below 1080p")
need(video_check["checks"]["has_audio"], "delivered film has no audio track")
need(not video_check["errors"], f"video check errors: {video_check['errors']}")
need(abs(video_check["duration_s"] - F["duration_s"]) < 0.05,
     "video_check duration differs from computed_stats")

scenes = json.loads((LOGS / "scene_results.json").read_text(encoding="utf-8"))
need(scenes["accepted"] >= 5, f"only {scenes['accepted']} generated video scenes")
need(len(scenes["scenes"]) == S["counts"]["storyboard_scenes"],
     "storyboard scene count differs between logs")

for name in ("cost.md", "worklog.md", "generation-method.md", "scene_results.json",
             "computed_stats.json", "video_check.json"):
    need((LOGS / name).exists(), f"missing log: {name}")

# ------------------------------------------------------------------ fonts
fonts = set()
for page in pdf:
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                if span["text"].strip():
                    fonts.add((span["font"], round(span["size"], 1)))
body = {(f, s) for f, s in fonts if s >= 13.9}
need(any("Times" in f for f, s in body), f"no Times New Roman body text: {sorted(fonts)[:8]}")

print(f"DOCX {DOCX.stat().st_size/1e6:.2f} MB, {len(d.paragraphs)} paragraphs, "
      f"{len(d.tables)} tables, {len(d.inline_shapes)} pictures")
print(f"PDF  {pdf.page_count} pages, {PDF.stat().st_size/1e6:.2f} MB")
print(f"film {F['width']}x{F['height']}, {F['duration_s']} s, voice-music delta "
      f"{video_check['levels']['speech_window_db'] - video_check['levels']['pause_window_db']:.1f} dB")
print(f"cost {ru(C['total_rub'])} RUB of {ru(S['budget_rub'], 0)} ({ru(C['budget_used_pct'], 1)} %), "
      f"{C['api_calls']} paid calls, rejected takes {C['video']['rejected_calls']}")
print("fonts:", ", ".join(sorted({f"{f} {s}" for f, s in fonts}))[:300])
print("ERRORS:", "none" if not errors else "")
for e in errors:
    print("  -", e)
sys.exit(1 if errors else 0)
