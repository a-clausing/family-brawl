# Engine: 2-4 fighters (teams / free-for-all), stocks, respawns. 1v1 code paths stay as they were.
P='/home/claude/iron-yard-brawl.html'; s=open(P).read()
def rep(old,new,cnt=1):
    global s
    n=s.count(old); assert n==cnt,(n,old[:120]); s=s.replace(old,new)

# ---- fighter factory: team, palette and stock fields
rep("  return { cfg:CH[key], key, side, cpu, x:side?AW/2+60:AW/2-60,",
    "  return { team:side, stocks:0, dead:false, elim:false, out:false, respawnT:0, outT:0, lastAtt:-1, cfg:CH[key], key, side, cpu, x:side?AW/2+60:AW/2-60,")

# ---- helpers (placed right after the untouchable rule)
rep("const untouchable=d=>d.kd||d.inv>0||d.held||d.thr;",
"""const untouchable=d=>d.kd||d.inv>0||d.held||d.thr;
/* ---------------- Team fights & free-for-all (2-4 fighters) ----------------
   G.multi is on for 2v2 and free-for-all. Every fighter has a team (in free-for-all each is its own team);
   attacks only hurt the other teams. Each fighter has a few lives (stocks): losing the health bar costs one
   and they drop back in; out of lives, they're out. The last team standing wins. */
const RESPAWN_T=110, RESPAWN_INV=100, OUT_T=70;
const fidx=f=>G.f.indexOf(f);
function foes(f){ return G.f.filter(o=>o!==f && !o.out && (!G.multi || o.team!==f.team)); }
function tgt(f){   // nearest opponent still in the fight
  let best=null, bd=1e9;
  for(const o of foes(f)){ if(o.dead) continue; const d=Math.abs(o.x-f.x)+(o.onGround?0:20); if(d<bd){ bd=d; best=o; } }
  return best||foes(f)[0]||G.f.find(o=>o!==f);
}
function koFighter(f){
  if(f.thr){ const v=G.f[f.thr.vi]; if(v) v.held=false; f.thr=null; }
  f.held=false; f.kd=null; f.state='ko'; f.move=null; f.stun=0; f.bstun=0; f.vy=-3.5; f.onGround=false; f.vx=-f.dir*1.8;
  f.sup=null; f.sprint=null; f.superArmor=false; f.bandOut=false; f.ib=null;
  if(G.cine && G.cine.who===fidx(f)) G.cine=null;
  f.dead=true; f.stocks=Math.max(0,f.stocks-1); f.respawnT=RESPAWN_T; f.outT=0; if(f.stocks<=0) f.elim=true;
  G.slow=Math.max(G.slow,24); G.shake=Math.max(G.shake,6); sfx('ko');
  G.kofeed={i:fidx(f),t:100};
}
function respawn(f){   // drop back in, as far from the opponents as possible, briefly invincible
  const fs=foes(f).filter(o=>!o.dead); let bx=AW/2, bs=-1;
  for(const x of [AW*0.12,AW*0.3,AW*0.5,AW*0.7,AW*0.88]){ const d=fs.length?Math.min(...fs.map(o=>Math.abs(o.x-x))):0; if(d>bs){ bs=d; bx=x; } }
  Object.assign(f,{x:bx,y:GROUND-80,vx:0,vy:0,onGround:false,state:'jump',hp:MAXHP,shp:MAXHP,lagT:0,dead:false,move:null,mf:0,mhit:false,stun:0,bstun:0,
    combo:0,kd:null,inv:RESPAWN_INV,held:false,thr:null,sup:null,sprint:null,superArmor:false,bandOut:false,ib:null,landT:10,flash:0});
  const o=tgt(f); if(o) f.dir=o.x>=f.x?1:-1;
  sparks(f.x,GROUND-40,['#ffffff',fcol(f)],12); sfx('jump');
}
function deadStep(f,o){
  updF(f,o);   // falls as a K.O.
  if(f.elim){ if(++f.outT>=OUT_T) f.out=true; }
  else if(G.phase==='fight' && --f.respawnT<=0) respawn(f);
}
function spawnX(i){
  const n=G.f.length;
  if(G.teams){ const t=G.f[i].team, k=G.f.slice(0,i).filter(o=>o.team===t).length; return AW*(t?[0.8,0.68]:[0.2,0.32])[k]; }
  return AW*(i+0.5)/n;
}
// extra victims of a dash super: anyone else it runs through takes that pass's hit once
function passExtras(f,o,s,px,dmg,opt){
  for(const e of foes(f)){
    if(e===o || e.dead || e.state==='ko') continue;
    const key=s.pass*10+fidx(e); s.xh=s.xh||[];
    if(s.xh.includes(key)) continue;
    if((px-e.x)*(f.x-e.x)<=0 || Math.abs(f.x-e.x)<1){ s.xh.push(key); superHit(f,e,dmg,opt); }
  }
}""")

