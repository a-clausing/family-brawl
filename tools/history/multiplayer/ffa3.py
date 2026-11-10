# Menus: Arcade -> Solo / Online, 1v1 / 2v2 / Free-for-All dropdown, per-slot CPU picks, lives option; solo match setup.
P='/home/claude/iron-yard-brawl.html'; s=open(P).read()
def rep(old,new,cnt=1):
    global s
    n=s.count(old); assert n==cnt,(n,old[:120]); s=s.replace(old,new)

# ---- CSS
rep("/* Fighter select header + options button */",
"""/* Fighter select header + options button */
.fmode{appearance:none;-webkit-appearance:none;font-family:var(--pixel);font-size:11px;color:var(--gold);background:var(--panel) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 6'%3E%3Cpath d='M0 0h10L5 6z' fill='%23ffd23f'/%3E%3C/svg%3E") no-repeat right 10px center/10px 6px;
  border:2px solid var(--gold);border-radius:8px;padding:10px 30px 10px 10px;margin-left:auto;min-width:0;max-width:52%}
.fmode:focus{outline:2px solid #fff;outline-offset:1px}
.cpumulti{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px}
.cpuslot{display:flex;flex-direction:column;gap:4px;min-width:0}
.cpuslot label{font-family:var(--pixel);font-size:8px;letter-spacing:.04em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cpuslot select{appearance:none;-webkit-appearance:none;width:100%;min-width:0;font:700 13px var(--ui);color:var(--ink);background:var(--panel);border:2px solid var(--line);border-radius:8px;padding:8px 6px;text-align:center}
.lobby{display:flex;flex-direction:column;gap:6px;width:100%}
.lobby .row{display:flex;justify-content:space-between;align-items:center;gap:8px;background:var(--panel);border:2px solid var(--line);border-radius:8px;padding:8px 10px;font-size:14px}
.lobby .row b{font-family:var(--pixel);font-size:10px}
.lobby .row span{color:var(--dim);font-size:13px}""")

# ---- main menu: ARCADE + CAMPAIGN; ARCADE opens SOLO / ONLINE
rep("""    <div class="mm-btns">
      <button class="go" id="mmArcade">ARCADE</button>
      <button class="go mm-alt" id="mmOnline">PLAY ONLINE</button>
      <button class="ghostbtn mm-soon" id="mmCampaign" disabled aria-disabled="true">CAMPAIGN <span>Coming soon</span></button>
    </div>""",
"""    <div class="mm-btns" id="mmTop">
      <button class="go" id="mmArcade">ARCADE</button>
      <button class="ghostbtn mm-soon" id="mmCampaign" disabled aria-disabled="true">CAMPAIGN <span>Coming soon</span></button>
    </div>
    <div class="mm-btns" id="mmArc" hidden>
      <button class="go" id="mmSolo">SOLO</button>
      <button class="go mm-alt" id="mmOnline">ONLINE</button>
      <button class="ghostbtn" id="mmBack">Back</button>
    </div>""")
# ---- fighter select: mode dropdown, CPU slot pickers
rep("""<span class="fs-title" id="fsTitle">ARCADE</span></div>""",
"""<span class="fs-title" id="fsTitle">SOLO</span>
        <select class="fmode" id="fmodeSel" aria-label="Fight type"><option value="1v1">1 VS 1</option><option value="2v2">2 VS 2</option><option value="ffa">FREE-FOR-ALL</option></select></div>""")
rep("""      <p class="label cpuonly">CPU OPPONENT</p>
      <div class="seg seg4 cpuonly" id="cpuPick">""",
"""      <p class="label cpuonly" id="cpuLbl">CPU OPPONENT</p>
      <div class="cpumulti" id="cpuMulti" hidden></div>
      <div class="seg seg4 cpuonly" id="cpuPick">""")
# ---- options: lives
rep("""    <p class="sub optnote" id="optOnlineNote" hidden>""",
"""    <div id="optLives" hidden>
      <p class="label">LIVES</p>
      <div class="seg" id="optStk" style="grid-template-columns:repeat(5,1fr)">
        <button data-v="1">1</button><button data-v="2">2</button><button data-v="3">3</button><button data-v="4">4</button><button data-v="5">5</button>
      </div>
      <p class="sub optnote">Lose your health bar and you lose a life, then drop back in. Out of lives, you’re out. Last one standing wins.</p>
    </div>
    <p class="sub optnote" id="optOnlineNote" hidden>""")
rep("""    <p class="big" style="color:var(--gold)">FIGHT OPTIONS</p>
    <p class="label">MATCH TYPE</p>
    <div class="seg seg2" id="optMode">""",
"""    <p class="big" style="color:var(--gold)">FIGHT OPTIONS</p>
    <p class="label" id="optModeLbl">MATCH TYPE</p>
    <div class="seg seg2" id="optMode">""")
