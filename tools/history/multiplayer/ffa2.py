# Rendering for team / free-for-all fights: 4 color sets per fighter, wide arena + following camera, 4-player HUD.
P='/home/claude/iron-yard-brawl.html'; s=open(P).read()
def rep(old,new,cnt=1):
    global s
    n=s.count(old); assert n==cnt,(n,old[:120]); s=s.replace(old,new)

# ---- palettes 2 and 3 (made on demand from the same hue rules as the mirror-match colors)
rep("const sheetImg=(key,alt)=>(alt&&ALT[key])||SHEETS[key].img();",
"""// Free-for-all can have up to four of the same fighter: color sets 2 and 3 rotate the accent hue further
const PAL_SHIFT={ac:[263,183],brick:[116,276],becky:[165,290],volt:[301,226],bmoney:[75,120],winston:[273,73]};
const PAL_COL={ac:['#3ddc5a','#ffc23d'],brick:['#3ddc5a','#b05cff'],becky:['#b05cff','#ffc23d'],volt:['#ff4a3d','#b05cff'],bmoney:['#ff4a3d','#ffc23d'],winston:['#3ddc5a','#c05cff']};
const PALS={2:{},3:{}}, PALS_S={2:{},3:{}}, PALS_P={2:{},3:{}}, PALS_C={2:{},3:{}};
function ensurePal(key,p){
  if(p<2) return; const r=ALT_RULES[key], sh=PAL_SHIFT[key][p-2];
  if(!PALS[p][key] && SHEETS[key].ready()) makeAlt(key,SHEETS[key].img(),r[0],sh,r[2],PALS[p]);
  if(!PALS_S[p][key] && supReady[key]) makeAlt(key,SUPIMG[key],r[0],sh,r[2],PALS_S[p]);
  const pi=PORT[key], ci=CARD[key];
  if(!PALS_P[p][key] && pi && pi.complete && pi.naturalWidth) makeAlt(key,pi,r[0],sh,r[2],PALS_P[p]);
  if(!PALS_C[p][key] && ci && ci.complete && ci.naturalWidth) makeAlt(key,ci,r[0],sh,r[2],PALS_C[p]);
}
const fcol=f=>(f.alt>=2?PAL_COL[f.key][f.alt-2]:(f.alt?f.cfg.altMeterCol:f.cfg.meterCol));
const portImg=f=>f.alt>=2?(PALS_P[f.alt][f.key]||PORT[f.key]):PORT[f.key+(f.alt?'_alt':'')];
const cardImg=f=>f.alt>=2?(PALS_C[f.alt][f.key]||CARD[f.key]):CARD[f.key+(f.alt?'_alt':'')];
const sheetImg=(key,alt)=>alt>=2?(PALS[alt][key]||(ensurePal(key,alt),PALS[alt][key])||SHEETS[key].img()):((alt&&ALT[key])||SHEETS[key].img());""")
rep("const supImg=(k,alt)=>(alt&&ALT_S[k])||SUPIMG[k];",
    "const supImg=(k,alt)=>alt>=2?(PALS_S[alt]&&PALS_S[alt][k]||SUPIMG[k]):((alt&&ALT_S[k])||SUPIMG[k]);")
# meter / spotlight / banner / VS colors and portraits go through the palette helpers
rep("sparks(hx,hy,['#ffffff',def.alt?def.cfg.altMeterCol:def.cfg.meterCol],6);","sparks(hx,hy,['#ffffff',fcol(def)],6);")
rep("  const w=cam.w, col=w.alt?w.cfg.altMeterCol:w.cfg.meterCol, cy=w.y-30;","  const w=cam.w, col=fcol(w), cy=w.y-30;")
rep("  const col=w.alt?w.cfg.altMeterCol:w.cfg.meterCol, left=w.side===0, y0=H-52,","  const col=fcol(w), left=G.multi?w.x<(LASTCAM?LASTCAM.cx:W/2):w.side===0, y0=H-52,")
rep("  const im=PORT[w.key+(w.alt?'_alt':'')], px=left?10:W-10-30;","  const im=portImg(w), px=left?10:W-10-30;")
rep("P(anchorLeft?x:x+w-mw,y,mw,h, ready&&(G.t>>3)%2?'#ffffff':(f.alt?f.cfg.altMeterCol:f.cfg.meterCol));","P(anchorLeft?x:x+w-mw,y,mw,h, ready&&(G.t>>3)%2?'#ffffff':fcol(f));")