# ---- combat
rep("function applyHit(att,def,m,srcX,hx,hy){\n  if(untouchable(def)) return;   // knocked down, getting up, being thrown, or throwing",
    "function applyHit(att,def,m,srcX,hx,hy){\n  if(untouchable(def)) return;   // knocked down, getting up, being thrown, or throwing\n  if(G.multi) def.lastAtt=fidx(att);")
rep("  f.sup={t:0,fr:0,ph:0,kt:0,k:0,lock:false,hitDone:false,hitT:0,hitFr:3,pass:0,dest:f.x,trail:[]};",
    "  f.sup={t:0,fr:0,ph:0,kt:0,k:0,lock:false,hitDone:false,hitT:0,hitFr:3,pass:0,dest:f.x,trail:[],ti:G.f.indexOf(o)};")
rep("  f.thr={t:0}; o.held=true;","  f.thr={t:0,vi:G.f.indexOf(o)}; o.held=true;")
# updF
rep("  if(f.move==='throw'){ if(f.thr) throwStep(f,o); else f.move=null; return; }",
    "  if(f.move==='throw'){ if(f.thr) throwStep(f,G.multi?G.f[f.thr.vi]:o); else f.move=null; return; }")
rep("if(f.stun===0){ o.combo=0; f.state=f.onGround?'idle':'jump'; } return; }",
    "if(f.stun===0){ (G.multi&&f.lastAtt>=0?G.f[f.lastAtt]:o).combo=0; f.state=f.onGround?'idle':'jump'; } return; }")
rep("  if(f.move==='super'){ if(f.sup) superStep(f,o); else f.move=null; return; }",
    "  if(f.move==='super'){ if(f.sup) superStep(f,G.multi?G.f[f.sup.ti]:o); else f.move=null; return; }")
rep("    if(m.dmg && !f.mhit && f.mf>m.st && f.mf<=m.st+m.ac) tryHit(f,o,m);",
    "    if(m.dmg && !f.mhit && f.mf>m.st && f.mf<=m.st+m.ac){ if(G.multi){ for(const e of foes(f)) tryHit(f,e,m); } else tryHit(f,o,m); }")
rep("    if(f===G.winner && G.pt>40 && f.onGround){ f.state='win'; f.vx=0; }",
    "    if((f===G.winner||(G.multi&&G.winner&&f.team===G.winner.team&&!f.dead)) && G.pt>40 && f.onGround){ f.state='win'; f.vx=0; }")

# ---- Volt: Hyper Sprint hits everyone it runs through (multi)
rep("""  const minD=(f.cfg.w+o.cfg.w)/2, lo=Math.min(x0,nx)-minD, hi=Math.max(x0,nx)+minD;
  if(o.x>lo && o.x<hi && o.state!=='ko'){""",
"""  if(G.multi){
    for(const e of foes(f)){
      const md=(f.cfg.w+e.cfg.w)/2;
      if(e.x>Math.min(x0,nx)-md && e.x<Math.max(x0,nx)+md && e.state!=='ko'){
        const grounded=e.y>GROUND-14;
        if(grounded && e===o) sp.through=true;
        sp.hs=sp.hs||[];
        if(!sp.hs.includes(fidx(e)) && grounded && G.phase==='fight' && !untouchable(e)){
          sp.hs.push(fidx(e)); sp.hit=true; f.impactT=7;
          const hx=(f.x+e.x)/2, hy=f.y-30;
          applyHit(f,e,f.cfg.moves.special,e.x+f.dir*10,hx,hy);
          G.parts.push({type:'zap',x:e.x,y:hy,life:12,max:12}); G.flashT=4; sfx('heavy');
        }
      }
    }
  }
  const minD=(f.cfg.w+o.cfg.w)/2, lo=Math.min(x0,nx)-minD, hi=Math.max(x0,nx)+minD;
  if(!G.multi && o.x>lo && o.x<hi && o.state!=='ko'){""")
rep("function startSprint(f){\n  const o=f===G.f[0]?G.f[1]:G.f[0], minD=(f.cfg.w+o.cfg.w)/2;",
    "function startSprint(f){\n  const o=G.multi?tgt(f):(f===G.f[0]?G.f[1]:G.f[0]), minD=(f.cfg.w+o.cfg.w)/2;")

