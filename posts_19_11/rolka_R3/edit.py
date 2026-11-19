# R3 reel editor: cuts, light retouch, animated captions, transitions, SFX.
import subprocess, json, math, os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import signal

D = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(D, 'src')
F = '/tmp/claude-0/fonts/'
W, H, FPS, SR = 1080, 1920, 30, 48000
GOLD = (243, 199, 122); WHITE = (255, 255, 255); CREAM = (251, 243, 230)
LOGO = '/home/user/congenial-winner/posts_19_11/src/logo.png'

def font(name, size): return ImageFont.truetype(F + name, size)

# ---------------------------------------------------------------- timeline
# Each V item: clip, in, out, zoom (start,end), plus events relative to segment start.
V = lambda clip, a, b, z=(1.0, 1.03), **k: dict(kind='v', clip=clip, a=a, b=b, z=z, **k)
C = lambda dur, **k: dict(kind='card', dur=dur, **k)
TL = [
    V('c1', 1.15, 4.75, z=(1.22, 1.0), tin=None, name='hook'),
    V('c5', 1.20, 2.20, z=(1.0, 1.03), tin='whip', name='n1a'),
    V('c5', 2.60, 3.80, z=(1.14, 1.17), tin='cut', name='n1b'),
    V('c5', 9.95, 13.45, z=(1.0, 1.05), tin='cut', name='n1c'),
    V('c5', 17.40, 20.15, z=(1.12, 1.16), tin='cut', name='n1d'),
    V('c2', 1.45, 2.40, z=(1.0, 1.03), tin='whip', name='n2a'),
    V('c2', 2.95, 4.05, z=(1.14, 1.17), tin='cut', name='n2b'),
    V('c2', 6.75, 7.90, z=(1.0, 1.04), tin='cut', name='nosun'),
    V('c2', 17.45, 20.80, z=(1.12, 1.18), tin='cut', name='uva'),
    V('c3', 10.20, 12.75, z=(1.0, 1.04), tin='whip', name='n3'),
    V('c3', 17.90, 22.20, z=(1.12, 1.16), tin='cut', name='heat'),
    V('c3', 26.90, 31.00, z=(1.0, 1.06), tin='flash', name='fix'),
    V('c4', 0.80, 3.75, z=(1.1, 1.14), tin='whip', name='porc'),
    V('c4', 4.85, 8.30, z=(1.0, 1.04), tin='cut', name='save'),
    C(3.0, name='cta', tin='zoom'),
]
t = 0.0
for s in TL:
    s['dur'] = s.get('dur') or (s['b'] - s['a'])
    s['t0'] = t; t += s['dur']
TOTAL = t
NF = int(round(TOTAL * FPS))
SEG = {s['name']: s for s in TL}
def T(name, rel): return SEG[name]['t0'] + rel

# ---------------------------------------------------------------- captions (word, rel start in segment, gold?)
CAP = {
 'hook':  [[('THAT', 1.20), ('ARE', 1.70), ('RUINING', 2.06, 1)], [('YOUR', 2.40), ('SKIN', 2.74, 1)]],
 'n1c':   [[('IT', 0.06), ('STRIPS', 0.16, 1)], [('YOUR', 0.76), ("SKIN'S", 1.38)], [('NATURAL', 1.78), ('LIPIDS', 2.50, 1)]],
 'n1d':   [[('SO', 0.06), ('IT', 0.56), ('ENDS', 0.96), ('UP', 1.16)], [('ROUGH', 1.44, 1), ('&', 1.94), ('TIGHT', 2.26, 1)]],
 'nosun': [[('NO', 0.08, 1), ('SUN?', 0.40, 1)]],
 'uva':   [[('UVA', 0.08, 1), ('STILL', 0.52), ('REACHES', 1.08)], [('YOUR', 1.42), ('SKIN', 1.62)], [('IN', 1.92), ('NOVEMBER', 2.32, 1)]],
 'heat':  [[('WITH', 0.10), ('THE', 0.54), ('HEATING', 0.76, 1), ('ON', 0.94)], [('YOUR', 1.28), ('SKIN', 1.60), ('LOSES', 1.92)], [('WATER', 2.52, 1), ('FASTER', 3.60, 1)]],
 'fix':   [[('IT', 0.08), ('NEEDS', 0.28)], [('TO', 1.94), ('REBUILD', 2.62)], [('ITS', 3.04), ('BARRIER', 3.58, 1)]],
 'porc':  [[("THAT'S", 0.08), ('EXACTLY', 0.42), ('WHAT', 0.78)], [('PORCERAMID', 1.10, 1), ('DOES', 2.04)]],
 'save':  [[('SO', 0.08), ('SAVE', 0.68, 1), ('THIS', 1.06), ('REEL', 1.28, 1)], [('AND', 1.54), ('SEND', 2.24), ('ME', 2.52)], [('A', 2.68), ('DIRECT', 2.78, 1), ('MESSAGE', 3.06, 1)]],
}

