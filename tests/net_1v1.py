"""Online 1v1 between two tabs (host AC vs guest Winston) with 30 ms lag: Bone Throw and a super,
then compares the game-state checkpoints both sides recorded. Expect 'mismatches []'."""
import asyncio, sys, json
from playwright.async_api import async_playwright
from _common import serve_out, BG_ARGS, page_url


async def main():
    page_url('net/index.html')
    with serve_out() as base:
        URL = base + '/net/index.html?lat=30'
        async with async_playwright() as p:
            b = await p.chromium.launch(args=BG_ARGS)
            ctx = await b.new_context(viewport={'width': 844, 'height': 390}); A = await ctx.new_page(); B = await ctx.new_page(); errs = []
            for n, pg in (('A', A), ('B', B)): pg.on('pageerror', lambda e, n=n: errs.append(n + ': ' + str(e)))
            await A.goto(URL); await B.goto(URL); await A.wait_for_timeout(500)
            await A.click('#mmArcade'); await A.click('#mmOnline'); await A.click('#hostBtn')
            await A.wait_for_selector('#room', state='visible'); await A.select_option('#fmodeSel', '1v1'); code = await A.inner_text('#codeOut')
            await B.click('#mmArcade'); await B.click('#mmOnline'); await B.fill('#codeIn', code); await B.click('#joinBtn')
            await B.wait_for_selector('#room', state='visible'); await B.click('.pick[data-c="winston"]')
            await B.click('#goBtn'); await A.wait_for_timeout(200); await A.click('#goBtn')   # both tap READY
            await A.wait_for_function("__G.phase==='fight'", timeout=15000)
            X = await A.evaluate("__NET.frame+20"); js = f"window.__posAt={X}; window.__mAt={X}"; await A.evaluate(js); await B.evaluate(js)
            await A.wait_for_timeout(700)
            await B.keyboard.press('KeyL'); await A.wait_for_timeout(1800)          # Bone Throw
            Y = await A.evaluate('__NET.frame+12'); await A.evaluate(f'window.__mAt={Y}'); await B.evaluate(f'window.__mAt={Y}'); await A.wait_for_timeout(1000)
            await B.keyboard.down('KeyU'); await B.wait_for_timeout(90); await B.keyboard.up('KeyU'); await A.wait_for_timeout(5800)   # super
            ha = json.loads(await A.evaluate("JSON.stringify(__NET.myHash)")); hb = json.loads(await B.evaluate("JSON.stringify(__NET.myHash)"))
            keys = await A.evaluate("__G.f.map(f=>f.key)")
            common = [k for k in ha if k in hb]; bad = [k for k in common if ha[k] != hb[k]]
            print('hp host/guest:', await A.evaluate("__G.f.map(f=>f.hp)"), await B.evaluate("__G.f.map(f=>f.hp)"),
                  '| checkpoints', len(common), 'mismatches', bad, '| resyncs', await B.evaluate("__NET.synced"))
            print('fighters', keys); print('errors', errs or 'none'); await b.close()
    sys.exit(1 if bad or errs or not common or keys != ['ac', 'winston'] else 0)

asyncio.run(main())
