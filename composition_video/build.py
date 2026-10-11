#!/usr/bin/env python3
"""Photography-composition motion graphic (9:16, 1080x1920, 30fps, ~105s).

All analysis graphics are re-drawn as vector layers over the ORIGINAL photos
(coordinates traced from the reference analysis images). The whole timeline
lives in the SCENES / SUBS tables below, so it is easy to retime or edit.

  python3 build.py --preview      # stills of key moments -> preview/
  python3 build.py                # full render -> out/*.mp4
"""
import math, os, sys, subprocess, wave
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, SS = 1080, 1920, 30, 2
DUR = 105.0
BG = (11, 12, 16)

COL = dict(red=(255, 48, 48), yellow=(255, 230, 0), cyan=(0, 229, 255), green=(37, 230, 90),
           orange=(255, 149, 28), pink=(239, 53, 220), white=(255, 255, 255),
           blue=(40, 150, 255), purple=(176, 112, 255))

FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(p, s): return ImageFont.truetype(p, s)

# ----------------------------------------------------------------- helpers
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(p):
    p = clamp(p)
    return 4 * p ** 3 if p < .5 else 1 - (-2 * p + 2) ** 3 / 2

def smooth(pts, n=24):
    if len(pts) < 3: return list(pts)
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            out.append(tuple(.5 * ((2 * p1[a]) + (-p0[a] + p2[a]) * t +
                                   (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * t * t +
                                   (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * t ** 3) for a in (0, 1)))
    out.append(pts[-1])
    return out

def cum(pts):
    d = [0.]
    for a, b in zip(pts, pts[1:]): d.append(d[-1] + math.dist(a, b))
    return d

def partial(pts, p):
    d = cum(pts); tgt = d[-1] * p
    out = [pts[0]]
    for i in range(1, len(pts)):
        if d[i] <= tgt: out.append(pts[i])
        else:
            f = (tgt - d[i - 1]) / max(d[i] - d[i - 1], 1e-9)
            out.append((pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f,
                        pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f))
            break
    return out

def dense(pts, step):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / step))
        for j in range(1, n + 1):
            out.append((a[0] + (b[0] - a[0]) * j / n, a[1] + (b[1] - a[1]) * j / n))
    return out

def rect_pts(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]

# ------------------------------------------------------------ element model
class E:
    def __init__(s, kind, start, dur=1.0, color='white', hl=None, **kw):
        s.kind, s.start, s.dur, s.color, s.hl = kind, start, dur, color, hl
        s.__dict__.update(kw)

def circ(cx, cy, rx, ry=None): return (cx, cy, rx, ry or rx)

class Scene:
    def __init__(s, key, t0, t1, ref_w, ref_h, img, chip, chip_ar, els, zoom):
        s.key, s.t0, s.t1, s.chip, s.chip_ar, s.els, s.zoom = key, t0, t1, chip, chip_ar, els, zoom
        im = Image.open(f'{HERE}/assets/{img}').convert('RGB')
        s.h = round(im.height * W / im.width)
        s.img = im.resize((W, s.h), Image.LANCZOS)
        s.k = W / ref_w
        s.s = min(1.0, 1530 / s.h)
        s.y0 = int(112 + (1530 - s.h * s.s) / 2)
        s.sprites = {}

