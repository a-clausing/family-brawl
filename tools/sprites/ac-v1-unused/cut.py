import numpy as np, json
from PIL import Image
from scipy import ndimage as nd
src=np.asarray(Image.open('../../../art/originals/ac-sheet-v1-unused.png').convert('RGBA')).copy()
lab=np.load('lab.npy')
objs=nd.find_objects(lab)
comps=[]
for i,sl in enumerate(objs):
    if sl is None: continue
    h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start
    area=(lab[sl]==i+1).sum()
    if area>1500 and h>30: comps.append(dict(y=sl[0].start,x=sl[1].start,h=h,w=w,id=i+1))
# rows by y band, then sorted by x
def band(c):
    cy=c['y']+c['h']
    return 0 if cy<250 else 1 if cy<470 else 2 if cy<660 else 3 if cy<850 else 4
rows=[[] for _ in range(5)]
for c in comps: rows[band(c)].append(c)
for r in rows: r.sort(key=lambda c:c['x'])
groups={'idle':(0,0,6),'walk':(0,6,6),'crouch':(1,0,3),'jump':(1,3,4),'block':(1,7,4),
 'lpunch':(2,0,4),'hpunch':(2,4,6),'combo':(2,10,6),'lkick':(3,0,4),'hkick':(3,4,6),'hit':(3,10,4),
 'down':(4,0,6),'getup':(4,6,4),'special':(4,10,6)}
for k,(r,s,n) in groups.items(): assert len(rows[r][s:s+n])==n,(k,len(rows[r]))
# pull small nearby components (energy ball / glow bits) into the special frames
def cutout(c,pad=0):
    y0,x0,y1,x1=c['y'],c['x'],c['y']+c['h'],c['x']+c['w']
    m=(lab[y0:y1,x0:x1]==c['id'])
    m=nd.binary_fill_holes(m)
    rgba=src[y0:y1,x0:x1].copy(); rgba[...,3]=np.where(m,255,0)
    return Image.fromarray(rgba)
meta={}
for k,(r,s,n) in groups.items():
    fr=rows[r][s:s+n]
    meta[k]=[]
    for j,c in enumerate(fr):
        im=cutout(c); im.save(f'raw_{k}_{j}.png')
        meta[k].append(dict(x=c['x'],y=c['y'],w=c['w'],h=c['h'],bottom=c['y']+c['h']))
json.dump(meta,open('meta.json','w'),indent=0)
print({k:[m['h'] for m in v] for k,v in meta.items()})
