import pickle,sys
from PIL import Image, ImageDraw
R=pickle.load(open(sys.argv[1],'rb')); W=1500
rows=[(k,v) for k,v in R.items()]
H=sum(max(f.shape[0] for f in v)+18 for k,v in rows)
sh=Image.new('RGBA',(W,H),(90,160,90,255)); d=ImageDraw.Draw(sh); y=0
for k,v in rows:
    x=4; h=max(f.shape[0] for f in v); d.text((x,y),k,fill=(0,0,0,255))
    for j,f in enumerate(v):
        sh.alpha_composite(Image.fromarray(f,'RGBA'),(x,y+14)); d.text((x,y+14),str(j),fill=(255,0,0,255)); x+=f.shape[1]+8
    y+=h+18
sh.save(sys.argv[2]); print(sh.size)
