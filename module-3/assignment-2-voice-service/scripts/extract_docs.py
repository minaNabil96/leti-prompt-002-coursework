"""Strip the archived ElevenLabs pages to plain text for fact extraction."""
import pathlib
import re

from bs4 import BeautifulSoup

LOGS = pathlib.Path(__file__).resolve().parents[1] / "logs"
TEXT = LOGS / "text"
TEXT.mkdir(exist_ok=True)

for src in sorted(LOGS.glob("elevenlabs_*.html")):
    html = src.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"web\.archive\.org/web/(\d{14})", html)
    stamp = m.group(1) if m else "?"
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    text = soup.get_text("\n")
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    out = TEXT / (src.stem + ".txt")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"{src.name:38s} snapshot={stamp} lines={len(lines):5d} chars={len(text):7d}")
