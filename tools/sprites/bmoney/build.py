import numpy as np, pickle, json, base64, io
from PIL import Image, ImageDraw
from scipy import ndimage as nd
R=pickle.load(open('raw.pkl','rb'))
TARGET=102   # standing height in sprite px (51 game px): a little shorter than AC/Volt, a little taller than Becky
REF={'idle':89,'walkf':86,'walkb':86,'crouch':86,'jump':86,'lpunch':79,'hpunch':78,'lkick':77,'hkick':78,'combo':75,
     'block':75,'dmg':77,'down':77,'getup':77,'special':91,'super':88}
def down(arr,scale):
    im=Image.fromarray(arr,'RGBA'); w,h=im.size; nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
    a_=arr.astype(np.float32)/255; pm=a_.copy(); pm[...,:3]*=pm[...,3:4]
    r=np.asarray(Image.fromarray((pm*255).astype(np.uint8),'RGBA').resize((nw,nh),Image.BOX if scale<1 else Image.LANCZOS)).astype(np.float32)/255
    al=np.clip(r[...,3:4],0,1); rgb=np.where(al>0,r[...,:3]/np.maximum(al,1e-4),0); keep=al>0.5
    return (np.concatenate([np.clip(rgb,0,1)*keep,keep],2)*255).astype(np.uint8)
def body_mask(img):
    al=img[...,3]>0; c=img[...,:3].astype(int)
    purple_fx=al&(c[...,2]>150)&(c[...,0]>120)&(c[...,1]<120)&(c[...,2]-c[...,1]>90)&((c[...,0]+c[...,2])>380)   # bright purple energy
    grey=al&((c.max(2)-c.min(2))<25)&(c.min(2)>90)                                                            # rock / dust
    shadow=al&((c.max(2)-c.min(2))<30)&(c.min(2)>25); shadow[:int(img.shape[0]*0.9)]=False   # flat floor shadow under the feet
    return al&~purple_fx&~grey&~shadow
def frame(row,j,sc=None,crop=True):
    raw=R[row][j]; s=(sc or TARGET/REF[row]); d=down(raw,s); m=body_mask(d)
    lb,n=nd.label(m); sz=nd.sum(m,lb,range(n+1)); sz[0]=0; body=lb==np.argmax(sz)
    ys,xs=np.where(body); feet=int(ys.max())+1; top=int(ys.min()); h=feet-top
    # drop stray debris far from the body (bits of a neighbouring frame's effect)
    al=d[...,3]>0; lab,k=nd.label(al); bx0,bx1=xs.min(),xs.max()
    for i,o in enumerate(nd.find_objects(lab)):
        if (lab[o]==i+1).sum()<400 and (o[1].start>bx1+30 or o[1].stop<bx0-30): d[lab==i+1]=0
    ys2,xs2=np.where(d[...,3]>0); d=d[:,:xs2.max()+1]
    if crop and row not in('down','getup'): d=d[:feet]   # nothing below the soles (floor shadows)
    band=body.copy(); band[:top+int(0.25*h)]=False; band[top+int(0.6*h):]=False
    ax=float(np.median(np.where(band)[1])) if band.any() else d.shape[1]/2
    return dict(img=d,ax=ax,ay=feet,h=h)
main={}
for row,name in [('idle','idle'),('walkf','walk'),('walkb','walkb'),('jump','jump'),('block','block'),('lpunch','lpunch'),
                 ('hpunch','hpunch'),('lkick','lkick'),('hkick','hkick'),('combo','combo'),('dmg','hit'),('down','down'),
                 ('getup','getup'),('crouch','crouch')]:
    main[name]=[frame(row,j) for j in range(len(R[row]))]
main['special']=[frame('special',j) for j in (0,1,2,4)]
# lying knockdown frames: anchor on the middle of the body
for j in (2,3,4): main['down'][j]['ax']=main['down'][j]['img'].shape[1]*0.55
main['getup'][0]['ax']=main['getup'][0]['img'].shape[1]*0.5
# super frames (by index): 0 stance, 1 crouch (power pose), 2 punch the floor, 3 stance, 4 step in, 5 ready, 6 leap, 7 uppercut, 8 uppercut peak, 9 land crouch, 10 stance
sup=[frame('special',0),frame('special',1),frame('super',1),frame('super',3),frame('super',4),frame('super',5),
     frame('super',6,crop=False),frame('super',7,crop=False),frame('crouch',1),frame('super',8)]
# uppercut frames: the purple arc is part of the drawing; anchor and feet on the body itself
fx={}
def fxsprite(arr,w_target):
    s=w_target/arr.shape[1]; return down(arr,s)
fx['ripple']=fxsprite(R['fx'][1],120)            # Ground Ripple projectile (~60 game px wide)
fx['burst']=fxsprite(R['fx'][0],90)              # small purple ground burst
fx['dust']=fxsprite(R['fx'][2],80)
fx['arc']=fxsprite(R['fx'][3],90)                # uppercut swoosh
fx['bigwave']=fxsprite(R['super'][2],190)        # Rising Quake wave (~95 game px wide)
pickle.dump((main,sup,fx),open('frames.pkl','wb'))
# lineup: in-game AC for scale reference, then every B-Money frame on one ground line
ac=pickle.load(open('../ac/frames.pkl','rb'))[0]['idle'][0]
seq=[('AC',ac)]+[(k+str(j),f) for k in ['idle','walk','walkb','crouch','jump','lpunch','hpunch','lkick','hkick','combo','block','hit','down','getup','special'] for j,f in enumerate(main[k])]+[('S'+str(j),f) for j,f in enumerate(sup)]
W=1900; rows=[]; cur=[]; x=0
for n,f in seq:
    w=f['img'].shape[1]+16
    if x+w>W: rows.append(cur); cur=[]; x=0
    cur.append((n,f)); x+=w
rows.append(cur)
sh=Image.new('RGBA',(W,len(rows)*140),(110,170,235,255)); d=ImageDraw.Draw(sh)
for r,row in enumerate(rows):
    x=8; base=r*140+130
    d.line([(0,base),(W,base)],fill=(255,0,0,255)); d.line([(0,base-102),(W,base-102)],fill=(255,255,255,120))
    for n,f in row:
        sh.alpha_composite(Image.fromarray(f['img'],'RGBA'),(int(x),int(base-f['ay']))); d.line([(x+f['ax'],base-4),(x+f['ax'],base+3)],fill=(255,0,0,255))
        d.text((x,r*140+2),n,fill=(0,0,0,255)); x+=f['img'].shape[1]+16
sh.save('lineup.png'); print(sh.size, 'super heights',[f['h'] for f in sup])
