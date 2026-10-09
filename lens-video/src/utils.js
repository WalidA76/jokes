// Shared helpers: constants, easing, colour, text, background
const W = 1080, H = 1920;
const SAFE = { x0: 108, x1: 972, y0: 230, y1: 1632 };           // top 12% / bottom 15% / sides 10%
const C = { gold: '#F5B82E', goldSoft: '#ffd877', teal: '#38d6c4', white: '#f2f4f8', dim: 'rgba(242,244,248,.62)' };
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (u, a, d) => clamp((u - a) / d);
const E = {
  io: t => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  out: t => 1 - Math.pow(1 - t, 3),
  expo: t => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t)),
  back: t => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  sine: t => 0.5 - 0.5 * Math.cos(Math.PI * t),
};
function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

function hex(c) { const n = parseInt(c.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
function rgba(c, a = 1) { const [r, g, b] = Array.isArray(c) ? c : hex(c); return `rgba(${r | 0},${g | 0},${b | 0},${a})`; }
function mix(a, b, t) { const A = Array.isArray(a) ? a : hex(a), B = Array.isArray(b) ? b : hex(b); return [lerp(A[0], B[0], t), lerp(A[1], B[1], t), lerp(A[2], B[2], t)]; }
function shade(c, f) { const A = Array.isArray(c) ? c : hex(c); return [clamp(A[0] * f, 0, 255), clamp(A[1] * f, 0, 255), clamp(A[2] * f, 0, 255)]; }

function txt(ctx, s, x, y, o = {}) {
  const { size = 32, weight = 700, color = '#fff', align = 'center', rtl = false, ls = 0, alpha = 1, baseline = 'alphabetic' } = o;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.font = `${weight} ${size}px Cairo, sans-serif`;
  ctx.direction = rtl ? 'rtl' : 'ltr';
  ctx.letterSpacing = ls + 'px';
  ctx.textAlign = align; ctx.textBaseline = baseline;
  if (o.shadow) { ctx.shadowColor = 'rgba(0,0,0,.55)'; ctx.shadowBlur = o.shadow; }
  ctx.fillStyle = color;
  ctx.fillText(s, x, y);
  ctx.restore();
}
function tw(ctx, s, size, weight = 700) { ctx.save(); ctx.font = `${weight} ${size}px Cairo, sans-serif`; const w = ctx.measureText(s).width; ctx.restore(); return w; }
function wrap(ctx, s, size, weight, maxW) {
  const words = s.split(' '); const lines = []; let cur = '';
  for (const w of words) { const t = cur ? cur + ' ' + w : w; if (tw(ctx, t, size, weight) > maxW && cur) { lines.push(cur); cur = w; } else cur = t; }
  if (cur) lines.push(cur); return lines;
}
function rr(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function pill(ctx, x, y, w, h, fill, stroke) { rr(ctx, x, y, w, h, h / 2); if (fill) { ctx.fillStyle = fill; ctx.fill(); } if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = 2; ctx.stroke(); } }

function drawBackground(ctx, t) {
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#0a0c10'); g.addColorStop(.45, '#161a22'); g.addColorStop(1, '#090b0e');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const rg = ctx.createRadialGradient(540, 820, 20, 540, 820, 900);
  rg.addColorStop(0, 'rgba(245,184,46,.07)'); rg.addColorStop(.5, 'rgba(60,90,130,.05)'); rg.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = rg; ctx.fillRect(0, 0, W, H);
  // technical grid
  ctx.save();
  const off = (t * 7) % 60;
  ctx.lineWidth = 1;
  for (let x = 0; x <= W; x += 60) { ctx.strokeStyle = (x / 60) % 5 === 0 ? 'rgba(255,255,255,.055)' : 'rgba(255,255,255,.028)'; ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = -60; y <= H; y += 60) { const yy = y + off; ctx.strokeStyle = 'rgba(255,255,255,.03)'; ctx.beginPath(); ctx.moveTo(0, yy); ctx.lineTo(W, yy); ctx.stroke(); }
  ctx.restore();
  // viewfinder corner marks
  ctx.save(); ctx.strokeStyle = 'rgba(245,184,46,.5)'; ctx.lineWidth = 3;
  const m = 56, l = 44;
  for (const [cx, cy, sx, sy] of [[m, m, 1, 1], [W - m, m, -1, 1], [m, H - m, 1, -1], [W - m, H - m, -1, -1]]) { ctx.beginPath(); ctx.moveTo(cx, cy + sy * l); ctx.lineTo(cx, cy); ctx.lineTo(cx + sx * l, cy); ctx.stroke(); }
  ctx.restore();
  // vignette
  const v = ctx.createRadialGradient(540, 960, 600, 540, 960, 1250);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,.55)');
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
}
const fovDiag = f => 2 * Math.atan(43.27 / (2 * f)) * 180 / Math.PI;   // full-frame diagonal angle of view
