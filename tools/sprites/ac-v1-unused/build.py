import numpy as np, json
from PIL import Image, ImageDraw
meta=json.load(open('meta.json'))
TARGET=96   # standing height in 2x pixels (= 48 game px)
use=['idle','walk','jump','block','lpunch','hpunch','lkick','hkick','hit','down','special']
# reference standing height per sheet row (rows were drawn at different sizes)
REF={'idle':157,'walk':157,'jump':139,'block':139,'lpunch':114,'hpunch':114,'lkick':111,'hkick':111,'hit':111,'down':105,'special':107}
def down(im,scale):
    w,h=im.size; nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
    a=np.asarray(im).astype(np.float32)/255
    pm=a.copy(); pm[...,:3]*=pm[...,3:4]
    r=np.asarray(Image.fromarray((pm*255).astype(np.uint8),'RGBA').resize((nw,nh),Image.BOX)).astype(np.float32)/255
    al=r[...,3:4]; rgb=np.where(al>0,r[...,:3]/np.maximum(al,1e-4),0)
    keep=al>0.45
    return np.concatenate([np.clip(rgb,0,1)*keep,keep],2)
frames={}
for k in use:
    frames[k]=[]
    for j in range(len(meta[k])):
        im=Image.open(f'raw_{k}_{j}.png')
        a=down(im,TARGET/REF[k])
        rgb=a[...,:3]*255; al=a[...,3]>0
        lum=rgb.mean(2)
        dark=al&(lum<55)
        rows=np.where(dark.any(1))[0]; feet=int(rows.max())+1
        hair=al&(rgb[...,0]>70)&(rgb[...,0]<175)&(rgb[...,1]>35)&(rgb[...,1]<115)&(rgb[...,2]<75)&(rgb[...,0]-rgb[...,2]>40)
        top=np.where(al.any(1))[0].min()
        hz=hair.copy(); hz[top+int(0.22*TARGET):]=False
        if k=='down' or hz.sum()<6: hx=None
        else: hx=float(np.where(hz)[1].mean())
        frames[k].append(dict(img=(a*255).astype(np.uint8),feet=feet,hx=hx,w=a.shape[1],h=a.shape[0]))
# anchor: keep idle's head-to-center relation for every frame
idl=frames['idle'][0]; off=idl['hx']-idl['w']/2
print('idle head offset',off)
for k in use:
    for fr in frames[k]:
        fr['ax']= (fr['hx']-off) if fr['hx'] is not None else fr['w']/2
        fr['ay']=fr['feet']
# knockdown: lying frames anchor so the body lies behind the start point
for j,fr in enumerate(frames['down']):
    if j>=1: fr['ax']=fr['w']*0.62
# lineup check image with anchor marks
W=sum(f['w']+6 for k in use for f in frames[k][:6])
sheet=Image.new('RGBA',(1500,len(use)*120),(110,170,235,255)); d=ImageDraw.Draw(sheet)
for r,k in enumerate(use):
    x=60
    for fr in frames[k]:
        im=Image.fromarray(fr['img'],'RGBA'); base=r*120+110
        sheet.alpha_composite(im,(int(x-fr['ax']),int(base-fr['ay'])))
        d.line([(x,r*120+5),(x,base)],fill=(255,0,0,255)); d.line([(x-30,base),(x+30,base)],fill=(255,0,0,255))
        x+=140
    d.text((2,r*120+50),k,fill=(0,0,0,255))
sheet.save('lineup.png')
import pickle; pickle.dump(frames,open('frames.pkl','wb'))
