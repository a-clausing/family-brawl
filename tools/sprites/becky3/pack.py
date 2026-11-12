# Pack Becky v3 frames: main atlas (becky-sheet.js) and super sheet (her entry in supers.js). Writes bk.json.
# The super sheet keeps the effect props cut from Alex's v2 sheet (stack, papers, puff, star, speed) from the current supers.js.
import numpy as np, json, pickle, base64, io
from PIL import Image
D=pickle.load(open('frames.pkl','rb')); F,SU,PROPS=D['F'],D['SU'],D['PROPS']
PROP_NAMES={'stack','papers','puff','star','speed','burst','mugfly'}   # drawn with drawSup, which needs the divider
def packit(items):
    W=1024; x=y=sh=0; pos={}
    for name,im,ax,ay,dv in sorted(items,key=lambda t:-t[1].shape[0]):
        h,w=im.shape[:2]
        if x+w+1>W: x=0; y+=sh+1; sh=0
        pos[name]=(x,y,w,h,ax,ay,dv); x+=w+1; sh=max(sh,h)
    at=Image.new('RGBA',(W,y+sh),(0,0,0,0))
    for name,im,ax,ay,dv in items: at.paste(Image.fromarray(im,'RGBA'),pos[name][:2])
    q=at.quantize(colors=255,method=Image.FASTOCTREE,dither=Image.Dither.NONE)
    buf=io.BytesIO(); q.save(buf,'PNG',optimize=True)
    return buf.getvalue(),{n:[p[0],p[1],p[2],p[3],int(round(float(p[4]))),int(round(float(p[5])))]+([p[6]] if (p[6]!=2 or n in PROP_NAMES) else []) for n,p in pos.items()}
data,spr=packit([(n,f['img'],f['ax'],f['ay'],2) for n,f in F.items()])
MAIN={'src':'data:image/png;base64,'+base64.b64encode(data).decode(),'spr':spr,'hand':D['hand']}
print('main',len(data),'bytes',len(spr),'frames')
s=open('../../../src/assets/supers.js').read(); old=json.loads(s[len('window.SUPERS='):].rstrip().rstrip(';'))['becky']
oim=np.asarray(Image.open(io.BytesIO(base64.b64decode(old['src'].split(',',1)[1]))).convert('RGBA'))
sup=[(k,v['img'],v['ax'],v['ay'],2) for k,v in SU.items()]
for k in ('stack','papers','puff','star','speed'):
    x,y,w,h,ax,ay,*dv=old['spr'][k]; sup.append((k,oim[y:y+h,x:x+w].copy(),ax,ay,dv[0] if dv else 2))
for k,a in PROPS.items(): sup.append((k,a,a.shape[1]/2,a.shape[0]/2,2))
data,sspr=packit(sup)
SUPER={'src':'data:image/png;base64,'+base64.b64encode(data).decode(),'spr':sspr,'meta':{'shelf':D['shelf'],'rel':D['rel']}}
print('super',len(data),'bytes',sorted(sspr))
json.dump({'main':MAIN,'super':SUPER},open('bk.json','w'))
