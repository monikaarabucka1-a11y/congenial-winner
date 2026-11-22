# ElastiStrom & RF Contour before/after reel — DETAIL CROPS ONLY (client consented to details, not full face).
import sys, os, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '/home/user/congenial-winner/posts_19_11/rolka_R3')
import edit as E
from scipy.io import wavfile

D = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[2] if len(sys.argv) > 2 else D   # folder with rotated photos (kept out of the repo)
sys.path.insert(0, SRC)
from crops import CROPS
W, H, FPS, SR = 1080, 1920, 30, 48000
F = E.font
CW, CH = 820, 574
TOP_Y, BOT_Y = 380 + CH // 2, 980 + CH // 2

def card(key, scale=1.0):
    f, b = CROPS[key]
    im = Image.open(os.path.join(SRC, f + '.jpg')).convert('RGB').crop(b)
    return np.array(im.resize((int(CW * 1.08), int(CH * 1.08)), Image.LANCZOS))
CARDS = {k: card(k) for k in CROPS}
MASK = Image.new('L', (CW + 12, CH + 12)); ImageDraw.Draw(MASK).rounded_rectangle((6, 6, CW + 6, CH + 6), 28, fill=255)
SHADOW = Image.new('RGBA', (CW + 80, CH + 80)); ImageDraw.Draw(SHADOW).rounded_rectangle((40, 50, CW + 40, CH + 50), 30, fill=(0, 0, 0, 170))
SHADOW = SHADOW.filter(ImageFilter.GaussianBlur(18))

def card_img(key, p):
    a = CARDS[key]; s = 1.0 + 0.04 * p
    h, w = a.shape[:2]; cw, ch = int(CW * 1.08 / s), int(CH * 1.08 / s)
    x, y = (w - cw) // 2, (h - ch) // 2
    crop = cv2.resize(a[y:y + ch, x:x + cw], (CW, CH), interpolation=cv2.INTER_AREA)
    im = Image.new('RGBA', (CW + 12, CH + 12), (216, 173, 116, 255))
    inner = Image.new('RGBA', (CW + 12, CH + 12)); inner.paste(Image.fromarray(crop), (6, 6))
    border = Image.new('L', (CW + 12, CH + 12)); ImageDraw.Draw(border).rounded_rectangle((0, 0, CW + 11, CH + 11), 32, fill=255)
    out = Image.new('RGBA', (CW + 12, CH + 12)); out.paste(im, (0, 0), border); out.paste(inner, (0, 0), MASK)
    return out

SEGS = [('A', 3.6), ('B', 3.0), ('C', 3.0), ('how', 3.2), ('price', 2.8), ('cta', 3.0)]
T0 = {}; t = 0
for n, d in SEGS: T0[n] = t; t += d
TOTAL = t; NF = int(round(TOTAL * FPS))
TITLES = {'A': ('SAME JAWLINE.', 'one session later'), 'B': ('FIRMER CONTOUR', 'jawline & neck'), 'C': ('FRESHER SKIN', 'with a healthy glow')}
AFTER_K = {'A': 30, 'B': 18, 'C': 18}  # frame when AFTER card lands

def bgbase():
    g = np.zeros((H, W, 3), np.float32); yy = np.linspace(0, 1, H)[:, None]
    g += np.exp(-((yy - 0.45) ** 2) / 0.05)[..., None] * np.array([40, 27, 14]); g += np.array([11, 9, 7])
    return np.clip(g, 0, 255).astype(np.uint8)
BG = bgbase()
BLUR = {k: (cv2.GaussianBlur(cv2.resize(CARDS[k], (W, int(W * CH / CW))), (0, 0), 20) * 0.35).astype(np.uint8) for k in ('A_a', 'B_a')}
def blurbg(k, p):
    a = BLUR[k]; f = BG.copy(); s = cv2.resize(a, (int(H * a.shape[1] / a.shape[0]), H)); x = (s.shape[1] - W) // 2 + int(30 * p)
    return s[:, x:x + W].copy()

def pop(k, d=7): return 0.3 + 0.7 * E.out_back(k / d)
def fade(k, d=3): return E.clamp(k / d)
def lift(k, d=6): return (1 - E.out_cubic(k / d)) * 26

