import numpy as np, json, pickle
from PIL import Image, ImageDraw
from scipy import ndimage as nd
exec(open('seg.py').read().split("if __name__")[0])
S=lambda v:int(round(v*SC))
# frame crop boxes (display coords x0,y0,x1,y1) and eyeballed torso x for the anchor
F={
 'ac':{'frames':[(10,110,285,405,95),(290,110,510,405,385),(514,110,722,405,620),(726,88,1013,405,880),(1020,110,1260,405,1130),
                 (1267,110,1561,405,1335),(1568,110,1786,405,1660),(1792,110,1988,405,1880)],
       'fx':{'bar_fly':(95,470,665,625),'bar_spin':(855,440,1185,650),'blast':(1350,435,1885,645)},'stance':7},
 'volt':{'frames':[(10,90,400,268,200),(407,90,788,268,600),(795,90,1203,268,1040),(1210,90,1603,268,1360),(1610,90,1990,268,1790),
                   (10,282,526,470,235),(534,282,1016,470,770),(1024,282,1501,470,1250),(1509,282,1990,470,1730)],
         'fx':{'bolt':(395,486,765,655),'star':(1140,488,1700,652)},'stance':8},
 'brick':{'frames':[(15,100,352,416,88),(372,100,604,416,480),(628,78,869,416,750),(888,100,1126,416,1010),(1146,100,1443,416,1232),
                    (1458,100,1748,416,1610),(1775,100,1988,416,1890)],
          'fx':{'rack_fall':(110,438,470,655),'erupt':(555,455,1395,652),'erupt_small':(1530,478,1850,652)},'stance':6},
 'becky':{'frames':[(12,84,408,296,205),(415,84,803,296,600),(810,84,1230,296,960),(1237,84,1641,296,1390),(1648,84,1988,296,1790),
                    (12,310,414,503,220),(421,310,793,503,610),(800,310,1201,503,990),(1208,310,1613,503,1380),(1620,310,1988,503,1800)],
          'fx':{'loop_fly':(310,535,930,645),'loop_snare':(1215,530,1700,645)},'stance':9}}
# Per-frame size correction. The AI-drawn sheets draw the fighter at slightly different sizes from pose to pose,
# so each frame is scaled by (stance body length / this frame's body length), measured as crown->waist plus
# waist->sole along the leg (pose-independent), cross-checked against head size.
FK={'ac':[1.0,1.03,1.06,1.10,1.15,1.06,1.12,1.0],'brick':[1.06,1.06,1.03,1.07,1.04,1.0,1.0],
    'becky':[1.0]*10,'volt':[1.0]*9}
# measured sole of the feet (source px, frame-local) where equipment or debris sits lower than the shoes
SOLE={'ac':[232,182,227,320,298,245,301,300],'brick':[228,230,343,318,195,None,212]}
FXK={'ac':1.06,'brick':1.10,'becky':1.0,'volt':1.0}   # effects match the frames they appear with
MASKS={}
TARGET={'ac':106,'brick':119,'becky':100,'volt':106}   # standing height in 2x sprite pixels, same as their main sheets
def cut(img,a,box,badges):
    x0,y0,x1,y1=[S(v) for v in box[:4]]
    sub=a[y0:y1,x0:x1]; fg=sub.min(2)<228
    hr=runs(fg); vr=runs(fg.T).T
    fg&=~nd.binary_dilation(((hr>=100)&(vr<=8))|((vr>=90)&(hr<=8)),iterations=1)   # panel border remnants
    for bx0,by0,bx1,by1 in badges:   # number badges
        fg[max(0,by0-y0-3):max(0,by1-y0+3),max(0,bx0-x0-3):max(0,bx1-x0+3)]=False
    lab,n=nd.label(fg); keep=np.zeros_like(fg)
    for i,sl in enumerate(nd.find_objects(lab)):
        m=lab[sl]==i+1; area=m.sum()
        if area<30: continue
        h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start; px=sub[sl][m]
        sat=(px.max(1)-px.min(1)).mean(); fill=area/(w*h)
        if area<1300 and 10<=w<=42 and 18<=h<=58 and 0.3<=fill<=0.75 and sat>60 and w<h: continue   # arrow
        keep[sl]|=m
    # drop border remnants touching the crop edge and stray specks far from the drawing
    lab2,n2=nd.label(keep); H_,W_=keep.shape
    objs=nd.find_objects(lab2); sizes=[(lab2[o]==i+1).sum() for i,o in enumerate(objs)]
    big=objs[int(np.argmax(sizes))] if objs else None
    for i,sl in enumerate(objs):
        h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start; area=sizes[i]
        edge=sl[0].start<=2 or sl[1].start<=2 or sl[0].stop>=H_-2 or sl[1].stop>=W_-2
        far=big is not None and (sl[1].stop<big[1].start-40 or sl[1].start>big[1].stop+40 or sl[0].stop<big[0].start-40 or sl[0].start>big[0].stop+40)
        if (edge and (w<=12 or h<=12)) or (area<80 and far) or (edge and area<400 and far):
            keep[lab2==i+1]=False
    for mx0,my0,mx1,my1 in MASKS.get(box,[]):   # hand masks (labels)
        keep[max(0,S(my0)-y0):max(0,S(my1)-y0),max(0,S(mx0)-x0):max(0,S(mx1)-x0)]=False
    # white background trapped between limbs becomes transparent
    wh=(sub.min(2)>=228)&nd.binary_fill_holes(keep)
    wl,wn=nd.label(wh); ws=nd.sum(wh,wl,range(wn+1))
    keep|=nd.binary_fill_holes(keep)&~(np.isin(wl,np.where(ws>=12)[0])&(wl>0))
    rgba=img[y0:y1,x0:x1].copy(); rgba[...,3]=np.where(keep,255,0); rgba[...,:3]*=keep[...,None]
    ys,xs=np.where(keep)
    return rgba,(x0,y0),(xs.min(),ys.min(),xs.max()+1,ys.max()+1)
