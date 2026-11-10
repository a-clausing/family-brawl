import json,re
P='/home/claude/iron-yard-brawl.html'; s=open(P).read()
WN=json.load(open('wn.json'))
def rep(old,new,cnt=1):
    global s
    n=s.count(old); assert n==cnt,(n,old[:90]); s=s.replace(old,new)
# ---------- HTML / CSS
rep('.pick[data-c="bmoney"] .spc{color:#c77dff}','.pick[data-c="bmoney"] .spc{color:#c77dff} .pick[data-c="winston"] .spc{color:#3fa9ff}')
rep('.picks{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:5px}','.picks{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:5px}')
rep('.seg.seg4{grid-template-columns:repeat(6,1fr)}','.seg.seg4{grid-template-columns:repeat(7,1fr)}')
for i,(x,r) in enumerate([(-102,-19),(-68,-12),(-34,-5),(34,5),(68,12),(102,19)]):
    pass
s=re.sub(r'\.mm-fan img:nth-child\(\d\)\{transform:[^}]*\}\n','',s)
fan=''.join('.mm-fan img:nth-child(%d){transform:translate(-50%%,-50%%) translateX(%dvh) rotate(%ddeg)}\n'%(i+1,x,r) for i,(x,r) in enumerate([(-102,-19),(-68,-12),(-34,-5),(34,5),(68,12),(102,19)]))
rep('.mm-fan img{position:absolute;','@@FAN@@.mm-fan img{position:absolute;')
s=s.replace('@@FAN@@','',1)
# insert fan rules right after the .mm-fan img rule block (ends at first '}\n' after it)
i=s.index('.mm-fan img{position:absolute;'); j=s.index('}\n',i)+2; s=s[:j]+fan+s[j:]
rep('<img data-card="bmoney" alt="">','<img data-card="bmoney" alt=""><img data-card="winston" alt="">')
pip=lambda n:'<span class="pips">'+'<span class="f"></span>'*n+'<span></span>'*(5-n)+'</span>'
card='''      <button class="pick" data-c="winston" aria-pressed="false">
        <canvas id="pv-winston" width="168" height="160"></canvas>
        <span class="nm">WINSTON</span>
        <span class="ep">The agile striker. Four fast paws, a quick bite, and a bone with your name on it.</span>
        <span class="spc">Special: Bone Throw</span>
        <span class="stats"><span>Speed</span>%s<span>Power</span>%s<span>Jump</span>%s<span>Durability</span>%s</span>
      </button>
'''%(pip(4),pip(2),pip(4),pip(2))
i=s.index('<button class="pick" data-c="bmoney"'); j=s.index('</button>\n',i)+len('</button>\n'); s=s[:j]+card+s[j:]
rep('<button data-o="bmoney" aria-pressed="false">B-Money</button>','<button data-o="bmoney" aria-pressed="false">B-Money</button>\n        <button data-o="winston" aria-pressed="false">Winston</button>')
# ---------- data
i=s.index('window.BM_SHEET='); j=s.index('\n',i)
s=s[:j+1]+'window.WN_SHEET='+json.dumps(WN['main'])+';\n'+s[j+1:]
def addkey(var,key,val):
    global s
    i=s.index('window.%s={'%var); j=s.index('\n',i); line=s[i:j]; assert line.endswith('};'),line[-20:]
    s=s[:j-2]+','+json.dumps(key)+':'+json.dumps(val)+s[j-2:]
addkey('SUPERS','winston',WN['super'])
addkey('PORTRAITS','winston',WN['face']); addkey('PORTRAITS','winston_alt',WN['face_alt'])
addkey('CARDS','winston',WN['card']); addkey('CARDS','winston_alt',WN['card_alt'])
# ---------- fighter definition
i=s.index('  bmoney: {\n    key:\'bmoney\''); j=s.index('\n  }\n};',i)
wdef='''
  },
  winston: {   // four-legged agile striker: long, low body; quick bites and paw swipes
    key:'winston', name:'WINSTON', speed:1.8, jump:-6.6, grav:0.3, weight:1.05, armor:-0.1, jumpVx:2.4, w:26, h:30,
    meterCol:'#2f9bff',
    moves:{
      punch:{st:3, ac:3, rc:7,  dmg:4, kb:1.4, hs:13, bs:8,  box:[9,27,-29,-17]},    // quick bite (chained: lunging bite)
      low:  {st:3, ac:3, rc:8,  dmg:4, kb:1.2, hs:13, bs:8,  box:[8,26,-13,-1]},     // low paw swipe at the ankles
      kick: {st:5, ac:4, rc:10, dmg:7, kb:2.4, hs:16, bs:10, box:[8,27,-24,-10]},    // quick paw swipe (chained: jumping paw strike)
      air:  {st:3, ac:12,rc:4,  dmg:6, kb:2.0, hs:15, bs:9,  box:[2,24,-12,4]},      // pounce
      // Bone Throw: grab the bone, whip the head forward, let it fly
      special:{st:13, ac:0, rc:16, cost:40}
    }'''
