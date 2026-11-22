# RF before/after reel: real client photos, wipes, kinetic text, SFX (no music).
import sys, os, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '/home/user/congenial-winner/posts_19_11/rolka_R3')
import edit as E
from scipy.io import wavfile

D = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, SR = 1080, 1920, 30, 48000
F = E.font

def load(n):
    im = Image.open(os.path.join(D, n)).convert('RGB')
    if n == 'profil_przed.jpg':  # hide device brand name in the background
        box = (0, 1080, 170, 1560); reg = im.crop(box).filter(ImageFilter.GaussianBlur(40)); im.paste(reg, box)
    return im

def cover(img, fx=0.5, fy=0.5, extra=1.0):
    s = max(W / img.width, H / img.height) * extra
    im = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
    return np.array(im), (int((im.width - W) * fx), int((im.height - H) * fy))

def kb(base, p, z0=1.0, z1=1.06, dx=0, dy=0):
    arr, (x, y) = base; s = z0 + (z1 - z0) * p
    cx = x + W / 2 + dx * p; cy = y + H / 2 + dy * p
    M = np.float32([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]])
    return cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

B = {
 'pb': cover(load('profil_przed.jpg'), 0.55, 0.45), 'pa': cover(load('profil_po.jpg'), 0.55, 0.45),
 'fb': cover(load('front_przed.jpg'), 0.5, 0.4), 'fa': cover(load('front_po.jpg'), 0.5, 0.42),
}
def half(img):  # for split screen: 540 wide
    a = np.array(img); h, w = a.shape[:2]; s = H / h; a = cv2.resize(a, (int(w * s), H), interpolation=cv2.INTER_AREA)
    x = (a.shape[1] - 540) // 2; return a[:, x:x + 540]
SPLIT = np.concatenate([half(load('front_przed.jpg')), half(load('front_po.jpg'))], 1)

SEGS = [('prof', 3.6), ('front', 3.4), ('facts', 3.4), ('split', 2.4), ('price', 2.8), ('cta', 3.0)]
T0 = {}; t = 0
for n, d in SEGS: T0[n] = t; t += d
TOTAL = t; NF = int(round(TOTAL * FPS))
WIPE = {'prof': 1.3, 'front': 1.1}
TOPG = E.vgrad(True, 0, 700, 0.8, 0.0); BOTG = E.vgrad(False, 1150, 1700, 0.0, 0.8)

def dark(f, a): return (f.astype(np.float32) * a).astype(np.uint8)
def wipe(b, a, rel, t0):
    w = E.in_out((rel - t0) / 0.55); x = int(W * w); f = b.copy(); f[:, :x] = a[:, :x]
    if 0 < x < W: f[:, max(0, x - 4):x + 4] = (240, 210, 160)
    return f

def bg(n, rel, dur):
    p = rel / dur
    if n == 'prof': return wipe(kb(B['pb'], p, 1.08, 1.0), kb(B['pa'], p, 1.08, 1.0), rel, WIPE['prof'])
    if n == 'front': return wipe(kb(B['fb'], p, 1.0, 1.07), kb(B['fa'], p, 1.0, 1.07), rel, WIPE['front'])
    if n == 'facts': return dark(cv2.GaussianBlur(kb(B['fa'], p, 1.05, 1.1), (0, 0), 16), 0.4)
    if n == 'split':
        f = SPLIT.copy(); f[:, 538:542] = (240, 210, 160); return E.zoom(f, 1.0 + 0.04 * p, (W / 2, H / 2))
    if n == 'price': return dark(cv2.GaussianBlur(kb(B['pa'], p, 1.05, 1.1), (0, 0), 18), 0.38)
    if n == 'cta':
        g = np.zeros((H, W, 3), np.float32); yy = np.linspace(0, 1, H)[:, None]
        g += np.exp(-((yy - 0.42) ** 2) / 0.02)[..., None] * np.array([34, 22, 12]); g += np.array([11, 9, 7])
        return np.clip(g, 0, 255).astype(np.uint8)