def down(arr,scale):
    im=Image.fromarray(arr,'RGBA'); w,h=im.size; nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
    a_=arr.astype(np.float32)/255; pm=a_.copy(); pm[...,:3]*=pm[...,3:4]
    r=np.asarray(Image.fromarray((pm*255).astype(np.uint8),'RGBA').resize((nw,nh),Image.BOX)).astype(np.float32)/255
    al=np.clip(r[...,3:4],0,1); rgb=np.where(al>0,r[...,:3]/np.maximum(al,1e-4),0); keep=al>0.45
    return (np.concatenate([np.clip(rgb,0,1)*keep,keep],2)*255).astype(np.uint8)
MASKS[(110,438,470,655,0)]=[(100,430,300,484)]
MASKS[(95,470,665,625,0)]=[(90,460,300,490)]
for b,m in [((10,110,285,405,95),[(250,225,285,280)]),((290,110,510,405,385),[(472,225,510,280)]),((1020,110,1260,405,1130),[(1020,225,1056,280),(1228,225,1260,280)]),
            ((1267,110,1561,405,1335),[(1525,225,1561,280),(1500,280,1561,405)]),((1568,110,1786,405,1660),[(1755,225,1786,280)])]: MASKS[b]=m
out={}
for key,spec in F.items():
    img,a,fg,lab,comps,vline=analyse(key)
    badges=[(c['x0'],c['y0'],c['x1'],c['y1']) for c in comps if c['lum']<70 and 30<=c['w']<=95 and 25<=c['h']<=65 and c['fill']>0.45]
    raw=[cut(img,a,b,badges) for b in spec['frames']]
    st=raw[spec['stance']]
    _al=st[0][...,3]>0; _lb,_n=nd.label(_al); _sz=nd.sum(_al,_lb,range(_n+1)); _sz[0]=0
    _ys=np.where((_lb==np.argmax(_sz)).any(1))[0]; sth=_ys.max()-_ys.min()+1   # the fighter's body only
    sc=TARGET[key]/sth
    frames=[]
    for j,((rgba,(ox,oy),bb),box) in enumerate(zip(raw,spec['frames'])):
        x0,y0,x1,y1=bb; crop=rgba[y0:y1,x0:x1]; fsc=sc*FK[key][j]
        d=down(crop,fsc); trim=0
        # drop tiny specks (arrow remnants) sitting beyond the right edge of the drawing
        al=d[...,3]>0; lb,nn=nd.label(al); objs=nd.find_objects(lb)
        if nn>1:
            sizes=[(lb[o]==i+1).sum() for i,o in enumerate(objs)]; mo=objs[int(np.argmax(sizes))]
            for i,o in enumerate(objs):
                h_=o[0].stop-o[0].start; w_=o[1].stop-o[1].start
                if (sizes[i]<70 and o[1].start>mo[1].stop+3) or (sizes[i]<90 and (h_<=3 or w_<=3)) or (sizes[i]<60 and o[0].stop<mo[0].start-2): d[lb==i+1]=0
            ys,xs=np.where(d[...,3]>0); y0_=ys.min(); d=d[y0_:ys.max()+1,:xs.max()+1]; trim=y0_
        ax=(S(box[4])-ox-x0)*fsc
        _al=d[...,3]>0; _lb,_n=nd.label(_al); _sz=nd.sum(_al,_lb,range(_n+1)); _sz[0]=0
        ay=int(np.where((_lb==np.argmax(_sz)).any(1))[0].max())+1   # feet = bottom of the body, not of stray bits
        so=SOLE.get(key,[None]*99)[j]
        if so is not None: ay=int(round(so*fsc))-trim
        frames.append(dict(img=d,ax=ax,ay=ay,sc=fsc))
    fx={}
    for name,box in spec['fx'].items():
        rgba,(ox,oy),bb=cut(img,a,box+(0,),badges); x0,y0,x1,y1=bb
        fx[name]=down(rgba[y0:y1,x0:x1],sc*FXK[key])
    out[key]=dict(frames=frames,fx=fx,scale=sc)
    print(key,'scale %.3f'%sc,[f['img'].shape[:2] for f in frames],{k:v.shape[:2] for k,v in fx.items()})
pickle.dump(out,open('super.pkl','wb'))
# lineup with anchors
sheet=Image.new('RGBA',(10*290+40,4*200),(110,170,235,255)); d=ImageDraw.Draw(sheet)
for r,(key,o) in enumerate(out.items()):
    x=150
    for f in o['frames']:
        base=r*200+180; sheet.alpha_composite(Image.fromarray(f['img'],'RGBA'),(int(x-f['ax']),int(base-f['ay'])))
        d.line([(x,r*200+20),(x,base)],fill=(255,0,0,255)); d.line([(x-40,base),(x+40,base)],fill=(255,0,0,255)); x+=290
sheet.save('lineup.png')
fxs=Image.new('RGBA',(1800,260),(110,170,235,255)); x=10; y=0
for key,o in out.items():
    for name,v in o['fx'].items():
        if x+v.shape[1]>1800: x=10; y+=130
        fxs.alpha_composite(Image.fromarray(v,'RGBA'),(x,y+5)); x+=v.shape[1]+10
fxs.save('fx.png')
