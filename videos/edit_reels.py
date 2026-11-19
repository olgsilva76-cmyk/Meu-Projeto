import sys, subprocess, math, random
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

SRC, OUT, S = sys.argv[1], sys.argv[2], sys.argv[3]
OFFSET = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0     # source time 0 = song time OFFSET
CUT_SRC = float(sys.argv[5]) if len(sys.argv) > 5 else 5.68   # look change, in source time
W, H, FPS = 1080, 1920, 30
CUT = CUT_SRC + OFFSET
ANTON = f"{S}/bebas/BebasNeue_Complete/Fonts/OTF/BebasNeue-Regular.otf"  # Bebas Neue
MARK = f"{S}/fonts/PermanentMarker-Regular.ttf"

# ---------- read frames ----------
cap = cv2.VideoCapture(SRC)
frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    if f.shape[1] > 700:
        f = cv2.resize(f, (f.shape[1] // 2, f.shape[0] // 2), interpolation=cv2.INTER_AREA)
    frames.append(f)
N = len(frames)
print("frames", N)

# ---------- models ----------
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path=f"{S}/models/seg.tflite"),
    output_confidence_masks=True))
fd = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(
    base_options=mpt.BaseOptions(model_asset_path=f"{S}/models/face.tflite"),
    min_detection_confidence=0.5))

# ---------- lighting ----------
def lum(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).mean()

cut_i = int(math.ceil(CUT_SRC * FPS))
ref = np.array([f.reshape(-1, 3).mean(0) for f in frames[:cut_i]]).mean(0)  # BGR mean part 1
target_y = np.mean([lum(f) for f in frames[:cut_i]]) - 2

def relight(img):
    f = img.astype(np.float32) / 255.0
    # partial white balance toward part-1 colour cast
    m = f.reshape(-1, 3).mean(0) + 1e-6
    g = (ref / 255.0) / m
    g = g / g.mean()
    g = 1 + 0.45 * (g - 1)
    f = np.clip(f * g, 0, 1)
    # exposure via gamma so midtones rise but highlights don't clip
    y = cv2.cvtColor((f * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).mean() / 255.0
    gamma = math.log(target_y / 255.0) / math.log(max(y, 1e-3))
    f = np.power(f, gamma)
    # local contrast / shadow lift in L channel
    lab = cv2.cvtColor((f * 255).astype(np.uint8), cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=0.5, tileGridSize=(6, 6))
    lab[..., 0] = clahe.apply(lab[..., 0])
    out = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    out = cv2.fastNlMeansDenoisingColored(out, None, 1, 1, 5, 11)
    return out

sr = cv2.dnn_superres.DnnSuperResImpl_create()
sr.readModel(f"{S}/models/FSRCNN_x2.pb"); sr.setModel("fsrcnn", 2)

# gentle "pro" grade: soft S-curve contrast + a touch of vibrance, warm skin
_x = np.arange(256) / 255.0
_curve = np.clip(255 * (_x - 0.04 * np.sin(2 * np.pi * _x)), 0, 255).astype(np.uint8)
def grade(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    lab[..., 0] = cv2.LUT(lab[..., 0], _curve)
    out = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.float32)
    sat = hsv[..., 1]
    hsv[..., 1] = np.clip(sat + 0.12 * (255 - sat) * (sat / 255.0) * 1.5, 0, 255)  # vibrance
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
    out[..., 2] *= 1.015; out[..., 0] *= 0.985                                     # slight warmth
    return np.clip(out, 0, 255).astype(np.uint8)

def sharpen(img, k_base=0.9, k_fine=0.5):
    # edge-aware detail boost on luminance only (no colour halos)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    L = lab[..., 0]
    base = cv2.bilateralFilter(L, 9, 20, 5)
    fine = L - cv2.GaussianBlur(L, (0, 0), 1.0)
    lab[..., 0] = np.clip(L + k_base * (L - base) + k_fine * fine, 0, 255)
    return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)