def overlay(c, n, rel):
    k = rel * FPS; dur = dict(SEGS)[n]; p = rel / dur
    if n in TITLES:
        t1, t2 = TITLES[n]
        k0 = k + (1 if n == 'A' else -2)
        E.paste(c, E.text_sprite(t1, F('mont800.ttf', 96), 'gold', stroke=9), W / 2, 200, (0.55 + 0.45 * E.out_back(k0 / 7)) if n == 'A' else pop(k0), 1 if n == 'A' else fade(k0, 2))
        E.paste(c, E.text_sprite(t2, F('pf700i.ttf', 60), E.CREAM, stroke=6), W / 2, 300 + lift(k - 6), 1, fade(k - 6, 4))
        kb = k + (8 if n == 'A' else -2)
        if kb > -2:
            s = 0.6 + 0.4 * E.out_back(kb / 8); x = W / 2 - (1 - E.out_cubic(kb / 8)) * 700
            c.alpha_composite(SHADOW, (int(x - (CW + 80) / 2), int(TOP_Y - (CH + 80) / 2))) if kb > 6 else None
            E.paste(c, card_img(n + '_b', p), x, TOP_Y, s, fade(kb, 3))
            E.paste(c, E.pill_sprite('BEFORE', F('mont800.ttf', 32), padx=32, pady=14), W / 2 - CW / 2 + 110, TOP_Y - CH / 2 + 4, pop(kb - 6), fade(kb - 6))
        ka = k - AFTER_K[n]
        if ka > -2:
            s = 0.6 + 0.4 * E.out_back(ka / 8); x = W / 2 + (1 - E.out_cubic(ka / 8)) * 700
            if ka > 6: c.alpha_composite(SHADOW, (int(x - (CW + 80) / 2), int(BOT_Y - (CH + 80) / 2)))
            E.paste(c, card_img(n + '_a', p), x, BOT_Y, s, fade(ka, 3))
            E.paste(c, E.pill_sprite('AFTER', F('mont800.ttf', 32), padx=32, pady=14), W / 2 - CW / 2 + 100, BOT_Y - CH / 2 + 4, pop(ka - 6), fade(ka - 6))
        E.paste(c, E.text_sprite('Real client · shared with permission · results vary', F('mont600.ttf', 28), (200, 185, 165), stroke=5), W / 2, 1620, 1, 1)
        return
    if n == 'how':
        E.paste(c, E.pill_sprite('THE TREATMENT', F('mont800.ttf', 36)), W / 2, 470, pop(k - 1), fade(k - 1))
        E.paste(c, E.text_sprite('ELASTISTROM', F('mont800.ttf', 110), 'gold', stroke=9), W / 2, 650, pop(k - 4), fade(k - 4))
        E.paste(c, E.text_sprite('& RF CONTOUR', F('mont800.ttf', 90), E.WHITE, stroke=9), W / 2, 770, pop(k - 8), fade(k - 8))
        rows = [('needle-free RF', 'firms & tightens'), ('microcurrent gloves', 'sculpt jawline & neck')]
        for i, (a, b) in enumerate(rows):
            kk = k - 18 - i * 10
            if kk > -1:
                E.paste(c, E.text_sprite(a, F('pf700i.ttf', 66), E.CREAM, stroke=6), W / 2, 950 + i * 170, pop(kk), fade(kk, 2))
                E.paste(c, E.text_sprite(b, F('mont600.ttf', 42), (220, 205, 185), stroke=5), W / 2, 1025 + i * 170 + lift(kk - 3), 1, fade(kk - 3, 4))
        kk = k - 46
        if kk > -1: E.paste(c, E.pill_sprite('NO NEEDLES · NO DOWNTIME', F('mont800.ttf', 36)), W / 2, 1330, pop(kk), fade(kk))
        return
    if n == 'price':
        E.paste(c, E.pill_sprite('BLACK FRIDAY · 8 DAYS LEFT', F('mont800.ttf', 38)), W / 2, 450, pop(k - 1), fade(k - 1))
        E.paste(c, E.text_sprite('ELASTISTROM & RF', F('mont800.ttf', 92), E.WHITE, stroke=9), W / 2, 640, pop(k - 4), fade(k - 4))
        ps = E.text_sprite('£130', F('pf800.ttf', 250), 'gold', stroke=9); so = E.text_sprite('£210', F('mont600.ttf', 76), (200, 185, 165), stroke=6)
        tot = ps.width + so.width - 30; px = W / 2 - tot / 2 + ps.width / 2; ox = px + ps.width / 2 + so.width / 2 - 30
        E.paste(c, ps, px, 880, pop(k - 10, 8), fade(k - 10, 2)); E.paste(c, so, ox, 920, pop(k - 14), fade(k - 14))
        a = E.clamp((k - 18) / 5)
        if a > 0:
            hw = (so.width - 72) / 2; ImageDraw.Draw(c).line((ox - hw, 926, ox - hw + 2 * hw * a, 926), fill=(232, 84, 70, 255), width=8)
        E.paste(c, E.text_sprite('Book by 30.11 · use until 31.01', F('mont600.ttf', 46), E.CREAM, stroke=6), W / 2, 1110 + lift(k - 24), 1, fade(k - 24, 4))
        return
    if n == 'cta':
        E.paste(c, E.text_sprite('SEND ME', F('mont800.ttf', 110), E.WHITE, stroke=9), W / 2, 600, pop(k - 2), fade(k - 2))
        E.paste(c, E.pill_sprite('“LIFT”', F('mont800.ttf', 150), padx=90, pady=34), W / 2, 820, pop(k - 8, 8), fade(k - 8), rot=-3 * (1 - E.out_cubic((k - 8) / 10)))
        E.paste(c, E.text_sprite('in DM to book', F('pf700i.ttf', 72), E.CREAM, stroke=6), W / 2, 1010 + lift(k - 16), 1, fade(k - 16, 4))
        E.paste(c, E.logo, W / 2, 1300, 1, fade(k - 26, 6))

