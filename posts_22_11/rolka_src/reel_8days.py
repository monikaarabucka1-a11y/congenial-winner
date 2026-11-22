# "8 days left" Black Friday reel: photos + kinetic text + SFX (no music).
import sys, os, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/user/congenial-winner/posts_19_11/rolka_R3')
import edit as E  # reuse text sprites, easing, SFX synths
from scipy.io import wavfile

D = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, SR = 1080, 1920, 30, 48000
out_path = sys.argv[1]

def load(name): return Image.open(os.path.join(D, name)).convert('RGB')
def cover(img, fx=0.5, fy=0.5, extra=1.18):
    s = max(W / img.width, H / img.height) * extra
    im = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
    x = int((im.width - W * 1.0) * fx); y = int((im.height - H * 1.0) * fy)
    return np.array(im), (x, y)

def kb(base, off, p, z0=1.0, z1=1.08, dx=0, dy=0):
    arr, (x, y) = base
    s = z0 + (z1 - z0) * p
    cw, ch = W / s * 1.0, H / s * 1.0
    cx = x + W / 2 + dx * p; cy = y + H / 2 + dy * p
    M = np.float32([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]])
    return cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def darken(f, a): return (f.astype(np.float32) * a).astype(np.uint8)

# segments: (name, dur)
SEGS = [('hook', 2.4), ('rf', 2.8), ('lift', 2.8), ('cer', 2.8), ('glow', 3.4), ('when', 2.2), ('cta', 3.0)]
T0 = {}; t = 0
for n, d in SEGS: T0[n] = t; t += d
TOTAL = t; NF = int(round(TOTAL * FPS))
B = {
 'hook': cover(load('salon.jpg'), 0.35, 0.5, 1.1),
 'rf': cover(load('rf_photo.jpg'), 0.5, 0.45, 1.12),
 'lift': cover(load('z4.jpg'), 0.45, 0.5, 1.05),
 'cer': cover(load('ceramide_caps.jpg'), 0.45, 0.5, 1.1),
 'before': cover(load('before.jpg'), 0.5, 0.4, 1.06),
 'after': cover(load('after.jpg'), 0.5, 0.4, 1.06),
 'when': cover(load('k2.jpg'), 0.5, 0.55, 1.1),
}
PRODUCTS = {
 'rf':   ('RF MICRONEEDLING', 'fine lines · pores · scars', '£110', '£180'),
 'lift': ('ELASTISTROM & RF', 'a lift without needles', '£130', '£210'),
 'cer':  ('PORCERAMID', 'smooth, calm winter skin', '£55', '£85'),
 'glow': ('HYDROGEN PURE GLOW', 'deep cleanse · real glow', '£55', '£75'),
}
F = E.font
TOPG = E.vgrad(True, 0, 700, 0.75, 0.0); BOTG = E.vgrad(False, 1050, 1650, 0.0, 0.85)
logo = E.logo

def bg_frame(n, rel, dur):
    p = rel / dur
    if n == 'hook': return darken(kb(B['hook'], None, p, 1.0, 1.12), 0.45)
    if n == 'rf': return kb(B['rf'], None, p, 1.0, 1.10, 0, -60)
    if n == 'lift': return kb(B['lift'], None, p, 1.04, 1.12, -40, 0)
    if n == 'cer': return kb(B['cer'], None, p, 1.0, 1.10, 0, 30)
    if n == 'glow':
        b = kb(B['before'], None, p, 1.0, 1.05); a = kb(B['after'], None, p, 1.0, 1.05)
        w = E.in_out((rel - 1.0) / 0.55)  # wipe before -> after
        x = int(W * w); f = b.copy(); f[:, :x] = a[:, :x]
        if 0 < x < W: f[:, max(0, x - 3):x + 3] = (240, 210, 160)
        return f
    if n == 'when': return darken(cv2.GaussianBlur(kb(B['when'], None, p, 1.0, 1.06), (0, 0), 14), 0.42)
    if n == 'cta':
        g = np.zeros((H, W, 3), np.uint8); g[:] = (7, 9, 11)
        yy = np.linspace(0, 1, H)[:, None]; glow = np.exp(-((yy - 0.42) ** 2) / 0.02) * 40
        g = np.clip(g + glow[..., None] * np.array([0.35, 0.55, 0.85]), 0, 255).astype(np.uint8)
        return g

def pop(k, d=7): return 0.3 + 0.7 * E.out_back(k / d)
def fade(k, d=3): return E.clamp(k / d)

