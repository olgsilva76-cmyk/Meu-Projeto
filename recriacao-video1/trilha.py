"""Gera a trilha original do vídeo (26 s, 44,1 kHz, estéreo) só com síntese.

Camadas: pad de acordes, baixo, kick/hi-hat a 120 BPM, whoosh em cada corte,
cliques nos botões e tique de digitação. Saída: trilha.wav
Uso: python3 trilha.py [saida.wav]
"""
import sys
import wave
import numpy as np

SR = 44100
DUR = 26.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)

CUTS = [2.4, 4.0, 6.0, 8.0, 10.4, 12.2, 14.6, 17.6, 21.2]
CLICKS = [1.95, 17.15, 24.3]
TYPING = [(0.3, 1.4, 17), (16.1, 17.0, 20)]  # (início, fim, nº de letras)
BPM = 120
BEAT = 60 / BPM


def note(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def env(start, dur, attack=0.005, release=None):
    e = np.zeros(N)
    i0 = int(start * SR)
    n = int(dur * SR)
    if i0 >= N:
        return e
    n = min(n, N - i0)
    x = np.arange(n) / SR
    a = np.clip(x / attack, 0, 1)
    r = np.exp(-x / (release or dur / 4))
    e[i0:i0 + n] = a * r
    return e


def lowpass(x, cutoff):
    # filtro de 1 polo simples
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


L = np.zeros(N)
R = np.zeros(N)

# ---- pad: Lá menor - Fá - Dó - Sol, 2 compassos cada (4 s) ----
chords = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]]
pad = np.zeros(N)
for ci in range(int(DUR / 4) + 1):
    ch = chords[ci % 4]
    s = ci * 4.0
    seg = (t >= s) & (t < s + 4.4)
    fade = np.clip((t - s) / 0.6, 0, 1) * np.clip((s + 4.4 - t) / 0.6, 0, 1)
    for m in ch:
        f = note(m)
        for det in (-0.12, 0.12):
            pad += seg * fade * np.sin(2 * np.pi * f * (1 + det / 100) * t) * 0.05
        pad += seg * fade * np.sin(2 * np.pi * f * 2 * t) * 0.012
pad *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.25 * t)  # leve "respiração"
L += pad * 0.9
R += pad * 1.0

# ---- baixo: nota fundamental em colcheias ----
roots = [45, 41, 36, 43]
bass = np.zeros(N)
for k in range(int(DUR / (BEAT / 2))):
    st = k * BEAT / 2
    r = roots[int(st // 4) % 4]
    e = env(st, BEAT / 2, 0.004, 0.12)
    bass += e * np.tanh(2.2 * np.sin(2 * np.pi * note(r) * t)) * 0.22
bass = lowpass(bass, 400)
L += bass
R += bass

# ---- bateria (entra no primeiro corte) ----
start_drums = 2.4
for k in range(int((DUR - start_drums) / BEAT)):
    st = start_drums + k * BEAT
    # kick: seno com queda de frequência
    i0 = int(st * SR)
    n = min(int(0.35 * SR), N - i0)
    x = np.arange(n) / SR
    f = 50 + 110 * np.exp(-x * 30)
    kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 9) * 0.75
    L[i0:i0 + n] += kick
    R[i0:i0 + n] += kick
    # hi-hat no contratempo
    hs = st + BEAT / 2
    i1 = int(hs * SR)
    m = min(int(0.06 * SR), N - i1)
    if m > 0:
        hh = rng.standard_normal(m) * np.exp(-np.arange(m) / SR * 70) * 0.08
        hh = hh - np.concatenate([[0], hh[:-1]])  # passa-alta grosseiro
        L[i1:i1 + m] += hh * 0.8
        R[i1:i1 + m] += hh * 1.2
    # palma nos tempos 2 e 4
    if k % 2 == 1:
        m = min(int(0.18 * SR), N - i0)
        cl = rng.standard_normal(m) * np.exp(-np.arange(m) / SR * 22) * 0.12
        L[i0:i0 + m] += cl
        R[i0:i0 + m] += cl

# ---- whoosh em cada corte (ruído filtrado subindo até o corte) ----
for c in CUTS:
    s = c - 0.35
    i0 = int(s * SR)
    n = int(0.6 * SR)
    x = np.arange(n) / SR
    noise = rng.standard_normal(n)
    shape = np.where(x < 0.35, (x / 0.35) ** 2, np.exp(-(x - 0.35) * 14))
    w = lowpass(noise, 2500) * shape * 0.5
    pan = np.linspace(-1, 1, n)
    L[i0:i0 + n] += w * (1 - pan) / 2 * 1.4
    R[i0:i0 + n] += w * (1 + pan) / 2 * 1.4
    # impacto grave no corte
    i1 = int(c * SR)
    m = int(0.5 * SR)
    y = np.arange(m) / SR
    hit = np.sin(2 * np.pi * (40 + 60 * np.exp(-y * 20)) * y) * np.exp(-y * 6) * 0.35
    L[i1:i1 + m] += hit
    R[i1:i1 + m] += hit

# ---- cliques de botão ----
for c in CLICKS:
    i0 = int(c * SR)
    m = int(0.05 * SR)
    y = np.arange(m) / SR
    ck = np.sin(2 * np.pi * 2200 * y) * np.exp(-y * 120) * 0.35
    L[i0:i0 + m] += ck
    R[i0:i0 + m] += ck
    # brilho ("ding") logo depois
    j0 = i0 + int(0.03 * SR)
    m2 = int(0.8 * SR)
    y2 = np.arange(m2) / SR
    ding = (np.sin(2 * np.pi * 1760 * y2) + 0.5 * np.sin(2 * np.pi * 2637 * y2)) * np.exp(-y2 * 5) * 0.09
    L[j0:j0 + m2] += ding
    R[j0:j0 + m2] += ding

# ---- tique de digitação ----
for a, b, letters in TYPING:
    for k in range(letters):
        st = a + (b - a) * k / letters + rng.uniform(-0.01, 0.01)
        i0 = int(st * SR)
        m = int(0.02 * SR)
        tk = rng.standard_normal(m) * np.exp(-np.arange(m) / SR * 300) * 0.12
        L[i0:i0 + m] += tk
        R[i0:i0 + m] += tk

# ---- final: fade out ----
fade = np.clip((DUR - t) / 0.8, 0, 1)
fade *= np.clip(t / 0.05, 0, 1)
L *= fade
R *= fade

mix = np.stack([L, R], axis=1)
mix = np.tanh(mix * 1.2) * 0.9  # saturação suave / limitador
pcm = (mix / max(1e-9, np.abs(mix).max()) * 0.95 * 32767).astype(np.int16)

out = sys.argv[1] if len(sys.argv) > 1 else "trilha.wav"
with wave.open(out, "wb") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(pcm.tobytes())
print("ok ->", out)
