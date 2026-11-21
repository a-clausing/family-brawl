"""Runic Golem (Nov 20 2026, spec art/specs/runic-golem.txt): Runic Blast is a fast bolt that fades after ~3 bodies and hits
like a punch (blockable); Runic Eruption marks the floor under every opponent wherever they are, then pillars erupt there:
anyone still on a mark is hit once (a jumper too: supers can't be jumped), a blocker takes a quarter and stays up, and
anyone who walked off their mark is safe. He shrugs off a light punch.

  python3 tests/golem.py
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
  function blast(gap,block){
    G.mode='play'; G.paused=false; G.multi=false;
    G.f=[mkF('golem',0,false),mkF('becky',1,false)]; G.round=1; startRound(); G.phase='fight';
    G.f[0].x=80; G.f[1].x=80+gap; G.f[0].dir=1; G.f[1].dir=-1; G.f.forEach(f=>f.netIn=inp());
    G.f[1].netIn=inp({block:!!block});
    G.f[0].netIn=inp({special:true}); step(); G.f[0].netIn=inp();
    let down=false; for(let i=0;i<60;i++){ step(); if(G.f[1].kd) down=true; }
    return {dmg:200-G.f[1].hp, down};
  }
  out.near=blast(90); out.far=blast(190); out.blocked=blast(90,true);
  G.f=[mkF('golem',0,false),mkF('becky',1,false)]; G.round=1; startRound(); G.phase='fight';
  G.f[0].x=180; G.f[1].x=206; G.f[0].dir=1; G.f[1].dir=-1; G.f.forEach(f=>f.netIn=inp());
  G.f[1].netIn=inp({punch:true}); step(); G.f[1].netIn=inp();
  let staggered=false; for(let i=0;i<20;i++){ step(); if(G.f[0].state==='hit') staggered=true; }
  out.armor={dmg:200-G.f[0].hp, staggered};
  // free-for-all: Becky far right jumps when the pillars erupt, B-Money behind the Golem blocks, the Imp walks off its mark
  __sim.setupMulti(['golem','becky','bmoney','imp'],[false,false,false,false],false);
  G.phase='fight'; G.f[0].x=300; G.f[1].x=600; G.f[2].x=80; G.f[3].x=420; G.f[0].dir=1;
  G.f.forEach(f=>{ f.netIn=inp(); f.inv=0; }); G.f[2].dir=1; G.f[0].meter=100;
  G.f[0].netIn=inp({super:true}); step(); G.f[0].netIn=inp();
  let erupt=-1, jumpY=0, bdown=false;
  for(let i=0;i<400;i++){
    const pr=G.proj.find(p=>p.type==='reruption'); if(pr && erupt<0) erupt=i+40-pr.t;
    const near=erupt>0 && i>=erupt-12;
    G.f[1].netIn=inp({up:near && i<erupt}); G.f[2].netIn=inp({block:true}); G.f[3].netIn=inp({right:pr&&pr.t>2&&pr.t<30});
    step(); if(erupt>0 && i===erupt) jumpY=G.f[1].y; if(G.f[2].kd) bdown=true;
    if(i>200 && !G.f[0].sup && !G.proj.length) break;
  }
  out.erupt={jumper:200-G.f[1].hp, jumpY, blocker:200-G.f[2].hp, bdown, walked:200-G.f[3].hp};
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
        e = r['erupt']
        ok = {
            'runic blast hits up close': r['near']['dmg'] >= 7 and not r['near']['down'],
            'runic blast fades at its range': r['far']['dmg'] == 0,
            'blocked blast: little damage': r['blocked']['dmg'] < 4,
            'shrugs off a light punch': r['armor']['dmg'] > 0 and not r['armor']['staggered'],
            'pillar hits a jumper on the mark': e['jumper'] >= 50 and e['jumpY'] < 150,
            'blocker on the mark: a quarter, no fall': 0 < e['blocker'] <= 15 and not e['bdown'],
            'walking off the mark dodges it': e['walked'] == 0,
        }
        for k, v in ok.items(): print(f'{k:40} {"ok" if v else "FAIL"}')
        print('errors', errs or 'none'); print('ALL OK' if all(ok.values()) and not errs else 'FAILED')
        await b.close()

asyncio.run(main())
