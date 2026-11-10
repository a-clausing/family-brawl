import numpy as np, json, pickle
from PIL import Image, ImageDraw
from scipy import ndimage as nd
exec(open('panels.py').read().split('res={}')[0])
TARGET=106
REF={'idle':118,'walkf':117,'walkb':117,'jump':97,'land':97,'block':97,'lpunch':96,'hpunch':96,'lkick':96,
     'hkick':92,'dmg':100,'down':100,'getup':100,'special':150}
use=list(REF)
def clean_mask(name,m,rgba):
    m0=m; holes=nd.binary_fill_holes(m0)&~m0
    hl,hn=nd.label(holes); hs=nd.sum(holes,hl,range(hn+1))
    m=m0|np.isin(hl,np.where(hs<80)[0])&(hl>0)
    col=rgba[...,:3].astype(np.float32); H_=m.shape[0]
    outside=~m; outside[:int(H_*0.6)]=False
    if outside.sum()>20:
        bgc=np.median(col[outside],0)
        gg=np.zeros(m.shape,np.float32)
        for dy,dx in [(0,1),(1,0),(0,-1),(-1,0)]:
            gg=np.maximum(gg,np.abs(col-np.roll(col,(dy,dx),(0,1))).max(2))
        sl_,sn=nd.label((gg<12)&m)
        for q in range(1,sn+1):
            qq=sl_==q; ys=np.where(qq)[0]
            if qq.sum()<25 or ys.mean()<H_*0.66: continue
            if np.abs(col[qq].mean(0)-bgc).max()<24: m=m&~nd.binary_dilation(qq,iterations=1)
        m=nd.binary_opening(m,iterations=1)
    cl,cn=nd.label(m)
    if cn>1: cs_=nd.sum(m,cl,range(cn+1)); cs_[0]=0; m=cl==cs_.argmax()
    return m
def cutouts(name):
    comps,fg,(ox,oy)=seg(name,12)
    l2,_=nd.label(fg); out=[]
    for c in comps:
        sl=(slice(c['y']-oy,c['y']-oy+c['h']),slice(c['x']-ox,c['x']-ox+c['w']))
        idx=np.bincount(l2[sl].ravel(),minlength=2); idx[0]=0; lid=idx.argmax()
        m=(l2[sl]==lid)
        rgba=img[c['y']:c['y']+c['h'],c['x']:c['x']+c['w']].copy()
        parts=[(m,rgba)]
        if name=='idle' and c['w']>110:   # touching frames: split at the thinnest columns
            cs=m.sum(0); w=m.shape[1]; n=max(2,round(w/76)); cuts=[0]
            for i in range(1,n):
                e=int(i*w/n); lo,hi=max(1,e-14),min(w-1,e+14); cuts.append(lo+int(np.argmin(cs[lo:hi])))
            cuts.append(w)
            parts=[(m[:,a:b],rgba[:,a:b]) for a,b in zip(cuts,cuts[1:])]
        for mm,rr in parts:
            mm=clean_mask(name,mm,rr)
            xs=np.where(mm.any(0))[0]; ys=np.where(mm.any(1))[0]
            mm=mm[ys.min():ys.max()+1,xs.min():xs.max()+1]; rr=rr[ys.min():ys.max()+1,xs.min():xs.max()+1].copy()
            rr[...,3]=np.where(mm,255,0); out.append(rr)
    return out,comps
def down(arr,scale):
    im=Image.fromarray(arr,'RGBA'); w,h=im.size; nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
    a=arr.astype(np.float32)/255; pm=a.copy(); pm[...,:3]*=pm[...,3:4]
    r=np.asarray(Image.fromarray((pm*255).astype(np.uint8),'RGBA').resize((nw,nh),Image.BOX if scale<1 else Image.LANCZOS)).astype(np.float32)/255
    al=np.clip(r[...,3:4],0,1); rgb=np.where(al>0,r[...,:3]/np.maximum(al,1e-4),0); keep=al>0.45
    return (np.concatenate([np.clip(rgb,0,1)*keep,keep],2)*255).astype(np.uint8)
