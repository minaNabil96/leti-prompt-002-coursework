# Журнал работ. Задание 4. Анализ открытого мультимедийного датасета

Курс «Применение генеративных нейронных моделей в мультимедиа», кафедра ИС, ЛЭТИ. Время — московское (MSK, UTC+3). Дата работы — 19.11.2026.

## Предполётные проверки

- Python 3.13.17; Pillow 13.0.0, python-docx, requests 2.34.2 установлены.
- Доступ к Hugging Face: `GET /api/datasets/HuggingFaceM4/COCO` → HTTP 200.
- Карточка датасета и README загружены: `logs/dataset_metadata.json` (1,7 КБ),
  `logs/dataset_readme.md` (3,7 КБ).
- Ключ Polza.ai и платные API не использовались: задание выполняется только на открытых
  данных и публичных API.

## Доступ к примерам: обход ограничений просмотрщика

1. `datasets-server.huggingface.co/rows?dataset=HuggingFaceM4/COCO...` → HTTP 404 с
   пояснением: «The dataset viewer doesn't support this dataset because it runs arbitrary
   python code».
2. Резервный миррор `nielsr/coco-100` → HTTP 401: датасет не найден или недоступен
   (ошибка сохранена в `logs/viewer_error.json`).
3. Миррор `merve/coco` доступен как репозиторий, но просмотрщик строк вернул HTTP 501
   («Job manager crashed while running this job»).
4. **Решение без замены датасета:** аннотации взяты из официального файла
   `captions_val2017.json` (3,87 МБ), загруженного из репозитория `merve/coco` на Hugging
   Face; изображения — с официального хоста COCO
   `http://images.cocodataset.org/val2017/<id>.jpg`. Это те же реальные изображения и
   подписи MS COCO, а не заменитель датасета. Подробности — `logs/access_notes.md`.

## Хронология

| Время (MSK) | Действие |
| --- | --- |
| 15:40 | Создана структура `dataset-analysis/`; проверены Python и доступ к Hugging Face. |
| 15:42 | Загружены карточка и README датасета `HuggingFaceM4/COCO`. |
| 15:43 | Проверены просмотрщик и резервные мирроры; зафиксированы 404/401/501. |
| 15:44 | Загружен `captions_val2017.json` (25 014 аннотаций, 5 000 изображений). |
| 15:46 | Скачаны 20 реальных изображений (3,38 МБ) с официального хоста COCO; подписи сохранены. |
| 15:50 | Собраны композиты `01_dataset_card.png`, `02_data_examples.png`, `03_limitations.png`. |
| 15:55 | Заполнены `limitations.md`, `creation_method.md`, `model_analysis.md`, `bias_analysis.md`, `legal_analysis.md`. |
| 16:05 | Собраны DOCX и PDF отчёта, выполнена самопроверка вёрстки. |

## Данные и статистика

- 20 изображений, 100 подписей (по 5 на изображение).
- Средняя длина первой подписи — 10,4 слова (минимум 8, максимум 14).
- Размер файлов — от 41 до 315 КБ, в среднем 169 КБ; разрешения от 426×640 до 640×480.
- Выборка: идентификаторы изображений взяты равномерно по отсортированному списку, чтобы
  не ограничиваться первыми кадрами одного сюжета.

## Инструменты

Python 3.13.17, Pillow 13.0.0, requests 2.34.2, python-docx, LibreOffice (конвертация
DOCX → PDF), curl.exe для загрузки файлов. Сторонние API с оплатой не использовались.

## Итоги

- Карточка: `screenshots/01_dataset_card.png`; метаданные — `logs/dataset_metadata.json`.
- Примеры: `screenshots/02_data_examples.png`; 20 файлов `example_01..20.jpg`;
  структурированные данные — `logs/examples.json`.
- Ограничения: `screenshots/03_limitations.png`, `logs/limitations.md`.
- Способ создания: смешанный (Flickr + Amazon Mechanical Turk).
- Отчёт: `report/Отчет_Задание4.docx`, `report/Отчет_Задание4.pdf`.
