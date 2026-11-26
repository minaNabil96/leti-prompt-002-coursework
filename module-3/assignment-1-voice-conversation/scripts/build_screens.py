"""Render the three report figures from the real session logs.

The figures are HTML views (chat window, settings panel, TTS analysis) built
from logs/conversation.json, logs/tts_results.json and logs/prosody.json, then
screenshotted with headless Chrome and trimmed to content.
"""
import html
import json
import pathlib
import re
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
SHOTS = ROOT / "screenshots"
TMP = pathlib.Path(r"C:\Temp\opencode\vc_screens")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

CONV = json.loads((LOGS / "conversation.json").read_text(encoding="utf-8"))
TTS = json.loads((LOGS / "tts_results.json").read_text(encoding="utf-8"))
PROS = json.loads((LOGS / "prosody.json").read_text(encoding="utf-8"))
STT = json.loads((LOGS / "stt_check.json").read_text(encoding="utf-8"))

CSS = """
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #eef1f6; }
body { font-family: "Segoe UI", Tahoma, sans-serif; color: #1d2433; }
.win { margin: 0; background: #ffffff; border-bottom: 1px solid #d7dce5; }
.bar { min-height: 54px; background: #f7f9fc; border-bottom: 1px solid #e3e8f0;
       color: #2a3346; display: flex; align-items: center; padding: 12px 22px;
       font-size: 18px; }
.t { font-weight: 600; letter-spacing: .2px; }
.r { margin-left: auto; color: #7c879c; font-size: 16px; }
.body { display: flex; }
.side { width: 348px; background: #f7f9fc; border-right: 1px solid #e3e8f0;
        padding: 20px 0 16px; }
.side h3 { margin: 0 20px 12px; font-size: 14px; letter-spacing: 1.2px;
           text-transform: uppercase; color: #7c879c; font-weight: 700; }
.item { padding: 9px 20px; border-left: 4px solid transparent; }
.item.on { background: #e8effc; border-left-color: #2d6cdf; }
.item .n { font-size: 13px; color: #8a94a8; }
.item .p { font-size: 16px; color: #2a3346; margin-top: 2px;
           white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.side .foot { margin: 18px 20px 0; padding-top: 14px; border-top: 1px solid #e3e8f0;
              font-size: 13px; color: #6e7a90; line-height: 1.65; }
.side .foot b { color: #2a3346; font-weight: 600; }
.main { flex: 1; padding: 24px 30px 30px; }
.topic { font-size: 24px; font-weight: 700; }
.sub { font-size: 15px; color: #7c879c; margin-top: 4px; }
.msg { display: flex; margin-top: 14px; }
.msg.u { justify-content: flex-end; }
.bub { max-width: 78%; border-radius: 16px; padding: 11px 16px; font-size: 18px;
       line-height: 1.38; }
.u .bub { background: #2d6cdf; color: #ffffff; border-bottom-right-radius: 5px; }
.a .bub { background: #f3f5fa; border: 1px solid #e3e8f0; border-bottom-left-radius: 5px; }
.who { font-size: 14px; color: #8a94a8; margin-bottom: 5px; }
.txt { white-space: pre-wrap; }
.chip { display: inline-flex; align-items: center; gap: 10px; margin-top: 10px;
        padding: 7px 12px; background: #ffffff; border: 1px solid #dfe5ef;
        border-radius: 10px; font-size: 14px; color: #55617a; }
.chip svg { display: block; }
.chip b { color: #2d6cdf; font-weight: 600; }
.gap { margin: 18px 0 0; padding: 9px 16px; background: #fbfcfe; border: 1px dashed #cfd7e4;
       border-radius: 10px; color: #8590a5; font-size: 14px; text-align: center; }
.hdr { display: flex; align-items: center; gap: 14px; }
.badge { font-size: 13px; background: #e8effc; color: #2d6cdf; border-radius: 20px;
         padding: 3px 10px; font-weight: 600; }
"""


def ru(v, d=2):
    return f"{v:.{d}f}".replace(".", ",")


def sp(v):
    return f"{int(v):,}".replace(",", " ")


def esc(t):
    t = html.escape(t)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


def hhmm(ts):
    return ts[11:16]


def wave_svg(env, width=132, height=30, color="#2d6cdf"):
    if not env:
        return ""
    n = 54
    idx = np.linspace(0, len(env) - 1, n).astype(int)
    v = np.array(env)[idx]
    v = v / (v.max() or 1)
    step = width / n
    bars = []
    for i, a in enumerate(v):
        h = max(1.5, a * height)
        x = i * step + 0.6
        bars.append(f'<rect x="{x:.1f}" y="{(height-h)/2:.1f}" width="{step*0.55:.1f}" '
                    f'height="{h:.1f}" rx="1" fill="{color}" opacity="0.85"/>')
    return (f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
            + "".join(bars) + "</svg>")


