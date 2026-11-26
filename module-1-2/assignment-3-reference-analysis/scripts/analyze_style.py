"""Step 3 — multimodal style analysis of the reference (LLM call 1)."""
import base64
import json
import pathlib
import time

from openai import OpenAI

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"
SHOTS = ROOT / "screenshots"
KEY = (ROOT / ".polza_key").read_text().strip()
client = OpenAI(api_key=KEY, base_url="https://polza.ai/api/v1")

img_b64 = base64.b64encode((SHOTS / "reference_1024.jpg").read_bytes()).decode()
data_url = f"data:image/jpeg;base64,{img_b64}"

ANALYSIS_PROMPT = (
    "Перед вами знаменитая картина Винсента Ван Гога «Звёздная ночь» (1889). "
    "Проведите детальный анализ её стиля. Разберите отдельно:\n"
    "1. Композицию (расположение объектов, баланс, направление взгляда)\n"
    "2. Цветовую палитру (основные цвета, их соотношение, контрасты)\n"
    "3. Освещение (источники света, распределение светотени, яркость)\n"
    "4. Технику и стиль (мазок, фактура, импасто, направление линий)\n"
    "5. Настроение (эмоциональный тон, атмосфера)\n"
    "Отвечайте на русском языке, по каждому пункту — 2–3 предложения с конкретными деталями."
)

t0 = time.time()
resp = client.chat.completions.create(
    model="google/gemini-2.5-flash",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": ANALYSIS_PROMPT},
            {"type": "image_url", "image_url": {"url": data_url}},
        ],
    }],
)
elapsed = time.time() - t0
text = resp.choices[0].message.content
usage = resp.usage.model_dump() if resp.usage else None

(LOGS / "analysis.json").write_text(json.dumps({
    "model": "google/gemini-2.5-flash",
    "architecture": "Transformer (multimodal MoE)",
    "prompt": ANALYSIS_PROMPT,
    "response": text,
    "elapsed": round(elapsed, 2),
    "usage": usage,
    "response_id": getattr(resp, "id", None),
}, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"elapsed {elapsed:.1f}s, usage {usage.get('total_tokens') if usage else '?'} tokens")
print(text)
