#!/usr/bin/env python3
"""Video 2 — 'How to choose your lens' (80 s, 9:16, 1080x1920, 30 fps, no voice-over).

  python3 build_lens.py --preview [t ...]   # stills -> preview/
  python3 build_lens.py                     # full render -> out/lens_guide_no_voiceover.mp4
"""
import math, os, sys, subprocess, wave
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw
from build import ease, clamp, ar_text, HERE
from PIL import ImageFont
FB = f'{HERE}/assets/fonts/Tajawal-Bold.ttf'
FR = f'{HERE}/assets/fonts/Tajawal-Medium.ttf'
def font(p, s): return ImageFont.truetype(p, int(s * 1.14))

W, H, FPS, DUR = 1080, 1920, 30, 80.0
BGC = (18, 18, 18)
COPPER, TEAL, WHITE, GREY = (232, 135, 58), (47, 168, 184), (255, 255, 255), (170, 170, 176)

def load(n): return Image.open(f'{HERE}/assets/{n}').convert('RGB')
IM = {k: load(f'lens_{k}.jpg') for k in ('abra_raw', 'abra_edit', 'souk_raw', 'souk_bw', 'creek_raw', 'creek_edit')}

# ------------------------------------------------------------------ helpers
def box_view(im, w, h, cx=.5, cy=.5, zoom=1.0):
    """cover-fit im into w x h, then zoom about (cx,cy) (fractions of image)."""
    s = max(w / im.width, h / im.height) * zoom
    cw, ch = w / s, h / s
    x = clamp(cx * im.width - cw / 2, 0, im.width - cw); y = clamp(cy * im.height - ch / 2, 0, im.height - ch)
    return im.resize((w, h), Image.BICUBIC, box=(x, y, x + cw, y + ch)), (x, y, cw, ch)

def rounded_paste(canvas, im, x, y, r=28, a=1.0):
    mask = Image.new('L', im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=int(255 * a))
    canvas.paste(im, (int(x), int(y)), mask)

def ss(fn, w, h):
    """draw with fn(d, k) on a 2x layer and return the 1x RGBA."""
    L = Image.new('RGBA', (w * 2, h * 2), (0, 0, 0, 0))
    fn(ImageDraw.Draw(L), 2)
    return L.reduce(2)

def arc_pts(cx, cy, r, p, a0=-90):
    n = max(4, int(120 * p))
    return [(cx + r * math.cos(math.radians(a0 + 360 * p * i / n)), cy + r * math.sin(math.radians(a0 + 360 * p * i / n))) for i in range(n + 1)]

def lens_icon(cx, cy, R, p, rot, glow=0.0):
    sz = int(R * 2.6)
    def f(d, k):
        c = sz * k / 2
        if glow > 0:
            for i in range(6):
                rr = (R * 1.08 + i * 10) * k
                d.ellipse([c - rr, c - rr, c + rr, c + rr], outline=COPPER + (int(70 * glow * (1 - i / 6)),), width=6 * k)
        d.ellipse([c - R * .62 * k, c - R * .62 * k, c + R * .62 * k, c + R * .62 * k], fill=(14, 34, 40, int(255 * clamp(p * 2 - 1))))
        for rad, col, w in ((R, COPPER, 9), (R * .84, WHITE, 3), (R * .62, TEAL, 5), (R * .30, WHITE, 3)):
            pts = arc_pts(c / k, c / k, rad, clamp(p * 1.2), -90)
            if len(pts) > 1: d.line([(x * k, y * k) for x, y in pts], fill=col + (255,), width=int(w * k), joint='curve')
        if p > .6:
            a = clamp((p - .6) / .4)
            for i in range(6):
                ang = math.radians(rot + 60 * i)
                x0, y0 = c / k + R * .32 * math.cos(ang), c / k + R * .32 * math.sin(ang)
                x1, y1 = c / k + R * .60 * math.cos(ang + .5), c / k + R * .60 * math.sin(ang + .5)
                d.line([(x0 * k, y0 * k), (x1 * k, y1 * k)], fill=TEAL + (int(200 * a),), width=3 * k)
            hx, hy = c / k - R * .35, c / k - R * .38
            d.ellipse([(hx - 10) * k, (hy - 10) * k, (hx + 10) * k, (hy + 10) * k], fill=(255, 255, 255, int(220 * a)))
    return ss(f, sz, sz), (int(cx - sz / 2), int(cy - sz / 2))

