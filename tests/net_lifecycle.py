"""Online free-for-all with 3 tabs and 1 life: forces a desync on one guest (should resync), KOs everyone
to reach the results screen, starts a rematch, then has one guest quit (match should end for all)."""
import asyncio, sys
from playwright.async_api import async_playwright
from _common import serve_out, BG_ARGS, page_url


async def main():
    page_url('net/index.html')
    with serve_out() as base:
        URL = base + '/net/index.html?lat=40'
        async with async_playwright() as p:
            b = await p.chromium.launch(args=BG_ARGS)
            ctx = await b.new_context(viewport={'width': 844, 'height': 390}); P = [await ctx.new_page() for _ in range(3)]; errs = []
            for n, pg in enumerate(P): pg.on('pageerror', lambda e, n=n: errs.append(f'{n}: {e}'))
            for pg in P: await pg.goto(URL)
            await P[0].wait_for_timeout(400); A = P[0]
            await A.evaluate("localStorage.setItem('nrb.fightOptions',JSON.stringify({mode:'bestof',bestOf:5,minutes:2,stocks:1}))")
            for pg in P: await pg.reload()
            await A.wait_for_timeout(400)
            await A.click('#mmArcade'); await A.click('#mmOnline'); await A.select_option('#fmodeSel', 'ffa'); await A.select_option('#cpuSel0', 'off')
            await A.click('#goBtn'); await A.click('#hostBtn'); await A.wait_for_timeout(300); code = await A.inner_text('#codeOut')
            for pg in P[1:]:
                await pg.click('#mmArcade'); await pg.click('#mmOnline'); await pg.click('#goBtn'); await pg.fill('#codeIn', code); await pg.click('#joinBtn'); await pg.wait_for_timeout(500)
            await A.click('#lobbyStart')
            for pg in P: await pg.wait_for_function("__G.phase==='fight'", timeout=20000)
            print('fighters', await A.evaluate("__G.f.length"), 'lives', await A.evaluate("__G.f.map(f=>f.stocks)"))
            await P[2].evaluate("__G.f[1].hp-=37"); await A.wait_for_timeout(2500)
            rs = await P[2].evaluate("__NET.synced"); ha = await A.evaluate("__G.f.map(f=>f.hp)"); hg = await P[2].evaluate("__G.f.map(f=>f.hp)")
            print('resyncs after forced desync:', rs, '| hp host / guest 2:', ha, hg)
            X = await A.evaluate("__NET.frame+30")
            for pg in P: await pg.evaluate(f"window.__koAt={X}")
            for pg in P: await pg.wait_for_function("!document.getElementById('resultOv').hidden", timeout=20000)
            print('results:', [await pg.inner_text('#resTitle') for pg in P])
            for pg in P: await pg.click('#againBtn')
            for pg in P: await pg.wait_for_function("__G.phase==='fight'", timeout=20000)
            print('rematch started on all tabs')
            await P[1].click('#pauseBtn'); await P[1].click('#quitBtn'); await A.wait_for_timeout(1500)
            print('after P2 leaves -> host:', await A.inner_text('#onStatus'), '| P3:', await P[2].inner_text('#onStatus'))
            print('errors', errs[:3] or 'none'); await b.close()
    sys.exit(1 if errs or rs < 1 else 0)

asyncio.run(main())