# ---------------------------------------------------------------- easing
def clamp(x, a=0, b=1): return max(a, min(b, x))
def out_back(x, s=2.2):
    x = clamp(x) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2
def out_cubic(x): x = clamp(x); return 1 - (1 - x) ** 3
def in_out(x): x = clamp(x); return x * x * (3 - 2 * x)

# ---------------------------------------------------------------- sprite rendering
_cache = {}
def text_sprite(txt, fnt, fill, stroke=8, stroke_col=(0, 0, 0), shadow=True, tracking=0):
    key = (txt, fnt.path, fnt.size, fill, stroke, shadow, tracking)
    if key in _cache: return _cache[key]
    pad = stroke + 30
    w = int(sum(fnt.getlength(ch) + tracking for ch in txt)) + pad * 2
    asc, desc = fnt.getmetrics(); h = asc + desc + pad * 2
    im = Image.new('RGBA', (w, h))
    def draw(img, col, sw, scol):
        d = ImageDraw.Draw(img); x = pad
        for ch in txt:
            d.text((x, pad), ch, font=fnt, fill=col, stroke_width=sw, stroke_fill=scol)
            x += fnt.getlength(ch) + tracking
    if shadow:
        sh = Image.new('RGBA', (w, h)); draw(sh, (0, 0, 0, 170), stroke + 2, (0, 0, 0, 170))
        sh = sh.filter(ImageFilter.GaussianBlur(10)); im.alpha_composite(sh, (0, 6))
    if isinstance(fill, str) and fill == 'gold':
        layer = Image.new('RGBA', (w, h)); draw(layer, (0, 0, 0, 255), stroke, stroke_col)
        txtmask = Image.new('L', (w, h)); dm = ImageDraw.Draw(txtmask); x = pad
        for ch in txt:
            dm.text((x, pad), ch, font=fnt, fill=255); x += fnt.getlength(ch) + tracking
        g = np.zeros((h, w, 4), np.uint8)
        yy = np.linspace(0, 1, h)[:, None]
        top, mid, bot = np.array([255, 232, 190]), np.array([228, 178, 110]), np.array([250, 215, 150])
        col = np.where(yy < .55, top + (mid - top) * (yy / .55), mid + (bot - mid) * ((yy - .55) / .45))
        g[..., :3] = np.repeat(col[:, None, :], w, 1).reshape(h, w, 3) if col.ndim == 2 else col
        g[..., :3] = np.broadcast_to(col.reshape(h, 1, 3), (h, w, 3))
        g[..., 3] = np.array(txtmask)
        layer.alpha_composite(Image.fromarray(g))
        im.alpha_composite(layer)
    else:
        draw(im, fill, stroke, stroke_col)
    _cache[key] = im
    return im

def paste(canvas, spr, cx, cy, scale=1.0, alpha=1.0, rot=0):
    if alpha <= 0.01 or scale <= 0.02: return
    s = spr
    if abs(scale - 1) > 0.005:
        s = s.resize((max(1, int(s.width * scale)), max(1, int(s.height * scale))), Image.BICUBIC)
    if rot: s = s.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = np.array(s); a[..., 3] = (a[..., 3] * alpha).astype(np.uint8); s = Image.fromarray(a)
    canvas.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2))) if (cx - s.width / 2 >= 0 and cy - s.height / 2 >= 0 and cx + s.width / 2 <= W and cy + s.height / 2 <= H) else _safe(canvas, s, int(cx - s.width / 2), int(cy - s.height / 2))

def _safe(canvas, s, x, y):
    big = Image.new('RGBA', canvas.size); big.paste(s, (x, y), s); canvas.alpha_composite(big)

