import numpy as np, json, pickle
from PIL import Image, ImageDraw
from scipy import ndimage as nd
exec(open('panels.py').read().split('res={}')[0])   # reuse P, seg()
TARGET=119
REF={'idle':118,'walkf':114,'walkb':114,'crouch':98,'jump':98,'land':98,'block':98,'lpunch':96,'hpunch':96,'lkick':97,
     'hkick':92,'combo':92,'dmg':99,'down':99,'getup':99,'special':140}
use=['idle','walkf','walkb','jump','land','block','lpunch','hpunch','lkick','hkick','dmg','down','getup','special']
def cutouts(name):
    x0,y0,x1,y1,n=P[name]
    comps,fg,(ox,oy)=seg(name,12)
    l2,_=nd.label(fg); out=[]
    for c in comps:
        sl=(slice(c['y']-oy,c['y']-oy+c['h']),slice(c['x']-ox,c['x']-ox+c['w']))
        idx=np.bincount(l2[sl].ravel(),minlength=2); idx[0]=0; lid=idx.argmax()
        m0=(l2[sl]==lid); holes=nd.binary_fill_holes(m0)&~m0
        hl,hn=nd.label(holes); hs=nd.sum(holes,hl,range(hn+1))
        m=m0|np.isin(hl,np.where(hs<80)[0])&(hl>0)
        rgba=img[c['y']:c['y']+c['h'],c['x']:c['x']+c['w']].copy()
        # background trapped between the legs: smooth, bg-coloured patches in the lower part of the frame
        col=rgba[...,:3].astype(np.float32); H_=m.shape[0]
        outside=~m; outside[:int(H_*0.6)]=False
        if outside.sum()>20:
            bgc=np.median(col[outside],0)
            gg=np.zeros(m.shape,np.float32)
            for dy,dx in [(0,1),(1,0),(0,-1),(-1,0)]:
                gg=np.maximum(gg,np.abs(col-np.roll(col,(dy,dx),(0,1))).max(2))
            sm=(gg<12)&m; sl_,sn=nd.label(sm)
            for q in range(1,sn+1):
                qq=sl_==q; ys=np.where(qq)[0]
                if qq.sum()<25 or ys.mean()<H_*0.66: continue
                if np.abs(col[qq].mean(0)-bgc).max()<24:
                    m=m&~nd.binary_dilation(qq,iterations=1)
            m=nd.binary_opening(m,iterations=1)
        if name!='special':
            cl,cn=nd.label(m)
            if cn>1: cs_=nd.sum(m,cl,range(cn+1)); cs_[0]=0; m=cl==cs_.argmax()
        rgba[...,3]=np.where(m,255,0)
        out.append(rgba)
    return out
def down(arr,scale):
    im=Image.fromarray(arr,'RGBA'); w,h=im.size; nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
    a=arr.astype(np.float32)/255; pm=a.copy(); pm[...,:3]*=pm[...,3:4]
    r=np.asarray(Image.fromarray((pm*255).astype(np.uint8),'RGBA').resize((nw,nh),Image.BOX if scale<1 else Image.LANCZOS)).astype(np.float32)/255
    al=np.clip(r[...,3:4],0,1); rgb=np.where(al>0,r[...,:3]/np.maximum(al,1e-4),0); keep=al>0.45
    return (np.concatenate([np.clip(rgb,0,1)*keep,keep],2)*255).astype(np.uint8)
frames={}
for k in use:
    cs=cutouts(k)
    if k=='special': cs=[c for c in cs if c.shape[0]>60]   # drop flying rocks
    if k=='jump':
        for c in cs:
            for y in range(6):
                row=c[y]; red=(row[:,3]>0)&(row[:,0].astype(int)>row[:,1].astype(int)+35)
                if red.sum()>row.shape[0]*0.3: c[y,:,3]=0
    frames[k]=[]
    for arr in cs:
        a2=down(arr,TARGET/REF[k]); al=a2[...,3]>0
        lum=a2[...,:3].mean(2); dark=al&(lum<70)
        feet=int(np.where(dark.any(1))[0].max())+1
        top=int(np.where(al.any(1))[0].min())
        band=al.copy(); band[top+int(0.24*TARGET):]=False
        hx=float(np.where(band)[1].mean())
        frames[k].append(dict(img=a2,feet=feet,hx=hx,w=a2.shape[1],h=a2.shape[0]))
    print(k,len(frames[k]),[f['h'] for f in frames[k]])
i0=frames['idle'][0]; off=i0['hx']-i0['w']/2
for k in use:
    for j,f in enumerate(frames[k]):
        f['ax']=f['hx']-off; f['ay']=f['feet']
for j in (2,3,4): frames['down'][j]['ax']=frames['down'][j]['w']*0.55
if 'getup' in frames and frames['getup'] and frames['getup'][0]['h']<frames['getup'][-1]['h']*0.75: frames['getup'][0]['ax']=frames['getup'][0]['w']*0.5   # lying start of the get-up
pickle.dump(frames,open('frames.pkl','wb'))
# lineup with anchor marks
sheet=Image.new('RGBA',(1300,len(use)*135),(110,170,235,255)); d=ImageDraw.Draw(sheet)
for r,k in enumerate(use):
    x=70
    for f in frames[k]:
        base=r*135+128; sheet.alpha_composite(Image.fromarray(f['img'],'RGBA'),(int(x-f['ax']),int(base-f['ay'])))
        d.line([(x,r*135+5),(x,base)],fill=(255,0,0,255)); d.line([(x-30,base),(x+30,base)],fill=(255,0,0,255))
        x+=170 if k!='special' else 215
    d.text((2,r*135+60),k,fill=(0,0,0,255))
sheet.save('lineup.png')
