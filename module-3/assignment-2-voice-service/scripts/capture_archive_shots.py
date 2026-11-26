"""Capture the three report figures as REAL screenshots of archived official pages.

Direct access to elevenlabs.io from Russia is blocked (HTTP redirect to
geo-restriction.elevenlabs.io), so the figures are screenshots of the archived
copies of the official pages served by web.archive.org. Chrome drives the page
through the DevTools Protocol: it loads the snapshot, waits for the archive
toolbar (visible provenance) and for images to finish loading, scrolls to the
relevant section and captures the viewport.

Snapshots (see Table A.1 of the report and logs/worklog.md):
  1) elevenlabs.io                                 25.11.2026  (главная страница)
  2) elevenlabs.io/docs/eleven-creative/playground/text-to-speech
                                                   24.11.2026  (экран настроек)
  3) elevenlabs.io/docs/help-center/other/what-languages-do-you-support
                                                   22.10.2026  (список языков)

Requires: Google Chrome, Python package websocket-client.
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

CHROME = pathlib.Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
ROOT = pathlib.Path(__file__).resolve().parents[1]
SHOTS = ROOT / "screenshots"
PORT = 9338
SCALE = 1.5

HOME = "https://web.archive.org/web/20261125090922"
SETTINGS = "https://web.archive.org/web/20261124121645"
LANGUAGES = "https://web.archive.org/web/20261022183159"

JOBS = [
    # name, url, viewport w, viewport h, scrollY
    ("01_service_interface.png", f"{HOME}/https://elevenlabs.io/", 1440, 900, 100),
    ("02_voice_settings.png",
     f"{SETTINGS}/https://elevenlabs.io/docs/eleven-creative/playground/text-to-speech",
     1440, 1000, 1090),
    ("03_language_selection.png",
     f"{LANGUAGES}/https://elevenlabs.io/docs/help-center/other/what-languages-do-you-support",
     1440, 1300, 3800),
]


def http(path, method="GET"):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


class Page:
    def __init__(self, url, width, height):
        target = http("/json/new?" + urllib.parse.quote(url, safe=""), method="PUT")
        self.ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=180,
                                              maxsize=300 * 1024 * 1024)
        self.n = 0
        self.send("Page.enable")
        self.send("Emulation.setDeviceMetricsOverride", width=width, height=height,
                  deviceScaleFactor=SCALE, mobile=False)

    def send(self, method, **params):
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.n:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})

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

    def screenshot(self, path):
        res = self.send("Page.captureScreenshot", format="png")
        pathlib.Path(path).write_bytes(base64.b64decode(res["data"]))


def main():
    if not CHROME.exists():
        raise SystemExit(f"Chrome not found: {CHROME}")
    SHOTS.mkdir(exist_ok=True)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="el_archive_"))
    subprocess.Popen([str(CHROME), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                      f"--remote-debugging-port={PORT}", f"--user-data-dir={tmp / 'profile'}",
                      "--no-first-run", "--no-default-browser-check",
                      "--autoplay-policy=no-user-gesture-required", "about:blank"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(80):
        try:
            http("/json/version")
            break
        except Exception:
            time.sleep(0.5)
    for name, url, w, h, scroll in JOBS:
        page = Page(url, w, h)
        page.wait("document.readyState==='complete'", 60)
        page.wait("!!document.querySelector('#wm-ipp-base')", 60)   # archive toolbar
        page.wait("Array.from(document.images).every(i=>i.complete)", 60)
        time.sleep(2)
        page.eval(f"window.scrollTo(0,{scroll})")
        time.sleep(3)
        page.screenshot(SHOTS / name)
        print(name, "scrollY", page.eval("window.scrollY"),
              (SHOTS / name).stat().st_size, "bytes")


if __name__ == "__main__":
    main()