# ---- camera
rep("function cineCam(){\n  const c=G.cine; if(!c||!G.f) return null;",
"""// Team / free-for-all camera: frames every fighter still in the fight, zooming out as they spread across the wide arena
const CAM={cx:0,z:1,init:false}; let LASTCAM=null;
function baseCam(){
  if(!G.multi||!G.f) return null;
  let lo=1e9,hi=-1e9;
  for(const f of G.f){ if(f.out||(f.dead&&f.y>=GROUND)) continue; lo=Math.min(lo,f.x); hi=Math.max(hi,f.x); }
  if(lo>hi){ lo=0; hi=AW; }
  const V=Math.max(W,Math.min(AW,hi-lo+150)), z=W/V;
  if(!CAM.init||G.phase==='vs'){ CAM.cx=(lo+hi)/2; CAM.z=z; CAM.init=true; }
  else { CAM.cx+=((lo+hi)/2-CAM.cx)*0.08; CAM.z+=(z-CAM.z)*0.06; }
  const hv=W/CAM.z/2; CAM.cx=Math.max(hv,Math.min(AW-hv,CAM.cx));
  return {cx:CAM.cx, cy:GROUND-(GROUND-H/2)/CAM.z, z:CAM.z};   // the floor stays at the same height on screen
}
function cineCam(base){
  const c=G.cine; if(!c||!G.f) return null;
  const b=base||{cx:W/2,cy:H/2,z:1};""")
rep("""  const z=1+(CINE_Z[w.key]-1)*k+0.22*hold*hold*k;                       // keeps creeping in as power builds""",
    """  const z=b.z+(CINE_Z[w.key]-b.z)*k+0.22*hold*hold*k;                   // keeps creeping in as power builds""")
rep("""  let cx=W/2+(w.x-W/2)*k+Math.sin(t*2.7)*shake, cy=H/2+(fy-H/2)*k+Math.cos(t*3.1)*shake; const hw=W/(2*z), hh=H/(2*z);
  cx=Math.max(hw,Math.min(W-hw,cx)); cy=Math.max(hh,Math.min(H-hh,cy));""",
"""  let cx=b.cx+(w.x-b.cx)*k+Math.sin(t*2.7)*shake, cy=b.cy+(fy-b.cy)*k+Math.cos(t*3.1)*shake; const hw=W/(2*z), hh=H/(2*z);
  cx=Math.max(hw,Math.min(AW-hw,cx)); if(z>=1) cy=Math.max(hh,Math.min(H-hh,cy));""")
rep("  ctx.fillStyle=`rgba(8,6,14,${0.62*cam.k})`; ctx.fillRect(-20,-20,W+40,H+40);",
    "  ctx.fillStyle=`rgba(8,6,14,${0.62*cam.k})`; if(G.multi) ctx.fillRect(-40,-400,AW+80,H+800); else ctx.fillRect(-20,-20,W+40,H+40);")

