"""Recalculate the LLM cost from the provider's actual per-token rates.

Two calibration requests with different token counts showed that the real
tariff is 35.9925 RUB / 1M input and 299.939 RUB / 1M output tokens, about
twice the catalogue values. The cost of all 12 turns is recomputed here from
the stored token counts.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
P = ROOT / "logs" / "conversation.json"

# least-squares solution of the two calibration requests:
#   9a + 4b = 0.00152368 ; 214a + b = 0.00800233
A_IN = 0.00003599248
B_OUT = 0.00029993947

data = json.loads(P.read_text(encoding="utf-8"))
for t in data["turns"]:
    t["cost_rub"] = round(t["prompt_tokens"] * A_IN
                          + t["completion_tokens"] * B_OUT, 6)
data["totals"]["cost_rub"] = round(sum(t["cost_rub"] for t in data["turns"]), 6)
data["pricing"] = {
    "source": "usage.cost_rub в ответах /chat/completions",
    "calibration_requests": [
        {"prompt_tokens": 9, "completion_tokens": 4, "cost_rub": 0.00152368},
        {"prompt_tokens": 214, "completion_tokens": 1, "cost_rub": 0.00800233},
    ],
    "rub_per_million_tokens": {"prompt": 35.99248, "completion": 299.93947},
    "catalogue_rub_per_million": {"prompt": 18.17802, "completion": 151.4835},
    "note": "Фактическая тарификация примерно вдвое выше каталожной; "
            "стоимость реплик пересчитана по фактическим ставкам.",
}
P.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("cost total:", data["totals"]["cost_rub"])
for t in data["turns"]:
    print(t["turn"], t["cost_rub"])
