"""Skeleton Warrior (Nov 20 2026): Sword Slash is a melee swing that reaches farther than his kick and steps in;
Skeleton Army strikes each fighter in its path several times (Teams/free-for-all: everyone it crosses), any height.

  python3 tests/skeleton.py
"""
import asyncio, json
from playwright.async_api import async_playwright
from _common import page_url

JS = """
(()=>{
  const {G,mkF,startRound,step}=__sim;
  const K=['left','right','up','down','punch','kick','special','block','super'];
  const inp=o=>{ const r={}; K.forEach(k=>r[k]=!!(o&&o[k])); return r; };
  const out={};
  function one(gap,btn){
    G.mode='play'; G.paused=false; G.multi=false;
    G.f=[mkF('skeleton',0,false),mkF('becky',1,false)]; G.round=1; startRound(); G.phase='fight';
    G.f[0].x=120; G.f[1].x=120+gap; G.f[0].dir=1; G.f[1].dir=-1; G.f.forEach(f=>f.netIn=inp());
    G.f[0].netIn=inp({[btn]:true}); step(); G.f[0].netIn=inp();
    const x0=G.f[0].x; for(let i=0;i<60;i++) step();
    return {dmg:200-G.f[1].hp, moved:Math.round(G.f[0].x-x0)};
  }
  out.kickFar=one(52,'kick'); out.slashFar=one(52,'special'); out.slashNear=one(36,'special');
  // free-for-all: two fighters lined up in front, one behind; the army should hit both in front, several times each
  __sim.setupMulti(['skeleton','becky','bmoney','imp'],[false,false,false,false],false);
  G.phase='fight'; G.f[0].x=200; G.f[1].x=260; G.f[2].x=360; G.f[3].x=120; G.f[0].dir=1;
  G.f.forEach(f=>{ f.netIn=inp(); f.inv=0; }); G.f[0].meter=100;
  G.f[0].netIn=inp({super:true}); step(); G.f[0].netIn=inp();
  let jumped=false;
  for(let i=0;i<700;i++){ if(i===100){ G.f[2].netIn=inp({up:true}); jumped=true; } else G.f[2].netIn=inp(); step(); if(!G.f[0].sup && i>100) break; }
  out.army=[G.f[1].hp,G.f[2].hp,G.f[3].hp];
  return out;
})()
"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await (await b.new_context()).new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(page_url('sim.html')); await pg.wait_for_timeout(400); await pg.evaluate("__sim.setW(390)")
        r = await pg.evaluate(JS)
        print(json.dumps(r))
        ok = {
            'kick misses at 52px': r['kickFar']['dmg'] == 0,
            'slash lands at 52px': r['slashFar']['dmg'] > 0,
            'slash ~1.75x punch': r['slashNear']['dmg'] >= 10,
            'slash steps in': r['slashFar']['moved'] > 10,
            'army hits both in front': r['army'][0] < 200 and r['army'][1] < 200,
            'army hits several times (not jumpable)': r['army'][0] <= 200 - 50 and r['army'][1] <= 200 - 50,
            'army leaves the one behind alone': r['army'][2] == 200,
        }
        for k, v in ok.items(): print(f'{k:40} {"ok" if v else "FAIL"}')
        print('errors', errs or 'none'); print('ALL OK' if all(ok.values()) and not errs else 'FAILED')
        await b.close()

asyncio.run(main())