# ------------------------------------------------------------------ scenes
VES = [
    E('circle', 4.3, 1.6, 'red', hl=0, c=circ(541, 1006, 328, 318)),
    E('label', 5.9, color='red', lines=['Main Subject', 'Vespa Scooter', '(Blue vs Red Contrast)'], tl=(450, 1332), anchors=[(550, 1324)]),
    E('circle', 9.2, 1.4, 'yellow', c=circ(543, 310, 204, 205)),
    E('dash', 10.2, 1.2, 'yellow', pts=rect_pts(318, 56, 766, 664)),
    E('label', 10.9, color='yellow', lines=['Secondary Subject', 'Window (Repeating Rectangle)'], tl=(422, 53)),
    E('arrow', 11.7, 1.6, 'yellow', hl=1, pts=smooth([(543, 312), (520, 450), (560, 600), (612, 690)]), heads=1),
    E('grid', 14.2, 1.4, 'white', hl=3, vs=[322, 765], hs=[476, 955]),
    E('arrow', 15.6, 1.5, 'cyan', hl=2, pts=[(838, 12), (838, 1055)], heads=0),
    E('arrow', 17.0, .8, 'cyan', pts=[(838, 1050), (1075, 1048)], heads=1),
    E('circle', 16.0, .6, 'green', c=circ(838, 52, 30, 50)),
    E('circle', 16.4, .6, 'green', c=circ(838, 360, 40)),
    E('circle', 17.4, .6, 'green', c=circ(855, 1055, 38)),
    E('label', 16.9, color='green', lines=['Vertical Pipe', '(Leading Line)'], tl=(892, 316), anchors=[(878, 360)]),
    E('label', 17.9, color='green', lines=['Pipe Bend', '(Visual Turn)'], tl=(880, 1082), anchors=[(862, 1085)]),
    E('dash', 18.4, .9, 'pink', pts=rect_pts(146, 880, 284, 1017)),
    E('label', 19.0, color='pink', lines=['Repeating Rectangle', '(Top Case)'], tl=(60, 795), anchors=[(190, 880)]),
    E('circle', 19.6, .9, 'orange', c=circ(640, 790, 100, 105)),
    E('label', 20.3, color='orange', lines=['Windshield & Mirrors', '(Detail / Interest)'], tl=(711, 686), anchors=[(700, 750)]),
    E('arrow', 20.2, 1.0, 'pink', pts=[(275, 908), (618, 792)], heads=2),
    E('label', 20.8, color='pink', lines=['Diagonal Line', '(Connects Elements)'], tl=(357, 756), anchors=[(445, 850)]),
    E('circle', 20.8, .8, 'blue', c=circ(450, 1000, 135, 55)),
    E('label', 21.4, color='blue', lines=['Seat', '(Color Echo with Frame)'], tl=(347, 892)),
    E('dash', 21.4, 1.4, 'white', pts=rect_pts(20, 293, 296, 713)),
    E('label', 22.6, color='white', lines=['Negative Space', '(Plain Red Wall)'], tl=(80, 421)),
    E('arrow', 23.2, 1.4, 'yellow', pts=smooth([(810, 825), (880, 935), (1065, 945)]), heads=1),
    E('arrow', 24.8, .9, 'white', pts=[(232, 1190), (15, 1195)], heads=1),
    E('arrow', 24.8, .9, 'white', pts=[(895, 1168), (1087, 1168)], heads=1),
    E('label', 25.4, color='white', lines=['Wall-Floor Boundary', '(Horizontal Line)'], tl=(14, 1130)),
]
BRI = [
    E('arrow', 5.2, 1.8, 'cyan', hl=1, pts=[(0, 1250), (540, 836)], heads=0),
    E('arrow', 5.4, 1.8, 'cyan', hl=1, pts=[(1122, 1285), (575, 838)], heads=0),
    E('label', 6.9, color='cyan', lines=['Leading Lines', 'Bridge'], tl=(30, 1300), anchors=[(90, 1205)]),
    E('arrow', 7.6, 1.8, 'yellow', pts=[(540, 1300), (553, 850)], heads=1),
    E('label', 9.2, color='yellow', lines=["Viewer's Eye Path", '(Bridge → Village → Peak)'], tl=(458, 1253)),
    E('circle', 12.3, 1.3, 'red', hl=0, c=circ(560, 255, 95)),
    E('arrow', 13.2, 2.2, 'yellow', hl=2, pts=smooth([(553, 850), (590, 790), (612, 690), (600, 560), (582, 420), (574, 262)]), heads=1),
    E('label', 14.6, color='red', lines=['Main Focal Point', 'Mountain Peak'], tl=(650, 100), anchors=[(592, 178)]),
    E('arrow', 15.4, 1.8, 'green', pts=smooth([(632, 300), (655, 400), (700, 475), (780, 535), (860, 595), (960, 638), (1122, 688)]), heads=0),
    E('label', 16.8, color='green', lines=['Leading Line', 'Mountain Slope'], tl=(826, 465), anchors=[(765, 525)]),
    E('circle', 18.2, .6, 'orange', c=circ(617, 662, 26)),
    E('circle', 18.6, .6, 'orange', c=circ(862, 708, 25)),
    E('circle', 19.0, .6, 'orange', c=circ(1017, 726, 25)),
    E('label', 19.4, color='orange', lines=['Warm Street Lights'], tl=(805, 640), anchors=[(643, 662), (862, 683), (1017, 701)]),
    E('circle', 19.8, 1.1, 'yellow', c=circ(432, 672, 110, 82)),
    E('label', 20.8, color='yellow', lines=['Warm Color Accent', 'Houses'], tl=(310, 500), anchors=[(432, 590)]),
    E('circle', 21.4, .7, 'blue', c=circ(135, 1055, 42)),
    E('circle', 21.7, .7, 'blue', c=circ(866, 1022, 42)),
    E('label', 22.2, color='blue', lines=['Reflection', 'in Water'], tl=(40, 940), anchors=[(130, 1013)]),
    E('label', 22.5, color='blue', lines=['Reflection', 'in Water'], tl=(985, 1060), anchors=[(905, 1035)]),
    E('dash', 23.0, 1.0, 'purple', pts=smooth([(912, 870), (925, 790), (960, 752), (1010, 742), (1122, 752)])),
    E('label', 23.8, color='purple', lines=['Balancing Rock', '(Secondary Element)'], tl=(930, 835), anchors=[(1040, 790)]),
    E('dash', 24.3, 1.5, 'white', pts=[(12, 15), (1108, 15), (1108, 430), (700, 430), (650, 370), (630, 290), (600, 195), (582, 172), (540, 205), (490, 270), (460, 340), (445, 362), (300, 360), (230, 330), (120, 298), (12, 282), (12, 15)]),
    E('label', 25.6, color='white', lines=['Negative Space', '(Gradient Sky)'], tl=(40, 60)),
    E('grid', 26.2, 1.3, 'white', hl=3, vs=[351, 770], hs=[467, 935]),
]
POR = [
    E('circle', 5.2, 1.5, 'red', hl=0, c=circ(412, 1035, 172)),
    E('label', 6.7, color='red', lines=['Main Subject', '(Porter / Journey)'], tl=(105, 1026), anchors=[(244, 1075)]),
    E('circle', 7.4, .8, 'orange', c=circ(425, 927, 40)),
    E('label', 8.3, color='orange', lines=['Detail Highlight', "(Porter's Face)"], tl=(560, 872), anchors=[(465, 927)]),
    E('glow', 9.3, 1.0, 'orange', c=circ(405, 995, 105, 135)),
    E('circle', 12.2, 1.3, 'yellow', c=circ(410, 330, 122, 76)),
    E('label', 13.3, color='yellow', lines=['Secondary Focal Point', '(Mountain Peak)'], tl=(375, 150), anchors=[(410, 254)]),
    E('arrow', 14.0, 2.0, 'yellow', hl=1, pts=smooth([(415, 858), (412, 640), (408, 408)]), heads=2),
    E('label', 15.7, color='blue', lines=['Scale', '(Small Human vs', 'Huge Mountain)'], tl=(45, 483), anchors=[(230, 568)]),
    E('arrow', 16.2, 1.6, 'cyan', pts=smooth([(500, 296), (560, 322), (620, 356), (670, 385), (700, 425), (740, 470), (790, 510), (850, 532), (920, 552), (1026, 585)]), heads=0),
    E('label', 17.6, color='cyan', lines=['Leading Line', '(Mountain Ridge)'], tl=(800, 420), anchors=[(790, 508)]),
    E('arrow', 18.2, 1.4, 'pink', hl=2, pts=[(15, 1488), (700, 1135)], heads=1),
    E('label', 19.5, color='pink', lines=['Diagonal Line', '(Leading to Subject)'], tl=(88, 1285), anchors=[(292, 1345)]),
    E('circle', 19.8, 1.2, 'green', c=circ(790, 1195, 158, 135)),
    E('label', 20.9, color='green', lines=['Element Highlight', '(Foreground Grass)'], tl=(775, 990), anchors=[(790, 1060)]),
    E('label', 21.5, color='orange', lines=['Warm Colors', '(Golden Grass)'], tl=(852, 1376), anchors=[(815, 1413)]),
    E('circle', 21.8, .8, 'blue', c=circ(808, 215, 75)),
    E('label', 22.5, color='blue', lines=['Blue Sky', '(Color Contrast)'], tl=(836, 70), anchors=[(832, 165)]),
    E('arrow', 22.8, 1.2, 'white', pts=smooth([(0, 770), (120, 790), (250, 815), (380, 835), (470, 800), (540, 760), (620, 737), (700, 735), (750, 765), (800, 828), (870, 810), (940, 780), (1026, 765)]), heads=0),
    E('label', 23.7, color='white', lines=['Cloud Line', '(Separates Subject', 'from Mountain)'], tl=(853, 850), anchors=[(800, 828)]),
    E('grid', 24.2, 1.3, 'white', hl=3, vs=[342, 684], hs=[511, 1021]),
    E('dash', 25.4, 1.4, 'white', pts=rect_pts(15, 15, 1010, 270)),
    E('label', 26.6, color='white', lines=['Negative Space', '(Clear Blue Sky)'], tl=(473, 45)),
    E('dash', 26.0, 1.2, 'white', pts=rect_pts(15, 845, 1010, 985)),
    E('label', 27.1, color='white', lines=['Negative Space', '(Clouds / Atmosphere)'], tl=(55, 870)),
]
# zoom: (start_scale, anchor_x, anchor_y, end_anchor_x, end_anchor_y, seconds)
SCENES = [
    Scene('ves', 8, 37, 1087, 1447, 'vespa.jpg', '01 — COLOR & SHAPES', 'التباين اللوني والأشكال', VES, (1.14, .52, .66, .52, .55, 4.2)),
    Scene('bri', 37, 67, 1122, 1402, 'bridge.jpg', '02 — LEADING LINES', 'الخطوط القائدة', BRI, (1.16, .50, .88, .52, .25, 5.0)),
    Scene('por', 67, 97, 1026, 1532, 'porter.jpg', '03 — SCALE & JOURNEY', 'المقياس وقصة الرحلة', POR, (1.14, .45, .65, .45, .45, 4.8)),
]

