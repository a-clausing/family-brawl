import numpy as np, json
from PIL import Image
from scipy import ndimage as nd
SRC='../../../art/originals/ac-sheet.png'
img=np.asarray(Image.open(SRC).convert('RGBA'))
a=img[...,:3].astype(np.float32)
P={ # name: (x0,y0,x1,y1, expected frames)
 'idle':(183,6,649,170,6),'walkf':(659,6,1094,170,6),'walkb':(1104,6,1528,170,6),
 'crouch':(183,178,459,317,3),'jump':(471,178,836,317,4),'land':(848,178,1149,317,3),'block':(1161,178,1528,317,4),
 'lpunch':(183,324,553,462,4),'hpunch':(564,324,1077,462,6),'lkick':(1089,324,1528,462,4),
 'hkick':(183,469,790,602,6),'combo':(802,469,1528,602,6),
 'dmg':(8,610,437,753,4),'down':(451,610,1032,753,5),'getup':(1047,610,1528,753,4),
 'special':(8,762,1528,1004,6)}
def seg(name,T):
    x0,y0,x1,y1,n=P[name]
    top=34
    c=a[y0+top:y1-5,x0+5:x1-5]
    g=np.zeros(c.shape[:2],np.float32)
    for dy,dx in [(0,1),(1,0),(0,-1),(-1,0)]:
        s=np.roll(c,(dy,dx),(0,1)); g=np.maximum(g,np.abs(c-s).max(2))
    g[0,:]=g[-1,:]=g[:,0]=g[:,-1]=0
    lab,k=nd.label(g<T); sz=nd.sum(np.ones_like(lab),lab,range(k+1))
    bg=np.isin(lab,np.where(sz>1200)[0])&(lab>0)
    fg=~bg
    def longrun(M):
        out=np.zeros(M.shape[0],bool)
        for i,r in enumerate(M):
            d=np.diff(np.concatenate([[0],r.astype(np.int8),[0]])); st=np.where(d==1)[0]; en=np.where(d==-1)[0]
            out[i]=len(st)>0 and (en-st).max()>0.5*M.shape[1]
        return out
    fg[longrun(fg),:]=False
    fg=nd.binary_opening(fg,iterations=1)
    l2,k2=nd.label(fg); comps=[]
    for i,sl in enumerate(nd.find_objects(l2)):
        h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start; ar=(l2[sl]==i+1).sum()
        if ar>700 and h>30: comps.append(dict(y=sl[0].start+y0+top,x=sl[1].start+x0+5,h=h,w=w,area=int(ar)))
    comps.sort(key=lambda c:c['x'])
    return comps,fg,(x0+5,y0+top)
res={}
for name in P:
    best=None
    for T in [12,14,17,20,24,28,32]:
        comps,fg,off=seg(name,T)
        n=P[name][4]
        hs=[c['h'] for c in comps]
        ok=len(comps)==n or (name=='special' and len(comps)>=n)
        if ok and (best is None): best=(T,comps)
    if best is None: best=(None,seg(name,14)[0])
    res[name]=best
    print(name,'T',best[0],len(best[1]),[(c['x'],c['w'],c['h']) for c in best[1]])
json.dump({k:v[0] for k,v in res.items()},open('panelT.json','w'))
