// All scenes. Each SCENES[id](ctx, u, sc) draws scene-local time u (seconds) onto a transparent layer.
const SCENES = {};
const CM = TIMELINE.common;
const CARD = { x: 108, y: 856, w: 864, h: 520 };
const FLOOR = 742;

// ───────────────────────── shared layout pieces ─────────────────────────
const fit = (c, s, size, weight, maxW) => Math.min(size, size * maxW / tw(c, s, size, weight));
function header(c, u, cfg) {
  const a = E.out(seg(u, 0.05, 0.6));
  c.save(); c.globalAlpha *= a; c.translate(0, (1 - a) * -22);
  txt(c, cfg.en, SAFE.x0, 272, { size: 26, color: C.gold, align: 'left', ls: 5, weight: 700 });
  const bt = cfg.zoom ? 'ZOOM  ·  متغيرة' : 'PRIME  ·  ثابتة';
  const bw = tw(c, bt, 24, 700) + 40;
  pill(c, SAFE.x1 - bw, 244, bw, 40, 'rgba(245,184,46,.12)', 'rgba(245,184,46,.7)');
  txt(c, bt, SAFE.x1 - bw / 2, 272, { size: 24, color: C.gold, rtl: true });
  txt(c, cfg.ar, 540, 352, { size: fit(c, cfg.ar, 68, 900, 864), weight: 900, rtl: true, shadow: 12 });
  c.restore();
}
function sceneK(keys) {
  let Lm = 0, Wm = 0;
  for (const k of keys) { const s = lensSize(k); Lm = Math.max(Lm, s.L); Wm = Math.max(Wm, s.W); }
  return Math.min(290 / Lm, 245 / Wm);
}
function stage(c, u, cfg) {
  const keys = cfg.lenses, k0 = cfg.k || (cfg.k = sceneK(keys)), sel = cfg.sel;
  const s = E.io(seg(u, CM.select, CM.selectDur));
  const others = [0, 1, 2].filter(i => i !== sel);
  const order = [...others, sel];
  for (const i of order) {
    const enter = E.back(seg(u, CM.lensIn + CM.lensStagger * i, 0.8)), al = E.out(seg(u, CM.lensIn + CM.lensStagger * i, 0.5));
    const isSel = i === sel;
    const bx0 = 270 + 270 * i;
    const oi = others.indexOf(i);
    const bx = isSel ? lerp(bx0, 540, s) : lerp(bx0, oi === 0 ? 178 : 902, s);
    const sc = isSel ? lerp(1, 1.16, s) : lerp(1, .72, s);
    const lensAlpha = al * (isSel ? 1 : lerp(1, .5, s));
    const mv = isSel ? Math.sin(Math.PI * seg(u, CM.select, CM.selectDur)) : 0;       // motion speed proxy
    const y = FLOOR + (1 - enter) * 80 + (isSel ? Math.sin(u * 1.6) * 3 * s : 0);
    const lean = isSel ? lerp(0, -9, s) + Math.sin(u * .9) * 1.2 * s : 0;
    const pitch = isSel ? lerp(15, 24, s) : 17;
    const st = cfg.lensState ? cfg.lensState(u, i) : {};
    drawLens(c, keys[i], { x: bx, y, k: k0 * sc, lean, pitch, alpha: lensAlpha, blur: mv * 3, glow: isSel && s > .2,
      rot: { focus: (st.focus != null ? st.focus : u * (isSel ? 1.1 : .25) + i), zoom: st.zoom != null ? st.zoom : u * .3 + i }, ext: st.ext || 0 });
    // label
    const lab = LENS[keys[i]].label;
    c.save(); c.globalAlpha *= al;
    const big = isSel ? s : 0;
    txt(c, lab, bx, 812 + (1 - enter) * 30, { size: lerp(38, 48, big), weight: 900, color: isSel && s > .5 ? C.gold : C.white, ls: 1, shadow: 8 });
    txt(c, (LENS[keys[i]].kind === 'zoom' ? 'Zoom' : 'Prime'), bx, 840 + (1 - enter) * 30, { size: 20, weight: 400, color: C.dim, ls: 3, alpha: 1 });
    c.restore();
  }
  // gold selection ring on the floor
  if (s > 0) { c.save(); c.globalAlpha *= s * .8; c.strokeStyle = C.gold; c.lineWidth = 3; c.beginPath(); c.ellipse(540, FLOOR + 4, 150 * s + 20, 20 * s + 3, 0, 0, 7); c.stroke(); c.restore(); }
}
function card(c, u, cfg, draw) {
  const a = E.out(seg(u, CM.cardIn, 0.7)); if (a <= 0.001) return;
  c.save(); c.globalAlpha *= a; c.translate(CARD.x, CARD.y + (1 - a) * 60);
  c.save();
  const g = c.createLinearGradient(0, 0, 0, CARD.h); g.addColorStop(0, '#121722'); g.addColorStop(1, '#0a0d13');
  rr(c, 0, 0, CARD.w, CARD.h, 30); c.fillStyle = g; c.shadowColor = 'rgba(0,0,0,.5)'; c.shadowBlur = 30; c.fill(); c.shadowBlur = 0;
  rr(c, 0, 0, CARD.w, CARD.h, 30); c.clip();
  draw(c, u, CARD.w, CARD.h);
  c.restore();
  rr(c, 0, 0, CARD.w, CARD.h, 30); c.strokeStyle = 'rgba(255,255,255,.14)'; c.lineWidth = 2; c.stroke();
  c.restore();
}
function bullets(c, u, arr, times, active) {
  arr.forEach((s, i) => {
    const a = E.out(seg(u, times[i], .5)); if (a <= 0) return;
    const y = 1440 + i * 58, on = active == null || active === i;
    c.save(); c.globalAlpha *= a; c.translate((1 - a) * 50, 0);
    c.fillStyle = on ? C.gold : 'rgba(245,184,46,.35)'; c.beginPath(); c.arc(SAFE.x1 - 10, y - 12, 9, 0, 7); c.fill();
    txt(c, s, SAFE.x1 - 40, y, { size: 35, weight: 700, rtl: true, align: 'right', color: on ? '#fff' : 'rgba(255,255,255,.5)' });
    c.restore();
  });
}
function quote(c, u, s, t0, sub) {
  const a = E.out(seg(u, t0, .6)); if (a <= 0) return;
  c.save(); c.globalAlpha *= a; c.translate(0, (1 - a) * 30);
  const lines = wrap(c, s, 46, 900, 790);
  c.fillStyle = C.gold; c.fillRect(SAFE.x1 - 6, 1398, 6, lines.length * 60 + (sub ? 56 : 0) - 6);
  lines.forEach((l, i) => txt(c, l, SAFE.x1 - 30, 1442 + i * 60, { size: 46, weight: 900, rtl: true, align: 'right' }));
  if (sub) wrap(c, sub, 29, 700, 800).forEach((l, i) => txt(c, l, SAFE.x1 - 30, 1442 + lines.length * 60 + 4 + i * 38, { size: 29, weight: 700, rtl: true, align: 'right', color: C.dim }));
  c.restore();
}
function foot(c, u, str, t0 = 3.4) {
  const a = E.out(seg(u, t0, .7)); if (a <= 0.001) return;
  const size = fit(c, str, 25, 700, 790), w = tw(c, str, size, 700) + 70, h = 42, x = 540 - w / 2, y = 1588;
  c.save(); c.globalAlpha *= a; c.translate(0, (1 - a) * 26);
  rr(c, x, y, w, h, h / 2); c.fillStyle = 'rgba(8,10,14,.94)'; c.fill();
  c.save(); rr(c, x, y, w, h, h / 2); c.clip();                                   // one-shot light sweep
  const sw = E.io(seg(u, t0 + .35, 1.0)); const gx = x - 120 + (w + 240) * sw;
  const g = c.createLinearGradient(gx - 60, 0, gx + 60, 0); g.addColorStop(0, 'rgba(245,184,46,0)'); g.addColorStop(.5, 'rgba(245,184,46,.38)'); g.addColorStop(1, 'rgba(245,184,46,0)');
  c.fillStyle = g; c.fillRect(x, y, w, h); c.restore();
  rr(c, x, y, w, h, h / 2); c.strokeStyle = 'rgba(245,184,46,.75)'; c.lineWidth = 2; c.stroke();
  c.fillStyle = C.gold; c.beginPath(); c.arc(x + w - 24, y + h / 2, 6, 0, 7); c.fill();
  txt(c, str, x + w - 42, y + h / 2 + size * .33, { size, weight: 700, rtl: true, align: 'right', color: 'rgba(255,255,255,.95)' });
  c.restore();
}
function catScene(cfg, drawCard, extra) {
  return (c, u, sc) => {
    header(c, u, cfg); stage(c, u, cfg);
    card(c, u, cfg, (cc, uu, w, h) => drawCard(cc, uu, w, h, sc));
    if (extra) extra(c, u, sc);
    if (cfg.foot) foot(c, u, cfg.foot);
  };
}
const fx = (u, sc) => E.io(seg(u, sc.fx[0], sc.fx[1] - sc.fx[0]));