# --------------------------------------------------------- narration/subtitles
SUBS = [
    (.4, 3.6, 'ليش بعض الصور تجذب عينك من أول نظرة؟'),
    (3.6, 8.0, 'السر مو دائماً في الكاميرا أو المكان… السر في طريقة ترتيب عناصر الصورة!'),
    (8, 12, 'شوف هالصورة… دراجة زرقاء، جدار أحمر، ونافذة بسيطة. لكن توزيع العناصر هنا هو اللي يصنع قوة المشهد.'),
    (12, 17, 'الدراجة هي العنصر الرئيسي، والتباين بين الأزرق الداكن والأحمر يخليها تبرز مباشرة.'),
    (17, 22, 'النافذة تضيف عنصراً ثانوياً يوازن التكوين، وتخلق علاقة بصرية مع الدراجة.'),
    (22, 29, 'لاحظ الخطوط المستقيمة في النافذة والأنبوب، وكيف تتكرر الأشكال المستطيلة، بينما تضيف المرايا والزجاج أشكالاً منحنية تكسر الجمود.'),
    (29, 37, 'حتى الجدار الفارغ له دور مهم… يعطي العناصر مساحة تتنفس فيها، ويمنع ازدحام الصورة.'),
    (37, 42, 'في الصورة الثانية، المصور استخدم واحداً من أقوى أساليب التكوين… الخطوط القائدة.'),
    (42, 49, 'حواف الجسر تسحب عينك من مقدمة الصورة إلى القرية، وتخلق إحساساً واضحاً بالعمق.'),
    (49, 55, 'ومن القرية ترتفع عينك نحو قمة الجبل، وهي نقطة الجذب الأساسية في المشهد.'),
    (55, 61, 'الإضاءة الدافئة في البيوت والمصابيح تتباين مع برودة السماء، وانعكاساتها تضيف تفاصيل جميلة للمشهد.'),
    (61, 67, 'أما السماء الهادئة، فتعطي الجبل مساحة بصرية وتساعد على إبراز شكله.'),
    (67, 72, 'الصورة الثالثة تحكي قصة رحلة، وتستخدم اختلاف الأحجام لتعطيك إحساساً بعظمة المكان.'),
    (72, 79, 'المتسلق هو بطل القصة، ووجوده أمام الجبل الضخم يعطيك إحساساً بالمقياس وصعوبة الرحلة.'),
    (79, 85, 'الجبل هنا مو مجرد خلفية… هو عنصر رئيسي في القصة، ويصنع علاقة قوية بين الإنسان والطبيعة.'),
    (85, 91, 'الخط المائل في المقدمة يضيف حركة، والأعشاب الذهبية تصنع تبايناً مع الثلج الأبيض والسماء الزرقاء.'),
    (91, 97, 'والمساحات الهادئة بين العناصر تخلي المشهد واضحاً، رغم ضخامة التفاصيل.'),
    (97, 105, 'التصوير مو بس توثيق مشهد… التصوير فن توجيه عين المشاهد. وكل ما فهمت التكوين، صارت صورك أقوى.'),
]

