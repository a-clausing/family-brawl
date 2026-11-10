import numpy as np
from PIL import Image
from scipy import ndimage as nd
im=Image.open('../../../art/originals/brick-sheet.png').convert('RGB')
print(im.size)
a=np.asarray(im).astype(np.float32)
g=np.zeros(a.shape[:2],np.float32)
for dy,dx in [(0,1),(1,0),(0,-1),(-1,0)]:
    s=np.roll(a,(dy,dx),(0,1)); g=np.maximum(g,np.abs(a-s).max(2))
T=float(__import__('sys').argv[1]) if len(__import__('sys').argv)>1 else 14
smooth=g<T
lab,n=nd.label(smooth)
sizes=nd.sum(np.ones_like(lab),lab,range(n+1))
bg=np.isin(lab,np.where(sizes>8000)[0])&(lab>0)
fg=nd.binary_opening(~bg,iterations=1)
lab2,n2=nd.label(fg)
out=[]
for i,sl in enumerate(nd.find_objects(lab2)):
    h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start; area=(lab2[sl]==i+1).sum()
    if area>800 and h>40: out.append((sl[0].start,sl[1].start,h,w,int(area),round(area/(h*w),2),i+1))
out.sort()
spr=[o for o in out if o[5]<0.9 and o[3]<250]
print("T",T,"sprites",len(spr),"merged",[o[:4] for o in out if not (o[5]<0.9 and o[3]<250)])
np.save('lab.npy',lab2)
Image.fromarray((fg*255).astype(np.uint8)).save('fg.png')
