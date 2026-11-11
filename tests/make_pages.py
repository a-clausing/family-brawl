"""Build the test pages in tests/out/ from the current source. Run this before any test.

  t.html          the normal game plus window.__G / __D hooks and a hit log (used by supers.py)
  sim.html        the game with rendering off and a window.__sim API, for fast CPU-vs-CPU sims
  net/index.html  the game with online play routed through BroadcastChannel instead of PeerJS,
                  so several tabs in one browser can play an online match against each other
  peer/index.html the game with its real PeerJS connections (and the net hooks), pointed by
                  ?port= at a local PeerJS server; used by net_peer.py
"""
import os
from _common import OUT
from build import game_source

NET_STATE = "  stall:0, match:0, conn:null, peer:null, rematch:[false,false], picks:[null,null], resyncAt:-1, synced:0};\n"
APPLY_HIT = "function applyHit(att,def,m,srcX,hx,hy){"


def once(s, a, b):
    assert s.count(a) == 1, f'test hook anchor not found exactly once: {a[:60]!r}'
    return s.replace(a, b)


def test_page(g):
    g = once(g, NET_STATE, NET_STATE + "window.__G=G; window.__D=DIFF;\n")
    return once(g, APPLY_HIT,
                "function applyHit(att,def,m,srcX,hx,hy){ const __h0=def.hp; __applyHit(att,def,m,srcX,hx,hy); "
                "(window.__hits||(window.__hits=[])).push({by:att.key,on:def.key,dmg:__h0-def.hp,t:G.t,blk:def.state==='block',x:att.x}); }\n"
                "function __applyHit(att,def,m,srcX,hx,hy){")


def sim_page(g):
    g = once(g, "function newMatch(){", """window.__sim={G,DIFF,CH,mkF,startRound,setupMulti,step:()=>step(),setW:v=>{W=v; if(!G.multi) AW=v;}};
function newMatch(){""")
    g = once(g, APPLY_HIT, """window.__log={};
function applyHit(att,def,m,srcX,hx,hy){
  const h0=def.hp, st0=def.state;
  applyHit0(att,def,m,srcX,hx,hy);
  const nm=Object.keys(att.cfg.moves).find(k=>att.cfg.moves[k]===m)||m.type||'?';
  const L=(window.__log[att.key]=window.__log[att.key]||{}), e=(L[nm]=L[nm]||{n:0,dmg:0,blocked:0,armored:0});
  e.n++; e.dmg+=h0-def.hp; if(st0==='block'&&def.state==='block') e.blocked++; if(def.state!=='hit'&&def.state!=='block'&&h0>def.hp) e.armored++;
}
function applyHit0(att,def,m,srcX,hx,hy){""")
    return '<!doctype html><html><head><meta charset="utf-8"></head><body><script>window.requestAnimationFrame=()=>0;</script>' + g + '</body></html>'


NET_PRE = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body><script>
window.__LAT=+(new URLSearchParams(location.search).get('lat')||0);
// Optional Wi-Fi-style hiccups: ?jit=120&jp=0.03 delays ~3% of messages by up to 120 ms extra. Messages on one
// connection stay in order, like a real WebRTC data channel. __lagSend(fn) schedules one send.
{ const q=new URLSearchParams(location.search); window.__JIT=+(q.get('jit')||0); window.__JP=+(q.get('jp')||0); }
// Optional Wi-Fi dropouts: ?bl=0.002&blen=250&rto=700 -- each message has a 0.2% chance to start a 250 ms dropout of
// this phone's Wi-Fi; everything it sends during one is lost and resent 700 ms later (like a real connection's resend).
{ const q=new URLSearchParams(location.search); window.__BL=+(q.get('bl')||0); window.__BLEN=+(q.get('blen')||250); window.__RTO=+(q.get('rto')||700); window.__dropUntil=0; }
window.__lagger=(unordered)=>{ let last=0; return fn=>{ let d=__LAT; const now=performance.now();
  if(__JIT && Math.random()<__JP) d+=__JIT*(0.4+0.6*Math.random());
  if(__BL){ if(now>=__dropUntil && Math.random()<__BL) __dropUntil=now+__BLEN; if(now<__dropUntil) d+=__RTO; }
  const at=unordered?now+d:Math.max(now+d,last); last=Math.max(last,at); setTimeout(fn,at-performance.now()); }; };