def pill_sprite(txt, fnt, bg=(236, 196, 132), fg=(26, 18, 11), padx=46, pady=22):
    key = ('pill', txt, fnt.size, bg)
    if key in _cache: return _cache[key]
    tw = fnt.getlength(txt) + 0; asc, desc = fnt.getmetrics()
    w, h = int(tw + padx * 2), int(asc + desc + pady * 2)
    im = Image.new('RGBA', (w + 40, h + 40)); d = ImageDraw.Draw(im)
    sh = Image.new('RGBA', im.size); ImageDraw.Draw(sh).rounded_rectangle((20, 26, 20 + w, 26 + h), h // 2, fill=(0, 0, 0, 140))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    grad = Image.new('RGBA', (w, h)); g = np.zeros((h, w, 4), np.uint8)
    yy = np.linspace(0, 1, h)[:, None, None]
    g[..., :3] = (np.array([248, 220, 168]) * (1 - yy) + np.array([201, 149, 90]) * yy).astype(np.uint8)
    m = Image.new('L', (w, h)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=255)
    g[..., 3] = np.array(m); grad = Image.fromarray(g)
    im.alpha_composite(grad, (20, 20))
    ImageDraw.Draw(im).text((20 + padx, 20 + pady), txt, font=fnt, fill=fg)
    _cache[key] = im; return im

# fonts
F_CAP = font('mont800.ttf', 84)
F_HEAD = font('mont800.ttf', 110)
F_NUM = font('pf800.ttf', 330)
F_SER = font('pf700i.ttf', 70)
F_SMALL = font('mont600.ttf', 40)
F_PILL = font('mont800.ttf', 40)
logo = Image.open(LOGO).convert('RGBA'); logo = logo.resize((420, int(300 * logo.height / logo.width)), Image.LANCZOS)

# ---------------------------------------------------------------- overlay events (headlines)
def headline_layer(canvas, t, shake):
    """Big kinetic titles. returns extra shake offset."""
    def stamp(lines, t_in, t_out, y0, gold_idx=(), sizes=None, stagger=0.12):
        if not (t_in - 0.01 <= t <= t_out): return
        for i, ln in enumerate(lines):
            ti = t_in + i * stagger
            if t < ti: continue
            k = (t - ti) * FPS
            sc = 0.35 + 0.65 * out_back(k / 7)
            fade_out = 1 - clamp((t - (t_out - 0.15)) / 0.15)
            fnt = sizes[i] if sizes else F_HEAD
            spr = text_sprite(ln, fnt, 'gold' if i in gold_idx else WHITE, stroke=9)
            fit = min(1.0, 980 / spr.width)
            paste(canvas, spr, W / 2, y0 + i * (fnt.size * 1.08), sc * fit, fade_out)
    # hook
    stamp(['3 WINTER', 'MISTAKES'], T('hook', 0.0), T('hook', 3.6), 330, gold_idx=(1,), stagger=0.18)
    # #1
    stamp(['#1'], T('n1a', 0.02), T('n1b', 1.2), 300, sizes=[font('pf800.ttf', 170)], gold_idx=(0,))
    stamp(['HOT WATER'], T('n1b', 0.02), T('n1b', 1.2), 470)
    # #2
    n2 = SEG['n2a']['t0']; stamp(['#2'], n2 + 0.02, T('n2b', 1.1), 300, sizes=[font('pf800.ttf', 170)], gold_idx=(0,))
    stamp(['SKIPPING SPF'], T('n2b', 0.02), T('n2b', 1.1), 470, gold_idx=())
    # #3
    stamp(['#3'], T('n3', 0.02), T('n3', 2.55), 300, sizes=[font('pf800.ttf', 170)], gold_idx=(0,))
    stamp(['NOT ENOUGH', 'HYDRATION'], T('n3', 1.12), T('n3', 2.55), 470, gold_idx=(1,), stagger=0.14)
    # fix
    stamp(['THE FIX:', 'CERAMIDES'], T('fix', 0.70), T('fix', 4.1), 330, gold_idx=(1,), stagger=0.16)
    # price badge on PorCerAmid
    tb = T('porc', 1.15)
    if tb <= t <= T('porc', 2.95):
        k = (t - tb) * FPS; sc = 0.3 + 0.7 * out_back(k / 8)
        paste(canvas, pill_sprite('BLACK FRIDAY  £55', font('mont800.ttf', 62), padx=54, pady=26), W / 2, 360, sc, 1, rot=-3 * (1 - out_cubic(k / 10)) + 2)
        s2 = text_sprite('was £85', font('mont600.ttf', 56), CREAM, stroke=6)
        paste(canvas, s2, W / 2, 500, 0.3 + 0.7 * out_back((k - 4) / 8), clamp((k - 4) / 4))
        a = clamp((k - 9) / 5)
        if a > 0:
            hw = (s2.width - 2 * 36) / 2; d = ImageDraw.Draw(canvas)
            d.line((W / 2 - hw, 506, W / 2 - hw + 2 * hw * a, 506), fill=(232, 84, 70, 255), width=7)
    # save icon pop on "SAVE"
    ts = T('save', 0.68)
    if ts <= t <= T('save', 3.45):
        k = (t - ts) * FPS
        paste(canvas, bookmark_sprite(), W / 2, 330, 0.3 + 0.7 * out_back(k / 7), 1 - clamp((t - T('save', 3.3)) / 0.15))

_bm = None
def bookmark_sprite():
    global _bm
    if _bm: return _bm
    im = Image.new('RGBA', (220, 260)); d = ImageDraw.Draw(im)
    sh = Image.new('RGBA', im.size); ImageDraw.Draw(sh).polygon([(60, 40), (160, 40), (160, 230), (110, 185), (60, 230)], fill=(0, 0, 0, 160))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (0, 8))
    d.polygon([(60, 30), (160, 30), (160, 220), (110, 175), (60, 220)], fill=GOLD + (255,), outline=(255, 255, 255, 255))
    d.line([(60, 30), (160, 30), (160, 220), (110, 175), (60, 220), (60, 30)], fill=WHITE + (255,), width=7)
    _bm = im; return im

