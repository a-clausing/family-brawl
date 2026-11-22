"""AC v2 (Nov 22 2026): Sword Slash is a melee swing whose blue crescent reaches past his kick, hitting harder than a kick with
no knockdown; Blade Fury dashes in, and if the opening slash lands, three held hits plus an energy blade (62 total) that can't
be blocked or jumped; the blade also hits anyone further along its path, never the one behind.

  python3 tests/ac.py
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
  function one(gap,btn,hold){
    G.mode='play'; G.paused=false; G.multi=false;
    G.f=[mkF('ac',0,false),mkF('bmoney',1,false)]; G.round=1; startRound(); G.phase='fight';
    G.f[0].x=100; G.f[1].x=100+gap; G.f[0].dir=1; G.f[1].dir=-1; G.f.forEach(f=>f.netIn=inp()); G.f[0].meter=100;
    G.f[0].netIn=inp({[btn]:true}); step(); G.f[0].netIn=inp();
    let fell=false, maxHs=0;
    for(let i=0;i<260;i++){ G.f[1].netIn=inp(hold); step(); const d=G.f[1]; if(d.kd||d.state==='ko') fell=true; }
    return {dmg:200-G.f[1].hp, fell, x0:G.f[0].x};
  }
  out.kickFar=one(46,'kick'); out.slashFar=one(46,'special'); out.slashTooFar=one(70,'special');
  out.superFar=one(200,'super'); out.superBlock=one(40,'super',{block:true}); out.superJump=one(40,'super',{up:true});
  // free-for-all: one fighter right in front, one far along the same side, one behind
  __sim.setupMulti(['ac','becky','imp','goblin'],[false,false,false,false],false);
  G.phase='fight'; G.f[0].x=200; G.f[1].x=240; G.f[2].x=420; G.f[3].x=120; G.f[0].dir=1;
  G.f.forEach(f=>{ f.netIn=inp(); f.inv=0; }); G.f[0].meter=100; G.f[0].dir=1;
  G.f[0].netIn=inp({super:true}); step(); G.f[0].netIn=inp();
  for(let i=0;i<300;i++){ step(); if(!G.f[0].sup && i>120) break; }
  out.ffa=[200-G.f[1].hp,200-G.f[2].hp,200-G.f[3].hp];
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
            'kick misses at 46px': r['kickFar']['dmg'] == 0,
            'slash lands at 46px': r['slashFar']['dmg'] > 0,
            'slash hits harder than his kick (11)': r['slashFar']['dmg'] > 11,
            'slash: no knockdown': not r['slashFar']['fell'],
            'slash has a limit': r['slashTooFar']['dmg'] == 0,
            'super dashes in from far away': r['superFar']['dmg'] >= 55 and r['superFar']['fell'],
            'super ignores block': r['superBlock']['dmg'] >= 55,
            'super catches a jumper': r['superJump']['dmg'] >= 55,
            'ffa: the one in front takes the combo': r['ffa'][0] >= 55,
            'ffa: the blade reaches the far one': r['ffa'][1] > 0,
            'ffa: the one behind is safe': r['ffa'][2] == 0,
        }
        for k, v in ok.items(): print(f'{k:40} {"ok" if v else "FAIL"}')
        print('errors', errs or 'none'); print('ALL OK' if all(ok.values()) and not errs else 'FAILED')
        await b.close()

asyncio.run(main())