# ---- dash supers: extra victims
rep("        if(s.ph===1 && !s.hitDone && (px-o.x)*(f.x-o.x)<=0) voltPassHit(f,o,s);",
    "        if(s.ph===1 && !s.hitDone && (px-o.x)*(f.x-o.x)<=0) voltPassHit(f,o,s);\n        if(G.multi && s.ph===1) passExtras(f,o,s,px,11,{kb:0.3,hs:40});")
rep("        if(!s.hitDone && ((px-o.x)*(f.x-o.x)<=0 || Math.abs(f.x-o.x)<1)) wnTailHit(f,o,s,HITS[s.pass]);",
    "        if(!s.hitDone && ((px-o.x)*(f.x-o.x)<=0 || Math.abs(f.x-o.x)<1)) wnTailHit(f,o,s,HITS[s.pass]);\n        if(G.multi) passExtras(f,o,s,px,HITS[s.pass],s.pass>=2?{launch:true,kb:3,hs:46,vy:-4.6,big:true}:{kb:0.3,hs:40});")

# ---- super projectiles in multi: barbell / rack quake hit everyone in the path; quake wave / snare grab the first one
rep("function superProj(p){\n","function superProj(p){\n  if(G.multi) return superProjMulti(p);\n")
rep("function bandLine(f,x2,y2){",
"""function superProjMulti(p){
  const f=p.owner; p.t++; p.x+=p.vx;
  const dir=Math.sign(p.vx), vs=foes(f).filter(e=>!e.dead && e.state!=='ko'), tg=f.sup?G.f[f.sup.ti]:null, fight=G.phase==='fight';
  const crossed=e=>(p.x-p.vx-e.x)*(p.x-e.x)<=0;
  if(p.type==='bquake'){
    if(p.t%2===0) sparks(p.x-dir*8,GROUND-3,f.alt?BM_FX_ALT:BM_FX,2);
    for(const o of vs){
      if(!fight || !f.sup || Math.abs(o.x-p.x)>o.cfg.w/2+12 || o.y<=GROUND-14 || untouchable(o)) continue;
      const keep=f.meter;
      applyHit(f,o,{dmg:14,kb:0,hs:70,bs:0,unblockable:true,noScale:true},p.x-dir*10,o.x,o.y-20);
      f.meter=keep; o.vx=0; o.vy=0;
      f.sup.ti=fidx(o); f.sup.ph=2; f.sup.kt=0; f.sup.lock=true;
      G.parts.push({type:'sfx',key:'bmoney',name:'burst',x:o.x,y:GROUND+2,life:18,max:18,sc:1,alt:f.alt});
      debris(o.x,GROUND-3,8); G.shake=Math.max(G.shake,6); sfx('heavy');
      return true;
    }
    if(p.x<6||p.x>AW-6){ sparks(clampX(p.x),GROUND-4,f.alt?BM_FX_ALT:BM_FX,8); dust(clampX(p.x),GROUND,6); return true; }
    return false;
  }
  if(p.type==='sbar'||p.type==='squake'){
    if(p.type==='squake' && p.t%3===0) debris(p.x,GROUND-2,3,true);
    p.hs=p.hs||[];
    for(const o of vs){
      if(!fight || p.hs.includes(fidx(o))) continue;
      const near=Math.abs(p.x-o.x)<o.cfg.w/2+(p.type==='sbar'?10:14);
      if(!(near || crossed(o) || (o===tg && p.t===1 && Math.sign(o.x-p.x)!==Math.sign(p.vx)))) continue;
      p.hs.push(fidx(o)); superLanded(f);
      const keep=f.meter; p.noScale=true; applyHit(f,o,p,p.x-p.vx*10,o.x,o.y-(p.type==='sbar'?26:30)); f.meter=keep;
      if(o.hp>0) knockDown(o,Math.sign(p.vx),p.type==='sbar'?2.6:2.4,p.type==='sbar'?-4.4:-4.8);
      if(p.type==='sbar'){ G.parts.push({type:'sfx',key:'ac',name:'blast',x:o.x,y:GROUND+2,life:26,max:26,sc:1,alt:f.alt}); debris(o.x,GROUND-2,8); G.shake=Math.max(G.shake,10); sfx('superhit'); }
      else { G.parts.push({type:'sfx',key:'brick',name:'erupt',x:o.x,y:GROUND+3,life:34,max:34,sc:0.85,alt:f.alt}); debris(o.x,GROUND-4,16); G.shake=Math.max(G.shake,13); sfx('quake'); sfx('superhit'); }
    }
    if(p.type==='sbar') return p.x<-40||p.x>AW+40;
    if(p.x<8||p.x>AW-8){ G.parts.push({type:'sfx',key:'brick',name:'erupt_small',x:clampX(p.x),y:GROUND+2,life:24,max:24,sc:0.8,alt:f.alt}); return true; }
    return false;
  }
  if(p.type==='slasso'){
    for(const o of vs){
      const dx=o.x-p.x;
      if(!(fight && f.sup && (Math.abs(dx)<o.cfg.w/2+10 || crossed(o) || (o===tg && Math.sign(dx)!==Math.sign(p.vx) && p.t<=2)))) continue;
      superLanded(f); f.sup.ti=fidx(o); f.sup.ph=2; f.sup.kt=0; f.sup.lock=true; o.vx=0; o.stun=Math.max(o.stun,30); o.state='hit'; o.move=null; o.sprint=null; o.sup=null;
      sfx('snap'); return true;
    }
    return p.x<-20||p.x>AW+20||!f.sup;
  }
  return true;
}
function bandLine(f,x2,y2){""")

