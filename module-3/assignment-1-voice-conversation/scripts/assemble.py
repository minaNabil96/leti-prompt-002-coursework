"""Assemble voice-chat deliverables and verify every copy by SHA-256."""
import hashlib
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "report"
SCREENS = ROOT / "screenshots"
AUDIO = ROOT / "audio"
LOGS = ROOT / "logs"

LOCAL = ROOT / "deliverable"
MAIN = ROOT.parent / "deliverable"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def plan():
    items = [
        (REPORT / "Отчет_М3_Задание1.docx", "Отчет_М3_Задание1.docx"),
        (REPORT / "Отчет_М3_Задание1.pdf", "Отчет_М3_Задание1.pdf"),
    ]
    for p in sorted(SCREENS.glob("*.png")):
        items.append((p, f"Задание1_screenshots/{p.name}"))
    for p in sorted(AUDIO.glob("*.mp3")):
        items.append((p, f"Задание1_audio/{p.name}"))
    for name in ("conversation.json", "tts_results.json", "stt_check.json",
                 "prosody.json", "analysis.md", "cost.md", "worklog.md",
                 "generation-method.md", "models_raw.json"):
        p = LOGS / name
        if not p.exists():
            raise SystemExit(f"missing log: {p}")
        items.append((p, f"Задание1_logs/{name}"))
    return items


def copy_all(items, dest):
    dest.mkdir(parents=True, exist_ok=True)
    for src, rel in items:
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        if sha(src) != sha(out):
            raise SystemExit(f"hash mismatch: {out}")
    return dest


def main():
    items = plan()
    print("files:", len(items))
    for dest in (LOCAL, MAIN):
        copy_all(items, dest)
        print("assembled", dest)
    total = sum((LOCAL / rel).stat().st_size for _, rel in items)
    print("local size MB:", round(total / 1048576, 2))


if __name__ == "__main__":
    main()