// ───────────────────────── shared illustration helpers ─────────────────────────
function person(c, x, gy, h, o = {}) {
  const s = h / 190, jacket = o.jacket || '#d9822b';
  c.save(); c.translate(x, gy); c.scale(s, s);
  c.fillStyle = 'rgba(0,0,0,.28)'; c.beginPath(); c.ellipse(0, 2, 40, 7, 0, 0, 7); c.fill();
  c.fillStyle = '#26303f'; rr(c, -17, -92, 15, 92, 5); c.fill(); rr(c, 2, -92, 15, 92, 5); c.fill();         // legs
  c.fillStyle = '#12161d'; rr(c, -20, -8, 20, 10, 4); c.fill(); rr(c, 1, -8, 20, 10, 4); c.fill();             // shoes
  c.fillStyle = jacket; rr(c, -26, -160, 52, 78, 14); c.fill();                                                  // torso
  c.fillStyle = shade(jacket, .75).map(Math.round) && rgba(shade(jacket, .75)); rr(c, -34, -156, 14, 64, 7); c.fill(); rr(c, 20, -156, 14, 64, 7); c.fill(); // arms
  c.fillStyle = '#e1ae8e'; c.beginPath(); c.arc(0, -178, 17, 0, 7); c.fill();                                    // head
  c.fillStyle = '#1b1612'; c.beginPath(); c.arc(0, -184, 17.5, Math.PI, 0); c.fill();                            // hair
  c.fillStyle = '#3a2f26'; rr(c, 14, -140, 22, 26, 5); c.fill();                                                // bag
  c.restore();
}
function cameraIcon(c, x, y, s, col = C.white) {
  c.save(); c.translate(x, y); c.scale(s, s); c.fillStyle = col;
  rr(c, -22, -12, 44, 28, 6); c.fill(); rr(c, -10, -18, 14, 8, 3); c.fill();
  c.fillStyle = '#0b0e13'; c.beginPath(); c.arc(0, 2, 9, 0, 7); c.fill(); c.fillStyle = col; c.beginPath(); c.arc(0, 2, 5, 0, 7); c.fill(); c.restore();
}
function cone(c, ox, oy, ang, len, rot, col = C.teal, a = 1) {
  const h = ang * Math.PI / 360;
  c.save(); const g = c.createRadialGradient(ox, oy, 0, ox, oy, len);
  g.addColorStop(0, rgba(col, .45 * a)); g.addColorStop(1, rgba(col, .05 * a));
  c.fillStyle = g; c.beginPath(); c.moveTo(ox, oy); c.arc(ox, oy, len, rot - h, rot + h); c.closePath(); c.fill();
  c.strokeStyle = rgba(col, .95 * a); c.lineWidth = 3; c.beginPath(); c.moveTo(ox + Math.cos(rot - h) * len, oy + Math.sin(rot - h) * len); c.lineTo(ox, oy); c.lineTo(ox + Math.cos(rot + h) * len, oy + Math.sin(rot + h) * len); c.stroke();
  c.restore();
}
function dimOutside(c, w, h, fx0, fy0, fw, fh, a = .6) {
  c.save(); c.fillStyle = `rgba(4,6,9,${a})`; c.beginPath(); c.rect(0, 0, w, h); c.rect(fx0, fy0, fw, fh); c.fill('evenodd'); c.restore();
}
function frameBox(c, x, y, w, h, col, lw = 3, brackets = true) {
  c.save(); c.strokeStyle = col; c.lineWidth = lw;
  if (!brackets) { c.strokeRect(x, y, w, h); c.restore(); return; }
  const l = Math.min(34, w / 4, h / 4);
  for (const [cx, cy, sx, sy] of [[x, y, 1, 1], [x + w, y, -1, 1], [x, y + h, 1, -1], [x + w, y + h, -1, -1]]) { c.beginPath(); c.moveTo(cx, cy + sy * l); c.lineTo(cx, cy); c.lineTo(cx + sx * l, cy); c.stroke(); }
  c.globalAlpha *= .35; c.lineWidth = 1.5; c.strokeRect(x, y, w, h); c.restore();
}
function buildingRow(c, x0, x1, baseY, seed, hMin, hMax, palette, win = true) {
  const R = rng(seed); let x = x0;
  while (x < x1) {
    const w = 60 + R() * 70, h = hMin + R() * (hMax - hMin), col = palette[Math.floor(R() * palette.length)];
    const g = c.createLinearGradient(x, baseY - h, x, baseY); g.addColorStop(0, rgba(shade(col, 1.25))); g.addColorStop(1, rgba(shade(col, .75)));
    c.fillStyle = g; c.fillRect(x, baseY - h, w, h);
    if (win) for (let yy = baseY - h + 14; yy < baseY - 18; yy += 22) for (let xx = x + 10; xx < x + w - 12; xx += 18) { const lit = R() > .55; c.fillStyle = lit ? 'rgba(255,205,110,.85)' : 'rgba(10,14,22,.55)'; c.fillRect(xx, yy, 9, 11); }
    x += w + 3 + R() * 6;
  }
}
function skyGrad(c, w, h, a = '#16233d', b = '#47658f', cc = '#e9ae67') {
  const g = c.createLinearGradient(0, 0, 0, h); g.addColorStop(0, a); g.addColorStop(.62, b); g.addColorStop(1, cc); c.fillStyle = g; c.fillRect(0, 0, w, h);
}
function chipLabel(c, s, x, y, col = C.gold, size = 26, align = 'left') {
  const w = tw(c, s, size, 700) + 28; const x0 = align === 'left' ? x : align === 'right' ? x - w : x - w / 2;
  pill(c, x0, y - size - 6, w, size + 18, 'rgba(8,10,14,.78)', rgba(col, .8)); txt(c, s, x0 + w / 2, y + 2, { size, color: col, rtl: /[؀-ۿ]/.test(s) });
}

