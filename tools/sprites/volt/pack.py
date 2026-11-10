import numpy as np, json, pickle, base64, io
from PIL import Image
frames=pickle.load(open('frames.pkl','rb'))
names={'walkf':'walk','dmg':'hit'}
items=[(f'{names.get(k,k)}{j}',fr['img'],fr['ax'],fr['ay']) for k,lst in frames.items() for j,fr in enumerate(lst)]
W=1024; x=y=sh=0; pos={}
for name,im,ax,ay in sorted(items,key=lambda t:-t[1].shape[0]):
    h,w=im.shape[:2]
    if x+w+1>W: x=0; y+=sh+1; sh=0
    pos[name]=(x,y,w,h,ax,ay); x+=w+1; sh=max(sh,h)
H=y+sh; atlas=Image.new('RGBA',(W,H),(0,0,0,0))
for name,im,ax,ay in items:
    px,py,w,h,_,_=pos[name]; atlas.paste(Image.fromarray(im,'RGBA'),(px,py))
q=atlas.quantize(colors=255,method=Image.FASTOCTREE,dither=Image.Dither.NONE)
buf=io.BytesIO(); q.save(buf,'PNG',optimize=True); data=buf.getvalue()
print('atlas',W,H,'bytes',len(data),'sprites',len(pos))
spr={n:[p[0],p[1],p[2],p[3],int(round(float(p[4]))),int(round(float(p[5])))] for n,p in pos.items()}
json.dump({'b64':base64.b64encode(data).decode(),'spr':spr},open('atlas.json','w'))
