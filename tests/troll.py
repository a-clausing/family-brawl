"""Cave Troll (Nov 20 2026): Stomp hits fighters on the ground on BOTH sides within short range, with a small hop back and
no knockdown, and misses anyone in the air above it; Earthquake ripples both ways across the whole arena and hits
everyone, jumpers too (Alex: supers can't be jumped). He shrugs off a light punch (lightArmor, like Becky).

  python3 tests/troll.py
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
  function stomp(gap,jump){
    G.mode='play'; G.paused=false; G.multi=false;
    G.f=[mkF('troll',0,false),mkF('becky',1,false)]; G.round=1; startRound(); G.phase='fight';
    G.f[0].x=180; G.f[1].x=180+gap; G.f[0].dir=1; G.f[1].dir=gap>0?-1:1; G.f.forEach(f=>f.netIn=inp());
    G.f[0].netIn=inp({special:true}); if(jump) G.f[1].netIn=inp({up:true}); step(); G.f[0].netIn=inp(); G.f[1].netIn=inp();
    let hop=false, down=false;
    for(let i=0;i<50;i++){ step(); if(G.f[1].state==='hit' && !G.f[1].onGround) hop=true; if(G.f[1].kd) down=true; }
    return {dmg:200-G.f[1].hp, hop, down};
  }
  out.front=stomp(40); out.behind=stomp(-40); out.far=stomp(90); out.jumper=stomp(40,true);
  // a light punch doesn't stagger him
  G.f=[mkF('troll',0,false),mkF('becky',1,false)]; G.round=1; startRound(); G.phase='fight';
  G.f[0].x=180; G.f[1].x=206; G.f[0].dir=1; G.f[1].dir=-1; G.f.forEach(f=>f.netIn=inp());
  G.f[1].netIn=inp({punch:true}); step(); G.f[1].netIn=inp();
  let staggered=false; for(let i=0;i<20;i++){ step(); if(G.f[0].state==='hit') staggered=true; }
  out.armor={dmg:200-G.f[0].hp, staggered};
  // free-for-all: one on each side, one far right jumping as the ripple arrives: everyone is hit
  __sim.setupMulti(['troll','becky','bmoney','imp'],[false,false,false,false],false);
  G.phase='fight'; G.f[0].x=320; G.f[1].x=420; G.f[2].x=600; G.f[3].x=120; G.f[0].dir=1;
  G.f.forEach(f=>{ f.netIn=inp(); f.inv=0; }); G.f[0].meter=100;
  G.f[0].netIn=inp({super:true}); step(); G.f[0].netIn=inp();
  for(let i=0;i<400;i++){ G.f[2].netIn=inp({up:i>130&&i<200}); step(); if(i>150 && !G.f[0].sup && !G.proj.length) break; }
  out.quake=[G.f[1].hp,G.f[2].hp,G.f[3].hp];
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
            'stomp hits in front': r['front']['dmg'] > 0,
            'stomp hits behind': r['behind']['dmg'] > 0,
            'stomp: small hop, no knockdown': r['front']['hop'] and not r['front']['down'] and not r['behind']['down'],
            'stomp is short range': r['far']['dmg'] == 0,
            'stomp misses a jumper': r['jumper']['dmg'] == 0,
            'shrugs off a light punch': r['armor']['dmg'] > 0 and not r['armor']['staggered'],
            'quake hits both sides and a jumper': all(h < 200 - 40 for h in r['quake']),
        }
        for k, v in ok.items(): print(f'{k:40} {"ok" if v else "FAIL"}')
        print('errors', errs or 'none'); print('ALL OK' if all(ok.values()) and not errs else 'FAILED')
        await b.close()

asyncio.run(main())
