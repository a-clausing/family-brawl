import numpy as np, pickle, json, base64, io, colorsys
from PIL import Image, ImageFilter
exec(open('build.py').read().split("main={}")[0])
main,sup,fx=pickle.load(open('frames.pkl','rb'))
def atlas(items):
    W=1024; x=y=sh=0; pos={}
    for name,im,ax,ay,dv in sorted(items,key=lambda t:-t[1].shape[0]):
        h,w=im.shape[:2]
        if x+w+1>W: x=0; y+=sh+1; sh=0
        pos[name]=(x,y,w,h,ax,ay,dv); x+=w+1; sh=max(sh,h)
    A=Image.new('RGBA',(W,y+sh),(0,0,0,0))
    for name,im,ax,ay,dv in items: A.paste(Image.fromarray(im,'RGBA'),pos[name][:2])
    q=A.quantize(colors=255,method=Image.FASTOCTREE,dither=Image.Dither.NONE); buf=io.BytesIO(); q.save(buf,'PNG',optimize=True)
    return 'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode(), pos, len(buf.getvalue())
it=[]
for k,lst in main.items():
    for j,f in enumerate(lst): it.append((f'{k}{j}',f['img'],f['ax'],f['ay'],2))
for k in ('ripple','burst','dust'): it.append((k,fx[k],fx[k].shape[1]/2,fx[k].shape[0],2))
src,pos,n=atlas(it); print('main atlas',n//1024,'KB',len(pos))
mainj={'src':src,'spr':{k:[v[0],v[1],v[2],v[3],int(round(v[4])),int(round(v[5]))] for k,v in pos.items()}}
it=[(str(j),f['img'],f['ax'],f['ay'],2) for j,f in enumerate(sup)]
hd=frame('special',1); hd2=frame('special',1,sc=2*TARGET/REF['special'])
it.append(('hd',hd2['img'],hd2['ax'],hd2['ay'],4))
for k in ('bigwave','arc','burst'): it.append((k,fx[k],fx[k].shape[1]/2,fx[k].shape[0] if k!='arc' else fx[k].shape[0]/2,2))
src,pos,n=atlas(it); print('super atlas',n//1024,'KB')
supj={'src':src,'spr':{k:[v[0],v[1],v[2],v[3],int(round(v[4])),int(round(v[5])),v[6]] for k,v in pos.items()},'meta':{}}
# card + face + alternates
card=Image.open('../../../art/originals/bmoney-card.png').convert('RGB')
c=card.resize((288,384),Image.LANCZOS).filter(ImageFilter.UnsharpMask(1,50,2))
face=card.crop((40,40,560,560)).resize((256,256),Image.LANCZOS)
def alt(im):
    a=np.asarray(im).astype(np.float32)/255; out=a.copy()
    mx=a.max(2); mn=a.min(2); d=mx-mn; ys,xs=np.where(d>0.12)
    for y,x in zip(ys,xs):
        h,l,s=colorsys.rgb_to_hls(*a[y,x])
        if 255<=h*360<=315 and s>0.3: out[y,x]=colorsys.hls_to_rgb(((h*360+240)%360)/360,l,s)
    return Image.fromarray((out*255).astype(np.uint8))
def enc(im,q=86): b=io.BytesIO(); im.save(b,'JPEG',quality=q,optimize=True); return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
ca=alt(c); fa=alt(face)
Image.fromarray(np.hstack([np.asarray(c),np.asarray(ca)])).save('cards_prev.png')
json.dump({'main':mainj,'super':supj,'card':enc(c),'card_alt':enc(ca),'face':enc(face,88),'face_alt':enc(fa,88)},open('bm.json','w'))
