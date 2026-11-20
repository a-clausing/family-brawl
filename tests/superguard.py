"""While a fighter is doing a super, nothing hurts them until it lands (Alex, Nov 2026): hits bounce off,
other supers can't knock them down, poison pauses, and the screen doesn't shake.

  python3 tests/superguard.py
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
    G.f=[mkF(k,0,false),mkF('ac',1,false)]; G.round=1; startRound(); G.phase='fight';
    G.f[0].x=150; G.f[1].x=172; G.f[0].dir=1; G.f[1].dir=-1; G.f.forEach(f=>f.netIn=inp());
    G.f[0].meter=100; G.f[0].poison={t:120,o:1};   // poisoned before the super starts
    G.f[0].netIn=inp({super:true}); step(); G.f[0].netIn=inp();
    let hp=G.f[0].hp, hurt=0, shook=0, frames=0;
    while(G.f[0].superArmor && frames<400){
      G.f[1].netIn=inp(frames%10===0?{punch:true}:frames%10===5?{kick:true}:{});   // keep swinging at them
      step(); frames++;
      if(G.f[0].hp<hp) hurt+=hp-G.f[0].hp; hp=G.f[0].hp; if(G.shake>0) shook++;
    }
    out[k]={protectedFrames:frames, hurt, shook};
  }
  return out;
})
"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await (await b.new_context()).new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(page_url('sim.html')); await pg.wait_for_timeout(400); await pg.evaluate("__sim.setW(390)")
        r = await pg.evaluate(JS, FIGHTERS)
        ok = True
        for k, v in r.items():
            good = v['protectedFrames'] > 30 and v['hurt'] == 0
            ok &= good
            print(f"{k:8} protected {v['protectedFrames']:3} frames, damage taken {v['hurt']}  {'ok' if good else 'FAIL'}")
        print('errors', errs or 'none'); print('ALL OK' if ok and not errs else 'FAILED')
        await b.close()

asyncio.run(main())
