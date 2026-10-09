// Frame compositor. window.renderFrame(t) draws the whole video at time t (seconds), deterministic.
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const layer = document.createElement('canvas'); layer.width = W; layer.height = H; const lctx = layer.getContext('2d');
const accum = document.createElement('canvas'); accum.width = W; accum.height = H; const actx = accum.getContext('2d');
const TL = window.TIMELINE;

function drawAt(t) {
  drawBackground(ctx, t);
  for (let i = 0; i < TL.scenes.length; i++) {
    const sc = TL.scenes[i];
    if (t < sc.start - 0.001 || t >= sc.start + sc.dur) continue;
    const u = t - sc.start, outT = 0.38, inT = (i === 0 ? 0 : 0.18);
    const fadeOut = i === TL.scenes.length - 1 ? 0 : seg(u, sc.dur - outT, outT);
    lctx.clearRect(0, 0, W, H);
    lctx.save(); SCENES[sc.id](lctx, u, sc); lctx.restore();
    ctx.save();
    const eo = E.io(fadeOut);
    ctx.globalAlpha = (1 - eo) * (inT ? E.out(seg(u, 0, inT)) : 1);
    const dx = -90 * eo;
    if (eo > 0.02) ctx.filter = `blur(${eo * 10}px)`;
    ctx.drawImage(layer, dx, 0);
    ctx.restore();
  }
  // match-cut ring at every scene boundary (aperture / front element expanding)
  for (let i = 1; i < TL.scenes.length; i++) {
    const b = TL.scenes[i].start, d = t - (b - 0.15);
    if (d >= 0 && d < 0.65) {
      const p = E.out(d / 0.65); ctx.save();
      ctx.strokeStyle = `rgba(245,184,46,${0.55 * (1 - p)})`; ctx.lineWidth = lerp(10, 2, p);
      ctx.beginPath(); ctx.arc(540, 780, lerp(60, 980, p), 0, 7); ctx.stroke();
      ctx.strokeStyle = `rgba(255,255,255,${0.25 * (1 - p)})`; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(540, 780, lerp(40, 860, p), 0, 7); ctx.stroke();
      ctx.restore();
    }
  }
}
window.renderFrame = function (t, shutter = 1 / 60) {
  // light motion blur: average of 2 sub-samples inside the shutter window
  drawAt(t - shutter / 2);
  actx.clearRect(0, 0, W, H); actx.drawImage(cv, 0, 0);
  drawAt(t + shutter / 2);
  ctx.save(); ctx.globalAlpha = 0.5; ctx.drawImage(accum, 0, 0); ctx.restore();
  // composite check: sub-sample 2 drawn opaque, then 0.5 of sample 1 => 50/50 blend
};
window.ready = Promise.all([
  document.fonts.load('700 40px Cairo', 'عدسات'), document.fonts.load('900 40px Cairo', 'عدسات'), document.fonts.load('400 40px Cairo', 'عدسات'),
  document.fonts.load('700 40px Cairo', '8mm 14mm'), document.fonts.load('900 40px Cairo', '8mm'), document.fonts.load('400 40px Cairo', '8mm'),
]).then(() => document.fonts.ready);
