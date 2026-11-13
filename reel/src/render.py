import numpy as np, subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
DUR = 32.0
U = '/root/.claude/uploads/7d9c0598-0815-5ad5-8f7a-92c4389c9bd1/'
S = '/tmp/claude-0/-home-user-congenial-winner/7d9c0598-0815-5ad5-8f7a-92c4389c9bd1/scratchpad/'
F = '/usr/share/fonts/opentype/inter/'
font = lambda name, size: ImageFont.truetype(F + name, size)

def load_photo(name):
    im = Image.open(U + name).convert('RGB')
    # cover-fit at 1.25x of frame so Ken Burns has room
    sc = max(W * 1.25 / im.width, H * 1.25 / im.height)
    return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)

def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_back(x):
    x = min(max(x, 0), 1); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

class Photo:
    def __init__(s, name, zoom=(1.0, 1.12), pan=(0, 0, 0, -0.04)):
        s.im = load_photo(name); s.zoom = zoom; s.pan = pan
    def frame(s, p):
        z = s.zoom[0] + (s.zoom[1] - s.zoom[0]) * p
        k = min(s.im.width / (W * 1.25), s.im.height / (H * 1.25))
        cw, ch = W * 1.12 / z * k, H * 1.12 / z * k
        cx = s.im.width / 2 + (s.pan[0] + (s.pan[2] - s.pan[0]) * p) * s.im.width
        cy = s.im.height / 2 + (s.pan[1] + (s.pan[3] - s.pan[1]) * p) * s.im.height
        box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
        return np.asarray(s.im.resize((W, H), Image.BILINEAR, box=box), dtype=np.float32)