def captions_layer(canvas, t):
    for name, chunks in CAP.items():
        s = SEG[name]
        if not (s['t0'] <= t < s['t0'] + s['dur']): continue
        rel = t - s['t0']
        # active chunk = last chunk whose first word has started
        act = None
        for i, ch in enumerate(chunks):
            if rel >= ch[0][1] - 0.02: act = i
        if act is None: return
        ch = chunks[act]
        nxt = chunks[act + 1][0][1] if act + 1 < len(chunks) else s['dur']
        if rel > nxt - 0.02: return
        words = [(w[0], w[1], len(w) > 2) for w in ch]
        sprs = [text_sprite(w, F_CAP, 'gold' if g else WHITE, stroke=9) for w, _, g in words]
        gap = -52
        wsc = [1.06 if g else 1.0 for _, _, g in words]
        total = sum(sp.width * k for sp, k in zip(sprs, wsc)) + gap * (len(sprs) - 1)
        fit = min(1.0, 1000 / total)
        x = W / 2 - total * fit / 2; y = 1365
        for (w, st, g), sp, kw in zip(words, sprs, wsc):
            k = (rel - st) * FPS
            if k >= -0.5:
                sc = (0.45 + 0.55 * out_back(k / 5)) * fit * (1.06 if g else 1)
                lift = (1 - out_cubic(k / 5)) * 26
                paste(canvas, sp, x + sp.width * kw * fit / 2, y + lift, sc, clamp(k / 2.5 + 0.2))
            x += (sp.width * kw + gap) * fit

# ---------------------------------------------------------------- cards
def card_layer(canvas, s, rel):
    if s['name'] == 'hot':
        k = rel * FPS
        paste(canvas, text_sprite('#1', font('pf800.ttf', 260), 'gold', stroke=8), W / 2, 640, 0.3 + 0.7 * out_back((k - 3) / 7), clamp((k - 3) / 2))
        paste(canvas, text_sprite('HOT WATER', font('mont800.ttf', 128), WHITE, stroke=9), W / 2, 880, 0.3 + 0.7 * out_back((k - 10) / 7), clamp((k - 10) / 2))
        for i, (ln, kk, g) in enumerate([('strips your skin\'s', 26, 0), ('natural lipids', 31, 1), ('rough, tight skin', 44, 1)]):
            fnt = F_SER
            spr = text_sprite(ln, fnt, 'gold' if g else CREAM, stroke=5)
            yy = 1060 + i * 92 + (70 if i == 2 else 0)
            paste(canvas, spr, W / 2, yy + (1 - out_cubic((k - kk) / 6)) * 30, 1, clamp((k - kk) / 4))
        if k > 40:
            paste(canvas, text_sprite('↓', font('mont800.ttf', 60), GOLD, stroke=4), W / 2, 1222, 1, clamp((k - 40) / 4))
    if s['name'] == 'cta':
        k = rel * FPS
        paste(canvas, text_sprite('SEND ME', font('mont800.ttf', 100), WHITE, stroke=9), W / 2, 560, 0.3 + 0.7 * out_back((k - 3) / 7), clamp((k - 3) / 2))
        paste(canvas, pill_sprite('“CERAMID”', font('mont800.ttf', 96), padx=60, pady=30), W / 2, 740, 0.3 + 0.7 * out_back((k - 9) / 8), clamp((k - 9) / 2), rot=-2 * (1 - out_cubic((k - 9) / 10)))
        paste(canvas, text_sprite('in DM to book', F_SER, CREAM, stroke=5), W / 2, 900 + (1 - out_cubic((k - 16) / 6)) * 30, 1, clamp((k - 16) / 4))
        paste(canvas, text_sprite('PorCerAmid  £55', font('mont800.ttf', 74), 'gold', stroke=7), W / 2, 1080, 0.4 + 0.6 * out_back((k - 24) / 7), clamp((k - 24) / 3))
        paste(canvas, text_sprite('Black Friday · until 30 November', font('mont600.ttf', 42), CREAM, stroke=5), W / 2, 1170, 1, clamp((k - 30) / 4))
        paste(canvas, logo, W / 2, 1460, 1, clamp((k - 36) / 6))

# ---------------------------------------------------------------- video decoding
def read_segment(clip, a, b):
    n = int(round((b - a) * FPS))
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{a:.3f}', '-i', os.path.join(SRC, clip + '.mov'), '-frames:v', str(n),
           '-vf', f'fps={FPS},scale={W}:{H}:flags=lanczos', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    if len(fr) < n: fr = np.concatenate([fr, np.repeat(fr[-1:], n - len(fr), 0)])
    return fr[:n]

