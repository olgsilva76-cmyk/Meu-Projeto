"""Alinha cada palavra da transcrição revisada ao áudio.

Dentro de cada trecho, as palavras são distribuídas só pelo tempo em que há voz
(energia acima do limiar), proporcional ao número de letras. Isso evita que as
legendas "andem" durante as micro-pausas.

Uso: python3 alinhar.py VIDEO transcricao_revisada.json palavras.json
"""
import json
import re
import subprocess
import sys

import numpy as np

video, src, out = sys.argv[1:4]
SR = 16000
HOP = 160  # 10 ms
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                     capture_output=True, check=True).stdout
a = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
n = len(a) // HOP
rms = np.sqrt((a[:n * HOP].reshape(n, HOP) ** 2).mean(1) + 1e-12)
db = 20 * np.log10(rms)
db = np.convolve(db, np.ones(5) / 5, mode="same")

words = []
for s, e, text in json.load(open(src, encoding="utf-8")):
    toks = text.split()
    i0, i1 = int(s * 100), int(e * 100)
    seg = db[i0:i1]
    thr = max(np.percentile(seg, 90) - 18, -45)
    voiced = (seg > thr).astype(float) + 0.08  # um pouco de peso também nas pausas
    cum = np.concatenate([[0], np.cumsum(voiced)])
    cum /= cum[-1]
    wts = np.array([len(re.sub(r"\W", "", w)) + 1.2 for w in toks])
    wc = np.concatenate([[0], np.cumsum(wts)]) / wts.sum()
    frames = np.interp(wc, cum, np.arange(len(cum)))
    for k, w in enumerate(toks):
        ws = s + frames[k] / 100
        we = s + frames[k + 1] / 100
        words.append({"w": w, "s": round(ws, 3), "e": round(we, 3), "chunk": [s, e]})

json.dump(words, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
for x in words:
    print(f'{x["s"]:7.2f} {x["e"]:7.2f} {x["w"]}')