// ───────────────────────── Scene 1: intro ─────────────────────────
SCENES.intro = (c, u) => {
  const cx = 540, tShift = E.io(seg(u, 3.5, 1.0));
  const cy = lerp(800, 600, tShift), sc = lerp(1, .74, tShift);
  c.save(); c.translate(cx, cy); c.scale(sc, sc);
  const R = 330, enter = E.out(seg(u, 0, .7));
  c.globalAlpha *= enter;
  // outer ring
  let g = c.createRadialGradient(0, 0, R * .8, 0, 0, R * 1.04); g.addColorStop(0, '#0b0c10'); g.addColorStop(.55, '#2a2d35'); g.addColorStop(.75, '#8e949f'); g.addColorStop(.86, '#1a1c22'); g.addColorStop(1, '#050608');
  c.fillStyle = g; c.beginPath(); c.arc(0, 0, R * 1.04, 0, 7); c.fill();
  for (let i = 0; i < 72; i++) { const a = i / 72 * Math.PI * 2, l = i % 6 === 0 ? 20 : 10; c.strokeStyle = i % 6 === 0 ? 'rgba(245,184,46,.85)' : 'rgba(220,225,235,.35)'; c.lineWidth = i % 6 === 0 ? 3 : 1.5; c.beginPath(); c.moveTo(Math.cos(a) * (R * .93 - l), Math.sin(a) * (R * .93 - l)); c.lineTo(Math.cos(a) * R * .93, Math.sin(a) * R * .93); c.stroke(); }
  // aperture disc
  const Rd = 262; g = c.createRadialGradient(0, 0, 40, 0, 0, Rd); g.addColorStop(0, '#2a2c33'); g.addColorStop(1, '#0d0e12'); c.fillStyle = g; c.beginPath(); c.arc(0, 0, Rd, 0, 7); c.fill();
  const open = E.out(seg(u, .15, 1.3)) * (1 - E.io(seg(u, 3.25, .25)) * .55) ;
  const Rh = Math.max(6, 205 * open + 6), rot = (1 - open) * 1.1 + u * .02, n = 9;
  const V = []; for (let i = 0; i < n; i++) { const a = rot + i * 2 * Math.PI / n; V.push([Math.cos(a) * Rh, Math.sin(a) * Rh]); }
  c.save(); c.beginPath(); c.arc(0, 0, Rd, 0, 7); c.clip();
  for (let i = 0; i < n; i++) {
    const a = V[i], b = V[(i + 1) % n]; let dx = b[0] - a[0], dy = b[1] - a[1]; const dl = Math.hypot(dx, dy) || 1; dx /= dl; dy /= dl;
    // extend from b backwards away to the disc edge
    const pb = b[0] * dx + b[1] * dy; const s = -pb + Math.sqrt(Math.max(0, pb * pb - (b[0] * b[0] + b[1] * b[1]) + Rd * Rd));
    const e = [b[0] + dx * s, b[1] + dy * s]; const f2 = [a[0] - dx * 600, a[1] - dy * 600];
    c.fillStyle = i % 2 ? 'rgba(255,255,255,.035)' : 'rgba(0,0,0,.12)'; c.beginPath(); c.moveTo(a[0], a[1]); c.lineTo(b[0], b[1]); c.lineTo(e[0], e[1]); c.lineTo(e[0] * 1.0 + (a[0] - b[0]) * 0, e[1]); c.closePath();
    c.strokeStyle = 'rgba(200,205,215,.4)'; c.lineWidth = 2; c.beginPath(); c.moveTo(b[0], b[1]); c.lineTo(e[0], e[1]); c.stroke();
  }
  c.restore();
  // glass behind hole
  c.save(); c.beginPath(); V.forEach((p, i) => i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.closePath(); c.clip();
  g = c.createRadialGradient(-40, -60, 10, 0, 0, Rh * 1.1); g.addColorStop(0, '#1d3b7a'); g.addColorStop(.5, '#10163f'); g.addColorStop(1, '#04060c'); c.fillStyle = g; c.fillRect(-300, -300, 600, 600);
  c.restore();
  c.strokeStyle = 'rgba(245,184,46,.9)'; c.lineWidth = 3; c.beginPath(); V.forEach((p, i) => i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.closePath(); c.stroke();
  // focal-length counter inside the glass
  const seq = ['8', '14', '24', '50', '85', '200', '600'], t0 = .75, dt = .34;
  const idx = Math.floor((u - t0) / dt);
  if (idx >= 0 && idx < seq.length && u < 3.3) {
    const ph = ((u - t0) / dt) % 1, pop = E.out(clamp(ph * 3));
    c.save(); c.scale(.9 + .1 * pop, .9 + .1 * pop); c.globalAlpha *= (1 - Math.pow(ph, 6) * .6);
    txt(c, seq[idx], 0, 40, { size: 150, weight: 900, color: C.gold, shadow: 24, ls: -2 });
    txt(c, 'mm', 0, 112, { size: 44, weight: 700, color: 'rgba(255,255,255,.8)' }); c.restore();
  }
  c.restore();
  // top label
  txt(c, 'THE WORLD OF CAMERA LENSES', 540, 262, { size: 26, color: C.gold, ls: 7, alpha: E.out(seg(u, .3, .6)) });
  // flash + title
  const fl = 1 - seg(u, 3.5, .3); if (u >= 3.5 && fl > 0) { c.fillStyle = `rgba(255,255,255,${.7 * fl})`; c.fillRect(0, 0, W, H); }
  const tIn = (t0, d = .7) => E.out(seg(u, t0, d));
  let a = tIn(3.7); txt(c, 'كل عدسة…', 540, 1195 + (1 - a) * 40, { size: 122, weight: 900, rtl: true, alpha: a, shadow: 16 });
  a = tIn(4.1); txt(c, 'تحكي قصة مختلفة!', 540, 1335 + (1 - a) * 40, { size: 88, weight: 900, rtl: true, color: C.gold, alpha: a, shadow: 16 });
  a = tIn(4.8); c.save(); c.globalAlpha *= a; c.fillStyle = C.gold; c.fillRect(540 - 60 * a, 1400, 120 * a, 4); c.restore();
  a = tIn(4.9); txt(c, 'عالم عدسات التصوير', 540, 1478, { size: 42, weight: 700, rtl: true, alpha: a });
  txt(c, 'من عين السمكة إلى تصوير الحياة البرية', 540, 1530, { size: 30, weight: 400, rtl: true, color: C.dim, alpha: a });
};

// ───────────────────────── Scene 2: fish-eye ─────────────────────────
const ROOM = (() => {
  const L = [], X = 2.6, Y = 1.6, z0 = 0.9, z1 = 9, W = 'rgba(255,255,255,.7)', T = '#38d6c4', G = '#F5B82E';
  for (let x = -2.6; x <= 2.7; x += 1.3) { L.push([[x, Y, z0], [x, Y, z1], W]); L.push([[x, -Y, z0], [x, -Y, z1], W]); }
  for (let y = -.8; y <= .85; y += .8) { L.push([[-X, y, z0], [-X, y, z1], T]); L.push([[X, y, z0], [X, y, z1], T]); }
  for (let z = z0 + .4; z <= z1; z += 1.0) { L.push([[-X, -Y, z], [X, -Y, z], T]); L.push([[X, -Y, z], [X, Y, z], T]); L.push([[X, Y, z], [-X, Y, z], T]); L.push([[-X, Y, z], [-X, -Y, z], T]); }
  for (let z = 2; z < 8; z += 2.2) for (const sx of [-X, X]) { L.push([[sx, -.6, z], [sx, -.6, z + 1.3], G]); L.push([[sx, -.6, z + 1.3], [sx, .6, z + 1.3], G]); L.push([[sx, .6, z + 1.3], [sx, .6, z], G]); L.push([[sx, .6, z], [sx, -.6, z], G]); }
  L.push([[-X, -Y, z1], [X, -Y, z1], G], [[X, -Y, z1], [X, Y, z1], G], [[X, Y, z1], [-X, Y, z1], G], [[-X, Y, z1], [-X, -Y, z1], G]);
  return L;
})();
function fishProject(p, lam, R) {
  const rx = p[0] / p[2], ry = p[1] / p[2], r = Math.hypot(rx, ry) || 1e-6;
  const rho = lerp(r * .78, Math.atan(r) / (Math.PI / 2), lam);
  return [rx / r * rho * R, ry / r * rho * R];
}
const CFG = {};
CFG.fisheye = { en: 'FISH-EYE LENSES', ar: 'عدسات عين السمكة', lenses: ['fe8', 'fe10', 'fe12'], sel: 0,
  foot: 'زاوية رؤية Fish-eye تختلف حسب تصميم العدسة وإسقاطها الخاص' };
SCENES.fisheye = catScene(CFG.fisheye, (c, u, w, h, sc) => {
  const lam = fx(u, sc), R = 200, cx = 262, cy = 252;
  c.save(); c.translate(cx, cy);
  c.save(); rr(c, -R, -R, 2 * R, 2 * R, lerp(26, R, lam)); c.clip();
  const bg = c.createRadialGradient(0, 0, 10, 0, 0, R * 1.2); bg.addColorStop(0, '#1b2740'); bg.addColorStop(1, '#0a0e16'); c.fillStyle = bg; c.fillRect(-R, -R, 2 * R, 2 * R);
  c.lineCap = 'round'; c.lineWidth = 2.6;
  for (const [a, b, col] of ROOM) {
    c.strokeStyle = col; c.beginPath();
    const N = 36; for (let i = 0; i <= N; i++) { const t = i / N; const p = [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)]; const q = fishProject(p, lam, R); i ? c.lineTo(q[0], q[1]) : c.moveTo(q[0], q[1]); }
    c.stroke();
  }
  c.restore();
  rr(c, -R, -R, 2 * R, 2 * R, lerp(26, R, lam)); c.strokeStyle = 'rgba(245,184,46,.85)'; c.lineWidth = 3; c.stroke();
  c.restore();
  const l1 = 1 - E.io(seg(u, sc.fx[0] + .6, .8)), l2 = E.io(seg(u, sc.fx[0] + 1.2, .8));
  txt(c, 'خطوط مستقيمة', cx, 494, { size: 28, rtl: true, color: C.white, alpha: l1 * E.out(seg(u, CM.cardIn + .3, .5)) });
  txt(c, 'تشوّه دائري منحنٍ', cx, 494, { size: 28, rtl: true, color: C.gold, alpha: l2 });
  // top-down angle diagram
  const ox = 668, oy = 440, ang = lerp(75, 180, lam);
  cone(c, ox, oy, ang, 165, -Math.PI / 2, C.teal, 1);
  cameraIcon(c, ox, oy + 6, 1.1);
  txt(c, Math.round(ang) + '°', ox, oy - 78, { size: 82, weight: 900, color: C.gold, shadow: 14 });
  txt(c, 'حتى 180°', ox, oy - 36, { size: 26, rtl: true, color: C.dim, alpha: lam });
  txt(c, 'TOP VIEW', ox, 70, { size: 20, color: C.dim, ls: 5 });
}, (c, u, sc) => bullets(c, u, ['زاوية رؤية واسعة جدًا — قد تصل إلى 180°', 'تشوّه منحنٍ مميّز للخطوط المستقيمة', 'للتصوير الإبداعي والرياضة والمناظر غير التقليدية'], sc.bullets));

// ───────────────────────── Scene 3: ultra-wide ─────────────────────────
CFG.ultrawide = { en: 'ULTRA-WIDE LENSES', ar: 'عدسات الزاوية الواسعة جدًا', lenses: ['uw14', 'uw16', 'uw20'], sel: 0, foot: 'زوايا الرؤية قُطرية ومحسوبة لمستشعر Full Frame' };
SCENES.ultrawide = catScene(CFG.ultrawide, (c, u, w, h, sc) => {
  skyGrad(c, w, h, '#14213b', '#3f5f8c', '#eab069');
  buildingRow(c, -20, w + 20, 392, 11, 90, 300, ['#1d2a44', '#26385c', '#1a2338', '#33466b']);
  buildingRow(c, -40, w + 20, 420, 77, 50, 150, ['#101827', '#16203a', '#0f1626']);
  c.fillStyle = '#d7dde8'; rr(c, 410, 70, 44, 330, 6); c.fill(); c.fillRect(428, 20, 8, 52);        // landmark tower
  for (let y = 100; y < 380; y += 28) { c.fillStyle = 'rgba(40,60,100,.6)'; c.fillRect(418, y, 28, 12); }
  const g = c.createLinearGradient(0, 400, 0, h); g.addColorStop(0, '#222a38'); g.addColorStop(1, '#0d1118'); c.fillStyle = g; c.fillRect(0, 400, w, h - 400);
  c.strokeStyle = 'rgba(255,255,255,.35)'; c.lineWidth = 4; c.setLineDash([36, 28]); c.beginPath(); c.moveTo(432, 410); c.lineTo(432, h); c.stroke(); c.setLineDash([]);
  const f = lerp(35, 14, fx(u, sc)), Wf = 760 * 14 / f, Hf = Wf / 1.5, fx0 = 432 - Wf / 2, fy0 = 262 - Hf / 2;
  dimOutside(c, w, h, fx0, fy0, Wf, Hf, .7);
  frameBox(c, fx0, fy0, Wf, Hf, C.gold, 4);
  txt(c, Math.round(f) + 'mm', fx0 + 18, fy0 + Hf - 16, { size: 54, weight: 900, color: C.gold, align: 'left', shadow: 10 });
  // HUD: field of view cone
  c.save(); rr(c, 16, 16, 176, 136, 18); c.fillStyle = 'rgba(8,10,14,.88)'; c.fill(); c.strokeStyle = 'rgba(255,255,255,.15)'; c.lineWidth = 1.5; c.stroke(); c.restore();
  const ang = fovDiag(f); cone(c, 104, 132, ang, 98, -Math.PI / 2, C.teal, 1); cameraIcon(c, 104, 136, .5);
  txt(c, Math.round(ang) + '°', 104, 78, { size: 38, weight: 900, color: C.gold, shadow: 6 });
}, (c, u, sc) => quote(c, u, 'للمعمار والمناظر الطبيعية والمساحات الضيقة', sc.quote));

// ───────────────────────── Scene 4: wide & standard ─────────────────────────
CFG.wide = { en: 'WIDE & STANDARD LENSES', ar: 'الزاوية المتوسطة والقياسية', lenses: ['w24', 'w35', 's50'], sel: 1, foot: 'الكاميرا ثابتة · الزوايا لمستشعر Full Frame · 50mm ≠ عين الإنسان تمامًا' };
SCENES.wide = catScene(CFG.wide, (c, u, w, h, sc) => {
  skyGrad(c, w, h, '#1b2a45', '#52709a', '#efbd7e');
  buildingRow(c, -20, w + 40, 370, 5, 150, 330, ['#2a3a5c', '#3b4d73', '#233150', '#4a5e86']);
  c.fillStyle = '#5b6779'; c.fillRect(0, 370, w, 22);                                                // sidewalk
  const g = c.createLinearGradient(0, 392, 0, h); g.addColorStop(0, '#2b3240'); g.addColorStop(1, '#10141b'); c.fillStyle = g; c.fillRect(0, 392, w, h - 392);
  // lamp + tree + car
  c.fillStyle = '#1b2230'; c.fillRect(110, 190, 8, 180); c.fillRect(110, 190, 34, 7); c.fillStyle = '#ffd877'; c.beginPath(); c.arc(146, 204, 9, 0, 7); c.fill();
  c.fillStyle = '#5a3d27'; c.fillRect(740, 280, 12, 92); c.fillStyle = '#2f7a4d'; for (const [dx, dy, r] of [[0, 0, 44], [-30, 24, 32], [32, 22, 34]]) { c.beginPath(); c.arc(746 + dx, 262 + dy, r, 0, 7); c.fill(); }
  c.fillStyle = '#9a2b34'; rr(c, 560, 404, 150, 40, 14); c.fill(); rr(c, 590, 384, 90, 30, 12); c.fill(); c.fillStyle = '#0c0f14'; c.beginPath(); c.arc(594, 446, 14, 0, 7); c.arc(676, 446, 14, 0, 7); c.fill();
  person(c, 432, 372, 190);
  const fr = [[24, 'مناسبة للسفر والبيئة'], [35, 'شارع'], [50, 'بورتريه']];
  const act = u < sc.segs[1] ? 0 : u < sc.segs[2] ? 1 : u < sc.segs[3] ? 2 : 2;
  const fa = fr.map(([f]) => { const Wf = 760 * 24 / f; return [432 - Wf / 2, 262 - Wf / 3, Wf, Wf / 1.5]; });
  // smooth active frame (interpolated rectangle)
  const tgt = fa[act], prevI = Math.max(0, act - 1), pr = fa[prevI];
  const mv = u < sc.segs[0] ? 0 : act === 0 ? E.io(seg(u, sc.segs[0] - .3, .7)) : E.io(seg(u, sc.segs[act], .6));
  const cur = act === 0 ? [lerp(fa[2][0], tgt[0], mv), lerp(fa[2][1], tgt[1], mv), lerp(fa[2][2], tgt[2], mv), lerp(fa[2][3], tgt[3], mv)] : tgt.map((v, i) => lerp(pr[i], v, mv));
  dimOutside(c, w, h, ...cur, .68);
  fa.forEach((b, i) => { frameBox(c, ...b, i === act ? 'rgba(0,0,0,0)' : 'rgba(255,255,255,.35)', 2, false); });
  frameBox(c, ...cur, C.gold, 4);
  const f = fr[act][0]; txt(c, f + 'mm', cur[0] + 14, cur[1] + cur[3] - 12, { size: 44, weight: 900, color: C.gold, align: 'left', shadow: 8 });
  txt(c, Math.round(fovDiag(f)) + '°', cur[0] + cur[2] - 14, cur[1] + 44, { size: 34, weight: 900, color: C.teal, align: 'right', shadow: 8 });
  // fixed-camera badge
  cameraIcon(c, 810, 482, .85, C.white); txt(c, 'ثابتة', 770, 490, { size: 22, rtl: true, color: C.dim, align: 'right' });
}, (c, u, sc) => {
  const act = u < sc.segs[1] ? 0 : u < sc.segs[2] ? 1 : 2;
  bullets(c, u, ['24mm: السفر والمناظر والبيئة المحيطة', '35mm: تصوير الشارع والتوثيق', '50mm: البورتريه والتصوير اليومي'], sc.bullets, act);
});

// ───────────────────────── Scene 5: portrait ─────────────────────────
CFG.portrait = { en: 'PORTRAIT · SHORT TELEPHOTO', ar: 'عدسات البورتريه', lenses: ['p85', 'p105', 'p135'], sel: 0, foot: 'العزل يعتمد أيضًا على الفتحة ومسافة التصوير وبُعد الخلفية' };
const BOKEH = (() => { const R = rng(21), a = []; for (let i = 0; i < 46; i++) a.push({ x: R() * 864, y: 40 + R() * 250, r: 22 + R() * 16, c: [[255, 214, 140], [255, 240, 200], [150, 230, 220], [255, 170, 130]][Math.floor(R() * 4)] }); return a; })();
function portraitCard(c, u, w, h, sc) {
  const b = fx(u, sc);
  skyGrad(c, w, h, '#22304f', '#6b6a8a', '#e9a76a');
  c.save(); if (b > .02) c.filter = `blur(${b * 15}px)`;
  const R = rng(5);
  for (let i = 0; i < 9; i++) { const x = i * 112 - 20 + R() * 30, tw_ = 20 + R() * 12; c.fillStyle = '#1a2230'; c.fillRect(x, 120, tw_, 420); c.fillStyle = i % 2 ? '#1f5a3e' : '#17482f'; for (let j = 0; j < 6; j++) { c.beginPath(); c.arc(x + 10 + (R() - .5) * 90, 90 + j * 34 + R() * 20, 44 + R() * 22, 0, 7); c.fill(); } }
  c.restore();
  // string lights (sharp dots -> bokeh discs)
  for (const d of BOKEH) {
    const r = lerp(3.2, d.r, b), a = lerp(.95, .5, b);
    const g = c.createRadialGradient(d.x, d.y, 0, d.x, d.y, r);
    g.addColorStop(0, rgba(d.c, a * (b > .1 ? .55 : 1))); g.addColorStop(.78, rgba(d.c, a * (b > .1 ? .7 : 1))); g.addColorStop(1, rgba(d.c, 0));
    c.fillStyle = g; c.beginPath(); c.arc(d.x, d.y, r, 0, 7); c.fill();
  }
  // person bust (sharp)
  const px = 432; c.save();
  c.fillStyle = 'rgba(0,0,0,.25)'; c.beginPath(); c.ellipse(px, 530, 190, 20, 0, 0, 7); c.fill();
  c.fillStyle = '#273447'; c.beginPath(); c.moveTo(px - 190, 540); c.quadraticCurveTo(px - 190, 400, px - 80, 372); c.lineTo(px + 80, 372); c.quadraticCurveTo(px + 190, 400, px + 190, 540); c.closePath(); c.fill();
  c.fillStyle = '#d9822b'; c.beginPath(); c.moveTo(px - 70, 372); c.lineTo(px, 450); c.lineTo(px + 70, 372); c.closePath(); c.fill();
  c.fillStyle = '#d7a283'; rr(c, px - 22, 330, 44, 56, 10); c.fill();
  c.fillStyle = '#e1ae8e'; c.beginPath(); c.ellipse(px, 292, 56, 68, 0, 0, 7); c.fill();
  c.fillStyle = '#1b1612'; c.beginPath(); c.ellipse(px, 262, 60, 54, 0, Math.PI, 0); c.fill(); c.beginPath(); c.ellipse(px - 52, 288, 12, 34, 0, 0, 7); c.fill(); c.beginPath(); c.ellipse(px + 52, 288, 12, 34, 0, 0, 7); c.fill();
  c.fillStyle = '#1a1411'; c.beginPath(); c.ellipse(px - 20, 292, 5, 6, 0, 0, 7); c.ellipse(px + 20, 292, 5, 6, 0, 0, 7); c.fill();
  c.strokeStyle = '#b9694f'; c.lineWidth = 4; c.lineCap = 'round'; c.beginPath(); c.arc(px, 316, 16, .25, Math.PI - .25); c.stroke();
  c.strokeStyle = 'rgba(255,220,150,.75)'; c.lineWidth = 3; c.beginPath(); c.arc(px, 292, 57, -.7, .5); c.stroke();
  c.restore();
  frameBox(c, px - 90, 214, 180, 190, 'rgba(61,255,170,' + (E.out(seg(u, CM.cardIn + .6, .5)) * .9) + ')', 3);
  // f-number readout + aperture icon
  const fnum = lerp(8, 1.8, E.io(seg(u, sc.fx[0] + .3, 2.0)));
  txt(c, 'f/' + (fnum < 2 ? fnum.toFixed(1) : fnum.toFixed(1)), 24, 62, { size: 56, weight: 900, color: C.gold, align: 'left', shadow: 10 });
  const ap = lerp(14, 34, E.io(seg(u, sc.fx[0] + .3, 2.0)));
  c.save(); c.translate(790, 52); c.strokeStyle = 'rgba(255,255,255,.7)'; c.lineWidth = 3; c.beginPath(); c.arc(0, 0, 38, 0, 7); c.stroke(); c.fillStyle = 'rgba(245,184,46,.9)'; c.beginPath();
  for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3 + .3; i ? c.lineTo(Math.cos(a) * ap, Math.sin(a) * ap) : c.moveTo(Math.cos(a) * ap, Math.sin(a) * ap); } c.closePath(); c.fill(); c.restore();
}
SCENES.portrait = catScene(CFG.portrait, portraitCard, (c, u, sc) => {
  quote(c, u, 'عدسات مثالية لعزل الخلفية وتصوير البورتريه', sc.quote);
  ['فتحة واسعة f/1.8', 'اقترب من الموضوع', 'ابعد الخلفية'].forEach((s, i) => {
    const a = E.out(seg(u, sc.chips[i], .5)), pop = E.back(seg(u, sc.chips[i], .6)); if (a <= 0) return; const cw = 262, gap = 39, x = SAFE.x1 - (i + 1) * cw - i * gap, cx = x + cw / 2;
    c.save(); c.globalAlpha *= a; c.translate(cx, 1546 + (1 - a) * 24); c.scale(.85 + .15 * pop, .85 + .15 * pop);
    pill(c, -cw / 2, -24, cw, 48, 'rgba(8,10,14,.95)', C.gold); c.lineWidth = 2.5;
    c.fillStyle = C.gold; c.beginPath(); c.arc(cw / 2 - 18, 0, 5, 0, 7); c.fill();
    txt(c, s, cw / 2 - 34, 9, { size: fit(c, s, 27, 900, 205), weight: 900, rtl: true, align: 'right', color: '#fff' }); c.restore();
  });
});

