import numpy as np, json, pickle, base64, io
from PIL import Image
frames=pickle.load(open('frames.pkl','rb'))
burst=frames['special'][4]['img']
al=burst[...,3]>0
colh=np.array([ (burst.shape[0]-np.where(al[:,x])[0].min()) if al[:,x].any() else 0 for x in range(burst.shape[1])])
W_=burst.shape[1]; mid=slice(int(W_*0.3),int(W_*0.7))
cx=int(np.argmax(colh[mid]))+int(W_*0.3)
x0=max(0,cx-40); chunk=burst[:,x0:x0+80]
rows=np.where((chunk[...,3]>0).any(1))[0]; chunk=chunk[rows.min():rows.max()+1]
# store the wave at half size so it is about 15 game px tall (its hitbox is 12)
im=Image.fromarray(chunk,'RGBA'); a=np.asarray(im).astype(np.float32)/255; pm=a.copy(); pm[...,:3]*=pm[...,3:4]
r=np.asarray(Image.fromarray((pm*255).astype(np.uint8),'RGBA').resize((im.width//2,im.height//2),Image.BOX)).astype(np.float32)/255
alr=r[...,3:4]; rgb=np.where(alr>0,r[...,:3]/np.maximum(alr,1e-4),0); keep=alr>0.4
wave=(np.concatenate([np.clip(rgb,0,1)*keep,keep],2)*255).astype(np.uint8)
print('wave',wave.shape)
items=[]
names={'walkf':'walk','walkb':'walkb','dmg':'hit'}
for k,lst in frames.items():
    if k=='special':
        for j,fr in enumerate(lst):
            if j==4: continue
            items.append((f'special{j}',fr['img'],fr['ax'],fr['ay']))
        continue
    for j,fr in enumerate(lst): items.append((f'{names.get(k,k)}{j}',fr['img'],fr['ax'],fr['ay']))
items.append(('wave',wave,wave.shape[1]/2,wave.shape[0]))
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
q.save('br_atlas_q.png')
spr={n:[p[0],p[1],p[2],p[3],int(round(float(p[4]))),int(round(float(p[5])))] for n,p in pos.items()}
json.dump({'b64':base64.b64encode(data).decode(),'spr':spr},open('atlas.json','w'))
v=Image.new('RGBA',q.size,(110,170,235,255)); v.alpha_composite(q.convert('RGBA')); v.save('atlas_view.png')
