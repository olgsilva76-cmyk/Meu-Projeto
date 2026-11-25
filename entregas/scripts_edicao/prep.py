import subprocess, json, os, sys
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from shots import SHOTS, HANDLE, FPS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CL = os.path.join(ROOT, 'clips'); OUT = os.path.join(ROOT, 'prep'); os.makedirs(OUT, exist_ok=True)

GRADE = {
 'day': "eq=contrast=1.10:saturation=0.80:gamma=0.95:brightness=-0.02,"
        "selectivecolor=cyans='0.12 0 0.06 0.24':blues='0.06 0 0 0.18':reds='0 0 -0.05 0',"
        "colorbalance=rs=-0.04:bs=0.05:rm=0.02:bm=-0.02:rh=0.06:gh=0.03:bh=-0.05,"
        "curves=all='0/0.03 0.25/0.21 0.5/0.5 0.75/0.79 1/0.97'",
 'night': "eq=contrast=1.12:saturation=0.78:gamma=0.90:brightness=-0.02,"
        "colorbalance=rs=-0.02:bs=0.06:rm=0.06:gm=0.01:bm=-0.05:rh=0.07:gh=0.02:bh=-0.07,"
        "curves=all='0/0.03 0.25/0.19 0.5/0.46 0.75/0.76 1/0.94'",
}
FRAME_ASPECT = {'s24': 1.43}

def probe(path):
    o = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                 'stream=r_frame_rate:format=duration', '-of', 'json', path])
    j = json.loads(o); a, b = j['streams'][0]['r_frame_rate'].split('/')
    return float(a) / float(b), float(j['format']['duration'])

def src_fn(s):
    sp = s['speed']
    if isinstance(sp, (int, float)):
        return lambda u: s['src'] + u * sp, sp, sp
    k = sp
    def f(u):
        if u <= k[0][0]:
            v = (k[1][1] - k[0][1]) / (k[1][0] - k[0][0]); return k[0][1] + (u - k[0][0]) * v
        for (a, sa), (b, sb) in zip(k, k[1:]):
            if u <= b: return sa + (u - a) * (sb - sa) / (b - a)
        v = (k[-1][1] - k[-2][1]) / (k[-1][0] - k[-2][0]); return k[-1][1] + (u - k[-1][0]) * v
    speeds = [(sb - sa) / (b - a) for (a, sa), (b, sb) in zip(k, k[1:])]
    return f, min(speeds), s.get('base', min(speeds))

def mask_png(w, h, feather=110):
    a = np.ones((h, w), np.float32)
    r = np.linspace(0, 1, feather) ** 1.6
    a[:feather] *= r[:, None]; a[-feather:] *= r[::-1][:, None]
    p = os.path.join(OUT, f'mask_{w}x{h}.png'); Image.fromarray((a * 255).astype(np.uint8)).save(p); return p

def prep(s):
    path = os.path.join(CL, s['clip'] + '.mov'); fps, dur = probe(path)
    f, mn, base = src_fn(s); base = s.get('base', base)
    d = s['t1'] - s['t0']
    a = max(0.0, f(-HANDLE)); b = min(dur - 0.08, f(d + HANDLE))
    nframes = int(round((b - a) / base * FPS))
    interp = fps * base < 29
    tm = f"setpts=(PTS-STARTPTS)/{base}," + (
        "minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1," if interp else "fps=30,")
    g = GRADE[s['grade']]; cx = s.get('cx', 0.5)
    if s.get('layout') == 'frame':
        fa = FRAME_ASPECT.get(s['id'], 0.8); fw = 1080; fh = int(round(1080 / fa / 2) * 2)
        m = mask_png(fw, fh)
        fc = (f"[0:v]{tm}split[a][b];"
              f"[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:3,eq=brightness=-0.10:saturation=0.75[bg];"
              f"[b]crop='min(iw,ih*{fa})':ih:'(iw-min(iw,ih*{fa}))*{cx}':0,scale={fw}:{fh}:flags=lanczos,unsharp=5:5:0.5,format=rgba[fg0];"
              f"[1:v]format=gray,scale={fw}:{fh}[m];[fg0][m]alphamerge[fg];"
              f"[bg][fg]overlay=0:{(1920 - fh)//2},{g},format=yuv420p[v]")
        inputs = ['-i', path, '-loop', '1', '-i', m]
    else:
        fc = (f"[0:v]{tm}scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
              f"crop=1080:1920:'(iw-1080)*{cx}':'(ih-1920)/2',unsharp=5:5:0.45,{g},format=yuv420p[v]")
        inputs = ['-i', path]
    out = os.path.join(OUT, s['id'] + '.mp4')
    cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-t', f'{(b - a) + 0.2:.3f}'] + inputs[:2] + inputs[2:] + [
        '-filter_complex', fc, '-map', '[v]', '-frames:v', str(nframes), '-an',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '12', out]
    subprocess.run(cmd, check=True)
    meta = dict(id=s['id'], srcA=a, base=base, nframes=nframes)
    json.dump(meta, open(os.path.join(OUT, s['id'] + '.json'), 'w'))
    return s['id'], round(a, 2), round(b, 2), nframes, interp

if __name__ == '__main__':
    only = sys.argv[1:]
    todo = [s for s in SHOTS if not only or s['id'] in only]
    with ThreadPoolExecutor(4) as ex:
        for r in ex.map(prep, todo): print(r, flush=True)
