# Find every figure/prop on Alex's v2 Becky sheet (transparent background, white sticker halos)
import numpy as np
from PIL import Image
from scipy import ndimage as nd
SRC='../../../art/originals/becky-sheet-v2.png'
img=np.asarray(Image.open(SRC).convert('RGBA')); rgb=img[...,:3].astype(int); al=img[...,3]
def mask(x0,y0,x1,y1):
    c=rgb[y0:y1,x0:x1]; a=al[y0:y1,x0:x1]
    solid=a>200
    white=(c.min(2)>205)&solid
    m=solid&~white
    m=nd.binary_opening(m,iterations=1)
    return m
if __name__=='__main__':
    m=mask(0,0,1536,1024)
    lab,k=nd.label(nd.binary_dilation(m,iterations=2))
    res=[]
    for i,sl in enumerate(nd.find_objects(lab)):
        h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start; ar=(lab[sl]==i+1).sum()
        if ar>250 and h>20: res.append((sl[0].start,sl[1].start,w,h,int(ar)))
    res.sort()
    for r in res: print(r)
