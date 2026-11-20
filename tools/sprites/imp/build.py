# Cut Imp's sheet into game frames. Run from this folder: python3 build.py
# Writes frames.pkl and lineup.png (check it by eye). One scale for every frame: idle = config.HEIGHT.
import pickle, sys, os, numpy as np
from scipy import ndimage as nd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import config as C
from dogsheet import load, down, trim, lineup

img, A = load(C.SHEET)


def cut(row, piece=150):
    y0, y1 = C.BANDS[row]; c = A[y0:y1]
    fg = C.foreground(c)
    fg = nd.binary_opening(fg, iterations=1)
    lab, k = nd.label(fg); objs = nd.find_objects(lab)
    out = []
    for a_, b_ in C.SPLITS[row]:
        keep = np.zeros_like(fg)
        for i, sl in enumerate(objs):
            m = lab[sl] == i + 1; n = m.sum()
            if n < piece: continue
            cx = (sl[1].start + sl[1].stop) / 2
            if not (a_ <= cx < b_): continue
            px = c[sl][m]
            red = ((px[:, 0] > 120) & (px[:, 1] < 100)).mean(); warm = (px[:, 0] > 150).mean()
            if red < 0.03 and warm < 0.2: continue      # a row label (black box, white text)
            keep[sl] |= m
        keep[:, :a_] = False; keep[:, b_:] = False
        keep = nd.binary_fill_holes(keep) & (C.foreground(c) | nd.binary_erosion(keep, iterations=2))
        ys, xs = np.where(keep)
        sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
        rgba = img[y0 + sl[0].start:y0 + sl[0].stop, sl[1].start:sl[1].stop].copy()
        rgba[..., 3] = np.where(keep[sl], 255, 0)
        out.append(rgba)
    return out


def despill(d):
    """Pull green-screen tint out of edge pixels."""
    c = d[..., :3].astype(int); g = c[..., 1]; lim = np.maximum(c[..., 0], c[..., 2])
    spill = (g > lim + 20) & (d[..., 3] > 0)
    c[..., 1] = np.where(spill, lim + 10, g)
    d = d.copy(); d[..., :3] = np.clip(c, 0, 255).astype(np.uint8); return d


def anchor(d, mode='body'):
    al = d[..., 3] > 0; ys, xs = np.where(al); feet = int(ys.max()) + 1; top = int(ys.min()); h = feet - top
    if mode == 'center': ax = d.shape[1] * 0.5
    else:   # middle of his red body in the torso band (ignores wings, tail and fire)
        band = np.zeros_like(al); band[top + int(h * 0.35):top + int(h * 0.75)] = True
        rb = al & band & C.isred(d[..., :3].astype(int))
        ax = float(np.median(np.where(rb)[1])) if rb.sum() > 20 else d.shape[1] * 0.5
    return dict(img=d, ax=ax, ay=feet, h=h, w=d.shape[1])


R = {row: cut(row) for row in C.SPLITS}
for k, v in R.items(): print(f'{k:12}', len(v), [f.shape[:2] for f in v])
idle_h = np.median([trim(f).shape[0] for f in R['idle']])
SCALE = C.HEIGHT / idle_h; print('scale', round(SCALE, 4))


def frame(raw, mode='body', s=None): return anchor(despill(trim(down(trim(raw), s or SCALE))), mode)


main = {k: [frame(f) for f in R[k]] for k in ('idle', 'walk', 'run', 'jump', 'attack', 'hit', 'getup')}
main['ko'] = [frame(f, 'center' if j >= 3 else 'body') for j, f in enumerate(R['ko'])]
main['special'] = [frame(f) for f in R['special'] + R['special_end']]
sup = [frame(f) for f in R['super'] + R['super_end']]
fx = {f'fire{j}': frame(f, 'center') for j, f in enumerate(R['fire'])}
fx.update({f'skull{j}': frame(f, 'center') for j, f in enumerate(R['skull'])})
pickle.dump((main, sup, fx, trim(R['super'][4]), SCALE), open('frames.pkl', 'wb'))   # raw super pose (arms up) for the close-up

others = [('WIN', pickle.load(open('../winston/frames.pkl', 'rb'))[0]['idle'][0])] if os.path.exists('../winston/frames.pkl') else []
print(lineup('lineup.png', type('c', (), {'TARGET': C.HEIGHT}), main, sup, {k: v['img'] for k, v in fx.items()}, others))
