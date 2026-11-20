# Survey Goblin's sheet: group blobs into rows and frames (prints x ranges for config.py).
import numpy as np
from PIL import Image
from scipy import ndimage as nd
A=np.asarray(Image.open('../../../art/originals/goblin-sheet.png').convert('RGB')).astype(int)
r,g,b=A[...,0],A[...,1],A[...,2]
fg=~((b>150)&(r<90)&(g<110)&(b>r+100)); fg=nd.binary_opening(fg,iterations=1)
lab,n=nd.label(fg); objs=nd.find_objects(lab); sizes=nd.sum(fg,lab,range(1,n+1))
GAP=int(__import__("sys").argv[1]) if len(__import__("sys").argv)>1 else 10
ROWS=[(12,106,'r1'),(112,225,'r2'),(233,316,'r3'),(324,408,'r4'),(408,500,'r5'),(505,591,'r6'),(591,724,'r7')]
def row_of(sl):
    cy=(sl[0].start+sl[0].stop)/2
    for y0,y1,nm in ROWS:
        if y0<=cy<y1: return nm
out={}
for i,sl in enumerate(objs):
    if sizes[i]<40: continue
    out.setdefault(row_of(sl),[]).append((sl[1].start,sl[1].stop,sl[0].start,sl[0].stop,int(sizes[i])))
for nm in [x[2] for x in ROWS]:
    c=sorted(out.get(nm,[]))
    fr=[]
    for x0,x1,y0,y1,s in c:
        if fr and x0-fr[-1][1]<GAP: fr[-1]=[fr[-1][0],max(fr[-1][1],x1),min(fr[-1][2],y0),max(fr[-1][3],y1)]
        else: fr.append([x0,x1,y0,y1])
    print(nm,len(fr),[(a,b_,c_,d) for a,b_,c_,d in fr])
