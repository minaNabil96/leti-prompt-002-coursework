"""Parse blind labels, compute agreement, write agreement.json."""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"

CLASSES = ["афиша", "обложка книги", "постер фильма", "вне категорий"]


def parse_label(text: str) -> tuple[str, str]:
    flat = " ".join(text.replace("**", "").split())
    m = re.search(r"КЛАСС\s*:\s*(.+?)(?:\s+СОМНЕНИЕ|$)", flat, re.IGNORECASE)
    raw = m.group(1) if m else flat
    label = "не удалось распарсить"
    for canonical in CLASSES:
        if canonical in raw.lower():
            label = canonical
            break
    m2 = re.search(r"СОМНЕНИЕ\s*:\s*(.+)$", flat, re.IGNORECASE)
    doubt = m2.group(1).strip() if m2 else ""
    return label, doubt


def main():
    records = json.loads((LOGS / "labels_blind.json").read_text(encoding="utf-8"))
    matches = 0
    mismatches = []
    for rec in records:
        label, doubt = parse_label(rec["blind_label_raw"])
        rec["blind_label"] = label
        rec["doubt"] = doubt
        rec["match"] = label == rec["ground_truth"]
        if rec["match"]:
            matches += 1
        else:
            mismatches.append({
                "id": rec["id"],
                "ground_truth": rec["ground_truth"],
                "blind_label": label,
                "doubt": doubt,
            })
    total = len(records)
    out = {
        "model": "google/gemini-2.5-flash",
        "total": total,
        "matches": matches,
        "mismatches_count": total - matches,
        "agreement_rate": round(matches / total, 4),
        "details": records,
        "mismatch_analysis": mismatches,
    }
    (LOGS / "agreement.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Agreement: {matches}/{total} = {matches / total:.0%}")
    for m in mismatches:
        print("MISMATCH", m["id"], m["ground_truth"], "->", m["blind_label"], "|", m["doubt"][:80])

    stress_path = LOGS / "labels_blind_stress.json"
    if stress_path.exists():
        srecs = json.loads(stress_path.read_text(encoding="utf-8"))
        smatches = 0
        for rec in srecs:
            label, doubt = parse_label(rec["blind_label_raw"])
            rec["blind_label"] = label
            rec["doubt"] = doubt
            rec["match"] = label == rec["ground_truth"]
            smatches += int(rec["match"])
        stotal = len(srecs)
        sout = {
            "model": "google/gemini-2.5-flash",
            "protocol": "тот же промпт и инструкция, 8 пограничных изображений",
            "total": stotal,
            "matches": smatches,
            "mismatches_count": stotal - smatches,
            "agreement_rate": round(smatches / stotal, 4),
            "details": srecs,
        }
        (LOGS / "stress_agreement.json").write_text(
            json.dumps(sout, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Stress agreement: {smatches}/{stotal} = {smatches / stotal:.0%}")


if __name__ == "__main__":
    main()
