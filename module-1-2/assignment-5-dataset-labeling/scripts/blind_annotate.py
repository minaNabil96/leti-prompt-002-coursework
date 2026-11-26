"""Blind annotation: 10 images, Gemini 2.5 Flash, instruction only (no labels/prompts)."""
import base64
import json
import pathlib
import time

from openai import OpenAI

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"
IMAGES = ROOT / "images"
KEY = (ROOT / ".polza_key").read_text().strip()
client = OpenAI(api_key=KEY, base_url="https://polza.ai/api/v1")

BLIND_IDS = ["P01", "P05", "P07", "P09", "P11", "P14", "P15", "P17", "P20", "P22"]

INSTRUCTION = (LOGS / "instruction.md").read_text(encoding="utf-8")
PROMPT = (
    f"{INSTRUCTION}\n\n"
    "Классифицируйте следующее изображение по этой инструкции. "
    "Ответьте только двумя строками строго в формате:\n"
    "КЛАСС: <афиша|обложка книги|постер фильма|вне категорий>\n"
    "СОМНЕНИЕ: <краткое пояснение или «нет»>"
)


def main():
    gt = {x["id"]: x["class"] for x in json.loads(
        (LOGS / "labels_ground_truth.json").read_text(encoding="utf-8"))}
    out_path = LOGS / "labels_blind.json"
    results = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else []
    done = {r["id"] for r in results}

    for pid in BLIND_IDS:
        if pid in done:
            print(pid, "already annotated")
            continue
        idx = int(pid[1:])
        b64 = base64.b64encode((IMAGES / f"img_{idx:02d}.png").read_bytes()).decode()
        t0 = time.time()
        resp = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            temperature=0,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
            ]}],
        )
        elapsed = time.time() - t0
        text = resp.choices[0].message.content or ""
        usage = resp.usage.model_dump() if resp.usage else None
        results.append({
            "id": pid,
            "image": f"img_{idx:02d}.png",
            "ground_truth": gt[pid],
            "blind_label_raw": text,
            "elapsed_sec": round(elapsed, 2),
            "usage": usage,
            "response_id": getattr(resp, "id", None),
            "annotated_at": time.strftime("%Y-%m-%d %H:%M:%S%z"),
        })
        out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{pid} ({gt[pid]}): {text.replace(chr(10), ' | ')[:110]}", flush=True)

    print("saved", out_path, len(results), "records")


if __name__ == "__main__":
    main()
