import numpy as np, sys, json
from PIL import Image, ImageDraw
from scipy import ndimage as nd
exec(open('cut.py').read().split("out={}")[0])
def frames_raw(key):
    spec=F[key]; img,a,fg,lab,comps,vline=analyse(key)
    badges=[(c['x0'],c['y0'],c['x1'],c['y1']) for c in comps if c['lum']<70 and 30<=c['w']<=95 and 25<=c['h']<=65 and c['fill']>0.45]
    out=[]
    for box in spec['frames']:
        rgba,(ox,oy),bb=cut(img,a,box,badges); X0,Y0,X1,Y1=bb; out.append(rgba[Y0:Y1,X0:X1])
    return out
def solid(R):
    al=R[...,3]>0; c=R[...,:3].astype(int); sat=c.max(2)-c.min(2)
    shadow=al&(sat<22)&(c.min(2)>95)&(c.max(2)<215)   # flat grey floor shadow
    return al&~shadow
def crown(R,x0,x1,yg):   # topmost solid pixel in the head column, searching around a rough guess
    m=solid(R); ys=range(max(0,yg-14),min(R.shape[0],yg+14))
    for y in ys:
        if m[y,x0:x1].sum()>=2: return y
    return None
def sole(R,x0,x1,yg):
    m=solid(R)
    for y in range(min(R.shape[0]-1,yg+14),max(0,yg-14),-1):
        if m[y,x0:x1].sum()>=3: return y+1
    return None
def show(key,R_list,marks,name):
    tiles=[]
    for j,(R,mk) in enumerate(zip(R_list,marks)):
        for (y,x0,x1,lbl) in mk:
            if y is None: continue
            y0=max(0,y-16); y1=min(R.shape[0],y+10)
            v=np.where(R[y0:y1,x0:x1,3:4]>0,R[y0:y1,x0:x1,:3],255).astype(np.uint8)
            im=Image.fromarray(v).resize((v.shape[1]*4,v.shape[0]*4),Image.NEAREST); d=ImageDraw.Draw(im)
            yy=(y-y0)*4; d.line([(0,yy),(im.width,yy)],fill=(255,0,0),width=1)
            pad=Image.new('RGB',(im.width,im.height+12),(255,255,255)); pad.paste(im,(0,12)); ImageDraw.Draw(pad).text((2,0),f'#{j} {lbl} y={y}',fill=(0,0,200))
            tiles.append(pad)
    cols=4; rows=(len(tiles)+cols-1)//cols; tw=max(t.width for t in tiles); th=max(t.height for t in tiles)
    sh=Image.new('RGB',(cols*(tw+6),rows*(th+6)),(170,170,170))
    for i,t in enumerate(tiles): sh.paste(t,((i%cols)*(tw+6),(i//cols)*(th+6)))
    sh.save(name)
if __name__=='__main__':
    key=sys.argv[1]; G=json.loads(sys.argv[2])   # [[crownX0,crownX1,crownY, soleX0,soleX1,soleY],...]
    R=frames_raw(key); res=[]; marks=[]
    for j,g in enumerate(G):
        c=crown(R[j],g[0],g[1],g[2]); s=sole(R[j],g[3],g[4],g[5]); res.append((c,s,(s-c) if c is not None and s is not None else None))
        marks.append([(c,g[0],g[1],'crown'),(s-1 if s else None,g[3],g[4],'sole')])
    print(key,res); show(key,R,marks,f'lm_{key}.png')
    json.dump(res,open(f'lm_{key}.json','w'))