def pop(k, d=7): return 0.3 + 0.7 * E.out_back(k / d)
def fade(k, d=3): return E.clamp(k / d)
def label(c, txt, y=1480): E.paste(c, E.pill_sprite(txt, F('mont800.ttf', 38), padx=40, pady=18), W / 2, y, 1, 1)
def lift(k, d=6): return (1 - E.out_cubic(k / d)) * 26

def overlay(c, n, rel):
    k = rel * FPS
    if n == 'prof':
        E.paste(c, E.text_sprite('ONE RF SESSION', F('mont800.ttf', 104), 'gold', stroke=9), W / 2, 300, 0.55 + 0.45 * E.out_back((k + 1) / 7), 1)
        E.paste(c, E.text_sprite('before → straight after', F('pf700i.ttf', 64), E.CREAM, stroke=6), W / 2, 410 + lift(k - 6), 1, fade(k - 6, 4))
        kw = (rel - WIPE['prof'] - 0.5) * FPS
        label(c, 'STRAIGHT AFTER' if kw > 0 else 'BEFORE')
        E.paste(c, E.text_sprite('Real client · results vary', F('mont600.ttf', 30), E.CREAM, stroke=5), W / 2, 1570, 1, 1)
        return
    if n == 'front':
        kw = (rel - WIPE['front'] - 0.5) * FPS
        label(c, 'STRAIGHT AFTER' if kw > 0 else 'BEFORE')
        E.paste(c, E.text_sprite('Real client · results vary', F('mont600.ttf', 30), E.CREAM, stroke=5), W / 2, 1570, 1, 1)
        for i, (w, g) in enumerate([('PLUMPER', 0), ('SMOOTHER', 1), ('GLOWING', 0)]):
            kk = kw - i * 5
            if kk > -1: E.paste(c, E.text_sprite(w, F('mont800.ttf', 96), 'gold' if g else E.WHITE, stroke=9), W / 2, 280 + i * 110, pop(kk), fade(kk, 2))
        return
    if n == 'facts':
        E.paste(c, E.text_sprite('What happens next?', F('pf700i.ttf', 78), E.CREAM, stroke=6), W / 2, 470, pop(k - 2), fade(k - 2))
        rows = [('1–2 DAYS', 'the redness settles'), ('4–6 WEEKS', 'new collagen keeps building'), ('3 SESSIONS', 'for the best results')]
        for i, (a, b) in enumerate(rows):
            kk = k - 12 - i * 14
            if kk > -1:
                E.paste(c, E.text_sprite(a, F('mont800.ttf', 100), 'gold', stroke=9), W / 2, 720 + i * 260, pop(kk), fade(kk, 2))
                E.paste(c, E.text_sprite(b, F('mont600.ttf', 46), E.CREAM, stroke=6), W / 2, 820 + i * 260 + lift(kk - 3), 1, fade(kk - 3, 4))
        return
    if n == 'split':
        E.paste(c, E.pill_sprite('BEFORE', F('mont800.ttf', 34), padx=34, pady=16), 270, 1480, pop(k), 1)
        E.paste(c, E.pill_sprite('AFTER', F('mont800.ttf', 34), padx=34, pady=16), 810, 1480, pop(k - 3), 1)
        E.paste(c, E.text_sprite('Same skin. One session.', F('pf700i.ttf', 70), E.WHITE, stroke=7), W / 2, 330, pop(k - 4), fade(k - 4))
        return
    if n == 'price':
        E.paste(c, E.pill_sprite('BLACK FRIDAY · 8 DAYS LEFT', F('mont800.ttf', 38)), W / 2, 450, pop(k - 1), fade(k - 1))
        E.paste(c, E.text_sprite('RF MICRONEEDLING', F('mont800.ttf', 92), E.WHITE, stroke=9), W / 2, 640, pop(k - 4), fade(k - 4))
        ps = E.text_sprite('£110', F('pf800.ttf', 250), 'gold', stroke=9); so = E.text_sprite('£180', F('mont600.ttf', 76), (200, 185, 165), stroke=6)
        tot = ps.width + so.width - 30; px = W / 2 - tot / 2 + ps.width / 2; ox = px + ps.width / 2 + so.width / 2 - 30
        E.paste(c, ps, px, 880, pop(k - 10, 8), fade(k - 10, 2)); E.paste(c, so, ox, 920, pop(k - 14), fade(k - 14))
        a = E.clamp((k - 18) / 5)
        if a > 0:
            hw = (so.width - 72) / 2; ImageDraw.Draw(c).line((ox - hw, 926, ox - hw + 2 * hw * a, 926), fill=(232, 84, 70, 255), width=8)
        E.paste(c, E.text_sprite('Book by 30.11 · use until 31.01', F('mont600.ttf', 46), E.CREAM, stroke=6), W / 2, 1110 + lift(k - 24), 1, fade(k - 24, 4))
        return
    if n == 'cta':
        E.paste(c, E.text_sprite('SEND ME', F('mont800.ttf', 110), E.WHITE, stroke=9), W / 2, 600, pop(k - 2), fade(k - 2))
        E.paste(c, E.pill_sprite('“RF”', F('mont800.ttf', 150), padx=90, pady=34), W / 2, 820, pop(k - 8, 8), fade(k - 8), rot=-3 * (1 - E.out_cubic((k - 8) / 10)))
        E.paste(c, E.text_sprite('in DM to book', F('pf700i.ttf', 72), E.CREAM, stroke=6), W / 2, 1010 + lift(k - 16), 1, fade(k - 16, 4))
        E.paste(c, E.logo, W / 2, 1300, 1, fade(k - 26, 6))

