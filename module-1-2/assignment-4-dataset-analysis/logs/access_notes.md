# Доступ к данным: замена датасета не потребовалась

## Что не сработало

- **Просмотрщик Hugging Face для `HuggingFaceM4/COCO`.** API вернул HTTP 404:
  «The dataset viewer doesn't support this dataset because it runs arbitrary python code».
  Причина в том, что датасет подключается через Python-скрипт `COCO.py`, а не через
  готовые Parquet-файлы.
- **Миррор `nielsr/coco-100`.** API вернул HTTP 401: датасет не найден или недоступен.
- **Просмотрщик `merve/coco`.** API вернул HTTP 501: «Job manager crashed while running
  this job (missing heartbeats)».

## Что использовано

Датасет остался тем же — **MS COCO**. Изменён только способ доступа к файлам:

1. **Подписи:** официальный файл `captions_val2017.json` из репозитория `merve/coco` на
   Hugging Face (3,87 МБ; 25 014 аннотаций, 5 000 изображений). Файл содержит официальные
   подписи COCO 2017.
2. **Изображения:** официальный хост COCO `http://images.cocodataset.org/val2017/<id>.jpg`.
   Скачаны 20 файлов, которые соответствуют выбранным идентификаторам из аннотаций.

## Почему это корректно

- Использованы реальные изображения и официальные подписи MS COCO, а не синтетические
  или чужие примеры.
- Карточка датасета взята с Hugging Face (`HuggingFaceM4/COCO`), как требует задание.
- Замена на LAION-400M, Flickr30k или WIT не потребовалась.

## Проверка целостности

- Все 20 файлов открываются Pillow как JPEG.
- Для каждого файла есть 5 официальных подписей; в `logs/examples.json` сохранены
  `coco_image_id`, `file_name`, `source_url`, размеры и все подписи.