s=s[:j]+wdef+s[j:]
rep("CH.bmoney.altMeterCol='#2fe0a8';","CH.bmoney.altMeterCol='#2fe0a8'; CH.winston.altMeterCol='#ff8a1f';")
rep("CH.ac.jump=-7.3;   // keeps AC's jump high enough to clear the taller Brick",
"CH.ac.jump=-7.3;   // keeps AC's jump high enough to clear the taller Brick\n"
"// Winston is drawn ~62% of a human's height (33px), but his hitbox stays tall enough that standing punches still land.\n"
"CH.winston.h=46; CH.winston.w=28; CH.winston.artH=33;")
rep("  bmoney:{punch:{dmg:6}, low:{dmg:6}, kick:{dmg:10}, air:{dmg:8}, speed:2.1}\n};",
    "  bmoney:{punch:{dmg:6}, low:{dmg:6}, kick:{dmg:10}, air:{dmg:8}, speed:2.1},\n  winston:{}\n};")
# ---------- sprites
rep("bmoney:[(h,s)=>h>=255&&h<=315&&s>0.3,240,1]};","bmoney:[(h,s)=>h>=255&&h<=315&&s>0.3,240,1],winston:[(h,s)=>h>=185&&h<=240&&s>0.3,178,1]};")
wnf='''const WNS=window.WN_SHEET, WNIMG=new Image(); let wnReady=false;
WNIMG.onload=()=>{ wnReady=true; makeAlt('winston',WNIMG,(h,s)=>h>=185&&h<=240&&s>0.3,178); };
WNIMG.src=WNS.src;
function wnFrame(f){
  const key=f.state+(f.move||'');
  if(f.vS!==key){ f.vS=key; f.vA=f.anim; }
  const t=f.anim-f.vA;
  switch(f.state){
    case 'idle': if(f.landT<7 && f.anim>12) return 'jump3'; return 'idle'+(Math.floor(t/8)%6);
    case 'walk': { const i=Math.floor(t/4)%6; return (Math.sign(f.vx)===f.dir?'walk':'walkb')+i; }
    case 'jump': if(f.vy<-1.5) return 'jump1'; if(f.vy>1.5&&f.y>GROUND-12) return 'jump3'; return 'jump2';
    case 'crouch': return t<3?'crouch0':'crouch1';
    case 'block': return f.bstun>0?'block3':'block'+Math.min(2,Math.floor(t/3));
    case 'hit': return 'hit'+Math.min(3,Math.floor(t/4));
    case 'ko': if(!f.onGround) return t<8?'down0':'down1'; return f.landT<5?'down2':(f.landT<10?'down3':'down4');
    case 'win': return 'hkick'+(Math.floor(t/10)%2?3:2);
    case 'attack': {
      const m=f.cfg.moves[f.move], k=f.mf, st=m.st, ac=m.ac, rc=m.rc;
      const ph=k<=st?0:(k<=st+ac?1:2);
      const pr=ph===0?k/Math.max(1,st):(ph===2?(k-st-ac)/Math.max(1,rc):0);
      const six=()=>ph===0?Math.min(2,Math.floor(pr*3)):(ph===1?3:4+Math.min(1,Math.floor(pr*2)));
      const four=()=>ph===0?0:(ph===1?1+Math.min(1,Math.floor((k-st)/2)):3);
      switch(f.move){
        case 'low': return 'combo'+six();                         // ground swipe at the ankles
        case 'punch': return f.combo>0?'hpunch'+six():'lpunch'+four();   // quick bite; chained = lunging bite
        case 'kick':  return f.combo>0?'hkick'+six():'lkick'+four();     // paw swipe; chained = jumping paw strike
        case 'air': return ph===0?'jump1':'jump2';
        case 'special':   // bone in the mouth, whip the head forward, release, settle
          if(k<4) return 'special0';
          if(k<st-4) return 'special1';
          if(k<st) return 'special2';
          if(k<st+5) return 'special3';
          return k<st+11?'special4':'special5';
      }
    }
  }
  return 'idle0';
}
'''
rep("const SHEETS={ac:","%sconst SHEETS={ac:"%wnf)
rep("  bmoney:{S:()=>BMS,img:()=>BMIMG,frame:bmFrame,ready:()=>bmReady}};","  bmoney:{S:()=>BMS,img:()=>BMIMG,frame:bmFrame,ready:()=>bmReady},\n  winston:{S:()=>WNS,img:()=>WNIMG,frame:wnFrame,ready:()=>wnReady}};")
# ---------- tables
rep("const FIGHTERS=['ac','brick','becky','volt','bmoney'];","const FIGHTERS=['ac','brick','becky','volt','bmoney','winston'];")
rep("CINE_Z={ac:2.0,brick:1.7,becky:2.2,volt:2.4,bmoney:1.9}, CINE_FY={ac:42,brick:50,becky:31,volt:24,bmoney:20};","CINE_Z={ac:2.0,brick:1.7,becky:2.2,volt:2.4,bmoney:1.9,winston:2.6}, CINE_FY={ac:42,brick:50,becky:31,volt:24,bmoney:20,winston:14};")
rep("const SUPER_DMG={ac:62, brick:58, becky:48, volt:62, bmoney:58};","const SUPER_DMG={ac:62, brick:58, becky:48, volt:62, bmoney:58, winston:56};")
rep("volt:'OVERLOAD FURY',bmoney:'RISING QUAKE'};","volt:'OVERLOAD FURY',bmoney:'RISING QUAKE',winston:'TAIL LASH RUSH'};")
rep("const SUPER_POSE={ac:3,brick:2,becky:1,volt:0,bmoney:1};","const SUPER_POSE={ac:3,brick:2,becky:1,volt:0,bmoney:1,winston:10};")
rep("const THROW_POWER={ac:3,brick:5,becky:3,volt:3,bmoney:3};","const THROW_POWER={ac:3,brick:5,becky:3,volt:3,bmoney:3,winston:2};")
rep("volt:'HYPER SPRINT',bmoney:'GROUND RIPPLE'};","volt:'HYPER SPRINT',bmoney:'GROUND RIPPLE',winston:'BONE THROW'};")
rep("volt:mkF('volt',0,true), bmoney:mkF('bmoney',0,true)};","volt:mkF('volt',0,true), bmoney:mkF('bmoney',0,true), winston:mkF('winston',0,true)};")
rep("bmoney:document.getElementById('pv-bmoney')};","bmoney:document.getElementById('pv-bmoney'), winston:document.getElementById('pv-winston')};")
# ---------- Bone Throw
rep("  } else if(f.key==='bmoney'){   // GROUND RIPPLE",
"""  } else if(f.key==='winston'){   // BONE THROW: the bone leaves from his mouth, flies straight, blockable
    const x=f.x+f.dir*WN_MOUTH[0], y=f.y-WN_MOUTH[1];
    G.proj.push({type:'bone',owner:f,x,y,vx:f.dir*4.6,t:0,dmg:11,kb:2.4,hs:20,bs:10,kd:true});
    sparks(x,y,f.alt?WN_FX_ALT:WN_FX,5); sfx('whoosh');
  } else if(f.key==='bmoney'){   // GROUND RIPPLE""")
