import numpy as np
from PIL import Image
from scipy import ndimage as nd
SRC='../../../art/originals/volt-sheet.png'
img=np.asarray(Image.open(SRC).convert('RGBA')); a=img[...,:3].astype(np.float32)
# name: (sprite-area x0,y0,x1,y1, expected)
P={'idle':(515,22,1190,146,6),'walkf':(515,160,1190,271,6),'walkb':(515,288,1190,396,6),
 'crouch':(124,408,505,526,3),'jump':(694,408,1190,526,4),
 'lpunch':(124,549,505,648,4),'hpunch':(654,549,1190,648,6),
 'lkick':(124,663,505,761,4),'hkick':(654,663,1190,761,6),
 'combo':(126,780,662,881,6),'block':(798,780,1190,881,4),
 'dmg':(126,900,480,993,4),'down':(656,900,1190,993,5),'getup':(128,1012,590,1110,4),
 'special':(160,1133,1190,1298,6)}
def seg(name):
    x0,y0,x1,y1,n=P[name]
    c=a[y0:y1,x0:x1]
    white=c.min(2)>222
    lab,k=nd.label(white); sz=nd.sum(white,lab,range(k+1))
    bg=np.isin(lab,np.where(sz>400)[0])&(lab>0)
    fg=nd.binary_opening(~bg,iterations=1)
    # ignore anything touching the crop's top/bottom edge rows that is only a thin line
    l2,k2=nd.label(fg); comps=[]
    for i,sl in enumerate(nd.find_objects(l2)):
        h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start; ar=(l2[sl]==i+1).sum()
        if ar>(150 if name=='down' else 250) and h>(12 if name=='down' else 25): comps.append(dict(y=sl[0].start+y0,x=sl[1].start+x0,h=h,w=w,area=int(ar),id=i+1))
    comps.sort(key=lambda c:c['x'])
    return comps,l2,(x0,y0)
if __name__=='__main__':
    for name in P:
        c,_,_=seg(name); print(name,len(c),P[name][4],[(q['x'],q['y'],q['w'],q['h']) for q in c])
