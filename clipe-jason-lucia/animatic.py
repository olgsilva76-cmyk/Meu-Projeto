"""Monta o animatic do clipe: imagens-chave no tempo da música.

- Baixa as imagens de frames.json (OpenArt) para a pasta frames/.
- Corta no compasso (refrões) ou a cada 2 compassos (versos), com zoom lento
  alternando entrada/saída, flash nos cortes dos refrões e faixas pretas 2,35:1.
- Escreve a letra (letra.srt) embaixo, em branco, e o título no final.
- Usa a música como áudio.

Uso (no seu computador, com Python 3 + ffmpeg):
    pip install numpy pillow opencv-python-headless
    python3 animatic.py CAMINHO/DA/MUSICA.m4a animatic.mp4
Teste sem baixar nada (imagens coloridas no lugar):  --teste
"""
import json
import math
import os
import re
import subprocess
import sys
import urllib.request

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1920, 1080, 24
IMG_H = int(W / 2.35)  # 817: área de imagem 2,35:1
TOP = (H - IMG_H) // 2
BPM = 143.55
BAR = 4 * 60 / BPM

musica, saida = sys.argv[1], sys.argv[2]
TESTE = "--teste" in sys.argv

# seção: (início, fim, lista de cenas, compassos por plano, flash nos cortes)
SECOES = [
    (0.19, 13.68, ["01"], 8, False),
    (13.68, 40.68, ["01", "13", "15", "13"], 2, False),
    (40.68, 54.45, ["16", "22", "16", "22"], 1, True),
    (54.45, 80.57, ["24", "30"], 2, False),
    (80.57, 82.27, ["33"], 1, False),
    (82.27, 95.57, ["36", "16", "15", "22"], 1, True),
    (95.57, 108.83, ["42"], 4, False),
    (108.83, 135.44, ["51", "36", "15"], 2, False),
    (135.44, 164.58, ["54", "22", "16", "51", "36", "15"], 1, True),
    (164.58, 171.46, ["62"], 4, False),
    (171.46, 183.46, ["54", "62", "42", "30", "13", "16"], 1, True),
    (183.46, 186.92, ["62"], 4, False),
]

# ---------- imagens ----------
cfg = json.load(open(os.path.join(AQUI, "frames.json"), encoding="utf-8"))
pasta = os.path.join(AQUI, "frames")
os.makedirs(pasta, exist_ok=True)
imgs = {}
for k, v in cfg["cenas"].items():
    p = os.path.join(pasta, f"cena_{k}.png")
    if TESTE:
        hue = (int(k) * 37) % 180
        a = np.zeros((672, 1584, 3), np.uint8)
        a[..., 0], a[..., 1], a[..., 2] = hue, 200, np.linspace(60, 230, 1584)[None, :]
        a = cv2.cvtColor(a, cv2.COLOR_HSV2BGR)
        cv2.putText(a, f"CENA {k}", (560, 360), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 6)
        imgs[k] = a
        continue
    if not os.path.exists(p):
        print("baixando cena", k)
        urllib.request.urlretrieve(v["url"], p)
    imgs[k] = cv2.imread(p)


def cover(img, w, h):
    """Redimensiona preenchendo w×h (corta o excesso)."""
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih)
    r = cv2.resize(img, (math.ceil(iw * s), math.ceil(ih * s)), interpolation=cv2.INTER_AREA)
    y0, x0 = (r.shape[0] - h) // 2, (r.shape[1] - w) // 2
    return r[y0:y0 + h, x0:x0 + w]


base = {k: cover(v, int(W * 1.15), int(IMG_H * 1.15)) for k, v in imgs.items()}

# ---------- planos ----------
planos = []  # (início, fim, cena, flash, idx)
for ini, fim, cenas, comp, flash in SECOES:
    t, i = ini, 0
    while t < fim - 0.05:
        f = min(fim, t + comp * BAR)
        planos.append((t, f, cenas[i % len(cenas)], flash and i > 0, len(planos)))
        t, i = f, i + 1

# ---------- letra ----------
def srt_t(s):
    h, m, r = s.split(":")
    sec, ms = r.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


letra = []
for bloco in open(os.path.join(AQUI, "letra.srt"), encoding="utf-8").read().strip().split("\n\n"):
    ln = bloco.split("\n")
    a, b = [srt_t(x.strip()) for x in ln[1].split("-->")]
    letra.append((a, b, " ".join(ln[2:])))