# ---- wide-arena backdrop: the gym photo scaled to cover the whole arena at the widest zoom
rep("GYMIMG.onload=()=>{ gymReady=true; buildGym(); }; GYMIMG.src=window.GYM_BG;",
"""const GYMM=mk(2,2); let GYMM_Y=0, GYMM_H=H, gymmFor=0;
function buildGymMulti(){
  if(!gymReady || gymmFor===AW*1000+W) return; gymmFor=AW*1000+W;
  const zmin=W/AW, top=GROUND-GROUND/zmin-4, bot=GROUND+(H-GROUND)/zmin+4, ar=GYMIMG.naturalWidth/GYMIMG.naturalHeight;
  const hd=Math.max(AW/ar,(GROUND-top)/FLOOR_ROW,(bot-GROUND)/(1-FLOOR_ROW)), wd=hd*ar, y0=GROUND-FLOOR_ROW*hd, x0=(AW-wd)/2;
  GYMM_Y=Math.min(top,y0); GYMM_H=Math.max(bot,y0+hd)-GYMM_Y;
  GYMM.width=Math.round(AW*2); GYMM.height=Math.round(GYMM_H*2);
  const g=GYMM.getContext('2d'); g.fillStyle='#14121c'; g.fillRect(0,0,GYMM.width,GYMM.height);
  g.imageSmoothingEnabled=true; g.imageSmoothingQuality='high'; g.drawImage(GYMIMG,x0*2,(y0-GYMM_Y)*2,wd*2,hd*2);
}
GYMIMG.onload=()=>{ gymReady=true; buildGym(); }; GYMIMG.src=window.GYM_BG;""")

# ---- render
rep("""  const cam=G.mode==='play'?cineCam():null;
  if(cam){ ctx.translate(W/2,H/2); ctx.scale(cam.z,cam.z); ctx.translate(-cam.cx,-cam.cy); ctx.imageSmoothingEnabled=true; }
  if(gymReady) ctx.drawImage(GYMC,0,0,W*2,H*2,0,0,W,H); else ctx.drawImage(SCENE,0,0);
  ctx.imageSmoothingEnabled=false;
  if(G.f && G.mode==='play'){
    for(const f of G.f){""",
"""  const base=G.mode==='play'?baseCam():null;
  const cam=G.mode==='play'?(cineCam(base)||base):null; LASTCAM=cam;
  if(cam){ ctx.translate(W/2,H/2); ctx.scale(cam.z,cam.z); ctx.translate(-cam.cx,-cam.cy); ctx.imageSmoothingEnabled=true; }
  if(G.multi && G.mode==='play'){ buildGymMulti(); if(gymReady) ctx.drawImage(GYMM,0,GYMM_Y,AW,GYMM_H); }
  else if(gymReady) ctx.drawImage(GYMC,0,0,W*2,H*2,0,0,W,H); else ctx.drawImage(SCENE,0,0);
  if(!cam||cam.z===1) ctx.imageSmoothingEnabled=false;
  if(G.f && G.mode==='play'){
    for(const f of G.f){
      if(f.out||(f.dead&&f.y>=GROUND&&f.elim)) continue;""")
rep("""    const order=[...G.f].sort((p,q)=>(p.move?1:0)-(q.move?1:0));
    for(const f of order){ if(f.sprint) drawSprintFx(f); drawSuperExtras(f); drawFighterAny(ctx,f,f.x,f.y); drawHeldFx(f); }""",
"""    const order=[...G.f].filter(f=>!f.out).sort((p,q)=>(p.move?1:0)-(q.move?1:0));
    for(const f of order){
      if(G.multi){
        if(f.inv>20 && !f.dead && (G.t>>2)%2) continue;   // blinking after a respawn: invincible
        if(f.elim){ ctx.save(); ctx.globalAlpha=Math.max(0,1-f.outT/OUT_T); drawFighterAny(ctx,f,f.x,f.y); ctx.restore(); continue; }
      }
      if(f.sprint) drawSprintFx(f); drawSuperExtras(f); drawFighterAny(ctx,f,f.x,f.y); drawHeldFx(f);
    }""")
rep("  if(G.f && G.mode==='play'){ if(G.phase==='vs') drawVS(); else if(G.cine) drawCineBanner(); else { hud(); banners(); } }",
    "  if(G.f && G.mode==='play'){ if(G.phase==='vs') (G.multi?drawVSMulti:drawVS)(); else if(G.cine) drawCineBanner(); else if(G.multi){ drawTags(cam); hudMulti(); bannersMulti(); } else { hud(); banners(); } }")