def pin_icon(cx, cy, s=1.0):
    sz = 160
    def f(d, k):
        c = sz * k / 2
        d.ellipse([c - 44 * k * s, c - 70 * k * s, c + 44 * k * s, c + 18 * k * s], fill=COPPER + (255,))
        d.polygon([(c - 36 * k * s, c - 2 * k * s), (c + 36 * k * s, c - 2 * k * s), (c, c + 62 * k * s)], fill=COPPER + (255,))
        d.ellipse([c - 16 * k * s, c - 42 * k * s, c + 16 * k * s, c - 10 * k * s], fill=(18, 18, 18, 255))
    return ss(f, sz, sz), (int(cx - sz / 2), int(cy - sz * .62))

def sun_icon(cx, cy, col, moon=False, r=26):
    sz = 120
    def f(d, k):
        c = sz * k / 2
        if moon:
            d.ellipse([c - r * k, c - r * k, c + r * k, c + r * k], fill=col + (255,))
            d.ellipse([c - r * k + 16 * k, c - r * k - 6 * k, c + r * k + 16 * k, c + r * k - 6 * k], fill=(0, 0, 0, 0))
        else:
            d.ellipse([c - r * .8 * k, c - r * .8 * k, c + r * .8 * k, c + r * .8 * k], fill=col + (255,))
            for i in range(8):
                a = math.radians(45 * i)
                d.line([(c + r * 1.15 * k * math.cos(a), c + r * 1.15 * k * math.sin(a)), (c + r * 1.6 * k * math.cos(a), c + r * 1.6 * k * math.sin(a))], fill=col + (255,), width=4 * k)
    return ss(f, sz, sz), (int(cx - sz / 2), int(cy - sz / 2))

# ------------------------------------------------------------------ text/ui
class Ctx:
    def __init__(s, T):
        s.T = T
        s.cv = bg_base.copy()
        s.ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        s.d = ImageDraw.Draw(s.ov)
    def put(s, rgba, pos, a=1.0):
        if a < 1: rgba = rgba.copy(); rgba.putalpha(rgba.getchannel('A').point(lambda v: int(v * a)))
        s.ov.alpha_composite(rgba, dest=(int(pos[0]), int(pos[1])))

def rv(t, t0, dur=.55): return ease((t - t0) / dur)