def fonte(size, bold=True):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf",
              "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


F_LETRA, F_TIT, F_SUB = fonte(40), fonte(120), fonte(44)
_cache = {}


def texto_bgra(txt, f, cor=(255, 255, 255), contorno=3):
    k = (txt, id(f), cor)
    if k not in _cache:
        b = f.getbbox(txt, stroke_width=contorno)
        im = Image.new("RGBA", (b[2] + 20, b[3] + 20), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), txt, font=f, fill=cor, stroke_width=contorno, stroke_fill=(0, 0, 0))
        _cache[k] = np.asarray(im)[..., [2, 1, 0, 3]].copy()
    return _cache[k]


def colar(dst, spr, cx, cy, alpha=1.0):
    h, w = spr.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    x1, y1 = max(0, x0), max(0, y0)
    x2, y2 = min(W, x0 + w), min(H, y0 + h)
    if x2 <= x1 or y2 <= y1:
        return
    s = spr[y1 - y0:y2 - y0, x1 - x0:x2 - x0]
    a = s[..., 3:4].astype(np.float32) / 255 * alpha
    dst[y1:y2, x1:x2] = (dst[y1:y2, x1:x2] * (1 - a) + s[..., :3] * a).astype(np.uint8)


def quadro(t):
    out = np.zeros((H, W, 3), np.uint8)
    p = next((p for p in planos if p[0] <= t < p[1]), planos[-1])
    ini, fim, cena, flash, idx = p
    k = (t - ini) / max(0.01, fim - ini)
    img = base[cena]
    z = 1.0 + 0.12 * (k if idx % 2 == 0 else 1 - k)  # zoom lento, alternando
    bh, bw = img.shape[:2]
    cw, ch = int(W / z * 1.0), int(IMG_H / z)
    x0 = int((bw - cw) / 2 + (k - 0.5) * 40 * (1 if idx % 3 else -1))
    y0 = (bh - ch) // 2
    x0 = max(0, min(bw - cw, x0))
    crop = img[y0:y0 + ch, x0:x0 + cw]
    out[TOP:TOP + IMG_H] = cv2.resize(crop, (W, IMG_H), interpolation=cv2.INTER_LINEAR)
    # flash branco nos cortes dos refrões
    if flash and t - ini < 0.12:
        a = 0.7 * (1 - (t - ini) / 0.12)
        out[TOP:TOP + IMG_H] = cv2.addWeighted(out[TOP:TOP + IMG_H], 1 - a, np.full_like(out[TOP:TOP + IMG_H], 255), a, 0)
    # entrada e saída em fade
    fade = min(1.0, t / 1.0, max(0.0, (186.92 - t) / 2.5))
    if fade < 1:
        out = (out * fade).astype(np.uint8)
    # letra
    for a, b, txt in letra:
        if a <= t < b:
            colar(out, texto_bgra(txt, F_LETRA), W / 2, TOP + IMG_H - 60)
            break
    # título no final instrumental
    if 172.3 <= t < 183.4:
        al = min(1.0, (t - 172.3) / 0.6, (183.4 - t) / 0.6)
        colar(out, texto_bgra("JASON & LÚCIA", F_TIT, contorno=4), W / 2, H / 2 - 30, al)
        colar(out, texto_bgra("VAMORLI MUSIC", F_SUB, (25, 227, 255) if False else (255, 46, 136), 2), W / 2, H / 2 + 70, al)
    return out


dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", musica],
                           capture_output=True, text=True).stdout.strip())
n = int(dur * FPS)
limite = None
if "--ate" in sys.argv:
    limite = float(sys.argv[sys.argv.index("--ate") + 1])
    n = int(limite * FPS)
ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                       "-i", "-", "-i", musica, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "20",
                       "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-shortest", saida],
                      stdin=subprocess.PIPE)
for i in range(n):
    ff.stdin.write(quadro(i / FPS).tobytes())
    if i % (FPS * 20) == 0:
        print(f"  {i / FPS:5.0f}/{n / FPS:.0f} s", flush=True)
ff.stdin.close()
ff.wait()
print("ok ->", saida, f"({len(planos)} planos)")
