import numpy as np, json
from PIL import Image
from scipy import ndimage as nd
src=np.asarray(Image.open('../../../art/originals/brick-sheet.png').convert('RGBA')).copy()
lab=np.load('lab.npy')
comps=[]
for i,sl in enumerate(nd.find_objects(lab)):
    if sl is None: continue
    h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start; area=(lab[sl]==i+1).sum()
    dens=area/(h*w)
    if area>800 and h>40 and ((dens<0.9 and w<250) or (w>500 and h<110 and sl[0].start>850)):
        comps.append(dict(y=sl[0].start,x=sl[1].start,h=h,w=w,id=i+1,cx=sl[1].start+w/2,by=sl[0].stop))
# rows by bottom y
bands=[(0,170),(170,320),(320,465),(465,605),(605,760),(760,1024)]
rows=[[c for c in comps if lo<=c['by']<hi] for lo,hi in bands]
for r in rows: r.sort(key=lambda c:c['x'])
for i,r in enumerate(rows): print(i,len(r),[(c['x'],c['w'],c['h']) for c in r])
json.dump(rows,open('rows.json','w'))
