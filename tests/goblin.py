"""Goblin's Poison Bomb rules (Alex, Nov 2026): the blast can't be jumped but can be outrun, it poisons,
the cloud poisons anyone who walks in, and poison never stacks past its full length.

  python3 tests/goblin.py
"""
import asyncio, json
from playwright.async_api import async_playwright
from _common import page_url

JS = """
(()=>{
  const {G,mkF,startRound,step}=__sim;
  const K=['left','right','up','down','punch','kick','special','block','super'];
  const inp=o=>{ const r={}; K.forEach(k=>r[k]=!!(o&&o[k])); return r; };
  function setup(xa,xb){
    G.mode='play'; G.paused=false; G.diff='hard';
    G.f=[mkF('goblin',0,false),mkF('becky',1,false)]; G.round=1; startRound();
    G.phase='fight'; G.f[0].x=xa; G.f[1].x=xb; G.f[0].dir=1; G.f[1].dir=-1; G.f[0].meter=100;
    G.f.forEach(f=>{ f.netIn=inp(); });
  }
  let maxP=0;
  function run(n,plan){ for(let i=0;i<n;i++){ const p=plan&&plan(i)||[]; G.f[0].netIn=inp(p[0]); G.f[1].netIn=inp(p[1]); step();
    if(G.f[1].poison) maxP=Math.max(maxP,G.f[1].poison.t); } }
  const thrown=()=>G.proj.some(p=>p.type==='sbomb');
  const out={};
  // 1. standing still: blast + poison
  setup(100,220); run(1,()=>[{super:true}]); run(500); out.stand={hp:G.f[1].hp, maxPoison:maxP};
  // 2. jumping the whole time: still caught
  setup(100,220); maxP=0; run(1,()=>[{super:true}]); run(500,i=>[{}, {up:true}]); out.jump=G.f[1].hp;
  // 3. running away as soon as the bomb is thrown: escapes the blast
  setup(100,200); run(1,()=>[{super:true}]); let ran=0;
  for(let i=0;i<500;i++){ const go=thrown()||ran>0; if(go) ran++; G.f[0].netIn=inp(); G.f[1].netIn=inp(go&&ran<60?{right:true}:{}); step(); }
  out.outrun=G.f[1].hp;
  // 4. the cloud: walk into it after the blast (start far away, walk back to the bomb spot)
  setup(100,200); run(1,()=>[{super:true}]); let spot=null, phase=0;
  for(let i=0;i<500;i++){ const b=G.proj.find(p=>p.type==='sbomb'); if(b) spot=b.tx;
    const cl=G.proj.find(p=>p.type==='scloud');
    let m={}; if(b) m={right:true}; else if(cl && G.f[1].x>cl.x+4) m={left:true};
    G.f[0].netIn=inp(); G.f[1].netIn=inp(m); step(); }
  out.cloud=G.f[1].hp;
  return out;
})()
"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await (await b.new_context(viewport={'width': 844, 'height': 390})).new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(page_url('sim.html')); await pg.wait_for_timeout(500)
        await pg.evaluate("__sim.setW(390)")
        r = await pg.evaluate(JS); print(json.dumps(r))
        ok = {
            'blast + poison': 200 - r['stand']['hp'] >= 50,
            'poison never stacks': r['stand']['maxPoison'] <= 120,
            "can't jump it": 200 - r['jump'] >= 40,
            'can outrun it': r['outrun'] == 200 or 200 - r['outrun'] < 20,
            'cloud poisons': 0 < 200 - r['cloud'] < 40,
        }
        for k, v in ok.items(): print(f'{k:22} {"ok" if v else "FAIL"}')
        print('errors', errs or 'none'); print('ALL OK' if all(ok.values()) and not errs else 'FAILED')
        await b.close()

asyncio.run(main())
