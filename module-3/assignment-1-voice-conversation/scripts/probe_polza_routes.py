"""List candidate routes on polza.ai from the model page and probe playground URLs."""
import json
import pathlib
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request

import websocket

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9356
TMP = pathlib.Path(tempfile.mkdtemp(prefix="polza_routes_"))


def http(path, method="GET"):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


class Page:
    def __init__(self, url, w=1440, h=1000):
        t = http("/json/new?" + urllib.parse.quote(url, safe=""), method="PUT")
        self.ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=120,
                                              maxsize=200 * 1024 * 1024)
        self.n = 0
        self.send("Page.enable")
        self.send("Emulation.setDeviceMetricsOverride", width=w, height=h,
                  deviceScaleFactor=1, mobile=False)

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

p = Page("https://polza.ai/models/google/gemini-2.5-flash")
time.sleep(6)
hrefs = p.eval("""JSON.stringify([...new Set([...document.querySelectorAll('a')]
  .map(a => a.getAttribute('href')).filter(Boolean))])""")
print("MODEL PAGE LINKS")
print(hrefs)

for url in ("https://polza.ai/playground", "https://polza.ai/app",
            "https://polza.ai/new", "https://polza.ai/models"):
    try:
        pg = Page(url)
        time.sleep(5)
        print(url, "->", pg.eval("location.href"), "|", (pg.eval("document.title") or ""),
              "|", (pg.eval("document.body.innerText") or "")[:160].replace("\n", " | "))
    except Exception as e:
        print(url, "ERROR", e)
