import numpy as np, sys
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100
BPM = 120
BEAT = 60 / BPM
DUR = 32.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
mix = np.zeros((N, 2))

def t_(d): return np.arange(int(SR * d)) / SR
def put(buf, start, sig, pan=0.0, gain=1.0):
    i = int(start * SR)
    if i >= N: return
    sig = sig[: N - i] * gain
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(sig), 0] += sig * l * 1.414
    buf[i:i + len(sig), 1] += sig * r * 1.414
def lp(x, fc, order=2): return sosfilt(butter(order, fc, 'low', fs=SR, output='sos'), x)
def hp(x, fc, order=2): return sosfilt(butter(order, fc, 'high', fs=SR, output='sos'), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
def midi(n): return 440 * 2 ** ((n - 69) / 12)
def saw(f, d, detune=0.0):
    t = t_(d); out = 0
    for dt in ([-detune, 0, detune] if detune else [0]):
        ph = (f * (1 + dt) * t + rng.random()) % 1
        out = out + (2 * ph - 1)
    return out / (3 if detune else 1)

# ---- drums
def kick():
    t = t_(0.45)
    f = 50 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7)
    s[:200] += rng.normal(0, 0.3, 200) * np.linspace(1, 0, 200)
    return np.tanh(s * 1.6)
def clap():
    t = t_(0.3); n = rng.normal(0, 1, len(t))
    env = np.exp(-t * 18)
    for o in (0.0, 0.011, 0.022):
        i = int(o * SR); env[i:i + 300] += 0.6 * np.exp(-np.arange(300) / 60)
    return bp(n, 900, 5000) * env
def hat(open_=False):
    t = t_(0.25 if open_ else 0.06); n = rng.normal(0, 1, len(t))
    return hp(n, 8000) * np.exp(-t * (12 if open_ else 70))

# ---- arrangement sections
drums_on = lambda b: (4 <= b * BEAT < 16) or (20 <= b * BEAT < 30.5)
half = lambda b: 16 <= b * BEAT < 20

K, C, H, HO = kick(), clap(), hat(), hat(True)
kick_times = []
for b in range(int(DUR / BEAT)):
    tb = b * BEAT
    if drums_on(b):
        put(mix, tb, K, gain=0.9); kick_times.append(tb)
        if b % 2 == 1: put(mix, tb, C, gain=0.45, pan=0.05)
        put(mix, tb + BEAT / 2, HO, gain=0.18, pan=0.25)
        for s in (0, 0.25, 0.75):
            put(mix, tb + s * BEAT, H, gain=0.12, pan=-0.3)
    elif half(b):
        if b % 2 == 1: put(mix, tb, C, gain=0.3)
        put(mix, tb + BEAT / 2, H, gain=0.12, pan=0.3)

# ---- harmony: Am F C G  (one chord per bar)
prog = [(57, [57, 60, 64, 67]), (53, [53, 57, 60, 64]), (48, [55, 60, 64, 67]), (55, [55, 59, 62, 67])]
BAR = 4 * BEAT
music = np.zeros((N, 2))
for bar in range(int(DUR / BAR)):
    t0 = bar * BAR
    root, chord = prog[bar % 4]
    # pad
    pad = sum(saw(midi(n), BAR, 0.006) for n in chord) / 4
    cutoff = 900 if t0 < 4 else (2500 if not (16 <= t0 < 20) else 1200)
    pad = lp(pad, cutoff) * np.minimum(1, t_(BAR) / 0.05) * np.minimum(1, (BAR - t_(BAR)) / 0.05)
    put(music, t0, pad, pan=-0.2, gain=0.22)
    put(music, t0, pad, pan=0.2, gain=0.22)
    # bass offbeat (from 4s)
    if t0 >= 4 and not (16 <= t0 < 18) and t0 < 30:
        for b in range(4):
            d = BEAT * 0.45
            s = lp(saw(midi(root - 12), d), 600) * np.exp(-t_(d) * 4)
            s += np.sin(2 * np.pi * midi(root - 24) * t_(d)) * 0.6 * np.exp(-t_(d) * 3)
            put(music, t0 + b * BEAT + BEAT / 2, np.tanh(s * 1.5), gain=0.35)
    # pluck arpeggio 16ths (from 8s)
    if (8 <= t0 < 16) or (20 <= t0 < 30):
        pattern = [0, 2, 1, 3, 2, 1, 3, 2, 0, 2, 1, 3, 2, 3, 1, 2]
        for i, p in enumerate(pattern):
            n = chord[p] + 12
            d = 0.2
            s = lp(saw(midi(n), d), 3500) * np.exp(-t_(d) * 22)
            put(music, t0 + i * BEAT / 4, s, pan=(0.5 if i % 2 else -0.5), gain=0.16)
            # echo
            put(music, t0 + i * BEAT / 4 + BEAT * 0.75, s, pan=(-0.5 if i % 2 else 0.5), gain=0.06)
    # bell lead at oxygen section & finale
    if 16 <= t0 < 20 or 24 <= t0 < 30:
        melody = [(0, 76), (1.5, 74), (2, 72), (3, 71)]
        for st, n in melody:
            d = 1.2
            tt = t_(d)
            s = (np.sin(2 * np.pi * midi(n) * tt) + 0.3 * np.sin(2 * np.pi * midi(n) * 2.01 * tt)) * np.exp(-tt * 3)
            put(music, t0 + st * BEAT, s, gain=0.12, pan=0.1)

# sidechain pump on music
env = np.ones(N)
for kt in kick_times:
    i = int(kt * SR); L = int(0.35 * SR)
    seg = env[i:i + L]
    seg *= 0.35 + 0.65 * (1 - np.exp(-np.arange(len(seg)) / (0.08 * SR)))
music *= env[:, None]
mix += music

# risers / impacts
def riser(d):
    t = t_(d); n = rng.normal(0, 1, len(t))
    out = np.zeros(len(t)); chunks = 40
    for k in range(chunks):
        a, b_ = k * len(t) // chunks, (k + 1) * len(t) // chunks
        fc = 400 + 9000 * (k / chunks) ** 2
        out[a:b_] = bp(n, fc, min(fc * 1.6, 20000))[a:b_]
    return out * (t / d) ** 2
def impact():
    t = t_(1.5)
    return np.sin(2 * np.pi * 45 * t) * np.exp(-t * 3) + lp(rng.normal(0, 1, len(t)), 3000) * np.exp(-t * 6) * 0.5
put(mix, 2.0, riser(2.0), gain=0.25)
put(mix, 18.0, riser(2.0), gain=0.25)
for tt in (4.0, 20.0):
    put(mix, tt, impact(), gain=0.5)
# whooshes on every other bar transition
def whoosh():
    t = t_(0.4); n = rng.normal(0, 1, len(t))
    return bp(n, 1500, 6000) * np.sin(np.pi * t / 0.4) ** 2
for tt in np.arange(6.0, 30.0, 2.0):
    if tt not in (20.0,):
        put(mix, tt - 0.2, whoosh(), gain=0.08, pan=rng.uniform(-0.6, 0.6))

# master: fades, soft clip, normalise
fade_in = np.minimum(1, np.arange(N) / (0.8 * SR))
fade_out = np.clip((DUR - np.arange(N) / SR) / 2.0, 0, 1)
mix *= (fade_in * fade_out)[:, None]
mix = np.tanh(mix * 1.2)
mix /= np.abs(mix).max() / 0.89
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16))
print('ok')
