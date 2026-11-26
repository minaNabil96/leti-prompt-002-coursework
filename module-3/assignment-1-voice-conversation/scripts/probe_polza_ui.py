"""Probe Polza.ai pages in headless Chrome to pick real screenshot targets."""
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
PORT = 9354
TMP = pathlib.Path(tempfile.mkdtemp(prefix="polza_probe_"))
URLS = [
    "https://polza.ai/models/google/gemini-2.5-flash",
    "https://polza.ai/models/google/gemini-3.8-flash-lite-tts",
    "https://polza.ai/chat",
    "https://polza.ai/",
]


def http(path, method="GET"):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


class Page:
    def __init__(self, url, w=1440, h=1000, scale=1):
        t = http("/json/new?" + urllib.parse.quote(url, safe=""), method="PUT")
        self.ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=120,
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

for url in URLS:
    try:
        p = Page(url)
        time.sleep(6)
        title = p.eval("document.title")
        text = (p.eval("document.body.innerText") or "")[:600].replace("\n", " | ")
        print("URL", url)
        print("  title:", title)
        print("  url:", p.eval("location.href"))
        print("  text:", text)
        print()
    except Exception as e:
        print("URL", url, "ERROR", e)
