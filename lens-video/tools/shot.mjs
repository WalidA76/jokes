// usage: node tools/shot.mjs <t1,t2,...> [outdir]  -> renders PNG stills (preview)
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import path from 'path'; import { fileURLToPath } from 'url'; import fs from 'fs';
const here = path.dirname(fileURLToPath(import.meta.url));
const times = (process.argv[2] || '0').split(',').map(Number);
const out = process.argv[3] || '/tmp/shots'; fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch({ args: ['--font-render-hinting=none', '--allow-file-access-from-files'] });
const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
p.on('pageerror', e => console.log('PAGEERR', e.message)); p.on('console', m => { if (m.type() === 'error') console.log('CONSOLE', m.text()); });
await p.goto('file://' + path.resolve(here, '../src/index.html'));
await p.evaluate(() => window.ready);
for (const t of times) {
  await p.evaluate(t => window.renderFrame(t), t);
  const d = await p.evaluate(() => document.getElementById('c').toDataURL('image/png'));
  fs.writeFileSync(path.join(out, `t${String(t).replace('.', '_')}.png`), Buffer.from(d.split(',')[1], 'base64'));
}
await b.close();
