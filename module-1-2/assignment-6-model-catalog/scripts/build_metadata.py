"""Compile parsed model records (facts from HF API + model cards)."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
META = ROOT / "logs" / "model_metadata"


def load(mid):
    return json.loads((META / f"{mid}.json").read_text(encoding="utf-8"))


def total_params(d):
    st = d.get("safetensors") or {}
    return st.get("total")


def fmt_params(n):
    if not n:
        return None
    return f"{n:,}".replace(",", " ") + f" ({n / 1e6:.1f} млн)"


RECORDS = {
    "M1": {
        "id": "facebook/detr-resnet-50",
        "direction": "Компьютерное зрение",
        "specialization": "Детекция объектов",
        "task": "Object detection (pipeline_tag: object-detection) — поиск и локализация объектов на изображении; DETR = DEtection TRansformer, энкодер-декодер с backbone ResNet-50 и 100 object queries.",
        "input_type": "Изображение RGB произвольного разрешения (в препроцессинге короткая сторона ≥ 800 px, длинная ≤ 1333 px).",
        "output_type": "До 100 объектов: метка класса (91 категория COCO), уверенность и bounding box; в карточке указан AP 42,0 на COCO 2017 val.",
        "training_data": "COCO 2017 object detection: 118 тыс. размеченных изображений для обучения и 5 тыс. для валидации; 300 эпох на 16 GPU V100.",
        "model_size": "41 631 008 параметров (41,6 млн), F32; ResNet-50 + transformer encoder-decoder.",
        "license": "Apache 2.0",
        "example_use": "Детекция объектов на фотографиях и видео: подсчёт людей и транспорта, видеоаналитика, автономные системы (карточка: «You can use the raw model for object detection»).",
        "limitations": "Карточка: поддержка только PyTorch, AP 42,0 (не SOTA); обучение только на 91 категории COCO, поэтому объекты вне этих классов не распознаются.",
        "downloads": None,
        "likes": None,
        "url": "https://huggingface.co/facebook/detr-resnet-50",
    },
    "M2": {
        "id": "dima806/facial_emotions_image_detection",
        "direction": "Компьютерное зрение",
        "specialization": "Распознавание эмоций по лицу",
        "task": "Image classification (pipeline_tag: image-classification) — классификация эмоции по изображению лица; ViT, дообученный на google/vit-base-patch16-224-in21k.",
        "input_type": "Изображение лица (RGB).",
        "output_type": "Один из 7 классов эмоций с вероятностью: angry, disgust, fear, happy, neutral, sad, surprise; accuracy 0,9092 на 25 170 изображениях (classification report в карточке).",
        "training_data": "Набор данных в карточке явно не назван: приведена ссылка на Kaggle-ноутбук и classification report по 25 170 изображениям (примерно по 3,6 тыс. на класс); базовая модель google/vit-base-patch16-224-in21k.",
        "model_size": "85 804 039 параметров (85,8 млн), F32; ViT-base (patch 16, 224 px).",
        "license": "Apache 2.0",
        "example_use": "Анализ эмоциональной реакции на фото и видео: UX-исследования, оценка рекламы, мониторинг аудитории (карточка: «Returns facial emotion with about 91% accuracy»).",
        "limitations": "Карточка приводит только accuracy 0,9092 и метрики по классам; ограничения (поза, освещение, культурные различия мимики) в карточке не описаны — это наш вывод из анализа.",
        "downloads": None,
        "likes": None,
        "url": "https://huggingface.co/dima806/facial_emotions_image_detection",
    },
    "M3": {
        "id": "facebook/musicgen-small",
        "direction": "Генерация контента",
        "specialization": "Генерация музыки",
        "task": "Text-to-audio (pipeline_tag: text-to-audio) — генерация музыки по текстовому описанию; авторегрессионный transformer над 32 кГц EnCodec-токенизатором с 4 кодовыми книгами.",
        "input_type": "Текстовый промпт на английском (например, «a catchy beat for a podcast intro»).",
        "output_type": "Аудиосигнал (32 кГц), в transformers — массив waveform; в карточке заявлена генерация музыкальных фрагментов.",
        "training_data": "20 тыс. часов лицензированной музыки: Meta Music Initiative Sound Collection, Shutterstock music collection, Pond5 music collection.",
        "model_size": "591 087 174 параметра в файлах весов (591,1 млн, F32); в карточке чекпоинт обозначен как MusicGen Small 300M — 300 млн относится к языковой модели без аудиокодека.",
        "license": "CC-BY-NC 4.0 (только некоммерческое использование)",
        "example_use": "Генерация фоновой музыки для видео, подкастов и презентаций по текстовому описанию (примеры виджета: «a funky house with 80s hip hop vibes», «a catchy beat for a podcast intro»).",
        "limitations": "Карточка: обучение на данных музыкальных профессионалов, возможна нехватка культурного разнообразия; модель исследовательская, не предназначена для продакшена без анализа рисков; лицензия запрещает коммерческое использование.",
        "downloads": None,
        "likes": None,
        "url": "https://huggingface.co/facebook/musicgen-small",
    },
    "M4": {
        "id": "Salesforce/codegen-350M-mono",
        "direction": "Генерация контента",
        "specialization": "Генерация кода",
        "task": "Text generation (pipeline_tag: text-generation) — синтез программ на Python по естественно-языковому описанию; авторегрессионная модель CodeGen.",
        "input_type": "Текст на английском в виде комментария или начала функции (например, «def hello_world():»).",
        "output_type": "Продолжение текста — код на Python (токены).",
        "training_data": "BigPython: 71,7 млрд токенов кода на Python; чекпоинт инициализирован из CodeGen-Multi 350M.",
        "model_size": "350 млн параметров (указано в карточке); веса в формате pytorch_model.bin, отдельного safetensors-файла нет.",
        "license": "BSD-3-Clause",
        "example_use": "Program synthesis: генерация и дополнение кода по комментарию; пример из карточки — продолжение «def hello_world():».",
        "limitations": "Карточка: релиз предназначен только для исследований в поддержку статьи; модель лучше всего работает с промптами в виде комментариев на английском; качество кода не гарантируется и требует проверки.",
        "downloads": None,
        "likes": None,
        "url": "https://huggingface.co/Salesforce/codegen-350M-mono",
    },
    "M5": {
        "id": "cardiffnlp/twitter-roberta-base-sentiment",
        "direction": "Анализ данных",
        "specialization": "Анализ тональности",
        "task": "Text classification (pipeline_tag: text-classification) — определение тональности короткого текста; roberta-base, дообученный на TweetEval.",
        "input_type": "Текст на английском (короткие сообщения в стиле Twitter).",
        "output_type": "Три класса с вероятностями: negative (LABEL_0), neutral (LABEL_1), positive (LABEL_2).",
        "training_data": "Около 58 млн твитов для предобучения и бенчмарк TweetEval для дообучения (датасет tweet_eval); язык — английский.",
        "model_size": "В карточке размер не указан; архитектура roberta-base, около 125 млн параметров; веса pytorch_model.bin.",
        "license": "Не указана в карточке модели (поле license отсутствует и в метаданных, и в README).",
        "example_use": "Мониторинг тональности упоминаний бренда в соцсетях, анализ отзывов и комментариев (карточка: задача sentiment в TweetEval).",
        "limitations": "Карточка: модель только для английского; обучена на твитах, поэтому стиль других текстов может давать смещение. Ограничения по сарказму и смешанной тональности в карточке не описаны — это наш вывод.",
        "downloads": None,
        "likes": None,
        "url": "https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment",
    },
    "M6": {
        "id": "d4data/biomedical-ner-all",
        "direction": "Анализ данных",
        "specialization": "Медицинский NER",
        "task": "Token classification (pipeline_tag: token-classification) — извлечение биомедицинских сущностей из клинического текста; DistilBERT, дообученный на MACCROBAT2018.",
        "input_type": "Текст на английском: клинические заметки, описания случаев.",
        "output_type": "Span-разметка сущностей: 107 типов (например, Disease, Medication, Anatomy) с границами и уверенностью.",
        "training_data": "MACCROBAT2018 (Maccrobat) — корпус клинических описаний случаев; базовая модель distilbert-base-uncased.",
        "model_size": "66 427 476 параметров (66,4 млн), F32; DistilBERT.",
        "license": "Apache 2.0",
        "example_use": "Извлечение болезней, лекарств и анатомических областей из медицинских текстов и описаний случаев (пример виджета — фрагмент клинического case report).",
        "limitations": "Карточка: только английский, 107 типов сущностей из одного корпуса (MACCROBAT); модель не является медицинским изделием и не предназначена для постановки диагноза (наш вывод).",
        "downloads": None,
        "likes": None,
        "url": "https://huggingface.co/d4data/biomedical-ner-all",
    },
}

EXPECTED = {
    "M1": ("object-detection", "apache-2.0", 41631008),
    "M2": ("image-classification", "apache-2.0", 85804039),
    "M3": ("text-to-audio", "cc-by-nc-4.0", 591087174),
    "M4": ("text-generation", "bsd-3-clause", None),
    "M5": ("text-classification", None, None),
    "M6": ("token-classification", "apache-2.0", 66427476),
}


def main():
    for mid, rec in RECORDS.items():
        d = load(mid)
        pipe, lic, params = EXPECTED[mid]
        assert d["pipeline_tag"] == pipe, (mid, d["pipeline_tag"])
        if lic:
            assert f"license:{lic}" in d["tags"], (mid, d["tags"])
        if params:
            assert total_params(d) == params, (mid, total_params(d))
        rec["downloads"] = d.get("downloads")
        rec["likes"] = d.get("likes")
        rec["library_name"] = d.get("library_name")
        rec["pipeline_tag"] = d.get("pipeline_tag")
        rec["model_type"] = (d.get("config") or {}).get("model_type")
        rec["fetched_at_utc"] = json.loads(
            (META / "_catalog.json").read_text(encoding="utf-8"))["fetched_at_utc"]
        (META / f"{mid}_parsed.json").write_text(
            json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        print(mid, rec["id"], "|", rec["specialization"], "|", rec["license"],
              "| downloads", rec["downloads"])


if __name__ == "__main__":
    main()
