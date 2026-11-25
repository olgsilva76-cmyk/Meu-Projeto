"""Reference-style edit (kinetic captions + fast montage + metallic logo) of the baptism footage."""
import os, sys, json, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'edit'))
from shots2 import SHOTS, TRANS, FPS, W, H, DUR, HANDLE
from prep import src_fn
PREP = os.path.join(ROOT, 'prep2'); FONTS = os.path.join(ROOT, 'fonts', 'use')
cv2.setNumThreads(1)

def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def sine_io(x): x = clamp(x); return 0.5 - 0.5 * math.cos(math.pi * x)
def out_cubic(x): x = clamp(x); return 1 - (1 - x) ** 3
def in_cubic(x): x = clamp(x); return x ** 3
def out_back(x, s=1.7):
    x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1
def lerp(a, b, p): return a + (b - a) * p

# ---------------- footage ----------------
class Shot:
    def __init__(self, s):
        self.s = s; self.meta = json.load(open(os.path.join(PREP, s['id'] + '.json')))
        self.f, _, _ = src_fn(s); self.cap = None; self.idx = -1; self.frame = None; self.d = s['t1'] - s['t0']
    def raw(self, t):
        i = int(round((self.f(t - self.s['t0']) - self.meta['srcA']) / self.meta['base'] * FPS))
        i = max(0, min(self.meta['nframes'] - 1, i))
        if self.cap is None or i < self.idx:
            if self.cap is not None: self.cap.release()
            self.cap = cv2.VideoCapture(os.path.join(PREP, self.s['id'] + '.mp4')); self.idx = -1
        while self.idx < i:
            ok, fr = self.cap.read()
            if not ok: break
            self.frame = fr; self.idx += 1
        return self.frame

HITS = []  # filled from text events: times of punches
def punch(t):
    v = 0.0
    for at in HITS:
        if t >= at: v += 0.05 * math.exp(-(t - at) / 0.12)
    return v

