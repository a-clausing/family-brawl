import numpy as np, json
from PIL import Image
from scipy import ndimage as nd
im=Image.open('../../../art/originals/brick-sheet.png').convert('RGB')
a=np.asarray(im).astype(np.float32)
g=np.zeros(a.shape[:2],np.float32)
for dy,dx in [(0,1),(1,0),(0,-1),(-1,0)]:
    s=np.roll(a,(dy,dx),(0,1)); g=np.maximum(g,np.abs(a-s).max(2))
lab,n=nd.label(g<14); sizes=nd.sum(np.ones_like(lab),lab,range(n+1))
bg=np.isin(lab,np.where(sizes>8000)[0])&(lab>0)
fg=~bg
fg=nd.binary_opening(fg,iterations=1)
core=nd.binary_opening(fg,structure=np.ones((3,3)),iterations=3)
lab2,n2=nd.label(core)
res=[]
for i,sl in enumerate(nd.find_objects(lab2)):
    h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start; area=(lab2[sl]==i+1).sum()
    if area<600 or h<35: continue
    res.append((sl[0].start,sl[1].start,h,w,int(area),round(area/(h*w),2),i+1))
res.sort()
for r in res: print(r)
np.save('core.npy',lab2); np.save('fgfull.npy',fg)