# ---- multi HUD, tags, banners, VS
rep("function banners(){",
r"""const SLOT_COL=['#ff5a4d','#4da6ff','#5ee06e','#ffd23f'], TEAM_COL=['#4da6ff','#ff5a4d'], TEAM_NAME=['BLUE','RED'];
const tagCol=f=>G.teams?TEAM_COL[f.team]:SLOT_COL[f.slot||0];
const tagTxt=f=>f.tag||(f.cpu?'CPU':'YOU');
function drawTags(cam){   // a label over every fighter so you can tell four fighters apart
  if(G.phase==='over') return;
  for(const f of G.f){
    if(f.out||f.dead) continue;
    if(f.inv>20 && (G.t>>2)%2) continue;
    const z=cam?cam.z:1, cx=cam?cam.cx:W/2, cy=cam?cam.cy:H/2;
    const sx=W/2+(f.x-cx)*z, sy=H/2+(f.y-(f.cfg.artH||f.cfg.h)-6-cy)*z-6;
    if(sx<-10||sx>W+10) continue;
    const col=tagCol(f), t=tagTxt(f)==='YOU'?'YOU':tagTxt(f);
    ctx.fillStyle=OUT; ctx.beginPath(); ctx.moveTo(sx-4,sy+1); ctx.lineTo(sx+4,sy+1); ctx.lineTo(sx,sy+6); ctx.fill();
    ctx.fillStyle=col; ctx.beginPath(); ctx.moveTo(sx-3,sy+1.5); ctx.lineTo(sx+3,sy+1.5); ctx.lineTo(sx,sy+5); ctx.fill();
    txt(t,Math.round(sx),Math.round(sy-9),8,t==='YOU'?'#ffd23f':col);
  }
}
function hudMulti(){
  const n=G.f.length, pw=Math.floor((W-4)/n);
  G.f.forEach((f,i)=>{
    const x=2+i*pw, w=pw-4, col=tagCol(f), done=f.elim&&(f.out||f.dead);
    P(x,2,w,33,'rgba(12,9,20,.78)'); P(x,2,w,2,col);
    const im=portImg(f);
    if(im&&im.complete!==false&&(im.naturalWidth||im.width)){ ctx.imageSmoothingEnabled=true; ctx.save(); if(done) ctx.globalAlpha=0.35; ctx.drawImage(im,x+2,6,16,16); ctx.restore(); ctx.imageSmoothingEnabled=false; }
    ctx.strokeStyle=col; ctx.lineWidth=1; ctx.strokeRect(x+2.5,6.5,15,15);
    ctx.save(); ctx.beginPath(); ctx.rect(x+20,5,w-21,10); ctx.clip(); txt(f.cfg.name,x+21,6,8,done?'#6d6390':'#ffffff','left'); ctx.restore();
    txt(tagTxt(f),x+w-2,24,8,tagTxt(f)==='YOU'?'#ffd23f':col,'right');
    // health
    const bw=w-22, hw=done?0:Math.round(bw*f.hp/MAXHP), lw=done?0:Math.round(bw*f.shp/MAXHP);
    P(x+20,16,bw,5,OUT); P(x+21,17,bw-2,3,'#3b1f2e');
    if(lw>2) P(x+21,17,lw-2,3,'#e8432f');
    if(hw>2){ const low=f.hp<=MAXHP*0.25&&(G.t>>3)%2; P(x+21,17,hw-2,3,low?'#ff8a3c':'#ffd23f'); }
    // meter
    const mw=Math.round((bw-2)*(done?0:f.meter)/100);
    P(x+20,22,bw,3,OUT); if(mw>0) P(x+21,23,mw,1,f.meter>=SUPER_COST?((G.t>>2)%2?'#ffe066':'#ff9a1f'):fcol(f));
    // lives
    for(let k=0;k<(G.rules.stocks||3);k++){ P(x+2+k*6,27,5,5,OUT); P(x+3+k*6,28,3,3,k<f.stocks?col:'#3a3050'); }
    if(done) txt('OUT',x+w/2+8,8,8,'#ff5a4d');
    else if(f.dead) txt(String(Math.ceil(f.respawnT/60)),x+w/2+8,8,8,'#ffffff');
  });
  if(G.combo && G.f[G.combo.side]) txt(`${G.f[G.combo.side].cfg.name} ${G.combo.n} HITS`,W/2,40,8,'#ffd23f');
}
function bannersMulti(){
  const pt=G.pt;
  if(G.phase==='intro'){
    if(pt>12&&pt<80) txt(G.teams?'2 VS 2':'FREE-FOR-ALL',W/2,66,16,'#ffd23f');
    else if(pt>=80) txt('FIGHT!',W/2,62,24,'#ff6a1f');
  } else if(G.phase==='fight'){
    if(G.kofeed){ const f=G.f[G.kofeed.i]; if(f) txt(f.elim?`${f.cfg.name} IS OUT!`:`${f.cfg.name} K.O.!`,W/2,58,f.elim?16:8,f.elim?'#ff3b30':'#ffffff'); }
  } else if(G.phase==='ko'||G.phase==='over'){
    if(G.phase!=='over'&&pt<90) txt('GAME!',W/2,58,32,'#ff3b30');
    else if(!G.winner) txt('DRAW',W/2,62,16,'#ffd23f');
    else if(G.teams) txt(`${TEAM_NAME[G.winner.team]} TEAM WINS`,W/2,62,16,TEAM_COL[G.winner.team]);
    else txt(`${G.winner.cfg.name} WINS`,W/2,62,16,'#ffd23f');
  }
}
function banners(){""")

