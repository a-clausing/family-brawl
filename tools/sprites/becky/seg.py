import numpy as np
from PIL import Image
from scipy import ndimage as nd
SRC='../../../art/originals/becky-sheet.png'
img=np.asarray(Image.open(SRC).convert('RGBA')); a=img[...,:3].astype(np.float32)
print(img.shape)
white=(a.min(2)>225)
lab,n=nd.label(white); sz=nd.sum(white,lab,range(n+1))
bg=np.isin(lab,np.where(sz>3000)[0])&(lab>0)
fg=~bg
# remove long straight lines (panel borders)
def longrun(M,frac):
    out=np.zeros(M.shape[0],bool)
    for i,r in enumerate(M):
        d=np.diff(np.concatenate([[0],r.astype(np.int8),[0]])); st=np.where(d==1)[0]; en=np.where(d==-1)[0]
        out[i]=len(st)>0 and (en-st).max()>frac
    return out
fg[longrun(fg,150),:]=False
fg[:,longrun(fg.T,150)]=False
fg=nd.binary_opening(fg,iterations=1)
l2,k=nd.label(fg); res=[]
for i,sl in enumerate(nd.find_objects(l2)):
    h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start; ar=(l2[sl]==i+1).sum()
    if ar>300 and h>35: res.append((sl[0].start,sl[1].start,h,w,int(ar),round(ar/(h*w),2),i+1))
res.sort()
for r in res: print(r)
np.save('lab.npy',l2)
