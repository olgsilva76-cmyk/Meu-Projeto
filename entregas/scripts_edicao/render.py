import os, sys, json, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from shots import SHOTS, TRANS, ACCENTS, FPS, W, H, DUR, HANDLE
from prep import src_fn

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREP = os.path.join(ROOT, 'prep'); FONTS = os.path.join(ROOT, 'fonts', 'use')
cv2.setNumThreads(1)

# ---------------- easing ----------------
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def sine_io(x): x = clamp(x); return 0.5 - 0.5 * math.cos(math.pi * x)
def out_cubic(x): x = clamp(x); return 1 - (1 - x) ** 3
def in_cubic(x): x = clamp(x); return x ** 3
def out_expo(x): x = clamp(x); return 1 if x >= 1 else 1 - 2 ** (-10 * x)
def lerp(a, b, p): return a + (b - a) * p
def env(t, a, b, fi, fo):
    """1 inside [a,b] with fade in/out lengths"""
    return clamp((t - a) / fi) * clamp((b - t) / fo) if fi > 0 and fo > 0 else 0

# ---------------- shots ----------------
class Shot:
    def __init__(self, s):
        self.s = s; self.meta = json.load(open(os.path.join(PREP, s['id'] + '.json')))
        self.f, _, _ = src_fn(s); self.cap = None; self.idx = -1; self.frame = None
        self.d = s['t1'] - s['t0']
    def raw(self, t):
        src = self.f(t - self.s['t0'])
        i = int(round((src - self.meta['srcA']) / self.meta['base'] * FPS))
        i = max(0, min(self.meta['nframes'] - 1, i))
        if self.cap is None or i < self.idx:
            if self.cap is not None: self.cap.release()
            self.cap = cv2.VideoCapture(os.path.join(PREP, self.s['id'] + '.mp4')); self.idx = -1
        while self.idx < i:
            ok, fr = self.cap.read()
            if not ok: break
            self.frame = fr; self.idx += 1
        return self.frame
    def close(self):
        if self.cap is not None: self.cap.release(); self.cap = None

def pulse_amt(t):
    v = 0.0
    for at, k in ACCENTS:
        if k == 'pulse' and t >= at: v += 0.035 * math.exp(-(t - at) / 0.18)
    return v

