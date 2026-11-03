"""Gera uma trilha original descontraída e um kit de efeitos sonoros, só com síntese.

Uso: python3 sons.py PASTA_SAIDA DURACAO_DA_TRILHA
Saídas: musica.wav + sfx_*.wav (44,1 kHz estéreo)
"""
import os
import sys
import wave

import numpy as np

SR = 44100
outdir = sys.argv[1]
DUR = float(sys.argv[2])
os.makedirs(outdir, exist_ok=True)
rng = np.random.default_rng(11)


def save(name, L, R=None):
    R = L if R is None else R
    x = np.stack([L, R], 1)
    peak = np.abs(x).max() or 1
    x = (x / peak * 0.9 * 32767).astype(np.int16)
    with wave.open(os.path.join(outdir, name), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(x.tobytes())


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    from scipy.signal import lfilter  # noqa
    return lfilter([1 - a], [1, -a], x)


def tone(f, d, wave_="sine", decay=6.0, attack=0.004):
    t = np.arange(int(d * SR)) / SR
    ph = 2 * np.pi * np.cumsum(np.broadcast_to(f, t.shape)) / SR if np.ndim(f) else 2 * np.pi * f * t
    if wave_ == "sine":
        y = np.sin(ph)
    elif wave_ == "tri":
        y = 2 / np.pi * np.arcsin(np.sin(ph))
    elif wave_ == "square":
        y = np.tanh(4 * np.sin(ph))
    else:
        y = np.sin(ph)
    return y * np.clip(t / attack, 0, 1) * np.exp(-t * decay)


# ====================== MÚSICA ======================
# groove "lo-fi funk" a 100 BPM: Ré menor 9 - Sol 7 - Dó maj7 - Lá 7
BPM = 100
B = 60 / BPM
N = int(DUR * SR)
t = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)


def add(buf, start, y, gain=1.0):
    i = int(start * SR)
    if i >= N:
        return
    n = min(len(y), N - i)
    buf[i:i + n] += y[:n] * gain


chords = [[62, 65, 69, 72, 76], [55, 59, 62, 65, 69], [60, 64, 67, 71, 74], [57, 61, 64, 67, 71]]
roots = [38, 43, 36, 45]
bar = 4 * B
nbars = int(DUR / bar) + 1
for bi in range(nbars):
    s = bi * bar
    ch = chords[bi % 4]
    # piano elétrico: acordes "picados" nos contratempos (estilo funk leve)
    for hit in (0.0, 1.5, 2.5, 3.0):
        for k, m in enumerate(ch):
            y = tone(hz(m), 0.9, "sine", 4.5)
            y += 0.3 * tone(hz(m) * 2, 0.9, "sine", 8)
            pan = (k - 2) * 0.15
            add(L, s + hit * B + k * 0.006, y, 0.05 * (1 - pan))
            add(R, s + hit * B + k * 0.006, y, 0.05 * (1 + pan))
    # baixo sincopado
    r = roots[bi % 4]
    for pos, off in ((0, 0), (0.75, 0), (1.5, 12), (2.5, 0), (3.25, 7)):
        y = tone(hz(r + off), 0.35, "tri", 7)
        add(L, s + pos * B, y, 0.28); add(R, s + pos * B, y, 0.28)
    # bateria
    for beat in range(4):
        bs = s + beat * B
        # kick nos tempos 1 e 3 (+ fantasma)
        if beat in (0, 2):
            n = int(0.3 * SR); x = np.arange(n) / SR
            k_ = np.sin(2 * np.pi * np.cumsum(48 + 90 * np.exp(-x * 35)) / SR) * np.exp(-x * 10)
            add(L, bs, k_, 0.55); add(R, bs, k_, 0.55)
        # caixa abafada nos tempos 2 e 4
        if beat in (1, 3):
            n = int(0.2 * SR); x = np.arange(n) / SR
            sn = (rng.standard_normal(n) * 0.6 + np.sin(2 * np.pi * 190 * x)) * np.exp(-x * 20)
            add(L, bs, sn, 0.18); add(R, bs, sn, 0.18)
        # chimbal em semicolcheias com dinâmica
        for sx in range(4):
            n = int(0.04 * SR)
            hh = np.diff(rng.standard_normal(n + 1)) * np.exp(-np.arange(n) / SR * 90)
            g = 0.035 if sx % 2 else 0.055
            add(L, bs + sx * B / 4, hh, g * 0.8); add(R, bs + sx * B / 4, hh, g * 1.2)

