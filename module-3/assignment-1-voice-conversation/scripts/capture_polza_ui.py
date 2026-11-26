"""Real captures for the М3-А1 report: model cards of both models used.

Figure 1 (the chat screen) is NOT produced here: it is captured manually from the
live Polza.ai UI in a logged-in browser, after the 12 questions of table 1 are
re-sent there (see logs/generation-method.md). Only genuine screenshots are used.
"""
import base64
import json
import pathlib
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request

import websocket

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9362
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "screenshots"
OUT.mkdir(exist_ok=True)
TMP = pathlib.Path(tempfile.mkdtemp(prefix="polza_ui1_"))

TARGETS = [
    # (name, url, width, height, marker text)
    ("02_settings_chat_model.png",
     "https://polza.ai/models/google/gemini-2.5-flash",
     1440, 1500, "google/gemini-2.5-flash"),
    ("03_settings_tts_model.png",
     "https://polza.ai/models/google/gemini-3.8-flash-lite-tts",
     1440, 1500, "google/gemini-3.8-flash-lite-tts"),
]


def http(path, method="GET"):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


class Page:
    def __init__(self, url, w, h, scale):
        t = http("/json/new?" + urllib.parse.quote(url, safe=""), method="PUT")
        self.ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=240,
                                              maxsize=200 * 1024 * 1024)
        self.n = 0
        self.send("Page.enable")
        self.send("Emulation.setDeviceMetricsOverride", width=w, height=h,
                  deviceScaleFactor=scale, mobile=False)

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

    def wait(self, expr, timeout=120):
        end = time.time() + timeout
        while time.time() < end:
            if self.eval(expr):
                return True
            time.sleep(0.5)
        return False

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

for name, url, w, h, marker in TARGETS:
    p = Page(url, w, h, 1.5)
    p.wait("document.readyState==='complete'", 90)
    ok = p.wait(f"document.body.innerText.includes({json.dumps(marker)})", 120)
    time.sleep(3)
    clicked = p.eval("""(() => {
      const b = [...document.querySelectorAll('button')]
        .find(e => ['Хорошо','Принять','Согласен'].includes(e.textContent.trim()));
      if (b) { b.click(); return b.textContent.trim(); } return false;
    })()""")
    time.sleep(1.5)
    p.eval("window.scrollTo(0, 0)")
    time.sleep(1.5)
    print(name, "marker", ok, "cookie", clicked,
          "scrollY", p.eval("window.scrollY"),
          "h", p.eval("document.body.scrollHeight"))
    p.shot(OUT / name)
    print("  saved", (OUT / name).stat().st_size, "bytes")
