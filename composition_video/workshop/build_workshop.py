#!/usr/bin/env python3
"""Workshop graphics — 16:9 (1920x1080, 30 fps), one clip per محور + closing clips.

  python3 build_workshop.py --preview m1 [t ...]     # stills -> workshop/preview/
  python3 build_workshop.py m1 m2 ...                # render clips (default: all) -> workshop/out/*.mp4
Clips: m1 exposure triangle, m2 composition, m3 light, m4 quick edit, m5 golden rules, m6 graduation project.
"""
import math, os, sys, subprocess
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
W, H, FPS = 1920, 1080, 30
COPPER, TEAL, WHITE, GREY, RED, GREEN, BLUE = (232, 135, 58), (47, 168, 184), (255, 255, 255), (170, 170, 176), (232, 40, 52), (64, 224, 110), (70, 150, 255)
FB = f'{ROOT}/assets/fonts/Tajawal-Bold.ttf'
FR = f'{ROOT}/assets/fonts/Tajawal-Medium.ttf'
_fc = {}
def font(p, s):
    k = (p, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s * 1.14))
    return _fc[k]
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(p):
    p = clamp(p); return 4 * p ** 3 if p < .5 else 1 - (-2 * p + 2) ** 3 / 2
def rv(t, t0, d=.5): return ease((t - t0) / d)
def lerp(a, b, p): return a + (b - a) * p
def has_ar(s): return any('؀' <= ch <= 'ۿ' for ch in s)

def load(n): return Image.open(f'{ROOT}/assets/{n}').convert('RGB')
IMG = {}
def img(n):
    if n not in IMG: IMG[n] = load(n)
    return IMG[n]

def cover(im, w, h, cx=.5, cy=.5, zoom=1.0):
    s = max(w / im.width, h / im.height) * zoom
    cw, ch = w / s, h / s
    x = clamp(cx * im.width - cw / 2, 0, im.width - cw); y = clamp(cy * im.height - ch / 2, 0, im.height - ch)
    return im.resize((w, h), Image.BICUBIC, box=(x, y, x + cw, y + ch)), (x, y, cw, ch)

# ------------------------------------------------------------------ canvas
_bg = None
def bg():
    global _bg
    if _bg is None:
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.sqrt(((xx - W * .5) / (W * .75)) ** 2 + ((yy - H * .45) / (H * .8)) ** 2)
        v = (30 - 20 * np.clip(d, 0, 1)).astype(np.float32)
        _bg = Image.fromarray(np.stack([v, v, v + 2], -1).clip(8, 34).astype(np.uint8))
    return _bg.copy()

class F:
    def __init__(s, T):
        s.T = T; s.im = bg(); s.d = ImageDraw.Draw(s.im, 'RGBA')
    def refresh(s): s.d = ImageDraw.Draw(s.im, 'RGBA')
    def paste(s, im, x, y, r=0, a=1.0):
        m = Image.new('L', im.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=int(255 * a))
        s.im.paste(im, (int(x), int(y)), m); s.refresh()
    def over(s, rgba, x, y):
        base = s.im.convert('RGBA'); base.alpha_composite(rgba, dest=(int(x), int(y))); s.im = base.convert('RGB'); s.refresh()
    def text(s, x, y, t, size, fill=WHITE, a=1.0, bold=True, anchor='mm'):
        if a <= 0 or not t: return
        f = font(FB if bold else FR, size)
        if has_ar(t): s.d.text((x, y), t, font=f, fill=fill + (int(255 * a),), anchor=anchor, direction='rtl', language='ar')
        else: s.d.text((x, y), t, font=f, fill=fill + (int(255 * a),), anchor=anchor)
    def shade(s, a):
        if a > 0: s.d.rectangle([0, 0, W, H], fill=(8, 8, 10, int(255 * a)))

def ssl(fn, w, h):
    L = Image.new('RGBA', (w * 2, h * 2), (0, 0, 0, 0)); fn(ImageDraw.Draw(L), 2); return L.reduce(2)

# ------------------------------------------------------------ shared pieces
def badge(f, num, title, a=1.0):
    """persistent top-right chapter tag"""
    f.d.rounded_rectangle([W - 96 - 560, 40, W - 96, 100], 16, fill=(0, 0, 0, int(150 * a)), outline=COPPER + (int(200 * a),), width=2)
    f.text(W - 96 - 30, 70, title, 30, WHITE, a, anchor='rm')
    f.text(W - 96 - 560 + 34, 70, num, 34, COPPER, a, anchor='lm')

def caption(f, ar, en=None, a=1.0, y=950):
    f.d.rounded_rectangle([96, y - 54, W - 96, y + 54], 22, fill=(0, 0, 0, int(165 * a)), outline=(255, 255, 255, int(40 * a)), width=2)
    f.d.rounded_rectangle([W - 96 - 10, y - 38, W - 96 - 2, y + 38], 4, fill=COPPER + (int(255 * a),))
    f.text(W - 96 - 40, y, ar, 44, WHITE, a, anchor='rm')
    aw = font(FB, 44).getlength(ar, direction='rtl', language='ar') if has_ar(ar) else 0
    if en and aw < W - 192 - 80 - font(FB, 38).getlength(en) - 90: f.text(96 + 40, y, en, 38, COPPER, a, anchor='lm')

def title_card(f, num, ar, items, dur_txt, t0=0.0, t1=3.5):
    T = f.T
    out = 1 - rv(T, t1 - .5, .5)
    if T >= t1 or out <= 0: return False
    f.shade(0.0)
    p = rv(T, t0 + .1, .7)
    f.d.text((W - 150, 360 - int((1 - p) * 40)), num, font=font(FB, 330), fill=COPPER + (int(255 * p * out),), anchor='rm')
    ln = ease((T - .3) / .9)
    f.d.line([(W - 150 - 620 * ln, 590), (W - 150, 590)], fill=COPPER + (int(255 * out),), width=5)
    q = rv(T, .5, .7)
    f.text(W - 150, 690 - int((1 - q) * 30), ar, 86, WHITE, q * out, anchor='rm')
    r = rv(T, 1.0, .7)
    f.text(W - 150, 800 - int((1 - r) * 20), '  •  '.join(items), 44, GREY, r * out, bold=False, anchor='rm')
    s = rv(T, 1.4, .6)
    f.d.rounded_rectangle([W - 150 - 320, 860, W - 150, 930], 18, outline=COPPER + (int(255 * s * out),), width=3)
    f.text(W - 150 - 160, 895, dur_txt, 34, COPPER, s * out)
    return True

def finalize(f):
    return f.im

def lens_glyph(f, cx, cy, R, rot=0.0, a=1.0):
    d = f.d
    for rad, col, w in ((R, COPPER, 6), (R * .78, WHITE, 2), (R * .55, TEAL, 4)):
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=col + (int(255 * a),), width=w)
    for i in range(6):
        ang = math.radians(rot + 60 * i)
        d.line([(cx + R * .22 * math.cos(ang), cy + R * .22 * math.sin(ang)), (cx + R * .52 * math.cos(ang + .5), cy + R * .52 * math.sin(ang + .5))], fill=TEAL + (int(200 * a),), width=3)

