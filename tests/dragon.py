"""Ancient Dragon (Nov 21 2026, spec art/specs/ancient-dragon.txt): the Tail Sweep reaches medium range (he lurches forward
as he twists), hits hard and sends the victim hopping back on their feet (no fall), and misses out of range; Inferno Breath
burns everyone in front of him up to its cap and knocks them down, a blocker takes a little and stays up, anyone behind
him is safe (even in free-for-all), and a jumper in front is still caught (supers can't be jumped).

  python3 tests/dragon.py
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
  function one(){ G.mode='play'; G.paused=false; G.multi=false;
    G.f=[mkF('dragon',0,false),mkF('becky',1,false)]; G.round=1; startRound(); G.phase='fight'; G.f.forEach(f=>f.netIn=inp()); }
  function sweep(gap){
    one(); G.f[0].x=80; G.f[1].x=80+gap; G.f[0].dir=1; G.f[1].dir=-1;
    G.f[0].netIn=inp({special:true}); step(); G.f[0].netIn=inp();
    let down=false, air=false; for(let i=0;i<70;i++){ step(); if(G.f[1].kd) down=true; if(!G.f[1].onGround) air=true; }
    return {dmg:200-G.f[1].hp, down, air, dist:Math.round(G.f[1].x-G.f[0].x)};
  }
  out.near=sweep(70); out.mid=sweep(110); out.far=sweep(170);
  function breath(mode){
    one(); G.f[0].x=110; G.f[1].x=170; G.f[0].dir=1; G.f[1].dir=-1; G.f[0].meter=100;
    G.f[0].netIn=inp({super:true}); step(); G.f[0].netIn=inp();
    let down=false, jumpHit=false;
    for(let i=0;i<400;i++){
      const pr=G.proj.find(p=>p.type==='dfire');
      G.f[1].netIn=inp(mode==='block'?{block:true}:mode==='jump'?{up:true}:{});
      const hp=G.f[1].hp; step(); if(G.f[1].kd) down=true; if(mode==='jump' && G.f[1].hp<hp && G.f[1].y<148) jumpHit=true;
      if(i>120 && !G.f[0].sup && !G.proj.length) break;
    }
    return {dmg:200-G.f[1].hp, down, jumpHit, self:200-G.f[0].hp};
  }
  out.stand=breath('stand'); out.block=breath('block'); out.jump=breath('jump');
  __sim.setupMulti(['dragon','becky','bmoney','imp'],[false,false,false,false],false);
  G.phase='fight'; G.f[0].x=300; G.f[1].x=380; G.f[2].x=520; G.f[3].x=160; G.f[0].dir=1;
  G.f.forEach(f=>{ f.netIn=inp(); f.inv=0; }); G.f[0].meter=100;
  G.f[0].netIn=inp({super:true}); step(); G.f[0].netIn=inp(); G.f[0].dir=1;
  for(let i=0;i<400;i++){ step(); if(i>120 && !G.f[0].sup && !G.proj.length) break; }
  out.multi=G.f.slice(1).map(f=>200-f.hp);
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
        m = r['multi']
        ok = {
            'tail sweep hits close, no fall': r['near']['dmg'] >= 10 and not r['near']['down'],
            'tail sweep reaches medium range': r['mid']['dmg'] >= 10,
            'victim hops back on their feet': r['near']['air'] and r['near']['dist'] > 90,
            'tail sweep misses far away': r['far']['dmg'] == 0,
            'breath: capped big hit, knocked down': r['stand']['dmg'] == 50 and r['stand']['down'] and r['stand']['self'] == 0,
            'breath: blocker takes a little, stays up': 0 < r['block']['dmg'] <= 20 and not r['block']['down'],
            'breath catches a jumper': r['jump']['jumpHit'] and r['jump']['dmg'] >= 40,
            'free-for-all: everyone in front burned': m[0] >= 40 and m[1] >= 40,
            'free-for-all: the one behind him is safe': m[2] == 0,
        }
        for k, v in ok.items(): print(f'{k:42} {"ok" if v else "FAIL"}')
        print('errors', errs or 'none'); print('ALL OK' if all(ok.values()) and not errs else 'FAILED')
        await b.close()

asyncio.run(main())