rep("const BM_FX=['#c77dff','#8a2be2','#f1d6ff'], BM_FX_ALT=['#4dffc3','#16a37a','#d6fff2'];",
"const BM_FX=['#c77dff','#8a2be2','#f1d6ff'], BM_FX_ALT=['#4dffc3','#16a37a','#d6fff2'];\n"
"const WN_FX=['#2f9bff','#8fd0ff','#e6f6ff'], WN_FX_ALT=['#ff8a1f','#ffc27a','#fff1e0'];\n"
"const WN_MOUTH=[21,27];   // Winston's mouth, measured from his frames: forward, up (game px)")
rep("    const box=p.type==='plate'?{x0:p.x-4,x1:p.x+4,y0:p.y-4,y1:p.y+4}:",
    "    const box=p.type==='plate'?{x0:p.x-4,x1:p.x+4,y0:p.y-4,y1:p.y+4}:p.type==='bone'?{x0:p.x-6,x1:p.x+6,y0:p.y-3,y1:p.y+3}:")
rep("      if(p.type==='plate'){ G.parts.push({type:'impact',x:hx,y:GROUND,life:18,max:18,alt:p.owner.alt}); debris(hx,GROUND-2,5); }",
    "      if(p.type==='plate'){ G.parts.push({type:'impact',x:hx,y:GROUND,life:18,max:18,alt:p.owner.alt}); debris(hx,GROUND-2,5); }\n"
    "      if(p.type==='bone'){ sparks(hx,p.y,p.owner.alt?WN_FX_ALT:WN_FX,8); G.parts.push({type:'sfx',key:'winston',name:'burst',x:hx,y:p.y,life:10,max:10,sc:0.4,alt:p.owner.alt,main:true}); }")
