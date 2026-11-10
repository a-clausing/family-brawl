import numpy as np, sys
from PIL import Image, ImageDraw
exec(open('cut.py').read().split("out={}")[0])
key=sys.argv[1]; idx=[int(v) for v in sys.argv[2].split(',')]; Z=float(sys.argv[3]) if len(sys.argv)>3 else 1.3
spec=F[key]; img,a,fg,lab,comps,vline=analyse(key)
badges=[(c['x0'],c['y0'],c['x1'],c['y1']) for c in comps if c['lum']<70 and 30<=c['w']<=95 and 25<=c['h']<=65 and c['fill']>0.45]
tiles=[]
for j in idx:
    rgba,(ox,oy),bb=cut(img,a,spec['frames'][j],badges); X0,Y0,X1,Y1=bb; R=rgba[Y0:Y1,X0:X1]
    v=Image.fromarray(np.where(R[...,3:4]>0,R[...,:3],255).astype(np.uint8)).convert('RGB')
    v=v.resize((int(v.width*Z),int(v.height*Z)),Image.LANCZOS)
    pad=Image.new('RGB',(v.width+30,v.height+24),(255,255,255)); pad.paste(v,(30,24)); d=ImageDraw.Draw(pad,'RGBA')
    for y in range(0,R.shape[0]+1,10):
        Y=int(y*Z)+24; d.line([(26,Y),(pad.width,Y)],fill=(255,0,0,150 if y%50==0 else 55))
        if y%20==0: d.text((0,Y-5),str(y),fill=(170,0,0))
    for x in range(0,R.shape[1]+1,10):
        X=int(x*Z)+30; d.line([(X,18),(X,pad.height)],fill=(0,0,255,150 if x%50==0 else 55))
        if x%20==0: d.text((X-6,4),str(x),fill=(0,0,170))
    d.text((34,10),f'#{j}',fill=(0,120,0)); tiles.append(pad)
W=sum(t.width+6 for t in tiles); H=max(t.height for t in tiles); sh=Image.new('RGB',(W,H),(170,170,170)); x=0
for t in tiles: sh.paste(t,(x,0)); x+=t.width+6
sh.save(f'g_{key}.png'); print(sh.size)
