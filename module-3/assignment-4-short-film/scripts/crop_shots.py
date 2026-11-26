"""Crop the UI screenshots to their content and drop the empty white margins.

The captures are real (Chrome, device scale 2); cropping only removes page
margins so the text stays readable in print. Nothing is added or retouched.
"""
import pathlib

from PIL import Image, ImageChops

ROOT = pathlib.Path(__file__).resolve().parents[1]
SHOTS = ROOT / "screenshots"

PAD = 16


def content_box(im):
    bg = Image.new("RGB", im.size, (255, 255, 255))
    diff = ImageChops.difference(im.convert("RGB"), bg)
    bbox = diff.point(lambda v: 255 if v > 12 else 0).getbbox()
    return bbox


for p in sorted(SHOTS.glob("*.png")):
    im = Image.open(p).convert("RGB")
    box = content_box(im)
    if not box:
        print(p.name, "no content found")
        continue
    x0, y0, x1, y1 = box
    x0 = max(0, x0 - PAD)
    y0 = max(0, y0 - PAD)
    x1 = min(im.width, x1 + PAD)
    y1 = min(im.height, y1 + PAD)
    crop = im.crop((x0, y0, x1, y1))
    crop.save(p, optimize=True)
    print(f"{p.name}: {im.width}x{im.height} -> {crop.width}x{crop.height}")
