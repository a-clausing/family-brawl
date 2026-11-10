# Pull each figure/prop out of the sheet as an RGBA crop (alpha from the cut mask)
import numpy as np, pickle
from scipy import ndimage as nd
from cut import ROWS, comps, img
def grab(name,pick=None,mina=1500,group=None):
    cs,lab,(x0,y0)=comps(name); cs=[c for c in cs if c['a']>=mina]; cs.sort(key=lambda c:c['x'])
    out=[]
    for c in cs:
        sl=c['sl']; m=lab[sl]==c['id']
        crop=img[c['y']:c['y']+c['h'],c['x']:c['x']+c['w']].copy()
        crop[...,3]=np.where(m,255,0); crop[...,:3]*=m[...,None]
        out.append(dict(img=crop,x=c['x'],y=c['y']))
    return out
def grab_box(name,box,mina=40):
    # every component whose box centre falls inside box, merged into one sprite
    cs,lab,(x0,y0)=comps(name); bx0,by0,bx1,by1=box
    sel=[c for c in cs if c['a']>=mina and bx0<=c['x']+c['w']/2<=bx1 and by0<=c['y']+c['h']/2<=by1]
    X0=min(c['x'] for c in sel); Y0=min(c['y'] for c in sel); X1=max(c['x']+c['w'] for c in sel); Y1=max(c['y']+c['h'] for c in sel)
    m=np.zeros((Y1-Y0,X1-X0),bool)
    for c in sel:
        sl=c['sl']; mm=lab[sl]==c['id']; m[c['y']-Y0:c['y']-Y0+c['h'],c['x']-X0:c['x']-X0+c['w']]|=mm
    crop=img[Y0:Y1,X0:X1].copy(); crop[...,3]=np.where(m,255,0); crop[...,:3]*=m[...,None]
    return dict(img=crop,x=X0,y=Y0)
R={k:grab(k) for k in ['idle','walk','run','jump','lp','hp','rk','hit','kd','getup','sp','su']}
P={'mug_fly':grab_box('sp',(1235,640,1300,700)),'mug':grab_box('fx',(190,915,285,1015)),'speed':grab_box('fx',(300,930,440,1000)),
   'star':grab_box('fx',(455,915,575,1015)),'stack':grab_box('fx',(595,915,720,1015)),'flybooks':grab_box('fx',(740,915,950,1015)),
   'papers':grab_box('fx',(955,915,1115,1015)),'puff':grab_box('fx',(1125,915,1330,1015)),'swoosh':grab_box('fx',(1345,915,1510,1015)),
   'books7':grab_box('su',(1150,780,1360,880))}
for k,v in R.items(): print(k,len(v),[(f['img'].shape[1],f['img'].shape[0]) for f in v])
for k,v in P.items(): print(k,v['img'].shape[1],v['img'].shape[0])
pickle.dump((R,P),open('raw.pkl','wb'))