SLAMS = [0, T0['prof'] + WIPE['prof'] + 0.5, T0['front'] + WIPE['front'] + 0.5, T0['split'], T0['price'] + 10 / FPS, T0['cta'] + 8 / FPS]
TRANS = {T0['front']: 'whip', T0['facts']: 'zoom', T0['split']: 'flash', T0['price']: 'whip', T0['cta']: 'zoom'}

def render_video(path):
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    bounds = {int(round(v * FPS)): k for v, k in TRANS.items()}
    for fi in range(NF):
        t = fi / FPS
        n = max((s for s in SEGS if T0[s[0]] <= t + 1e-6), key=lambda s: T0[s[0]])[0]
        dur = dict(SEGS)[n]; rel = t - T0[n]
        f = bg(n, rel, dur)
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
            if 0 <= d < 0.18:
                amp = 12 * (1 - d / 0.18); f = np.roll(np.roll(f, int(amp * math.sin(d * 90)), 1), int(amp * math.cos(d * 70)), 0)
        c = Image.fromarray(f).convert('RGBA')
        if n != 'cta': c.alpha_composite(TOPG); c.alpha_composite(BOTG)
        overlay(c, n, rel)
        ImageDraw.Draw(c).rectangle((0, 0, int(W * (fi + 1) / NF), 8), fill=E.GOLD + (230,))
        enc.stdin.write(np.array(c.convert('RGB')).tobytes())
    enc.stdin.close(); enc.wait()

def render_audio(path):
    L = int((TOTAL + 1) * SR); tr = np.zeros(L)
    def add(x, t, g=1.0):
        i = int(max(0, t) * SR); x = x[:L - i]; tr[i:i + len(x)] += x * g
    add(E.boom(1.0), 0, 0.9); add(E.pop(), 6 / FPS, 0.4)
    for s in ('prof', 'front'):
        w = T0[s] + WIPE[s]; add(E.riser(0.5), w - 0.5, 0.5); add(E.whoosh(0.55), w, 0.7); add(E.boom(0.7), w + 0.5, 0.5); add(E.ding(1760, 1.0), w + 0.5, 0.35)
    for i in range(3): add(E.pop(f0=1300 + i * 200), T0['front'] + WIPE['front'] + 0.5 + i * 5 / FPS, 0.45)
    add(E.whoosh(0.4), T0['front'] - 0.15, 0.7); add(E.whoosh(0.5), T0['facts'] - 0.2, 0.6); add(E.pop(), T0['facts'] + 2 / FPS, 0.4)
    for i in range(3): add(E.pop(f0=1100 + i * 250), T0['facts'] + (12 + i * 14) / FPS, 0.5); add(E.tick(), T0['facts'] + (15 + i * 14) / FPS, 0.5)
    add(E.boom(0.8), T0['split'], 0.6); add(E.pop(), T0['split'] + 3 / FPS, 0.4)
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