# ---- normal projectiles: band hits the first opponent it reaches; waves hit everyone in the path (multi)
rep("""      const o=p.owner, dd=o===G.f[0]?G.f[1]:G.f[0]; p.t++;""","""      const o=p.owner; p.t++;""")
rep("""        const hb=hurt(dd);
        if(G.phase==='fight' && dd.state!=='ko' && !untouchable(dd) && p.x+5>=hb.x0 && p.x-5<=hb.x1){""",
"""        let dd=null;
        for(const e of (G.multi?foes(o):[o===G.f[0]?G.f[1]:G.f[0]])){ const eb=hurt(e); if(G.phase==='fight' && e.state!=='ko' && !untouchable(e) && p.x+5>=eb.x0 && p.x-5<=eb.x1){ dd=e; break; } }
        const hb=dd?hurt(dd):null;
        if(dd){""")
rep("""    const d=p.owner===G.f[0]?G.f[1]:G.f[0];
    if(p.type==='ripple' && p.t>p.range){""","""    if(p.type==='ripple' && p.t>p.range){""")
rep("""    const hb=hurt(d);
    if(G.phase==='fight' && d.state!=='ko' && !untouchable(d) && !(box.x1<hb.x0||box.x0>hb.x1||box.y1<hb.y0||box.y0>hb.y1)){
      const hx=(Math.max(box.x0,hb.x0)+Math.min(box.x1,hb.x1))/2;""",
"""    let gone=false;
    for(const d of (G.multi?foes(p.owner):[p.owner===G.f[0]?G.f[1]:G.f[0]])){
    if(p.hs && p.hs.includes(fidx(d))) continue;
    const hb=hurt(d);
    if(G.phase==='fight' && d.state!=='ko' && !untouchable(d) && !(box.x1<hb.x0||box.x0>hb.x1||box.y1<hb.y0||box.y0>hb.y1)){
      const hx=(Math.max(box.x0,hb.x0)+Math.min(box.x1,hb.x1))/2;""")
rep("""      if(p.type==='bone'){ sparks(hx,p.y,p.owner.alt?WN_FX_ALT:WN_FX,8); G.parts.push({type:'sfx',key:'winston',name:'burst',x:hx,y:p.y,life:10,max:10,sc:0.4,alt:p.owner.alt,main:true}); }
      G.proj.splice(i,1); continue;
    }
    if(p.x<-20||p.x>AW+20) G.proj.splice(i,1);""",
"""      if(p.type==='bone'){ sparks(hx,p.y,p.owner.alt?WN_FX_ALT:WN_FX,8); G.parts.push({type:'sfx',key:'winston',name:'burst',x:hx,y:p.y,life:10,max:10,sc:0.4,alt:p.owner.alt,main:true}); }
      if(G.multi && (p.type==='ripple'||p.type==='wave')){ (p.hs=p.hs||[]).push(fidx(d)); continue; }   // shockwaves roll on to the next fighter
      gone=true; break;
    }
    }
    if(gone){ G.proj.splice(i,1); continue; }
    if(p.x<-20||p.x>AW+20) G.proj.splice(i,1);""")

# ---- CPU: deterministic random numbers (needed for CPUs in online rooms), ignore teammates' projectiles
i=s.index('function aiInput(f,o){'); j=s.index('\n/* ---------------- Particles',i)
body=s[i:j].replace('rnd()','arnd()')
body=body.replace("    if(p.owner===f) continue;","    if(p.owner===f||(G.multi&&p.owner.team===f.team)) continue;")
assert body.count('arnd()')>5
s=s[:i]+"let arnd=rnd;   // CPU decisions; online rooms swap in a seeded generator so every phone agrees\n"+body+s[j:]

