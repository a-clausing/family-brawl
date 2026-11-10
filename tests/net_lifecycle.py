"""Online free-for-all with 3 tabs and 1 life, checking that the room stays open between matches:
ready-up starts a match, a forced desync resyncs, KOs reach the results screen, Rematch starts the next match,
ending a match from the pause menu sends everyone back to the lobby, a fighter change in the lobby is used in the
next match, a guest leaving the online area only removes them from the room, and a guest dropping out mid-match
sends the rest back to the lobby."""
import asyncio, sys
from playwright.async_api import async_playwright
from _common import serve_out, BG_ARGS, page_url

FIGHT = "__G.mode==='play' && !!__G.f && __G.phase==='fight'"
HUMANS = "[...document.querySelectorAll('#lobby .row b')].filter(b=>/^P\\d/.test(b.textContent)).length"
IN_LOBBY = "!document.getElementById('menu').hidden && !document.getElementById('room').hidden"


async def main():
    page_url('net/index.html')
    fails = []
    def check(ok, what):
        print(('ok   ' if ok else 'FAIL ') + what)
        if not ok: fails.append(what)
    with serve_out() as base:
        URL = base + '/net/index.html?lat=40'
        async with async_playwright() as p:
            b = await p.chromium.launch(args=BG_ARGS)
            ctx = await b.new_context(viewport={'width': 844, 'height': 390}); P = [await ctx.new_page() for _ in range(3)]; errs = []
            for n, pg in enumerate(P): pg.on('pageerror', lambda e, n=n: errs.append(f'{n}: {e}'))
            for pg in P: await pg.goto(URL)
            await P[0].wait_for_timeout(400); A = P[0]
            await A.evaluate("localStorage.setItem('nrb.fightOptions',JSON.stringify({mode:'bestof',bestOf:5,minutes:2,stocks:1}))")
            for pg in P: await pg.reload()
            await A.wait_for_timeout(400)
            await A.click('#mmArcade'); await A.click('#mmOnline'); await A.click('#hostBtn'); await A.wait_for_selector('#room', state='visible')
            await A.select_option('#fmodeSel', 'ffa'); await A.select_option('#lobbyCpu0', 'off'); code = await A.inner_text('#codeOut')
            for pg in P[1:]:
                await pg.click('#mmArcade'); await pg.click('#mmOnline'); await pg.fill('#codeIn', code); await pg.click('#joinBtn')
                await pg.wait_for_selector('#room', state='visible'); await pg.wait_for_timeout(300)
            check(await P[1].evaluate("document.getElementById('fmodeSel').value==='ffa' && document.getElementById('fmodeSel').disabled"),
                  "guest sees the host's fight type and can't change it")
            check(await A.evaluate(HUMANS) == 3, 'host lobby lists 3 players')
            for pg in P[:2]: await pg.click('#goBtn')
            await A.wait_for_timeout(600)
            check(not await A.evaluate(FIGHT), 'no start until everyone is ready')
            await P[2].click('#goBtn')
            for pg in P: await pg.wait_for_function(FIGHT, timeout=20000)
            print('fighters', await A.evaluate("__G.f.length"), 'lives', await A.evaluate("__G.f.map(f=>f.stocks)"))
            await P[2].evaluate("__G.f[1].hp-=37"); await A.wait_for_timeout(2500)
            rs = await P[2].evaluate("__NET.synced"); check(rs >= 1, f'forced desync resynced ({rs})')
            X = await A.evaluate("__NET.frame+30")
            for pg in P: await pg.evaluate(f"window.__koAt={X}")
            for pg in P: await pg.wait_for_function("!document.getElementById('resultOv').hidden", timeout=20000)
            print('results:', [await pg.inner_text('#resTitle') for pg in P], '| button:', await A.inner_text('#menuBtn'))
            for pg in P: await pg.evaluate("window.__koAt=-1")
            for pg in P: await pg.click('#againBtn')
            for pg in P: await pg.wait_for_function(FIGHT, timeout=20000)
            check(True, 'rematch started on all tabs')
            await P[1].click('#pauseBtn'); await P[1].click('#quitBtn')
            for pg in P: await pg.wait_for_function(IN_LOBBY, timeout=8000)
            check(await A.evaluate(HUMANS) == 3, 'ending a match sends all 3 back to the lobby, room intact')
            print('   host status:', await A.inner_text('#lobbyStatus'))
            await P[2].click('.pick[data-c="becky"]'); await P[2].wait_for_timeout(200)
            for pg in P: await pg.click('#goBtn'); await pg.wait_for_timeout(150)
            for pg in P: await pg.wait_for_function(FIGHT, timeout=20000)
            check(await A.evaluate("__G.f[2].key") == 'becky', 'fighter changed in the lobby is used in the next match')
            await A.wait_for_timeout(800)
            await P[2].close()   # P3 drops out mid-match; the test transport can't see a closed tab, so report it like PeerJS would
            await A.evaluate("__guestLeft(__NET.conns.find(c=>c.slot===2))")
            for pg in P[:2]: await pg.wait_for_function(IN_LOBBY, timeout=20000)
            check(True, 'a player dropping out mid-match sends the rest back to the lobby')
            await A.wait_for_timeout(300)
            check(await A.evaluate(HUMANS) == 2, 'dropped player is gone from the lobby')
            await P[1].click('#fsBack'); await A.wait_for_timeout(600)
            check(await A.evaluate(HUMANS) == 1 and await A.evaluate(IN_LOBBY), 'guest leaving only removes them; host keeps the room')
            check(await P[1].evaluate("!document.getElementById('mainMenu').hidden && !__NET.room"), 'the guest who left is back on the main menu')
            print('errors', errs[:3] or 'none'); await b.close()
    sys.exit(1 if errs or fails else 0)

asyncio.run(main())
