import numpy as np, json, pickle, base64, io
from PIL import Image
frames=pickle.load(open('frames.pkl','rb'))
# energy ball from special frame 4: bright cyan pixels in front of the fist
f4=frames['special'][4]; img=f4['img'].astype(int)
al=img[...,3]>0; lum=img[...,:3].mean(2)
cols=np.arange(img.shape[1])[None,:].repeat(img.shape[0],0)
rowsI=np.arange(img.shape[0])[:,None].repeat(img.shape[1],1)
from scipy import ndimage as nd
ballmask=nd.binary_fill_holes(al&(rowsI<f4['ay']-36)&(cols>f4['ax']+40))
ys,xs=np.where(ballmask)
x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
ball=img[y0:y1,x0:x1].copy(); ball[...,3]=np.where(ballmask[y0:y1,x0:x1],255,0)
ballcy=(y0+y1)/2; print('ball box',x0,x1,y0,y1,'center above feet (2x px):',f4['ay']-ballcy, 'ahead of anchor:',(x0+x1)/2-f4['ax'])
# items to pack
items=[]
for k,lst in frames.items():
    for j,fr in enumerate(lst): items.append((f'{k}{j}',fr['img'],fr['ax'],fr['ay']))
items.append(('ball',ball.astype(np.uint8),(x1-x0)/2,(y1-y0)/2))
nb=f4['img'].copy(); nb[...,3]=np.where(ballmask,0,nb[...,3]); nb[...,:3]*=(nb[...,3:4]>0)
items.append(('special4nb',nb,f4['ax'],f4['ay']))
# shelf packing
W=1024; x=y=sh=0; pos={}
for name,im,ax,ay in sorted(items,key=lambda t:-t[1].shape[0]):
    h,w=im.shape[:2]
    if x+w+1>W: x=0; y+=sh+1; sh=0
    pos[name]=(x,y,w,h,ax,ay); x+=w+1; sh=max(sh,h)
H=y+sh
atlas=Image.new('RGBA',(W,H),(0,0,0,0))
for name,im,ax,ay in items:
    px,py,w,h,_,_=pos[name]; atlas.paste(Image.fromarray(im,'RGBA'),(px,py))
atlas.save('ac_atlas.png',optimize=True)
q=atlas.quantize(colors=255,method=Image.FASTOCTREE,dither=Image.Dither.NONE)
buf=io.BytesIO(); q.save(buf,'PNG',optimize=True); data=buf.getvalue()
print('atlas',W,H,'png bytes',len(data))
q.save('ac_atlas_q.png')
spr={n:[p[0],p[1],p[2],p[3],int(round(float(p[4]))),int(round(float(p[5])))] for n,p in pos.items()}
json.dump({'b64':base64.b64encode(data).decode(),'spr':spr,'counts':{k:len(v) for k,v in frames.items()},
  'ballY':float(f4['ay']-ballcy)},open('atlas.json','w'))
