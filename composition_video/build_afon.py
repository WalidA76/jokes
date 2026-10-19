#!/usr/bin/env python3
"""Video 3 — AF-ON / Back-Button Focus explainer (76 s, 9:16, 1080x1920, 30 fps, no voice-over).

  python3 build_afon.py --preview [t ...]   # stills -> preview/
  python3 build_afon.py                     # full render (silent video + SFX) -> out/_afon_v.mp4, out/afon_sfx.wav
  python3 build_afon.py --mux               # mix with assets/music.mp3 -> out/afon_back_button_focus.mp4
"""
import math, os, sys, subprocess, wave
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import build_lens as L
from build_lens import (Ctx, rv, txt, chip, card, rounded_paste, box_view, ss, font, FB, FR, ease, clamp, ar_text,
                        COPPER, TEAL, WHITE, GREY, W, H, FPS, HERE)

DUR = 76.0
RED = (232, 40, 52)
GREEN = (64, 224, 110)
PANEL = (18, 18, 20)

def load(n): return Image.open(f'{HERE}/assets/{n}').convert('RGB')
IMG = dict(cam=load('afon_cam.png'), bird=load('afon_bird.png'), runner=load('afon_runner.png'),
           tripod=load('afon_tripod.png'), souk=load('lens_souk_raw.jpg'))

# ----------------------------------------------------------------- camera
BUTTONS = dict(afon=(740, 255, 34), ae=(815, 270, 32), afpt=(885, 295, 30))

def cam_layer(w, h, Z, fx, fy, glow=0.0, press=0.0, lcd=None, spot=1.0):
    """Vector Canon-style camera back. World 1000x820 -> panel (w,h), zoom Z around world point (fx,fy)."""
    def f(d, k):
        T = lambda x, y: ((w / 2 + (x - fx) * Z) * k, (h / 2 + (y - fy) * Z) * k)
        S = lambda r: r * Z * k
        def rr(x0, y0, x1, y1, r, fill=None, outline=None, wd=0):
            a, b = T(x0, y0), T(x1, y1)
            d.rounded_rectangle([a[0], a[1], b[0], b[1]], S(r), fill=fill, outline=outline, width=int(wd * k))
        def ci(x, y, r, fill=None, outline=None, wd=0):
            a = T(x, y); rr_ = S(r)
            d.ellipse([a[0] - rr_, a[1] - rr_, a[0] + rr_, a[1] + rr_], fill=fill, outline=outline, width=int(wd * k))
        rr(40, 120, 960, 780, 70, fill=(31, 31, 35, 255), outline=(255, 255, 255, int(90 * spot)), wd=3)
        # rim light on the top edge
        a, b = T(110, 122), T(890, 122)
        d.line([a, b], fill=(255, 140, 70, int(190 * spot)), width=int(4 * k))
        rr(330, 40, 650, 150, 36, fill=(28, 28, 31, 255), outline=(255, 255, 255, 40), wd=2)
        rr(350, 80, 650, 270, 44, fill=(14, 14, 16, 255), outline=(255, 255, 255, 36), wd=2)
        rr(425, 125, 575, 225, 28, fill=(8, 12, 22, 255), outline=(90, 110, 160, 90), wd=2)
        a = T(440, 140); b = T(500, 160)
        d.line([a, b], fill=(160, 190, 255, 70), width=int(5 * k))
        for i in range(6):                                   # grip texture
            for j in range(9):
                ci(780 + i * 26, 600 + j * 18 - 120, 2.2, fill=(255, 255, 255, 18))
        rr(170, 320, 710, 710, 24, fill=(12, 12, 14, 255), outline=(255, 255, 255, 40), wd=2)
        rr(190, 335, 690, 695, 10, fill=(5, 8, 14, 255))
        for i, y in enumerate((360, 430, 500, 570, 640)):    # left button column
            ci(105, y, 24, fill=(34, 34, 38, 255), outline=(255, 255, 255, 40), wd=2)
        ci(170, 235, 30, fill=(34, 34, 38, 255), outline=(255, 255, 255, 40), wd=2)
        ci(255, 235, 30, fill=(34, 34, 38, 255), outline=(255, 255, 255, 40), wd=2)
        for name, (x, y, r) in BUTTONS.items():
            rad = r * (1 - .08 * press if name == 'afon' else 1)
            if name == 'afon' and glow > 0:
                for i in range(5):
                    ci(x, y, rad + 6 + i * 6, outline=RED + (int(170 * glow * (1 - i / 5)),), wd=4)
                ci(x, y, rad, fill=(120 + int(110 * glow), 24, 30, 255), outline=RED + (255,), wd=3)
            else:
                ci(x, y, rad, fill=(36, 36, 41, 255), outline=(255, 255, 255, 60), wd=2)
        ci(770, 372, 46, fill=(30, 30, 34, 255), outline=(255, 255, 255, 50), wd=2)
        ci(770, 372, 20, fill=(18, 18, 20, 255))
        ci(790, 545, 126, fill=(26, 26, 29, 255), outline=(255, 255, 255, 55), wd=2)
        for i in range(40):
            ang = math.radians(i * 9)
            a = T(790 + 108 * math.cos(ang), 545 + 108 * math.sin(ang)); b = T(790 + 124 * math.cos(ang), 545 + 124 * math.sin(ang))
            d.line([a, b], fill=(255, 255, 255, 38), width=int(2 * k))
        ci(790, 545, 54, fill=(14, 14, 16, 255), outline=(255, 255, 255, 60), wd=2)
    return ss_wh(f, w, h)

