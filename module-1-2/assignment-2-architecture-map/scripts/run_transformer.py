"""Step 3 — transformer service actions (T1, T2, T3) via Polza.ai.

Uses the OpenAI-compatible endpoint https://polza.ai/api/v1.
Writes ./logs/raw_T{1,2,3}.json with input, output, usage and timing.
"""

import json
import pathlib
import time

from openai import OpenAI

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = (ROOT / ".polza_key").read_text().strip()
client = OpenAI(api_key=KEY, base_url="https://polza.ai/api/v1")

SOURCE = (ROOT / "logs" / "summarization_source.txt").read_text(encoding="utf-8").strip()

ACTIONS = [
    {
        "id": "T1",
        "model": "openai/gpt-4o",
        "service": "OpenAI ChatGPT (GPT-4o)",
        "task": "Чат-бот / объяснение",
        "architecture": "Transformer (autoregressive decoder-only, GPT family)",
        "messages": [
            {
                "role": "user",
                "content": (
                    "Объясни принцип механизма внимания (attention) в трансформерах "
                    "двумя предложениями."
                ),
            }
        ],
    },
    {
        "id": "T2",
        "model": "yandex/yandexgpt-5-lite",
        "service": "Yandex GPT (Яндекс GPT)",
        "task": "Переводчик",
        "architecture": "Transformer (YaLM — Yandex Large Language Model, decoder-only transformer)",
        "messages": [
            {
                "role": "user",
                "content": (
                    "Переведи на английский язык: \"Привет, мир! Сегодня хорошая погода "
                    "для прогулки в парке.\""
                ),
            }
        ],
    },
    {
        "id": "T3",
        "model": "google/gemini-2.5-flash",
        "service": "Google Gemini 2.5 Flash",
        "task": "Суммаризация",
        "architecture": "Transformer (autoregressive MoE transformer, multimodal)",
        "messages": [
            {
                "role": "user",
                "content": "Суммаризируй этот текст в 2 предложениях:\n\n" + SOURCE,
            }
        ],
    },
]

for action in ACTIONS:
    t0 = time.time()
    resp = client.chat.completions.create(
        model=action["model"],
        messages=action["messages"],
    )
    elapsed = time.time() - t0
    out = resp.choices[0].message.content
    usage = None
    try:
        usage = resp.usage.model_dump()
    except Exception:  # noqa: BLE001
        usage = getattr(resp, "usage", None) and str(resp.usage)

    record = {
        "id": action["id"],
        "service": action["service"],
        "model": action["model"],
        "task": action["task"],
        "architecture": action["architecture"],
        "input": action["messages"][-1]["content"],
        "output": out,
        "elapsed": round(elapsed, 2),
        "usage": usage,
        "response_id": getattr(resp, "id", None),
    }
    (ROOT / "logs" / f"raw_{action['id']}.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"{action['id']} [{action['model']}] {elapsed:.1f}s -> {out[:90]!r}")
