import numpy as np
from PIL import Image
from scipy import ndimage as nd
im=Image.open('../../../art/originals/ac-sheet-v1-unused.png').convert('RGB')
a=np.asarray(im).astype(np.float32)
# local gradient: max abs diff to 4-neighbours
g=np.zeros(a.shape[:2],np.float32)
for dy,dx in [(0,1),(1,0),(0,-1),(-1,0)]:
    s=np.roll(a,(dy,dx),(0,1)); g=np.maximum(g,np.abs(a-s).max(2))
smooth=g<14
lab,n=nd.label(smooth)
sizes=nd.sum(np.ones_like(lab),lab,range(n+1))
bg=np.isin(lab,np.where(sizes>15000)[0]) & (lab>0)
# close tiny holes in bg (noise speckles), then sprite = not bg
fg=~bg
fg=nd.binary_opening(fg,iterations=1)
lab2,n2=nd.label(fg)
objs=nd.find_objects(lab2)
out=[]
for i,sl in enumerate(objs):
    h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start
    area=(lab2[sl]==i+1).sum()
    if area>1500: out.append((sl[0].start,sl[1].start,h,w,area,i+1))
out.sort()
for o in out: print(o)
np.save('lab.npy',lab2)
Image.fromarray((fg*255).astype(np.uint8)).save('fg.png')
