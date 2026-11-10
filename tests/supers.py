"""Fire every fighter's super at close range on both sides, at long range, and while being attacked.
Each line should end in OK: the super dealt at least its expected damage and the user took none.

  python3 tests/supers.py            # all fighters
  python3 tests/supers.py winston    # one fighter
"""
import asyncio, sys
from playwright.async_api import async_playwright
from _common import page_url

EXP = {'ac': 62, 'brick': 58, 'becky': 48, 'volt': 62, 'bmoney': 58, 'winston': 56, 'haddie': 56, 'harper': 56}   # expected super damage
OPP = {'ac': 'becky', 'brick': 'volt', 'becky': 'ac', 'volt': 'brick', 'bmoney': 'ac', 'winston': 'becky', 'haddie': 'ac', 'harper': 'brick'}
fails = []


async def run(b, me, opp, gap, aggr=False):
    ctx = await b.new_context(viewport={'width': 844, 'height': 390}); pg = await ctx.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(page_url('t.html')); await pg.wait_for_timeout(300)
    await pg.click('#mmArcade'); await pg.click('#mmSolo'); await pg.select_option('#fmodeSel', '1v1')
    await pg.click(f'.pick[data-c="{me}"]'); await pg.click(f'#cpuPick button[data-o="{opp}"]')
    await pg.evaluate("__D.normal=" + ("{react:1,block:0,dodge:0,aggr:5,combo:1}" if aggr else "{react:9999,block:0,dodge:0,aggr:0.0001,combo:0}"))
    await pg.click('#goBtn'); await pg.wait_for_function("__G.phase==='fight'", timeout=10000)
    if not aggr: await pg.evaluate("__G.f[1].ai.cool=1e9")
    await pg.evaluate(f"__G.f[0].x=180; __G.f[1].x=180+({gap}); __G.f[0].meter=100; __G.f[0].dir={1 if gap > 0 else -1}")
    await pg.keyboard.press('KeyU')
    await pg.wait_for_function("__G.f[0].superArmor===true", timeout=3000)
    await pg.wait_for_function("__G.f[0].superArmor===false", timeout=10000, polling=16)
    mh = await pg.evaluate("__G.f[0].hp")
    await pg.wait_for_function("!__G.f[0].sup", timeout=10000); await pg.wait_for_timeout(200)
    d = 200 - await pg.evaluate("__G.f[1].hp"); e = round(EXP[me] * (0.82 if opp == 'brick' else 1))
    ok = d >= e - 1 and mh == 200 and not errs
    if not ok: fails.append(me)
    print(f"{me:7} vs {opp:7} gap {gap:4} {'attacked' if aggr else '':9} dmg {d:3} expected {e:3} self hp {mh} {'OK' if ok else 'CHECK'} {errs}", flush=True)
    await ctx.close()


async def main():
    who = sys.argv[1:] or list(EXP)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for me in who:
            for gap in (16, -16, 130): await run(b, me, OPP[me], gap)
            if me != 'bmoney': await run(b, me, OPP[me], 24, True)
        await b.close()
    print('ALL OK' if not fails else f'CHECK: {sorted(set(fails))}')
    sys.exit(1 if fails else 0)

asyncio.run(main())
