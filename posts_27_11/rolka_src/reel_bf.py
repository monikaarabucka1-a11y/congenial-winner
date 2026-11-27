# "Christmas party: what to book & when" reel — photos + kinetic text + SFX (no music).
import sys, os, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/user/congenial-winner/posts_19_11/rolka_R3')
import edit as E
from scipy.io import wavfile
D = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, SR = 1080, 1920, 30, 48000
F = E.font
def load(n): return Image.open(os.path.join(D, n)).convert('RGB')
def cover(img, fx=.5, fy=.5, extra=1.1):
    s = max(W / img.width, H / img.height) * extra
    im = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
    return np.array(im), (int((im.width - W) * fx), int((im.height - H) * fy))
def kb(base, p, z0=1.0, z1=1.08, dx=0, dy=0):
    arr, (x, y) = base; s = z0 + (z1 - z0) * p
    cx = x + W / 2 + dx * p; cy = y + H / 2 + dy * p
    M = np.float32([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]])
    return cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
def dark(f, a): return (f.astype(np.float32) * a).astype(np.uint8)
B = {'hook': cover(load('gabinet.jpg'), .45, .5), 'booked': cover(load('rf_blue.jpg'), .5, .1), 'but': cover(load('party_woman.jpg'), .5, .2),
     'rf': cover(load('rf_photo.jpg'), .5, .45), 'lift': cover(load('k2.jpg'), .5, .55), 'cer': cover(load('ceramide_caps.jpg'), .45, .5),
     'glow': cover(load('glow_a.jpg'), .5, .4), 'pkg': cover(load('party_woman.jpg'), .5, .2)}
SEGS = [('hook', 2.6), ('booked', 2.6), ('but', 2.4), ('rf', 2.2), ('lift', 2.2), ('cer', 2.2), ('glow', 2.2), ('pkg', 2.4), ('when', 2.6), ('cta', 3.0)]
T0 = {}; t = 0
for n, d in SEGS: T0[n] = t; t += d
TOTAL = t; NF = int(round(TOTAL * FPS))
TOPG = E.vgrad(True, 0, 760, 0.85, 0.0); BOTG = E.vgrad(False, 1050, 1650, 0.0, 0.85)
ROWS = {'rf': ('RF MICRONEEDLING', 'lines · pores · scars', '£110', '£180'), 'lift': ('ELASTISTROM & RF', 'lift · no needles', '£130', '£210'),
        'cer': ('PORCERAMID', 'winter skin SOS', '£55', '£85'), 'glow': ('HYDROGEN PURE GLOW', 'instant glow', '£55', '£75'),
        'pkg': ('GLOW BEFORE CHRISTMAS', 'Hydrogen Pure Glow + PorCerAmid', '£75', '£160')}
def pop(k, d=7): return 0.3 + 0.7 * E.out_back(k / d)
def fade(k, d=3): return E.clamp(k / d)
def lift_(k, d=6): return (1 - E.out_cubic(k / d)) * 26
def bg(n, rel, dur):
    p = rel / dur
    if n == 'hook': return dark(kb(B['hook'], p, 1.0, 1.12), .4)
    if n == 'booked': return kb(B['booked'], p, 1.0, 1.06)
    if n == 'but': return dark(cv2.GaussianBlur(kb(B['but'], p, 1.05, 1.1), (0, 0), 14), .4)
    if n in ROWS: return kb(B[n], p, 1.0, 1.08, 0, -40)
    if n == 'when': return dark(cv2.GaussianBlur(kb(B['glow'], p, 1.05, 1.1), (0, 0), 16), .38)
    g = np.zeros((H, W, 3), np.float32); yy = np.linspace(0, 1, H)[:, None]
    g += np.exp(-((yy - .42) ** 2) / .02)[..., None] * np.array([34, 22, 12]); g += np.array([11, 9, 7])
    return np.clip(g, 0, 255).astype(np.uint8)
def price(c, k, p, o, y):
    ps = E.text_sprite(p, F('pf800.ttf', 200), 'gold', stroke=9); so = E.text_sprite(o, F('mont600.ttf', 64), (200, 185, 165), stroke=6)
    tot = ps.width + so.width - 30; px = W / 2 - tot / 2 + ps.width / 2; ox = px + ps.width / 2 + so.width / 2 - 30
    E.paste(c, ps, px, y, pop(k, 8), fade(k, 2)); E.paste(c, so, ox, y + 30, pop(k - 4), fade(k - 4))
    a = E.clamp((k - 8) / 5)
    if a > 0:
        hw = (so.width - 66) / 2; ImageDraw.Draw(c).line((ox - hw, y + 35, ox - hw + 2 * hw * a, y + 35), fill=(232, 84, 70, 255), width=7)
