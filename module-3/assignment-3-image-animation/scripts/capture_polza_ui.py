"""Real screenshot of the Polza.ai Seedance 2 Mini model page (settings/parameters)."""
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
PORT = 9350
OUT = pathlib.Path(r".\image-animation\screenshots")
OUT.mkdir(parents=True, exist_ok=True)
TMP = pathlib.Path(tempfile.mkdtemp(prefix="polza_ui_"))
URL = "https://polza.ai/models/bytedance/seedance-2-mini"


def http(path, method="GET"):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


class Page:
    def __init__(self, url, w, h, scale):
        t = http("/json/new?" + urllib.parse.quote(url, safe=""), method="PUT")
        self.ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=180,
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

    def wait(self, expr, timeout=90):
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

p = Page(URL, 1440, 1420, 1.5)
p.wait("document.readyState==='complete'", 60)
p.wait("document.body.innerText.includes('Параметры генерации')", 60)
time.sleep(3)

# dismiss the cookie notice by clicking its button
clicked = p.eval("""(() => {
  const b = [...document.querySelectorAll('button')].find(e => e.textContent.trim() === 'Хорошо');
  if (b) { b.click(); return true; } return false;
})()""")
print("cookie dismissed:", clicked)
time.sleep(1.5)

# scroll so the model card and the parameters table are both in view
p.eval("window.scrollTo(0, 0)")
time.sleep(1.5)
print("scrollY", p.eval("window.scrollY"), "innerText has ID:",
      p.eval("document.body.innerText.includes('bytedance/seedance-2-mini')"))
p.shot(OUT / "03_interface_settings.png")
print("saved", (OUT / "03_interface_settings.png").stat().st_size, "bytes")
