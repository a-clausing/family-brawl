# Cut Alex's v2 Becky sheet (art/originals/becky-sheet-v2.png) into frames and props.
# Writes raw.pkl: {row: [ {img, x, y} ...] } in sheet order, and cut_debug.png to check the boxes.
import numpy as np, pickle
from PIL import Image, ImageDraw
from scipy import ndimage as nd
from seg import img, rgb, al, mask
# row: (x0,y0,x1,y1)  sprite areas between the labels
ROWS={'idle':(380,45,900,170),'walk':(970,45,1530,170),'run':(390,195,960,310),'jump':(1025,195,1530,312),
 'lp':(405,372,740,472),'hp':(785,372,1130,472),'rk':(1185,372,1530,472),
 'hit':(405,508,740,604),'kd':(768,508,1188,604),'getup':(1192,508,1530,604),
 'sp':(398,638,1530,752),'su':(40,775,1530,915),'fx':(185,915,1530,1020)}
def comps(name,minh=28,mina=900):
    x0,y0,x1,y1=ROWS[name]; m=mask(x0,y0,x1,y1)
    lab,k=nd.label(m); out=[]
    for i,sl in enumerate(nd.find_objects(lab)):
        h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start; a=int((lab[sl]==i+1).sum())
        out.append(dict(x=sl[1].start+x0,y=sl[0].start+y0,w=w,h=h,a=a,id=i+1,sl=sl))
    return out,lab,(x0,y0)
if __name__=='__main__':
    dbg=Image.new('RGBA',(1536,1024),(110,170,235,255)); dbg.alpha_composite(Image.open('../../../art/originals/becky-sheet-v2.png'))
    d=ImageDraw.Draw(dbg)
    for name,(x0,y0,x1,y1) in ROWS.items():
        d.rectangle([x0,y0,x1,y1],outline=(255,0,255,255))
        cs,_,_=comps(name); cs=[c for c in cs if c['a']>60]; cs.sort(key=lambda c:c['x'])
        print(name,[(c['x'],c['y'],c['w'],c['h'],c['a']) for c in cs])
        for c in cs: d.rectangle([c['x'],c['y'],c['x']+c['w'],c['y']+c['h']],outline=(255,0,0,255) if c['a']>900 else (255,255,0,255))
    dbg.save('cut_debug.png')
