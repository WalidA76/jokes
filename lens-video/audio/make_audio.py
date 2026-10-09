"""Procedural sound design + music for 'The World of Camera Lenses' (no samples, everything synthesised with numpy).
Reads ../src/timeline.js so SFX stay locked to the picture.  Output: out/{music,sfx,mix}.wav (44.1k stereo)."""
import json, re, wave, sys, os
import numpy as np

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.loads(re.sub(r'^window\.TIMELINE\s*=\s*|;\s*$', '', open(os.path.join(HERE, '../src/timeline.js')).read().strip()))
DUR = TL['duration']
N = int((DUR + 1.0) * SR)
rng = np.random.default_rng(7)

# ───────────── DSP helpers ─────────────
def tt(d): return np.arange(int(d * SR)) / SR
def env_ad(n, a, d):          # attack / exponential decay
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(d, 1e-4))
    return e
def fftfilt(x, lo=None, hi=None, order=4):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR) + 1e-9
    g = np.ones_like(f)
    if hi: g *= 1 / (1 + (f / hi) ** order)
    if lo: g *= 1 / (1 + (lo / f) ** order)
    return np.fft.irfft(X * g, len(x))
def noise(d): return rng.standard_normal(int(d * SR))
def norm(x, peak=1.0): m = np.max(np.abs(x)) or 1; return x / m * peak
def sine(f, d, ph=0): return np.sin(2 * np.pi * f * tt(d) + ph)
def sweep(f0, f1, d, expo=True):
    t = tt(d); k = (f1 / f0) ** (t / d) if expo else None
    ph = 2 * np.pi * f0 * d / np.log(f1 / f0) * (k - 1)
    return np.sin(ph)

class Bus:
    def __init__(self): self.L = np.zeros(N); self.R = np.zeros(N)
    def add(self, sig, t, gain=1.0, pan=0.0):
        i = int(t * SR); 
        if i >= N or i + len(sig) <= 0: return
        a = max(0, -i); sig = sig[a:]; i = max(0, i); sig = sig[: N - i]
        l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
        self.L[i:i + len(sig)] += sig * gain * l * 1.414; self.R[i:i + len(sig)] += sig * gain * r * 1.414

# ───────────── SFX ─────────────
def shutter(vol=1.0, rate=1.0):
    d = 0.22; n = int(d * SR); out = np.zeros(n)
    t = np.arange(n) / SR
    # mirror slap: low thump + woody noise
    thump = np.sin(2 * np.pi * (170 * np.exp(-t * 28) + 55) * t) * np.exp(-t / 0.028)
    slap = fftfilt(noise(d), 600, 3200) * np.exp(-t / 0.014)
    out += 0.9 * thump + 0.55 * slap
    # first curtain / second curtain
    for off, g, lo, hi in [(0.052, 0.8, 1800, 7500), (0.092, 0.55, 1200, 5200)]:
        i = int(off * SR / rate); m = int(0.016 * SR)
        if i + m < n: out[i:i + m] += g * fftfilt(noise(0.016), lo, hi)[:m] * np.exp(-np.arange(m) / SR / 0.0045)
    # small metallic ping
    out += 0.06 * np.sin(2 * np.pi * 3100 * t) * np.exp(-t / 0.02)
    return norm(out, 0.9 * vol)
def aperture_tick(vol=1.0):
    d = 0.05; t = tt(d)
    return norm(fftfilt(noise(d), 2500, 9000) * np.exp(-t / 0.004) + 0.5 * np.sin(2 * np.pi * 3300 * t) * np.exp(-t / 0.012), 0.5 * vol)
def ui_pop(f=880, vol=1.0):
    d = 0.14; t = tt(d); f_t = f * (1 + 0.9 * (1 - np.exp(-t / 0.012)))
    ph = 2 * np.pi * np.cumsum(f_t) / SR
    return norm(np.sin(ph) * np.exp(-t / 0.035) * np.minimum(1, t / 0.002), 0.45 * vol)
def beep(f=2400, d=0.09, vol=1.0):
    t = tt(d); e = np.minimum(1, t / 0.004) * np.minimum(1, (d - t) / 0.01)
    return 0.4 * vol * (np.sin(2 * np.pi * f * t) + 0.15 * np.sin(2 * np.pi * 2 * f * t)) * e