# ------------------------------------------------------------- drawing core
def shadow_line(d, pts, w):
    d.line(pts, fill=(0, 0, 0, 110), width=int(w + 5 * SS), joint='curve')

def draw_stroke(d, pts, col, w, shadow=True):
    if len(pts) < 2: return
    if shadow: shadow_line(d, pts, w)
    d.line(pts, fill=col + (255,), width=int(w), joint='curve')
    r = w / 2
    for q in (pts[0], pts[-1]):
        d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=col + (255,))

def arrowhead(d, tip, frm, col, size):
    ang = math.atan2(tip[1] - frm[1], tip[0] - frm[0])
    pts = [tip,
           (tip[0] - size * math.cos(ang - .42), tip[1] - size * math.sin(ang - .42)),
           (tip[0] - size * .62 * math.cos(ang), tip[1] - size * .62 * math.sin(ang)),
           (tip[0] - size * math.cos(ang + .42), tip[1] - size * math.sin(ang + .42))]
    d.polygon(pts, fill=col + (255,))

def draw_element(d, e, t, K, lwm, sc):
    """Draw one non-label element at time t onto SS-scale overlay draw d."""
    p = ease((t - e.start) / e.dur)
    if p <= 0: return
    col = COL[e.color]
    w = 4.2 * SS * lwm
    M = lambda q: (q[0] * K, q[1] * K)
    if e.kind == 'circle':
        cx, cy, rx, ry = e.c
        N = max(6, int(150 * p))
        pts = [((cx + rx * math.cos(-math.pi / 2 + 2 * math.pi * p * i / N)) * K,
                (cy + ry * math.sin(-math.pi / 2 + 2 * math.pi * p * i / N)) * K) for i in range(N + 1)]
        draw_stroke(d, pts, col, w)
    elif e.kind == 'glow':
        cx, cy, rx, ry = e.c
        bb = [(cx - rx) * K, (cy - ry) * K, (cx + rx) * K, (cy + ry) * K]
        pulse = .75 + .25 * math.sin(t * 4)
        d.ellipse(bb, fill=col + (int(60 * p * pulse),))
    elif e.kind == 'arrow':
        pts = [M(q) for q in e.pts]
        part = partial(pts, p)
        draw_stroke(d, part, col, w)
        hs = 30 * SS * max(1, lwm * .75)
        if e.heads >= 1 and p > .02 and len(part) >= 2:
            back = part[-2] if math.dist(part[-1], part[-2]) > 2 else part[max(0, len(part) - 6)]
            arrowhead(d, part[-1], back, col, hs)
        if e.heads == 2 and p > .02:
            arrowhead(d, part[0], part[min(len(part) - 1, 5)] if len(part) > 5 else part[-1], col, hs)
    elif e.kind == 'dash':
        pts = dense([M(q) for q in e.pts], 5 * SS)
        tgt = cum(pts)[-1] * p
        dd, gp = 16 * SS, 11 * SS
        acc = 0.
        for a, b in zip(pts, pts[1:]):
            seg = math.dist(a, b)
            if acc + seg > tgt: break
            if (acc % (dd + gp)) < dd:
                d.line([a, b], fill=(0, 0, 0, 100), width=int(w * .8 + 4 * SS))
                d.line([a, b], fill=col + (255,), width=int(w * .8))
            acc += seg
    elif e.kind == 'grid':
        end = e.start + e.dur
        a = 1.0 if t < end else 1.0 - .6 * ease((t - end) / 1.0)
        c = (255, 255, 255, int(255 * a * .9))
        wid = int(2.2 * SS * max(1, lwm * .6))
        for i, x in enumerate(e.vs):
            pp = ease((t - e.start - i * .15) / (e.dur * .75))
            d.line([(x * K, 0), (x * K, sc.h * SS * pp)], fill=c, width=wid)
        for i, y in enumerate(e.hs):
            pp = ease((t - e.start - .3 - i * .15) / (e.dur * .75))
            d.line([(0, y * K), (W * SS * pp, y * K)], fill=c, width=wid)
        for x in e.vs:
            for y in e.hs:
                if p > .9:
                    r = 5 * SS
                    d.ellipse([x * K - r, y * K - r, x * K + r, y * K + r], fill=(255, 255, 255, int(c[3])))