// ───────────────────────── Scene 6: macro ─────────────────────────
CFG.macro = { en: 'MACRO LENSES', ar: 'عدسات الماكرو', lenses: ['m60', 'm90', 'm100'], sel: 2, foot: 'Macro ليست مجرد زوم: تركيز من مسافة قريبة جدًا وتكبير حتى 1:1',
  lensState: (u, i) => ({ focus: (i === 2 ? 1 : 0) * (E.io(seg(u, 3.2, 3.8)) * 9) + u * .2 }) };
function hexFacets(c, R, a) {
  const r = 12, hh = r * Math.sqrt(3) / 2; c.save(); c.beginPath(); c.arc(0, 0, R, 0, 7); c.clip();
  for (let row = -18; row <= 18; row++) for (let col = -18; col <= 18; col++) {
    const x = col * r * 1.5, y = row * hh * 2 + (col & 1 ? hh : 0); const d = Math.hypot(x, y); if (d > R + r) continue;
    const n = d / R, sh = Math.sin(col * 1.7 + row * 2.3) * .06;
    c.beginPath(); for (let k = 0; k < 6; k++) { const aa = k * Math.PI / 3; k ? c.lineTo(x + Math.cos(aa) * r * .93, y + Math.sin(aa) * r * .93) : c.moveTo(x + Math.cos(aa) * r * .93, y + Math.sin(aa) * r * .93); } c.closePath();
    const g = c.createRadialGradient(x - r * .3, y - r * .3, 1, x, y, r); g.addColorStop(0, `rgba(255,200,170,${.95 * a})`); g.addColorStop(1, `rgba(${150 - n * 70 + sh * 200},${20},${24},${a})`); c.fillStyle = g; c.fill();
  }
  c.restore();
}
function drawFly(c) {
  c.save();
  c.strokeStyle = '#141a14'; c.lineWidth = 2; for (const [sx, sy, ex, ey] of [[-8, -4, -34, -22], [-8, 4, -36, 18], [0, -6, 6, -34], [0, 8, 10, 34], [10, -4, 36, -24], [10, 4, 38, 20]]) { c.beginPath(); c.moveTo(sx, sy); c.lineTo(ex, ey); c.stroke(); }
  c.fillStyle = 'rgba(190,225,235,.35)'; c.strokeStyle = 'rgba(255,255,255,.4)'; c.lineWidth = 1; for (const s of [-1, 1]) { c.beginPath(); c.ellipse(24, s * 18, 38, 12, s * .35, 0, 7); c.fill(); c.stroke(); }
  const gb = c.createLinearGradient(0, -20, 0, 20); gb.addColorStop(0, '#2c6b6a'); gb.addColorStop(1, '#0d1f2a');
  c.fillStyle = gb; c.beginPath(); c.ellipse(34, 0, 34, 17, 0, 0, 7); c.fill(); c.beginPath(); c.ellipse(0, 0, 18, 15, 0, 0, 7); c.fill();
  c.fillStyle = '#1e5a58'; c.beginPath(); c.arc(-24, 0, 13, 0, 7); c.fill();
  const ge = c.createRadialGradient(-26, -4, 1, -24, -2, 11); ge.addColorStop(0, '#ff9a7a'); ge.addColorStop(.6, '#c2282b'); ge.addColorStop(1, '#5c0d12');
  c.fillStyle = ge; c.beginPath(); c.ellipse(-26, -9, 7, 8.5, .3, 0, 7); c.fill(); c.beginPath(); c.ellipse(-26, 9, 7, 8.5, -.3, 0, 7); c.fill();
  c.restore();
}
SCENES.macro = catScene(CFG.macro, (c, u, w, h, sc) => {
  const t = E.io(seg(u, sc.fx[0], sc.fx[1] - sc.fx[0])), S = Math.exp(lerp(0, Math.log(16), t));
  const ex = 432 - 26, ey = 262 - 9;                       // eye in world coords (fly at 432,262)
  const bg = c.createLinearGradient(0, 0, 0, h); bg.addColorStop(0, '#1d4a2f'); bg.addColorStop(1, '#0e2a1b'); c.fillStyle = bg; c.fillRect(0, 0, w, h);
  c.save(); const foc = E.io(seg(u, sc.fx[0] + .6, 3.2)); const bl = (1 - foc) * 7 * (t > 0 ? 1 : 0); if (bl > .3) c.filter = `blur(${bl}px)`;
  c.translate(432, 262); c.scale(S, S); c.translate(-ex, -ey);
  // leaf
  const lg = c.createLinearGradient(100, 100, 760, 420); lg.addColorStop(0, '#4fa05a'); lg.addColorStop(1, '#2c7440');
  c.fillStyle = lg; c.beginPath(); c.moveTo(60, 330); c.bezierCurveTo(200, 60, 640, 40, 820, 250); c.bezierCurveTo(650, 470, 220, 520, 60, 330); c.closePath(); c.fill();
  c.strokeStyle = 'rgba(200,255,200,.45)'; c.lineWidth = 3 / Math.sqrt(S); c.beginPath(); c.moveTo(60, 330); c.quadraticCurveTo(400, 250, 820, 250); c.stroke();
  for (let i = 0; i < 7; i++) { const x = 160 + i * 90; c.lineWidth = 1.8 / Math.sqrt(S); c.beginPath(); c.moveTo(x, 285 - i * 3); c.quadraticCurveTo(x + 40, 190 - i * 12, x + 90, 140); c.moveTo(x, 285 - i * 3); c.quadraticCurveTo(x + 40, 370 + i * 8, x + 90, 410); c.stroke(); }
  // dew drops
  c.fillStyle = 'rgba(255,255,255,.22)'; for (const [x, y, r] of [[250, 220, 7], [560, 340, 9], [640, 180, 6], [330, 380, 5]]) { c.beginPath(); c.arc(x, y, r, 0, 7); c.fill(); }
  c.save(); c.translate(432, 262); c.rotate(-.1); drawFly(c); c.restore();
  c.restore();
  // faceted compound-eye close-up
  const fa = clamp((S - 4.5) / 8); if (fa > 0) {
    c.save(); c.translate(432, 262); c.globalAlpha *= fa;
    const R = Math.min(170, 9 * S); c.fillStyle = '#2a0a0e'; c.beginPath(); c.arc(0, 0, R + 5, 0, 7); c.fill(); hexFacets(c, R, 1);
    c.strokeStyle = 'rgba(20,10,10,.9)'; c.lineWidth = 6; c.beginPath(); c.arc(0, 0, R + 3, 0, 7); c.stroke();
    // bristles
    c.strokeStyle = 'rgba(20,30,20,.9)'; c.lineWidth = 3; c.lineCap = 'round'; for (let i = 0; i < 18; i++) { const a = -Math.PI * .95 + i * .13, r0 = R + 2; c.beginPath(); c.moveTo(Math.cos(a) * r0, Math.sin(a) * r0); c.lineTo(Math.cos(a) * (r0 + 28 + (i % 3) * 14), Math.sin(a) * (r0 + 28 + (i % 3) * 14)); c.stroke(); }
    c.restore();
  }
  // viewfinder brackets + magnification
  frameBox(c, 32, 32, w - 64, h - 64, 'rgba(255,255,255,.35)', 2);
  const bd = E.out(seg(u, sc.badge, .6));
  if (bd > 0) { c.save(); c.globalAlpha *= bd; c.translate(432, 470 + (1 - bd) * 20); pill(c, -170, -30, 340, 60, 'rgba(8,10,14,.85)', C.gold); txt(c, '1:1 Magnification', 0, 11, { size: 31, weight: 900, color: C.gold }); c.restore(); }
  txt(c, 'MACRO', 52, 74, { size: 22, color: C.dim, align: 'left', ls: 6 });
  txt(c, (S < 1.05 ? '×1' : '×' + S.toFixed(1)), w - 52, 78, { size: 40, weight: 900, color: C.gold, align: 'right' });
}, (c, u, sc) => quote(c, u, 'اكتشف تفاصيل لا تراها العين بسهولة', sc.quote));