CASC = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
def faces_for(frames):
    boxes = []; last = None
    for i, f in enumerate(frames):
        if i % 3 == 0:
            g = cv2.cvtColor(cv2.resize(f, (W // 3, H // 3)), cv2.COLOR_BGR2GRAY)
            fs = CASC.detectMultiScale(g, 1.1, 6, minSize=(60, 60))
            if len(fs): last = max(fs, key=lambda r: r[2]) * 3
        boxes.append(last)
    # fill + smooth
    first = next((b for b in boxes if b is not None), np.array([300, 700, 400, 400]))
    arr = np.array([b if b is not None else first for b in boxes], float)
    for i in range(1, len(arr)): arr[i] = arr[i - 1] * 0.7 + arr[i] * 0.3
    return arr

# ---------------------------------------------------------------- retouch (no geometry changes)
LUT = np.clip(np.array([((x / 255) ** 0.96) * 255 for x in range(256)]), 0, 255)
curve = np.array([255 * (0.5 - 0.5 * math.cos(math.pi * (x / 255))) * 0.18 + x * 0.82 for x in range(256)])
LUT = np.clip(curve * 1.0, 0, 255)
LUT_R = np.clip(LUT * 1.03 + 2, 0, 255).astype(np.uint8)
LUT_G = np.clip(LUT * 1.005 + 1, 0, 255).astype(np.uint8)
LUT_B = np.clip(LUT * 0.965, 0, 255).astype(np.uint8)
yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.22 * np.clip((((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.7)) ** 2) - 0.25, 0, 1)).astype(np.float32)[..., None]

def retouch(f, box):
    x, y, w, h = box
    # soft mask: face + hair zone (ellipse a bit larger than face, extended upward for hair)
    m = np.zeros((H // 4, W // 4), np.uint8)
    cx, cy = (x + w / 2) / 4, (y + h * 0.42) / 4
    cv2.ellipse(m, (int(cx), int(cy)), (int(w * 0.80 / 4), int(h * 0.95 / 4)), 0, 0, 360, 255, -1)
    m = cv2.GaussianBlur(m, (0, 0), 6)
    m = cv2.resize(m, (W, H)).astype(np.float32)[..., None] / 255
    # edge-preserving smoothing: evens skin texture & frizz, keeps eyes/lips/outline
    sm = cv2.bilateralFilter(f, 0, 22, 7)
    f2 = f.astype(np.float32) * (1 - 0.55 * m) + sm.astype(np.float32) * (0.55 * m)
    # hair: gentle golden lift where bright-yellowish pixels inside mask's upper area
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    hair = ((hsv[..., 0] > 10) & (hsv[..., 0] < 32) & (hsv[..., 2] > 120) & (hsv[..., 1] > 40)).astype(np.float32)
    up = (yy < (y + h * 0.35)).astype(np.float32)
    hm = cv2.GaussianBlur(hair * up, (0, 0), 3)[..., None] * m
    f2 = f2 + hm * np.array([-4, 6, 14], np.float32)  # BGR: warmer, a touch brighter blonde
    f2 = np.clip(f2, 0, 255).astype(np.uint8)
    # global grade
    b, g, r = cv2.split(f2)
    f2 = cv2.merge([cv2.LUT(b, LUT_B), cv2.LUT(g, LUT_G), cv2.LUT(r, LUT_R)])
    f2 = (f2.astype(np.float32) * VIG)
    return np.clip(f2, 0, 255).astype(np.uint8)

def zoom(f, s, anchor):
    if abs(s - 1) < 1e-3: return f
    ax, ay = anchor
    M = np.float32([[s, 0, ax - s * ax], [0, s, ay - s * ay]])
    return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def motion_blur(f, amt):
    k = int(abs(amt))
    if k < 3: return f
    ker = np.zeros((1, k), np.float32); ker[0, :] = 1 / k
    return cv2.filter2D(f, -1, ker)

# ---------------------------------------------------------------- build frames
def build_video(out_path):
    frames_by_seg = {}
    for s in TL:
        if s['kind'] == 'v':
            fr = read_segment(s['clip'], s['a'], s['b'])
            boxes = faces_for(fr)
            anc = (float(np.median(boxes[:, 0] + boxes[:, 2] / 2)), float(np.median(boxes[:, 1] + boxes[:, 3] / 2)))
            out = []
            for i, f in enumerate(fr):
                p = i / max(1, len(fr) - 1)
                z0, z1 = s['z']
                sc = z0 + (z1 - z0) * (out_cubic(p * 2.2) if s['name'] == 'hook' else p)
                out.append(zoom(retouch(f, boxes[i]), sc, anc))
            frames_by_seg[s['name']] = out
            print('seg', s['name'], len(out), flush=True)
    # card backgrounds: blurred darkened freeze of neighbour
    def card_bg(src_frame):
        b = cv2.GaussianBlur(src_frame, (0, 0), 28)
        return (b.astype(np.float32) * 0.38).astype(np.uint8)
    for s in TL:
        if s['kind'] == 'card':
            n = int(round(s['dur'] * FPS))
            src = frames_by_seg['hook'][-1] if s['name'] == 'hot' else frames_by_seg['save'][-1]
            bg = card_bg(src); out = []
            for i in range(n):
                sc = 1.0 + 0.06 * i / n
                out.append(zoom(bg, sc, (W / 2, H / 2)))
            frames_by_seg[s['name']] = out
    seq = []
    for s in TL: seq += [(s, i, f) for i, f in enumerate(frames_by_seg[s['name']])]
    seq = seq[:NF]
    # transitions at boundaries
    starts = {s['name']: int(round(s['t0'] * FPS)) for s in TL}
    trans = {}
    for idx, s in enumerate(TL):
        if idx == 0: continue
        trans[starts[s['name']]] = s.get('tin')
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', out_path], stdin=subprocess.PIPE)
    shake_until = {}
    for fi, (s, i, f) in enumerate(seq):
        t = fi / FPS
        img = f
        # transition FX around boundary b
        for b, kind in trans.items():
            d = fi - b
            if kind == 'whip' and -4 <= d < 4:
                if d < 0:
                    sh = [-40, -140, -330, -620][d + 4]; img = motion_blur(np.roll(img, sh, 1), abs(sh) * 0.5)
                else:
                    sh = [620, 330, 140, 40][d]; img = motion_blur(np.roll(img, sh, 1), abs(sh) * 0.5)
            if kind == 'zoom' and -4 <= d < 5:
                if d < 0:
                    sc = 1 + 0.08 * (d + 5) ** 1.5 / 4; img = cv2.GaussianBlur(zoom(img, sc, (W / 2, H * 0.45)), (0, 0), 2 + 3 * (d + 5))
                else:
                    sc = 1.25 - 0.25 * out_cubic(d / 5); img = zoom(img, sc, (W / 2, H / 2))
            if kind == 'flash' and 0 <= d < 6:
                a = (1 - d / 6) ** 1.5 * 0.85
                img = (img.astype(np.float32) * (1 - a) + 255 * a).astype(np.uint8)
            if kind == 'cut' and 0 <= d < 2:
                pass
        # impact shakes on slams
        for ts in SHAKES:
            d = t - ts
            if 0 <= d < 0.2:
                amp = 14 * (1 - d / 0.2); dx = int(amp * math.sin(d * 90)); dy = int(amp * math.cos(d * 70))
                img = np.roll(np.roll(img, dx, 1), dy, 0)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        canvas = Image.fromarray(rgb).convert('RGBA')
        # readability gradients
        canvas.alpha_composite(TOPGRAD); canvas.alpha_composite(BOTGRAD)
        if s['kind'] == 'card': card_layer(canvas, s, i / FPS)
        headline_layer(canvas, t, None)
        captions_layer(canvas, t)
        # progress bar
        d = ImageDraw.Draw(canvas); d.rectangle((0, 0, int(W * (fi + 1) / NF), 8), fill=GOLD + (230,))
        enc.stdin.write(np.array(canvas.convert('RGB')).tobytes())
        if fi % 60 == 0: print('frame', fi, '/', NF, flush=True)
    enc.stdin.close(); enc.wait()

def vgrad(top, h0, h1, a0, a1):
    g = np.zeros((H, W, 4), np.uint8)
    ys = np.arange(H)
    a = np.clip((ys - h0) / (h1 - h0), 0, 1); a = a0 + (a1 - a0) * a
    a[(ys < min(h0, h1)) | (ys > max(h0, h1))] = 0
    if top: a[ys < h0] = a0
    else: a[ys > h1] = a1
    g[..., 3] = (a * 255)[:, None]
    return Image.fromarray(g)
TOPGRAD = vgrad(True, 0, 620, 0.55, 0.0)
BOTGRAD = vgrad(False, 1150, 1600, 0.0, 0.55)

# slam moments (for shake + boom)
SHAKES = [T('hook', 0.0), T('n1a', 0.0), SEG['n2a']['t0'], T('n3', 0.0), T('fix', 0.70), T('cta', 0.3)]

# ---------------------------------------------------------------- SFX
rng = np.random.default_rng(7)
def env(n, a, r):
    e = np.ones(n); ai = int(a * SR); e[:ai] = np.linspace(0, 1, ai) if ai else 1
    e *= np.exp(-np.linspace(0, r, n)); return e
def whoosh(d=0.45, up=True):
    n = int(d * SR); x = rng.standard_normal(n)
    out = np.zeros(n); fc = np.geomspace(300, 4500, n) if up else np.geomspace(4500, 300, n)
    # chunked bandpass sweep
    for k in range(0, n, 1024):
        f0 = fc[k]; sos = signal.butter(2, [f0 * 0.6, min(f0 * 1.6, 20000)], 'band', fs=SR, output='sos')
        out[k:k + 1024] = signal.sosfilt(sos, x[k:k + 1024])
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return out * e / (np.abs(out).max() + 1e-9) * 0.7
def boom(d=1.0):
    n = int(d * SR); tt = np.arange(n) / SR
    f = 62 * np.exp(-tt * 3) + 30; ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-tt * 4.5)
    click = signal.sosfilt(signal.butter(2, 2500, 'low', fs=SR, output='sos'), rng.standard_normal(n)) * np.exp(-tt * 60) * 0.6
    return np.tanh((s + click) * 1.6) * 0.9
def pop(d=0.09, f0=1300, f1=380):
    n = int(d * SR); tt = np.arange(n) / SR
    f = np.geomspace(f0, f1, n); s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return s * np.exp(-tt * 45) * 0.8
def ding(f=1568, d=1.4):
    n = int(d * SR); tt = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * f * m * tt) * np.exp(-tt * dk) for m, a, dk in [(1, 1, 3.5), (2.0, .45, 5), (2.76, .25, 7), (5.4, .12, 10)])
    return s / 1.8 * np.minimum(1, tt / 0.003) * 0.6
def kaching():
    a = ding(2093, 0.9) * 0.6; b = ding(2637, 1.2) * 0.6
    out = np.zeros(int(1.4 * SR)); out[:len(a)] += a; o = int(0.08 * SR); out[o:o + len(b)] += b
    nz = signal.sosfilt(signal.butter(2, [3000, 9000], 'band', fs=SR, output='sos'), rng.standard_normal(int(0.06 * SR))) * 0.5
    out[:len(nz)] += nz; return out
def bloop():
    n = int(0.16 * SR); tt = np.arange(n) / SR
    f = np.geomspace(260, 1400, n); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 22)
    return s * 0.7