def label_sprite(sc, e):
    key = id(e)
    if key in sc.sprites: return sc.sprites[key]
    f1, f2 = font(FB, 22), font(FR, 19)
    col = COL[e.color]
    tw = [f1.getlength(e.lines[0])] + [f2.getlength(s) for s in e.lines[1:]]
    pad = 13
    lh1, lh2 = 28, 25
    w = int(max(tw) + 2 * pad + 2)
    h = int(pad * 2 - 4 + lh1 + lh2 * (len(e.lines) - 1))
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 7, fill=(12, 12, 15, 220), outline=col + (255,), width=3)
    y = pad - 4
    d.text((pad, y), e.lines[0], font=f1, fill=(255, 255, 255, 255)); y += lh1
    for s in e.lines[1:]:
        d.text((pad, y), s, font=f2, fill=(232, 232, 232, 255)); y += lh2
    x = e.tl[0] * sc.k; yy = e.tl[1] * sc.k
    x = clamp(x, 8, W - 8 - w); yy = clamp(yy, 8, sc.h - 8 - h)
    sc.sprites[key] = (im, int(x), int(yy))
    return sc.sprites[key]

def draw_leader(d, sc, e, t):
    im, x, y = label_sprite(sc, e)
    p = ease((t - e.start) / .35)
    col = COL[e.color]
    for a in getattr(e, 'anchors', []) or []:
        ax, ay = a[0] * sc.k, a[1] * sc.k
        nx, ny = clamp(ax, x, x + im.width), clamp(ay, y, y + im.height)
        if math.dist((ax, ay), (nx, ny)) < 3: continue
        q = (nx + (ax - nx) * p, ny + (ay - ny) * p)
        S = lambda z: (z[0] * SS, z[1] * SS)
        d.line([S((nx, ny)), S(q)], fill=(0, 0, 0, 110), width=int(5 * SS))
        d.line([S((nx, ny)), S(q)], fill=col + (255,), width=int(2.4 * SS))
        if p > .95:
            r = 6 * SS
            d.ellipse([ax * SS - r, ay * SS - r, ax * SS + r, ay * SS + r], fill=col + (255,))

def zoom_img(sc, t):
    z0, ax0, ay0, ax1, ay1, secs = sc.zoom
    p = ease(t / secs)
    s = z0 + (1 - z0) * p
    ax, ay = ax0 + (ax1 - ax0) * p, ay0 + (ay1 - ay0) * p
    if s <= 1.0005: return sc.img
    cw, ch = W / s, sc.h / s
    x = clamp(ax * W - cw / 2, 0, W - cw); y = clamp(ay * sc.h - ch / 2, 0, sc.h - ch)
    return sc.img.resize((W, sc.h), Image.BICUBIC, box=(x, y, x + cw, y + ch))

