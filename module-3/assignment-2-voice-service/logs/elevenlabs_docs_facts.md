# ElevenLabs — извлечённые факты (официальная документация и сайт)

Дата обращения: **25.11.2026**.
Прямой доступ к `elevenlabs.io` из РФ закрыт: сервер отвечает редиректом (302) на
`https://geo-restriction.elevenlabs.io/` со страницей **«Access restricted»**.
Страницы получены из архива официального сайта
(web.archive.org) — снимки от 06.12.2025 до 25.11.2026; сырые HTML лежат в `logs/`,
очищенный текст — в `logs/text/`.

## Сервис

- Название: ElevenLabs.
- URL: https://elevenlabs.io
- Продукты: Text to Speech, Speech to Text, Voice Cloning (Instant / Professional),
  Voice Design, Studio (редактор озвучки), Dubbing, Music, Agents.
- Библиотека голосов: 17 000+ голосов (главная страница: 17 500+).
- Бесплатный тариф: $0, **10 000 кредитов в месяц**, доступны TTS, STT, Sound
  Effects, Voice Design, Music, 3 проекта в Studio.
- Клонирование голоса в бесплатный тариф **не входит**: в карточке тарифа Starter
  перечислено «Everything in free, plus: Commercial License, Instant Voice
  Cloning, 20 Projects in Studio»; Professional Voice Cloning появляется на
  тарифе Creator («Everything in Starter, plus: Professional Voice Cloning»).
  Пробного периода для клонирования на сайте не заявлено.
- Коммерческая лицензия: с тарифа Starter («Commercial License»); на бесплатном
  тарифе коммерческое использование не предусмотрено.

## Входные данные для клонирования

### Instant Voice Cloning (IVC)

- Документация: «Record at least 1 minute of audio»; «Avoid recording more than
  3 minutes, this will yield little improvement and can, in some cases, even be
  detrimental to the clone».
- Рекомендуется «approximately 1-2 minutes of clear audio without any reverb,
  artifacts, or background noise of any kind».
- Кодек не важен («we do not mean the codec, such as MP3 or WAV; we mean how the
  audio was captured»), но «using MP3 at 128 kbps and above is advised».
- Уровень: «between -23 dB and -18 dB RMS with a true peak of -3 dB».
- Один диктор, ровная манера: «Feeding the AI audio that is very dynamic, meaning
  wide fluctuations in pitch and volume, will yield less predictable results».
- Готовность: секунды (маркетинговая страница: «voice replica ready in seconds»,
  «Clone any voice with 1-5 minutes of audio»).

### Professional Voice Cloning (PVC)

- Минимум: «The bare minimum we recommend is 30 minutes of audio»; оптимум —
  «closer to 2-3 hours of audio» (в другом месте: «at least an hour … ideally as
  close to three hours as possible»).
- Обучение: «usually fine-tuning will take 3-6 hours» (в очереди — до 6–24 ч).
- Только собственный голос: «For now, we only allow you to clone your own voice.
  You will be asked to go through a verification process»; в FAQ: «You can only
  create a Professional Voice Clone of your own voice. Even with their consent,
  you cannot clone someone else's voice».
- Пение не поддерживается: «Professional Voice Clones do not currently support
  singing».
- Рекомендации по записи: XLR-микрофон (примеры — Audio-Technica AT2020, Rode NT1
  + Focusrite), поп-фильтр, расстояние «approximately two fists away», комната с
  акустической обработкой.
- Выход 44.1 кГц PCM/WAV — на тарифе Pro («44.1kHz PCM audio output via API»).

## Управляемые параметры (страница Voice settings)

- Общая рекомендация: «The most common setting is stability around 50, similarity
  around 75, and keeping style at 0, with minimal changes thereafter».
- **Speed** — 0.7–1.2, по умолчанию 1.0; «Extreme values may affect the quality»;
  недоступен для Eleven v3.
- **Stability** (0–1): ниже — шире эмоциональный диапазон и больше вариативности
  между генерациями; выше — стабильнее и ровнее, вплоть до монотонности.
- **Similarity** (0–1): насколько близко к исходному голосу; при шумном исходнике
  высокое значение переносит артефакты. Недоступен для Eleven v3.
- **Style exaggeration** (0–1): усиливает манеру оригинала, повышает задержку;
  «we recommend keeping this setting at 0 at all times».
- **Speaker Boost** (on/off): усиливает сходство с оригиналом, немного повышает
  задержку; недоступен для Eleven v3.
- **Clone Strength** (0–100 %): только для PVC + Eleven v4; «For most voices,
  start at 0%».
- **Модель**: Eleven v4 Turbo (90+ языков, задержка ~100 мс), Eleven v3 (70+
  языков, эмоциональные аудиотеги вида `[sarcastically]`, `[whispers]`),
  Eleven Multilingual v2 (29 языков, «most life-like, emotionally rich», лимит
  10 000 символов), Eleven Flash v2.5 (32 языка, задержка <75 мс, лимит 40 000
  символов).
- **Голос**: 17 000+ готовых голосов, Voice Design (голос по текстовому
  описанию), клонированный голос.
- **Паузы**: SSML-теги `break` и пунктуация; «How the model handles these pauses
  can vary».
- **Аудиоэффекты**: filter, noise, space, distance (near/medium/far).

## Языки

- Multilingual v2 — 29 языков, в списке есть `ru` Russian и `uk` Ukrainian
  (полный список: ar, bg, zh, hr, cs, da, nl, en, fil, fi, fr, de, el, hi, id,
  it, ja, ko, ms, pl, pt, ro, ru, sk, es, sv, ta, tr, uk).
- Flash v2.5 — 32 языка, русский есть.
- Eleven v3 — 70+ языков, русский есть.
- Eleven v4 — 90+ языков.
- Отдельная страница https://elevenlabs.io/text-to-speech/russian с русской
  демонстрацией (голос Artem, аудиотеги `[sarcastically]`, `[giggles]`,
  `[whispers]`).
- Оговорка PVC: если клон обучен на англоязычных записях, в другом языке будет
  акцент — «It is best to use samples speaking the language you want the PVC to be
  used for».

## Ограничения и согласие

- «You can freely clone your own voice for any purpose. Cloning someone else's
  voice requires their explicit consent. Using cloned voices for fraud,
  impersonation, or creating misleading content is illegal in most jurisdictions.
  Commercial use may require appropriate licensing».
- При создании IVC нужно подтвердить право и согласие: «confirm that you have the
  right and consent to clone the voice».
- «voice verification systems that confirm you have permission to clone a voice»;
  «Your voice data is never shared or used for training without explicit consent».
- «Your voice data is encrypted and protected from unauthorized use».
- Ограничения по странам (страница блокировки): Беларусь, Куба, Иран, КНДР,
  Россия, Сирия, Крым и отдельные области Украины.

## Применение в мультимедиа

Маркетинговые сценарии самого сервиса: аудиокниги, подкасты, видеоозвучка,
игры, реклама, локализация на 90+ языков. Для PR-специальности выбраны два
собственных сценария — см. `research_notes.md`.
