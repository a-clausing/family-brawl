"""Demon Lord (Nov 20 2026, spec art/specs/demon-lord.txt): Soul Grasp flies ~4 bodies, grabs the first opponent it touches
for low damage and drags them to just in front of him, then lets go (they can act again soon); blocked = it fades, out of
range = nothing. Infernal Apocalypse: meteors with floor warnings; the final big one knocks down whoever stays on its mark,
a blocker takes a quarter and stays up, someone who walks off the final mark avoids it, and it hits several opponents.

  python3 tests/demon.py
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
  function one(opp){ G.mode='play'; G.paused=false; G.multi=false;
    G.f=[mkF('demon',0,false),mkF(opp||'becky',1,false)]; G.round=1; startRound(); G.phase='fight'; G.f.forEach(f=>f.netIn=inp()); }
  function grasp(gap,block){
    one(); G.f[0].x=80; G.f[1].x=80+gap; G.f[0].dir=1; G.f[1].dir=-1; G.f[1].netIn=inp({block:!!block});
    G.f[0].netIn=inp({special:true}); step(); G.f[0].netIn=inp();
    let down=false, free=-1; for(let i=0;i<120;i++){ step(); if(G.f[1].kd) down=true;
      if(i>20 && free<0 && G.f[1].state!=='hit' && !G.proj.length) free=i; }
    return {dmg:200-G.f[1].hp, down, dist:Math.round(G.f[1].x-G.f[0].x), free};
  }
  out.near=grasp(100); out.far=grasp(230); out.blocked=grasp(100,true);
  // the super: Becky stands still / blocks / walks off when the final mark appears
  function sup(mode){
    one(); G.f[0].x=120; G.f[1].x=160; G.f[0].dir=1; G.f[1].dir=-1; G.f[0].meter=100;
    G.f[0].netIn=inp({super:true}); step(); G.f[0].netIn=inp();
    let down=false;
    for(let i=0;i<400;i++){
      const pr=G.proj.find(p=>p.type==='meteors'), fin=pr&&pr.list[pr.list.length-1];
      G.f[1].netIn=inp(mode==='block'?{block:true}:mode==='walk'&&fin&&fin.x!==null&&!fin.done?{right:true}:{});
      step(); if(G.f[1].kd) down=true; if(i>150 && !G.f[0].sup && !G.proj.length) break;
    }
    return {dmg:200-G.f[1].hp, down, self:200-G.f[0].hp};
  }
  out.stand=sup('stand'); out.block=sup('block'); out.walk=sup('walk');
  __sim.setupMulti(['demon','becky','bmoney','imp'],[false,false,false,false],false);
  G.phase='fight'; G.f[0].x=320; G.f[1].x=100; G.f[2].x=360; G.f[3].x=560; G.f[0].dir=1;
  G.f.forEach(f=>{ f.netIn=inp(); f.inv=0; }); G.f[0].meter=100;
  G.f[0].netIn=inp({super:true}); step(); G.f[0].netIn=inp();
  for(let i=0;i<400;i++){ step(); if(i>150 && !G.f[0].sup && !G.proj.length) break; }
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
        n = r['near']
        ok = {
            'soul grasp: low damage, no fall': 0 < n['dmg'] <= 6 and not n['down'],
            'soul grasp pulls them in front of him': 0 < n['dist'] <= 30,
            'soul grasp lets go (not a lock)': 0 < n['free'] < 90,
            'out of range: nothing': r['far']['dmg'] == 0 and r['far']['dist'] == 230,
            'blocked: fades, no pull': r['blocked']['dmg'] <= 2 and r['blocked']['dist'] > 80,
            'standing still: big hit and knocked down': r['stand']['dmg'] >= 36 and r['stand']['down'] and r['stand']['self'] == 0,
            'blocking: a quarter, no fall': 0 < r['block']['dmg'] <= 15 and not r['block']['down'],
            'walking off the final mark dodges it': r['walk']['dmg'] < 36,
            'hits several opponents': sum(1 for d in r['multi'] if d > 0) >= 2,
        }
        for k, v in ok.items(): print(f'{k:42} {"ok" if v else "FAIL"}')
        print('errors', errs or 'none'); print('ALL OK' if all(ok.values()) and not errs else 'FAILED')
        await b.close()

asyncio.run(main())