# ---- step: multi-fighter loop
rep("  if(G.slow>0){ G.slow--; if(G.slow%2) return; }\n  if(G.cine){",
    "  if(G.slow>0){ G.slow--; if(G.slow%2) return; }\n  if(G.multi){ stepMulti(); return; }\n  if(G.cine){")
rep("/* ---------------- Render ---------------- */",
"""function stepMulti(){
  const act=G.f.filter(f=>!f.out);
  if(G.cine){
    const w=G.f[G.cine.who];
    for(const f of act) f.in=f.netIn||(f.cpu?blankIn():playerInput());
    updF(w,G.f[w.sup?w.sup.ti:0]||tgt(w));
    for(const f of act) f.prev={...f.in};
    clearTaps(); updParts();
    const ct=++G.cine.t;
    if(ct===16) sfx('buildup');
    if(ct>=24 && ct<CINE-14 && (ct-24)%Math.max(5,14-Math.floor((ct-24)/6))===0) sfx('beat');
    if(ct===CINE-12){ sfx('release'); G.flashT=5; G.shake=Math.max(G.shake,7); }
    if(ct>=CINE) G.cine=null;
    return;
  }
  for(const f of act) f.in=f.netIn||(f.cpu?(f.dead?blankIn():aiInput(f,tgt(f))):playerInput());
  for(const f of act){ if(f.dead) deadStep(f,tgt(f)); else updF(f,tgt(f)); }
  for(const f of act) f.prev={...f.in};
  clearTaps();
  for(let i=0;i<act.length;i++) for(let j=i+1;j<act.length;j++) if(!act[i].dead&&!act[j].dead) separate(act[i],act[j]);
  updProj(); updParts();
  G.f.forEach(f=>{ if(f.shp>f.hp){ if(f.lagT>0) f.lagT--; else f.shp=Math.max(f.hp,f.shp-0.8); } else f.shp=f.hp; });
  if(G.combo && --G.combo.t<=0) G.combo=null;
  if(G.kofeed && --G.kofeed.t<=0) G.kofeed=null;
  G.pt++;
  if(G.phase==='vs'){
    if(G.pt===6||G.pt===12) sfx('slide');
    if(G.pt===VS_SLAM){ sfx('vs'); G.shake=Math.max(G.shake,6); }
    if(G.pt>=VS_LEN){ G.phase='intro'; G.pt=0; }
  } else if(G.phase==='intro'){
    if(G.pt===20) sfx('round');
    if(G.pt===82) sfx('fight');
    if(G.pt>=112) G.phase='fight';
  } else if(G.phase==='fight'){
    for(const f of act) if(!f.dead && f.hp<=0) koFighter(f);
    const alive=new Set(G.f.filter(f=>!f.elim).map(f=>f.team));
    if(alive.size<=1){ G.phase='ko'; G.pt=0; G.winner=G.f.find(f=>!f.elim)||null; G.slow=50; G.shake=8; sfx('ko'); }
  } else if(G.phase==='ko'){
    if(G.pt>=170){ if(G.winner) G.winner.wins++; G.phase='over'; G.pt=0; sfx('cheer'); }
  } else if(G.phase==='over'){
    if(G.pt===50) showResult();
  }
}

/* ---------------- Render ---------------- */""")

# ---- rounds: start positions and lives
rep("  G.cine=null; G.proj=[]; G.parts=[]; G.timer=60; G.ft=0; G.phase='intro'; G.pt=0; G.winner=null; G.combo=null; G.slow=0; G.hitstop=0;\n}",
"""  G.cine=null; G.proj=[]; G.parts=[]; G.timer=60; G.ft=0; G.phase='intro'; G.pt=0; G.winner=null; G.combo=null; G.slow=0; G.hitstop=0; G.kofeed=null;
  if(G.multi) G.f.forEach((f,i)=>{ f.x=spawnX(i); f.dir=f.x<AW/2?1:-1; Object.assign(f,{stocks:G.rules.stocks||3,dead:false,elim:false,out:false,respawnT:0,outT:0,lastAtt:-1}); });
}""")
# hash: lives
rep("add(f.inv||0); add(f.thr?f.thr.t:-1); }","add(f.inv||0); add(f.thr?f.thr.t:-1); add(f.stocks||0); add(f.dead?1:0); add(f.out?1:0); }")
open(P,'w').write(s); print('engine ok')
