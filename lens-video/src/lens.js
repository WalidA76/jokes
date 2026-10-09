// Procedural 2.5D lens renderer: a lens is a surface of revolution projected orthographically.
const MAT = {
  black: [34, 36, 43], grip: [26, 28, 34], metal: [176, 182, 193], gold: [245, 184, 46], dark: [62, 65, 74], hood: [22, 23, 28],
};
const LENS = {
  fe8:  { L: 82,  D: 76, kind: 'fisheye', label: '8mm' },
  fe10: { L: 90,  D: 78, kind: 'fisheye', label: '10mm' },
  fe12: { L: 98,  D: 80, kind: 'fisheye', label: '12mm' },
  uw14: { L: 100, D: 84, kind: 'wide', hood: 1, label: '14mm' },
  uw16: { L: 90,  D: 80, kind: 'wide', hood: 1, label: '16mm' },
  uw20: { L: 85,  D: 77, kind: 'wide', hood: 1, label: '20mm' },
  w24:  { L: 78,  D: 76, kind: 'prime', label: '24mm' },
  w35:  { L: 80,  D: 72, kind: 'prime', label: '35mm' },
  s50:  { L: 72,  D: 70, kind: 'prime', label: '50mm' },
  p85:  { L: 92,  D: 82, kind: 'prime', label: '85mm' },
  p105: { L: 112, D: 85, kind: 'prime', label: '105mm' },
  p135: { L: 128, D: 90, kind: 'prime', label: '135mm' },
  m60:  { L: 72,  D: 70, kind: 'macro', label: '60mm' },
  m90:  { L: 122, D: 78, kind: 'macro', label: '90mm' },
  m100: { L: 128, D: 78, kind: 'macro', label: '100mm' },
  z70200:  { L: 200, D: 88,  kind: 'zoom', hood: 1, label: '70–200mm' },
  z100400: { L: 205, D: 94,  kind: 'zoom', hood: 1, label: '100–400mm' },
  z150600: { L: 260, D: 105, kind: 'zoom', hood: 1, label: '150–600mm' },
  t400: { L: 250, D: 115, kind: 'super', label: '400mm' },
  t600: { L: 450, D: 165, kind: 'super', label: '600mm' },
  t800: { L: 470, D: 160, kind: 'super', label: '800mm' },
};

function buildProfile(sp) {
  const L = sp.L, D = sp.D, R = D / 2, S = [];
  const add = (f, r0, r1, mat, role, ribs) => S.push({ l: f * L, r0, r1, mat, role, ribs });
  if (sp.kind === 'fisheye') {
    add(.07, .40 * R, .40 * R, 'metal');
    add(.14, .92 * R, .98 * R, 'black');
    add(.22, R, R, 'grip', 'focus', 30);
    add(.05, 1.0 * R, 1.0 * R, 'metal');
    add(.12, 1.0 * R, 1.02 * R, 'black');
    add(.02, 1.03 * R, 1.03 * R, 'gold');
    add(.30, 1.05 * R, 1.30 * R, 'hood');            // petal hood around the bulbous front element
    S.dome = 1.0 * R;
    return S;
  }
  add(.05, .40 * R, .40 * R, 'metal');
  add(.09, .92 * R, .98 * R, 'black');
  if (sp.kind === 'zoom') {
    add(.28, R, R, 'grip', 'zoom', 40);
    add(.10, R, R, 'black');
    add(.16, R, R, 'grip', 'focus', 28);
    add(.015, 1.02 * R, 1.02 * R, 'metal');
    S.push({ l: .17 * L, r0: .93 * R, r1: .93 * R, mat: 'dark', ext: true });
  } else if (sp.kind === 'macro') {
    add(.30, R, R, 'grip', 'focus', 44);
    add(.14, R, R, 'black');
    add(.02, 1.02 * R, 1.02 * R, 'metal');
    add(.28, .96 * R, .92 * R, 'black');
  } else if (sp.kind === 'super') {
    add(.14, R * .94, R, 'black');
    add(.08, R, R, 'grip', 'focus', 36);
    add(.06, R * 1.06, R * 1.06, 'metal');
    add(.05, R * 1.08, R * 1.08, 'black');
    add(.30, R, .92 * R, 'black');
    add(.015, .93 * R, .93 * R, 'gold');
  } else {
    add(.26, R, R, 'grip', 'focus', 36);
    add(.12, R, R, 'black');
    add(.02, 1.02 * R, 1.02 * R, 'metal');
    add(.24, .98 * R, .94 * R, 'black');
  }
  add(.014, .95 * R * (sp.kind === 'super' ? 1 : 1), .95 * R, 'gold');
  add(.07, .93 * R, .88 * R, 'black');
  if (sp.hood || sp.kind === 'super') add(sp.kind === 'super' ? .17 : .14, .90 * R, 1.16 * R, 'hood');
  return S;
}
const _profCache = {};
function profileOf(key) { return _profCache[key] || (_profCache[key] = buildProfile(LENS[key])); }
function lensSize(key) { const sp = LENS[key]; const p = profileOf(key); const maxR = Math.max(...p.map(s => Math.max(s.r0, s.r1)), p.dome || 0); return { L: p.reduce((a, s) => a + s.l, 0), W: maxR * 2 }; }

