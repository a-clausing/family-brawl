import numpy as np, pickle
from PIL import Image, ImageDraw
from scipy import ndimage as nd
R=pickle.load(open('raw.pkl','rb'))
s8=R['super'][8]; R['super']=R['super'][:8]+[s8[:,:85].copy(),s8[:,85:].copy()]
def trim(a):
    ys,xs=np.where(a[...,3]>0); return a[ys.min():ys.max()+1,xs.min():xs.max()+1]
R['super']=[trim(x) for x in R['super']]
TARGET=66          # standing height (paws to ear tip) in sprite px = 33 game px, ~62% of a human fighter
def darkarea(f): c=f[...,:3].astype(int); return ((f[...,3]>0)&(c.max(2)<95)).sum()
IDLE=np.median([darkarea(f) for f in R['idle']])
def relsc(f): return np.sqrt(darkarea(f)/IDLE)      # how large the sheet drew this frame, relative to idle
ROWMED={k:np.median([relsc(f) for f in v]) for k,v in R.items() if k not in('fx','spfx')}
ROWMED['crouch']=relsc(R['crouch'][0]); ROWMED['down']=np.mean([relsc(f) for f in R['down'][:2]]); ROWMED['getup']=np.mean([relsc(f) for f in R['getup'][2:]])
def down(arr,scale):
    a_=arr.astype(np.float32)/255; pm=a_.copy(); pm[...,:3]*=pm[...,3:4]
    h,w=arr.shape[:2]; nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
    r=np.asarray(Image.fromarray((pm*255).astype(np.uint8),'RGBA').resize((nw,nh),Image.BOX if scale<1 else Image.LANCZOS)).astype(np.float32)/255
    al=np.clip(r[...,3:4],0,1); rgb=np.where(al>0,r[...,:3]/np.maximum(al,1e-4),0); keep=al>0.5
    return (np.concatenate([np.clip(rgb,0,1)*keep,keep],2)*255).astype(np.uint8)
def deshadow(a):
    al=a[...,3]>0; c=a[...,:3].astype(int); sat=c.max(2)-c.min(2)
    sh=al&(sat<28)&(c.min(2)>85)&(c.min(2)<=232); sh[:int(a.shape[0]*0.82)]=False
    a=a.copy(); a[sh]=0
    # drop specks far from the body
    lab,n=nd.label(a[...,3]>0); sz=nd.sum(a[...,3]>0,lab,range(n+1)); sz[0]=0; big=np.argmax(sz)
    for i in range(1,n+1):
        if i!=big and sz[i]<60: a[lab==i]=0
    return trim(a)
SCALE_FREE={('crouch',1),('crouch',2),('down',2),('down',3),('down',4),('getup',0),('getup',1)}
def frame(row,j,lying=False,extra=1.0):
    raw=R[row][j]; rm=ROWMED[row]
    rs=rm if ((row,j) in SCALE_FREE or row in('super','special')) else float(np.clip(relsc(raw),rm*0.93,rm*1.07))
    s=TARGET/88/rs*extra
    raw=deshadow(raw); d=down(raw,s)
    al=d[...,3]>0; c=d[...,:3].astype(int); ys,xs=np.where(al); feet=int(ys.max())+1; top=int(ys.min()); h=feet-top
    dark=al&(c.max(2)<110); band=dark.copy(); band[:top+int(0.35*h)]=False; band[top+int(0.75*h):]=False
    ax=float(np.median(np.where(band)[1])) if band.any() and not lying else d.shape[1]*0.5
    return dict(img=d,ax=ax,ay=feet,h=h,w=d.shape[1])
main={}
for row,name in [('idle','idle'),('walkf','walk'),('walkb','walkb'),('jump','jump'),('block','block'),('lpunch','lpunch'),
                 ('hpunch','hpunch'),('lkick','lkick'),('hkick','hkick'),('combo','combo'),('dmg','hit'),('crouch','crouch'),('special','special')]:
    main[name]=[frame(row,j) for j in range(len(R[row]))]
main['down']=[frame('down',j,lying=j>=2) for j in range(5)]
main['getup']=[frame('getup',j,lying=j==0) for j in range(4)]
main['crouch'][1]=frame('crouch',1,lying=True); main['crouch'][2]=frame('crouch',2,lying=True)
sup=[frame('super',j) for j in range(10)]
sup.append(frame('crouch',1,lying=True))     # 10: sprinter's crouch (close-up pose)
# effects (sizes in sprite px, i.e. 2x game px)
fx={}
def fxs(arr,w): return down(trim(arr),w/arr.shape[1])
b0=R['fx'][0]; c=b0[...,:3].astype(int); isblue=(c[...,2]-c[...,0]>50)&(b0[...,3]>0)
bone=b0.copy(); bone[isblue]=0; bone=trim(bone)
lab,n=nd.label(bone[...,3]>0); sz=nd.sum(bone[...,3]>0,lab,range(n+1)); sz[0]=0; bone[lab!=np.argmax(sz)]=0; bone=trim(bone)
trail=b0.copy(); trail[~isblue]=0; trail=trim(trail)
fx['bone']=fxs(bone,30); fx['trail']=fxs(trail,56)
fx['dust']=fxs(R['fx'][1],70); fx['dust2']=fxs(R['fx'][2],70)
fx['arc']=fxs(R['fx'][3],70); fx['arc2']=fxs(R['fx'][4],70); fx['burst']=fxs(R['fx'][5],86)
pickle.dump((main,sup,fx),open('frames.pkl','wb'))
# lineup with AC and B-Money for scale
ac=pickle.load(open('../ac/frames.pkl','rb'))[0]['idle'][0]
bm=pickle.load(open('../bmoney/frames.pkl','rb'))[0]['idle'][0]
seq=[('AC',ac),('BM',bm)]+[(k+str(j),f) for k in main for j,f in enumerate(main[k])]+[('S'+str(j),f) for j,f in enumerate(sup)]
W=1600; rows=[]; cur=[]; x=0
for n,f in seq:
    w=f['img'].shape[1]+14
    if x+w>W: rows.append(cur); cur=[]; x=0
    cur.append((n,f)); x+=w
rows.append(cur)
sh=Image.new('RGBA',(W,len(rows)*125+90),(110,170,235,255)); d=ImageDraw.Draw(sh)
for r,row in enumerate(rows):
    x=8; base=r*125+118
    d.line([(0,base),(W,base)],fill=(255,0,0,255)); d.line([(0,base-TARGET),(W,base-TARGET)],fill=(255,255,255,255))
    for n,f in row:
        sh.alpha_composite(Image.fromarray(f['img'],'RGBA'),(int(x),int(base-f['ay']))); d.line([(x+f['ax'],base-4),(x+f['ax'],base+4)],fill=(255,0,0,255))
        d.text((x,r*125+2),n,fill=(0,0,0,255)); x+=f['img'].shape[1]+14
x=8
for k,v in fx.items(): sh.alpha_composite(Image.fromarray(v,'RGBA'),(x,len(rows)*125+5)); x+=v.shape[1]+12
sh.save('lineup.png'); print(sh.size,{k:round(float(v),3) for k,v in ROWMED.items()})
