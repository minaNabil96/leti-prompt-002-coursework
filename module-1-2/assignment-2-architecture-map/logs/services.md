# Карта архитектур: выбранные сервисы

Все действия выполнены через единый OpenAI-совместимый шлюз **Polza.ai** (`https://polza.ai/api/v1`).
Архитектурные метки подтверждены первоисточниками (технические отчёты, документация, arXiv).

## Трансформерные сервисы (текст)

| # | Polza model ID | Сервис / продукт | Задача | Архитектура | Основание |
| --- | --- | --- | --- | --- | --- |
| T1 | `openai/gpt-4o` | OpenAI ChatGPT (GPT-4o) | Чат-бот | Трансформер: авторегрессионный decoder-only, семейство GPT | GPT-4 Technical Report, arXiv:2303.08774: «GPT-4 is a Transformer-based model pre-trained to predict the next token in a document.» |
| T2 | `yandex/yandexgpt-5-lite` | Yandex GPT (Яндекс GPT) | Переводчик | Трансформер: YaLM, decoder-only | YaLM 100B (GitHub, yandex/YaLM-100B): «YaLM 100B is a GPT-like neural network for generating and processing text.» + документация Yandex Cloud |
| T3 | `google/gemini-2.5-flash` | Google Gemini 2.5 Flash | Суммаризация | Трансформер: авторегрессионный MoE-трансформер, мультимодальный | Gemini 1.5, arXiv:2403.05530, §3.1: «Gemini 1.5 Pro is a sparse mixture-of-expert (MoE) Transformer-based model.» |

## Диффузионные сервисы (изображения)

| # | Polza model ID | Сервис / продукт | Задача | Архитектура | Основание |
| --- | --- | --- | --- | --- | --- |
| D1 | `tongyi-mai/z-image` | Alibaba Z-Image | Генерация изображения | Диффузия: flow-matching DiT (S3-DiT) | Z-Image, arXiv:2511.22699: «...built upon a Scalable Single-Stream Diffusion Transformer (S3-DiT) architecture.» |
| D2 | `qwen/image` | Alibaba Qwen-Image | Генерация изображения | Диффузия: латентная, MMDiT | Qwen-Image Technical Report, arXiv:2508.02324, §2: «...a Multimodal Diffusion Transformer (MMDiT) functions as the backbone diffusion model...» |
| D3 | `bytedance/seedream-4` | ByteDance Seedream 4.0 | Генерация изображения | Диффузия: rectified flow / flow matching, DiT | Seedream 4.0, arXiv:2509.20427: «We develop a highly efficient diffusion transformer with a powerful VAE...» |

## Гибридный сервис

| # | Сервис | Трансформерная часть | Диффузионная часть | Основание |
| --- | --- | --- | --- | --- |
| H1 | Sber GigaChat (gigachat.ai) | GigaChat — LLM на трансформере (MoE) | Kandinsky 3.1 — латентная диффузия | GigaChat Family, arXiv:2506.09440; Kandinsky 3.1 (ai-forever.github.io/Kandinsky-3): «...a large-scale text-to-image generation model based on latent diffusion...» |

## Замены моделей (документированы)

- **T2:** `yandex/yandex-gpt` отсутствует в каталоге Polza.ai (проверено `GET /api/v1/models`).
  Заменено на `yandex/yandexgpt-5-lite` — самая дешёвая модель того же семейства YaLM
  (decoder-only трансформер). Архитектура не изменена.
- **D2:** `yandex/yandex-art` присутствует в каталоге, но провайдер стабильно отвечает HTTP 503
  `SERVICE_UNAVAILABLE` («Провайдер модели временно недоступен», 13+ попыток, см.
  `logs/d2_yandex-art_unavailable.log`). Заменено на `qwen/image` (3,00 ₽) — ближайшая по цене
  модель того же класса (латентная диффузия, MMDiT). Архитектура не изменена.