# ---- online overlay: lobby list + start button
rep("""    <div id="onWait" hidden class="onwait">
      <p class="label">ROOM CODE</p>
      <p class="code" id="codeOut">----</p>
      <p class="sub">On your friend’s phone: Play Online, then join with this code.</p>
    </div>""",
"""    <div id="onWait" hidden class="onwait">
      <p class="label">ROOM CODE</p>
      <p class="code" id="codeOut">----</p>
      <p class="sub" id="onWaitSub">On your friend’s phone: Arcade, Online, then join with this code.</p>
    </div>
    <div class="lobby" id="lobby" hidden></div>
    <button class="go" id="lobbyStart" hidden>START</button>""")

# ---- options model
rep("const OPT_DEFAULT={mode:'bestof',bestOf:5,minutes:2};","const OPT_DEFAULT={mode:'bestof',bestOf:5,minutes:2,stocks:3};")
rep("const optLabel=o=>o.mode==='mostwins'?`MOST WINS · ${o.minutes} MIN`:`BEST OF ${o.bestOf}`;",
    "const optLabel=(o,fm)=>(fm||G.fmode||'1v1')!=='1v1'?`${o.stocks||3} ${(o.stocks||3)===1?'LIFE':'LIVES'}`:(o.mode==='mostwins'?`MOST WINS · ${o.minutes} MIN`:`BEST OF ${o.bestOf}`);")
rep("txt(optLabel(G.rules),C,H*0.42+24,8,'#ffffff');","txt(optLabel(G.rules,'1v1'),C,H*0.42+24,8,'#ffffff');")
rep("const G={rules:{mode:'bestof',bestOf:5,minutes:2}, mclock:0,",
    "const G={fmode:(()=>{ try{ return localStorage.getItem('nrb.fmode')||'1v1'; }catch(e){ return '1v1'; } })(), cpuPicks:['random','random','random'], multi:false, teams:false,\n  rules:{mode:'bestof',bestOf:5,minutes:2,stocks:3}, mclock:0,")

# ---- match setup
rep("function newMatch(){\n  const other=",
"""const pickKey=p=>p==='random'?FIGHTERS[Math.floor(Math.random()*FIGHTERS.length)]:p;
// keys: fighter per slot; cpus: which slots the CPU plays; teamsOn: 2v2 (slots 0-1 vs 2-3)
function setupMulti(keys,cpus,teamsOn){
  G.multi=true; G.teams=teamsOn; AW=MULTI_AW; CAM.init=false;
  G.f=keys.map((k,i)=>{ const f=mkF(k,i,cpus[i]); f.slot=i; f.team=teamsOn?(i<2?0:1):i; return f; });
  // repeats of the same fighter wear the next color set (up to four of one fighter)
  G.f.forEach((f,i)=>{ f.alt=G.f.slice(0,i).filter(o=>o.key===f.key).length; ensurePal(f.key,f.alt); });
}
function newMatchMulti(){
  const teamsOn=G.fmode==='2v2';
  const keys=[G.pick], cpus=[false];
  G.cpuPicks.forEach((p,i)=>{ if(p==='off' && !teamsOn && i>0) return; keys.push(pickKey(p==='off'?'random':p)); cpus.push(true); });
  setupMulti(keys,cpus,teamsOn);
  G.f.forEach(f=>{ f.tag=f.cpu?'CPU':'YOU'; });
  G.rules={...G.opts}; G.mclock=0; G.sudden=false;
  G.round=1; startRound(); G.phase='vs';
}
function newMatch(){
  if(G.fmode!=='1v1') return newMatchMulti();
  G.multi=false; G.teams=false; AW=W;
  const other=""")