def bg(n, rel):
    p = rel / dict(SEGS)[n]
    if n == 'how': return blurbg('B_a', p)
    if n == 'price': return blurbg('A_a', p)
    return BG

SLAMS = [0] + [T0[s] + AFTER_K[s] / FPS for s in ('A', 'B', 'C')] + [T0['price'] + 10 / FPS, T0['cta'] + 8 / FPS]
TRANS = {T0['B']: 'whip', T0['C']: 'whip', T0['how']: 'zoom', T0['price']: 'whip', T0['cta']: 'zoom'}

def render_video(path):
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    bounds = {int(round(v * FPS)): k for v, k in TRANS.items()}
    for fi in range(NF):
        t = fi / FPS
        n = max((s for s in SEGS if T0[s[0]] <= t + 1e-6), key=lambda s: T0[s[0]])[0]; rel = t - T0[n]
        c = Image.fromarray(bg(n, rel)).convert('RGBA')
        overlay(c, n, rel)
        f = np.array(c.convert('RGB'))
        for b, kind in bounds.items():
            d = fi - b
            if kind == 'whip' and -4 <= d < 4:
                sh = [-40, -140, -330, -620][d + 4] if d < 0 else [620, 330, 140, 40][d]
                f = E.motion_blur(np.roll(f, sh, 1), abs(sh) * 0.5)
            if kind == 'zoom' and -4 <= d < 5:
                if d < 0: f = cv2.GaussianBlur(E.zoom(f, 1 + 0.1 * (d + 5) / 4, (W / 2, H / 2)), (0, 0), 2 + 3 * (d + 5))
                else: f = E.zoom(f, 1.25 - 0.25 * E.out_cubic(d / 5), (W / 2, H / 2))
        for ts in SLAMS:
            d = t - ts
            if 0 <= d < 0.18:
                amp = 12 * (1 - d / 0.18); f = np.roll(np.roll(f, int(amp * math.sin(d * 90)), 1), int(amp * math.cos(d * 70)), 0)
        f[:8, :int(W * (fi + 1) / NF)] = E.GOLD
        enc.stdin.write(f.tobytes())
    enc.stdin.close(); enc.wait()

def render_audio(path):
    L = int((TOTAL + 1) * SR); tr = np.zeros(L)
    def add(x, t, g=1.0):
        i = int(max(0, t) * SR); x = x[:L - i]; tr[i:i + len(x)] += x * g
    add(E.boom(1.0), 0, 0.85); add(E.pop(), 4 / FPS, 0.4)
    for s in ('A', 'B', 'C'):
        add(E.whoosh(0.4), T0[s] + 0.0, 0.6)                       # BEFORE card slides in
        add(E.whoosh(0.45, False), T0[s] + (AFTER_K[s] - 6) / FPS, 0.6)  # AFTER card
        add(E.boom(0.7), T0[s] + AFTER_K[s] / FPS, 0.5); add(E.ding(1760, 0.9), T0[s] + AFTER_K[s] / FPS, 0.3)
    add(E.whoosh(0.5), T0['how'] - 0.2, 0.6); add(E.pop(), T0['how'] + 4 / FPS, 0.45); add(E.pop(f0=1500), T0['how'] + 8 / FPS, 0.45)
    for i in range(2): add(E.pop(f0=1100 + i * 250), T0['how'] + (18 + i * 10) / FPS, 0.45)
    add(E.ding(1318, 1.2), T0['how'] + 46 / FPS, 0.35)
    add(E.whoosh(0.4), T0['price'] - 0.15, 0.7); add(E.kaching(), T0['price'] + 10 / FPS, 0.5)
    add(E.whoosh(0.5), T0['cta'] - 0.2, 0.8); add(E.boom(0.8), T0['cta'] + 8 / FPS, 0.6); add(E.ding(2093, 1.4), T0['cta'] + 16 / FPS, 0.45)
    mix = tr[:int(TOTAL * SR)] * 1.7; fo = int(0.3 * SR); mix[-fo:] *= np.linspace(1, 0, fo)
    wavfile.write(path, SR, (np.tanh(mix * 1.2) / np.tanh(1.2) * 0.9).astype(np.float32))

if __name__ == '__main__':
    out = sys.argv[1]; base = out[:-4]
    render_audio(base + '.wav'); render_video(base + '_v.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', base + '_v.mp4', '-i', base + '.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    '-movflags', '+faststart', '-shortest', out], check=True)
    print('done', TOTAL)