def riser(d=0.7):
    n = int(d * SR); tt = np.arange(n) / SR
    x = whoosh(d, True) * 0.6
    f = np.geomspace(200, 1600, n); tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15
    return (x + tone) * np.linspace(0.1, 1, n) ** 2
def tick():
    n = int(0.03 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * 2200 * tt) * np.exp(-tt * 200) * 0.5

def sfx_track():
    L = int((TOTAL + 1.5) * SR); tr = np.zeros(L)
    def add(x, t, g=1.0):
        i = int(max(0, t) * SR); x = x[:L - i]; tr[i:i + len(x)] += x * g
    # hook
    add(boom(), T('hook', 0.0), 0.9); add(pop(), T('hook', 0.0), 0.5); add(pop(f0=1500), T('hook', 0.18), 0.45)
    add(pop(f0=1700, f1=600), T('hook', 2.06), 0.35)  # RUINING
    # hot water card
    add(whoosh(0.4), T('n1a', -0.15), 0.8); add(boom(0.7), T('n1a', 0.0), 0.55); add(pop(), T('n1b', 0.02), 0.55)
    add(pop(f0=1500, f1=500), T('n1c', 0.16), 0.35); add(bloop(), T('n1c', 2.50), 0.4)
    add(pop(f0=900, f1=300), T('n1d', 1.44), 0.4); add(pop(f0=1200, f1=400), T('n1d', 2.26), 0.4)
    # #2
    add(whoosh(0.4, False), SEG['n2a']['t0'] - 0.15, 0.8); add(boom(0.7), SEG['n2a']['t0'], 0.55); add(pop(), T('n2b', 0.02), 0.55)
    add(pop(f0=900, f1=300), T('nosun', 0.08), 0.5)
    add(ding(1760, 0.9), T('uva', 2.32), 0.35)  # NOVEMBER
    # #3
    add(whoosh(0.4), SEG['n3']['t0'] - 0.15, 0.8); add(boom(0.7), T('n3', 0.0), 0.55); add(pop(), T('n3', 1.12), 0.5); add(pop(f0=1500), T('n3', 1.26), 0.45)
    add(bloop(), T('heat', 2.52), 0.6); add(bloop(), T('heat', 2.70), 0.4)  # WATER
    # fix
    add(riser(0.75), T('fix', 0.70) - 0.75, 0.7); add(boom(0.9), T('fix', 0.70), 0.7); add(ding(1318, 1.6), T('fix', 0.72), 0.45)
    # porceramid price
    add(whoosh(0.4, False), SEG['porc']['t0'] - 0.15, 0.7); add(kaching(), T('porc', 1.15), 0.5)
    add(pop(f0=1100, f1=500), T('save', 0.68), 0.5)
    # cta
    add(whoosh(0.5), T('cta', -0.2), 0.8); add(boom(0.8), T('cta', 0.1), 0.6); add(pop(), T('cta', 0.3), 0.5)
    add(ding(2093, 1.4), T('cta', 0.8), 0.45); add(tick(), T('cta', 1.0), 0.6)
    return tr