def whoosh(d=0.8, up=True, vol=1.0, bright=1.0):
    n = int(d * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    centers = [200, 500, 1100, 2400, 5000, 9000]
    out = np.zeros(n)
    for k, c in enumerate(centers):
        b = fftfilt(x, c / 1.5, c * 1.5, 2)
        pos = (k / (len(centers) - 1))
        peak = (0.25 + 0.5 * pos) if up else (0.75 - 0.5 * pos)          # when this band is loudest
        out += b * np.exp(-((t / d - peak) ** 2) / (2 * 0.12 ** 2)) * (1 if k < 4 else bright)
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5
    return norm(out * env, 0.7 * vol)
def impact(vol=1.0, d=1.4):
    t = tt(d); f = 38 + 60 * np.exp(-t / 0.12)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.45)
    crack = fftfilt(noise(d), 80, 2500) * np.exp(-t / 0.05)
    tail = fftfilt(noise(d), 200, 3000) * np.exp(-t / 0.6) * 0.12
    return norm(body + 0.35 * crack + tail, 0.85 * vol)
def focus_motor(d=1.0, vol=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    f = 150 + 70 * np.sin(2 * np.pi * 2.2 * t) + 160 * np.minimum(1, t / 0.12)
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = sum(np.sin(h * ph) / h for h in range(1, 12))
    am = 0.65 + 0.35 * np.sign(np.sin(2 * np.pi * 46 * t))
    x = fftfilt(saw * am + 0.25 * noise(d), 300, 4200)
    env = np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.06)
    return norm(x * env, 0.35 * vol)
def ring_rotate(d=1.5, vol=1.0, rate=24):
    n = int(d * SR); t = np.arange(n) / SR
    g = fftfilt(rng.standard_normal(n), 700, 3800)
    ribs = 0.45 + 0.55 * (np.sin(2 * np.pi * rate * t) > 0.2)
    slow = 0.75 + 0.25 * np.sin(2 * np.pi * 3 * t)
    env = np.minimum(1, t / 0.08) * np.minimum(1, (d - t) / 0.12)
    low = fftfilt(rng.standard_normal(n), 80, 400) * 0.5
    return norm((g * ribs + low) * slow * env, 0.4 * vol)

sfx = Bus()
def S(id_): return next(s for s in TL['scenes'] if s['id'] == id_)
CM = TL['common']

# intro
t0 = 0
for i, tc in enumerate(np.linspace(0.15, 1.35, 14) ** 1.0): sfx.add(aperture_tick(0.9), tc, 0.9, pan=rng.uniform(-.3, .3))
sfx.add(focus_motor(1.1, 0.8), 0.15, 0.55)
for i in range(7): sfx.add(ui_pop(600 * (1.0595 ** (i * 2)), 0.9), 0.75 + 0.34 * i, 0.8, pan=(i - 3) / 6)
sfx.add(focus_motor(0.4, 0.8), 3.0, 0.5)
sfx.add(shutter(), 3.5, 1.0); sfx.add(impact(1.0), 3.5, 0.9)
sfx.add(whoosh(0.8, True), 3.35, 0.5)
for tt_ in (3.7, 4.1, 4.9): sfx.add(ui_pop(1000, .8), tt_, 0.6)

