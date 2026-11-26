from PIL import ImageFont

# 144 px font at 96 dpi = 108 pt; scale to 12 pt by 12/108.
f = ImageFont.truetype(r"C:\Windows\Fonts\times.ttf", 144)
for word in ["Суммаризация", "предложения", "Изображение", "Подтверждено",
             "Трансформер", "мультимодальный", "flow-matching",
             "yandex/YaLM-100B", "(attention)…", "Изображение"]:
    px = f.getlength(word)
    cm = px / 96 * 2.54 * (12 / 108)
    print(f"{word:<18} {cm:.2f} cm")
