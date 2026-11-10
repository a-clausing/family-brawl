"""CPU-only 4-fighter sims for free-for-all and 2v2 (random fighters, 3 lives).
Reports average match length, wins by fighter, and any errors or stuck matches (CAP = hit the 6-minute cap).

  python3 tests/sim_multi.py 50
"""
import asyncio, sys
from playwright.async_api import async_playwright
from _common import page_url, FIGHTERS

N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
JS = """(([mode,n,F])=>{
  const {G,setupMulti,startRound,step}=__sim;
  G.diff='hard'; G.mode='play'; G.paused=false; const res={wins:{},frames:0,draws:0,errors:[],maxF:0};
  for(let i=0;i<n;i++){
    const keys=[0,1,2,3].map(()=>F[Math.floor(Math.random()*F.length)]);
    setupMulti(keys,[true,true,true,true],mode==='2v2'); G.rules={mode:'bestof',bestOf:5,minutes:2,stocks:3};
    G.round=1; startRound(); G.phase='intro';
    let fr=0;
    try{ while(G.phase!=='over' && fr<60*60*6){ step(); fr++; } }catch(e){ res.errors.push(String(e)+' '+e.stack.slice(0,200)); }
    if(fr>=60*60*6) res.errors.push('CAP '+JSON.stringify(G.f.map(f=>[f.key,f.team,f.stocks,Math.round(f.hp),f.state,f.move,f.dead,f.elim,f.out,Math.round(f.x),Math.round(f.y),f.kd?f.kd.ph:0,f.stun,f.held,!!f.thr,!!f.sup]))+' phase '+G.phase);
    res.frames+=fr; res.maxF=Math.max(res.maxF,fr);
    if(G.winner) res.wins[G.winner.key]=(res.wins[G.winner.key]||0)+1; else res.draws++;
  }
  return res;
})"""


async def main():
    bad = False
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await (await b.new_context()).new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(page_url('sim.html')); await pg.wait_for_timeout(500); await pg.evaluate("__sim.setW(360)")
        for mode in ['ffa', '2v2']:
            r = await pg.evaluate(JS, [mode, N, FIGHTERS])
            bad |= bool(r['errors'])
            print(f"{mode}: avg match {r['frames'] / N / 60:.0f}s, longest {r['maxF'] / 60:.0f}s | wins by fighter {r['wins']} | draws {r['draws']} | errors {r['errors'][:2] or 'none'}")
        print('page errors:', errs[:2] or 'none'); await b.close()
    sys.exit(1 if bad or errs else 0)

asyncio.run(main())
