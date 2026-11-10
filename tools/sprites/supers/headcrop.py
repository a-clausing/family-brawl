import numpy as np, sys, json
from PIL import Image, ImageDraw
exec(open('cut.py').read().split("out={}")[0])
# usage: headcrop.py key "j:y0:y1:x0:x1;j:y0:y1:x0:x1;..."   (source px, frame-local; x range optional)
key=sys.argv[1]; specs=[s.split(':') for s in sys.argv[2].split(';')]
spec=F[key]; img,a,fg,lab,comps,vline=analyse(key)
badges=[(c['x0'],c['y0'],c['x1'],c['y1']) for c in comps if c['lum']<70 and 30<=c['w']<=95 and 25<=c['h']<=65 and c['fill']>0.45]
Z=4; tiles=[]
for sp in specs:
    j,y0,y1=int(sp[0]),int(sp[1]),int(sp[2])
    rgba,(ox,oy),bb=cut(img,a,spec['frames'][j],badges); X0,Y0,X1,Y1=bb; R=rgba[Y0:Y1,X0:X1]
    v=np.where(R[...,3:4]>0,R[...,:3],255).astype(np.uint8)[y0:y1]
    if len(sp)>3: v=v[:,int(sp[3]):int(sp[4])]
    else:   # centre on the head: skin/hair (non-grey, non-white) pixels in this band
        c=v.astype(int); sat=c.max(2)-c.min(2); m=(sat>45)&(c.min(2)<235)&(c[...,0]>c[...,2]+20)
        xs=np.where(m.sum(0)>=2)[0]
        if len(xs): cx=int(np.median(xs)); v=v[:,max(0,cx-45):cx+45]
    im=Image.fromarray(v).resize((v.shape[1]*Z,v.shape[0]*Z),Image.NEAREST)
    pad=Image.new('RGB',(im.width+46,im.height),(255,255,255)); pad.paste(im,(46,0)); d=ImageDraw.Draw(pad)
    for y in range(0,v.shape[0]+1,2):
        Y=y*Z; col=(220,0,0) if (y0+y)%10==0 else (255,190,190)
        d.line([(30 if (y0+y)%10 else 22,Y),(pad.width,Y)],fill=col,width=1)
        if (y0+y)%10==0: d.text((0,Y-5),str(y0+y),fill=(160,0,0))
    d.text((48,2),f'#{j}',fill=(0,0,255)); tiles.append(pad)
W=sum(t.width+6 for t in tiles); H=max(t.height for t in tiles); sh=Image.new('RGB',(W,H),(170,170,170)); x=0
for t in tiles: sh.paste(t,(x,0)); x+=t.width+6
sh.save(f'hc_{key}.png'); print(sh.size)
