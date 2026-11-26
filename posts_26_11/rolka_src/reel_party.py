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
B = {'hook': cover(load('salon.jpg'), .35, .5), 'rf': cover(load('rf_photo.jpg'), .5, .45), 'lift': cover(load('k2.jpg'), .5, .55),
     'glow': cover(load('glow_a.jpg'), .5, .4)}
SEGS = [('hook', 2.8), ('rf', 3.4), ('lift', 3.4), ('glow', 3.6), ('pkg', 2.8), ('cta', 3.0)]
T0 = {}; t = 0
for n, d in SEGS: T0[n] = t; t += d
TOTAL = t; NF = int(round(TOTAL * FPS))
TOPG = E.vgrad(True, 0, 760, 0.85, 0.0); BOTG = E.vgrad(False, 1050, 1650, 0.0, 0.85)
ROWS = {'rf': ('PARTY IN 4+ WEEKS?', 'RF MICRONEEDLING', 'results peak in 4–6 weeks', '£110', '£180'),
        'lift': ('PARTY NEXT WEEK?', 'ELASTISTROM & RF', 'instant lift · no needles', '£130', '£210'),
        'glow': ('PARTY THIS WEEKEND?', 'HYDROGEN PURE GLOW', 'instant glow · zero downtime', '£55', '£75')}
def pop(k, d=7): return 0.3 + 0.7 * E.out_back(k / d)
def fade(k, d=3): return E.clamp(k / d)
def lift_(k, d=6): return (1 - E.out_cubic(k / d)) * 26
def bg(n, rel, dur):
    p = rel / dur
    if n == 'hook': return dark(kb(B['hook'], p, 1.0, 1.12), .42)
    if n in ROWS: return kb(B[n], p, 1.0, 1.08, 0, -40)
    if n == 'pkg': return dark(cv2.GaussianBlur(kb(B['glow'], p, 1.05, 1.1), (0, 0), 16), .38)
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
        E.paste(c, E.pill_sprite('BLACK FRIDAY · 4 DAYS LEFT', F('mont800.ttf', 36)), W / 2, 420, pop(k - 14), fade(k - 14))
        E.paste(c, E.text_sprite('CHRISTMAS', F('mont800.ttf', 140), 'gold', stroke=10), W / 2, 700, 0.55 + 0.45 * E.out_back((k + 1) / 7), 1)
        E.paste(c, E.text_sprite('PARTY?', F('mont800.ttf', 160), E.WHITE, stroke=10), W / 2, 870, pop(k + 4), fade(k + 3))
        E.paste(c, E.text_sprite('here’s what to book & when 🎄'.replace(' 🎄', ''), F('pf700i.ttf', 66), E.CREAM, stroke=6), W / 2, 1040 + lift_(k - 12), 1, fade(k - 12, 4))
        return
    if n in ROWS:
        q, name, sub, p, o = ROWS[n]
        E.paste(c, E.pill_sprite(q, F('mont800.ttf', 40), padx=44, pady=20), W / 2, 300, pop(k - 1), fade(k - 1))
        sp = E.text_sprite(name, F('mont800.ttf', 92), E.WHITE, stroke=9)
        E.paste(c, sp, W / 2, 440, pop(k - 8) * min(1, 980 / sp.width), fade(k - 8))
        E.paste(c, E.text_sprite(sub, F('pf700i.ttf', 60), E.CREAM, stroke=6), W / 2, 545 + lift_(k - 14), 1, fade(k - 14, 4))
        price(c, k - 22, p, o, 1300)
        return
    if n == 'pkg':
        E.paste(c, E.pill_sprite('BEST OF BOTH 🎄'.replace(' 🎄', ''), F('mont800.ttf', 38)), W / 2, 470, pop(k - 1), fade(k - 1))
        E.paste(c, E.text_sprite('GLOW BEFORE', F('mont800.ttf', 100), 'gold', stroke=9), W / 2, 640, pop(k - 4), fade(k - 4))
        E.paste(c, E.text_sprite('CHRISTMAS', F('mont800.ttf', 100), 'gold', stroke=9), W / 2, 750, pop(k - 7), fade(k - 7))
        E.paste(c, E.text_sprite('Hydrogen Pure Glow + PorCerAmid', F('mont600.ttf', 46), E.CREAM, stroke=6), W / 2, 880 + lift_(k - 12), 1, fade(k - 12, 4))
        price(c, k - 18, '£75', '£160', 1080)
        return
    if n == 'cta':
        E.paste(c, E.text_sprite('SEND ME', F('mont800.ttf', 110), E.WHITE, stroke=9), W / 2, 560, pop(k - 2), fade(k - 2))
        E.paste(c, E.pill_sprite('“PARTY”', F('mont800.ttf', 140), padx=80, pady=32), W / 2, 780, pop(k - 8, 8), fade(k - 8), rot=-3 * (1 - E.out_cubic((k - 8) / 10)))
        E.paste(c, E.text_sprite('and your party date', F('pf700i.ttf', 70), E.CREAM, stroke=6), W / 2, 960 + lift_(k - 16), 1, fade(k - 16, 4))
        E.paste(c, E.text_sprite('I’ll plan your glow 🤍'.replace(' 🤍', ''), F('pf700i.ttf', 70), E.CREAM, stroke=6), W / 2, 1050 + lift_(k - 20), 1, fade(k - 20, 4))
        E.paste(c, E.text_sprite('Black Friday ends Monday 30.11', F('mont600.ttf', 40), (220, 205, 185), stroke=5), W / 2, 1190, 1, fade(k - 26, 4))
        E.paste(c, E.logo, W / 2, 1380, 1, fade(k - 30, 6))
SLAMS = [0, T0['rf'] + 22 / FPS, T0['lift'] + 22 / FPS, T0['glow'] + 22 / FPS, T0['pkg'] + 18 / FPS, T0['cta'] + 8 / FPS]
TRANS = {T0['rf']: 'flash', T0['lift']: 'whip', T0['glow']: 'whip', T0['pkg']: 'zoom', T0['cta']: 'zoom'}
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
    add(E.boom(1.0), 0, .85); bells(0.15, L, tr); add(E.pop(), 5 / FPS, .45); add(E.pop(f0=1500), 14 / FPS, .4)
    for n in ('rf', 'lift', 'glow'):
        add(E.whoosh(.4), T0[n] - .15, .7); add(E.pop(), T0[n] + 1 / FPS, .45); add(E.pop(f0=1500), T0[n] + 8 / FPS, .4)
        add(E.kaching(), T0[n] + 22 / FPS, .45)
    add(E.whoosh(.5), T0['pkg'] - .2, .6); bells(T0['pkg'] + .1, L, tr); add(E.kaching(), T0['pkg'] + 18 / FPS, .45)
    add(E.whoosh(.5), T0['cta'] - .2, .8); add(E.boom(.8), T0['cta'] + 8 / FPS, .6); add(E.ding(2093, 1.4), T0['cta'] + 16 / FPS, .45)
    mix = tr[:int(TOTAL * SR)] * 1.7; fo = int(.3 * SR); mix[-fo:] *= np.linspace(1, 0, fo)
    wavfile.write(path, SR, (np.tanh(mix * 1.2) / np.tanh(1.2) * .9).astype(np.float32))
if __name__ == '__main__':
    out = sys.argv[1]; base = out[:-4]
    render_audio(base + '.wav'); render_video(base + '_v.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', base + '_v.mp4', '-i', base + '.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    '-movflags', '+faststart', '-shortest', out], check=True)
    print('done', TOTAL)
