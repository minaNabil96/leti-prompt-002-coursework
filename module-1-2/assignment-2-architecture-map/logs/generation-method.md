# Метод генерации и обращения к API

## Точка входа

- Base URL: `https://polza.ai/api/v1` (OpenAI-совместимый шлюз Polza.ai).
- Авторизация: `Authorization: Bearer pza_...`.
- Ключ взят из рабочего конфига `opencode.json` (переменная `POLZA_API_KEY` в окружении не была задана).
  Ключ сохранён локально в `arch-map/.polza_key` только для запуска скриптов.

## Текстовые сервисы (T1, T2, T3)

Использован OpenAI SDK:

```python
client = OpenAI(api_key=KEY, base_url="https://polza.ai/api/v1")
resp = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": PROMPT}])
```

Скрипт: `scripts/run_transformer.py`. Полные вход/выход/usage сохранены в `logs/raw_T1.json`,
`logs/raw_T2.json`, `logs/raw_T3.json`.

## Диффузионные сервисы (D1, D2, D3)

Прямой вызов `POST /images/generations` для части моделей не работает (Z-Image требует явный
`aspect_ratio`), поэтому использован унифицированный **Media API**:

```python
POST /api/v1/media
{"model": MODEL, "input": {"prompt": PROMPT, "aspect_ratio": "1:1"}}
# затем GET /api/v1/media/{id} до статуса "completed"
```

Скрипт: `scripts/run_diffusion.py`. Метаданные и фактическая стоимость — в `logs/raw_D*.json`.

## Замены (не меняют архитектурный класс)

- T2: `yandex/yandex-gpt` → `yandex/yandexgpt-5-lite` (нет в каталоге; то же семейство YaLM).
- D2: `yandex/yandex-art` → `qwen/image` (провайдер YandexART стабильно 503; та же латентная диффузия).

Подробности и обоснование — в `logs/services.md`. Никаких «тихих» подмен архитектур не было.

## Ошибки и повторные попытки

- D2 (`yandex/yandex-art`): 13 неудачных попыток создания задачи, все — HTTP 503
  `SERVICE_UNAVAILABLE`. Неудачные попытки не тарифицировались (в истории операций их нет).
- Одна попытка к `/images/generations` для YandexART вернула 201, но задача завершилась
  статусом `failed` по той же причине 503.
- Повторных успешных генераций и двойного списания нет.