TTS_BY_TURN = {f["turn"]: f for f in TTS["files"]}
PROS_BY_TURN = {r["turn"]: r for r in PROS["by_file"]}


def screen_chat():
    turns = CONV["turns"]
    items = []
    for t in turns:
        on = " on" if t["turn"] == 1 else ""
        prev = t["user"].replace("\n", " ")
        prev = prev[:34] + ("…" if len(prev) > 34 else "")
        items.append(
            f'<div class="item{on}"><div class="n">{t["turn"]:02d} · {hhmm(t["timestamp"])}'
            f' · {t["completion_tokens"]} ток.</div>'
            f'<div class="p">{esc(prev)}</div></div>')
    sidebar = "".join(items)

    def msg_user(t):
        return (f'<div class="msg u"><div><div class="who" style="text-align:right">'
                f'Вы · {hhmm(t["timestamp"])}</div>'
                f'<div class="bub"><div class="txt">{esc(t["user"])}</div></div></div></div>')

    def msg_assistant(t, limit=None):
        audio = ""
        text = t["assistant"]
        cut = False
        if limit and len(text) > limit:
            text = text[:limit].rsplit(" ", 1)[0] + " …"
            cut = True
        if t["turn"] in TTS_BY_TURN:
            a = TTS_BY_TURN[t["turn"]]
            pr = PROS_BY_TURN[t["turn"]]
            audio = (f'<div class="chip">{wave_svg(pr["envelope"])}'
                     f'<span>🔊 Озвучено · <b>{a["duration_decoded_s"]:.1f} с</b> · '
                     f'{a["cost_rub"]:.2f} ₽ · voice Kore</span></div>')
        note = ('<div class="chip" style="color:#8590a5">текст сокращён для рисунка · '
                'полностью — Приложение А</div>' if cut else '')
        return (f'<div class="msg a"><div><div class="who">{hhmm(t["timestamp"])} · '
                f'ассистент</div><div class="bub"><div class="txt">{esc(text)}</div>'
                f'{audio}{note}</div></div></div>')

    by = {t["turn"]: t for t in turns}
    body = [msg_user(by[1]), msg_assistant(by[1]),
            '<div class="gap">Реплики 2–6 свёрнуты: музеи, билеты, рестораны, '
            'транспорт, часы работы Кремля</div>',
            msg_user(by[7]), msg_assistant(by[7]),
            '<div class="gap">Реплика 8 свёрнута: уточнение про дождь в Петербурге</div>',
            msg_user(by[9]), msg_assistant(by[9], limit=430),
            '<div class="gap">Реплики 10–12 свёрнуты: выбор отеля, стоимость номера, '
            'благодарность</div>']

    tot = CONV["totals"]
    return f"""<!doctype html><meta charset="utf-8"><style>{CSS}</style>
<div class="win">
  <div class="bar">
    <div class="t">Протокол беседы · logs/conversation.json</div>
    <div class="r">25.11.2026 · 18:23–18:24 MSK · 12 реплик</div>
  </div>
  <div class="body">
    <div class="side">
      <h3>Диалог · 12 реплик</h3>
      {sidebar}
      <div class="foot">
        <b>LLM:</b> google/gemini-2.5-flash<br>
        <b>TTS:</b> gemini-3.8-flash-lite-tts, Kore<br>
        <b>Токены:</b> {tot["prompt_tokens"]:,} → {tot["completion_tokens"]:,}<br>
        <b>Стоимость:</b> {tot["cost_rub"]:.2f} ₽
      </div>
    </div>
    <div class="main">
      <div class="hdr"><div class="topic">Планирование поездки в Казань</div>
        <div class="badge">голосовой режим</div></div>
      <div class="sub">тема удерживается через смену контекста (реплика 7) и возврат (реплика 9)</div>
      {''.join(body)}
    </div>
  </div>
</div>
<div style="height:2px;background:#ff00ff"></div>"""



