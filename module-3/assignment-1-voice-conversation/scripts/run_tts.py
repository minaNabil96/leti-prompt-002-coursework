"""Synthesize six assistant replies with Polza.ai TTS and encode them to MP3.

Model: google/gemini-3.8-flash-lite-tts (text->speech)
Endpoint: POST https://polza.ai/api/v1/audio/speech
The API returns base64 WAV in JSON, so the audio is decoded and re-encoded to
MP3 with lameenc (no external ffmpeg available in this environment).
"""
import base64
import json
import pathlib
import re
import sys
import time

import lameenc
import miniaudio
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
AUDIO = ROOT / "audio"
RAW = pathlib.Path(r"C:\Temp\opencode\vc_wav")
RAW.mkdir(parents=True, exist_ok=True)

KEY = (ROOT / ".polza_key").read_text(encoding="utf-8").strip()
MODEL = "google/gemini-3.8-flash-lite-tts"
VOICE = "Kore"
TURNS = [1, 3, 6, 7, 9, 11]
URL = "https://polza.ai/api/v1/audio/speech"

# The model truncated one word in turn 1 ("планиру" instead of "планируете");
# the typo is quoted in the report and corrected only for the synthesis input.
FIXES = {"планиру провести": "планируете провести"}


def to_speech(text: str) -> str:
    """Turn the markdown reply into plain text suitable for TTS."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^\d+\.\s+", "", line)      # numbered list marker
        line = re.sub(r"^[*-]\s+", "", line)       # bullet marker
        line = line.strip()
        if not line:
            continue
        if line[-1] not in ".!?…:;":
            line += "."
        out.append(line)
    speech = " ".join(out)
    for bad, good in FIXES.items():
        speech = speech.replace(bad, good)
    speech = re.sub(r"\s+", " ", speech).strip()
    return speech


def encode_mp3(wav_path: pathlib.Path, mp3_path: pathlib.Path) -> dict:
    # Keep the native provider format (24 kHz mono); no resampling.
    decoded = miniaudio.decode_file(
        str(wav_path), output_format=miniaudio.SampleFormat.SIGNED16,
        nchannels=1, sample_rate=24000)
    pcm = decoded.samples.tobytes()
    enc = lameenc.Encoder()
    enc.set_bit_rate(64)
    enc.set_in_sample_rate(decoded.sample_rate)
    enc.set_channels(decoded.nchannels)
    enc.set_quality(2)
    data = enc.encode(pcm) + enc.flush()
    mp3_path.write_bytes(data)
    return {
        "sample_rate": decoded.sample_rate,
        "channels": decoded.nchannels,
        "frames": decoded.num_frames,
        "duration_decoded_s": round(decoded.num_frames / decoded.sample_rate, 3),
        "mp3_bytes": len(data),
    }


def main():
    conv = json.loads((LOGS / "conversation.json").read_text(encoding="utf-8"))
    by_turn = {t["turn"]: t for t in conv["turns"]}
    results = []
    total_cost = 0.0

    for n, turn in enumerate(TURNS, 1):
        raw_text = by_turn[turn]["assistant"]
        speech = to_speech(raw_text)
        t0 = time.time()
        r = requests.post(
            URL,
            headers={"Authorization": f"Bearer {KEY}",
                     "Content-Type": "application/json"},
            json={"model": MODEL, "input": speech, "voice": VOICE,
                  "response_format": "wav"},
            timeout=300,
        )
        dt = time.time() - t0
        r.raise_for_status()
        payload = r.json()

        audio = base64.b64decode(payload["audio"])
        wav_path = RAW / f"response_{n:02d}.wav"
        wav_path.write_bytes(audio)
        mp3_name = f"response_{n:02d}.mp3"
        info = encode_mp3(wav_path, AUDIO / mp3_name)

        usage = payload.get("usage") or {}
        cost = float(usage.get("cost_rub") or 0.0)
        total_cost += cost
        rec = {
            "file": f"audio/{mp3_name}",
            "turn": turn,
            "voice": VOICE,
            "model": payload.get("model", MODEL),
            "content_type": payload.get("contentType"),
            "chars": len(speech),
            "api_duration_s": payload.get("duration"),
            "api_duration_note": "duration reported by the provider; includes"
                                 " leading and trailing silence",
            "request_seconds": round(dt, 2),
            "wav_bytes": len(audio),
            "bitrate_kbps": 64,
            "cost_rub": round(cost, 6),
            "usage": usage,
            "source_text": raw_text,
            "speech_text": speech,
            "text_changed": speech.strip() != raw_text.strip(),
            **info,
        }
        results.append(rec)
        print(f"[{n}/6] turn {turn:2d} {len(speech):4d} chars "
              f"{info['duration_decoded_s']:5.2f}s {info['mp3_bytes']/1024:6.1f} KB "
              f"{cost:.4f} RUB in {dt:.1f}s")

    out = {
        "model": MODEL,
        "voice": VOICE,
        "endpoint": URL,
        "requested_format": "wav",
        "provider_content_type": "audio/wav",
        "delivered_format": "mp3 (64 kbps mono 24 kHz, encoded locally with lameenc)",
        "sample_rate": results[0]["sample_rate"],
        "channels": results[0]["channels"],
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "files": results,
        "totals": {
            "files": len(results),
            "chars": sum(x["chars"] for x in results),
            "duration_s": round(sum(x["duration_decoded_s"] for x in results), 3),
            "cost_rub": round(total_cost, 6),
        },
    }
    (LOGS / "tts_results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("total:", out["totals"])


def reencode_from_cache():
    """Re-encode the cached provider WAVs without new API calls."""
    path = LOGS / "tts_results.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for n, rec in enumerate(data["files"], 1):
        wav = RAW / f"response_{n:02d}.wav"
        info = encode_mp3(wav, AUDIO / f"response_{n:02d}.mp3")
        rec.update(info)
        rec["bitrate_kbps"] = 64
        print(f"[{n}/6] {rec['file']}: {info['duration_decoded_s']:.2f}s "
              f"{info['mp3_bytes']/1024:.1f} KB")
    data["delivered_format"] = ("mp3 (64 kbps mono 24 kHz, encoded locally"
                                " with lameenc)")
    data["files"] = data["files"]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8")
    print("updated", path)


if __name__ == "__main__":
    if "--reencode" in sys.argv:
        reencode_from_cache()
    else:
        sys.exit(main())
