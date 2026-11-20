"""Timed specials (Alex, Nov 20 2026): free (no meter), recharge per fighter (stronger = longer),
one out at a time, and every special stops at the first fighter it hits (also in free-for-all).

  python3 tests/specials.py
"""
import asyncio, json
from playwright.async_api import async_playwright
from _common import page_url, FIGHTERS

JS = """
((keys)=>{
  const {G,mkF,startRound,step}=__sim;
  const K=['left','right','up','down','punch','kick','special','block','super'];
  const inp=o=>{ const r={}; K.forEach(k=>r[k]=!!(o&&o[k])); return r; };
  const out={};
  for(const k of keys){
    G.mode='play'; G.paused=false; G.multi=false;
    G.f=[mkF(k,0,false),mkF('becky',1,false)]; G.round=1; startRound(); G.phase='fight';
    G.f[0].x=60; G.f[1].x=330; G.f[0].dir=1; G.f[0].meter=0; G.f.forEach(f=>f.netIn=inp());
    const fire=()=>{ G.f[0].netIn=inp({special:true}); step(); G.f[0].netIn=inp(); };
    fire(); const used=G.f[0].move==='special', meter=G.f[0].meter;
    let back=-1; for(let i=1;i<400;i++){ step(); if(back<0 && !(G.f[0].skillCD>0) && !G.proj.some(p=>p.owner===G.f[0])) back=i; }
    out[k]={used, meterAfter:meter, readyAfterFrames:back};
  }
  return out;
})
"""
JS_FFA = """
(()=>{   // three fighters in a row: a special hits the first and stops
  const {G,mkF,step}=__sim;
  const K=['left','right','up','down','punch','kick','special','block','super'];
  const inp=o=>{ const r={}; K.forEach(k=>r[k]=!!(o&&o[k])); return r; };
  const res={};
  for(const k of ['bmoney','ac','imp','goblin']){
    __sim.setupMulti([k,'becky','becky'],[false,false,false],false);
    G.phase='fight'; G.f[0].x=100; G.f[1].x=170; G.f[2].x=200; G.f[0].dir=1; G.f.forEach(f=>{ f.netIn=inp(); f.inv=0; });
    G.f[0].netIn=inp({special:true}); step(); G.f[0].netIn=inp();
    for(let i=0;i<200;i++) step();
    res[k]=[G.f[1].hp, G.f[2].hp];
  }
  return res;
})()
"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await (await b.new_context()).new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(page_url('sim.html')); await pg.wait_for_timeout(400); await pg.evaluate("__sim.setW(390)")
        r = await pg.evaluate(JS, FIGHTERS)
        for k, v in r.items(): print(f"{k:8} fired={v['used']} meter={v['meterAfter']} ready again after {v['readyAfterFrames']/60:.2f}s")
        has_multi = await pg.evaluate("typeof __sim.setupMulti==='function'")
        ffa = await pg.evaluate(JS_FFA) if has_multi else {}
        print('free-for-all (2nd, 3rd fighter health):', json.dumps(ffa))
        ok = all(v['used'] and v['meterAfter'] == 0 and v['readyAfterFrames'] > 0 for v in r.values())
        ok = ok and r['goblin']['readyAfterFrames'] < r['ac']['readyAfterFrames'] and r['imp']['readyAfterFrames'] < r['becky']['readyAfterFrames']
        ok = ok and all(h3 == 200 for h2, h3 in ffa.values())
        print('errors', errs or 'none'); print('ALL OK' if ok and not errs else 'FAILED')
        await b.close()

asyncio.run(main())