def scene_layer(sc, t, mode='full', tc=0., lwm=1.0):
    """Return RGB image (W x sc.h) of the scene at local time t."""
    first = min(e.start for e in sc.els)
    base = zoom_img(sc, t) if mode == 'full' else sc.img
    dim = ease((t - (first - .4)) / .8) if mode == 'full' else 1
    if dim > 0:
        base = Image.blend(Image.new('RGB', base.size, (0, 0, 0)), base, 1 - .16 * dim)
    ovl = Image.new('RGBA', (W * SS, sc.h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(ovl)
    K = sc.k * SS
    labels = []
    if mode == 'full':
        for e in sorted(sc.els, key=lambda x: x.kind != 'glow'):
            if e.kind == 'label':
                if t >= e.start: draw_leader(d, sc, e, t); labels.append(e)
            else:
                draw_element(d, e, t, K, lwm, sc)
    else:  # closing highlights: tc = seconds since this tile began drawing
        for e in sc.els:
            if e.hl is None or e.kind == 'label': continue
            ee = E(e.kind, .45 * e.hl, .9, e.color, **{k: v for k, v in e.__dict__.items() if k not in ('kind', 'start', 'dur', 'color', 'hl')})
            ee.hl = e.hl
            if ee.kind == 'grid': ee.dur = .9
            draw_element(d, ee, tc, K, lwm, sc)
    im = base.convert('RGBA')
    im.alpha_composite(ovl.reduce(SS))
    for e in labels:
        spr, x, y = label_sprite(sc, e)
        p = ease((t - e.start) / .3)
        s = .9 + .1 * p
        sp = spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BICUBIC)
        a = sp.getchannel('A').point(lambda v: int(v * p))
        sp.putalpha(a)
        im.alpha_composite(sp, dest=(x + (spr.width - sp.width) // 2, y + (spr.height - sp.height) // 2))
    return im.convert('RGB')

# --------------------------------------------------------- text / chrome
_grad = None
def bg_canvas():
    global _grad
    if _grad is None:
        a = np.linspace(0, 1, H)[:, None, None]
        top, bot = np.array([20, 24, 34]), np.array([8, 9, 12])
        _grad = (top * (1 - a) + bot * a).astype(np.uint8) * np.ones((1, W, 1), np.uint8)
    return Image.fromarray(_grad.copy())

def ar_text(d, xy, text, f, fill, anchor='ma'):
    d.text(xy, text, font=f, fill=fill, anchor=anchor, direction='rtl', language='ar')

def wrap_ar(text, f, maxw):
    words, lines, cur = text.split(' '), [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if f.getlength(trial, direction='rtl', language='ar') <= maxw or not cur: cur = trial
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

_band = None
def subtitle_overlay(img, t):
    global _band
    for s0, s1, txt in SUBS:
        if s0 <= t < s1:
            a = clamp(min((t - s0) / .25, (s1 - t) / .25))
            f = font(FR, 46)
            lines = wrap_ar(txt, f, 940)
            y0 = 1840 - len(lines) * 66
            if _band is None:
                g = np.zeros((H, W, 4), np.uint8); g[..., 3] = 0
                for i in range(220): g[H - 220 + i, :, 3] = int(185 * (i / 220) ** .8)
                _band = Image.fromarray(g, 'RGBA')
            band = _band.copy()
            band.putalpha(band.getchannel('A').point(lambda v: int(v * a)))
            img = img.convert('RGBA'); img.alpha_composite(band)
            d = ImageDraw.Draw(img)
            for i, ln in enumerate(lines):
                ar_text(d, (W // 2 + 2, y0 + i * 66 + 2), ln, f, (0, 0, 0, int(200 * a)))
                ar_text(d, (W // 2, y0 + i * 66), ln, f, (255, 255, 255, int(255 * a)))
            return img.convert('RGB')
    return img

def cover(im, scale=1.0, ax=.5, ay=.5):
    s = max(W / im.width, H / im.height) * scale
    w, h = im.width * s, im.height * s
    x = clamp(ax * w - W / 2, 0, w - W); y = clamp(ay * h - H / 2, 0, h - H)
    return im.resize((W, H), Image.BICUBIC, box=(x / s, y / s, (x + W) / s, (y + H) / s))

def thirds(d, prog, alpha):
    c = (255, 255, 255, int(255 * alpha))
    for x in (W // 3, 2 * W // 3): d.line([(x, 0), (x, H * prog)], fill=c, width=2)
    for y in (H // 3, 2 * H // 3): d.line([(0, y), (W * prog, y)], fill=c, width=2)

def text_c(d, y, s, f, fill, anchor='mm'):
    d.text((W // 2, y), s, font=f, fill=fill, anchor=anchor)

def flash(img, a):
    if a <= 0: return img
    return Image.blend(img, Image.new('RGB', img.size, (255, 255, 255)), clamp(a))

# --------------------------------------------------------------- frame logic
def opening(t):
    shots = [('vespa.jpg', .6, 1.9, (.5, .6)), ('bridge.jpg', 1.9, 3.2, (.5, .45)), ('porter.jpg', 3.2, 8.0, (.5, .5))]
    cur = None
    for name, a, b, anc in shots:
        if t >= a: cur = (name, a, b, anc)
    if t < .6 or cur is None: return Image.new('RGB', (W, H), (0, 0, 0)), 0
    name, a, b, anc = cur
    im = Image.open(f'{HERE}/assets/{name}').convert('RGB')
    z = 1 + .12 * ease((t - a) / (b - a if name != 'porter.jpg' else 2.0))
    img = cover(im, z, *anc)
    dark = .0 if t < 4.0 else .62 * ease((t - 4.0) / 1.0)
    img = Image.blend(img, Image.new('RGB', (W, H), (0, 0, 0)), dark)
    fl = max(0, .55 - (t - a) * 6) if t - a < .1 else 0
    if t < 8: fl = max(fl, 0)
    return flash(img, fl), dark

def render_opening(t):
    img, _ = opening(t)
    img = img.convert('RGBA')
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    if 5.0 <= t < 7.8:
        a = .55 * min(1, (7.8 - t) / 1.0)
        thirds(d, ease((t - 5.0) / 1.3), a)
    if t >= 4.4:
        a = ease((t - 4.4) / .8)
        a2 = a * clamp((8.0 - t) / .5)
        dy = int((1 - a) * 24)
        text_c(d, 760 + dy, 'THE ART OF', font(FB, 74), (255, 255, 255, int(255 * a2)))
        text_c(d, 850 + dy, 'COMPOSITION', font(FB, 96), (255, 255, 255, int(255 * a2)))
        ln = ease((t - 5.0) / .9)
        x0 = W // 2 - 220 * ln
        d.line([(x0, 925), (W - x0, 925)], fill=COL['yellow'] + (int(255 * a2),), width=5)
        if t > 5.6:
            b = ease((t - 5.6) / .7) * clamp((8.0 - t) / .5)
            ar_text(d, (W // 2, 990 + int((1 - b) * 20)), 'كيف تقرأ الصورة؟', font(FR, 66), (255, 230, 0, int(255 * b)), 'mm')
    img.alpha_composite(ov)
    return img.convert('RGB')

def chrome(img, sc, t):
    d = ImageDraw.Draw(img, 'RGBA')
    a = clamp((t - .3) / .5)
    d.rounded_rectangle([40, 44, 40 + font(FB, 28).getlength(sc.chip) + 40, 94], 12, fill=(255, 255, 255, int(24 * a)), outline=(255, 255, 255, int(70 * a)), width=2)
    d.text((60, 69), sc.chip, font=font(FB, 28), fill=(255, 255, 255, int(255 * a)), anchor='lm')
    ar_text(d, (W - 44, 69), sc.chip_ar, font(FR, 32), (255, 230, 0, int(255 * a)), 'rm')

def render_scene(sc, T):
    t = T - sc.t0
    lay = scene_layer(sc, t)
    img = bg_canvas()
    a = clamp(min(t / .5, (sc.t1 - T) / .4))
    if sc.s < 1: lay = lay.resize((int(W * sc.s), int(sc.h * sc.s)), Image.LANCZOS)
    x = (W - lay.width) // 2
    reg = img.crop((x, sc.y0, x + lay.width, sc.y0 + lay.height))
    img.paste(Image.blend(reg, lay, a), (x, sc.y0))
    chrome(img, sc, t)
    return flash(img, .5 - t * 6 if t < .08 else 0)

TRI = {'ves': 0, 'bri': 1, 'por': 2}
def render_closing(T):
    t = T - 97.0
    img = bg_canvas()
    cw = 336; gap = 16; x0 = (W - (3 * cw + 2 * gap)) // 2
    for i, sc in enumerate(SCENES):
        ta = .5 + .7 * i
        a = ease((t - ta) / .6)
        if a <= 0: continue
        lay = scene_layer(sc, 0, mode='close', tc=max(0, t - ta - .4), lwm=2.4)
        th = int(cw * sc.h / W)
        tile = lay.resize((cw, th), Image.LANCZOS)
        x = x0 + i * (cw + gap); y = 560 + int((1 - a) * 40) + (510 - th) // 2
        reg = img.crop((x, y, x + cw, y + th))
        img.paste(Image.blend(reg, tile, a), (x, y))
        if t - ta < .08: img = flash(img, .35 - (t - ta) * 4)
    d = ImageDraw.Draw(img, 'RGBA')
    if t >= 3.6:
        a = ease((t - 3.6) / .8)
        dy = int((1 - a) * 24)
        text_c(d, 1250 + dy, "DON'T JUST TAKE A PHOTO.", font(FB, 56), (255, 255, 255, int(255 * a)))
        text_c(d, 1330 + dy, 'COMPOSE IT.', font(FB, 92), (255, 230, 0, int(255 * a)))
        ar_text(d, (W // 2, 1450 + dy), 'لا تلتقط الصورة فقط… اصنع تكوينها.', font(FR, 52), (255, 255, 255, int(235 * a)), 'mm')
    end = clamp((DUR - T) / .6)
    if end < 1: img = Image.blend(Image.new('RGB', (W, H), (0, 0, 0)), img, end)
    return img

def render_frame(i):
    T = i / FPS
    if T < 8:
        img = render_opening(T)
        if 7.4 <= T:  # fade into scene 1 handled by scene's own fade-in
            pass
    elif T < 97:
        sc = next(s for s in SCENES if s.t0 <= T < s.t1)
        img = render_scene(sc, T)
    else:
        img = render_closing(T)
    if T >= 7.5 and T < 8.0:  # quick dip so the opening hands over cleanly
        pass
    clean = img
    subs = subtitle_overlay(clean.copy(), T)
    return clean.tobytes(), subs.tobytes()

# ------------------------------------------------------------------- audio
def synth_audio(path):
    sr = 44100
    n = int((DUR + 1) * sr)
    out = np.zeros(n, np.float32)
    def add(t, sig, g=1.0):
        i = int(t * sr)
        if i >= n: return
        sig = sig[:n - i]
        out[i:i + len(sig)] += (sig * g).astype(np.float32)
    rng = np.random.default_rng(7)
    # pad: slow chord progression (Am - F - C - G), 8 s each
    chords = [[110, 164.8, 220, 261.6], [87.3, 174.6, 220, 261.6], [130.8, 196, 261.6, 329.6], [98, 196, 246.9, 293.7]]
    tt = np.arange(int(8.4 * sr)) / sr
    env = np.minimum(1, np.minimum(tt / 2.0, (8.4 - tt) / 2.0)) ** 1.5
    k = 0
    for c in range(0, int(DUR) + 1, 8):
        sig = sum(np.sin(2 * np.pi * f * tt + .3 * np.sin(2 * np.pi * .2 * tt + j)) / (1 + j * .35)
                  for j, f in enumerate(chords[k % 4])) * env
        add(c, sig, .045); k += 1
    # sfx
    def shutter():
        s = np.zeros(int(.2 * sr)); tt2 = np.arange(len(s)) / sr
        for o in (0, .055):
            m = tt2 >= o
            nz = rng.standard_normal(len(s)); nz = np.diff(nz, prepend=0)
            s += m * nz * np.exp(-(tt2 - o) / .012)
        return s * .18
    def whoosh(d=.7):
        m = int(d * sr); tt2 = np.arange(m) / sr
        nz = rng.standard_normal(m)
        for _ in range(3): nz = np.convolve(nz, np.ones(24) / 24, 'same')
        return nz * np.sin(np.pi * tt2 / d) ** 2 * 4.0
    def draw(d):
        m = int(d * sr); tt2 = np.arange(m) / sr
        f = 500 + 900 * tt2 / d
        return np.sin(2 * np.pi * np.cumsum(f) / sr) * np.sin(np.pi * tt2 / d) * .6
    def tick(f=1500, d=.05):
        m = int(d * sr); tt2 = np.arange(m) / sr
        return np.sin(2 * np.pi * f * tt2) * np.exp(-tt2 / (d / 4))
    for t in (.6, 1.9, 3.2): add(t, shutter())
    add(4.3, whoosh(.9), .5); add(5.0, draw(1.0), .06)
    for sc in SCENES:
        add(sc.t0, shutter()); add(sc.t0 - .3, whoosh(.6), .5)
        for e in sc.els:
            t = sc.t0 + e.start
            if e.kind == 'label': add(t, tick(1200, .05), .05)
            elif e.kind == 'arrow': add(t, whoosh(min(1.2, e.dur)), .3); add(t, draw(min(1.2, e.dur)), .035)
            elif e.kind in ('circle', 'dash'): add(t, draw(min(1.0, e.dur)), .04); add(t + e.dur, tick(1800, .035), .08)
            elif e.kind == 'grid': add(t, draw(e.dur), .04)
    for i in range(3): add(97.5 + .7 * i, shutter())
    add(100.6, whoosh(.9), .5)
    out *= np.minimum(1, np.minimum(np.arange(n) / (2 * sr), (n - np.arange(n)) / (2.5 * sr)))
    out /= max(1e-6, np.abs(out).max()) / .8
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((out * 32767).astype(np.int16).tobytes())

def srt(path):
    def f(t):
        h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
        return f'{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}'
    with open(path, 'w', encoding='utf-8') as fh:
        for i, (a, b, tx) in enumerate(SUBS, 1): fh.write(f'{i}\n{f(a)} --> {f(b)}\n{tx}\n\n')

# -------------------------------------------------------------------- main
def main():
    out = f'{HERE}/out'; os.makedirs(out, exist_ok=True)
    if '--preview' in sys.argv:
        pv = f'{HERE}/preview'; os.makedirs(pv, exist_ok=True)
        times = [float(x) for x in sys.argv[sys.argv.index('--preview') + 1:] if not x.startswith('-')] or \
                [2.5, 6.8, 10, 16, 24, 35, 43, 52, 62, 70, 80, 95, 100, 104]
        for T in times:
            c, s = render_frame(int(T * FPS))
            Image.frombytes('RGB', (W, H), s).save(f'{pv}/t{T:05.1f}.jpg', quality=88)
        return
    synth_audio(f'{out}/audio.wav'); srt(f'{out}/subtitles_ar.srt')
    N = int(DUR * FPS)
    def enc(name):
        return subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                                 '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', f'{out}/{name}'],
                                stdin=subprocess.PIPE)
    pc, ps = enc('_clean_video.mp4'), enc('_sub_video.mp4')
    with Pool(4) as pool:
        for i, (c, s) in enumerate(pool.imap(render_frame, range(N), chunksize=6)):
            pc.stdin.write(c); ps.stdin.write(s)
            if i % 150 == 0: print(f'{i}/{N}', flush=True)
    pc.stdin.close(); ps.stdin.close(); pc.wait(); ps.wait()
    for v, name in (('_clean_video.mp4', 'composition_clean_no_voiceover.mp4'), ('_sub_video.mp4', 'composition_arabic_subtitles.mp4')):
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{out}/{v}', '-i', f'{out}/audio.wav', '-c:v', 'copy',
                        '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', f'{out}/{name}'], check=True)
        os.remove(f'{out}/{v}')
    print('done')

if __name__ == '__main__':
    main()
