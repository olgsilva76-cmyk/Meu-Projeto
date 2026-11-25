# Edit decision list — music 03:05–04:07 of "Nunca Foi Sobre Nós" (62 s, 123 BPM)
# Bar downbeats (s): 0.46 2.41 4.34 6.29 8.20 10.15 12.07 14.02 15.93 17.90 19.81 21.76 23.68
# 25.63 27.56 29.49 31.42 33.37 35.29 37.24 39.20 41.12 43.05 44.98 46.90 | drop 48.34 | bass out 51.76
FPS = 30
W, H = 1080, 1920
DUR = 62.0
HANDLE = 0.45  # output-time handle each side, for transitions

# grade: 'night' | 'day'
# layout: 'full' (portrait cover) | 'frame' (landscape inside blurred bg)
# cx: horizontal crop centre (0..1) for cover crop
# speed: either float (constant) or list of (out_time_rel, src_time) knots for a ramp (linear between)
# base: prep playback speed (frame density); must be <= min speed of the shot
# move: (scale0, scale1, dx0, dy0, dx1, dy1) camera move in output pixels
SHOTS = [
 # ---- A: worship night — presença (contemplativo) ----
 dict(id='s01', t0=0.00,  t1=4.34,  clip='c07', src=0.60,  speed=0.60, grade='night', cx=0.50, move=(1.10,1.00,0,40,0,0)),
 dict(id='s02', t0=4.34,  t1=8.20,  clip='c02', src=1.00,  speed=0.70, grade='night', cx=0.62, move=(1.00,1.10,0,0,-30,-20)),
 dict(id='s03', t0=8.20,  t1=10.15, clip='c13', src=5.70,  speed=0.70, grade='night', cx=0.50, move=(1.12,1.04,0,-60,0,-40)),
 dict(id='s04', t0=10.15, t1=12.07, clip='c02', src=19.40, speed=0.70, grade='night', cx=0.40, move=(1.04,1.12,30,0,-10,0)),
 dict(id='s05', t0=12.07, t1=14.02, clip='c07', src=6.50,  speed=0.60, grade='night', cx=0.50, move=(1.30,1.38,0,180,0,170)),
 dict(id='s06', t0=14.02, t1=15.93, clip='c10', src=0.30,  speed=0.70, grade='day',   cx=0.58, layout='frame', move=(1.00,1.07,0,0,0,0)),
 # ---- B: batismo — entrega / novidade de vida ----
 dict(id='s07', t0=15.93, t1=17.90, clip='c12', src=13.30, speed=1.00, grade='day', cx=0.45, move=(1.10,1.02,0,0,0,0)),
 dict(id='s08', t0=17.90, t1=19.81, clip='c06', src=10.60, speed=1.00, grade='day', cx=0.55, move=(1.05,1.14,0,0,0,40)),
 dict(id='s09', t0=19.81, t1=23.68, clip='c09', src=2.20,  speed=[(0,2.20),(1.80,4.00),(3.87,4.72)], base=0.35, grade='day', cx=0.55, move=(1.06,1.16,0,0,0,30)),
 dict(id='s10', t0=23.68, t1=25.63, clip='c04', src=60.60, speed=[(0,60.60),(0.60,61.20),(1.95,61.74)], base=0.40, grade='day', cx=0.50, move=(1.15,1.22,0,60,0,60)),
 dict(id='s11', t0=25.63, t1=27.56, clip='c03', src=53.60, speed=[(0,53.60),(0.70,54.30),(1.93,54.79)], base=0.40, grade='day', cx=0.45, move=(1.25,1.32,0,80,0,60)),
 dict(id='s12', t0=27.56, t1=29.49, clip='c06', src=14.30, speed=[(0,14.30),(0.30,14.60),(1.93,15.42)], base=0.50, grade='day', cx=0.55, move=(1.06,1.12,0,0,0,0)),
 dict(id='s13', t0=29.49, t1=31.42, clip='c06', src=24.40, speed=0.80, grade='day', cx=0.50, move=(1.02,1.10,0,0,0,0)),
 # ---- C: comunhão — abraços, alegria ----
 dict(id='s14', t0=31.42, t1=33.37, clip='c03', src=88.00, speed=0.80, grade='day', cx=0.60, move=(1.18,1.10,0,40,0,40)),
 dict(id='s15', t0=33.37, t1=35.29, clip='c01', src=114.00,speed=0.80, grade='day', cx=0.50, move=(1.10,1.18,0,60,0,60)),
 dict(id='s16', t0=35.29, t1=37.24, clip='c04', src=97.00, speed=0.80, grade='day', cx=0.45, move=(1.04,1.12,0,0,0,0)),
 dict(id='s17', t0=37.24, t1=39.20, clip='c09', src=29.40, speed=0.80, grade='day', cx=0.55, move=(1.12,1.04,0,0,0,0)),
 dict(id='s18', t0=39.20, t1=41.12, clip='c05', src=2.00,  speed=0.80, grade='day', cx=0.45, layout='frame', move=(1.00,1.06,0,0,0,0)),
 dict(id='s19', t0=41.12, t1=43.05, clip='c10', src=16.90, speed=0.80, grade='day', cx=0.55, layout='frame', move=(1.06,1.00,0,0,0,0)),
 dict(id='s20', t0=43.05, t1=44.98, clip='c01', src=63.50, speed=0.80, grade='day', cx=0.50, move=(1.20,1.28,0,60,0,60)),
 dict(id='s21', t0=44.98, t1=46.90, clip='c03', src=70.00, speed=0.80, grade='day', cx=0.50, move=(1.22,1.14,0,60,0,60)),
 dict(id='s22', t0=46.90, t1=48.34, clip='c06', src=21.20, speed=0.80, grade='day', cx=0.50, move=(1.04,1.10,0,0,0,0)),
 # ---- D: respiro (instrumentos recuam) ----
 dict(id='s23', t0=48.34, t1=51.76, clip='c09', src=14.80, speed=0.45, grade='day', cx=0.50, move=(1.10,1.24,0,40,0,60)),
 # ---- E: desfecho contemplativo ----
 dict(id='s24', t0=51.76, t1=55.62, clip='c14', src=0.50,  speed=0.80, grade='day', cx=0.50, layout='frame', move=(1.00,1.08,0,0,0,0)),
 dict(id='s25', t0=55.62, t1=62.00, clip='c07', src=2.00,  speed=0.50, grade='night', cx=0.50, move=(1.06,1.20,0,40,0,80)),
]

# transitions at the start of each shot (key = shot id): (type, half-duration)
TRANS = {
 's01': ('fadein', 0.9),
 's02': ('leak', 0.45), 's03': ('dissolve', 0.35), 's04': ('mask', 0.35), 's05': ('dissolve', 0.30),
 's06': ('zoom', 0.22), 's07': ('whip', 0.20), 's08': ('cut', 0), 's09': ('zoom', 0.20),
 's10': ('flash', 0.25), 's11': ('whip', 0.18), 's12': ('flash', 0.22), 's13': ('cut', 0),
 's14': ('zoom', 0.22), 's15': ('cut', 0), 's16': ('whip', 0.18), 's17': ('cut', 0), 's18': ('zoom', 0.20),
 's19': ('mask', 0.30), 's20': ('cut', 0), 's21': ('whip', 0.18), 's22': ('cut', 0),
 's23': ('leak', 0.55), 's24': ('dissolve', 0.70), 's25': ('dissolve', 0.80),
}
# in-shot accents (beat hits): (time, kind)
ACCENTS = [(21.70, 'bloom'), (24.25, 'bloom'), (26.40, 'bloom'), (15.93, 'pulse'), (31.42, 'pulse'), (46.90, 'pulse')]
