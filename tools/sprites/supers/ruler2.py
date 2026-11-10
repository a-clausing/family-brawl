import numpy as np, sys
from PIL import Image, ImageDraw
exec(open('cut.py').read().split("out={}")[0])
key=sys.argv[1]; idxs=[int(v) for v in sys.argv[2].split(',')]; zoom=float(sys.argv[3]) if len(sys.argv)>3 else 1.5
spec=F[key]; img,a,fg,lab,comps,vline=analyse(key)
badges=[(c['x0'],c['y0'],c['x1'],c['y1']) for c in comps if c['lum']<70 and 30<=c['w']<=95 and 25<=c['h']<=65 and c['fill']>0.45]
tiles=[]
for j in idxs:
    box=spec['frames'][j]
    rgba,(ox,oy),bb=cut(img,a,box,badges); x0,y0,x1,y1=bb; R=rgba[y0:y1,x0:x1]
    v=Image.fromarray(np.where(R[...,3:4]>0,R[...,:3],255).astype(np.uint8)).convert('RGB')
    v=v.resize((int(v.width*zoom),int(v.height*zoom)),Image.LANCZOS)
    pad=Image.new('RGB',(v.width+40,v.height+16),(255,255,255)); pad.paste(v,(40,8)); d=ImageDraw.Draw(pad)
    for y in range(0,int(v.height/zoom)+1,5):
        Y=int(y*zoom)+8
        d.line([(34 if y%10 else 26,Y),(pad.width,Y)],fill=(220,0,0) if y%50==0 else ((255,140,140) if y%10==0 else (255,215,215)),width=1)
        if y%10==0: d.text((0,Y-6),str(y),fill=(180,0,0))
    d.text((44,0),f'#{j}',fill=(0,0,255)); tiles.append(pad)
W=sum(t.width+4 for t in tiles); H=max(t.height for t in tiles); sh=Image.new('RGB',(W,H),(180,180,180)); x=0
for t in tiles: sh.paste(t,(x,0)); x+=t.width+4
sh.save(f'r2_{key}.png'); print(sh.size)
