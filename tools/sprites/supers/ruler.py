import numpy as np, sys
from PIL import Image, ImageDraw
exec(open('cut.py').read().split("out={}")[0])
key=sys.argv[1]; idxs=[int(v) for v in sys.argv[2].split(',')] if len(sys.argv)>2 else None
spec=F[key]; img,a,fg,lab,comps,vline=analyse(key)
badges=[(c['x0'],c['y0'],c['x1'],c['y1']) for c in comps if c['lum']<70 and 30<=c['w']<=95 and 25<=c['h']<=65 and c['fill']>0.45]
tiles=[]
for j,box in enumerate(spec['frames']):
    if idxs and j not in idxs: continue
    rgba,(ox,oy),bb=cut(img,a,box,badges); x0,y0,x1,y1=bb; R=rgba[y0:y1,x0:x1]
    v=Image.fromarray(np.where(R[...,3:4]>0,R[...,:3],255).astype(np.uint8)).convert('RGB')
    pad=Image.new('RGB',(v.width+34,v.height+20),(255,255,255)); pad.paste(v,(34,10)); d=ImageDraw.Draw(pad)
    for y in range(0,v.height,10):
        d.line([(28,y+10),(pad.width,y+10)],fill=(255,0,0) if y%50==0 else (255,170,170),width=1)
        if y%20==0: d.text((0,y+5),str(y),fill=(200,0,0))
    d.text((40,0),f'#{j}',fill=(0,0,255)); tiles.append(pad)
W=sum(t.width+4 for t in tiles); H=max(t.height for t in tiles); sh=Image.new('RGB',(W,H),(180,180,180)); x=0
for t in tiles: sh.paste(t,(x,0)); x+=t.width+4
sh.save(f'ruler_{key}.png'); print(sh.size)
