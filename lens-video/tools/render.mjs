// usage: node tools/render.mjs <outdir> [workers=4] [fpsOverride]  → numbered JPEG frames (deterministic, parallel)
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import path from 'path'; import { fileURLToPath } from 'url'; import fs from 'fs';
const here = path.dirname(fileURLToPath(import.meta.url));
const out = process.argv[2] || '/tmp/frames'; const workers = +(process.argv[3] || 4);
const from = +(process.env.FROM || 0), to = process.env.TO ? +process.env.TO : null;
fs.mkdirSync(out, { recursive: true });
const FPS = 30, DUR = 85, N = to ?? FPS * DUR;
async function worker(id) {
  const b = await chromium.launch({ args: ['--font-render-hinting=none', '--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.goto('file://' + path.resolve(here, '../src/index.html')); await p.evaluate(() => window.ready);
  for (let f = from + id; f < N; f += workers) {
    const d = await p.evaluate(t => { window.renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', 0.95); }, f / FPS);
    fs.writeFileSync(path.join(out, `f${String(f).padStart(5, '0')}.jpg`), Buffer.from(d.split(',')[1], 'base64'));
    if (f % 120 < workers) console.log('frame', f, '/', N);
  }
  await b.close();
}
const t0 = Date.now(); await Promise.all(Array.from({ length: workers }, (_, i) => worker(i)));
console.log('done', ((Date.now() - t0) / 1000).toFixed(1) + 's');
