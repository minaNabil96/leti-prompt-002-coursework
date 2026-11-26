import pathlib
from PIL import Image

root = pathlib.Path(__file__).resolve().parents[1]
out = root / "logs" / "inspect"
out.mkdir(exist_ok=True)
for p in sorted((root / "screenshots").glob("img_only_*.png")):
    im = Image.open(p).convert("RGB")
    w, h = im.size
    band = im.crop((0, int(h * 0.42), w, int(h * 0.80)))
    band = band.resize((1600, int(band.height * 1600 / band.width)), Image.LANCZOS)
    band.save(out / f"{p.stem}_band.png")
    print(p.stem, im.size, "->", band.size)
