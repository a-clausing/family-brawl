# Cut Harper's sheet into game frames. Run from this folder: python3 build.py
# Writes frames.pkl (main frames, super frames, effects) and lineup.png (check it by eye).
import pickle, numpy as np
from scipy import ndimage as nd
import config as C
from dogsheet import Sheet, build, lineup, down, trim

S = Sheet(C)
R = {}
for row in C.P:
    if row in ('super', 'fx'): continue
    R[row] = S.frames(row, piece=400)            # piece=400 drops the dark frame numbers
    print(f'{row:8} {len(R[row])} frames', [f.shape[:2] for f in R[row]])
sup_all = S.frames('super', splits=C.SUPER_SPLITS, minA=600, piece=400)
print('super   ', len(sup_all), [f.shape[:2] for f in sup_all])
R['super'] = [sup_all[j] for j in C.SUPER_DOG]

# effects are pink-on-pink with no outline: cut them by their light highlights instead
def fxcut():
    x0, y0, x1, y1 = C.P['fx']; c = S.a[y0:y1, x0:x1]
    m = nd.binary_closing(C.light(c), structure=np.ones((3, 3))); m = nd.binary_opening(m, iterations=1)
    out = []
    for a_, b_ in C.FX_SPLITS:
        mm = m.copy(); mm[:, :a_ - x0] = False; mm[:, b_ - x0:] = False
        lab, k = nd.label(mm); sz = nd.sum(mm, lab, range(k + 1)); keep = np.isin(lab, np.where(sz >= 40)[0]) & (lab > 0)
        ys, xs = np.where(keep); sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
        rgba = S.img[y0 + sl[0].start:y0 + sl[0].stop, x0 + sl[1].start:x0 + sl[1].stop].copy(); rgba[..., 3] = np.where(keep[sl], 255, 0)
        out.append(rgba)
    return out
fxr = fxcut()
print('fx      ', len(fxr), [f.shape[:2] for f in fxr])

main, sup = build(C, R)
FXW = {'swoosh': 60, 'swoosh2': 80, 'wave': 120, 'dust': 90}
fx = {n: down(trim(a), FXW[n] / trim(a).shape[1]) for n, a in zip(C.FX_NAMES, fxr)}
pickle.dump((main, sup, fx), open('frames.pkl', 'wb'))

wn = pickle.load(open('../winston/frames.pkl', 'rb'))[0]['idle'][0]
hd = pickle.load(open('../haddie/frames.pkl', 'rb'))[0]['idle'][0]
print(lineup('lineup.png', C, main, sup, fx, [('WIN', wn), ('HAD', hd)]))