def overlay(c, n, rel):
    k = rel * FPS
    if n == 'hook':
        E.paste(c, E.pill_sprite('ELYSIUM CLINIC', F('mont800.ttf', 36)), W / 2, 520, pop(k - 12), fade(k - 12))
        E.paste(c, E.text_sprite('IT’S', F('mont800.ttf', 120), E.WHITE, stroke=10), W / 2, 700, 0.55 + 0.45 * E.out_back((k + 1) / 7), 1)
        E.paste(c, E.text_sprite('BLACK', F('mont800.ttf', 190), 'gold', stroke=10), W / 2, 880, pop(k + 3), fade(k + 2))
        E.paste(c, E.text_sprite('FRIDAY', F('mont800.ttf', 190), 'gold', stroke=10), W / 2, 1070, pop(k - 2), fade(k - 2))
        return
    if n == 'booked':
        E.paste(c, E.text_sprite('THANK YOU', F('mont600.ttf', 48), E.GOLD, stroke=6), W / 2, 260, pop(k - 1), fade(k - 1))
        E.paste(c, E.text_sprite('Fully booked', F('pf800.ttf', 150), 'gold', stroke=9), W / 2, 420, pop(k - 4), fade(k - 4))
        E.paste(c, E.text_sprite('this weekend', F('pf700i.ttf', 100), E.CREAM, stroke=7), W / 2, 570 + lift_(k - 10), 1, fade(k - 10, 4))
        return
    if n == 'but':
        E.paste(c, E.text_sprite('BUT…', F('mont800.ttf', 150), 'gold', stroke=10), W / 2, 700, pop(k - 1), fade(k - 1))
        E.paste(c, E.text_sprite('you can still grab', F('pf700i.ttf', 76), E.CREAM, stroke=6), W / 2, 860 + lift_(k - 8), 1, fade(k - 8, 4))
        E.paste(c, E.text_sprite('BLACK FRIDAY PRICES', F('mont800.ttf', 80), E.WHITE, stroke=9), W / 2, 990, pop(k - 14) * 0.92, fade(k - 14))
        return
    if n in ROWS:
        name, sub, p, o = ROWS[n]
        sp = E.text_sprite(name, F('mont800.ttf', 92), E.WHITE, stroke=9)
        E.paste(c, sp, W / 2, 330, pop(k - 1) * min(1, 980 / sp.width), fade(k - 1))
        E.paste(c, E.text_sprite(sub, F('pf700i.ttf', 60), E.CREAM, stroke=6), W / 2, 440 + lift_(k - 6), 1, fade(k - 6, 4))
        price(c, k - 10, p, o, 1300)
        return
    if n == 'when':
        E.paste(c, E.text_sprite('Book by', F('pf700i.ttf', 80), E.CREAM, stroke=6), W / 2, 620, pop(k - 2), fade(k - 2))
        E.paste(c, E.text_sprite('MONDAY 30.11', F('mont800.ttf', 120), 'gold', stroke=9), W / 2, 760, pop(k - 6), fade(k - 6))
        E.paste(c, E.text_sprite('enjoy it any time until', F('pf700i.ttf', 70), E.CREAM, stroke=6), W / 2, 960, pop(k - 18), fade(k - 18))
        E.paste(c, E.text_sprite('31 JANUARY', F('mont800.ttf', 120), 'gold', stroke=9), W / 2, 1090, pop(k - 22), fade(k - 22))
        return
    if n == 'cta':
        E.paste(c, E.text_sprite('SEND ME', F('mont800.ttf', 110), E.WHITE, stroke=9), W / 2, 580, pop(k - 2), fade(k - 2))
        E.paste(c, E.pill_sprite('“BF”', F('mont800.ttf', 150), padx=90, pady=34), W / 2, 800, pop(k - 8, 8), fade(k - 8), rot=-3 * (1 - E.out_cubic((k - 8) / 10)))
        E.paste(c, E.text_sprite('I reply within 1 hour', F('pf700i.ttf', 72), E.CREAM, stroke=6), W / 2, 990 + lift_(k - 16), 1, fade(k - 16, 4))
        E.paste(c, E.text_sprite('Ends Monday at midnight', F('mont600.ttf', 42), (220, 205, 185), stroke=5), W / 2, 1120, 1, fade(k - 24, 4))
        E.paste(c, E.logo, W / 2, 1330, 1, fade(k - 30, 6))
