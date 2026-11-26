import json
import pathlib

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots"
LOGS = ROOT / "logs"

raw = SHOTS / "reference_raw.jpg"
im = Image.open(raw)
print("raw:", im.format, im.size, im.mode, raw.stat().st_size, "bytes")

im = im.convert("RGB")
scale = 1024 / max(im.size)
if scale < 1:
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
im.save(SHOTS / "reference_1024.jpg", quality=92)
print("reference_1024.jpg:", im.size)

(LOGS / "reference.md").write_text(
    """# Референсное изображение

- **Название:** The Starry Night («Звёздная ночь»)
- **Автор:** Vincent van Gogh (Винсент Ван Гог)
- **Год:** 1889
- **Техника:** масло на холсте (oil on canvas)
- **Размер:** 73,7 × 92,1 см
- **Музей:** Museum of Modern Art (MoMA), Нью-Йорк
- **Источник:** Wikimedia Commons, Google Art Project
- **URL страницы:** https://commons.wikimedia.org/wiki/File:Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg
- **Прямая ссылка:** https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg
- **Лицензия:** общественное достояние (public domain). Ван Гог умер в 1890 году, авторские права
  истекли не позднее чем через 70 лет после смерти (с 1961 года); фотография картины Google Art
  Project также распространяется как свободная.

## Почему выбран этот референс

Стиль «Звёздной ночи» предельно узнаваем и одновременно сложен для имитации: закрученные
спиральные мазки, плотное импасто, доминирующая кобальтово-синяя палитра с кадмиево-жёлтыми
акцентами, светящиеся луна и звёзды, силуэт кипариса на переднем плане. Это позволяет наглядно
проверить, насколько подробный промпт, составленный после анализа референса, воспроизводит стиль
лучше, чем короткий «наивный» промпт.
""",
    encoding="utf-8",
)
(LOGS / "preflight.json").write_text(json.dumps({
    "reference_bytes": raw.stat().st_size,
    "reference_size_1024": list(im.size),
}, ensure_ascii=False, indent=2), encoding="utf-8")
print("logs written")
