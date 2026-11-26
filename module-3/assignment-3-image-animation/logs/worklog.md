# Журнал выполнения — М3, задание 3

Все даты и время — 25.11.2026, московское время (MSK, UTC+3).

| Время | Этап | Что сделано | Артефакт |
|---|---|---|---|
| 23:04–23:05 | Pre-flight | Python 3.13.17, python-docx 1.2.0, Pillow 13.0.0, requests 2.34.2. `GET /api/v1/models` → 200, 401 модель; `tongyi-mai/z-image` и `bytedance/seedance-2-mini` присутствуют | — |
| 23:06:16 | Баланс | `GET /api/v1/balance` → 342,03694906 ₽ | — |
| 23:06:18 | S3 | Скачивание «Звёздной ночи» с Wikimedia Commons: 200, 618 432 Б, 1280×1014 | `sources/source_03_painting.jpg` |
| 23:06:29–23:06:50 | S1 | `tongyi-mai/z-image`, 1024×1024, 1,40 ₽, задача `gen_2236961525218676737` | `sources/source_01_portrait.png` |
| 23:06:38–23:07:00 | S2 | `tongyi-mai/z-image`, 1280×720, 1,40 ₽, задача `gen_2236961565524103169` | `sources/source_02_landscape.png` |
| 23:07:10–23:08:55 | A1 | `bytedance/seedance-2-mini`, 5 с, 640×640, 1 461 394 Б, 12,825 ₽; клиент упал при разборе ответа, файл восстановлен по `id` из истории | `animations/animation_01_portrait.mp4` |
| 23:09:23–23:11:35 | A2 | `bytedance/seedance-2-mini`, 5 с, 864×496, 1 373 408 Б, 12,825 ₽ | `animations/animation_02_landscape.mp4` |
| 23:11:22–23:13:10 | A3 | `bytedance/seedance-2-mini`, 5 с, 752×560, 2 876 649 Б, 12,825 ₽ | `animations/animation_03_painting.mp4` |
| 23:13 | Контроль видео | ffmpeg 9.0.2: H.264, 24 кадра/с, 121 кадр, 5,04 с, звуковой дорожки нет | `logs/video_info.json` |
| 23:15–23:16 | Скриншот | Реальный снимок `polza.ai/models/bytedance/seedance-2-mini` в headless Chrome 158.0.8127.88, 2160×2130; для отчёта нижнее поле кадрировано до 2160×2020 | `screenshots/03_interface_settings.png` |
| 23:18 | Метрики движения | Средняя покадровая разница и сетка 3×3 по каждому ролику | `logs/motion_metrics.json`, `logs/motion_regions.json` |
| 23:19–23:23 | Визуализации | Обзор исходников, таблица настроек, раскадровка из пяти кадров | `screenshots/01_sources_overview.png`, `02_settings_table.png`, `04_frames_montage.png` |
| 23:24–23:35 | Отчёт | Сборка DOCX, конвертация в PDF, самопроверка | `report/Отчет_М3_Задание3.docx`, `.pdf` |

## Замечания

- Имя файла скриншота — `03_interface_settings.png`, а не `03_interface_mockup.png` из плана:
  это настоящий снимок страницы, и слово «mockup» в имени противоречило бы его содержанию.
- Стоимость считалась по `usage.cost_rub` каждого ответа и сверена с историей генераций.
- Повторных или калибровочных медиа-запросов не было; все 5 задач завершились статусом
  `completed`.