# "vinil": chiado leve
L += lp(rng.standard_normal(N), 3000) * 0.004
R += lp(rng.standard_normal(N), 3000) * 0.004
fade = np.clip(t / 1.5, 0, 1) * np.clip((DUR - t) / 2.5, 0, 1)
L = lp(L, 7000) * fade; R = lp(R, 7000) * fade
save("musica.wav", np.tanh(L * 1.3), np.tanh(R * 1.3))

# ====================== EFEITOS ======================
# whoosh (transição)
n = int(0.5 * SR); x = np.arange(n) / SR
sh = np.where(x < 0.3, (x / 0.3) ** 2, np.exp(-(x - 0.3) * 18))
w = lp(rng.standard_normal(n), 1800) * sh
save("sfx_whoosh.wav", w * np.linspace(1, 0.3, n), w * np.linspace(0.3, 1, n))

# pop (texto aparecendo)
save("sfx_pop.wav", tone(np.linspace(900, 300, int(0.08 * SR)), 0.08, "sine", 40))

# ding (ideia / destaque)
d = tone(1568, 1.0, "sine", 4) + 0.5 * tone(2349, 1.0, "sine", 5) + 0.25 * tone(3136, 1.0, "sine", 8)
save("sfx_ding.wav", d)

# boing (momento engraçado)
n = int(0.5 * SR); x = np.arange(n) / SR
f = 220 + 160 * np.sin(2 * np.pi * 9 * x) * np.exp(-x * 4)
save("sfx_boing.wav", tone(f, 0.5, "tri", 5))

# swish de zoom rápido (punch)
n = int(0.22 * SR); x = np.arange(n) / SR
sw = lp(rng.standard_normal(n), 4000) * np.exp(-x * 14) * (1 - np.exp(-x * 200))
hit = tone(np.linspace(140, 50, n), 0.22, "sine", 14)
save("sfx_punch.wav", sw * 0.7 + hit)

# "record scratch" (quebra de expectativa)
n = int(0.45 * SR); x = np.arange(n) / SR
f = 600 + 500 * np.sign(np.sin(2 * np.pi * 7 * x)) * (1 - x / 0.45)
scr = lp(rng.standard_normal(n), 2500) * 0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(f) / SR)
save("sfx_scratch.wav", scr * np.exp(-x * 3))

# grilos (silêncio constrangedor)
n = int(1.4 * SR); x = np.arange(n) / SR
gate = (np.sin(2 * np.pi * 15 * x) > 0.3) * (np.sin(2 * np.pi * 1.6 * x) > 0)
save("sfx_grilo.wav", np.sin(2 * np.pi * 4600 * x) * gate * 0.5 * np.exp(-x * 0.8))

# "tchan" (revelação): acorde maior brilhante subindo
tc = sum(tone(hz(m), 1.4, "tri", 2.5, 0.01) for m in (72, 76, 79, 84))
save("sfx_tchan.wav", tc)

# tick de texto (máquina de escrever leve)
save("sfx_tick.wav", rng.standard_normal(int(0.02 * SR)) * np.exp(-np.arange(int(0.02 * SR)) / SR * 300))

# riser curto (antes de um momento importante)
n = int(1.0 * SR); x = np.arange(n) / SR
rs = np.sin(2 * np.pi * np.cumsum(200 + 1400 * x ** 2) / SR) * x ** 2 + lp(rng.standard_normal(n), 3000) * x ** 3 * 0.6
save("sfx_riser.wav", rs)
print("ok")
