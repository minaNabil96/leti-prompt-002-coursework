"""Transcribe the synthesized files with Whisper to check what is actually heard."""
import difflib
import json
import pathlib
import re
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
KEY = (ROOT / ".polza_key").read_text(encoding="utf-8").strip()
URL = "https://polza.ai/api/v1/audio/transcriptions"
MODEL = "openai/whisper-large-v3"
PRICE_PER_MIN = 0.108

DIGITS = {"ноль": 0, "один": 1, "одна": 1, "два": 2, "две": 2, "три": 3,
          "четыре": 4, "пять": 5, "шесть": 6, "семь": 7, "восемь": 8,
          "девять": 9, "десять": 10}


def norm_words(text: str) -> list[str]:
    text = text.lower().replace("ё", "е")
    text = re.sub(r"[^а-яa-z0-9\s-]", " ", text)
    return [w for w in text.split() if w]


def main():
    data = json.loads((LOGS / "tts_results.json").read_text(encoding="utf-8"))
    out = []
    for n, rec in enumerate(data["files"], 1):
        p = ROOT / rec["file"]
        t0 = time.time()
        with p.open("rb") as f:
            r = requests.post(
                URL,
                headers={"Authorization": f"Bearer {KEY}"},
                files={"file": (p.name, f, "audio/mpeg")},
                data={"model": MODEL, "language": "ru",
                      "response_format": "json", "temperature": 0},
                timeout=600,
            )
        r.raise_for_status()
        text = r.json()["text"].strip()
        dt = time.time() - t0
        minutes = rec["duration_decoded_s"] / 60
        ref, hyp = norm_words(rec["speech_text"]), norm_words(text)
        sm = difflib.SequenceMatcher(None, ref, hyp)
        diffs = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal":
                diffs.append({"op": tag, "reference": " ".join(ref[i1:i2]),
                              "heard": " ".join(hyp[j1:j2])})
        out.append({
            "file": rec["file"],
            "turn": rec["turn"],
            "model": MODEL,
            "duration_s": rec["duration_decoded_s"],
            "cost_rub": round(minutes * PRICE_PER_MIN, 4),
            "transcript": text,
            "reference": rec["speech_text"],
            "similarity": round(sm.ratio(), 4),
            "differences": diffs,
            "request_seconds": round(dt, 2),
        })
        print(f"[{n}/6] {rec['file']}: similarity {sm.ratio():.3f}, "
              f"diffs {len(diffs)}, {out[-1]['cost_rub']:.3f} RUB")
        for d in diffs:
            print("     ", d)

    res = {
        "model": MODEL,
        "endpoint": URL,
        "price_per_minute_rub": PRICE_PER_MIN,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "note": "Whisper нормализует числа в цифры; расхождения в записи чисел"
                " не считаются ошибкой синтеза.",
        "files": out,
        "totals": {
            "files": len(out),
            "duration_s": round(sum(x["duration_s"] for x in out), 2),
            "cost_rub": round(sum(x["cost_rub"] for x in out), 4),
        },
    }
    (LOGS / "stt_check.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print("total:", res["totals"])


if __name__ == "__main__":
    main()
