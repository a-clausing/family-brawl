import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
SRC='../../../art/originals/bmoney-sheet.png'
img=np.asarray(Image.open(SRC).convert('RGBA')); a=img[...,:3].astype(np.float32)
P={'idle':(510,14,1188,106,6),'walkf':(510,114,1188,206,6),'walkb':(510,214,1188,308,6),
 'crouch':(130,323,512,410,3),'jump':(692,320,1188,410,4),
 'lpunch':(132,421,514,506,4),'hpunch':(668,421,1188,506,6),
 'lkick':(132,516,514,603,4),'hkick':(668,516,1188,603,6),
 'combo':(132,614,668,698,6),'block':(812,614,1188,698,4),
 'dmg':(128,707,490,791,4),'down':(655,707,1188,791,5),'getup':(128,799,600,886,4),
 'special':(188,899,1188,1006,5),'super':(158,1022,1188,1184,10),'fx':(100,1198,1188,1302,4)}
def seg(name,minA=150):
    x0,y0,x1,y1,n=P[name]
    c=a[y0:y1,x0:x1]
    white=c.min(2)>225
    lab,k=nd.label(white); sz=nd.sum(white,lab,range(k+1))
    bg=np.isin(lab,np.where(sz>400)[0])&(lab>0)
    fg=nd.binary_opening(~bg,iterations=1)
    l2,k2=nd.label(fg); comps=[]
    for i,sl in enumerate(nd.find_objects(l2)):
        h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start; ar=(l2[sl]==i+1).sum()
        if ar>minA: comps.append(dict(y=sl[0].start+y0,x=sl[1].start+x0,h=h,w=w,area=int(ar),id=i+1))
    comps.sort(key=lambda c:c['x'])
    return comps,l2,(x0,y0)
if __name__=='__main__':
    vis=Image.open(SRC).convert('RGB'); d=ImageDraw.Draw(vis)
    for name,(x0,y0,x1,y1,n) in P.items():
        d.rectangle([x0,y0,x1,y1],outline=(0,160,255),width=2)
        c,_,_=seg(name)
        for q in c: d.rectangle([q['x'],q['y'],q['x']+q['w'],q['y']+q['h']],outline=(255,0,0) if q['area']>800 else (0,200,0),width=1)
        print(name,n,len(c),[(q['x'],q['w'],q['h'],q['area']) for q in c if q['area']>300])
    vis.save('panels_dbg.png')
