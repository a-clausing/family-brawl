import numpy as np, json, sys
from PIL import Image, ImageDraw
from scipy import ndimage as nd
A='../../../art/originals/'
SHEETS={'ac':'ac-super-max-rep.png','volt':'volt-super-overload-fury.png','brick':'brick-super-rack-quake.png','becky':'becky-super-band-snare.png'}
SC=2172/2000
ROWS={'ac':[(95,410),(430,660)],'volt':[(85,272),(278,475),(485,660)],'brick':[(90,420),(432,660)],'becky':[(78,302),(304,508),(518,660)]}
def runs(M):
    """length of the horizontal run of True each pixel belongs to"""
    out=np.zeros(M.shape,np.int32)
    for i,r in enumerate(M):
        d=np.diff(np.concatenate([[0],r.astype(np.int8),[0]])); st=np.where(d==1)[0]; en=np.where(d==-1)[0]
        for a,b in zip(st,en): out[i,a:b]=b-a
    return out
def analyse(key):
    img=np.asarray(Image.open(A+SHEETS[key]).convert('RGBA')); a=img[...,:3].astype(int)
    fg=a.min(2)<228
    hr=runs(fg); vr=runs(fg.T).T
    hline=(hr>=170)&(vr<=8); vline=(vr>=110)&(hr<=8)
    lines=nd.binary_dilation(hline|vline,iterations=1)
    fg2=fg&~lines
    lab,n=nd.label(fg2); objs=nd.find_objects(lab)
    comps=[]
    for i,sl in enumerate(objs):
        m=lab[sl]==i+1; area=int(m.sum())
        if area<25: continue
        y0,y1,x0,x1=sl[0].start,sl[0].stop,sl[1].start,sl[1].stop; w=x1-x0; h=y1-y0
        px=a[sl][m]; lum=px.mean(); sat=(px.max(1)-px.min(1)).mean(); fill=area/(w*h)
        comps.append(dict(id=i+1,x0=x0,y0=y0,x1=x1,y1=y1,w=w,h=h,area=area,lum=lum,sat=sat,fill=fill,std=px.std(0).mean()))
    # vertical panel borders per row -> x positions
    vx=np.where(vline.any(0))[0]
    return img,a,fg,lab,comps,vline
def classify(key,c,band):
    by0,by1=band
    # title header
    if c['y1']<int(85*SC): return 'title'
    # number badges: dark rounded boxes near the top-left of a panel
    if c['lum']<70 and 30<=c['w']<=95 and 25<=c['h']<=65 and c['fill']>0.45 and c['y0']<by0+int(70*SC): return 'badge'
    # arrows: small uniform saturated triangles
    if c['area']<1400 and 10<=c['w']<=40 and 18<=c['h']<=55 and 0.35<=c['fill']<=0.7 and c['sat']>90 and c['std']<40: return 'arrow'
    return None
if __name__=='__main__':
    for key in SHEETS:
        img,a,fg,lab,comps,vline=analyse(key)
        bands=[(int(y0*SC),int(y1*SC)) for y0,y1 in ROWS[key]]
        vis=Image.fromarray(img).convert('RGB'); d=ImageDraw.Draw(vis)
        cnt={}
        for c in comps:
            cy=(c['y0']+c['y1'])/2; band=next((b for b in bands if b[0]<=cy<b[1]),None)
            if band is None: cls='outside'
            else: cls=classify(key,c,band) or 'keep'
            cnt[cls]=cnt.get(cls,0)+1
            col={'keep':(0,200,0),'badge':(255,0,255),'arrow':(255,0,0),'title':(0,0,255),'outside':(128,128,128)}[cls]
            if c['area']>60 or cls!='keep': d.rectangle([c['x0'],c['y0'],c['x1'],c['y1']],outline=col,width=2)
        for b in bands: d.line([(0,b[0]),(2172,b[0])],fill=(255,160,0)); d.line([(0,b[1]),(2172,b[1])],fill=(255,160,0))
        vis.save(f'cls_{key}.png'); print(key,cnt)