class Clip:
    def __init__(s, folder, f0, f1, zoom=(1.0, 1.06)):
        s.folder, s.f0, s.f1, s.zoom = folder, f0, f1, zoom
    def frame(s, p):
        i = int(s.f0 + (s.f1 - s.f0) * p)
        im = Image.open(f'{S}{s.folder}/{i:04d}.jpg')
        z = s.zoom[0] + (s.zoom[1] - s.zoom[0]) * p
        cw, ch = W / z, H / z
        box = ((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2)
        return np.asarray(im.resize((W, H), Image.BILINEAR, box=box), dtype=np.float32)

# ---------------- timeline ----------------
# (start, end, source, accent colour, kicker, title, subtitle, transition-in)
SEG = [
 (0, 4,  Clip('v1', 1, 120, (1.15, 1.0)), (255, 90, 60), None, None, None, None),
 (4, 6,  Photo('0cc2958c-image.jpg', (1.0, 1.1)), (255, 45, 45), 'RED  ·  630 nm', 'Collagen boost', 'Firms, smooths & softens fine lines', 'flash'),
 (6, 8,  Photo('4b5f7ae5-image.jpg', (1.12, 1.0)), (255, 170, 50), 'AMBER  ·  590 nm', 'Calm & soothe', 'Eases redness and sensitive skin', 'whip'),
 (8, 10, Photo('413e142a-image.jpg', (1.0, 1.12), (0.03, 0, -0.03, 0)), (70, 255, 110), 'GREEN  ·  520 nm', 'Even tone', 'Helps fade pigmentation & dark spots', 'circle'),
 (10, 12, Photo('9ab41917-image.jpg', (1.1, 1.0)), (60, 110, 255), 'BLUE  ·  415 nm', 'Clear skin', 'Targets acne-causing bacteria', 'glitch'),
 (12, 14, Photo('ea91f6cf-image.jpg', (1.0, 1.1)), (60, 230, 255), 'CYAN  ·  490 nm', 'De-puff', 'Cools, calms & reduces swelling', 'zoom'),
 (14, 16, Photo('097420db-image.jpg', (1.1, 1.0), (0, 0.02, 0, -0.02)), (240, 110, 255), 'PURPLE  ·  RED + BLUE', 'Clarify & repair', 'Double action for breakout-prone skin', 'wipe'),
 (16, 20, Clip('v2', 1, 120, (1.0, 1.08)), (120, 220, 255), None, None, None, 'flash'),
 (20, 22, Photo('944429de-image.jpg', (1.0, 1.12)), (120, 220, 255), 'OXYGEN DOME', 'Pure O₂ infusion', 'Boosts circulation & cell renewal', 'zoom'),
 (22, 24, Photo('f17a79c3-image.jpg', (1.12, 1.0)), (120, 220, 255), 'OXYGEN + LED', 'Deep hydration', 'Serums absorb deeper, skin looks plumper', 'whip'),
 (24, 26, Photo('939db691-image.jpg', (1.0, 1.12)), (255, 80, 170), 'THE RESULT', 'Radiant. Calm. Renewed.', 'That lit-from-within glow', 'circle'),
 (26, 28, Clip('v1', 121, 240, (1.0, 1.08)), (255, 120, 80), 'NON-INVASIVE', 'Zero downtime', '30 minutes of pure relaxation', 'glitch'),
 (28, 32, Clip('v2', 121, 240, (1.0, 1.1)), (255, 255, 255), None, None, None, 'wipe'),
]
TR = 0.30  # transition length (centred on the cut)

# ---------------- text layers ----------------
def text_layer(kicker, title, sub, accent):
    """Render a text card to RGBA once; animate per frame."""
    pad = 70
    img = Image.new('RGBA', (W, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    fk, ft, fs = font('Inter-Bold.otf', 34), font('InterDisplay-Black.otf', 104), font('Inter-SemiBold.otf', 44)
    y = 40
    # kicker pill
    kw = d.textlength(kicker, font=fk, ) + 8 * len(kicker) * 0  # no tracking
    d.rounded_rectangle((pad, y, pad + kw + 48, y + 64), 32, fill=accent + (255,))
    lum = 0.3 * accent[0] + 0.59 * accent[1] + 0.11 * accent[2]
    d.text((pad + 24, y + 13), kicker, font=fk, fill=(15, 15, 20) if lum > 120 else (255, 255, 255))
    y += 100
    # title, wrapped if needed
    lines = [title] if d.textlength(title, font=ft) < W - 2 * pad else wrap(title, ft, d, W - 2 * pad)
    for ln in lines:
        d.text((pad, y), ln, font=ft, fill=(255, 255, 255))
        y += 112
    y += 14
    for ln in wrap(sub, fs, d, W - 2 * pad):
        d.text((pad, y), ln, font=fs, fill=(255, 255, 255, 235))
        y += 58
    img = img.crop((0, 0, W, y + 30))
    # soft shadow for legibility
    a = img.split()[3].filter(ImageFilter.GaussianBlur(14))
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); sh.putalpha(a.point(lambda v: int(v * 0.75)))
    out = Image.alpha_composite(sh, img)
    return out

def wrap(text, f, d, maxw):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w_
    lines.append(cur); return lines

def centred(lines, y0):
    """lines: list of (text, font, rgba). Returns RGBA canvas of full frame width."""
    img = Image.new('RGBA', (W, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    y = 30
    for txt, f, col, gap in lines:
        w_ = d.textlength(txt, font=f)
        d.text(((W - w_) / 2, y), txt, font=f, fill=col); y += gap
    img = img.crop((0, 0, W, y + 30))
    a = img.split()[3].filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(26))
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); sh.putalpha(a.point(lambda v: min(255, int(v * 1.6))))
    return Image.alpha_composite(sh, img)

cards = {}
for i, s in enumerate(SEG):
    if s[4]: cards[i] = text_layer(s[4], s[5], s[6], s[3])

intro_a = centred([('LED LIGHT', font('InterDisplay-Black.otf', 150), (255, 255, 255, 255), 150),
                   ('THERAPY', font('InterDisplay-Black.otf', 150), (255, 255, 255, 255), 175),
                   ('×  OXYGEN DOME  ×', font('Inter-Bold.otf', 52), (255, 200, 170, 255), 70)], 0)
intro_b = centred([('Your skin’s glow-up,', font('InterDisplay-Bold.otf', 76), (255, 255, 255, 255), 92),
                   ('explained in light', font('InterDisplay-Bold.otf', 76), (255, 255, 255, 255), 92)], 0)
oxy_a = centred([('+ OXYGEN', font('InterDisplay-Black.otf', 140), (255, 255, 255, 255), 150),
                 ('Concentrated O₂ meets LED', font('Inter-SemiBold.otf', 52), (190, 235, 255, 255), 70)], 0)
oxy_b = centred([('Light energises your cells.', font('InterDisplay-Bold.otf', 62), (255, 255, 255, 255), 78),
                 ('Oxygen feeds them.', font('InterDisplay-Bold.otf', 62), (190, 235, 255, 255), 78)], 0)
cta_a = centred([('Treat your skin', font('InterDisplay-Black.otf', 104), (255, 255, 255, 255), 116),
                 ('to the light', font('InterDisplay-Black.otf', 104), (255, 255, 255, 255), 140),
                 ('Book your session today', font('Inter-Bold.otf', 54), (255, 255, 255, 255), 70)], 0)

def paste(frame, layer, x, y, alpha=1.0, scale=1.0):
    if alpha <= 0.01: return frame
    L = layer
    if scale != 1.0:
        L = L.resize((max(1, int(L.width * scale)), max(1, int(L.height * scale))), Image.BILINEAR)
        x += (layer.width - L.width) / 2; y += (layer.height - L.height) / 2
    arr = np.asarray(L, dtype=np.float32)
    x, y = int(x), int(y)
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + L.width), min(H, y + L.height)
    if x1 <= x0 or y1 <= y0: return frame
    sub = arr[y0 - y:y1 - y, x0 - x:x1 - x]
    a = sub[..., 3:4] / 255 * alpha
    frame[y0:y1, x0:x1] = frame[y0:y1, x0:x1] * (1 - a) + sub[..., :3] * a
    return frame

def card_anim(frame, card, lt, dur):
    """Slide-up + fade in, quick fade out at end."""
    pin = ease_out((lt - 0.12) / 0.4)
    pout = 1 - ease((lt - (dur - 0.25)) / 0.2)
    y = 1180 + (1 - pin) * 70
    return paste(frame, card, 0, y, alpha=pin * pout)

def overlay_text(frame, i, lt, dur):
    if i == 0:
        if lt < 2.0:
            p = ease_back(lt / 0.5); out = 1 - ease((lt - 1.8) / 0.2)
            frame = paste(frame, intro_a, 0, 700, alpha=min(1, lt / 0.25) * out, scale=0.75 + 0.25 * p + 0.03 * lt)
        else:
            l2 = lt - 2.0; out = 1 - ease((l2 - 1.75) / 0.2)
            frame = paste(frame, intro_b, 0, 1150 + (1 - ease_out(l2 / 0.4)) * 60, alpha=ease_out(l2 / 0.3) * out)
    elif i == 7:
        if lt < 2.0:
            p = ease_back((lt - 0.1) / 0.5); out = 1 - ease((lt - 1.8) / 0.2)
            frame = paste(frame, oxy_a, 0, 760, alpha=min(1, max(0, lt - 0.1) / 0.2) * out, scale=0.8 + 0.2 * p)
        else:
            l2 = lt - 2.0; out = 1 - ease((l2 - 1.75) / 0.2)
            frame = paste(frame, oxy_b, 0, 1180 + (1 - ease_out(l2 / 0.4)) * 60, alpha=ease_out(l2 / 0.3) * out)
    elif i == len(SEG) - 1:
        p = ease_back((lt - 0.15) / 0.6); fade = 1 - ease((lt - 3.3) / 0.6)
        frame = paste(frame, cta_a, 0, 760, alpha=min(1, max(0, lt - 0.15) / 0.3) * fade, scale=0.85 + 0.15 * p)
    elif i in cards:
        frame = card_anim(frame, cards[i], lt, dur)
    return frame

# vignette + bottom gradient for legibility
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vig = 1 - 0.45 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2)
grad = np.clip((yy - 1000) / 900, 0, 1) * 0.55
shade = (vig * (1 - grad))[..., None].astype(np.float32)