cats = ['fisheye', 'ultrawide', 'wide', 'portrait', 'macro', 'tele', 'super']
for si, sc in enumerate(TL['scenes']):
    s0 = sc['start']; id_ = sc['id']
    if si > 0: sfx.add(whoosh(0.8, True, 1.0), s0 - 0.28, 0.75, pan=-.2); 
    if si > 0 and id_ != 'outro': sfx.add(impact(0.6, 0.9), s0 + 0.02, 0.35)
    if id_ in cats:
        for i in range(3): sfx.add(ui_pop(780 + 140 * i, 0.9), s0 + CM['lensIn'] + CM['lensStagger'] * i + .1, 0.7, pan=(i - 1) * .5)
        sfx.add(whoosh(0.55, True, 0.8), s0 + CM['select'] - 0.05, 0.6); sfx.add(focus_motor(0.45, 0.7), s0 + CM['select'], 0.55)
        sfx.add(impact(0.6, 0.8), s0 + CM['select'] + 0.7, 0.45)
        sfx.add(ui_pop(520, 1), s0 + CM['cardIn'] + 0.05, 0.7); sfx.add(whoosh(0.5, False, 0.6), s0 + CM['cardIn'] - 0.05, 0.4)
        # info text pops
        for key in ('bullets', 'chips'):
            for tb in sc.get(key, []): sfx.add(ui_pop(1100, .8), s0 + tb + 0.05, 0.5)
        if 'quote' in sc: sfx.add(ui_pop(1200, .9), s0 + sc['quote'] + 0.05, 0.55)
    f0, f1 = (sc.get('fx') or [0, 0])
    if id_ == 'fisheye':
        sfx.add(whoosh(f1 - f0, True, 1.0, 0.6), s0 + f0, 0.55)       # lens-warp swell
        sfx.add(ring_rotate(f1 - f0, .7, 14), s0 + f0, 0.35)
    if id_ == 'ultrawide':
        sfx.add(whoosh(f1 - f0 - 0.4, True, 0.9, 0.8), s0 + f0, 0.5)
        for k in range(6): sfx.add(ui_pop(900 + 90 * k, .5), s0 + f0 + 0.3 + k * 0.5, 0.25)
    if id_ == 'wide':
        for tb in sc['segs'][:3]: sfx.add(ui_pop(1400, .8), s0 + tb, 0.6); sfx.add(aperture_tick(1.0), s0 + tb + 0.03, 0.9)
        sfx.add(ring_rotate(1.2, .6, 20), s0 + sc['segs'][1] - 0.2, 0.25)
    if id_ == 'portrait':
        sfx.add(focus_motor(1.8, .9), s0 + f0 + 0.3, 0.5)
        for k in range(5): sfx.add(aperture_tick(1.0), s0 + f0 + 0.4 + k * 0.4, 0.9)
        sfx.add(shutter(0.9), s0 + 6.1, 0.8); 
    if id_ == 'macro':
        sfx.add(focus_motor(3.2, .9), s0 + f0, 0.45); sfx.add(ring_rotate(3.0, .8, 28), s0 + f0 + 0.2, 0.5)
        sfx.add(beep(2400, 0.08), s0 + 6.65, 0.4); sfx.add(impact(0.6, 0.9), s0 + sc['badge'], 0.5)
    if id_ == 'tele':
        sfx.add(ring_rotate(f1 - f0, 1.0, 22), s0 + f0, 0.75); sfx.add(whoosh(f1 - f0, True, .6), s0 + f0, 0.3)
    if id_ == 'super':
        sfx.add(ring_rotate(f1 - f0, 1.0, 22), s0 + f0, 0.6); sfx.add(focus_motor(1.0, .9), s0 + sc['af'][0] - 0.3, 0.5)
        for k, tb in enumerate((0.0, 0.14)): sfx.add(beep(2300, 0.085), s0 + sc['af'][1] - 0.05 + tb, 0.8)
        b0, b1 = sc['burst']
        for k, tb in enumerate(np.arange(b0, b1, 0.1)): sfx.add(shutter(0.7 + .3 * rng.random(), 1.0), s0 + tb, 0.75, pan=rng.uniform(-.2, .2))
    if id_ == 'guide':
        for i in range(7): sfx.add(ui_pop(700 + 60 * i, 1), s0 + 0.8 + 0.6015 * i, 0.55, pan=0.2)
        sfx.add(ui_pop(1300, 1), s0 + 5.2, 0.5); sfx.add(ui_pop(1500, 1), s0 + 5.6, 0.5)
    if id_ == 'outro':
        sfx.add(whoosh(1.6, True, 1.0, 1.0), s0 - 0.05, 1.0, pan=-.3); sfx.add(impact(0.9, 1.6), s0 + 1.55, 0.7)
        sfx.add(ui_pop(900, 1), s0 + 1.65, 0.6); sfx.add(ui_pop(1100, 1), s0 + 2.4, 0.6)
        sfx.add(shutter(1.0), s0 + 3.0, 0.9); sfx.add(beep(2600, 0.07), s0 + 3.2, 0.25)

