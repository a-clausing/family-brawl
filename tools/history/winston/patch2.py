P='/home/claude/iron-yard-brawl.html'; s=open(P).read()
def rep(old,new,cnt=1):
    global s
    n=s.count(old); assert n==cnt,(n,old[:90]); s=s.replace(old,new)
sup='''      else { s.fr=8; if(++s.kt>=8) return endSuper(f,o); }
      break; }
    case 'winston': {   // TAIL LASH RUSH: three high-speed passes through the opponent, a tail whip on each
      const FX=f.alt?WN_FX_ALT:WN_FX;
      if(t<=CINE){ s.fr=10;   // sprinter's crouch while blue energy streaks gather
        if(t%2===0){ const y=f.y-4-rnd()*26; part(f.x-f.dir*(14+rnd()*16),y,-f.dir*(1.5+rnd()*2),0,8+(rnd()*6|0),FX[(t>>1)%3],1,0); }
        break; }
      const minD=(f.cfg.w+o.cfg.w)/2, HITS=WN_TAIL;
      if(s.ph===0){   // launch
        s.fr=10;
        if(u===1){ dust(f.x-f.dir*10,GROUND,8); sfx('whoosh'); G.shake=Math.max(G.shake,3); }
        if(u>=7){ s.ph=1; s.pass=0; s.hitDone=false; s.trail=[]; f.dir=o.x>=f.x?1:-1; }
      } else if(s.ph===1){   // dash straight through the opponent and out the far side
        if(!s.hitDone) s.dest=clampX(o.x+f.dir*(minD+30));
        const sp=s.pass<2?9:12, px=f.x, dx=s.dest-f.x;
        f.x+=Math.sign(dx)*Math.min(Math.abs(dx),sp);
        s.fr=s.hitT>0?7:2+((s.t>>1)%3);
        s.trail.push(f.x); if(s.trail.length>5) s.trail.shift();
        if(G.t%2===0) part(f.x-f.dir*(10+rnd()*12),f.y-6-rnd()*22,-f.dir*2.5,0,7,FX[G.t%3],1,0);
        if(!s.hitDone && ((px-o.x)*(f.x-o.x)<=0 || Math.abs(f.x-o.x)<1)) wnTailHit(f,o,s,HITS[s.pass]);
        if(Math.abs(s.dest-f.x)<0.5){
          if(!s.hitDone && Math.abs(f.x-o.x)<minD+34) wnTailHit(f,o,s,HITS[s.pass]);   // pinned on a wall: still connect
          if(s.pass<2 && (o.x-f.x)*f.dir>-minD) o.x=clampX(f.x-f.dir*(minD+4));    // always finish on the far side
          s.ph=2; s.kt=0; dust(f.x,GROUND,6);
          G.parts.push({type:'sfx',key:'winston',name:'dust2',x:f.x+f.dir*4,y:GROUND+1,life:16,max:16,sc:0.55,dir:-f.dir,alt:f.alt,main:true});
        }
      } else if(s.ph===2){   // skid and turn around
        if(s.trail.length) s.trail.shift();
        if(s.pass>=2){ s.ph=3; s.kt=0; }
        else { s.fr=6; if(++s.kt>=7){ s.pass++; f.dir=o.x>=f.x?1:-1; s.trail=[]; s.ph=1; s.hitDone=false; } }
      } else if(s.ph===3){   // final skid to a stop, dust settles
        s.fr=s.kt<10?5:9; s.trail=[];
        if(s.kt<10){ f.x=clampX(f.x+f.dir*(3-s.kt*0.3)); if(s.kt%3===0) dust(f.x-f.dir*8,GROUND,3); }
        if(++s.kt>=26) return endSuper(f,o);
      }
      break; }
  }
  phys(f);'''
rep('''      else { s.fr=8; if(++s.kt>=8) return endSuper(f,o); }
      break; }
  }
  phys(f);''',sup)
rep("function superStep(f,o){",
'''const WN_TAIL=[14,14,28];   // Tail Lash Rush: two lashes, then the strongest one (56 total)
function wnTailHit(f,o,s,dmg){
  s.hitDone=true; s.hitT=6;
  const last=s.pass>=2, FX=f.alt?WN_FX_ALT:WN_FX;
  if(!last){ s.lock=true; superHit(f,o,dmg,{kb:0.3,hs:40}); }
  else { superHit(f,o,dmg,{launch:true,kb:3,hs:46,vy:-4.6,big:true}); s.lock=false;
    G.parts.push({type:'sfx',key:'winston',name:'burst',x:o.x,y:o.y-20,life:20,max:20,sc:1.25,alt:f.alt,main:true}); sparks(o.x,o.y-20,FX,14); }
  // the tail whips back across the opponent as he passes
  G.parts.push({type:'sfx',key:'winston',name:s.pass===1?'arc2':'arc',x:o.x,y:o.y-20,life:12,max:12,sc:last?1.05:0.8,dir:-f.dir,alt:f.alt,main:true});
  sparks(o.x,o.y-18,FX,6); sfx(last?'heavy':'hit');
}
function superStep(f,o){''')
rep('''  if(f.key==='becky' && (s.ph===2||(s.ph===3&&s.k===0&&s.kt<4))){''',
'''  if(f.key==='winston' && s.trail && s.trail.length && s.ph===1){   // blue afterimages behind each dash
    const col=f.alt?'#ff8a1f':'#2f9bff';
    s.trail.forEach((x,i)=>{ ctx.save(); ctx.globalAlpha=0.12+i*0.08; drawAC(ctx,f,x,f.y,col,'S:3'); ctx.restore(); });
  }
  if(f.key==='becky' && (s.ph===2||(s.ph===3&&s.k===0&&s.kt<4))){''')
open(P,'w').write(s); print('ok')