def base(i, t):
    s0, s1, src = SEG[i][0], SEG[i][1], SEG[i][2]
    p = min(max((t - s0) / (s1 - s0), 0), 1)
    return src.frame(p)

def radial_blur(img, amt):
    if amt < 0.01: return img
    acc = img.copy(); n = 4
    for k in range(1, n + 1):
        z = 1 + amt * 0.06 * k
        cw, ch = W / z, H / z
        im = Image.fromarray(img.astype(np.uint8)).resize((W, H), Image.BILINEAR, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
        acc += np.asarray(im, dtype=np.float32)
    return acc / (n + 1)

def transition(kind, A, B, p, accent):
    q = ease(p)
    if kind == 'flash':
        m = A * (1 - q) + B * q
        f = math.exp(-((p - 0.5) / 0.18) ** 2)
        col = np.array(accent, np.float32) * 0.4 + 255 * 0.6
        return m * (1 - f) + col * f
    if kind == 'whip':
        off = int(q * W)
        out = np.empty_like(A)
        out[:, :W - off] = A[:, off:]; out[:, W - off:] = B[:, :off]
        # motion blur horizontally
        k = int(60 * math.sin(math.pi * p)) + 1
        if k > 2:
            im = Image.fromarray(out.astype(np.uint8)).resize((max(1, W // k), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
            out = np.asarray(im, np.float32)
        return out
    if kind == 'circle':
        r = q * math.hypot(W, H) / 2 * 1.05
        d = np.sqrt((xx - W / 2) ** 2 + (yy - H / 2) ** 2)
        m = np.clip((r - d) / 40, 0, 1)[..., None]
        out = A * (1 - m) + B * m
        ring = np.exp(-((d - r) / 18) ** 2)[..., None] * math.sin(math.pi * p)
        return out * (1 - ring) + np.array(accent, np.float32) * ring + ring * 60
    if kind == 'glitch':
        src = A if p < 0.5 else B
        amt = int(40 * math.sin(math.pi * p))
        out = src.copy()
        out[..., 0] = np.roll(src[..., 0], amt, axis=1)
        out[..., 2] = np.roll(src[..., 2], -amt, axis=1)
        rng = np.random.default_rng(int(p * 1000))
        for _ in range(6):
            y0 = rng.integers(0, H - 80); h = rng.integers(20, 80); sh = rng.integers(-80, 80)
            out[y0:y0 + h] = np.roll(out[y0:y0 + h], sh, axis=1)
        return out
    if kind == 'zoom':
        if p < 0.5:
            img = radial_blur(A, p * 2 * 3)
            z = 1 + 0.25 * ease(p * 2)
        else:
            img = radial_blur(B, (1 - p) * 2 * 3)
            z = 1 + 0.25 * (1 - ease((p - 0.5) * 2))
        cw, ch = W / z, H / z
        im = Image.fromarray(img.astype(np.uint8)).resize((W, H), Image.BILINEAR, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
        return np.asarray(im, np.float32)
    if kind == 'wipe':
        edge = H * (1 - q * 1.1) + 0.0
        m = np.clip((yy - edge) / 60, 0, 1)[..., None]
        out = A * (1 - m) + B * m
        line = np.exp(-((yy - edge) / 10) ** 2)[..., None] * math.sin(math.pi * p)
        return out * (1 - line) + 255 * line
    return A * (1 - q) + B * q

def render_frame(t):
    i = max(k for k, s in enumerate(SEG) if s[0] <= t)
    s0 = SEG[i][0]
    frame = None
    # entering a transition into segment i+1?
    if i + 1 < len(SEG) and t > SEG[i][1] - TR / 2:
        j = i + 1
    elif i > 0 and t < s0 + TR / 2:
        j = i; i = i - 1
    else:
        j = None
    if j is not None:
        cut = SEG[j][0]
        p = (t - (cut - TR / 2)) / TR
        A = base(i, t); B = base(j, t)
        frame = transition(SEG[j][7], A, B, p, SEG[j][3])
        cur = j if t >= cut else i
    else:
        frame = base(i, t); cur = i
    frame = frame * shade
    # subtle "pulse" on the beat (120 bpm) from 4s
    if 4 <= t < 30:
        ph = (t % 0.5) / 0.5
        frame = frame * (1 + 0.05 * math.exp(-ph * 8))
    frame = overlay_text(frame, cur, t - SEG[cur][0], SEG[cur][1] - SEG[cur][0])
    # global fade in/out
    g = min(1, t / 0.4) * min(1, (DUR - t) / 0.8)
    return np.clip(frame * g, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    out = sys.argv[1]
    only = [float(x) for x in sys.argv[2:]]
    if only:
        for t in only:
            Image.fromarray(render_frame(t)).save(f'{S}preview_{t:05.2f}.jpg', quality=85)
        sys.exit()
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-i', S + 'music.wav', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
                           '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    n = int(DUR * FPS)
    for k in range(n):
        ff.stdin.write(render_frame(k / FPS).tobytes())
        if k % 60 == 0: print(k, '/', n, flush=True)
    ff.stdin.close(); ff.wait(); print('done')