// ───────────────────────── Scene 7: telephoto zoom ─────────────────────────
CFG.tele = { en: 'TELEPHOTO ZOOM', ar: 'عدسات التيليفوتو زوم', lenses: ['z70200', 'z100400', 'z150600'], zoom: true, sel: 0, foot: 'الزوم يضيّق الإطار فقط — المنظور لا يتغير ما دامت الكاميرا في مكانها',
  lensState: (u, i) => { const t = E.io(seg(u, 3.4, 3.4)); return i === 0 ? { zoom: t * 6, ext: t } : {}; } };
SCENES.tele = catScene(CFG.tele, (c, u, w, h, sc) => {
  const t = E.io(seg(u, sc.fx[0], sc.fx[1] - sc.fx[0])), f = lerp(70, 200, t), S = f / 70;
  const px = 470, py = 330;
  c.save(); c.translate(432, 262); c.scale(S, S); c.translate(-px, -py);
  skyGrad(c, 864 + 600, 160, '#243656', '#5a77a6', '#9fb3d1'); c.save(); c.translate(-300, 0); skyGrad(c, 1464, 160, '#243656', '#5a77a6', '#9fb3d1'); c.restore();
  // stands with crowd
  const R = rng(9); c.fillStyle = '#2a3140'; c.fillRect(-300, 120, 1464, 120);
  for (let i = 0; i < 520; i++) { c.fillStyle = ['#e5594f', '#f2c14e', '#4fa3e5', '#e8e8f0', '#6bd09a'][i % 5]; c.globalAlpha = .75; c.beginPath(); c.arc(-300 + R() * 1464, 130 + R() * 100, 2.6, 0, 7); c.fill(); } c.globalAlpha = 1;
  // pitch
  for (let i = 0; i < 12; i++) { c.fillStyle = i % 2 ? '#2f8a4b' : '#35984f'; c.fillRect(-300 + i * 122, 240, 122, 420); }
  c.strokeStyle = 'rgba(255,255,255,.75)'; c.lineWidth = 3; c.strokeRect(-100, 270, 1064, 300); c.beginPath(); c.moveTo(432, 270); c.lineTo(432, 570); c.stroke(); c.beginPath(); c.arc(432, 420, 54, 0, 7); c.stroke();
  c.strokeRect(-100, 340, 120, 160); c.strokeRect(844, 340, 120, 160);
  // player
  person(c, px, py + 36, 62, { jacket: '#e5594f' }); c.fillStyle = '#fff'; c.beginPath(); c.arc(px + 22, py + 32, 6, 0, 7); c.fill(); c.strokeStyle = '#111'; c.lineWidth = 1.2; c.stroke();
  c.restore();
  // ghost target frame
  const gh = 1 - E.out(seg(u, sc.fx[1] - .2, .6)); c.save(); c.globalAlpha *= gh * .8; c.setLineDash([10, 8]); c.strokeStyle = C.gold; c.lineWidth = 2.5; c.strokeRect(432 - 864 / 2.86 / 2, 262 - 520 / 2.86 / 2 + 0, 864 / 2.86, 520 / 2.86); c.restore();
  // viewfinder UI
  frameBox(c, 28, 28, w - 56, h - 56, 'rgba(255,255,255,.45)', 3);
  c.strokeStyle = 'rgba(61,255,170,.85)'; c.lineWidth = 2.5; c.strokeRect(432 - 20, 262 - 20, 40, 40);
  txt(c, Math.round(f) + 'mm', 56, h - 54, { size: 68, weight: 900, color: C.gold, align: 'left', shadow: 12 });
  txt(c, '70–200mm', w - 56, h - 62, { size: 26, color: C.dim, align: 'right', ls: 2 });
  txt(c, '×' + S.toFixed(1), w - 56, 84, { size: 40, weight: 900, color: C.white, align: 'right' });
}, (c, u, sc) => quote(c, u, 'للرياضة والأحداث والموضوعات البعيدة', sc.quote));

