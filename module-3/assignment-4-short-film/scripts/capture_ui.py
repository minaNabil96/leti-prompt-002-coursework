"""Step 7 — real Polza.ai UI screenshots with local Chrome (headless).

The pages are public (model catalogue, model card, API docs), so no account
data is captured. Each URL is rendered by the installed Chrome in a throwaway
profile and saved as PNG; the DOM dump is kept only to prove the page text.
"""
import re
import subprocess
import sys
import pathlib

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE = r"C:\Temp\opencode\chrome_sf"
ROOT = pathlib.Path(__file__).resolve().parents[1]
SHOTS = ROOT / "screenshots"
SHOTS.mkdir(exist_ok=True)
TMP = pathlib.Path(r"C:\Temp\opencode\sf_shot")
TMP.mkdir(parents=True, exist_ok=True)

PAGES = [
    ("01_polza_video_catalog", "https://polza.ai/collections/video", 1440, 1150),
    ("02_polza_model_card_grok", "https://polza.ai/models/grok-imagine-video-1-5", 1440, 1100),
    ("03_polza_music_catalog", "https://polza.ai/collections/music", 1440, 1150),
]


def chrome(args):
    return subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                           f"--user-data-dir={PROFILE}"] + args,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def dump(url, name):
    p = chrome(["--virtual-time-budget=9000", "--dump-dom", url])
    (TMP / f"{name}.html").write_text(p.stdout or "", encoding="utf-8")
    return p.stdout or ""


def text_of(html):
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "shots"
    if mode == "links":
        html = dump("https://polza.ai/models", "models")
        hrefs = sorted(set(re.findall(r'href="(/models[^"]*)"', html)))
        print("\n".join(hrefs[:60]))
        sys.exit()
    for name, url, w, h in PAGES:
        out = SHOTS / f"{name}.png"
        p = chrome([f"--window-size={w},{h}", "--force-device-scale-factor=2",
                    "--virtual-time-budget=10000",
                    f"--screenshot={out}", url])
        ok = out.exists()
        print(f"{name}: {'ok' if ok else 'FAILED'} {out.stat().st_size if ok else 0} B  {url}")
        if not ok:
            print(p.stderr[-500:])
