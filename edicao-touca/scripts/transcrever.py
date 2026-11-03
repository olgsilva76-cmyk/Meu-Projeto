"""Transcreve o vídeo bruto por trechos de fala.

1. Detecta os trechos de fala pela energia do áudio (silencedetect do ffmpeg).
2. Transcreve cada trecho com o Whisper (sherpa-onnx, roda offline).
3. Estima o tempo de cada palavra dentro do trecho, proporcional ao tamanho dela.

Saída: JSON com [{start, end, text, words:[{w, s, e}]}].
Uso: python3 transcrever.py VIDEO MODEL_DIR SAIDA.json
"""
import json
import re
import subprocess
import sys

import numpy as np
import sherpa_onnx

video, model_dir, out = sys.argv[1:4]
SR = 16000

# áudio mono 16 kHz em memória
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
dur = len(audio) / SR

# trechos de silêncio
log = subprocess.run(["ffmpeg", "-hide_banner", "-i", video, "-af", "silencedetect=n=-35dB:d=0.3", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
sil = list(zip(starts, ends + [dur] * (len(starts) - len(ends))))

speech, cur = [], 0.0
for a, b in sil:
    if a - cur > 0.15:
        speech.append([cur, a])
    cur = b
if dur - cur > 0.15:
    speech.append([cur, dur])

# junta trechos muito curtos ao vizinho (Whisper erra em pedaços < 1 s)
merged = []
for s in speech:
    if merged and (s[0] - merged[-1][1] < 0.45 and (s[1] - s[0] < 1.0 or merged[-1][1] - merged[-1][0] < 1.0)):
        merged[-1][1] = s[1]
    else:
        merged.append(s)

rec = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=f"{model_dir}/small-encoder.int8.onnx",
    decoder=f"{model_dir}/small-decoder.int8.onnx",
    tokens=f"{model_dir}/small-tokens.txt",
    language="pt", task="transcribe", num_threads=4)

result = []
for a, b in merged:
    pa, pb = max(0, a - 0.12), min(dur, b + 0.12)
    st = rec.create_stream()
    st.accept_waveform(SR, audio[int(pa * SR):int(pb * SR)])
    rec.decode_stream(st)
    text = st.result.text.strip()
    words = text.split()
    seg = {"start": round(a, 3), "end": round(b, 3), "text": text, "words": []}
    if words:
        weights = np.array([len(re.sub(r"\W", "", w)) + 1.5 for w in words], float)
        edges = a + np.concatenate([[0], np.cumsum(weights)]) / weights.sum() * (b - a)
        seg["words"] = [{"w": w, "s": round(edges[i], 3), "e": round(edges[i + 1], 3)} for i, w in enumerate(words)]
    result.append(seg)
    print(f"[{a:7.2f}-{b:7.2f}] {text}", flush=True)

with open(out, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
