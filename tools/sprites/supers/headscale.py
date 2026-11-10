import numpy as np, cv2, json, pickle
from PIL import Image, ImageDraw
from scipy import ndimage as nd
src=open('cut.py').read().split("out={}")[0]
exec(src)
HEADFRAC={'ac':0.20,'brick':0.19,'becky':0.17,'volt':0.20}
def body(rgba):
    al=rgba[...,3]>0; lb,n=nd.label(al); sz=nd.sum(al,lb,range(n+1)); sz[0]=0
    return lb==np.argmax(sz)
def head_template(rgba,frac):
    m=body(rgba); ys,xs=np.where(m); y0=ys.min(); h=ys.max()-y0+1
    band=m[y0:y0+int(h*frac)]; cols=np.where(band.any(0))[0]
    T=rgba[y0:y0+int(h*frac),cols.min():cols.max()+1].copy(); Tm=band[:,cols.min():cols.max()+1]
    return T,Tm
def match(R,T,Tm):
    best=(-2,1,0,0)
    img=cv2.cvtColor(np.where(R[...,3:4]>0,R[...,:3],255).astype(np.uint8),cv2.COLOR_RGB2BGR)
    for s in np.arange(0.70,1.46,0.015):
        th,tw=int(round(T.shape[0]*s)),int(round(T.shape[1]*s))
        if th<8 or tw<8 or th>img.shape[0] or tw>img.shape[1]: continue
        t=cv2.resize(cv2.cvtColor(T[...,:3].astype(np.uint8),cv2.COLOR_RGB2BGR),(tw,th),interpolation=cv2.INTER_AREA)
        mk=cv2.resize(Tm.astype(np.uint8)*255,(tw,th),interpolation=cv2.INTER_NEAREST)
        mk=cv2.merge([mk,mk,mk])
        r=cv2.matchTemplate(img,t,cv2.TM_CCOEFF_NORMED,mask=mk)
        r=np.nan_to_num(r,nan=-1,posinf=-1,neginf=-1)
        _,mx,_,loc=cv2.minMaxLoc(r)
        if mx>best[0]: best=(mx,s,loc[0],loc[1],tw,th)
    return best
report={}
for key,spec in F.items():
    img,a,fg,lab,comps,vline=analyse(key)
    badges=[(c['x0'],c['y0'],c['x1'],c['y1']) for c in comps if c['lum']<70 and 30<=c['w']<=95 and 25<=c['h']<=65 and c['fill']>0.45]
    raws=[]
    for box in spec['frames']:
        rgba,(ox,oy),bb=cut(img,a,box,badges); x0,y0,x1,y1=bb; raws.append(rgba[y0:y1,x0:x1])
    T,Tm=head_template(raws[spec['stance']],HEADFRAC[key])
    res=[]; vis=[]
    for j,R in enumerate(raws):
        sc_,s,x,y,tw,th=match(R,T,Tm); res.append((round(float(s),3),round(float(sc_),2)))
        v=Image.fromarray(np.where(R[...,3:4]>0,R[...,:3],255).astype(np.uint8)); d=ImageDraw.Draw(v); d.rectangle([x,y,x+tw,y+th],outline=(255,0,0),width=3)
        d.text((4,4),f'{s:.2f} ({sc_:.2f})',fill=(255,0,0)); vis.append(v)
    report[key]=res; print(key,res)
    W=sum(v.width+6 for v in vis); H=max(v.height for v in vis); sheet=Image.new('RGB',(W,H),(200,200,200)); x=0
    for v in vis: sheet.paste(v,(x,0)); x+=v.width+6
    sheet.thumbnail((2000,400)); sheet.save(f'head_{key}.png')
json.dump(report,open('headscale.json','w'))
