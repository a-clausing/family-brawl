"""Online room test: one host tab plus N guest tabs play 2v2 or free-for-all while mashing buttons,
then compares state checkpoints across every tab. Expect 'mismatched 0'. Screenshots go to tests/out/.

  python3 tests/net_multi.py ffa 3     # host + 3 guests
  python3 tests/net_multi.py 2v2 1     # host + 1 guest, CPUs fill the other two spots
"""
import asyncio, sys, json, os, random
from playwright.async_api import async_playwright
from _common import serve_out, BG_ARGS, OUT, page_url

MODE = sys.argv[1] if len(sys.argv) > 1 else 'ffa'
NG = int(sys.argv[2]) if len(sys.argv) > 2 else 3
PICKS = ['ac', 'volt', 'winston', 'brick']


async def main():
    page_url('net/index.html')
    with serve_out() as base:
        URL = base + '/net/index.html?lat=40'
        async with async_playwright() as p:
            b = await p.chromium.launch(args=BG_ARGS)
            ctx = await b.new_context(viewport={'width': 844, 'height': 390}); pages = [await ctx.new_page() for _ in range(NG + 1)]; errs = []
            for n, pg in enumerate(pages): pg.on('pageerror', lambda e, n=n: errs.append(f'{n}: {e}'))
            for pg in pages: await pg.goto(URL)
            await pages[0].wait_for_timeout(500); A = pages[0]
            await A.click('#mmArcade'); await A.click('#mmOnline'); await A.select_option('#fmodeSel', MODE); await A.click(f'.pick[data-c="{PICKS[0]}"]')
            await A.click('#goBtn'); await A.click('#hostBtn'); await A.wait_for_timeout(300); code = await A.inner_text('#codeOut')
            for i, pg in enumerate(pages[1:], 1):
                await pg.click('#mmArcade'); await pg.click('#mmOnline'); await pg.click(f'.pick[data-c="{PICKS[i]}"]'); await pg.click('#goBtn')
                await pg.fill('#codeIn', code); await pg.click('#joinBtn'); await pg.wait_for_timeout(600)
            await A.wait_for_timeout(500); await A.screenshot(path=os.path.join(OUT, f'net_lobby_{MODE}.png'))
            await A.click('#lobbyStart')
            for pg in pages: await pg.wait_for_function("__G.phase==='fight'", timeout=20000)
            print('fighters [key, team, cpu, tag]:', await A.evaluate("JSON.stringify(__G.f.map(f=>[f.key,f.team,f.cpu,f.tag]))"))
            keys = ['KeyA', 'KeyD', 'KeyJ', 'KeyK', 'KeyW', 'KeyL', 'KeyU']
            for _ in range(60):
                for pg in pages:
                    k = random.choice(keys); await pg.keyboard.down(k); await pg.wait_for_timeout(15); await pg.keyboard.up(k)
                await A.wait_for_timeout(250)
            await A.screenshot(path=os.path.join(OUT, f'net_fight_{MODE}.png'))
            hs = [json.loads(await pg.evaluate("JSON.stringify(__NET.myHash)")) for pg in pages]
            common = [k for k in hs[0] if all(k in h for h in hs)]; bad = [k for k in common if len({h[k] for h in hs}) > 1]
            print('checkpoints', len(common), 'mismatched', len(bad), '| resyncs', [await pg.evaluate("__NET.synced") for pg in pages[1:]])
            print('errors', errs[:3] or 'none'); await b.close()
    sys.exit(1 if bad or errs or not common else 0)

asyncio.run(main())