def ss_wh(fn, w, h):
    Lr = Image.new('RGBA', (w * 2, h * 2), (0, 0, 0, 0))
    fn(ImageDraw.Draw(Lr), 2)
    return Lr.reduce(2)

def screen_of(w, h, Z, fx, fy, x, y): return (w / 2 + (x - fx) * Z, h / 2 + (y - fy) * Z)

_spot = None
def spotlight(w, h, a):
    global _spot
    if _spot is None:
        yy, xx = np.mgrid[0:h, 0:w]
        dist = np.sqrt(((xx - w * .55) / (w * .55)) ** 2 + ((yy - h * .15) / (h * .9)) ** 2)
        arr = np.zeros((h, w, 4), np.uint8); arr[..., :3] = (255, 150, 90)
        arr[..., 3] = (np.clip(1 - dist, 0, 1) ** 1.6 * 90).astype(np.uint8)
        _spot = Image.fromarray(arr, 'RGBA')
    s = _spot.copy(); s.putalpha(s.getchannel('A').point(lambda v: int(v * a)))
    return s

def scene_tag(c, num, ar, t0, t1):
    a = rv(c.T, t0, .5) * (1 - rv(c.T, t1, .4))
    if a <= 0: return
    f = font(FB, 30)
    c.d.text((W // 2 - 4, 262), f'{num}', font=font(FB, 40), fill=COPPER + (int(255 * a),), anchor='rm')
    ar_text(c.d, (W // 2 + 14, 262), ar, font(FB, 38), (255, 255, 255, int(235 * a)), 'lm')
    c.d.line([(W // 2 - 70, 300), (W // 2 + 70, 300)], fill=COPPER + (int(180 * a),), width=3)

# ------------------------------------------------------------- scene 1
def scene1(c):
    t = c.T
    x0, y0, pw, ph = 100, 440, 880, 700
    fade_all = 1 - rv(t, 15.4, .5)
    cam_a = rv(t, .8, 1.2)
    z = ease((t - 2.5) / 2.5)
    Z = .88 + (3.4 - .88) * z
    fx = 500 + (BUTTONS['afon'][0] - 500) * z
    fy = 430 + (BUTTONS['afon'][1] - 430) * z
    press = clamp((t - 5.0) / .15) * (1 - clamp((t - 5.5) / .3)) if t >= 5.0 else 0
    glow = rv(t, 5.0, .4) * (.75 + .25 * math.sin(t * 6)) if t >= 5.0 else 0
    if t > .4:
        layer = Image.new('RGBA', (pw, ph), PANEL + (255,))
        layer.alpha_composite(spotlight(pw, ph, rv(t, .5, 1.2)))
        cam = cam_layer(pw, ph, Z, fx, fy, glow=glow, press=press, spot=rv(t, .8, 1.2))
        cam.putalpha(cam.getchannel('A').point(lambda v: int(v * cam_a)))
        layer.alpha_composite(cam)
        mask = Image.new('L', (pw, ph), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph - 1], 32, fill=int(255 * fade_all))
        c.ov.paste(layer, (x0, y0), mask)
        c.d.rounded_rectangle([x0, y0, x0 + pw - 1, y0 + ph - 1], 32, outline=(255, 255, 255, int(50 * fade_all)), width=2)
        # HUD brackets
        ha = rv(t, 2.0, .6) * fade_all
        for sx, sy, dx, dy in ((x0 + 24, y0 + 24, 1, 1), (x0 + pw - 24, y0 + 24, -1, 1), (x0 + 24, y0 + ph - 24, 1, -1), (x0 + pw - 24, y0 + ph - 24, -1, -1)):
            c.d.line([(sx, sy + dy * 44), (sx, sy), (sx + dx * 44, sy)], fill=WHITE + (int(180 * ha),), width=4)
        if t > 5.2:
            bx, by = screen_of(pw, ph, Z, fx, fy, *BUTTONS['afon'][:2])
            a = rv(t, 5.3, .4) * fade_all
            chip(c, x0 + bx + 70, y0 + by - 28, 'AF-ON', 5.3, RED, 34)
    # kinetic type (phase A)
    a1 = rv(t, 5.6, .5) * (1 - rv(t, 7.4, .4))
    txt(c, 1280, 'AF-ON', 110, WHITE, a1, dy=int((1 - a1) * 30))
    txt(c, 1405, '= Back-Button Focusing', 56, COPPER, rv(t, 6.2, .5) * (1 - rv(t, 7.4, .4)))
    # phase B: shutter button splits
    pB = rv(t, 7.6, .5) * (1 - rv(t, 13.0, .4))
    if pB > 0:
        sp = ease((t - 8.4) / 1.4)
        cx, cy, r = W // 2, 1330, 92
        def half(sign, glyph):
            ox = sign * 210 * sp
            arc0, arc1 = (90, 270) if sign < 0 else (-90, 90)
            pts = [(cx + ox + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
                   for a in np.linspace(arc0, arc1, 40)]
            c.d.line(pts + [pts[0]], fill=COPPER + (int(255 * pB),), width=7, joint='curve')
            gx = cx + ox + sign * 36
            if glyph == 'focus':
                for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                    c.d.line([(gx + dx * 26, cy + dy * 12), (gx + dx * 26, cy + dy * 26), (gx + dx * 12, cy + dy * 26)] if False else
                             [(gx + dx * 14, cy + dy * 26), (gx + dx * 26, cy + dy * 26), (gx + dx * 26, cy + dy * 14)], fill=WHITE + (int(255 * pB),), width=5)
            else:
                c.d.ellipse([gx - 22, cy - 22, gx + 22, cy + 22], outline=WHITE + (int(255 * pB),), width=5)
                c.d.ellipse([gx - 6, cy - 6, gx + 6, cy + 6], fill=WHITE + (int(255 * pB),))
        half(-1, 'focus'); half(1, 'capture')
        if sp > 0:
            c.d.line([(cx, cy - r - 12), (cx, cy + r + 12)], fill=COPPER + (int(150 * (1 - sp) * pB),), width=3)
        lab = rv(t, 9.6, .5) * pB
        txt(c, 1490, 'FOCUS', 44, WHITE, lab, x=cx - 210)
        txt(c, 1540, 'التركيز البؤري', 34, GREY, lab, bold=False, x=cx - 210)
        txt(c, 1490, 'CAPTURE', 44, WHITE, lab, x=cx + 210)
        txt(c, 1540, 'التقاط الصورة', 34, GREY, lab, bold=False, x=cx + 210)
        txt(c, 1610, 'زر الغالق التقليدي يجمع الوظيفتين', 36, COPPER, rv(t, 10.4, .5) * pB, bold=False)
    # phase C
    pC = rv(t, 13.2, .5) * fade_all
    txt(c, 1300, 'AF-ON', 76, WHITE, pC)
    txt(c, 1420, 'عزل قرار الفوكس', 62, COPPER, rv(t, 13.6, .5) * fade_all)
    txt(c, 1510, 'عن لحظة الالتقاط', 62, WHITE, rv(t, 14.1, .5) * fade_all)

# ------------------------------------------------------------- LCD menu
MENU_L1 = ['Warnings in viewfinder', 'LV shooting area display', 'Dial direction during Tv/Av', 'Multi function lock', 'Custom Controls']
MENU_L2 = [('Shutter button', 'Metering and AF start'), ('AF-ON button', 'Metering start'), ('AE lock button', 'AE lock'), ('SET button', 'Quick Control')]

def lcd_menu(w, h, level, sel, values=None, flash=0.0, strike=None):
    im = Image.new('RGBA', (w, h), (28, 29, 33, 255)); d = ImageDraw.Draw(im)
    tabs = ['SHOOT', 'AF', 'PLAY', 'SET', 'C.Fn', 'MY']
    tw = w // len(tabs)
    for i, n in enumerate(tabs):
        on = (n == 'C.Fn')
        d.rectangle([i * tw, 0, (i + 1) * tw, 78], fill=(COPPER if on else (44, 45, 50)) + (255,))
        d.text((i * tw + tw // 2, 40), n, font=font(FB, 26), fill=((18, 18, 18) if on else (200, 200, 205)) + (255,), anchor='mm')
    rows = MENU_L1 if level == 1 else [r[0] for r in MENU_L2]
    rh = 84
    for i, r in enumerate(rows):
        y = 96 + i * rh
        on = (i == sel)
        d.rounded_rectangle([14, y, w - 14, y + rh - 10], 12, fill=(COPPER + (255,)) if on else (40, 41, 46, 255))
        d.text((34, y + (rh - 10) // 2), r, font=font(FB, 31), fill=((18, 18, 18) if on else (235, 235, 238)) + (255,), anchor='lm')
        if level == 2:
            val = (values or [v for _, v in MENU_L2])[i]
            d.text((w - 34, y + (rh - 10) // 2), val, font=font(FR, 27), fill=((18, 18, 18) if on else (255, 170, 100)) + (255,), anchor='rm')
            if strike is not None and strike == i:
                tw2 = font(FR, 27).getlength(val)
                d.line([(w - 34 - tw2, y + 34), (w - 34, y + 34)], fill=(18, 18, 18, 255), width=3)
        elif on:
            d.text((w - 34, y + 36), '›', font=font(FB, 40), fill=(18, 18, 18, 255), anchor='rm')
    if flash > 0:
        im.alpha_composite(Image.new('RGBA', (w, h), (255, 255, 255, int(70 * flash))))
    return im

# ------------------------------------------------------------- scene 2
def scene2(c):
    t = c.T
    scene_tag(c, '02', 'الضبط داخل قوائم كانون', 16.0, 36.0)
    # A) the user's reference photo: MENU -> tab -> Custom Controls
    a = rv(t, 16.5, .6) * (1 - rv(t, 21.6, .45))
    if a > 0:
        im = IMG['cam'].resize((700, int(700 * IMG['cam'].height / IMG['cam'].width)), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(2, 80, 2))
        y = 520 + int((1 - a) * 40)
        rounded_paste(c.cv, im, (W - im.width) // 2, y, 24, a)
        for i, (lab, tt) in enumerate((('1  MENU', 17.4), ('2  ⚙  C.Fn', 18.6), ('3  Custom Controls', 19.8))):
            chip(c, 190, 520 + im.height + 40 + i * 62, lab, tt, COPPER, 30)
    # B) menu mock
    pw, ph = 880, 520
    b = rv(t, 22.0, .6) * (1 - rv(t, 29.0, .5))
    if b > 0:
        if t < 24.8: level, sel = 1, min(4, int(max(0, t - 22.4) / .4))
        else: level = 2
        values = [v for _, v in MENU_L2]
        strike = None
        sel2 = 0 if t < 27.0 else 1
        if level == 2:
            if t < 26.2: values[0] = 'Metering and AF start'
            elif t < 26.7: values[0] = 'Metering and AF start'; strike = 0
            else: values[0] = 'Metering start'
            if t < 28.0: values[1] = 'Metering start' if t < 27.8 else 'Metering start'
            else: values[1] = 'Metering and AF start'
        fl = 0.0
        if 24.8 <= t < 25.0: fl = 1 - (t - 24.8) / .2
        lcd = lcd_menu(pw, ph, level, sel if level == 1 else sel2, values, fl, strike)
        mask = Image.new('L', (pw, ph), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph - 1], 24, fill=int(255 * b))
        c.cv.paste(lcd.convert('RGB'), (100, 520 + int((1 - b) * 40)), mask)
        c.d.rounded_rectangle([100, 520, 100 + pw - 1, 520 + ph - 1], 24, outline=COPPER + (int(150 * b),), width=3)
        chip(c, 120, 462, 'C.Fn  ›  Customize Buttons' if level == 2 else 'C.Fn  ›  Custom Controls', 22.6, COPPER, 26)
        if level == 2 and t >= 26.2: card(c, 1110, 'Shutter button', 'Metering start  (بدون تركيز)', 26.3, h=112)
        if level == 2 and t >= 28.0: card(c, 1250, 'AF-ON button', 'Metering and AF start', 28.2, h=112)
    # C) workflow lanes
    p = rv(t, 29.4, .6) * (1 - rv(t, 35.6, .4))
    if p > 0:
        lx, lw = 150, 780
        ph_t = clamp((t - 30.2) / 4.8)                      # playhead 0..1
        lanes = [('AF-ON  (الإبهام)', 620), ('FOCUS  (التركيز)', 800), ('SHUTTER  (السبابة)', 980)]
        press_end = .55
        for name, y in lanes:
            txt(c, y - 64, name, 32, WHITE, p, bold=True, x=W // 2)
            c.d.rounded_rectangle([lx, y - 30, lx + lw, y + 30], 18, fill=(255, 255, 255, int(20 * p)))
        # lane 1: pressed segment then released
        c.d.rounded_rectangle([lx, 590, lx + int(lw * press_end), 650], 18, fill=COPPER + (int(230 * p),))
        # lane 2: tracking (green dots) then locked
        for i in range(14):
            x = lx + 30 + i * (lw * press_end - 40) / 13
            if (x - lx) / lw <= ph_t:
                c.d.ellipse([x - 9, 800 - 9 + 8 * math.sin(i * 1.7 + t * 5), x + 9, 800 + 9 + 8 * math.sin(i * 1.7 + t * 5)], fill=GREEN + (int(255 * p),))
        lk = lx + lw * press_end
        if ph_t > press_end:
            c.d.rounded_rectangle([lk + 14, 772, lx + lw - 10, 828], 16, fill=RED + (int(220 * p),))
            c.d.text(((lk + lx + lw) / 2, 800), 'LOCKED', font=font(FB, 28), fill=WHITE + (int(255 * p),), anchor='mm')
        # lane 3: shutter clicks
        for tx in (.18, .34, .7, .86):
            x = lx + lw * tx
            if ph_t >= tx:
                c.d.ellipse([x - 14, 966, x + 14, 994], fill=WHITE + (int(255 * p),))
        # playhead
        px = lx + lw * ph_t
        c.d.line([(px, 530), (px, 1040)], fill=WHITE + (int(200 * p),), width=3)
        card(c, 1180, 'إبهامك على AF-ON = تتبع (AI Servo)', None, 30.6, h=104)
        card(c, 1310, 'رفعت إبهامك؟ الفوكس مقفول فوراً', None, 32.6, h=104)
        card(c, 1440, 'سبابتك حرّة تماماً لالتقاط اللحظة', None, 34.0, h=104)

# ------------------------------------------------------------- viewfinder
def viewfinder(c, x0, y0, pw, ph, a, info, af_on=True, thirds=True):
    for sx, sy, dx, dy in ((x0 + 22, y0 + 22, 1, 1), (x0 + pw - 22, y0 + 22, -1, 1), (x0 + 22, y0 + ph - 22, 1, -1), (x0 + pw - 22, y0 + ph - 22, -1, -1)):
        c.d.line([(sx, sy + dy * 40), (sx, sy), (sx + dx * 40, sy)], fill=WHITE + (int(220 * a),), width=4)
    if thirds:
        for i in (1, 2):
            c.d.line([(x0 + pw * i / 3, y0 + 14), (x0 + pw * i / 3, y0 + ph - 14)], fill=(255, 255, 255, int(46 * a)), width=2)
            c.d.line([(x0 + 14, y0 + ph * i / 3), (x0 + pw - 14, y0 + ph * i / 3)], fill=(255, 255, 255, int(46 * a)), width=2)
    c.d.rounded_rectangle([x0 + 22, y0 + ph - 78, x0 + pw - 22, y0 + ph - 26], 10, fill=(0, 0, 0, int(150 * a)))
    c.d.text((x0 + 42, y0 + ph - 52), info, font=font(FB, 26), fill=WHITE + (int(255 * a),), anchor='lm')
    col = RED if af_on else (90, 90, 95)
    c.d.ellipse([x0 + pw - 210, y0 + ph - 66, x0 + pw - 186, y0 + ph - 42], fill=col + (int(255 * a),))
    c.d.text((x0 + pw - 176, y0 + ph - 54), 'AF-ON', font=font(FB, 22), fill=WHITE + (int(255 * a),), anchor='lm')

def focus_box(c, cx, cy, size, col, a, locked=False, label=None):
    s = size
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        px, py = cx + sx * s, cy + sy * s
        c.d.line([(px, py - sy * s * .45), (px, py), (px - sx * s * .45, py)], fill=col + (int(255 * a),), width=6)
    if locked:
        c.d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=col + (int(255 * a),))
    if label: c.d.text((cx, cy - s - 24), label, font=font(FB, 26), fill=col + (int(255 * a),), anchor='mm')

def panel_img(c, im, x, y, w, h, a, cx=.5, cy=.5, z=1.0):
    v, box = box_view(im, w, h, cx, cy, z)
    rounded_paste(c.cv, v, x, y, 28, a)
    return box

def img_to_panel(box, w, h, ix, iy):
    bx, by, bw, bh = box
    return ((ix - bx) / bw * w, (iy - by) / bh * h)

# ------------------------------------------------------------- scene 3
def scene3(c):
    t = c.T
    scene_tag(c, '03', 'من يحتاج هذا الزر؟', 36.0, 64.0)
    x0, y0, pw, ph = 100, 440, 880, 740
    # 1) bird  38 -> 45.5
    if 37.6 <= t < 46.0:
        a = rv(t, 37.8, .5) * (1 - rv(t, 45.5, .4))
        lt = t - 38
        box = panel_img(c, IMG['bird'], x0, y0, pw, ph, a, .5, .45, 1.0)
        ex, ey = img_to_panel(box, pw, ph, 411, 237)
        cx, cy = x0 + ex, y0 + ey
        # foreground branches sweeping across the eye
        sw = ease((lt - 2.0) / 3.0)
        if 1.6 < lt < 5.4:
            for i in range(3):
                bxs = x0 + pw + 160 - sw * (pw + 520) + i * 120
                pts = [(bxs + 90, y0 + 20), (bxs - 70, y0 + ph - 90)]
                c.d.line(pts, fill=(10, 10, 12, int(235 * a)), width=34 - i * 8)
        covering = 2.7 < lt < 4.6
        focus_box(c, cx, cy, 44, RED if covering else GREEN, a, locked=covering, label='LOCK' if covering else 'AI SERVO')
        viewfinder(c, x0, y0, pw, ph, a, '1/2000  F5.6  ISO 800', af_on=not covering)
        if covering: chip(c, x0 + 30, y0 + 40, '↑  رفعت إبهامي', 38 + 2.7, COPPER, 28)
        if lt > 5.3 and lt < 6.8 and int((lt - 5.3) * 12) % 2 == 0:
            c.ov.alpha_composite(Image.new('RGBA', (pw, ph), (255, 255, 255, 30)), dest=(x0, y0))
        if lt > 5.3: chip(c, x0 + pw - 250, y0 + 40, 'BURST  12 fps', 38 + 5.3, TEAL, 28)
        card(c, 1240, 'مصورو الحياة البرية والطيور', 'الفوكس يبقى على العين رغم الأغصان', 38.8, h=118)
        card(c, 1380, 'لا يقفز الفوكس إلى الغصن', 'رفعتَ إبهامك لحظة مروره', 41.0, h=118)
    # 2) runner 45.5 -> 53
    if 45.1 <= t < 53.4:
        a = rv(t, 45.3, .5) * (1 - rv(t, 52.9, .4))
        lt = t - 45.5
        z = 1.0 + .22 * ease(lt / 6.5)
        box = panel_img(c, IMG['runner'], x0, y0, pw, ph, a, .42 + .08 * ease(lt / 6.5), .6, z)
        rx, ry = img_to_panel(box, pw, ph, 130 + 8 * lt, 150)
        cx, cy = x0 + rx, y0 + ry
        for i in range(10):                                # AF-point trail
            tt = lt - i * .12
            if tt > 0:
                px, py = img_to_panel(box, pw, ph, 130 + 8 * tt, 150)
                c.d.rectangle([x0 + px - 8, y0 + py - 8, x0 + px + 8, y0 + py + 8], outline=GREEN + (int(220 * a * (1 - i / 11)),), width=3)
        focus_box(c, cx, cy, 70, GREEN, a, label='CONTINUOUS TRACKING')
        viewfinder(c, x0, y0, pw, ph, a, '1/4000  F4  ISO 400', af_on=True)
        card(c, 1240, 'مصورو الرياضة والحركة', 'تتبّع مستمر للهدف المتحرك', 46.2, h=118)
        card(c, 1380, 'الإبهام ثابت على AF-ON', 'والسبابة جاهزة للرشق', 48.6, h=118)
    # 3) street / portrait  53 -> 59
    if 52.9 <= t < 59.4:
        a = rv(t, 53.1, .5) * (1 - rv(t, 59.0, .4))
        lt = t - 53.5
        shift = ease((lt - 2.0) / 1.8) * .10
        box = panel_img(c, IMG['souk'], x0, y0, pw, ph, a, .5 - shift + .0, .5, 1.12)
        mx, my = img_to_panel(box, pw, ph, 1290, 700)
        cx, cy = x0 + pw / 2 + (0 if lt < 2.0 else 0), y0 + ph / 2 - 40
        if lt < 2.0:
            focus_box(c, x0 + mx, y0 + my, 80, GREEN, a, label='AI SERVO')
        else:
            focus_box(c, cx, cy, 80, RED, a, locked=True, label='FOCUS LOCK')
            c.d.rounded_rectangle([x0 + 40, y0 + 120, x0 + 40 + 300, y0 + 168], 10, fill=(0, 0, 0, int(170 * a)))
            c.d.text((x0 + 56, y0 + 144), 'DISTANCE  3.2 m  🔒'.replace('🔒', '•'), font=font(FB, 24), fill=RED + (int(255 * a),), anchor='lm')
            if lt < 4.0: chip(c, x0 + pw - 270, y0 + 40, 'RECOMPOSE', 55.5, COPPER, 28)
        viewfinder(c, x0, y0, pw, ph, a, '1/500  F2.8  ISO 200', af_on=lt < 2.0)
        card(c, 1240, 'مصورو البورتريه والشارع', 'اقفل الفوكس ثم أعد التكوين', 54.0, h=118)
        card(c, 1380, 'الهدف لا يتغير موضعه في العمق', None, 57.0, h=104)
    # 4) tripod / non-essential  59 -> 64
    if 58.9 <= t < 64.2:
        a = rv(t, 59.1, .5) * (1 - rv(t, 63.8, .4))
        im = IMG['tripod'].resize((pw, int(pw * IMG['tripod'].height / IMG['tripod'].width)), Image.LANCZOS)
        rounded_paste(c.cv, im, x0, 470, 28, a)
        chip(c, x0 + 24, 490, 'TRIPOD', 59.6, GREY, 28)
        card(c, 470 + im.height + 40, 'من لا يحتاجه بالضرورة؟', 'اللاندسكيب • المنتجات • الاستوديو', 59.8, h=118)
        pa = rv(t, 61.0, .6) * (1 - rv(t, 63.8, .4))
        yb = 470 + im.height + 190
        c.d.rounded_rectangle([x0, yb, x0 + pw, yb + 230], 28, fill=(255, 255, 255, int(22 * pa)), outline=COPPER + (int(220 * pa),), width=3)
        ar_text(c.d, (W // 2, yb + 78), 'إذا كان هدفك ثابتاً والكاميرا على الترايبود..', font(FB, 36), WHITE + (int(255 * pa),), 'mm')
        ar_text(c.d, (W // 2, yb + 150), 'فزر الغالق التقليدي يؤدي الغرض تماماً', font(FB, 38), COPPER + (int(255 * pa),), 'mm')

# ------------------------------------------------------------- scene 4
def iris(img, p):
    """close aperture: p 0..1 (1 = fully closed)."""
    if p <= 0: return img
    cx, cy = W / 2, H / 2
    R = (1 - ease(p)) * 1100
    mask = Image.new('L', (W, H), 255)
    if R > 4:
        pts = [(cx + R * math.cos(math.radians(a + 90 / 7)), cy + R * math.sin(math.radians(a + 90 / 7))) for a in np.linspace(0, 360, 8)[:-1]]
        ImageDraw.Draw(mask).polygon(pts, fill=0)
    black = Image.new('RGB', (W, H), (0, 0, 0))
    inv = Image.eval(mask, lambda v: 255 - v)
    out = Image.composite(img, black, inv) if R > 4 else black
    return out

def scene4(c):
    t = c.T
    snap = ease((t - 64.0) / .9)
    # photos collapse
    if t < 65.4:
        a = 1 - rv(t, 64.3, .6)
        tiles = [('bird', -1, -1), ('runner', 1, -1), ('souk', -1, 1), ('tripod', 1, 1)]
        for k, sx, sy in tiles:
            im = IMG[k]
            tw = 400; th = int(tw * im.height / im.width)
            sc = 1 - .75 * snap
            tim = im.resize((max(2, int(tw * sc)), max(2, int(th * sc))), Image.BICUBIC)
            px = W // 2 + sx * (270 * (1 - snap)) - tim.width // 2
            py = 640 + sy * (300 * (1 - snap)) - tim.height // 2
            rounded_paste(c.cv, tim, px, py, 18, a * .85)
    # camera
    cw, ch = 880, 560
    zz = 1.7 - .8 * snap
    if t > 64.4:
        cam = cam_layer(cw, ch, zz * .52 + .4, 500, 420, glow=rv(t, 66, .5) * .9, spot=1.0)
        cam.putalpha(cam.getchannel('A').point(lambda v: int(v * rv(t, 64.4, .5))))
        c.ov.alpha_composite(cam, dest=(100, 400))
    words = [('دقة أعلى', 'Precision', 66.0), ('سرعة استجابة', 'Speed', 67.4), ('تحكم مطلق', 'Total Control', 68.8)]
    for i, (ar, en, t0) in enumerate(words):
        p = rv(t, t0, .5)
        if p <= 0: continue
        y = 1090 + i * 150 + int((1 - p) * 40)
        c.d.rounded_rectangle([140, y, W - 140, y + 124], 26, fill=(255, 255, 255, int(20 * p)), outline=COPPER + (int(200 * p),), width=3)
        ar_text(c.d, (W - 190, y + 50), ar, font(FB, 52), WHITE + (int(255 * p),), 'rm')
        c.d.text((190, y + 62), en, font=font(FB, 38), fill=COPPER + (int(255 * p),), anchor='lm')
    txt(c, 1600, 'AF-ON  =  Back-Button Focusing', 34, GREY, rv(t, 70.0, .6) * (1 - rv(t, 72.4, .4)), bold=False)
    a = rv(t, 70.3, .7) * (1 - rv(t, 72.4, .4))
    c.d.text((W // 2, 1680), 'Walidphotoz', font=font(FB, 52), fill=WHITE + (int(255 * a),), anchor='mm')

# ------------------------------------------------------------- frame
def render_frame(i):
    T = i / FPS
    c = Ctx(T)
    if T < 16: scene1(c)
    elif T < 36: scene2(c)
    elif T < 64.4: scene3(c)
    else: scene4(c)
    out = c.cv.convert('RGBA'); out.alpha_composite(c.ov); out = out.convert('RGB')
    for edge in (16, 36, 64.4):
        dd = abs(T - edge)
        if dd < .22 and edge != 64.4:
            out = Image.blend(out, Image.new('RGB', (W, H), (18, 18, 18)), (1 - dd / .22) * .9)
    if 36 <= T < 36.4:
        pass
    f = clamp(T / .5)
    if f < 1: out = Image.blend(Image.new('RGB', (W, H), (0, 0, 0)), out, f)
    if T > 72.6: out = iris(out, (T - 72.6) / 2.4)
    return out.tobytes()

# ------------------------------------------------------------------ audio
def synth_sfx(path):
    sr = 44100; n = int((DUR + 1) * sr)
    out = np.zeros(n, np.float32); rng = np.random.default_rng(11)
    def add(t, sig, g=1.):
        i = int(t * sr)
        if i >= n or i < 0: return
        sig = sig[:n - i]; out[i:i + len(sig)] += (sig * g).astype(np.float32)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{HERE}/assets/shutter.mp3', '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'], capture_output=True, check=True).stdout
    sh = np.frombuffer(raw, np.float32).copy(); sh /= max(1e-6, np.abs(sh).max())
    def tt(d): return np.arange(int(d * sr)) / sr
    def bass_drop():
        t2 = tt(1.6); f = 120 * np.exp(-t2 * 2.2) + 32
        return np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t2 * 1.6)
    def tactile():
        t2 = tt(.12)
        nz = np.convolve(rng.standard_normal(len(t2)), np.ones(8) / 8, 'same')
        return (np.sin(2 * np.pi * 180 * t2) * np.exp(-t2 / .02) + nz * np.exp(-t2 / .012) * .6)
    def beep(f=2700, d=.09):
        t2 = tt(d); return np.sin(2 * np.pi * f * t2) * np.minimum(1, t2 / .005) * np.minimum(1, (d - t2) / .01)
    def tick(f=3200, d=.025):
        t2 = tt(d); return np.sin(2 * np.pi * f * t2) * np.exp(-t2 / (d / 4))
    def whoosh(d=.7):
        t2 = tt(d); nz = rng.standard_normal(len(t2))
        for _ in range(3): nz = np.convolve(nz, np.ones(24) / 24, 'same')
        return nz * np.sin(np.pi * t2 / d) ** 2 * 4
    def servo(d=.7):
        t2 = tt(d); f = 260 + 520 * np.sin(np.pi * t2 / d)
        s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / sr)) * .35 + np.sin(2 * np.pi * np.cumsum(f * 2) / sr) * .2
        return np.convolve(s, np.ones(6) / 6, 'same') * np.sin(np.pi * t2 / d) ** .6
    def chime():
        t2 = tt(.5); return (np.sin(2 * np.pi * 1318 * t2) + .5 * np.sin(2 * np.pi * 1975 * t2)) * np.exp(-t2 * 7)
    add(.3, bass_drop(), .5); add(1.0, whoosh(1.0), .4); add(2.5, whoosh(.9), .4)
    add(5.0, tactile(), .35); add(5.35, sh, .8); add(5.5, beep(), .22)
    add(7.8, whoosh(.7), .35); add(8.4, whoosh(.9), .3); add(13.2, tick(), .25)
    add(16.0, whoosh(.6), .4); add(17.4, tick(), .25); add(18.6, tick(), .25); add(19.8, tick(), .25)
    add(21.8, whoosh(.5), .35)
    for k in range(5): add(22.4 + k * .4, tick(), .3)
    add(24.8, chime(), .22); add(26.3, chime(), .2); add(28.2, chime(), .2)
    add(26.0, tick(2200), .3); add(27.0, tick(), .25)
    add(30.2, servo(1.2), .3); add(31.8, beep(2700, .07), .15); add(33.5, tactile(), .3)
    for tx in (.18, .34, .7, .86): add(30.2 + 4.8 * tx, sh, .35)
    add(35.9, whoosh(.5), .35)
    add(37.6, whoosh(.5), .3); add(40.7, beep(2700, .07), .18); add(43.3, beep(2700, .07), .18)
    for k in range(14): add(43.3 + k * .085, sh, .55)
    add(45.2, whoosh(.5), .3)
    for k in range(10): add(48.6 + k * .1, sh, .45)
    add(46.0, servo(1.5), .2)
    add(52.9, whoosh(.5), .3); add(55.5, beep(2700, .09), .25); add(55.5, tactile(), .3); add(57.6, sh, .8)
    add(58.9, whoosh(.5), .3)
    add(64.0, bass_drop(), .45); add(64.0, whoosh(.9), .5)
    for t0 in (66.0, 67.4, 68.8): add(t0, chime(), .22)
    for k in range(8): add(72.6 + k * .3, tick(1800, .03), .2)
    add(75.0, sh, .9)
    out *= np.minimum(1, np.maximum(0, (DUR + .5 - np.arange(n) / sr)) / 1.0)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())

def main():
    out = f'{HERE}/out'; os.makedirs(out, exist_ok=True)
    if '--preview' in sys.argv:
        pv = f'{HERE}/preview'; os.makedirs(pv, exist_ok=True)
        ts = [float(x) for x in sys.argv[sys.argv.index('--preview') + 1:]] or [1.5, 4, 6, 9, 14, 18, 24, 27, 33, 40, 49, 56, 61, 68, 74]
        for T in ts:
            Image.frombytes('RGB', (W, H), render_frame(int(T * FPS))).save(f'{pv}/A{T:05.1f}.jpg', quality=88)
        return
    if '--mux' in sys.argv:
        m = f'{HERE}/assets/music.mp3'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{out}/_afon_v.mp4', '-i', m, '-i', f'{out}/afon_sfx.wav', '-filter_complex',
            f'[1:a]atrim=0:{DUR},asetpts=PTS-STARTPTS,afade=t=in:d=1.5,afade=t=out:st={DUR-3.5}:d=3.5,volume=0.85[mu];[2:a]volume=0.95[fx];[mu][fx]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]',
            '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', str(DUR), '-movflags', '+faststart', f'{out}/afon_back_button_focus.mp4'], check=True)
        return
    synth_sfx(f'{out}/afon_sfx.wav')
    N = int(DUR * FPS)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', f'{out}/_afon_v.mp4'], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, fr in enumerate(pool.imap(render_frame, range(N), chunksize=6)):
            p.stdin.write(fr)
            if i % 150 == 0: print(f'{i}/{N}', flush=True)
    p.stdin.close(); p.wait(); print('done')

if __name__ == '__main__':
    main()