_clean = {}
def clean_clip(clip):
    """Whole-clip denoise with a noise profile taken from the clip's quietest moments, then a soft expander."""
    if clip in _clean: return _clean[clip]
    import noisereduce as nr
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(SRC, clip + '.mov'), '-vn', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    x = signal.sosfilt(signal.butter(4, 90, 'high', fs=SR, output='sos'), x)
    hop = int(0.05 * SR)
    rms = np.array([np.sqrt(np.mean(x[j:j + hop] ** 2)) for j in range(0, len(x) - hop, hop)])
    q = np.argsort(rms)[:max(10, len(rms) // 6)]
    noise = np.concatenate([x[j * hop:(j + 1) * hop] for j in sorted(q)])
    y = nr.reduce_noise(y=x, sr=SR, y_noise=noise, stationary=True, prop_decrease=0.95, n_fft=2048, freq_mask_smooth_hz=300, time_mask_smooth_ms=60)
    y = nr.reduce_noise(y=y, sr=SR, stationary=False, prop_decrease=0.6, n_fft=2048)
    # expander: pull down what is left between words (-14 dB), smooth so words are never clipped
    env = np.array([np.sqrt(np.mean(y[j:j + hop] ** 2)) for j in range(0, len(y), hop)])
    edb = 20 * np.log10(env + 1e-9); thr = np.percentile(edb, 92) - 24
    g = np.where(edb > thr, 1.0, 10 ** (-14 / 20))
    g = np.maximum.reduce([g, np.roll(g, 1), np.roll(g, 2), np.roll(g, -1), np.roll(g, -2), np.roll(g, -3)])  # hold/lookahead
    g = np.convolve(g, np.ones(3) / 3, 'same')
    gs = np.interp(np.arange(len(y)), np.arange(len(g)) * hop + hop / 2, g)
    y = y * gs
    _clean[clip] = y.astype(np.float32); return _clean[clip]

def voice_track():
    parts = []
    for s in TL:
        n = int(round(s['dur'] * FPS)) * SR // FPS
        if s['kind'] == 'card': parts.append(np.zeros(n)); continue
        full = clean_clip(s['clip']); a = int(s['a'] * SR)
        x = full[a:a + n].astype(float)
        if len(x) < n: x = np.pad(x, (0, n - len(x)))
        f = int(0.012 * SR); x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
        parts.append(x)
    return np.concatenate(parts)

if __name__ == '__main__':
    from scipy.io import wavfile
    out = sys.argv[1]; only = sys.argv[2] if len(sys.argv) > 2 else 'all'
    base = out[:-4]
    vo = voice_track(); wavfile.write(base + '_voice.wav', SR, vo.astype(np.float32))
    # voice polish: rumble cut, denoise, presence, compression, loudness
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', base + '_voice.wav', '-af',
        'highpass=f=90,lowpass=f=13000,afftdn=nr=10:nf=-50:tn=1,equalizer=f=3000:t=q:w=1.2:g=3,equalizer=f=220:t=q:w=1:g=-2.5,equalizer=f=8000:t=q:w=1:g=-2,acompressor=threshold=-24dB:ratio=4:attack=5:release=100:makeup=6,loudnorm=I=-12:TP=-1:LRA=5,alimiter=limit=0.95',
        '-ar', str(SR), base + '_voice_p.wav'], check=True)
    sr, v = wavfile.read(base + '_voice_p.wav'); v = v.astype(np.float32)
    if v.dtype != np.float32 or np.abs(v).max() > 2: v = v / 32768.0
    sf = sfx_track()
    L = max(len(v), int(TOTAL * SR)); mix = np.zeros(int(TOTAL * SR))
    mix[:min(len(v), len(mix))] += v[:len(mix)]
    mix += sf[:len(mix)] * 0.32
    fo = int(0.25 * SR); mix[-fo:] *= np.linspace(1, 0, fo)
    mix = np.tanh(mix * 1.0) / np.tanh(1.0) * 0.97
    wavfile.write(base + '_mix.wav', SR, mix.astype(np.float32))
    print('audio ok', TOTAL, flush=True)
    if only == 'audio': sys.exit()
    build_video(base + '_v.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', base + '_v.mp4', '-i', base + '_mix.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k',
                    '-movflags', '+faststart', '-shortest', out], check=True)
    print('done', out)
