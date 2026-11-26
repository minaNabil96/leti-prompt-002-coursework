"""Final scan of the М3-А1 logs: numbers, dates, forbidden words."""
import json
import pathlib
import re

ROOT = pathlib.Path(r".\voice-chat")
LOGS = ROOT / "logs"
S = json.loads((LOGS / "computed_stats.json").read_text(encoding="utf-8"))
texts = {p.name: p.read_text(encoding="utf-8") for p in sorted(LOGS.glob("*.md"))}
ok = []


def chk(name, cond, detail=""):
    ok.append(cond)
    print(("PASS" if cond else "FAIL"), name, ("| " + detail) if detail else "")


# numbers present in the prose logs
chk("L1 163,1 Гц в analysis.md и worklog.md",
    "163,1" in texts["analysis.md"] and "163,1" in texts["worklog.md"])
chk("L2 0,75–0,82 в analysis.md",
    "0,75–0,82" in texts["analysis.md"] or "0,751" in texts["analysis.md"])
chk("L3 «в 16 раз» в analysis.md, «в 15 раз» нет",
    "в 16 раз" in texts["analysis.md"] and "в 15 раз" not in texts["analysis.md"])
chk("L4 6,35 мин в cost.md",
    "6,35 мин" in texts["cost.md"])
chk("L5 13,2761 и 0,0095 в cost.md",
    "13,2761" in texts["cost.md"] and "0,0095" in texts["cost.md"])
chk("L6 381,16 и 381,52 в cost.md",
    "381,16" in texts["cost.md"] and "381,52" in texts["cost.md"])
chk("L7 TTS 6,3149 / STT 0,6861 / LLM 1,9649 / UI 4,3007",
    all(f"{v:.4f}".replace(".", ",") in texts["cost.md"]
        for v in (S["cost"]["tts_rub"], S["cost"]["stt_rub"], S["cost"]["llm_rub"],
                  S["cost"]["ui_repeat_rub"])))
chk("L8 нет «композита» в prose-логах",
    all("композит" not in texts[n].lower()
        for n in ("analysis.md", "worklog.md", "generation-method.md", "cost.md")))
chk("L9 нет «методом Praat» в analysis.md",
    "методом Praat" not in texts["analysis.md"])
chk("L10 prosody.json: pitch = librosa pYIN",
    json.loads((LOGS / "prosody.json").read_text(encoding="utf-8"))["method"]["pitch"]
    .startswith("librosa pYIN"))

# dates
w = texts["worklog.md"]
rows = re.findall(r"^\| (\d{2}\.\d{2}\.\d{4}), (\d{2}:\d{2})", w, re.M)
chk("L11 хронология: 22 строки с полной датой", len(rows) >= 18, str(len(rows)))
chk("L12 в worklog только 25.11.2026 и 26.11.2026",
    {d for d, _ in rows} <= {"25.11.2026", "26.11.2026"})
chk("L13 разделы worklog датированы",
    "## Предполётные проверки (25.11.2026" in w)
chk("L14 в cost.md указана дата генераций",
    "25.11.2026" in texts["cost.md"])

# hygiene
bad = re.compile(r"TODO|XXX|FIXME|placeholder|симуляц|макет|mock", re.I)
hits = {n: sorted({m.group(0) for m in bad.finditer(t)}) for n, t in texts.items()}
chk("L15 нет заглушек и запрещённых слов", not any(hits.values()),
    str({k: v for k, v in hits.items() if v}))
chk("L16 нет пустых подстановок ___",
    all("___" not in t for t in texts.values()))
chk("L17 в логах нет квадратных скобок",
    all("[" not in t for t in texts.values()))

# changelog supersede note
cl = texts["repair-changelog.md"]
chk("L18 changelog: пометка о приоритете последнего раздела",
    "действует последний раздел" in cl and "163,1 Гц" in cl)
import hashlib

hashes = {n: hashlib.sha256((ROOT / "report" / n).read_bytes()).hexdigest().upper()
          for n in ("Отчет_М3_Задание1.docx", "Отчет_М3_Задание1.pdf")}
chk("L19 changelog: новые хеши совпадают с файлами",
    all(h in cl for h in hashes.values()),
    str(hashes))

print("\nSUMMARY", sum(ok), "/", len(ok))
if not all(ok):
    raise SystemExit(1)
