"""Capture the live Polza.ai model cards and crop them to the header + price card."""
import base64
import json
import pathlib
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request

import websocket
from PIL import Image

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9366
ROOT = pathlib.Path(__file__).resolve().parents[1]
SHOTS = ROOT / "screenshots"
TMP = pathlib.Path(tempfile.mkdtemp(prefix="polza_crop2_"))
SCALE = 1.5

TARGETS = [
    ("02_settings_chat_model.png",
     "https://polza.ai/models/google/gemini-2.5-flash"),
    ("03_settings_tts_model.png",
     "https://polza.ai/models/google/gemini-3.8-flash-lite-tts"),
]
MARKER = "Провайдеры для"


def http(path, method="GET"):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


class Page:
    def __init__(self, url, w=1440, h=1500):
        t = http("/json/new?" + urllib.parse.quote(url, safe=""), method="PUT")
        self.ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=240,
                                              maxsize=200 * 1024 * 1024)
        self.n = 0
        self.send("Page.enable")
        self.send("Emulation.setDeviceMetricsOverride", width=w, height=h,
                  deviceScaleFactor=SCALE, mobile=False)

    def send(self, method, **params):
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.n:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})

    def eval(self, expr):
        return self.send("Runtime.evaluate", expression=expr, returnByValue=True) \
            .get("result", {}).get("value")

    def shot(self, path):
        res = self.send("Page.captureScreenshot", format="png")
        pathlib.Path(path).write_bytes(base64.b64decode(res["data"]))


subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                  f"--remote-debugging-port={PORT}", f"--user-data-dir={TMP/'p'}",
                  "--no-first-run", "--no-default-browser-check", "about:blank"],
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(80):
    try:
        http("/json/version")
        break
    except Exception:
        time.sleep(0.5)

EXPR = """(() => {
  const h = [...document.querySelectorAll('h1,h2,h3,h4,div,p')]
    .find(e => e.textContent.trim().startsWith(%s));
  return h ? h.getBoundingClientRect().top + window.scrollY : null;
})()"""

for name, url in TARGETS:
    p = Page(url)
    time.sleep(9)
    y = p.eval(EXPR % json.dumps(MARKER))
    raw = TMP / name
    p.shot(raw)
    im = Image.open(raw)
    cut = int((y - 28) * SCALE) if y else im.height
    cut = max(300, min(cut, im.height))
    im.crop((0, 0, im.width, cut)).save(SHOTS / name)
    print(name, "css_y", round(y or -1), "raw", im.size,
          "->", Image.open(SHOTS / name).size)