rep("  if(p.type==='plate' && acReady){",
"""  if(p.type==='bone' && wnReady){   // spinning bone with a blue speed trail
    const S=WNS.spr, IMGW=sheetImg('winston',p.owner.alt), dir=Math.sign(p.vx)||1;
    { const [sx,sy,w,h,ax,ay]=S.trail; ctx.save(); ctx.globalAlpha=0.85; ctx.translate(p.x-dir*5,p.y); if(dir<0) ctx.scale(-1,1); ctx.drawImage(IMGW,sx,sy,w,h,-ax/2,-ay/2,w/2,h/2); ctx.restore(); }
    { const [sx,sy,w,h,ax,ay]=S.bone; ctx.save(); ctx.translate(Math.round(p.x*2)/2,Math.round(p.y*2)/2); ctx.rotate(p.t*0.35*dir); ctx.drawImage(IMGW,sx,sy,w,h,-ax/2,-ay/2,w/2,h/2); ctx.restore(); }
    return;
  }
  if(p.type==='plate' && acReady){""")
# bone in his mouth during the wind-up
rep("    for(const f of order){ if(f.sprint) drawSprintFx(f); drawSuperExtras(f); drawFighterAny(ctx,f,f.x,f.y); }",
    "    for(const f of order){ if(f.sprint) drawSprintFx(f); drawSuperExtras(f); drawFighterAny(ctx,f,f.x,f.y); drawHeldFx(f); }")
rep("function drawSuperExtras(f){",
"""function drawHeldFx(f){   // Winston holds the bone in his mouth while winding up the throw
  if(f.key!=='winston' || f.move!=='special' || f.state!=='attack' || !wnReady) return;
  const st=f.cfg.moves.special.st; if(f.mf<4 || f.mf>=st) return;
  const [sx,sy,w,h,ax,ay]=WNS.spr.bone, k=f.mf<st-4?0:1;
  ctx.save(); ctx.translate(f.x+f.dir*(WN_MOUTH[0]-3-k),f.y-WN_MOUTH[1]+1-k*2); if(f.dir<0) ctx.scale(-1,1); ctx.rotate(-0.25-k*0.3); ctx.scale(0.8,0.8);
  ctx.drawImage(sheetImg('winston',f.alt),sx,sy,w,h,-ax/2,-ay/2,w/2,h/2); ctx.restore();
}
function drawSuperExtras(f){""")
# AI: block the bone like the dumbbell
rep("if(p.type==='plate'||p.type==='band'){ if(pd<70)","if(p.type==='plate'||p.type==='band'||p.type==='bone'){ if(pd<70)")
# push boxes: other fighters hop over his low back; super dashes pass through
rep("const through=f=>f.sprint||(f.sup&&(f.key==='volt'||(f.key==='becky'&&f.sup.ph>=2)));",
    "const through=f=>f.sprint||(f.sup&&(f.key==='volt'||f.key==='winston'||(f.key==='becky'&&f.sup.ph>=2)));")
rep("  if(a.y<=b.y-b.cfg.h+2 || b.y<=a.y-a.cfg.h+2) return; // clearing the other's head: pass over",
    "  if(a.y<=b.y-(b.cfg.artH||b.cfg.h)+2 || b.y<=a.y-(a.cfg.artH||a.cfg.h)+2) return; // clearing the other's head: pass over")
# effect sprites can face a direction
rep("ctx.save(); ctx.globalAlpha=al; ctx.translate(p.x,p.y); ctx.scale(sc,sc);\n        ctx.drawImage(sheetImg(p.key,p.alt)",
    "ctx.save(); ctx.globalAlpha=al; ctx.translate(p.x,p.y); ctx.scale(sc*(p.dir||1),sc);\n        ctx.drawImage(sheetImg(p.key,p.alt)")
open(P,'w').write(s); print('ok',len(s))