def view(sh, t, z=1.0, tx=0.0, img=None):
    s0, s1, dx0, dy0, dx1, dy1 = sh.s['move']; p = sine_io((t - sh.s['t0']) / sh.d)
    sc = lerp(s0, s1, p) * z * (1 + punch(t)); dx = lerp(dx0, dx1, p) + tx; dy = lerp(dy0, dy1, p)
    img = sh.raw(t) if img is None else img
    M = np.float32([[sc, 0, (1 - sc) * W / 2 + dx], [0, sc, (1 - sc) * H / 2 + dy]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)

def zoomblur(sh, t, z, amt, n=7):
    img = sh.raw(t); acc = np.zeros((H, W, 3), np.float32)
    for k in range(n): acc += view(sh, t, z * (1 + amt * k / (n - 1)), img=img)
    return acc / n
def hblur(img, k):
    k = int(k) | 1
    return cv2.blur(img, (k, 1)) if k > 1 else img

def transition(A, B, kind, tc, d, t):
    if kind == 'cut': return (view(A, t) if t < tc else view(B, t)).astype(np.float32)
    if kind in ('dissolve', 'glow'):
        a = sine_io((t - (tc - d)) / (2 * d))
        f = view(A, t).astype(np.float32) * (1 - a) + view(B, t).astype(np.float32) * a
        if kind == 'glow': f = f + np.float32([90, 170, 255]) * 0.45 * math.sin(math.pi * a)
        return f
    if kind == 'zoom':
        if t < tc:
            p = (t - (tc - d)) / d; return zoomblur(A, t, 1 + in_cubic(p) * 0.6, in_cubic(p) * 0.25)
        p = (t - tc) / d; return zoomblur(B, t, 1 - (1 - out_cubic(p)) * 0.2, (1 - out_cubic(p)) * 0.25)
    if kind == 'whip':
        if t < tc:
            p = in_cubic((t - (tc - d)) / d); return hblur(view(A, t, tx=-p * W * 0.6), 1 + p * 300).astype(np.float32)
        p = 1 - out_cubic((t - tc) / d); return hblur(view(B, t, tx=p * W * 0.6), 1 + p * 300).astype(np.float32)
    if kind == 'flash':
        f = (view(A, t) if t < tc else view(B, t)).astype(np.float32)
        k = 0.70 * math.exp(-((t - tc) / (0.035 if t < tc else d * 0.5)) ** 2)
        return f + (255 - f) * k
    if kind == 'invert':
        f = (view(A, t) if t < tc else view(B, t)).astype(np.float32)
        if tc <= t < tc + 2.5 / FPS:  # two negative frames, blown out
            f = np.clip((255 - f) * 1.25 + 30, 0, 255)
        elif t >= tc:
            k = 0.6 * math.exp(-((t - tc) / 0.12) ** 2); f = f + (255 - f) * k
        return f
    raise ValueError(kind)

# ---------------- atmosphere ----------------
vy_, vx_ = np.mgrid[0:H, 0:W].astype(np.float32)
rr = np.sqrt(((vx_ - W / 2) / (W * 0.62)) ** 2 + ((vy_ - H / 2) / (H * 0.60)) ** 2)
VIG = np.clip(1 - 0.45 * rr ** 2.2, 0.3, 1)[..., None].astype(np.float32); del vy_, vx_, rr
rng = np.random.default_rng(3)
GRAIN = [cv2.resize(rng.normal(0, 4.0, (H // 2, W // 2)).astype(np.float32), (W, H))[..., None] for _ in range(6)]
def bloom(f, lvl):
    sm = cv2.resize(f, (270, 480), interpolation=cv2.INTER_AREA)
    hl = cv2.GaussianBlur(np.clip(sm - 160, 0, None) * 1.6, (0, 0), 12)
    return f + cv2.resize(hl, (W, H)) * lvl * np.float32([0.8, 0.95, 1.1])

# ---------------- typography ----------------
def font(name, size): return ImageFont.truetype(os.path.join(FONTS, name), size)
TEKO = 'teko-latin-700-normal.woff'; CINZEL = 'cinzel-latin-500-normal.woff'
C = dict(white=(246, 246, 242), magenta=(236, 40, 226), cyan=(40, 214, 242), yellow=(250, 232, 40), red=(226, 26, 30))

def mk(text, fnt, color, fill=None):
    l, tp, r, b = fnt.getbbox(text); pad = 30
    im = Image.new('L', (r - l + 2 * pad, b - tp + 2 * pad), 0)
    ImageDraw.Draw(im).text((pad - l, pad - tp), text, font=fnt, fill=255)
    a = np.asarray(im, np.float32) / 255
    if fill is None: col = np.ones(a.shape + (3,), np.float32) * (np.float32(color[::-1]) / 255)
    else: col = fill(a.shape)
    return dict(a=a, col=col, ox=l - pad, oy=tp - pad, cache={})

def grad_fill(top, bot, noise=0.04):
    def f(shape):
        h, w = shape; g = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
        c = np.float32(top[::-1]) / 255 * (1 - g) + np.float32(bot[::-1]) / 255 * g
        c = np.broadcast_to(c, (h, w, 3)).copy()
        c *= 1 + rng.normal(0, noise, (h, w, 1)).astype(np.float32)
        return np.clip(c, 0, 1)
    return f
def metal_fill(shape):
    h, w = shape; y = np.linspace(0, 1, h, dtype=np.float32)
    v = 0.92 - 0.45 * np.exp(-((y - 0.52) / 0.10) ** 2) + 0.08 * np.sin(y * 9)
    v = np.clip(v, 0.3, 1)[:, None, None]
    c = np.broadcast_to(v * np.float32([0.86, 0.93, 1.0]), (h, w, 3)).copy()
    c *= 1 + rng.normal(0, 0.03, (h, w, 1)).astype(np.float32)
    return np.clip(c, 0, 1)

def scaled(sp, s, blur):
    key = (round(s * 50) / 50, round(blur * 2) / 2)
    if key not in sp['cache']:
        a, col = sp['a'], sp['col']
        if abs(key[0] - 1) > 1e-3:
            nh, nw = max(1, int(a.shape[0] * key[0])), max(1, int(a.shape[1] * key[0]))
            a = cv2.resize(a, (nw, nh), interpolation=cv2.INTER_LINEAR); col = cv2.resize(col, (nw, nh), interpolation=cv2.INTER_LINEAR)
        if key[1] > 0.25: a = cv2.GaussianBlur(a, (0, 0), key[1])
        if len(sp['cache']) > 60: sp['cache'].clear()
        sp['cache'][key] = (a, col)
    return sp['cache'][key]

class Layer:
    def __init__(self):
        self.C = np.zeros((H, W, 3), np.float32); self.A = np.zeros((H, W), np.float32); self.used = False
        self.glow = None
    def blit(self, sp, cx, cy, s=1.0, op=1.0, blur=0.0, anchor_center=True):
        """cx,cy = position of the sprite's text origin (unscaled coords); scale s about the sprite centre"""
        if op <= 0.003: return
        a, col = scaled(sp, s, blur); h, w = a.shape
        h0, w0 = sp['a'].shape
        # centre of unscaled sprite in frame coords
        mx = cx + sp['ox'] + w0 / 2; my = cy + sp['oy'] + h0 / 2
        x = int(round(mx - w / 2)); y = int(round(my - h / 2))
        x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + w), min(H, y + h)
        if x1 <= x0 or y1 <= y0: return
        aa = a[y0 - y:y1 - y, x0 - x:x1 - x] * op; cc = col[y0 - y:y1 - y, x0 - x:x1 - x]
        self.C[y0:y1, x0:x1] = cc * aa[..., None] + self.C[y0:y1, x0:x1] * (1 - aa[..., None])
        self.A[y0:y1, x0:x1] = aa + self.A[y0:y1, x0:x1] * (1 - aa); self.used = True

class Caption:
    """reference-style kinetic caption: words pop in on the sung syllable, line 2 in accent colour,
    letters dissolve out left->right"""
    def __init__(self, t_out, lines, y, size=130, align='center', x=None):
        self.t_out = t_out; self.items = []
        fnt = {}; lh = size * 0.98; sp_w = None
        for li, line in enumerate(lines):
            sz = size if not isinstance(line, tuple) else size
            words = line
            while True:
                fz = fnt.setdefault(sz, font(TEKO, sz)); sp_w = fz.getlength(' ') * 1.0
                ws = [fz.getlength(w) for w, _, _ in words]
                if sum(ws) + sp_w * (len(ws) - 1) <= 900 or sz < 60: break
                sz -= 6
            tot = sum(ws) + sp_w * (len(ws) - 1)
            xx = (W - tot) / 2 if align == 'center' else (x if align == 'left' else x - tot)
            for (w, ts, colr), ww in zip(words, ws):
                letters = []
                for i, ch in enumerate(w):
                    letters.append(dict(sp=mk(ch, fz, C[colr]), dx=fz.getlength(w[:i])))
                self.items.append(dict(x=xx, y=y + li * lh, w=ww, ts=ts, letters=letters))
                xx += ww + sp_w
        n = sum(len(it['letters']) for it in self.items); k = 0
        for it in self.items:
            for L in it['letters']: L['k'] = k; k += 1
        self.n = n; self.t_in = min(it['ts'] for it in self.items)
        for it in self.items: HITS.append(it['ts']) if False else None
    def active(self, t): return self.t_in - 0.05 <= t <= self.t_out + 0.02
    def draw(self, Lr, t):
        if not self.active(t): return
        for it in self.items:
            p = (t - it['ts']) / 0.13
            if p < 0: continue
            s = 1 + 0.22 * (1 - out_cubic(p)); op = clamp(p * 2.2); blur = (1 - out_cubic(p)) * 3
            wc = it['x'] + it['w'] / 2
            for L in it['letters']:
                te = self.t_out - 0.30 + 0.30 * L['k'] / max(1, self.n - 1) * 0.8
                q = clamp((t - te) / 0.12)
                lx = wc + (it['x'] + L['dx'] - wc) * s
                Lr.blit(L['sp'], lx, it['y'], s, op * (1 - q), blur + q * 6)

class Big:
    """huge single word on a cut: slams in (scale 1.45->1), slow push while held"""
    def __init__(self, t_in, t_out, text, fill, y=860):
        self.t_in, self.t_out = t_in, t_out; size = 420
        while True:
            fz = font(TEKO, size)
            if fz.getlength(text) <= 860: break
            size -= 10
        self.sp = mk(text, fz, None, fill); self.x = (W - fz.getlength(text)) / 2; self.y = y
        HITS.append(t_in)
    def active(self, t): return self.t_in <= t < self.t_out
    def draw(self, Lr, t):
        if not self.active(t): return
        p = (t - self.t_in) / 0.10
        s = (1 + 0.45 * (1 - out_cubic(p))) * (1 + 0.05 * (t - self.t_in))
        Lr.blit(self.sp, self.x, self.y, s, clamp(p * 3), (1 - out_cubic(p)) * 6)

class TitleCard:
    """wide-tracked title (DOOMSDAY-card style): letters drift apart, fade with blur"""
    def __init__(self, t_in, t_out, text, y=900):
        self.t_in, self.t_out, self.y = t_in, t_out, y
        fz = font(CINZEL, 96); self.ch = [dict(sp=mk(c, fz, (236, 236, 232)), w=fz.getlength(c)) for c in text]
        fs = font('montserrat-latin-400-normal.woff', 22)
    def active(self, t): return self.t_in <= t <= self.t_out
    def draw(self, Lr, t):
        if not self.active(t): return
        p = (t - self.t_in) / (self.t_out - self.t_in)
        tr = lerp(34, 58, out_cubic(p)); op = smooth((t - self.t_in) / 0.35) * (1 - smooth((t - (self.t_out - 0.3)) / 0.3))
        tot = sum(c['w'] for c in self.ch) + tr * (len(self.ch) - 1); x = (W - tot) / 2
        for i, c in enumerate(self.ch):
            q = out_cubic((t - self.t_in - 0.04 * i) / 0.45)
            Lr.blit(c['sp'], x, self.y, 1.0, op * q, (1 - q) * 8); x += c['w'] + tr
        # thin rules like the reference title card
        w2 = tot * 0.5 * out_cubic((t - self.t_in) / 0.8)
        y0 = int(self.y + 150)
        if op > 0: Lr.C[y0:y0 + 2, int(W / 2 - w2):int(W / 2 + w2)] = 0.9; Lr.A[y0:y0 + 2, int(W / 2 - w2):int(W / 2 + w2)] = op * 0.7; Lr.used = True

class Logo:
    """metallic JESUS with warm glow and a light sweep (closing logo, reference style)"""
    def __init__(self, t_in, t_out, text, y=780):
        self.t_in, self.t_out = t_in, t_out; size = 520
        while True:
            fz = font(TEKO, size)
            if fz.getlength(text) <= 900: break
            size -= 10
        self.sp = mk(text, fz, None, metal_fill); self.x = (W - fz.getlength(text)) / 2; self.y = y
        a = self.sp['a']; g = cv2.GaussianBlur(a, (0, 0), 3)
        gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3); gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
        bevel = np.clip(-(gy + gx * 0.5) * 2.2, -0.5, 0.6)[..., None]
        self.sp['col'] = np.clip(self.sp['col'] + bevel, 0, 1)
        self.base_col = self.sp['col'].copy()
        HITS.append(t_in)
    def active(self, t): return self.t_in <= t <= self.t_out
    def draw(self, Lr, t):
        if not self.active(t): return
        p = (t - self.t_in) / 0.5
        s = (1 + 0.25 * (1 - out_cubic(p))) * (1 + 0.025 * (t - self.t_in))
        op = clamp(p * 1.6) * (1 - smooth((t - (self.t_out - 0.7)) / 0.7))
        # light sweep
        h, w = self.sp['a'].shape; sw = (t - self.t_in - 0.6) / 1.1
        xx = np.arange(w, dtype=np.float32)[None, :] / w; yy = np.arange(h, dtype=np.float32)[:, None] / h
        band = np.exp(-((xx + yy * 0.35 - lerp(-0.4, 1.4, sw)) / 0.06) ** 2)[..., None] if 0 <= sw <= 1 else 0
        self.sp['col'] = np.clip(self.base_col + band * 0.9, 0, 1); self.sp['cache'] = {}
        Lr.blit(self.sp, self.x, self.y, s, op, (1 - out_cubic(p)) * 10)
        Lr.glow = op * (0.9 + 0.25 * math.exp(-((t - self.t_in - 0.1) / 0.25) ** 2))

W_ = 'white'
TEXT = [
 Caption(3.00, [[('SEM', 1.68, W_), ('TI,', 2.04, W_)]], 1150, 150),
 Caption(4.30, [[('SEM', 3.04, 'magenta'), ('TI', 4.04, 'magenta')]], 1080, 160),
 Caption(6.55, [[('EU', 4.36, W_), ('NADA', 4.64, W_)], [('POSSO', 4.92, 'yellow'), ('FAZER', 5.36, 'yellow')]], 1230, 140, 'left', 100),
 Caption(9.65, [[('É', 6.84, W_), ('TUDO', 7.88, W_)], [('SOBRE', 8.26, 'cyan'), ('VOCÊ,', 9.04, 'cyan')]], 1180, 150),
 Caption(11.55, [[('TUDO', 9.88, W_), ('PRA', 10.48, W_), ('VOCÊ,', 10.86, W_)]], 1120, 170),
 Caption(13.65, [[('JESUS', 11.96, 'red')]], 1200, 250),
 Caption(15.90, [[('VOCÊ', 14.80, W_), ('É', 15.78, W_)]], 1200, 150, 'left', 110),
 Big(16.16, 17.14, 'SANTO,', grad_fill((255, 255, 255), (214, 214, 220))),
 Big(17.14, 18.06, 'SANTO,', grad_fill((255, 255, 255), (214, 214, 220))),
 Big(18.06, 18.95, 'SANTO', grad_fill((255, 236, 170), (226, 158, 50))),
 Big(19.00, 20.48, 'SANTO,', grad_fill((255, 255, 255), (214, 214, 220))),
 Big(20.48, 21.96, 'SANTO,', grad_fill((255, 255, 255), (214, 214, 220))),
 Big(21.96, 22.76, 'SANTO', grad_fill((250, 120, 220), (140, 60, 210))),
 Caption(25.30, [[('É', 22.80, W_), ('TUDO', 23.38, W_)], [('SOBRE', 23.78, 'cyan'), ('VOCÊ,', 24.54, 'cyan')]], 1230, 150),
 Caption(27.04, [[('TUDO', 25.36, W_), ('PRA', 25.88, W_), ('VOCÊ,', 26.32, W_)]], 1200, 165),
 Caption(29.40, [[('JESUS', 27.08, 'red')]], 1250, 260),
 Caption(31.55, [[('VOCÊ', 29.90, W_), ('É', 30.95, W_)]], 1230, 160),
 Big(31.62, 32.62, 'SANTO,', grad_fill((255, 255, 255), (214, 214, 220))),
 Big(32.62, 33.56, 'SANTO,', grad_fill((255, 255, 255), (214, 214, 220))),
 Big(33.56, 34.40, 'SANTO', grad_fill((150, 245, 255), (30, 160, 230))),
 Big(34.44, 36.16, 'SANTO,', grad_fill((255, 255, 255), (214, 214, 220))),
 Big(36.16, 37.38, 'SANTO,', grad_fill((255, 255, 255), (214, 214, 220))),
 Big(37.38, 38.17, 'SANTO', grad_fill((255, 90, 80), (180, 14, 24))),
 Caption(40.75, [[('É', 38.22, W_), ('TUDO', 38.90, W_)], [('SOBRE', 39.20, 'yellow'), ('VOCÊ,', 40.02, 'yellow')]], 1230, 150, 'left', 100),
 Caption(42.70, [[('TUDO', 40.80, W_), ('PRA', 41.38, W_), ('VOCÊ,', 41.82, W_)]], 1150, 170),
 Caption(44.05, [[('JESUS', 42.76, 'red')]], 1250, 260),
 TitleCard(44.15, 45.50, 'BATISMO', 880),
 Caption(47.05, [[('VOCÊ', 45.58, W_), ('É', 46.74, W_)]], 1230, 160),
 Caption(48.30, [[('SANTO,', 47.08, 'magenta'), ('SANTO,', 48.10, 'magenta')]], 1200, 160),
 Caption(51.70, [[('SANTO,', 49.06, W_)], [('SANTO,', 49.94, 'yellow'), ('SANTO', 51.44, 'yellow')]], 1220, 160),
 Caption(53.70, [[('SANTO', 52.90, 'cyan')]], 1200, 220),
 Caption(56.30, [[('É', 53.74, W_), ('TUDO', 54.40, W_)], [('SOBRE', 54.84, 'cyan'), ('VOCÊ,', 55.56, 'cyan')]], 1230, 150, 'left', 100),
 Caption(58.28, [[('TUDO', 56.34, W_), ('PRA', 56.88, W_)], [('VOCÊ,', 57.34, 'red')]], 1180, 170),
 Logo(58.32, 61.85, 'JESUS', 760),
]
for tx in TEXT:
    if isinstance(tx, Caption):
        for it in tx.items: HITS.append(it['ts']) if it['ts'] in (11.96, 27.08, 42.76) else None

SH = [Shot(s) for s in SHOTS]
def frame(n):
    t = n / FPS
    i = max(k for k, s in enumerate(SHOTS) if s['t0'] <= t + 1e-6); cur = SH[i]
    kind, d = TRANS.get(SHOTS[i]['id'], ('cut', 0))
    nk, nd = TRANS.get(SHOTS[i + 1]['id'], ('cut', 0)) if i + 1 < len(SHOTS) else ('cut', 0)
    if kind not in ('cut', 'fadein') and i > 0 and t < cur.s['t0'] + d:
        f = transition(SH[i - 1], cur, kind, cur.s['t0'], d, t)
    elif nk != 'cut' and i + 1 < len(SHOTS) and t >= SHOTS[i + 1]['t0'] - nd:
        f = transition(cur, SH[i + 1], nk, SHOTS[i + 1]['t0'], nd, t)
    else:
        f = view(cur, t).astype(np.float32)
    # slam flash on every big word / key hit
    for at in HITS:
        if at - 0.04 <= t < at + 0.3:
            k = 0.20 * math.exp(-((t - at) / 0.07) ** 2); f = f + (255 - f) * k
    f = bloom(f, 0.32)
    f *= VIG
    if t < 0.9: f *= out_cubic(t / 0.9)
    Lr = Layer()
    for tx in TEXT: tx.draw(Lr, t)
    for tx in TEXT:
        if isinstance(tx, TitleCard) and tx.active(t):
            f *= 1 - 0.5 * smooth((t - tx.t_in) / 0.3) * (1 - smooth((t - (tx.t_out - 0.25)) / 0.25))
    if t > 58.0:  # logo background: darken + warm glow
        k = smooth((t - 58.3) / 0.4); f *= 1 - 0.45 * k
    if t > 60.9: f *= 1 - smooth((t - 60.9) / 1.0)
    if Lr.used:
        if Lr.glow:
            g = cv2.GaussianBlur(Lr.A, (0, 0), 28)[..., None] * np.float32([70, 170, 255]) * 1.3 * Lr.glow
            g2 = cv2.GaussianBlur(Lr.A, (0, 0), 90)[..., None] * np.float32([40, 120, 255]) * 1.2 * Lr.glow
            f = f + g + g2
        sh = np.roll(cv2.GaussianBlur(Lr.A, (0, 0), 6), 6, axis=0)[..., None]
        f *= 1 - 0.65 * sh
        a = Lr.A[..., None]; f = f * (1 - a) + Lr.C * 255
    if t > 61.0: f *= 1 - smooth((t - 61.0) / 0.9)
    f += GRAIN[n % len(GRAIN)]
    return np.clip(f, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    a, b, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    lossless = out.endswith('.mkv')
    enc = ['-c:v', 'libx264', '-preset', 'ultrafast', '-qp', '0', '-pix_fmt', 'yuv444p'] if lossless else \
          ['-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p']
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-'] + enc + [out], stdin=subprocess.PIPE)
    for n in range(a, b):
        p.stdin.write(frame(n).tobytes())
        if (n - a) % 60 == 0: print(out, n, flush=True)
    p.stdin.close(); p.wait()
