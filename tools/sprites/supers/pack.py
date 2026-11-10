import numpy as np, json, pickle, base64, io
from PIL import Image
exec(open('cut.py').read().split("out={}")[0].replace("exec(open('seg.py').read().split(\"if __name__\")[0])","exec(open('seg.py').read().split(\"if __name__\")[0])"))
out=pickle.load(open('super.pkl','rb'))
POSE={'ac':3,'brick':2,'becky':1,'volt':0}
res={}
for key,o in out.items():
    items=[]
    for j,f in enumerate(o['frames']): items.append((str(j),f['img'],f['ax'],f['ay'],2))
    # high-detail power pose for the close-up
    spec=F[key]; img,a,fg,lab,comps,vline=analyse(key)
    badges=[(c['x0'],c['y0'],c['x1'],c['y1']) for c in comps if c['lum']<70 and 30<=c['w']<=95 and 25<=c['h']<=65 and c['fill']>0.45]
    box=spec['frames'][POSE[key]]; rgba,(ox,oy),bb=cut(img,a,box,badges); x0,y0,x1,y1=bb
    fp=o['frames'][POSE[key]]; hd=down(rgba[y0:y1,x0:x1],fp['sc']*2)
    items.append(('hd',hd,fp['ax']*2,fp['ay']*2,4))
    meta={}
    for name,v in o['fx'].items():
        al=v[...,3]>0; rgb=v[...,:3].astype(int)
        if name in('bar_fly','bar_spin'):
            dark=al&(rgb.mean(2)<90); ys,xs=np.where(dark); ax,ay=float(np.median(xs)),float(np.median(ys))
        elif name in('loop_fly','loop_snare','star'): ax,ay=v.shape[1]/2,v.shape[0]/2
        else: ax,ay=v.shape[1]/2,v.shape[0]
        items.append((name,v,ax,ay,2))
    # gameplay points measured from the art (game px: ahead of anchor, above feet)
    if key=='ac':
        f5=o['frames'][5]; v=f5['img']; al=v[...,3]>0; rgb=v[...,:3].astype(int)
        cols=np.arange(v.shape[1])[None,:]; rows=np.arange(v.shape[0])[:,None]
        m=al&(rgb.mean(2)<80)&(cols>f5['ax']+14)&(rows<f5['ay']-50); ys,xs=np.where(m)
        meta['release']=[round((xs.mean()-f5['ax'])/2,1),round((f5['ay']-ys.mean())/2,1)]
    if key=='becky':
        f2=o['frames'][2]; v=f2['img']; al=v[...,3]>0; rgb=v[...,:3].astype(int)
        cols=np.arange(v.shape[1])[None,:]
        m=al&(rgb[...,1]>140)&(rgb[...,1]>rgb[...,0]+40)&(cols>f2['ax']+20); ys,xs=np.where(m)
        meta['loop']=[round((xs.mean()-f2['ax'])/2,1),round((f2['ay']-ys.mean())/2,1)]
        meta['hand']=[round((xs.min()-f2['ax'])/2,1),round((f2['ay']-ys.mean())/2,1)]
    W=1024; x=y=sh=0; pos={}
    for name,im,ax,ay,dv in sorted(items,key=lambda t:-t[1].shape[0]):
        h,w=im.shape[:2]
        if x+w+1>W: x=0; y+=sh+1; sh=0
        pos[name]=(x,y,w,h,ax,ay,dv); x+=w+1; sh=max(sh,h)
    H=y+sh; atlas=Image.new('RGBA',(W,H),(0,0,0,0))
    for name,im,ax,ay,dv in items:
        px,py=pos[name][:2]; atlas.paste(Image.fromarray(im,'RGBA'),(px,py))
    q=atlas.quantize(colors=255,method=Image.FASTOCTREE,dither=Image.Dither.NONE)
    buf=io.BytesIO(); q.save(buf,'PNG',optimize=True)
    res[key]={'src':'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode(),
              'spr':{n:[p[0],p[1],p[2],p[3],int(round(p[4])),int(round(p[5])),p[6]] for n,p in pos.items()},'meta':meta}
    print(key,'atlas',W,H,len(buf.getvalue())//1024,'KB',meta)
json.dump(res,open('supers.json','w'))
