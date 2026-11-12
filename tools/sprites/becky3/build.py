# Becky v3: Alex's "game ready package" (Nov 2026), one PNG per frame in art/originals/becky-v3/.
# Cleans, scales and anchors every frame, maps them to the frame names the game uses, writes frames.pkl + lineup.png.
# The package also had its own atlas/JSON, but it squashed every frame to the same height (lying poses came out
# huge), so the game is built from the single PNGs instead.
import os, pickle, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
SRC='../../../art/originals/becky-v3/'
STAND=146      # her idle height in the package
TARGET=100     # her idle height in the game atlas (2x detail), same as every Becky before
G=TARGET/STAND
# Alex (Nov 12 2026): "her height changes a lot based on the move". The package draws her head the same size in every
# move (checked by matching her face across frames), but idle/walk have longer legs (146 px tall) than the fighting
# stances (121-135 px). So each move gets its own scale that makes her standing height match idle; her head then
# differs by under a pixel in the game, while her height stays put. REF = a standing frame of that move.
REF={'idle':'idle0','walk':'walk0','run':'walk0','block':'block1','punch':'punch3','kick':'kick0','hit':'hit0',
     'getup':'getup3','special':'special0','jump':'punch3','down':'punch3','super':'super0'}
def standing_h(n):
    a=np.asarray(Image.open(SRC+n+'.png').convert('RGBA'))[...,3]>128; ys=np.where(a.any(1))[0]; return ys.max()-ys.min()+1
RS={row:STAND/standing_h(n) for row,n in REF.items()}
def rowof(n): return n.rstrip('0123456789')

def load(name, clean=True):
    a=np.asarray(Image.open(SRC+name+'.png').convert('RGBA')).copy()
    if clean:   # keep only the figure: drops faint stray lines left over from the sheet (block0, punch0)
        m=a[...,3]>40; lab,k=nd.label(m)
        if k>1:
            sz=nd.sum(m,lab,range(1,k+1)); keep=np.isin(lab,[i+1 for i,s in enumerate(sz) if s>=0.02*sz.max()])
            a[~keep]=0
    return a
def down(arr,scale=G):
    a=arr.astype(np.float32)/255; pm=a.copy(); pm[...,:3]*=pm[...,3:4]
    h,w=arr.shape[:2]; nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
    r=np.asarray(Image.fromarray((pm*255).astype(np.uint8),'RGBA').resize((nw,nh),Image.BOX)).astype(np.float32)/255
    al=r[...,3:4]; rgb=np.where(al>0,r[...,:3]/np.maximum(al,1e-4),0); keep=al>0.5   # crisp edges, like the other fighters
    out=(np.concatenate([np.clip(rgb,0,1)*keep,keep],2)*255).astype(np.uint8)
    ys,xs=np.where(out[...,3]>0); return out[ys.min():ys.max()+1, xs.min():xs.max()+1]
def torso(a,band=(0.30,0.55),exclude=None):
    al=a[...,3]>0
    if exclude is not None: al=al&~exclude
    lab,k=nd.label(al)
    if k>1: al=lab==(np.argmax(nd.sum(al,lab,range(1,k+1)))+1)
    H=a.shape[0]; b=al.copy(); b[:int(band[0]*H)]=False; b[int(band[1]*H):]=False
    return float(np.median(np.where(b)[1]))
def com(a): return float(np.where(a[...,3]>0)[1].mean())
F={}
def add(name,a,ax): F[name]=dict(img=a,ax=ax,ay=a.shape[0])   # feet on the bottom row
UP='upright'
MAP=[  # game name, package frame, anchor
 *[(f'idle{i}',f'idle{i}',UP) for i in range(4)],
 *[(f'walk{i}',f'walk{i}',UP) for i in range(4)],
 *[(f'run{i}',f'run{i}',UP) for i in range(4)],   # not used in a fight yet (Alex: walk only), packed for a future dash
 *[(f'jump{i}',f'jump{i}',UP) for i in range(4)],
 *[(f'block{i}',f'block{i}',UP) for i in range(4)],
 *[(f'punch{i}',f'punch{i}',UP) for i in range(4)],
 *[(f'kick{i}',f'kick{i}',UP) for i in range(4)],
 *[(f'hit{i}',f'hit{i}',UP) for i in range(4)],
 ('down0','down0','com'),('down1','down1','com'),('down2','down2','com'),('down3','down3','com'),
 ('getup0','getup0','com'),('getup1','getup1','com'),('getup2','getup2',UP),('getup3','getup3',UP),
 *[(f'special{i}',f'special{i}',UP) for i in (0,1,2,3,4,6)],
]
i0=down(load('idle0')); OFF=torso(i0)-i0.shape[1]/2   # idle0 is anchored on its centre; the rest share its body line
for g,p,how in MAP:
    a=down(load(p),G*RS[rowof(p)]); add(g,a,(torso(a)-OFF) if how==UP else com(a))
