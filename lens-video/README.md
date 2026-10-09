# The World of Camera Lenses — عالم عدسات التصوير

فيديو موشن غرافيك عمودي 1080×1920 (9:16) · 85 ثانية · 30fps — مبني بالكامل بالكود (Canvas 2D + ffmpeg)، بلا صور فوتوغرافية ولا Stock.

## البنية
| المسار | الوظيفة |
|---|---|
| `src/timeline.js` | **مصدر التوقيت الوحيد** (مشاهد، لحظات الحركة) — يقرؤه الرسم والصوت معًا فيبقيان متزامنين |
| `src/lens.js` | محرك العدسات 2.5D: كل عدسة سطح دوراني (مقاطع + حلقات + زجاج) يُسقَط بصريًا؛ قابلة للدوران والإمالة وحركة حلقات التركيز/الزوم |
| `src/scenes.js` | المشاهد العشرة + الرسوم التوضيحية Vector |
| `src/main.js` | المُركِّب: انتقالات، Match-cut ring، Motion Blur خفيف (متوسط عينتين) |
| `audio/make_audio.py` | تصميم صوت وموسيقى إجرائيان (numpy) |
| `tools/render.mjs` | تصيير الإطارات بالتوازي (Playwright/Chromium) |
| `tools/shot.mjs` | معاينة لقطات ثابتة: `node tools/shot.mjs 12.5,40 /tmp/shots` |
| `script/` | نص التعليق الصوتي العربي + ملف ترجمة SRT |

## إعادة الإنتاج
```bash
node tools/render.mjs /tmp/frames 4            # الإطارات
python3 audio/make_audio.py                    # الصوت → audio/out/{music,sfx,mix}.wav
ffmpeg -framerate 30 -i /tmp/frames/f%05d.jpg -i audio/out/mix.wav -c:v libx264 -crf 16 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest out/lens_world_9x16.mp4
```
للمعاينة التفاعلية: افتح `src/index.html` عبر خادم محلي (`npx http-server`) ثم نفّذ `renderFrame(t)` في الكونسول.

## الخطوط
Cairo (SIL OFL) — مضمّن في `assets/fonts`.