// ───────────────────────── Scene 8: wildlife super-tele ─────────────────────────
CFG.super = { en: 'WILDLIFE · SUPER TELEPHOTO', ar: 'عدسات السوبر تيليفوتو', lenses: ['t400', 't600', 't800'], sel: 1, foot: 'طول بؤري أكبر لا يعني جودة صورة أعلى — بل مجال رؤية أضيق' ,
  lensState: (u, i) => ({ focus: i === 1 ? E.io(seg(u, 3.0, 2.6)) * 5 + u * .3 : u * .2 }) };
function drawBird(c) {
  c.save();
  c.fillStyle = '#24412c'; c.beginPath(); c.moveTo(-80, 12); c.lineTo(80, -2); c.lineTo(80, 4); c.lineTo(-80, 20); c.fill();               // branch
  c.strokeStyle = '#1f3a28'; c.lineWidth = 3; c.beginPath(); c.moveTo(30, 6); c.quadraticCurveTo(50, -10, 70, -20); c.stroke();
  c.fillStyle = '#e8743b'; c.beginPath(); c.ellipse(0, -14, 22, 17, -.2, 0, 7); c.fill();                                              // body
  const gb = c.createLinearGradient(-20, -34, 10, 0); gb.addColorStop(0, '#3a97d1'); gb.addColorStop(1, '#1f5d92'); c.fillStyle = gb; c.beginPath(); c.ellipse(4, -19, 21, 11, -.2, 0, 7); c.fill();
  c.fillStyle = '#1f5d92'; c.beginPath(); c.moveTo(14, -6); c.lineTo(46, 8); c.lineTo(38, 14); c.lineTo(10, 2); c.closePath(); c.fill();     // tail
  c.fillStyle = '#e8743b'; c.beginPath(); c.arc(-20, -26, 11, 0, 7); c.fill(); c.fillStyle = '#3a97d1'; c.beginPath(); c.arc(-18, -31, 9, Math.PI, 0); c.fill();
  c.fillStyle = '#1a1a1a'; c.beginPath(); c.moveTo(-30, -27); c.lineTo(-52, -24); c.lineTo(-30, -22); c.closePath(); c.fill();       // beak
  c.fillStyle = '#fff'; c.beginPath(); c.arc(-23, -28, 3.2, 0, 7); c.fill(); c.fillStyle = '#000'; c.beginPath(); c.arc(-23.5, -28, 1.9, 0, 7); c.fill();
  c.restore();
}
SCENES.super = catScene(CFG.super, (c, u, w, h, sc) => {
  const t = E.io(seg(u, sc.fx[0], sc.fx[1] - sc.fx[0])), S = Math.exp(lerp(0, Math.log(5.4), t));
  const bx = 432, by = 262, eyeX = bx - 23, eyeY = by - 28;
  const bg = c.createLinearGradient(0, 0, 0, h); bg.addColorStop(0, '#5aa6b9'); bg.addColorStop(.6, '#2e6f58'); bg.addColorStop(1, '#173f2d'); c.fillStyle = bg; c.fillRect(0, 0, w, h);
  const R = rng(3); for (let i = 0; i < 26; i++) { const g = c.createRadialGradient(0, 0, 0, 0, 0, 1); const x = R() * w, y = R() * h, r = 26 + R() * 44; c.fillStyle = `rgba(${200 + R() * 55},${230},${180},${.05 + R() * .08})`; c.beginPath(); c.arc(x, y, r, 0, 7); c.fill(); }
  c.save(); c.translate(432, 262); c.scale(S, S); c.translate(-eyeX, -eyeY); c.translate(bx, by); drawBird(c); c.restore();
  // far background layer lines to hint distance
  frameBox(c, 28, 28, w - 56, h - 56, 'rgba(255,255,255,.45)', 3);
  const eyeS = [432, 262];
  // AF: wide zone -> grid -> eye lock
  const a1 = E.out(seg(u, sc.af[0] - .5, .4)), lock = E.out(seg(u, sc.af[1] - .5, .5));
  if (a1 > 0 && u < sc.burst[1] + .5) {
    const bw = lerp(300, 74, lock), bh = lerp(230, 74, lock), jit = (1 - lock) * Math.sin(u * 23) * 6;
    c.save(); c.globalAlpha *= a1; const col = lock > .95 ? '#3dffaa' : '#ffffff';
    if (lock < .98) for (let i = -4; i <= 4; i++) for (let j = -3; j <= 3; j++) { c.strokeStyle = 'rgba(255,255,255,.35)'; c.lineWidth = 1.5; c.strokeRect(432 + i * 36 - 6 + jit, 262 + j * 32 - 6, 12, 12); }
    c.shadowColor = col; c.shadowBlur = lock > .95 ? 16 : 0; frameBox(c, 432 - bw / 2 + jit, 262 - bh / 2, bw, bh, col, 4); c.restore();
    if (lock > .95) { const p = E.out(seg(u, sc.af[1], .5)); c.save(); c.strokeStyle = `rgba(61,255,170,${.8 * (1 - p)})`; c.lineWidth = 3; c.beginPath(); c.arc(432, 262, 40 + p * 90, 0, 7); c.stroke(); c.restore(); txt(c, 'AF ●', 56, 84, { size: 34, weight: 900, color: '#3dffaa', align: 'left' }); }
    else txt(c, 'AF', 56, 84, { size: 34, weight: 900, color: '#fff', align: 'left', alpha: .8 });
  }
  const fv = lerp(fovDiag(50), fovDiag(600), t);
  txt(c, 'FOV ' + fv.toFixed(1) + '°', w - 56, 84, { size: 36, weight: 900, color: C.teal, align: 'right' });
  txt(c, (t < .02 ? '50mm' : Math.round(lerp(50, 600, t)) + 'mm'), 56, h - 54, { size: 64, weight: 900, color: C.gold, align: 'left', shadow: 12 });
  // burst flashes
  if (u > sc.burst[0] && u < sc.burst[1]) { const ph = ((u - sc.burst[0]) * 10) % 1; c.fillStyle = `rgba(255,255,255,${.3 * Math.pow(1 - ph, 3)})`; c.fillRect(0, 0, w, h); txt(c, 'BURST', w - 56, h - 54, { size: 34, weight: 900, color: '#fff', align: 'right', ls: 4 }); }
}, (c, u, sc) => quote(c, u, 'اقترب بصريًا من الحياة البرية دون إزعاجها', sc.quote));