def overlay(c, n, rel):
    k = rel * FPS
    if n == 'hook':
        E.paste(c, E.pill_sprite('BLACK FRIDAY AT ELYSIUM', F('mont800.ttf', 40)), W / 2, 430, pop(k - 12), fade(k - 12))
        E.paste(c, E.text_sprite('8', F('pf800.ttf', 620), 'gold', stroke=10), W / 2, 860, 0.55 + 0.45 * E.out_back((k + 1) / 7, 2.6), 1)
        E.paste(c, E.text_sprite('DAYS LEFT', F('mont800.ttf', 120), E.WHITE, stroke=9), W / 2, 1250, pop(k - 7), fade(k - 7))
        return
    if n in PRODUCTS:
        name, sub, price, old = PRODUCTS[n]
        E.paste(c, E.text_sprite(name, F('mont800.ttf', 86), E.WHITE, stroke=9), W / 2, 330, pop(k - 2) * min(1, 960 / E.text_sprite(name, F('mont800.ttf', 86), E.WHITE, stroke=9).width), fade(k - 2))
        E.paste(c, E.text_sprite(sub, F('pf700i.ttf', 60), E.CREAM, stroke=6), W / 2, 430 + (1 - E.out_cubic((k - 8) / 6)) * 24, 1, fade(k - 8, 4))
        kp = k - (40 if n == 'glow' else 14)
        if kp > -1:
            ps = E.text_sprite(price, F('pf800.ttf', 230), 'gold', stroke=9)
            so = E.text_sprite(old, F('mont600.ttf', 72), (200, 185, 165), stroke=6)
            ov = 30  # sprite padding overlap
            tot = ps.width + so.width - ov
            px = W / 2 - tot / 2 + ps.width / 2; ox = px + ps.width / 2 + so.width / 2 - ov
            E.paste(c, ps, px, 1270, pop(kp, 8), fade(kp, 2))
            E.paste(c, so, ox, 1310, pop(kp - 4), fade(kp - 4))
            a = E.clamp((kp - 8) / 5)
            if a > 0:
                hw = (so.width - 72) / 2; d = ImageDraw.Draw(c)
                d.line((ox - hw, 1316, ox - hw + 2 * hw * a, 1316), fill=(232, 84, 70, 255), width=8)
        if n == 'glow':
            lab = 'AFTER' if rel > 1.3 else 'BEFORE'
            E.paste(c, E.pill_sprite(lab, F('mont800.ttf', 34), padx=36, pady=16), W / 2, 1010, 1, 1)
            if rel > 1.3: E.paste(c, E.text_sprite('Real client · one treatment · results vary', F('mont600.ttf', 30), E.CREAM, stroke=5), W / 2, 1450, 1, fade(k - 42, 4))
        return
    if n == 'when':
        E.paste(c, E.text_sprite('Book by', F('pf700i.ttf', 80), E.CREAM, stroke=6), W / 2, 640, pop(k - 2), fade(k - 2))
        E.paste(c, E.text_sprite('30 NOVEMBER', F('mont800.ttf', 120), 'gold', stroke=9), W / 2, 780, pop(k - 6), fade(k - 6))
        E.paste(c, E.text_sprite('use any time until', F('pf700i.ttf', 70), E.CREAM, stroke=6), W / 2, 980, pop(k - 18), fade(k - 18))
        E.paste(c, E.text_sprite('31 JANUARY', F('mont800.ttf', 120), 'gold', stroke=9), W / 2, 1110, pop(k - 22), fade(k - 22))
        E.paste(c, E.text_sprite('perfect for your Christmas glow 🎁'.replace(' 🎁', ''), F('mont600.ttf', 40), E.CREAM, stroke=5), W / 2, 1290, 1, fade(k - 34, 5))
        return
    if n == 'cta':
        E.paste(c, E.text_sprite('SEND ME', F('mont800.ttf', 110), E.WHITE, stroke=9), W / 2, 600, pop(k - 2), fade(k - 2))
        E.paste(c, E.pill_sprite('“BF”', F('mont800.ttf', 150), padx=90, pady=34), W / 2, 820, pop(k - 8, 8), fade(k - 8), rot=-3 * (1 - E.out_cubic((k - 8) / 10)))
        E.paste(c, E.text_sprite('in DM to book', F('pf700i.ttf', 72), E.CREAM, stroke=6), W / 2, 1010 + (1 - E.out_cubic((k - 16) / 6)) * 30, 1, fade(k - 16, 4))
        E.paste(c, E.text_sprite('or tap the link in bio', F('mont600.ttf', 40), (200, 185, 165), stroke=5), W / 2, 1110, 1, fade(k - 24, 4))
        E.paste(c, logo, W / 2, 1330, 1, fade(k - 30, 6))