SLAMS = [0, T0['booked'], T0['but']] + [T0[n] + 10 / FPS for n in ROWS] + [T0['cta'] + 8 / FPS]
TRANS = {T0['booked']: 'flash', T0['but']: 'zoom', T0['rf']: 'flash', T0['lift']: 'whip', T0['cer']: 'whip', T0['glow']: 'whip', T0['pkg']: 'whip', T0['when']: 'zoom', T0['cta']: 'zoom'}
def render_video(path):
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    bounds = {int(round(v * FPS)): k for v, k in TRANS.items()}
    for fi in range(NF):
        t = fi / FPS
        n = max((s for s in SEGS if T0[s[0]] <= t + 1e-6), key=lambda s: T0[s[0]])[0]; dur = dict(SEGS)[n]; rel = t - T0[n]
        f = bg(n, rel, dur)
        for b, kind in bounds.items():
            d = fi - b
            if kind == 'whip' and -4 <= d < 4:
                sh = [-40, -140, -330, -620][d + 4] if d < 0 else [620, 330, 140, 40][d]
                f = E.motion_blur(np.roll(f, sh, 1), abs(sh) * .5)
            if kind == 'zoom' and -4 <= d < 5:
                if d < 0: f = cv2.GaussianBlur(E.zoom(f, 1 + .1 * (d + 5) / 4, (W / 2, H / 2)), (0, 0), 2 + 3 * (d + 5))
                else: f = E.zoom(f, 1.25 - .25 * E.out_cubic(d / 5), (W / 2, H / 2))
            if kind == 'flash' and 0 <= d < 6:
                a = (1 - d / 6) ** 1.5 * .85; f = (f.astype(np.float32) * (1 - a) + 255 * a).astype(np.uint8)
        for ts in SLAMS:
            d = t - ts
            if 0 <= d < .18:
                amp = 12 * (1 - d / .18); f = np.roll(np.roll(f, int(amp * math.sin(d * 90)), 1), int(amp * math.cos(d * 70)), 0)
        c = Image.fromarray(f).convert('RGBA')
        if n != 'cta': c.alpha_composite(TOPG); c.alpha_composite(BOTG)
        overlay(c, n, rel)
        ImageDraw.Draw(c).rectangle((0, 0, int(W * (fi + 1) / NF), 8), fill=E.GOLD + (230,))
        enc.stdin.write(np.array(c.convert('RGB')).tobytes())
    enc.stdin.close(); enc.wait()
def bells(t0, L, tr):
    for i, f0 in enumerate([2637, 3136, 3520]):
        x = E.ding(f0, .6) * .35; j = int((t0 + i * .07) * SR); x = x[:L - j]; tr[j:j + len(x)] += x
def render_audio(path):
    L = int((TOTAL + 1) * SR); tr = np.zeros(L)
    def add(x, t, g=1.0):
        i = int(max(0, t) * SR); x = x[:L - i]; tr[i:i + len(x)] += x * g
    add(E.boom(1.0), 0, .9); add(E.pop(), 3 / FPS, .45); add(E.boom(.7), 8 / FPS, .4)
    add(E.boom(.8), T0['booked'], .55); bells(T0['booked'] + .1, L, tr); add(E.pop(f0=1500), T0['booked'] + 6 / FPS, .4)
    add(E.whoosh(.5), T0['but'] - .2, .6); add(E.pop(), T0['but'] + 1 / FPS, .5); add(E.riser(.5), T0['but'] + .1, .4)
    for n in ROWS:
        add(E.whoosh(.35), T0[n] - .12, .6); add(E.pop(), T0[n] + 1 / FPS, .4); add(E.kaching(), T0[n] + 10 / FPS, .4)
    add(E.whoosh(.5), T0['when'] - .2, .6); add(E.pop(), T0['when'] + 6 / FPS, .45); add(E.pop(f0=1500), T0['when'] + 22 / FPS, .45)
    add(E.whoosh(.5), T0['cta'] - .2, .8); add(E.boom(.8), T0['cta'] + 8 / FPS, .6); add(E.ding(2093, 1.4), T0['cta'] + 16 / FPS, .45)
    mix = tr[:int(TOTAL * SR)] * 1.7; fo = int(.3 * SR); mix[-fo:] *= np.linspace(1, 0, fo)
    wavfile.write(path, SR, (np.tanh(mix * 1.2) / np.tanh(1.2) * .9).astype(np.float32))
if __name__ == '__main__':
    out = sys.argv[1]; base = out[:-4]
    render_audio(base + '.wav'); render_video(base + '_v.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', base + '_v.mp4', '-i', base + '.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    '-movflags', '+faststart', '-shortest', out], check=True)
    print('done', TOTAL)
