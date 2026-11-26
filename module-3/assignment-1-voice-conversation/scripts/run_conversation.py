"""Run the 12-turn conversation with the Polza.ai assistant.

LLM: google/gemini-2.5-flash via https://polza.ai/api/v1/chat/completions
The assistant is asked to write numbers, prices and dates as words so that the
TTS step does not have to expand digits.
"""
import json
import pathlib
import time

from openai import OpenAI

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
KEY = (ROOT / ".polza_key").read_text(encoding="utf-8").strip()

MODEL = "google/gemini-2.5-flash"
PRICE_IN = 18.17802 / 1_000_000     # RUB per prompt token
PRICE_OUT = 151.4835 / 1_000_000    # RUB per completion token

SYSTEM_PROMPT = (
    "Ты — голосовой ассистент для планирования путешествий. "
    "Отвечай на русском языке, дружелюбно и по делу. "
    "Если пользователь меняет тему — отвечай на новый вопрос, "
    "но помни всё, что обсуждалось ранее, и можешь вернуться к нему. "
    "Адаптируй стиль под пользователя: если он говорит коротко — отвечай кратко; "
    "если развёрнуто — отвечай подробно. "
    "В ответах с числами, ценами и датами пиши их прописью для удобства озвучки."
)

USER_REMARKS = [
    "Привет! Я планирую поездку в Казань на выходные. Что там обязательно нужно посмотреть?",
    "А какие музеи самые интересные? Можно с адресами?",
    "Сколько примерно стоит билет на поезд из Москвы в Казань в одну сторону?",
    "Посоветуй, пожалуйста, пару хороших ресторанов с татарской кухней. Желательно в центре города, недалеко от Кремля.",
    "А как лучше добраться от вокзала до центра — на такси или на метро?",
    "В какие дни Кремль открыт для туристов? Есть ли экскурсии с гидом?",
    "Стоп, забыла спросить. Какая сейчас погода в Санкт-Петербурге? Стоит ли брать зонт?",
    "Спасибо. А завтра в Питере тоже будет дождь?",
    "Так вот, вернёмся к Казани. Ты упоминал музеи — какой из них самый популярный у туристов?",
    "Окей. А где лучше остановиться — в гостинице возле Кремля или на улице Баумана?",
    "Сколько будет стоить номер на двоих на две ночи в среднем?",
    "Спасибо большое за помощь! Очень подробные ответы.",
]


def main():
    client = OpenAI(api_key=KEY, base_url="https://polza.ai/api/v1")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    turns = []
    started = time.strftime("%Y-%m-%d %H:%M:%S")

    for i, user_text in enumerate(USER_REMARKS, 1):
        messages.append({"role": "user", "content": user_text})
        t0 = time.time()
        r = client.chat.completions.create(
            model=MODEL, messages=messages, temperature=0.7)
        dt = time.time() - t0
        text = r.choices[0].message.content
        messages.append({"role": "assistant", "content": text})

        usage = r.usage
        tin = getattr(usage, "prompt_tokens", 0)
        tout = getattr(usage, "completion_tokens", 0)
        cost = tin * PRICE_IN + tout * PRICE_OUT
        turns.append({
            "turn": i,
            "user": user_text,
            "assistant": text,
            "elapsed_seconds": round(dt, 2),
            "prompt_tokens": tin,
            "completion_tokens": tout,
            "cost_rub": round(cost, 6),
            "finish_reason": r.choices[0].finish_reason,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        })
        print(f"[{i:2d}] {dt:4.1f}s in={tin:4d} out={tout:4d} "
              f"{cost:.4f} ₽ | {text[:70]}...")

    data = {
        "assistant": "Голосовой режим чат-бота (Polza.ai)",
        "llm_model": MODEL,
        "tts_model": "google/gemini-3.8-flash-lite-tts",
        "system_prompt": SYSTEM_PROMPT,
        "topic": "Планирование поездки в Казань",
        "started": started,
        "finished": time.strftime("%Y-%m-%d %H:%M:%S"),
        "temperature": 0.7,
        "turns": turns,
        "totals": {
            "turns": len(turns),
            "prompt_tokens": sum(t["prompt_tokens"] for t in turns),
            "completion_tokens": sum(t["completion_tokens"] for t in turns),
            "cost_rub": round(sum(t["cost_rub"] for t in turns), 6),
        },
    }
    (LOGS / "conversation.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("saved", LOGS / "conversation.json")
    print("LLM total:", data["totals"])


if __name__ == "__main__":
    main()