SLAMS = [T0['hook'], T0['rf'] + 14 / FPS, T0['lift'] + 14 / FPS, T0['cer'] + 14 / FPS, T0['glow'] + 40 / FPS, T0['cta'] + 8 / FPS]
TRANS = {T0['rf']: 'flash', T0['lift']: 'whip', T0['cer']: 'whip', T0['glow']: 'whip', T0['when']: 'zoom', T0['cta']: 'zoom'}

def render_video(path):
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    bounds = {int(round(v * FPS)): k for v, k in TRANS.items()}
    for fi in range(NF):
        t = fi / FPS
        n = max((s for s in SEGS if T0[s[0]] <= t + 1e-6), key=lambda s: T0[s[0]])[0]
        dur = dict(SEGS)[n]; rel = t - T0[n]
        f = bg_frame(n, rel, dur)
        for b, kind in bounds.items():
            d = fi - b
            if kind == 'whip' and -4 <= d < 4:
                sh = [-40, -140, -330, -620][d + 4] if d < 0 else [620, 330, 140, 40][d]
                f = E.motion_blur(np.roll(f, sh, 1), abs(sh) * 0.5)
            if kind == 'zoom' and -4 <= d < 5:
                if d < 0: f = cv2.GaussianBlur(E.zoom(f, 1 + 0.1 * (d + 5) / 4, (W / 2, H / 2)), (0, 0), 2 + 3 * (d + 5))
                else: f = E.zoom(f, 1.25 - 0.25 * E.out_cubic(d / 5), (W / 2, H / 2))
            if kind == 'flash' and 0 <= d < 6:
                a = (1 - d / 6) ** 1.5 * 0.85; f = (f.astype(np.float32) * (1 - a) + 255 * a).astype(np.uint8)
        for ts in SLAMS:
            d = t - ts
            if 0 <= d < 0.2:
                amp = 14 * (1 - d / 0.2); f = np.roll(np.roll(f, int(amp * math.sin(d * 90)), 1), int(amp * math.cos(d * 70)), 0)
        c = Image.fromarray(f).convert('RGBA')
        if n not in ('cta',): c.alpha_composite(TOPG); c.alpha_composite(BOTG)
        overlay(c, n, rel)
        ImageDraw.Draw(c).rectangle((0, 0, int(W * (fi + 1) / NF), 8), fill=E.GOLD + (230,))
        enc.stdin.write(np.array(c.convert('RGB')).tobytes())
    enc.stdin.close(); enc.wait()

def render_audio(path):
    L = int((TOTAL + 1) * SR); tr = np.zeros(L)
    def add(x, t, g=1.0):
        i = int(max(0, t) * SR); x = x[:L - i]; tr[i:i + len(x)] += x * g
    # clock ticks = countdown pulse (no music)
    tk = E.tick()
    for i in range(int(T0['cta'] / 0.5)):
        add(tk * (1.0 if i % 2 == 0 else 0.6), i * 0.5, 0.5)
    add(E.boom(1.0), 0, 0.9); add(E.pop(), 7 / FPS, 0.5); add(E.pop(f0=1500), 12 / FPS, 0.45)
    for n in ('rf', 'lift', 'cer', 'glow'):
        add(E.whoosh(0.4), T0[n] - 0.15, 0.7); add(E.pop(), T0[n] + 2 / FPS, 0.45)
        add(E.kaching(), T0[n] + (40 if n == 'glow' else 14) / FPS, 0.45)
    add(E.whoosh(0.6), T0['glow'] + 0.95, 0.5); add(E.ding(1760, 1.0), T0['glow'] + 1.3, 0.35)
    add(E.whoosh(0.5), T0['when'] - 0.2, 0.7); add(E.pop(), T0['when'] + 6 / FPS, 0.5); add(E.pop(f0=1500), T0['when'] + 22 / FPS, 0.5)
    add(E.whoosh(0.5), T0['cta'] - 0.2, 0.8); add(E.boom(0.8), T0['cta'] + 8 / FPS, 0.6); add(E.ding(2093, 1.4), T0['cta'] + 16 / FPS, 0.45)
    mix = tr[:int(TOTAL * SR)] * 1.7
    fo = int(0.3 * SR); mix[-fo:] *= np.linspace(1, 0, fo)
    mix = np.tanh(mix * 1.2) / np.tanh(1.2) * 0.9
    wavfile.write(path, SR, mix.astype(np.float32))

if __name__ == '__main__':
    base = out_path[:-4]
    render_audio(base + '.wav'); render_video(base + '_v.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', base + '_v.mp4', '-i', base + '.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    '-movflags', '+faststart', '-shortest', out_path], check=True)
    print('done', TOTAL)