def view(sh, t, z=1.0, tx=0.0, ty=0.0, img=None):
    s0, s1, dx0, dy0, dx1, dy1 = sh.s['move']
    p = sine_io((t - sh.s['t0']) / sh.d)
    sc = lerp(s0, s1, p) * z * (1 + pulse_amt(t))
    dx = lerp(dx0, dx1, p) + tx; dy = lerp(dy0, dy1, p) + ty
    img = sh.raw(t) if img is None else img
    M = np.float32([[sc, 0, (1 - sc) * W / 2 + dx], [0, sc, (1 - sc) * H / 2 + dy]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)

def zoomblur(sh, t, z, amt, n=7):
    img = sh.raw(t); acc = np.zeros((H, W, 3), np.float32)
    for k in range(n):
        acc += view(sh, t, z * (1 + amt * k / (n - 1)), img=img)
    return acc / n

def hblur(img, k):
    k = int(k) | 1
    return cv2.blur(img, (k, 1)) if k > 1 else img

# diagonal coordinate for mask wipes (low-res)
LW, LH = 135, 240
yy, xx = np.mgrid[0:LH, 0:LW].astype(np.float32)
DIAG = (0.62 * xx / LW + 0.38 * yy / LH)

def transition(A, B, kind, tc, d, t):
    """returns float32 BGR frame and extra leak amount"""
    if kind == 'cut':
        return (view(A, t) if t < tc else view(B, t)).astype(np.float32), 0
    if kind in ('dissolve', 'leak'):
        a = sine_io((t - (tc - d)) / (2 * d))
        f = view(A, t).astype(np.float32) * (1 - a) + view(B, t).astype(np.float32) * a
        return f, (0.55 if kind == 'leak' else 0.12) * math.sin(math.pi * a)
    if kind == 'zoom':
        if t < tc:
            p = (t - (tc - d)) / d
            f = zoomblur(A, t, 1 + in_cubic(p) * 0.55, in_cubic(p) * 0.22)
        else:
            p = (t - tc) / d
            f = zoomblur(B, t, 1 - (1 - out_cubic(p)) * 0.22, (1 - out_cubic(p)) * 0.22)
        return f, 0.08
    if kind == 'whip':
        if t < tc:
            p = in_cubic((t - (tc - d)) / d)
            f = hblur(view(A, t, tx=-p * W * 0.55), 1 + p * 260)
        else:
            p = 1 - out_cubic((t - tc) / d)
            f = hblur(view(B, t, tx=p * W * 0.55), 1 + p * 260)
        return f.astype(np.float32), 0
    if kind == 'flash':
        f = (view(A, t) if t < tc else view(B, t)).astype(np.float32)
        w = 0.05 if t < tc else d * 0.55
        k = 0.55 * math.exp(-((t - tc) / w) ** 2)
        return f + (255 - f) * k, 0.1 * k
    if kind == 'mask':
        p = sine_io((t - (tc - d)) / (2 * d)); pos = lerp(-0.2, 1.2, p)
        m = np.clip((pos - DIAG) / 0.14, 0, 1)
        e = np.exp(-((pos - DIAG) / 0.05) ** 2) * math.sin(math.pi * p) * 0.55
        m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
        e = cv2.resize(e, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
        f = view(A, t).astype(np.float32) * (1 - m) + view(B, t).astype(np.float32) * m
        f += e * np.float32([150, 210, 255])
        return f, 0.15 * math.sin(math.pi * p)
    raise ValueError(kind)

# ---------------- atmosphere ----------------
def section_level(t, table):
    # table: list of (time, value), linear interpolation
    for (a, va), (b, vb) in zip(table, table[1:]):
        if t <= b: return lerp(va, vb, smooth((t - a) / (b - a)))
    return table[-1][1]

LEAK_LV = [(0, .30), (4, .20), (15.5, .20), (16.5, .08), (31, .08), (32, .12), (48, .12), (49, .30), (52, .22), (56, .26), (62, .26)]
PART_LV = [(0, .9), (15.5, .9), (16.5, .25), (31, .25), (32, .35), (48, .35), (49, 1.0), (62, 1.0)]
BLOOM_LV = [(0, .40), (15.5, .40), (16.5, .25), (48, .25), (49, .45), (62, .45)]

lyy, lxx = np.mgrid[0:LH, 0:LW].astype(np.float32); lxx /= LW; lyy /= LH
def leak(t, lvl):
    acc = np.zeros((LH, LW, 3), np.float32)
    blobs = [((0.05 + 0.25 * math.sin(0.23 * t), 0.08 + 0.10 * math.sin(0.17 * t + 1)), 0.55, (40, 140, 255)),
             ((0.95 - 0.20 * math.sin(0.19 * t + 2), 0.35 + 0.25 * math.sin(0.11 * t)), 0.40, (80, 120, 245)),
             ((0.50 + 0.35 * math.sin(0.13 * t + 4), 0.95), 0.50, (110, 190, 255))]
    for (cx, cy), r, col in blobs:
        g = np.exp(-(((lxx - cx) * 1.0) ** 2 + ((lyy - cy) * 0.56) ** 2) / (r * r * 0.35))
        acc += g[..., None] * np.float32(col)
    acc = np.clip(acc * lvl, 0, 255)
    return cv2.resize(acc, (W, H), interpolation=cv2.INTER_CUBIC)

rng = np.random.default_rng(7)
NP = 90
P = dict(x=rng.uniform(0, W, NP), y=rng.uniform(0, H, NP), vy=rng.uniform(8, 45, NP), amp=rng.uniform(8, 45, NP),
         fr=rng.uniform(0.1, 0.4, NP), ph=rng.uniform(0, 6.28, NP), r=rng.choice([1.5, 2, 2.5, 3, 4, 6, 9], NP,
         p=[.2, .2, .2, .15, .12, .08, .05]), a=rng.uniform(0.25, 0.8, NP))
SPR = {}
for r in set(P['r'].tolist()):
    s = int(r * 4) | 1; c = s // 2; g = np.mgrid[0:s, 0:s].astype(np.float32)
    SPR[r] = np.exp(-((g[0] - c) ** 2 + (g[1] - c) ** 2) / (2 * (r * 0.8) ** 2))[..., None] * np.float32([200, 235, 255])
def particles(f, t, lvl):
    if lvl < 0.02: return
    for i in range(NP):
        r = P['r'][i]; spr = SPR[r]; s = spr.shape[0]
        x = (P['x'][i] + P['amp'][i] * math.sin(P['fr'][i] * t * 6.28 + P['ph'][i])) % W
        y = (P['y'][i] - P['vy'][i] * t) % H
        a = P['a'][i] * lvl * (0.65 + 0.35 * math.sin(t * 2.1 + P['ph'][i] * 3)) * (0.6 if r >= 6 else 1)
        x0, y0 = int(x) - s // 2, int(y) - s // 2
        if x0 < 0 or y0 < 0 or x0 + s > W or y0 + s > H: continue
        f[y0:y0 + s, x0:x0 + s] += spr * a

vy_, vx_ = np.mgrid[0:H, 0:W].astype(np.float32)
rr = np.sqrt(((vx_ - W / 2) / (W * 0.62)) ** 2 + ((vy_ - H / 2) / (H * 0.60)) ** 2)
VIG = np.clip(1 - 0.42 * rr ** 2.4, 0.35, 1)[..., None].astype(np.float32)
del vy_, vx_, rr
GRAIN = [rng.normal(0, 4.2, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
GRAIN = [cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)[..., None] for g in GRAIN]

def bloom(f, lvl):
    sm = cv2.resize(f, (270, 480), interpolation=cv2.INTER_AREA)
    hl = np.clip(sm - 165, 0, None) * 1.6
    hl = cv2.GaussianBlur(hl, (0, 0), 14)
    return f + cv2.resize(hl, (W, H), interpolation=cv2.INTER_LINEAR) * lvl * np.float32([0.85, 0.95, 1.05])

# ---------------- typography ----------------
def font(name, size): return ImageFont.truetype(os.path.join(FONTS, name), size)
F_VERSE = 'cormorant-garamond-latin-500-italic.woff'
F_TITLE = 'cinzel-latin-500-normal.woff'
F_SANS = 'montserrat-latin-400-normal.woff'
WHITE = (250, 246, 238); GOLD = (240, 212, 160)

def sprite(text, fnt, color):
    l, tp, r, b = fnt.getbbox(text); pad = 40
    im = Image.new('L', (r - l + 2 * pad, b - tp + 2 * pad), 0)
    ImageDraw.Draw(im).text((pad - l, pad - tp), text, font=fnt, fill=255)
    a = np.asarray(im, np.float32) / 255
    col = np.float32(color[::-1]) / 255  # BGR
    return dict(a=a, col=col, ox=l - pad, oy=tp - pad, cache={})
def spr_get(sp, blur):
    q = round(blur * 2) / 2
    if q not in sp['cache']:
        a = cv2.GaussianBlur(sp['a'], (0, 0), q) if q > 0.25 else sp['a']
        sp['cache'][q] = a
    return sp['cache'][q]

class Layer:
    def __init__(self): self.C = np.zeros((H, W, 3), np.float32); self.A = np.zeros((H, W), np.float32); self.used = False
    def blit(self, sp, x, y, op, blur=0.0):
        if op <= 0.003: return
        a = spr_get(sp, blur) * op; x = int(round(x + sp['ox'])); y = int(round(y + sp['oy']))
        h, w = a.shape; x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + w), min(H, y + h)
        if x1 <= x0 or y1 <= y0: return
        a = a[y0 - y:y1 - y, x0 - x:x1 - x]
        self.C[y0:y1, x0:x1] = sp['col'] * a[..., None] + self.C[y0:y1, x0:x1] * (1 - a[..., None])
        self.A[y0:y1, x0:x1] = a + self.A[y0:y1, x0:x1] * (1 - a); self.used = True
    def rect(self, x0, y0, x1, y1, color, op):
        if op <= 0.003 or x1 <= x0: return
        x0, x1 = int(x0), int(math.ceil(x1)); y0, y1 = int(y0), int(math.ceil(y1))
        self.C[y0:y1, x0:x1] = np.float32(color[::-1]) / 255 * op + self.C[y0:y1, x0:x1] * (1 - op)
        self.A[y0:y1, x0:x1] = op + self.A[y0:y1, x0:x1] * (1 - op); self.used = True

class Verse:
    """word-by-word blur/rise reveal, gold emphasis, tracked reference with growing rule"""
    def __init__(self, t_in, t_out, lines, ref, yc, size=72):
        self.t_in, self.t_out, self.yc = t_in, t_out, yc
        fv = font(F_VERSE, size); self.sp_space = fv.getlength(' ')
        self.lines = []; k = 0; lh = size * 1.22
        for li, line in enumerate(lines):
            words = []
            for w in line.split(' '):
                gold = w.startswith('*'); w = w.strip('*')
                words.append(dict(sp=sprite(w, fv, GOLD if gold else WHITE), w=fv.getlength(w), k=k)); k += 1
            tot = sum(x['w'] for x in words) + self.sp_space * (len(words) - 1)
            x = (W - tot) / 2
            for wd in words: wd['x'] = x; x += wd['w'] + self.sp_space
            self.lines.append(dict(words=words, y=yc - (len(lines) - 1) * lh / 2 + li * lh - size * 0.55))
        self.nw = k
        fr = font(F_SANS, 28); self.ref = [dict(sp=sprite(c, fr, (225, 215, 200)), w=fr.getlength(c)) for c in ref]
        self.ref_y = yc + (len(lines) - 1) * lh / 2 + size * 1.45
        self.ref_t = t_in + 0.14 * k + 0.35
    def vis(self, t): return env(t, self.t_in, self.t_out, 0.6, 0.7)
    def draw(self, L, t):
        if t < self.t_in - 0.1 or t > self.t_out + 0.1: return
        for ln in self.lines:
            for wd in ln['words']:
                ts = self.t_in + 0.14 * wd['k']; p = out_cubic((t - ts) / 0.75)
                te = self.t_out - 0.7 + 0.04 * wd['k']; q = in_cubic((t - te) / 0.6)
                op = p * (1 - q); blur = (1 - p) * 9 + q * 7; dy = (1 - p) * 28 - q * 16
                L.blit(wd['sp'], wd['x'], ln['y'] + dy, op, blur)
        # reference: rule grows from centre, letters tighten tracking
        p = out_expo((t - self.ref_t) / 1.4); q = in_cubic((t - (self.t_out - 0.6)) / 0.6)
        op = smooth((t - self.ref_t) / 0.6) * (1 - q)
        rw = 70 * out_cubic((t - self.ref_t + 0.15) / 0.9) * (1 - q)
        L.rect(W / 2 - rw, self.ref_y - 22, W / 2 + rw, self.ref_y - 20.5, (225, 205, 170), 0.8 * (1 - q))
        tr = lerp(22, 9, p)
        tot = sum(c['w'] for c in self.ref) + tr * (len(self.ref) - 1); x = (W - tot) / 2
        for c in self.ref:
            L.blit(c['sp'], x, self.ref_y, op * 0.92, (1 - p) * 3); x += c['w'] + tr

class Title:
    def __init__(self, t_in, t_out, l1, l2, sub, yc):
        self.t_in, self.t_out, self.yc = t_in, t_out, yc
        size = 112; self.final_tr = 16
        while True:
            ft = font(F_TITLE, size)
            wmax = max(sum(ft.getlength(c) for c in s) + self.final_tr * (len(s) - 1) for s in (l1, l2))
            if wmax <= 880: break
            size -= 4
        self.size = size
        self.l = [[dict(sp=sprite(c, ft, WHITE), w=ft.getlength(c)) for c in s] for s in (l1, l2)]
        fs = font(F_SANS, 28); self.sub = [dict(sp=sprite(c, fs, (230, 214, 186)), w=fs.getlength(c)) for c in sub]
    def vis(self, t): return env(t, self.t_in, self.t_out, 0.8, 0.6)
    def draw(self, L, t):
        if t < self.t_in - 0.1: return
        fade = 1 - smooth((t - (self.t_out - 0.6)) / 0.6)
        for li, chars in enumerate(self.l):
            t0 = self.t_in + li * 0.45
            p = out_expo((t - t0) / 3.2); tr = lerp(70, self.final_tr, p)
            n = len(chars); tot = sum(c['w'] for c in chars) + tr * (n - 1); x = (W - tot) / 2
            y = self.yc - self.size * 0.62 + li * self.size * 1.18 - self.size * 0.6
            for j, c in enumerate(chars):
                dly = abs(j - (n - 1) / 2) * 0.07
                q = out_cubic((t - t0 - dly) / 1.1)
                if li == 1:  # second line rises from a mask
                    pass
                L.blit(c['sp'], x, y + (1 - q) * (22 if li == 0 else -22), q * fade, (1 - q) * 12)
                x += c['w'] + tr
        ts = self.t_in + 1.5; p = out_expo((t - ts) / 1.6); op = smooth((t - ts) / 0.8) * fade
        tr = lerp(26, 12, p); n = len(self.sub)
        tot = sum(c['w'] for c in self.sub) + tr * (n - 1); x = (W - tot) / 2
        ys = self.yc + self.size * 1.45
        for c in self.sub: L.blit(c['sp'], x, ys, op * 0.9, (1 - p) * 3); x += c['w'] + tr
        rw = 60 * out_cubic((t - ts) / 1.2) * fade
        L.rect(W / 2 - tot / 2 - 30 - rw, ys + 10, W / 2 - tot / 2 - 30, ys + 11.5, (225, 205, 170), 0.7 * fade)
        L.rect(W / 2 + tot / 2 + 30, ys + 10, W / 2 + tot / 2 + 30 + rw, ys + 11.5, (225, 205, 170), 0.7 * fade)

class Lyric:
    """song lyric block: each word blooms in (blur->sharp, rise) exactly when it is sung"""
    def __init__(self, t_in, t_out, lines, yc=1360, size=76):
        self.t_in, self.t_out, self.yc = t_in, t_out, yc
        fv = font(F_VERSE, size); sp = fv.getlength(' '); lh = size * 1.2
        self.lines = []; k = 0
        for li, line in enumerate(lines):
            words = []
            for w, ts in line:
                gold = w.startswith('*'); w = w.strip('*')
                words.append(dict(sp=sprite(w, fv, GOLD if gold else WHITE), w=fv.getlength(w), ts=max(ts - 0.10, t_in), k=k)); k += 1
            tot = sum(x['w'] for x in words) + sp * (len(words) - 1); x = (W - tot) / 2
            for wd in words: wd['x'] = x; x += wd['w'] + sp
            self.lines.append(dict(words=words, y=yc - (len(lines) - 1) * lh / 2 + li * lh - size * 0.55))
    def vis(self, t): return env(t, self.t_in, self.t_out, 0.5, 0.5)
    def draw(self, L, t):
        if t < self.t_in - 0.1 or t > self.t_out + 0.1: return
        for ln in self.lines:
            for wd in ln['words']:
                p = out_cubic((t - wd['ts']) / 0.45)
                q = in_cubic((t - (self.t_out - 0.45 + 0.025 * wd['k'])) / 0.4)
                op = p * (1 - q); blur = (1 - p) * 8 + q * 6; dy = (1 - p) * 22 - q * 14
                L.blit(wd['sp'], wd['x'], ln['y'] + dy, op, blur)

# Lyrics of the 03:05–04:07 section, word times from Whisper large-v3 transcription of the track (clip seconds)
TEXTS = [
    Lyric(1.25, 6.45, [[('Sem', 1.68), ('Ti,', 2.04), ('sem', 3.04), ('Ti', 4.04)],
                       [('eu', 4.36), ('nada', 4.64), ('posso', 4.92), ('fazer', 5.36)]]),
    Lyric(6.60, 12.75, [[('É', 6.84), ('tudo', 7.88), ('sobre', 8.26), ('você,', 9.04)],
                        [('tudo', 9.88), ('pra', 10.48), ('você,', 10.86), ('*Jesus*', 11.96)]]),
    Lyric(13.90, 18.85, [[('Você', 14.80), ('é', 15.78), ('santo,', 16.16)], [('santo,', 17.14), ('santo', 18.06)]]),
    Lyric(18.90, 22.60, [[('Santo,', 19.00), ('santo,', 20.48), ('santo', 21.96)]]),
    Lyric(22.65, 28.30, [[('É', 22.80), ('tudo', 23.38), ('sobre', 23.78), ('você,', 24.54)],
                         [('tudo', 25.36), ('pra', 25.88), ('você,', 26.32), ('*Jesus*', 27.08)]]),
    Lyric(29.40, 34.30, [[('Você', 29.90), ('é', 30.95), ('santo,', 31.62)], [('santo,', 32.62), ('santo', 33.56)]]),
    Lyric(34.35, 38.10, [[('Santo,', 34.44), ('santo,', 36.16), ('santo', 37.38)]]),
    Lyric(38.15, 44.00, [[('É', 38.22), ('tudo', 38.90), ('sobre', 39.20), ('você,', 40.02)],
                         [('tudo', 40.80), ('pra', 41.38), ('você,', 41.82), ('*Jesus*', 42.76)]]),
    Lyric(44.90, 49.85, [[('Você', 45.58), ('é', 46.74), ('santo,', 47.08)], [('santo,', 48.10), ('santo', 49.06)]]),
    Lyric(49.90, 53.60, [[('Santo,', 49.94), ('santo,', 51.44), ('santo', 52.90)]]),
    Lyric(53.65, 61.70, [[('É', 53.74), ('tudo', 54.40), ('sobre', 54.84), ('você,', 55.56)],
                         [('tudo', 56.34), ('pra', 56.88), ('você,', 57.34), ('*Jesus*', 58.32)]]),
]
ROWS = np.arange(H, dtype=np.float32)[:, None, None]

# ---------------- frame ----------------
SH = [Shot(s) for s in SHOTS]
def frame(n):
    t = n / FPS
    i = max(k for k, s in enumerate(SHOTS) if s['t0'] <= t + 1e-6)
    cur = SH[i]; extra = 0
    kind, d = TRANS[SHOTS[i]['id']]
    nk, nd = TRANS[SHOTS[i + 1]['id']] if i + 1 < len(SHOTS) else ('cut', 0)
    if kind not in ('cut', 'fadein') and i > 0 and t < cur.s['t0'] + d:
        f, extra = transition(SH[i - 1], cur, kind, cur.s['t0'], d, t)
    elif nk not in ('cut',) and i + 1 < len(SHOTS) and t >= SHOTS[i + 1]['t0'] - nd:
        f, extra = transition(cur, SH[i + 1], nk, SHOTS[i + 1]['t0'], nd, t)
    else:
        f = view(cur, t).astype(np.float32)
    # accents (bloom flash on hits)
    for at, k in ACCENTS:
        if k == 'bloom' and abs(t - at) < 0.6:
            a = 0.22 * math.exp(-((t - at) / (0.05 if t < at else 0.28)) ** 2); f = f + (255 - f) * a
    lk = section_level(t, LEAK_LV) + extra
    L = leak(t, lk)
    f = 255 - (255 - f) * (255 - L) / 255
    f = bloom(f, section_level(t, BLOOM_LV))
    particles(f, t, section_level(t, PART_LV))
    f *= VIG
    # legibility band behind text
    for tx in TEXTS:
        v = tx.vis(t)
        if v > 0: f *= 1 - 0.34 * v * np.exp(-((ROWS - tx.yc) / 260) ** 2)
    # global fades (image)
    if t < 1.6: f *= out_cubic(t / 1.6) ** 1.2
    if t > 60.1: f *= 1 - smooth((t - 60.1) / 1.35)
    # typography
    Lr = Layer()
    for tx in TEXTS: tx.draw(Lr, t)
    if Lr.used:
        sh = cv2.GaussianBlur(Lr.A, (0, 0), 7); sh = np.roll(sh, 4, axis=0)[..., None]
        f *= 1 - 0.55 * sh
        glow = cv2.GaussianBlur(Lr.C, (0, 0), 16) * 255 * 0.35
        f = f + glow * np.float32([0.75, 0.9, 1.1])
        a = Lr.A[..., None]; f = f * (1 - a) + Lr.C * 255
    f += GRAIN[n % len(GRAIN)]
    return np.clip(f, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    a, b, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'ultrafast', '-qp', '0', '-pix_fmt', 'yuv444p',
                          '-x264-params', 'keyint=60', out], stdin=subprocess.PIPE)
    for n in range(a, b):
        p.stdin.write(frame(n).tobytes())
        if (n - a) % 60 == 0: print(out, n, flush=True)
    p.stdin.close(); p.wait()
