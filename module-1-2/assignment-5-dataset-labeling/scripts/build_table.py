"""Build ground-truth labels JSON and the XLSX labeling table (with images)."""
import json
import pathlib
import tempfile

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.table import Table, TableStyleInfo
from PIL import Image as PILImage

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"
IMAGES = ROOT / "images"
XLSX = ROOT / "разметка.xlsx"

# Doubt comments for intentionally ambiguous images (actual IDs by content)
COMMENTS = {
    "P04": "Афиша лекции с крупным портретом — может напоминать обложку книги",
    "P11": "Портрет + крупный шрифт — может напоминать постер фильма",
    "P13": "Тёмная атмосферная иллюстрация — визуально близко к постеру фильма",
    "P20": "Реалистичное изображение + лауреаты фестиваля — может напоминать афишу",
}

THUMB = (96, 128)      # preview column
GALLERY = (168, 224)   # gallery sheet


def make_thumb(src: pathlib.Path, dst: pathlib.Path, box):
    im = PILImage.open(src).convert("RGB")
    im.thumbnail(box, PILImage.LANCZOS)
    canvas = PILImage.new("RGB", box, (255, 255, 255))
    canvas.paste(im, ((box[0] - im.width) // 2, (box[1] - im.height) // 2))
    canvas.save(dst, "JPEG", quality=86)
    return box


def main():
    labels = []
    for i in range(1, 25):
        rec = json.loads((LOGS / "gen" / f"gen_{i:02d}.json").read_text(encoding="utf-8"))
        labels.append({
            "id": rec["id"],
            "file": rec["file"],
            "class": rec["class"],
            "prompt": rec["prompt"],
            "source": "Сгенерировано через Polza.ai (tongyi-mai/z-image)",
            "license": "Собственное (сгенерировано ИИ, права использования по условиям Polza.ai)",
            "annotator": "Ханна М. Н.",
            "comment": COMMENTS.get(rec["id"], ""),
        })
    (LOGS / "labels_ground_truth.json").write_text(
        json.dumps(labels, ensure_ascii=False, indent=2), encoding="utf-8")

    header_font = Font(name="Times New Roman", size=12, bold=True)
    header_fill = PatternFill("solid", start_color="F2F2F2")
    body_font = Font(name="Times New Roman", size=12)
    thin = Side(style="thin", color="000000")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    with tempfile.TemporaryDirectory(prefix="a5thumbs_") as td:
        td = pathlib.Path(td)
        thumbs = {}
        for item in labels:
            dst = td / f"{item['id']}.jpg"
            make_thumb(IMAGES / item["file"], dst, THUMB)
            thumbs[item["id"]] = dst

        wb = Workbook()
        ws = wb.active
        ws.title = "Разметка"
        headers = ["ID", "Превью", "Файл", "Класс", "Источник",
                   "Лицензия", "Разметчик", "Комментарий о сомнениях"]

        for col, h in enumerate(headers, 1):
            c = ws.cell(row=1, column=col, value=h)
            c.font = header_font
            c.fill = header_fill
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            c.border = border

        for r, item in enumerate(labels, 2):
            row = [item["id"], None, item["file"], item["class"], item["source"],
                   item["license"], item["annotator"], item["comment"]]
            for col, val in enumerate(row, 1):
                c = ws.cell(row=r, column=col, value=val)
                c.font = body_font
                c.alignment = Alignment(
                    vertical="center" if col == 2 else "top", wrap_text=True)
                c.border = border
            ws.row_dimensions[r].height = 100
            img = XLImage(str(thumbs[item["id"]]))
            img.width, img.height = THUMB
            ws.add_image(img, f"B{r}")

        for col, width in zip("ABCDEFGH", [8, 15, 14, 18, 34, 32, 16, 42]):
            ws.column_dimensions[col].width = width
        ws.row_dimensions[1].height = 32
        ws.freeze_panes = "C2"

        ref = f"A1:H{len(labels) + 1}"
        tab = Table(displayName="Razmetka", ref=ref)
        tab.tableStyleInfo = TableStyleInfo(name="TableGrid", showRowStripes=False)
        ws.add_table(tab)

        # ---- gallery sheet with larger previews
        ws3 = wb.create_sheet("Превью")
        for col, width in zip("ABCD", [24, 26, 24, 26]):
            ws3.column_dimensions[col].width = width
        for j, item in enumerate(labels):
            side = j % 2
            band = j // 2
            row = 1 + band * 2
            label_col = "A" if side == 0 else "C"
            image_col = "B" if side == 0 else "D"
            c = ws3.cell(row=row, column=1 if side == 0 else 3,
                         value=f"{item['id']} — {item['class']}\n{item['file']}")
            c.font = Font(name="Times New Roman", size=12, bold=True)
            c.alignment = Alignment(vertical="center", wrap_text=True)
            dst = td / f"{item['id']}_big.jpg"
            make_thumb(IMAGES / item["file"], dst, GALLERY)
            img = XLImage(str(dst))
            img.width, img.height = GALLERY
            ws3.add_image(img, f"{image_col}{row}")
            ws3.row_dimensions[row].height = 175

        # ---- instruction sheet
        ws2 = wb.create_sheet("Инструкция")
        text = (LOGS / "instruction.md").read_text(encoding="utf-8")
        ws2.column_dimensions["A"].width = 120
        for r, line in enumerate(text.splitlines(), 1):
            c = ws2.cell(row=r, column=1, value=line)
            c.font = Font(name="Times New Roman", size=12, bold=line.startswith("**Правило"))
            c.alignment = Alignment(wrap_text=True, vertical="top")

        wb.save(XLSX)

    print("saved", XLSX, "rows:", len(labels))
    print("sheets:", wb.sheetnames)
    print("classes:", {c: sum(1 for x in labels if x["class"] == c)
                       for c in ("афиша", "обложка книги", "постер фильма")})


if __name__ == "__main__":
    main()
