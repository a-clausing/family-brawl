"""A 3-phone free-for-all where the fast lanes die in one direction mid-fight, like Alex's Nov 2026 freeze (his
screen waited on both guests, theirs on each other). The fight must keep going: no one 'OUT', frames advancing.

  python3 tests/net_deadlane.py guests   # the guests' fast lanes to the host die
  python3 tests/net_deadlane.py host     # the host's fast lanes to the guests die
"""
import asyncio, sys
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from playwright.async_api import async_playwright
from _common import serve_out, BG_ARGS, page_url
WHICH=sys.argv[1] if len(sys.argv)>1 else 'guests'   # guests: guest->host lanes die; host: host->guest lanes die
async def main():
    page_url('net/index.html')
    with serve_out() as base:
        URL=base+'/net/index.html?lat=30'
        async with async_playwright() as p:
            b=await p.chromium.launch(args=BG_ARGS); ctx=await b.new_context(viewport={'width':844,'height':390})
            tabs=[await ctx.new_page() for _ in range(3)]; errs=[]
            for i,pg in enumerate(tabs): pg.on('pageerror',lambda e,i=i: errs.append(f'{i}: {e}')); await pg.goto(URL)
            H=tabs[0]; await H.wait_for_timeout(500)
            await H.click('#mmArcade'); await H.click('#mmOnline'); await H.click('#hostBtn')
            await H.wait_for_selector('#room',state='visible'); await H.select_option('#fmodeSel','ffa'); code=await H.inner_text('#codeOut')
            for g in tabs[1:]:
                await g.click('#mmArcade'); await g.click('#mmOnline'); await g.fill('#codeIn',code); await g.click('#joinBtn')
                await g.wait_for_selector('#room',state='visible'); await g.click('#goBtn'); await H.wait_for_timeout(300)
            await H.wait_for_function("__NET.conns.filter(x=>x.slot>0&&x.ready).length===2",timeout=20000)
            await H.click('#goBtn'); await H.wait_for_function("__G.phase==='fight'",timeout=20000); await H.wait_for_timeout(1500)
            if WHICH=='guests':
                for g in tabs[1:]: await g.evaluate("__NET.conn.fast=()=>{}")          # their fast lanes to the host die
            else:
                await H.evaluate("__NET.conns.forEach(x=>x.c.fast=()=>{})")            # the host's fast lanes to them die
            print('fast lanes', WHICH, '-> host dead at frame', await H.evaluate('__NET.frame'))
            for t in range(8):
                await H.wait_for_timeout(2000)
                st=[await pg.evaluate("({f:__NET.frame, fight:__NET.active&&__G.mode==='play', note:__NET.note||''})") for pg in tabs]
                print(f'  t+{2*(t+1)}s', [(s['f'], 'fight' if s['fight'] else 'OUT: '+s['note']) for s in st])
            hs=[await pg.evaluate("JSON.stringify(__NET.myHash)") for pg in tabs]
            import json; hs=[json.loads(h) for h in hs]; bad=sum(1 for k in hs[0] for h in hs[1:] if k in h and h[k]!=hs[0][k])
            out=any(not s['fight'] for s in st); print('mismatched',bad,'| still fighting' if not out else '| SOMEONE GOT KICKED','| errors',errs or 'none'); await b.close()
            sys.exit(1 if bad or out or errs else 0)
asyncio.run(main())