// ───────────────────────── Scene 9: guide / comparison ─────────────────────────
function icon(c, k, x, y, s) {
  c.save(); c.translate(x, y); c.scale(s, s); c.strokeStyle = C.gold; c.fillStyle = C.gold; c.lineWidth = 3.5; c.lineCap = 'round'; c.lineJoin = 'round';
  if (k === 0) { c.beginPath(); c.arc(0, 0, 22, 0, 7); c.stroke(); c.beginPath(); c.moveTo(-22, 0); c.quadraticCurveTo(0, -12, 22, 0); c.moveTo(-22, 0); c.quadraticCurveTo(0, 12, 22, 0); c.moveTo(0, -22); c.quadraticCurveTo(-12, 0, 0, 22); c.moveTo(0, -22); c.quadraticCurveTo(12, 0, 0, 22); c.stroke(); }
  if (k === 1) { c.beginPath(); c.moveTo(-26, 18); c.lineTo(-8, -10); c.lineTo(4, 6); c.lineTo(14, -6); c.lineTo(28, 18); c.closePath(); c.stroke(); c.beginPath(); c.arc(14, -18, 5, 0, 7); c.fill(); }
  if (k === 2) { c.strokeRect(-24, -12, 18, 30); c.strokeRect(2, -22, 22, 40); c.beginPath(); c.moveTo(-28, 18); c.lineTo(28, 18); c.stroke(); }
  if (k === 3) { c.beginPath(); c.arc(0, -8, 11, 0, 7); c.stroke(); c.beginPath(); c.moveTo(-22, 22); c.quadraticCurveTo(-20, 4, 0, 4); c.quadraticCurveTo(20, 4, 22, 22); c.stroke(); }
  if (k === 4) { c.beginPath(); c.arc(-4, -4, 15, 0, 7); c.stroke(); c.beginPath(); c.moveTo(7, 7); c.lineTo(22, 22); c.stroke(); c.beginPath(); c.arc(-4, -4, 4, 0, 7); c.fill(); }
  if (k === 5) { c.beginPath(); c.arc(0, 0, 22, 0, 7); c.stroke(); c.beginPath(); c.moveTo(0, -8); c.lineTo(8, -2); c.lineTo(5, 7); c.lineTo(-5, 7); c.lineTo(-8, -2); c.closePath(); c.stroke(); c.beginPath(); c.moveTo(0, -8); c.lineTo(0, -22); c.moveTo(8, -2); c.lineTo(21, -7); c.moveTo(5, 7); c.lineTo(13, 18); c.moveTo(-5, 7); c.lineTo(-13, 18); c.moveTo(-8, -2); c.lineTo(-21, -7); c.stroke(); }
  if (k === 6) { c.beginPath(); c.ellipse(-2, 2, 18, 11, -.2, 0, 7); c.stroke(); c.beginPath(); c.arc(-18, -8, 8, 0, 7); c.stroke(); c.beginPath(); c.moveTo(-26, -9); c.lineTo(-34, -6); c.lineTo(-26, -5); c.stroke(); c.beginPath(); c.moveTo(14, 6); c.lineTo(30, 14); c.stroke(); c.beginPath(); c.moveTo(-6, 12); c.lineTo(-8, 22); c.moveTo(4, 12); c.lineTo(4, 22); c.stroke(); }
  c.restore();
}
const GUIDE = [
  { n: 'Fish-eye', ar: 'إبداعي', tag: 'متخصص', v: .30 }, { n: 'Ultra Wide', ar: 'مناظر ومعمار', tag: 'متعدد الاستخدامات', v: .62 },
  { n: '35mm', ar: 'شارع وتوثيق', tag: 'متعدد الاستخدامات', v: .86, star: 1 }, { n: '85mm', ar: 'بورتريه', tag: 'متخصص', v: .74 },
  { n: 'Macro', ar: 'تفاصيل دقيقة', tag: 'متخصص', v: .48 }, { n: '70–200mm', ar: 'رياضة', tag: 'احترافي', v: .58 }, { n: '600mm', ar: 'حياة برية', tag: 'احترافي', v: .36 },
];
SCENES.guide = (c, u, sc) => {
  const a0 = E.out(seg(u, .05, .6));
  c.save(); c.globalAlpha *= a0; txt(c, 'QUICK GUIDE', SAFE.x0, 272, { size: 26, color: C.gold, align: 'left', ls: 5 }); txt(c, 'ماذا تصوّر بكل عدسة؟', 540, 352, { size: 68, weight: 900, rtl: true, shadow: 12 }); c.restore();
  const y0 = 530, dy = 150;
  txt(c, 'شائع بين المصورين (مؤشر توضيحي)', 140, 462, { size: 24, rtl: true, color: C.dim, alpha: a0, align: 'left' });
  GUIDE.forEach((g, i) => {
    const t0 = sc.rows[0] + i * sc.rows[1] * .55, a = E.out(seg(u, t0 * .6 + .2 + i * .42, .6)); if (a <= 0) return;
    const cy = y0 + i * dy; c.save(); c.globalAlpha *= a; c.translate((1 - a) * 120, 0);
    rr(c, SAFE.x0, cy - 54, 864, 112, 24); c.fillStyle = 'rgba(255,255,255,.04)'; c.fill(); c.strokeStyle = 'rgba(255,255,255,.1)'; c.lineWidth = 1.5; c.stroke();
    c.beginPath(); c.arc(920, cy, 40, 0, 7); c.fillStyle = 'rgba(245,184,46,.12)'; c.fill(); c.strokeStyle = 'rgba(245,184,46,.6)'; c.lineWidth = 2; c.stroke(); icon(c, i, 920, cy, .8);
    txt(c, g.n, 858, cy - 4, { size: 38, weight: 900, align: 'right' }); txt(c, g.ar, 858, cy + 36, { size: 28, color: C.gold, rtl: true, align: 'right' });
    const bw = 300, bx = 140, bb = E.out(seg(u, t0 * .6 + .5 + i * .42, .9));
    rr(c, bx, cy + 8, bw, 16, 8); c.fillStyle = 'rgba(255,255,255,.08)'; c.fill();
    const bg = c.createLinearGradient(bx, 0, bx + bw, 0); bg.addColorStop(0, '#b07d12'); bg.addColorStop(1, '#ffd877'); rr(c, bx, cy + 8, Math.max(16, bw * g.v * bb), 16, 8); c.fillStyle = bg; c.fill();
    const tcol = g.tag === 'احترافي' ? '#9db7ff' : g.tag === 'متخصص' ? C.teal : C.gold; const tww = tw(c, g.tag, 22, 700) + 26;
    pill(c, bx, cy - 40, tww, 34, rgba(tcol, .14), rgba(tcol, .8)); txt(c, g.tag, bx + tww / 2, cy - 15, { size: 22, rtl: true, color: tcol });
    if (g.star) { const sw = tw(c, 'مناسبة للبدء', 22, 700) + 26; pill(c, bx + tww + 12, cy - 40, sw, 34, 'rgba(61,255,170,.12)', 'rgba(61,255,170,.8)'); txt(c, 'مناسبة للبدء', bx + tww + 12 + sw / 2, cy - 15, { size: 22, rtl: true, color: '#3dffaa' }); }
    c.restore();
  });
  const fa = E.out(seg(u, 5.2, .6)); txt(c, 'المؤشرات توضيحية فقط — وليست إحصاءات مبيعات أو انتشار', 540, 1548, { size: 24, rtl: true, color: 'rgba(242,244,248,.6)', alpha: fa });
  const lg = E.out(seg(u, 5.6, .6)); txt(c, 'Prime ثابتة  ·  Zoom متغيرة  —  اختر بحسب ما تصوّره', 540, 1604, { size: 28, rtl: true, color: C.white, alpha: lg });
};

