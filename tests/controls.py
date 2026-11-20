"""Checks the Nov 2026 controls: dodge roll (Block + push left/right), the free SKILL move's recharge,
jumping (J button) and ducking (stick down).

  python3 tests/controls.py
"""
import asyncio, json
from playwright.async_api import async_playwright
from _common import page_url

JS = """
(()=>{
  const {G,mkF,startRound,step}=__sim;
  const K=['left','right','up','down','punch','kick','special','block','super'];
  const inp=o=>{ const r={}; K.forEach(k=>r[k]=!!(o&&o[k])); return r; };
  function setup(a='ac',b='bmoney',xa=150,xb=176){
    G.mode='play'; G.paused=false; G.diff='hard';
    G.f=[mkF(a,0,false),mkF(b,1,false)]; G.round=1; startRound();
    G.phase='fight'; G.f[0].x=xa; G.f[1].x=xb; G.f[0].dir=1; G.f[1].dir=-1;
    G.f.forEach(f=>{ f.netIn=inp(); });
  }
  function run(n,plan){ for(let i=0;i<n;i++){ const p=plan&&plan(i)||[]; G.f[0].netIn=inp(p[0]); G.f[1].netIn=inp(p[1]); step(); } }
  const out={};
  // 1. roll past a standing opponent
  setup(); run(40,i=>[i<1?{block:true}:i<30?{block:true,right:i>=1}:{}]);
  out.rollPast={x0:G.f[0].x|0,x1:G.f[1].x|0,dir:G.f[0].dir,hp:G.f[0].hp,rolling:!!G.f[0].roll};
  // 2. punched in the middle of a roll: no damage
  setup('ac','bmoney',150,190); run(30,i=>[i<1?{block:true}:i<24?{block:true,right:true}:{}, i===2?{punch:true}:{}]);
  out.midRollPunch=G.f[0].hp;
  // 3. same punch without rolling: it lands
  setup('ac','bmoney',150,176); run(30,i=>[{}, i===2?{punch:true}:{}]);
  out.standPunch=G.f[0].hp;
  // 4. a super still catches a rolling fighter
  setup('ac','becky',150,260); G.f[1].meter=100; run(500,i=>[i<1?{block:true}:i<24?{block:true,right:true}:{}, i===6?{super:true}:{}]);
  out.superOnRoll=G.f[0].hp;
  // 5. skill: free, then recharging
  setup('ac','bmoney',100,300); const m0=G.f[0].meter;
  run(1,()=>[{special:true}]); const first=G.f[0].move; run(40); run(1,()=>[{special:true}]); const second=G.f[0].move;
  run(200); run(1,()=>[{special:true}]); const third=G.f[0].move;
  out.skill={first,second,third,meterSame:G.f[0].meter>=m0};
  // 6. stick up jumps, down ducks
  setup('ac','bmoney',100,300); run(3,()=>[{up:true}]); out.jump=!G.f[0].onGround;
  setup('ac','bmoney',100,300); run(3,()=>[{down:true}]); out.duck=G.f[0].state;
  return out;
})()
"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await (await b.new_context(viewport={'width': 844, 'height': 390})).new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(page_url('sim.html')); await pg.wait_for_timeout(500)
        await pg.evaluate("__sim.setW(360)")
        r = await pg.evaluate(JS)
        print(json.dumps(r, indent=1))
        ok = {
            'roll past': r['rollPast']['x0'] > r['rollPast']['x1'] and r['rollPast']['dir'] == -1 and not r['rollPast']['rolling'],
            'mid-roll punch misses': r['midRollPunch'] == 200,
            'standing punch lands': r['standPunch'] < 200,
            'special hits a roller': r['superOnRoll'] < 200,
            'skill free + recharge': r['skill']['first'] == 'special' and r['skill']['second'] != 'special' and r['skill']['third'] == 'special' and r['skill']['meterSame'],
            'jump (J) works': r['jump'],
            'stick down ducks': r['duck'] == 'crouch',
        }
        for k, v in ok.items(): print(f'{k:24} {"ok" if v else "FAIL"}')
        print('errors', errs or 'none')
        print('ALL OK' if all(ok.values()) and not errs else 'FAILED')
        await b.close()

asyncio.run(main())
