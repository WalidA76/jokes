import sys,asyncio
from playwright.async_api import async_playwright
START=int(sys.argv[3]) if len(sys.argv)>3 else 0
import json; k,n=int(sys.argv[1]),int(sys.argv[2]); FPS=30; total=int(round(json.load(open('/home/user/jokes/walid-video/timing.json'))['total']*FPS))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':1080,'height':1920})
        await pg.goto('file:///home/user/jokes/walid-video/index.html'); await pg.evaluate('document.fonts.ready')
        for f in range(k+START,total,n):
            await pg.evaluate(f'render({f/FPS})'); await pg.screenshot(path=f'/home/user/jokes/walid-video/frames/f{f:05d}.jpg',type='jpeg',quality=94)
        await b.close()
asyncio.run(main())
