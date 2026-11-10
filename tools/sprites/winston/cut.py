import numpy as np, pickle
from PIL import Image
from scipy import ndimage as nd
exec(open('panels.py').read().split("if __name__")[0])
P['special']=(180,899,1188,1006,7); P['super']=(150,1030,1188,1180,12); P['fx']=(135,1205,1188,1298,6)
def longrun(M,frac):
    out=np.zeros(M.shape[0],bool)
    for i,r in enumerate(M):
        d=np.diff(np.concatenate([[0],r.astype(np.int8),[0]])); st=np.where(d==1)[0]; en=np.where(d==-1)[0]
        out[i]=len(st)>0 and (en-st).max()>frac*M.shape[1]
    return out
def fgmask(name):
    x0,y0,x1,y1,n=P[name]; c=a[y0:y1,x0:x1]; white=c.min(2)>228
    ci=c.astype(int); shadow=((ci.max(2)-ci.min(2))<28)&(ci.min(2)>120); shadow[:int(c.shape[0]*0.72)]=False
    white=white|shadow   # the grey floor shadow joins the background, so gaps between the legs open up
    lab,k=nd.label(white); sz=nd.sum(white,lab,range(k+1))
    bg=np.isin(lab,np.where(sz>400)[0])&(lab>0)
    fg=~bg; fg[longrun(fg,0.45),:]=False
    fg=nd.binary_opening(fg,iterations=1)
    # recover white toes / chest touching the background: close small notches, but only with bright pixels
    cl=nd.binary_closing(fg,structure=np.ones((5,5)))&~fg
    fg=fg|(cl&(c.min(2)>150))
    return fg,(x0,y0),c
def blue(c):
    c=c.astype(int); return (c[...,2]>150)&(c[...,2]-c[...,0]>60)
def cutbox(fg,c,x0,y0,sl):
    m=fg[sl]; rgba=img[y0+sl[0].start:y0+sl[0].stop,x0+sl[1].start:x0+sl[1].stop].copy()
    holes=nd.binary_fill_holes(m)&~m; hl,hn=nd.label(holes); hs=nd.sum(holes,hl,range(hn+1))
    m=m|(np.isin(hl,np.where(hs<40)[0])&(hl>0))   # fill pinholes only; gaps between the legs stay open
    rgba[...,3]=np.where(m,255,0); return rgba
def frames(name):
    fg,(x0,y0),c=fgmask(name)
    l2,k=nd.label(fg); comps=[(sl,i+1,(l2[sl]==i+1).sum()) for i,sl in enumerate(nd.find_objects(l2))]
    big=sorted([t for t in comps if t[2]>700 and t[0][1].stop-t[0][1].start>40 and t[0][0].stop-t[0][0].start>25],key=lambda t:t[0][1].start)
    out=[]
    for sl,i,ar in big:
        m=np.isin(l2,[i]); 
        # attach small nearby bits (motion marks) within the frame's x-span
        for sl2,j,ar2 in comps:
            if ar2<300 and sl2[1].start>=sl[1].start-6 and sl2[1].stop<=sl[1].stop+6: m|=l2==j
        ys,xs=np.where(m); s=(slice(ys.min(),ys.max()+1),slice(xs.min(),xs.max()+1))
        out.append(cutbox(m,c,x0,y0,s))
    return out
def dogs(name, minA=1500):
    """split rows where blue effects merge frames: find dogs by dark fur, keep each dog's own pixels"""
    fg,(x0,y0),c=fgmask(name)
    dark=(c.max(2)<95)&fg
    dl,k=nd.label(nd.binary_closing(dark,iterations=2)); objs=nd.find_objects(dl)
    res=[]
    for i,sl in enumerate(objs):
        if (dl[sl]==i+1).sum()<minA: continue
        reg=nd.binary_dilation(dl==i+1,iterations=5)
        m=fg&reg&~(blue(c)&~nd.binary_dilation(dl==i+1,iterations=1))   # drop blue streaks except the collar
        lb,n=nd.label(m); sz=nd.sum(m,lb,range(n+1)); sz[0]=0; m=lb==np.argmax(sz)
        ys,xs=np.where(m); s=(slice(ys.min(),ys.max()+1),slice(xs.min(),xs.max()+1))
        res.append((xs.min()+x0,cutbox(m,c,x0,y0,s)))
    res.sort(key=lambda t:t[0]); return [r for _,r in res]
def fxitems(name,minA=300):
    fg,(x0,y0),c=fgmask(name)
    l2,k=nd.label(nd.binary_dilation(fg,iterations=3)); out=[]
    for i,sl in enumerate(nd.find_objects(l2)):
        m=(l2==i+1)&fg
        if m.sum()<minA: continue
        ys,xs=np.where(m); s=(slice(ys.min(),ys.max()+1),slice(xs.min(),xs.max()+1))
        out.append((xs.min()+x0,cutbox(m,c,x0,y0,s)))
    out.sort(key=lambda t:t[0]); return [r for _,r in out]
if __name__=='__main__':
    R={k:frames(k) for k in P if k not in('special','super','fx')}
    R['special']=dogs('special'); R['super']=dogs('super',1200); R['fx']=fxitems('fx'); R['spfx']=fxitems('special')
    pickle.dump(R,open('raw.pkl','wb'))
    for k,v in R.items(): print(k,len(v),[f.shape[:2] for f in v])