# ───────────── Music ─────────────
mus = Bus()
BPM = 120; beat = 60 / BPM
def pad_note(f, d, vol=1.0, det=0.004):
    n = int(d * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for dd in (-det, 0, det):
        ph = 2 * np.pi * f * (1 + dd) * t
        x += sum(np.sin(h * ph + dd * 9 * h) / h ** 1.3 for h in range(1, 9))
    e = np.minimum(1, t / 1.1) * np.minimum(1, (d - t) / 1.4)
    return x * e * vol / 3
def pluck(f, vol=1.0, d=0.35):
    t = tt(d); x = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.08) + 0.25 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.05)
    return x * np.exp(-t / 0.12) * np.minimum(1, t / 0.002) * vol
def kick(vol=1.0):
    d = 0.35; t = tt(d); f = 48 + 110 * np.exp(-t / 0.035)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16) + 0.25 * fftfilt(noise(d), 1500, 6000) * np.exp(-t / 0.004)
    return x * vol
def hat(vol=1.0, open_=False):
    d = 0.18 if open_ else 0.05; t = tt(d); return fftfilt(noise(d), 7000, None, 2) * np.exp(-t / (0.06 if open_ else 0.012)) * vol * .6
def clap(vol=1.0):
    d = 0.3; t = tt(d); x = np.zeros(len(t))
    for o in (0, 0.012, 0.024): 
        i = int(o * SR); m = fftfilt(noise(d), 900, 4500)[: len(t) - i] * np.exp(-t[: len(t) - i] / 0.012); x[i:] += m
    x += 0.5 * fftfilt(noise(d), 800, 3500) * np.exp(-t / 0.09)
    return x * vol * 0.5
def bass(f, d=0.24, vol=1.0):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t)) * np.minimum(1, t / 0.004) * np.minimum(1, (d - t) / 0.03) * vol

chords = [  # Am F C G  (pad voicings), roots
    ([220.0, 261.63, 329.63, 440.0], 55.0, [220.0, 261.63, 329.63, 392.0]),
    ([174.61, 220.0, 261.63, 349.23], 43.65, [220.0, 261.63, 349.23, 440.0]),
    ([196.0, 261.63, 329.63, 392.0], 65.41, [261.63, 329.63, 392.0, 523.25]),
    ([196.0, 246.94, 293.66, 392.0], 49.0, [246.94, 293.66, 392.0, 493.88]),
]
def level(t):   # global energy 0..1 following the story: wide → long
    knots = [(0, .15), (3.4, .2), (6, .45), (15, .55), (24, .65), (34, .75), (44, .78), (53, .85), (63, 1.0), (73, .6), (81, .9), (85, .5)]
    xs, ys = zip(*knots); return float(np.interp(t, xs, ys))
sidechain = np.ones(N)
def duck(t0, depth=.55):
    i = int(t0 * SR); m = int(0.28 * SR); tt_ = np.arange(m) / SR
    if i < N: g = 1 - depth * np.exp(-tt_ / 0.1); sidechain[i:i + m] = np.minimum(sidechain[i:i + m], g[: N - i])
pad_bus = Bus(); bass_bus = Bus(); drum_bus = Bus(); lead_bus = Bus()
t = 0.0; ci = 0
while t < DUR + 0.5:
    ch = chords[ci % 4]; d = 4.0
    for f in ch[0]: pad_bus.add(pad_note(f, d + 1.2, 0.55 * (0.5 + level(t))), t - 0.2, 1.0, pan=rng.uniform(-.5, .5))
    t += d; ci += 1