print('per-move scale vs idle:',{k:round(v,3) for k,v in RS.items()})
# where the coffee mug leaves her fist: front of the fist in special3 (arm out), [ahead, above feet] in game px before drawK
s=F['special3']; im=s['img']; c=im[...,:3].astype(int); al=im[...,3]>0
skin=al&(c[...,0]>150)&(c[...,1]>80)&(c[...,2]<150)&(c[...,0]>c[...,1]+25); skin[int(im.shape[0]*0.55):]=False
fx=int(np.where(skin.any(0))[0].max()); fy=float(np.where(skin[:,fx-5:fx+1].any(1))[0].mean())
HAND=[round((fx-s['ax'])/2,1),round((s['ay']-fy)/2,1)]
# ---- super: Becky frames 0-6 and 8 (1-3 have the bookshelf drawn in), frame 7 is the books bursting
SU={}
def wood(a):
    c=a[...,:3].astype(int); return (a[...,3]>0)&(c[...,0]>90)&(c[...,0]<200)&(c[...,1]>40)&(c[...,1]<130)&(c[...,2]<80)&(c[...,0]>c[...,1]+25)
for n in (0,1,2,3,4,5,6,8):
    a=down(load(f'super{n}',clean=False),G*RS['super']); w=wood(a)
    shelf=np.zeros(a.shape[1],bool)
    if n in (1,2,3):   # the shelf is the solid block of wood on the right (her brown hair also looks like wood, so only look there)
        colw=w.sum(0); hit=colw>0.25*a.shape[0]; hit[:int(a.shape[1]*0.55)]=False; shelf=hit
    ex=np.zeros_like(w)
    if shelf.any():
        x0=int(np.where(shelf)[0].min())-2; ex[:,x0:]=True
    SU[str(n)]=dict(img=a,ax=torso(a,(0.45,0.62),ex)-OFF,ay=a.shape[0],shelf=(np.where(shelf)[0] if shelf.any() else None))
s1=SU['1']; xs=s1['shelf']; SHELF_DX=round(((xs.min()+xs.max())/2-s1['ax'])/2,1)   # shelf centre ahead of her (game px)
# book stack in her hands (super5): where the thrown stack starts, [ahead, above feet]
a=SU['5']['img']; c=a[...,:3].astype(int); bl=(a[...,3]>0)&(c[...,2]>130)&(c[...,2]>c[...,0]+40)
ys,xs=np.where(bl); REL=[round((xs.mean()-SU['5']['ax'])/2,1),round((SU['5']['ay']-ys.mean())/2,1)]
PROPS={'burst':down(load('super7',clean=False),G*RS['super']),'mugfly':down(load('special5',clean=False),G*RS['special'])}
print('hand',HAND,'shelf',SHELF_DX,'stack release',REL,'mug prop',PROPS['mugfly'].shape,'burst',PROPS['burst'].shape)
pickle.dump(dict(F=F,SU=SU,PROPS=PROPS,hand=HAND,shelf=SHELF_DX,rel=REL),open('frames.pkl','wb'))
# ---- contact sheet: red line = anchor, so a row of frames should stand on one spot without sliding
rows=[[f'idle{i}' for i in range(4)]+[f'walk{i}' for i in range(4)],[f'run{i}' for i in range(4)]+[f'jump{i}' for i in range(4)],
 [f'block{i}' for i in range(4)]+[f'punch{i}' for i in range(4)],[f'kick{i}' for i in range(4)]+[f'hit{i}' for i in range(4)],
 [f'down{i}' for i in range(4)]+[f'getup{i}' for i in range(4)],[f'special{i}' for i in (0,1,2,3,4,6)]]
L=Image.new('RGBA',(1400,(len(rows)+1)*130),(110,170,235,255)); d=ImageDraw.Draw(L)
for r,row in enumerate(rows):
    x=70
    for n in row:
        f=F[n]; base=r*130+122
        L.alpha_composite(Image.fromarray(f['img']),(int(x-f['ax']),int(base-f['ay'])))
        d.line([(x,r*130+10),(x,base)],fill=(255,0,0,255)); d.line([(x-30,base),(x+30,base)],fill=(255,0,0,255)); d.text((x-25,r*130+1),n,fill=(0,0,0,255))
        x+=165
r=len(rows); x=70
for n in ('0','1','2','3','4','5','6','8'):
    s=SU[n]; base=r*130+122; L.alpha_composite(Image.fromarray(s['img']),(int(x-s['ax']),int(base-s['ay']))); d.line([(x,r*130+10),(x,base)],fill=(255,0,0,255)); x+=165
L.save('lineup.png')
