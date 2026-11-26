"""Demo D2: sentiment analysis with cardiffnlp/twitter-roberta-base-sentiment.

Real custom text, real checkpoint. The online Inference API/widget needs an account
token, so the model is executed locally through transformers (CPU).
"""
import json
import pathlib
import time

from transformers import pipeline

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEMO = ROOT / "logs" / "demo_results"

TEXT = ("I absolutely love the new AI course on prompt engineering — it's "
        "incredibly useful and well-structured!")


def main():
    t0 = time.time()
    clf = pipeline("text-classification",
                   model="cardiffnlp/twitter-roberta-base-sentiment",
                   top_k=None, device=-1)
    load_s = time.time() - t0
    t1 = time.time()
    raw = clf(TEXT)[0]
    infer_s = time.time() - t1
    print(raw)

    labels = {"LABEL_0": "negative", "LABEL_1": "neutral", "LABEL_2": "positive"}
    scores = {labels.get(r["label"], r["label"]): round(float(r["score"]), 4)
              for r in raw}
    best = max(scores, key=scores.get)

    (DEMO / "D2.json").write_text(json.dumps({
        "model": "cardiffnlp/twitter-roberta-base-sentiment",
        "run_mode": "local transformers pipeline (CPU), same checkpoint as the card",
        "reason": "HF Inference API returns HTTP 401 without a token; online widget asks to log in",
        "input_text": TEXT,
        "raw_output": raw,
        "scores": scores,
        "predicted": best,
        "confidence": scores[best],
        "model_load_seconds": round(load_s, 1),
        "inference_seconds": round(infer_s, 1),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("predicted", best, scores)


if __name__ == "__main__":
    main()