# ---- UI wiring
rep("""document.getElementById('mmArcade').addEventListener('click',()=>openSelect('arcade'));
document.getElementById('mmOnline').addEventListener('click',()=>openSelect('online'));
document.getElementById('fsBack').addEventListener('click',()=>{ sfx('select'); menuEl.hidden=true; mainMenu.hidden=false; });""",
"""const mmTop=document.getElementById('mmTop'), mmArc=document.getElementById('mmArc');
document.getElementById('mmArcade').addEventListener('click',()=>{ audioInit(); sfx('select'); mmTop.hidden=true; mmArc.hidden=false; });
document.getElementById('mmBack').addEventListener('click',()=>{ sfx('select'); mmArc.hidden=true; mmTop.hidden=false; });
document.getElementById('mmSolo').addEventListener('click',()=>openSelect('arcade'));
document.getElementById('mmOnline').addEventListener('click',()=>openSelect('online'));
document.getElementById('fsBack').addEventListener('click',()=>{ sfx('select'); menuEl.hidden=true; mainMenu.hidden=false; mmTop.hidden=true; mmArc.hidden=false; });
// ---- 1v1 / 2v2 / free-for-all
const fmodeSel=document.getElementById('fmodeSel'), cpuMulti=document.getElementById('cpuMulti');
const NAMES={ac:'AC',brick:'Brick',becky:'Becky',volt:'Volt',bmoney:'B-Money',winston:'Winston'};
function renderCpuSlots(){
  const fm=G.fmode, multi=fm!=='1v1', online=appMode==='online';
  document.getElementById('cpuPick').hidden=multi; cpuMulti.hidden=!multi;
  document.getElementById('cpuLbl').textContent=multi?(online?'CPUS FILL EMPTY SPOTS':(fm==='2v2'?'YOUR PARTNER & OPPONENTS':'CPU OPPONENTS')):'CPU OPPONENT';
  document.getElementById('cpuLbl').hidden=online&&!multi;
  if(!multi) return;
  const labels=fm==='2v2'?['PARTNER','OPPONENT 1','OPPONENT 2']:['CPU 1','CPU 2','CPU 3'];
  cpuMulti.innerHTML='';
  labels.forEach((lb,i)=>{
    const d=document.createElement('div'); d.className='cpuslot';
    const id='cpuSel'+i, l=document.createElement('label'); l.htmlFor=id; l.textContent=lb;
    l.style.color=fm==='2v2'?(i===0?TEAM_COL[0]:TEAM_COL[1]):SLOT_COL[i+1];
    const sel=document.createElement('select'); sel.id=id;
    const opts=[['random','Random'],...FIGHTERS.map(k=>[k,NAMES[k]])];
    if(fm==='ffa' && (i>0||online)) opts.push(['off','None']);
    for(const [v,t] of opts){ const o=document.createElement('option'); o.value=v; o.textContent=t; sel.appendChild(o); }
    if(!opts.some(o=>o[0]===G.cpuPicks[i])) G.cpuPicks[i]='random';
    sel.value=G.cpuPicks[i];
    sel.addEventListener('change',()=>{ G.cpuPicks[i]=sel.value; sfx('select'); });
    d.append(l,sel); cpuMulti.appendChild(d);
  });
}
fmodeSel.value=G.fmode;
fmodeSel.addEventListener('change',()=>{ G.fmode=fmodeSel.value; try{ localStorage.setItem('nrb.fmode',G.fmode); }catch(e){} sfx('select'); renderCpuSlots(); refreshOptsLabel(); });""")
rep("""  document.getElementById('fsTitle').textContent=mode==='online'?'PLAY ONLINE':'ARCADE';""",
    """  document.getElementById('fsTitle').textContent=mode==='online'?'ONLINE':'SOLO';
  fmodeSel.value=G.fmode; renderCpuSlots();""")
rep("""function renderOpts(){
  const o=G.opts, mw=o.mode==='mostwins';""",
"""function renderOpts(){
  const o=G.opts, mw=o.mode==='mostwins', multi=G.fmode!=='1v1';
  for(const id of ['optModeLbl','optMode']) document.getElementById(id).hidden=multi;
  document.getElementById('optLives').hidden=!multi;
  document.querySelectorAll('#optStk button').forEach(b=>b.setAttribute('aria-pressed',String(+b.dataset.v===(o.stocks||3))));""")
rep("""  document.getElementById('optBestOf').hidden=mw; document.getElementById('optMostWins').hidden=!mw;""",
    """  document.getElementById('optBestOf').hidden=mw||multi; document.getElementById('optMostWins').hidden=!mw||multi;""")
rep("""document.querySelectorAll('#optMin button').forEach(b=>b.addEventListener('click',()=>{ G.opts.minutes=+b.dataset.v; sfx('select'); renderOpts(); }));""",
    """document.querySelectorAll('#optMin button').forEach(b=>b.addEventListener('click',()=>{ G.opts.minutes=+b.dataset.v; sfx('select'); renderOpts(); }));
document.querySelectorAll('#optStk button').forEach(b=>b.addEventListener('click',()=>{ G.opts.stocks=+b.dataset.v; sfx('select'); renderOpts(); }));""")
# results
rep("""function showResult(){
  const [a,b]=G.f,""","""function showResult(){
  if(G.multi) return showResultMulti();
  const [a,b]=G.f,""")
rep("""

/* ---------------- Online play (lockstep netcode) ----------------""",
"""
function showResultMulti(){
  const you=G.f[NET.active?NET.local:0], w=G.winner, win=!!w&&(G.teams?w.team===you.team:w===you);
  const t=document.getElementById('resTitle');
  t.textContent=!w?'DRAW':(win?'YOU WIN':'YOU LOSE'); t.style.color=win?'var(--gold)':'var(--ember)';
  document.getElementById('resSub').textContent=!w?'Nobody was left standing.':(G.teams?`${TEAM_NAME[w.team]} team wins: ${G.f.filter(f=>f.team===w.team).map(f=>f.cfg.name).join(' & ')}`:`${w.cfg.name} is the last one standing`);
  document.getElementById('againBtn').textContent='REMATCH';
  document.getElementById('menuBtn').textContent=NET.active?'Leave match':'Change fighter';
  resultOv.hidden=false;
}

/* ---------------- Online play (lockstep netcode) ----------------""")
# leaving a match puts the arena back to the screen's width
rep("function toMenu(){ if(NET.active||NET.conn) netClose(); G.mode='menu';","function toMenu(){ if(NET.active||NET.conn) netClose(); G.multi=false; G.teams=false; AW=W; G.mode='menu';")
open(P,'w').write(s); print('menus ok')