def txt(c, y, s, size, fill=WHITE, a=1.0, bold=True, x=W // 2, anchor='mm', dy=0):
    if a <= 0: return
    ar_text(c.d, (x, y + dy), s, font(FB if bold else FR, size), fill + (int(255 * a),), anchor)

def title(c, num, text, t0):
    t = c.T - t0
    p = rv(t, 0.1, .6); q = rv(t, .35, .6)
    if p > 0:
        r = 46
        c.d.ellipse([W // 2 - r, 300 - r - int((1 - p) * 30), W // 2 + r, 300 + r - int((1 - p) * 30)], fill=COPPER + (int(255 * p),))
        c.d.text((W // 2, 300 - int((1 - p) * 30)), str(num), font=font(FB, 56), fill=(18, 18, 18, int(255 * p)), anchor='mm')
    txt(c, 410, text, 68, WHITE, q, dy=int((1 - q) * 30))

def card(c, y, main, sub, t0, h=124):
    p = rv(c.T, t0, .6)
    if p <= 0: return
    x0, x1 = 100, W - 100
    yy = y + int((1 - p) * 50)
    c.d.rounded_rectangle([x0, yy, x1, yy + h], 22, fill=(255, 255, 255, int(20 * p)), outline=(255, 255, 255, int(46 * p)), width=2)
    c.d.rounded_rectangle([x1 - 10, yy + 18, x1 - 2, yy + h - 18], 4, fill=COPPER + (int(255 * p),))
    txt(c, yy + (int(h * .36) if sub else h // 2), main, 42, WHITE, p, x=x1 - 40, anchor='rm')
    if sub: txt(c, yy + int(h * .76), sub, 30, COPPER, p, bold=False, x=x1 - 40, anchor='rm')

def chip(c, x, y, s, t0, col=COPPER, size=28):
    p = rv(c.T, t0, .4)
    if p <= 0: return
    f = font(FB, size); w = int(f.getlength(s)) + 36
    c.d.rounded_rectangle([x, y, x + w, y + 48], 14, fill=(10, 10, 10, int(210 * p)), outline=col + (int(255 * p),), width=2)
    c.d.text((x + 18, y + 24), s, font=f, fill=WHITE + (int(255 * p),), anchor='lm')

def progress(c, step, t_in):
    for i in range(4):
        x0 = 140 + i * 205
        c.d.rounded_rectangle([x0, 222, x0 + 185, 230], 4, fill=(255, 255, 255, 40))
        if i + 1 < step: fill = 1
        elif i + 1 == step: fill = clamp((c.T - t_in) / 1.2)
        else: fill = 0
        if fill > 0: c.d.rounded_rectangle([x0, 222, x0 + max(8, 185 * fill), 230], 4, fill=COPPER + (255,))

# ------------------------------------------------------------------ scenes
def scene1(c):
    t = c.T
    p = ease(t / 1.8)
    R = 215 * (.75 + .25 * ease(t / 1.2)) * (1 + .05 * math.exp(-(t - 2.4) * 6) * (t > 2.4))
    img, pos = lens_icon(W // 2, 640, R, p, t * 40, glow=clamp((t - 1.5) / 1) * (.6 + .4 * math.sin(t * 3)))
    c.put(img, pos, 1 - ease((t - 9.5) / .5))
    fade = 1 - ease((t - 9.4) / .6)
    txt(c, 1010, 'تحتار أي عدسة', 92, WHITE, rv(t, 2.4, .7) * fade, dy=int((1 - rv(t, 2.4, .7)) * 40))
    txt(c, 1125, 'تاخذ معك؟', 100, COPPER, rv(t, 3.1, .7) * fade, dy=int((1 - rv(t, 3.1, .7)) * 40))
    txt(c, 1270, '٤ خطوات بسيطة تختصر عليك الكثير', 40, GREY, rv(t, 5.2, .7) * fade, bold=False)
    labels = ['التخطيط', 'الهدف', 'العدسة', 'التعديل']
    for i in range(4):
        a = rv(t, 7.0 + i * .35, .5) * fade
        x = 810 - i * 180
        c.d.ellipse([x - 40, 1440 - 40, x + 40, 1440 + 40], outline=COPPER + (int(255 * a),), width=4)
        c.d.text((x, 1440), str(i + 1), font=font(FB, 44), fill=WHITE + (int(255 * a),), anchor='mm')
        txt(c, 1515, labels[i], 28, GREY, a, bold=False, x=x)

def map_card(c, y0, h, t0):
    p = rv(c.T, t0, .7)
    if p <= 0: return
    x0, w = 100, 880
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 28, fill=(24, 34, 40, 255))
    for i in range(1, 8): d.line([(i * w / 8, 0), (i * w / 8, h)], fill=(255, 255, 255, 14), width=2)
    for j in range(1, 4): d.line([(0, j * h / 4), (w, j * h / 4)], fill=(255, 255, 255, 14), width=2)
    d.line([(0, h * .72), (w * .3, h * .58), (w * .6, h * .70), (w, h * .52)], fill=TEAL + (170,), width=26, joint='curve')
    d.line([(w * .15, 0), (w * .35, h * .5), (w * .9, h)], fill=(255, 255, 255, 40), width=8)
    d.line([(0, h * .3), (w, h * .22)], fill=(255, 255, 255, 40), width=8)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 28, outline=(255, 255, 255, 60), width=2)
    c.put(layer, (x0, y0 + int((1 - p) * 40)), p)
    tt = c.T - t0 - .6
    if tt > 0:
        drop = max(0, 1 - tt / .5)
        bounce = abs(math.sin(tt * 9)) * 40 * math.exp(-tt * 3.5) if tt > .5 else 0
        py = y0 + h * .55 - drop * 260 - bounce
        for k in range(3):
            rp = ((tt * .8 + k / 3) % 1)
            rr = 30 + rp * 120
            c.d.ellipse([x0 + w / 2 - rr, y0 + h * .55 - rr * .35, x0 + w / 2 + rr, y0 + h * .55 + rr * .35], outline=COPPER + (int(160 * (1 - rp)),), width=3)
        img, pos = pin_icon(x0 + w / 2, py)
        c.put(img, pos)

def scene2(c):
    t = c.T - 10
    title(c, 1, 'التخطيط أولاً', 10)
    map_card(c, 480, 380, 11.0)
    chip(c, 130, 500, 'GPS', 12.0, TEAL)
    # sun / moon arc
    p = rv(t, 7.0, .6)
    if p > 0:
        cx, cy, rx, ry = W // 2, 1150, 380, 210
        pts = [(cx + rx * math.cos(math.pi * (1 - u / 60)), cy - ry * math.sin(math.pi * (1 - u / 60))) for u in range(61)]
        c.d.line(pts, fill=(255, 255, 255, int(60 * p)), width=3)
        names = ['شروق', 'ظهيرة', 'غروب', 'ليل']
        cols = [(255, 170, 80), (255, 225, 110), (255, 120, 60), (170, 200, 255)]
        for i in range(4):
            u = i / 3
            ang = math.pi * (1 - u)
            x, y = cx + rx * math.cos(ang), cy - ry * math.sin(ang)
            on = rv(t, 8.0 + i * 1.5, .5)
            a = p * (.35 + .65 * on)
            if on > 0:
                c.d.ellipse([x - 52, y - 52, x + 52, y + 52], outline=COPPER + (int(220 * on),), width=4)
            img, pos = sun_icon(x, y, cols[i], moon=(i == 3))
            c.put(img, pos, a)
            txt(c, y + 78, names[i], 28, WHITE, a, bold=False, x=x)
        gold = rv(t, 9.0, .5) * (1 - rv(t, 11.5, .4) * .0)
        for gx in (cx + rx * math.cos(math.pi), cx + rx * math.cos(math.pi * (1 - 2 / 3))):
            pass
        chip(c, 100, 1262, 'Golden Hour', 19.3, COPPER, 24)
    card(c, 1330, 'اعرف الموقع', '(طبيعة، مدن، استوديو)', 12.5 - 0.0)
    card(c, 1480, 'حدد التوقيت', '(ساعة ذهبية، ظهيرة حادة، ليل)', 14.2)

def scene3(c):
    t = c.T - 25
    title(c, 2, 'حدد هدفك', 25)
    pw, ph, px = 720, 480, 180
    imc = IM['creek_edit']
    crop = (1300 / 2576 * 2576, 0, 0, 0)
    # panels
    a1 = rv(t, 1.5, .7); a2 = rv(t, 2.5, .7)
    top, tv = box_view(imc, pw, ph, .5, .5, 1.0)
    # tele crop in image-space fractions
    cxf, cyf, zoom_t = .83, .43, 2.9
    z = ease((t - 4.0) / 3.5) if t < 12 else (1 - ease((t - 14.0) / 3.5)) if 14 <= t < 17.5 else (1 if t < 14 else 0)
    if 17.5 <= t < 19.0: z = 0
    if t >= 19.0: z = ease((t - 19.0) / 3.5) if t < 25 else 1 - ease((t - 25) / 3.5)
    bot, bv = box_view(imc, pw, ph, .5 + (cxf - .5) * z, .5 + (cyf - .5) * z, 1 + (zoom_t - 1) * z)
    if a1 > 0: rounded_paste(c.cv, top, px, 460 + int((1 - a1) * 40), 28, a1)
    if a2 > 0: rounded_paste(c.cv, bot, px, 965 + int((1 - a2) * 40), 28, a2)
    chip(c, px + 20, 480, 'WIDE  16–35mm', 27.0, TEAL)
    chip(c, px + 20, 985, 'TELE  70–200mm', 28.0, COPPER)
    # crop rectangle on the top panel showing the telephoto framing
    if t > 4.0 and z > 0:
        s_top = max(pw / imc.width, ph / imc.height)
        offx = (imc.width * s_top - pw) / 2; offy = (imc.height * s_top - ph) / 2
        _, (bx, by, bw, bh) = box_view(imc, pw, ph, cxf, cyf, zoom_t)
        rx0 = px + bx * s_top - offx; ry0 = 460 + by * s_top - offy
        c.d.rectangle([rx0, ry0, rx0 + bw * s_top, ry0 + bh * s_top], outline=COPPER + (int(255 * z),), width=4)
    if t > 12.5 and t < 14.0 or (17.5 <= t < 18.8):
        pass
    card(c, 1470, 'هل تبحث عن مشهد واسع؟', '(Landscape)', 29.5, h=92)
    card(c, 1572, 'أم عزل التفاصيل الدقيقة؟', '(Portrait / Details)', 35.0, h=92)

def card_item(c, x, scale, a, k, active, near=True):
    names = [('16–35mm', 'المناظر والمساحات', IM['creek_edit'], (.5, .5, 1.0)),
             ('24–70mm', 'الشارع والرحلات اليومية', IM['souk_raw'], (.5, .5, 1.0)),
             ('70–200mm', 'العزل والبورتريه', IM['abra_edit'], (.62, .62, 1.7))]
    nm, ar, im, (cx, cy, z) = names[k]
    cw, ch, ih = 520, 700, 430
    layer = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.rounded_rectangle([0, 0, cw - 1, ch - 1], 32, fill=(30, 30, 32, 255), outline=(COPPER if active else (255, 255, 255)) + (255 if active else 60,), width=5 if active else 2)
    ph, _ = box_view(im, cw - 36, ih, cx, cy, z)
    m = Image.new('L', ph.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, ph.width - 1, ph.height - 1], 22, fill=255)
    layer.paste(ph, (18, 18), m)
    if near:
        d.text((cw // 2, 515), nm, font=font(FB, 58), fill=COPPER + (255,), anchor='mm')
        ar_text(d, (cw // 2, 595), ar, font(FR, 34), (255, 255, 255, 255), 'mm')
    d.ellipse([cw // 2 - 8 - 40, 650, cw // 2 - 8 - 24, 666], fill=(255, 255, 255, 40))
    if scale != 1: layer = layer.resize((int(cw * scale), int(ch * scale)), Image.BICUBIC)
    c.put(layer, (x - layer.width / 2, 900 - layer.height / 2), a)

def scene4(c):
    t = c.T - 45
    title(c, 3, 'اختر عدستك بذكاء', 45)
    keys = [(0, 4.0), (1, 4.0), (2, 8.0), (1, 12.0)]
    # holds: idx 0 until 4.0, move to 1 (4.0-5.0) hold, to 2 (7.0-8.0) hold, back to 1 (10.0-11.5)
    if t < 4.0: pos = 0.0
    elif t < 5.0: pos = ease(t - 4.0)
    elif t < 7.0: pos = 1.0
    elif t < 8.0: pos = 1 + ease(t - 7.0)
    elif t < 10.0: pos = 2.0
    else: pos = 2 - ease((t - 10.0) / 1.5)
    appear = rv(t, 1.2, .8)
    for k in (0, 2, 1):
        dpos = k - pos
        dist = min(1, abs(dpos))
        scale = 1 - .3 * dist
        x = W // 2 + dpos * 640
        active = (abs(dpos) < .2) and t > 11.5
        card_item(c, x, scale, appear * (1 - .5 * dist), k, active, near=abs(dpos) < .6)
    for k in range(3):
        on = 1 - min(1, abs(k - pos))
        c.d.ellipse([W // 2 - 50 + k * 50 - 8 + 0, 1330 - 8, W // 2 - 50 + k * 50 + 8, 1330 + 8], fill=(COPPER if on > .5 else (255, 255, 255)) + (255 if on > .5 else 80,))
    if t > 11.5:
        g = rv(t, 11.5, .5)
        r = 44
        c.d.ellipse([W // 2 - r, 1250 - r, W // 2 + r, 1250 + r], fill=COPPER + (int(255 * g),))
        c.d.line([(W // 2 - 20, 1250), (W // 2 - 4, 1266), (W // 2 + 22, 1236)], fill=(18, 18, 18, int(255 * g)), width=9, joint='curve')
    txt(c, 1430, 'اترك العدسات الزائدة', 42, GREY, rv(t, 11.6, .6) * (1 - rv(t, 14.6, .4)), bold=False)
    txt(c, 1510, 'واعتمد على عدسة تلبي ٨٠٪ من احتياجك', 44, WHITE, rv(t, 12.3, .6) * (1 - rv(t, 14.6, .4)))

PAIRS = [('abra_raw', 'abra_edit', (.55, .6, 1.0)), ('creek_raw', 'creek_edit', (.5, .5, 1.0)), ('souk_raw', 'souk_bw', (.5, .5, 1.0))]

def scene5(c):
    t = c.T - 60
    title(c, 4, 'في المونتاج والتعديل', 60)
    pw, ph, px, py = 880, 640, 100, 480
    a = rv(t, 1.0, .7) * (1 - rv(t, 13.4, .5))
    seg = 3.8
    for i, (ra, ed, (cx, cy, z)) in enumerate(PAIRS):
        t0 = 1.8 + i * 3.9
        if not (t0 - .6 <= t < t0 + 3.9 + .1): continue
        local = t - t0
        al = a * (clamp((t - (t0 - .5)) / .5)) * (1 - clamp((t - (t0 + 3.4)) / .5) if i < 2 else 1)
        raw, _ = box_view(IM[ra], pw, ph, cx, cy, z)
        edit, _ = box_view(IM[ed], pw, ph, cx, cy, z)
        s = ease((local - .3) / 2.4)
        sx = int(pw * s)
        comp = raw.copy()
        if sx > 0: comp.paste(edit.crop((0, 0, sx, ph)), (0, 0))
        d2 = ImageDraw.Draw(comp)
        d2.line([(sx, 0), (sx, ph)], fill=(255, 255, 255), width=5)
        d2.ellipse([sx - 28, ph // 2 - 28, sx + 28, ph // 2 + 28], fill=(255, 255, 255))
        d2.polygon([(sx - 14, ph // 2), (sx - 4, ph // 2 - 10), (sx - 4, ph // 2 + 10)], fill=(18, 18, 18))
        d2.polygon([(sx + 14, ph // 2), (sx + 4, ph // 2 - 10), (sx + 4, ph // 2 + 10)], fill=(18, 18, 18))
        rounded_paste(c.cv, comp, px, py, 28, al)
        chip(c, px + 20, py + 18, 'RAW', 60 + t0, GREY)
        if s > .5: chip(c, px + pw - 190, py + 18, 'EDIT', 60 + t0 + 1.4, COPPER)
    card(c, 1180, 'لا تبالغ في التشبع والحدة', '(Saturation / Clarity)', 62.5, h=118)
    card(c, 1320, 'ركّز على الأساسيات', 'الإضاءة • التكوين • القص السليم', 65.5, h=118)
    card(c, 1460, 'الصورة الجميلة تبدأ من الميدان!', 'لا من الفلاتر', 68.5, h=118)

def scene6(c):
    t = c.T - 74
    p = rv(t, .3, .8)
    img, pos = lens_icon(W // 2, 600, 120, 1.0, c.T * 40, glow=.7)
    c.put(img, pos, p)
    txt(c, 840, 'الصورة الجميلة', 90, WHITE, rv(t, .8, .7), dy=int((1 - rv(t, .8, .7)) * 40))
    txt(c, 950, 'تبدأ من الميدان', 90, COPPER, rv(t, 1.4, .7), dy=int((1 - rv(t, 1.4, .7)) * 40))
    txt(c, 1060, 'لا من الفلاتر!', 56, WHITE, rv(t, 2.0, .7), bold=False)
    c.d.line([(W // 2 - 90, 1150), (W // 2 + 90, 1150)], fill=COPPER + (int(255 * rv(t, 2.4, .6)),), width=4)
    txt(c, 1250, 'احفظ الفيديو • شاركه • وعلّق برأيك', 38, GREY, rv(t, 3.0, .7), bold=False)
    a = rv(t, 3.6, .7)
    c.d.text((W // 2, 1370), 'Walidphotoz', font=font(FB, 54), fill=WHITE + (int(255 * a),), anchor='mm')

# ------------------------------------------------------------------ frame
def make_bg():
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * .8)) ** 2 + ((yy - H * .45) / (H * .75)) ** 2)
    v = (30 - 22 * np.clip(d, 0, 1)).astype(np.float32)
    arr = np.stack([v + 0, v + 0, v + 2], -1).clip(8, 34).astype(np.uint8)
    return Image.fromarray(arr)
bg_base = make_bg()

STEP_IN = {1: 10, 2: 25, 3: 45, 4: 60}
def render_frame(i):
    T = i / FPS
    c = Ctx(T)
    if T < 10: scene1(c)
    elif T < 25: scene2(c)
    elif T < 45: scene3(c)
    elif T < 60: scene4(c)
    elif T < 74: scene5(c)
    else: scene6(c)
    if 10 <= T < 74:
        step = 1 if T < 25 else 2 if T < 45 else 3 if T < 60 else 4
        progress(c, step, STEP_IN[step])
    out = c.cv.convert('RGBA'); out.alpha_composite(c.ov)
    out = out.convert('RGB')
    # scene transition dips
    for edge in (10, 25, 45, 60, 74):
        dd = abs(T - edge)
        if dd < .25:
            out = Image.blend(out, Image.new('RGB', (W, H), (18, 18, 18)), (1 - dd / .25) * .85)
    f = clamp(min(T / .4, (DUR - T) / .8))
    if f < 1: out = Image.blend(Image.new('RGB', (W, H), (0, 0, 0)), out, f)
    return out.tobytes()

# ------------------------------------------------------------------- audio
def synth(path):
    sr = 44100; n = int((DUR + 1) * sr)
    out = np.zeros(n, np.float32); rng = np.random.default_rng(3)
    def add(t, sig, g=1.):
        i = int(t * sr)
        if i >= n or i < 0: return
        sig = sig[:n - i]; out[i:i + len(sig)] += (sig * g).astype(np.float32)
    chords = [[130.8, 196, 246.9, 329.6], [110, 164.8, 261.6, 329.6], [87.3, 174.6, 261.6, 329.6], [98, 196, 293.7, 392]]
    tt = np.arange(int(6.4 * sr)) / sr
    env = np.minimum(1, np.minimum(tt / 1.5, (6.4 - tt) / 1.5)) ** 1.5
    for k, c0 in enumerate(range(0, int(DUR) + 1, 6)):
        sig = sum(np.sin(2 * np.pi * f * tt + .4 * np.sin(2 * np.pi * .25 * tt + j)) / (1 + j * .3) for j, f in enumerate(chords[k % 4])) * env
        add(c0, sig, .05)
    beat = 60 / 80
    def kick():
        m = int(.28 * sr); t2 = np.arange(m) / sr
        return np.sin(2 * np.pi * np.cumsum(110 * np.exp(-t2 * 14) + 42) / sr) * np.exp(-t2 * 9)
    def hat():
        m = int(.05 * sr); t2 = np.arange(m) / sr
        return np.diff(rng.standard_normal(m + 1))[:m] * np.exp(-t2 * 70)
    def tick(f=1500, d=.05):
        m = int(d * sr); t2 = np.arange(m) / sr
        return np.sin(2 * np.pi * f * t2) * np.exp(-t2 / (d / 4))
    def whoosh(d=.7):
        m = int(d * sr); t2 = np.arange(m) / sr
        nz = rng.standard_normal(m)
        for _ in range(3): nz = np.convolve(nz, np.ones(24) / 24, 'same')
        return nz * np.sin(np.pi * t2 / d) ** 2 * 4
    def shutter():
        m = int(.2 * sr); t2 = np.arange(m) / sr; s = np.zeros(m)
        for o in (0, .055):
            s += (t2 >= o) * np.diff(rng.standard_normal(m + 1))[:m] * np.exp(-(t2 - o) / .012)
        return s * .18
    t = 6.0
    while t < DUR - 3:
        lvl = 1.0 if t < DUR - 6 else .6
        add(t, kick(), .16 * lvl)
        add(t + beat / 2, hat(), .05 * lvl)
        if int((t - 6.0) / beat) % 2 == 1: add(t, hat(), .04 * lvl)
        t += beat
    add(.2, whoosh(.9), .5); add(2.4, tick(900, .12), .12); add(3.1, tick(1100, .1), .1)
    for e in (10, 25, 45, 60, 74): add(e - .25, whoosh(.6), .45)
    for tm in (11.6, 12.5, 14.2, 7.0 + 10 + 1.5 * 0, 18, 19.5, 21, 22.5): add(tm, tick(1400, .05), .07)
    add(35.0, tick(1300, .05), .07); add(29.5, tick(1300, .05), .07)
    for tm in (33.8, 36.3, 61.8): add(tm, shutter())
    for tm in (49.0, 52.0, 55.5): add(tm, whoosh(.5), .3)
    add(56.5, tick(2000, .1), .1); add(56.5, shutter())
    for tm in (62.5, 65.5, 68.5, 63.8, 67.5, 71.4): add(tm, tick(1300, .05), .07)
    for tm in (63.8, 67.7, 71.6): add(tm, whoosh(.6), .3)
    out *= np.minimum(1, np.minimum(np.arange(n) / (1.5 * sr), np.maximum(0, (DUR + .5 - np.arange(n) / sr)) / 3.0))
    out /= max(1e-6, np.abs(out).max()) / .8
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((out * 32767).astype(np.int16).tobytes())

def main():
    out = f'{HERE}/out'; os.makedirs(out, exist_ok=True)
    if '--preview' in sys.argv:
        pv = f'{HERE}/preview'; os.makedirs(pv, exist_ok=True)
        ts = [float(x) for x in sys.argv[sys.argv.index('--preview') + 1:]] or [4, 8, 13, 22, 30, 40, 52, 58, 64, 70, 77]
        for T in ts:
            Image.frombytes('RGB', (W, H), render_frame(int(T * FPS))).save(f'{pv}/L{T:05.1f}.jpg', quality=88)
        return
    synth(f'{out}/lens_audio.wav')
    N = int(DUR * FPS)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', f'{out}/_lens_v.mp4'], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, fr in enumerate(pool.imap(render_frame, range(N), chunksize=6)):
            p.stdin.write(fr)
            if i % 150 == 0: print(f'{i}/{N}', flush=True)
    p.stdin.close(); p.wait()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{out}/_lens_v.mp4', '-i', f'{out}/lens_audio.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    '-shortest', '-movflags', '+faststart', f'{out}/lens_guide_no_voiceover.mp4'], check=True)
    os.remove(f'{out}/_lens_v.mp4'); print('done')

if __name__ == '__main__':
    main()