// ───────────────────────── Scene 10: outro ─────────────────────────
const LINEUP = ['fe8', 'uw14', 'w24', 'w35', 's50', 'p85', 'm100', 'z70200', 'z100400', 't600', 't800'];
const LINE_LBL = ['8', '14', '24', '35', '50', '85', '100', '70–200', '100–400', '600', '800'];
SCENES.outro = (c, u) => {
  const kG = .86, gap = 70; let wx = 0; const pos = LINEUP.map(k => { const s = lensSize(k), w = Math.max(s.W, 80) * kG; const x = wx + w / 2; wx += w + gap; return { x, w }; });
  const total = wx - gap;
  const pan = E.io(seg(u, 0, 1.6)), pull = E.io(seg(u, 1.5, 1.0));
  const Zfin = 864 / total, Z = lerp(1, Zfin, pull);
  const camStart = pos[0].x - 300, camEnd = pos[pos.length - 1].x - 240, camFin = total / 2;
  const cam = lerp(lerp(camStart, camEnd, pan), camFin, pull);
  const floorY = lerp(1250, 1150, pull), vel = Math.abs(Math.sin(Math.PI * seg(u, 0, 1.6))) * (1 - pull);
  c.save();
  c.strokeStyle = 'rgba(245,184,46,.5)'; c.lineWidth = 2; c.beginPath(); c.moveTo(0, floorY + 8); c.lineTo(W, floorY + 8); c.stroke();
  LINEUP.forEach((k, i) => {
    const x = 540 + (pos[i].x - cam) * Z; if (x < -250 || x > W + 250) return;
    drawLens(c, k, { x, y: floorY, k: kG * Z, lean: 0, pitch: 18, blur: vel * 14, rot: { focus: i + u, zoom: i } });
    const sz = Math.max(21, 40 * Z + 2), lab = LINE_LBL[i], dy2 = pull > .5 && i % 2 ? sz + 8 : 0;
    txt(c, lab, x, floorY + 48 + sz * .6 + dy2 * pull, { size: sz, weight: 900, color: C.gold, ls: 0, alpha: .95 });
  });
  c.restore();
  txt(c, 'mm', 540, floorY + 160, { size: 22, color: C.dim, ls: 4, alpha: pull });
  txt(c, 'من الأقصر إلى الأطول', 540, floorY + 205, { size: 26, rtl: true, color: C.dim, alpha: pull });
  let a = E.out(seg(u, 1.6, .7));
  wrap(c, 'العدسة المناسبة أهم من العدسة الأغلى!', 66, 900, 800).forEach((l, i) => txt(c, l, 540, 540 + i * 88 + (1 - a) * 30, { size: 66, weight: 900, rtl: true, alpha: a, shadow: 14 }));
  a = E.out(seg(u, 2.35, .7)); txt(c, 'وأنت… أي عدسة تستخدم أكثر؟', 540, 790 + (1 - a) * 30, { size: 54, weight: 900, rtl: true, color: C.gold, alpha: a, shadow: 14 });
  a = E.out(seg(u, 3.0, .7));
  c.save(); c.globalAlpha *= a; cameraIcon(c, 540, 1458, 1.25, C.gold); txt(c, 'walidphotoz', 540, 1540, { size: 56, weight: 700, ls: 8 }); c.fillStyle = C.gold; c.fillRect(540 - 130 * a, 1558, 260 * a, 3); c.restore();
};