rep("/* ---------------- VS screen ---------------- */",
"""/* ---------------- VS screen ---------------- */
function drawVSMulti(){   // 2v2 / free-for-all intro: every fighter's card in a row
  const t=G.pt, n=G.f.length;
  const ease=x=>{ x=Math.min(1,Math.max(0,x)); return 1-Math.pow(1-x,3); };
  const leave=ease((t-(VS_LEN-14))/14);
  ctx.fillStyle=`rgba(10,8,16,${0.82*(1-leave)})`; ctx.fillRect(0,0,W,H);
  const CH_=112, gap=G.teams?22:8;
  const ws=G.f.map(f=>{ const im=cardImg(f); return Math.round(CH_*((im&&im.naturalWidth)?im.naturalWidth/im.naturalHeight:(im&&im.width?im.width/im.height:168/382))); });
  const total=ws.reduce((a,b)=>a+b,0)+gap*(n-1)+(G.teams?16:0);
  let x=(W-total)/2;
  G.f.forEach((f,i)=>{
    const enter=ease((t-2-i*5)/14), off=(1-enter)*H+leave*H*(i%2?1:-1), w=ws[i], col=tagCol(f), im=cardImg(f), y=22+off;
    ctx.fillStyle='rgba(0,0,0,.55)'; ctx.fillRect(x+3,y+3,w,CH_);
    if(im&&(im.naturalWidth||im.width)){ ctx.imageSmoothingEnabled=true; ctx.drawImage(im,x,y,w,CH_); ctx.imageSmoothingEnabled=false; }
    ctx.strokeStyle=col; ctx.lineWidth=2; ctx.strokeRect(x-1,y-1,w+2,CH_+2);
    txt(tagTxt(f),x+w/2,y+CH_+6,8,tagTxt(f)==='YOU'?'#ffd23f':col);
    x+=w+gap; if(G.teams && i===1){ if(t>=VS_SLAM&&leave<1) txt('VS',x-gap/2+8,y+CH_/2-8,16,'#ffd23f'); x+=16; }
  });
  if(leave<1 && t>VS_SLAM){ ctx.save(); ctx.globalAlpha=1-leave; txt(G.teams?'2 VS 2':'FREE-FOR-ALL',W/2,6,8,'#ffd23f'); txt(`${G.rules.stocks||3} ${(G.rules.stocks||3)===1?'LIFE':'LIVES'} EACH`,W/2,H-16,8,'#ffffff'); ctx.restore(); }
  if(!NET.active && t>40 && t<VS_LEN-14 && (t>>4)%2) txt('TAP TO SKIP',W-60,H-16,8,'#a99fbf');
}""")
open(P,'w').write(s); print('render ok')
