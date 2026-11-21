"""CPU-vs-CPU sim for ONE fighter against everyone (both sides), much faster than sim_1v1.py when tuning one fighter.

  python3 tests/sim_one.py skeleton 20          # 20 matches per side per opponent, on hard
  python3 tests/sim_one.py skeleton 20 normal
"""
import asyncio, sys
from playwright.async_api import async_playwright
from _common import page_url, FIGHTERS
ARGS = sys.argv[1:]; sys.argv[1:] = []  # sim_1v1 reads sys.argv on import
from sim_1v1 import JS, NAMES

K = ARGS[0]
N = int(ARGS[1]) if len(ARGS) > 1 else 10
DIFF = ARGS[2] if len(ARGS) > 2 else 'hard'


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await (await b.new_context(viewport={'width': 844, 'height': 390})).new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(page_url('sim.html')); await pg.wait_for_timeout(500)
        await pg.evaluate("__sim.setW(360)")
        tw = tl = 0
        for o in FIGHTERS:
            if o == K: continue
            x = await pg.evaluate(JS, [K, o, N, DIFF]); y = await pg.evaluate(JS, [o, K, N, DIFF])
            w = x['aw'] + y['bw']; l = x['bw'] + y['aw']; tw += w; tl += l
            print(f'  vs {NAMES[o]:>8}: {100 * w / max(1, w + l):5.1f}%', flush=True)
        print(f'{NAMES[K]} overall ({DIFF}): {100 * tw / max(1, tw + tl):.1f}%')
        print('page errors:', errs[:3] or 'none')
        await b.close()

asyncio.run(main())
