# Cut Goblin's sheet into game frames. Run from this folder: python3 build.py
# Writes frames.pkl and lineup.png (check it by eye). One scale for every frame: idle = config.HEIGHT.
import pickle, sys, os, numpy as np
from scipy import ndimage as nd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import config as C
from dogsheet import load, down, trim, lineup

img, A = load(C.SHEET)
FG = nd.binary_opening(C.foreground(A), iterations=1)
LAB, N = nd.label(FG); OBJ = nd.find_objects(LAB); SIZE = nd.sum(FG, LAB, range(1, N + 1))


def row_of(sl):
    cy = (sl[0].start + sl[0].stop) / 2
    for k, (y0, y1) in C.ROWS.items():
        if y0 <= cy < y1: return k


def cut(row, a, b, piece=30):
    keep = np.zeros_like(FG)
    for i, sl in enumerate(OBJ):
        if SIZE[i] < piece or row_of(sl) != row: continue
        x0, x1 = sl[1].start, sl[1].stop; cx = (x0 + x1) / 2
        ov = min(x1, b) - max(x0, a)
        if a <= cx < b or ov > 0.4 * (x1 - x0) or (ov > 0 and x1 - x0 > b - a):   # whole blob, or the part of a wide one in range
            keep[sl] |= LAB[sl] == i + 1
    keep[:, :a] = False; keep[:, b:] = False
    keep = nd.binary_fill_holes(keep) & C.foreground(A)   # fill, but drop background caught between his legs
    ys, xs = np.where(keep)
    rgba = img[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    rgba[..., 3] = np.where(keep[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return rgba


def despill(d):
    """Pull blue-screen tint out of edge pixels."""
    c = d[..., :3].astype(int); b = c[..., 2]; lim = np.maximum(c[..., 0], c[..., 1])
    edge = (d[..., 3] > 0) & ~nd.binary_erosion(d[..., 3] > 0, iterations=2)
    spill = (b > lim + 30) & (d[..., 3] > 0) & edge
    c[..., 2] = np.where(spill, lim, b)
    d = d.copy(); d[..., :3] = np.clip(c, 0, 255).astype(np.uint8); return d


def anchor(d, mode='body'):
    al = d[..., 3] > 0; ys, xs = np.where(al); feet = int(ys.max()) + 1; top = int(ys.min()); h = feet - top
    if mode == 'center': ax = d.shape[1] * 0.5
    else:   # middle of the body near the feet-to-chest band (ignores swooshes and effects)
        band = np.zeros_like(al); band[top + int(h * 0.3):top + int(h * 0.8)] = True
        cols = np.where((al & band).sum(0) > max(3, h * 0.25))[0]
        ax = float(np.median(cols)) if len(cols) else d.shape[1] * 0.5
    return dict(img=d, ax=ax, ay=feet, h=h, w=d.shape[1])


R = {k: [cut(*f) for f in v] for k, v in C.FRAMES.items()}
X = {k: [cut(*f) for f in v] for k, v in C.FX.items()}
for k, v in R.items(): print(f'{k:8}', len(v), [f.shape[:2] for f in v])
idle_h = np.median([trim(f).shape[0] for f in R['idle']])
SCALE = C.HEIGHT / idle_h; print('scale', round(SCALE, 4))


def frame(raw, mode='body', s=None): return anchor(despill(trim(down(trim(raw), s or SCALE))), mode)


main = {k: [frame(f, 'center' if (k == 'ko' and j >= 2) or k == 'roll' and 0 < j < 5 else 'body') for j, f in enumerate(v)] for k, v in R.items() if k != 'super'}
sup = [frame(f) for f in R['super']]
fx = {f'{k}{j}': frame(f, 'center') for k, v in X.items() for j, f in enumerate(v)}
pickle.dump((main, sup, fx, trim(R['super'][2]), SCALE), open('frames.pkl', 'wb'))   # raw super pose (bomb held up) for the close-up
others = [('IMP', pickle.load(open('../imp/frames.pkl', 'rb'))[0]['idle'][0])] if os.path.exists('../imp/frames.pkl') else []
print(lineup('lineup.png', type('c', (), {'TARGET': C.HEIGHT}), main, sup, {k: v['img'] for k, v in fx.items()}, others))
