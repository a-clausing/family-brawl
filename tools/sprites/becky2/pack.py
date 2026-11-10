# Pack Becky's v2 frames into her atlas and her super sheet; writes bk.json {main, super}
import numpy as np, json, pickle, base64, io
from PIL import Image
D=pickle.load(open('frames.pkl','rb')); F,SU,SHELF,P,hand=D['F'],D['SU'],D['SHELF'],D['P'],D['hand']
SKIP={'lp2','hp2','rk2','oldwin'}   # painted-on impact effects / the old band pose
def packit(items):
    W=1024; x=y=sh=0; pos={}
    for name,im,ax,ay,dv in sorted(items,key=lambda t:-t[1].shape[0]):
        h,w=im.shape[:2]
        if x+w+1>W: x=0; y+=sh+1; sh=0
        pos[name]=(x,y,w,h,ax,ay,dv); x+=w+1; sh=max(sh,h)
    at=Image.new('RGBA',(W,y+sh),(0,0,0,0))
    for name,im,ax,ay,dv in items: at.paste(Image.fromarray(im,'RGBA'),pos[name][:2])
    q=at.quantize(colors=255,method=Image.FASTOCTREE,dither=Image.Dither.NONE)
    buf=io.BytesIO(); q.save(buf,'PNG',optimize=True); data=buf.getvalue()
    v=Image.new('RGBA',q.size,(110,170,235,255)); v.alpha_composite(q.convert('RGBA'))
    return data,{n:[p[0],p[1],p[2],p[3],int(round(float(p[4]))),int(round(float(p[5])))]+([p[6]] if p[6]!=2 else []) for n,p in pos.items()},v
main=[(n,f['img'],f['ax'],f['ay'],2) for n,f in F.items() if n not in SKIP]
data,spr,v=packit(main); v.save('atlas_view.png'); print('main',len(data),'bytes',len(spr),'sprites')
MAIN={'src':'data:image/png;base64,'+base64.b64encode(data).decode(),'spr':spr,'hand':hand}
# super sheet: Becky+shelf frames at 2x, props stored at 3x their game size
sup=[(k,s['img'],s['ax'],s['ay'],2) for k,s in SU.items()]
sup.append(('shelf',SHELF['img'],0,SHELF['ay'],2))
GW={'stack':16,'flybooks':42,'papers':32,'puff':46,'star':20,'speed':18,'mug':12,'mug_fly':13}
for k,gw in GW.items():
    im=P[k]['img']; s=3*gw/im.shape[1]
    r=Image.fromarray(im,'RGBA').resize((max(1,round(im.shape[1]*s)),max(1,round(im.shape[0]*s))),Image.LANCZOS); a=np.asarray(r).copy()
    a[...,3]=np.where(a[...,3]>110,255,0); a[...,:3]*=(a[...,3:4]>0)
    ay=a.shape[0] if k=='puff' else a.shape[0]/2
    sup.append((k,a,a.shape[1]/2,ay,3))
data,spr,v=packit(sup); v.save('super_view.png'); print('super',len(data),'bytes')
SUPER={'src':'data:image/png;base64,'+base64.b64encode(data).decode(),'spr':spr,'meta':{'shelf':SHELF['dx']}}
json.dump({'main':MAIN,'super':SUPER},open('bk.json','w'))
