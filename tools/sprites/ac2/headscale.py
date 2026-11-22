# How big is each frame drawn compared with idle? Finds the dragon's head (from idle frame 0) in every frame at scales
# 0.7–1.5 by template matching; prints the scale that matches best per frame and the median per row.
# The sheet draws many poses smaller than idle, and some frames of a row smaller than others (the walk shrinks as it goes).
import pickle, numpy as np, cv2, sys
m = pickle.load(open('frames.pkl', 'rb'))[0]
def gray(f):
    a = f['img'].astype(np.float32); g = (a[..., :3].mean(2) * (a[..., 3] / 255)); return g
ref = m['idle'][0]; g = gray(ref); h, w = g.shape
head = g[0:int(h * 0.5), int(w * 0.3):int(w * 0.85)]   # head, horns and neck (facing right)
def best(f):
    t = gray(f); out = (0, 1)
    for s in np.arange(0.7, 1.4, 0.02):
        hh = cv2.resize(head, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        if hh.shape[0] > t.shape[0] or hh.shape[1] > t.shape[1]: continue
        r = cv2.matchTemplate(t, hh, cv2.TM_CCOEFF_NORMED).max()
        if r > out[0]: out = (r, s)
    return out
res = {}
for k, v in m.items():
    if k in ('down', 'roll', 'duck'): continue
    sc = [best(f) for f in v]; res[k] = sc
    print(f'{k:8}', ' '.join(f'{s:.2f}({r:.2f})' for r, s in sc))
