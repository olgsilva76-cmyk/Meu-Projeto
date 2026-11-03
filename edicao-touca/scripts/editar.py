"""Motor de edição: executa o plano.py sobre o vídeo bruto.

Vídeo: lê cada clipe com ffmpeg, aplica zoom/tremida/transições, cor, legendas
animadas, emojis, grafismos e o contador da touca quadro a quadro (OpenCV + Pillow)
e codifica em H.264.
Áudio: voz tratada + música com ducking + efeitos sonoros, normalizado em -14 LUFS.

Uso: python3 editar.py VIDEO_BRUTO palavras.json PASTA_SONS SAIDA.mp4 [--ate SEGUNDOS] [--quadros t1,t2,...]
"""
import json
import math
import os
import subprocess
import sys
import wave

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import plano  # noqa: E402

FPS = 30
W, H = 720, 1280
SR = 44100
_FONTES = os.path.join(os.path.dirname(__file__), "..", "fontes")
FONT_BLACK = os.path.join(_FONTES, "Ronzino-Bold.otf")
FONT_BOLD = os.path.join(_FONTES, "Ronzino-Medium.otf")
FONT_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
CORES = {"y": (255, 222, 60), "g": (90, 255, 150), "r": (255, 92, 120), "w": (255, 255, 255)}

src, words_json, sons_dir, out = sys.argv[1:5]
args = sys.argv[5:]
LIMIT = float(args[args.index("--ate") + 1]) if "--ate" in args else None
STILLS = [float(x) for x in args[args.index("--quadros") + 1].split(",")] if "--quadros" in args else None
work = os.path.splitext(out)[0] + "_work"
os.makedirs(work, exist_ok=True)


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def ease_out(k):
    return 1 - (1 - k) ** 3


def ease_back(k):
    c = 1.9
    return 1 + (c + 1) * (k - 1) ** 3 + c * (k - 1) ** 2


# =================================================================
# 1. LINHA DO TEMPO
# =================================================================
clips = []
t_out = 0.0
for i, c in enumerate(plano.CLIPS):
    c = dict(c)
    sp = c.get("speed", 1)
    c["n"] = int(round((c["e"] - c["s"]) * FPS / abs(sp)))
    c["hold_n"] = int(round(c.get("hold", 0) * FPS))
    c["o0"] = t_out
    c["o1"] = t_out + c["n"] / FPS
    t_out = c["o1"] + c["hold_n"] / FPS
    c["idx"] = i
    clips.append(c)
TOTAL = t_out
NFRAMES = int(round(TOTAL * FPS))
print(f"duração final: {TOTAL:.2f} s ({len(clips)} clipes)")
if "--mapa" in args:
    for c in clips:
        print(f"  saída {c['o0']:7.2f}-{c['o1']:7.2f}  bruto {c['s']:7.2f}-{c['e']:7.2f}  {c.get('tag', '')}")


def occurrences(ts):
    """Todos os instantes de saída em que o tempo ts do bruto aparece (velocidade normal)."""
    res = []
    for c in clips:
        if c.get("speed", 1) == 1 and c["s"] <= ts < c["e"]:
            res.append((c["o0"] + (ts - c["s"]), c))
        elif c.get("speed", 1) > 1 and c["s"] <= ts < c["e"]:
            res.append((c["o0"] + (ts - c["s"]) / c["speed"], c))
    return res


