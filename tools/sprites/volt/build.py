import numpy as np, json, pickle
from PIL import Image, ImageDraw
from scipy import ndimage as nd
exec(open('panels.py').read().split("if __name__")[0])
TARGET=106   # same standing height as AC
REF={'idle':123,'walkf':111,'walkb':106,'jump':108,'block':96,'lpunch':98,'hpunch':97,'lkick':97,'hkick':97,'combo':97,
     'dmg':93,'down':93,'getup':96,'special':123}
use=list(REF)
def cut(name):
    comps,l2,(ox,oy)=seg(name)
    groups=[]
    for c in comps:   # merge pieces that overlap horizontally (effects detached from the body)
        if groups and c['x']<groups[-1]['x1']-6 and name=='special':
            g=groups[-1]; g['ids'].append(c['id']); g['x1']=max(g['x1'],c['x']+c['w']); g['y0']=min(g['y0'],c['y']); g['y1']=max(g['y1'],c['y']+c['h'])
        else: groups.append(dict(ids=[c['id']],x0=c['x'],x1=c['x']+c['w'],y0=c['y'],y1=c['y']+c['h']))
    out=[]
    for g in groups:
        sl=(slice(g['y0']-oy,g['y1']-oy),slice(g['x0']-ox,g['x1']-ox))
        m=np.isin(l2[sl],g['ids'])
        rgba=img[g['y0']:g['y1'],g['x0']:g['x1']].copy(); col=rgba[...,:3].astype(int)
        wh=(col.min(2)>215)&m; wl,wn=nd.label(wh); ws=nd.sum(wh,wl,range(wn+1))
        m=m&~(np.isin(wl,np.where(ws>=10)[0])&(wl>0))
        holes=nd.binary_fill_holes(m)&~m; hl,hn=nd.label(holes); hs=nd.sum(holes,hl,range(hn+1))
        m=m|(np.isin(hl,np.where(hs<6)[0])&(hl>0))
        rgba[...,3]=np.where(m,255,0); out.append(rgba)
    return out
def down(arr,scale):
    im=Image.fromarray(arr,'RGBA'); w,h=im.size; nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
    a_=arr.astype(np.float32)/255; pm=a_.copy(); pm[...,:3]*=pm[...,3:4]
    r=np.asarray(Image.fromarray((pm*255).astype(np.uint8),'RGBA').resize((nw,nh),Image.BOX)).astype(np.float32)/255
    al=np.clip(r[...,3:4],0,1); rgb=np.where(al>0,r[...,:3]/np.maximum(al,1e-4),0); keep=al>0.5
    return (np.concatenate([np.clip(rgb,0,1)*keep,keep],2)*255).astype(np.uint8)
frames={}
for k in use:
    frames[k]=[]
    for arr in cut(k):
        a2=down(arr,TARGET/REF[k]); al=a2[...,3]>0
        rows=np.where(al.any(1))[0]; feet=int(rows.max())+1
        top=int(rows.min())
        band=al.copy(); band[:top+int(0.25*TARGET)]=False; band[top+int(0.55*TARGET):]=False
        rgb=a2[...,:3].astype(int); dark=(rgb.mean(2)<90)
        band&=dark   # body (black armour), not the yellow lightning trails
        frames[k].append(dict(img=a2,feet=feet,hx=float(np.median(np.where(band)[1])) if band.any() else a2.shape[1]/2,w=a2.shape[1],h=a2.shape[0]))
    print(k,len(frames[k]),[f['h'] for f in frames[k]])
i0=frames['idle'][0]; off=i0['hx']-i0['w']/2
for k in use:
    for f in frames[k]: f['ax']=f['hx']-off; f['ay']=f['feet']
for j in (2,3,4): frames['down'][j]['ax']=frames['down'][j]['w']*0.55
if 'getup' in frames and frames['getup'] and frames['getup'][0]['h']<frames['getup'][-1]['h']*0.75: frames['getup'][0]['ax']=frames['getup'][0]['w']*0.5   # lying start of the get-up
d1=frames['down'][1]; d1['ax']=d1['w']*0.45
# sprint frames: speed trails stream out behind him, so anchor on the front of the body
for j in (0,1,2,3):
    f=frames['special'][j]; a=f['img'][...,3]>0; rgb=f['img'][...,:3].astype(int)
    body=a&(rgb.mean(2)<90); cols=np.where(body.sum(0)>3)[0]
    f['ax']=float(cols.max())-14 if j!=3 else float(np.percentile(np.where(body)[1],60))
pickle.dump(frames,open('frames.pkl','wb'))
sheet=Image.new('RGBA',(1300,len(use)*125),(110,170,235,255)); d=ImageDraw.Draw(sheet)
for r,k in enumerate(use):
    x=80
    for f in frames[k]:
        base=r*125+118; sheet.alpha_composite(Image.fromarray(f['img'],'RGBA'),(int(x-f['ax']),int(base-f['ay'])))
        d.line([(x,r*125+5),(x,base)],fill=(255,0,0,255)); d.line([(x-30,base),(x+30,base)],fill=(255,0,0,255))
        x+=200 if k=='special' else 165
    d.text((2,r*125+60),k,fill=(0,0,0,255))
sheet.save('lineup.png')
