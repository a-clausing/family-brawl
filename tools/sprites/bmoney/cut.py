import numpy as np, pickle
from PIL import Image, ImageDraw
from scipy import ndimage as nd
exec(open('panels.py').read().split("if __name__")[0])
def longrun(M,frac):
    out=np.zeros(M.shape[0],bool)
    for i,r in enumerate(M):
        d=np.diff(np.concatenate([[0],r.astype(np.int8),[0]])); st=np.where(d==1)[0]; en=np.where(d==-1)[0]
        out[i]=len(st)>0 and (en-st).max()>frac*M.shape[1]
    return out
GROUPS={'special':[188,260,380,540,1000,1188],'super':[150,214,320,610,712,808,900,983,1098,1190],'fx':[100,150,290,690,930,1190]}
def frames(name):
    x0,y0,x1,y1,n=P[name]
    c=a[y0:y1,x0:x1]; white=c.min(2)>225
    lab,k=nd.label(white); sz=nd.sum(white,lab,range(k+1))
    fg=~(np.isin(lab,np.where(sz>400)[0])&(lab>0))
    fg[longrun(fg,0.45),:]=False
    fg=nd.binary_opening(fg,iterations=1)
    l2,k2=nd.label(fg); objs=nd.find_objects(l2)
    comps=[]
    for i,sl in enumerate(objs):
        ar=(l2[sl]==i+1).sum()
        if ar<40: continue
        comps.append((sl,i+1,ar))
    if name in GROUPS:
        b=GROUPS[name]; groups=[[] for _ in range(len(b)-1)]
        for sl,i,ar in comps:
            cx=(sl[1].start+sl[1].stop)/2+x0
            for g in range(len(b)-1):
                if b[g]<=cx<b[g+1]: groups[g].append(i); break
        if name=='fx': groups=groups[1:]   # first slot is the label
    else:
        big=[(sl,i,ar) for sl,i,ar in comps if ar>700]; big.sort(key=lambda t:t[0][1].start)
        groups=[[i] for sl,i,ar in big]
        for sl,i,ar in comps:   # attach small bits (dust, sparks) to the nearest frame
            if ar>700: continue
            cx=(sl[1].start+sl[1].stop)/2; best=min(range(len(big)),key=lambda g:abs((big[g][0][1].start+big[g][0][1].stop)/2-cx))
            if abs((big[best][0][1].start+big[best][0][1].stop)/2-cx)<40 and ar<300: groups[best].append(i)
    out=[]
    for g in groups:
        if not g: continue
        m=np.isin(l2,g); ys,xs=np.where(m)
        sl=(slice(ys.min(),ys.max()+1),slice(xs.min(),xs.max()+1)); mm=m[sl]
        rgba=img[y0+sl[0].start:y0+sl[0].stop,x0+sl[1].start:x0+sl[1].stop].copy()
        col=rgba[...,:3].astype(int); wh=(col.min(2)>215)&mm
        wl,wn=nd.label(wh); ws=nd.sum(wh,wl,range(wn+1)); mm=mm&~(np.isin(wl,np.where(ws>=10)[0])&(wl>0))
        holes=nd.binary_fill_holes(mm)&~mm; hl,hn=nd.label(holes); hs=nd.sum(holes,hl,range(hn+1))
        mm=mm|(np.isin(hl,np.where(hs<6)[0])&(hl>0))
        rgba[...,3]=np.where(mm,255,0); out.append(rgba)
    return out
if __name__=='__main__':
    R={k:frames(k) for k in P}
    pickle.dump(R,open('raw.pkl','wb'))
    for k,v in R.items(): print(k,len(v),[f.shape[:2] for f in v])