# =================================================================
# 2. LEGENDAS (grupos de 1–3 palavras)
# =================================================================
words = json.load(open(words_json, encoding="utf-8"))
caps = []  # cada grupo: dict(words=[(texto, o_s, o_e, cor, impact)], o0, o1)
for c in clips:
    if c.get("speed", 1) != 1 or c.get("tag") == "rewind":
        continue
    ws = [w for w in words if c["s"] <= (w["s"] + w["e"]) / 2 < c["e"] and w["w"] not in plano.SEM_LEGENDA]
    group = []

    def flush():
        if group:
            caps.append(dict(words=list(group)))
            group.clear()

    for w in ws:
        txt = w["w"].replace("...", "…")
        os_ = c["o0"] + max(0, w["s"] - c["s"])
        oe_ = c["o0"] + min(c["e"], w["e"]) - c["s"]
        cor, _ = plano.DESTAQUES.get(w["w"], ("w", False))
        # legenda por frase: troca quando a frase acaba ou quando fica longa demais
        if group:
            dur = oe_ - group[0][1]
            chars = sum(len(g[0]) + 1 for g in group) + len(txt)
            if dur > 2.6 or chars > 34:
                # não termina a legenda em artigo/preposição solta ("o", "de", "a"...)
                carry = []
                while len(group) > 1 and len(group[-1][0]) <= 3 and group[-1][0][-1].isalpha():
                    carry.insert(0, group.pop())
                flush()
                group.extend(carry)
        group.append((txt, os_, oe_, cor, False))
        chars = sum(len(g[0]) + 1 for g in group)
        if txt[-1] in ".?!…" or (txt[-1] == "," and chars >= 14):
            flush()
    flush()
caps.sort(key=lambda g: g["words"][0][1])
for i, g in enumerate(caps):
    g["o0"] = g["words"][0][1]
    nxt = caps[i + 1]["words"][0][1] if i + 1 < len(caps) else 1e9
    g["o1"] = min(nxt, g["words"][-1][2] + 0.35)
    g["impact"] = False


# =================================================================
# 3. SPRITES (Pillow -> RGBA numpy)
# =================================================================
_fonts = {}


def font(path, size):
    k = (path, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]


def to_np(img):
    """Pillow (RGBA) -> numpy BGRA, que é a ordem usada pelos quadros do OpenCV."""
    return np.ascontiguousarray(np.asarray(img.convert("RGBA"), dtype=np.uint8)[..., [2, 1, 0, 3]])