# ---------- per-frame analysis ----------
proc, masks, faces = [], [], []
for i, f in enumerate(frames):
    g = relight(f) if i >= cut_i else f
    if i < cut_i:
        g = cv2.fastNlMeansDenoisingColored(g, None, 2, 2, 5, 11)  # clean compression noise before upscaling
    g = sr.upsample(g)                                            # AI upscale x2
    g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LANCZOS4)
    g = grade(g)
    proc.append(g)
    rgb = cv2.cvtColor(g, cv2.COLOR_BGR2RGB)
    im = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    cm = seg.segment(im).confidence_masks
    person = 1.0 - cm[0].numpy_view()  # 1 - background
    masks.append(cv2.GaussianBlur(person.astype(np.float32), (9, 9), 0).astype(np.float16))
    det = fd.detect(im).detections
    if det:
        b = max(det, key=lambda d: d.bounding_box.width).bounding_box
        faces.append([b.origin_x + b.width / 2, b.origin_y + b.height / 2, b.width])
    else:
        faces.append(None)

# fill + smooth face track
last = next(x for x in faces if x is not None)
for i in range(N):
    if faces[i] is None: faces[i] = last
    else: last = faces[i]
F = np.array(faces, dtype=np.float32)
k = 9
F = np.stack([np.convolve(np.pad(F[:, j], k // 2, mode="edge"), np.ones(k) / k, "valid") for j in range(3)], 1)

# static anchor per caption: median face position over the word's time window
def anchor(t0, t1):
    idx = [i for i in range(N) if t0 <= i / FPS + OFFSET < t1] or [0]
    return np.median(F[idx], axis=0)
ANCH = {"UPSIDE": anchor(0, 1.15), "DOWN": anchor(1.2, 2.05), "BOY": anchor(2.8, 3.4),
        "YTM": anchor(3.4, 4.3), "INSIDE": anchor(4.7, CUT), "OUT": anchor(5.9, 6.7), "AND": anchor(6.8, 7.2)}

# ---------- helpers ----------
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def eout(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def font(p, s): return ImageFont.truetype(p, int(s))

def roughen(layer, amount):
    a = np.array(layer.split()[-1]).astype(np.float32)
    noise = cv2.GaussianBlur(np.random.RandomState(7).rand(*a.shape).astype(np.float32), (0, 0), 2.5)
    a = np.where(a > 0, a * (noise > amount), 0)
    layer.putalpha(Image.fromarray(a.astype(np.uint8)))
    return layer

def text_layer(txt, path, size, fill, cx, cy, sx=1.0, sy=1.0, alpha=1.0, rot=0, shadow=True, rough=0, clamp=True):
    f = font(path, size)
    l, t, r, b = f.getbbox(txt)
    w, h = r - l + 40, b - t + 40
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if shadow:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((20 - l + 3, 20 - t + 5), txt, font=f, fill=(0, 0, 0, 110))
        lay = Image.alpha_composite(lay, sh.filter(ImageFilter.GaussianBlur(6)))
        d = ImageDraw.Draw(lay)
    d.text((20 - l, 20 - t), txt, font=f, fill=fill)
    if rough: lay = roughen(lay, rough)
    if sx != 1 or sy != 1:
        lay = lay.resize((max(1, int(w * sx)), max(1, int(abs(h * sy)))), Image.LANCZOS)
        if sy < 0: lay = lay.transpose(Image.FLIP_TOP_BOTTOM)
    if rot: lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        a = lay.split()[-1].point(lambda v: int(v * alpha)); lay.putalpha(a)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if clamp and lay.width < W - 60:
        cx = min(max(cx, 30 + lay.width / 2), W - 30 - lay.width / 2)
    canvas.paste(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)), lay)
    return canvas

def arc_text(txt, n_show, cx, cy, radius, size, alpha=1.0):
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = font(MARK, size)
    widths = [f.getlength(c) for c in txt]
    total = sum(widths) * 1.05
    ang0 = -total / radius / 2
    pos = 0
    for i, c in enumerate(txt[:n_show]):
        a = ang0 + (pos + widths[i] / 2) / radius
        pos += widths[i] * 1.05
        if c == " ": continue
        jitter = 1 + 0.25 * math.sin(i * 2.3)  # hand-made size variation
        lf = font(MARK, size * jitter)
        lay = Image.new("RGBA", (int(size * 2), int(size * 2)), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((size, size), c, font=lf, fill=(255, 255, 255, int(255 * alpha)), anchor="mm")
        shd = Image.new("RGBA", lay.size, (0, 0, 0, 0)); shd.putalpha(lay.split()[-1].point(lambda v: int(v * 0.6)))
        shd = shd.filter(ImageFilter.GaussianBlur(5))
        lay = Image.alpha_composite(shd, lay)
        lay = lay.rotate(-math.degrees(a), resample=Image.BICUBIC)
        x = cx + radius * math.sin(a)
        y = cy - radius * math.cos(a) + radius
        canvas.paste(lay, (int(x - lay.width / 2), int(y - lay.height / 2)), lay)
    return canvas

# light-leak blobs for second part
rs = np.random.RandomState(3)
blobs = [(rs.rand() * W, rs.rand() * H * 0.6, c) for c in
         [(255, 60, 200), (140, 70, 255), (255, 210, 60), (255, 120, 60)]]

def leaks(t, strength):
    img = np.zeros((H // 4, W // 4, 3), np.float32)
    for j, (x, y, c) in enumerate(blobs):
        xx = (x + 260 * math.sin(t * 1.3 + j)) / 4
        yy = (y + 180 * math.cos(t * 0.9 + j * 2)) / 4
        cv2.circle(img, (int(xx), int(yy)), int(70 + 25 * math.sin(t * 2 + j)), c[::-1], -1)
    img = cv2.GaussianBlur(img, (0, 0), 30)
    img = cv2.resize(img, (W, H)) / 255.0
    return img * strength

# ---------- render ----------
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                       "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", SRC,
                       "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slower", "-crf", "14",
                       "-profile:v", "high", "-tune", "film", "-x264-params", "aq-mode=3",
                       "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-c:a", "aac", "-b:a", "320k", "-shortest",
                       "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)

for i in range(N):
    t = i / FPS + OFFSET
    fx, fy, fw = F[i]
    img = proc[i].astype(np.float32) / 255.0

    # ---- camera: locked off, like the reference (no follow / no zoom = no shake) ----
    img = proc[i]
    img = (sharpen(img, 1.0, 0.65) if t < CUT else sharpen(img, 0.2, 0.6)).astype(np.float32) / 255.0
    grain = np.random.normal(0, 0.014 if t >= CUT else 0.007, (H, W, 1)).astype(np.float32)
    img = img + grain
    m = masks[i].astype(np.float32)[..., None]

    img = np.power(np.clip(img, 0, 1), 1.06)  # overall slightly darker / richer

    # second part: colourful light leaks on the background only
    if t >= CUT:
        s = 0.18 + 0.4 * ease((t - 6.6) / 0.8)
        bg = cv2.GaussianBlur(img, (0, 0), 12 * ease((t - 6.6) / 0.8) + 0.01)
        bg = 1 - (1 - bg) * (1 - leaks(t, s))
        img = bg * (1 - m) + img * m

    # ---- OUT: over the body but behind the face ----
    if 5.9 <= t < 6.7:
        p = eout((t - 5.9) / 0.15)
        a = 1 - ease((t - 6.55) / 0.15)
        ax, ay, aw = ANCH["OUT"]
        lay = text_layer("OUT", ANTON, 680, (247, 228, 60, 255), W / 2, ay + aw * 0.55,
                         sx=1.3 * (0.8 + 0.2 * p), sy=0.8 + 0.2 * p, alpha=a, shadow=False, rough=0.45, clamp=False)
        face = np.zeros((H, W), np.float32)
        cv2.ellipse(face, (int(fx), int(fy - fw * 0.05)), (int(fw * 0.45), int(fw * 0.62)), 0, 0, 360, 1, -1)
        face = cv2.GaussianBlur(face, (0, 0), 8)[..., None] * np.clip(m * 1.3, 0, 1)
        la = np.array(lay).astype(np.float32) / 255.0
        al = la[..., 3:4] * (1 - face)
        img = img * (1 - al) + la[..., 2::-1] * al

    # ---- text in FRONT ----
    front = []
    side_l = fx - fw * 0.75
    side_r = fx + fw * 0.75
    if 0.0 <= t < 1.15:  # UPSIDE (flips in)
        fx, fy, fw = ANCH["UPSIDE"]; side_l = fx - fw * 0.75; side_r = fx + fw * 0.75
        p = eout(t / 0.2)
        front.append(text_layer("UPSIDE", ANTON, 190, (255, 255, 255, 255), max(190, side_l - 120), fy,
                                sy=-1 + 2 * p if p < 1 else 1, alpha=min(1, p * 2)))
    if 1.2 <= t < 2.05:  # DOWN (arrives upside down, rights itself)
        fx, fy, fw = ANCH["DOWN"]; side_l = fx - fw * 0.75; side_r = fx + fw * 0.75
        p = eout((t - 1.2) / 0.25)
        front.append(text_layer("DOWN", ANTON, 200, (255, 255, 255, 255), min(W - 170, side_r + 110), fy + fw * 0.15,
                                sy=-1 + 2 * p if p < 1 else 1))
    if 2.8 <= t < 3.4:  # BOY grows to fill the frame
        fx, fy, fw = ANCH["BOY"]; side_l = fx - fw * 0.75; side_r = fx + fw * 0.75
        p = min((t - 2.8) / 0.42, 1)
        sc = 0.35 + 2.3 * p ** 3
        a = 1 - ease((t - 3.27) / 0.12)
        front.append(text_layer("BOY", ANTON, 400, (255, 255, 255, 255), W / 2, fy + fw * 0.1,
                                sx=sc, sy=sc, alpha=a, shadow=sc < 1.2, rough=0.35 if sc > 1 else 0, clamp=False))
    if 3.4 <= t < 4.3:  # YOU TURN ME fades in under the chin
        fx, fy, fw = ANCH["YTM"]; side_l = fx - fw * 0.75; side_r = fx + fw * 0.75
        a = ease((t - 3.4) / 0.25) * (1 - ease((t - 4.15) / 0.15))
        front.append(text_layer("YOU TURN ME", ANTON, 170, (255, 255, 255, 255), W / 2, fy + fw * 1.05,
                                alpha=a))
    if 4.7 <= t < CUT:  # INSIDE typed, then shrinks away
        fx, fy, fw = ANCH["INSIDE"]; side_l = fx - fw * 0.75; side_r = fx + fw * 0.75
        word = "INSIDE"
        n = min(len(word), 3 + int((t - 4.7) / 0.05)) if t < 4.8 else len(word)
        sh = 1 - ease((t - 5.45) / 0.2) * 0.9
        front.append(text_layer(word[:n], ANTON, 200, (255, 255, 255, 255), max(200, side_l - 110), fy,
                                sx=sh, sy=sh))
    if 6.8 <= t < 7.2:  # AND
        fx, fy, fw = ANCH["AND"]; side_l = fx - fw * 0.75; side_r = fx + fw * 0.75
        p = eout((t - 6.8) / 0.12)
        front.append(text_layer("AND", ANTON, 185, (255, 255, 255, 255), min(W - 150, side_r + 90), fy,
                                sx=0.6 + 0.4 * p, sy=0.6 + 0.4 * p))
    if t >= 7.6:  # ROUND & ROUND hand-written along an arc
        txt = "ROUND & ROUND"
        n = min(len(txt), int((t - 7.6) / 0.07) + 1)
        front.append(arc_text(txt, n, W / 2, H * 0.74, 520, 120))
    for lay in front:
        a = np.array(lay).astype(np.float32) / 255.0
        al = a[..., 3:4]
        img = img * (1 - al) + a[..., 2::-1] * al

    out = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    ff.stdin.write(out.tobytes())
    if i % 30 == 0: print("t", round(t, 1), flush=True)

ff.stdin.close(); ff.wait()
print("done")