// o: {x,y,k,lean(deg),pitch(deg),rot:{focus,zoom},ext,alpha,blur,glow}
function drawLens(ctx, key, o) {
  const sp = LENS[key], prof = profileOf(key);
  const k = o.k, lean = (o.lean || 0) * Math.PI / 180, pitch = (o.pitch == null ? 20 : o.pitch) * Math.PI / 180;
  const cp = Math.cos(pitch), spn = Math.sin(pitch);
  const dx = Math.sin(lean), dy = -Math.cos(lean), mx = Math.cos(lean), my = Math.sin(lean);
  const rot = o.rot || {}, ext = o.ext || 0;
  const cen = s => [o.x + s * k * cp * dx, o.y + s * k * cp * dy];
  ctx.save();
  ctx.globalAlpha *= (o.alpha == null ? 1 : o.alpha);
  if (o.blur > 0.3) ctx.filter = `blur(${o.blur}px)`;
  // contact shadow + glow
  const maxR = Math.max(...prof.map(s => Math.max(s.r0, s.r1))) * k;
  ctx.save(); ctx.translate(o.x, o.y + 4); ctx.scale(1, .22 + spn * .12);
  const sg = ctx.createRadialGradient(0, 0, maxR * .2, 0, 0, maxR * 1.45);
  sg.addColorStop(0, o.glow ? 'rgba(245,184,46,.45)' : 'rgba(0,0,0,.65)'); sg.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = sg; ctx.beginPath(); ctx.arc(0, 0, maxR * 1.45, 0, 7); ctx.fill(); ctx.restore();

  let s = 0;
  const ellipsePath = (c, r) => { ctx.beginPath(); ctx.ellipse(c[0], c[1], r * k, r * k * spn, lean, 0, Math.PI * 2); };
  const arc = (c, r, a0, a1) => { ctx.beginPath(); for (let i = 0; i <= 28; i++) { const th = a0 + (a1 - a0) * i / 28; const px = c[0] + r * k * (Math.cos(th) * mx - Math.sin(th) * spn * dx), py = c[1] + r * k * (Math.cos(th) * my - Math.sin(th) * spn * dy); i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); } };
  for (const sec of prof) {
    let l = sec.l; if (sec.ext) l = sec.l * (1 + ext * 1.3);
    const s0 = s, s1 = s + l; s = s1;
    const c0 = cen(s0), c1 = cen(s1), R0 = sec.r0 * k, R1 = sec.r1 * k, Rm = Math.max(R0, R1);
    const base = MAT[sec.mat];
    const gx0 = c0[0] - mx * Rm, gy0 = c0[1] - my * Rm, gx1 = c0[0] + mx * Rm, gy1 = c0[1] + my * Rm;
    const g = ctx.createLinearGradient(gx0, gy0, gx1, gy1);
    const metal = sec.mat === 'metal', gold = sec.mat === 'gold';
    g.addColorStop(0, rgba(shade(base, .30))); g.addColorStop(.16, rgba(shade(base, metal ? .8 : .85)));
    g.addColorStop(.30, rgba(shade(base, metal ? 1.15 : 1.85))); g.addColorStop(.42, rgba(shade(base, metal ? 1.0 : 1.2)));
    g.addColorStop(.72, rgba(shade(base, metal ? .55 : .6))); g.addColorStop(.90, rgba(shade(base, .35)));
    g.addColorStop(.965, rgba(gold ? [255, 220, 130] : [110, 135, 170], .28)); g.addColorStop(1, rgba(shade(base, .2)));
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.moveTo(c0[0] - mx * R0, c0[1] - my * R0); ctx.lineTo(c1[0] - mx * R1, c1[1] - my * R1); ctx.lineTo(c1[0] + mx * R1, c1[1] + my * R1); ctx.lineTo(c0[0] + mx * R0, c0[1] + my * R0); ctx.closePath(); ctx.fill();
    ellipsePath(c0, sec.r0); ctx.fill();
    // ribs
    if (sec.ribs) {
      const rr0 = (sec.role === 'zoom' ? rot.zoom : rot.focus) || 0;
      ctx.lineCap = 'round';
      for (let j = 0; j < sec.ribs; j++) {
        const th = rr0 + (Math.PI * 2 * j) / sec.ribs; const sn = Math.sin(th); if (sn <= 0.02) continue; const cs = Math.cos(th);
        const P = (c, r) => [c[0] + r * (cs * mx - sn * spn * dx), c[1] + r * (cs * my - sn * spn * dy)];
        const a = P(c0, sec.r0 * k * 1.0), b = P(c1, sec.r1 * k * 1.0);
        ctx.strokeStyle = `rgba(255,255,255,${0.05 + 0.20 * sn * (1 - Math.abs(cs) * .5) * (cs < 0.2 ? 1.5 : 1)})`;
        ctx.lineWidth = Math.max(1, 0.012 * D(sp) * k); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
      }
      ctx.strokeStyle = 'rgba(0,0,0,.45)'; ctx.lineWidth = 2; arc(c0, sec.r0, 0, Math.PI); ctx.stroke();
    }
    // top cap (visible face), edge lines
    const capCol = shade(base, metal ? 1.2 : 1.35);
    ellipsePath(c1, sec.r1);
    const cg = ctx.createRadialGradient(c1[0] - Rm * .2, c1[1] - Rm * .2 * spn, 2, c1[0], c1[1], Rm);
    cg.addColorStop(0, rgba(shade(capCol, 1.25))); cg.addColorStop(1, rgba(shade(capCol, .65)));
    ctx.fillStyle = cg; ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,.16)'; ctx.lineWidth = 1.5; arc(c1, sec.r1, 0.05, Math.PI - 0.05); ctx.stroke();
    ctx.strokeStyle = 'rgba(0,0,0,.5)'; ctx.lineWidth = 1.5; arc(c0, sec.r0, 0.05, Math.PI - 0.05); ctx.stroke();
    if (sec.mat === 'hood') { // inner hood lining: draw darker inside ellipse
      ellipsePath(c1, sec.r1 * .86); const hg = ctx.createRadialGradient(c1[0], c1[1], 2, c1[0], c1[1], R1); hg.addColorStop(0, '#050608'); hg.addColorStop(1, '#14161b'); ctx.fillStyle = hg; ctx.fill();
    }
  }
  // front glass
  const cF = cen(s);
  const last = prof[prof.length - 1];
  const rg = (sec => sec.mat === 'hood' ? sec.r1 * .86 : sec.r1)(last) * (prof.dome ? .0 : 0.8);
  if (!prof.dome) {
    const gr = (last.mat === 'hood' ? last.r1 * .86 * .78 : last.r1 * .82);
    // glass sits at the front of the barrel (hoods: recessed a bit)
    const recess = last.mat === 'hood' ? -last.l * .55 : 0;
    const cG = cen(s + recess);
    ctx.save(); ctx.translate(cG[0], cG[1]); ctx.rotate(lean); ctx.scale(1, spn);
    const R = gr * k;
    let gg = ctx.createRadialGradient(-R * .2, -R * .25, R * .05, 0, 0, R);
    gg.addColorStop(0, '#2b4a8f'); gg.addColorStop(.3, '#1b2a63'); gg.addColorStop(.55, '#1c1646'); gg.addColorStop(.78, '#0b2c3a'); gg.addColorStop(1, '#05060a');
    ctx.fillStyle = '#0a0b0f'; ctx.beginPath(); ctx.arc(0, 0, R * 1.08, 0, 7); ctx.fill();
    ctx.fillStyle = gg; ctx.beginPath(); ctx.arc(0, 0, R, 0, 7); ctx.fill();
    ctx.strokeStyle = 'rgba(120,150,255,.35)'; ctx.lineWidth = 2; for (const f of [.86, .62, .38]) { ctx.beginPath(); ctx.arc(0, 0, R * f, 0, 7); ctx.stroke(); }
    ctx.strokeStyle = 'rgba(255,255,255,.55)'; ctx.lineWidth = Math.max(2, R * .05); ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(0, 0, R * .74, -2.55, -1.85); ctx.stroke();
    ctx.strokeStyle = 'rgba(255,200,120,.35)'; ctx.lineWidth = Math.max(1.5, R * .035); ctx.beginPath(); ctx.arc(0, 0, R * .48, 0.5, 1.1); ctx.stroke();
    ctx.restore();
  } else {
    // fisheye dome: bulbous front element seen as a sphere
    const Rd = prof.dome * k, cc = [cF[0] + dx * k * cp * 6, cF[1] + dy * k * cp * 6 + 4];
    const gg = ctx.createRadialGradient(cc[0] - Rd * .3, cc[1] - Rd * .35, Rd * .05, cc[0], cc[1], Rd);
    gg.addColorStop(0, '#3a62b8'); gg.addColorStop(.25, '#1d2f6e'); gg.addColorStop(.6, '#150f38'); gg.addColorStop(.88, '#07161f'); gg.addColorStop(1, '#030407');
    ctx.fillStyle = gg; ctx.beginPath(); ctx.arc(cc[0], cc[1], Rd, 0, 7); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,.6)'; ctx.lineWidth = Math.max(2, Rd * .06); ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(cc[0], cc[1], Rd * .78, -2.6, -1.75); ctx.stroke();
    ctx.strokeStyle = 'rgba(100,255,230,.25)'; ctx.lineWidth = Math.max(1.5, Rd * .04); ctx.beginPath(); ctx.arc(cc[0], cc[1], Rd * .55, .3, 1.2); ctx.stroke();
    ctx.strokeStyle = 'rgba(160,185,230,.4)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(cc[0], cc[1], Rd, 0, 7); ctx.stroke();
  }
  ctx.restore();
}
function D(sp) { return sp.D; }
