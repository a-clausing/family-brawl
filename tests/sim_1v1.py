"""CPU-vs-CPU 1v1 balance sim: every pairing, N matches each, then a win-rate table.

  python3 tests/sim_1v1.py 20            # 20 matches per pairing on hard
  python3 tests/sim_1v1.py 20 hard,easy
Results are also saved to tests/out/simres.json.
"""
import asyncio, sys, json, os
from playwright.async_api import async_playwright
from _common import page_url, OUT, FIGHTERS

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
DIFFS = sys.argv[2] if len(sys.argv) > 2 else 'hard'
JS = """
(([a,b,n,diff])=>{
  const {G,mkF,startRound,step}=__sim;
  G.diff=diff; G.mode='play'; G.paused=false;
  const res={aw:0,bw:0,draw:0,frames:0,rounds:0,timeups:0};
  for(let i=0;i<n;i++){
    G.f=[mkF(a,0,true),mkF(b,1,true)]; G.f[1].alt=a===b; G.round=1; startRound();
    let fr=0;
    while(G.phase!=='over' && fr<40000){ step(); fr++; if(G.phase==='timeup'&&G.pt===1) res.timeups++; }
    res.frames+=fr; res.rounds+=G.f[0].wins+G.f[1].wins;
    if(G.f[0].wins>G.f[1].wins) res.aw++; else if(G.f[1].wins>G.f[0].wins) res.bw++; else res.draw++;
  }
  return res;
})
"""
NAMES = {'ac': 'AC', 'brick': 'Brick', 'becky': 'Becky', 'volt': 'Volt', 'bmoney': 'BMoney', 'winston': 'Winston'}


def report(d):
    F = FIGHTERS
    for diff in sorted({k.split(':')[0] for k in d}):
        print(f'\n== {diff.upper()}  (row fighter win % vs column; both sides combined)')
        print('         ' + ''.join(f'{NAMES[b]:>8}' for b in F) + '   overall')
        for a in F:
            row = []; tw = tl = 0
            for b in F:
                if a == b:
                    r = d[f'{diff}:{a}:{a}']; row.append(f"{'mir':>5}{100 * r['aw'] // max(1, r['aw'] + r['bw']):>3}"); continue
                x = d[f'{diff}:{a}:{b}']; y = d[f'{diff}:{b}:{a}']
                w = x['aw'] + y['bw']; l = x['bw'] + y['aw']; tw += w; tl += l
                row.append(f'{100 * w / max(1, w + l):>7.0f}%')
            print(f'{NAMES[a]:>8} ' + ''.join(row) + f'   {100 * tw / max(1, tw + tl):5.1f}%')
        ks = [k for k in d if k.startswith(diff)]
        to = sum(d[k]['timeups'] for k in ks); rr = sum(d[k]['rounds'] for k in ks)
        fr = sum(d[k]['frames'] for k in ks); m = sum(d[k]['aw'] + d[k]['bw'] + d[k]['draw'] for k in ks)
        print(f'  time-outs: {to}/{rr} rounds; avg match {fr / m / 60:.0f}s')


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await (await b.new_context(viewport={'width': 844, 'height': 390})).new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(page_url('sim.html')); await pg.wait_for_timeout(500)
        await pg.evaluate("__sim.setW(360)")
        out = {}
        for diff in DIFFS.split(','):
            for a in FIGHTERS:
                for bb in FIGHTERS:
                    out[f'{diff}:{a}:{bb}'] = await pg.evaluate(JS, [a, bb, N, diff])
        json.dump(out, open(os.path.join(OUT, 'simres.json'), 'w'))
        await b.close()
    report(out)
    print('\npage errors:', errs[:3] or 'none')

if __name__ == '__main__':
    asyncio.run(main())
