import numpy as np, io, base64, colorsys, json
from PIL import Image, ImageDraw, ImageFilter
im=Image.open('sheet.png').convert('RGB')
panel=im.crop((11,11,387,314))                        # portrait panel, inside its border
lab=im.crop((24,1029,137,1122))                       # "SUPER: TAIL LASH RUSH" lettering from the sheet
la=np.asarray(lab).astype(int); la[la.max(2)<60]=(6,8,12); lab=Image.fromarray(la.astype(np.uint8))
W,H=576,768                                           # build at 2x, downsample to 288x384
card=Image.new('RGB',(W,H),(6,8,12)); d=ImageDraw.Draw(card)
p=panel.resize((W-24,round((W-24)*panel.height/panel.width)),Image.LANCZOS); card.paste(p,(12,12))
y0=12+p.height
# blue brush streaks behind the lettering, echoing the sheet's background
rng=np.random.default_rng(3)
for i in range(16):
    x=rng.uniform(-60,W); y=rng.uniform(y0+10,H-30); L=rng.uniform(80,260); t=rng.uniform(5,16)
    d.polygon([(x,y),(x+L,y-L*0.45),(x+L+t,y-L*0.45+t*0.6),(x+t,y+t*0.6)],fill=(22,120,235) if i%3 else (90,190,255))
card=card.filter(ImageFilter.GaussianBlur(0.6)); d=ImageDraw.Draw(card)
# black slab for the lettering
lh=H-12-y0-46; lw=round(lh*lab.width/lab.height); l2=lab.resize((lw,lh),Image.LANCZOS)
ly=y0+(H-12-y0-l2.height)//2+4; lx=(W-lw)//2
d.polygon([(lx-30,ly-14),(lx+lw+40,ly-14),(lx+lw+10,ly+l2.height+14),(lx-50,ly+l2.height+14)],fill=(6,8,12))
card.paste(l2,(lx,ly))
# rounded electric-blue frame like the other cards
mask=Image.new('L',(W,H),0); ImageDraw.Draw(mask).rounded_rectangle([0,0,W-1,H-1],radius=26,fill=255)
fr=Image.new('RGB',(W,H),(6,8,12)); fr.paste(card,(0,0),mask); card=fr; d=ImageDraw.Draw(card)
d.rounded_rectangle([3,3,W-4,H-4],radius=24,outline=(30,140,255),width=7)
card=card.resize((288,384),Image.LANCZOS).filter(ImageFilter.UnsharpMask(1,50,2))
face=im.crop((40,30,215,205)).resize((256,256),Image.LANCZOS)
def alt(img,shift=178):   # mirror-match colors: blue -> orange
    a=np.asarray(img).astype(np.float32)/255; out=a.copy()
    d_=a.max(2)-a.min(2); ys,xs=np.where(d_>0.12)
    for y,x in zip(ys,xs):
        h,l,s=colorsys.rgb_to_hls(*a[y,x])
        if 185<=h*360<=235 and s>0.3: out[y,x]=colorsys.hls_to_rgb(((h*360+shift)%360)/360,l,s)
    return Image.fromarray((out*255).astype(np.uint8))
ca=alt(card); fa=alt(face)
Image.fromarray(np.hstack([np.asarray(card),np.asarray(ca)])).save('cards_prev.png')
def enc(i,q=86): b=io.BytesIO(); i.save(b,'JPEG',quality=q,optimize=True); return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
json.dump({'card':enc(card),'card_alt':enc(ca),'face':enc(face,88),'face_alt':enc(fa,88)},open('cards.json','w'))
face.save('face.png')
