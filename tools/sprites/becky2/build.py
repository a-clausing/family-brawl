# Scale and anchor the v2 frames, pull in the old poses the v2 sheet doesn't have, write frames.pkl + lineup.png
import numpy as np, pickle, json, base64, io, re, subprocess
from PIL import Image, ImageDraw
R,P=pickle.load(open('raw.pkl','rb'))
R['sp']=R['sp'][1:]            # drop the label bar
R['su']=R['su'][:6]+R['su'][7:]  # drop frame 7 (books only; kept as a prop)
STAND=103                       # her idle height on Alex's sheet
SC={'idle':1,'walk':1,'jump':1.05,'run':1.05,'lp':1.2,'hp':1.2,'rk':1.2,'hit':1.2,'kd':1.2,'getup':1.2,'sp':1.05,'su':0.86}
# old atlas (v1 art): the poses Alex chose to keep
old_js=subprocess.run(['git','show','f59de20:src/assets/becky-sheet.js'],capture_output=True,text=True,cwd='../../..').stdout
src=re.search(r'src:"data:image/png;base64,([^"]+)"',old_js).group(1)
spr=json.loads(re.search(r'spr:(\{.*?\})',old_js).group(1))
oldimg=np.asarray(Image.open(io.BytesIO(base64.b64decode(src))).convert('RGBA'))
TARGET=spr['idle0'][3]          # keep her drawn height exactly as before
print('target idle height',TARGET)
def down(arr,scale):
    a_=arr.astype(np.float32)/255; pm=a_.copy(); pm[...,:3]*=pm[...,3:4]
    h,w=arr.shape[:2]; nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
    r=np.asarray(Image.fromarray((pm*255).astype(np.uint8),'RGBA').resize((nw,nh),Image.BOX if scale<1 else Image.LANCZOS)).astype(np.float32)/255
    al=np.clip(r[...,3:4],0,1); rgb=np.where(al>0,r[...,:3]/np.maximum(al,1e-4),0); keep=al>0.5
    return (np.concatenate([np.clip(rgb,0,1)*keep,keep],2)*255).astype(np.uint8)
def torso(a2,xmax=None):
    al=a2[...,3]>0
    if xmax is not None: al=al.copy(); al[:,xmax:]=False
    rows=np.where(al.any(1))[0]; top,bot=rows.min(),rows.max(); H=bot-top
    band=al.copy(); band[:top+int(0.30*H)]=False; band[top+int(0.55*H):]=False
    return float(np.median(np.where(band)[1]))
F={}
def add(name,a2,ax,ay): F[name]=dict(img=a2,ax=ax,ay=ay)
g=TARGET/STAND
# reference offset from idle0 so the standing poses sit where the old ones did
i0=down(R['idle'][0]['img'],g); off=torso(i0)-i0.shape[1]/2
def std(name,arr,row,ax=None):
    a2=down(arr,g*SC[row]); al=a2[...,3]>0; feet=int(np.where(al.any(1))[0].max())+1
    add(name,a2,(torso(a2)-off) if ax is None else ax(a2),feet)
for i,f in enumerate(R['idle']): std(f'idle{i}',f['img'],'idle')
for i,f in enumerate(R['walk']): std(f'walk{i}',f['img'],'walk')
for i,f in enumerate(R['jump']): std(f'jump{i}',f['img'],'jump')
for i,f in enumerate(R['lp']): std(f'lp{i}',f['img'],'lp')
for i,f in enumerate(R['hp']): std(f'hp{i}',f['img'],'hp')
for i,f in enumerate(R['rk']): std(f'rk{i}',f['img'],'rk')
for i,f in enumerate(R['hit']): std(f'hit{i}',f['img'],'hit')
for i,f in enumerate(R['kd']): std(f'down{i}',f['img'],'kd',None if i<2 else (lambda a:a.shape[1]*0.5))
for i,f in enumerate(R['getup']): std(f'getup{i}',f['img'],'getup',(lambda a:a.shape[1]*0.5) if i==0 else None)
for i,f in enumerate(R['sp']): std(f'special{i}',f['img'],'sp')
# kept v1 poses (already at atlas scale)
KEEP={'jump0':'crouch','block0':'block0','block1':'block1','block2':'block2','block3':'block3','lkick1':'air0','lkick2':'air1',
      'lpunch1':'t_lpunch1','hpunch3':'t_hpunch3','hpunch4':'t_hpunch4','hpunch5':'t_hpunch5','special1':'oldwin'}