# =========================================================== M1 exposure triangle
PX = {'ap': 1264, 'sh': 680, 'iso': 96}
PW, PH, PY = 560, 700, 190
M1_DUR = 37.0

def m1_panel(f, key, title_ar, title_en, active, appear, content):
    x = PX[key]
    a = appear * (1.0 if active else .5)
    if a <= 0: return
    f.d.rounded_rectangle([x, PY, x + PW, PY + PH], 28, fill=(22, 22, 26, int(235 * a)), outline=(COPPER if active else (255, 255, 255)) + (int((255 if active else 60) * a),), width=4 if active else 2)
    f.text(x + PW - 30, PY + 44, title_ar, 40, WHITE, a, anchor='rm')
    f.text(x + 30, PY + 44, title_en, 30, COPPER, a, anchor='lm')
    content(f, x, a)

_blur_cache = {}
def blurred(name, lv):
    k = (name, lv)
    if k not in _blur_cache:
        base, _ = cover(img(name), 520, 330, .62, .55, 1.15)
        _blur_cache[k] = base.filter(ImageFilter.GaussianBlur(lv)) if lv else base
    return _blur_cache[k]

def ap_content(f, x, a):
    T = f.T
    o = ease((T - 5.0) / 4.0) if T < 13.2 else 1.0 - ease((T - 30) / 1.0) * 0
    o = clamp(o)
    if T > 30.0: o = 1.0
    base = blurred('lens_abra_edit.jpg', 0)
    levels = (0, 3, 6, 10, 16)
    pos = o * (len(levels) - 1); i0 = int(min(pos, len(levels) - 2)); fr = pos - i0
    b0, b1 = blurred('lens_abra_edit.jpg', levels[i0]), blurred('lens_abra_edit.jpg', levels[i0 + 1])
    bl = Image.blend(b0, b1, fr)
    mask = Image.new('L', bl.size, 0)
    ImageDraw.Draw(mask).ellipse([bl.width * .38, bl.height * .30, bl.width * .88, bl.height * .98], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(26))
    out = Image.composite(base, bl, mask)
    f.paste(out, x + 20, PY + 80, 18, a)
    # iris
    cx, cy = x + PW // 2, PY + 520
    R = lerp(34, 100, o)
    pts = [(cx + R * math.cos(math.radians(60 * i + 15)), cy + R * math.sin(math.radians(60 * i + 15))) for i in range(7)]
    f.d.ellipse([cx - 112, cy - 112, cx + 112, cy + 112], outline=(255, 255, 255, int(70 * a)), width=3)
    f.d.polygon([(cx + R * math.cos(math.radians(360 / 7 * i)), cy + R * math.sin(math.radians(360 / 7 * i))) for i in range(7)], fill=(255, 235, 190, int(235 * a)), outline=COPPER + (int(255 * a),))
    fnum = lerp(16, 1.8, o)
    f.text(x + PW // 2, PY + 646, 'f/%.1f' % fnum if o < .98 else 'f/1.8', 52, COPPER, a)
    f.text(x + PW - 30, PY + 440, 'فتحة واسعة ← خلفية مغبّشة (Bokeh)' if o > .6 else 'فتحة ضيقة ← الصورة كلها واضحة', 26, GREY, a, bold=False, anchor='rm')

def sh_content(f, x, a):
    T = f.T
    # slider position over 13 -> 21 : 1/15 .. 1/1000
    s = ease((T - 14.0) / 5.5) if T < 21 else 1.0
    if T > 30: s = 1.0
    speeds = [15, 60, 250, 1000]
    val = 15 * (1000 / 15) ** s
    E = 1.0 / val
    cx, cy = x + PW // 2, PY + 250
    f.d.rounded_rectangle([x + 20, PY + 80, x + PW - 20, PY + 410], 18, fill=(10, 10, 12, int(255 * a)))
    omega = 2160.0  # deg/s (6 rev/s)
    th = (T * 120) % 360
    arc = omega * E
    n = 16
    layer = Image.new('RGBA', (PW - 40, 330), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    lcx, lcy = (PW - 40) // 2, 165
    for k in range(n):
        ang0 = th - arc * k / max(1, n - 1)
        al = int(255 / max(1, n * (arc / 40 + 1) ** .5 / 2.2)) if arc > 4 else 255
        for b in range(4):
            ba = math.radians(ang0 + 90 * b)
            p1 = (lcx + 20 * math.cos(ba), lcy + 20 * math.sin(ba))
            p2 = (lcx + 125 * math.cos(ba - .22), lcy + 125 * math.sin(ba - .22))
            p3 = (lcx + 125 * math.cos(ba + .22), lcy + 125 * math.sin(ba + .22))
            ld.polygon([p1, p2, p3], fill=(255, 190, 120, max(10, min(255, al))))
    ld.ellipse([lcx - 16, lcy - 16, lcx + 16, lcy + 16], fill=(60, 60, 66, 255))
    layer = layer.filter(ImageFilter.GaussianBlur(1.2 if arc > 6 else .4))
    f.over(layer, x + 20, PY + 80)
    # slider
    sx0, sx1, sy = x + 50, x + PW - 50, PY + 520
    f.d.rounded_rectangle([sx0, sy - 6, sx1, sy + 6], 6, fill=(255, 255, 255, int(60 * a)))
    for i, sp in enumerate(speeds):
        tx = sx0 + (sx1 - sx0) * (math.log(sp / 15) / math.log(1000 / 15))
        f.d.line([(tx, sy - 14), (tx, sy + 14)], fill=(255, 255, 255, int(120 * a)), width=2)
        f.text(tx, sy + 40, '1/%d' % sp, 24, GREY, a, bold=False)
    hx = sx0 + (sx1 - sx0) * s
    f.d.ellipse([hx - 18, sy - 18, hx + 18, sy + 18], fill=COPPER + (int(255 * a),), outline=WHITE + (int(255 * a),), width=3)
    f.text(x + PW // 2, PY + 636, '1/%d' % round(val), 52, COPPER, a)
    f.text(x + PW - 30, PY + 440, 'سرعة عالية ← تجميد الحركة' if s > .85 else 'سرعة منخفضة ← تمويه وانسياب', 26, GREY, a, bold=False, anchor='rm')

_noise_rng = np.random.default_rng(1)
def iso_content(f, x, a):
    T = f.T
    v = ease((T - 22.0) / 6.0) if T < 28.5 else 1.0
    if T > 30: v = 1.0
    iso = 100 * 64 ** v
    base, _ = cover(img('bridge.jpg'), 520, 330, .5, .55, 1.0)
    arr = np.asarray(base).astype(np.float32)
    gain = .35 + .95 * (math.log2(iso / 100) / 6)
    arr = np.clip(arr * (gain * 2.2 if gain < .6 else gain * 1.9), 0, 255) if True else arr
    sigma = 0 if iso <= 3200 else 10 + 42 * (math.log2(iso / 3200))
    if sigma > 0:
        rng = np.random.default_rng(int(T * 30))
        arr = arr + rng.normal(0, sigma, arr.shape[:2])[:, :, None]
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    f.paste(out, x + 20, PY + 80, 18, a)
    # gradient bar
    gx0, gx1, gy = x + 40, x + PW - 40, PY + 520
    for i in range(int(gx1 - gx0)):
        t = i / (gx1 - gx0); c = int(30 + 200 * t)
        f.d.line([(gx0 + i, gy - 14), (gx0 + i, gy + 14)], fill=(c, c, c, int(255 * a)))
    nx = gx0 + (gx1 - gx0) * (math.log2(3200 / 100) / 6)
    f.d.line([(nx, gy - 30), (nx, gy + 30)], fill=RED + (int(255 * a),), width=3)
    f.text(nx, gy - 52, 'بداية التشويش', 24, RED, a, anchor='mm')
    mx = gx0 + (gx1 - gx0) * v
    f.d.polygon([(mx, gy - 20), (mx - 14, gy - 44), (mx + 14, gy - 44)], fill=COPPER + (int(255 * a),))
    for lab, p in (('100', 0), ('800', .5), ('6400', 1)):
        f.text(gx0 + (gx1 - gx0) * p, gy + 44, lab, 24, GREY, a, bold=False)
    f.text(x + PW // 2, PY + 636, 'ISO %d' % (round(iso / 50) * 50), 52, COPPER, a)
    f.text(x + PW - 30, PY + 440, 'ISO عالٍ ← صورة أسطع لكن بتشويش' if iso > 1500 else 'ISO منخفض ← صورة نقية', 26, GREY, a, bold=False, anchor='rm')

def m1(T):
    f = F(T)
    if title_card(f, '01', 'فك شيفرة الكاميرا ومثلث التعريض', ['الفتحة', 'الغالق', 'ISO'], '10 دقائق'):
        return f.im
    badge(f, '01', 'مثلث التعريض')
    appear = lambda t0: rv(T, t0, .6)
    act = lambda a, b: a <= T < b
    tri = T >= 29.2
    k = 1 - rv(T, 29.2, .8)
    f.d.rectangle([0, 0, 0, 0])
    m1_panel(f, 'ap', 'الفتحة', 'APERTURE', act(5, 13.4) or not (5 <= T < 29.2) and False, appear(3.6) * max(k, .0), ap_content) if k > 0 else None
    m1_panel(f, 'sh', 'سرعة الغالق', 'SHUTTER', act(13.4, 21.4), appear(4.0) * max(k, .0), sh_content) if k > 0 else None
    m1_panel(f, 'iso', 'الحساسية', 'ISO', act(21.4, 29.2), appear(4.4) * max(k, .0), iso_content) if k > 0 else None
    caps = [(5, 'الفتحة الواسعة (f/1.8) = خلفية مغبّشة وعزل للهدف', 'APERTURE'), (13.4, 'سرعة 1/1000 = تجميد الحركة تماماً', 'SHUTTER'), (21.4, 'ISO فوق 3200 = بداية التشويش الرقمي', 'ISO')]
    cur = None
    for t0, ar, en in caps:
        if T >= t0: cur = (t0, ar, en)
    if cur and T < 29.2:
        caption(f, cur[1], cur[2], rv(T, cur[0] + .2, .5))
    # triangle summary
    if T >= 29.2:
        p = rv(T, 29.6, .8); fade = 1 - rv(T, 36, .8)
        cx, cy = W // 2, 560
        pts = [(cx, cy - 300), (cx - 360, cy + 220), (cx + 360, cy + 220)]
        for i in range(3):
            a_, b_ = pts[i], pts[(i + 1) % 3]
            q = ease((T - 29.8 - i * .4) / .7)
            if q > 0: f.d.line([a_, (lerp(a_[0], b_[0], q), lerp(a_[1], b_[1], q))], fill=COPPER + (int(255 * fade),), width=8)
        labs = [('الفتحة', 'العمق', pts[0], (0, -70)), ('سرعة الغالق', 'الحركة', pts[1], (-30, 80)), ('ISO', 'نقاء الصورة', pts[2], (30, 80))]
        for i, (a1, a2, pt, off) in enumerate(labs):
            q = rv(T, 30.4 + i * .5, .5) * fade
            f.d.ellipse([pt[0] - 22, pt[1] - 22, pt[0] + 22, pt[1] + 22], fill=COPPER + (int(255 * q),))
            f.text(pt[0] + off[0], pt[1] + off[1] - (10 if off[1] > 0 else 0), a1, 44, WHITE, q)
            f.text(pt[0] + off[0], pt[1] + off[1] + (42 if off[1] > 0 else -42), a2, 32, COPPER, q, bold=False)
        f.text(cx, cy + 40, 'مثلث التعريض', 62, WHITE, rv(T, 32.4, .6) * fade)
        f.text(cx, cy + 112, 'غيّر عنصراً... وازن الباقي', 34, GREY, rv(T, 33.0, .6) * fade, bold=False)
    out = f.im
    if T > M1_DUR - .6: out = Image.blend(out, Image.new('RGB', (W, H), (8, 8, 10)), clamp((T - (M1_DUR - .6)) / .6))
    return out

# =========================================================== M2 composition
M2_DUR = 41.0
SOUK = 'lens_souk_raw.jpg'
MAN = (1380, 640)         # torso centre in souk image px
VP = (1280, 610)          # vanishing point
M2_LINES = [[(520, 1717), (1180, 790), VP], [(2350, 1717), (1560, 830), VP]]

def souk_view(zoom, cx_t, cy_t):
    im = img(SOUK)
    cw = im.width / zoom; ch = cw * 9 / 16
    x = clamp(cx_t * im.width - cw / 2, 0, im.width - cw); y = clamp(cy_t * im.height - ch / 2, 0, im.height - ch)
    return im.resize((W, H), Image.BICUBIC, box=(x, y, x + cw, y + ch)), (x, y, cw, ch)

def to_scr(pt, box): return ((pt[0] - box[0]) / box[2] * W, (pt[1] - box[1]) / box[3] * H)

def m2(T):
    f = F(T)
    if title_card(f, '02', 'قواعد التكوين وصناعة الكادر', ['الأثلاث', 'الخطوط الرائدة', 'التأطير', 'الزوايا'], '12 دقيقة'):
        return f.im
    # ---- sections 3.5-28.5 on the souk photo
    if T < 28.5:
        z = lerp(1.0, 1.35, ease((T - 4.0) / 3.0)) if T < 7 else 1.35
        # pan so that MAN lands on the right-third / upper intersection
        zv = z
        cw = img(SOUK).width / zv; ch = cw * 9 / 16
        tx = MAN[0] - cw * (2 / 3); ty = MAN[1] - ch * (1 / 2) + 40
        pan = ease((T - 5.0) / 3.0)
        x0 = lerp((img(SOUK).width - cw) / 2, clamp(tx, 0, img(SOUK).width - cw), pan)
        y0 = lerp((img(SOUK).height - ch) / 2, clamp(ty, 0, img(SOUK).height - ch), pan)
        box = (x0, y0, cw, ch)
        v = img(SOUK).resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
        dim = .12 + .30 * rv(T, 3.6, .6)
        f.im.paste(v); f.refresh(); f.shade(dim * (0 if T > 28 else 1))
        badge(f, '02', 'قاعدة الأثلاث' if T < 13.5 else 'الخطوط الرائدة' if T < 21.5 else 'التأطير الطبيعي')
        mx, my = to_scr(MAN, box)
        # grid
        if T < 21.5 or T >= 21.5:
            gp = ease((T - 4.2) / 1.6)
            ga = 1.0 if T < 8.5 else .55
            for i in (1, 2):
                f.d.line([(W * i / 3, 0), (W * i / 3, H * gp)], fill=(255, 255, 255, int(235 * ga)), width=3)
                f.d.line([(0, H * i / 3), (W * gp, H * i / 3)], fill=(255, 255, 255, int(235 * ga)), width=3)
            # intersection glows
            for gx in (W / 3, 2 * W / 3):
                for gy in (H / 3, 2 * H / 3):
                    near = math.hypot(mx - gx, my - gy) < 150 and T > 8
                    r = 16
                    if near:
                        pulse = .7 + .3 * math.sin(T * 6)
                        for k in range(8):
                            f.d.ellipse([gx - 20 - k * 9, gy - 20 - k * 9, gx + 20 + k * 9, gy + 20 + k * 9], outline=BLUE + (int(170 * pulse * (1 - k / 8)),), width=4)
                        f.d.ellipse([gx - 20, gy - 20, gx + 20, gy + 20], fill=BLUE + (255,))
                    elif gp > .9:
                        f.d.ellipse([gx - r, gy - r, gx + r, gy + r], outline=WHITE + (200,), width=3)
        if 8.5 < T < 13.6:
            caption(f, 'ضع نقطة الجذب على إحدى نقاط التقاطع الأربع بدل المنتصف', 'RULE OF THIRDS', rv(T, 8.7, .5) * (1 - rv(T, 13, .5)))
        if 4.2 < T < 8.8:
            caption(f, 'الصورة مقسّمة إلى 9 مربعات بخطين أفقيين وخطين عموديين', None, rv(T, 4.4, .5) * (1 - rv(T, 8.3, .5)))
        # leading lines
        if 13.5 <= T < 28.5:
            la = rv(T, 13.8, .5) * (1 - rv(T, 21.2, .4))
            for i, ln in enumerate(M2_LINES):
                pts = [to_scr(p, box) for p in ln]
                q = ease((T - 14.2 - i * .3) / 2.2)
                seg = []
                tot = sum(math.dist(pts[j], pts[j + 1]) for j in range(len(pts) - 1)); acc = 0; tgt = tot * q
                seg = [pts[0]]
                for j in range(len(pts) - 1):
                    d_ = math.dist(pts[j], pts[j + 1])
                    if acc + d_ <= tgt: seg.append(pts[j + 1]); acc += d_
                    else:
                        r_ = (tgt - acc) / d_ if d_ else 0
                        seg.append((lerp(pts[j][0], pts[j + 1][0], r_), lerp(pts[j][1], pts[j + 1][1], r_))); break
                if len(seg) > 1:
                    f.d.line(seg, fill=(0, 0, 0, int(120 * la)), width=14)
                    f.d.line(seg, fill=TEAL + (int(255 * la),), width=8)
                    tip = seg[-1]; prv = seg[-2] if math.dist(seg[-2], tip) > 4 else seg[0]
                    ang = math.atan2(tip[1] - prv[1], tip[0] - prv[0])
                    f.d.polygon([tip, (tip[0] - 40 * math.cos(ang - .4), tip[1] - 40 * math.sin(ang - .4)), (tip[0] - 40 * math.cos(ang + .4), tip[1] - 40 * math.sin(ang + .4))], fill=TEAL + (int(255 * la),))
            if 15 < T < 21.5:
                caption(f, 'الممرات والجدران والسقوف تسحب العين نحو مركز المشهد', 'LEADING LINES', rv(T, 15.2, .5) * (1 - rv(T, 21, .4)))
        # natural framing
        if 21.5 <= T < 28.5:
            fa = rv(T, 21.8, .6) * (1 - rv(T, 28, .4))
            poly = [to_scr(p, box) for p in [(880, 190), (1850, 210), (1930, 1260), (800, 1280)]]
            m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon(poly, fill=255); m = m.filter(ImageFilter.GaussianBlur(3))
            dark = Image.new('RGB', (W, H), (0, 0, 0))
            f.im = Image.composite(f.im, Image.blend(f.im, dark, .62 * fa), m); f.refresh()
            f.d.line(poly + [poly[0]], fill=COPPER + (int(255 * fa),), width=8, joint='curve')
            caption(f, 'الأبواب والنوافذ والممرات المسقوفة تصنع إطاراً طبيعياً حول الهدف', 'NATURAL FRAMING', rv(T, 22.2, .5) * (1 - rv(T, 28, .4)))
    elif T < 37.0:
        # ---- angles diagram
        t = T - 28.5
        badge(f, '02', 'زوايا الالتقاط')
        sx, sy = 1320, 640
        p = rv(T, 28.8, .6)
        f.d.ellipse([sx - 55, sy - 55, sx + 55, sy + 55], fill=COPPER + (int(255 * p),))
        f.text(sx, sy, 'الهدف', 30, (18, 18, 18), p)
        f.d.line([(300, 900), (1700, 900)], fill=(255, 255, 255, int(90 * p)), width=3)
        cams = [('مستوى العين', 'صورة عادية كالجميع', (420, 520), GREY, 29.6), ('منخفضة', 'هيبة ومنظور درامي', (520, 860), TEAL, 31.8), ('مرتفعة', 'منظور غير مألوف', (500, 250), BLUE, 34.0)]
        for ar, sub, (cx_, cy_), col, t0 in cams:
            q = rv(T, t0, .6)
            if q <= 0: continue
            f.d.rounded_rectangle([cx_ - 56, cy_ - 38, cx_ + 56, cy_ + 38], 12, fill=(30, 30, 34, int(255 * q)), outline=col + (int(255 * q),), width=4)
            f.d.ellipse([cx_ + 10, cy_ - 24, cx_ + 58, cy_ + 24], outline=col + (int(255 * q),), width=4)
            ray = ease((T - t0 - .3) / .9)
            f.d.line([(cx_ + 58, cy_), (lerp(cx_ + 58, sx - 60, ray), lerp(cy_, sy, ray))], fill=col + (int(255 * q),), width=5)
            f.text(cx_, cy_ - 70, ar, 38, WHITE, q)
            f.text(cx_, cy_ + 66, sub, 28, col, q, bold=False)
        caption(f, 'ابتعد عن مستوى النظر العادي: انزل نحو الأرض أو اصعد للأعلى', 'ANGLES', rv(T, 29, .5))
    else:
        # ---- recap
        badge(f, '02', 'خلاصة التكوين')
        items = [('الأثلاث', 'ضع الهدف على نقطة تقاطع', 'RULE OF THIRDS'), ('الخطوط الرائدة', 'اجعل الممر يقود العين', 'LEADING LINES'), ('التأطير الطبيعي', 'نافذة، باب، أغصان', 'NATURAL FRAMING'), ('الزوايا', 'انزل أو اصعد', 'ANGLES')]
        for i, (ar, sub, en) in enumerate(items):
            q = rv(T, 37.2 + i * .35, .5)
            x = W - 96 - 440 * (i % 2 + 1) - 24 * (i % 2); x = W - 96 - 880 + (1 - i % 2) * 456 + 0
            xx = 96 + (i % 2) * 0
            col_x = W - 96 - 840 if i % 2 else W - 96 - 840 + 0
            bx = 96 + (1 - i % 2) * 900
            by = 270 + (i // 2) * 270
            f.d.rounded_rectangle([bx, by, bx + 820, by + 220], 28, fill=(255, 255, 255, int(20 * q)), outline=COPPER + (int(220 * q),), width=3)
            f.text(bx + 790, by + 80, ar, 56, WHITE, q, anchor='rm')
            f.text(bx + 790, by + 150, sub, 34, GREY, q, bold=False, anchor='rm')
            f.text(bx + 30, by + 110, en, 30, COPPER, q, anchor='lm')
    out = f.im
    if T > M2_DUR - .6: out = Image.blend(out, Image.new('RGB', (W, H), (8, 8, 10)), clamp((T - (M2_DUR - .6)) / .6))
    return out

# =========================================================== M3 light
M3_DUR = 37.0
_sph = {}
def sphere(theta_deg, size=420):
    """Lambert sphere lit from azimuth theta (0 = from the camera / front, 90 = side, 180 = from behind)."""
    th = math.radians(theta_deg)
    if 'g' not in _sph:
        ys, xs = np.mgrid[0:size, 0:size].astype(np.float32)
        nx = (xs - size / 2) / (size / 2 - 6); ny = (ys - size / 2) / (size / 2 - 6)
        r2 = nx ** 2 + ny ** 2
        mask = r2 <= 1
        nz = np.sqrt(np.clip(1 - r2, 0, 1))
        _sph['g'] = (nx, -ny, nz, mask)
    nx, ny, nz, mask = _sph['g']
    L = np.array([math.sin(th), .25, math.cos(th)]); L /= np.linalg.norm(L)
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    back = max(0.0, -L[2])
    rim = (1 - nz) ** 2.2 * back * 1.4 * np.clip(nx * L[0] + ny * L[1] + 1.0, 0, 1.4)
    val = .06 + .94 * diff ** 1.15 + rim
    rgb = np.stack([val * 255, val * 238, val * 215], -1)
    a = (mask * 255).astype(np.uint8)
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)); im.putalpha(Image.fromarray(a))
    return im.filter(ImageFilter.GaussianBlur(.6))

def m3(T):
    f = F(T)
    if title_card(f, '03', 'لغة الضوء وزوايا السقوط', ['أمامي', 'جانبي', 'خلفي', 'الساعة الذهبية'], '10 دقائق'):
        return f.im
    badge(f, '03', 'لغة الضوء')
    # ----- light sphere 3.5 - 22.5
    if T < 22.8:
        out_a = 1 - rv(T, 22.2, .5)
        t = T - 3.6
        th = 0 if t < 1.5 else ((t - 1.5) / 17.5) * 360
        th = min(th, 360)
        cx, cy = 640, 520
        # floor shadow
        shx = -math.sin(math.radians(th)) * 150; shy = 10
        slen = 1.0 + abs(math.sin(math.radians(th))) * .9
        sh = Image.new('RGBA', (900, 260), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([450 - 170 * slen + shx * .6, 130 - 30, 450 + 170 * slen + shx * .6, 130 + 50], fill=(0, 0, 0, 170))
        sh = sh.filter(ImageFilter.GaussianBlur(22))
        f.over(sh, cx - 450, cy + 190)
        sp = sphere(th)
        sp = sp.resize((520, 520), Image.BICUBIC)
        a = rv(T, 3.8, .6)
        if a < 1: sp.putalpha(sp.getchannel('A').point(lambda v: int(v * a)))
        f.over(sp, cx - 260, cy - 260)
        # orbit
        for i in range(120):
            ang = math.radians(i * 3)
            f.d.ellipse([cx + 380 * math.sin(ang) - 2, cy + 120 * -math.cos(ang) - 2 - 0, cx + 380 * math.sin(ang) + 2, cy + 120 * -math.cos(ang) + 2], fill=(255, 255, 255, int(70 * a)))
        lx = cx + 380 * math.sin(math.radians(th)); ly = cy - 120 * math.cos(math.radians(th)) - (0)
        # front (th=0) = nearest to viewer => bottom of ellipse
        ly = cy + 120 * math.cos(math.radians(th)) + 20
        for k in range(7): f.d.ellipse([lx - 26 - k * 8, ly - 26 - k * 8, lx + 26 + k * 8, ly + 26 + k * 8], fill=(255, 210, 120, int(46 * (1 - k / 7) * a)))
        f.d.ellipse([lx - 24, ly - 24, lx + 24, ly + 24], fill=(255, 225, 150, int(255 * a)))
        # kind
        thn = th % 360
        def near(c, w): return min(abs(thn - c), 360 - abs(thn - c)) < w
        kinds = [('الضوء الأمامي', 'يضيء بالتساوي لكنه يسطّح الأبعاد', near(0, 40), 'FRONT LIGHT'),
                 ('الضوء الجانبي', 'تباين وملمس وبُعد واقعي', near(90, 40) or near(270, 40), 'SIDE LIGHT'),
                 ('الإضاءة الخلفية', 'هالة حواف ناعمة أو سلويت', near(180, 40), 'BACKLIGHT')]
        for i, (ar, sub, on, en) in enumerate(kinds):
            y = 250 + i * 190
            q = rv(T, 4.4 + i * .3, .5) * out_a
            f.d.rounded_rectangle([1180, y, 1824, y + 160], 24, fill=(255, 255, 255, int((26 if on else 10) * q)), outline=(COPPER if on else (255, 255, 255)) + (int((255 if on else 50) * q),), width=4 if on else 2)
            f.text(1790, y + 54, ar, 46, WHITE if on else GREY, q, anchor='rm')
            f.text(1790, y + 112, sub, 30, COPPER if on else (110, 110, 116), q, bold=False, anchor='rm')
            f.text(1212, y + 80, en, 24, COPPER if on else (90, 90, 95), q, anchor='lm')
        caption(f, 'نفس الكرة... ثلاث صور مختلفة تماماً حسب اتجاه الضوء', 'LIGHT DIRECTION', rv(T, 5, .6) * out_a)
    # ----- golden hour 22.5 - 29.5
    elif T < 29.6:
        t = T - 22.5
        a = rv(T, 22.7, .6) * (1 - rv(T, 29.1, .5))
        # sky bar
        for i in range(W - 192):
            u = i / (W - 192)
            warm = max(0, 1 - abs(u - .14) / .12) + max(0, 1 - abs(u - .86) / .12)
            r = int(30 + 200 * warm + 20 * (1 - warm)); g = int(40 + 110 * warm + 40 * (1 - warm)); b_ = int(70 + 10 * warm + 110 * (1 - warm) * (1 - .6 * abs(u - .5)))
            f.d.line([(96 + i, 330), (96 + i, 470)], fill=(r, g, b_, int(255 * a)))
        f.d.rounded_rectangle([96, 330, W - 96, 470], 20, outline=(255, 255, 255, int(70 * a)), width=2)
        # sun arc
        sx = lerp(180, W - 180, ease((T - 23.0) / 5.5))
        arcy = 700 - 230 * math.sin(math.pi * (sx - 180) / (W - 360))
        f.d.arc([180, 470, W - 180, 930], 180, 360, fill=(255, 255, 255, int(70 * a)), width=3)
        f.d.line([(120, 700), (W - 120, 700)], fill=(255, 255, 255, int(60 * a)), width=3)
        for k in range(6): f.d.ellipse([sx - 36 - k * 9, arcy - 36 - k * 9, sx + 36 + k * 9, arcy + 36 + k * 9], fill=(255, 190, 90, int(50 * (1 - k / 6) * a)))
        f.d.ellipse([sx - 34, arcy - 34, sx + 34, arcy + 34], fill=(255, 215, 120, int(255 * a)))
        f.text(96 + .14 * (W - 192), 400, 'ساعة بعد الشروق', 34, WHITE, a * rv(T, 23.6, .5))
        f.text(96 + .86 * (W - 192), 400, 'ساعة قبل الغروب', 34, WHITE, a * rv(T, 25, .5))
        f.text(W // 2, 400, 'ضوء قاسٍ', 34, GREY, a * rv(T, 26, .5), bold=False)
        caption(f, 'الساعة الذهبية: ضوء مائل ودافئ وألوان لا تحتاج تعديلاً معقّداً', 'GOLDEN HOUR', a)
    else:
        # ----- tip card
        t = T - 29.6
        a = rv(T, 29.8, .6) * (1 - rv(T, 36.4, .5))
        lens_glyph(f, 560, 520, 190, T * 20, a)
        # fingerprint haze
        haze = (1 - ease((T - 31.5) / 2.0)) * .55
        f.d.ellipse([560 - 175, 520 - 175, 560 + 175, 520 + 175], fill=(255, 255, 255, int(255 * haze * a)))
        # progress ring 0 -> 80%
        p = ease((T - 32.0) / 2.5) * .8
        rr = 150
        f.d.arc([1300 - rr, 520 - rr, 1300 + rr, 520 + rr], -90, 270, fill=(255, 255, 255, int(40 * a)), width=24)
        f.d.arc([1300 - rr, 520 - rr, 1300 + rr, 520 + rr], -90, -90 + 360 * p, fill=COPPER + (int(255 * a),), width=24)
        f.text(1300, 520, '%d%%' % round(p * 100), 90, WHITE, a)
        f.text(1300, 720, 'من الهالات الباهتة تزول', 40, GREY, a, bold=False)
        f.text(W // 2, 230, 'نصيحة ذهبية للهاتف', 62, WHITE, a)
        f.text(W // 2, 310, 'نظّف العدسة بقطعة قطن', 44, COPPER, a)
        caption(f, 'بصمات الأصابع تصنع هالات باهتة... وقطعة قطن تحلّ المشكلة', 'LENS TIP', a)
    out = f.im
    if T > M3_DUR - .6: out = Image.blend(out, Image.new('RGB', (W, H), (8, 8, 10)), clamp((T - (M3_DUR - .6)) / .6))
    return out

# =========================================================== M4 quick edit
M4_DUR = 31.0
def m4_edit(raw, ed, p):
    return Image.blend(raw, ed, clamp(p))

def m4(T):
    f = F(T)
    if title_card(f, '04', 'التحرير السريع والمعالجة البصرية', ['توازن البياض', 'الظلال والسطوع'], '8 دقائق'):
        return f.im
    badge(f, '04', 'التحرير السريع')
    raw, _ = cover(img('lens_creek_raw.jpg'), 1000, 560)
    ed, _ = cover(img('lens_creek_edit.jpg'), 1000, 560)
    over = ImageEnhance.Contrast(ImageEnhance.Color(ed).enhance(2.6)).enhance(1.55).filter(ImageFilter.UnsharpMask(4, 260, 0))
    if T < 15.0:
        # phone
        px, py, pw, ph = 190, 130, 470, 880
        a = rv(T, 3.7, .6)
        f.d.rounded_rectangle([px, py, px + pw, py + ph], 56, fill=(14, 14, 16, int(255 * a)), outline=(255, 255, 255, int(120 * a)), width=5)
        f.d.rounded_rectangle([px + pw // 2 - 50, py + 18, px + pw // 2 + 50, py + 36], 9, fill=(40, 40, 44, int(255 * a)))
        # progress per slider
        sl = [('توازن البياض', 'White Balance', 5.0), ('الظلال', 'Shadows', 6.6), ('السطوع', 'Highlights', 8.2), ('التباين', 'Contrast', 9.8)]
        vals = [ease((T - t0) / 1.4) for _, _, t0 in sl]
        prog = sum(vals) / len(vals)
        photo = Image.blend(raw, ed, prog).resize((430, 242), Image.BICUBIC)
        f.paste(photo, px + 20, py + 60, 18, a)
        for i, (ar, en, t0) in enumerate(sl):
            y = py + 360 + i * 120
            f.text(px + pw - 30, y, ar, 34, WHITE, a, anchor='rm')
            f.text(px + 30, y, en, 26, COPPER, a, anchor='lm')
            f.d.rounded_rectangle([px + 30, y + 42, px + pw - 30, y + 52], 5, fill=(255, 255, 255, int(60 * a)))
            hx = px + 30 + (pw - 60) * (.5 + .38 * vals[i] * (1 if i % 2 == 0 else .9))
            f.d.ellipse([hx - 16, y + 47 - 16, hx + 16, y + 47 + 16], fill=COPPER + (int(255 * a),), outline=WHITE + (int(255 * a),), width=3)
        # result side
        rx, ry = 760, 200
        rb = rv(T, 4.2, .6)
        view = Image.blend(raw, ed, ease((T - 10.8) / 1.8))
        f.paste(view, rx + 0, ry, 28, rb)
        f.d.rounded_rectangle([rx, ry, rx + 1000, ry + 560], 28, outline=(255, 255, 255, int(70 * rb)), width=2)
        chip_t = 'قبل' if T < 11.5 else 'بعد'
        f.d.rounded_rectangle([rx + 24, ry + 24, rx + 150, ry + 76], 14, fill=(0, 0, 0, int(190 * rb)), outline=COPPER + (int(255 * rb),), width=2)
        f.text(rx + 87, ry + 50, chip_t, 34, WHITE, rb)
        if T > 12.2:
            q = rv(T, 12.2, .5)
            f.d.rounded_rectangle([rx + 700, ry + 24, rx + 976, ry + 76], 14, fill=COPPER + (int(235 * q),))
            f.text(rx + 838, ry + 50, 'أقل من ثانيتين', 32, (18, 18, 18), q)
        caption(f, 'عدّل توازن البياض ثم الظلال والسطوع... والنتيجة فورية', 'WHITE BALANCE • SHADOWS • HIGHLIGHTS', rb, y=930)
    elif T < 26.0:
        t = T - 15.0
        a = rv(T, 15.2, .5) * (1 - rv(T, 25.4, .5))
        pw_, ph_ = 560, 315
        items = [(raw, 'خام', 'RAW', GREY, None), (ed.resize((1000, 560)), 'تعديل طبيعي', 'NATURAL', GREEN, True), (over.resize((1000, 560)), 'تعديل مبالغ فيه', 'OVER-EDITED', RED, False)]
        for i, (im, ar, en, col, ok) in enumerate(items):
            q = rv(T, 15.4 + i * .6, .6) * (1 - rv(T, 25.4, .5))
            x = W - 96 - pw_ - i * (pw_ + 48) - 0
            x = 96 + (2 - i) * (pw_ + 48)
            x = W - 96 - pw_ - i * (pw_ + 48)
            im2 = im.resize((pw_, ph_), Image.BICUBIC)
            f.paste(im2, x, 300, 22, q)
            f.d.rounded_rectangle([x, 300, x + pw_, 300 + ph_], 22, outline=col + (int(255 * q),), width=5)
            f.text(x + pw_ // 2, 690, ar, 48, WHITE, q)
            f.text(x + pw_ // 2, 750, en, 28, col, q)
            if ok is not None:
                cx_, cy_ = x + pw_ - 50, 350
                f.d.ellipse([cx_ - 32, cy_ - 32, cx_ + 32, cy_ + 32], fill=col + (int(255 * q),))
                if ok:
                    f.d.line([(cx_ - 14, cy_), (cx_ - 3, cy_ + 12), (cx_ + 16, cy_ - 12)], fill=(18, 18, 18, int(255 * q)), width=7)
                else:
                    f.d.line([(cx_ - 12, cy_ - 12), (cx_ + 12, cy_ + 12)], fill=WHITE + (int(255 * q),), width=7); f.d.line([(cx_ - 12, cy_ + 12), (cx_ + 12, cy_ - 12)], fill=WHITE + (int(255 * q),), width=7)
        f.text(W // 2, 880, 'التعديل الجيد هو الذي لا يلاحظه أحد', 52, WHITE, rv(T, 19.0, .6) * (1 - rv(T, 25.4, .5)))
        caption(f, 'عالج عيوب التعريض وأبرز الألوان... بدون مرشحات ثقيلة', 'ENHANCE • DON\'T OVERDO', a, y=980 - 20)
    else:
        a = rv(T, 26.2, .6) * (1 - rv(T, 30.4, .5))
        f.text(W // 2, 300, 'أدوات مجانية مقترحة', 64, WHITE, a)
        for i, (nm, sub) in enumerate((('Snapseed', 'مجاني بالكامل'), ('Adobe Lightroom Mobile', 'استخدام مجاني وشامل'))):
            q = rv(T, 26.6 + i * .5, .6) * (1 - rv(T, 30.4, .5))
            x = W // 2 - 520 + i * 560 if False else (W // 2 + 40 if i == 0 else W // 2 - 760)
            f.d.rounded_rectangle([x, 420, x + 720, 640], 32, fill=(255, 255, 255, int(24 * q)), outline=COPPER + (int(230 * q),), width=3)
            f.text(x + 360, 500, nm, 52, WHITE, q)
            f.text(x + 360, 580, sub, 34, COPPER, q, bold=False)
        f.text(W // 2, 780, 'للهواتف الذكية', 38, GREY, a, bold=False)
    out = f.im
    if T > M4_DUR - .6: out = Image.blend(out, Image.new('RGB', (W, H), (8, 8, 10)), clamp((T - (M4_DUR - .6)) / .6))
    return out

# =========================================================== M5 golden rules
M5_DUR = 17.0
def m5(T):
    f = F(T)
    f.text(W // 2, 150, 'القواعد الذهبية', 56, COPPER, rv(T, .2, .6) * (1 - rv(T, 16.4, .5)))
    for i, (num, ar, sub, ic) in enumerate((('1', 'الكاميرا أداة... والعين هي الصانع', 'التقنية لا تعوّض التكوين الضعيف. فهم الزاوية والضوء بالهاتف يتفوّق على كاميرا احترافية بإعدادات عشوائية.', 'eye'),
                                            ('2', 'ثانية التنظيف وتريّث الإطار', 'امسح العدسة قبل كل جلسة، وامنح نفسك 5 ثوانٍ قبل الضغط لمراجعة الأطراف وخلوّ الخلفية من المشتتات.', 'timer'))):
        t0 = .8 + i * 8.0
        q = rv(T, t0, .7) * (1 - rv(T, t0 + 7.3, .5)) if i == 0 else rv(T, t0, .7) * (1 - rv(T, 16.4, .5))
        if q <= 0: continue
        cx, cy = 460, 560
        f.d.ellipse([cx - 220, cy - 220, cx + 220, cy + 220], outline=COPPER + (int(255 * q),), width=6)
        if ic == 'eye':
            f.d.arc([cx - 150, cy - 90, cx + 150, cy + 90], 180, 360, fill=WHITE + (int(255 * q),), width=10)
            f.d.arc([cx - 150, cy - 90, cx + 150, cy + 90], 0, 180, fill=WHITE + (int(255 * q),), width=10)
            f.d.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=COPPER + (int(255 * q),))
            f.d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(18, 18, 18, int(255 * q)))
        else:
            p = clamp((T - t0 - 1.5) / 5.0)
            f.d.arc([cx - 150, cy - 150, cx + 150, cy + 150], -90, 270, fill=(255, 255, 255, int(50 * q)), width=22)
            f.d.arc([cx - 150, cy - 150, cx + 150, cy + 150], -90, -90 + 360 * p, fill=COPPER + (int(255 * q),), width=22)
            f.text(cx, cy, str(max(0, 5 - int(p * 5))), 130, WHITE, q)
        f.d.text((W - 150, 470), num, font=font(FB, 200), fill=COPPER + (int(255 * q),), anchor='rm')
        f.text(W - 360, 470, ar, 66, WHITE, q, anchor='rm')
        # wrap sub
        words = sub.split(' '); lines = []; cur = ''
        for w_ in words:
            trial = (cur + ' ' + w_).strip()
            if font(FR, 40).getlength(trial, direction='rtl', language='ar') < 960 or not cur: cur = trial
            else: lines.append(cur); cur = w_
        lines.append(cur)
        for j, ln in enumerate(lines): f.text(W - 150, 600 + j * 64, ln, 40, GREY, q * rv(T, t0 + .5, .6), bold=False, anchor='rm')
    return f.im

# =========================================================== M6 graduation project
M6_DUR = 22.0
def mug(f, cx, cy, s=1.0, col=(235, 235, 240), a=1.0):
    f.d.rounded_rectangle([cx - 60 * s, cy - 60 * s, cx + 60 * s, cy + 60 * s], 14 * s, fill=col + (int(255 * a),))
    f.d.arc([cx + 40 * s, cy - 36 * s, cx + 110 * s, cy + 34 * s], -90, 90, fill=col + (int(255 * a),), width=int(16 * s))

def m6(T):
    f = F(T)
    badge(f, '★', 'مشروع التخرج', rv(T, .2, .5))
    if T < 11.0:
        q0 = rv(T, .3, .6) * (1 - rv(T, 10.5, .4))
        f.text(W // 2, 190, 'التحدي الأول: الكائن اليومي', 66, WHITE, q0)
        f.text(W // 2, 262, '3 زوايا وتكوينات لعنصر واحد من البيت', 38, COPPER, q0, bold=False)
        cards = [('لقطة ثلثية', 'على أحد خطوط الثلث مع فراغ مريح', 'thirds'), ('لقطة أرضية منخفضة', 'الهاتف ملاصق للطاولة ويتجه للأعلى', 'low'), ('لقطة بإطار طبيعي', 'من فتحة أو بين كتابين أو خلف زجاج', 'frame')]
        for i, (ar, sub, kind) in enumerate(cards):
            q = rv(T, 1.2 + i * .7, .6) * (1 - rv(T, 10.5, .4))
            x = W - 96 - 560 - i * 592
            f.d.rounded_rectangle([x, 340, x + 560, 880], 30, fill=(22, 22, 26, int(235 * q)), outline=COPPER + (int(220 * q),), width=3)
            f.d.rounded_rectangle([x + 20, 360, x + 540, 640], 18, fill=(40, 42, 50, int(255 * q)))
            if kind == 'thirds':
                for k in (1, 2):
                    f.d.line([(x + 20 + 520 * k / 3, 360), (x + 20 + 520 * k / 3, 640)], fill=(255, 255, 255, int(110 * q)), width=2)
                    f.d.line([(x + 20, 360 + 280 * k / 3), (x + 540, 360 + 280 * k / 3)], fill=(255, 255, 255, int(110 * q)), width=2)
                mug(f, x + 20 + 520 * 2 / 3, 360 + 280 * 2 / 3 - 20, .75, a=q)
                f.d.ellipse([x + 20 + 520 * 2 / 3 - 12, 360 + 280 * 2 / 3 - 32, x + 20 + 520 * 2 / 3 + 12, 360 + 280 * 2 / 3 - 8], outline=BLUE + (int(255 * q),), width=3)
            elif kind == 'low':
                f.d.rectangle([x + 20, 560, x + 540, 640], fill=(70, 55, 45, int(255 * q)))
                mug(f, x + 280, 520, 1.1, a=q)
                f.d.polygon([(x + 280, 700), (x + 250, 740), (x + 310, 740)], fill=COPPER + (int(255 * q),))
                f.d.line([(x + 280, 700), (x + 280, 660)], fill=COPPER + (int(255 * q),), width=4)
            else:
                f.d.rounded_rectangle([x + 60, 380, x + 500, 620], 20, outline=COPPER + (int(255 * q),), width=14)
                mug(f, x + 280, 505, .8, a=q)
            f.text(x + 280, 700, ar, 44, WHITE, q)
            f.text(x + 280, 770, sub, 28, GREY, q, bold=False)
    else:
        q0 = rv(T, 11.0, .6) * (1 - rv(T, 21.4, .4))
        f.text(W // 2, 190, 'التحدي الثاني: ترويض الضوء', 66, WHITE, q0)
        f.text(W // 2, 262, 'صورتان لنفس العنصر أو لشخص في البيت', 38, COPPER, q0, bold=False)
        for i, (ar, sub, kind) in enumerate((('ضوء جانبي', 'من نافذة نهارية لإظهار نسيج السطح وظلاله', 'side'), ('سلويت', 'العنصر أمام نافذة ساطعة مع خفض التعريض', 'sil'))):
            q = rv(T, 11.8 + i * .8, .6) * (1 - rv(T, 21.4, .4))
            x = W - 96 - 820 - i * 880
            f.d.rounded_rectangle([x, 340, x + 820, 880], 30, fill=(22, 22, 26, int(235 * q)), outline=COPPER + (int(220 * q),), width=3)
            f.d.rounded_rectangle([x + 20, 360, x + 800, 700], 18, fill=(36, 38, 46, int(255 * q)))
            if kind == 'side':
                f.d.rounded_rectangle([x + 40, 380, x + 240, 680], 10, fill=(255, 235, 190, int(255 * q)))
                f.d.line([(x + 140, 380), (x + 140, 680)], fill=(80, 70, 60, int(255 * q)), width=6)
                mug(f, x + 540, 560, 1.2, col=(200, 200, 208), a=q)
                f.d.polygon([(x + 600, 620), (x + 780, 650), (x + 780, 690), (x + 590, 690)], fill=(0, 0, 0, int(90 * q)))
                f.d.rectangle([x + 20 + 580, 360, x + 800, 700], fill=(0, 0, 0, int(50 * q)))
            else:
                f.d.rounded_rectangle([x + 140, 380, x + 680, 690], 10, fill=(255, 240, 200, int(255 * q)))
                f.d.line([(x + 410, 380), (x + 410, 690)], fill=(70, 60, 50, int(255 * q)), width=8)
                mug(f, x + 410, 560, 1.4, col=(8, 8, 10), a=q)
            f.text(x + 410, 750, ar, 48, WHITE, q)
            f.text(x + 410, 820, sub, 28, GREY, q, bold=False)
    f.text(W // 2, 990, 'أرسلوا أعمالكم ليتم تقييمها في نهاية الورشة', 38, WHITE, rv(T, 3.0, .6) * (1 - rv(T, 21.4, .4)), bold=False)
    return f.im

CLIPS = {'m1': (m1, M1_DUR, '01_exposure_triangle'), 'm2': (m2, M2_DUR, '02_composition'), 'm3': (m3, M3_DUR, '03_light'),
         'm4': (m4, M4_DUR, '04_quick_edit'), 'm5': (m5, M5_DUR, '05_golden_rules'), 'm6': (m6, M6_DUR, '06_graduation_project')}

def _frame(args):
    key, i = args
    return CLIPS[key][0](i / FPS).tobytes()

def main():
    av = sys.argv[1:]
    out = f'{HERE}/out'; os.makedirs(out, exist_ok=True)
    if '--preview' in av:
        pv = f'{HERE}/preview'; os.makedirs(pv, exist_ok=True)
        rest = [a for a in av if a != '--preview']
        key = rest[0]; ts = [float(x) for x in rest[1:]] or [1.5, 6, 11, 17, 24, 30, 34]
        for T in ts: CLIPS[key][0](T).save(f'{pv}/{key}_{T:05.1f}.jpg', quality=88)
        return
    keys = [a for a in av if a in CLIPS] or list(CLIPS)
    for key in keys:
        fn, dur, name = CLIPS[key]
        N = int(dur * FPS)
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', f'{out}/{name}.mp4'], stdin=subprocess.PIPE)
        with Pool(4) as pool:
            for i, fr in enumerate(pool.imap(_frame, [(key, i) for i in range(N)], chunksize=6)):
                p.stdin.write(fr)
        p.stdin.close(); p.wait(); print('done', name, flush=True)

if __name__ == '__main__':
    main()