def screen_analysis():
    # duration bars
    mx = max(f["duration_decoded_s"] for f in TTS["files"])
    bars = []
    for f in TTS["files"]:
        w = f["duration_decoded_s"] / mx * 100
        bars.append(
            f'<div class="brow"><div class="bl">{f["file"].split("/")[-1][-6:-4]} · '
            f'реплика {f["turn"]}</div>'
            f'<div class="btrack"><div class="bfill" style="width:{w:.1f}%"></div></div>'
            f'<div class="bv">{ru(f["duration_decoded_s"], 1)} с · {ru(f["cost_rub"])} ₽</div></div>')

    r = PROS_BY_TURN[6]
    W, H = 1150, 240
    env = np.array(r["envelope"])
    env = env / (env.max() or 1)
    n = len(env)
    mid = H / 2
    step = W / n
    poly_top = " ".join(f"{i*step:.1f},{mid - a*(H/2-12):.1f}" for i, a in enumerate(env))
    poly_bot = " ".join(f"{i*step:.1f},{mid + a*(H/2-12):.1f}"
                        for i, a in reversed(list(enumerate(env))))
    color = "#2d6cdf"
    shades = []
    for a, b in r["pause_spans"]:
        x1, x2 = a / r["duration_s"] * W, b / r["duration_s"] * W
        shades.append(f'<rect x="{x1:.1f}" y="0" width="{max(1.5, x2-x1):.1f}" '
                      f'height="{H}" fill="#ffb020" opacity="0.13"/>')

    # f0 contour: 1-second medians (raw 0.13 s bins are too noisy to plot)
    fc = r["f0_contour"]
    dur = r["duration_s"]
    nb = int(round(dur))
    coarse = []
    for b in range(nb):
        t0, t1 = b, b + 1
        vals = [fc[i] for i in range(len(fc))
                if fc[i] is not None and t0 <= i / len(fc) * dur < t1]
        coarse.append(float(np.median(vals)) if vals else None)
    lo, hi = 100, 320
    segs, cur = [], []
    for i, v in enumerate(coarse):
        x = (i + 0.5) / nb * W
        if v is None:
            if len(cur) > 1:
                segs.append(cur)
            cur = []
        else:
            y = H - (v - lo) / (hi - lo) * H
            y = min(H - 4, max(4, y))
            cur.append((x, y))
    if len(cur) > 1:
        segs.append(cur)
    f0_paths = []
    for s in segs:
        d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in s)
        f0_paths.append(f'<path d="{d}" fill="none" stroke="#d9480f" stroke-width="2.2" '
                        f'opacity="0.85"/>')

    ticks = "".join(
        f'<div class="tick" style="left:{t/r["duration_s"]*100:.1f}%">{t:.0f} с</div>'
        for t in (0, 15, 30, 45, 60, 75))

    files = []
    for x in PROS["by_file"]:
        files.append(
            f'<tr><td>{x["file"].split("/")[-1]}</td><td class="c">{x["turn"]}</td>'
            f'<td class="c">{ru(x["duration_s"], 1)}</td><td class="c">{x["pause_count"]}</td>'
            f'<td class="c">{x["pauses_per_min"]:.0f}</td><td class="c">{ru(x["pause_mean_s"])}</td>'
            f'<td class="c">{ru(x["pause_max_s"])}</td><td class="c">{x["wpm"]:.0f}</td>'
            f'<td class="c">{x["f0_median_hz"]:.0f}</td>'
            f'<td class="c">{ru(x["f0_span_semitones"], 1)}</td>'
            f'<td class="c">{ru(x["hnr_voiced_db"], 1)}</td></tr>')

    t = PROS["totals"]
    return f"""<!doctype html><meta charset="utf-8"><style>{CSS}
.wrap {{ padding: 26px 30px 34px; background:#eef1f6; }}
h1 {{ font-size: 25px; margin: 0 0 3px; }}
.lead {{ color: #7c879c; font-size: 15px; margin-bottom: 18px; }}
.card {{ background:#fff; border:1px solid #dde3ee; border-radius:14px; padding:18px 22px; margin-bottom:16px; }}
.card h2 {{ font-size:16px; margin:0 0 12px; color:#2a3346; }}
.brow {{ display:grid; grid-template-columns: 150px 1fr 165px; align-items:center; gap:12px; padding:4px 0; }}
.bl {{ font-size:14px; color:#55617a; }}
.btrack {{ height:16px; background:#f0f3f9; border-radius:8px; overflow:hidden; }}
.bfill {{ height:100%; background:linear-gradient(90deg,#2d6cdf,#6aa8ff); }}
.bv {{ font-size:14px; color:#3b465c; text-align:right; }}
.chart {{ position:relative; background:#fbfcfe; border:1px solid #e6ebf4; border-radius:10px; padding:8px 8px 26px; }}
.ticks {{ position:relative; height:0; }}
.tick {{ position:absolute; top:2px; transform:translateX(-50%); font-size:12px; color:#8a94a8; }}
.leg {{ display:flex; gap:22px; font-size:13px; color:#6e7a90; margin-top:10px; }}
.sw {{ display:inline-block; width:22px; height:4px; border-radius:2px; vertical-align:middle; margin-right:7px; }}
table {{ width:100%; border-collapse:collapse; font-size:14.5px; }}
th, td {{ padding:6px 6px; border-bottom:1px solid #eef1f6; text-align:left; }}
th {{ color:#7c879c; font-weight:600; font-size:13px; text-transform:uppercase; letter-spacing:.4px; }}
td.c, th.c {{ text-align:center; }}
.note {{ font-size:13.5px; color:#7c879c; }}
</style>
<div class="wrap">
  <h1>Анализ синтезированной речи</h1>
  <div class="lead">google/gemini-3.8-flash-lite-tts · voice Kore · {t["files"]} файлов, {ru(t["duration_s"], 1)} с, {ru(TTS["totals"]["cost_rub"])} ₽</div>

  <div class="card">
    <h2>Длительность файлов</h2>
    {''.join(bars)}
  </div>

  <div class="card">
    <h2>Реплика 6 (Кремль): амплитуда, паузы и тон</h2>
    <div class="chart">
      <svg width="100%" height="{H}" viewBox="0 0 {W} {H}" preserveAspectRatio="none">
        {''.join(shades)}
        <line x1="0" y1="{mid}" x2="{W}" y2="{mid}" stroke="#dde3ee" stroke-width="1"/>
        <polygon points="{poly_top} {poly_bot}" fill="{color}" opacity="0.20"/>
        <polyline points="{poly_top}" fill="none" stroke="{color}" stroke-width="1.1"/>
        {''.join(f0_paths)}
      </svg>
      <div class="ticks">{ticks}</div>
    </div>
    <div class="leg">
      <span><span class="sw" style="background:#2d6cdf"></span>огибающая RMS</span>
      <span><span class="sw" style="background:#d9480f"></span>тон f0, 100–320 Гц (медиана за 1 с)</span>
      <span><span class="sw" style="background:#ffb020"></span>пауза ≥ 0,20 с</span>
      <span>{r["pause_count"]} пауз · средняя {ru(r["pause_mean_s"])} с · максимум {ru(r["pause_max_s"])} с</span>
    </div>
  </div>

  <div class="card">
    <h2>Метрики по файлам</h2>
    <table>
      <tr><th>Файл</th><th class="c">Реплика</th><th class="c">Длит., с</th><th class="c">Пауз</th>
      <th class="c">Пауз/мин</th><th class="c">Ср. пауза</th><th class="c">Макс. пауза</th>
      <th class="c">Темп, сл/мин</th><th class="c">f0, Гц</th><th class="c">Диапазон, пт</th>
      <th class="c">HNR, дБ</th></tr>
      {''.join(files)}
    </table>
    <div class="note" style="margin-top:10px">Всего {t["words"]} слов, {t["syllables"]} слогов, средний темп {t["wpm"]:.0f} слов/мин;
    диапазон — p10–p90 основного тона; тон — librosa pYIN (75–320 Гц), HNR — Praat (cc) по озвученным кадрам.</div>
  </div>
</div>
<div style="height:2px;background:#ff00ff"></div>"""


