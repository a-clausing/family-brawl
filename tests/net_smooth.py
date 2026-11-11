"""Online smoothness: a room of tabs fights for ~20 s over a laggy, hiccupy connection and every tab
counts how often it had to freeze waiting for someone's button presses.

  python3 tests/net_smooth.py                 # 1v1, 40 ms each way, 4% of messages delayed up to 120 ms more
  python3 tests/net_smooth.py ffa 3           # host + 3 guests in a free-for-all
  python3 tests/net_smooth.py 1v1 1 60 150 0.05   # mode, guests, lag ms, hiccup ms, hiccup share

Prints per tab: freezes (stretches of 2+ frames where the fight stopped), total frozen time, whose presses
each freeze waited on ('none' = every press was there and the test machine itself was too busy, which happens
with 4 tabs on a small machine), and the input delay the room picked. The last line counts only network
freezes. Pass looks like: a handful of network freezes per minute at most, and 'mismatched 0'.
Before the fast lane (Nov 2026) the defaults gave ~170/min in 1v1 and ~440/min in a 4-phone free-for-all.
"""
import asyncio, sys, json
from playwright.async_api import async_playwright
from _common import serve_out, BG_ARGS, page_url

MODE = sys.argv[1] if len(sys.argv) > 1 else '1v1'
GUESTS = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 1
LAT, JIT, JP = (sys.argv[3:6] + ['40', '120', '0.04'][len(sys.argv[3:6]):]) if len(sys.argv) > 3 else ('40', '120', '0.04')
FAST = '0' if '--nofast' in sys.argv else '1'   # --nofast: compare with presses on the in-order connection
SECS = 20

# Watches __NET.frame every 60 Hz tick of the page: a tick where the fight didn't move is a frozen tick.
METER = """(()=>{ const M=window.__meter={ticks:0,frozen:0,freezes:0,run:0,longest:0}; let last=-1;
  setInterval(()=>{ if(__G.mode!=='play'||__G.phase!=='fight') { last=-1; return; }
    const f=__NET.frame; M.ticks++;
    if(f===last){ M.frozen++; M.run++; if(M.run===2){ const miss=__NET.humans.filter(s=>__NET.inputs[s][f]===undefined); M.who=M.who||{}; for(const s of miss) M.who[s]=(M.who[s]||0)+1; if(!miss.length) M.who.none=(M.who.none||0)+1; } } else { if(M.run>=2) M.freezes++; M.longest=Math.max(M.longest,M.run); M.run=0; }
    last=f; },1000/60); })()"""


async def main():
    page_url('net/index.html')
    with serve_out() as base:
        URL = f'{base}/net/index.html?lat={LAT}&jit={JIT}&jp={JP}&fast={FAST}'
        async with async_playwright() as p:
            b = await p.chromium.launch(args=BG_ARGS)
            ctx = await b.new_context(viewport={'width': 844, 'height': 390})
            tabs = [await ctx.new_page() for _ in range(GUESTS + 1)]; errs = []
            for i, pg in enumerate(tabs): pg.on('pageerror', lambda e, i=i: errs.append(f'{i}: {e}'))
            for pg in tabs: await pg.goto(URL)
            H = tabs[0]; await H.wait_for_timeout(500)
            await H.click('#mmArcade'); await H.click('#mmOnline'); await H.click('#hostBtn')
            await H.wait_for_selector('#room', state='visible'); await H.select_option('#fmodeSel', MODE)
            code = await H.inner_text('#codeOut')
            for g in tabs[1:]:
                await g.click('#mmArcade'); await g.click('#mmOnline'); await g.fill('#codeIn', code); await g.click('#joinBtn')
                await g.wait_for_selector('#room', state='visible'); await g.click('#goBtn'); await H.wait_for_timeout(300)
            await H.click('#goBtn')
            await H.wait_for_function("__G.phase==='fight'", timeout=20000)
            for pg in tabs: await pg.evaluate(METER)
            # everyone keeps walking and attacking so the fight is busy
            keys = ['KeyJ', 'KeyK', 'KeyL', 'ArrowLeft', 'ArrowRight']
            for t in range(SECS * 4):
                for i, pg in enumerate(tabs):
                    k = keys[(t + i) % len(keys)]
                    await pg.keyboard.down(k)
                await H.wait_for_timeout(125)
                for i, pg in enumerate(tabs):
                    await pg.keyboard.up(keys[(t + i) % len(keys)])
                await H.wait_for_timeout(125)
            D = await H.evaluate('__NET.D')
            hs = [json.loads(await pg.evaluate("JSON.stringify(__NET.myHash)")) for pg in tabs]
            bad = sum(1 for k in hs[0] for h in hs[1:] if k in h and h[k] != hs[0][k])
            print(f'{MODE}, {GUESTS} guest(s), lag {LAT} ms, hiccups {JIT} ms on {float(JP)*100:.0f}% of messages, input delay {D} frames')
            tot = 0
            for i, pg in enumerate(tabs):
                m = await pg.evaluate('__meter')
                tot += sum(v for k, v in m.get('who', {}).items() if k != 'none')   # freezes spent waiting on someone's presses
                print(f"  {'host ' if i == 0 else 'guest'+str(i)}: {m['freezes']:3} freezes, frozen {m['frozen']*1000//60:5} ms of {m['ticks']*1000//60} ms, longest {m['longest']*1000//60} ms, resyncs {await pg.evaluate('__NET.synced')}, waiting on {m.get('who', {})}")
            print(f'mismatched {bad} | network freezes per tab per minute {tot/len(tabs)*60/SECS:.1f}   ("none" = the test machine was too busy; not the network)')
            print('errors', errs or 'none'); await b.close()

asyncio.run(main())
