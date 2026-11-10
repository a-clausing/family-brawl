import numpy as np, pickle, json, base64, io
from PIL import Image
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
FXA={'bone':(0.5,0.5),'trail':(1.0,0.5),'dust':(0.5,1.0),'dust2':(0.5,1.0),'arc':(0.5,0.5),'arc2':(0.5,0.5),'burst':(0.5,0.5)}
def fxitems():
    return [(k,fx[k],fx[k].shape[1]*FXA[k][0],fx[k].shape[0]*FXA[k][1],2) for k in FXA]
it=[]
for k,lst in main.items():
    for j,f in enumerate(lst): it.append((f'{k}{j}',f['img'],f['ax'],f['ay'],2))
it+=fxitems()
src,pos,n=atlas(it); print('main atlas',n//1024,'KB',len(pos))
mainj={'src':src,'spr':{k:[v[0],v[1],v[2],v[3],int(round(v[4])),int(round(v[5]))] for k,v in pos.items()}}
it=[(str(j),f['img'],f['ax'],f['ay'],2) for j,f in enumerate(sup)]
hd=frame('crouch',1,lying=True,extra=2.0); it.append(('hd',hd['img'],hd['ax'],hd['ay'],4))
it+=fxitems()
src,pos,n=atlas(it); print('super atlas',n//1024,'KB')
supj={'src':src,'spr':{k:[v[0],v[1],v[2],v[3],int(round(v[4])),int(round(v[5])),v[6]] for k,v in pos.items()},'meta':{}}
c=json.load(open('cards.json'))
json.dump({'main':mainj,'super':supj,**c},open('wn.json','w'))
print({k:v for k,v in mainj['spr'].items() if k in('idle0','special3','bone','trail','arc','burst')})