def render(name, html_text, width, max_height=4600):
    TMP.mkdir(parents=True, exist_ok=True)
    hp = TMP / f"{name}.html"
    pp = TMP / f"{name}.png"
    hp.write_text(html_text, encoding="utf-8")
    profile = TMP / "profile"
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
           "--force-device-scale-factor=1", "--virtual-time-budget=3000",
           f"--user-data-dir={profile}", f"--window-size={width},{max_height}",
           f"--screenshot={pp}", hp.as_uri()]
    subprocess.run(cmd, check=True, capture_output=True, timeout=180)
    im = Image.open(pp).convert("RGB")
    arr = np.array(im)
    magenta = (arr[:, :, 0] > 240) & (arr[:, :, 1] < 30) & (arr[:, :, 2] > 240)
    rows = np.where(magenta.any(axis=1))[0]
    if len(rows):
        cut = int(rows[0])
        im = im.crop((0, 0, width, min(im.height, cut)))
    out = SHOTS / f"{name}.png"
    im.save(out, optimize=True)
    print(f"{out.name}: {im.width}x{im.height} {out.stat().st_size/1024:.0f} KB")
    return out


def main():
    SHOTS.mkdir(parents=True, exist_ok=True)
    render("01_conversation_screen", screen_chat(), 1400)
    render("03_tts_analysis", screen_analysis(), 1400)


if __name__ == "__main__":
    main()
