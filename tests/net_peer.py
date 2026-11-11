"""Online play over the game's REAL connection code (PeerJS + WebRTC), using a local PeerJS server, so the
two-connection setup (reliable lane + fast lane for button presses) is tested as players will use it.

  python3 tests/net_peer.py            # 1v1: host + 1 guest
  python3 tests/net_peer.py ffa 3      # free-for-all: host + 3 guests

Needs Node; the first run installs the `peer` package into tests/out and starts tests/peer_server.js on port 9123. Pass looks like: every phone reports its fast lane
open, nearly all presses sent on it, 'mismatched 0' and 'errors none'.
"""
import asyncio, sys, json, subprocess, time, socket, os
from playwright.async_api import async_playwright
from _common import serve_out, BG_ARGS, page_url

MODE = sys.argv[1] if len(sys.argv) > 1 else '1v1'
GUESTS = int(sys.argv[2]) if len(sys.argv) > 2 else 1
PORT = 9123

# counts what each phone sends on the fast lane vs the reliable connection
COUNT = """(()=>{ window.__sent={fast:0,slow:0};
  const wrap=c=>{ if(!c||c.__w) return; c.__w=1; const s=c.send.bind(c); c.send=m=>{ if(m&&m.t==='i') __sent[c.metadata&&c.metadata.fast?'fast':'slow']++; return s(m); }; };
  setInterval(()=>{ Object.values(__NET.fastBy).forEach(wrap); wrap(__NET.conn); (__NET.conns||[]).forEach(x=>wrap(x.c)); },50); })()"""


def wait_port(port, secs=90):
    t = time.time()
    while time.time() - t < secs:
        try: socket.create_connection(('127.0.0.1', port), 0.5).close(); return True
        except OSError: time.sleep(0.3)
    return False


async def main():
    page_url('peer/index.html')
    here = os.path.dirname(os.path.abspath(__file__)); out = os.path.join(here, 'out')
    if not os.path.isdir(os.path.join(out, 'node_modules', 'peer')):
        subprocess.run(['npm', 'install', '--silent', '--no-save', '--prefix', out, 'peer@1.0.2'], check=True)
    srv = subprocess.Popen(['node', os.path.join(here, 'peer_server.js'), str(PORT)], env={**os.environ, 'NODE_PATH': os.path.join(out, 'node_modules')},
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        assert wait_port(PORT), 'local PeerJS server did not start'
        with serve_out() as base:
            URL = f'{base}/peer/index.html?port={PORT}'
            async with async_playwright() as p:
                b = await p.chromium.launch(args=BG_ARGS)
                ctx = await b.new_context(viewport={'width': 844, 'height': 390})
                tabs = [await ctx.new_page() for _ in range(GUESTS + 1)]; errs = []
                for i, pg in enumerate(tabs): pg.on('pageerror', lambda e, i=i: errs.append(f'{i}: {e}'))
                for pg in tabs: await pg.goto(URL)
                H = tabs[0]; await H.wait_for_timeout(500)
                await H.click('#mmArcade'); await H.click('#mmOnline'); await H.click('#hostBtn')
                await H.wait_for_selector('#room', state='visible', timeout=20000); await H.select_option('#fmodeSel', MODE)
                code = await H.inner_text('#codeOut')
                for g in tabs[1:]:
                    await g.click('#mmArcade'); await g.click('#mmOnline'); await g.fill('#codeIn', code); await g.click('#joinBtn')
                    await g.wait_for_selector('#room', state='visible', timeout=20000); await g.click('#goBtn'); await H.wait_for_timeout(500)
                await H.wait_for_function(f"__NET.conns.filter(x=>x.slot>0&&x.ready).length==={GUESTS}", timeout=20000)   # every guest's READY reached the host
                for pg in tabs: await pg.evaluate(COUNT)
                await H.click('#goBtn')
                try: await H.wait_for_function("__G.phase==='fight'", timeout=20000)
                except Exception:   # say where the start got stuck
                    print('match did not start. host:', await H.evaluate("({ready:__NET.ready, pinging:__NET.pinging, active:__NET.active, note:__NET.note, guests:__NET.conns.map(x=>({slot:x.slot,ready:x.ready,where:x.where,rtts:x.rtts.length,peer:x.c.peer,label:x.c.label,meta:x.c.metadata,reliable:x.c.reliable,open:x.c.open})), fastBy:Object.keys(__NET.fastBy)})"))
                    for g in tabs[1:]: print('  guest:', await g.evaluate("({ready:__NET.ready, where:__NET.where, active:__NET.active, room:!!__NET.room, myId:__NET.peer&&__NET.peer.id, conns:Object.keys(__NET.peer?__NET.peer.connections:{}).map(k=>[k,__NET.peer.connections[k].map(c=>({label:c.label,meta:c.metadata,open:c.open}))])})"))
                    raise
                keys = ['KeyJ', 'KeyK', 'KeyL', 'ArrowLeft', 'ArrowRight']
                for t in range(48):   # ~12 s of everyone walking and attacking
                    for i, pg in enumerate(tabs): await pg.keyboard.down(keys[(t + i) % 5])
                    await H.wait_for_timeout(125)
                    for i, pg in enumerate(tabs): await pg.keyboard.up(keys[(t + i) % 5])
                    await H.wait_for_timeout(125)
                hs = [json.loads(await pg.evaluate("JSON.stringify(__NET.myHash)")) for pg in tabs]
                common = [k for k in hs[0] if all(k in h for h in hs[1:])]
                bad = sum(1 for k in common for h in hs[1:] if h[k] != hs[0][k])
                print(f'{MODE}, {GUESTS} guest(s) over real WebRTC, input delay {await H.evaluate("__NET.D")} frames, fight frame {await H.evaluate("__NET.frame")}')
                ok = True
                for i, pg in enumerate(tabs):
                    lanes = await pg.evaluate("Object.values(__NET.fastBy).map(c=>c.open)")
                    sent = await pg.evaluate('__sent')
                    want = GUESTS if i == 0 else 1
                    good = len(lanes) == want and all(lanes) and sent['fast'] > 10 * max(1, sent['slow'])
                    ok &= good
                    print(f"  {'host ' if i == 0 else 'guest' + str(i)}: fast lanes open {sum(lanes)}/{want}, presses sent fast {sent['fast']} / reliable {sent['slow']}, resyncs {await pg.evaluate('__NET.synced')}", '' if good else '  <-- CHECK')
                print(f'checkpoints {len(common)} mismatched {bad}')
                print('errors', errs or 'none'); await b.close()
        sys.exit(0 if ok and not bad and not errs and common else 1)
    finally:
        srv.terminate()

asyncio.run(main())
