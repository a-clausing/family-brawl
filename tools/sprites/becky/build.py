import numpy as np, json, pickle
from PIL import Image, ImageDraw
from scipy import ndimage as nd
exec(open('panels.py').read().split("if __name__")[0])
TARGET=100
REF={'idle':122,'walkf':111,'walkb':104,'jump':117,'block':95,'lpunch':97,'hpunch':96,'lkick':96,'hkick':96,'dmg':91,'down':91,'getup':96,'special':146}
use=list(REF)
def cut(name):
    comps,l2,(ox,oy)=seg(name); out=[]
    for c in comps:
        sl=(slice(c['y']-oy,c['y']-oy+c['h']),slice(c['x']-ox,c['x']-ox+c['w']))
        m=l2[sl]==c['id']
        rgba=img[c['y']:c['y']+c['h'],c['x']:c['x']+c['w']].copy()
        col=rgba[...,:3].astype(int)
        wh=(col.min(2)>215)&m              # white background trapped inside (gaps between limbs)
        wl,wn=nd.label(wh); ws=nd.sum(wh,wl,range(wn+1))
        m=m&~(np.isin(wl,np.where(ws>=10)[0])&(wl>0))
        holes=nd.binary_fill_holes(m)&~m; hl,hn=nd.label(holes); hs=nd.sum(holes,hl,range(hn+1))
        m=m|(np.isin(hl,np.where(hs<6)[0])&(hl>0))
        rgba[...,3]=np.where(m,255,0); out.append(rgba)
    return out
def down(arr,scale):
    im=Image.fromarray(arr,'RGBA'); w,h=im.size; nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
    a_=arr.astype(np.float32)/255; pm=a_.copy(); pm[...,:3]*=pm[...,3:4]
    r=np.asarray(Image.fromarray((pm*255).astype(np.uint8),'RGBA').resize((nw,nh),Image.BOX if scale<1 else Image.LANCZOS)).astype(np.float32)/255
    al=np.clip(r[...,3:4],0,1); rgb=np.where(al>0,r[...,:3]/np.maximum(al,1e-4),0); keep=al>0.5
    return (np.concatenate([np.clip(rgb,0,1)*keep,keep],2)*255).astype(np.uint8)
frames={}
for k in use:
    frames[k]=[]
    for arr in cut(k):
        a2=down(arr,TARGET/REF[k]); al=a2[...,3]>0
        lum=a2[...,:3].mean(2); dark=al&(lum<80)
        feet=int(np.where(dark.any(1))[0].max())+1
        top=int(np.where(al.any(1))[0].min())
        # anchor on the torso band (hair flows behind her, so the top band isn't reliable)
        band=al.copy(); band[:top+int(0.30*TARGET)]=False; band[top+int(0.55*TARGET):]=False
        frames[k].append(dict(img=a2,feet=feet,hx=float(np.median(np.where(band)[1])),w=a2.shape[1],h=a2.shape[0]))
    print(k,len(frames[k]),[f['h'] for f in frames[k]])
i0=frames['idle'][0]; off=i0['hx']-i0['w']/2
for k in use:
    for f in frames[k]: f['ax']=f['hx']-off; f['ay']=f['feet']
for j in (2,3,4): frames['down'][j]['ax']=frames['down'][j]['w']*0.55
if 'getup' in frames and frames['getup'] and frames['getup'][0]['h']<frames['getup'][-1]['h']*0.75: frames['getup'][0]['ax']=frames['getup'][0]['w']*0.5   # lying start of the get-up
# whip frame: cut the band off at her fist (the game draws the stretching band itself)
f3=frames['special'][3]; im3=f3['img'].copy(); rgb=im3[...,:3].astype(int); al=im3[...,3]>0
skin=al&(rgb[...,0]>150)&(rgb[...,1]>70)&(rgb[...,1]<170)&(rgb[...,2]<120)&(rgb[...,0]>rgb[...,1]+30)
skin[int(im3.shape[0]*0.6):]=False   # upper body only (shoe soles are orange too)
fx=int(np.where(skin.any(0))[0].max())          # front edge of her fist
rows=np.where(skin[:,fx-5:fx+1].any(1))[0]; hand_y=float(rows.mean())
im3[:,fx+3:,3]=0; im3[...,:3]*=(im3[...,3:4]>0)
# anchor this pose on her body (torso band), now that the band is gone
alb=im3[...,3]>0; top=int(np.where(alb.any(1))[0].min())
band=alb.copy(); band[:top+30]=False; band[top+55:]=False; band[:,fx-12:]=False
ax3=float(np.median(np.where(band)[1]))-off
for fr in (f3,):
    fr['ax']=ax3
frames['special'].append(dict(img=im3,ax=ax3,ay=f3['ay'],w=im3.shape[1],h=im3.shape[0]))
hand=[(fx+2-ax3)/2,(f3['ay']-hand_y)/2]
print('band hand (game px ahead, above feet):',hand)
# knockdown frame 1 (falling): anchor on the hips rather than the torso band
d1=frames['down'][1]; d1['ax']=d1['w']*0.45
pickle.dump((frames,hand),open('frames.pkl','wb'))
sheet=Image.new('RGBA',(1300,len(use)*120),(110,170,235,255)); d=ImageDraw.Draw(sheet)
for r,k in enumerate(use):
    x=70
    for f in frames[k]:
        base=r*120+114; sheet.alpha_composite(Image.fromarray(f['img'],'RGBA'),(int(x-f['ax']),int(base-f['ay'])))
        d.line([(x,r*120+5),(x,base)],fill=(255,0,0,255)); d.line([(x-30,base),(x+30,base)],fill=(255,0,0,255))
        x+=165
    d.text((2,r*120+60),k,fill=(0,0,0,255))
sheet.save('lineup.png')
