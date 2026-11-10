import numpy as np, sys
from PIL import Image, ImageDraw
exec(open('cut.py').read().split("out={}")[0])
# usage: shoecrop.py key "j,j,j" [rows] -> bottom band of each frame, 3x, with a horizontal ruler every 2px
key=sys.argv[1]; idx=[int(v) for v in sys.argv[2].split(',')]; rows=int(sys.argv[3]) if len(sys.argv)>3 else 60
spec=F[key]; img,a,fg,lab,comps,vline=analyse(key)
badges=[(c['x0'],c['y0'],c['x1'],c['y1']) for c in comps if c['lum']<70 and 30<=c['w']<=95 and 25<=c['h']<=65 and c['fill']>0.45]
Z=3; tiles=[]
for j in idx:
    rgba,(ox,oy),bb=cut(img,a,spec['frames'][j],badges); X0,Y0,X1,Y1=bb; R=rgba[Y0:Y1,X0:X1]
    v=np.where(R[...,3:4]>0,R[...,:3],255).astype(np.uint8)[-rows:]
    im=Image.fromarray(v).resize((v.shape[1]*Z,v.shape[0]*Z),Image.NEAREST)
    pad=Image.new('RGB',(im.width,im.height+22),(255,255,255)); pad.paste(im,(0,22)); d=ImageDraw.Draw(pad)
    for x in range(0,v.shape[1]+1,2):
        X=x*Z; d.line([(X,22 if x%10 else 12),(X,pad.height)],fill=(220,0,0) if x%10==0 else (255,200,200))
        if x%20==0: d.text((X+1,0),str(x),fill=(160,0,0))
    d.text((4,12),f'#{j}',fill=(0,0,255)); tiles.append(pad)
H=sum(t.height+6 for t in tiles); W=max(t.width for t in tiles); sh=Image.new('RGB',(W,H),(170,170,170)); y=0
for t in tiles: sh.paste(t,(0,y)); y+=t.height+6
sh.save(f'sc_{key}.png'); print(sh.size)
