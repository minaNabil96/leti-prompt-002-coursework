"""Measure the prosody of the synthesized replies: pauses, tempo, pitch, level.

Pitch and HNR are measured with Praat (parselmouth, cross-correlation method),
pauses and the amplitude envelope with a simple RMS gate.
"""
import json
import math
import pathlib
import re

import librosa
import miniaudio
import numpy as np
import parselmouth

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
SR = 24000
WIN = 480          # 20 ms analysis window
HOP = 240          # 10 ms hop
VOWELS = set("аеёиоуыэюя")


def load(path: pathlib.Path) -> np.ndarray:
    # miniaudio cannot open this Cyrillic path by name, so pass the bytes.
    d = miniaudio.decode(path.read_bytes(),
                         output_format=miniaudio.SampleFormat.SIGNED16,
                         nchannels=1, sample_rate=SR)
    return np.frombuffer(d.samples.tobytes(), dtype=np.int16).astype(np.float32) / 32768.0


def rms_frames(x: np.ndarray) -> np.ndarray:
    n = 1 + max(0, (len(x) - WIN) // HOP)
    idx = np.arange(WIN)[None, :] + HOP * np.arange(n)[:, None]
    return np.sqrt((x[idx] ** 2).mean(axis=1))


def analyze(rec: dict) -> dict:
    x = load(ROOT / rec["file"])
    dur = len(x) / SR
    rms = rms_frames(x)
    noise = float(np.percentile(rms, 10))
    loud = float(np.percentile(rms, 90))
    thr = noise + 0.10 * (loud - noise)
    voiced = rms > thr

    segs, start = [], None
    for i, v in enumerate(voiced):
        if v and start is None:
            start = i
        elif not v and start is not None:
            segs.append((start, i))
            start = None
    if start is not None:
        segs.append((start, len(voiced)))
    merged = []
    for s in segs:
        if merged and (s[0] - merged[-1][1]) * HOP / SR < 0.12:
            merged[-1] = (merged[-1][0], s[1])
        else:
            merged.append(s)
    segs = [s for s in merged if (s[1] - s[0]) * HOP / SR >= 0.10]

    pauses, pause_spans = [], []
    for a, b in zip(segs, segs[1:]):
        gap = (b[0] - a[1]) * HOP / SR
        if gap >= 0.20:
            pauses.append(round(gap, 3))
            pause_spans.append([round(a[1] * HOP / SR, 2),
                                round(b[0] * HOP / SR, 2)])

    speech = sum((b - a) * HOP / SR for a, b in segs)
    lead = segs[0][0] * HOP / SR if segs else dur
    tail = dur - segs[-1][1] * HOP / SR if segs else 0

    text = rec["speech_text"]
    words = re.findall(r"[А-Яа-яЁёA-Za-z]+(?:-[А-Яа-яЁёA-Za-z]+)*", text)
    syll = sum(sum(1 for ch in w.lower() if ch in VOWELS) for w in words)

    # Pitch: librosa pYIN (robust to octave errors); HNR: Praat.
    snd = parselmouth.Sound(x.astype(np.float64), sampling_frequency=SR)
    f0_raw, _, _ = librosa.pyin(
        x, fmin=75, fmax=320, sr=SR, frame_length=1024, hop_length=HOP,
        fill_na=np.nan, center=True)
    ft = librosa.times_like(f0_raw, sr=SR, hop_length=HOP)
    hnr = snd.to_harmonicity_cc(minimum_pitch=70, time_step=0.01)
    hv = hnr.values.ravel()
    m = ~np.isnan(f0_raw)
    n = min(len(hv), len(m))
    hnr_voiced = hv[:n][m[:n]]
    hnr_voiced = hnr_voiced[hnr_voiced > -200]

    f0 = f0_raw[m]
    st = 12 * np.log2(f0 / np.median(f0))

    contour = []
    nb = 600
    for b in range(nb):
        t0, t1 = b * dur / nb, (b + 1) * dur / nb
        sel = f0_raw[(ft >= t0) & (ft < t1)]
        sel = sel[~np.isnan(sel)]
        contour.append(round(float(np.median(sel)), 1) if len(sel) else None)
    # median smoother over three bins removes isolated outliers on the plot
    smooth = []
    for i, v in enumerate(contour):
        w = [contour[j] for j in range(max(0, i - 1), min(len(contour), i + 2))
             if contour[j] is not None]
        smooth.append(round(float(np.median(w)), 1) if w else None)
    contour = smooth

    peak = float(np.max(np.abs(x)))
    clip = int(np.sum(np.abs(x) >= 0.999))

    return {
        "file": rec["file"],
        "turn": rec["turn"],
        "duration_s": round(dur, 2),
        "speech_s": round(speech, 2),
        "speech_ratio": round(speech / dur, 3),
        "lead_silence_s": round(lead, 2),
        "tail_silence_s": round(tail, 2),
        "pauses": pauses,
        "pause_spans": pause_spans,
        "pause_count": len(pauses),
        "pause_total_s": round(sum(pauses), 1),
        "pause_mean_s": round(sum(pauses) / len(pauses), 2) if pauses else 0,
        "pause_max_s": max(pauses) if pauses else 0,
        "pauses_per_min": round(len(pauses) / (dur / 60), 1),
        "words": len(words),
        "syllables": syll,
        "wpm": round(len(words) / (speech / 60), 1),
        "syll_per_s": round(syll / speech, 2),
        "f0_median_hz": round(float(np.median(f0)), 1),
        "f0_p10_hz": round(float(np.percentile(f0, 10)), 1),
        "f0_p90_hz": round(float(np.percentile(f0, 90)), 1),
        "f0_span_semitones": round(float(np.percentile(st, 90)
                                         - np.percentile(st, 10)), 2),
        "f0_std_semitones": round(float(np.std(st)), 2),
        "hnr_voiced_db": round(float(np.mean(hnr_voiced)), 1),
        "voiced_frames": int(m.sum()),
        "peak_dbfs": round(20 * math.log10(peak), 2),
        "clipped_samples": clip,
        "dc_offset": round(float(np.mean(x)), 5),
        "envelope": [round(float(v), 4) for v in
                     rms[np.linspace(0, len(rms) - 1, 600).astype(int)]],
        "envelope_dt_s": round(dur / 600, 3),
        "f0_contour": contour,
    }


def main():
    data = json.loads((LOGS / "tts_results.json").read_text(encoding="utf-8"))
    rows = [analyze(r) for r in data["files"]]
    overall = {
        "method": {
            "sample_rate_hz": SR,
            "pause_threshold_s": 0.20,
            "voicing_gate": "RMS > 10-й процентиль + 10% размаха",
            "pitch": "librosa pYIN, 75-320 Гц, кадр 1024, шаг 240 (10 мс)",
            "hnr": "Praat to_harmonicity_cc, минимум 70 Гц",
        },
        "by_file": rows,
        "totals": {
            "files": len(rows),
            "duration_s": round(sum(r["duration_s"] for r in rows), 2),
            "speech_s": round(sum(r["speech_s"] for r in rows), 2),
            "pause_count": sum(r["pause_count"] for r in rows),
            "pause_total_s": round(sum(r["pause_total_s"] for r in rows), 1),
            "words": sum(r["words"] for r in rows),
            "syllables": sum(r["syllables"] for r in rows),
            "wpm": round(sum(r["words"] for r in rows)
                         / (sum(r["speech_s"] for r in rows) / 60), 1),
            "syll_per_s": round(sum(r["syllables"] for r in rows)
                                / sum(r["speech_s"] for r in rows), 2),
            "pause_mean_s": round(sum(r["pause_total_s"] for r in rows)
                                  / sum(r["pause_count"] for r in rows), 2),
            "f0_median_hz": round(float(np.median([r["f0_median_hz"] for r in rows])), 1),
        },
    }
    (LOGS / "prosody.json").write_text(
        json.dumps(overall, ensure_ascii=False, indent=2), encoding="utf-8")

    hdr = ("file", "dur", "speech", "ratio", "pauses", "p/min", "mean", "max",
           "wpm", "syl/s", "f0med", "span", "hnr", "peak")
    print(("%-16s" + "%7s" * 13) % hdr)
    for r in rows:
        print(("%-16s%7.1f%7.1f%7.2f%7d%7.1f%7.2f%7.2f%7.0f%7.2f%7.1f%7.1f%7.1f%7.1f") % (
            pathlib.Path(r["file"]).name, r["duration_s"], r["speech_s"],
            r["speech_ratio"], r["pause_count"], r["pauses_per_min"],
            r["pause_mean_s"], r["pause_max_s"], r["wpm"], r["syll_per_s"],
            r["f0_median_hz"], r["f0_span_semitones"], r["hnr_voiced_db"],
            r["peak_dbfs"]))
    print("totals:", json.dumps(overall["totals"], ensure_ascii=False))
    print("lead/tail:", [(r["turn"], r["lead_silence_s"], r["tail_silence_s"]) for r in rows])
    print("clipped:", [(r["turn"], r["clipped_samples"]) for r in rows])


if __name__ == "__main__":
    main()
