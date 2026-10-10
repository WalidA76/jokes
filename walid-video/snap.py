import sys,asyncio
from playwright.async_api import async_playwright
ts=[float(x) for x in sys.argv[2:]]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':1080,'height':1920})
        pg.on('pageerror',lambda e:print('ERR',e)); pg.on('console',lambda m:print('LOG',m.text))
        await pg.goto('file:///home/user/jokes/walid-video/index.html'); await pg.evaluate('document.fonts.ready')
        for t in ts:
            await pg.evaluate(f'render({t})'); await pg.screenshot(path=f'{sys.argv[1]}_{t:05.2f}.png')
        await b.close()
asyncio.run(main())
