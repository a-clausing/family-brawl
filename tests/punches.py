"""Real-size punches (Alex, Nov 20 2026): a standing punch lands only if it reaches the target's real drawn body
(small fighters keep a 46px hit area for everything else), and ducking shrinks the body. Kicks and the low jab
(duck + punch) still hit small fighters.

  python3 tests/punches.py
"""
import asyncio, json
from playwright.async_api import async_playwright
from _common import page_url

JS = """
((cases)=>{
  const {G,mkF,startRound,step}=__sim;
  const K=['left','right','up','down','punch','kick','special','block','super'];
  const inp=o=>{ const r={}; K.forEach(k=>r[k]=!!(o&&o[k])); return r; };
  return cases.map(([a,b,press,duck])=>{
    G.mode='play'; G.paused=false; G.multi=false;
    G.f=[mkF(a,0,false),mkF(b,1,false)]; G.round=1; startRound(); G.phase='fight';
    G.f[0].x=150; G.f[1].x=172; G.f[0].dir=1; G.f[1].dir=-1; G.f.forEach(f=>f.netIn=inp());
    for(let i=0;i<40;i++){ G.f[0].netIn=inp(i===8?press:(press.down?{down:true}:{})); G.f[1].netIn=inp(duck?{down:true}:{}); step(); }
    return [a,b,JSON.stringify(press),duck,200-G.f[1].hp];
  });
})
"""
P, K, LOW = {'punch': True}, {'kick': True}, {'down': True, 'punch': True}
CASES = [  # attacker, target, press, target ducks, should land
    ('ac', 'haddie', P, False, False), ('ac', 'slime', P, False, False), ('becky', 'harper', P, False, False),
    ('ac', 'goblin', P, False, True), ('ac', 'becky', P, False, True), ('ac', 'becky', P, True, False),
    ('ac', 'haddie', K, False, True), ('ac', 'slime', LOW, False, True), ('becky', 'harper', LOW, False, True),
    ('bmoney', 'slime', LOW, False, True), ('goblin', 'imp', P, False, True), ('goblin', 'ac', P, True, True),
]


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await (await b.new_context()).new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(page_url('sim.html')); await pg.wait_for_timeout(400); await pg.evaluate("__sim.setW(390)")
        r = await pg.evaluate(JS, [[a, t, pr, d] for a, t, pr, d, _ in CASES])
        ok = True
        for (a, t, pr, d, want), row in zip(CASES, r):
            got = row[4] > 0; ok &= got == want
            print(f"{a:7} {'+'.join(pr):10} -> {t:7}{' (ducking)' if d else '':11} damage {row[4]:3}  {'ok' if got == want else 'FAIL (expected ' + ('hit' if want else 'miss') + ')'}")
        print('errors', errs or 'none'); print('ALL OK' if ok and not errs else 'FAILED')
        await b.close()

asyncio.run(main())