# drums + bass + arp
tb = 0.0; step = 0
while tb < DUR:
    lv = level(tb); bar = int(tb // (4 * beat)); ch = chords[(bar // 2) % 4]
    pos = step % 16                                    # 16th grid
    t16 = tb
    drums_on = 6 <= tb < 73 or 81 <= tb < 84.2
    if tb < 6 and pos % 8 == 0 and tb > 2.0: bass_bus.add(bass(ch[1] * 2, 0.5, 0.5), tb, 0.5)
    if drums_on:
        if pos % 4 == 0:
            drum_bus.add(kick(0.9 if lv > .5 else .65), tb, 1.0); duck(tb)
        if tb >= 15 and pos % 4 == 2: drum_bus.add(hat(0.55 + .35 * lv, open_=(pos == 14)), tb, 0.7, pan=.3)
        if tb >= 53 and pos % 4 in (1, 3): drum_bus.add(hat(0.35), tb, 0.5, pan=-.3)
        if tb >= 34 and pos in (4, 12): drum_bus.add(clap(0.9), tb, 0.8)
        if tb >= 61 and tb < 63 and pos % 2 == 0: drum_bus.add(clap(0.5 + 0.3 * (tb - 61)), tb, 0.6)   # build roll
        if tb >= 6 and pos % 2 == 0 and pos not in (0, 4, 8, 12): bass_bus.add(bass(ch[1], 0.22, 0.9 * min(1, lv + .3)), tb, 0.8)
        if tb >= 6 and pos in (0, 4, 8, 12): bass_bus.add(bass(ch[1], 0.3, 1.0), tb + 0.0, 0.9)
    arp_on = (24 <= tb < 73) or (73 <= tb < 81)
    if arp_on and (pos % 2 == 0 or tb >= 53):
        notes = ch[2]; f = notes[(step * 3) % 4] * (2 if (step // 4) % 4 == 3 else 1)
        vol = (0.25 + .25 * lv) * (0.7 if tb < 34 else 1.0) * (0.8 if 73 <= tb < 81 else 1.0)
        lead_bus.add(pluck(f, vol), tb, 1.0, pan=np.sin(step * 0.9) * .5)
    step += 1; tb += beat / 4
# final hits
for tc in (81.0,): 
    for f in chords[0][0]: pad_bus.add(pad_note(f * 0.5, 4.5, 0.9), tc, 1.0)
    drum_bus.add(kick(1.0), tc, 1.0)
# combine music with sidechain on pad+bass
pad_bus.L *= sidechain; pad_bus.R *= sidechain; bass_bus.L *= (0.5 + 0.5 * sidechain); bass_bus.R *= (0.5 + 0.5 * sidechain)
for b, g in ((pad_bus, 0.55), (bass_bus, 0.5), (drum_bus, 0.6), (lead_bus, 0.5)):
    mus.L += b.L * g; mus.R += b.R * g
# intro/outro filter swell: simple gain envelopes
tgrid = np.arange(N) / SR
mg = np.clip(tgrid / 2.5, 0, 1) * np.where(tgrid > DUR - 1.8, np.clip((DUR + 0.2 - tgrid) / 2.0, 0, 1), 1)
mus.L *= mg; mus.R *= mg

def soft(x): return np.tanh(x * 1.1) / np.tanh(1.1)
def write(path, L, R):
    y = np.stack([L, R], 1); y = np.clip(y, -1, 1); pcm = (y * 32767).astype('<i2')
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
# loudness balance: music ~ -16 dBFS rms-ish, sfx lead
mp = max(np.max(np.abs(mus.L)), np.max(np.abs(mus.R))); mus.L *= 0.42 / mp; mus.R *= 0.42 / mp
sp = max(np.max(np.abs(sfx.L)), np.max(np.abs(sfx.R))); sfx.L *= 0.8 / sp; sfx.R *= 0.8 / sp
fade = np.clip((DUR - tgrid) / 0.8, 0, 1)
mixL = soft((mus.L + sfx.L) * fade * 1.0); mixR = soft((mus.R + sfx.R) * fade * 1.0)
n = int(DUR * SR)
write(os.path.join(out, 'music.wav'), (mus.L * fade)[:n], (mus.R * fade)[:n])
write(os.path.join(out, 'sfx.wav'), (sfx.L * fade)[:n], (sfx.R * fade)[:n])
write(os.path.join(out, 'mix.wav'), (mixL * 0.92)[:n], (mixR * 0.92)[:n])
print('audio ok', n / SR, 's')
