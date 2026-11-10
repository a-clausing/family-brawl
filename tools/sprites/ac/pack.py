import numpy as np, json, pickle, base64, io
from PIL import Image
frames,fx=pickle.load(open('frames.pkl','rb'))
names={'walkf':'walk','dmg':'hit'}
items=[]
for k,lst in frames.items():
    for j,fr in enumerate(lst): items.append((f'{names.get(k,k)}{j}',fr['img'],fr['ax'],fr['ay']))
# dumbbell: anchor on the iron itself (dark, non-blue pixels), not the streak
db=fx['dumbbell']; al=db[...,3]>0; rgb=db[...,:3].astype(int)
iron=al&(rgb[...,2]<rgb[...,0]+60)&(rgb.mean(2)<120)
ys,xs=np.where(iron); dax,day=float(np.median(xs)),float(np.median(ys))
items.append(('dumbbell',db,dax,day))
imp=fx['impact']; items.append(('impact',imp,imp.shape[1]/2,imp.shape[0]))
# fist on the throw frame, relative to anchor/feet (game px)
t=frames['special'][3]; a=t['img'][...,3]>0
col=np.where(a.any(0))[0].max(); rows=np.where(a[:,col-4:col+1].any(1))[0]
fist_y=(t['ay']-rows.mean())/2; fist_x=(col-t['ax'])/2
print('fist above feet',fist_y,'ahead',fist_x,'dumbbell anchor',dax,day,db.shape)
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
json.dump({'b64':base64.b64encode(data).decode(),'spr':spr,'fist':[fist_x,fist_y]},open('atlas.json','w'))
v=Image.new('RGBA',q.size,(110,170,235,255)); v.alpha_composite(q.convert('RGBA')); v.save('atlas_view.png')