for o,n in KEEP.items():
    x,y,w,h,ax,ay=spr[o]; add(n,oldimg[y:y+h,x:x+w].copy(),ax,ay)
# mug release point: front of her fist in special2 (arm out), as [ahead, above feet] in game px before drawK
s2=F['special2']; im=s2['img']; rgb=im[...,:3].astype(int); al=im[...,3]>0
skin=al&(rgb[...,0]>150)&(rgb[...,1]>70)&(rgb[...,1]<175)&(rgb[...,2]<130)&(rgb[...,0]>rgb[...,1]+25); skin[int(im.shape[0]*0.5):]=False
fx=int(np.where(skin.any(0))[0].max()); hy=float(np.where(skin[:,fx-4:fx+1].any(1))[0].mean())
hand=[round((fx-s2['ax'])/2,1),round((s2['ay']-hy)/2,1)]
print('mug hand',hand)
# ---- super: Becky + bookshelf composites, anchored on the shelf so it stands still
SU={}
gs=g*SC['su']; offs=[]; shelfL=[]
for i,f in enumerate(R['su'][:6]):
    a2=down(f['img'],gs); al=a2[...,3]>0
    sl=int(np.where(al[:5].any(0))[0].min()); bt=torso(a2,sl-1)
    feet=int(np.where(al[:, :sl].any(1))[0].max())+1
    shelfL.append(sl); offs.append(sl-bt); SU[str(i)]=dict(img=a2,sl=sl,bt=bt,ay=feet)
D=float(np.mean(offs))
for i in range(6):
    s=SU[str(i)]; s['ax']=s['sl']-D-off
a8=down(R['su'][6]['img'],gs); SU['6']=dict(img=a8,ax=torso(a8)-off,ay=int(np.where((a8[...,3]>0).any(1))[0].max())+1)
# standalone bookshelf (from frame 1, right of Becky), anchored at its left foot
s0=SU['0']; sh=s0['img'][:,s0['sl']-1:].copy()
from scipy import ndimage as nd
lab,k=nd.label(sh[...,3]>0); big=np.argmax(nd.sum(sh[...,3]>0,lab,range(1,k+1)))+1; sh[...,3]=np.where(lab==big,255,0); sh[...,:3]*=(lab==big)[...,None]
SHELF=dict(img=sh,ax=0,ay=int(np.where((sh[...,3]>0).any(1))[0].max())+1,dx=round((s0['sl']-1-s0['ax'])/2,1))
print('shelf left edge ahead of her (game px):',SHELF['dx'],'D',D)
pickle.dump(dict(F=F,SU=SU,SHELF=SHELF,P=P,hand=hand),open('frames.pkl','wb'))
# contact sheet
groups=[['idle0','idle1','idle2','idle3','walk0','walk1','walk2','walk3','crouch'],['jump0','jump1','jump2','jump3','air0','air1','block0','block1','block2','block3'],
 ['lp0','lp1','lp2','hp0','hp1','hp2','rk0','rk1','rk2'],['hit0','hit1','hit2','down0','down1','down2','down3','getup0','getup1','getup2'],
 ['special0','special1','special2','special3','special4','t_lpunch1','t_hpunch3','t_hpunch4','t_hpunch5','oldwin']]
L=Image.new('RGBA',(1500,(len(groups)+1)*125),(110,170,235,255)); d=ImageDraw.Draw(L)
for r,gr in enumerate(groups):
    x=60
    for n in gr:
        f=F[n]; base=r*125+118
        L.alpha_composite(Image.fromarray(f['img'],'RGBA'),(int(x-f['ax']),int(base-f['ay'])))
        d.line([(x,r*125+8),(x,base)],fill=(255,0,0,255)); d.line([(x-25,base),(x+25,base)],fill=(255,0,0,255)); d.text((x-20,r*125+2),n,fill=(0,0,0,255))
        x+=145
r=len(groups); x=60
for i in range(7):
    s=SU[str(i)]; base=r*125+122; L.alpha_composite(Image.fromarray(s['img'],'RGBA'),(int(x-s['ax']),int(base-s['ay']))); d.line([(x,r*125+8),(x,base)],fill=(255,0,0,255)); x+=200
L.save('lineup.png')