def emoji_img(ch, size):
    f = font(FONT_EMOJI, 109)
    im = Image.new("RGBA", (160 * max(1, len(ch)), 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    r = size / max(im.size)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)


def shadowed(img, blur=10, off=(0, 6), alpha=150):
    """Adiciona sombra suave atrás de um sprite."""
    pad = blur * 3
    big = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    a = img.split()[3].point(lambda v: v * alpha // 255)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 255))
    sh.putalpha(a)
    big.alpha_composite(sh, (pad + off[0], pad + off[1]))
    big = big.filter(ImageFilter.GaussianBlur(blur))
    big.alpha_composite(img, (pad, pad))
    return big


_cap_cache = {}


def caption_sprite(gi, active):
    key = (gi, active)
    if key in _cap_cache:
        return _cap_cache[key]
    g = caps[gi]
    size = 56
    parts = []
    for k, (txt, _, _, cor, imp) in enumerate(g["words"]):
        f = font(FONT_BLACK, size)
        parts.append((txt, f, CORES[cor], size))  # cor fixa: branco, ou cor da palavra em destaque
    space = 14
    # quebra em até 2 linhas
    widths = [p[1].getbbox(p[0], stroke_width=7)[2] for p in parts]
    items = list(zip(parts, widths))
    total = sum(widths) + space * (len(items) - 1)
    if total <= 600 or len(items) < 2:
        lines = [items]
    else:
        # duas linhas equilibradas (sem palavra sobrando sozinha)
        best, best_k = 1e9, 1
        for k in range(1, len(items)):
            w1 = sum(w for _, w in items[:k]) + space * (k - 1)
            w2 = sum(w for _, w in items[k:]) + space * (len(items) - k - 1)
            if max(w1, w2) < best:
                best, best_k = max(w1, w2), k
        lines = [items[:best_k], items[best_k:]]
    lh = [max(p[3] for p, _ in ln) for ln in lines]
    tw = max(sum(wd for _, wd in ln) + space * (len(ln) - 1) for ln in lines)
    th = int(sum(h * 1.12 for h in lh))
    img = Image.new("RGBA", (tw + 40, th + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = 20
    for ln, h in zip(lines, lh):
        lw = sum(wd for _, wd in ln) + space * (len(ln) - 1)
        x = 20 + (tw - lw) // 2
        for (txt, f, col, sz), wd in ln:
            d.text((x, y + (h - sz) * 0.8), txt, font=f, fill=col, stroke_width=7, stroke_fill=(10, 10, 10))
            x += wd + space
        y += int(h * 1.12)
    spr = to_np(shadowed(img, 8, (0, 5), 170))
    _cap_cache[key] = spr
    return spr


_misc_cache = {}


def cached(key, fn):
    if key not in _misc_cache:
        _misc_cache[key] = fn()
    return _misc_cache[key]


def big_sprite(text, sub):
    def mk():
        f = font(FONT_BLACK, 132)
        f2 = font(FONT_BOLD, 42)
        b = f.getbbox(text, stroke_width=9)
        b2 = f2.getbbox(sub, stroke_width=5)
        wdt = max(b[2], b2[2]) + 60
        img = Image.new("RGBA", (wdt, b[3] + b2[3] + 60), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text(((wdt - b[2]) // 2, 10), text, font=f, fill=CORES["y"], stroke_width=9, stroke_fill=(15, 10, 0))
        # faixa do subtítulo
        sx = (wdt - b2[2]) // 2
        sy = b[3] + 18
        d.rounded_rectangle((sx - 18, sy - 6, sx + b2[2] + 18, sy + b2[3] + 10), 14, fill=(15, 15, 15, 230))
        d.text((sx, sy), sub, font=f2, fill=(255, 255, 255))
        return to_np(shadowed(img.rotate(4, resample=Image.BICUBIC, expand=True), 12, (0, 8), 180))
    return cached(("big", text, sub), mk)


def emoji_sprite(ch, size=150):
    return cached(("emo", ch, size), lambda: to_np(shadowed(emoji_img(ch, size), 8, (0, 6), 120)))


def counter_sprite(n):
    def mk():
        f = font(FONT_BOLD, 26)
        f2 = font(FONT_BLACK, 34)
        label = "AJUSTES NA TOUCA"
        lb = f.getbbox(label)
        nb = f2.getbbox(str(n))
        w_ = lb[2] + 26 + 64 + 22
        img = Image.new("RGBA", (w_, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, w_ - 1, 63), 32, fill=(16, 16, 18, 215), outline=(255, 255, 255, 70), width=2)
        d.text((22, (64 - lb[3]) // 2 - 2), label, font=f, fill=(255, 255, 255))
        cx = w_ - 22 - 32
        d.ellipse((cx - 24, 8, cx + 24, 56), fill=CORES["r"])
        d.text((cx - nb[2] // 2, 32 - nb[3] // 2 - 4), str(n), font=f2, fill=(255, 255, 255))
        return to_np(shadowed(img, 8, (0, 4), 120))
    return cached(("cnt", n), mk)


def label_sprite(text, bg=(255, 92, 120), emoji=None):
    def mk():
        f = font(FONT_BLACK, 40)
        b = f.getbbox(text)
        em = emoji_img(emoji, 44) if emoji else None
        ew = em.width + 14 if em else 0
        img = Image.new("RGBA", (b[2] + 50 + ew, b[3] + 30), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, img.width - 1, img.height - 1), 18, fill=bg + (240,))
        if em:
            img.alpha_composite(em, (22, (img.height - em.height) // 2))
        d.text((25 + ew, 10), text, font=f, fill=(255, 255, 255))
        return to_np(shadowed(img, 8, (0, 5), 140))
    return cached(("lbl", text, emoji), mk)


def end_card_sprite():
    def mk():
        t = plano.CARTAO_FINAL
        f = font(FONT_BLACK, 56)
        b = f.getbbox(t, stroke_width=6)
        img = Image.new("RGBA", (b[2] + 40, b[3] + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((20, 20), t, font=f, fill=(255, 255, 255), stroke_width=6, stroke_fill=(10, 10, 10))
        return to_np(shadowed(img, 10, (0, 6), 170))
    return cached(("end",), mk)


def blit(frame, spr, cx, cy, scale=1.0, alpha=1.0, angle=0.0):
    """Cola o sprite RGBA centralizado em (cx, cy)."""
    if alpha <= 0.01 or scale <= 0.01:
        return
    s = spr
    if abs(scale - 1) > 0.01 or abs(angle) > 0.1:
        h0, w0 = s.shape[:2]
        if abs(angle) > 0.1:
            M = cv2.getRotationMatrix2D((w0 / 2, h0 / 2), angle, scale)
            cos, sin = abs(M[0, 0]), abs(M[0, 1])
            nw, nh = int(h0 * sin + w0 * cos), int(h0 * cos + w0 * sin)
            M[0, 2] += nw / 2 - w0 / 2
            M[1, 2] += nh / 2 - h0 / 2
            s = cv2.warpAffine(s, M, (nw, nh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        else:
            s = cv2.resize(s, (max(1, int(w0 * scale)), max(1, int(h0 * scale))), interpolation=cv2.INTER_LINEAR)
    h, w = s.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if fx1 <= fx0 or fy1 <= fy0:
        return
    sub = s[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0]
    a = sub[:, :, 3:4].astype(np.float32) / 255 * alpha
    reg = frame[fy0:fy1, fx0:fx1].astype(np.float32)
    frame[fy0:fy1, fx0:fx1] = (reg * (1 - a) + sub[:, :, :3].astype(np.float32) * a).astype(np.uint8)


# =================================================================
# 4. EFEITOS POR CLIPE (em tempo de saída)
# =================================================================
fx_by_type = {}
for ef in plano.EFEITOS:
    kind, ts = ef[0], ef[1]
    for o, c in occurrences(ts):
        if c.get("tag") == "rewind":
            continue
        fx_by_type.setdefault(kind, []).append((o, c["idx"], ef))
for k in fx_by_type:
    fx_by_type[k].sort(key=lambda x: x[0])

touca_times = [o for o, _, _ in fx_by_type.get("touca", [])]


def zoom_at(c, t):
    """Zoom do clipe no instante de saída t (base + zoom lento + punches)."""
    k = clamp((t - c["o0"]) / max(1e-6, c["o1"] - c["o0"]))
    z = c.get("z", 1.0) + (c.get("z2", c.get("z", 1.0)) - c.get("z", 1.0)) * ease_out(k) if "z2" in c else c.get("z", 1.0)
    mult = 1.0
    for o, ci, ef in fx_by_type.get("punch", []):
        if ci != c["idx"] or t < o:
            continue
        amount, dur = ef[2], ef[3]
        rise = ease_out(clamp((t - o) / 0.1))
        fall = 1.0
        if dur is not None:
            fall = 1 - ease_out(clamp((t - o - dur) / 0.18))
        mult = max(mult, 1 + (amount - 1) * rise * fall)
    # transição "whip": começa mais perto e assenta
    if c.get("enter") == "whip":
        mult *= 1 + 0.12 * (1 - ease_out(clamp((t - c["o0"]) / 0.22)))
    return z * mult


def shake_at(t):
    dx = dy = 0.0
    for o, _, ef in fx_by_type.get("shake", []):
        dur, force = ef[2], ef[3]
        if o <= t < o + dur:
            k = 1 - (t - o) / dur
            dx += math.sin(t * 95) * force * k
            dy += math.cos(t * 77) * force * k
    return dx, dy


# =================================================================
# 5. LEITURA DOS CLIPES + DETECÇÃO DO ROSTO
# =================================================================
cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def read_frames(s, e):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{s:.3f}", "-i", src, "-t", f"{e - s:.3f}",
                        "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                       capture_output=True, check=True).stdout
    arr = np.frombuffer(p, np.uint8)
    n = len(arr) // (W * H * 3)
    return arr[:n * W * H * 3].reshape(n, H, W, 3)


def face_center(frames):
    pts = []
    for f in frames[:: max(1, len(frames) // 5)][:6]:
        g = cv2.cvtColor(cv2.resize(f, (W // 2, H // 2)), cv2.COLOR_BGR2GRAY)
        det = cascade.detectMultiScale(g, 1.1, 5, minSize=(40, 40))
        if len(det):
            x, y, w, h = max(det, key=lambda r: r[2] * r[3])
            pts.append(((x + w / 2) * 2, (y + h / 2) * 2, w * 2))
    if not pts:
        return (W / 2, H * 0.36, 160)
    a = np.median(np.array(pts), 0)
    return tuple(a)


# cor: leve contraste/saturação/calor + vinheta
yy, xx = np.mgrid[0:H, 0:W]
vig = 1 - 0.28 * np.clip(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.7)) ** 2, 0, 1)
vig = vig[..., None].astype(np.float32)
lut = np.clip((np.arange(256) / 255.0 - 0.5) * 1.08 + 0.5 + 0.01, 0, 1)
lut = (lut * 255).astype(np.uint8)
warm = np.array([0.97, 1.0, 1.04], np.float32)  # BGR


def grade(f):
    f = cv2.LUT(f, lut)
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    hsv[..., 1] = cv2.convertScaleAbs(hsv[..., 1], alpha=1.12)
    f = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR).astype(np.float32)
    f *= warm
    f *= vig
    return np.clip(f, 0, 255).astype(np.uint8)


def transform(f, z, center, dx=0, dy=0):
    fx, fy, fw = center
    if z <= 1.001 and abs(dx) < 0.5 and abs(dy) < 0.5:
        return f, (lambda x, y: (x, y))
    z = max(z, 1.0)
    cw, ch = W / z, H / z
    cx = clamp(fx, cw / 2, W - cw / 2)
    cy = clamp(fy + ch * 0.16, ch / 2, H - ch / 2)  # rosto a ~1/3 da altura
    x0, y0 = cx - cw / 2, cy - ch / 2
    if z <= 1.001:
        x0 = y0 = 0
    M = np.float32([[z, 0, -x0 * z + dx], [0, z, -y0 * z + dy]])
    out_ = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    return out_, (lambda x, y: (x * z - x0 * z + dx, y * z - y0 * z + dy))


# =================================================================
# 6. RENDER
# =================================================================
def overlays(frame, t, c, face_out):
    # ---- grafismos grandes ----
    for o, _, ef in fx_by_type.get("big", []):
        dur = ef[4]
        if o <= t < o + dur:
            k_in = clamp((t - o) / 0.28)
            k_out = clamp((t - (o + dur - 0.2)) / 0.2)
            sc = (0.4 + 0.6 * ease_back(k_in)) * (1 - 0.3 * k_out)
            blit(frame, big_sprite(ef[2], ef[3]), W / 2, 250, sc, (1 - k_out) * clamp(k_in * 3))
    # ---- rótulo do trecho acelerado ----
    if c.get("tag") == "fast":
        blit(frame, label_sprite("ACELERANDO 4x", (40, 40, 44)), W / 2, 980)
    # ---- legendas: frase inteira, fixa, troca de uma frase para a outra ----
    for gi, g in enumerate(caps):
        if g["o0"] <= t < g["o1"]:
            blit(frame, caption_sprite(gi, 0), W / 2, 905)
            break


def render_frame(fi, cache):
    t = fi / FPS
    c = next((c for c in clips if c["o0"] <= t + 1e-6 < c["o1"] + c["hold_n"] / FPS), clips[-1])
    if c["idx"] not in cache:
        cache.clear()
        sp = c.get("speed", 1)
        raw = read_frames(c["s"], c["e"])
        if sp > 1:
            raw = raw[::sp]
        elif sp < 0:
            raw = raw[::sp]  # de trás pra frente, pulando quadros
        cache[c["idx"]] = (raw, face_center(raw))
    raw, center = cache[c["idx"]]
    k = int(round((t - c["o0"]) * FPS))
    k = min(max(k, 0), len(raw) - 1)
    f = raw[k]
    hold = t >= c["o1"]
    tt = min(t, c["o1"] - 1e-3)
    z = zoom_at(c, tt)
    dx, dy = shake_at(t)
    f, mp = transform(f, z, center, dx, dy)
    # transição "whip": desfoque de movimento nos primeiros quadros
    if c.get("enter") == "whip" and t - c["o0"] < 0.17:
        ksz = int(3 + 40 * (1 - (t - c["o0"]) / 0.17))
        kern = np.zeros((ksz, ksz), np.float32)
        kern[:, ksz // 2] = 1 / ksz
        f = cv2.filter2D(f, -1, kern)
    f = grade(f)
    if c.get("tag") == "rewind":
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        f = cv2.merge([g, g, g])
        f = np.roll(f, 4, axis=1)
        f[..., 2] = np.roll(f[..., 2], -8, axis=1)
        f = (f.astype(np.float32) * 0.85).astype(np.uint8)
        f[(np.arange(H) % 4 == 0)] //= 2
    if c.get("tag") == "fast":
        f = cv2.addWeighted(f, 0.92, np.full_like(f, (30, 20, 10)), 0.08, 0)
    fx_, fy_, fw_ = center
    ox, oy = mp(fx_, fy_)
    face_out = (ox, oy, fw_ * max(1.0, z))
    if hold and c.get("tag") == "end":
        kk = clamp((t - c["o1"]) / 0.4)
        f = (f.astype(np.float32) * (1 - 0.45 * kk)).astype(np.uint8)
        f = cv2.GaussianBlur(f, (0, 0), 0.1 + 6 * kk)
    overlays(f, t, c, face_out)
    if hold and c.get("tag") == "end":
        kk = clamp((t - c["o1"] - 0.15) / 0.35)
        blit(f, end_card_sprite(), W / 2, H * 0.45, 0.6 + 0.4 * ease_back(kk), clamp(kk * 2))
        fade = clamp((t - (TOTAL - 0.5)) / 0.5)
        f = (f.astype(np.float32) * (1 - fade)).astype(np.uint8)
    # flash branco de entrada
    if c.get("enter") == "flash" and t - c["o0"] < 0.2:
        a = 0.85 * (1 - (t - c["o0"]) / 0.2)
        f = cv2.addWeighted(f, 1 - a, np.full_like(f, 255), a, 0)
    return f


def render_video(path):
    n = NFRAMES if LIMIT is None else min(NFRAMES, int(LIMIT * FPS))
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                           "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    cache = {}
    for fi in range(n):
        ff.stdin.write(render_frame(fi, cache).tobytes())
        if fi % 300 == 0:
            print(f"  vídeo {fi / FPS:6.1f}/{n / FPS:.1f} s", flush=True)
    ff.stdin.close()
    ff.wait()


# =================================================================
# 7. ÁUDIO
# =================================================================
def read_wav(p):
    with wave.open(p) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return x.reshape(-1, w.getnchannels())


def db(g):
    return 10 ** (g / 20)


def render_audio(path):
    n = int(TOTAL * SR) + SR
    # voz
    parts = []
    for c in clips:
        sp = c.get("speed", 1)
        d = c["n"] / FPS
        if c.get("tag") == "rewind":
            parts.append(f"aevalsrc=0|0:d={d:.4f}:s={SR}")
        elif sp > 1:
            parts.append(f"[0:a]atrim={c['s']:.4f}:{c['e']:.4f},asetpts=PTS-STARTPTS,asetrate={SR * sp},aresample={SR},"
                         f"atrim=0:{d:.4f},volume=0.22")
        else:
            parts.append(f"[0:a]atrim={c['s']:.4f}:{c['s'] + d:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,"
                         f"afade=t=out:st={max(0, d - 0.02):.4f}:d=0.02")
        if c["hold_n"]:
            parts.append(f"aevalsrc=0|0:d={c['hold_n'] / FPS:.4f}:s={SR}")
    fc = ";".join(f"{p}[v{i}]" for i, p in enumerate(parts))
    fc += ";" + "".join(f"[v{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=0:a=1,"
    fc += "highpass=f=85,afftdn=nf=-28,acompressor=threshold=-21dB:ratio=3:attack=6:release=90:makeup=2,"
    fc += "equalizer=f=3200:t=q:w=1:g=2[out]"
    voice = os.path.join(work, "voz.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-filter_complex", fc, "-map", "[out]", "-ac", "2",
                    "-ar", str(SR), voice], check=True)

    # efeitos
    sfx = np.zeros((n, 2), np.float32)
    for o, ci, ef in fx_by_type.get("sfx", []):
        x = read_wav(os.path.join(sons_dir, f"sfx_{ef[2]}.wav")) * db(ef[3])
        i = int(o * SR)
        m = min(len(x), n - i)
        if m > 0:
            sfx[i:i + m] += x[:m]
    for c in clips:  # sons automáticos de transição
        i = int((c["o0"] - 0.18) * SR)
        name = {"whip": ("whoosh", -14), "flash": ("whoosh", -12)}.get(c.get("enter"))
        if c.get("tag") == "rewind":
            name = ("scratch", -8)
        if c.get("tag") == "fast":
            name = ("riser", -16)
        if name and i >= 0:
            x = read_wav(os.path.join(sons_dir, f"sfx_{name[0]}.wav")) * db(name[1])
            m = min(len(x), n - i)
            sfx[i:i + m] += x[:m]
    for gi, g in enumerate(caps):  # "pop" discreto nas legendas de impacto
        if g["impact"]:
            x = read_wav(os.path.join(sons_dir, "sfx_pop.wav")) * db(-20)
            i = int(g["o0"] * SR)
            m = min(len(x), n - i)
            sfx[i:i + m] += x[:m]
    # música com automação de volume
    mus = read_wav(os.path.join(sons_dir, "musica.wav"))
    if len(mus) < n:
        mus = np.concatenate([mus, mus[:n - len(mus)]])
    mus = mus[:n].copy()
    tt = np.arange(n) / SR
    gain = np.full(n, db(-17), np.float32)
    for c in clips:
        if c.get("tag") == "fast":
            gain[(tt >= c["o0"]) & (tt < c["o1"])] = db(-9)
        if c.get("tag") == "rewind":
            gain[(tt >= c["o0"]) & (tt < c["o1"])] = 0
        if c["hold_n"] and c.get("tag") != "end":
            gain[(tt >= c["o1"]) & (tt < c["o1"] + c["hold_n"] / FPS)] = db(-30)  # pausa cômica
    hook_end = clips[1]["o1"]
    gain[tt < hook_end] = db(-24)
    gain = np.convolve(gain, np.ones(2205) / 2205, mode="same")  # suaviza (50 ms)
    fade = np.clip((TOTAL - tt) / 1.2, 0, 1)
    mus *= (gain * fade)[:, None]

    def wr(p, x):
        with wave.open(p, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    wr(os.path.join(work, "sfx.wav"), sfx)
    wr(os.path.join(work, "musica.wav"), mus)
    # ducking da música pela voz + mix + loudness
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", voice, "-i", os.path.join(work, "musica.wav"),
                    "-i", os.path.join(work, "sfx.wav"), "-filter_complex",
                    "[0:a]asplit=2[v][sc];[1:a][sc]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=350[m];"
                    "[v][m][2:a]amix=inputs=3:normalize=0:duration=first,"
                    "loudnorm=I=-14:TP=-1.5:LRA=11[out]",
                    "-map", "[out]", "-ar", str(SR), "-t", f"{TOTAL:.3f}", path], check=True)


if STILLS:
    cache = {}
    for ts in STILLS:
        cv2.imwrite(f"{os.path.splitext(out)[0]}_{ts:06.2f}.jpg", render_frame(int(ts * FPS), cache))
    sys.exit(0)

vpath = os.path.join(work, "video.mp4")
apath = os.path.join(work, "audio.wav")
render_audio(apath)
print("áudio ok")
render_video(vpath)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vpath, "-i", apath, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", "-shortest", out], check=True)
print("ok ->", out)