// ?fast=0 turns the game's fast lane off (presses go on the in-order connection), to compare
window.__FAST=new URLSearchParams(location.search).get('fast')!=='0';
window.__netTransport={
  host(code,h){ const bc=new BroadcastChannel('t-'+code); const conns={}; setTimeout(()=>h.open(),10);
    bc.onmessage=e=>{ const d=e.data;
      if(d.k==='join'&&!conns[d.id]){ const lag=__lagger(), fl=__lagger(true); const c={send:m=>lag(()=>bc.postMessage({k:'m',to:d.id,m})),close(){}};
        if(__FAST) c.fast=m=>fl(()=>bc.postMessage({k:'m',to:d.id,m})); conns[d.id]=c; bc.postMessage({k:'welcome',to:d.id}); h.conn(c); }
      else if(d.k==='m'&&d.from&&conns[d.from]) h.data(d.m,conns[d.from]); }; },
  join(code,h){ const bc=new BroadcastChannel('t-'+code); const id=Math.random().toString(36).slice(2);
    bc.onmessage=e=>{ const d=e.data; if(d.to!==id) return;
      if(d.k==='welcome'){ const lag=__lagger(), fl=__lagger(true); const c={send:m=>lag(()=>bc.postMessage({k:'m',from:id,m})),close(){}};
        if(__FAST) c.fast=m=>fl(()=>bc.postMessage({k:'m',from:id,m})); h.conn(c); }
      else if(d.k==='m') h.data(d.m); };
    bc.postMessage({k:'join',id}); },
  close(){}
};
</script>'''


def net_page(g):
    g = once(g, NET_STATE, NET_STATE + "window.__G=G; window.__NET=NET; window.__guestLeft=x=>guestLeft(x);\n")
    b = "  for(const s of NET.humans) G.f[s].netIn=dec(NET.inputs[s][n]);\n"
    # __posAt / __mAt / __koAt: at that lockstep frame, place fighters, fill meters, or KO everyone but P1.
    g = once(g, b, b + "  if(window.__posAt===NET.frame){ G.f[0].x=130; G.f[1].x=260; G.f.forEach(f=>f.vx=0); }\n"
                       "  if(window.__mAt===NET.frame){ G.f.forEach(f=>f.meter=100); }\n"
                       "  if(window.__koAt===NET.frame){ G.f.forEach((f,i)=>{ if(i>0) f.hp=0; }); }\n")
    return NET_PRE + g + '</body></html>'


PEER_PRE = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<script src="peerjs.min.js"></script><script>
{ const q=new URLSearchParams(location.search); window.__peerOpts={host:'127.0.0.1',port:+(q.get('port')||9000),path:'/',secure:false,config:{iceServers:[]}}; }
</script></head><body>'''


def peer_page(g):
    return PEER_PRE + net_page(g)[len(NET_PRE):]


if __name__ == '__main__':
    import shutil
    g = game_source()
    for d in ('net', 'peer'): os.makedirs(os.path.join(OUT, d), exist_ok=True)
    shutil.copy(os.path.join(os.path.dirname(OUT), '..', 'peerjs.min.js'), os.path.join(OUT, 'peer', 'peerjs.min.js'))
    for name, fn in [('t.html', test_page), ('sim.html', sim_page), ('net/index.html', net_page), ('peer/index.html', peer_page)]:
        open(os.path.join(OUT, name), 'w', encoding='utf-8').write(fn(g))
    print('test pages written to tests/out/')