frames={}; fx={}
for k in use:
    cs,comps=cutouts(k)
    if k=='special':
        byx={c['x']:a for c,a in zip(comps,cs)}
        order=[22,187,376,551,1366]
        fx['dumbbell']=byx[812]
        cs=[byx[x] for x in order]
    frames[k]=[]
    for arr in cs:
        a2=down(arr,TARGET/REF[k]); al=a2[...,3]>0
        lum=a2[...,:3].mean(2); dark=al&(lum<70)
        feet=int(np.where(dark.any(1))[0].max())+1
        top=int(np.where(al.any(1))[0].min())
        band=al.copy(); band[top+int(0.24*TARGET):]=False
        frames[k].append(dict(img=a2,feet=feet,hx=float(np.where(band)[1].mean()),w=a2.shape[1],h=a2.shape[0]))
    print(k,len(frames[k]),[f['h'] for f in frames[k]])
i0=frames['idle'][0]; off=i0['hx']-i0['w']/2
for k in use:
    for f in frames[k]: f['ax']=f['hx']-off; f['ay']=f['feet']
for j in (2,3,4): frames['down'][j]['ax']=frames['down'][j]['w']*0.55
if 'getup' in frames and frames['getup'] and frames['getup'][0]['h']<frames['getup'][-1]['h']*0.75: frames['getup'][0]['ax']=frames['getup'][0]['w']*0.5   # lying start of the get-up
# overhead wind-up: the raised dumbbell pulls the top band forward; anchor on the hips instead
f2=frames['special'][2]; al=f2['img'][...,3]>0; band=al.copy(); band[:int(f2['h']*0.55)]=False; band[int(f2['h']*0.75):]=False
f0=frames['special'][0]; al0=f0['img'][...,3]>0; b0=al0.copy(); b0[:int(f0['h']*0.55)]=False; b0[int(f0['h']*0.75):]=False
f2['ax']=float(np.where(band)[1].mean())-(float(np.where(b0)[1].mean())-f0['ax'])
# effects: dumbbell projectile and impact burst
sc=TARGET/REF['special']
fx['dumbbell']=down(fx['dumbbell'],sc)
src=img; x0,y0,x1,y1=1105,800,1366,975
crop=src[y0:y1,x0:x1].copy(); comps,fg,(ox,oy)=seg('special',12)
m=fg[y0-oy:y1-oy,x0-ox:x1-ox].copy()
m[np.arange(m.shape[0])>=m.shape[0]-6]=False
cl,cn=nd.label(m); szs=nd.sum(m,cl,range(cn+1)); m=np.isin(cl,np.where(szs>25)[0])&(cl>0)
m=nd.binary_fill_holes(m)
ys=np.where(m.any(1))[0]; xs=np.where(m.any(0))[0]
crop=crop[ys.min():ys.max()+1,xs.min():xs.max()+1]; m=m[ys.min():ys.max()+1,xs.min():xs.max()+1]
crop[...,3]=np.where(m,255,0); fx['impact']=down(crop,sc*0.7)
print('fx',{k:v.shape for k,v in fx.items()})
pickle.dump((frames,fx),open('frames.pkl','wb'))
sheet=Image.new('RGBA',(1300,len(use)*125),(110,170,235,255)); d=ImageDraw.Draw(sheet)
for r,k in enumerate(use):
    x=70
    for f in frames[k]:
        base=r*125+118; sheet.alpha_composite(Image.fromarray(f['img'],'RGBA'),(int(x-f['ax']),int(base-f['ay'])))
        d.line([(x,r*125+5),(x,base)],fill=(255,0,0,255)); d.line([(x-30,base),(x+30,base)],fill=(255,0,0,255))
        x+=170
    d.text((2,r*125+60),k,fill=(0,0,0,255))
x=900
for k,v in fx.items(): sheet.alpha_composite(Image.fromarray(v,'RGBA'),(x,1400)); x+=v.shape[1]+20
sheet.save('lineup.png')
