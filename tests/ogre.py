"""Iron Ogre (Nov 20 2026, spec art/specs/iron-ogre.txt): Shoulder Hit lunges ~1.5 bodies, hits hard with a strong push
and no knockdown; blocking it takes far less. Axe Chop: a direct axe hit up close deals more than the shockwave; the
shockwave runs forward, hits a jumper too (supers can't be jumped), leaves the fighter behind alone, and a blocker takes
a quarter and stays up. He shrugs off a light punch.

  python3 tests/ogre.py
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
  function charge(gap,block){
    G.mode='play'; G.paused=false; G.multi=false;
    G.f=[mkF('ogre',0,false),mkF('becky',1,false)]; G.round=1; startRound(); G.phase='fight';
    G.f[0].x=120; G.f[1].x=120+gap; G.f[0].dir=1; G.f[1].dir=-1; G.f.forEach(f=>f.netIn=inp());
    G.f[1].netIn=inp({block:!!block});
    G.f[0].netIn=inp({special:true}); step(); G.f[0].netIn=inp();
    const x0=G.f[0].x, o0=G.f[1].x; let down=false;
    for(let i=0;i<60;i++){ step(); if(G.f[1].kd) down=true; }
    return {dmg:200-G.f[1].hp, moved:Math.round(G.f[0].x-x0), pushed:Math.round(G.f[1].x-o0), down};
  }
  out.hit=charge(70); out.far=charge(140); out.blocked=charge(70,true);
  G.f=[mkF('ogre',0,false),mkF('becky',1,false)]; G.round=1; startRound(); G.phase='fight';
  G.f[0].x=180; G.f[1].x=206; G.f[0].dir=1; G.f[1].dir=-1; G.f.forEach(f=>f.netIn=inp());
  G.f[1].netIn=inp({punch:true}); step(); G.f[1].netIn=inp();
  let staggered=false; for(let i=0;i<20;i++){ step(); if(G.f[0].state==='hit') staggered=true; }
  out.armor={dmg:200-G.f[0].hp, staggered};
  // free-for-all: one right in front (the axe), one far ahead jumping, one far ahead blocking, ... and one behind
  __sim.setupMulti(['ogre','becky','bmoney','imp'],[false,false,false,false],false);
  G.phase='fight'; G.f[0].x=200; G.f[1].x=236; G.f[2].x=420; G.f[3].x=110; G.f[0].dir=1;
  G.f.forEach(f=>{ f.netIn=inp(); f.inv=0; }); G.f[0].meter=100;
  G.f[0].netIn=inp({super:true}); step(); G.f[0].netIn=inp();
  for(let i=0;i<300;i++){ G.f[2].netIn=inp({up:i>120&&i<170}); step(); if(i>150 && !G.f[0].sup && !G.proj.length) break; }
  out.chop=[G.f[1].hp,G.f[2].hp,G.f[3].hp];
  __sim.setupMulti(['ogre','becky','bmoney','imp'],[false,false,false,false],false);
  G.phase='fight'; G.f[0].x=200; G.f[1].x=330; G.f[2].x=600; G.f[3].x=20; G.f[0].dir=1;
  G.f.forEach(f=>{ f.netIn=inp(); f.inv=0; }); G.f[1].dir=-1; G.f[0].meter=100;
  G.f[0].netIn=inp({super:true}); step(); G.f[0].netIn=inp(); let bdown=false;
  for(let i=0;i<300;i++){ G.f[1].netIn=inp({block:true}); step(); if(G.f[1].kd) bdown=true; if(i>150 && !G.f[0].sup && !G.proj.length) break; }
  out.block={hp:G.f[1].hp, down:bdown};
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
            'shoulder hit lands after a lunge': r['hit']['dmg'] >= 12 and r['hit']['moved'] > 15,
            'shoulder hit pushes far, no fall': r['hit']['pushed'] > 40 and not r['hit']['down'],
            'shoulder hit is short range': r['far']['dmg'] == 0,
            'blocked shoulder hit: little damage': r['blocked']['dmg'] < 5,
            'shrugs off a light punch': r['armor']['dmg'] > 0 and not r['armor']['staggered'],
            'axe up close hits harder than the wave': 200 - r['chop'][0] > 200 - r['chop'][1] >= 50,
            'wave hits a jumper': r['chop'][1] < 200,
            'wave leaves the one behind alone': r['chop'][2] == 200,
            'blocked wave: a quarter, no fall': 200 - r['block']['hp'] <= 15 and 200 - r['block']['hp'] > 0 and not r['block']['down'],
        }
        for k, v in ok.items(): print(f'{k:40} {"ok" if v else "FAIL"}')
        print('errors', errs or 'none'); print('ALL OK' if all(ok.values()) and not errs else 'FAILED')
        await b.close()

asyncio.run(main())
