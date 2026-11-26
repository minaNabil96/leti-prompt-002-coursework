"""Step 4 — compose the detailed generation prompt (LLM call 2, multi-turn)."""
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

analysis = json.loads((LOGS / "analysis.json").read_text(encoding="utf-8"))["response"]

COMPOSE_PROMPT = (
    "На основе вашего анализа стиля этой картины составьте подробный промпт "
    "для генератора изображений на новый сюжет: «кот под дождём». "
    "Изображение должно быть выполнено в стиле этого референса — "
    "с теми же цветовыми сочетаниями, техникой мазка, освещением и настроением. "
    "Промпт должен быть на английском языке (генераторы работают лучше на английском), "
    "содержать 4–6 предложений и включать конкретные описания: "
    "палитру, тип мазка, освещение, композицию, атмосферу. "
    "Не упоминайте имя Ван Гога и не копируйте картину — нужен новый сюжет в том же стиле."
)

t0 = time.time()
resp = client.chat.completions.create(
    model="google/gemini-2.5-flash",
    messages=[
        {"role": "user", "content": [
            {"type": "text", "text": "Проанализируйте стиль этой картины."},
            {"type": "image_url", "image_url": {"url": data_url}},
        ]},
        {"role": "assistant", "content": analysis},
        {"role": "user", "content": COMPOSE_PROMPT},
    ],
)
elapsed = time.time() - t0
composed = resp.choices[0].message.content
usage = resp.usage.model_dump() if resp.usage else None

(LOGS / "composed_prompt.txt").write_text(composed, encoding="utf-8")
(LOGS / "naive_prompt.txt").write_text("A cat in the rain\n", encoding="utf-8")
(LOGS / "compose_call.json").write_text(json.dumps({
    "model": "google/gemini-2.5-flash",
    "architecture": "Transformer (multimodal MoE)",
    "prompt": COMPOSE_PROMPT,
    "response": composed,
    "elapsed": round(elapsed, 2),
    "usage": usage,
    "response_id": getattr(resp, "id", None),
}, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"elapsed {elapsed:.1f}s, usage {usage.get('total_tokens') if usage else '?'} tokens")
print(composed)
