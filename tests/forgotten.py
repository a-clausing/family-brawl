"""The Forgotten One (Nov 21 2026, spec art/specs/forgotten-one.txt): Void Grasp reaches medium range, wraps the first
opponent, squeezes them and flings them far back on their feet (no fall), fades when blocked or out of reach; Reality
Collapse pulls nearby opponents in (jumpers too), burns them a little at a time up to a cap, then explodes and knocks them
down; a blocker takes little and stays up; anyone outside its pull is safe.

  python3 tests/forgotten.py
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
    G.f=[mkF('forgotten',0,false),mkF('becky',1,false)]; G.round=1; startRound(); G.phase='fight'; G.f.forEach(f=>f.netIn=inp()); }
  function grasp(gap,block){
    one(); G.f[0].x=80; G.f[1].x=80+gap; G.f[0].dir=1; G.f[1].dir=-1; G.f[1].netIn=inp({block:!!block});
    G.f[0].netIn=inp({special:true}); step(); G.f[0].netIn=inp();
    let down=false, air=false, maxStun=0; for(let i=0;i<120;i++){ step(); if(G.f[1].kd) down=true; if(!G.f[1].onGround) air=true; }
    return {dmg:200-G.f[1].hp, down, air, dist:Math.round(G.f[1].x-G.f[0].x)};
  }
  out.near=grasp(90); out.far=grasp(200); out.blocked=grasp(90,true);
  function hole(mode,gap){
    one(); G.f[0].x=90; G.f[1].x=90+gap; G.f[0].dir=1; G.f[1].dir=-1; G.f[0].meter=100;
    G.f[0].netIn=inp({super:true}); step(); G.f[0].netIn=inp();
    let down=false, pulled=0, x0=G.f[1].x, jumpHit=false;
    for(let i=0;i<400;i++){
      G.f[1].netIn=inp(mode==='block'?{block:true}:mode==='jump'?{up:true}:{});
      const hp=G.f[1].hp; step(); if(G.f[1].kd) down=true; if(mode==='jump'&&G.f[1].hp<hp&&G.f[1].y<148) jumpHit=true;
      const pr=G.proj.find(p=>p.type==='vhole'); if(pr) pulled=Math.max(pulled,Math.abs(x0-G.f[1].x));
      if(i>150 && !G.f[0].sup && !G.proj.length) break;
    }
    return {dmg:200-G.f[1].hp, down, pulled:Math.round(pulled), jumpHit, self:200-G.f[0].hp};
  }
  out.stand=hole('stand',120); out.block=hole('block',120); out.jump=hole('jump',100); out.outside=hole('stand',300);
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
            'void grasp: squeeze damage, no fall': 8 <= n['dmg'] <= 14 and not n['down'],
            'flung far back on their feet': n['air'] and n['dist'] > 150,
            'out of reach: nothing': r['far']['dmg'] == 0,
            'blocked: fades': r['blocked']['dmg'] <= 2,
            'black hole pulls in, burns, explodes': r['stand']['dmg'] == 54 and r['stand']['down'] and r['stand']['pulled'] > 15 and r['stand']['self'] == 0,
            'blocker takes little, stays up': 0 < r['block']['dmg'] <= 16 and not r['block']['down'],
            'jumper is still caught': r['jump']['jumpHit'] and r['jump']['dmg'] >= 40,
            'outside its pull is safe': r['outside']['dmg'] == 0,
        }
        for k, v in ok.items(): print(f'{k:40} {"ok" if v else "FAIL"}')
        print('errors', errs or 'none'); print('ALL OK' if all(ok.values()) and not errs else 'FAILED')
        await b.close()

asyncio.run(main())
